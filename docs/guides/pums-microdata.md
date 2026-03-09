# Working with PUMS Microdata

Public Use Microdata Samples (PUMS) are individual-level Census records -- each row represents a single person or housing unit rather than a geographic summary. This makes PUMS the tool of choice when you need custom cross-tabulations that are not available in pre-built summary tables. PyPUMS provides `get_pums()` to pull PUMS microdata directly from the Census API.

## What is PUMS?

ACS summary tables (accessed via `get_acs()`) give you pre-aggregated statistics like median income or total population for a geographic area. PUMS gives you the underlying individual records with person- and household-level variables such as age, sex, income, education, and occupation. You can then build your own tabulations with any combination of variables.

Key characteristics:

- **Individual-level records**: each row is one person or one housing unit
- **Weighted data**: every record carries a weight (`PWGTP` for persons, `WGTP` for housing units) that must be applied for valid estimates
- **Largest geography is PUMA**: Public Use Microdata Areas have roughly 100,000 people each; you cannot get tract- or county-level PUMS data
- **Privacy protection**: records are anonymized with top-coding, swapping, and noise infusion

## Function signature

```python
pypums.get_pums(
    variables=None,
    *,
    state,
    puma=None,
    year=2023,
    survey="acs5",
    variables_filter=None,
    rep_weights=None,
    recode=False,
    show_call=False,
    cache_table=False,
    key=None,
)
```

!!! note "State is required"
    Unlike `get_acs()`, the `state` parameter is required for PUMS
    queries. The Census API serves PUMS data one state at a time.
    Pass a state abbreviation (`"CA"`), full name (`"California"`),
    or FIPS code (`"06"`).

!!! note "API key required"
    All Census API calls require a key. Request one for free at
    <https://api.census.gov/data/key_signup.html>, then set the
    `CENSUS_API_KEY` environment variable or pass `key="YOUR_KEY"` to
    every call.

---

## Base variables

Every PUMS query automatically includes these columns, regardless of
what you request in `variables`:

| Variable | Description |
|----------|-------------|
| `SERIALNO` | Unique household serial number |
| `SPORDER` | Person number within the household (1, 2, 3, ...) |
| `PWGTP` | Person weight (use for person-level tabulations) |
| `ST` | State FIPS code |
| `PUMA` | Public Use Microdata Area code |

These are always present in the returned DataFrame.

---

## Getting started

### Age and sex for a single state

```python
import pypums

ca_people = pypums.get_pums(
    variables=["AGEP", "SEX"],
    state="CA",
    year=2022,
    survey="acs5",
)
print(ca_people.head())
```

```
     SERIALNO  SPORDER  PWGTP  ST   PUMA  AGEP SEX
0  2022HU00001       1     45  06  03701    35   1
1  2022HU00001       2     50  06  03701    33   2
2  2022HU00002       1     22  06  03701    67   1
3  2022HU00003       1     88  06  03702    28   2
4  2022HU00003       2     88  06  03702    30   1
```

!!! tip "Always use weights"
    Raw row counts in PUMS are meaningless for population estimates.
    Always weight by `PWGTP` (for person-level analysis) or `WGTP`
    (for housing-unit analysis). For example, weighted total population
    is `ca_people["PWGTP"].sum()`, not `len(ca_people)`.

---

## Variable filtering

The `variables_filter` parameter applies server-side filters *before*
downloading, which reduces the amount of data transferred and speeds up
queries significantly.

### Filter to a single value

```python
# Only female respondents
females = pypums.get_pums(
    variables=["AGEP", "SEX", "SCHL"],
    state="CA",
    year=2022,
    variables_filter={"SEX": 2},
)
```

### Filter to multiple values

```python
# People with a Bachelor's, Master's, or Doctorate degree
grad_degrees = pypums.get_pums(
    variables=["AGEP", "SEX", "SCHL", "WAGP"],
    state="CA",
    year=2022,
    variables_filter={"SCHL": [21, 22, 24]},
)
```

!!! tip "Server-side vs. client-side filtering"
    `variables_filter` is applied on the Census API server before
    data is sent back. This is much faster than downloading the full
    state file and filtering locally, especially for large states like
    California or Texas.

### Multiple simultaneous filters

```python
# Employed males with a Bachelor's degree
employed_male_ba = pypums.get_pums(
    variables=["AGEP", "SEX", "SCHL", "ESR", "WAGP"],
    state="NY",
    year=2022,
    variables_filter={
        "SEX": 1,
        "SCHL": 21,
        "ESR": 1,
    },
)
```

---

## Recoding variables

PUMS variables use numeric codes. Set `recode=True` to add
human-readable `_label` columns alongside the coded values:

```python
people = pypums.get_pums(
    variables=["SEX", "MAR", "SCHL", "RAC1P"],
    state="WA",
    year=2022,
    recode=True,
)
print(people[["SEX", "SEX_label", "MAR", "MAR_label"]].head())
```

```
  SEX SEX_label MAR    MAR_label
0   1      Male   1      Married
1   2    Female   5  Never married
2   1      Male   3     Divorced
3   2    Female   1      Married
4   1      Male   5  Never married
```

### Available recodes

The following variables have built-in label mappings:

| Variable | Description | Example codes |
|----------|-------------|---------------|
| `SEX` | Sex | 1=Male, 2=Female |
| `MAR` | Marital status | 1=Married, 2=Widowed, 3=Divorced, 4=Separated, 5=Never married |
| `SCHL` | Educational attainment | 16=High school diploma, 21=Bachelor's, 22=Master's, 24=Doctorate |
| `RAC1P` | Race (detailed) | 1=White alone, 2=Black alone, 6=Asian alone, 9=Two or More |
| `HISP` | Hispanic origin | 01=Not Hispanic/Latino |
| `ESR` | Employment status | 1=Employed at work, 3=Unemployed, 6=Not in labor force |

!!! note "Partial recodes"
    The built-in recode maps cover the most common values. Codes not in
    the map will produce `NaN` in the label column. For complete code
    lists, consult the Census Bureau's PUMS data dictionary at
    <https://www.census.gov/programs-surveys/acs/microdata/documentation.html>.

---

## Replicate weights

PUMS data includes replicate weights for computing standard errors. The
`rep_weights` parameter controls which sets of replicate weight columns
are included.

=== "Person weights"

    ```python
    df = pypums.get_pums(
        variables=["AGEP", "WAGP"],
        state="CA",
        year=2022,
        rep_weights="person",
    )
    print([c for c in df.columns if c.startswith("PWGTP")])
    # ['PWGTP', 'PWGTP1', 'PWGTP2', ..., 'PWGTP80']
    ```

    Adds 80 person replicate weight columns (`PWGTP1` through
    `PWGTP80`) alongside the main weight `PWGTP`.

=== "Housing weights"

    ```python
    df = pypums.get_pums(
        variables=["VALP", "RNTP"],
        state="CA",
        year=2022,
        rep_weights="housing",
    )
    print([c for c in df.columns if c.startswith("WGTP")])
    # ['WGTP1', 'WGTP2', ..., 'WGTP80']
    ```

    Adds 80 housing replicate weight columns (`WGTP1` through `WGTP80`).

=== "Both"

    ```python
    df = pypums.get_pums(
        variables=["AGEP", "VALP"],
        state="CA",
        year=2022,
        rep_weights="both",
    )
    ```

    Adds all 160 replicate weight columns (80 person + 80 housing).

### Computing standard errors with replicate weights

The successive difference replication (SDR) formula used by the Census
Bureau:

```python
import numpy as np

df = pypums.get_pums(
    variables=["WAGP"],
    state="CA",
    year=2022,
    variables_filter={"WAGP": "0:"},  # positive wages only
    rep_weights="person",
)

# Weighted mean wages using the main weight
main_est = np.average(df["WAGP"], weights=df["PWGTP"])

# Replicate estimates
rep_ests = []
for i in range(1, 81):
    rep_est = np.average(df["WAGP"], weights=df[f"PWGTP{i}"])
    rep_ests.append(rep_est)

# Standard error via SDR
se = np.sqrt(4 / 80 * sum((r - main_est) ** 2 for r in rep_ests))
moe_90 = se * 1.645

print(f"Mean wages: ${main_est:,.0f}")
print(f"MOE (90%):  +/- ${moe_90:,.0f}")
```

---

## PUMA geography

PUMAs (Public Use Microdata Areas) are the smallest geography available
in PUMS data. Each PUMA contains roughly 100,000 people.

!!! warning "PUMAs are not the same as tracts or zip codes"
    PUMAs are large areas designed specifically for microdata privacy.
    A single PUMA may cover an entire rural county or a few
    neighborhoods within a dense city. They do not align neatly with
    counties, zip codes, or school districts.

### Filtering by PUMA

```python
# Downtown Los Angeles PUMA
dtla = pypums.get_pums(
    variables=["AGEP", "SEX", "WAGP"],
    state="CA",
    puma="03710",
    year=2022,
)
```

### Multiple PUMAs

```python
# Several PUMAs in the San Francisco area
sf_area = pypums.get_pums(
    variables=["AGEP", "SEX", "WAGP"],
    state="CA",
    puma=["07501", "07502", "07503"],
    year=2022,
)
```

---

## Multi-state queries

Pass a list of states to combine data from multiple states in a single
call:

```python
west_coast = pypums.get_pums(
    variables=["AGEP", "SEX", "SCHL", "WAGP"],
    state=["CA", "OR", "WA"],
    year=2022,
)
print(west_coast["ST"].value_counts())
```

```
06    391245
53     75012
41     42318
Name: ST, dtype: int64
```

PyPUMS makes separate API calls per state and concatenates the results
into a single DataFrame.

---

## Person vs. housing weights

PUMS records carry two types of weights. Using the correct one is
essential for valid estimates.

| Weight | Column | Use when... |
|--------|--------|-------------|
| Person weight | `PWGTP` | Tabulating person-level variables (age, sex, income, education, etc.) |
| Housing weight | `WGTP` | Tabulating housing-unit-level variables (rent, home value, number of rooms, etc.) |

!!! warning "Using the wrong weight"
    If you weight person variables by `WGTP` or housing variables by
    `PWGTP`, your estimates will be wrong. Person records for the same
    household share the same `SERIALNO` but may have different `PWGTP`
    values. Housing variables are typically on the first person record
    in each household (`SPORDER == 1`).

### Person-level example

```python
# Weighted count of people by educational attainment
import pandas as pd

edu = pypums.get_pums(
    variables=["SCHL"],
    state="MA",
    year=2022,
    recode=True,
)
weighted_counts = (
    edu.groupby("SCHL_label")["PWGTP"]
    .sum()
    .sort_values(ascending=False)
)
print(weighted_counts.head())
```

### Housing-level example

For housing variables, include `WGTP` in the variables list and filter
to one record per household:

```python
housing = pypums.get_pums(
    variables=["VALP", "RNTP", "WGTP"],
    state="MA",
    year=2022,
)
# Keep one record per household
hh = housing[housing["SPORDER"] == 1]
weighted_median_rent = hh.loc[hh["RNTP"] > 0, "RNTP"].median()
```

---

## Debugging API calls

Set `show_call=True` to print the exact Census API URL and parameters
before the request is made:

```python
df = pypums.get_pums(
    variables=["AGEP", "SEX"],
    state="CA",
    year=2022,
    show_call=True,
)
```

```
Census API call: https://api.census.gov/data/2022/acs/acs5/pums
  Parameters: {'get': 'SERIALNO,SPORDER,PWGTP,ST,PUMA,AGEP,SEX', 'for': 'state:06', 'key': '...'}
```

This is useful for debugging or reproducing queries outside PyPUMS.

---

## Caching

Cache PUMS responses on disk with `cache_table=True`:

```python
df = pypums.get_pums(
    variables=["AGEP", "SEX", "SCHL"],
    state="CA",
    year=2022,
    cache_table=True,
)
```

PUMS queries for large states can be slow due to the volume of
individual records. Caching avoids re-downloading during iterative
analysis.

---

## End-to-end example: earnings by education

This example demonstrates a complete weighted cross-tabulation workflow
-- computing median earnings by educational attainment level for
California.

```python
import numpy as np
import pandas as pd
import pypums

# 1. Pull microdata with recodes
pums = pypums.get_pums(
    variables=["AGEP", "SCHL", "WAGP", "ESR"],
    state="CA",
    year=2022,
    survey="acs5",
    recode=True,
    variables_filter={"ESR": [1, 2]},  # employed civilians only
    cache_table=True,
)

# 2. Filter to working-age adults with positive wages
workers = pums[(pums["AGEP"] >= 25) & (pums["AGEP"] <= 64) & (pums["WAGP"] > 0)]

# 3. Map education to broader categories
edu_map = {
    "Regular high school diploma": "High school",
    "Associate's degree": "Associate's",
    "Bachelor's degree": "Bachelor's",
    "Master's degree": "Master's",
    "Doctorate degree": "Doctorate",
}
workers = workers.copy()
workers["edu_group"] = workers["SCHL_label"].map(edu_map)
workers = workers.dropna(subset=["edu_group"])

# 4. Compute weighted median earnings by education group
def weighted_median(values, weights):
    """Compute a weighted median."""
    sorted_idx = np.argsort(values)
    sorted_vals = values.iloc[sorted_idx].values
    sorted_wts = weights.iloc[sorted_idx].values
    cumwt = np.cumsum(sorted_wts)
    cutoff = sorted_wts.sum() / 2.0
    return sorted_vals[cumwt >= cutoff][0]

results = []
for group, gdf in workers.groupby("edu_group"):
    med_wage = weighted_median(gdf["WAGP"], gdf["PWGTP"])
    total = gdf["PWGTP"].sum()
    results.append({
        "education": group,
        "median_earnings": med_wage,
        "weighted_n": total,
    })

summary = pd.DataFrame(results).sort_values("median_earnings", ascending=False)
print(summary.to_string(index=False))
```

```
   education  median_earnings  weighted_n
   Doctorate            95000      234500
    Master's            78000      891200
  Bachelor's            62000     2456000
 Associate's            42000      789000
 High school            32000     1534000
```

!!! tip "For publication-quality standard errors"
    Use the `rep_weights="person"` parameter and the SDR formula
    (shown earlier) to compute standard errors for your custom
    estimates. This is the Census Bureau's recommended approach for
    PUMS-based tabulations.

---

## Troubleshooting

**"error: unknown/unsupported geography"**
:   PUMS data is only available at the state level. You cannot request county
    or tract-level PUMS data — that is what `get_acs()` is for.

**Empty DataFrame returned**
:   Check that the `state` you passed is valid. PUMS requires a state;
    national-level queries are not supported by the Census API.

**`variables_filter` not reducing rows**
:   Filters apply server-side but only to the variables you specify. If a
    variable name is misspelled, the API silently ignores it. Use
    `pums_variables()` to confirm the exact variable codes.

**"PWGTP" or weight columns missing**
:   The base weight `PWGTP` (person) or `WGTP` (housing) is always included
    automatically. If you need replicate weights (`PWGTP1`–`PWGTP80`), pass
    `rep_weights="person"` (or `"housing"`).

**Large result sets timing out**
:   PUMS queries that request many variables for large states can be slow.
    Reduce the number of variables, or cache results with `cache_table=True`.

---

## See Also

- [Survey Design & Weights](survey-design.md) — Using replicate weights and the `SurveyDesign` class for standard errors
- [API Reference](../reference/api.md) — Full `get_pums()` function signature
- [Finding Variables](variables.md) — Browsing PUMS variable codes with `pums_variables()`
- [Coming from Census FTP](../migration/from-census-ftp.md) — Migration guide for users switching from direct FTP downloads
