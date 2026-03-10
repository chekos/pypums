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
    print(gdf.head())
    ```

    ```
    <class 'geopandas.geodataframe.GeoDataFrame'>
    ```

    ```
       GEOID                           NAME     variable  estimate  moe                                           geometry
    0  06001     Alameda County, California  B01001_001   1682353  NaN  MULTIPOLYGON (((-122.34 37.79, -122.33 37.79,...
    1  06003      Alpine County, California  B01001_001      1235  143  POLYGON ((-120.07 38.70, -120.07 38.70, -120....
    2  06005      Amador County, California  B01001_001     41259  NaN  POLYGON ((-121.03 38.71, -121.02 38.71, -121....
    3  06007       Butte County, California  B01001_001    211632  NaN  POLYGON ((-122.05 39.82, -122.05 39.82, -122....
    4  06009  Calaveras County, California  B01001_001     46221  NaN  POLYGON ((-120.99 38.23, -120.98 38.23, -120....
    ```

    !!! tip
        Notice the `geometry` column — that is what makes this a
        **GeoDataFrame** instead of a plain DataFrame. Each row carries its
        polygon boundary, ready for mapping or spatial analysis.

=== "get_decennial()"

    ```python
    import pypums

    gdf = pypums.get_decennial(
        geography="state",
        variables="P1_001N",
        year=2020,
        geometry=True,
    )
    print(gdf.head())
    ```

    ```
       GEOID       NAME  variable      value                                           geometry
    0     01    Alabama  P1_001N    5024279  MULTIPOLYGON (((-88.47 30.22, -88.47 30.22,...
    1     02     Alaska  P1_001N     733391  MULTIPOLYGON ((-179.17 51.27, -179.17 51.27,...
    2     04    Arizona  P1_001N    7151502  POLYGON ((-114.82 32.51, -114.82 32.51, -114....
    3     05   Arkansas  P1_001N    3011524  POLYGON ((-94.62 36.50, -94.62 36.50, -94.48...
    4     06  California  P1_001N   39538223  MULTIPOLYGON ((-122.42 37.87, -122.42 37.87,...
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
       GEOID       NAME     variable      value                                           geometry
    0     01    Alabama  POP_2023    5108468  MULTIPOLYGON (((-88.47 30.22, -88.47 30.22,...
    1     02     Alaska  POP_2023     733406  MULTIPOLYGON ((-179.17 51.27, -179.17 51.27,...
    2     04    Arizona  POP_2023    7303398  POLYGON ((-114.82 32.51, -114.82 32.51, -114....
    3     05   Arkansas  POP_2023    3067732  POLYGON ((-94.62 36.50, -94.62 36.50, -94.48...
    4     06  California  POP_2023   38965193  MULTIPOLYGON ((-122.42 37.87, -122.42 37.87,...
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
       GEOID1  GEOID2                          NAME1                       NAME2  MOVEDIN  MOVEDOUT   AGE_MEDIAN                                         geometry
    0   36001   36003  Albany County, New York     Allegany County, New York      45        38        31.5  POLYGON ((-74.26 42.41, -74.26 42.41, -74.08...
    1   36001   36005  Albany County, New York        Bronx County, New York     120        95        27.0  POLYGON ((-74.26 42.41, -74.26 42.41, -74.08...
    2   36001   36007  Albany County, New York       Broome County, New York      89        72        29.0  POLYGON ((-74.26 42.41, -74.26 42.41, -74.08...
    3   36001   36009  Albany County, New York   Cattaraugus County, New York      12        18        34.0  POLYGON ((-74.26 42.41, -74.26 42.41, -74.08...
    4   36001   36011  Albany County, New York      Cayuga County, New York       32        28        33.0  POLYGON ((-74.26 42.41, -74.26 42.41, -74.08...
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
                {"id": 53, "value": 7614893, "name": "Washington"},
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
          "legend": {"title": "Population", "format": ","}
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
native CRS of the Census Bureau's TIGER/Line files. You can verify this on any
`GeoDataFrame`:

```python
print(gdf.crs)
```

```
EPSG:4269
```

```python
print(gdf.crs.name)
```

```
NAD83
```

### Reprojecting

You will often need to reproject to a different CRS depending on your use case.

=== "Web mapping (EPSG:4326)"

    Most web mapping libraries (Leaflet, Mapbox, Folium) expect **WGS 84**:

    ```python
    gdf_wgs84 = gdf.to_crs(epsg=4326)
    print(gdf_wgs84.crs)
    ```

    ```
    EPSG:4326
    ```

=== "Local analysis (projected CRS)"

    For area or distance calculations, use a projected CRS appropriate to your
    region. For example, **EPSG:2229** (NAD83 / California zone 5, in feet):

    ```python
    gdf_projected = gdf.to_crs(epsg=2229)
    area_sq_ft = gdf_projected.geometry.area
    print(area_sq_ft.head())
    ```

    ```
    0    4.983527e+11
    1    2.065981e+10
    2    1.694534e+10
    3    4.622175e+10
    4    2.854179e+10
    dtype: float64
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

```
       GEOID                                         NAME     variable  estimate      moe
0  17031010100  Census Tract 101, Cook County, Illinois  B19013_001     62344    12038
1  17031010201  Census Tract 102.01, Cook County, Illinois  B19013_001     78250    11587
2  17031010202  Census Tract 102.02, Cook County, Illinois  B19013_001     46985    10341
3  17031010300  Census Tract 103, Cook County, Illinois  B19013_001     38750     8204
4  17031010400  Census Tract 104, Cook County, Illinois  B19013_001     31563     6427
```

```python
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

```
<class 'geopandas.geodataframe.GeoDataFrame'>
['GEOID', 'NAME', 'variable', 'estimate', 'moe', 'geometry']
```

```
       GEOID                                              NAME     variable  estimate      moe                                           geometry
0  17031010100  Census Tract 101, Cook County, Illinois  B19013_001     62344    12038  POLYGON ((-87.63 41.90, -87.63 41.90, -87.62...
1  17031010201  Census Tract 102.01, Cook County, Illinois  B19013_001     78250    11587  POLYGON ((-87.63 41.91, -87.63 41.91, -87.62...
2  17031010202  Census Tract 102.02, Cook County, Illinois  B19013_001     46985    10341  POLYGON ((-87.64 41.91, -87.64 41.91, -87.63...
3  17031010300  Census Tract 103, Cook County, Illinois  B19013_001     38750     8204  POLYGON ((-87.64 41.92, -87.64 41.92, -87.63...
4  17031010400  Census Tract 104, Cook County, Illinois  B19013_001     31563     6427  POLYGON ((-87.65 41.92, -87.65 41.91, -87.64...
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
          "legend": {"title": "Median Household Income"}
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
print(gdf.head())
```

```
       GEOID                                              NAME  B03002_003E  B03002_003M  B03002_004E  B03002_004M  B03002_006E  B03002_006M  B03002_012E  B03002_012M                                           geometry
0  17031010100  Census Tract 101, Cook County, Illinois         2841          312          152           78          125           59          401          148  POLYGON ((-87.63 41.90, -87.63 41.90, -87.62...
1  17031010201  Census Tract 102.01, Cook County, Illinois      3512          398           98           56          210           84          285          121  POLYGON ((-87.63 41.91, -87.63 41.91, -87.62...
2  17031010202  Census Tract 102.02, Cook County, Illinois      1245          215          412          132           89           47          892          204  POLYGON ((-87.64 41.91, -87.64 41.91, -87.63...
3  17031010300  Census Tract 103, Cook County, Illinois          523          148         2105          301           45           28         1230          189  POLYGON ((-87.64 41.92, -87.64 41.92, -87.63...
4  17031010400  Census Tract 104, Cook County, Illinois          312          102         2890          345           31           22          985          167  POLYGON ((-87.65 41.92, -87.65 41.91, -87.64...
```

```python
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
print(dots.head(10))
```

```
                     geometry    value
0  POINT (-87.6312 41.9045)    White
1  POINT (-87.6287 41.9023)    White
2  POINT (-87.6298 41.9051)    White
3  POINT (-87.6305 41.9038)    White
4  POINT (-87.6291 41.9029)    White
5  POINT (-87.6245 41.9061)    Black
6  POINT (-87.6267 41.9044)    Black
7  POINT (-87.6341 41.9073)    Asian
8  POINT (-87.6278 41.9055)  Hispanic
9  POINT (-87.6319 41.9082)  Hispanic
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
).project("albersUsa").properties(width=600, height=600)
chart
```

!!! example "Interactive preview — dot density map of Cook County, IL (sample data)"

    Each dot represents 100 people. The spatial distribution of dots reveals
    neighborhood-level patterns of racial and ethnic composition.

    ```vegalite
    {
      "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
      "width": 500,
      "height": 550,
      "title": "Racial & Ethnic Dot Density — Cook County, IL (sample)",
      "data": {
        "values": [
          {"lon": -87.631, "lat": 41.904, "value": "White"},
          {"lon": -87.629, "lat": 41.902, "value": "White"},
          {"lon": -87.633, "lat": 41.910, "value": "White"},
          {"lon": -87.637, "lat": 41.913, "value": "White"},
          {"lon": -87.641, "lat": 41.918, "value": "White"},
          {"lon": -87.648, "lat": 41.923, "value": "White"},
          {"lon": -87.655, "lat": 41.931, "value": "White"},
          {"lon": -87.662, "lat": 41.939, "value": "White"},
          {"lon": -87.668, "lat": 41.946, "value": "White"},
          {"lon": -87.671, "lat": 41.951, "value": "White"},
          {"lon": -87.675, "lat": 41.958, "value": "White"},
          {"lon": -87.680, "lat": 41.965, "value": "White"},
          {"lon": -87.686, "lat": 41.972, "value": "White"},
          {"lon": -87.690, "lat": 41.978, "value": "White"},
          {"lon": -87.695, "lat": 41.985, "value": "White"},
          {"lon": -87.699, "lat": 41.992, "value": "White"},
          {"lon": -87.703, "lat": 41.997, "value": "White"},
          {"lon": -87.710, "lat": 42.005, "value": "White"},
          {"lon": -87.715, "lat": 42.012, "value": "White"},
          {"lon": -87.720, "lat": 42.018, "value": "White"},
          {"lon": -87.726, "lat": 42.025, "value": "White"},
          {"lon": -87.730, "lat": 42.033, "value": "White"},
          {"lon": -87.736, "lat": 42.041, "value": "White"},
          {"lon": -87.742, "lat": 42.048, "value": "White"},
          {"lon": -87.748, "lat": 42.055, "value": "White"},
          {"lon": -87.755, "lat": 42.063, "value": "White"},
          {"lon": -87.760, "lat": 42.070, "value": "White"},
          {"lon": -87.766, "lat": 42.078, "value": "White"},
          {"lon": -87.772, "lat": 42.085, "value": "White"},
          {"lon": -87.779, "lat": 42.092, "value": "White"},
          {"lon": -87.623, "lat": 41.780, "value": "Black"},
          {"lon": -87.618, "lat": 41.773, "value": "Black"},
          {"lon": -87.630, "lat": 41.768, "value": "Black"},
          {"lon": -87.615, "lat": 41.762, "value": "Black"},
          {"lon": -87.625, "lat": 41.755, "value": "Black"},
          {"lon": -87.635, "lat": 41.748, "value": "Black"},
          {"lon": -87.620, "lat": 41.741, "value": "Black"},
          {"lon": -87.612, "lat": 41.735, "value": "Black"},
          {"lon": -87.628, "lat": 41.728, "value": "Black"},
          {"lon": -87.640, "lat": 41.721, "value": "Black"},
          {"lon": -87.605, "lat": 41.715, "value": "Black"},
          {"lon": -87.622, "lat": 41.708, "value": "Black"},
          {"lon": -87.638, "lat": 41.698, "value": "Black"},
          {"lon": -87.610, "lat": 41.691, "value": "Black"},
          {"lon": -87.625, "lat": 41.685, "value": "Black"},
          {"lon": -87.632, "lat": 41.795, "value": "Black"},
          {"lon": -87.645, "lat": 41.790, "value": "Black"},
          {"lon": -87.650, "lat": 41.783, "value": "Black"},
          {"lon": -87.658, "lat": 41.776, "value": "Black"},
          {"lon": -87.660, "lat": 41.770, "value": "Black"},
          {"lon": -87.655, "lat": 41.765, "value": "Black"},
          {"lon": -87.649, "lat": 41.758, "value": "Black"},
          {"lon": -87.643, "lat": 41.752, "value": "Black"},
          {"lon": -87.637, "lat": 41.745, "value": "Black"},
          {"lon": -87.665, "lat": 41.738, "value": "Black"},
          {"lon": -87.670, "lat": 41.730, "value": "Black"},
          {"lon": -87.675, "lat": 41.722, "value": "Black"},
          {"lon": -87.680, "lat": 41.715, "value": "Black"},
          {"lon": -87.685, "lat": 41.708, "value": "Black"},
          {"lon": -87.690, "lat": 41.700, "value": "Black"},
          {"lon": -87.635, "lat": 41.852, "value": "Asian"},
          {"lon": -87.632, "lat": 41.849, "value": "Asian"},
          {"lon": -87.630, "lat": 41.846, "value": "Asian"},
          {"lon": -87.628, "lat": 41.843, "value": "Asian"},
          {"lon": -87.695, "lat": 41.998, "value": "Asian"},
          {"lon": -87.700, "lat": 42.003, "value": "Asian"},
          {"lon": -87.705, "lat": 42.008, "value": "Asian"},
          {"lon": -87.710, "lat": 42.013, "value": "Asian"},
          {"lon": -87.715, "lat": 42.018, "value": "Asian"},
          {"lon": -87.720, "lat": 42.023, "value": "Asian"},
          {"lon": -87.725, "lat": 42.028, "value": "Asian"},
          {"lon": -87.633, "lat": 41.870, "value": "Asian"},
          {"lon": -87.637, "lat": 41.875, "value": "Asian"},
          {"lon": -87.641, "lat": 41.880, "value": "Asian"},
          {"lon": -87.645, "lat": 41.885, "value": "Asian"},
          {"lon": -87.680, "lat": 41.975, "value": "Asian"},
          {"lon": -87.683, "lat": 41.980, "value": "Asian"},
          {"lon": -87.686, "lat": 41.985, "value": "Asian"},
          {"lon": -87.689, "lat": 41.990, "value": "Asian"},
          {"lon": -87.692, "lat": 41.995, "value": "Asian"},
          {"lon": -87.660, "lat": 41.950, "value": "Asian"},
          {"lon": -87.720, "lat": 41.860, "value": "Hispanic"},
          {"lon": -87.725, "lat": 41.855, "value": "Hispanic"},
          {"lon": -87.730, "lat": 41.850, "value": "Hispanic"},
          {"lon": -87.735, "lat": 41.845, "value": "Hispanic"},
          {"lon": -87.715, "lat": 41.840, "value": "Hispanic"},
          {"lon": -87.710, "lat": 41.835, "value": "Hispanic"},
          {"lon": -87.705, "lat": 41.830, "value": "Hispanic"},
          {"lon": -87.700, "lat": 41.825, "value": "Hispanic"},
          {"lon": -87.695, "lat": 41.820, "value": "Hispanic"},
          {"lon": -87.690, "lat": 41.815, "value": "Hispanic"},
          {"lon": -87.685, "lat": 41.875, "value": "Hispanic"},
          {"lon": -87.680, "lat": 41.870, "value": "Hispanic"},
          {"lon": -87.675, "lat": 41.865, "value": "Hispanic"},
          {"lon": -87.670, "lat": 41.860, "value": "Hispanic"},
          {"lon": -87.665, "lat": 41.855, "value": "Hispanic"},
          {"lon": -87.660, "lat": 41.850, "value": "Hispanic"},
          {"lon": -87.740, "lat": 41.870, "value": "Hispanic"},
          {"lon": -87.745, "lat": 41.865, "value": "Hispanic"},
          {"lon": -87.750, "lat": 41.860, "value": "Hispanic"},
          {"lon": -87.755, "lat": 41.855, "value": "Hispanic"},
          {"lon": -87.758, "lat": 41.880, "value": "Hispanic"},
          {"lon": -87.762, "lat": 41.885, "value": "Hispanic"},
          {"lon": -87.765, "lat": 41.890, "value": "Hispanic"},
          {"lon": -87.768, "lat": 41.895, "value": "Hispanic"},
          {"lon": -87.770, "lat": 41.900, "value": "Hispanic"},
          {"lon": -87.773, "lat": 41.905, "value": "Hispanic"},
          {"lon": -87.776, "lat": 41.910, "value": "Hispanic"},
          {"lon": -87.778, "lat": 41.915, "value": "Hispanic"},
          {"lon": -87.780, "lat": 41.920, "value": "Hispanic"},
          {"lon": -87.783, "lat": 41.925, "value": "Hispanic"}
        ]
      },
      "mark": {"type": "circle", "size": 8, "opacity": 0.7},
      "encoding": {
        "longitude": {"field": "lon", "type": "quantitative"},
        "latitude": {"field": "lat", "type": "quantitative"},
        "color": {
          "field": "value",
          "type": "nominal",
          "scale": {
            "domain": ["White", "Black", "Asian", "Hispanic"],
            "range": ["#1f77b4", "#2ca02c", "#d62728", "#ff7f0e"]
          },
          "legend": {"title": "Group"}
        },
        "tooltip": [{"field": "value", "type": "nominal", "title": "Group"}]
      },
      "projection": {
        "type": "mercator",
        "scale": 30000,
        "center": [-87.7, 41.85]
      }
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

        ```python
        df = pd.DataFrame(gdf.drop(columns="geometry"))
        print(type(df))
        ```

        ```
        <class 'pandas.core.frame.DataFrame'>
        ```

    - **Save to file** and work from disk instead of re-downloading:

        ```python
        gdf.to_parquet("tracts_il_2023.parquet")
        # Later:
        gdf = gpd.read_parquet("tracts_il_2023.parquet")
        print(gdf.shape)
        ```

        ```
        (1318, 6)
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
