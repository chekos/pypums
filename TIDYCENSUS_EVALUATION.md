# tidycensus Evaluation & pypums Implementation Plan

## 1. tidycensus Feature Inventory

### 1.1 Core Data Retrieval Functions

| Function | Description | Census API Endpoint | Priority |
|----------|-------------|---------------------|----------|
| `get_acs()` | ACS aggregate data (1yr/5yr) by geography | `/data/{year}/acs/acs{1,5}` | P0 |
| `get_decennial()` | Decennial Census data (2000/2010/2020) | `/data/{year}/dec/{sumfile}` | P0 |
| `get_pums()` | PUMS microdata via API with filtering | `/data/{year}/acs/acs{1,5}/pums` | P1 |
| `get_estimates()` | Population Estimates Program | `/data/{vintage}/pep/...` | P1 |
| `get_flows()` | ACS Migration Flows | `/data/{year}/acs/flows` | P2 |

### 1.2 Variable Discovery

| Function | Description | Priority |
|----------|-------------|----------|
| `load_variables()` | Search/browse Census variable dictionaries | P0 |
| `summary_files()` | List available summary files for a year | P2 |

### 1.3 API Key Management

| Function | Description | Priority |
|----------|-------------|----------|
| `census_api_key()` | Store/retrieve API key in env or config | P0 |

### 1.4 Margin of Error Utilities

| Function | Description | Priority |
|----------|-------------|----------|
| `moe_sum()` | MOE for derived sums | P1 |
| `moe_prop()` | MOE for derived proportions | P1 |
| `moe_ratio()` | MOE for derived ratios | P1 |
| `moe_product()` | MOE for derived products | P1 |
| `significance()` | Statistical significance of estimate diffs | P1 |

### 1.5 Spatial/Geometry

| Function | Description | Priority |
|----------|-------------|----------|
| `geometry=True` param | Return GeoDataFrame with TIGER/Line shapes | P1 |
| `as_dot_density()` | Convert polygons to dot-density points | P2 |
| `interpolate_pw()` | Population-weighted areal interpolation | P3 |

### 1.6 PUMS Utilities

| Function | Description | Priority |
|----------|-------------|----------|
| `to_survey()` | Convert PUMS DataFrame to survey design object | P2 |
| `recode` param | Auto-label coded PUMS values | P1 |
| `variables_filter` | Server-side PUMS filtering | P1 |
| `rep_weights` param | Include replicate weights | P1 |

### 1.7 Built-in Datasets

| Dataset | Description | Priority |
|---------|-------------|----------|
| `fips_codes` | FIPS codes for all US states/counties | P0 |
| `pums_variables` | PUMS variable dictionary with labels | P1 |
| `mig_recodes` | Migration flow characteristic recodes | P2 |
| `state_laea` / `county_laea` | Shifted AK/HI geometry | P3 |
| `acs5_geography` | Geography availability in ACS 5yr | P1 |

### 1.8 Miscellaneous

| Function | Description | Priority |
|----------|-------------|----------|
| `get_pop_groups()` | Available population groups for decennial | P2 |
| `check_ddhca_groups()` | Check geography/pop group availability in DHC-A | P3 |

---

## 2. Current pypums Capabilities (What Exists)

- **ACS PUMS download via FTP** — downloads zip files from `census.gov/programs-surveys/acs/data/pums/`
- **URL builder** — constructs FTP URLs for 1yr/3yr/5yr ACS PUMS (2000-2024)
- **DataFrame loading** — reads downloaded CSVs into pandas
- **CLI** — `acs_url` and `download_acs` commands via typer
- **State lookup** — uses `us` package for state name/abbreviation resolution
- **Data caching** — basic: checks if zip file already downloaded

### What Does NOT Exist

- No Census API integration (everything uses FTP)
- No API key management
- No variable search/discovery
- No aggregate data (get_acs/get_decennial — only PUMS microdata)
- No geography hierarchy support (only state-level PUMS)
- No spatial/geometry support
- No margin of error functions
- No tidy/wide output format options
- No population estimates or migration flows
- No survey weighting
- No data dictionaries/reference datasets

---

## 3. Proposed Module Architecture

```
pypums/
├── __init__.py              # Public API exports (expanded)
├── __main__.py              # CLI entry point (unchanged)
├── constants.py             # App constants, URLs (expanded)
├── cli.py                   # Typer CLI (expanded with new commands)
├── surveys.py               # Existing ACS dataclass (kept for backward compat)
│
├── api/                     # NEW — Census API integration
│   ├── __init__.py
│   ├── client.py            # Census API HTTP client (httpx-based)
│   ├── key.py               # API key management (env vars, config file)
│   └── geography.py         # Geography hierarchy definitions & validation
│
├── acs.py                   # NEW — get_acs() function
├── decennial.py             # NEW — get_decennial() function
├── pums.py                  # NEW — get_pums() via API (enhances existing)
├── estimates.py             # NEW — get_estimates() function
├── flows.py                 # NEW — get_flows() function
├── variables.py             # NEW — load_variables() function
│
├── moe.py                   # NEW — Margin of error utilities
├── spatial.py               # NEW — Geometry/spatial support (optional geopandas)
│
├── datasets/                # NEW — Built-in reference data
│   ├── __init__.py
│   ├── fips.py              # fips_codes dataset
│   ├── pums_vars.py         # pums_variables dataset
│   └── data/                # Bundled CSV/JSON data files
│       ├── fips_codes.csv
│       └── acs5_geography.json
│
├── cache.py                 # NEW — Local caching layer
└── utils.py                 # Existing utilities (preserved + extended)
```

---

## 4. Detailed Function Signatures

### 4.1 API Key Management

```python
# pypums/api/key.py

def census_api_key(
    key: str | None = None,
    *,
    install: bool = False,
    overwrite: bool = False,
) -> str:
    """Get, set, or install a Census API key.

    - No args: returns current key from env/config
    - key provided: sets for current session (os.environ)
    - install=True: persists to ~/.pypums/config.toml
    """
```

### 4.2 get_acs()

```python
# pypums/acs.py

def get_acs(
    geography: str,
    variables: str | list[str] | None = None,
    table: str | None = None,
    *,
    year: int = 2023,
    survey: str = "acs5",
    state: str | list[str] | None = None,
    county: str | list[str] | None = None,
    zcta: str | list[str] | None = None,
    output: str = "tidy",
    geometry: bool = False,
    keep_geo_vars: bool = False,
    summary_var: str | None = None,
    moe_level: int = 90,
    cache_table: bool = False,
    show_call: bool = False,
    key: str | None = None,
) -> pd.DataFrame:
    """Obtain ACS data and optionally geometry.

    Returns DataFrame with columns:
    - GEOID, NAME, variable, estimate, moe (tidy)
    - GEOID, NAME, {var1}E, {var1}M, ... (wide)

    If geometry=True, returns GeoDataFrame with geometry column.
    """
```

### 4.3 get_decennial()

```python
# pypums/decennial.py

def get_decennial(
    geography: str,
    variables: str | list[str] | None = None,
    table: str | None = None,
    *,
    year: int = 2020,
    sumfile: str | None = None,
    state: str | list[str] | None = None,
    county: str | list[str] | None = None,
    output: str = "tidy",
    geometry: bool = False,
    keep_geo_vars: bool = False,
    summary_var: str | None = None,
    pop_group: str | None = None,
    pop_group_label: bool = False,
    cache_table: bool = False,
    show_call: bool = False,
    key: str | None = None,
) -> pd.DataFrame:
    """Obtain decennial Census data and optionally geometry.

    Returns DataFrame with columns:
    - GEOID, NAME, variable, value (tidy)
    - GEOID, NAME, {var1}, {var2}, ... (wide)
    """
```

### 4.4 get_pums()

```python
# pypums/pums.py

def get_pums(
    variables: str | list[str] | None = None,
    *,
    state: str | list[str] | None = None,
    puma: str | list[str] | None = None,
    year: int = 2023,
    survey: str = "acs5",
    variables_filter: dict[str, list | int | str] | None = None,
    rep_weights: str | None = None,  # "person", "housing", or "both"
    recode: bool = False,
    return_vacant: bool = False,
    show_call: bool = False,
    key: str | None = None,
) -> pd.DataFrame:
    """Load PUMS microdata from the Census API.

    Enhanced version of existing FTP download approach.
    Supports server-side filtering, recoding, and replicate weights.
    """
```

### 4.5 get_estimates()

```python
# pypums/estimates.py

def get_estimates(
    geography: str,
    *,
    product: str | None = None,  # "population", "components", "housing", "characteristics"
    variables: str | list[str] | None = None,
    breakdown: str | list[str] | None = None,
    breakdown_labels: bool = False,
    vintage: int = 2023,
    year: int | None = None,
    state: str | list[str] | None = None,
    county: str | list[str] | None = None,
    time_series: bool = False,
    output: str = "tidy",
    geometry: bool = False,
    keep_geo_vars: bool = False,
    show_call: bool = False,
    key: str | None = None,
) -> pd.DataFrame:
    """Get Census Bureau Population Estimates Program data."""
```

### 4.6 get_flows()

```python
# pypums/flows.py

def get_flows(
    geography: str,
    *,
    variables: str | list[str] | None = None,
    breakdown: str | list[str] | None = None,
    breakdown_labels: bool = False,
    year: int = 2019,
    output: str = "tidy",
    state: str | list[str] | None = None,
    county: str | list[str] | None = None,
    msa: str | None = None,
    geometry: bool = False,
    moe_level: int = 90,
    show_call: bool = False,
    key: str | None = None,
) -> pd.DataFrame:
    """Obtain ACS Migration Flows data."""
```

### 4.7 load_variables()

```python
# pypums/variables.py

def load_variables(
    year: int = 2023,
    dataset: str = "acs5",
    *,
    cache: bool = False,
) -> pd.DataFrame:
    """Load Census variables for searching.

    Returns DataFrame with columns: name, label, concept, geography.

    dataset options:
    - ACS: "acs1", "acs5", "acs1/subject", "acs5/subject",
            "acs1/profile", "acs5/profile"
    - Decennial: "pl", "dhc", "dp", "sf1", "sf2", "sf3"
    - PUMS: "acs1/pums", "acs5/pums"
    """
```

### 4.8 Margin of Error Functions

```python
# pypums/moe.py

def moe_sum(
    moe: float | np.ndarray | pd.Series,
    estimate: float | np.ndarray | pd.Series = 0,
    *,
    na_rm: bool = False,
) -> float | np.ndarray:
    """Calculate MOE for a derived sum.

    Formula: sqrt(sum(moe^2))
    """

def moe_prop(
    num: float,
    denom: float,
    moe_num: float,
    moe_denom: float,
) -> float:
    """Calculate MOE for a derived proportion.

    Formula: sqrt(moe_num^2 - (num/denom)^2 * moe_denom^2) / denom
    Uses moe_ratio as fallback when result would be imaginary.
    """

def moe_ratio(
    num: float,
    denom: float,
    moe_num: float,
    moe_denom: float,
) -> float:
    """Calculate MOE for a derived ratio.

    Formula: sqrt(moe_num^2 + (num/denom)^2 * moe_denom^2) / denom
    """

def moe_product(
    est1: float,
    est2: float,
    moe1: float,
    moe2: float,
) -> float:
    """Calculate MOE for a derived product.

    Formula: sqrt(est1^2 * moe2^2 + est2^2 * moe1^2)
    """

def significance(
    est1: float,
    est2: float,
    moe1: float,
    moe2: float,
    *,
    clevel: float = 0.90,
) -> bool:
    """Test statistical significance of difference between estimates.

    Returns True if difference is statistically significant at clevel.
    Formula: |est1 - est2| > z * sqrt(moe1_se^2 + moe2_se^2)
    """
```

---

## 5. Census API Integration Design

### 5.1 API Client

```python
# pypums/api/client.py

class CensusAPIClient:
    """Thin wrapper around Census Bureau REST API.

    Base URL: https://api.census.gov/data/

    Responsibilities:
    - Construct API URLs from dataset, year, variables, geography
    - Handle API key injection
    - Parse JSON responses into DataFrames
    - Rate limiting and retry logic
    - show_call debugging support
    """

    BASE_URL = "https://api.census.gov/data"

    def __init__(self, key: str | None = None):
        self.key = key or get_census_api_key()
        self._client = httpx.Client(timeout=30.0)

    def get(
        self,
        dataset: str,           # e.g. "2023/acs/acs5"
        variables: list[str],   # e.g. ["B01001_001E", "NAME"]
        geography: str,         # e.g. "county:*"
        *,
        within: str | None = None,  # e.g. "state:06"
        show_call: bool = False,
    ) -> pd.DataFrame:
        """Execute Census API query and return DataFrame."""
```

### 5.2 Geography Handling

```python
# pypums/api/geography.py

GEOGRAPHY_HIERARCHY = {
    "us": {"fips": "us:1", "requires": []},
    "region": {"fips": "region:*", "requires": []},
    "division": {"fips": "division:*", "requires": []},
    "state": {"fips": "state:*", "requires": []},
    "county": {"fips": "county:*", "requires": ["state"]},
    "county subdivision": {"fips": "county subdivision:*", "requires": ["state", "county"]},
    "tract": {"fips": "tract:*", "requires": ["state", "county"]},
    "block group": {"fips": "block group:*", "requires": ["state", "county", "tract"]},
    "block": {"fips": "block:*", "requires": ["state", "county", "tract"]},
    "place": {"fips": "place:*", "requires": ["state"]},
    "congressional district": {"fips": "congressional district:*", "requires": ["state"]},
    "state legislative district (upper)": {"fips": "state legislative district (upper chamber):*", "requires": ["state"]},
    "state legislative district (lower)": {"fips": "state legislative district (lower chamber):*", "requires": ["state"]},
    "zcta": {"fips": "zip code tabulation area:*", "requires": []},
    "school district (unified)": {"fips": "school district (unified):*", "requires": ["state"]},
    "school district (elementary)": {"fips": "school district (elementary):*", "requires": ["state"]},
    "school district (secondary)": {"fips": "school district (secondary):*", "requires": ["state"]},
    "cbsa": {"fips": "metropolitan statistical area/micropolitan statistical area:*", "requires": []},
    "csa": {"fips": "combined statistical area:*", "requires": []},
    "puma": {"fips": "public use microdata area:*", "requires": ["state"]},
    "american indian area/alaska native area/hawaiian home land": {"fips": "american indian area/alaska native area/hawaiian home land:*", "requires": []},
}

def build_geography_query(
    geography: str,
    state: str | None = None,
    county: str | None = None,
) -> tuple[str, str | None]:
    """Convert geography + state/county to Census API 'for' and 'in' params."""
```

### 5.3 Spatial Integration

```python
# pypums/spatial.py

def attach_geometry(
    df: pd.DataFrame,
    geography: str,
    *,
    state: str | None = None,
    county: str | None = None,
    year: int = 2023,
    cb: bool = True,          # cartographic boundary (smaller files)
    keep_geo_vars: bool = False,
    resolution: str = "500k",  # "500k", "5m", "20m"
) -> "gpd.GeoDataFrame":
    """Fetch TIGER/Line shapefiles and merge with Census data.

    Downloads shapefiles from:
    https://www2.census.gov/geo/tiger/GENZ{year}/shp/

    Requires geopandas (optional dependency).
    """

def as_dot_density(
    gdf: "gpd.GeoDataFrame",
    values: dict[str, str],  # {column: label}
    *,
    dots_per_value: int = 100,
    seed: int | None = None,
) -> "gpd.GeoDataFrame":
    """Convert polygon GeoDataFrame to dot-density points."""
```

---

## 6. Caching Strategy

```python
# pypums/cache.py

class CensusCache:
    """File-based caching for Census API responses and variable tables.

    Cache location: ~/.pypums/cache/
    Structure:
        cache/
        ├── variables/           # load_variables() results
        │   ├── 2023_acs5.parquet
        │   └── 2020_pl.parquet
        ├── api/                 # API response cache (keyed by URL hash)
        │   └── {url_hash}.parquet
        └── tiger/               # TIGER/Line shapefiles
            └── {year}/{geo_type}/

    TTL: Variable tables cached indefinitely (historical data doesn't change)
         API responses: 24h default, configurable
         Shapefiles: cached indefinitely per year
    """
```

---

## 7. Phased Implementation Plan

### Phase 0: Foundation (API Infrastructure) — Week 1-2
**Goal:** Build the Census API client and core infrastructure that all features depend on.

1. **`pypums/api/key.py`** — API key management
   - `census_api_key()`: get/set/install API key
   - Support `CENSUS_API_KEY` env var + `~/.pypums/config.toml`
   - Key validation via test API call

2. **`pypums/api/client.py`** — Census API HTTP client
   - Build on existing `httpx` dependency
   - URL construction, request execution, JSON→DataFrame parsing
   - Error handling (invalid key, rate limits, invalid variables)
   - `show_call` debug support
   - Retry logic with exponential backoff

3. **`pypums/api/geography.py`** — Geography definitions
   - Full geography hierarchy mapping (25+ levels)
   - `build_geography_query()` for API `for`/`in` params
   - Geography validation (e.g., county requires state)
   - FIPS code resolution from state/county names

4. **`pypums/cache.py`** — Caching layer
   - File-based cache using parquet format
   - Cache key generation from request parameters
   - TTL-based expiration
   - Cache clear/manage utilities

5. **`pypums/datasets/fips.py`** — FIPS codes dataset
   - Bundle `fips_codes` reference data
   - State/county name ↔ FIPS lookups

6. **Update `pyproject.toml`**
   - Add `[project.optional-dependencies] spatial = ["geopandas>=0.12"]`
   - Update description

### Phase 1: Core Data Functions — Week 3-5
**Goal:** Implement the two most-used functions.

7. **`pypums/acs.py`** — `get_acs()`
   - All parameters from tidycensus signature
   - Tidy (long) and wide output formats
   - Automatic E/M suffix handling for estimates and MOE
   - `summary_var` support
   - `moe_level` scaling (90/95/99)
   - Table-based requests (all variables from a table)
   - Multi-state requests (loop and combine)

8. **`pypums/decennial.py`** — `get_decennial()`
   - Support for 2000, 2010, 2020 Census years
   - Summary file selection (pl, dhc, dp, sf1, sf2, sf3, sf4)
   - Population group parameters
   - Tidy/wide output

9. **`pypums/variables.py`** — `load_variables()`
   - Fetch variable metadata from Census API
   - Support all dataset types (ACS, decennial, subject, profile, PUMS)
   - Local caching of variable tables
   - Return searchable DataFrame (name, label, concept)

10. **Update `pypums/__init__.py`**
    - Export: `get_acs`, `get_decennial`, `load_variables`, `census_api_key`

### Phase 2: MOE + Spatial + Enhanced PUMS — Week 6-8
**Goal:** Add statistical and spatial capabilities.

11. **`pypums/moe.py`** — Margin of error functions
    - `moe_sum()`, `moe_prop()`, `moe_ratio()`, `moe_product()`
    - `significance()` function
    - Vectorized operations (work with Series/arrays)
    - Handle edge cases (zero denominators, negative radicands)

12. **`pypums/spatial.py`** — Geometry support
    - `attach_geometry()`: download and merge TIGER/Line shapefiles
    - Support cartographic boundary files (cb=True) and TIGER/Line (cb=False)
    - Integrate with `get_acs()` and `get_decennial()` via `geometry=True`
    - CRS handling (default NAD83/EPSG:4269)
    - Graceful import error if geopandas not installed

13. **`pypums/pums.py`** — `get_pums()` via Census API
    - Server-side variable filtering (`variables_filter`)
    - Variable recoding with `*_label` columns
    - Replicate weight handling
    - Multi-state PUMA requests
    - Keep existing FTP-based `ACS` class for backward compat

14. **`pypums/datasets/pums_vars.py`** — PUMS variable dictionary
    - Bundle PUMS variables reference data
    - Searchable by variable name, label, concept

15. **`pypums/datasets/__init__.py`** — `acs5_geography` dataset
    - Geography availability reference for ACS 5-year tables

### Phase 3: Estimates, Flows, Survey — Week 9-11
**Goal:** Complete the feature set.

16. **`pypums/estimates.py`** — `get_estimates()`
    - Population estimates products (population, components, housing, characteristics)
    - Breakdown parameters (AGEGROUP, RACE, SEX, HISP)
    - Time series support
    - Vintage vs year handling

17. **`pypums/flows.py`** — `get_flows()`
    - Migration flows data (MOVEDIN, MOVEDOUT, MOVEDNET)
    - County-to-county and MSA-to-MSA flows
    - Breakdown parameters
    - Geometry support for flow maps

18. **`pypums/datasets/mig_recodes.py`** — Migration recodes dataset

19. **`pypums/survey.py`** — `to_survey()`
    - Convert PUMS DataFrame to weighted survey design
    - Integrate with `samplics` or implement custom survey stats
    - Support for replicate weight standard errors

20. **`pypums/spatial.py`** — Additional spatial utilities
    - `as_dot_density()`: polygon → dot density conversion
    - `interpolate_pw()`: population-weighted areal interpolation (P3)

### Phase 4: CLI + Polish — Week 12
**Goal:** Expose new features via CLI and finalize.

21. **Update `pypums/cli.py`**
    - `pypums config set-key` — set Census API key
    - `pypums acs` — fetch ACS data
    - `pypums decennial` — fetch decennial data
    - `pypums variables` — search variables
    - `pypums estimates` — fetch estimates
    - Keep existing `acs_url` and `download_acs` commands

22. **Comprehensive tests**
    - Unit tests with mocked API responses
    - Integration tests (optional, with real API key)
    - Test geography hierarchy validation
    - Test MOE calculations against known values

23. **Documentation**
    - Update mkdocs site
    - Add usage examples/tutorials

---

## 8. Key Design Decisions

### 8.1 Functional API (not class-based)
tidycensus uses standalone functions (`get_acs()`, `get_decennial()`, etc.), not OOP.
pypums should follow the same pattern for the new API features. The existing `ACS`
dataclass is preserved for backward compatibility but new features use functions.

### 8.2 Census API as Primary, FTP as Legacy
New features use the Census API (`api.census.gov`). The existing FTP-based PUMS
download stays but is considered the legacy path. `get_pums()` provides the modern
API-based alternative.

### 8.3 DataFrame-First Returns
All functions return `pd.DataFrame` (or `gpd.GeoDataFrame` with `geometry=True`).
This is Pythonic and matches the pandas ecosystem.

### 8.4 Optional Dependencies
- `geopandas` — only required for `geometry=True` features
- Core functionality works with just the existing dependencies
- Install via: `pip install pypums[spatial]`

### 8.5 Variable Naming
- Python snake_case throughout (already the case)
- Geography values use lowercase with spaces: `"block group"`, `"congressional district"`
- Survey identifiers: `"acs1"`, `"acs5"` (not `"1-Year"` for API functions)

### 8.6 Backward Compatibility
- Existing `ACS` class, `build_acs_url()`, CLI commands all preserved
- New functions added alongside, not replacing existing code
- `pypums.ACS` continues to work for FTP-based PUMS downloads

---

## 9. Testing Approach

### Unit Tests (no network)
- Mock Census API responses with `httpx`'s mock transport
- Test URL construction, geography validation, DataFrame formatting
- Test MOE calculations against hand-verified values
- Test caching logic
- Test FIPS code lookups

### Integration Tests (optional, requires API key)
- Mark with `@pytest.mark.integration`
- Skip if no API key available (`CENSUS_API_KEY` env var)
- Test real API calls for each function
- Verify response schema matches expectations

### Fixture Data
- Bundle small sample API responses as JSON fixtures
- Use for snapshot testing of DataFrame output

---

## 10. Dependencies Summary

### Required (existing)
- `httpx` — HTTP client (Census API + FTP downloads)
- `pandas` — DataFrame operations
- `us` — State FIPS lookups
- `rich` — Progress bars, pretty printing
- `typer` — CLI framework

### Optional (new)
- `geopandas>=0.12` — Spatial features (`pip install pypums[spatial]`)

### Dev/Test (existing)
- `pytest` — Testing
- `mkdocs` — Documentation

---

## 11. Feature Parity Checklist

| tidycensus Feature | pypums Equivalent | Phase | Status |
|---|---|---|---|
| `census_api_key()` | `census_api_key()` | 0 | Done |
| `get_acs()` | `get_acs()` | 1 | Done |
| `get_decennial()` | `get_decennial()` | 1 | Done |
| `load_variables()` | `load_variables()` | 1 | Done |
| `get_pums()` | `get_pums()` | 2 | Done |
| `get_estimates()` | `get_estimates()` | 3 | Done |
| `get_flows()` | `get_flows()` | 3 | Done |
| `moe_sum()` | `moe_sum()` | 2 | Done |
| `moe_prop()` | `moe_prop()` | 2 | Done |
| `moe_ratio()` | `moe_ratio()` | 2 | Done |
| `moe_product()` | `moe_product()` | 2 | Done |
| `significance()` | `significance()` | 2 | Done |
| `geometry=TRUE` | `geometry=True` | 2 | Done |
| `as_dot_density()` | `as_dot_density()` | 3 | Done |
| `interpolate_pw()` | `interpolate_pw()` | 3 | Done |
| `to_survey()` | `to_survey()` | 3 | Done |
| `fips_codes` | `fips_codes` | 0 | Done |
| `pums_variables` | `pums_variables()` | 2 | Done |
| `mig_recodes` | `mig_recodes` | 3 | Done |
| `state_laea` / `county_laea` | deferred | — | Low priority |
| `acs5_geography` | `acs5_geography()` | 2 | Done |
| `summary_files()` | `summary_files()` | 3 | Done |
| `get_pop_groups()` | `get_pop_groups()` | 3 | Done |
| `check_ddhca_groups()` | deferred | — | Low priority |
| `shift_geo` (deprecated) | not implementing | — | Skip |

---

## 12. Test-Driven Development Approach

All features are developed **test-first**. Failing tests have been written for every
planned feature, organized by phase. Each test file imports the not-yet-existing
module and calls its expected public API, so tests fail immediately with
`ImportError` until the module is implemented.

### Test Files by Phase

| Phase | Test File | Tests | What They Verify |
|-------|-----------|-------|-----------------|
| 0 | `tests/test_api_key.py` | 3 | `census_api_key()` set/get/env/missing |
| 0 | `tests/test_geography.py` | 5 | Geography hierarchy, validation, query building |
| 0 | `tests/test_fips.py` | 4 | `fips_codes` dataset structure and lookups |
| 0 | `tests/test_cache.py` | 4 | Cache store/retrieve, TTL, clearing |
| 1 | `tests/test_get_acs.py` | 8 | `get_acs()` return type, tidy/wide, MOE, summary_var |
| 1 | `tests/test_get_decennial.py` | 6 | `get_decennial()` return type, tidy/wide, sumfile defaults |
| 1 | `tests/test_load_variables.py` | 7 | `load_variables()` return type, columns, datasets, cache |
| 2 | `tests/test_moe.py` | 10 | `moe_sum/prop/ratio/product`, `significance` |
| 2 | `tests/test_spatial.py` | 3 | `geometry=True` GeoDataFrame, CRS, `as_dot_density` |
| 2 | `tests/test_get_pums_api.py` | 5 | `get_pums()` API, filter, recode, rep_weights |
| 3 | `tests/test_get_estimates.py` | 5 | `get_estimates()` products, breakdown, time_series |
| 3 | `tests/test_get_flows.py` | 3 | `get_flows()` columns, county-to-county |

### Running Tests by Phase

```bash
uv run pytest -m phase0      # Foundation tests only
uv run pytest -m phase1      # Core data function tests
uv run pytest -m phase2      # MOE + spatial + PUMS tests
uv run pytest -m phase3      # Estimates + flows tests
uv run pytest -m spatial      # Spatial tests only (need geopandas)
uv run pytest -m integration  # Real API tests (need CENSUS_API_KEY)
```

### Shared Fixtures

`tests/conftest.py` provides mock Census API responses for all test files:
- `fake_api_key` — a fake API key string
- `cache_dir` — a `tmp_path`-based cache directory
- `acs_api_response_tidy` — sample ACS API JSON (2 vars, 2 counties)
- `decennial_api_response` — sample Decennial JSON (2 vars, 2 states)
- `variables_api_response` — sample variables endpoint JSON
- `pums_api_response` — sample PUMS person-level records
- `estimates_api_response` — sample PEP JSON
- `flows_api_response` — sample Migration Flows JSON
