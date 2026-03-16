# Understanding Margins of Error

The American Community Survey (ACS) is a **sample** --- not a full count of
every person in the United States. Because only a fraction of the population
is surveyed, every ACS estimate comes with a **margin of error** (MOE) that
quantifies the uncertainty.

This guide explains MOE at three levels of depth, from the basics that
everyone needs to understand, through statistical testing for analysts, to
the propagation formulas researchers need when deriving new estimates.

---

## Level 1: What is an MOE?

**Audience:** Everyone working with ACS data.

### The basics

An MOE tells you the range around an estimate where the true value likely
falls. The Census Bureau publishes MOEs at the **90% confidence level**,
meaning there is a 90% chance the true value is within the estimate +/- MOE.

!!! example "Reading an MOE"

    Suppose a county's median household income is reported as:

    - **Estimate:** $50,000
    - **MOE:** +/- $3,000

    This means the true median income for that county is likely between
    **$47,000 and $53,000** (with 90% confidence).

### Why do MOEs exist?

The ACS surveys about 3.5 million households per year --- roughly 2.4% of
all US households. This sample is large enough to produce reliable estimates
for states and big cities, but for smaller geographies (tracts, block
groups, small counties) the sample size drops and uncertainty grows.

**Rule of thumb:** The smaller the geography or population, the larger the
MOE relative to the estimate.

| Geography level | Typical reliability |
|---|---|
| United States | Very precise (tiny MOE) |
| State | Precise |
| Large county (500k+) | Good |
| Small county (<50k) | Moderate to poor |
| Census tract | Variable --- check MOE |
| Block group | Often very large MOEs |

### Can I ignore MOEs for mapping?

For **visualization** purposes (choropleth maps, general patterns), it is
common practice to map the estimates without displaying MOEs. The spatial
patterns are usually meaningful even if individual values are uncertain.

!!! warning "Be cautious with comparisons"

    MOEs matter most when you are **comparing** two geographies or tracking
    changes over time. Two estimates that look different may have overlapping
    confidence intervals, meaning the difference is not statistically
    significant. See [Level 2](#level-2-when-does-moe-affect-my-analysis)
    for how to test this.

### MOE in PyPUMS output

By default, `get_acs()` returns both the estimate and MOE in tidy format:

```python exec="on" source="tabbed-left" session="moe"
from pypums import get_acs

df = get_acs(
    "county",
    variables="B19013_001",
    state="CA",
    year=2022,
)

print(df[["NAME", "variable", "estimate", "moe"]].head())
```

Notice how Alpine County (population ~1,100) has a much larger MOE relative
to its estimate compared to Alameda County (population ~1.6 million).

---

## Level 2: When does MOE affect my analysis?

**Audience:** Journalists, policy analysts, data scientists.

### Testing if a difference is statistically significant

The most common question is: **"Is the difference between two estimates
real or just noise?"** PyPUMS provides the `significance()` function to
answer this.

```python
from pypums import significance
```

#### Function signature

```python
significance(
    est1,           # first estimate
    est2,           # second estimate
    moe1,           # MOE of first estimate (at 90% confidence)
    moe2,           # MOE of second estimate (at 90% confidence)
    *,
    clevel=0.90,    # confidence level for the test: 0.90, 0.95, or 0.99
) -> bool           # True if difference is statistically significant
```

#### Example: comparing two cities' income

```python exec="on" source="tabbed-left" session="moe"
from pypums import significance

# Suppose:
# City A: estimate = $85,000, MOE = $4,000
# City B: estimate = $78,000, MOE = $5,000

is_different = significance(85000, 78000, 4000, 5000, clevel=0.90)
print(is_different)
```

The $7,000 gap is statistically significant at the 90% confidence level.

#### Confidence levels

The `clevel` parameter controls how strict the test is:

| Confidence level | Z-score | Interpretation |
|---|---|---|
| `0.90` | 1.645 | Standard Census threshold --- "likely different" |
| `0.95` | 1.960 | Common in academic research --- "probably different" |
| `0.99` | 2.576 | Very strict --- "almost certainly different" |

```python exec="on" source="tabbed-left" session="moe"
# Same comparison at different confidence levels
print(f"90% confidence: {significance(85000, 78000, 4000, 5000, clevel=0.90)}")
print(f"95% confidence: {significance(85000, 78000, 4000, 5000, clevel=0.95)}")
print(f"99% confidence: {significance(85000, 78000, 4000, 5000, clevel=0.99)}")
```

!!! info "How the test works"

    `significance()` converts 90% MOEs to standard errors, computes the
    standard error of the difference, and checks whether the observed
    difference exceeds the critical value:

    1. Convert MOE to SE: $SE = MOE / 1.645$
    2. SE of the difference: $SE_{diff} = \sqrt{SE_1^2 + SE_2^2}$
    3. Significant if: $|est_1 - est_2| > z \times SE_{diff}$

### Scaling MOE to different confidence levels

The Census API publishes MOEs at 90% confidence. If your analysis requires
95% or 99% confidence intervals, use the `moe_level` parameter:

```python
# Get data with MOE scaled to 95% confidence
df_95 = get_acs(
    "county",
    variables="B19013_001",
    state="CA",
    year=2022,
    moe_level=95,
)
```

The scaling formula divides by the 90% z-score and multiplies by the target
z-score:

$$
MOE_{new} = MOE_{90} \times \frac{z_{new}}{1.645}
$$

| Target level | Multiplier | Effect |
|---|---|---|
| 90% | 1.000 | No change (default) |
| 95% | 1.192 | MOE increases ~19% |
| 99% | 1.566 | MOE increases ~57% |

### The MOE-to-SE relationship

All MOE math starts from converting to standard errors:

$$
SE = \frac{MOE}{z}
$$

| Confidence level | Z-score |
|---|---|
| 90% | 1.645 |
| 95% | 1.960 |
| 99% | 2.576 |

Since the Census publishes at 90%:

$$
SE = \frac{MOE_{90}}{1.645}
$$

---

## Level 3: MOE propagation for derived estimates

**Audience:** Researchers, statisticians, advanced analysts.

When you create a **new** estimate by combining Census variables --- adding
them up, computing a ratio, calculating a proportion --- you need to propagate
the MOEs through the arithmetic. PyPUMS implements the standard Census Bureau
formulas from the **ACS General Handbook, Chapter 8**.

### `moe_sum()` --- combining margins of error for sums

When adding estimates together (e.g., summing age groups to get a total):

```python
from pypums import moe_sum
```

**Formula:**

$$
MOE_{sum} = \sqrt{\sum_{i} MOE_i^2}
$$

**Example:** Combine two age groups to get total population 18-34.

```python exec="on" source="tabbed-left" session="moe"
from pypums import moe_sum

# Age 18-24: estimate=5000, moe=800
# Age 25-34: estimate=7000, moe=600

total_est = 5000 + 7000  # 12,000
total_moe = moe_sum([800, 600])  # sqrt(800^2 + 600^2) = 1000.0

print(f"Population 18-34: {total_est} +/- {total_moe:.0f}")
```

!!! note

    This formula assumes the estimates are **independent** (uncorrelated).
    If the variables come from the same table and are subsets of the same
    total, the formula still provides a conservative approximation.

### `moe_ratio()` --- margins of error for ratios

When dividing one estimate by another where the numerator is **not** a
subset of the denominator:

```python
from pypums import moe_ratio
```

**Formula:**

$$
MOE_{ratio} = \frac{\sqrt{MOE_{num}^2 + \left(\frac{num}{denom}\right)^2 \times MOE_{denom}^2}}{denom}
$$

**Example:** Ratio of renters to homeowners.

```python exec="on" source="tabbed-left" session="moe"
from pypums import moe_ratio

# Renters: estimate=3000, moe=400
# Owners:  estimate=7000, moe=500

ratio_moe = moe_ratio(num=3000, denom=7000, moe_num=400, moe_denom=500)
ratio_est = 3000 / 7000  # 0.4286

print(f"Renter-to-owner ratio: {ratio_est:.3f} +/- {ratio_moe:.3f}")
```

### `moe_prop()` --- margins of error for proportions

When the numerator **is** a subset of the denominator (e.g., percent of
population with a bachelor's degree):

```python
from pypums import moe_prop
```

**Formula:**

$$
MOE_{prop} = \frac{\sqrt{MOE_{num}^2 - \hat{p}^2 \times MOE_{denom}^2}}{denom}
$$

where $\hat{p} = num / denom$.

!!! info "Negative radicand fallback"

    When $MOE_{num}^2 < \hat{p}^2 \times MOE_{denom}^2$ (the expression
    under the square root is negative), the proportion formula is undefined.
    In this case, `moe_prop()` automatically falls back to `moe_ratio()`,
    which uses addition instead of subtraction under the radical.

    This is the recommended approach from the Census Bureau's handbook.

**Example:** Proportion of population with a bachelor's degree.

```python exec="on" source="tabbed-left" session="moe"
from pypums import moe_prop

# Bachelor's holders: estimate=15000, moe=1200
# Total population 25+: estimate=50000, moe=800

prop_moe = moe_prop(num=15000, denom=50000, moe_num=1200, moe_denom=800)
prop_est = 15000 / 50000  # 0.30

print(f"Bachelor's rate: {prop_est:.1%} +/- {prop_moe:.4f}")
```

### `moe_product()` --- margins of error for products

When multiplying two estimates together:

```python
from pypums import moe_product
```

**Formula:**

$$
MOE_{product} = \sqrt{est_1^2 \times MOE_2^2 + est_2^2 \times MOE_1^2}
$$

**Example:** Estimated total income (households x median income).

```python exec="on" source="tabbed-left" session="moe"
from pypums import moe_product

# Households: estimate=10000, moe=500
# Avg income: estimate=60000, moe=3000

product_moe = moe_product(est1=10000, est2=60000, moe1=500, moe2=3000)
product_est = 10000 * 60000  # 600,000,000

print(f"Total income: ${product_est:,.0f} +/- ${product_moe:,.0f}")
```

### Practical workflow: deriving a custom estimate

Here is a complete example that computes the percentage of housing units that
are vacant, with a properly propagated MOE:

```python exec="on" source="tabbed-left" session="moe"
from pypums import moe_prop

# Get occupied and total housing units
df = get_acs(
    "county",
    variables=["B25002_001", "B25002_003"],
    state="CA",
    year=2022,
    output="wide",
)

# B25002_001E = total housing units
# B25002_003E = vacant housing units
df["vacancy_rate"] = df["B25002_003E"] / df["B25002_001E"]

# Propagate MOE for each row
df["vacancy_moe"] = df.apply(
    lambda row: moe_prop(
        num=row["B25002_003E"],
        denom=row["B25002_001E"],
        moe_num=row["B25002_003M"],
        moe_denom=row["B25002_001M"],
    ),
    axis=1,
)

print(df[["NAME", "vacancy_rate", "vacancy_moe"]].head())
```

### Z-score reference table

All MOE calculations use z-scores from the standard normal distribution:

| Confidence level | Z-score | Use case |
|---|---|---|
| 90% | 1.645 | Census Bureau default; `moe_level=90` |
| 95% | 1.960 | Standard academic threshold; `moe_level=95` |
| 99% | 2.576 | Conservative threshold; `moe_level=99` |

The relationship between MOE and standard error at any confidence level is:

$$
MOE = z \times SE
$$

$$
SE = \frac{MOE}{z}
$$

### Source

All formulas in this guide come from the **U.S. Census Bureau's ACS General
Handbook, Chapter 8: Calculating Measures of Error for Derived Estimates**.
This is the authoritative reference for working with ACS margins of error.

---

## Quick reference

| Task | Function | Formula |
|---|---|---|
| Combine estimates by addition | `moe_sum(moe)` | $\sqrt{\sum MOE_i^2}$ |
| Ratio (numerator not subset of denominator) | `moe_ratio(num, denom, moe_num, moe_denom)` | $\frac{\sqrt{MOE_n^2 + r^2 \cdot MOE_d^2}}{denom}$ |
| Proportion (numerator is subset) | `moe_prop(num, denom, moe_num, moe_denom)` | $\frac{\sqrt{MOE_n^2 - p^2 \cdot MOE_d^2}}{denom}$ |
| Product of two estimates | `moe_product(est1, est2, moe1, moe2)` | $\sqrt{est_1^2 \cdot MOE_2^2 + est_2^2 \cdot MOE_1^2}$ |
| Test if difference is significant | `significance(est1, est2, moe1, moe2, clevel=)` | $\|est_1 - est_2\| > z \cdot SE_{diff}$ |
| Scale MOE confidence level | `get_acs(..., moe_level=95)` | $MOE_{new} = MOE_{90} \times \frac{z_{new}}{1.645}$ |

All functions are available from the top-level `pypums` namespace:

```python
from pypums import moe_sum, moe_ratio, moe_prop, moe_product, significance
```

---

## See Also

- [ACS Data](acs-data.md) — Using `moe_level` in ACS queries and combining MOE utilities with results
- [API Reference](../reference/api.md) — Full function signatures for MOE utilities and data retrieval
