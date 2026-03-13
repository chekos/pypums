# Working with ACS Data

The American Community Survey (ACS) is the most widely used Census Bureau product, providing detailed demographic, economic, housing, and social characteristics for every community in the United States. PyPUMS makes it straightforward to pull ACS summary tables directly from the Census API into pandas DataFrames.

## Function signature

```python
pypums.get_acs(
    geography,
    variables=None,
    table=None,
    state=None,
    county=None,
    year=2023,
    survey="acs5",
    output="tidy",
    moe_level=90,
    summary_var=None,
    geometry=False,
    keep_geo_vars=False,
    cache_table=False,
    key=None,
)
```

!!! note "API key required"
    All Census API calls require a key. Request one for free at
    <https://api.census.gov/data/key_signup.html>, then set the
    `CENSUS_API_KEY` environment variable or pass `key="YOUR_KEY"` to
    every call.

---

## Getting started

### Single variable

Retrieve total population (variable `B01003_001`) for every state:

```python
import pypums

pop = pypums.get_acs(
    geography="state",
    variables=["B01003_001"],
    year=2022,
)
print(pop.head())
```

```
       GEOID                 NAME     variable  estimate      moe
0         01              Alabama  B01003_001   5074296      NaN
1         02               Alaska  B01003_001    733583      NaN
2         04              Arizona  B01003_001   7359197      NaN
3         05             Arkansas  B01003_001   3045637      NaN
4         06           California  B01003_001  39029342      NaN
```

!!! info "Why is `moe` showing `NaN`?"
    Some ACS variables — particularly total-population counts derived from the
    Decennial Census base — do not have a margin of error. When the Census API
    returns no MOE for a variable, PyPUMS fills the column with `NaN`. This is
    expected, not a bug. Most other variables (income, housing, etc.) will
    return numeric MOE values.

!!! tip "Variable naming convention"
    ACS variable IDs follow the pattern `TABLE_SEQUENCE`. For example,
    `B19013_001` is sequence 001 (the estimate) from table B19013
    (Median Household Income). You do **not** need to add the `E` or `M`
    suffix -- PyPUMS appends those automatically.

### Multiple variables

Pass a list to request several variables at once. Here we pull median
household income (`B19013_001`) and median home value (`B25077_001`) for
all counties in California:

```python
income_housing = pypums.get_acs(
    geography="county",
    variables=["B19013_001", "B25077_001"],
    state="CA",
    year=2022,
)
print(income_housing.head(6))
```

```
       GEOID                          NAME     variable  estimate      moe
0      06001      Alameda County, California  B19013_001    122488     1729
1      06001      Alameda County, California  B25077_001    958200    11988
2      06003       Alpine County, California  B19013_001     62750    20225
3      06003       Alpine County, California  B25077_001    394500    76504
4      06005       Amador County, California  B19013_001     70634     5180
5      06005       Amador County, California  B25077_001    385800    13247
```

### Full table

Instead of listing individual variables, pass a table ID to pull the
entire table. Table `B01001` is Sex by Age:

```python
age_sex = pypums.get_acs(
    geography="state",
    table="B01001",
    state="CA",
    year=2022,
)
print(age_sex.shape)
```

```
(49, 5)
```

49 variables in B01001, one row per variable.

!!! warning "Large tables"
    Some tables have hundreds of variables. Pulling the full group
    fetches every estimate and margin of error column, which can be
    slow. Use `cache_table=True` to avoid redundant API calls during
    iterative work.

---

## Tidy vs. wide output

The `output` parameter controls the shape of the returned DataFrame.

=== "Tidy (default)"

    Each row is one geography-variable combination. This is ideal for
    plotting with [Altair](https://altair-viz.github.io/).

    ```python
    df_tidy = pypums.get_acs(
        geography="state",
        variables=["B19013_001", "B25077_001"],
        state="CA",
        year=2022,
        output="tidy",
    )
    ```

    | GEOID | NAME | variable | estimate | moe |
    |-------|------|----------|----------|-----|
    | 06001 | Alameda County, California | B19013_001 | 122488 | 1729 |
    | 06001 | Alameda County, California | B25077_001 | 958200 | 11988 |

    Columns: `GEOID`, `NAME`, `variable`, `estimate`, `moe`

=== "Wide"

    Each variable gets its own estimate and MOE columns. This is closer
    to a traditional spreadsheet layout.

    ```python
    df_wide = pypums.get_acs(
        geography="state",
        variables=["B19013_001", "B25077_001"],
        state="CA",
        year=2022,
        output="wide",
    )
    ```

    | GEOID | NAME | B19013_001E | B19013_001M | B25077_001E | B25077_001M |
    |-------|------|-------------|-------------|-------------|-------------|
    | 06001 | Alameda County, California | 122488 | 1729 | 958200 | 11988 |

    Columns: `GEOID`, `NAME`, then pairs of `<VAR>E` (estimate) and
    `<VAR>M` (margin of error) for each variable.

---

## Geography levels

PyPUMS supports all major Census geography levels. Some require a
parent geography (state or county) as context.

| Geography | `geography=` | Requires `state`? | Requires `county`? |
|-----------|-------------|:-----------------:|:------------------:|
| Nation | `"us"` | | |
| Region | `"region"` | | |
| Division | `"division"` | | |
| State | `"state"` | | |
| County | `"county"` | Yes | |
| County subdivision | `"county subdivision"` | Yes | Yes |
| Census tract | `"tract"` | Yes | Yes |
| Block group | `"block group"` | Yes | Yes |
| Place (city/town) | `"place"` | Yes | |
| ZCTA (zip code) | `"zcta"` | | |
| PUMA | `"puma"` | Yes | |
| CBSA (metro area) | `"cbsa"` | | |
| CSA | `"csa"` | | |
| Congressional district | `"congressional district"` | Yes | |

### Sub-state queries

**All counties in a state:**

```python
ca_counties = pypums.get_acs(
    geography="county",
    variables=["B01003_001"],
    state="CA",
    year=2022,
)
print(f"{len(ca_counties)} counties")
print(ca_counties.head(3))
```

```
58 counties
     GEOID                          NAME    variable  estimate    moe
0  06001      Alameda County, California  B01003_001   1682353    NaN
1  06003       Alpine County, California  B01003_001      1204    NaN
2  06005       Amador County, California  B01003_001     40474    NaN
```

**All tracts in a single county:**

```python
la_tracts = pypums.get_acs(
    geography="tract",
    variables=["B01003_001"],
    state="CA",
    county="037",
    year=2022,
)
print(f"{len(la_tracts)} tracts in LA County")
```

```
2495 tracts in LA County
```

!!! tip "County FIPS codes"
    County FIPS codes are three-digit strings. Los Angeles County is
    `"037"`, Cook County (IL) is `"031"`, Harris County (TX) is `"201"`.
    You can look up codes at
    <https://www.census.gov/library/reference/code-lists/ansi.html>.

**All block groups in a county:**

```python
cook_bgs = pypums.get_acs(
    geography="block group",
    variables=["B19013_001"],
    state="IL",
    county="031",
    year=2022,
)
print(f"{len(cook_bgs)} block groups in Cook County")
```

```
4010 block groups in Cook County
```

**All places in a state:**

```python
tx_places = pypums.get_acs(
    geography="place",
    variables=["B01003_001"],
    state="TX",
    year=2022,
)
print(f"{len(tx_places)} places in Texas")
print(tx_places.head(3))
```

```
1834 places in Texas
     GEOID                    NAME    variable  estimate     moe
0  4800100  Abernathy city, Texas  B01003_001      2846   229.0
1  4800484     Addison town, Texas  B01003_001     16661  1031.0
2  4800820      Adrian city, Texas  B01003_001       148    56.0
```

---

## ACS 1-Year vs. 5-Year

The `survey` parameter selects between the 1-year and 5-year ACS.

=== "5-Year (default)"

    ```python
    df = pypums.get_acs(
        geography="tract",
        variables=["B19013_001"],
        state="CA",
        county="037",
        year=2022,
        survey="acs5",   # default
    )
    ```

    - Covers **all** geographies, including tracts and block groups
    - 5-year pooled sample provides smaller margins of error
    - Best for small-area analysis

=== "1-Year"

    ```python
    df = pypums.get_acs(
        geography="county",
        variables=["B19013_001"],
        state="CA",
        year=2022,
        survey="acs1",
    )
    ```

    - Only areas with population **65,000+**
    - Most current single-year snapshot
    - Best for year-over-year trend analysis of large areas

!!! warning "1-Year geography restrictions"
    The ACS 1-year survey does not publish data for tracts, block
    groups, or places with fewer than 65,000 people. Use `survey="acs5"`
    for small-area geographies.

---

## Margin of error confidence levels

ACS estimates come with margins of error (MOE) at the 90% confidence
level by default. You can rescale them to 95% or 99%:

```python
# Default: 90% confidence
df_90 = pypums.get_acs(
    geography="state",
    variables=["B19013_001"],
    year=2022,
    moe_level=90,
)

# 95% confidence -- wider MOE
df_95 = pypums.get_acs(
    geography="state",
    variables=["B19013_001"],
    year=2022,
    moe_level=95,
)

# Compare California's MOE at different confidence levels
ca_90 = df_90[df_90["GEOID"] == "06"]["moe"].values[0]
ca_95 = df_95[df_95["GEOID"] == "06"]["moe"].values[0]
print(f"CA median income MOE at 90%: ±{ca_90:,.0f}")
print(f"CA median income MOE at 95%: ±{ca_95:,.0f}")
```

```
CA median income MOE at 90%: ±482
CA median income MOE at 95%: ±575
```

The rescaling uses the standard z-score formula:

| Level | Z-score | Scale factor (from 90%) |
|-------|---------|------------------------|
| 90% | 1.645 | 1.000 |
| 95% | 1.960 | 1.192 |
| 99% | 2.576 | 1.566 |

!!! note "When to change the confidence level"
    Most Census Bureau publications use the default 90% MOE. Switch to
    95% or 99% when your analysis demands a higher confidence threshold,
    for instance when the result will inform policy decisions or
    statistical tests.

---

## Summary variables

The `summary_var` parameter adds a denominator column alongside each
row in tidy output, making it easy to compute proportions:

```python
# Sex by Age, with total population as the summary variable
age_with_total = pypums.get_acs(
    geography="county",
    table="B01001",
    state="CA",
    year=2022,
    summary_var="B01003_001",
)
print(age_with_total.columns.tolist())
```

```
['GEOID', 'NAME', 'variable', 'estimate', 'moe', 'summary_est', 'summary_moe']
```

The `summary_est` and `summary_moe` columns carry the denominator value for every row. You can then compute a share column directly:

```python
age_with_total["share"] = (
    age_with_total["estimate"] / age_with_total["summary_est"]
)
```

---

## Geometry support

Set `geometry=True` to return a GeoDataFrame with cartographic boundary
shapes joined to your data (downloaded via pygris, cached locally).

```python
ca_counties_geo = pypums.get_acs(
    geography="county",
    variables=["B01003_001"],
    state="CA",
    year=2022,
    geometry=True,
)
print(type(ca_counties_geo))
print(ca_counties_geo.head(3))
```

```
<class 'geopandas.geodataframe.GeoDataFrame'>
     GEOID                          NAME    variable  estimate  moe                                           geometry
0  06001      Alameda County, California  B01003_001   1682353  NaN  POLYGON ((-122.34230 37.76530, -122.33915 37....
1  06003       Alpine County, California  B01003_001      1204  NaN  POLYGON ((-120.07210 38.50980, -120.07112 38....
2  06005       Amador County, California  B01003_001     40474  NaN  POLYGON ((-121.02730 38.30210, -121.02516 38....
```

```python
import altair as alt

alt.Chart(ca_counties_geo).mark_geoshape(stroke="white", strokeWidth=0.5).encode(
    color=alt.Color("estimate:Q", legend=alt.Legend(title="Population")),
    tooltip=["NAME:N", alt.Tooltip("estimate:Q", format=",")],
).project("albersUsa").properties(width=500, height=400)
```

!!! note "Optional dependency"
    `geometry=True` requires `geopandas`. Install it with
    `uv add "pypums[spatial]"`.

---

## Preserving raw FIPS columns

By default, PyPUMS collapses the individual FIPS components (state,
county, tract, etc.) into a single `GEOID` column and drops the raw
parts. Set `keep_geo_vars=True` to retain them:

```python
tracts = pypums.get_acs(
    geography="tract",
    variables=["B01003_001"],
    state="CA",
    county="037",
    year=2022,
    keep_geo_vars=True,
)
print(tracts.columns.tolist())
```

```
['GEOID', 'NAME', 'state', 'county', 'tract', 'variable', 'estimate', 'moe']
```

This is useful when you need to join against other data sources that
store FIPS codes in separate columns.

---

## Caching

Set `cache_table=True` to cache the API response on disk for 24 hours:

```python
df = pypums.get_acs(
    geography="tract",
    variables=["B19013_001"],
    state="CA",
    county="037",
    year=2022,
    cache_table=True,
)
```

The cache is stored under `~/.pypums/cache/api/`. Subsequent calls with
the same parameters return instantly from disk instead of hitting the
Census API.

!!! tip "When to cache"
    Enable caching when you are iterating on analysis code and making
    the same API call repeatedly. Disable it (the default) for
    one-off pulls or production pipelines where you always want fresh
    data.

---

## Common patterns

### Median household income for all states

```python
income = pypums.get_acs(
    geography="state",
    variables=["B19013_001"],
    year=2022,
)
top_10 = income.nlargest(10, "estimate")
print(top_10[["NAME", "estimate", "moe"]])
```

```
                         NAME  estimate    moe
   District of Columbia         101027    NaN
                Maryland          90203    NaN
         New Jersey              89703    NaN
        Massachusetts            89026    NaN
             Hawaii              88005    NaN
          Washington             84247    NaN
        California               84097    NaN
         Connecticut             83771    NaN
        New Hampshire            83449    NaN
          Colorado               82254    NaN
```

### Poverty rate by county

Table B17001 contains poverty status counts. Variable `B17001_002` is
the count below the poverty level, and `B17001_001` is the universe
(total for whom poverty status is determined):

```python
poverty = pypums.get_acs(
    geography="county",
    variables=["B17001_002"],
    state="NY",
    year=2022,
    summary_var="B17001_001",
)
poverty["poverty_rate"] = poverty["estimate"] / poverty["summary_est"]
poverty_sorted = poverty.sort_values("poverty_rate", ascending=False)
print(poverty_sorted.head(5)[["NAME", "estimate", "summary_est", "poverty_rate"]])
```

```
                              NAME  estimate  summary_est  poverty_rate
    Bronx County, New York          359876      1418207        0.2537
    Kings County, New York          495322      2559903        0.1935
    New York County, New York       256108      1629153        0.1572
    Monroe County, New York         102814       721193        0.1426
    Erie County, New York           120853       903638        0.1337
```

### Race/ethnicity composition for a metro area

```python
race = pypums.get_acs(
    geography="cbsa",
    variables=[
        "B03002_003",  # White alone, not Hispanic
        "B03002_004",  # Black alone
        "B03002_006",  # Asian alone
        "B03002_012",  # Hispanic or Latino
    ],
    year=2022,
)
print(race.head(8))
```

```
     GEOID                               NAME    variable  estimate      moe
0  10180  Abilene, TX Metro Area          B03002_003    118252      NaN
1  10180  Abilene, TX Metro Area          B03002_004     11368      NaN
2  10180  Abilene, TX Metro Area          B03002_006      2985      NaN
3  10180  Abilene, TX Metro Area          B03002_012     37620      NaN
4  10420  Akron, OH Metro Area            B03002_003    536478      NaN
5  10420  Akron, OH Metro Area            B03002_004     89742      NaN
6  10420  Akron, OH Metro Area            B03002_006     14532      NaN
7  10420  Akron, OH Metro Area            B03002_012     10853      NaN
```

### Educational attainment for tracts with geometry

```python
education = pypums.get_acs(
    geography="tract",
    variables=[
        "B15003_022",  # Bachelor's degree
        "B15003_023",  # Master's degree
        "B15003_025",  # Doctorate degree
    ],
    state="MA",
    county="025",   # Suffolk County (Boston)
    year=2022,
    summary_var="B15003_001",
    geometry=True,
)
education["pct_bachelors_plus"] = (
    education["estimate"] / education["summary_est"]
)
print(education[["NAME", "variable", "estimate", "summary_est", "pct_bachelors_plus"]].head(3))
```

```
                                  NAME    variable  estimate  summary_est  pct_bachelors_plus
0  Census Tract 101, Suffolk County...  B15003_022      1285         3410              0.3768
1  Census Tract 101, Suffolk County...  B15003_023       842         3410              0.2469
2  Census Tract 101, Suffolk County...  B15003_025       215         3410              0.0631
```

### Year-over-year comparison

```python
import pandas as pd

years = [2019, 2021, 2022, 2023]
frames = []
for yr in years:
    df = pypums.get_acs(
        geography="state",
        variables=["B19013_001"],
        year=yr,
        survey="acs1",
        cache_table=True,
    )
    df["year"] = yr
    frames.append(df)

trend = pd.concat(frames, ignore_index=True)
print(trend[trend["GEOID"] == "06"][["NAME", "estimate", "year"]])
```

```
          NAME  estimate  year
  California   78672  2019
  California   84097  2021
  California   91905  2022
  California   95521  2023
```

!!! warning "2020 ACS 1-Year"
    The Census Bureau did not release a standard 2020 ACS 1-Year
    product due to low response rates during the COVID-19 pandemic.
    An experimental release was published separately. Use the 5-year
    ACS for 2020 small-area analysis.

### Combining MOE utilities with ACS data

After retrieving data, use PyPUMS MOE functions to compute derived
margins of error:

```python
from pypums import moe_sum, moe_prop, significance

# Sum two estimates and their MOEs
combined_moe = moe_sum([1500, 2300])  # MOEs from two variables

# Proportion MOE
prop_moe = moe_prop(
    num=5000,
    denom=25000,
    moe_num=800,
    moe_denom=1200,
)

# Test whether two estimates differ significantly
is_sig = significance(
    est1=55000,
    est2=62000,
    moe1=3200,
    moe2=2800,
    clevel=0.90,
)
print(f"Combined MOE: {combined_moe:.1f}")
print(f"Proportion MOE: {prop_moe:.4f}")
print(f"Statistically significant: {is_sig}")
```

```
Combined MOE: 2746.4
Proportion MOE: 0.0305
Statistically significant: True
```

---

## Discovering variables

Use `load_variables()` to search for variable codes in any ACS dataset:

```python
vars_2022 = pypums.load_variables(2022, "acs5", cache=True)
# Filter to a concept
income_vars = vars_2022[
    vars_2022["concept"].str.contains("MEDIAN HOUSEHOLD INCOME", na=False)
]
print(income_vars[["name", "label"]].head())
```

```
           name                                              label
0   B19013_001      Estimate!!Median household income in the ...
1   B19013A_001     Estimate!!Median household income in the ...
2   B19013B_001     Estimate!!Median household income in the ...
3   B19013C_001     Estimate!!Median household income in the ...
4   B19013D_001     Estimate!!Median household income in the ...
```

See the [Finding Variables](variables.md) guide for full details.

---

## Troubleshooting

**`ValueError: No Census API key found`**

:   You need to set the `CENSUS_API_KEY` environment variable or call
    `census_api_key()` before making any API requests. Request a free key at
    <https://api.census.gov/data/key_signup.html>.

**`ValueError: Geography 'tract' requires a state`**

:   Sub-state geographies (tract, block group, place, county, etc.) need the
    `state` parameter. Pass a state abbreviation, full name, or FIPS code.

**`ValueError: Must provide either 'variables' or 'table'`**

:   You must pass one of the two parameters. Use `variables` for specific
    variable codes or `table` for an entire table group.

**Empty DataFrame returned**

:   The variable code may be wrong for the requested year or survey. Use
    `load_variables()` to check which variables are available for a given
    year and dataset.

**`ImportError: geopandas`**

:   Geometry support requires the spatial extras. Install them with
    `uv add "pypums[spatial]"`.

**`moe_level must be one of [90, 95, 99]`**

:   Only these three confidence levels are supported for margin-of-error
    rescaling. Pass `moe_level=90`, `moe_level=95`, or `moe_level=99`.

---

## See Also

- [API Reference](../reference/api.md) — Full function signature for `get_acs()` and related functions
- [Finding Variables](variables.md) — Discovering variable codes with `load_variables()`
- [Geography & FIPS](geography.md) — Understanding geography levels and FIPS code lookups
- [Margins of Error](margins-of-error.md) — MOE propagation formulas and statistical testing
- [Spatial Data](spatial.md) — Attaching geometry to query results
