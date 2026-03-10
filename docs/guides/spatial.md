# Spatial Data & Mapping

PyPUMS can attach TIGER/Line cartographic boundary shapefiles to any Census
query, returning a `GeoDataFrame` that is ready for mapping, spatial joins, and
geospatial analysis.

!!! info "Requires the spatial extras"
    Geometry features depend on **geopandas** and its dependencies (`shapely`,
    `pyproj`, `fiona`). Install them with:

    ```bash
    uv add "pypums[spatial]"
    ```

---

## The `geometry=True` flag

The fastest way to get spatial data is to pass `geometry=True` to any of the
main data retrieval functions. PyPUMS will automatically download the
corresponding TIGER/Line shapefile, merge it with the tabular data on the
`GEOID` column, and return a `GeoDataFrame`.

=== "get_acs()"

    ```python
    import pypums

    gdf = pypums.get_acs(
        geography="county",
        variables="B01001_001",
        state="CA",
        year=2023,
        geometry=True,
    )
    print(type(gdf))
    # <class 'geopandas.geodataframe.GeoDataFrame'>
    ```

=== "get_decennial()"

    ```python
    import pypums

    gdf = pypums.get_decennial(
        geography="state",
        variables="P1_001N",
        year=2020,
        geometry=True,
    )
    ```

=== "get_estimates()"

    ```python
    import pypums

    gdf = pypums.get_estimates(
        geography="state",
        product="population",
        vintage=2023,
        geometry=True,
    )
    ```

=== "get_flows()"

    ```python
    import pypums

    gdf = pypums.get_flows(
        geography="county",
        state="NY",
        year=2019,
        geometry=True,
    )
    ```

---

## Coordinate reference system

All geometry returned by PyPUMS is in **NAD83 (EPSG:4269)**, which is the
native CRS of the Census Bureau's TIGER/Line files. You can verify this on any
`GeoDataFrame`:

```python
print(gdf.crs)
# EPSG:4269
```

### Reprojecting

You will often need to reproject to a different CRS depending on your use case.

=== "Web mapping (EPSG:4326)"

    Most web mapping libraries (Leaflet, Mapbox, Folium) expect **WGS 84**:

    ```python
    gdf_wgs84 = gdf.to_crs(epsg=4326)
    ```

=== "Local analysis (projected CRS)"

    For area or distance calculations, use a projected CRS appropriate to your
    region. For example, **EPSG:2229** (NAD83 / California zone 5, in feet):

    ```python
    gdf_projected = gdf.to_crs(epsg=2229)
    area_sq_ft = gdf_projected.geometry.area
    ```

!!! tip
    The EPSG code you pick should match the part of the country you are
    studying. [epsg.io](https://epsg.io/) is a handy search tool for finding
    the right projection.

---

## Shapefile resolution

TIGER/Line cartographic boundary files come in three resolutions. The default
is `500k`, which strikes a good balance between detail and file size.

| Resolution | Description                   | Best for                          |
|------------|-------------------------------|-----------------------------------|
| `500k`     | 1:500,000 (default)           | Most maps and analysis            |
| `5m`       | 1:5,000,000                   | National-level overview maps      |
| `20m`      | 1:20,000,000                  | Thumbnail or small inset maps     |

You control the resolution through the `attach_geometry()` function (see below)
or when calling it indirectly via `geometry=True`. The `geometry=True` flag
always uses `500k`.

---

## Supported geographies

The following geography levels have matching TIGER/Line shapefiles:

| Geography              | Requires `state`? | Notes                                  |
|------------------------|--------------------|----------------------------------------|
| `state`                | No                 | All 50 states + DC + territories       |
| `county`               | No                 | All US counties                        |
| `tract`                | Yes                | Census tracts (sub-county)             |
| `block group`          | Yes                | Block groups (sub-tract)               |
| `place`                | Yes                | Census-designated and incorporated places |
| `congressional district` | No              | US House districts                     |
| `zcta`                 | No                 | ZIP Code Tabulation Areas              |
| `puma`                 | Yes                | Public Use Microdata Areas             |
| `cbsa`                 | No                 | Core-Based Statistical Areas (metros)  |
| `csa`                  | No                 | Combined Statistical Areas             |

!!! warning "Sub-state geographies require the `state` parameter"
    For `tract`, `block group`, `place`, and `puma`, the Census Bureau
    publishes shapefiles per state. PyPUMS needs the `state` parameter to
    know which file to download.

---

## `attach_geometry()` standalone function

If you already have a DataFrame with a `GEOID` column (for example, from a
cached query or an external source), you can attach geometry after the fact
with `attach_geometry()`:

```python
from pypums.spatial import attach_geometry

# Fetch tabular data without geometry.
df = pypums.get_acs(
    geography="tract",
    variables="B19013_001",
    state="IL",
    county="031",
    year=2023,
)

# Attach geometry separately, choosing a coarser resolution.
gdf = attach_geometry(
    df,
    geography="tract",
    state="IL",
    year=2023,
    resolution="500k",
)
```

**Signature:**

```python
attach_geometry(
    df,                   # DataFrame with a GEOID column
    geography,            # geography level name
    state=None,           # state FIPS or abbreviation
    year=2023,            # data year
    resolution="500k",    # "500k", "5m", or "20m"
) -> GeoDataFrame
```

---

## Plotting with Altair

[Altair](https://altair-viz.github.io/) works naturally with `GeoDataFrame` objects
returned by PyPUMS. Use `mark_geoshape()` to create choropleth maps:

```python
import altair as alt

alt.Chart(gdf).mark_geoshape().encode(
    color=alt.Color("estimate:Q", title="Median Household Income"),
    tooltip=["NAME:N", "estimate:Q"],
).project("albersUsa").properties(
    width=600, height=400,
    title="Median Household Income by Tract",
)
```

For more control, use a color scale and configure the legend:

```python
alt.Chart(gdf).mark_geoshape(stroke="white", strokeWidth=0.3).encode(
    color=alt.Color(
        "estimate:Q",
        scale=alt.Scale(scheme="yellowgreenblue"),
        legend=alt.Legend(title="Median Income ($)"),
    ),
    tooltip=["NAME:N", alt.Tooltip("estimate:Q", format="$,")],
).project("albersUsa").properties(width=600, height=400)
```

!!! example "Interactive preview — state-level median household income"

```vegalite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": 600,
  "height": 400,
  "title": "Median Household Income by State (sample data)",
  "data": {
    "url": "https://cdn.jsdelivr.net/npm/vega-datasets@v2.7.0/data/us-10m.json",
    "format": {"type": "topojson", "feature": "states"}
  },
  "transform": [
    {
      "lookup": "id",
      "from": {
        "data": {
          "values": [
            {"id": 1, "estimate": 56950, "name": "Alabama"},
            {"id": 2, "estimate": 77640, "name": "Alaska"},
            {"id": 4, "estimate": 65913, "name": "Arizona"},
            {"id": 5, "estimate": 52528, "name": "Arkansas"},
            {"id": 6, "estimate": 91905, "name": "California"},
            {"id": 8, "estimate": 82254, "name": "Colorado"},
            {"id": 9, "estimate": 83771, "name": "Connecticut"},
            {"id": 10, "estimate": 72724, "name": "Delaware"},
            {"id": 11, "estimate": 101027, "name": "District of Columbia"},
            {"id": 12, "estimate": 63062, "name": "Florida"},
            {"id": 13, "estimate": 65030, "name": "Georgia"},
            {"id": 15, "estimate": 84857, "name": "Hawaii"},
            {"id": 16, "estimate": 65988, "name": "Idaho"},
            {"id": 17, "estimate": 72205, "name": "Illinois"},
            {"id": 18, "estimate": 62222, "name": "Indiana"},
            {"id": 19, "estimate": 65573, "name": "Iowa"},
            {"id": 20, "estimate": 64521, "name": "Kansas"},
            {"id": 21, "estimate": 55573, "name": "Kentucky"},
            {"id": 22, "estimate": 52087, "name": "Louisiana"},
            {"id": 23, "estimate": 64767, "name": "Maine"},
            {"id": 24, "estimate": 90203, "name": "Maryland"},
            {"id": 25, "estimate": 89026, "name": "Massachusetts"},
            {"id": 26, "estimate": 63498, "name": "Michigan"},
            {"id": 27, "estimate": 77706, "name": "Minnesota"},
            {"id": 28, "estimate": 48610, "name": "Mississippi"},
            {"id": 29, "estimate": 60789, "name": "Missouri"},
            {"id": 30, "estimate": 60560, "name": "Montana"},
            {"id": 31, "estimate": 65551, "name": "Nebraska"},
            {"id": 32, "estimate": 65686, "name": "Nevada"},
            {"id": 33, "estimate": 83449, "name": "New Hampshire"},
            {"id": 34, "estimate": 89296, "name": "New Jersey"},
            {"id": 35, "estimate": 53992, "name": "New Mexico"},
            {"id": 36, "estimate": 74314, "name": "New York"},
            {"id": 37, "estimate": 60516, "name": "North Carolina"},
            {"id": 38, "estimate": 68131, "name": "North Dakota"},
            {"id": 39, "estimate": 61938, "name": "Ohio"},
            {"id": 40, "estimate": 55826, "name": "Oklahoma"},
            {"id": 41, "estimate": 70084, "name": "Oregon"},
            {"id": 42, "estimate": 67587, "name": "Pennsylvania"},
            {"id": 44, "estimate": 71169, "name": "Rhode Island"},
            {"id": 45, "estimate": 59318, "name": "South Carolina"},
            {"id": 46, "estimate": 63920, "name": "South Dakota"},
            {"id": 47, "estimate": 59695, "name": "Tennessee"},
            {"id": 48, "estimate": 66963, "name": "Texas"},
            {"id": 49, "estimate": 79449, "name": "Utah"},
            {"id": 50, "estimate": 67674, "name": "Vermont"},
            {"id": 51, "estimate": 80615, "name": "Virginia"},
            {"id": 53, "estimate": 84247, "name": "Washington"},
            {"id": 54, "estimate": 50884, "name": "West Virginia"},
            {"id": 55, "estimate": 67125, "name": "Wisconsin"},
            {"id": 56, "estimate": 65003, "name": "Wyoming"}
          ]
        },
        "key": "id",
        "fields": ["estimate", "name"]
      }
    }
  ],
  "projection": {"type": "albersUsa"},
  "mark": {"type": "geoshape", "stroke": "white", "strokeWidth": 0.5},
  "encoding": {
    "color": {
      "field": "estimate",
      "type": "quantitative",
      "scale": {"scheme": "yellowgreenblue"},
      "legend": {"title": "Median Income ($)", "format": "$,"}
    },
    "tooltip": [
      {"field": "name", "type": "nominal", "title": "State"},
      {"field": "estimate", "type": "quantitative", "title": "Median Income", "format": "$,"}
    ]
  }
}
```

---

## Spatial joins

Combine Census data with non-Census spatial data using `geopandas.sjoin()`.
This is useful when you have points (e.g., business locations, crime incidents)
and want to know which Census geography they fall into.

```python
import geopandas as gpd
import pypums

# Census tracts with population data.
tracts = pypums.get_acs(
    geography="tract",
    variables="B01001_001",
    state="TX",
    county="201",
    year=2023,
    geometry=True,
)

# Your own point data (e.g., store locations).
stores = gpd.read_file("stores.geojson")

# Make sure both layers share the same CRS.
stores = stores.to_crs(tracts.crs)

# Spatial join: assign each store to its tract.
joined = gpd.sjoin(stores, tracts, how="left", predicate="within")
```

!!! note
    `sjoin()` requires both GeoDataFrames to be in the same CRS. Always
    call `.to_crs()` on one of them before joining if they differ.

---

## Dot density mapping

`as_dot_density()` converts polygon data into random points, where each
dot represents a fixed number of people (or any other count). This is a
popular technique for visualizing racial or ethnic composition at fine
spatial scales.

```python
from pypums.spatial import as_dot_density
import pypums

# Get race data by tract.
gdf = pypums.get_acs(
    geography="tract",
    variables=["B03002_003", "B03002_004", "B03002_006", "B03002_012"],
    state="IL",
    county="031",
    year=2023,
    output="wide",
    geometry=True,
)

# Convert to dots (1 dot = 100 people).
dots = as_dot_density(
    gdf,
    values={
        "B03002_003E": "White",
        "B03002_004E": "Black",
        "B03002_006E": "Asian",
        "B03002_012E": "Hispanic",
    },
    dots_per_value=100,
    seed=42,
)

# Extract point coordinates for Altair.
dots = dots.copy()
dots["lon"] = dots.geometry.x
dots["lat"] = dots.geometry.y

# Plot.
import altair as alt

alt.Chart(dots).mark_circle(size=1, opacity=0.6).encode(
    longitude="lon:Q",
    latitude="lat:Q",
    color=alt.Color(
        "value:N",
        scale=alt.Scale(
            domain=["White", "Black", "Asian", "Hispanic"],
            range=["#1f77b4", "#2ca02c", "#d62728", "#ff7f0e"],
        ),
    ),
    tooltip=["value:N"],
).project("albersUsa").properties(width=600, height=600)
```

**Signature:**

```python
as_dot_density(
    gdf,                  # GeoDataFrame with polygon geometries
    values,               # dict of {column_name: label}
    dots_per_value=100,   # data units per dot
    seed=None,            # random seed for reproducibility
) -> GeoDataFrame        # point GeoDataFrame with "geometry" and "value" columns
```

---

## Population-weighted interpolation

When you need to transfer data from one set of boundaries to another (for
example, from 2010 tracts to 2020 tracts, or from tracts to school districts),
use `interpolate_pw()`. It distributes values proportionally based on
population weights.

```python
from pypums.spatial import interpolate_pw

# Source: income data on 2010 tracts.
from_gdf = ...  # GeoDataFrame with "median_income" and "POP" columns

# Target: 2020 tract boundaries.
to_gdf = ...    # GeoDataFrame with 2020 tract polygons

result = interpolate_pw(
    from_gdf,
    to_gdf,
    value_col="median_income",
    weight_col="POP",
    extensive=True,
)
```

**Signature:**

```python
interpolate_pw(
    from_gdf,             # source GeoDataFrame
    to_gdf,               # target GeoDataFrame
    value_col,            # column name in from_gdf to interpolate
    weight_col="POP",     # column name in from_gdf with population weights
    extensive=True,       # True for counts (sum), False for rates (weighted avg)
) -> GeoDataFrame
```

| Parameter   | `extensive=True`          | `extensive=False`           |
|-------------|---------------------------|-----------------------------|
| Use for     | Counts, totals            | Rates, medians, averages    |
| Method      | Proportional distribution | Population-weighted average |
| Example     | Total population          | Median household income     |

---

## Memory considerations

Spatial queries download shapefiles and store full polygon geometries in
memory. A few tips for working with large datasets:

!!! tip "Keep memory usage in check"

    - **Use a coarser resolution** (`5m` or `20m`) if you only need a national
      overview and do not need precise boundaries.
    - **Filter by state** whenever possible. Tract-level shapefiles for a
      single state are much smaller than a nationwide download.
    - **Drop the geometry column** when you no longer need it:

        ```python
        df = pd.DataFrame(gdf.drop(columns="geometry"))
        ```

    - **Save to file** and work from disk instead of re-downloading:

        ```python
        gdf.to_parquet("tracts_il_2023.parquet")
        # Later:
        gdf = gpd.read_parquet("tracts_il_2023.parquet")
        ```

    - **Cache your queries** with `cache_table=True` so repeated runs do not
      re-fetch the shapefile from the Census Bureau servers.

---

## Troubleshooting

**`ImportError: geopandas is required for spatial operations`**
:   Install the spatial extra: `uv add "pypums[spatial]"`. This pulls in
    `geopandas`, `shapely`, and `pyproj`.

**Geometry column is all `None`**
:   The Census TIGER/Line server may not have shapefiles for the geography
    level and year you requested. Try a different year or a broader
    geography (e.g., county instead of block group).

**CRS mismatch when combining DataFrames**
:   All PyPUMS geometry is returned in EPSG:4269 (NAD83). If you are
    combining with data in a different CRS, reproject first:

    ```python
    gdf = gdf.to_crs(epsg=4326)  # convert to WGS84
    ```

**`MemoryError` with tract-level national data**
:   Nationwide tract shapefiles are very large. Filter by state, use a
    coarser resolution (`20m`), or work state-by-state and concatenate
    after dropping unneeded columns.

**Dot-density map is slow or crashes**
:   `as_dot_density()` generates one point per `dots_per_value` people. For
    large areas, increase `dots_per_value` (e.g., `dots_per_value=100`
    instead of `dots_per_value=1`) or subset to a single county before
    generating dots.

---

## See Also

- [ACS Data](acs-data.md) — Using `get_acs(geometry=True)` to retrieve spatial ACS data
- [Geography & FIPS](geography.md) — Supported geographies and FIPS code structure
