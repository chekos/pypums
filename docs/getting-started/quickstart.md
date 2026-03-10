# Quick Start

Three runnable examples to get you productive with PyPUMS in under five minutes.
Each example assumes you have already [installed PyPUMS and configured your API key](installation.md).

---

## 1. Get a table -- County-level median household income

Fetch median household income (variable `B19013_001`) for every county in California from the 2023 ACS 5-year estimates.

```python
import pypums

ca_income = pypums.get_acs(
    geography="county",       # (1)!
    variables="B19013_001",   # (2)!
    state="CA",               # (3)!
    year=2023,                # (4)!
    survey="acs5",            # (5)!
)

print(ca_income.head())
```

1. **geography** -- The level of geographic detail. Common values: `"state"`, `"county"`, `"tract"`, `"block group"`, `"place"`, `"zip code tabulation area"`.
2. **variables** -- One or more Census variable codes. `B19013_001` is median household income from table B19013. Pass a list for multiple variables: `["B19013_001", "B01001_001"]`.
3. **state** -- Filter to a single state. Accepts FIPS codes (`"06"`), abbreviations (`"CA"`), or full names (`"California"`).
4. **year** -- The data year. Defaults to `2023`.
5. **survey** -- `"acs5"` (5-year, default) or `"acs1"` (1-year). See [Census 101](census-101.md) for guidance on which to choose.

**Expected output** (tidy format, one row per geography per variable):

```
     GEOID               NAME      variable  estimate     moe
0  06001  Alameda County, ...  B19013_001  113650.0  1282.0
1  06003   Alpine County, ...  B19013_001   72857.0  9631.0
2  06005   Amador County, ...  B19013_001   71346.0  4076.0
3  06007    Butte County, ...  B19013_001   56219.0  1775.0
4  06009 Calaveras County, ...  B19013_001   70587.0  5047.0
```

| Column       | Description                                                  |
|--------------|--------------------------------------------------------------|
| `GEOID`      | FIPS code identifying the geography (state + county)         |
| `NAME`       | Human-readable place name from the Census Bureau             |
| `variable`   | The Census variable code you requested                       |
| `estimate`   | The point estimate value                                     |
| `moe`        | Margin of error at 90% confidence (default)                  |

!!! tip "Wide format"
    Pass `output="wide"` to get one column per variable instead of the tidy
    (long) layout. This is useful when you need to compute ratios across
    variables in the same row.

**What to try next:** [ACS Data guide](../guides/acs-data.md) for multi-variable queries, summary variables, and confidence level adjustment.

---

## 2. Make a map -- Tract-level choropleth

Fetch tract-level poverty rates for Los Angeles County and plot a choropleth. This requires the `spatial` extras (`uv add "pypums[spatial]"`).

```python
import pypums

la_poverty = pypums.get_acs(
    geography="tract",        # (1)!
    variables="B17001_002",   # (2)!
    state="CA",               # (3)!
    county="037",             # (4)!
    year=2023,
    survey="acs5",
    geometry=True,            # (5)!
)

print(la_poverty.head())
print(type(la_poverty))  # <class 'geopandas.geodataframe.GeoDataFrame'>
```

1. **geography** -- `"tract"` gives you Census tracts, small statistical areas with 1,200--8,000 people.
2. **variables** -- `B17001_002` is the count of people whose income is below the poverty level (from table B17001).
3. **state** -- Required for tract-level queries so the API knows which state to pull tracts from.
4. **county** -- `"037"` is the FIPS code for Los Angeles County. Use `pypums.datasets.fips.lookup_fips(state="California", county="Los Angeles County")` to look up codes.
5. **geometry** -- When `True`, PyPUMS fetches TIGER/Line cartographic boundary shapefiles and merges them with the data. The result is a `GeoDataFrame` with a `geometry` column.

Now plot it with [Altair](https://altair-viz.github.io/):

```python
import altair as alt

alt.Chart(la_poverty).mark_geoshape(
    stroke="white", strokeWidth=0.3,
).encode(
    color=alt.Color(
        "estimate:Q",
        scale=alt.Scale(scheme="yelloworangered"),
        legend=alt.Legend(title="Below Poverty Level"),
    ),
    tooltip=["NAME:N", alt.Tooltip("estimate:Q", format=",")],
).project("albersUsa").properties(
    width=600, height=500,
    title="Poverty by Census Tract, Los Angeles County",
)
```

The resulting map shows poverty counts by Census tract across Los Angeles County, with darker shades indicating higher counts.

```vegalite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": 600,
  "height": 400,
  "title": "Population by State (sample choropleth)",
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
            {"id": 1, "estimate": 5074296, "name": "Alabama"},
            {"id": 2, "estimate": 733583, "name": "Alaska"},
            {"id": 4, "estimate": 7359197, "name": "Arizona"},
            {"id": 5, "estimate": 3045637, "name": "Arkansas"},
            {"id": 6, "estimate": 39029342, "name": "California"},
            {"id": 8, "estimate": 5839926, "name": "Colorado"},
            {"id": 9, "estimate": 3626205, "name": "Connecticut"},
            {"id": 10, "estimate": 1018396, "name": "Delaware"},
            {"id": 12, "estimate": 22244823, "name": "Florida"},
            {"id": 13, "estimate": 10912876, "name": "Georgia"},
            {"id": 15, "estimate": 1440196, "name": "Hawaii"},
            {"id": 16, "estimate": 1939033, "name": "Idaho"},
            {"id": 17, "estimate": 12582032, "name": "Illinois"},
            {"id": 18, "estimate": 6833037, "name": "Indiana"},
            {"id": 19, "estimate": 3200517, "name": "Iowa"},
            {"id": 20, "estimate": 2937150, "name": "Kansas"},
            {"id": 21, "estimate": 4512310, "name": "Kentucky"},
            {"id": 22, "estimate": 4590241, "name": "Louisiana"},
            {"id": 23, "estimate": 1385340, "name": "Maine"},
            {"id": 24, "estimate": 6164660, "name": "Maryland"},
            {"id": 25, "estimate": 6981974, "name": "Massachusetts"},
            {"id": 26, "estimate": 10034113, "name": "Michigan"},
            {"id": 27, "estimate": 5717184, "name": "Minnesota"},
            {"id": 28, "estimate": 2940057, "name": "Mississippi"},
            {"id": 29, "estimate": 6177957, "name": "Missouri"},
            {"id": 30, "estimate": 1122867, "name": "Montana"},
            {"id": 31, "estimate": 1967923, "name": "Nebraska"},
            {"id": 32, "estimate": 3177772, "name": "Nevada"},
            {"id": 33, "estimate": 1395231, "name": "New Hampshire"},
            {"id": 34, "estimate": 9261699, "name": "New Jersey"},
            {"id": 35, "estimate": 2113344, "name": "New Mexico"},
            {"id": 36, "estimate": 19677151, "name": "New York"},
            {"id": 37, "estimate": 10698973, "name": "North Carolina"},
            {"id": 38, "estimate": 779261, "name": "North Dakota"},
            {"id": 39, "estimate": 11756058, "name": "Ohio"},
            {"id": 40, "estimate": 4019800, "name": "Oklahoma"},
            {"id": 41, "estimate": 4240137, "name": "Oregon"},
            {"id": 42, "estimate": 12972008, "name": "Pennsylvania"},
            {"id": 44, "estimate": 1093734, "name": "Rhode Island"},
            {"id": 45, "estimate": 5282634, "name": "South Carolina"},
            {"id": 46, "estimate": 909824, "name": "South Dakota"},
            {"id": 47, "estimate": 7051339, "name": "Tennessee"},
            {"id": 48, "estimate": 30029572, "name": "Texas"},
            {"id": 49, "estimate": 3380800, "name": "Utah"},
            {"id": 50, "estimate": 647064, "name": "Vermont"},
            {"id": 51, "estimate": 8642274, "name": "Virginia"},
            {"id": 53, "estimate": 7785786, "name": "Washington"},
            {"id": 54, "estimate": 1775156, "name": "West Virginia"},
            {"id": 55, "estimate": 5892539, "name": "Wisconsin"},
            {"id": 56, "estimate": 576851, "name": "Wyoming"}
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
      "scale": {"scheme": "yelloworangered"},
      "legend": {"title": "Population", "format": ","}
    },
    "tooltip": [
      {"field": "name", "type": "nominal", "title": "State"},
      {"field": "estimate", "type": "quantitative", "title": "Population", "format": ","}
    ]
  }
}
```

!!! info "What is a TIGER/Line shapefile?"
    The Census Bureau publishes free geographic boundary files called
    TIGER/Line shapefiles. When you set `geometry=True`, PyPUMS automatically
    downloads the correct shapefile for your geography level and year, then
    joins it to your data on the `GEOID` column.

**What to try next:** [Spatial Data & Mapping guide](../guides/spatial.md) for dot-density maps, population-weighted interpolation, and custom resolutions.

---

## 3. PUMS microdata -- Age, sex, and wages for individuals

The Public Use Microdata Sample (PUMS) contains individual-level records, allowing custom tabulations that pre-made tables cannot provide. Fetch age, sex, and wage data for California.

```python
import pypums

ca_pums = pypums.get_pums(
    variables=["AGEP", "SEX", "WAGP"],  # (1)!
    state="CA",                          # (2)!
    year=2023,                           # (3)!
    survey="acs5",                       # (4)!
    recode=True,                         # (5)!
)

print(ca_pums.head())
```

1. **variables** -- PUMS variable names (all caps). `AGEP` = age, `SEX` = sex, `WAGP` = wage/salary income. These differ from ACS table variables like `B19013_001`.
2. **state** -- Required for PUMS queries. Accepts abbreviations, full names, or FIPS codes.
3. **year** -- The data year. Defaults to `2023`.
4. **survey** -- `"acs1"` (1-year) or `"acs5"` (5-year, default).
5. **recode** -- When `True`, PyPUMS adds `*_label` columns that translate numeric codes into human-readable values. For example, `SEX=1` gets `SEX_label="Male"`.

**Expected output:**

```
   SERIALNO  SPORDER  PWGTP  ST   PUMA  AGEP SEX    WAGP SEX_label
0  2022...        1     72  06  03701    35   1   45000      Male
1  2022...        2     55  06  03701    32   2   38000    Female
2  2022...        1     88  06  03702    28   1   52000      Male
3  2022...        1     63  06  03702    41   2   67000    Female
4  2022...        2     45  06  03702    19   1    8500      Male
```

| Column       | Description                                                  |
|--------------|--------------------------------------------------------------|
| `SERIALNO`   | Unique housing unit serial number                            |
| `SPORDER`    | Person number within the household                           |
| `PWGTP`      | Person weight -- use this when computing population totals   |
| `ST`         | State FIPS code                                              |
| `PUMA`       | Public Use Microdata Area code                               |
| `AGEP`       | Age in years                                                 |
| `SEX`        | Sex code (1 = Male, 2 = Female)                              |
| `WAGP`       | Wage or salary income in dollars                             |
| `SEX_label`  | Human-readable label (added by `recode=True`)                |

!!! warning "Always use weights"
    PUMS records are a sample, not a full count. To estimate population totals
    or averages, you must use the `PWGTP` (person weight) column:

    ```python
    import numpy as np

    # Weighted mean wage for California
    weighted_mean = np.average(
        ca_pums["WAGP"].dropna(),
        weights=ca_pums.loc[ca_pums["WAGP"].notna(), "PWGTP"],
    )
    print(f"Weighted mean wage: ${weighted_mean:,.0f}")
    ```

**Server-side filtering** -- You can filter records before they are downloaded to speed up large queries:

```python
# Only employed people with wages over $0
employed = pypums.get_pums(
    variables=["AGEP", "SEX", "WAGP"],
    state="CA",
    survey="acs1",
    variables_filter={"WAGP": "1:999999"},  # wage range filter
)
```

**What to try next:** [PUMS Microdata guide](../guides/pums-microdata.md) for replicate weights, standard error calculation, multi-state queries, and housing-unit variables.

---

## Recap

| Task                       | Function          | Key parameters                          |
|----------------------------|-------------------|-----------------------------------------|
| Pre-tabulated statistics   | `get_acs()`       | `geography`, `variables` or `table`     |
| Individual-level microdata | `get_pums()`      | `variables`, `state`, `recode`          |
| Maps and spatial joins     | any + `geometry=True` | Requires `pypums[spatial]`         |

Not sure which dataset to use? Read [Census 101: Which Dataset?](census-101.md) next.
