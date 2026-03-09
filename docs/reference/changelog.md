# Changelog

## 0.2 (2026)

Major release with complete Census API feature parity with R's tidycensus.

### Added

- **`get_acs()`** — Retrieve American Community Survey data via the Census API
    - Tidy and wide output formats
    - MOE confidence level scaling (90%, 95%, 99%)
    - Summary variable support for proportion calculations
    - Geometry attachment (returns GeoDataFrame)
    - `keep_geo_vars` option to preserve raw FIPS columns
    - Built-in caching with configurable TTL

- **`get_decennial()`** — Retrieve Decennial Census data (2000, 2010, 2020)
    - Population group support for DHC-A disaggregated data
    - Tidy and wide output formats
    - Geometry support

- **`get_pums()`** — Load PUMS microdata from the Census API
    - Server-side variable filtering
    - Person and housing replicate weights (80 columns each)
    - Variable recoding with human-readable labels
    - Multi-state queries
    - PUMA-level filtering

- **`get_estimates()`** — Population Estimates Program data
    - Products: population, components, housing, characteristics
    - Breakdown dimensions (age, sex, race, Hispanic origin)
    - Time series support
    - Vintage-based queries

- **`get_flows()`** — ACS Migration Flows data
    - County and MSA-level flows
    - Breakdown labels from migration recodes
    - MOE confidence scaling
    - Geometry support for origin geography

- **`load_variables()`** — Browse and search Census variable metadata
    - In-memory and persistent disk caching
    - Search across datasets: acs5, acs1, pl, acs5/subject, acs5/profile

- **MOE functions** — Margin of error calculations from ACS General Handbook
    - `moe_sum()` — Combined MOE for derived sums
    - `moe_ratio()` — MOE for derived ratios
    - `moe_prop()` — MOE for derived proportions
    - `moe_product()` — MOE for derived products
    - `significance()` — Statistical significance testing

- **Spatial support** — TIGER/Line cartographic boundary integration
    - `attach_geometry()` — Merge shapefiles with Census data
    - `as_dot_density()` — Dot-density point conversion
    - `interpolate_pw()` — Population-weighted areal interpolation
    - Multiple resolution levels: 500k, 5m, 20m

- **Survey design** — Replicate weight standard errors
    - `SurveyDesign` class with SDR method
    - `to_survey()` helper for PUMS DataFrames
    - Weighted estimates and means

- **`get_survey_metadata()`** — Census API dataset discovery

- **Census helpers**
    - `summary_files()` — List available decennial summary files
    - `get_pop_groups()` — Population groups for DHC-A

- **Reference datasets** (`pypums.datasets`)
    - `fips_codes` — State/county FIPS lookup table
    - `lookup_fips()` / `lookup_name()` — FIPS code resolution
    - `mig_recodes` — Migration flow labels
    - `pums_variables()` — PUMS variable dictionary
    - `acs5_geography()` — Available ACS5 geographies

- **Geography system** — Hierarchical query building for 20+ geography levels

- **Caching system** — Parquet-based file caching with SHA256 keys and TTL

- **CLI commands** — `pypums acs`, `pypums decennial`, `pypums variables`, `pypums estimates`, `pypums config`

### Deprecated

- `ACS` class — Use `get_acs()` and `get_pums()` instead

---

## 0.0.7 (2020-06-23)

- Fixes bug where `_check_data_folder()` would ignore the `path` parameter
- Uses `path.mkdir(..., exists_ok=True)`
- Adds 2018 to possible survey years
- First contributor! [@yonran](https://github.com/yonran)

## 0.0.6 (2020-05-23)

- Bug fixes (some URLs at the Census website didn't have `content-size`)

## 0.0.5 (2019-05-11)

- Add `.as_dataframe()` to ACS class

## 0.0.4 (2019-05-10)

- Add `.download_data()` to ACS class

## 0.0.3 (2019-05-09)

- Accidentally released

## 0.0.2 (2019-05-09)

- Add `ACS()` class for Python interface

## 0.0.1 (2019-04-29)

- First release on PyPI
