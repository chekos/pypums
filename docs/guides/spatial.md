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
       GEOID                                           geometry                          NAME    variable  estimate        moe
    0  06001  POLYGON ((-122.34225 37.80556, -122.33385 37.8...    Alameda County, California  B01001_001   1651949 -555555555
    1  06003  POLYGON ((-120.07239 38.70277, -120.06762 38.7...     Alpine County, California  B01001_001      1695        234
    2  06005  POLYGON ((-121.02741 38.50354, -121.02747 38.5...     Amador County, California  B01001_001     41029 -555555555
    3  06007  POLYGON ((-122.06874 39.84222, -122.06694 39.8...      Butte County, California  B01001_001    209470 -555555555
    4  06009  POLYGON ((-120.9936 38.22558, -120.99161 38.22...  Calaveras County, California  B01001_001     45995 -555555555
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
         GEOID                                        NAME    variable  estimate    moe
0  17031010100     Census Tract 101; Cook County; Illinois  B19013_001     69460  21834
1  17031010201  Census Tract 102.01; Cook County; Illinois  B19013_001     49639  24247
2  17031010202  Census Tract 102.02; Cook County; Illinois  B19013_001     55119  15618
3  17031010300     Census Tract 103; Cook County; Illinois  B19013_001     65871  14559
4  17031010400     Census Tract 104; Cook County; Illinois  B19013_001     49017   8306
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
['GEOID', 'geometry', 'NAME', 'variable', 'estimate', 'moe']
```

```
         GEOID                                           geometry                                        NAME  \
0  17031010100  POLYGON ((-87.6772 42.02294, -87.67188 42.0229...     Census Tract 101; Cook County; Illinois
1  17031010201  POLYGON ((-87.68465 42.01948, -87.68045 42.019...  Census Tract 102.01; Cook County; Illinois
2  17031010202  POLYGON ((-87.67686 42.01941, -87.67331 42.019...  Census Tract 102.02; Cook County; Illinois
3  17031010300  POLYGON ((-87.67133 42.01937, -87.6695 42.0193...     Census Tract 103; Cook County; Illinois
4  17031010400  POLYGON ((-87.66345 42.01283, -87.66133 42.012...     Census Tract 104; Cook County; Illinois

     variable  estimate    moe
0  B19013_001     69460  21834
1  B19013_001     49639  24247
2  B19013_001     55119  15618
3  B19013_001     65871  14559
4  B19013_001     49017   8306
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

```python
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

```
         GEOID                                           geometry                                           NAME  \
0  06001400100  POLYGON ((-122.24691 37.88536, -122.24197 37.8...  Census Tract 4001; Alameda County; California
1  06001400200  POLYGON ((-122.25742 37.8431, -122.2562 37.844...  Census Tract 4002; Alameda County; California
2  06001400300  POLYGON ((-122.26534 37.83846, -122.26459 37.8...  Census Tract 4003; Alameda County; California
3  06001400400  POLYGON ((-122.2618 37.84179, -122.2613 37.845...  Census Tract 4004; Alameda County; California
4  06001400500  POLYGON ((-122.26941 37.84811, -122.26896 37.8...  Census Tract 4005; Alameda County; California

   B03002_003E  B03002_004E  B03002_006E  B03002_012E  B03002_003M  B03002_004M  B03002_006M  B03002_012M
0         2107          137          462          200          428          113          106          107
1         1408           43          256          196          195           52          115           95
2         3365          524          609          497          471          137          197          305
3         2645          433          422          604          566          258          106          280
4         1696          911          306          557          389          636          113          236
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
                      geometry  value
0  POINT (-122.22019 37.86251)  White
1  POINT (-122.22283 37.87751)  White
2  POINT (-122.24249 37.87414)  White
3  POINT (-122.23136 37.87632)  White
4  POINT (-122.22468 37.86307)  White
5   POINT (-122.2316 37.85667)  White
6   POINT (-122.22776 37.8668)  White
7   POINT (-122.2251 37.86543)  White
8   POINT (-122.23612 37.8662)  White
9  POINT (-122.21817 37.87009)  White
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

!!! example "Interactive preview — dot density map of Alameda County, CA (sample data)"

    Each dot represents 500 people. The spatial distribution of dots reveals
    neighborhood-level patterns of racial and ethnic composition.

    ```vegalite
    {
      "layer": [
        {
          "data": {
            "values": [
              {
                "id": "0",
                "type": "Feature",
                "properties": {},
                "geometry": {
                  "type": "Polygon",
                  "coordinates": [
                    [
                      [
                        -122.279401,
                        37.768134
                      ],
                      [
                        -122.289012,
                        37.764608
                      ],
                      [
                        -122.328024583922,
                        37.7813728248168
                      ],
                      [
                        -122.342253,
                        37.805558
                      ],
                      [
                        -122.317296,
                        37.816261
                      ],
                      [
                        -122.330369,
                        37.82058
                      ],
                      [
                        -122.296618,
                        37.828465
                      ],
                      [
                        -122.298044,
                        37.836349
                      ],
                      [
                        -122.315913,
                        37.836812
                      ],
                      [
                        -122.314195,
                        37.842311
                      ],
                      [
                        -122.299233,
                        37.840479
                      ],
                      [
                        -122.301372,
                        37.855493
                      ],
                      [
                        -122.308352,
                        37.862934
                      ],
                      [
                        -122.316944,
                        37.858809
                      ],
                      [
                        -122.325193,
                        37.874276
                      ],
                      [
                        -122.308502,
                        37.87088
                      ],
                      [
                        -122.326912,
                        37.892492
                      ],
                      [
                        -122.311101,
                        37.89043
                      ],
                      [
                        -122.313147550967,
                        37.8972880379388
                      ],
                      [
                        -122.27108,
                        37.905824
                      ],
                      [
                        -122.241971,
                        37.881927
                      ],
                      [
                        -122.22362,
                        37.878566
                      ],
                      [
                        -122.208898,
                        37.851941
                      ],
                      [
                        -122.185116,
                        37.837353
                      ],
                      [
                        -122.185577,
                        37.820726
                      ],
                      [
                        -122.166873,
                        37.813424
                      ],
                      [
                        -122.157392,
                        37.817952
                      ],
                      [
                        -122.140317,
                        37.804701
                      ],
                      [
                        -122.045473,
                        37.798126
                      ],
                      [
                        -121.997411,
                        37.76336
                      ],
                      [
                        -122.011771,
                        37.747428
                      ],
                      [
                        -121.96004,
                        37.718531
                      ],
                      [
                        -121.556997,
                        37.816488
                      ],
                      [
                        -121.556655,
                        37.542732
                      ],
                      [
                        -121.541833,
                        37.530215
                      ],
                      [
                        -121.501475,
                        37.525003
                      ],
                      [
                        -121.496017,
                        37.504938
                      ],
                      [
                        -121.482065,
                        37.501439
                      ],
                      [
                        -121.47106,
                        37.483317
                      ],
                      [
                        -121.865267,
                        37.484637
                      ],
                      [
                        -121.925041,
                        37.454186
                      ],
                      [
                        -121.944914,
                        37.469163
                      ],
                      [
                        -121.951921,
                        37.461461
                      ],
                      [
                        -122.040872722043,
                        37.4628633674882
                      ],
                      [
                        -122.053431,
                        37.473321
                      ],
                      [
                        -122.055541,
                        37.49523
                      ],
                      [
                        -122.10942,
                        37.500254
                      ],
                      [
                        -122.111998,
                        37.528851
                      ],
                      [
                        -122.147014,
                        37.588411
                      ],
                      [
                        -122.152993,
                        37.641923
                      ],
                      [
                        -122.167587,
                        37.677178
                      ],
                      [
                        -122.204161,
                        37.711603
                      ],
                      [
                        -122.214744,
                        37.699247
                      ],
                      [
                        -122.252172,
                        37.724952
                      ],
                      [
                        -122.261679,
                        37.743373
                      ],
                      [
                        -122.243947,
                        37.751779
                      ],
                      [
                        -122.279401,
                        37.768134
                      ]
                    ]
                  ]
                },
                "bbox": [
                  -122.342253,
                  37.454186,
                  -121.47106,
                  37.905824
                ]
              }
            ]
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
            "values": [
              {
                "lon": -122.2202,
                "lat": 37.8631,
                "value": "White"
              },
              {
                "lon": -122.2437,
                "lat": 37.8657,
                "value": "White"
              },
              {
                "lon": -122.2132,
                "lat": 37.858,
                "value": "White"
              },
              {
                "lon": -122.2206,
                "lat": 37.8696,
                "value": "White"
              },
              {
                "lon": -122.2458,
                "lat": 37.8495,
                "value": "White"
              },
              {
                "lon": -122.2548,
                "lat": 37.8444,
                "value": "White"
              },
              {
                "lon": -122.2561,
                "lat": 37.8373,
                "value": "White"
              },
              {
                "lon": -122.2474,
                "lat": 37.8444,
                "value": "White"
              },
              {
                "lon": -122.248,
                "lat": 37.8454,
                "value": "White"
              },
              {
                "lon": -122.2571,
                "lat": 37.841,
                "value": "White"
              },
              {
                "lon": -122.251,
                "lat": 37.8375,
                "value": "White"
              },
              {
                "lon": -122.2553,
                "lat": 37.8403,
                "value": "White"
              },
              {
                "lon": -122.262,
                "lat": 37.8399,
                "value": "Black"
              },
              {
                "lon": -122.2598,
                "lat": 37.8388,
                "value": "Asian"
              },
              {
                "lon": -122.2557,
                "lat": 37.8529,
                "value": "White"
              },
              {
                "lon": -122.2579,
                "lat": 37.8457,
                "value": "White"
              },
              {
                "lon": -122.2605,
                "lat": 37.8474,
                "value": "White"
              },
              {
                "lon": -122.2572,
                "lat": 37.8517,
                "value": "White"
              },
              {
                "lon": -122.2572,
                "lat": 37.8525,
                "value": "White"
              },
              {
                "lon": -122.2608,
                "lat": 37.845,
                "value": "Hispanic"
              },
              {
                "lon": -122.2612,
                "lat": 37.8522,
                "value": "White"
              },
              {
                "lon": -122.2612,
                "lat": 37.8462,
                "value": "White"
              },
              {
                "lon": -122.2646,
                "lat": 37.8452,
                "value": "White"
              },
              {
                "lon": -122.2623,
                "lat": 37.8501,
                "value": "Black"
              },
              {
                "lon": -122.2666,
                "lat": 37.8454,
                "value": "Hispanic"
              },
              {
                "lon": -122.2625,
                "lat": 37.8424,
                "value": "White"
              },
              {
                "lon": -122.266,
                "lat": 37.8379,
                "value": "Black"
              },
              {
                "lon": -122.2773,
                "lat": 37.8458,
                "value": "White"
              },
              {
                "lon": -122.2757,
                "lat": 37.837,
                "value": "White"
              },
              {
                "lon": -122.275,
                "lat": 37.8375,
                "value": "White"
              },
              {
                "lon": -122.2714,
                "lat": 37.846,
                "value": "White"
              },
              {
                "lon": -122.2691,
                "lat": 37.8418,
                "value": "Black"
              },
              {
                "lon": -122.2763,
                "lat": 37.8411,
                "value": "Black"
              },
              {
                "lon": -122.2831,
                "lat": 37.8419,
                "value": "White"
              },
              {
                "lon": -122.2849,
                "lat": 37.8472,
                "value": "White"
              },
              {
                "lon": -122.2811,
                "lat": 37.8464,
                "value": "White"
              },
              {
                "lon": -122.2825,
                "lat": 37.8476,
                "value": "White"
              },
              {
                "lon": -122.2871,
                "lat": 37.8464,
                "value": "Asian"
              },
              {
                "lon": -122.2838,
                "lat": 37.8414,
                "value": "Hispanic"
              },
              {
                "lon": -122.2801,
                "lat": 37.841,
                "value": "White"
              },
              {
                "lon": -122.2779,
                "lat": 37.8373,
                "value": "Black"
              },
              {
                "lon": -122.2796,
                "lat": 37.837,
                "value": "Hispanic"
              },
              {
                "lon": -122.2691,
                "lat": 37.8338,
                "value": "White"
              },
              {
                "lon": -122.2762,
                "lat": 37.8267,
                "value": "White"
              },
              {
                "lon": -122.2694,
                "lat": 37.8269,
                "value": "White"
              },
              {
                "lon": -122.2712,
                "lat": 37.8298,
                "value": "Black"
              },
              {
                "lon": -122.2768,
                "lat": 37.8307,
                "value": "Black"
              },
              {
                "lon": -122.2748,
                "lat": 37.8262,
                "value": "Black"
              },
              {
                "lon": -122.2711,
                "lat": 37.8281,
                "value": "Black"
              },
              {
                "lon": -122.2734,
                "lat": 37.8337,
                "value": "Hispanic"
              },
              {
                "lon": -122.2605,
                "lat": 37.8355,
                "value": "White"
              },
              {
                "lon": -122.264,
                "lat": 37.8272,
                "value": "White"
              },
              {
                "lon": -122.2639,
                "lat": 37.828,
                "value": "White"
              },
              {
                "lon": -122.2657,
                "lat": 37.8277,
                "value": "White"
              },
              {
                "lon": -122.2608,
                "lat": 37.8332,
                "value": "Black"
              },
              {
                "lon": -122.2652,
                "lat": 37.8335,
                "value": "Black"
              },
              {
                "lon": -122.2635,
                "lat": 37.8253,
                "value": "Asian"
              },
              {
                "lon": -122.2609,
                "lat": 37.8302,
                "value": "Hispanic"
              },
              {
                "lon": -122.2573,
                "lat": 37.8359,
                "value": "White"
              },
              {
                "lon": -122.257,
                "lat": 37.8289,
                "value": "White"
              },
              {
                "lon": -122.2611,
                "lat": 37.8269,
                "value": "White"
              },
              {
                "lon": -122.267,
                "lat": 37.8187,
                "value": "White"
              },
              {
                "lon": -122.2632,
                "lat": 37.82,
                "value": "White"
              },
              {
                "lon": -122.2668,
                "lat": 37.8222,
                "value": "Black"
              },
              {
                "lon": -122.2672,
                "lat": 37.8164,
                "value": "Black"
              },
              {
                "lon": -122.2627,
                "lat": 37.8231,
                "value": "Asian"
              },
              {
                "lon": -122.2697,
                "lat": 37.8209,
                "value": "White"
              },
              {
                "lon": -122.2752,
                "lat": 37.8211,
                "value": "White"
              },
              {
                "lon": -122.2766,
                "lat": 37.8254,
                "value": "Black"
              },
              {
                "lon": -122.2741,
                "lat": 37.8173,
                "value": "Black"
              },
              {
                "lon": -122.2752,
                "lat": 37.8202,
                "value": "Black"
              },
              {
                "lon": -122.2754,
                "lat": 37.8223,
                "value": "Asian"
              },
              {
                "lon": -122.2735,
                "lat": 37.8171,
                "value": "Hispanic"
              },
              {
                "lon": -122.2743,
                "lat": 37.8134,
                "value": "Hispanic"
              },
              {
                "lon": -122.2862,
                "lat": 37.8212,
                "value": "White"
              },
              {
                "lon": -122.279,
                "lat": 37.821,
                "value": "Black"
              },
              {
                "lon": -122.2799,
                "lat": 37.8264,
                "value": "Black"
              },
              {
                "lon": -122.2836,
                "lat": 37.8208,
                "value": "Hispanic"
              },
              {
                "lon": -122.2804,
                "lat": 37.8177,
                "value": "White"
              },
              {
                "lon": -122.2804,
                "lat": 37.8174,
                "value": "Black"
              },
              {
                "lon": -122.2773,
                "lat": 37.8145,
                "value": "Hispanic"
              },
              {
                "lon": -122.2937,
                "lat": 37.825,
                "value": "White"
              },
              {
                "lon": -122.3022,
                "lat": 37.8161,
                "value": "White"
              },
              {
                "lon": -122.3101,
                "lat": 37.8152,
                "value": "Black"
              },
              {
                "lon": -122.3072,
                "lat": 37.8255,
                "value": "Asian"
              },
              {
                "lon": -122.2999,
                "lat": 37.8168,
                "value": "Hispanic"
              },
              {
                "lon": -122.3002,
                "lat": 37.8099,
                "value": "Black"
              },
              {
                "lon": -122.2979,
                "lat": 37.8079,
                "value": "Hispanic"
              },
              {
                "lon": -122.2924,
                "lat": 37.8131,
                "value": "White"
              },
              {
                "lon": -122.2952,
                "lat": 37.807,
                "value": "Black"
              },
              {
                "lon": -122.2795,
                "lat": 37.8124,
                "value": "Black"
              },
              {
                "lon": -122.2806,
                "lat": 37.8136,
                "value": "Black"
              },
              {
                "lon": -122.2822,
                "lat": 37.8149,
                "value": "Black"
              },
              {
                "lon": -122.2835,
                "lat": 37.8027,
                "value": "Black"
              },
              {
                "lon": -122.2788,
                "lat": 37.8052,
                "value": "Black"
              },
              {
                "lon": -122.2791,
                "lat": 37.8082,
                "value": "Black"
              },
              {
                "lon": -122.2717,
                "lat": 37.8079,
                "value": "White"
              },
              {
                "lon": -122.2728,
                "lat": 37.8105,
                "value": "Black"
              },
              {
                "lon": -122.2701,
                "lat": 37.8071,
                "value": "Black"
              },
              {
                "lon": -122.2715,
                "lat": 37.8056,
                "value": "Asian"
              },
              {
                "lon": -122.2729,
                "lat": 37.8089,
                "value": "Black"
              },
              {
                "lon": -122.2678,
                "lat": 37.8045,
                "value": "Asian"
              },
              {
                "lon": -122.2702,
                "lat": 37.8025,
                "value": "Asian"
              },
              {
                "lon": -122.2703,
                "lat": 37.803,
                "value": "Asian"
              },
              {
                "lon": -122.2679,
                "lat": 37.8009,
                "value": "Asian"
              },
              {
                "lon": -122.2689,
                "lat": 37.7995,
                "value": "Asian"
              },
              {
                "lon": -122.2778,
                "lat": 37.8029,
                "value": "White"
              },
              {
                "lon": -122.2769,
                "lat": 37.7992,
                "value": "Black"
              },
              {
                "lon": -122.2762,
                "lat": 37.8013,
                "value": "Asian"
              },
              {
                "lon": -122.2678,
                "lat": 37.7979,
                "value": "Asian"
              },
              {
                "lon": -122.2675,
                "lat": 37.799,
                "value": "Asian"
              },
              {
                "lon": -122.2711,
                "lat": 37.7926,
                "value": "White"
              },
              {
                "lon": -122.2631,
                "lat": 37.7947,
                "value": "White"
              },
              {
                "lon": -122.2674,
                "lat": 37.7938,
                "value": "Asian"
              },
              {
                "lon": -122.2576,
                "lat": 37.8019,
                "value": "White"
              },
              {
                "lon": -122.2562,
                "lat": 37.8021,
                "value": "White"
              },
              {
                "lon": -122.2554,
                "lat": 37.8034,
                "value": "Asian"
              },
              {
                "lon": -122.2575,
                "lat": 37.8182,
                "value": "White"
              },
              {
                "lon": -122.2643,
                "lat": 37.8127,
                "value": "White"
              },
              {
                "lon": -122.2575,
                "lat": 37.8236,
                "value": "White"
              },
              {
                "lon": -122.2597,
                "lat": 37.8169,
                "value": "Black"
              },
              {
                "lon": -122.2644,
                "lat": 37.8124,
                "value": "Asian"
              },
              {
                "lon": -122.2626,
                "lat": 37.8177,
                "value": "Asian"
              },
              {
                "lon": -122.2582,
                "lat": 37.818,
                "value": "Asian"
              },
              {
                "lon": -122.2566,
                "lat": 37.8167,
                "value": "White"
              },
              {
                "lon": -122.2516,
                "lat": 37.8116,
                "value": "White"
              },
              {
                "lon": -122.2549,
                "lat": 37.8158,
                "value": "White"
              },
              {
                "lon": -122.2534,
                "lat": 37.8128,
                "value": "White"
              },
              {
                "lon": -122.2557,
                "lat": 37.8131,
                "value": "Black"
              },
              {
                "lon": -122.2531,
                "lat": 37.8116,
                "value": "Black"
              },
              {
                "lon": -122.2563,
                "lat": 37.8142,
                "value": "Asian"
              },
              {
                "lon": -122.2522,
                "lat": 37.8153,
                "value": "Hispanic"
              },
              {
                "lon": -122.2562,
                "lat": 37.8099,
                "value": "White"
              },
              {
                "lon": -122.2606,
                "lat": 37.8108,
                "value": "White"
              },
              {
                "lon": -122.256,
                "lat": 37.8102,
                "value": "Black"
              },
              {
                "lon": -122.261,
                "lat": 37.8112,
                "value": "Asian"
              },
              {
                "lon": -122.2489,
                "lat": 37.8087,
                "value": "White"
              },
              {
                "lon": -122.2552,
                "lat": 37.8088,
                "value": "White"
              },
              {
                "lon": -122.2459,
                "lat": 37.8127,
                "value": "White"
              },
              {
                "lon": -122.238,
                "lat": 37.8156,
                "value": "White"
              },
              {
                "lon": -122.2356,
                "lat": 37.8169,
                "value": "White"
              },
              {
                "lon": -122.2451,
                "lat": 37.811,
                "value": "White"
              },
              {
                "lon": -122.2362,
                "lat": 37.8171,
                "value": "Black"
              },
              {
                "lon": -122.2455,
                "lat": 37.8194,
                "value": "White"
              },
              {
                "lon": -122.248,
                "lat": 37.8204,
                "value": "White"
              },
              {
                "lon": -122.2494,
                "lat": 37.8145,
                "value": "White"
              },
              {
                "lon": -122.25,
                "lat": 37.8176,
                "value": "White"
              },
              {
                "lon": -122.2458,
                "lat": 37.8181,
                "value": "White"
              },
              {
                "lon": -122.2524,
                "lat": 37.8212,
                "value": "White"
              },
              {
                "lon": -122.2581,
                "lat": 37.8254,
                "value": "White"
              },
              {
                "lon": -122.2548,
                "lat": 37.8266,
                "value": "White"
              },
              {
                "lon": -122.256,
                "lat": 37.8245,
                "value": "Hispanic"
              },
              {
                "lon": -122.2519,
                "lat": 37.8311,
                "value": "White"
              },
              {
                "lon": -122.2535,
                "lat": 37.8315,
                "value": "White"
              },
              {
                "lon": -122.2552,
                "lat": 37.83,
                "value": "White"
              },
              {
                "lon": -122.2545,
                "lat": 37.8291,
                "value": "White"
              },
              {
                "lon": -122.2552,
                "lat": 37.8275,
                "value": "White"
              },
              {
                "lon": -122.2495,
                "lat": 37.825,
                "value": "White"
              },
              {
                "lon": -122.2309,
                "lat": 37.8329,
                "value": "White"
              },
              {
                "lon": -122.2304,
                "lat": 37.8357,
                "value": "White"
              },
              {
                "lon": -122.2279,
                "lat": 37.8331,
                "value": "White"
              },
              {
                "lon": -122.2286,
                "lat": 37.8407,
                "value": "White"
              },
              {
                "lon": -122.238,
                "lat": 37.852,
                "value": "White"
              },
              {
                "lon": -122.2371,
                "lat": 37.8441,
                "value": "White"
              },
              {
                "lon": -122.2489,
                "lat": 37.8386,
                "value": "White"
              },
              {
                "lon": -122.2383,
                "lat": 37.8438,
                "value": "White"
              },
              {
                "lon": -122.238,
                "lat": 37.8484,
                "value": "White"
              },
              {
                "lon": -122.2272,
                "lat": 37.8457,
                "value": "White"
              },
              {
                "lon": -122.2207,
                "lat": 37.8377,
                "value": "White"
              },
              {
                "lon": -122.2174,
                "lat": 37.8385,
                "value": "White"
              },
              {
                "lon": -122.2109,
                "lat": 37.84,
                "value": "White"
              },
              {
                "lon": -122.213,
                "lat": 37.8471,
                "value": "White"
              },
              {
                "lon": -122.2014,
                "lat": 37.8474,
                "value": "White"
              },
              {
                "lon": -122.2139,
                "lat": 37.8378,
                "value": "Asian"
              },
              {
                "lon": -122.2176,
                "lat": 37.8472,
                "value": "Asian"
              },
              {
                "lon": -122.2169,
                "lat": 37.8281,
                "value": "White"
              },
              {
                "lon": -122.2232,
                "lat": 37.829,
                "value": "White"
              },
              {
                "lon": -122.2003,
                "lat": 37.8365,
                "value": "White"
              },
              {
                "lon": -122.2064,
                "lat": 37.8359,
                "value": "White"
              },
              {
                "lon": -122.2009,
                "lat": 37.8391,
                "value": "White"
              },
              {
                "lon": -122.2045,
                "lat": 37.8398,
                "value": "White"
              },
              {
                "lon": -122.2088,
                "lat": 37.8379,
                "value": "White"
              },
              {
                "lon": -122.2048,
                "lat": 37.8332,
                "value": "White"
              },
              {
                "lon": -122.1935,
                "lat": 37.8357,
                "value": "White"
              },
              {
                "lon": -122.2028,
                "lat": 37.8389,
                "value": "Asian"
              },
              {
                "lon": -122.2095,
                "lat": 37.8347,
                "value": "Asian"
              },
              {
                "lon": -122.1877,
                "lat": 37.8147,
                "value": "White"
              },
              {
                "lon": -122.1892,
                "lat": 37.8279,
                "value": "White"
              },
              {
                "lon": -122.1833,
                "lat": 37.8104,
                "value": "White"
              },
              {
                "lon": -122.1836,
                "lat": 37.8195,
                "value": "White"
              },
              {
                "lon": -122.1927,
                "lat": 37.8279,
                "value": "White"
              },
              {
                "lon": -122.1791,
                "lat": 37.8077,
                "value": "Asian"
              },
              {
                "lon": -122.2071,
                "lat": 37.8107,
                "value": "White"
              },
              {
                "lon": -122.2037,
                "lat": 37.8131,
                "value": "White"
              },
              {
                "lon": -122.2155,
                "lat": 37.805,
                "value": "White"
              },
              {
                "lon": -122.2133,
                "lat": 37.801,
                "value": "White"
              },
              {
                "lon": -122.2172,
                "lat": 37.7986,
                "value": "White"
              },
              {
                "lon": -122.2199,
                "lat": 37.8049,
                "value": "White"
              },
              {
                "lon": -122.2214,
                "lat": 37.8052,
                "value": "White"
              },
              {
                "lon": -122.2264,
                "lat": 37.8048,
                "value": "White"
              },
              {
                "lon": -122.2222,
                "lat": 37.8024,
                "value": "White"
              },
              {
                "lon": -122.2242,
                "lat": 37.8036,
                "value": "Asian"
              },
              {
                "lon": -122.2179,
                "lat": 37.8058,
                "value": "Hispanic"
              },
              {
                "lon": -122.2359,
                "lat": 37.806,
                "value": "White"
              },
              {
                "lon": -122.2437,
                "lat": 37.8109,
                "value": "White"
              },
              {
                "lon": -122.2184,
                "lat": 37.8097,
                "value": "White"
              },
              {
                "lon": -122.2225,
                "lat": 37.8109,
                "value": "White"
              },
              {
                "lon": -122.233,
                "lat": 37.8109,
                "value": "White"
              },
              {
                "lon": -122.2372,
                "lat": 37.8094,
                "value": "White"
              },
              {
                "lon": -122.2343,
                "lat": 37.8117,
                "value": "White"
              },
              {
                "lon": -122.2336,
                "lat": 37.8083,
                "value": "White"
              },
              {
                "lon": -122.2371,
                "lat": 37.8123,
                "value": "White"
              },
              {
                "lon": -122.2241,
                "lat": 37.8138,
                "value": "Asian"
              },
              {
                "lon": -122.2345,
                "lat": 37.8047,
                "value": "White"
              },
              {
                "lon": -122.2474,
                "lat": 37.805,
                "value": "White"
              },
              {
                "lon": -122.2445,
                "lat": 37.8036,
                "value": "Black"
              },
              {
                "lon": -122.2455,
                "lat": 37.8055,
                "value": "Asian"
              },
              {
                "lon": -122.2443,
                "lat": 37.804,
                "value": "Asian"
              },
              {
                "lon": -122.2462,
                "lat": 37.806,
                "value": "Asian"
              },
              {
                "lon": -122.2386,
                "lat": 37.8064,
                "value": "Hispanic"
              },
              {
                "lon": -122.2534,
                "lat": 37.8035,
                "value": "White"
              },
              {
                "lon": -122.2524,
                "lat": 37.8029,
                "value": "White"
              },
              {
                "lon": -122.2516,
                "lat": 37.8015,
                "value": "Black"
              },
              {
                "lon": -122.2558,
                "lat": 37.7997,
                "value": "White"
              },
              {
                "lon": -122.2527,
                "lat": 37.7969,
                "value": "Black"
              },
              {
                "lon": -122.2518,
                "lat": 37.798,
                "value": "Asian"
              },
              {
                "lon": -122.2464,
                "lat": 37.7973,
                "value": "White"
              },
              {
                "lon": -122.2486,
                "lat": 37.7979,
                "value": "Black"
              },
              {
                "lon": -122.2471,
                "lat": 37.7972,
                "value": "Asian"
              },
              {
                "lon": -122.253,
                "lat": 37.7952,
                "value": "Asian"
              },
              {
                "lon": -122.2491,
                "lat": 37.7988,
                "value": "Hispanic"
              },
              {
                "lon": -122.2445,
                "lat": 37.7958,
                "value": "White"
              },
              {
                "lon": -122.2484,
                "lat": 37.7927,
                "value": "Asian"
              },
              {
                "lon": -122.2471,
                "lat": 37.7935,
                "value": "Asian"
              },
              {
                "lon": -122.2445,
                "lat": 37.7928,
                "value": "Hispanic"
              },
              {
                "lon": -122.2472,
                "lat": 37.7991,
                "value": "White"
              },
              {
                "lon": -122.2434,
                "lat": 37.7985,
                "value": "Black"
              },
              {
                "lon": -122.2415,
                "lat": 37.7986,
                "value": "Asian"
              },
              {
                "lon": -122.2433,
                "lat": 37.8009,
                "value": "Asian"
              },
              {
                "lon": -122.2441,
                "lat": 37.8017,
                "value": "Hispanic"
              },
              {
                "lon": -122.2351,
                "lat": 37.8029,
                "value": "White"
              },
              {
                "lon": -122.2362,
                "lat": 37.8006,
                "value": "Asian"
              },
              {
                "lon": -122.238,
                "lat": 37.7999,
                "value": "Asian"
              },
              {
                "lon": -122.2362,
                "lat": 37.8029,
                "value": "Hispanic"
              },
              {
                "lon": -122.2261,
                "lat": 37.7991,
                "value": "White"
              },
              {
                "lon": -122.2259,
                "lat": 37.797,
                "value": "Black"
              },
              {
                "lon": -122.2297,
                "lat": 37.7958,
                "value": "Asian"
              },
              {
                "lon": -122.2265,
                "lat": 37.7963,
                "value": "Hispanic"
              },
              {
                "lon": -122.2318,
                "lat": 37.7986,
                "value": "Hispanic"
              },
              {
                "lon": -122.2351,
                "lat": 37.7974,
                "value": "Black"
              },
              {
                "lon": -122.2313,
                "lat": 37.7909,
                "value": "Asian"
              },
              {
                "lon": -122.234,
                "lat": 37.7953,
                "value": "Asian"
              },
              {
                "lon": -122.231,
                "lat": 37.7941,
                "value": "Asian"
              },
              {
                "lon": -122.237,
                "lat": 37.797,
                "value": "Hispanic"
              },
              {
                "lon": -122.2361,
                "lat": 37.7911,
                "value": "Black"
              },
              {
                "lon": -122.2381,
                "lat": 37.7854,
                "value": "Asian"
              },
              {
                "lon": -122.2342,
                "lat": 37.7874,
                "value": "Asian"
              },
              {
                "lon": -122.2331,
                "lat": 37.7868,
                "value": "Hispanic"
              },
              {
                "lon": -122.2367,
                "lat": 37.7872,
                "value": "Hispanic"
              },
              {
                "lon": -122.2366,
                "lat": 37.7906,
                "value": "Hispanic"
              },
              {
                "lon": -122.2423,
                "lat": 37.7919,
                "value": "Asian"
              },
              {
                "lon": -122.241,
                "lat": 37.7904,
                "value": "Asian"
              },
              {
                "lon": -122.2408,
                "lat": 37.7918,
                "value": "Hispanic"
              },
              {
                "lon": -122.256,
                "lat": 37.7907,
                "value": "White"
              },
              {
                "lon": -122.2633,
                "lat": 37.7869,
                "value": "Black"
              },
              {
                "lon": -122.2363,
                "lat": 37.7759,
                "value": "Asian"
              },
              {
                "lon": -122.2613,
                "lat": 37.7927,
                "value": "Asian"
              },
              {
                "lon": -122.2419,
                "lat": 37.7757,
                "value": "Asian"
              },
              {
                "lon": -122.2425,
                "lat": 37.7844,
                "value": "Hispanic"
              },
              {
                "lon": -122.2321,
                "lat": 37.7801,
                "value": "White"
              },
              {
                "lon": -122.2189,
                "lat": 37.7701,
                "value": "Asian"
              },
              {
                "lon": -122.2329,
                "lat": 37.779,
                "value": "Asian"
              },
              {
                "lon": -122.2274,
                "lat": 37.7694,
                "value": "Hispanic"
              },
              {
                "lon": -122.2251,
                "lat": 37.7689,
                "value": "Hispanic"
              },
              {
                "lon": -122.2353,
                "lat": 37.7779,
                "value": "Hispanic"
              },
              {
                "lon": -122.2323,
                "lat": 37.7763,
                "value": "Hispanic"
              },
              {
                "lon": -122.2243,
                "lat": 37.7681,
                "value": "Hispanic"
              },
              {
                "lon": -122.2278,
                "lat": 37.7864,
                "value": "Black"
              },
              {
                "lon": -122.2312,
                "lat": 37.7886,
                "value": "Asian"
              },
              {
                "lon": -122.2316,
                "lat": 37.7837,
                "value": "Asian"
              },
              {
                "lon": -122.2289,
                "lat": 37.7881,
                "value": "Hispanic"
              },
              {
                "lon": -122.2278,
                "lat": 37.7848,
                "value": "Hispanic"
              },
              {
                "lon": -122.2311,
                "lat": 37.7842,
                "value": "Hispanic"
              },
              {
                "lon": -122.2301,
                "lat": 37.783,
                "value": "Hispanic"
              },
              {
                "lon": -122.2338,
                "lat": 37.783,
                "value": "Hispanic"
              },
              {
                "lon": -122.23,
                "lat": 37.7813,
                "value": "Asian"
              },
              {
                "lon": -122.2256,
                "lat": 37.7804,
                "value": "Hispanic"
              },
              {
                "lon": -122.2298,
                "lat": 37.7803,
                "value": "Hispanic"
              },
              {
                "lon": -122.2259,
                "lat": 37.7834,
                "value": "Hispanic"
              },
              {
                "lon": -122.2297,
                "lat": 37.7807,
                "value": "Hispanic"
              },
              {
                "lon": -122.2259,
                "lat": 37.7819,
                "value": "Hispanic"
              },
              {
                "lon": -122.2269,
                "lat": 37.7823,
                "value": "Hispanic"
              },
              {
                "lon": -122.2226,
                "lat": 37.788,
                "value": "Black"
              },
              {
                "lon": -122.2279,
                "lat": 37.7887,
                "value": "Asian"
              },
              {
                "lon": -122.222,
                "lat": 37.7859,
                "value": "Asian"
              },
              {
                "lon": -122.2248,
                "lat": 37.7897,
                "value": "Hispanic"
              },
              {
                "lon": -122.2276,
                "lat": 37.7891,
                "value": "Hispanic"
              },
              {
                "lon": -122.2248,
                "lat": 37.7919,
                "value": "Hispanic"
              },
              {
                "lon": -122.2199,
                "lat": 37.7961,
                "value": "White"
              },
              {
                "lon": -122.2202,
                "lat": 37.7939,
                "value": "Hispanic"
              },
              {
                "lon": -122.2186,
                "lat": 37.7937,
                "value": "White"
              },
              {
                "lon": -122.2171,
                "lat": 37.7856,
                "value": "Black"
              },
              {
                "lon": -122.2214,
                "lat": 37.7862,
                "value": "Asian"
              },
              {
                "lon": -122.2162,
                "lat": 37.7883,
                "value": "Asian"
              },
              {
                "lon": -122.2186,
                "lat": 37.7932,
                "value": "Hispanic"
              },
              {
                "lon": -122.2187,
                "lat": 37.7884,
                "value": "Hispanic"
              },
              {
                "lon": -122.2185,
                "lat": 37.7874,
                "value": "Hispanic"
              },
              {
                "lon": -122.221,
                "lat": 37.7878,
                "value": "Hispanic"
              },
              {
                "lon": -122.217,
                "lat": 37.7939,
                "value": "Hispanic"
              },
              {
                "lon": -122.219,
                "lat": 37.7839,
                "value": "Hispanic"
              },
              {
                "lon": -122.2074,
                "lat": 37.7936,
                "value": "White"
              },
              {
                "lon": -122.2026,
                "lat": 37.7941,
                "value": "Black"
              },
              {
                "lon": -122.21,
                "lat": 37.794,
                "value": "Black"
              },
              {
                "lon": -122.2111,
                "lat": 37.7954,
                "value": "Asian"
              },
              {
                "lon": -122.2084,
                "lat": 37.7928,
                "value": "Hispanic"
              },
              {
                "lon": -122.2036,
                "lat": 37.7929,
                "value": "Hispanic"
              },
              {
                "lon": -122.2142,
                "lat": 37.7968,
                "value": "Black"
              },
              {
                "lon": -122.2129,
                "lat": 37.7978,
                "value": "Asian"
              },
              {
                "lon": -122.2174,
                "lat": 37.7958,
                "value": "Hispanic"
              },
              {
                "lon": -122.2024,
                "lat": 37.8041,
                "value": "White"
              },
              {
                "lon": -122.2093,
                "lat": 37.8036,
                "value": "White"
              },
              {
                "lon": -122.207,
                "lat": 37.8003,
                "value": "White"
              },
              {
                "lon": -122.204,
                "lat": 37.8077,
                "value": "White"
              },
              {
                "lon": -122.1988,
                "lat": 37.8071,
                "value": "Asian"
              },
              {
                "lon": -122.2033,
                "lat": 37.7981,
                "value": "Asian"
              },
              {
                "lon": -122.1976,
                "lat": 37.8077,
                "value": "Hispanic"
              },
              {
                "lon": -122.197,
                "lat": 37.8009,
                "value": "Hispanic"
              },
              {
                "lon": -122.201,
                "lat": 37.7967,
                "value": "White"
              },
              {
                "lon": -122.1943,
                "lat": 37.8016,
                "value": "White"
              },
              {
                "lon": -122.1913,
                "lat": 37.8012,
                "value": "Black"
              },
              {
                "lon": -122.1984,
                "lat": 37.7962,
                "value": "Asian"
              },
              {
                "lon": -122.1995,
                "lat": 37.7973,
                "value": "Hispanic"
              },
              {
                "lon": -122.1912,
                "lat": 37.7936,
                "value": "White"
              },
              {
                "lon": -122.1932,
                "lat": 37.7908,
                "value": "White"
              },
              {
                "lon": -122.1928,
                "lat": 37.7923,
                "value": "White"
              },
              {
                "lon": -122.1855,
                "lat": 37.7973,
                "value": "Black"
              },
              {
                "lon": -122.189,
                "lat": 37.7981,
                "value": "Asian"
              },
              {
                "lon": -122.1952,
                "lat": 37.7883,
                "value": "Hispanic"
              },
              {
                "lon": -122.1981,
                "lat": 37.788,
                "value": "White"
              },
              {
                "lon": -122.2024,
                "lat": 37.7904,
                "value": "White"
              },
              {
                "lon": -122.1974,
                "lat": 37.7862,
                "value": "Black"
              },
              {
                "lon": -122.2022,
                "lat": 37.7888,
                "value": "Black"
              },
              {
                "lon": -122.2055,
                "lat": 37.7888,
                "value": "Asian"
              },
              {
                "lon": -122.2079,
                "lat": 37.7869,
                "value": "Asian"
              },
              {
                "lon": -122.1984,
                "lat": 37.7878,
                "value": "Hispanic"
              },
              {
                "lon": -122.2006,
                "lat": 37.7895,
                "value": "Hispanic"
              },
              {
                "lon": -122.202,
                "lat": 37.7871,
                "value": "Hispanic"
              },
              {
                "lon": -122.2099,
                "lat": 37.7878,
                "value": "Hispanic"
              },
              {
                "lon": -122.2122,
                "lat": 37.7824,
                "value": "Asian"
              },
              {
                "lon": -122.2144,
                "lat": 37.782,
                "value": "Hispanic"
              },
              {
                "lon": -122.2156,
                "lat": 37.78,
                "value": "Hispanic"
              },
              {
                "lon": -122.2158,
                "lat": 37.7823,
                "value": "Hispanic"
              },
              {
                "lon": -122.2077,
                "lat": 37.7815,
                "value": "Black"
              },
              {
                "lon": -122.2109,
                "lat": 37.7816,
                "value": "Black"
              },
              {
                "lon": -122.2065,
                "lat": 37.781,
                "value": "Asian"
              },
              {
                "lon": -122.21,
                "lat": 37.7798,
                "value": "Asian"
              },
              {
                "lon": -122.2058,
                "lat": 37.7825,
                "value": "Hispanic"
              },
              {
                "lon": -122.2123,
                "lat": 37.7815,
                "value": "Hispanic"
              },
              {
                "lon": -122.2097,
                "lat": 37.7782,
                "value": "Hispanic"
              },
              {
                "lon": -122.2248,
                "lat": 37.7772,
                "value": "White"
              },
              {
                "lon": -122.2214,
                "lat": 37.7832,
                "value": "Asian"
              },
              {
                "lon": -122.2196,
                "lat": 37.7772,
                "value": "Hispanic"
              },
              {
                "lon": -122.2225,
                "lat": 37.7761,
                "value": "Hispanic"
              },
              {
                "lon": -122.2192,
                "lat": 37.7775,
                "value": "Hispanic"
              },
              {
                "lon": -122.2157,
                "lat": 37.7754,
                "value": "Hispanic"
              },
              {
                "lon": -122.2182,
                "lat": 37.7788,
                "value": "Hispanic"
              },
              {
                "lon": -122.2232,
                "lat": 37.7786,
                "value": "Hispanic"
              },
              {
                "lon": -122.2188,
                "lat": 37.7752,
                "value": "Hispanic"
              },
              {
                "lon": -122.2237,
                "lat": 37.7775,
                "value": "Hispanic"
              },
              {
                "lon": -122.2227,
                "lat": 37.7782,
                "value": "Hispanic"
              },
              {
                "lon": -122.2137,
                "lat": 37.7714,
                "value": "Hispanic"
              },
              {
                "lon": -122.2058,
                "lat": 37.766,
                "value": "Hispanic"
              },
              {
                "lon": -122.2013,
                "lat": 37.7701,
                "value": "Black"
              },
              {
                "lon": -122.205,
                "lat": 37.772,
                "value": "Black"
              },
              {
                "lon": -122.211,
                "lat": 37.7729,
                "value": "Hispanic"
              },
              {
                "lon": -122.2019,
                "lat": 37.7696,
                "value": "Hispanic"
              },
              {
                "lon": -122.2073,
                "lat": 37.7716,
                "value": "Hispanic"
              },
              {
                "lon": -122.2062,
                "lat": 37.7718,
                "value": "Hispanic"
              },
              {
                "lon": -122.1997,
                "lat": 37.7676,
                "value": "Hispanic"
              },
              {
                "lon": -122.1949,
                "lat": 37.7714,
                "value": "Hispanic"
              },
              {
                "lon": -122.1962,
                "lat": 37.7709,
                "value": "Hispanic"
              },
              {
                "lon": -122.1996,
                "lat": 37.7689,
                "value": "Hispanic"
              },
              {
                "lon": -122.1967,
                "lat": 37.7814,
                "value": "White"
              },
              {
                "lon": -122.1991,
                "lat": 37.7801,
                "value": "White"
              },
              {
                "lon": -122.2056,
                "lat": 37.7787,
                "value": "White"
              },
              {
                "lon": -122.2056,
                "lat": 37.7756,
                "value": "Black"
              },
              {
                "lon": -122.2034,
                "lat": 37.7791,
                "value": "Black"
              },
              {
                "lon": -122.2055,
                "lat": 37.7762,
                "value": "Asian"
              },
              {
                "lon": -122.2003,
                "lat": 37.7736,
                "value": "Hispanic"
              },
              {
                "lon": -122.2007,
                "lat": 37.7792,
                "value": "Hispanic"
              },
              {
                "lon": -122.199,
                "lat": 37.7788,
                "value": "Hispanic"
              },
              {
                "lon": -122.2101,
                "lat": 37.774,
                "value": "Hispanic"
              },
              {
                "lon": -122.2106,
                "lat": 37.7747,
                "value": "Hispanic"
              },
              {
                "lon": -122.1979,
                "lat": 37.7793,
                "value": "White"
              },
              {
                "lon": -122.1884,
                "lat": 37.7755,
                "value": "White"
              },
              {
                "lon": -122.1994,
                "lat": 37.7765,
                "value": "White"
              },
              {
                "lon": -122.1958,
                "lat": 37.7796,
                "value": "Black"
              },
              {
                "lon": -122.1888,
                "lat": 37.7753,
                "value": "Hispanic"
              },
              {
                "lon": -122.1766,
                "lat": 37.7809,
                "value": "White"
              },
              {
                "lon": -122.1967,
                "lat": 37.7822,
                "value": "Black"
              },
              {
                "lon": -122.1876,
                "lat": 37.7814,
                "value": "Hispanic"
              },
              {
                "lon": -122.1805,
                "lat": 37.7852,
                "value": "White"
              },
              {
                "lon": -122.1843,
                "lat": 37.7847,
                "value": "White"
              },
              {
                "lon": -122.1934,
                "lat": 37.7863,
                "value": "Hispanic"
              },
              {
                "lon": -122.1799,
                "lat": 37.8028,
                "value": "White"
              },
              {
                "lon": -122.1712,
                "lat": 37.797,
                "value": "White"
              },
              {
                "lon": -122.1776,
                "lat": 37.8041,
                "value": "White"
              },
              {
                "lon": -122.1558,
                "lat": 37.7769,
                "value": "White"
              },
              {
                "lon": -122.1672,
                "lat": 37.7971,
                "value": "White"
              },
              {
                "lon": -122.1726,
                "lat": 37.7884,
                "value": "White"
              },
              {
                "lon": -122.1586,
                "lat": 37.7932,
                "value": "White"
              },
              {
                "lon": -122.1401,
                "lat": 37.783,
                "value": "Black"
              },
              {
                "lon": -122.1588,
                "lat": 37.7789,
                "value": "Black"
              },
              {
                "lon": -122.1761,
                "lat": 37.7881,
                "value": "Black"
              },
              {
                "lon": -122.1681,
                "lat": 37.7808,
                "value": "Black"
              },
              {
                "lon": -122.1675,
                "lat": 37.8048,
                "value": "Asian"
              },
              {
                "lon": -122.1594,
                "lat": 37.7817,
                "value": "Asian"
              },
              {
                "lon": -122.1576,
                "lat": 37.7907,
                "value": "Asian"
              },
              {
                "lon": -122.1619,
                "lat": 37.7797,
                "value": "Hispanic"
              },
              {
                "lon": -122.1771,
                "lat": 37.775,
                "value": "White"
              },
              {
                "lon": -122.1772,
                "lat": 37.7749,
                "value": "Black"
              },
              {
                "lon": -122.1748,
                "lat": 37.7789,
                "value": "Black"
              },
              {
                "lon": -122.1778,
                "lat": 37.7739,
                "value": "Black"
              },
              {
                "lon": -122.1778,
                "lat": 37.7727,
                "value": "Hispanic"
              },
              {
                "lon": -122.1724,
                "lat": 37.7764,
                "value": "Hispanic"
              },
              {
                "lon": -122.1713,
                "lat": 37.7745,
                "value": "Hispanic"
              },
              {
                "lon": -122.1649,
                "lat": 37.7751,
                "value": "White"
              },
              {
                "lon": -122.17,
                "lat": 37.7788,
                "value": "Black"
              },
              {
                "lon": -122.1582,
                "lat": 37.7694,
                "value": "Black"
              },
              {
                "lon": -122.1717,
                "lat": 37.7783,
                "value": "Black"
              },
              {
                "lon": -122.161,
                "lat": 37.767,
                "value": "Asian"
              },
              {
                "lon": -122.156,
                "lat": 37.7683,
                "value": "Hispanic"
              },
              {
                "lon": -122.1616,
                "lat": 37.7713,
                "value": "Hispanic"
              },
              {
                "lon": -122.1694,
                "lat": 37.763,
                "value": "Black"
              },
              {
                "lon": -122.1662,
                "lat": 37.7625,
                "value": "Black"
              },
              {
                "lon": -122.1759,
                "lat": 37.7659,
                "value": "Black"
              },
              {
                "lon": -122.1714,
                "lat": 37.7611,
                "value": "Hispanic"
              },
              {
                "lon": -122.1739,
                "lat": 37.7638,
                "value": "Hispanic"
              },
              {
                "lon": -122.1734,
                "lat": 37.7652,
                "value": "Hispanic"
              },
              {
                "lon": -122.1715,
                "lat": 37.7614,
                "value": "Hispanic"
              },
              {
                "lon": -122.1795,
                "lat": 37.756,
                "value": "Black"
              },
              {
                "lon": -122.1775,
                "lat": 37.7624,
                "value": "Black"
              },
              {
                "lon": -122.1803,
                "lat": 37.7571,
                "value": "Black"
              },
              {
                "lon": -122.1814,
                "lat": 37.757,
                "value": "Black"
              },
              {
                "lon": -122.1715,
                "lat": 37.7604,
                "value": "Hispanic"
              },
              {
                "lon": -122.1745,
                "lat": 37.763,
                "value": "Hispanic"
              },
              {
                "lon": -122.1813,
                "lat": 37.7624,
                "value": "Hispanic"
              },
              {
                "lon": -122.1823,
                "lat": 37.7597,
                "value": "Hispanic"
              },
              {
                "lon": -122.1796,
                "lat": 37.7605,
                "value": "Hispanic"
              },
              {
                "lon": -122.1836,
                "lat": 37.7629,
                "value": "Black"
              },
              {
                "lon": -122.1866,
                "lat": 37.7621,
                "value": "Black"
              },
              {
                "lon": -122.1839,
                "lat": 37.7679,
                "value": "Black"
              },
              {
                "lon": -122.1856,
                "lat": 37.7614,
                "value": "Black"
              },
              {
                "lon": -122.1835,
                "lat": 37.7639,
                "value": "Hispanic"
              },
              {
                "lon": -122.1815,
                "lat": 37.7727,
                "value": "Hispanic"
              },
              {
                "lon": -122.1873,
                "lat": 37.7643,
                "value": "Hispanic"
              },
              {
                "lon": -122.1761,
                "lat": 37.7692,
                "value": "Hispanic"
              },
              {
                "lon": -122.1874,
                "lat": 37.76,
                "value": "Hispanic"
              },
              {
                "lon": -122.1885,
                "lat": 37.7621,
                "value": "Hispanic"
              },
              {
                "lon": -122.1896,
                "lat": 37.7713,
                "value": "White"
              },
              {
                "lon": -122.1934,
                "lat": 37.7691,
                "value": "Black"
              },
              {
                "lon": -122.1932,
                "lat": 37.7647,
                "value": "Black"
              },
              {
                "lon": -122.1847,
                "lat": 37.7689,
                "value": "Black"
              },
              {
                "lon": -122.186,
                "lat": 37.773,
                "value": "Black"
              },
              {
                "lon": -122.1909,
                "lat": 37.7695,
                "value": "Asian"
              },
              {
                "lon": -122.1854,
                "lat": 37.7706,
                "value": "Hispanic"
              },
              {
                "lon": -122.1941,
                "lat": 37.7663,
                "value": "Hispanic"
              },
              {
                "lon": -122.1864,
                "lat": 37.7719,
                "value": "Hispanic"
              },
              {
                "lon": -122.1856,
                "lat": 37.7727,
                "value": "Hispanic"
              },
              {
                "lon": -122.1914,
                "lat": 37.7668,
                "value": "Hispanic"
              },
              {
                "lon": -122.191,
                "lat": 37.7638,
                "value": "Hispanic"
              },
              {
                "lon": -122.1917,
                "lat": 37.7633,
                "value": "Hispanic"
              },
              {
                "lon": -122.1962,
                "lat": 37.7578,
                "value": "Black"
              },
              {
                "lon": -122.2006,
                "lat": 37.7612,
                "value": "Black"
              },
              {
                "lon": -122.1912,
                "lat": 37.7598,
                "value": "Black"
              },
              {
                "lon": -122.1933,
                "lat": 37.7589,
                "value": "Black"
              },
              {
                "lon": -122.1945,
                "lat": 37.7558,
                "value": "Hispanic"
              },
              {
                "lon": -122.1944,
                "lat": 37.7579,
                "value": "Hispanic"
              },
              {
                "lon": -122.1993,
                "lat": 37.7557,
                "value": "Hispanic"
              },
              {
                "lon": -122.1899,
                "lat": 37.7584,
                "value": "Hispanic"
              },
              {
                "lon": -122.1927,
                "lat": 37.7588,
                "value": "Hispanic"
              },
              {
                "lon": -122.1983,
                "lat": 37.7637,
                "value": "Hispanic"
              },
              {
                "lon": -122.1926,
                "lat": 37.7534,
                "value": "Black"
              },
              {
                "lon": -122.1907,
                "lat": 37.7566,
                "value": "Hispanic"
              },
              {
                "lon": -122.1891,
                "lat": 37.7552,
                "value": "Hispanic"
              },
              {
                "lon": -122.194,
                "lat": 37.7523,
                "value": "Hispanic"
              },
              {
                "lon": -122.1889,
                "lat": 37.7562,
                "value": "Hispanic"
              },
              {
                "lon": -122.1845,
                "lat": 37.7552,
                "value": "Hispanic"
              },
              {
                "lon": -122.1926,
                "lat": 37.7504,
                "value": "Hispanic"
              },
              {
                "lon": -122.2101,
                "lat": 37.714,
                "value": "Black"
              },
              {
                "lon": -122.2146,
                "lat": 37.7134,
                "value": "Black"
              },
              {
                "lon": -122.2178,
                "lat": 37.719,
                "value": "Asian"
              },
              {
                "lon": -122.2408,
                "lat": 37.7214,
                "value": "Hispanic"
              },
              {
                "lon": -122.2287,
                "lat": 37.7132,
                "value": "Hispanic"
              },
              {
                "lon": -122.2054,
                "lat": 37.7323,
                "value": "Hispanic"
              },
              {
                "lon": -122.2211,
                "lat": 37.7174,
                "value": "Hispanic"
              },
              {
                "lon": -122.1975,
                "lat": 37.7308,
                "value": "Hispanic"
              },
              {
                "lon": -122.1808,
                "lat": 37.7362,
                "value": "Hispanic"
              },
              {
                "lon": -122.1828,
                "lat": 37.7325,
                "value": "Hispanic"
              },
              {
                "lon": -122.1828,
                "lat": 37.7335,
                "value": "Hispanic"
              },
              {
                "lon": -122.1809,
                "lat": 37.7278,
                "value": "Black"
              },
              {
                "lon": -122.1818,
                "lat": 37.7286,
                "value": "Hispanic"
              },
              {
                "lon": -122.1819,
                "lat": 37.7291,
                "value": "Hispanic"
              },
              {
                "lon": -122.18,
                "lat": 37.7303,
                "value": "Hispanic"
              },
              {
                "lon": -122.1771,
                "lat": 37.7278,
                "value": "Hispanic"
              },
              {
                "lon": -122.1788,
                "lat": 37.7367,
                "value": "Black"
              },
              {
                "lon": -122.1722,
                "lat": 37.7413,
                "value": "Black"
              },
              {
                "lon": -122.1725,
                "lat": 37.7335,
                "value": "Hispanic"
              },
              {
                "lon": -122.1768,
                "lat": 37.7393,
                "value": "Hispanic"
              },
              {
                "lon": -122.1717,
                "lat": 37.7436,
                "value": "Hispanic"
              },
              {
                "lon": -122.1789,
                "lat": 37.7392,
                "value": "Hispanic"
              },
              {
                "lon": -122.1769,
                "lat": 37.7414,
                "value": "Hispanic"
              },
              {
                "lon": -122.1734,
                "lat": 37.7319,
                "value": "Hispanic"
              },
              {
                "lon": -122.1681,
                "lat": 37.7379,
                "value": "Hispanic"
              },
              {
                "lon": -122.1781,
                "lat": 37.7416,
                "value": "Black"
              },
              {
                "lon": -122.1782,
                "lat": 37.7462,
                "value": "Hispanic"
              },
              {
                "lon": -122.1843,
                "lat": 37.7439,
                "value": "Hispanic"
              },
              {
                "lon": -122.1809,
                "lat": 37.7453,
                "value": "Hispanic"
              },
              {
                "lon": -122.1726,
                "lat": 37.7436,
                "value": "Hispanic"
              },
              {
                "lon": -122.1851,
                "lat": 37.7417,
                "value": "Hispanic"
              },
              {
                "lon": -122.1717,
                "lat": 37.7458,
                "value": "Hispanic"
              },
              {
                "lon": -122.1833,
                "lat": 37.7403,
                "value": "Hispanic"
              },
              {
                "lon": -122.1814,
                "lat": 37.7517,
                "value": "Black"
              },
              {
                "lon": -122.1888,
                "lat": 37.7502,
                "value": "Hispanic"
              },
              {
                "lon": -122.1904,
                "lat": 37.7482,
                "value": "Hispanic"
              },
              {
                "lon": -122.1905,
                "lat": 37.7497,
                "value": "Hispanic"
              },
              {
                "lon": -122.1927,
                "lat": 37.7494,
                "value": "Hispanic"
              },
              {
                "lon": -122.1923,
                "lat": 37.7486,
                "value": "Hispanic"
              },
              {
                "lon": -122.1918,
                "lat": 37.7497,
                "value": "Hispanic"
              },
              {
                "lon": -122.1763,
                "lat": 37.7568,
                "value": "Black"
              },
              {
                "lon": -122.1738,
                "lat": 37.7562,
                "value": "Black"
              },
              {
                "lon": -122.1714,
                "lat": 37.7577,
                "value": "Black"
              },
              {
                "lon": -122.1723,
                "lat": 37.7577,
                "value": "Hispanic"
              },
              {
                "lon": -122.1749,
                "lat": 37.7518,
                "value": "Hispanic"
              },
              {
                "lon": -122.1754,
                "lat": 37.7541,
                "value": "Hispanic"
              },
              {
                "lon": -122.1682,
                "lat": 37.7493,
                "value": "Hispanic"
              },
              {
                "lon": -122.1734,
                "lat": 37.7559,
                "value": "Hispanic"
              },
              {
                "lon": -122.1757,
                "lat": 37.7526,
                "value": "Hispanic"
              },
              {
                "lon": -122.1748,
                "lat": 37.7552,
                "value": "Hispanic"
              },
              {
                "lon": -122.1657,
                "lat": 37.7552,
                "value": "Black"
              },
              {
                "lon": -122.165,
                "lat": 37.753,
                "value": "Black"
              },
              {
                "lon": -122.1637,
                "lat": 37.7542,
                "value": "Black"
              },
              {
                "lon": -122.1713,
                "lat": 37.7596,
                "value": "Hispanic"
              },
              {
                "lon": -122.1648,
                "lat": 37.7593,
                "value": "Hispanic"
              },
              {
                "lon": -122.162,
                "lat": 37.7529,
                "value": "Hispanic"
              },
              {
                "lon": -122.1706,
                "lat": 37.7598,
                "value": "Hispanic"
              },
              {
                "lon": -122.1549,
                "lat": 37.7658,
                "value": "Black"
              },
              {
                "lon": -122.1525,
                "lat": 37.7646,
                "value": "Black"
              },
              {
                "lon": -122.1521,
                "lat": 37.7607,
                "value": "Black"
              },
              {
                "lon": -122.1539,
                "lat": 37.7548,
                "value": "Hispanic"
              },
              {
                "lon": -122.1474,
                "lat": 37.7614,
                "value": "White"
              },
              {
                "lon": -122.1481,
                "lat": 37.7671,
                "value": "Black"
              },
              {
                "lon": -122.1339,
                "lat": 37.7659,
                "value": "Black"
              },
              {
                "lon": -122.1268,
                "lat": 37.7589,
                "value": "Black"
              },
              {
                "lon": -122.1375,
                "lat": 37.7391,
                "value": "White"
              },
              {
                "lon": -122.1217,
                "lat": 37.7455,
                "value": "Black"
              },
              {
                "lon": -122.1244,
                "lat": 37.7337,
                "value": "Black"
              },
              {
                "lon": -122.1497,
                "lat": 37.7436,
                "value": "Black"
              },
              {
                "lon": -122.1486,
                "lat": 37.7426,
                "value": "Black"
              },
              {
                "lon": -122.1488,
                "lat": 37.7436,
                "value": "Black"
              },
              {
                "lon": -122.1551,
                "lat": 37.7452,
                "value": "Hispanic"
              },
              {
                "lon": -122.1545,
                "lat": 37.7436,
                "value": "Black"
              },
              {
                "lon": -122.1506,
                "lat": 37.7406,
                "value": "Black"
              },
              {
                "lon": -122.1572,
                "lat": 37.7438,
                "value": "Hispanic"
              },
              {
                "lon": -122.1602,
                "lat": 37.7507,
                "value": "Hispanic"
              },
              {
                "lon": -122.1575,
                "lat": 37.7463,
                "value": "Hispanic"
              },
              {
                "lon": -122.16,
                "lat": 37.7452,
                "value": "Black"
              },
              {
                "lon": -122.1712,
                "lat": 37.747,
                "value": "Hispanic"
              },
              {
                "lon": -122.1604,
                "lat": 37.7455,
                "value": "Hispanic"
              },
              {
                "lon": -122.1693,
                "lat": 37.7438,
                "value": "Hispanic"
              },
              {
                "lon": -122.1634,
                "lat": 37.7464,
                "value": "Hispanic"
              },
              {
                "lon": -122.1675,
                "lat": 37.7494,
                "value": "Hispanic"
              },
              {
                "lon": -122.1683,
                "lat": 37.7477,
                "value": "Hispanic"
              },
              {
                "lon": -122.1683,
                "lat": 37.7424,
                "value": "Black"
              },
              {
                "lon": -122.1615,
                "lat": 37.7417,
                "value": "Black"
              },
              {
                "lon": -122.163,
                "lat": 37.7398,
                "value": "Hispanic"
              },
              {
                "lon": -122.1648,
                "lat": 37.7376,
                "value": "Hispanic"
              },
              {
                "lon": -122.1602,
                "lat": 37.7398,
                "value": "Hispanic"
              },
              {
                "lon": -122.1606,
                "lat": 37.742,
                "value": "Hispanic"
              },
              {
                "lon": -122.2899,
                "lat": 37.8153,
                "value": "White"
              },
              {
                "lon": -122.2896,
                "lat": 37.8114,
                "value": "Black"
              },
              {
                "lon": -122.2886,
                "lat": 37.8078,
                "value": "Black"
              },
              {
                "lon": -122.2917,
                "lat": 37.81,
                "value": "Black"
              },
              {
                "lon": -122.288,
                "lat": 37.8951,
                "value": "White"
              },
              {
                "lon": -122.2927,
                "lat": 37.8914,
                "value": "White"
              },
              {
                "lon": -122.2884,
                "lat": 37.897,
                "value": "Asian"
              },
              {
                "lon": -122.2953,
                "lat": 37.8927,
                "value": "White"
              },
              {
                "lon": -122.3011,
                "lat": 37.8979,
                "value": "White"
              },
              {
                "lon": -122.2957,
                "lat": 37.8906,
                "value": "Asian"
              },
              {
                "lon": -122.2963,
                "lat": 37.8936,
                "value": "Asian"
              },
              {
                "lon": -122.3082,
                "lat": 37.8967,
                "value": "White"
              },
              {
                "lon": -122.3052,
                "lat": 37.8908,
                "value": "Asian"
              },
              {
                "lon": -122.3069,
                "lat": 37.8965,
                "value": "Asian"
              },
              {
                "lon": -122.3067,
                "lat": 37.8904,
                "value": "White"
              },
              {
                "lon": -122.3027,
                "lat": 37.8904,
                "value": "Asian"
              },
              {
                "lon": -122.3181,
                "lat": 37.8885,
                "value": "White"
              },
              {
                "lon": -122.3109,
                "lat": 37.8866,
                "value": "Asian"
              },
              {
                "lon": -122.2965,
                "lat": 37.8903,
                "value": "White"
              },
              {
                "lon": -122.2972,
                "lat": 37.8873,
                "value": "White"
              },
              {
                "lon": -122.2979,
                "lat": 37.8868,
                "value": "Asian"
              },
              {
                "lon": -122.2846,
                "lat": 37.8851,
                "value": "White"
              },
              {
                "lon": -122.2898,
                "lat": 37.8845,
                "value": "White"
              },
              {
                "lon": -122.2868,
                "lat": 37.8847,
                "value": "White"
              },
              {
                "lon": -122.2914,
                "lat": 37.8872,
                "value": "White"
              },
              {
                "lon": -122.2639,
                "lat": 37.897,
                "value": "White"
              },
              {
                "lon": -122.265,
                "lat": 37.8982,
                "value": "White"
              },
              {
                "lon": -122.2696,
                "lat": 37.8983,
                "value": "White"
              },
              {
                "lon": -122.2769,
                "lat": 37.8979,
                "value": "White"
              },
              {
                "lon": -122.2719,
                "lat": 37.9017,
                "value": "White"
              },
              {
                "lon": -122.2746,
                "lat": 37.8915,
                "value": "White"
              },
              {
                "lon": -122.2714,
                "lat": 37.9001,
                "value": "White"
              },
              {
                "lon": -122.2768,
                "lat": 37.8907,
                "value": "Asian"
              },
              {
                "lon": -122.2815,
                "lat": 37.8954,
                "value": "White"
              },
              {
                "lon": -122.2856,
                "lat": 37.8944,
                "value": "White"
              },
              {
                "lon": -122.2852,
                "lat": 37.8929,
                "value": "White"
              },
              {
                "lon": -122.281,
                "lat": 37.8823,
                "value": "White"
              },
              {
                "lon": -122.2791,
                "lat": 37.8842,
                "value": "White"
              },
              {
                "lon": -122.2852,
                "lat": 37.8983,
                "value": "Asian"
              },
              {
                "lon": -122.2721,
                "lat": 37.8885,
                "value": "White"
              },
              {
                "lon": -122.2688,
                "lat": 37.8919,
                "value": "White"
              },
              {
                "lon": -122.2602,
                "lat": 37.8839,
                "value": "White"
              },
              {
                "lon": -122.2603,
                "lat": 37.8861,
                "value": "White"
              },
              {
                "lon": -122.2616,
                "lat": 37.8967,
                "value": "White"
              },
              {
                "lon": -122.2516,
                "lat": 37.8918,
                "value": "White"
              },
              {
                "lon": -122.2587,
                "lat": 37.8936,
                "value": "White"
              },
              {
                "lon": -122.2635,
                "lat": 37.8891,
                "value": "White"
              },
              {
                "lon": -122.2627,
                "lat": 37.8796,
                "value": "White"
              },
              {
                "lon": -122.2551,
                "lat": 37.8864,
                "value": "White"
              },
              {
                "lon": -122.2505,
                "lat": 37.8834,
                "value": "White"
              },
              {
                "lon": -122.2626,
                "lat": 37.8835,
                "value": "White"
              },
              {
                "lon": -122.2496,
                "lat": 37.882,
                "value": "White"
              },
              {
                "lon": -122.2713,
                "lat": 37.8831,
                "value": "White"
              },
              {
                "lon": -122.2685,
                "lat": 37.8838,
                "value": "White"
              },
              {
                "lon": -122.2715,
                "lat": 37.88,
                "value": "White"
              },
              {
                "lon": -122.274,
                "lat": 37.8805,
                "value": "White"
              },
              {
                "lon": -122.2729,
                "lat": 37.8844,
                "value": "Asian"
              },
              {
                "lon": -122.2779,
                "lat": 37.8803,
                "value": "White"
              },
              {
                "lon": -122.28,
                "lat": 37.8801,
                "value": "White"
              },
              {
                "lon": -122.2964,
                "lat": 37.8821,
                "value": "White"
              },
              {
                "lon": -122.2894,
                "lat": 37.8763,
                "value": "White"
              },
              {
                "lon": -122.2854,
                "lat": 37.8768,
                "value": "White"
              },
              {
                "lon": -122.2875,
                "lat": 37.8792,
                "value": "White"
              },
              {
                "lon": -122.2898,
                "lat": 37.8814,
                "value": "Asian"
              },
              {
                "lon": -122.3079,
                "lat": 37.8801,
                "value": "White"
              },
              {
                "lon": -122.3168,
                "lat": 37.8651,
                "value": "White"
              },
              {
                "lon": -122.2877,
                "lat": 37.8514,
                "value": "Asian"
              },
              {
                "lon": -122.2969,
                "lat": 37.8683,
                "value": "White"
              },
              {
                "lon": -122.2985,
                "lat": 37.8779,
                "value": "White"
              },
              {
                "lon": -122.2975,
                "lat": 37.8777,
                "value": "White"
              },
              {
                "lon": -122.2965,
                "lat": 37.877,
                "value": "Hispanic"
              },
              {
                "lon": -122.2914,
                "lat": 37.8724,
                "value": "White"
              },
              {
                "lon": -122.2837,
                "lat": 37.8729,
                "value": "White"
              },
              {
                "lon": -122.2929,
                "lat": 37.8726,
                "value": "White"
              },
              {
                "lon": -122.2836,
                "lat": 37.8749,
                "value": "Asian"
              },
              {
                "lon": -122.2794,
                "lat": 37.8769,
                "value": "White"
              },
              {
                "lon": -122.2815,
                "lat": 37.8756,
                "value": "White"
              },
              {
                "lon": -122.2743,
                "lat": 37.8725,
                "value": "White"
              },
              {
                "lon": -122.2759,
                "lat": 37.8714,
                "value": "Asian"
              },
              {
                "lon": -122.2724,
                "lat": 37.8716,
                "value": "White"
              },
              {
                "lon": -122.272,
                "lat": 37.877,
                "value": "White"
              },
              {
                "lon": -122.2721,
                "lat": 37.8754,
                "value": "White"
              },
              {
                "lon": -122.2709,
                "lat": 37.8745,
                "value": "Asian"
              },
              {
                "lon": -122.2693,
                "lat": 37.8747,
                "value": "Asian"
              },
              {
                "lon": -122.2603,
                "lat": 37.8762,
                "value": "White"
              },
              {
                "lon": -122.2557,
                "lat": 37.8761,
                "value": "White"
              },
              {
                "lon": -122.2565,
                "lat": 37.8774,
                "value": "White"
              },
              {
                "lon": -122.2633,
                "lat": 37.8768,
                "value": "Asian"
              },
              {
                "lon": -122.2576,
                "lat": 37.8781,
                "value": "Asian"
              },
              {
                "lon": -122.2574,
                "lat": 37.8759,
                "value": "Hispanic"
              },
              {
                "lon": -122.2455,
                "lat": 37.8693,
                "value": "White"
              },
              {
                "lon": -122.2513,
                "lat": 37.8664,
                "value": "White"
              },
              {
                "lon": -122.2488,
                "lat": 37.8666,
                "value": "White"
              },
              {
                "lon": -122.2449,
                "lat": 37.867,
                "value": "Asian"
              },
              {
                "lon": -122.2541,
                "lat": 37.869,
                "value": "Asian"
              },
              {
                "lon": -122.2524,
                "lat": 37.866,
                "value": "Asian"
              },
              {
                "lon": -122.2457,
                "lat": 37.8697,
                "value": "Hispanic"
              },
              {
                "lon": -122.2605,
                "lat": 37.8678,
                "value": "White"
              },
              {
                "lon": -122.2617,
                "lat": 37.867,
                "value": "White"
              },
              {
                "lon": -122.2646,
                "lat": 37.8675,
                "value": "White"
              },
              {
                "lon": -122.2546,
                "lat": 37.8673,
                "value": "White"
              },
              {
                "lon": -122.2561,
                "lat": 37.8655,
                "value": "Black"
              },
              {
                "lon": -122.2646,
                "lat": 37.8656,
                "value": "Asian"
              },
              {
                "lon": -122.2627,
                "lat": 37.8668,
                "value": "Asian"
              },
              {
                "lon": -122.2641,
                "lat": 37.8648,
                "value": "Asian"
              },
              {
                "lon": -122.2647,
                "lat": 37.8649,
                "value": "Asian"
              },
              {
                "lon": -122.2556,
                "lat": 37.8663,
                "value": "Asian"
              },
              {
                "lon": -122.2647,
                "lat": 37.8655,
                "value": "Asian"
              },
              {
                "lon": -122.2563,
                "lat": 37.8677,
                "value": "Asian"
              },
              {
                "lon": -122.2657,
                "lat": 37.8676,
                "value": "Hispanic"
              },
              {
                "lon": -122.2635,
                "lat": 37.8676,
                "value": "Hispanic"
              },
              {
                "lon": -122.2619,
                "lat": 37.8669,
                "value": "Hispanic"
              },
              {
                "lon": -122.2686,
                "lat": 37.8652,
                "value": "White"
              },
              {
                "lon": -122.267,
                "lat": 37.8655,
                "value": "Asian"
              },
              {
                "lon": -122.2673,
                "lat": 37.8674,
                "value": "Asian"
              },
              {
                "lon": -122.2714,
                "lat": 37.8648,
                "value": "White"
              },
              {
                "lon": -122.2703,
                "lat": 37.8706,
                "value": "Asian"
              },
              {
                "lon": -122.2785,
                "lat": 37.8647,
                "value": "White"
              },
              {
                "lon": -122.2814,
                "lat": 37.8694,
                "value": "White"
              },
              {
                "lon": -122.2811,
                "lat": 37.8663,
                "value": "White"
              },
              {
                "lon": -122.2811,
                "lat": 37.863,
                "value": "White"
              },
              {
                "lon": -122.276,
                "lat": 37.8696,
                "value": "White"
              },
              {
                "lon": -122.2762,
                "lat": 37.8676,
                "value": "Asian"
              },
              {
                "lon": -122.2783,
                "lat": 37.8657,
                "value": "Hispanic"
              },
              {
                "lon": -122.2877,
                "lat": 37.8627,
                "value": "White"
              },
              {
                "lon": -122.2849,
                "lat": 37.8637,
                "value": "White"
              },
              {
                "lon": -122.2868,
                "lat": 37.8642,
                "value": "White"
              },
              {
                "lon": -122.285,
                "lat": 37.8657,
                "value": "Black"
              },
              {
                "lon": -122.2843,
                "lat": 37.8677,
                "value": "Asian"
              },
              {
                "lon": -122.2898,
                "lat": 37.8674,
                "value": "Hispanic"
              },
              {
                "lon": -122.2925,
                "lat": 37.8629,
                "value": "White"
              },
              {
                "lon": -122.2945,
                "lat": 37.8606,
                "value": "White"
              },
              {
                "lon": -122.2948,
                "lat": 37.8668,
                "value": "Hispanic"
              },
              {
                "lon": -122.2817,
                "lat": 37.8546,
                "value": "White"
              },
              {
                "lon": -122.2813,
                "lat": 37.8594,
                "value": "White"
              },
              {
                "lon": -122.2852,
                "lat": 37.8579,
                "value": "White"
              },
              {
                "lon": -122.2822,
                "lat": 37.8581,
                "value": "Black"
              },
              {
                "lon": -122.2859,
                "lat": 37.8599,
                "value": "Hispanic"
              },
              {
                "lon": -122.2715,
                "lat": 37.8546,
                "value": "White"
              },
              {
                "lon": -122.2715,
                "lat": 37.8559,
                "value": "White"
              },
              {
                "lon": -122.2785,
                "lat": 37.8624,
                "value": "White"
              },
              {
                "lon": -122.2735,
                "lat": 37.8585,
                "value": "White"
              },
              {
                "lon": -122.278,
                "lat": 37.8613,
                "value": "White"
              },
              {
                "lon": -122.2737,
                "lat": 37.854,
                "value": "Black"
              },
              {
                "lon": -122.2714,
                "lat": 37.8556,
                "value": "Asian"
              },
              {
                "lon": -122.2792,
                "lat": 37.8555,
                "value": "Hispanic"
              },
              {
                "lon": -122.2707,
                "lat": 37.8609,
                "value": "White"
              },
              {
                "lon": -122.2698,
                "lat": 37.8573,
                "value": "White"
              },
              {
                "lon": -122.2716,
                "lat": 37.8596,
                "value": "White"
              },
              {
                "lon": -122.2553,
                "lat": 37.8587,
                "value": "White"
              },
              {
                "lon": -122.2549,
                "lat": 37.8592,
                "value": "White"
              },
              {
                "lon": -122.2554,
                "lat": 37.8608,
                "value": "White"
              },
              {
                "lon": -122.2623,
                "lat": 37.8636,
                "value": "White"
              },
              {
                "lon": -122.2586,
                "lat": 37.8641,
                "value": "White"
              },
              {
                "lon": -122.2645,
                "lat": 37.8634,
                "value": "White"
              },
              {
                "lon": -122.2578,
                "lat": 37.8626,
                "value": "White"
              },
              {
                "lon": -122.2586,
                "lat": 37.8642,
                "value": "White"
              },
              {
                "lon": -122.2613,
                "lat": 37.8618,
                "value": "White"
              },
              {
                "lon": -122.2606,
                "lat": 37.863,
                "value": "Asian"
              },
              {
                "lon": -122.2652,
                "lat": 37.864,
                "value": "Asian"
              },
              {
                "lon": -122.2551,
                "lat": 37.8628,
                "value": "Asian"
              },
              {
                "lon": -122.2619,
                "lat": 37.8622,
                "value": "Asian"
              },
              {
                "lon": -122.2603,
                "lat": 37.8635,
                "value": "Hispanic"
              },
              {
                "lon": -122.2471,
                "lat": 37.8617,
                "value": "White"
              },
              {
                "lon": -122.2487,
                "lat": 37.862,
                "value": "White"
              },
              {
                "lon": -122.2473,
                "lat": 37.8638,
                "value": "White"
              },
              {
                "lon": -122.2509,
                "lat": 37.8619,
                "value": "Asian"
              },
              {
                "lon": -122.2462,
                "lat": 37.8546,
                "value": "White"
              },
              {
                "lon": -122.2468,
                "lat": 37.8566,
                "value": "White"
              },
              {
                "lon": -122.2345,
                "lat": 37.8552,
                "value": "White"
              },
              {
                "lon": -122.2417,
                "lat": 37.8568,
                "value": "White"
              },
              {
                "lon": -122.2429,
                "lat": 37.8559,
                "value": "White"
              },
              {
                "lon": -122.2696,
                "lat": 37.8493,
                "value": "White"
              },
              {
                "lon": -122.2697,
                "lat": 37.8486,
                "value": "White"
              },
              {
                "lon": -122.2571,
                "lat": 37.855,
                "value": "White"
              },
              {
                "lon": -122.2597,
                "lat": 37.8549,
                "value": "White"
              },
              {
                "lon": -122.2718,
                "lat": 37.8531,
                "value": "White"
              },
              {
                "lon": -122.2723,
                "lat": 37.8536,
                "value": "White"
              },
              {
                "lon": -122.2746,
                "lat": 37.846,
                "value": "White"
              },
              {
                "lon": -122.2732,
                "lat": 37.849,
                "value": "Black"
              },
              {
                "lon": -122.2753,
                "lat": 37.8491,
                "value": "Asian"
              },
              {
                "lon": -122.2788,
                "lat": 37.8533,
                "value": "Hispanic"
              },
              {
                "lon": -122.2819,
                "lat": 37.8472,
                "value": "White"
              },
              {
                "lon": -122.2819,
                "lat": 37.8494,
                "value": "White"
              },
              {
                "lon": -122.2825,
                "lat": 37.8489,
                "value": "Black"
              },
              {
                "lon": -122.3035,
                "lat": 37.8373,
                "value": "White"
              },
              {
                "lon": -122.2946,
                "lat": 37.8443,
                "value": "White"
              },
              {
                "lon": -122.2968,
                "lat": 37.8438,
                "value": "White"
              },
              {
                "lon": -122.298,
                "lat": 37.8456,
                "value": "Black"
              },
              {
                "lon": -122.292,
                "lat": 37.8346,
                "value": "Asian"
              },
              {
                "lon": -122.2924,
                "lat": 37.836,
                "value": "Asian"
              },
              {
                "lon": -122.2933,
                "lat": 37.8379,
                "value": "Asian"
              },
              {
                "lon": -122.29,
                "lat": 37.8374,
                "value": "White"
              },
              {
                "lon": -122.2897,
                "lat": 37.8492,
                "value": "Black"
              },
              {
                "lon": -122.2898,
                "lat": 37.8439,
                "value": "Asian"
              },
              {
                "lon": -122.284,
                "lat": 37.831,
                "value": "White"
              },
              {
                "lon": -122.2883,
                "lat": 37.8305,
                "value": "White"
              },
              {
                "lon": -122.2791,
                "lat": 37.8322,
                "value": "White"
              },
              {
                "lon": -122.2765,
                "lat": 37.836,
                "value": "Black"
              },
              {
                "lon": -122.277,
                "lat": 37.8337,
                "value": "Asian"
              },
              {
                "lon": -122.2872,
                "lat": 37.8308,
                "value": "Hispanic"
              },
              {
                "lon": -122.2244,
                "lat": 37.8262,
                "value": "White"
              },
              {
                "lon": -122.2226,
                "lat": 37.8209,
                "value": "White"
              },
              {
                "lon": -122.2166,
                "lat": 37.8184,
                "value": "White"
              },
              {
                "lon": -122.2299,
                "lat": 37.8274,
                "value": "White"
              },
              {
                "lon": -122.23,
                "lat": 37.8229,
                "value": "White"
              },
              {
                "lon": -122.2362,
                "lat": 37.8308,
                "value": "White"
              },
              {
                "lon": -122.2149,
                "lat": 37.8201,
                "value": "White"
              },
              {
                "lon": -122.2127,
                "lat": 37.8169,
                "value": "White"
              },
              {
                "lon": -122.2351,
                "lat": 37.822,
                "value": "Asian"
              },
              {
                "lon": -122.2262,
                "lat": 37.8233,
                "value": "Asian"
              },
              {
                "lon": -122.2168,
                "lat": 37.8178,
                "value": "Asian"
              },
              {
                "lon": -122.2379,
                "lat": 37.8233,
                "value": "White"
              },
              {
                "lon": -122.2417,
                "lat": 37.8231,
                "value": "White"
              },
              {
                "lon": -122.2351,
                "lat": 37.8254,
                "value": "White"
              },
              {
                "lon": -122.2409,
                "lat": 37.822,
                "value": "White"
              },
              {
                "lon": -122.2379,
                "lat": 37.8286,
                "value": "White"
              },
              {
                "lon": -122.243,
                "lat": 37.8193,
                "value": "White"
              },
              {
                "lon": -122.2467,
                "lat": 37.8235,
                "value": "Asian"
              },
              {
                "lon": -122.2374,
                "lat": 37.7657,
                "value": "White"
              },
              {
                "lon": -122.2258,
                "lat": 37.762,
                "value": "White"
              },
              {
                "lon": -122.2388,
                "lat": 37.7672,
                "value": "White"
              },
              {
                "lon": -122.232,
                "lat": 37.7692,
                "value": "White"
              },
              {
                "lon": -122.2245,
                "lat": 37.756,
                "value": "Asian"
              },
              {
                "lon": -122.2276,
                "lat": 37.7667,
                "value": "Hispanic"
              },
              {
                "lon": -122.251,
                "lat": 37.7808,
                "value": "White"
              },
              {
                "lon": -122.2481,
                "lat": 37.7717,
                "value": "White"
              },
              {
                "lon": -122.246,
                "lat": 37.7805,
                "value": "Asian"
              },
              {
                "lon": -122.2543,
                "lat": 37.7734,
                "value": "Asian"
              },
              {
                "lon": -122.2412,
                "lat": 37.7719,
                "value": "Asian"
              },
              {
                "lon": -122.2529,
                "lat": 37.7836,
                "value": "Hispanic"
              },
              {
                "lon": -122.2612,
                "lat": 37.7748,
                "value": "White"
              },
              {
                "lon": -122.2735,
                "lat": 37.7788,
                "value": "White"
              },
              {
                "lon": -122.264,
                "lat": 37.7757,
                "value": "White"
              },
              {
                "lon": -122.2698,
                "lat": 37.7835,
                "value": "Black"
              },
              {
                "lon": -122.2609,
                "lat": 37.7767,
                "value": "Asian"
              },
              {
                "lon": -122.2556,
                "lat": 37.7751,
                "value": "Asian"
              },
              {
                "lon": -122.2676,
                "lat": 37.7817,
                "value": "Asian"
              },
              {
                "lon": -122.2602,
                "lat": 37.7794,
                "value": "Hispanic"
              },
              {
                "lon": -122.2889,
                "lat": 37.7783,
                "value": "White"
              },
              {
                "lon": -122.286,
                "lat": 37.7781,
                "value": "White"
              },
              {
                "lon": -122.2893,
                "lat": 37.7782,
                "value": "Black"
              },
              {
                "lon": -122.2855,
                "lat": 37.7779,
                "value": "Asian"
              },
              {
                "lon": -122.2777,
                "lat": 37.7756,
                "value": "Asian"
              },
              {
                "lon": -122.277,
                "lat": 37.7793,
                "value": "Asian"
              },
              {
                "lon": -122.2831,
                "lat": 37.7798,
                "value": "Hispanic"
              },
              {
                "lon": -122.2886,
                "lat": 37.7713,
                "value": "White"
              },
              {
                "lon": -122.2876,
                "lat": 37.7685,
                "value": "White"
              },
              {
                "lon": -122.2854,
                "lat": 37.7679,
                "value": "White"
              },
              {
                "lon": -122.2843,
                "lat": 37.7748,
                "value": "White"
              },
              {
                "lon": -122.2858,
                "lat": 37.7693,
                "value": "White"
              },
              {
                "lon": -122.2808,
                "lat": 37.7701,
                "value": "White"
              },
              {
                "lon": -122.289,
                "lat": 37.7688,
                "value": "Asian"
              },
              {
                "lon": -122.2855,
                "lat": 37.7733,
                "value": "Asian"
              },
              {
                "lon": -122.2681,
                "lat": 37.7695,
                "value": "White"
              },
              {
                "lon": -122.2666,
                "lat": 37.7698,
                "value": "White"
              },
              {
                "lon": -122.2751,
                "lat": 37.7749,
                "value": "White"
              },
              {
                "lon": -122.2658,
                "lat": 37.7738,
                "value": "White"
              },
              {
                "lon": -122.2667,
                "lat": 37.7746,
                "value": "Asian"
              },
              {
                "lon": -122.2589,
                "lat": 37.771,
                "value": "White"
              },
              {
                "lon": -122.2612,
                "lat": 37.7729,
                "value": "White"
              },
              {
                "lon": -122.2592,
                "lat": 37.7686,
                "value": "White"
              },
              {
                "lon": -122.2584,
                "lat": 37.77,
                "value": "White"
              },
              {
                "lon": -122.2601,
                "lat": 37.7696,
                "value": "Asian"
              },
              {
                "lon": -122.2604,
                "lat": 37.7697,
                "value": "Asian"
              },
              {
                "lon": -122.2601,
                "lat": 37.7702,
                "value": "Asian"
              },
              {
                "lon": -122.2567,
                "lat": 37.7714,
                "value": "Hispanic"
              },
              {
                "lon": -122.2506,
                "lat": 37.7681,
                "value": "White"
              },
              {
                "lon": -122.2506,
                "lat": 37.7681,
                "value": "Asian"
              },
              {
                "lon": -122.2436,
                "lat": 37.7642,
                "value": "Hispanic"
              },
              {
                "lon": -122.2246,
                "lat": 37.7549,
                "value": "White"
              },
              {
                "lon": -122.2368,
                "lat": 37.7643,
                "value": "White"
              },
              {
                "lon": -122.2411,
                "lat": 37.7634,
                "value": "White"
              },
              {
                "lon": -122.2362,
                "lat": 37.7633,
                "value": "White"
              },
              {
                "lon": -122.2367,
                "lat": 37.7596,
                "value": "Asian"
              },
              {
                "lon": -122.2306,
                "lat": 37.7566,
                "value": "Asian"
              },
              {
                "lon": -122.2383,
                "lat": 37.7589,
                "value": "White"
              },
              {
                "lon": -122.2403,
                "lat": 37.7549,
                "value": "White"
              },
              {
                "lon": -122.2375,
                "lat": 37.7487,
                "value": "White"
              },
              {
                "lon": -122.2478,
                "lat": 37.7581,
                "value": "White"
              },
              {
                "lon": -122.2462,
                "lat": 37.7543,
                "value": "White"
              },
              {
                "lon": -122.2401,
                "lat": 37.7579,
                "value": "White"
              },
              {
                "lon": -122.2403,
                "lat": 37.753,
                "value": "Asian"
              },
              {
                "lon": -122.2449,
                "lat": 37.749,
                "value": "Asian"
              },
              {
                "lon": -122.2364,
                "lat": 37.7575,
                "value": "Hispanic"
              },
              {
                "lon": -122.235,
                "lat": 37.748,
                "value": "White"
              },
              {
                "lon": -122.2293,
                "lat": 37.7382,
                "value": "White"
              },
              {
                "lon": -122.2366,
                "lat": 37.7434,
                "value": "White"
              },
              {
                "lon": -122.2527,
                "lat": 37.7346,
                "value": "White"
              },
              {
                "lon": -122.2387,
                "lat": 37.735,
                "value": "Asian"
              },
              {
                "lon": -122.2549,
                "lat": 37.7355,
                "value": "Asian"
              },
              {
                "lon": -122.2528,
                "lat": 37.7373,
                "value": "Asian"
              },
              {
                "lon": -122.2292,
                "lat": 37.7301,
                "value": "Asian"
              },
              {
                "lon": -122.2296,
                "lat": 37.7487,
                "value": "Asian"
              },
              {
                "lon": -122.2308,
                "lat": 37.7345,
                "value": "Hispanic"
              },
              {
                "lon": -122.2246,
                "lat": 37.7525,
                "value": "Hispanic"
              },
              {
                "lon": -122.2419,
                "lat": 37.7482,
                "value": "White"
              },
              {
                "lon": -122.2393,
                "lat": 37.7382,
                "value": "White"
              },
              {
                "lon": -122.244,
                "lat": 37.7475,
                "value": "White"
              },
              {
                "lon": -122.2588,
                "lat": 37.7444,
                "value": "White"
              },
              {
                "lon": -122.2411,
                "lat": 37.743,
                "value": "White"
              },
              {
                "lon": -122.2378,
                "lat": 37.7416,
                "value": "Asian"
              },
              {
                "lon": -122.2447,
                "lat": 37.7463,
                "value": "Asian"
              },
              {
                "lon": -122.2446,
                "lat": 37.7411,
                "value": "Asian"
              },
              {
                "lon": -122.2398,
                "lat": 37.7359,
                "value": "Asian"
              },
              {
                "lon": -122.2447,
                "lat": 37.7393,
                "value": "Asian"
              },
              {
                "lon": -122.2402,
                "lat": 37.741,
                "value": "Hispanic"
              },
              {
                "lon": -122.2471,
                "lat": 37.7608,
                "value": "White"
              },
              {
                "lon": -122.2483,
                "lat": 37.7591,
                "value": "White"
              },
              {
                "lon": -122.2534,
                "lat": 37.7612,
                "value": "White"
              },
              {
                "lon": -122.2491,
                "lat": 37.7622,
                "value": "Asian"
              },
              {
                "lon": -122.2536,
                "lat": 37.7573,
                "value": "Asian"
              },
              {
                "lon": -122.253,
                "lat": 37.7642,
                "value": "Hispanic"
              },
              {
                "lon": -122.261,
                "lat": 37.7633,
                "value": "White"
              },
              {
                "lon": -122.2616,
                "lat": 37.7608,
                "value": "White"
              },
              {
                "lon": -122.2602,
                "lat": 37.7622,
                "value": "White"
              },
              {
                "lon": -122.2577,
                "lat": 37.7622,
                "value": "Asian"
              },
              {
                "lon": -122.279,
                "lat": 37.768,
                "value": "White"
              },
              {
                "lon": -122.2745,
                "lat": 37.767,
                "value": "White"
              },
              {
                "lon": -122.2691,
                "lat": 37.7654,
                "value": "Asian"
              },
              {
                "lon": -122.2677,
                "lat": 37.7669,
                "value": "Asian"
              },
              {
                "lon": -122.2676,
                "lat": 37.7613,
                "value": "Hispanic"
              },
              {
                "lon": -122.3168,
                "lat": 37.7799,
                "value": "White"
              },
              {
                "lon": -122.2947,
                "lat": 37.7911,
                "value": "White"
              },
              {
                "lon": -122.3251,
                "lat": 37.7845,
                "value": "Black"
              },
              {
                "lon": -122.3169,
                "lat": 37.7908,
                "value": "Asian"
              },
              {
                "lon": -122.301,
                "lat": 37.7735,
                "value": "Asian"
              },
              {
                "lon": -122.3208,
                "lat": 37.7928,
                "value": "Asian"
              },
              {
                "lon": -122.3043,
                "lat": 37.7853,
                "value": "Hispanic"
              },
              {
                "lon": -122.0014,
                "lat": 37.7253,
                "value": "White"
              },
              {
                "lon": -122.0096,
                "lat": 37.7041,
                "value": "White"
              },
              {
                "lon": -122.0244,
                "lat": 37.7118,
                "value": "White"
              },
              {
                "lon": -121.9984,
                "lat": 37.7143,
                "value": "White"
              },
              {
                "lon": -122.0246,
                "lat": 37.7453,
                "value": "Asian"
              },
              {
                "lon": -122.0226,
                "lat": 37.7073,
                "value": "Asian"
              },
              {
                "lon": -121.9892,
                "lat": 37.7279,
                "value": "Asian"
              },
              {
                "lon": -122.0098,
                "lat": 37.7599,
                "value": "Asian"
              },
              {
                "lon": -122.0071,
                "lat": 37.7614,
                "value": "Asian"
              },
              {
                "lon": -121.9955,
                "lat": 37.7364,
                "value": "Asian"
              },
              {
                "lon": -122.0112,
                "lat": 37.7176,
                "value": "Hispanic"
              },
              {
                "lon": -122.1091,
                "lat": 37.7662,
                "value": "White"
              },
              {
                "lon": -122.05,
                "lat": 37.7677,
                "value": "White"
              },
              {
                "lon": -122.0743,
                "lat": 37.7711,
                "value": "Asian"
              },
              {
                "lon": -122.0736,
                "lat": 37.7048,
                "value": "White"
              },
              {
                "lon": -122.0639,
                "lat": 37.7186,
                "value": "White"
              },
              {
                "lon": -122.0656,
                "lat": 37.7121,
                "value": "White"
              },
              {
                "lon": -122.0597,
                "lat": 37.7278,
                "value": "White"
              },
              {
                "lon": -122.058,
                "lat": 37.7421,
                "value": "White"
              },
              {
                "lon": -122.0601,
                "lat": 37.7405,
                "value": "White"
              },
              {
                "lon": -122.0633,
                "lat": 37.723,
                "value": "White"
              },
              {
                "lon": -122.0537,
                "lat": 37.7282,
                "value": "Asian"
              },
              {
                "lon": -122.0565,
                "lat": 37.7341,
                "value": "Asian"
              },
              {
                "lon": -122.0526,
                "lat": 37.7248,
                "value": "Asian"
              },
              {
                "lon": -122.0695,
                "lat": 37.7166,
                "value": "Asian"
              },
              {
                "lon": -122.0574,
                "lat": 37.7175,
                "value": "Hispanic"
              },
              {
                "lon": -122.0787,
                "lat": 37.7194,
                "value": "White"
              },
              {
                "lon": -122.0808,
                "lat": 37.7173,
                "value": "White"
              },
              {
                "lon": -122.0801,
                "lat": 37.7231,
                "value": "White"
              },
              {
                "lon": -122.0913,
                "lat": 37.7275,
                "value": "Asian"
              },
              {
                "lon": -122.0837,
                "lat": 37.7133,
                "value": "Hispanic"
              },
              {
                "lon": -122.0936,
                "lat": 37.7198,
                "value": "White"
              },
              {
                "lon": -122.1062,
                "lat": 37.7185,
                "value": "White"
              },
              {
                "lon": -122.0923,
                "lat": 37.7187,
                "value": "Asian"
              },
              {
                "lon": -122.1183,
                "lat": 37.7061,
                "value": "White"
              },
              {
                "lon": -122.1131,
                "lat": 37.7132,
                "value": "White"
              },
              {
                "lon": -122.1079,
                "lat": 37.7084,
                "value": "Black"
              },
              {
                "lon": -122.1166,
                "lat": 37.7106,
                "value": "Black"
              },
              {
                "lon": -122.1115,
                "lat": 37.7128,
                "value": "Black"
              },
              {
                "lon": -122.1082,
                "lat": 37.7084,
                "value": "Asian"
              },
              {
                "lon": -122.1115,
                "lat": 37.705,
                "value": "Asian"
              },
              {
                "lon": -122.1066,
                "lat": 37.7001,
                "value": "Hispanic"
              },
              {
                "lon": -122.1078,
                "lat": 37.7038,
                "value": "Hispanic"
              },
              {
                "lon": -122.0905,
                "lat": 37.701,
                "value": "White"
              },
              {
                "lon": -122.1003,
                "lat": 37.705,
                "value": "White"
              },
              {
                "lon": -122.102,
                "lat": 37.7028,
                "value": "White"
              },
              {
                "lon": -122.0954,
                "lat": 37.7059,
                "value": "White"
              },
              {
                "lon": -122.0986,
                "lat": 37.6993,
                "value": "Asian"
              },
              {
                "lon": -122.1025,
                "lat": 37.7034,
                "value": "Asian"
              },
              {
                "lon": -122.0907,
                "lat": 37.7071,
                "value": "Asian"
              },
              {
                "lon": -122.0976,
                "lat": 37.7125,
                "value": "Asian"
              },
              {
                "lon": -122.0954,
                "lat": 37.7026,
                "value": "Asian"
              },
              {
                "lon": -122.1037,
                "lat": 37.7094,
                "value": "Asian"
              },
              {
                "lon": -122.0988,
                "lat": 37.7021,
                "value": "Hispanic"
              },
              {
                "lon": -122.0993,
                "lat": 37.7034,
                "value": "Hispanic"
              },
              {
                "lon": -122.0896,
                "lat": 37.7099,
                "value": "White"
              },
              {
                "lon": -122.0747,
                "lat": 37.7047,
                "value": "White"
              },
              {
                "lon": -122.0865,
                "lat": 37.7085,
                "value": "Asian"
              },
              {
                "lon": -122.0864,
                "lat": 37.7067,
                "value": "Asian"
              },
              {
                "lon": -122.0871,
                "lat": 37.7034,
                "value": "Hispanic"
              },
              {
                "lon": -122.0719,
                "lat": 37.7019,
                "value": "White"
              },
              {
                "lon": -122.0603,
                "lat": 37.7038,
                "value": "White"
              },
              {
                "lon": -122.0574,
                "lat": 37.7003,
                "value": "White"
              },
              {
                "lon": -122.0647,
                "lat": 37.7012,
                "value": "Asian"
              },
              {
                "lon": -122.0645,
                "lat": 37.6948,
                "value": "Asian"
              },
              {
                "lon": -122.0721,
                "lat": 37.6975,
                "value": "Asian"
              },
              {
                "lon": -122.0631,
                "lat": 37.704,
                "value": "Asian"
              },
              {
                "lon": -122.0662,
                "lat": 37.7006,
                "value": "Asian"
              },
              {
                "lon": -122.0586,
                "lat": 37.6956,
                "value": "Hispanic"
              },
              {
                "lon": -122.0669,
                "lat": 37.6995,
                "value": "Hispanic"
              },
              {
                "lon": -122.0786,
                "lat": 37.6985,
                "value": "White"
              },
              {
                "lon": -122.0895,
                "lat": 37.6963,
                "value": "White"
              },
              {
                "lon": -122.0909,
                "lat": 37.6999,
                "value": "Black"
              },
              {
                "lon": -122.0769,
                "lat": 37.696,
                "value": "Black"
              },
              {
                "lon": -122.0869,
                "lat": 37.7009,
                "value": "Asian"
              },
              {
                "lon": -122.0806,
                "lat": 37.6991,
                "value": "Asian"
              },
              {
                "lon": -122.0836,
                "lat": 37.6985,
                "value": "Hispanic"
              },
              {
                "lon": -122.0844,
                "lat": 37.7005,
                "value": "Hispanic"
              },
              {
                "lon": -122.0831,
                "lat": 37.6978,
                "value": "Hispanic"
              },
              {
                "lon": -122.0728,
                "lat": 37.6924,
                "value": "White"
              },
              {
                "lon": -122.0758,
                "lat": 37.6936,
                "value": "Asian"
              },
              {
                "lon": -122.0759,
                "lat": 37.6954,
                "value": "Hispanic"
              },
              {
                "lon": -122.0607,
                "lat": 37.6894,
                "value": "White"
              },
              {
                "lon": -122.0715,
                "lat": 37.682,
                "value": "White"
              },
              {
                "lon": -122.0643,
                "lat": 37.6884,
                "value": "Black"
              },
              {
                "lon": -122.0635,
                "lat": 37.6884,
                "value": "Asian"
              },
              {
                "lon": -122.0645,
                "lat": 37.689,
                "value": "Hispanic"
              },
              {
                "lon": -122.0856,
                "lat": 37.6857,
                "value": "White"
              },
              {
                "lon": -122.0836,
                "lat": 37.6783,
                "value": "White"
              },
              {
                "lon": -122.0818,
                "lat": 37.6789,
                "value": "White"
              },
              {
                "lon": -122.0799,
                "lat": 37.682,
                "value": "White"
              },
              {
                "lon": -122.0799,
                "lat": 37.6786,
                "value": "Black"
              },
              {
                "lon": -122.079,
                "lat": 37.6871,
                "value": "Asian"
              },
              {
                "lon": -122.0834,
                "lat": 37.6901,
                "value": "Hispanic"
              },
              {
                "lon": -122.0915,
                "lat": 37.6867,
                "value": "Hispanic"
              },
              {
                "lon": -122.1398,
                "lat": 37.7323,
                "value": "White"
              },
              {
                "lon": -122.1431,
                "lat": 37.7335,
                "value": "White"
              },
              {
                "lon": -122.1535,
                "lat": 37.7383,
                "value": "Black"
              },
              {
                "lon": -122.1493,
                "lat": 37.7329,
                "value": "Hispanic"
              },
              {
                "lon": -122.1416,
                "lat": 37.7364,
                "value": "Hispanic"
              },
              {
                "lon": -122.1553,
                "lat": 37.7323,
                "value": "White"
              },
              {
                "lon": -122.162,
                "lat": 37.7336,
                "value": "White"
              },
              {
                "lon": -122.1598,
                "lat": 37.7366,
                "value": "Asian"
              },
              {
                "lon": -122.1529,
                "lat": 37.7305,
                "value": "Hispanic"
              },
              {
                "lon": -122.1584,
                "lat": 37.729,
                "value": "Hispanic"
              },
              {
                "lon": -122.1517,
                "lat": 37.7341,
                "value": "Hispanic"
              },
              {
                "lon": -122.1656,
                "lat": 37.7372,
                "value": "White"
              },
              {
                "lon": -122.1677,
                "lat": 37.7364,
                "value": "White"
              },
              {
                "lon": -122.1692,
                "lat": 37.7321,
                "value": "Asian"
              },
              {
                "lon": -122.1666,
                "lat": 37.735,
                "value": "Asian"
              },
              {
                "lon": -122.1655,
                "lat": 37.727,
                "value": "Hispanic"
              },
              {
                "lon": -122.1655,
                "lat": 37.7278,
                "value": "Hispanic"
              },
              {
                "lon": -122.1635,
                "lat": 37.7329,
                "value": "Hispanic"
              },
              {
                "lon": -122.1836,
                "lat": 37.7077,
                "value": "White"
              },
              {
                "lon": -122.1867,
                "lat": 37.7189,
                "value": "Asian"
              },
              {
                "lon": -122.1904,
                "lat": 37.719,
                "value": "Asian"
              },
              {
                "lon": -122.1841,
                "lat": 37.7034,
                "value": "Hispanic"
              },
              {
                "lon": -122.2018,
                "lat": 37.707,
                "value": "Hispanic"
              },
              {
                "lon": -122.1822,
                "lat": 37.7001,
                "value": "Hispanic"
              },
              {
                "lon": -122.1859,
                "lat": 37.6979,
                "value": "Hispanic"
              },
              {
                "lon": -122.1929,
                "lat": 37.7156,
                "value": "Hispanic"
              },
              {
                "lon": -122.1934,
                "lat": 37.7124,
                "value": "Hispanic"
              },
              {
                "lon": -122.1662,
                "lat": 37.7205,
                "value": "White"
              },
              {
                "lon": -122.1718,
                "lat": 37.7175,
                "value": "Asian"
              },
              {
                "lon": -122.1721,
                "lat": 37.7171,
                "value": "Asian"
              },
              {
                "lon": -122.1609,
                "lat": 37.7184,
                "value": "Asian"
              },
              {
                "lon": -122.176,
                "lat": 37.7189,
                "value": "Asian"
              },
              {
                "lon": -122.1726,
                "lat": 37.7182,
                "value": "Hispanic"
              },
              {
                "lon": -122.1662,
                "lat": 37.7135,
                "value": "Hispanic"
              },
              {
                "lon": -122.1731,
                "lat": 37.7252,
                "value": "Black"
              },
              {
                "lon": -122.1724,
                "lat": 37.7234,
                "value": "Asian"
              },
              {
                "lon": -122.1774,
                "lat": 37.7252,
                "value": "Asian"
              },
              {
                "lon": -122.1713,
                "lat": 37.7231,
                "value": "Asian"
              },
              {
                "lon": -122.1745,
                "lat": 37.7255,
                "value": "Hispanic"
              },
              {
                "lon": -122.1747,
                "lat": 37.7199,
                "value": "Hispanic"
              },
              {
                "lon": -122.1762,
                "lat": 37.7254,
                "value": "Hispanic"
              },
              {
                "lon": -122.1569,
                "lat": 37.7169,
                "value": "White"
              },
              {
                "lon": -122.1544,
                "lat": 37.7215,
                "value": "Black"
              },
              {
                "lon": -122.1638,
                "lat": 37.7246,
                "value": "Asian"
              },
              {
                "lon": -122.1632,
                "lat": 37.7243,
                "value": "Asian"
              },
              {
                "lon": -122.1563,
                "lat": 37.7238,
                "value": "Hispanic"
              },
              {
                "lon": -122.1555,
                "lat": 37.7203,
                "value": "Hispanic"
              },
              {
                "lon": -122.1474,
                "lat": 37.7226,
                "value": "White"
              },
              {
                "lon": -122.1511,
                "lat": 37.726,
                "value": "Black"
              },
              {
                "lon": -122.1479,
                "lat": 37.7225,
                "value": "Asian"
              },
              {
                "lon": -122.1559,
                "lat": 37.7277,
                "value": "Hispanic"
              },
              {
                "lon": -122.1555,
                "lat": 37.725,
                "value": "Hispanic"
              },
              {
                "lon": -122.1445,
                "lat": 37.7221,
                "value": "White"
              },
              {
                "lon": -122.1469,
                "lat": 37.725,
                "value": "White"
              },
              {
                "lon": -122.1468,
                "lat": 37.7266,
                "value": "Asian"
              },
              {
                "lon": -122.1459,
                "lat": 37.7247,
                "value": "Hispanic"
              },
              {
                "lon": -122.1125,
                "lat": 37.7193,
                "value": "White"
              },
              {
                "lon": -122.1221,
                "lat": 37.7231,
                "value": "White"
              },
              {
                "lon": -122.1194,
                "lat": 37.723,
                "value": "White"
              },
              {
                "lon": -122.1162,
                "lat": 37.7172,
                "value": "Asian"
              },
              {
                "lon": -122.1147,
                "lat": 37.7156,
                "value": "Asian"
              },
              {
                "lon": -122.1286,
                "lat": 37.7289,
                "value": "Hispanic"
              },
              {
                "lon": -122.1354,
                "lat": 37.7193,
                "value": "White"
              },
              {
                "lon": -122.1287,
                "lat": 37.7067,
                "value": "White"
              },
              {
                "lon": -122.1312,
                "lat": 37.7114,
                "value": "Asian"
              },
              {
                "lon": -122.1362,
                "lat": 37.7211,
                "value": "Asian"
              },
              {
                "lon": -122.1333,
                "lat": 37.7147,
                "value": "Hispanic"
              },
              {
                "lon": -122.1276,
                "lat": 37.6992,
                "value": "Asian"
              },
              {
                "lon": -122.1333,
                "lat": 37.7067,
                "value": "Asian"
              },
              {
                "lon": -122.1395,
                "lat": 37.7019,
                "value": "Asian"
              },
              {
                "lon": -122.1393,
                "lat": 37.7027,
                "value": "Asian"
              },
              {
                "lon": -122.1242,
                "lat": 37.7009,
                "value": "Hispanic"
              },
              {
                "lon": -122.1336,
                "lat": 37.7096,
                "value": "White"
              },
              {
                "lon": -122.1355,
                "lat": 37.7109,
                "value": "Asian"
              },
              {
                "lon": -122.1313,
                "lat": 37.709,
                "value": "Hispanic"
              },
              {
                "lon": -122.1372,
                "lat": 37.7091,
                "value": "Hispanic"
              },
              {
                "lon": -122.1524,
                "lat": 37.7158,
                "value": "White"
              },
              {
                "lon": -122.1504,
                "lat": 37.7139,
                "value": "Black"
              },
              {
                "lon": -122.1443,
                "lat": 37.7151,
                "value": "Asian"
              },
              {
                "lon": -122.1446,
                "lat": 37.7134,
                "value": "Hispanic"
              },
              {
                "lon": -122.1448,
                "lat": 37.719,
                "value": "Hispanic"
              },
              {
                "lon": -122.1448,
                "lat": 37.7177,
                "value": "Hispanic"
              },
              {
                "lon": -122.1527,
                "lat": 37.7016,
                "value": "White"
              },
              {
                "lon": -122.1483,
                "lat": 37.7066,
                "value": "Black"
              },
              {
                "lon": -122.1605,
                "lat": 37.7129,
                "value": "Asian"
              },
              {
                "lon": -122.1574,
                "lat": 37.7082,
                "value": "Asian"
              },
              {
                "lon": -122.1442,
                "lat": 37.6969,
                "value": "Asian"
              },
              {
                "lon": -122.1538,
                "lat": 37.7022,
                "value": "Asian"
              },
              {
                "lon": -122.1468,
                "lat": 37.7005,
                "value": "Asian"
              },
              {
                "lon": -122.1502,
                "lat": 37.7054,
                "value": "Asian"
              },
              {
                "lon": -122.1508,
                "lat": 37.7093,
                "value": "Hispanic"
              },
              {
                "lon": -122.1472,
                "lat": 37.7036,
                "value": "Hispanic"
              },
              {
                "lon": -122.1502,
                "lat": 37.7092,
                "value": "Hispanic"
              },
              {
                "lon": -122.1405,
                "lat": 37.6987,
                "value": "Hispanic"
              },
              {
                "lon": -122.1387,
                "lat": 37.6912,
                "value": "Hispanic"
              },
              {
                "lon": -122.1376,
                "lat": 37.6909,
                "value": "Hispanic"
              },
              {
                "lon": -122.1559,
                "lat": 37.6941,
                "value": "White"
              },
              {
                "lon": -122.1573,
                "lat": 37.6967,
                "value": "White"
              },
              {
                "lon": -122.1513,
                "lat": 37.6975,
                "value": "Asian"
              },
              {
                "lon": -122.161,
                "lat": 37.6961,
                "value": "Asian"
              },
              {
                "lon": -122.1627,
                "lat": 37.6998,
                "value": "Asian"
              },
              {
                "lon": -122.1637,
                "lat": 37.7002,
                "value": "Asian"
              },
              {
                "lon": -122.1618,
                "lat": 37.7004,
                "value": "Asian"
              },
              {
                "lon": -122.1459,
                "lat": 37.6923,
                "value": "Asian"
              },
              {
                "lon": -122.1449,
                "lat": 37.6953,
                "value": "Asian"
              },
              {
                "lon": -122.1583,
                "lat": 37.6994,
                "value": "Hispanic"
              },
              {
                "lon": -122.1503,
                "lat": 37.6943,
                "value": "Hispanic"
              },
              {
                "lon": -122.1653,
                "lat": 37.7029,
                "value": "Hispanic"
              },
              {
                "lon": -122.1637,
                "lat": 37.6806,
                "value": "White"
              },
              {
                "lon": -122.1609,
                "lat": 37.6771,
                "value": "Asian"
              },
              {
                "lon": -122.1597,
                "lat": 37.674,
                "value": "Asian"
              },
              {
                "lon": -122.172,
                "lat": 37.6844,
                "value": "Asian"
              },
              {
                "lon": -122.1728,
                "lat": 37.6979,
                "value": "Asian"
              },
              {
                "lon": -122.1651,
                "lat": 37.6785,
                "value": "Asian"
              },
              {
                "lon": -122.1755,
                "lat": 37.6848,
                "value": "Asian"
              },
              {
                "lon": -122.1606,
                "lat": 37.6851,
                "value": "Asian"
              },
              {
                "lon": -122.1569,
                "lat": 37.6903,
                "value": "White"
              },
              {
                "lon": -122.1548,
                "lat": 37.6883,
                "value": "White"
              },
              {
                "lon": -122.1552,
                "lat": 37.68,
                "value": "Asian"
              },
              {
                "lon": -122.1558,
                "lat": 37.6768,
                "value": "Asian"
              },
              {
                "lon": -122.1553,
                "lat": 37.6763,
                "value": "Asian"
              },
              {
                "lon": -122.1591,
                "lat": 37.6872,
                "value": "Asian"
              },
              {
                "lon": -122.1573,
                "lat": 37.6862,
                "value": "Hispanic"
              },
              {
                "lon": -122.1462,
                "lat": 37.6863,
                "value": "White"
              },
              {
                "lon": -122.1469,
                "lat": 37.6909,
                "value": "White"
              },
              {
                "lon": -122.1357,
                "lat": 37.6867,
                "value": "White"
              },
              {
                "lon": -122.1429,
                "lat": 37.6839,
                "value": "Asian"
              },
              {
                "lon": -122.145,
                "lat": 37.6896,
                "value": "Asian"
              },
              {
                "lon": -122.1471,
                "lat": 37.6809,
                "value": "Asian"
              },
              {
                "lon": -122.1457,
                "lat": 37.6856,
                "value": "Asian"
              },
              {
                "lon": -122.1506,
                "lat": 37.6846,
                "value": "Asian"
              },
              {
                "lon": -122.1494,
                "lat": 37.6814,
                "value": "Hispanic"
              },
              {
                "lon": -122.1243,
                "lat": 37.6892,
                "value": "Asian"
              },
              {
                "lon": -122.1111,
                "lat": 37.6861,
                "value": "Hispanic"
              },
              {
                "lon": -122.1168,
                "lat": 37.6878,
                "value": "Hispanic"
              },
              {
                "lon": -122.1195,
                "lat": 37.687,
                "value": "Hispanic"
              },
              {
                "lon": -122.1209,
                "lat": 37.7038,
                "value": "Black"
              },
              {
                "lon": -122.1265,
                "lat": 37.7054,
                "value": "Asian"
              },
              {
                "lon": -122.125,
                "lat": 37.706,
                "value": "Hispanic"
              },
              {
                "lon": -122.1258,
                "lat": 37.707,
                "value": "Hispanic"
              },
              {
                "lon": -122.1211,
                "lat": 37.6964,
                "value": "Asian"
              },
              {
                "lon": -122.1202,
                "lat": 37.6977,
                "value": "Asian"
              },
              {
                "lon": -122.1192,
                "lat": 37.693,
                "value": "Asian"
              },
              {
                "lon": -122.1252,
                "lat": 37.6941,
                "value": "Hispanic"
              },
              {
                "lon": -122.1196,
                "lat": 37.6927,
                "value": "Hispanic"
              },
              {
                "lon": -122.1161,
                "lat": 37.6979,
                "value": "Black"
              },
              {
                "lon": -122.1167,
                "lat": 37.6985,
                "value": "Black"
              },
              {
                "lon": -122.1119,
                "lat": 37.6973,
                "value": "Black"
              },
              {
                "lon": -122.1143,
                "lat": 37.6966,
                "value": "Black"
              },
              {
                "lon": -122.1124,
                "lat": 37.695,
                "value": "Asian"
              },
              {
                "lon": -122.1113,
                "lat": 37.7001,
                "value": "Hispanic"
              },
              {
                "lon": -122.1108,
                "lat": 37.6964,
                "value": "Hispanic"
              },
              {
                "lon": -122.1181,
                "lat": 37.7015,
                "value": "Hispanic"
              },
              {
                "lon": -122.1105,
                "lat": 37.698,
                "value": "Hispanic"
              },
              {
                "lon": -122.1122,
                "lat": 37.7015,
                "value": "Hispanic"
              },
              {
                "lon": -122.1123,
                "lat": 37.6987,
                "value": "Hispanic"
              },
              {
                "lon": -122.1169,
                "lat": 37.6937,
                "value": "White"
              },
              {
                "lon": -122.1068,
                "lat": 37.6913,
                "value": "Black"
              },
              {
                "lon": -122.1117,
                "lat": 37.6898,
                "value": "Asian"
              },
              {
                "lon": -122.1148,
                "lat": 37.6892,
                "value": "Hispanic"
              },
              {
                "lon": -122.1059,
                "lat": 37.6936,
                "value": "Hispanic"
              },
              {
                "lon": -122.1188,
                "lat": 37.6927,
                "value": "Hispanic"
              },
              {
                "lon": -122.114,
                "lat": 37.6926,
                "value": "Hispanic"
              },
              {
                "lon": -122.1186,
                "lat": 37.6896,
                "value": "Hispanic"
              },
              {
                "lon": -122.061,
                "lat": 37.661,
                "value": "White"
              },
              {
                "lon": -122.0337,
                "lat": 37.6518,
                "value": "White"
              },
              {
                "lon": -122.0484,
                "lat": 37.6468,
                "value": "Black"
              },
              {
                "lon": -122.0275,
                "lat": 37.6548,
                "value": "Asian"
              },
              {
                "lon": -122.042,
                "lat": 37.6503,
                "value": "Asian"
              },
              {
                "lon": -122.039,
                "lat": 37.6519,
                "value": "Hispanic"
              },
              {
                "lon": -122.0527,
                "lat": 37.6496,
                "value": "Hispanic"
              },
              {
                "lon": -122.0334,
                "lat": 37.6837,
                "value": "White"
              },
              {
                "lon": -122.0042,
                "lat": 37.6853,
                "value": "White"
              },
              {
                "lon": -121.9815,
                "lat": 37.6725,
                "value": "White"
              },
              {
                "lon": -122.0127,
                "lat": 37.6623,
                "value": "White"
              },
              {
                "lon": -121.9187,
                "lat": 37.6105,
                "value": "Asian"
              },
              {
                "lon": -121.9299,
                "lat": 37.6026,
                "value": "Asian"
              },
              {
                "lon": -122.0079,
                "lat": 37.6297,
                "value": "Asian"
              },
              {
                "lon": -121.9941,
                "lat": 37.6584,
                "value": "Asian"
              },
              {
                "lon": -121.9425,
                "lat": 37.6181,
                "value": "Asian"
              },
              {
                "lon": -121.9418,
                "lat": 37.6423,
                "value": "Asian"
              },
              {
                "lon": -121.9223,
                "lat": 37.6099,
                "value": "Hispanic"
              },
              {
                "lon": -122.0299,
                "lat": 37.6341,
                "value": "White"
              },
              {
                "lon": -122.0558,
                "lat": 37.6462,
                "value": "Black"
              },
              {
                "lon": -122.026,
                "lat": 37.629,
                "value": "Asian"
              },
              {
                "lon": -122.0298,
                "lat": 37.6437,
                "value": "Asian"
              },
              {
                "lon": -122.0582,
                "lat": 37.6469,
                "value": "Asian"
              },
              {
                "lon": -122.0275,
                "lat": 37.6392,
                "value": "Asian"
              },
              {
                "lon": -122.0199,
                "lat": 37.6341,
                "value": "Asian"
              },
              {
                "lon": -122.0474,
                "lat": 37.6466,
                "value": "Hispanic"
              },
              {
                "lon": -122.0503,
                "lat": 37.6349,
                "value": "Hispanic"
              },
              {
                "lon": -122.0496,
                "lat": 37.6444,
                "value": "Hispanic"
              },
              {
                "lon": -122.0525,
                "lat": 37.6834,
                "value": "White"
              },
              {
                "lon": -122.0437,
                "lat": 37.6761,
                "value": "White"
              },
              {
                "lon": -122.0477,
                "lat": 37.6786,
                "value": "Black"
              },
              {
                "lon": -122.0519,
                "lat": 37.6807,
                "value": "Asian"
              },
              {
                "lon": -122.053,
                "lat": 37.6873,
                "value": "Asian"
              },
              {
                "lon": -122.0545,
                "lat": 37.6871,
                "value": "Hispanic"
              },
              {
                "lon": -122.044,
                "lat": 37.6762,
                "value": "Hispanic"
              },
              {
                "lon": -122.0656,
                "lat": 37.6814,
                "value": "White"
              },
              {
                "lon": -122.0673,
                "lat": 37.6828,
                "value": "White"
              },
              {
                "lon": -122.0545,
                "lat": 37.6841,
                "value": "Black"
              },
              {
                "lon": -122.0639,
                "lat": 37.6797,
                "value": "Asian"
              },
              {
                "lon": -122.0668,
                "lat": 37.6824,
                "value": "Asian"
              },
              {
                "lon": -122.0735,
                "lat": 37.6808,
                "value": "Hispanic"
              },
              {
                "lon": -122.07,
                "lat": 37.6777,
                "value": "Hispanic"
              },
              {
                "lon": -122.0742,
                "lat": 37.6768,
                "value": "Hispanic"
              },
              {
                "lon": -122.0782,
                "lat": 37.6758,
                "value": "White"
              },
              {
                "lon": -122.087,
                "lat": 37.6734,
                "value": "White"
              },
              {
                "lon": -122.0794,
                "lat": 37.6721,
                "value": "Black"
              },
              {
                "lon": -122.0785,
                "lat": 37.6724,
                "value": "Asian"
              },
              {
                "lon": -122.0859,
                "lat": 37.669,
                "value": "Hispanic"
              },
              {
                "lon": -122.0849,
                "lat": 37.6767,
                "value": "Hispanic"
              },
              {
                "lon": -122.0771,
                "lat": 37.6782,
                "value": "Hispanic"
              },
              {
                "lon": -122.0947,
                "lat": 37.6828,
                "value": "White"
              },
              {
                "lon": -122.0929,
                "lat": 37.6792,
                "value": "White"
              },
              {
                "lon": -122.0992,
                "lat": 37.6861,
                "value": "Hispanic"
              },
              {
                "lon": -122.0923,
                "lat": 37.6796,
                "value": "Hispanic"
              },
              {
                "lon": -122.0959,
                "lat": 37.6761,
                "value": "Hispanic"
              },
              {
                "lon": -122.1015,
                "lat": 37.6791,
                "value": "White"
              },
              {
                "lon": -122.1039,
                "lat": 37.672,
                "value": "Asian"
              },
              {
                "lon": -122.1023,
                "lat": 37.6757,
                "value": "Hispanic"
              },
              {
                "lon": -122.1015,
                "lat": 37.676,
                "value": "Hispanic"
              },
              {
                "lon": -122.1005,
                "lat": 37.6763,
                "value": "Hispanic"
              },
              {
                "lon": -122.1006,
                "lat": 37.6737,
                "value": "Hispanic"
              },
              {
                "lon": -122.1056,
                "lat": 37.6715,
                "value": "Hispanic"
              },
              {
                "lon": -122.1086,
                "lat": 37.681,
                "value": "White"
              },
              {
                "lon": -122.1103,
                "lat": 37.6785,
                "value": "Black"
              },
              {
                "lon": -122.104,
                "lat": 37.6801,
                "value": "Asian"
              },
              {
                "lon": -122.0999,
                "lat": 37.6832,
                "value": "Hispanic"
              },
              {
                "lon": -122.1094,
                "lat": 37.6815,
                "value": "Hispanic"
              },
              {
                "lon": -122.1051,
                "lat": 37.6802,
                "value": "Hispanic"
              },
              {
                "lon": -122.1097,
                "lat": 37.6843,
                "value": "Hispanic"
              },
              {
                "lon": -122.1125,
                "lat": 37.6826,
                "value": "Hispanic"
              },
              {
                "lon": -122.112,
                "lat": 37.676,
                "value": "White"
              },
              {
                "lon": -122.1261,
                "lat": 37.6839,
                "value": "Asian"
              },
              {
                "lon": -122.1235,
                "lat": 37.6838,
                "value": "Hispanic"
              },
              {
                "lon": -122.119,
                "lat": 37.679,
                "value": "Hispanic"
              },
              {
                "lon": -122.1177,
                "lat": 37.684,
                "value": "Hispanic"
              },
              {
                "lon": -122.1084,
                "lat": 37.6735,
                "value": "Hispanic"
              },
              {
                "lon": -122.1291,
                "lat": 37.6785,
                "value": "White"
              },
              {
                "lon": -122.1348,
                "lat": 37.6832,
                "value": "White"
              },
              {
                "lon": -122.1284,
                "lat": 37.6824,
                "value": "Asian"
              },
              {
                "lon": -122.1335,
                "lat": 37.6771,
                "value": "Asian"
              },
              {
                "lon": -122.1334,
                "lat": 37.6745,
                "value": "Asian"
              },
              {
                "lon": -122.1324,
                "lat": 37.6788,
                "value": "Asian"
              },
              {
                "lon": -122.1338,
                "lat": 37.6763,
                "value": "Hispanic"
              },
              {
                "lon": -122.1292,
                "lat": 37.6834,
                "value": "Hispanic"
              },
              {
                "lon": -122.1346,
                "lat": 37.6776,
                "value": "Hispanic"
              },
              {
                "lon": -122.1323,
                "lat": 37.6828,
                "value": "Hispanic"
              },
              {
                "lon": -122.1532,
                "lat": 37.6639,
                "value": "White"
              },
              {
                "lon": -122.1557,
                "lat": 37.664,
                "value": "White"
              },
              {
                "lon": -122.1551,
                "lat": 37.6671,
                "value": "Asian"
              },
              {
                "lon": -122.1508,
                "lat": 37.6765,
                "value": "Asian"
              },
              {
                "lon": -122.1456,
                "lat": 37.6698,
                "value": "Asian"
              },
              {
                "lon": -122.1501,
                "lat": 37.6745,
                "value": "Asian"
              },
              {
                "lon": -122.1445,
                "lat": 37.6751,
                "value": "Hispanic"
              },
              {
                "lon": -122.1469,
                "lat": 37.6707,
                "value": "Hispanic"
              },
              {
                "lon": -122.1485,
                "lat": 37.6713,
                "value": "Hispanic"
              },
              {
                "lon": -122.1352,
                "lat": 37.6652,
                "value": "White"
              },
              {
                "lon": -122.1358,
                "lat": 37.6688,
                "value": "White"
              },
              {
                "lon": -122.1325,
                "lat": 37.6711,
                "value": "Asian"
              },
              {
                "lon": -122.1329,
                "lat": 37.6666,
                "value": "Asian"
              },
              {
                "lon": -122.1402,
                "lat": 37.6699,
                "value": "Hispanic"
              },
              {
                "lon": -122.1374,
                "lat": 37.6654,
                "value": "Hispanic"
              },
              {
                "lon": -122.1372,
                "lat": 37.6733,
                "value": "Hispanic"
              },
              {
                "lon": -122.1246,
                "lat": 37.6719,
                "value": "White"
              },
              {
                "lon": -122.1297,
                "lat": 37.672,
                "value": "Asian"
              },
              {
                "lon": -122.1247,
                "lat": 37.6745,
                "value": "Asian"
              },
              {
                "lon": -122.1165,
                "lat": 37.6746,
                "value": "Asian"
              },
              {
                "lon": -122.1293,
                "lat": 37.6689,
                "value": "Hispanic"
              },
              {
                "lon": -122.1176,
                "lat": 37.6724,
                "value": "Hispanic"
              },
              {
                "lon": -122.1312,
                "lat": 37.6694,
                "value": "Hispanic"
              },
              {
                "lon": -122.123,
                "lat": 37.6709,
                "value": "Hispanic"
              },
              {
                "lon": -122.115,
                "lat": 37.6702,
                "value": "Black"
              },
              {
                "lon": -122.1096,
                "lat": 37.6703,
                "value": "Hispanic"
              },
              {
                "lon": -122.1114,
                "lat": 37.6691,
                "value": "Hispanic"
              },
              {
                "lon": -122.1132,
                "lat": 37.6686,
                "value": "Hispanic"
              },
              {
                "lon": -122.1146,
                "lat": 37.668,
                "value": "Hispanic"
              },
              {
                "lon": -122.0946,
                "lat": 37.674,
                "value": "Asian"
              },
              {
                "lon": -122.092,
                "lat": 37.6625,
                "value": "Asian"
              },
              {
                "lon": -122.0918,
                "lat": 37.661,
                "value": "Asian"
              },
              {
                "lon": -122.0925,
                "lat": 37.6612,
                "value": "Hispanic"
              },
              {
                "lon": -122.0947,
                "lat": 37.6715,
                "value": "Hispanic"
              },
              {
                "lon": -122.094,
                "lat": 37.6737,
                "value": "Hispanic"
              },
              {
                "lon": -122.0945,
                "lat": 37.6707,
                "value": "Hispanic"
              },
              {
                "lon": -122.0888,
                "lat": 37.6686,
                "value": "White"
              },
              {
                "lon": -122.0829,
                "lat": 37.6664,
                "value": "Asian"
              },
              {
                "lon": -122.0884,
                "lat": 37.6632,
                "value": "Hispanic"
              },
              {
                "lon": -122.0884,
                "lat": 37.663,
                "value": "Hispanic"
              },
              {
                "lon": -122.086,
                "lat": 37.6658,
                "value": "Hispanic"
              },
              {
                "lon": -122.0435,
                "lat": 37.6615,
                "value": "White"
              },
              {
                "lon": -122.0452,
                "lat": 37.6694,
                "value": "White"
              },
              {
                "lon": -122.044,
                "lat": 37.6744,
                "value": "Hispanic"
              },
              {
                "lon": -122.0693,
                "lat": 37.6657,
                "value": "White"
              },
              {
                "lon": -122.077,
                "lat": 37.6652,
                "value": "White"
              },
              {
                "lon": -122.0639,
                "lat": 37.6682,
                "value": "Asian"
              },
              {
                "lon": -122.0668,
                "lat": 37.6766,
                "value": "Hispanic"
              },
              {
                "lon": -122.0694,
                "lat": 37.6766,
                "value": "Hispanic"
              },
              {
                "lon": -122.0614,
                "lat": 37.6679,
                "value": "White"
              },
              {
                "lon": -122.0723,
                "lat": 37.6732,
                "value": "White"
              },
              {
                "lon": -122.0574,
                "lat": 37.6677,
                "value": "White"
              },
              {
                "lon": -122.0528,
                "lat": 37.6701,
                "value": "Asian"
              },
              {
                "lon": -122.0536,
                "lat": 37.6763,
                "value": "Hispanic"
              },
              {
                "lon": -122.065,
                "lat": 37.6553,
                "value": "White"
              },
              {
                "lon": -122.0668,
                "lat": 37.6599,
                "value": "Black"
              },
              {
                "lon": -122.0716,
                "lat": 37.6538,
                "value": "Asian"
              },
              {
                "lon": -122.0737,
                "lat": 37.6603,
                "value": "Hispanic"
              },
              {
                "lon": -122.0675,
                "lat": 37.6574,
                "value": "Hispanic"
              },
              {
                "lon": -122.0677,
                "lat": 37.6598,
                "value": "Hispanic"
              },
              {
                "lon": -122.062,
                "lat": 37.658,
                "value": "Hispanic"
              },
              {
                "lon": -122.0718,
                "lat": 37.6552,
                "value": "Hispanic"
              },
              {
                "lon": -122.0822,
                "lat": 37.6608,
                "value": "White"
              },
              {
                "lon": -122.084,
                "lat": 37.6601,
                "value": "Black"
              },
              {
                "lon": -122.0714,
                "lat": 37.6515,
                "value": "Asian"
              },
              {
                "lon": -122.0841,
                "lat": 37.6612,
                "value": "Asian"
              },
              {
                "lon": -122.0747,
                "lat": 37.655,
                "value": "Hispanic"
              },
              {
                "lon": -122.077,
                "lat": 37.6568,
                "value": "Hispanic"
              },
              {
                "lon": -122.071,
                "lat": 37.651,
                "value": "Hispanic"
              },
              {
                "lon": -122.0821,
                "lat": 37.6626,
                "value": "Hispanic"
              },
              {
                "lon": -122.082,
                "lat": 37.6582,
                "value": "Hispanic"
              },
              {
                "lon": -122.0772,
                "lat": 37.6516,
                "value": "Hispanic"
              },
              {
                "lon": -122.082,
                "lat": 37.6606,
                "value": "Hispanic"
              },
              {
                "lon": -122.0798,
                "lat": 37.6539,
                "value": "Hispanic"
              },
              {
                "lon": -122.0776,
                "lat": 37.6502,
                "value": "Black"
              },
              {
                "lon": -122.0876,
                "lat": 37.6535,
                "value": "Asian"
              },
              {
                "lon": -122.0903,
                "lat": 37.6504,
                "value": "Asian"
              },
              {
                "lon": -122.0841,
                "lat": 37.6545,
                "value": "Hispanic"
              },
              {
                "lon": -122.0813,
                "lat": 37.6497,
                "value": "Hispanic"
              },
              {
                "lon": -122.0816,
                "lat": 37.6544,
                "value": "Hispanic"
              },
              {
                "lon": -122.082,
                "lat": 37.6528,
                "value": "Hispanic"
              },
              {
                "lon": -122.1033,
                "lat": 37.6659,
                "value": "Black"
              },
              {
                "lon": -122.1047,
                "lat": 37.6623,
                "value": "Asian"
              },
              {
                "lon": -122.099,
                "lat": 37.6579,
                "value": "Asian"
              },
              {
                "lon": -122.0954,
                "lat": 37.662,
                "value": "Hispanic"
              },
              {
                "lon": -122.0992,
                "lat": 37.6592,
                "value": "Hispanic"
              },
              {
                "lon": -122.1002,
                "lat": 37.6547,
                "value": "Asian"
              },
              {
                "lon": -122.0936,
                "lat": 37.6523,
                "value": "Asian"
              },
              {
                "lon": -122.0889,
                "lat": 37.6556,
                "value": "Hispanic"
              },
              {
                "lon": -122.0927,
                "lat": 37.6548,
                "value": "Hispanic"
              },
              {
                "lon": -122.0929,
                "lat": 37.6479,
                "value": "Hispanic"
              },
              {
                "lon": -122.0976,
                "lat": 37.6528,
                "value": "Hispanic"
              },
              {
                "lon": -122.1136,
                "lat": 37.66,
                "value": "Asian"
              },
              {
                "lon": -122.1075,
                "lat": 37.6552,
                "value": "Asian"
              },
              {
                "lon": -122.1088,
                "lat": 37.6625,
                "value": "Hispanic"
              },
              {
                "lon": -122.1113,
                "lat": 37.666,
                "value": "Hispanic"
              },
              {
                "lon": -122.1152,
                "lat": 37.6655,
                "value": "Hispanic"
              },
              {
                "lon": -122.1093,
                "lat": 37.6615,
                "value": "Hispanic"
              },
              {
                "lon": -122.1079,
                "lat": 37.6606,
                "value": "Hispanic"
              },
              {
                "lon": -122.1088,
                "lat": 37.6651,
                "value": "Hispanic"
              },
              {
                "lon": -122.1155,
                "lat": 37.6634,
                "value": "Hispanic"
              },
              {
                "lon": -122.108,
                "lat": 37.6579,
                "value": "Hispanic"
              },
              {
                "lon": -122.1036,
                "lat": 37.6584,
                "value": "Hispanic"
              },
              {
                "lon": -122.1087,
                "lat": 37.6506,
                "value": "White"
              },
              {
                "lon": -122.0984,
                "lat": 37.6421,
                "value": "Asian"
              },
              {
                "lon": -122.0974,
                "lat": 37.6422,
                "value": "Asian"
              },
              {
                "lon": -122.1012,
                "lat": 37.6474,
                "value": "Hispanic"
              },
              {
                "lon": -122.107,
                "lat": 37.6512,
                "value": "Hispanic"
              },
              {
                "lon": -122.1078,
                "lat": 37.603,
                "value": "White"
              },
              {
                "lon": -122.1126,
                "lat": 37.6037,
                "value": "Black"
              },
              {
                "lon": -122.1434,
                "lat": 37.6123,
                "value": "Asian"
              },
              {
                "lon": -122.1022,
                "lat": 37.6031,
                "value": "Asian"
              },
              {
                "lon": -122.1131,
                "lat": 37.5813,
                "value": "Asian"
              },
              {
                "lon": -122.1296,
                "lat": 37.6482,
                "value": "Asian"
              },
              {
                "lon": -122.1065,
                "lat": 37.602,
                "value": "Asian"
              },
              {
                "lon": -122.1432,
                "lat": 37.62,
                "value": "Asian"
              },
              {
                "lon": -122.1303,
                "lat": 37.61,
                "value": "Asian"
              },
              {
                "lon": -122.1057,
                "lat": 37.6267,
                "value": "Asian"
              },
              {
                "lon": -122.1258,
                "lat": 37.5989,
                "value": "Hispanic"
              },
              {
                "lon": -122.1131,
                "lat": 37.5735,
                "value": "Hispanic"
              },
              {
                "lon": -122.1317,
                "lat": 37.6623,
                "value": "Hispanic"
              },
              {
                "lon": -122.102,
                "lat": 37.6343,
                "value": "Asian"
              },
              {
                "lon": -122.0977,
                "lat": 37.6288,
                "value": "Asian"
              },
              {
                "lon": -122.1048,
                "lat": 37.6322,
                "value": "Hispanic"
              },
              {
                "lon": -122.0939,
                "lat": 37.6259,
                "value": "Hispanic"
              },
              {
                "lon": -122.0999,
                "lat": 37.6308,
                "value": "Hispanic"
              },
              {
                "lon": -122.1114,
                "lat": 37.6397,
                "value": "White"
              },
              {
                "lon": -122.1134,
                "lat": 37.6521,
                "value": "Black"
              },
              {
                "lon": -122.1165,
                "lat": 37.646,
                "value": "Asian"
              },
              {
                "lon": -122.1093,
                "lat": 37.649,
                "value": "Asian"
              },
              {
                "lon": -122.1125,
                "lat": 37.6396,
                "value": "Asian"
              },
              {
                "lon": -122.1162,
                "lat": 37.6518,
                "value": "Asian"
              },
              {
                "lon": -122.1077,
                "lat": 37.6346,
                "value": "Asian"
              },
              {
                "lon": -122.1074,
                "lat": 37.6367,
                "value": "Asian"
              },
              {
                "lon": -122.1165,
                "lat": 37.6406,
                "value": "Hispanic"
              },
              {
                "lon": -122.1121,
                "lat": 37.6513,
                "value": "Hispanic"
              },
              {
                "lon": -122.1197,
                "lat": 37.6494,
                "value": "Hispanic"
              },
              {
                "lon": -122.1172,
                "lat": 37.6416,
                "value": "Hispanic"
              },
              {
                "lon": -122.11,
                "lat": 37.6509,
                "value": "Hispanic"
              },
              {
                "lon": -122.1198,
                "lat": 37.6531,
                "value": "Hispanic"
              },
              {
                "lon": -122.0929,
                "lat": 37.6348,
                "value": "Asian"
              },
              {
                "lon": -122.0975,
                "lat": 37.6334,
                "value": "Asian"
              },
              {
                "lon": -122.0918,
                "lat": 37.6378,
                "value": "Hispanic"
              },
              {
                "lon": -122.0961,
                "lat": 37.6363,
                "value": "Hispanic"
              },
              {
                "lon": -122.0881,
                "lat": 37.6419,
                "value": "White"
              },
              {
                "lon": -122.0925,
                "lat": 37.6456,
                "value": "Asian"
              },
              {
                "lon": -122.0901,
                "lat": 37.64,
                "value": "Hispanic"
              },
              {
                "lon": -122.0922,
                "lat": 37.6439,
                "value": "Hispanic"
              },
              {
                "lon": -122.0915,
                "lat": 37.6471,
                "value": "Hispanic"
              },
              {
                "lon": -122.08,
                "lat": 37.6467,
                "value": "Asian"
              },
              {
                "lon": -122.0762,
                "lat": 37.6449,
                "value": "Hispanic"
              },
              {
                "lon": -122.0766,
                "lat": 37.6412,
                "value": "Hispanic"
              },
              {
                "lon": -122.0812,
                "lat": 37.6424,
                "value": "Hispanic"
              },
              {
                "lon": -122.0729,
                "lat": 37.6426,
                "value": "Hispanic"
              },
              {
                "lon": -122.0816,
                "lat": 37.6427,
                "value": "Hispanic"
              },
              {
                "lon": -122.085,
                "lat": 37.6338,
                "value": "Asian"
              },
              {
                "lon": -122.0765,
                "lat": 37.6357,
                "value": "Asian"
              },
              {
                "lon": -122.0758,
                "lat": 37.6334,
                "value": "Hispanic"
              },
              {
                "lon": -122.0764,
                "lat": 37.6321,
                "value": "Hispanic"
              },
              {
                "lon": -122.0721,
                "lat": 37.6318,
                "value": "Asian"
              },
              {
                "lon": -122.0728,
                "lat": 37.6329,
                "value": "Hispanic"
              },
              {
                "lon": -122.0653,
                "lat": 37.6356,
                "value": "Hispanic"
              },
              {
                "lon": -122.0697,
                "lat": 37.638,
                "value": "Hispanic"
              },
              {
                "lon": -122.0763,
                "lat": 37.6406,
                "value": "Hispanic"
              },
              {
                "lon": -122.074,
                "lat": 37.6362,
                "value": "Hispanic"
              },
              {
                "lon": -122.075,
                "lat": 37.64,
                "value": "Hispanic"
              },
              {
                "lon": -122.0721,
                "lat": 37.6364,
                "value": "Hispanic"
              },
              {
                "lon": -122.0738,
                "lat": 37.6367,
                "value": "Hispanic"
              },
              {
                "lon": -122.0727,
                "lat": 37.6374,
                "value": "Hispanic"
              },
              {
                "lon": -122.0717,
                "lat": 37.6499,
                "value": "White"
              },
              {
                "lon": -122.0632,
                "lat": 37.641,
                "value": "Asian"
              },
              {
                "lon": -122.0736,
                "lat": 37.6436,
                "value": "Asian"
              },
              {
                "lon": -122.0595,
                "lat": 37.6365,
                "value": "Asian"
              },
              {
                "lon": -122.0692,
                "lat": 37.6462,
                "value": "Hispanic"
              },
              {
                "lon": -122.0653,
                "lat": 37.6416,
                "value": "Hispanic"
              },
              {
                "lon": -122.0768,
                "lat": 37.6466,
                "value": "Hispanic"
              },
              {
                "lon": -122.0675,
                "lat": 37.6478,
                "value": "Asian"
              },
              {
                "lon": -122.057,
                "lat": 37.6414,
                "value": "Hispanic"
              },
              {
                "lon": -122.0577,
                "lat": 37.6373,
                "value": "Hispanic"
              },
              {
                "lon": -122.0211,
                "lat": 37.608,
                "value": "White"
              },
              {
                "lon": -122.0372,
                "lat": 37.6284,
                "value": "Asian"
              },
              {
                "lon": -122.0419,
                "lat": 37.6275,
                "value": "Asian"
              },
              {
                "lon": -122.034,
                "lat": 37.6218,
                "value": "Hispanic"
              },
              {
                "lon": -122.0445,
                "lat": 37.6226,
                "value": "White"
              },
              {
                "lon": -122.0401,
                "lat": 37.6217,
                "value": "Black"
              },
              {
                "lon": -122.0346,
                "lat": 37.6124,
                "value": "Asian"
              },
              {
                "lon": -122.0512,
                "lat": 37.6246,
                "value": "Asian"
              },
              {
                "lon": -122.0345,
                "lat": 37.6135,
                "value": "Asian"
              },
              {
                "lon": -122.0315,
                "lat": 37.6092,
                "value": "Asian"
              },
              {
                "lon": -122.0487,
                "lat": 37.6255,
                "value": "Asian"
              },
              {
                "lon": -122.0309,
                "lat": 37.6145,
                "value": "Asian"
              },
              {
                "lon": -122.0356,
                "lat": 37.6192,
                "value": "Hispanic"
              },
              {
                "lon": -122.0317,
                "lat": 37.6104,
                "value": "Hispanic"
              },
              {
                "lon": -122.0482,
                "lat": 37.6232,
                "value": "Hispanic"
              },
              {
                "lon": -122.0314,
                "lat": 37.6136,
                "value": "Hispanic"
              },
              {
                "lon": -122.0375,
                "lat": 37.6123,
                "value": "Hispanic"
              },
              {
                "lon": -122.0735,
                "lat": 37.6204,
                "value": "Asian"
              },
              {
                "lon": -122.0833,
                "lat": 37.6313,
                "value": "Asian"
              },
              {
                "lon": -122.0779,
                "lat": 37.6262,
                "value": "Hispanic"
              },
              {
                "lon": -122.0759,
                "lat": 37.6237,
                "value": "Hispanic"
              },
              {
                "lon": -122.0751,
                "lat": 37.6282,
                "value": "Hispanic"
              },
              {
                "lon": -122.0738,
                "lat": 37.6292,
                "value": "Hispanic"
              },
              {
                "lon": -122.0787,
                "lat": 37.6247,
                "value": "Hispanic"
              },
              {
                "lon": -122.0508,
                "lat": 37.6223,
                "value": "White"
              },
              {
                "lon": -122.0519,
                "lat": 37.6156,
                "value": "Asian"
              },
              {
                "lon": -122.0474,
                "lat": 37.6149,
                "value": "Asian"
              },
              {
                "lon": -122.0457,
                "lat": 37.6168,
                "value": "Asian"
              },
              {
                "lon": -122.0571,
                "lat": 37.617,
                "value": "Hispanic"
              },
              {
                "lon": -122.0623,
                "lat": 37.619,
                "value": "White"
              },
              {
                "lon": -122.0625,
                "lat": 37.6252,
                "value": "Asian"
              },
              {
                "lon": -122.0567,
                "lat": 37.6319,
                "value": "Asian"
              },
              {
                "lon": -122.0619,
                "lat": 37.6322,
                "value": "Asian"
              },
              {
                "lon": -122.057,
                "lat": 37.6242,
                "value": "Asian"
              },
              {
                "lon": -122.0654,
                "lat": 37.6264,
                "value": "Hispanic"
              },
              {
                "lon": -122.0579,
                "lat": 37.6263,
                "value": "Hispanic"
              },
              {
                "lon": -122.0577,
                "lat": 37.624,
                "value": "Hispanic"
              },
              {
                "lon": -122.0653,
                "lat": 37.6278,
                "value": "Hispanic"
              },
              {
                "lon": -122.0891,
                "lat": 37.6271,
                "value": "Asian"
              },
              {
                "lon": -122.0826,
                "lat": 37.6276,
                "value": "Asian"
              },
              {
                "lon": -122.0892,
                "lat": 37.631,
                "value": "Asian"
              },
              {
                "lon": -122.0849,
                "lat": 37.6312,
                "value": "Hispanic"
              },
              {
                "lon": -122.0935,
                "lat": 37.631,
                "value": "Hispanic"
              },
              {
                "lon": -122.0886,
                "lat": 37.6309,
                "value": "Hispanic"
              },
              {
                "lon": -122.0857,
                "lat": 37.6207,
                "value": "Asian"
              },
              {
                "lon": -122.082,
                "lat": 37.6115,
                "value": "Asian"
              },
              {
                "lon": -122.082,
                "lat": 37.6188,
                "value": "Hispanic"
              },
              {
                "lon": -121.9616,
                "lat": 37.638,
                "value": "White"
              },
              {
                "lon": -122.0118,
                "lat": 37.6053,
                "value": "Asian"
              },
              {
                "lon": -122.0212,
                "lat": 37.6025,
                "value": "Asian"
              },
              {
                "lon": -122.0183,
                "lat": 37.6002,
                "value": "Asian"
              },
              {
                "lon": -122.0215,
                "lat": 37.6048,
                "value": "Hispanic"
              },
              {
                "lon": -122.0196,
                "lat": 37.5987,
                "value": "Hispanic"
              },
              {
                "lon": -122.0201,
                "lat": 37.6033,
                "value": "Hispanic"
              },
              {
                "lon": -122.0261,
                "lat": 37.6056,
                "value": "Hispanic"
              },
              {
                "lon": -122.0179,
                "lat": 37.5982,
                "value": "Hispanic"
              },
              {
                "lon": -122.0207,
                "lat": 37.6038,
                "value": "Hispanic"
              },
              {
                "lon": -122.0337,
                "lat": 37.5992,
                "value": "White"
              },
              {
                "lon": -122.0543,
                "lat": 37.6056,
                "value": "White"
              },
              {
                "lon": -122.0332,
                "lat": 37.5959,
                "value": "White"
              },
              {
                "lon": -122.0405,
                "lat": 37.5973,
                "value": "Asian"
              },
              {
                "lon": -122.0279,
                "lat": 37.6087,
                "value": "Asian"
              },
              {
                "lon": -122.0263,
                "lat": 37.6086,
                "value": "Asian"
              },
              {
                "lon": -122.0563,
                "lat": 37.6056,
                "value": "Hispanic"
              },
              {
                "lon": -122.0313,
                "lat": 37.6014,
                "value": "Hispanic"
              },
              {
                "lon": -122.0482,
                "lat": 37.603,
                "value": "Hispanic"
              },
              {
                "lon": -122.0457,
                "lat": 37.6007,
                "value": "Hispanic"
              },
              {
                "lon": -122.075,
                "lat": 37.585,
                "value": "White"
              },
              {
                "lon": -122.0782,
                "lat": 37.5842,
                "value": "Asian"
              },
              {
                "lon": -122.0716,
                "lat": 37.5904,
                "value": "Asian"
              },
              {
                "lon": -122.0764,
                "lat": 37.5878,
                "value": "Asian"
              },
              {
                "lon": -122.0753,
                "lat": 37.5904,
                "value": "Asian"
              },
              {
                "lon": -122.0762,
                "lat": 37.5902,
                "value": "Asian"
              },
              {
                "lon": -122.0741,
                "lat": 37.5739,
                "value": "White"
              },
              {
                "lon": -122.0742,
                "lat": 37.5822,
                "value": "Asian"
              },
              {
                "lon": -122.0695,
                "lat": 37.579,
                "value": "Asian"
              },
              {
                "lon": -122.0714,
                "lat": 37.5781,
                "value": "Asian"
              },
              {
                "lon": -122.0759,
                "lat": 37.5771,
                "value": "Asian"
              },
              {
                "lon": -122.0732,
                "lat": 37.5805,
                "value": "Hispanic"
              },
              {
                "lon": -122.0677,
                "lat": 37.5887,
                "value": "Asian"
              },
              {
                "lon": -122.0632,
                "lat": 37.5856,
                "value": "Asian"
              },
              {
                "lon": -122.0654,
                "lat": 37.5827,
                "value": "Asian"
              },
              {
                "lon": -122.0727,
                "lat": 37.5833,
                "value": "Asian"
              },
              {
                "lon": -122.069,
                "lat": 37.5902,
                "value": "Hispanic"
              },
              {
                "lon": -122.0502,
                "lat": 37.5904,
                "value": "White"
              },
              {
                "lon": -122.0427,
                "lat": 37.5896,
                "value": "Asian"
              },
              {
                "lon": -122.0443,
                "lat": 37.5932,
                "value": "Asian"
              },
              {
                "lon": -122.0468,
                "lat": 37.59,
                "value": "Asian"
              },
              {
                "lon": -122.0413,
                "lat": 37.5926,
                "value": "Asian"
              },
              {
                "lon": -122.0537,
                "lat": 37.5908,
                "value": "Hispanic"
              },
              {
                "lon": -122.0277,
                "lat": 37.5838,
                "value": "White"
              },
              {
                "lon": -122.0305,
                "lat": 37.5916,
                "value": "Asian"
              },
              {
                "lon": -122.0223,
                "lat": 37.5889,
                "value": "Asian"
              },
              {
                "lon": -122.0278,
                "lat": 37.5813,
                "value": "Asian"
              },
              {
                "lon": -122.0239,
                "lat": 37.5884,
                "value": "Asian"
              },
              {
                "lon": -122.0212,
                "lat": 37.5926,
                "value": "Asian"
              },
              {
                "lon": -122.0215,
                "lat": 37.5897,
                "value": "Asian"
              },
              {
                "lon": -122.0282,
                "lat": 37.5941,
                "value": "Hispanic"
              },
              {
                "lon": -122.0306,
                "lat": 37.5881,
                "value": "Hispanic"
              },
              {
                "lon": -122.0252,
                "lat": 37.5887,
                "value": "Hispanic"
              },
              {
                "lon": -122.0889,
                "lat": 37.5971,
                "value": "Asian"
              },
              {
                "lon": -122.0722,
                "lat": 37.5927,
                "value": "Asian"
              },
              {
                "lon": -122.0715,
                "lat": 37.5925,
                "value": "Asian"
              },
              {
                "lon": -122.0848,
                "lat": 37.6058,
                "value": "Asian"
              },
              {
                "lon": -122.085,
                "lat": 37.5865,
                "value": "Asian"
              },
              {
                "lon": -122.0883,
                "lat": 37.5896,
                "value": "Asian"
              },
              {
                "lon": -122.0876,
                "lat": 37.5888,
                "value": "Asian"
              },
              {
                "lon": -122.0822,
                "lat": 37.587,
                "value": "Asian"
              },
              {
                "lon": -122.0818,
                "lat": 37.61,
                "value": "Asian"
              },
              {
                "lon": -122.0704,
                "lat": 37.612,
                "value": "Asian"
              },
              {
                "lon": -122.083,
                "lat": 37.6062,
                "value": "Asian"
              },
              {
                "lon": -122.0712,
                "lat": 37.6092,
                "value": "Asian"
              },
              {
                "lon": -122.0625,
                "lat": 37.5906,
                "value": "Asian"
              },
              {
                "lon": -122.0608,
                "lat": 37.5916,
                "value": "Asian"
              },
              {
                "lon": -122.0625,
                "lat": 37.5963,
                "value": "Asian"
              },
              {
                "lon": -122.0706,
                "lat": 37.5968,
                "value": "Asian"
              },
              {
                "lon": -122.0604,
                "lat": 37.5959,
                "value": "Asian"
              },
              {
                "lon": -122.0656,
                "lat": 37.5945,
                "value": "Hispanic"
              },
              {
                "lon": -122.0196,
                "lat": 37.5771,
                "value": "White"
              },
              {
                "lon": -122.0144,
                "lat": 37.5798,
                "value": "Asian"
              },
              {
                "lon": -122.0152,
                "lat": 37.583,
                "value": "Asian"
              },
              {
                "lon": -122.025,
                "lat": 37.5783,
                "value": "Asian"
              },
              {
                "lon": -122.0157,
                "lat": 37.5773,
                "value": "Asian"
              },
              {
                "lon": -122.0167,
                "lat": 37.5843,
                "value": "Hispanic"
              },
              {
                "lon": -122.0089,
                "lat": 37.5918,
                "value": "Asian"
              },
              {
                "lon": -122.0059,
                "lat": 37.5929,
                "value": "Asian"
              },
              {
                "lon": -122.008,
                "lat": 37.5898,
                "value": "Asian"
              },
              {
                "lon": -122.0154,
                "lat": 37.5967,
                "value": "Asian"
              },
              {
                "lon": -122.0102,
                "lat": 37.5841,
                "value": "White"
              },
              {
                "lon": -122.0114,
                "lat": 37.5885,
                "value": "Asian"
              },
              {
                "lon": -122.0141,
                "lat": 37.5852,
                "value": "Asian"
              },
              {
                "lon": -122.0135,
                "lat": 37.5885,
                "value": "Asian"
              },
              {
                "lon": -122.0181,
                "lat": 37.5907,
                "value": "Asian"
              },
              {
                "lon": -121.9468,
                "lat": 37.574,
                "value": "White"
              },
              {
                "lon": -121.9715,
                "lat": 37.5976,
                "value": "White"
              },
              {
                "lon": -121.9434,
                "lat": 37.5846,
                "value": "White"
              },
              {
                "lon": -121.9353,
                "lat": 37.5879,
                "value": "White"
              },
              {
                "lon": -121.9516,
                "lat": 37.5903,
                "value": "Asian"
              },
              {
                "lon": -121.9863,
                "lat": 37.5927,
                "value": "Asian"
              },
              {
                "lon": -121.9761,
                "lat": 37.5874,
                "value": "Asian"
              },
              {
                "lon": -121.9466,
                "lat": 37.5712,
                "value": "Hispanic"
              },
              {
                "lon": -121.9835,
                "lat": 37.5721,
                "value": "White"
              },
              {
                "lon": -121.9877,
                "lat": 37.5739,
                "value": "White"
              },
              {
                "lon": -121.9776,
                "lat": 37.5758,
                "value": "White"
              },
              {
                "lon": -121.9934,
                "lat": 37.5739,
                "value": "White"
              },
              {
                "lon": -121.9926,
                "lat": 37.574,
                "value": "Asian"
              },
              {
                "lon": -121.9857,
                "lat": 37.5778,
                "value": "Asian"
              },
              {
                "lon": -121.9992,
                "lat": 37.5859,
                "value": "Asian"
              },
              {
                "lon": -122.0041,
                "lat": 37.5845,
                "value": "Asian"
              },
              {
                "lon": -121.9882,
                "lat": 37.5733,
                "value": "Asian"
              },
              {
                "lon": -121.9997,
                "lat": 37.5878,
                "value": "Asian"
              },
              {
                "lon": -121.9812,
                "lat": 37.5738,
                "value": "Hispanic"
              },
              {
                "lon": -121.998,
                "lat": 37.5742,
                "value": "White"
              },
              {
                "lon": -122.016,
                "lat": 37.5748,
                "value": "Asian"
              },
              {
                "lon": -122.0039,
                "lat": 37.5777,
                "value": "Asian"
              },
              {
                "lon": -122.0067,
                "lat": 37.5765,
                "value": "Asian"
              },
              {
                "lon": -122.0264,
                "lat": 37.5705,
                "value": "White"
              },
              {
                "lon": -122.0131,
                "lat": 37.567,
                "value": "Asian"
              },
              {
                "lon": -122.0127,
                "lat": 37.568,
                "value": "Asian"
              },
              {
                "lon": -122.0117,
                "lat": 37.5626,
                "value": "Asian"
              },
              {
                "lon": -122.0209,
                "lat": 37.5714,
                "value": "Asian"
              },
              {
                "lon": -122.0114,
                "lat": 37.5652,
                "value": "Asian"
              },
              {
                "lon": -122.0222,
                "lat": 37.5679,
                "value": "Asian"
              },
              {
                "lon": -122.0301,
                "lat": 37.5716,
                "value": "Asian"
              },
              {
                "lon": -122.0205,
                "lat": 37.5659,
                "value": "Hispanic"
              },
              {
                "lon": -122.0362,
                "lat": 37.5772,
                "value": "White"
              },
              {
                "lon": -122.0286,
                "lat": 37.5762,
                "value": "White"
              },
              {
                "lon": -122.0344,
                "lat": 37.5717,
                "value": "White"
              },
              {
                "lon": -122.0455,
                "lat": 37.5764,
                "value": "Asian"
              },
              {
                "lon": -122.0326,
                "lat": 37.577,
                "value": "Asian"
              },
              {
                "lon": -122.0408,
                "lat": 37.5737,
                "value": "Asian"
              },
              {
                "lon": -122.0311,
                "lat": 37.5796,
                "value": "Asian"
              },
              {
                "lon": -122.0345,
                "lat": 37.5698,
                "value": "Asian"
              },
              {
                "lon": -122.0298,
                "lat": 37.5774,
                "value": "Asian"
              },
              {
                "lon": -122.0306,
                "lat": 37.5793,
                "value": "Asian"
              },
              {
                "lon": -122.0298,
                "lat": 37.574,
                "value": "Asian"
              },
              {
                "lon": -122.0381,
                "lat": 37.569,
                "value": "Asian"
              },
              {
                "lon": -122.0409,
                "lat": 37.5663,
                "value": "Hispanic"
              },
              {
                "lon": -122.044,
                "lat": 37.5864,
                "value": "White"
              },
              {
                "lon": -122.0402,
                "lat": 37.5861,
                "value": "Asian"
              },
              {
                "lon": -122.0478,
                "lat": 37.5818,
                "value": "Asian"
              },
              {
                "lon": -122.0376,
                "lat": 37.5824,
                "value": "Asian"
              },
              {
                "lon": -122.0358,
                "lat": 37.5863,
                "value": "Asian"
              },
              {
                "lon": -122.048,
                "lat": 37.5855,
                "value": "Asian"
              },
              {
                "lon": -122.0419,
                "lat": 37.5858,
                "value": "Asian"
              },
              {
                "lon": -122.0459,
                "lat": 37.5832,
                "value": "Asian"
              },
              {
                "lon": -122.084,
                "lat": 37.5664,
                "value": "White"
              },
              {
                "lon": -122.0732,
                "lat": 37.5662,
                "value": "Asian"
              },
              {
                "lon": -122.0804,
                "lat": 37.5622,
                "value": "Asian"
              },
              {
                "lon": -122.0725,
                "lat": 37.5738,
                "value": "Asian"
              },
              {
                "lon": -122.0792,
                "lat": 37.5629,
                "value": "Asian"
              },
              {
                "lon": -122.0655,
                "lat": 37.5712,
                "value": "Asian"
              },
              {
                "lon": -122.0754,
                "lat": 37.5628,
                "value": "Asian"
              },
              {
                "lon": -122.0673,
                "lat": 37.5731,
                "value": "Asian"
              },
              {
                "lon": -122.0796,
                "lat": 37.5664,
                "value": "Asian"
              },
              {
                "lon": -122.1064,
                "lat": 37.5022,
                "value": "White"
              },
              {
                "lon": -121.9561,
                "lat": 37.4905,
                "value": "Asian"
              },
              {
                "lon": -122.0305,
                "lat": 37.4655,
                "value": "Asian"
              },
              {
                "lon": -122.0603,
                "lat": 37.5477,
                "value": "Asian"
              },
              {
                "lon": -121.9856,
                "lat": 37.5083,
                "value": "Asian"
              },
              {
                "lon": -121.9905,
                "lat": 37.5064,
                "value": "Asian"
              },
              {
                "lon": -121.9671,
                "lat": 37.4763,
                "value": "Asian"
              },
              {
                "lon": -121.984,
                "lat": 37.5142,
                "value": "Asian"
              },
              {
                "lon": -122.0632,
                "lat": 37.5635,
                "value": "Asian"
              },
              {
                "lon": -122.1034,
                "lat": 37.542,
                "value": "Asian"
              },
              {
                "lon": -121.9629,
                "lat": 37.4883,
                "value": "Asian"
              },
              {
                "lon": -121.9364,
                "lat": 37.4734,
                "value": "Asian"
              },
              {
                "lon": -121.9208,
                "lat": 37.4627,
                "value": "Asian"
              },
              {
                "lon": -122.1282,
                "lat": 37.5599,
                "value": "Hispanic"
              },
              {
                "lon": -122.0576,
                "lat": 37.5692,
                "value": "White"
              },
              {
                "lon": -122.0566,
                "lat": 37.5727,
                "value": "Asian"
              },
              {
                "lon": -122.0488,
                "lat": 37.5747,
                "value": "Asian"
              },
              {
                "lon": -122.0535,
                "lat": 37.5776,
                "value": "Asian"
              },
              {
                "lon": -122.0494,
                "lat": 37.5733,
                "value": "Asian"
              },
              {
                "lon": -122.0554,
                "lat": 37.5678,
                "value": "Asian"
              },
              {
                "lon": -122.0501,
                "lat": 37.5775,
                "value": "Asian"
              },
              {
                "lon": -122.0541,
                "lat": 37.5713,
                "value": "Asian"
              },
              {
                "lon": -122.0477,
                "lat": 37.5675,
                "value": "Asian"
              },
              {
                "lon": -122.0599,
                "lat": 37.5859,
                "value": "White"
              },
              {
                "lon": -122.0601,
                "lat": 37.5851,
                "value": "White"
              },
              {
                "lon": -122.0575,
                "lat": 37.5804,
                "value": "Asian"
              },
              {
                "lon": -122.057,
                "lat": 37.5868,
                "value": "Asian"
              },
              {
                "lon": -122.0598,
                "lat": 37.58,
                "value": "Asian"
              },
              {
                "lon": -122.0617,
                "lat": 37.5898,
                "value": "Asian"
              },
              {
                "lon": -122.0551,
                "lat": 37.5834,
                "value": "Asian"
              },
              {
                "lon": -122.05,
                "lat": 37.5807,
                "value": "Asian"
              },
              {
                "lon": -122.0596,
                "lat": 37.5812,
                "value": "Asian"
              },
              {
                "lon": -122.0457,
                "lat": 37.5673,
                "value": "Asian"
              },
              {
                "lon": -122.0493,
                "lat": 37.5665,
                "value": "Asian"
              },
              {
                "lon": -122.0494,
                "lat": 37.5626,
                "value": "Asian"
              },
              {
                "lon": -122.0453,
                "lat": 37.5675,
                "value": "Asian"
              },
              {
                "lon": -122.0468,
                "lat": 37.5628,
                "value": "Asian"
              },
              {
                "lon": -122.0543,
                "lat": 37.558,
                "value": "Asian"
              },
              {
                "lon": -122.0558,
                "lat": 37.566,
                "value": "Asian"
              },
              {
                "lon": -122.0518,
                "lat": 37.5561,
                "value": "Asian"
              },
              {
                "lon": -122.0396,
                "lat": 37.5626,
                "value": "Asian"
              },
              {
                "lon": -122.0427,
                "lat": 37.5603,
                "value": "Asian"
              },
              {
                "lon": -122.0511,
                "lat": 37.5571,
                "value": "Asian"
              },
              {
                "lon": -122.0443,
                "lat": 37.5595,
                "value": "Asian"
              },
              {
                "lon": -121.9415,
                "lat": 37.5132,
                "value": "Asian"
              },
              {
                "lon": -121.9366,
                "lat": 37.5079,
                "value": "Asian"
              },
              {
                "lon": -121.9377,
                "lat": 37.4946,
                "value": "Asian"
              },
              {
                "lon": -122.0256,
                "lat": 37.564,
                "value": "White"
              },
              {
                "lon": -122.0377,
                "lat": 37.5642,
                "value": "White"
              },
              {
                "lon": -122.0255,
                "lat": 37.5662,
                "value": "Asian"
              },
              {
                "lon": -122.029,
                "lat": 37.5609,
                "value": "Asian"
              },
              {
                "lon": -122.033,
                "lat": 37.5616,
                "value": "Asian"
              },
              {
                "lon": -122.026,
                "lat": 37.5604,
                "value": "Hispanic"
              },
              {
                "lon": -122.0188,
                "lat": 37.5617,
                "value": "White"
              },
              {
                "lon": -122.0226,
                "lat": 37.5567,
                "value": "White"
              },
              {
                "lon": -122.0213,
                "lat": 37.558,
                "value": "White"
              },
              {
                "lon": -122.0155,
                "lat": 37.5598,
                "value": "Black"
              },
              {
                "lon": -122.0202,
                "lat": 37.5565,
                "value": "Asian"
              },
              {
                "lon": -122.0241,
                "lat": 37.5579,
                "value": "Asian"
              },
              {
                "lon": -122.0156,
                "lat": 37.5591,
                "value": "Asian"
              },
              {
                "lon": -122.0256,
                "lat": 37.5534,
                "value": "Asian"
              },
              {
                "lon": -122.0156,
                "lat": 37.5595,
                "value": "Asian"
              },
              {
                "lon": -122.0203,
                "lat": 37.5585,
                "value": "Hispanic"
              },
              {
                "lon": -122.0229,
                "lat": 37.5612,
                "value": "Hispanic"
              },
              {
                "lon": -122.0211,
                "lat": 37.5505,
                "value": "Hispanic"
              },
              {
                "lon": -122.0172,
                "lat": 37.5457,
                "value": "White"
              },
              {
                "lon": -122.0204,
                "lat": 37.5494,
                "value": "Asian"
              },
              {
                "lon": -122.0092,
                "lat": 37.5523,
                "value": "Asian"
              },
              {
                "lon": -122.0124,
                "lat": 37.5506,
                "value": "Asian"
              },
              {
                "lon": -122.008,
                "lat": 37.5544,
                "value": "Asian"
              },
              {
                "lon": -122.0108,
                "lat": 37.5528,
                "value": "Hispanic"
              },
              {
                "lon": -122.0126,
                "lat": 37.5592,
                "value": "White"
              },
              {
                "lon": -122.0042,
                "lat": 37.559,
                "value": "Asian"
              },
              {
                "lon": -122.016,
                "lat": 37.5546,
                "value": "Asian"
              },
              {
                "lon": -122.0114,
                "lat": 37.5572,
                "value": "Asian"
              },
              {
                "lon": -122.0087,
                "lat": 37.5626,
                "value": "Asian"
              },
              {
                "lon": -122.0024,
                "lat": 37.5611,
                "value": "Asian"
              },
              {
                "lon": -122.0111,
                "lat": 37.5553,
                "value": "Hispanic"
              },
              {
                "lon": -122.009,
                "lat": 37.5583,
                "value": "Hispanic"
              },
              {
                "lon": -122.0026,
                "lat": 37.5581,
                "value": "White"
              },
              {
                "lon": -121.9999,
                "lat": 37.5549,
                "value": "White"
              },
              {
                "lon": -121.9908,
                "lat": 37.555,
                "value": "White"
              },
              {
                "lon": -121.9912,
                "lat": 37.5618,
                "value": "White"
              },
              {
                "lon": -121.9946,
                "lat": 37.5579,
                "value": "Asian"
              },
              {
                "lon": -121.9923,
                "lat": 37.5598,
                "value": "Asian"
              },
              {
                "lon": -121.9871,
                "lat": 37.5585,
                "value": "Asian"
              },
              {
                "lon": -121.9919,
                "lat": 37.5568,
                "value": "Asian"
              },
              {
                "lon": -121.996,
                "lat": 37.562,
                "value": "Asian"
              },
              {
                "lon": -121.9842,
                "lat": 37.5651,
                "value": "Asian"
              },
              {
                "lon": -121.9836,
                "lat": 37.5629,
                "value": "Hispanic"
              },
              {
                "lon": -121.9677,
                "lat": 37.538,
                "value": "White"
              },
              {
                "lon": -121.9692,
                "lat": 37.5461,
                "value": "Asian"
              },
              {
                "lon": -121.9688,
                "lat": 37.5411,
                "value": "Asian"
              },
              {
                "lon": -121.9699,
                "lat": 37.5476,
                "value": "Asian"
              },
              {
                "lon": -121.9719,
                "lat": 37.5447,
                "value": "Hispanic"
              },
              {
                "lon": -121.9682,
                "lat": 37.5446,
                "value": "Hispanic"
              },
              {
                "lon": -121.9816,
                "lat": 37.5559,
                "value": "White"
              },
              {
                "lon": -121.9835,
                "lat": 37.5566,
                "value": "Asian"
              },
              {
                "lon": -121.9905,
                "lat": 37.5463,
                "value": "Asian"
              },
              {
                "lon": -121.9869,
                "lat": 37.5452,
                "value": "Asian"
              },
              {
                "lon": -121.9824,
                "lat": 37.5553,
                "value": "Asian"
              },
              {
                "lon": -121.9822,
                "lat": 37.5532,
                "value": "Asian"
              },
              {
                "lon": -121.9826,
                "lat": 37.548,
                "value": "Asian"
              },
              {
                "lon": -121.9893,
                "lat": 37.5499,
                "value": "Hispanic"
              },
              {
                "lon": -121.9885,
                "lat": 37.5538,
                "value": "Hispanic"
              },
              {
                "lon": -121.9762,
                "lat": 37.5647,
                "value": "White"
              },
              {
                "lon": -121.966,
                "lat": 37.5664,
                "value": "White"
              },
              {
                "lon": -121.9782,
                "lat": 37.5636,
                "value": "Asian"
              },
              {
                "lon": -121.9806,
                "lat": 37.5655,
                "value": "Asian"
              },
              {
                "lon": -121.971,
                "lat": 37.5608,
                "value": "Asian"
              },
              {
                "lon": -121.9737,
                "lat": 37.5629,
                "value": "Asian"
              },
              {
                "lon": -121.9794,
                "lat": 37.5671,
                "value": "Asian"
              },
              {
                "lon": -121.9818,
                "lat": 37.5645,
                "value": "Asian"
              },
              {
                "lon": -121.9786,
                "lat": 37.5677,
                "value": "Asian"
              },
              {
                "lon": -121.9721,
                "lat": 37.568,
                "value": "Asian"
              },
              {
                "lon": -121.9761,
                "lat": 37.5577,
                "value": "Asian"
              },
              {
                "lon": -121.9742,
                "lat": 37.5687,
                "value": "Asian"
              },
              {
                "lon": -121.9699,
                "lat": 37.5643,
                "value": "Hispanic"
              },
              {
                "lon": -121.9754,
                "lat": 37.5404,
                "value": "White"
              },
              {
                "lon": -121.9803,
                "lat": 37.5422,
                "value": "Asian"
              },
              {
                "lon": -121.9737,
                "lat": 37.5408,
                "value": "Asian"
              },
              {
                "lon": -121.975,
                "lat": 37.5398,
                "value": "Asian"
              },
              {
                "lon": -121.9794,
                "lat": 37.5424,
                "value": "Asian"
              },
              {
                "lon": -121.9782,
                "lat": 37.5395,
                "value": "Hispanic"
              },
              {
                "lon": -121.9807,
                "lat": 37.5401,
                "value": "Hispanic"
              },
              {
                "lon": -121.98,
                "lat": 37.5453,
                "value": "White"
              },
              {
                "lon": -121.9762,
                "lat": 37.5453,
                "value": "Asian"
              },
              {
                "lon": -121.9744,
                "lat": 37.5487,
                "value": "Asian"
              },
              {
                "lon": -121.9779,
                "lat": 37.5513,
                "value": "Asian"
              },
              {
                "lon": -121.9737,
                "lat": 37.5448,
                "value": "Asian"
              },
              {
                "lon": -121.9752,
                "lat": 37.5458,
                "value": "Asian"
              },
              {
                "lon": -121.9763,
                "lat": 37.5484,
                "value": "Hispanic"
              },
              {
                "lon": -121.9617,
                "lat": 37.5548,
                "value": "White"
              },
              {
                "lon": -121.9622,
                "lat": 37.5584,
                "value": "Asian"
              },
              {
                "lon": -121.9628,
                "lat": 37.5573,
                "value": "Asian"
              },
              {
                "lon": -121.9666,
                "lat": 37.5518,
                "value": "Asian"
              },
              {
                "lon": -121.961,
                "lat": 37.5567,
                "value": "Asian"
              },
              {
                "lon": -121.9727,
                "lat": 37.5501,
                "value": "White"
              },
              {
                "lon": -121.9747,
                "lat": 37.5509,
                "value": "Asian"
              },
              {
                "lon": -121.9738,
                "lat": 37.5506,
                "value": "Asian"
              },
              {
                "lon": -121.9715,
                "lat": 37.5554,
                "value": "Asian"
              },
              {
                "lon": -121.9732,
                "lat": 37.5575,
                "value": "Asian"
              },
              {
                "lon": -121.9302,
                "lat": 37.5454,
                "value": "Asian"
              },
              {
                "lon": -121.9231,
                "lat": 37.5626,
                "value": "Asian"
              },
              {
                "lon": -121.9306,
                "lat": 37.5558,
                "value": "Asian"
              },
              {
                "lon": -121.9273,
                "lat": 37.5544,
                "value": "Asian"
              },
              {
                "lon": -121.9474,
                "lat": 37.5519,
                "value": "Asian"
              },
              {
                "lon": -121.9482,
                "lat": 37.549,
                "value": "Asian"
              },
              {
                "lon": -121.9436,
                "lat": 37.5506,
                "value": "Asian"
              },
              {
                "lon": -121.9404,
                "lat": 37.5494,
                "value": "Asian"
              },
              {
                "lon": -121.9534,
                "lat": 37.553,
                "value": "Asian"
              },
              {
                "lon": -121.9478,
                "lat": 37.5419,
                "value": "Asian"
              },
              {
                "lon": -121.9533,
                "lat": 37.5465,
                "value": "Asian"
              },
              {
                "lon": -121.9541,
                "lat": 37.5358,
                "value": "Asian"
              },
              {
                "lon": -121.9356,
                "lat": 37.5392,
                "value": "White"
              },
              {
                "lon": -121.9446,
                "lat": 37.5431,
                "value": "Asian"
              },
              {
                "lon": -121.935,
                "lat": 37.5447,
                "value": "Asian"
              },
              {
                "lon": -121.948,
                "lat": 37.5282,
                "value": "Asian"
              },
              {
                "lon": -121.943,
                "lat": 37.5344,
                "value": "Asian"
              },
              {
                "lon": -121.9395,
                "lat": 37.5339,
                "value": "Asian"
              },
              {
                "lon": -121.9397,
                "lat": 37.5431,
                "value": "Asian"
              },
              {
                "lon": -121.9519,
                "lat": 37.531,
                "value": "Asian"
              },
              {
                "lon": -121.9458,
                "lat": 37.5239,
                "value": "Asian"
              },
              {
                "lon": -121.945,
                "lat": 37.5306,
                "value": "Asian"
              },
              {
                "lon": -121.9425,
                "lat": 37.538,
                "value": "Asian"
              },
              {
                "lon": -121.9315,
                "lat": 37.5395,
                "value": "Asian"
              },
              {
                "lon": -121.9641,
                "lat": 37.5274,
                "value": "White"
              },
              {
                "lon": -121.9618,
                "lat": 37.5309,
                "value": "Asian"
              },
              {
                "lon": -121.9649,
                "lat": 37.5261,
                "value": "Asian"
              },
              {
                "lon": -121.9559,
                "lat": 37.5252,
                "value": "Asian"
              },
              {
                "lon": -121.9566,
                "lat": 37.532,
                "value": "Asian"
              },
              {
                "lon": -121.9663,
                "lat": 37.524,
                "value": "Asian"
              },
              {
                "lon": -121.9573,
                "lat": 37.5313,
                "value": "Hispanic"
              },
              {
                "lon": -121.9597,
                "lat": 37.5386,
                "value": "White"
              },
              {
                "lon": -121.9647,
                "lat": 37.5371,
                "value": "Asian"
              },
              {
                "lon": -121.9607,
                "lat": 37.536,
                "value": "Asian"
              },
              {
                "lon": -121.9665,
                "lat": 37.5325,
                "value": "Asian"
              },
              {
                "lon": -121.9598,
                "lat": 37.5363,
                "value": "Asian"
              },
              {
                "lon": -121.966,
                "lat": 37.5352,
                "value": "Asian"
              },
              {
                "lon": -121.9684,
                "lat": 37.5319,
                "value": "Asian"
              },
              {
                "lon": -121.9604,
                "lat": 37.5415,
                "value": "Asian"
              },
              {
                "lon": -121.9644,
                "lat": 37.533,
                "value": "Hispanic"
              },
              {
                "lon": -121.9617,
                "lat": 37.5365,
                "value": "Hispanic"
              },
              {
                "lon": -121.974,
                "lat": 37.5239,
                "value": "White"
              },
              {
                "lon": -121.9718,
                "lat": 37.5366,
                "value": "White"
              },
              {
                "lon": -121.9704,
                "lat": 37.5382,
                "value": "White"
              },
              {
                "lon": -121.9703,
                "lat": 37.5284,
                "value": "Asian"
              },
              {
                "lon": -121.969,
                "lat": 37.5379,
                "value": "Asian"
              },
              {
                "lon": -121.9742,
                "lat": 37.5353,
                "value": "Asian"
              },
              {
                "lon": -121.9706,
                "lat": 37.5267,
                "value": "Asian"
              },
              {
                "lon": -121.974,
                "lat": 37.5338,
                "value": "Asian"
              },
              {
                "lon": -121.968,
                "lat": 37.5366,
                "value": "Hispanic"
              },
              {
                "lon": -121.9766,
                "lat": 37.5351,
                "value": "Hispanic"
              },
              {
                "lon": -121.977,
                "lat": 37.5308,
                "value": "Hispanic"
              },
              {
                "lon": -121.9832,
                "lat": 37.5381,
                "value": "Asian"
              },
              {
                "lon": -121.9914,
                "lat": 37.5334,
                "value": "Asian"
              },
              {
                "lon": -121.9893,
                "lat": 37.5328,
                "value": "Asian"
              },
              {
                "lon": -121.9806,
                "lat": 37.5333,
                "value": "Hispanic"
              },
              {
                "lon": -121.9898,
                "lat": 37.5441,
                "value": "White"
              },
              {
                "lon": -121.9937,
                "lat": 37.5354,
                "value": "Asian"
              },
              {
                "lon": -121.9895,
                "lat": 37.5429,
                "value": "Asian"
              },
              {
                "lon": -121.9957,
                "lat": 37.5377,
                "value": "Asian"
              },
              {
                "lon": -121.991,
                "lat": 37.5383,
                "value": "Asian"
              },
              {
                "lon": -121.9926,
                "lat": 37.5396,
                "value": "Hispanic"
              },
              {
                "lon": -121.9926,
                "lat": 37.5501,
                "value": "White"
              },
              {
                "lon": -122.0038,
                "lat": 37.5405,
                "value": "Asian"
              },
              {
                "lon": -121.9916,
                "lat": 37.5449,
                "value": "Asian"
              },
              {
                "lon": -121.996,
                "lat": 37.5439,
                "value": "Asian"
              },
              {
                "lon": -121.9954,
                "lat": 37.5434,
                "value": "Hispanic"
              },
              {
                "lon": -121.9992,
                "lat": 37.5448,
                "value": "Hispanic"
              },
              {
                "lon": -122.0077,
                "lat": 37.5491,
                "value": "White"
              },
              {
                "lon": -122.0095,
                "lat": 37.548,
                "value": "White"
              },
              {
                "lon": -122.0028,
                "lat": 37.5544,
                "value": "Asian"
              },
              {
                "lon": -122.0022,
                "lat": 37.5549,
                "value": "Asian"
              },
              {
                "lon": -122.0074,
                "lat": 37.5509,
                "value": "Asian"
              },
              {
                "lon": -122.0013,
                "lat": 37.5483,
                "value": "Hispanic"
              },
              {
                "lon": -122.0023,
                "lat": 37.5544,
                "value": "Hispanic"
              },
              {
                "lon": -122.0154,
                "lat": 37.5408,
                "value": "White"
              },
              {
                "lon": -122.01,
                "lat": 37.5394,
                "value": "Asian"
              },
              {
                "lon": -122.0052,
                "lat": 37.5387,
                "value": "Asian"
              },
              {
                "lon": -122.0086,
                "lat": 37.5387,
                "value": "Asian"
              },
              {
                "lon": -121.9872,
                "lat": 37.5285,
                "value": "White"
              },
              {
                "lon": -121.9939,
                "lat": 37.5262,
                "value": "Asian"
              },
              {
                "lon": -121.9884,
                "lat": 37.524,
                "value": "Asian"
              },
              {
                "lon": -121.9952,
                "lat": 37.532,
                "value": "Asian"
              },
              {
                "lon": -121.9972,
                "lat": 37.5304,
                "value": "Hispanic"
              },
              {
                "lon": -121.9651,
                "lat": 37.5109,
                "value": "White"
              },
              {
                "lon": -121.978,
                "lat": 37.5232,
                "value": "Asian"
              },
              {
                "lon": -121.9656,
                "lat": 37.5107,
                "value": "Asian"
              },
              {
                "lon": -121.9762,
                "lat": 37.5233,
                "value": "Asian"
              },
              {
                "lon": -121.9698,
                "lat": 37.5193,
                "value": "Asian"
              },
              {
                "lon": -121.9775,
                "lat": 37.5199,
                "value": "Asian"
              },
              {
                "lon": -121.9712,
                "lat": 37.5115,
                "value": "Asian"
              },
              {
                "lon": -121.9761,
                "lat": 37.5176,
                "value": "Asian"
              },
              {
                "lon": -121.9719,
                "lat": 37.5214,
                "value": "Asian"
              },
              {
                "lon": -121.9671,
                "lat": 37.5101,
                "value": "Asian"
              },
              {
                "lon": -121.9692,
                "lat": 37.517,
                "value": "Hispanic"
              },
              {
                "lon": -121.9791,
                "lat": 37.5221,
                "value": "Hispanic"
              },
              {
                "lon": -121.9564,
                "lat": 37.5227,
                "value": "Asian"
              },
              {
                "lon": -121.9529,
                "lat": 37.5173,
                "value": "Asian"
              },
              {
                "lon": -121.9536,
                "lat": 37.5222,
                "value": "Hispanic"
              },
              {
                "lon": -121.9603,
                "lat": 37.5139,
                "value": "White"
              },
              {
                "lon": -121.9534,
                "lat": 37.5155,
                "value": "Asian"
              },
              {
                "lon": -121.9612,
                "lat": 37.5234,
                "value": "Asian"
              },
              {
                "lon": -121.9586,
                "lat": 37.5207,
                "value": "Asian"
              },
              {
                "lon": -121.9596,
                "lat": 37.5144,
                "value": "Asian"
              },
              {
                "lon": -121.9559,
                "lat": 37.5133,
                "value": "Asian"
              },
              {
                "lon": -121.964,
                "lat": 37.5136,
                "value": "Asian"
              },
              {
                "lon": -121.9631,
                "lat": 37.5189,
                "value": "Asian"
              },
              {
                "lon": -121.9564,
                "lat": 37.5121,
                "value": "Asian"
              },
              {
                "lon": -121.9624,
                "lat": 37.5227,
                "value": "Hispanic"
              },
              {
                "lon": -121.9668,
                "lat": 37.5179,
                "value": "Hispanic"
              },
              {
                "lon": -121.9349,
                "lat": 37.5101,
                "value": "Asian"
              },
              {
                "lon": -121.9247,
                "lat": 37.5124,
                "value": "Asian"
              },
              {
                "lon": -121.9255,
                "lat": 37.5098,
                "value": "Asian"
              },
              {
                "lon": -121.925,
                "lat": 37.5017,
                "value": "Asian"
              },
              {
                "lon": -121.9324,
                "lat": 37.5119,
                "value": "Asian"
              },
              {
                "lon": -121.932,
                "lat": 37.5063,
                "value": "Asian"
              },
              {
                "lon": -121.9322,
                "lat": 37.5063,
                "value": "Asian"
              },
              {
                "lon": -121.9093,
                "lat": 37.5329,
                "value": "White"
              },
              {
                "lon": -121.883,
                "lat": 37.5193,
                "value": "Asian"
              },
              {
                "lon": -121.884,
                "lat": 37.5065,
                "value": "Asian"
              },
              {
                "lon": -121.8907,
                "lat": 37.5255,
                "value": "Asian"
              },
              {
                "lon": -121.8885,
                "lat": 37.544,
                "value": "Asian"
              },
              {
                "lon": -121.8878,
                "lat": 37.519,
                "value": "Asian"
              },
              {
                "lon": -121.9009,
                "lat": 37.5151,
                "value": "Asian"
              },
              {
                "lon": -121.932,
                "lat": 37.5356,
                "value": "White"
              },
              {
                "lon": -121.9396,
                "lat": 37.5317,
                "value": "Asian"
              },
              {
                "lon": -121.9223,
                "lat": 37.535,
                "value": "Asian"
              },
              {
                "lon": -121.9266,
                "lat": 37.534,
                "value": "Asian"
              },
              {
                "lon": -121.9211,
                "lat": 37.5287,
                "value": "Asian"
              },
              {
                "lon": -121.9367,
                "lat": 37.5332,
                "value": "Asian"
              },
              {
                "lon": -121.9251,
                "lat": 37.5361,
                "value": "Asian"
              },
              {
                "lon": -121.9305,
                "lat": 37.5329,
                "value": "Asian"
              },
              {
                "lon": -121.938,
                "lat": 37.5203,
                "value": "Asian"
              },
              {
                "lon": -121.924,
                "lat": 37.5197,
                "value": "Asian"
              },
              {
                "lon": -121.9424,
                "lat": 37.5299,
                "value": "Asian"
              },
              {
                "lon": -121.9284,
                "lat": 37.5167,
                "value": "Asian"
              },
              {
                "lon": -121.9301,
                "lat": 37.5214,
                "value": "Asian"
              },
              {
                "lon": -121.9269,
                "lat": 37.5208,
                "value": "Asian"
              },
              {
                "lon": -121.9358,
                "lat": 37.5186,
                "value": "Asian"
              },
              {
                "lon": -121.9283,
                "lat": 37.5184,
                "value": "Asian"
              },
              {
                "lon": -121.9062,
                "lat": 37.4963,
                "value": "Asian"
              },
              {
                "lon": -121.8773,
                "lat": 37.4815,
                "value": "Asian"
              },
              {
                "lon": -121.9125,
                "lat": 37.496,
                "value": "Asian"
              },
              {
                "lon": -121.8962,
                "lat": 37.4765,
                "value": "Asian"
              },
              {
                "lon": -121.8759,
                "lat": 37.4886,
                "value": "Asian"
              },
              {
                "lon": -121.9124,
                "lat": 37.4747,
                "value": "White"
              },
              {
                "lon": -121.9133,
                "lat": 37.4725,
                "value": "Asian"
              },
              {
                "lon": -121.9186,
                "lat": 37.4746,
                "value": "Asian"
              },
              {
                "lon": -121.9164,
                "lat": 37.4818,
                "value": "Asian"
              },
              {
                "lon": -121.9119,
                "lat": 37.4652,
                "value": "Asian"
              },
              {
                "lon": -121.9164,
                "lat": 37.4716,
                "value": "Asian"
              },
              {
                "lon": -121.922,
                "lat": 37.4939,
                "value": "Asian"
              },
              {
                "lon": -121.9229,
                "lat": 37.4935,
                "value": "Asian"
              },
              {
                "lon": -121.9235,
                "lat": 37.4939,
                "value": "Asian"
              },
              {
                "lon": -121.9257,
                "lat": 37.493,
                "value": "Asian"
              },
              {
                "lon": -121.9233,
                "lat": 37.4901,
                "value": "Asian"
              },
              {
                "lon": -121.9224,
                "lat": 37.4875,
                "value": "White"
              },
              {
                "lon": -121.9203,
                "lat": 37.4829,
                "value": "Asian"
              },
              {
                "lon": -121.9189,
                "lat": 37.4773,
                "value": "Asian"
              },
              {
                "lon": -121.9243,
                "lat": 37.4849,
                "value": "Asian"
              },
              {
                "lon": -121.9223,
                "lat": 37.4862,
                "value": "Asian"
              },
              {
                "lon": -122.042,
                "lat": 37.5573,
                "value": "White"
              },
              {
                "lon": -122.0437,
                "lat": 37.5537,
                "value": "White"
              },
              {
                "lon": -122.0355,
                "lat": 37.5556,
                "value": "White"
              },
              {
                "lon": -122.0442,
                "lat": 37.5548,
                "value": "White"
              },
              {
                "lon": -122.0415,
                "lat": 37.5547,
                "value": "Black"
              },
              {
                "lon": -122.0357,
                "lat": 37.5429,
                "value": "Asian"
              },
              {
                "lon": -122.0302,
                "lat": 37.546,
                "value": "Asian"
              },
              {
                "lon": -122.0306,
                "lat": 37.5509,
                "value": "Asian"
              },
              {
                "lon": -122.0372,
                "lat": 37.5483,
                "value": "Asian"
              },
              {
                "lon": -122.0331,
                "lat": 37.5535,
                "value": "Hispanic"
              },
              {
                "lon": -122.0291,
                "lat": 37.549,
                "value": "Hispanic"
              },
              {
                "lon": -122.0461,
                "lat": 37.5432,
                "value": "White"
              },
              {
                "lon": -122.0473,
                "lat": 37.5474,
                "value": "White"
              },
              {
                "lon": -122.051,
                "lat": 37.5496,
                "value": "Asian"
              },
              {
                "lon": -122.0517,
                "lat": 37.5451,
                "value": "Asian"
              },
              {
                "lon": -122.0523,
                "lat": 37.5482,
                "value": "Asian"
              },
              {
                "lon": -122.0466,
                "lat": 37.5447,
                "value": "Asian"
              },
              {
                "lon": -122.0528,
                "lat": 37.5446,
                "value": "Asian"
              },
              {
                "lon": -122.0498,
                "lat": 37.5489,
                "value": "Hispanic"
              },
              {
                "lon": -122.0444,
                "lat": 37.5335,
                "value": "Hispanic"
              },
              {
                "lon": -122.0523,
                "lat": 37.5447,
                "value": "Hispanic"
              },
              {
                "lon": -122.0407,
                "lat": 37.5409,
                "value": "Hispanic"
              },
              {
                "lon": -122.0545,
                "lat": 37.5303,
                "value": "White"
              },
              {
                "lon": -122.058,
                "lat": 37.5317,
                "value": "Asian"
              },
              {
                "lon": -122.0552,
                "lat": 37.5314,
                "value": "Asian"
              },
              {
                "lon": -122.058,
                "lat": 37.5315,
                "value": "Hispanic"
              },
              {
                "lon": -122.0377,
                "lat": 37.5118,
                "value": "White"
              },
              {
                "lon": -122.0488,
                "lat": 37.5263,
                "value": "Asian"
              },
              {
                "lon": -122.0409,
                "lat": 37.5115,
                "value": "Asian"
              },
              {
                "lon": -122.0376,
                "lat": 37.5142,
                "value": "Asian"
              },
              {
                "lon": -122.0278,
                "lat": 37.5072,
                "value": "Asian"
              },
              {
                "lon": -122.0397,
                "lat": 37.5023,
                "value": "Asian"
              },
              {
                "lon": -122.0453,
                "lat": 37.5026,
                "value": "Asian"
              },
              {
                "lon": -122.0249,
                "lat": 37.5126,
                "value": "Asian"
              },
              {
                "lon": -122.055,
                "lat": 37.5232,
                "value": "Hispanic"
              },
              {
                "lon": -122.0528,
                "lat": 37.5054,
                "value": "Hispanic"
              },
              {
                "lon": -122.0392,
                "lat": 37.5247,
                "value": "Hispanic"
              },
              {
                "lon": -122.0346,
                "lat": 37.5369,
                "value": "White"
              },
              {
                "lon": -122.0407,
                "lat": 37.5313,
                "value": "Asian"
              },
              {
                "lon": -122.0362,
                "lat": 37.5377,
                "value": "Asian"
              },
              {
                "lon": -122.0311,
                "lat": 37.5429,
                "value": "Hispanic"
              },
              {
                "lon": -122.0347,
                "lat": 37.5331,
                "value": "Hispanic"
              },
              {
                "lon": -122.0361,
                "lat": 37.539,
                "value": "Hispanic"
              },
              {
                "lon": -122.0384,
                "lat": 37.5372,
                "value": "Hispanic"
              },
              {
                "lon": -122.04,
                "lat": 37.5359,
                "value": "Hispanic"
              },
              {
                "lon": -122.0268,
                "lat": 37.5307,
                "value": "White"
              },
              {
                "lon": -122.0275,
                "lat": 37.5311,
                "value": "White"
              },
              {
                "lon": -122.0202,
                "lat": 37.537,
                "value": "Asian"
              },
              {
                "lon": -122.0332,
                "lat": 37.5335,
                "value": "Asian"
              },
              {
                "lon": -122.0205,
                "lat": 37.5389,
                "value": "Asian"
              },
              {
                "lon": -122.03,
                "lat": 37.5342,
                "value": "Hispanic"
              },
              {
                "lon": -122.0287,
                "lat": 37.535,
                "value": "Hispanic"
              },
              {
                "lon": -122.0258,
                "lat": 37.5409,
                "value": "Hispanic"
              },
              {
                "lon": -122.0192,
                "lat": 37.5403,
                "value": "Hispanic"
              },
              {
                "lon": -122.028,
                "lat": 37.54,
                "value": "Hispanic"
              },
              {
                "lon": -122.011,
                "lat": 37.5192,
                "value": "White"
              },
              {
                "lon": -122.0086,
                "lat": 37.527,
                "value": "White"
              },
              {
                "lon": -122.0195,
                "lat": 37.5257,
                "value": "Asian"
              },
              {
                "lon": -122.0259,
                "lat": 37.5272,
                "value": "Asian"
              },
              {
                "lon": -122.0188,
                "lat": 37.5273,
                "value": "Asian"
              },
              {
                "lon": -122.0126,
                "lat": 37.5274,
                "value": "Asian"
              },
              {
                "lon": -122.0119,
                "lat": 37.5249,
                "value": "Asian"
              },
              {
                "lon": -122.0091,
                "lat": 37.5296,
                "value": "Asian"
              },
              {
                "lon": -122.017,
                "lat": 37.5382,
                "value": "Asian"
              },
              {
                "lon": -122.0046,
                "lat": 37.5308,
                "value": "Hispanic"
              },
              {
                "lon": -122.0124,
                "lat": 37.5248,
                "value": "Hispanic"
              },
              {
                "lon": -122.0057,
                "lat": 37.5178,
                "value": "White"
              },
              {
                "lon": -122.0066,
                "lat": 37.5252,
                "value": "Asian"
              },
              {
                "lon": -121.9981,
                "lat": 37.5133,
                "value": "Asian"
              },
              {
                "lon": -121.9911,
                "lat": 37.521,
                "value": "Asian"
              },
              {
                "lon": -122.0075,
                "lat": 37.515,
                "value": "Asian"
              },
              {
                "lon": -121.9963,
                "lat": 37.5246,
                "value": "Asian"
              },
              {
                "lon": -122.0073,
                "lat": 37.5065,
                "value": "Asian"
              },
              {
                "lon": -121.8748,
                "lat": 37.7091,
                "value": "White"
              },
              {
                "lon": -121.8904,
                "lat": 37.7049,
                "value": "White"
              },
              {
                "lon": -121.8851,
                "lat": 37.706,
                "value": "Asian"
              },
              {
                "lon": -121.8827,
                "lat": 37.706,
                "value": "Asian"
              },
              {
                "lon": -121.8952,
                "lat": 37.7024,
                "value": "Asian"
              },
              {
                "lon": -121.8729,
                "lat": 37.7092,
                "value": "Asian"
              },
              {
                "lon": -121.8748,
                "lat": 37.7038,
                "value": "Asian"
              },
              {
                "lon": -121.8868,
                "lat": 37.7052,
                "value": "Asian"
              },
              {
                "lon": -121.8876,
                "lat": 37.7083,
                "value": "Asian"
              },
              {
                "lon": -121.8982,
                "lat": 37.7052,
                "value": "Hispanic"
              },
              {
                "lon": -121.9017,
                "lat": 37.713,
                "value": "White"
              },
              {
                "lon": -121.876,
                "lat": 37.7228,
                "value": "White"
              },
              {
                "lon": -121.8941,
                "lat": 37.7305,
                "value": "White"
              },
              {
                "lon": -121.9061,
                "lat": 37.7146,
                "value": "Black"
              },
              {
                "lon": -121.8987,
                "lat": 37.7154,
                "value": "Asian"
              },
              {
                "lon": -121.8723,
                "lat": 37.721,
                "value": "Asian"
              },
              {
                "lon": -121.8896,
                "lat": 37.7158,
                "value": "Asian"
              },
              {
                "lon": -121.8886,
                "lat": 37.7258,
                "value": "Asian"
              },
              {
                "lon": -121.8966,
                "lat": 37.7084,
                "value": "Asian"
              },
              {
                "lon": -121.9036,
                "lat": 37.7146,
                "value": "Asian"
              },
              {
                "lon": -121.8791,
                "lat": 37.7292,
                "value": "Asian"
              },
              {
                "lon": -121.8826,
                "lat": 37.7199,
                "value": "Hispanic"
              },
              {
                "lon": -121.8788,
                "lat": 37.7321,
                "value": "Hispanic"
              },
              {
                "lon": -121.917,
                "lat": 37.7272,
                "value": "White"
              },
              {
                "lon": -121.9122,
                "lat": 37.7125,
                "value": "White"
              },
              {
                "lon": -121.9106,
                "lat": 37.7269,
                "value": "White"
              },
              {
                "lon": -121.9122,
                "lat": 37.7238,
                "value": "Asian"
              },
              {
                "lon": -121.9108,
                "lat": 37.7137,
                "value": "Asian"
              },
              {
                "lon": -121.9133,
                "lat": 37.726,
                "value": "Asian"
              },
              {
                "lon": -121.9113,
                "lat": 37.7197,
                "value": "Asian"
              },
              {
                "lon": -121.9199,
                "lat": 37.7232,
                "value": "Hispanic"
              },
              {
                "lon": -121.9206,
                "lat": 37.7201,
                "value": "White"
              },
              {
                "lon": -121.9213,
                "lat": 37.7189,
                "value": "White"
              },
              {
                "lon": -121.9237,
                "lat": 37.7207,
                "value": "White"
              },
              {
                "lon": -121.9231,
                "lat": 37.713,
                "value": "White"
              },
              {
                "lon": -121.9178,
                "lat": 37.7094,
                "value": "Asian"
              },
              {
                "lon": -121.9243,
                "lat": 37.7057,
                "value": "Asian"
              },
              {
                "lon": -121.9156,
                "lat": 37.708,
                "value": "Hispanic"
              },
              {
                "lon": -121.9342,
                "lat": 37.7082,
                "value": "White"
              },
              {
                "lon": -121.9369,
                "lat": 37.7229,
                "value": "White"
              },
              {
                "lon": -121.936,
                "lat": 37.715,
                "value": "White"
              },
              {
                "lon": -121.9305,
                "lat": 37.721,
                "value": "White"
              },
              {
                "lon": -121.9343,
                "lat": 37.7069,
                "value": "Asian"
              },
              {
                "lon": -121.9314,
                "lat": 37.7176,
                "value": "Asian"
              },
              {
                "lon": -121.9369,
                "lat": 37.7208,
                "value": "Asian"
              },
              {
                "lon": -121.9358,
                "lat": 37.7119,
                "value": "Asian"
              },
              {
                "lon": -121.9269,
                "lat": 37.719,
                "value": "Asian"
              },
              {
                "lon": -121.9278,
                "lat": 37.7051,
                "value": "Hispanic"
              },
              {
                "lon": -121.9343,
                "lat": 37.7151,
                "value": "Hispanic"
              },
              {
                "lon": -121.9417,
                "lat": 37.7062,
                "value": "White"
              },
              {
                "lon": -121.9438,
                "lat": 37.7125,
                "value": "White"
              },
              {
                "lon": -121.9398,
                "lat": 37.7017,
                "value": "White"
              },
              {
                "lon": -121.9443,
                "lat": 37.7062,
                "value": "Asian"
              },
              {
                "lon": -121.9765,
                "lat": 37.7059,
                "value": "White"
              },
              {
                "lon": -121.9712,
                "lat": 37.7195,
                "value": "White"
              },
              {
                "lon": -121.96,
                "lat": 37.7007,
                "value": "White"
              },
              {
                "lon": -121.9599,
                "lat": 37.6983,
                "value": "White"
              },
              {
                "lon": -121.9668,
                "lat": 37.7043,
                "value": "Asian"
              },
              {
                "lon": -121.9675,
                "lat": 37.7027,
                "value": "Asian"
              },
              {
                "lon": -121.9628,
                "lat": 37.7042,
                "value": "Asian"
              },
              {
                "lon": -121.9652,
                "lat": 37.7006,
                "value": "Asian"
              },
              {
                "lon": -121.9622,
                "lat": 37.7155,
                "value": "Asian"
              },
              {
                "lon": -121.9688,
                "lat": 37.7214,
                "value": "Hispanic"
              },
              {
                "lon": -121.9817,
                "lat": 37.6963,
                "value": "White"
              },
              {
                "lon": -121.9551,
                "lat": 37.662,
                "value": "White"
              },
              {
                "lon": -121.9061,
                "lat": 37.6312,
                "value": "White"
              },
              {
                "lon": -121.8894,
                "lat": 37.5994,
                "value": "Asian"
              },
              {
                "lon": -121.9367,
                "lat": 37.6933,
                "value": "Asian"
              },
              {
                "lon": -121.8829,
                "lat": 37.6024,
                "value": "Asian"
              },
              {
                "lon": -121.9044,
                "lat": 37.6933,
                "value": "White"
              },
              {
                "lon": -121.9149,
                "lat": 37.701,
                "value": "White"
              },
              {
                "lon": -121.9129,
                "lat": 37.6915,
                "value": "White"
              },
              {
                "lon": -121.9155,
                "lat": 37.6962,
                "value": "Asian"
              },
              {
                "lon": -121.9073,
                "lat": 37.6918,
                "value": "Asian"
              },
              {
                "lon": -121.9146,
                "lat": 37.6965,
                "value": "Asian"
              },
              {
                "lon": -121.903,
                "lat": 37.6785,
                "value": "Hispanic"
              },
              {
                "lon": -121.885,
                "lat": 37.6844,
                "value": "White"
              },
              {
                "lon": -121.8955,
                "lat": 37.6771,
                "value": "White"
              },
              {
                "lon": -121.8796,
                "lat": 37.6877,
                "value": "White"
              },
              {
                "lon": -121.8891,
                "lat": 37.6803,
                "value": "White"
              },
              {
                "lon": -121.9022,
                "lat": 37.6801,
                "value": "Asian"
              },
              {
                "lon": -121.8943,
                "lat": 37.6794,
                "value": "Asian"
              },
              {
                "lon": -121.8824,
                "lat": 37.6836,
                "value": "Hispanic"
              },
              {
                "lon": -121.8865,
                "lat": 37.6743,
                "value": "White"
              },
              {
                "lon": -121.8916,
                "lat": 37.6745,
                "value": "White"
              },
              {
                "lon": -121.8774,
                "lat": 37.6767,
                "value": "White"
              },
              {
                "lon": -121.8889,
                "lat": 37.6746,
                "value": "Asian"
              },
              {
                "lon": -121.8753,
                "lat": 37.6656,
                "value": "Asian"
              },
              {
                "lon": -121.8808,
                "lat": 37.6717,
                "value": "Asian"
              },
              {
                "lon": -121.903,
                "lat": 37.6712,
                "value": "White"
              },
              {
                "lon": -121.8947,
                "lat": 37.6741,
                "value": "White"
              },
              {
                "lon": -121.896,
                "lat": 37.6714,
                "value": "White"
              },
              {
                "lon": -121.8929,
                "lat": 37.6719,
                "value": "White"
              },
              {
                "lon": -121.8935,
                "lat": 37.6695,
                "value": "White"
              },
              {
                "lon": -121.8914,
                "lat": 37.6719,
                "value": "Asian"
              },
              {
                "lon": -121.8973,
                "lat": 37.6673,
                "value": "Asian"
              },
              {
                "lon": -121.9034,
                "lat": 37.6701,
                "value": "Asian"
              },
              {
                "lon": -121.9021,
                "lat": 37.6723,
                "value": "Asian"
              },
              {
                "lon": -121.8982,
                "lat": 37.6658,
                "value": "Asian"
              },
              {
                "lon": -121.8854,
                "lat": 37.6539,
                "value": "White"
              },
              {
                "lon": -121.8874,
                "lat": 37.666,
                "value": "White"
              },
              {
                "lon": -121.8891,
                "lat": 37.662,
                "value": "White"
              },
              {
                "lon": -121.8977,
                "lat": 37.6591,
                "value": "Asian"
              },
              {
                "lon": -121.8876,
                "lat": 37.6489,
                "value": "Asian"
              },
              {
                "lon": -121.8907,
                "lat": 37.6534,
                "value": "Asian"
              },
              {
                "lon": -121.8881,
                "lat": 37.6561,
                "value": "Hispanic"
              },
              {
                "lon": -121.8898,
                "lat": 37.6665,
                "value": "Hispanic"
              },
              {
                "lon": -121.8956,
                "lat": 37.6447,
                "value": "White"
              },
              {
                "lon": -121.8873,
                "lat": 37.6398,
                "value": "White"
              },
              {
                "lon": -121.8981,
                "lat": 37.6434,
                "value": "White"
              },
              {
                "lon": -121.8934,
                "lat": 37.6485,
                "value": "Asian"
              },
              {
                "lon": -121.9002,
                "lat": 37.6453,
                "value": "Asian"
              },
              {
                "lon": -121.9064,
                "lat": 37.6584,
                "value": "Asian"
              },
              {
                "lon": -121.9053,
                "lat": 37.6588,
                "value": "Asian"
              },
              {
                "lon": -121.9328,
                "lat": 37.6961,
                "value": "White"
              },
              {
                "lon": -121.9286,
                "lat": 37.6938,
                "value": "White"
              },
              {
                "lon": -121.9203,
                "lat": 37.6774,
                "value": "White"
              },
              {
                "lon": -121.9264,
                "lat": 37.6843,
                "value": "White"
              },
              {
                "lon": -121.9226,
                "lat": 37.6944,
                "value": "Asian"
              },
              {
                "lon": -121.9315,
                "lat": 37.6986,
                "value": "Asian"
              },
              {
                "lon": -121.9219,
                "lat": 37.682,
                "value": "Asian"
              },
              {
                "lon": -121.9303,
                "lat": 37.693,
                "value": "Hispanic"
              },
              {
                "lon": -121.7359,
                "lat": 37.5288,
                "value": "White"
              },
              {
                "lon": -121.7037,
                "lat": 37.5517,
                "value": "White"
              },
              {
                "lon": -121.7803,
                "lat": 37.5028,
                "value": "White"
              },
              {
                "lon": -121.7756,
                "lat": 37.5389,
                "value": "White"
              },
              {
                "lon": -121.7299,
                "lat": 37.5528,
                "value": "White"
              },
              {
                "lon": -121.754,
                "lat": 37.559,
                "value": "White"
              },
              {
                "lon": -121.7916,
                "lat": 37.6073,
                "value": "White"
              },
              {
                "lon": -121.7338,
                "lat": 37.5082,
                "value": "Asian"
              },
              {
                "lon": -121.7944,
                "lat": 37.5032,
                "value": "Asian"
              },
              {
                "lon": -121.8159,
                "lat": 37.5575,
                "value": "Asian"
              },
              {
                "lon": -121.8952,
                "lat": 37.5874,
                "value": "Asian"
              },
              {
                "lon": -121.8824,
                "lat": 37.5683,
                "value": "Asian"
              },
              {
                "lon": -121.9146,
                "lat": 37.5681,
                "value": "Asian"
              },
              {
                "lon": -121.843,
                "lat": 37.5649,
                "value": "Asian"
              },
              {
                "lon": -121.7793,
                "lat": 37.536,
                "value": "Hispanic"
              },
              {
                "lon": -121.8756,
                "lat": 37.6565,
                "value": "White"
              },
              {
                "lon": -121.8595,
                "lat": 37.6662,
                "value": "White"
              },
              {
                "lon": -121.8632,
                "lat": 37.6623,
                "value": "White"
              },
              {
                "lon": -121.8611,
                "lat": 37.6574,
                "value": "White"
              },
              {
                "lon": -121.8651,
                "lat": 37.6625,
                "value": "Asian"
              },
              {
                "lon": -121.8714,
                "lat": 37.658,
                "value": "Asian"
              },
              {
                "lon": -121.8657,
                "lat": 37.6599,
                "value": "Hispanic"
              },
              {
                "lon": -121.861,
                "lat": 37.6655,
                "value": "Hispanic"
              },
              {
                "lon": -121.8273,
                "lat": 37.6634,
                "value": "White"
              },
              {
                "lon": -121.8303,
                "lat": 37.6639,
                "value": "White"
              },
              {
                "lon": -121.8301,
                "lat": 37.6621,
                "value": "White"
              },
              {
                "lon": -121.8211,
                "lat": 37.6679,
                "value": "White"
              },
              {
                "lon": -121.8239,
                "lat": 37.6684,
                "value": "Asian"
              },
              {
                "lon": -121.831,
                "lat": 37.6593,
                "value": "Asian"
              },
              {
                "lon": -121.8146,
                "lat": 37.6682,
                "value": "Asian"
              },
              {
                "lon": -121.8488,
                "lat": 37.6593,
                "value": "Asian"
              },
              {
                "lon": -121.903,
                "lat": 37.699,
                "value": "White"
              },
              {
                "lon": -121.8989,
                "lat": 37.6984,
                "value": "White"
              },
              {
                "lon": -121.8869,
                "lat": 37.6954,
                "value": "White"
              },
              {
                "lon": -121.887,
                "lat": 37.6948,
                "value": "Black"
              },
              {
                "lon": -121.8827,
                "lat": 37.6954,
                "value": "Asian"
              },
              {
                "lon": -121.8826,
                "lat": 37.6966,
                "value": "Asian"
              },
              {
                "lon": -121.8924,
                "lat": 37.6851,
                "value": "Asian"
              },
              {
                "lon": -121.8844,
                "lat": 37.6931,
                "value": "Asian"
              },
              {
                "lon": -121.8862,
                "lat": 37.6925,
                "value": "Asian"
              },
              {
                "lon": -121.8993,
                "lat": 37.6847,
                "value": "Asian"
              },
              {
                "lon": -121.8981,
                "lat": 37.6909,
                "value": "Asian"
              },
              {
                "lon": -121.8811,
                "lat": 37.6993,
                "value": "Asian"
              },
              {
                "lon": -121.8844,
                "lat": 37.6934,
                "value": "Hispanic"
              },
              {
                "lon": -121.8884,
                "lat": 37.6963,
                "value": "Hispanic"
              },
              {
                "lon": -121.8787,
                "lat": 37.7006,
                "value": "White"
              },
              {
                "lon": -121.8538,
                "lat": 37.6978,
                "value": "White"
              },
              {
                "lon": -121.8694,
                "lat": 37.7014,
                "value": "White"
              },
              {
                "lon": -121.8635,
                "lat": 37.6966,
                "value": "White"
              },
              {
                "lon": -121.851,
                "lat": 37.6963,
                "value": "White"
              },
              {
                "lon": -121.8773,
                "lat": 37.6976,
                "value": "Asian"
              },
              {
                "lon": -121.8559,
                "lat": 37.6941,
                "value": "Asian"
              },
              {
                "lon": -121.8756,
                "lat": 37.6969,
                "value": "Asian"
              },
              {
                "lon": -121.8782,
                "lat": 37.693,
                "value": "Hispanic"
              },
              {
                "lon": -121.8626,
                "lat": 37.6955,
                "value": "Hispanic"
              },
              {
                "lon": -121.8556,
                "lat": 37.68,
                "value": "White"
              },
              {
                "lon": -121.8483,
                "lat": 37.6832,
                "value": "White"
              },
              {
                "lon": -121.8402,
                "lat": 37.6881,
                "value": "White"
              },
              {
                "lon": -121.8427,
                "lat": 37.6766,
                "value": "Asian"
              },
              {
                "lon": -121.8536,
                "lat": 37.6833,
                "value": "Asian"
              },
              {
                "lon": -121.864,
                "lat": 37.6798,
                "value": "Asian"
              },
              {
                "lon": -121.8711,
                "lat": 37.6912,
                "value": "Asian"
              },
              {
                "lon": -121.8762,
                "lat": 37.6873,
                "value": "Asian"
              },
              {
                "lon": -121.8476,
                "lat": 37.6907,
                "value": "Asian"
              },
              {
                "lon": -121.8638,
                "lat": 37.6778,
                "value": "Asian"
              },
              {
                "lon": -121.8732,
                "lat": 37.6755,
                "value": "White"
              },
              {
                "lon": -121.8641,
                "lat": 37.6712,
                "value": "White"
              },
              {
                "lon": -121.8731,
                "lat": 37.6831,
                "value": "Asian"
              },
              {
                "lon": -121.8621,
                "lat": 37.6695,
                "value": "Hispanic"
              },
              {
                "lon": -121.8666,
                "lat": 37.7049,
                "value": "White"
              },
              {
                "lon": -121.8519,
                "lat": 37.7099,
                "value": "White"
              },
              {
                "lon": -121.8572,
                "lat": 37.7052,
                "value": "Asian"
              },
              {
                "lon": -121.8618,
                "lat": 37.7022,
                "value": "Asian"
              },
              {
                "lon": -121.8653,
                "lat": 37.7091,
                "value": "Asian"
              },
              {
                "lon": -121.8651,
                "lat": 37.7052,
                "value": "Asian"
              },
              {
                "lon": -121.8653,
                "lat": 37.7073,
                "value": "Asian"
              },
              {
                "lon": -121.8617,
                "lat": 37.7083,
                "value": "Asian"
              },
              {
                "lon": -121.8619,
                "lat": 37.7062,
                "value": "Asian"
              },
              {
                "lon": -121.8629,
                "lat": 37.7063,
                "value": "Asian"
              },
              {
                "lon": -121.8319,
                "lat": 37.7168,
                "value": "White"
              },
              {
                "lon": -121.8633,
                "lat": 37.7109,
                "value": "White"
              },
              {
                "lon": -121.8415,
                "lat": 37.7122,
                "value": "White"
              },
              {
                "lon": -121.833,
                "lat": 37.7055,
                "value": "Asian"
              },
              {
                "lon": -121.8411,
                "lat": 37.7195,
                "value": "Asian"
              },
              {
                "lon": -121.8245,
                "lat": 37.7095,
                "value": "Asian"
              },
              {
                "lon": -121.8431,
                "lat": 37.7279,
                "value": "Asian"
              },
              {
                "lon": -121.8301,
                "lat": 37.7251,
                "value": "Asian"
              },
              {
                "lon": -121.8349,
                "lat": 37.707,
                "value": "Asian"
              },
              {
                "lon": -121.8407,
                "lat": 37.7199,
                "value": "Asian"
              },
              {
                "lon": -121.8421,
                "lat": 37.7306,
                "value": "Asian"
              },
              {
                "lon": -121.8614,
                "lat": 37.7137,
                "value": "Asian"
              },
              {
                "lon": -121.8645,
                "lat": 37.7111,
                "value": "Asian"
              },
              {
                "lon": -121.8457,
                "lat": 37.728,
                "value": "Asian"
              },
              {
                "lon": -121.8497,
                "lat": 37.7155,
                "value": "Asian"
              },
              {
                "lon": -121.8249,
                "lat": 37.7176,
                "value": "Asian"
              },
              {
                "lon": -121.8388,
                "lat": 37.7092,
                "value": "Asian"
              },
              {
                "lon": -121.8533,
                "lat": 37.7271,
                "value": "Asian"
              },
              {
                "lon": -121.8341,
                "lat": 37.7038,
                "value": "Asian"
              },
              {
                "lon": -121.8301,
                "lat": 37.7113,
                "value": "Asian"
              },
              {
                "lon": -121.8296,
                "lat": 37.7175,
                "value": "Asian"
              },
              {
                "lon": -121.8436,
                "lat": 37.715,
                "value": "Hispanic"
              },
              {
                "lon": -121.8445,
                "lat": 37.7396,
                "value": "White"
              },
              {
                "lon": -121.8198,
                "lat": 37.751,
                "value": "White"
              },
              {
                "lon": -121.8143,
                "lat": 37.7438,
                "value": "Asian"
              },
              {
                "lon": -121.838,
                "lat": 37.7427,
                "value": "Asian"
              },
              {
                "lon": -121.8247,
                "lat": 37.726,
                "value": "Asian"
              },
              {
                "lon": -121.8081,
                "lat": 37.7042,
                "value": "Asian"
              },
              {
                "lon": -121.8151,
                "lat": 37.7165,
                "value": "Asian"
              },
              {
                "lon": -121.8227,
                "lat": 37.7226,
                "value": "Asian"
              },
              {
                "lon": -121.8158,
                "lat": 37.7116,
                "value": "Asian"
              },
              {
                "lon": -121.815,
                "lat": 37.7168,
                "value": "Asian"
              },
              {
                "lon": -121.8732,
                "lat": 37.7329,
                "value": "Asian"
              },
              {
                "lon": -121.8573,
                "lat": 37.7311,
                "value": "Asian"
              },
              {
                "lon": -121.8596,
                "lat": 37.7309,
                "value": "Asian"
              },
              {
                "lon": -121.816,
                "lat": 37.7312,
                "value": "Asian"
              },
              {
                "lon": -121.8671,
                "lat": 37.7388,
                "value": "Asian"
              },
              {
                "lon": -121.8563,
                "lat": 37.7208,
                "value": "Hispanic"
              },
              {
                "lon": -121.7895,
                "lat": 37.6451,
                "value": "White"
              },
              {
                "lon": -121.7901,
                "lat": 37.6473,
                "value": "White"
              },
              {
                "lon": -121.7841,
                "lat": 37.6483,
                "value": "White"
              },
              {
                "lon": -121.7715,
                "lat": 37.6477,
                "value": "White"
              },
              {
                "lon": -121.8,
                "lat": 37.644,
                "value": "White"
              },
              {
                "lon": -121.7782,
                "lat": 37.6517,
                "value": "Asian"
              },
              {
                "lon": -121.7369,
                "lat": 37.6629,
                "value": "White"
              },
              {
                "lon": -121.7079,
                "lat": 37.6166,
                "value": "White"
              },
              {
                "lon": -121.6547,
                "lat": 37.6344,
                "value": "White"
              },
              {
                "lon": -121.5812,
                "lat": 37.5882,
                "value": "White"
              },
              {
                "lon": -121.687,
                "lat": 37.6107,
                "value": "White"
              },
              {
                "lon": -121.6823,
                "lat": 37.6734,
                "value": "White"
              },
              {
                "lon": -121.7495,
                "lat": 37.5955,
                "value": "White"
              },
              {
                "lon": -121.5793,
                "lat": 37.6079,
                "value": "White"
              },
              {
                "lon": -121.6936,
                "lat": 37.7499,
                "value": "White"
              },
              {
                "lon": -121.6771,
                "lat": 37.7163,
                "value": "Asian"
              },
              {
                "lon": -121.6961,
                "lat": 37.6723,
                "value": "Asian"
              },
              {
                "lon": -121.5326,
                "lat": 37.5143,
                "value": "Hispanic"
              },
              {
                "lon": -121.707,
                "lat": 37.7653,
                "value": "Hispanic"
              },
              {
                "lon": -121.733,
                "lat": 37.7121,
                "value": "White"
              },
              {
                "lon": -121.7424,
                "lat": 37.7063,
                "value": "White"
              },
              {
                "lon": -121.7361,
                "lat": 37.7121,
                "value": "White"
              },
              {
                "lon": -121.7261,
                "lat": 37.7124,
                "value": "White"
              },
              {
                "lon": -121.7345,
                "lat": 37.7049,
                "value": "White"
              },
              {
                "lon": -121.7424,
                "lat": 37.7176,
                "value": "White"
              },
              {
                "lon": -121.7345,
                "lat": 37.7071,
                "value": "White"
              },
              {
                "lon": -121.7461,
                "lat": 37.7105,
                "value": "Asian"
              },
              {
                "lon": -121.7286,
                "lat": 37.7077,
                "value": "Asian"
              },
              {
                "lon": -121.7339,
                "lat": 37.7169,
                "value": "Hispanic"
              },
              {
                "lon": -121.7339,
                "lat": 37.7069,
                "value": "Hispanic"
              },
              {
                "lon": -121.7291,
                "lat": 37.7106,
                "value": "Hispanic"
              },
              {
                "lon": -121.7624,
                "lat": 37.7463,
                "value": "White"
              },
              {
                "lon": -121.7785,
                "lat": 37.7082,
                "value": "White"
              },
              {
                "lon": -121.7611,
                "lat": 37.7217,
                "value": "White"
              },
              {
                "lon": -121.7921,
                "lat": 37.735,
                "value": "White"
              },
              {
                "lon": -121.7876,
                "lat": 37.7041,
                "value": "Asian"
              },
              {
                "lon": -121.8008,
                "lat": 37.7207,
                "value": "Asian"
              },
              {
                "lon": -121.7644,
                "lat": 37.7229,
                "value": "Asian"
              },
              {
                "lon": -121.7747,
                "lat": 37.7629,
                "value": "Hispanic"
              },
              {
                "lon": -121.8082,
                "lat": 37.6836,
                "value": "White"
              },
              {
                "lon": -121.8155,
                "lat": 37.6927,
                "value": "White"
              },
              {
                "lon": -121.821,
                "lat": 37.6924,
                "value": "White"
              },
              {
                "lon": -121.7904,
                "lat": 37.6977,
                "value": "White"
              },
              {
                "lon": -121.7954,
                "lat": 37.6929,
                "value": "White"
              },
              {
                "lon": -121.8119,
                "lat": 37.6787,
                "value": "White"
              },
              {
                "lon": -121.8044,
                "lat": 37.6934,
                "value": "Asian"
              },
              {
                "lon": -121.8119,
                "lat": 37.6923,
                "value": "Hispanic"
              },
              {
                "lon": -121.821,
                "lat": 37.6777,
                "value": "Hispanic"
              },
              {
                "lon": -121.7498,
                "lat": 37.6981,
                "value": "White"
              },
              {
                "lon": -121.7821,
                "lat": 37.6964,
                "value": "White"
              },
              {
                "lon": -121.7655,
                "lat": 37.701,
                "value": "White"
              },
              {
                "lon": -121.7466,
                "lat": 37.7005,
                "value": "White"
              },
              {
                "lon": -121.7727,
                "lat": 37.6916,
                "value": "Hispanic"
              },
              {
                "lon": -121.7626,
                "lat": 37.6876,
                "value": "Hispanic"
              },
              {
                "lon": -121.7515,
                "lat": 37.7023,
                "value": "Hispanic"
              },
              {
                "lon": -121.7528,
                "lat": 37.6921,
                "value": "Hispanic"
              },
              {
                "lon": -121.7645,
                "lat": 37.6963,
                "value": "Hispanic"
              },
              {
                "lon": -121.7897,
                "lat": 37.6884,
                "value": "White"
              },
              {
                "lon": -121.778,
                "lat": 37.6916,
                "value": "White"
              },
              {
                "lon": -121.785,
                "lat": 37.6878,
                "value": "White"
              },
              {
                "lon": -121.7819,
                "lat": 37.6874,
                "value": "White"
              },
              {
                "lon": -121.7825,
                "lat": 37.6818,
                "value": "White"
              },
              {
                "lon": -121.7652,
                "lat": 37.6859,
                "value": "White"
              },
              {
                "lon": -121.7822,
                "lat": 37.6833,
                "value": "Asian"
              },
              {
                "lon": -121.773,
                "lat": 37.6841,
                "value": "Hispanic"
              },
              {
                "lon": -121.7813,
                "lat": 37.6831,
                "value": "Hispanic"
              },
              {
                "lon": -121.7803,
                "lat": 37.6874,
                "value": "Hispanic"
              },
              {
                "lon": -121.7731,
                "lat": 37.6883,
                "value": "Hispanic"
              },
              {
                "lon": -121.7812,
                "lat": 37.6819,
                "value": "Hispanic"
              },
              {
                "lon": -121.7893,
                "lat": 37.686,
                "value": "Hispanic"
              },
              {
                "lon": -121.7899,
                "lat": 37.6862,
                "value": "Hispanic"
              },
              {
                "lon": -121.7223,
                "lat": 37.678,
                "value": "White"
              },
              {
                "lon": -121.7431,
                "lat": 37.6705,
                "value": "White"
              },
              {
                "lon": -121.7252,
                "lat": 37.6712,
                "value": "White"
              },
              {
                "lon": -121.726,
                "lat": 37.6763,
                "value": "White"
              },
              {
                "lon": -121.7315,
                "lat": 37.6725,
                "value": "White"
              },
              {
                "lon": -121.7391,
                "lat": 37.6695,
                "value": "Asian"
              },
              {
                "lon": -121.7335,
                "lat": 37.6731,
                "value": "Hispanic"
              },
              {
                "lon": -121.7359,
                "lat": 37.6805,
                "value": "White"
              },
              {
                "lon": -121.7524,
                "lat": 37.6876,
                "value": "White"
              },
              {
                "lon": -121.7386,
                "lat": 37.6823,
                "value": "White"
              },
              {
                "lon": -121.7446,
                "lat": 37.6814,
                "value": "White"
              },
              {
                "lon": -121.7457,
                "lat": 37.6891,
                "value": "White"
              },
              {
                "lon": -121.7456,
                "lat": 37.6807,
                "value": "White"
              },
              {
                "lon": -121.7499,
                "lat": 37.6914,
                "value": "Asian"
              },
              {
                "lon": -121.7631,
                "lat": 37.6816,
                "value": "Hispanic"
              },
              {
                "lon": -121.7412,
                "lat": 37.6808,
                "value": "Hispanic"
              },
              {
                "lon": -121.7356,
                "lat": 37.6905,
                "value": "White"
              },
              {
                "lon": -121.7198,
                "lat": 37.6885,
                "value": "White"
              },
              {
                "lon": -121.7287,
                "lat": 37.6934,
                "value": "White"
              },
              {
                "lon": -121.7257,
                "lat": 37.6922,
                "value": "White"
              },
              {
                "lon": -121.7271,
                "lat": 37.6874,
                "value": "White"
              },
              {
                "lon": -121.7224,
                "lat": 37.6804,
                "value": "White"
              },
              {
                "lon": -121.7338,
                "lat": 37.6863,
                "value": "White"
              },
              {
                "lon": -121.7334,
                "lat": 37.6822,
                "value": "Asian"
              },
              {
                "lon": -121.7303,
                "lat": 37.6836,
                "value": "Hispanic"
              },
              {
                "lon": -121.7357,
                "lat": 37.6859,
                "value": "Hispanic"
              },
              {
                "lon": -121.7637,
                "lat": 37.6602,
                "value": "White"
              },
              {
                "lon": -121.7605,
                "lat": 37.6725,
                "value": "White"
              },
              {
                "lon": -121.7602,
                "lat": 37.6639,
                "value": "White"
              },
              {
                "lon": -121.7583,
                "lat": 37.6636,
                "value": "White"
              },
              {
                "lon": -121.751,
                "lat": 37.6655,
                "value": "White"
              },
              {
                "lon": -121.7571,
                "lat": 37.6653,
                "value": "White"
              },
              {
                "lon": -121.7584,
                "lat": 37.6678,
                "value": "Asian"
              },
              {
                "lon": -121.7713,
                "lat": 37.6782,
                "value": "White"
              },
              {
                "lon": -121.7815,
                "lat": 37.6802,
                "value": "White"
              },
              {
                "lon": -121.772,
                "lat": 37.6781,
                "value": "White"
              },
              {
                "lon": -121.7792,
                "lat": 37.673,
                "value": "White"
              },
              {
                "lon": -121.7745,
                "lat": 37.6764,
                "value": "White"
              },
              {
                "lon": -121.7699,
                "lat": 37.6768,
                "value": "White"
              },
              {
                "lon": -121.773,
                "lat": 37.6645,
                "value": "White"
              },
              {
                "lon": -121.769,
                "lat": 37.6712,
                "value": "White"
              },
              {
                "lon": -121.7736,
                "lat": 37.6691,
                "value": "White"
              },
              {
                "lon": -121.7771,
                "lat": 37.6643,
                "value": "Asian"
              },
              {
                "lon": -121.7822,
                "lat": 37.6759,
                "value": "Hispanic"
              },
              {
                "lon": -121.776,
                "lat": 37.6703,
                "value": "Hispanic"
              },
              {
                "lon": -121.7894,
                "lat": 37.6727,
                "value": "White"
              },
              {
                "lon": -121.7864,
                "lat": 37.6677,
                "value": "White"
              },
              {
                "lon": -121.7908,
                "lat": 37.6711,
                "value": "White"
              },
              {
                "lon": -121.7847,
                "lat": 37.6743,
                "value": "Asian"
              },
              {
                "lon": -121.7996,
                "lat": 37.6588,
                "value": "White"
              },
              {
                "lon": -121.8047,
                "lat": 37.6661,
                "value": "White"
              },
              {
                "lon": -121.7997,
                "lat": 37.659,
                "value": "White"
              },
              {
                "lon": -121.8012,
                "lat": 37.6708,
                "value": "White"
              },
              {
                "lon": -121.8051,
                "lat": 37.6726,
                "value": "Asian"
              },
              {
                "lon": -121.7973,
                "lat": 37.6678,
                "value": "White"
              },
              {
                "lon": -121.7813,
                "lat": 37.6627,
                "value": "White"
              },
              {
                "lon": -121.7872,
                "lat": 37.6607,
                "value": "White"
              },
              {
                "lon": -121.7826,
                "lat": 37.6643,
                "value": "White"
              },
              {
                "lon": -121.7932,
                "lat": 37.6643,
                "value": "White"
              },
              {
                "lon": -121.785,
                "lat": 37.6581,
                "value": "Asian"
              },
              {
                "lon": -121.7889,
                "lat": 37.6573,
                "value": "Hispanic"
              }
            ]
          },
          "mark": {
            "type": "circle",
            "opacity": 0.6,
            "size": 8
          },
          "encoding": {
            "color": {
              "field": "value",
              "legend": {
                "title": "Race/Ethnicity"
              },
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
              "type": "nominal"
            },
            "latitude": {
              "field": "lat",
              "type": "quantitative"
            },
            "longitude": {
              "field": "lon",
              "type": "quantitative"
            }
          }
        }
      ],
      "height": 500,
      "projection": {
        "type": "mercator"
      },
      "title": "Racial & Ethnic Dot Density \u2014 Alameda County, CA (1 dot = 500 people)",
      "width": 500,
      "$schema": "https://vega.github.io/schema/vega-lite/v5.json"
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
