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

Now plot it:

```python
la_poverty.plot(
    column="estimate",
    cmap="YlOrRd",
    legend=True,
    figsize=(12, 10),
    edgecolor="0.8",
    linewidth=0.3,
    missing_kwds={"color": "lightgrey"},
)
```

The resulting map shows poverty counts by Census tract across Los Angeles County, with darker shades indicating higher counts.

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
