# Finding Variables

Every piece of Census data is identified by a **variable code** --- a short
alphanumeric string like `B19013_001` that points to a specific table, row,
and measurement. Before you can pull data with `get_acs()` or
`get_decennial()`, you need to know the right variable codes.

PyPUMS provides `pypums.load_variables()` to search and browse the full Census
variable catalog, plus `pypums.datasets.pums_variables()` for PUMS microdata fields.

## What is a Census variable?

A Census variable code encodes three pieces of information:

```
B19013_001
│     │ │
│     │ └── Variable number (001 = first variable in the table)
│     └──── Table number (19013)
└────────── Table prefix (B = detailed table)
```

The variable `B19013_001` is **Median Household Income** from detailed
table B19013.

!!! info "Estimate and MOE suffixes"

    When you pass a variable like `B19013_001` to `get_acs()`, PyPUMS
    automatically requests **two** columns from the API:

    - `B19013_001E` --- the **estimate**
    - `B19013_001M` --- the **margin of error**

    You never need to add the `E` or `M` suffix yourself. Just pass the
    base variable name.

## Variable naming conventions

The Census Bureau uses letter prefixes to organize tables by type:

### ACS tables

| Prefix | Type | Description | Example |
|---|---|---|---|
| **B** | Detailed | Full cross-tabulations with the most detail | `B19013_001` (median income) |
| **S** | Subject | Pre-computed summaries on a theme | `S1701_C01_001` (poverty status) |
| **DP** | Data Profile | Broad demographic profiles | `DP05_0001` (total population) |
| **C** | Collapsed | Simplified versions of B-tables with fewer categories | `C17002_001` (ratio of income to poverty) |

### Decennial Census tables

| Prefix | Type | Description | Example |
|---|---|---|---|
| **P** | Population | Population counts and characteristics | `P1_001N` (total population) |
| **H** | Housing | Housing unit counts and characteristics | `H1_001N` (total housing units) |

!!! note "Decennial suffix conventions"

    Decennial Census 2020 (PL 94-171) variables use an `N` suffix for values
    (e.g., `P1_001N`), unlike the ACS `E`/`M` convention. There are no MOE
    columns for decennial data because it is a complete count, not a sample.

## Browsing variables with `load_variables()`

### Function signature

```python
from pypums import load_variables

vars_df = load_variables(
    year,           # e.g. 2022
    dataset,        # e.g. "acs5", "acs1", "acs5/subject", "pl"
    cache=False,    # cache results for fast subsequent lookups
)
```

### Returns

A DataFrame with three columns:

| Column | Description |
|---|---|
| `name` | Variable code (e.g., `B19013_001E`) |
| `label` | Human-readable label |
| `concept` | Broader topic or table name |

### Dataset identifiers

| Identifier | Dataset |
|---|---|
| `"acs5"` | ACS 5-year detailed tables |
| `"acs1"` | ACS 1-year detailed tables |
| `"acs5/subject"` | ACS 5-year subject tables (S-tables) |
| `"acs5/profile"` | ACS 5-year data profile tables (DP-tables) |
| `"acs1/subject"` | ACS 1-year subject tables |
| `"acs1/profile"` | ACS 1-year data profile tables |
| `"pl"` | Decennial Census PL 94-171 Redistricting Data |

### Example: search for income variables

```python
from pypums import load_variables

vars_df = load_variables(2022, "acs5")

# Search by label
income_vars = vars_df[
    vars_df["label"].str.contains("median household income", case=False, na=False)
]
print(income_vars[["name", "label"]].head())
```

```
            name                                             label
12345  B19013_001E  Estimate!!Median household income in the past...
12346  B19013_001M  Margin of Error!!Median household income in t...
```

## Filtering strategies

The variable catalog is large --- the ACS 5-year dataset alone contains over
30,000 variables. Use pandas filtering to narrow your search:

=== "Search by label"

    ```python
    vars_df = load_variables(2022, "acs5")

    # Find variables about educational attainment
    education = vars_df[
        vars_df["label"].str.contains("bachelor", case=False, na=False)
    ]
    print(f"{len(education)} variables matching 'bachelor'")
    print(education[["name", "label"]].head(3))
    ```

    ```
    42 variables matching 'bachelor'
              name                                              label
    0  B15003_022E  Estimate!!Total:!!Bachelor's degree
    1  B15003_022M  Margin of Error!!Total:!!Bachelor's degree
    2  B15002_015E  Estimate!!Total:!!Male:!!Bachelor's degree
    ```

=== "Search by concept"

    ```python
    # Find all variables in a specific table or topic
    poverty = vars_df[
        vars_df["concept"].str.contains("poverty", case=False, na=False)
    ]
    print(f"{len(poverty)} variables related to poverty")
    ```

    ```
    584 variables related to poverty
    ```

=== "Search by variable name"

    ```python
    # Find all variables in table B01001 (Sex by Age)
    sex_by_age = vars_df[
        vars_df["name"].str.startswith("B01001_")
    ]
    print(f"{len(sex_by_age)} variables in B01001")
    print(sex_by_age[["name", "label"]].head(3))
    ```

    ```
    98 variables in B01001
              name                                         label
    0  B01001_001E  Estimate!!Total:
    1  B01001_001M  Margin of Error!!Total:
    2  B01001_002E  Estimate!!Total:!!Male:
    ```

=== "Combined search"

    ```python
    # Search across name, label, and concept simultaneously
    query = "median income"
    mask = (
        vars_df["name"].str.contains(query, case=False, na=False)
        | vars_df["label"].str.contains(query, case=False, na=False)
        | vars_df["concept"].str.contains(query, case=False, na=False)
    )
    results = vars_df[mask]
    print(f"{len(results)} variables matching 'median income'")
    ```

    ```
    186 variables matching 'median income'
    ```

## Caching variable lookups

The variable catalog does not change within a Census release year. Pass
`cache=True` to save the result to disk so subsequent calls return instantly:

```python
# First call fetches from the Census API (~2-5 seconds)
vars_df = load_variables(2022, "acs5", cache=True)

# Second call loads from disk (~instant)
vars_df = load_variables(2022, "acs5", cache=True)
```

Cached files are stored in `~/.pypums/cache/variables/`. Both an in-memory
cache and a persistent disk cache are used: the in-memory cache speeds up
repeated calls in the same Python session, and the disk cache persists across
sessions.

## PUMS variables

PUMS (Public Use Microdata Sample) uses a different variable system. Instead
of table-based codes, PUMS variables are named fields like `AGEP` (age),
`SCHL` (educational attainment), or `PINCP` (personal income).

Use `pums_variables()` to browse them:

```python
from pypums.datasets import pums_variables

pums_df = pums_variables(year=2023, survey="acs5", cache=True)

# Search for income-related PUMS variables
income_pums = pums_df[
    pums_df["label"].str.contains("income", case=False, na=False)
]
print(income_pums[["name", "label"]].head())
```

```
    name                                    label
0  FINCP     Family income (past 12 months)
1  HINCP  Household income (past 12 months)
2   INTP        Interest, dividends, and net ...
3    OIP        All other income (past 12 months)
4  PINCP  Total person's income (past 12 months)
```

The `pums_variables()` function returns a DataFrame with columns:

| Column | Description |
|---|---|
| `name` | Variable code (e.g., `PINCP`) |
| `label` | Human-readable label |
| `concept` | Broader topic category |
| `var_type` | Data type (int, string, float) |

## Common variables quick reference

These are some of the most frequently used ACS 5-year variables:

| Variable | Description | Table |
|---|---|---|
| `B01003_001` | Total population | Total Population |
| `B01001_001` | Total population (Sex by Age) | Sex by Age |
| `B01002_001` | Median age | Median Age by Sex |
| `B19013_001` | Median household income | Median Household Income |
| `B19001_001` | Total households (income brackets) | Household Income |
| `B25077_001` | Median home value | Median Value (Owner-Occupied) |
| `B25064_001` | Median gross rent | Median Gross Rent |
| `B15003_001` | Total population 25+ (education) | Educational Attainment |
| `B15003_022` | Bachelor's degree | Educational Attainment |
| `B15003_023` | Master's degree | Educational Attainment |
| `B25001_001` | Total housing units | Housing Units |
| `B25002_002` | Occupied housing units | Occupancy Status |
| `B25002_003` | Vacant housing units | Occupancy Status |
| `B03002_001` | Total population (race/ethnicity) | Hispanic or Latino Origin by Race |
| `B23025_005` | Unemployed population | Employment Status |

!!! tip "Table vs. variable"

    If you want **all** variables from a table, pass the `table` parameter
    to `get_acs()` instead of listing variables individually:

    ```python
    from pypums import get_acs

    # Get ALL variables from the Sex by Age table
    df = get_acs("state", table="B01001", year=2022)
    ```

## CLI: searching variables from the terminal

PyPUMS includes a `variables` CLI command for quick lookups without writing
Python code:

```shell
# Browse all ACS 5-year variables for 2022
pypums variables --dataset acs5 --year 2022

# Search for income-related variables
pypums variables --dataset acs5 --year 2022 --search "income"

# Search subject tables for poverty
pypums variables --dataset acs5/subject --year 2022 --search "poverty"

# Cache results for faster subsequent searches
pypums variables --dataset acs5 --year 2022 --search "income" --cache
```

The `--search` flag filters across the `name`, `label`, and `concept` columns
simultaneously, matching any variable where at least one column contains
the search term (case-insensitive).

## Workflow: from variable discovery to data

A typical workflow looks like this:

```python
from pypums import load_variables, get_acs

# Step 1: Find the variable you need
vars_df = load_variables(2022, "acs5", cache=True)
results = vars_df[vars_df["label"].str.contains("median household income", case=False, na=False)]
print(results[["name", "label"]])
```

```
            name                                              label
12345  B19013_001E  Estimate!!Median household income in the past...
12346  B19013_001M  Margin of Error!!Median household income in t...
```

```python
# Step 2: Use the base variable name (without E/M suffix) in get_acs()
income = get_acs(
    "county",
    variables="B19013_001",    # no E or M suffix needed
    state="CA",
    year=2022,
)

print(income.head())
```

```
     GEOID                          NAME    variable  estimate     moe
0  06001      Alameda County, California  B19013_001  122488.0  1729.0
1  06003       Alpine County, California  B19013_001   62750.0 20225.0
2  06005       Amador County, California  B19013_001   70634.0  5180.0
3  06007        Butte County, California  B19013_001   55718.0  2214.0
4  06009    Calaveras County, California  B19013_001   68906.0  5439.0
```

!!! warning "Suffix mismatch"

    `load_variables()` returns variable names **with** their suffixes
    (e.g., `B19013_001E`), but `get_acs()` expects the base name
    **without** suffixes (e.g., `B19013_001`). PyPUMS adds the `E` and
    `M` suffixes automatically when building the API request.

    Strip the suffix before passing to `get_acs()`:

    ```python
    var_name = "B19013_001E"
    base_name = var_name[:-1]  # "B19013_001"
    ```

---

## See Also

- [ACS Data](acs-data.md) — Using variables with `get_acs()` to pull summary table data
- [Decennial Census](decennial-data.md) — Decennial variable codes and naming conventions
- [Datasets Reference](../reference/datasets.md) — Built-in datasets including FIPS codes and recode tables
