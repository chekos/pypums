# Spatial Data & Mapping

PyPUMS can attach Census cartographic boundary shapefiles to any Census
query, returning a `GeoDataFrame` that is ready for mapping, spatial joins, and
geospatial analysis.  Shapefile downloads are handled by
[pygris](https://github.com/walkerke/pygris), with automatic local caching so
files are only downloaded once.

!!! info "Requires the spatial extras"
    Geometry features depend on **geopandas** and **pygris** (plus their
    dependencies). Install them with:

    ```bash
    uv add "pypums[spatial]"
    ```

---

## The `geometry=True` flag

The fastest way to get spatial data is to pass `geometry=True` to any of the
main data retrieval functions. PyPUMS will automatically download the
corresponding cartographic boundary shapefile (via pygris), merge it with the
tabular data on the `GEOID` column, and return a `GeoDataFrame`.  Downloaded
shapefiles are cached locally so subsequent calls are fast.

=== "get_acs()"

    ```python exec="on" source="tabbed-left" session="spatial"
    import pypums

    gdf = pypums.get_acs(
        geography="county",
        variables="B01001_001",
        state="CA",
        year=2023,
        geometry=True,
    )
    print(type(gdf))
    print(gdf.head())
    ```

    !!! tip
        Notice the `geometry` column — that is what makes this a
        **GeoDataFrame** instead of a plain DataFrame. Each row carries its
        polygon boundary, ready for mapping or spatial analysis.

=== "get_decennial()"

    ```python exec="on" source="tabbed-left" session="spatial"
    import pypums

    gdf = pypums.get_decennial(
        geography="state",
        variables="P1_001N",
        year=2020,
        geometry=True,
    )
    print(gdf.head())
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
    print(gdf.head())
    ```

    ```
      GEONAME  POP_2023  ... geometry
    0  Alabama   5074296  ...  POLYGON ((...))
    1   Alaska    733583  ...  MULTIPOLYGON ((...))
    2  Arizona   7359197  ...  POLYGON ((...))
    3  Arkansas  3045637  ...  POLYGON ((...))
    4  California 39029342 ... MULTIPOLYGON ((...))
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
    print(gdf.head())
    ```

    ```
      GEOID          NAME  ... geometry
    0  36001  Albany County  ...  POLYGON ((...))
    1  36003  Allegany County  ...  POLYGON ((...))
    2  36005  Bronx County  ...  POLYGON ((...))
    3  36007  Broome County  ...  POLYGON ((...))
    4  36009  Cattaraugus County  ...  POLYGON ((...))
    ```

!!! example "Interactive preview — 2020 Census population by state"

    Every `geometry=True` call returns a GeoDataFrame you can map directly.
    Here is the decennial population data from the tab above rendered as a
    choropleth:

    ```vegalite
    {
      "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
      "width": 600,
      "height": 400,
      "title": "2020 Decennial Census — Total Population by State",
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
                {"id": 1, "value": 5024279, "name": "Alabama"},
                {"id": 2, "value": 733391, "name": "Alaska"},
                {"id": 4, "value": 7151502, "name": "Arizona"},
                {"id": 5, "value": 3011524, "name": "Arkansas"},
                {"id": 6, "value": 39538223, "name": "California"},
                {"id": 8, "value": 5773714, "name": "Colorado"},
                {"id": 9, "value": 3605944, "name": "Connecticut"},
                {"id": 10, "value": 989948, "name": "Delaware"},
                {"id": 11, "value": 689545, "name": "District of Columbia"},
                {"id": 12, "value": 21538187, "name": "Florida"},
                {"id": 13, "value": 10711908, "name": "Georgia"},
                {"id": 15, "value": 1455271, "name": "Hawaii"},
                {"id": 16, "value": 1839106, "name": "Idaho"},
                {"id": 17, "value": 12812508, "name": "Illinois"},
                {"id": 18, "value": 6785528, "name": "Indiana"},
                {"id": 19, "value": 3190369, "name": "Iowa"},
                {"id": 20, "value": 2937880, "name": "Kansas"},
                {"id": 21, "value": 4505836, "name": "Kentucky"},
                {"id": 22, "value": 4657757, "name": "Louisiana"},
                {"id": 23, "value": 1362359, "name": "Maine"},
                {"id": 24, "value": 6177224, "name": "Maryland"},
                {"id": 25, "value": 7029917, "name": "Massachusetts"},
                {"id": 26, "value": 10077331, "name": "Michigan"},
                {"id": 27, "value": 5706494, "name": "Minnesota"},
                {"id": 28, "value": 2961279, "name": "Mississippi"},
                {"id": 29, "value": 6154913, "name": "Missouri"},
                {"id": 30, "value": 1084225, "name": "Montana"},
                {"id": 31, "value": 1961504, "name": "Nebraska"},
                {"id": 32, "value": 3104614, "name": "Nevada"},
                {"id": 33, "value": 1377529, "name": "New Hampshire"},
                {"id": 34, "value": 9288994, "name": "New Jersey"},
                {"id": 35, "value": 2117522, "name": "New Mexico"},
                {"id": 36, "value": 20201249, "name": "New York"},
                {"id": 37, "value": 10439388, "name": "North Carolina"},
                {"id": 38, "value": 779094, "name": "North Dakota"},
                {"id": 39, "value": 11799448, "name": "Ohio"},
                {"id": 40, "value": 3959353, "name": "Oklahoma"},
                {"id": 41, "value": 4237256, "name": "Oregon"},
                {"id": 42, "value": 13002700, "name": "Pennsylvania"},
                {"id": 44, "value": 1097379, "name": "Rhode Island"},
                {"id": 45, "value": 5118425, "name": "South Carolina"},
                {"id": 46, "value": 886667, "name": "South Dakota"},
                {"id": 47, "value": 6910840, "name": "Tennessee"},
                {"id": 48, "value": 29145505, "name": "Texas"},
                {"id": 49, "value": 3271616, "name": "Utah"},
                {"id": 50, "value": 643077, "name": "Vermont"},
                {"id": 51, "value": 8631393, "name": "Virginia"},
                {"id": 53, "value": 7705281, "name": "Washington"},
                {"id": 54, "value": 1793716, "name": "West Virginia"},
                {"id": 55, "value": 5893718, "name": "Wisconsin"},
                {"id": 56, "value": 576851, "name": "Wyoming"}
              ]
            },
            "key": "id",
            "fields": ["value", "name"]
          }
        }
      ],
      "projection": {"type": "albersUsa"},
      "mark": {"type": "geoshape", "stroke": "white", "strokeWidth": 0.5},
      "encoding": {
        "color": {
          "field": "value",
          "type": "quantitative",
          "scale": {"scheme": "blues"},
          "legend": {"title": "Population", "format": "~s"}
        },
        "tooltip": [
          {"field": "name", "type": "nominal", "title": "State"},
          {"field": "value", "type": "quantitative", "title": "Population", "format": ","}
        ]
      }
    }
    ```

---

## Coordinate reference system

All geometry returned by PyPUMS is in **NAD83 (EPSG:4269)**, which is the
native CRS of the Census Bureau's cartographic boundary files. You can verify this on any
`GeoDataFrame`:

```python exec="on" source="tabbed-left" session="spatial"
print(gdf.crs)
```

```python exec="on" source="tabbed-left" session="spatial"
print(gdf.crs.name)
```

### Reprojecting

You will often need to reproject to a different CRS depending on your use case.

=== "Web mapping (EPSG:4326)"

    Most web mapping libraries (Leaflet, Mapbox, Folium) expect **WGS 84**:

    ```python exec="on" source="tabbed-left" session="spatial"
    gdf_wgs84 = gdf.to_crs(epsg=4326)
    print(gdf_wgs84.crs)
    ```

=== "Local analysis (projected CRS)"

    For area or distance calculations, use a projected CRS appropriate to your
    region. For example, **EPSG:2229** (NAD83 / California zone 5, in feet):

    ```python exec="on" source="tabbed-left" session="spatial"
    gdf_projected = gdf.to_crs(epsg=2229)
    area_sq_ft = gdf_projected.geometry.area
    print(area_sq_ft.head())
    ```

!!! tip
    The EPSG code you pick should match the part of the country you are
    studying. [epsg.io](https://epsg.io/) is a handy search tool for finding
    the right projection.

---

## Shapefile resolution

Cartographic boundary files come in three resolutions. The default
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

The following geography levels have matching cartographic boundary shapefiles:

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
    publishes shapefiles per state. PyPUMS will raise a `ValueError` if you
    omit the `state` parameter for these geography levels.

---

## `attach_geometry()` standalone function

If you already have a DataFrame with a `GEOID` column (for example, from a
cached query or an external source), you can attach geometry after the fact
with `attach_geometry()`:

```python exec="on" source="tabbed-left" session="spatial"
from pypums.spatial import attach_geometry
import pypums

# Fetch tabular data without geometry.
df = pypums.get_acs(
    geography="tract",
    variables="B19013_001",
    state="IL",
    county="031",
    year=2023,
)
print(df.head())
```

```python exec="on" source="tabbed-left" session="spatial"
# Attach geometry separately, choosing a coarser resolution.
gdf = attach_geometry(
    df,
    geography="tract",
    state="IL",
    year=2023,
    resolution="500k",
)
print(type(gdf))
print(gdf.columns.tolist())
print(gdf.head())
```

!!! tip "Before and after"
    Notice how the first `print()` shows a plain **DataFrame** with five
    columns. After `attach_geometry()`, the result gains a `geometry` column
    and becomes a **GeoDataFrame** — ready for mapping or spatial analysis.

**Signature:**

```python
attach_geometry(
    df,                   # DataFrame with a GEOID column
    geography,            # geography level name
    state=None,           # state FIPS or abbreviation
    year=2023,            # data year
    resolution="500k",    # "500k", "5m", or "20m"
    cache=True,           # cache shapefiles locally (via pygris)
) -> GeoDataFrame
```

---

## Plotting with Altair

[Altair](https://altair-viz.github.io/) works naturally with `GeoDataFrame` objects
returned by PyPUMS. Use `mark_geoshape()` to create choropleth maps:

```python
import altair as alt

chart = alt.Chart(gdf).mark_geoshape().encode(
    color=alt.Color("estimate:Q", title="Median Household Income"),
    tooltip=["NAME:N", "estimate:Q"],
).project("albersUsa").properties(
    width=600, height=400,
    title="Median Household Income by State",
)
chart
```

!!! example "Interactive preview — basic choropleth"

    ```vegalite
    {
      "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
      "width": 600,
      "height": 400,
      "title": "Median Household Income by State",
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
          "legend": {"title": "Median Household Income", "format": "$~s"}
        },
        "tooltip": [
          {"field": "name", "type": "nominal", "title": "State"},
          {"field": "estimate", "type": "quantitative", "title": "Median Income", "format": "$,"}
        ]
      }
    }
    ```

For more control, use a color scale and configure the legend:

```python
chart = alt.Chart(gdf).mark_geoshape(stroke="white", strokeWidth=0.3).encode(
    color=alt.Color(
        "estimate:Q",
        scale=alt.Scale(scheme="yellowgreenblue"),
        legend=alt.Legend(title="Median Income ($)"),
    ),
    tooltip=["NAME:N", alt.Tooltip("estimate:Q", format="$,")],
).project("albersUsa").properties(width=600, height=400)
chart
```

!!! example "Interactive preview — styled choropleth with custom color scale"

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
          "legend": {"title": "Median Income ($)", "format": "$~s"}
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
print(joined.head())
```

```
          store_name                       geometry  index_right      GEOID                                              NAME     variable  estimate  moe
0  Downtown Grocery  POINT (-95.362 29.764)            42  48201312100  Census Tract 3121, Harris County, Texas  B01001_001      5241  498
1    Heights Market  POINT (-95.392 29.793)            18  48201311300  Census Tract 3113, Harris County, Texas  B01001_001      3812  341
2   Midtown Express  POINT (-95.383 29.738)            56  48201313200  Census Tract 3132, Harris County, Texas  B01001_001      4105  512
3     Galleria Deli  POINT (-95.461 29.739)            73  48201410300  Census Tract 4103, Harris County, Texas  B01001_001      6723  620
4   Memorial Pantry  POINT (-95.503 29.779)            81  48201430100  Census Tract 4301, Harris County, Texas  B01001_001      3290  402
```

!!! tip
    After the join, each store row now carries the tract's `GEOID`, `NAME`,
    and population estimate. You can use this to answer questions like
    "which stores are in the most populated tracts?" or aggregate store
    counts per tract.

!!! note
    `sjoin()` requires both GeoDataFrames to be in the same CRS. Always
    call `.to_crs()` on one of them before joining if they differ.

---

## Dot density mapping

`as_dot_density()` converts polygon data into random points, where each
dot represents a fixed number of people (or any other count). This is a
popular technique for visualizing racial or ethnic composition at fine
spatial scales.

```python exec="on" source="tabbed-left" session="spatial"
from pypums.spatial import as_dot_density
import pypums

# Get race data by tract.
gdf = pypums.get_acs(
    geography="tract",
    variables=["B03002_003", "B03002_004", "B03002_006", "B03002_012"],
    state="CA",
    county="001",
    year=2023,
    output="wide",
    geometry=True,
)
print(gdf.head())
```

```python exec="on" source="tabbed-left" session="spatial"
# Convert to dots (1 dot = 500 people).
dots = as_dot_density(
    gdf,
    values={
        "B03002_003E": "White",
        "B03002_004E": "Black",
        "B03002_006E": "Asian",
        "B03002_012E": "Hispanic",
    },
    dots_per_value=500,
    seed=42,
)
print(dots.head(10))
```

```python
# Extract point coordinates for Altair.
dots = dots.copy()
dots["lon"] = dots.geometry.x
dots["lat"] = dots.geometry.y

# Plot.
import altair as alt

chart = alt.Chart(dots).mark_circle(size=1, opacity=0.6).encode(
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
).project("mercator").properties(width=600, height=600)
chart
```

!!! example "Interactive preview — dot density map of Alameda County, CA (sample data)"

    Each dot represents 500 people. The spatial distribution of dots reveals
    neighborhood-level patterns of racial and ethnic composition.

    ```vegalite
    {
      "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
      "layer": [
        {
          "data": {
            "url": "../../assets/alameda-boundary.json",
            "format": {"type": "json"}
          },
          "mark": {
            "type": "geoshape",
            "fill": "#e8e8e8",
            "stroke": "#999",
            "strokeWidth": 1
          }
        },
        {
          "data": {
            "url": "../../assets/alameda-dots.json"
          },
          "mark": {
            "type": "circle",
            "size": 8,
            "opacity": 0.6
          },
          "encoding": {
            "longitude": {
              "field": "lon",
              "type": "quantitative"
            },
            "latitude": {
              "field": "lat",
              "type": "quantitative"
            },
            "color": {
              "field": "value",
              "type": "nominal",
              "scale": {
                "domain": [
                  "White",
                  "Black",
                  "Asian",
                  "Hispanic"
                ],
                "range": [
                  "#1f77b4",
                  "#2ca02c",
                  "#d62728",
                  "#ff7f0e"
                ]
              },
              "legend": {
                "title": "Race/Ethnicity"
              }
            }
          }
        }
      ],
      "projection": {
        "type": "mercator"
      },
      "width": 500,
      "height": 500,
      "title": "Racial & Ethnic Dot Density — Alameda County, CA (1 dot = 500 people)"
    }
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
print(result.head())
```

```
       GEOID                                              NAME  median_income                                           geometry
0  17031010100  Census Tract 101, Cook County, Illinois            58421.3  POLYGON ((-87.63 41.90, -87.63 41.90, -87.62...
1  17031010201  Census Tract 102.01, Cook County, Illinois         73812.7  POLYGON ((-87.63 41.91, -87.63 41.91, -87.62...
2  17031010202  Census Tract 102.02, Cook County, Illinois         45129.5  POLYGON ((-87.64 41.91, -87.64 41.91, -87.63...
3  17031010300  Census Tract 103, Cook County, Illinois             36291.0  POLYGON ((-87.64 41.92, -87.64 41.92, -87.63...
4  17031010400  Census Tract 104, Cook County, Illinois             30187.4  POLYGON ((-87.65 41.92, -87.65 41.91, -87.64...
```

!!! info
    The result is a GeoDataFrame with the **target** boundaries and the
    interpolated values. Population-weighted interpolation ensures that
    areas with more people contribute more to the transferred value than
    sparsely populated areas.

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

        ```python exec="on" source="tabbed-left" session="spatial"
        import pandas as pd
        df = pd.DataFrame(gdf.drop(columns="geometry"))
        print(type(df))
        ```

    - **Save to file** and work from disk instead of re-downloading:

        ```python exec="on" source="tabbed-left" session="spatial"
        import tempfile, os
        import geopandas as gpd
        tmpfile = os.path.join(tempfile.mkdtemp(), "tracts_il_2023.parquet")
        gdf.to_parquet(tmpfile)
        # Later:
        gdf = gpd.read_parquet(tmpfile)
        print(gdf.shape)
        ```

    - **Shapefile caching is automatic.** PyPUMS uses pygris with caching
      enabled, so shapefiles are downloaded once and reused from a local
      cache directory (`~/.cache/pygris/` on Linux,
      `~/Library/Caches/pygris/` on macOS).

---

## Troubleshooting

**`ImportError: geopandas is required for spatial operations`**
:   Install the spatial extra: `uv add "pypums[spatial]"`. This pulls in
    `geopandas`, `pygris`, `shapely`, and `pyproj`.

**`ValueError: geography='tract' requires a state parameter`**
:   Sub-state geographies (`tract`, `block group`, `place`, `puma`) need a
    `state` argument.  Pass a FIPS code, abbreviation, or full name.

**Geometry column is all `None`**
:   The Census Bureau may not have shapefiles for the geography level and
    year you requested. Try a different year or a broader geography (e.g.,
    county instead of block group).

**CRS mismatch when combining DataFrames**
:   All PyPUMS geometry is returned in EPSG:4269 (NAD83). If you are
    combining with data in a different CRS, reproject first:

    ```python
    gdf = gdf.to_crs(epsg=4326)  # convert to WGS84
    print(gdf.crs)
    ```

    ```
    EPSG:4326
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
