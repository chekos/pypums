# Population Estimates

The Census Bureau's Population Estimates Program (PEP) produces annual estimates of the population for the nation, states, counties, and other geographies in the years between decennial censuses. PyPUMS provides `get_estimates()` to pull these estimates from the Census API, including breakdowns by age, sex, race, and Hispanic origin.

## Function signature

```python
pypums.get_estimates(
    geography,
    *,
    product=None,
    variables=None,
    breakdown=None,
    breakdown_labels=False,
    vintage=2023,
    year=None,
    state=None,
    county=None,
    time_series=False,
    output="tidy",
    geometry=False,
    cache_table=False,
    show_call=False,
    key=None,
)
```

!!! note "API key required"
    All Census API calls require a key. Request one for free at
    <https://api.census.gov/data/key_signup.html>, then set the
    `CENSUS_API_KEY` environment variable or pass `key="YOUR_KEY"` to
    every call.

---

## Products

The `product` parameter selects which estimates dataset to query.
If omitted, it defaults to `"population"`.

| Product | `product=` | Dataset | Description |
|---------|-----------|---------|-------------|
| Population | `"population"` | `pep/population` | Total population estimates |
| Components of Change | `"components"` | `pep/components` | Births, deaths, migration |
| Housing | `"housing"` | `pep/housing` | Housing unit estimates |
| Characteristics | `"characteristics"` | `pep/charagegroups` | Population by age, sex, race, Hispanic origin |

---

## Getting started

### State population estimates

```python
import pypums

state_pop = pypums.get_estimates(
    geography="state",
    product="population",
    vintage=2023,
)
print(state_pop.head())
```

```
       GEOID                 NAME     variable      value
0         01              Alabama  POP_2023    5108468
1         02               Alaska  POP_2023     733406
2         04              Arizona  POP_2023    7303398
3         05             Arkansas  POP_2023    3067732
4         06           California  POP_2023   38965193
```

### County population estimates

```python
tx_counties = pypums.get_estimates(
    geography="county",
    product="population",
    state="TX",
    vintage=2023,
)
print(tx_counties.head())
```

---

## Vintage vs. year

Population estimates use a **vintage** model. The `vintage` parameter
specifies which release of estimates to query, while the optional
`year` parameter filters to a specific data year within that vintage.

```python
# All data from the 2023 vintage (default)
df = pypums.get_estimates(
    geography="state",
    vintage=2023,
)

# Only the 2021 estimate from the 2023 vintage
df_2021 = pypums.get_estimates(
    geography="state",
    vintage=2023,
    year=2021,
)
```

!!! tip "What is a vintage?"
    A vintage is the reference year for an estimates release. The 2023
    vintage contains estimates for July 1 of each year from the last
    decennial census (April 2020) through July 2023. Later vintages may
    revise earlier estimates based on updated data.

---

## Breakdown dimensions

The `breakdown` parameter adds demographic dimensions to the query.
This is primarily used with `product="characteristics"`.

Available breakdown dimensions:

| Dimension | `breakdown=` | Values |
|-----------|-------------|--------|
| Age group | `"AGEGROUP"` | 0=All ages, 1=0-4, 2=5-13, 3=14-17, 4=18-24, 5=25-44, 6=45-64, 7=65+, ... |
| Sex | `"SEX"` | 0=Both, 1=Male, 2=Female |
| Race | `"RACE"` | 0=All, 1=White alone, 2=Black alone, 3=AIAN alone, 4=Asian alone, ... |
| Hispanic origin | `"HISP"` | 0=Both, 1=Non-Hispanic, 2=Hispanic |

### Single breakdown

```python
by_sex = pypums.get_estimates(
    geography="state",
    product="characteristics",
    breakdown="SEX",
    vintage=2023,
)
```

### Multiple breakdowns

Pass a list to cross-tabulate by multiple dimensions:

```python
by_age_sex = pypums.get_estimates(
    geography="state",
    product="characteristics",
    breakdown=["AGEGROUP", "SEX"],
    vintage=2023,
)
```

---

## Breakdown labels

Numeric breakdown codes are not always intuitive. Set
`breakdown_labels=True` to add human-readable label columns:

```python
labeled = pypums.get_estimates(
    geography="state",
    product="characteristics",
    breakdown=["AGEGROUP", "SEX"],
    breakdown_labels=True,
    vintage=2023,
)
print(labeled[["NAME", "AGEGROUP", "AGEGROUP_label", "SEX", "SEX_label"]].head())
```

```
                  NAME  AGEGROUP       AGEGROUP_label  SEX SEX_label
0              Alabama         0            All ages    0  Both sexes
1              Alabama         0            All ages    1       Male
2              Alabama         0            All ages    2     Female
3              Alabama         1    Age 0 to 4 years    0  Both sexes
4              Alabama         1    Age 0 to 4 years    1       Male
```

### Available label mappings

=== "AGEGROUP"

    | Code | Label |
    |------|-------|
    | 0 | All ages |
    | 1 | Age 0 to 4 years |
    | 2 | Age 5 to 13 years |
    | 3 | Age 14 to 17 years |
    | 4 | Age 18 to 24 years |
    | 5 | Age 25 to 44 years |
    | 6 | Age 45 to 64 years |
    | 7 | Age 65 years and over |
    | 8 | Age 85 years and over |
    | 9 | Age 0 to 17 years |
    | 10 | Age 18 to 64 years |
    | 11 | Age 18 years and over |
    | 12 | Age 65 years and over |
    | 13 | Under 18 years |
    | 14 | 5 to 13 years |
    | 15 | 14 to 17 years |
    | 16 | 18 to 64 years |
    | 17 | 16 years and over |
    | 18 | Under 5 years |
    | 29 | Age 0 to 14 years |
    | 30 | Age 15 to 44 years |
    | 31 | Age 16 years and over |

=== "SEX"

    | Code | Label |
    |------|-------|
    | 0 | Both sexes |
    | 1 | Male |
    | 2 | Female |

=== "RACE"

    | Code | Label |
    |------|-------|
    | 0 | All races |
    | 1 | White alone |
    | 2 | Black alone |
    | 3 | American Indian and Alaska Native alone |
    | 4 | Asian alone |
    | 5 | Native Hawaiian and Other Pacific Islander alone |
    | 6 | Two or more races |
    | 7 | White alone or in combination |
    | 8 | Black alone or in combination |
    | 9 | American Indian and Alaska Native alone or in combination |
    | 10 | Asian alone or in combination |
    | 11 | Native Hawaiian and Other Pacific Islander alone or in combination |

=== "HISP"

    | Code | Label |
    |------|-------|
    | 0 | Both Hispanic Origins |
    | 1 | Non-Hispanic |
    | 2 | Hispanic |

---

## Time series

Set `time_series=True` to retrieve estimates across multiple years
within a single vintage. This adds `DATE_CODE` and `DATE_DESC` columns
to the output.

```python
pop_trend = pypums.get_estimates(
    geography="state",
    product="population",
    vintage=2023,
    time_series=True,
)
print(pop_trend[["NAME", "DATE_CODE", "DATE_DESC"]].head(8))
```

```
                  NAME  DATE_CODE              DATE_DESC
0              Alabama          1  4/1/2020 Census population
1              Alabama          2  4/1/2020 estimates base
2              Alabama          3  7/1/2020 population estimate
3              Alabama          4  7/1/2021 population estimate
4              Alabama          5  7/1/2022 population estimate
5              Alabama          6  7/1/2023 population estimate
6               Alaska          1  4/1/2020 Census population
7               Alaska          2  4/1/2020 estimates base
```

!!! warning "Time series is only available for population estimates"
    Setting `time_series=True` with any product other than
    `"population"` will raise a `ValueError`. The Census API only
    supports the time-series endpoint for the `pep/population` dataset.

### Plotting a time series

```python
import pandas as pd

ts = pypums.get_estimates(
    geography="state",
    product="population",
    vintage=2023,
    time_series=True,
)

# Filter to July 1 estimates (DATE_CODE >= 3)
july_ests = ts[ts["DATE_CODE"] >= 3].copy()

# Extract year from DATE_DESC
july_ests["year"] = july_ests["DATE_DESC"].str.extract(r"(\d{4})")

# Pivot for a specific state
ca = july_ests[july_ests["NAME"] == "California"]
print(ca[["year", "value"]])
```

---

## Tidy vs. wide output

=== "Tidy (default)"

    ```python
    df_tidy = pypums.get_estimates(
        geography="county",
        product="population",
        state="CA",
        vintage=2023,
        output="tidy",
    )
    ```

    | GEOID | NAME | variable | value |
    |-------|------|----------|-------|
    | 06001 | Alameda County, California | POP_2023 | 1638215 |

    Columns: `GEOID`, `NAME`, `variable`, `value`, plus any breakdown
    columns.

=== "Wide"

    ```python
    df_wide = pypums.get_estimates(
        geography="county",
        product="population",
        state="CA",
        vintage=2023,
        output="wide",
    )
    ```

    | GEOID | NAME | POP_2023 |
    |-------|------|----------|
    | 06001 | Alameda County, California | 1638215 |

    Each variable gets its own column.

---

## Components of change

The `"components"` product provides the building blocks of population
change: births, deaths, domestic migration, and international migration.

```python
components = pypums.get_estimates(
    geography="state",
    product="components",
    vintage=2023,
)
print(components.head(10))
```

Common component variables include:

| Variable | Description |
|----------|-------------|
| `BIRTHS` | Number of births |
| `DEATHS` | Number of deaths |
| `NATURALCHG` | Natural change (births minus deaths) |
| `DOMESTICMIG` | Net domestic migration |
| `INTERNATIONALMIG` | Net international migration |
| `NETMIG` | Net migration (domestic + international) |

---

## Housing unit estimates

```python
housing = pypums.get_estimates(
    geography="county",
    product="housing",
    state="FL",
    vintage=2023,
)
```

---

## Geometry support

Set `geometry=True` to get a GeoDataFrame with TIGER/Line shapes:

```python
pop_geo = pypums.get_estimates(
    geography="county",
    product="population",
    state="WA",
    vintage=2023,
    geometry=True,
)
import altair as alt

alt.Chart(pop_geo).mark_geoshape(stroke="white", strokeWidth=0.5).encode(
    color=alt.Color("value:Q", scale=alt.Scale(scheme="blues"), legend=alt.Legend(title="Population")),
    tooltip=["NAME:N", alt.Tooltip("value:Q", format=",")],
).project("albersUsa").properties(width=500, height=400)
```

```vegalite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": 500,
  "height": 350,
  "title": "2023 Population Estimates by State (sample data)",
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
            {"id": 1, "value": 5108468, "name": "Alabama"},
            {"id": 2, "value": 733406, "name": "Alaska"},
            {"id": 4, "value": 7303398, "name": "Arizona"},
            {"id": 5, "value": 3067732, "name": "Arkansas"},
            {"id": 6, "value": 38965193, "name": "California"},
            {"id": 8, "value": 5877610, "name": "Colorado"},
            {"id": 9, "value": 3617176, "name": "Connecticut"},
            {"id": 10, "value": 1017551, "name": "Delaware"},
            {"id": 12, "value": 22610726, "name": "Florida"},
            {"id": 13, "value": 11029227, "name": "Georgia"},
            {"id": 15, "value": 1435138, "name": "Hawaii"},
            {"id": 16, "value": 1964726, "name": "Idaho"},
            {"id": 17, "value": 12549689, "name": "Illinois"},
            {"id": 18, "value": 6862199, "name": "Indiana"},
            {"id": 19, "value": 3207004, "name": "Iowa"},
            {"id": 20, "value": 2940546, "name": "Kansas"},
            {"id": 21, "value": 4526154, "name": "Kentucky"},
            {"id": 22, "value": 4573749, "name": "Louisiana"},
            {"id": 23, "value": 1395722, "name": "Maine"},
            {"id": 24, "value": 6180253, "name": "Maryland"},
            {"id": 25, "value": 7001399, "name": "Massachusetts"},
            {"id": 26, "value": 10037261, "name": "Michigan"},
            {"id": 27, "value": 5737915, "name": "Minnesota"},
            {"id": 28, "value": 2939690, "name": "Mississippi"},
            {"id": 29, "value": 6196156, "name": "Missouri"},
            {"id": 30, "value": 1132812, "name": "Montana"},
            {"id": 31, "value": 1978379, "name": "Nebraska"},
            {"id": 32, "value": 3194176, "name": "Nevada"},
            {"id": 33, "value": 1402054, "name": "New Hampshire"},
            {"id": 34, "value": 9290841, "name": "New Jersey"},
            {"id": 35, "value": 2114371, "name": "New Mexico"},
            {"id": 36, "value": 19571216, "name": "New York"},
            {"id": 37, "value": 10835491, "name": "North Carolina"},
            {"id": 38, "value": 783926, "name": "North Dakota"},
            {"id": 39, "value": 11785935, "name": "Ohio"},
            {"id": 40, "value": 4019800, "name": "Oklahoma"},
            {"id": 41, "value": 4233358, "name": "Oregon"},
            {"id": 42, "value": 12961683, "name": "Pennsylvania"},
            {"id": 44, "value": 1095962, "name": "Rhode Island"},
            {"id": 45, "value": 5373555, "name": "South Carolina"},
            {"id": 46, "value": 919318, "name": "South Dakota"},
            {"id": 47, "value": 7126489, "name": "Tennessee"},
            {"id": 48, "value": 30503301, "name": "Texas"},
            {"id": 49, "value": 3417734, "name": "Utah"},
            {"id": 50, "value": 647464, "name": "Vermont"},
            {"id": 51, "value": 8683619, "name": "Virginia"},
            {"id": 53, "value": 7812880, "name": "Washington"},
            {"id": 54, "value": 1770071, "name": "West Virginia"},
            {"id": 55, "value": 5910955, "name": "Wisconsin"},
            {"id": 56, "value": 584057, "name": "Wyoming"}
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

!!! note "Optional dependency"
    `geometry=True` requires `geopandas`. Install with
    `uv add "pypums[spatial]"`.

---

## Caching

Cache responses locally with `cache_table=True`:

```python
df = pypums.get_estimates(
    geography="state",
    product="population",
    vintage=2023,
    cache_table=True,
)
```

---

## Debugging API calls

Set `show_call=True` to see the exact Census API URL and parameters:

```python
df = pypums.get_estimates(
    geography="state",
    product="population",
    vintage=2023,
    show_call=True,
)
```

```
Census API call: https://api.census.gov/data/2023/pep/population
  Parameters: {'get': 'NAME', 'for': 'state:*', 'key': '...'}
```

---

## Common patterns

### Population change between two vintages

```python
pop_2022 = pypums.get_estimates(
    geography="state",
    product="population",
    vintage=2022,
)
pop_2023 = pypums.get_estimates(
    geography="state",
    product="population",
    vintage=2023,
)

merged = pop_2022.merge(
    pop_2023,
    on=["GEOID", "NAME"],
    suffixes=("_2022", "_2023"),
)
merged["change"] = merged["value_2023"] - merged["value_2022"]
merged["pct_change"] = merged["change"] / merged["value_2022"] * 100
```

### Population by age group for a state

```python
age_groups = pypums.get_estimates(
    geography="state",
    product="characteristics",
    breakdown=["AGEGROUP"],
    breakdown_labels=True,
    vintage=2023,
    state="CA",
)
# Filter to non-overlapping age groups
primary_ages = age_groups[age_groups["AGEGROUP"].isin([1, 2, 3, 4, 5, 6, 7])]
print(primary_ages[["NAME", "AGEGROUP_label", "value"]])
```

### County-level race breakdown

```python
race_data = pypums.get_estimates(
    geography="county",
    product="characteristics",
    breakdown=["RACE", "HISP"],
    breakdown_labels=True,
    state="TX",
    vintage=2023,
)
```

### Components of change for fast-growing states

```python
components = pypums.get_estimates(
    geography="state",
    product="components",
    vintage=2023,
    output="wide",
    cache_table=True,
)
fastest = components.nlargest(10, "NETMIG")
print(fastest[["NAME", "NATURALCHG", "DOMESTICMIG", "INTERNATIONALMIG"]])
```

### County population map

```python
county_map = pypums.get_estimates(
    geography="county",
    product="population",
    state="CO",
    vintage=2023,
    geometry=True,
)
import altair as alt

alt.Chart(county_map).mark_geoshape(stroke="white", strokeWidth=0.5).encode(
    color=alt.Color("value:Q", scale=alt.Scale(scheme="yellowgreenblue"), legend=alt.Legend(title="Population")),
    tooltip=["NAME:N", alt.Tooltip("value:Q", format=",")],
).project("albersUsa").properties(width=500, height=400)
```

---

## See Also

- [API Reference](../reference/api.md) — Full `get_estimates()` function signature
- [Multi-Year Analysis](multi-year.md) — Time series patterns and best practices for longitudinal work
- [Geography & FIPS](geography.md) — Understanding geography levels and FIPS code lookups
