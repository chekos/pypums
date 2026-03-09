# Working with Decennial Census Data

The Decennial Census is a complete count of the United States population conducted every ten years. Unlike the ACS, decennial data has no margins of error because it aims to enumerate every person rather than sample a subset. PyPUMS provides `get_decennial()` to pull decennial summary tables from the Census API.

## Function signature

```python
pypums.get_decennial(
    geography,
    variables=None,
    table=None,
    state=None,
    county=None,
    year=2020,
    output="tidy",
    pop_group=None,
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

## Default datasets by year

PyPUMS automatically selects the correct dataset for each census year:

| Year | Default dataset | Description |
|------|----------------|-------------|
| 2020 | `dec/dhc` | Demographic and Housing Characteristics |
| 2010 | `dec/sf1` | Summary File 1 |
| 2000 | `dec/sf1` | Summary File 1 |

When you use the `pop_group` parameter, the dataset switches to
`dec/dhc-a` (Demographic and Housing Characteristics -- A), which
provides disaggregated race and ethnicity data.

---

## Getting started

### Total population by state

Variable `P1_001N` is total population in the 2020 DHC file:

```python
import pypums

pop = pypums.get_decennial(
    geography="state",
    variables=["P1_001N"],
    year=2020,
)
print(pop.head())
```

```
       GEOID                 NAME  variable      value
0         01              Alabama  P1_001N    5024279
1         02               Alaska  P1_001N     733391
2         04              Arizona  P1_001N    7151502
3         05             Arkansas  P1_001N    3011524
4         06           California  P1_001N   39538223
```

!!! tip "Variable naming convention"
    Decennial 2020 DHC variables use a different naming pattern than
    the ACS. Population variables start with `P` (e.g., `P1_001N`),
    housing variables with `H` (e.g., `H1_001N`). The suffix `N` means
    the numeric value. There are no separate estimate/MOE pairs because
    decennial data is a complete count.

### Multiple variables

Pull both total population and housing units:

```python
pop_housing = pypums.get_decennial(
    geography="county",
    variables=["P1_001N", "H1_001N"],
    state="TX",
    year=2020,
)
print(pop_housing.head(4))
```

```
       GEOID                            NAME  variable      value
0      48001   Anderson County, Texas         P1_001N      57922
1      48001   Anderson County, Texas         H1_001N      23456
2      48003   Andrews County, Texas          P1_001N      18610
3      48003   Andrews County, Texas          H1_001N       7214
```

### Full table

Pass a table ID to pull all variables in a group:

```python
race_table = pypums.get_decennial(
    geography="state",
    table="P1",
    state="CA",
    year=2020,
)
print(race_table.shape)
```

---

## Tidy vs. wide output

=== "Tidy (default)"

    Each row is one geography-variable combination. The value column is
    named `value` (not `estimate`, since decennial data has no MOE).

    ```python
    df_tidy = pypums.get_decennial(
        geography="county",
        variables=["P1_001N", "H1_001N"],
        state="NY",
        year=2020,
        output="tidy",
    )
    ```

    | GEOID | NAME | variable | value |
    |-------|------|----------|-------|
    | 36001 | Albany County, New York | P1_001N | 314848 |
    | 36001 | Albany County, New York | H1_001N | 140465 |

    Columns: `GEOID`, `NAME`, `variable`, `value`

=== "Wide"

    Each variable gets its own column.

    ```python
    df_wide = pypums.get_decennial(
        geography="county",
        variables=["P1_001N", "H1_001N"],
        state="NY",
        year=2020,
        output="wide",
    )
    ```

    | GEOID | NAME | P1_001N | H1_001N |
    |-------|------|---------|---------|
    | 36001 | Albany County, New York | 314848 | 140465 |

    Columns: `GEOID`, `NAME`, then one column per variable.

---

## Population groups (DHC-A)

The 2020 Census introduced the DHC-A file, which provides population
counts disaggregated by detailed race and ethnicity categories. Use the
`pop_group` parameter to access this data.

### Discovering population groups

Use `get_pop_groups()` to see available codes:

```python
groups = pypums.get_pop_groups(year=2020)
print(groups.head(10))
```

```
   code                            label
0     1               Total population
1     2  Hispanic or Latino
2     3  Not Hispanic or Latino
3     4  White alone
4     5  Black or African American alone
...
```

You can also filter by state:

```python
ca_groups = pypums.get_pop_groups(year=2020, state="06")
```

### Querying with a population group

```python
# Total population for the Hispanic or Latino group, by state
hispanic_pop = pypums.get_decennial(
    geography="state",
    variables=["P1_001N"],
    year=2020,
    pop_group="2",
)
print(hispanic_pop.head())
```

!!! warning "DHC-A availability"
    The `pop_group` parameter is only available for the 2020 Census.
    Earlier census years (2010, 2000) use different data structures and
    do not support population group queries through this parameter.

---

## Geometry support

Set `geometry=True` to return a GeoDataFrame with TIGER/Line shapes:

```python
county_geo = pypums.get_decennial(
    geography="county",
    variables=["P1_001N"],
    state="IL",
    year=2020,
    geometry=True,
)
county_geo.plot(column="value", legend=True)
```

!!! note "Optional dependency"
    `geometry=True` requires `geopandas`. Install with
    `uv add "pypums[spatial]"`.

---

## Preserving raw FIPS columns

Set `keep_geo_vars=True` to retain the individual FIPS columns
alongside the composite `GEOID`:

```python
tracts = pypums.get_decennial(
    geography="tract",
    variables=["P1_001N"],
    state="CA",
    county="037",
    year=2020,
    keep_geo_vars=True,
)
print(tracts.columns.tolist())
# ['GEOID', 'NAME', 'state', 'county', 'tract', 'variable', 'value']
```

---

## Caching

Cache API responses to disk for 24 hours with `cache_table=True`:

```python
df = pypums.get_decennial(
    geography="tract",
    variables=["P1_001N"],
    state="CA",
    county="037",
    year=2020,
    cache_table=True,
)
```

---

## Discovering available datasets

Use `summary_files()` to list all available decennial census datasets
for a given year:

```python
files = pypums.summary_files(year=2020)
print(files)
```

```
     dataset_name                                    title  ...
0         dec/dhc  Demographic and Housing Characteristics  ...
1       dec/dhc-a  DHC-A (Disaggregated)                   ...
2          dec/pl  Redistricting Data (PL 94-171)          ...
...
```

This is useful for discovering what data products are available beyond
the default DHC file.

---

## Differences from ACS

Understanding when to use `get_decennial()` versus `get_acs()` is
critical for sound analysis.

| Feature | Decennial (`get_decennial`) | ACS (`get_acs`) |
|---------|---------------------------|-----------------|
| **Frequency** | Every 10 years | Annual (1-year or 5-year) |
| **Type** | Complete count | Sample-based survey |
| **Margins of error** | None (complete count) | Always present |
| **Output columns** | `variable`, `value` | `variable`, `estimate`, `moe` |
| **Variable names** | `P1_001N`, `H1_001N` | `B01001_001`, `B19013_001` |
| **Subject coverage** | Basic demographics and housing | Detailed socioeconomic topics |
| **Smallest geography** | Block | Block group (5-year) |

### When to use decennial data

- You need block-level counts (the smallest geography available)
- You want a complete count without sampling uncertainty
- You are doing redistricting or apportionment analysis
- You need a population baseline for a census year

### When to use ACS data

- You need recent data between decennial years
- You need socioeconomic detail (income, education, commuting, etc.)
- You need annual time series
- Your analysis requires tract-level data with rich subject detail

---

## Common patterns

### Race and ethnicity by county

```python
race = pypums.get_decennial(
    geography="county",
    variables=[
        "P1_003N",  # Population of one race: White alone
        "P1_004N",  # Black or African American alone
        "P1_005N",  # American Indian and Alaska Native alone
        "P1_006N",  # Asian alone
        "P1_007N",  # Native Hawaiian and Other Pacific Islander alone
        "P1_008N",  # Some Other Race alone
        "P1_009N",  # Population of two or more races
    ],
    state="CA",
    year=2020,
    output="wide",
)
```

### Occupied vs. vacant housing units

```python
housing = pypums.get_decennial(
    geography="county",
    variables=[
        "H1_001N",  # Total housing units
        "H1_002N",  # Occupied
        "H1_003N",  # Vacant
    ],
    state="FL",
    year=2020,
)
housing_wide = pypums.get_decennial(
    geography="county",
    variables=["H1_001N", "H1_002N", "H1_003N"],
    state="FL",
    year=2020,
    output="wide",
)
housing_wide["vacancy_rate"] = housing_wide["H1_003N"] / housing_wide["H1_001N"]
```

### Tract-level population map

```python
pop_map = pypums.get_decennial(
    geography="tract",
    variables=["P1_001N"],
    state="NY",
    county="061",   # New York County (Manhattan)
    year=2020,
    geometry=True,
)
pop_map.plot(column="value", legend=True, cmap="YlOrRd")
```

### Comparing 2010 and 2020

```python
pop_2010 = pypums.get_decennial(
    geography="state",
    variables=["P001001"],  # 2010 SF1 total population variable
    year=2010,
)

pop_2020 = pypums.get_decennial(
    geography="state",
    variables=["P1_001N"],
    year=2020,
)
```

!!! warning "Variable names differ across decades"
    The 2020 DHC uses variables like `P1_001N`. The 2010 SF1 uses
    `P001001`. The 2000 SF1 uses `P001001` as well, but the available
    tables differ. Always check `load_variables()` for the correct
    variable names for each year.

```python
# Look up 2010 variable names
vars_2010 = pypums.load_variables(2010, "sf1", cache=True)
pop_vars = vars_2010[vars_2010["label"].str.contains("Total", na=False)]
```

---

## Troubleshooting

**"error: unknown variable" for 2020 queries**
:   The 2020 Decennial uses the DHC dataset, not SF1. Variable names changed
    (e.g., `P1_001N` instead of `P001001`). Use
    `load_variables(2020, "dhc")` to find the correct codes.

**`pop_group` parameter has no effect**
:   Population groups are only available in the 2020 DHC-A detailed tables.
    They do not apply to the 2010 or 2000 SF1 datasets.

**Missing data for small geographies**
:   The Census Bureau suppresses block-level data for very small populations
    to protect privacy. Try a broader geography (block group or tract).

**"error: unsupported year"**
:   `get_decennial()` supports 2000, 2010, and 2020. Other years are not
    available through the Census API's decennial endpoint.

---

## See Also

- [API Reference](../reference/api.md) — Full `get_decennial()` function signature
- [Geography & FIPS](geography.md) — Understanding geography levels and FIPS code lookups
- [Spatial Data](spatial.md) — Attaching TIGER/Line geometry to query results
- [ACS Data](acs-data.md) — For when you need margins of error and more recent annual data
