# Coming from tidycensus (R)

If you've used Kyle Walker's [tidycensus](https://walker-data.com/tidycensus/) R package, PyPUMS will feel familiar. This guide maps tidycensus concepts to their PyPUMS equivalents.

## Function Mapping

| tidycensus (R) | PyPUMS (Python) | Notes |
|----------------|-----------------|-------|
| `get_acs()` | `pypums.get_acs()` | Nearly identical parameters |
| `get_decennial()` | `pypums.get_decennial()` | Nearly identical parameters |
| `get_pums()` | `pypums.get_pums()` | Similar, uses Census API |
| `get_estimates()` | `pypums.get_estimates()` | Similar structure |
| `get_flows()` | `pypums.get_flows()` | Similar structure |
| `load_variables()` | `pypums.load_variables()` | Same concept |
| `fips_codes` | `pypums.datasets.fips_codes` | DataFrame |

## Parameter Mapping

### get_acs()

| tidycensus | PyPUMS | Notes |
|-----------|---------|-------|
| `geography = "county"` | `geography="county"` | Same strings |
| `variables = c("B19013_001")` | `variables=["B19013_001"]` | List instead of c() |
| `table = "B01001"` | `table="B01001"` | Identical |
| `state = "CA"` | `state="CA"` | Identical |
| `county = "Los Angeles"` | `county="037"` | PyPUMS uses FIPS codes (see tip below) |
| `year = 2022` | `year=2022` | Identical |
| `survey = "acs5"` | `survey="acs5"` | Identical |
| `output = "tidy"` | `output="tidy"` | Identical |
| `moe_level = 90` | `moe_level=90` | Identical |
| `geometry = TRUE` | `geometry=True` | Python boolean |
| `cache_table = TRUE` | `cache_table=True` | Identical concept |
| `key = "..."` | `key="..."` | Identical |
| `summary_var = "B01003_001"` | `summary_var="B01003_001"` | Identical |
| `keep_geo_vars = TRUE` | `keep_geo_vars=True` | Identical |

!!! tip "Looking up county FIPS codes"
    Unlike tidycensus, PyPUMS requires numeric FIPS codes for the `county`
    parameter. Use `lookup_fips()` to translate a county name:

    ```python
    from pypums.datasets import lookup_fips

    lookup_fips(state="California", county="Los Angeles County")
    # => '06037'  →  pass county="037" (last 3 digits)
    ```

    See [Geography & FIPS Codes](../guides/geography.md) for more details.

### get_pums()

| tidycensus | PyPUMS | Notes |
|-----------|---------|-------|
| `variables = c("AGEP", "SEX")` | `variables=["AGEP", "SEX"]` | List instead of c() |
| `state = "CA"` | `state="CA"` | Identical |
| `puma = "00106"` | `puma="00106"` | Identical |
| `survey = "acs5"` | `survey="acs5"` | Identical |
| `variables_filter = list(SEX = 1)` | `variables_filter={"SEX": 1}` | Dict instead of named list |
| `rep_weights = "person"` | `rep_weights="person"` | Identical |
| `recode = TRUE` | `recode=True` | Identical concept |
| `show_call = TRUE` | `show_call=True` | Identical |

## Side-by-Side Examples

### Basic ACS query

=== "R (tidycensus)"

    ```r
    library(tidycensus)

    df <- get_acs(
      geography = "county",
      variables = c(
        medincome = "B19013_001"
      ),
      state = "CA",
      year = 2022
    )
    head(df)
    ```

=== "Python (PyPUMS)"

    ```python
    import pypums

    df = pypums.get_acs(
        geography="county",
        variables=["B19013_001"],
        state="CA",
        year=2022,
    )
    df.head()
    ```

### ACS with geometry

=== "R (tidycensus)"

    ```r
    library(tidycensus)

    df <- get_acs(
      geography = "tract",
      variables = "B19013_001",
      state = "CA",
      county = "Los Angeles",
      geometry = TRUE,
      year = 2022
    )
    plot(df["estimate"])
    ```

=== "Python (PyPUMS)"

    ```python
    import pypums

    df = pypums.get_acs(
        geography="tract",
        variables=["B19013_001"],
        state="CA",
        county="037",  # FIPS code for Los Angeles
        geometry=True,
        year=2022,
    )
    df.plot(column="estimate", legend=True)
    ```

### PUMS microdata

=== "R (tidycensus)"

    ```r
    library(tidycensus)

    pums <- get_pums(
      variables = c("AGEP", "SEX", "WAGP"),
      state = "CA",
      survey = "acs1",
      year = 2022,
      recode = TRUE,
      rep_weights = "person"
    )
    head(pums)
    ```

=== "Python (PyPUMS)"

    ```python
    import pypums

    pums = pypums.get_pums(
        variables=["AGEP", "SEX", "WAGP"],
        state="CA",
        survey="acs1",
        year=2022,
        recode=True,
        rep_weights="person",
    )
    pums.head()
    ```

### Variable discovery

=== "R (tidycensus)"

    ```r
    vars <- load_variables(2022, "acs5")
    vars[grepl("median.*income", vars$label, ignore.case = TRUE), ]
    ```

=== "Python (PyPUMS)"

    ```python
    import pypums

    vars_df = pypums.load_variables(2022, "acs5")
    vars_df[vars_df["label"].str.contains("median.*income", case=False)]
    ```

## Key Differences

| Feature | tidycensus | PyPUMS |
|---------|-----------|---------|
| **Variable naming** | Can rename inline: `c(medincome = "B19013_001")` | Use standard variable codes; rename with pandas after |
| **County parameter** | Accepts county names: `county = "Los Angeles"` | Uses FIPS codes: `county="037"`. Use `lookup_fips()` to find codes |
| **Output type** | tibble / sf object | pandas DataFrame / GeoDataFrame |
| **Spatial CRS** | Varies by function | Always NAD83 (EPSG:4269) from TIGER/Line |
| **Plotting** | ggplot2 / tmap | matplotlib / geopandas `.plot()` |
| **PUMS download** | Downloads CSV files from FTP | Queries Census API directly (faster for filtered requests) |
| **Survey design** | Returns `tbl_svy` (srvyr package) | Returns `SurveyDesign` object with SDR methods |

## What's the Same

- Same Census API under the hood
- Same variable codes (B19013_001, P1_001N, etc.)
- Same geography names ("state", "county", "tract", etc.)
- Same TIGER/Line shapefiles for geometry
- Same MOE formulas from the ACS Handbook
- Same replicate weight methodology (SDR with 80 weights)
