# Multi-Year Analysis

Census data is released annually, making it a powerful source for tracking
trends over time. This guide covers patterns for pulling the same variables
across multiple years, common pitfalls with time-series comparisons, and
built-in features that simplify longitudinal work.

---

## Basic loop pattern

The simplest approach is to loop over a range of years and concatenate the
results:

```python
import pandas as pd
import pypums

years = range(2018, 2023)  # 2018 through 2022
frames = []

for year in years:
    df = pypums.get_acs(
        geography="state",
        variables="B01001_001",
        state="CA",
        year=year,
        survey="acs5",
    )
    df["year"] = year
    frames.append(df)

trend = pd.concat(frames, ignore_index=True)
print(trend[["year", "NAME", "variable", "estimate"]])
```

This produces a tidy DataFrame with one row per year, ready for plotting or
further analysis.

---

## Example: population trends 2018--2022

```python
import pandas as pd
import matplotlib.pyplot as plt
import pypums

states = ["CA", "TX", "FL", "NY"]
years = range(2018, 2023)
frames = []

for year in years:
    for st in states:  # get_acs() accepts one state at a time
        df = pypums.get_acs(
            geography="state",
            variables="B01001_001",
            state=st,
            year=year,
            survey="acs5",
            cache_table=True,  # cache to avoid re-fetching
        )
        df["year"] = year
        frames.append(df)

trend = pd.concat(frames, ignore_index=True)

# Plot.
fig, ax = plt.subplots(figsize=(10, 6))
for name, group in trend.groupby("NAME"):
    ax.plot(group["year"], group["estimate"], marker="o", label=name)
ax.set_xlabel("Year")
ax.set_ylabel("Population (ACS 5-year estimate)")
ax.set_title("Population Trends, 2018-2022")
ax.legend()
plt.tight_layout()
plt.show()
```

!!! tip "Cache results when pulling many years"
    Pass `cache_table=True` to avoid re-fetching data you have already
    downloaded. This is especially important when you are looping over many
    years or geographies, since the Census API has rate limits.

---

## Variable code stability

Most Census **B-table** variable codes (e.g., `B01001_001` for total
population) are stable from year to year. However, the Census Bureau
occasionally introduces new variables, retires old ones, or changes their
definitions.

**Best practice:** check `load_variables()` for each year you plan to use:

```python
import pypums

vars_2018 = pypums.load_variables(2018, "acs5", cache=True)
vars_2022 = pypums.load_variables(2022, "acs5", cache=True)

# Check if a specific variable exists in both years.
target = "B19013_001"  # Median household income
print(target in vars_2018["name"].values)  # True
print(target in vars_2022["name"].values)  # True

# Look for label changes.
label_2018 = vars_2018.loc[vars_2018["name"] == target, "label"].iloc[0]
label_2022 = vars_2022.loc[vars_2022["name"] == target, "label"].iloc[0]
print(f"2018: {label_2018}")
print(f"2022: {label_2022}")
```

!!! warning "Subject and profile tables change more often"
    S-table (Subject) and DP-table (Data Profile) variable codes are less
    stable across years than B-table codes. Always verify before building a
    time series with these tables.

---

## ACS 1-year vs. 5-year

The Census Bureau publishes two main ACS products. Choosing the right one is
critical for multi-year analysis.

| Product      | Population threshold | Geographies available           | Period covered  |
|--------------|----------------------|---------------------------------|-----------------|
| **ACS 1-year** (`acs1`) | 65,000+   | States, large counties, large cities | Single calendar year |
| **ACS 5-year** (`acs5`) | None      | All geographies down to block group  | Rolling 5-year period |

=== "ACS 1-year"

    ```python
    # Only available for geographies with 65,000+ population.
    df = pypums.get_acs(
        geography="state",
        variables="B01001_001",
        year=2022,
        survey="acs1",
    )
    ```

=== "ACS 5-year"

    ```python
    # Available for all geographies, including tracts.
    df = pypums.get_acs(
        geography="tract",
        variables="B01001_001",
        state="CA",
        county="037",
        year=2022,
        survey="acs5",
    )
    ```

### Year interpretation for ACS 5-year

An ACS 5-year dataset labeled "2022" actually covers the **2018--2022** period.
The estimate represents an average over those five years, not a snapshot of
2022 alone.

| Dataset label | Period covered |
|---------------|----------------|
| 2022          | 2018--2022     |
| 2021          | 2017--2021     |
| 2020          | 2016--2020     |
| 2019          | 2015--2019     |
| 2018          | 2014--2018     |

!!! danger "Do not compare overlapping 5-year periods"
    ACS 5-year estimates from consecutive years share most of their underlying
    data. For example, 2017--2021 and 2018--2022 share four years of data.
    Comparing them as if they were independent violates statistical assumptions
    and can produce misleading trend lines.

    **Safe comparisons for 5-year data:**

    - 2013--2017 vs. 2018--2022 (non-overlapping)
    - Any two periods that share **zero** years

    If you need annual trends, use the **ACS 1-year** product instead (at the
    cost of geographic granularity).

---

## Geography boundary changes

Census geography boundaries are not fixed. The most important boundary change
happens with each decennial census, when **tract** and **block group**
boundaries are redrawn.

| Vintage   | Tract/BG boundaries | Notes                          |
|-----------|---------------------|--------------------------------|
| 2010--2019 | 2010 Census tracts | Based on 2010 TIGER/Line      |
| 2020--present | 2020 Census tracts | Based on 2020 TIGER/Line   |

This means that a tract GEOID like `06037101110` in 2019 data refers to a
**different physical area** than the same GEOID in 2020 data (if it even
exists in both vintages).

### What to do about boundary changes

=== "Option 1: Only compare within the same vintage"

    The safest approach is to restrict your time series to years that use the
    same tract definitions:

    ```python
    # All use 2020-vintage tracts.
    for year in [2020, 2021, 2022]:
        df = pypums.get_acs(
            geography="tract",
            variables="B01001_001",
            state="CA",
            county="037",
            year=year,
        )
    ```

=== "Option 2: Use population-weighted interpolation"

    If you need to compare across vintages, use `interpolate_pw()` to transfer
    data from one set of boundaries to another:

    ```python
    from pypums.spatial import interpolate_pw

    # 2019 data on 2010-vintage tracts.
    old_tracts = pypums.get_acs(
        geography="tract",
        variables="B01001_001",
        state="CA",
        county="037",
        year=2019,
        geometry=True,
    )

    # 2020-vintage tract boundaries.
    new_tracts = pypums.get_acs(
        geography="tract",
        variables="B01001_001",
        state="CA",
        county="037",
        year=2022,
        geometry=True,
    )

    # Interpolate 2019 values onto 2020 boundaries.
    interpolated = interpolate_pw(
        old_tracts,
        new_tracts,
        value_col="estimate",
        weight_col="estimate",  # use population as weight
        extensive=True,
    )
    ```

=== "Option 3: Use county or state level"

    County and state boundaries rarely change. If your analysis does not
    require sub-county detail, comparing counties or states across decades is
    straightforward and avoids boundary issues entirely.

---

## Inflation adjustment

Census income and dollar-denominated variables are reported in **nominal
(current-year) dollars**. To compare dollar values across years, you must
adjust for inflation manually.

The Census Bureau does **not** adjust for inflation in its API responses.
A common approach is to use the Consumer Price Index (CPI) from the Bureau of
Labor Statistics:

```python
import pandas as pd
import pypums

# CPI-U annual averages (illustrative values -- use actual BLS data).
cpi = {
    2018: 251.1,
    2019: 255.7,
    2020: 258.8,
    2021: 270.9,
    2022: 292.7,
}
target_year = 2022

frames = []
for year in range(2018, 2023):
    df = pypums.get_acs(
        geography="state",
        variables="B19013_001",  # Median household income
        state="CA",
        year=year,
        survey="acs1",
        cache_table=True,
    )
    df["year"] = year
    # Adjust to target-year dollars.
    df["estimate_real"] = df["estimate"] * (cpi[target_year] / cpi[year])
    frames.append(df)

trend = pd.concat(frames, ignore_index=True)
print(trend[["year", "estimate", "estimate_real"]])
```

!!! note
    For ACS 5-year estimates, the Census Bureau recommends adjusting to the
    **final year** of the period using the CPI annual average for that year.
    For example, the 2018--2022 estimate should be adjusted to 2022 dollars.

---

## Population Estimates time series

The Population Estimates Program (PEP) has a built-in time-series mode that
returns data for all years within a vintage in a single API call:

```python
import pypums

df = pypums.get_estimates(
    geography="state",
    product="population",
    vintage=2023,
    state="CA",
    time_series=True,
)

# The result includes DATE_CODE and DATE_DESC columns.
print(df[["NAME", "DATE_CODE", "DATE_DESC", "value"]].head(10))
```

This is more efficient than looping over individual years and avoids the need
to concatenate DataFrames manually.

!!! info
    `time_series=True` is only supported for `product="population"`. For other
    PEP products, use the loop pattern shown at the top of this guide.

---

## Best practices summary

| Practice | Reason |
|----------|--------|
| Use `cache_table=True` in loops | Avoids re-fetching and respects API rate limits |
| Check `load_variables()` per year | Variable codes and labels can change |
| Use ACS 1-year for annual trends | Avoids overlapping-period bias |
| Use ACS 5-year for small geographies | 1-year data is not available below 65,000 population |
| Compare non-overlapping 5-year periods | Overlapping periods share data and are not independent |
| Stay within the same tract vintage | Tract boundaries change each decade |
| Adjust dollar values with CPI | Census reports nominal dollars |
| Use `time_series=True` for PEP | Single API call for all years in a vintage |

---

## See Also

- [ACS Data](acs-data.md) — ACS query patterns and year-over-year comparisons
- [Population Estimates](population-estimates.md) — Using `time_series=True` for built-in multi-year PEP data
- [Finding Variables](variables.md) — Checking variable availability across years with `load_variables()`
