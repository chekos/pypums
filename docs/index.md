# PyPUMS

**Python interface to the US Census Bureau API** — American Community Survey, Decennial Census, PUMS microdata, population estimates, and migration flows.

---

## What is PyPUMS?

PyPUMS gives you programmatic access to US Census Bureau data directly from Python. Query the Census API, get back pandas DataFrames (or GeoDataFrames with geometries), and start analyzing immediately.

```python
import pypums

# Median household income by county in California
df = pypums.get_acs(
    geography="county",
    variables=["B19013_001"],
    state="CA",
    year=2023,
)
```

## Key Features

<div class="grid cards" markdown>

-   **Five data sources**

    ---

    `get_acs()` &middot; `get_decennial()` &middot; `get_pums()` &middot; `get_estimates()` &middot; `get_flows()`

    [:octicons-arrow-right-24: Guides](guides/acs-data.md)

-   **Spatial support**

    ---

    Add `geometry=True` to any query and get a GeoDataFrame with TIGER/Line boundaries.

    [:octicons-arrow-right-24: Spatial guide](guides/spatial.md)

-   **Variable discovery**

    ---

    Browse and search thousands of Census variables with `load_variables()`.

    [:octicons-arrow-right-24: Finding variables](guides/variables.md)

-   **MOE calculations**

    ---

    Built-in margin of error functions for derived estimates, following Census Bureau formulas.

    [:octicons-arrow-right-24: MOE guide](guides/margins-of-error.md)

-   **Survey design**

    ---

    `SurveyDesign` class with replicate-weight standard errors for PUMS microdata.

    [:octicons-arrow-right-24: Survey design](guides/survey-design.md)

-   **CLI access**

    ---

    Query Census data from the command line with `pypums acs`, `pypums decennial`, and more.

    [:octicons-arrow-right-24: CLI reference](reference/cli.md)

</div>

## Quick Install

```bash
uv add pypums
```

For spatial/mapping support:

```bash
uv add "pypums[spatial]"
```

You'll need a free [Census API key](https://api.census.gov/data/key_signup.html).

[:octicons-arrow-right-24: Full installation guide](getting-started/installation.md)

## Where to Start

| I want to... | Start here |
|---|---|
| Get Census data into a DataFrame quickly | [Quick Start](getting-started/quickstart.md) |
| Figure out which dataset I need | [Census 101](getting-started/census-101.md) |
| Find the right variable codes | [Finding Variables](guides/variables.md) |
| Make a choropleth map | [Spatial Guide](guides/spatial.md) |
| Work with PUMS microdata | [PUMS Guide](guides/pums-microdata.md) |
| Migrate from R/tidycensus | [tidycensus Migration](migration/from-tidycensus.md) |
| Migrate from old PyPUMS (ACS class) | [Migration Guide](migration/from-old-pypums.md) |
| Look up a function signature | [API Reference](reference/api.md) |
