# Migration Flows

The ACS Migration Flows dataset tracks county-to-county and metro-to-metro
migration patterns across the United States. PyPUMS wraps the Census Bureau's
`/acs/flows` endpoint with `get_flows()`, giving you tidy DataFrames of
who moved where --- and how many.

## Function signature

```python
from pypums import get_flows

df = get_flows(
    geography,                    # "county" or "metropolitan statistical area"
    *,
    variables=None,               # additional variable IDs to request
    breakdown=None,               # breakdown dimensions (e.g. "AGE_GROUP")
    breakdown_labels=False,       # add human-readable label columns
    year=2019,                    # data year (default 2019)
    output="tidy",                # "tidy" or "wide"
    state=None,                   # state FIPS, abbreviation, or name
    county=None,                  # county FIPS code
    msa=None,                     # metropolitan statistical area code
    geometry=False,               # attach TIGER/Line shapes
    moe_level=90,                 # confidence level: 90, 95, or 99
    cache_table=False,            # cache API response on disk
    show_call=False,              # print the API URL
    key=None,                     # Census API key override
)
```

!!! info "Supported geographies"

    Migration flows are only available at two geography levels:

    - `"county"` --- county-to-county flows
    - `"metropolitan statistical area"` --- MSA-to-MSA flows

    Passing any other geography raises a `ValueError`.

## Default columns

Every call to `get_flows()` returns these columns automatically:

| Column | Description |
|---|---|
| `FULL1_NAME` | Origin geography name |
| `FULL2_NAME` | Destination geography name |
| `MOVEDIN` | Number of people who moved **into** the origin from the destination |
| `MOVEDIN_M` | Margin of error for MOVEDIN |
| `MOVEDOUT` | Number of people who moved **out of** the origin to the destination |
| `MOVEDOUT_M` | Margin of error for MOVEDOUT |
| `MOVEDNET` | Net migration (MOVEDIN - MOVEDOUT) |
| `MOVEDNET_M` | Margin of error for MOVEDNET |

## Basic example: county flows for California

```python
from pypums import get_flows

ca_flows = get_flows(
    "county",
    state="CA",
    year=2019,
)

ca_flows.head()
```

In tidy output (the default), the DataFrame has `variable`, `estimate`, and `moe`
columns instead of separate MOVEDIN/MOVEDOUT/MOVEDNET columns:

```
  FULL1_NAME                  FULL2_NAME      GEOID  variable   estimate    moe
  Alameda County, California  Los Angeles...  06001  MOVEDIN    2345.0      890.0
  Alameda County, California  Los Angeles...  06001  MOVEDOUT   1987.0      780.0
  Alameda County, California  Los Angeles...  06001  MOVEDNET    358.0     1182.0
  ...
```

!!! tip "Wide output"

    Pass `output="wide"` to keep MOVEDIN, MOVEDOUT, and MOVEDNET as separate
    columns rather than melting into tidy format:

    ```python
    ca_flows_wide = get_flows("county", state="CA", year=2019, output="wide")
    ```

## MSA-level flows

Metropolitan Statistical Area flows capture migration between metro regions,
regardless of state boundaries:

```python
msa_flows = get_flows(
    "metropolitan statistical area",
    year=2019,
)

# Filter to a specific MSA by code
la_metro = get_flows(
    "metropolitan statistical area",
    msa="31080",       # Los Angeles-Long Beach-Anaheim
    year=2019,
)
```

## Breakdowns by demographic characteristics

The flows API supports several breakdown dimensions that let you slice
migration by age, race, sex, and Hispanic origin:

| Breakdown | Values |
|---|---|
| `MOTEFG` | Metro/micro/noncore origin-destination type |
| `AGE_GROUP` | Age groups (all ages, 1-4, 5-17, 18-24, ..., 75+) |
| `RACE_GROUP` | Race categories (White alone, Black alone, Asian alone, ...) |
| `SEX_GROUP` | Male, Female, Both sexes |
| `HISP_GROUP` | Hispanic or Latino, Non-Hispanic, Both |

```python
# County flows broken down by age group
age_flows = get_flows(
    "county",
    state="CA",
    breakdown="AGE_GROUP",
    year=2019,
)
```

### Adding human-readable labels

By default, breakdown columns contain numeric codes (e.g., `"004"` for the
18-24 age group). Set `breakdown_labels=True` to add a `*_label` column
with the decoded description:

```python
age_flows = get_flows(
    "county",
    state="CA",
    breakdown="AGE_GROUP",
    breakdown_labels=True,
    year=2019,
)

# Now includes AGE_GROUP_label column:
# "004" -> "18 to 24 years"
```

The label mapping comes from `pypums.datasets.mig_recodes`. You can inspect
the full lookup table directly:

```python
from pypums.datasets import mig_recodes

print(mig_recodes)
#   dimension   code  label
# 0 MOTEFG      00    Not identified
# 1 MOTEFG      01    Metro to metro
# 2 MOTEFG      02    Metro to micro
# ...
```

## MOE scaling

The Census API returns margins of error at the 90% confidence level. You can
rescale to 95% or 99% confidence using the `moe_level` parameter:

=== "90% confidence (default)"

    ```python
    flows_90 = get_flows("county", state="CA", year=2019, moe_level=90)
    ```

=== "95% confidence"

    ```python
    flows_95 = get_flows("county", state="CA", year=2019, moe_level=95)
    # MOE values are multiplied by 1.960 / 1.645 ~ 1.19
    ```

=== "99% confidence"

    ```python
    flows_99 = get_flows("county", state="CA", year=2019, moe_level=99)
    # MOE values are multiplied by 2.576 / 1.645 ~ 1.57
    ```

The scaling formula is:

$$
\text{MOE}_{\text{new}} = \text{MOE}_{90} \times \frac{z_{\text{new}}}{z_{90}}
$$

where z-scores are 1.645 (90%), 1.960 (95%), and 2.576 (99%).

## Geometry support

Set `geometry=True` to attach TIGER/Line cartographic boundary shapes to
the origin geography. This returns a GeoDataFrame you can plot directly:

```python
ca_flows_geo = get_flows(
    "county",
    state="CA",
    year=2019,
    geometry=True,
)

# ca_flows_geo is a GeoDataFrame with a 'geometry' column
ca_flows_geo.plot(column="estimate", legend=True)
```

!!! note "Origin geography only"

    Shapes are attached to the **origin** geography (the first geography in
    each flow pair). If you need shapes for destinations, join them separately
    using `pypums.spatial.attach_geometry`.

!!! warning "Requires geopandas"

    The `geometry=True` option requires `geopandas` to be installed:

    ```shell
    pip install pypums[spatial]
    ```

## Caching

For repeated analysis, cache the API response to avoid redundant network calls:

```python
flows = get_flows(
    "county",
    state="CA",
    year=2019,
    cache_table=True,    # saves to ~/.pypums/cache/api/
)
```

Cached results expire after 24 hours. Subsequent calls with identical
parameters return the cached DataFrame instantly.

## Debugging API calls

Set `show_call=True` to print the URL and parameters sent to the Census API:

```python
flows = get_flows("county", state="CA", year=2019, show_call=True)
# Census API call: https://api.census.gov/data/2019/acs/flows
#   Parameters: {'get': 'FULL1_NAME,...', 'for': 'county:*', ...}
```

## Interpreting flow data

!!! warning "Large MOEs for small geographies"

    Migration flow estimates for small counties can have very large margins
    of error --- sometimes larger than the estimate itself. This is inherent
    to the ACS sample design: migration is a rare event, and the ACS samples
    only a fraction of the population each year.

    **Before drawing conclusions from flow data:**

    - Check the MOE relative to the estimate (coefficient of variation)
    - Aggregate small counties into larger regions when possible
    - Focus on flows with larger magnitudes where the signal-to-noise ratio
      is better
    - Use `pypums.significance()` to test whether a net flow is meaningfully
      different from zero

### Example: is net migration significant?

```python
from pypums import significance

# Suppose a county shows MOVEDNET=500 with MOVEDNET_M=1200
# Is this net inflow statistically significant?
result = significance(500, 0, 1200, 0, clevel=0.90)
print(result)  # False --- the MOE swamps the estimate
```

## Complete example

Putting it all together --- county-level flows for California, broken down
by age, with labels and geometry:

```python
from pypums import get_flows

ca_age_flows = get_flows(
    "county",
    state="California",
    breakdown="AGE_GROUP",
    breakdown_labels=True,
    year=2019,
    output="wide",
    geometry=True,
    moe_level=95,
    cache_table=True,
)

# Filter to working-age adults (25-34)
young_workers = ca_age_flows[
    ca_age_flows["AGE_GROUP_label"] == "25 to 34 years"
]

# Map net migration
young_workers.plot(column="MOVEDNET", legend=True, cmap="RdBu")
```

---

## See Also

- [API Reference](../reference/api.md) — Full `get_flows()` function signature
- [Margins of Error](margins-of-error.md) — Understanding and propagating flow MOEs
- [Datasets Reference](../reference/datasets.md) — The `mig_recodes` lookup table for breakdown labels
