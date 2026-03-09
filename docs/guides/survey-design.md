# Survey Design & Weights

The American Community Survey (ACS) Public Use Microdata Sample (PUMS) is a
survey, not a full census count. Every record carries a **weight** that tells
you how many people or housing units that record represents in the full
population. Ignoring weights produces biased estimates; using them correctly
lets you reproduce the official Census Bureau tabulations.

---

## What are replicate weights?

Standard error estimation for complex survey designs is not as simple as the
textbook formulas for simple random samples. The Census Bureau provides
**replicate weights** so that analysts can compute standard errors without
knowing the full details of the sample design.

ACS PUMS uses the **successive differences replication (SDR)** method. Each
dataset ships with **80 replicate weight columns** in addition to the main
weight. The idea is:

1. Compute your estimate using the full (main) weight.
2. Re-compute the estimate 80 times, each time using a different replicate
   weight column.
3. The variability across those 80 replicate estimates gives you the standard
   error.

The formula is:

$$
SE = \sqrt{\frac{4}{80} \sum_{r=1}^{80} \left(\hat{\theta}_r - \hat{\theta}\right)^2}
$$

where $\hat{\theta}$ is the full-weight estimate and $\hat{\theta}_r$ is the
estimate from replicate weight $r$.

!!! note "Scale factor: 4/80"
    The `4/80 = 0.05` scale factor is specific to the ACS 80-replicate SDR
    design. Other Census products may use a different number of replicates
    or a different scaling constant. PyPUMS applies this default automatically.

---

## Person weights vs. housing weights

PUMS has two sets of weights because each record can describe either a
**person** or a **housing unit**.

| Weight set       | Main weight | Replicate weights   | Use for                                    |
|------------------|-------------|---------------------|--------------------------------------------|
| **Person**       | `PWGTP`     | `PWGTP1` - `PWGTP80` | Person-level variables: age, income, education, occupation |
| **Housing**      | `WGTP`      | `WGTP1` - `WGTP80`   | Housing-level variables: rent, mortgage, rooms, vehicles   |

!!! warning "Choose the right weight"
    Using person weights for a housing variable (or vice versa) will produce
    incorrect estimates. If your variable describes a characteristic of a
    **person** (e.g., `AGEP`, `WAGP`, `SEX`, `SCHL`), use person weights.
    If it describes a characteristic of a **housing unit** (e.g., `RNTP`,
    `VALP`, `BDSP`, `VEH`), use housing weights.

---

## Fetching PUMS data with replicate weights

Pass `rep_weights="person"` or `rep_weights="housing"` to `get_pums()` to
include the replicate weight columns in the returned DataFrame:

=== "Person weights"

    ```python
    import pypums

    df = pypums.get_pums(
        variables=["AGEP", "WAGP"],
        state="CA",
        year=2023,
        survey="acs5",
        rep_weights="person",
    )

    # The DataFrame now has PWGTP plus PWGTP1 through PWGTP80.
    print(df.columns.tolist()[:10])
    # ['SERIALNO', 'SPORDER', 'PWGTP', 'ST', 'PUMA', 'AGEP', 'WAGP',
    #  'PWGTP1', 'PWGTP2', 'PWGTP3']
    ```

=== "Housing weights"

    ```python
    import pypums

    df = pypums.get_pums(
        variables=["RNTP", "VALP"],
        state="CA",
        year=2023,
        survey="acs5",
        rep_weights="housing",
    )

    # The DataFrame now has WGTP plus WGTP1 through WGTP80.
    ```

=== "Both weight sets"

    ```python
    import pypums

    df = pypums.get_pums(
        variables=["AGEP", "RNTP"],
        state="CA",
        year=2023,
        rep_weights="both",
    )
    ```

---

## The `SurveyDesign` class

`to_survey()` wraps a PUMS DataFrame into a `SurveyDesign` object that
provides methods for weighted estimation and standard error computation.

```python
import pypums

# 1. Fetch PUMS data with replicate weights.
df = pypums.get_pums(
    variables=["AGEP", "WAGP"],
    state="CA",
    year=2023,
    rep_weights="person",
)

# 2. Create a survey design object.
design = pypums.to_survey(df, weight_type="person")
print(design)
# SurveyDesign(n=..., weight='PWGTP', rep_weights=80)
```

### `weighted_estimate(variable)`

Returns the weighted sum (total) for a variable -- the estimate of the
population total.

```python
total_wages = design.weighted_estimate("WAGP")
print(f"Total wages in CA: ${total_wages:,.0f}")
```

### `weighted_mean(variable)`

Returns the weighted mean -- the estimate of the population average.

```python
mean_age = design.weighted_mean("AGEP")
print(f"Mean age in CA: {mean_age:.1f} years")
```

### `standard_error(variable)`

Returns the standard error of the weighted sum using the SDR formula with
all 80 replicate weights.

```python
se_wages = design.standard_error("WAGP")
print(f"SE of total wages: ${se_wages:,.0f}")
```

---

## End-to-end example

Here is a complete workflow that estimates total wages and their standard error
for California workers:

```python
import pypums

# Step 1 -- Fetch person-level PUMS data with replicate weights.
df = pypums.get_pums(
    variables=["AGEP", "WAGP"],
    state="CA",
    year=2023,
    survey="acs5",
    rep_weights="person",
)

# Step 2 -- Filter to workers with positive wages.
workers = df[df["WAGP"] > 0].copy()

# Step 3 -- Create the survey design.
design = pypums.to_survey(workers, weight_type="person")

# Step 4 -- Compute the weighted estimate and standard error.
total_wages = design.weighted_estimate("WAGP")
se_wages = design.standard_error("WAGP")
mean_wage = design.weighted_mean("WAGP")

print(f"Estimated total wages:   ${total_wages:>20,.0f}")
print(f"Standard error:          ${se_wages:>20,.0f}")
print(f"Estimated mean wage:     ${mean_wage:>20,.0f}")
print(f"90% confidence interval: ${total_wages - 1.645 * se_wages:>20,.0f}"
      f" to ${total_wages + 1.645 * se_wages:,.0f}")
```

!!! tip "Confidence intervals"
    The Census Bureau publishes ACS margins of error at the **90% confidence
    level** (z = 1.645). To build a 95% interval, use z = 1.960 instead.

---

## `to_survey()` reference

```python
to_survey(
    df,                       # PUMS DataFrame from get_pums()
    weight_type="person",     # "person" or "housing"
    design="rep_weights",     # only "rep_weights" is supported
) -> SurveyDesign
```

| Parameter     | Default          | Description                                    |
|---------------|------------------|------------------------------------------------|
| `df`          | *(required)*     | PUMS DataFrame containing weight columns       |
| `weight_type` | `"person"`       | `"person"` uses `PWGTP`; `"housing"` uses `WGTP` |
| `design`      | `"rep_weights"`  | Survey design method (only SDR replicate weights is supported) |

!!! warning "Missing weight columns"
    `to_survey()` raises a `ValueError` if the expected weight columns are
    not in the DataFrame. Make sure you passed `rep_weights="person"` (or
    `"housing"`) to `get_pums()`.

---

## Discovering available datasets

`get_survey_metadata()` queries the Census API discovery endpoint and returns
a DataFrame of every available Census Bureau dataset, optionally filtered by
year:

```python
import pypums

# All available datasets.
all_datasets = pypums.get_survey_metadata()
print(all_datasets.shape)
# (hundreds of rows, 5 columns)

# Only 2023 datasets.
datasets_2023 = pypums.get_survey_metadata(year=2023)
print(datasets_2023[["title", "dataset_name"]].head())
```

The returned DataFrame has these columns:

| Column             | Description                          |
|--------------------|--------------------------------------|
| `title`            | Human-readable dataset name          |
| `description`      | Longer description                   |
| `vintage`          | Year / vintage                       |
| `dataset_name`     | API path component (e.g. `acs/acs5`) |
| `distribution_url` | Base URL for the dataset endpoint    |

---

## Verifying results against published tables

A good way to build confidence in your PUMS-based estimates is to compare them
against the official pre-tabulated ACS tables (the "B" and "C" tables available
via `get_acs()`). The official tables are based on the full ACS sample and will
not match your PUMS-based estimates exactly, but they should be in the same
ballpark.

```python
import pypums

# PUMS-based estimate: total population of California.
df_pums = pypums.get_pums(
    variables=["AGEP"],
    state="CA",
    year=2023,
    rep_weights="person",
)
design = pypums.to_survey(df_pums)
pums_total = design.weighted_estimate("AGEP")  # not quite right for pop count

# A simpler approach for population: use the weight itself.
pums_pop = df_pums["PWGTP"].sum()

# Published ACS table estimate.
df_acs = pypums.get_acs(
    geography="state",
    variables="B01001_001",
    state="CA",
    year=2023,
)
acs_pop = df_acs["estimate"].iloc[0]

print(f"PUMS population:  {pums_pop:>12,.0f}")
print(f"ACS table value:  {acs_pop:>12,.0f}")
```

!!! note
    Small differences between PUMS estimates and published table estimates are
    normal. PUMS is a subsample of the full ACS, so some sampling variability
    is expected. Large discrepancies usually indicate a weight or filtering
    error.

---

## See Also

- [PUMS Microdata](pums-microdata.md) — Fetching microdata with replicate weights via `get_pums()`
- [API Reference](../reference/api.md) — Full `SurveyDesign` class reference and `to_survey()` signature
