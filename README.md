# PyPUMS

**Python interface to the US Census Bureau API** — American Community Survey, Decennial Census, PUMS microdata, population estimates, and migration flows.

[![PyPI version](https://img.shields.io/pypi/v/pypums)](https://pypi.org/project/pypums/)
[![Python versions](https://img.shields.io/pypi/pyversions/pypums)](https://pypi.org/project/pypums/)
[![License](https://img.shields.io/github/license/chekos/pypums)](https://github.com/chekos/pypums/blob/main/LICENSE)
[![Build status](https://github.com/chekos/pypums/workflows/build/badge.svg)](https://github.com/chekos/pypums/actions?query=workflow%3Abuild)

## Quick Start

Get county-level median household income for California:

```python
import pypums

df = pypums.get_acs(
    geography="county",
    variables=["B19013_001"],
    state="CA",
    year=2023,
)
df.head()
```

Make a map with tract-level data:

```python
df = pypums.get_acs(
    geography="tract",
    variables=["B19013_001"],
    state="CA",
    county="037",
    year=2023,
    geometry=True,  # returns a GeoDataFrame
)
df.plot(column="estimate", legend=True, figsize=(12, 8))
```

Work with PUMS microdata:

```python
pums = pypums.get_pums(
    variables=["AGEP", "SEX", "WAGP"],
    state="CA",
    year=2023,
    recode=True,  # adds human-readable labels
)
pums.head()
```

## Features

- **`get_acs()`** — American Community Survey data (1-year and 5-year)
- **`get_decennial()`** — Decennial Census data (2000, 2010, 2020)
- **`get_pums()`** — PUMS microdata with replicate weight support
- **`get_estimates()`** — Population Estimates Program data
- **`get_flows()`** — ACS migration flows (county and MSA level)
- **`load_variables()`** — Search and browse Census variable codes
- **MOE functions** — `moe_sum()`, `moe_ratio()`, `moe_prop()`, `moe_product()`, `significance()`
- **Spatial support** — Attach TIGER/Line geometries, returns GeoDataFrames
- **Survey design** — `SurveyDesign` class with successive difference replication
- **Caching** — File-based caching with configurable TTL
- **CLI** — Command-line access to all data functions

## Installation

```bash
uv add pypums
```

For spatial/mapping support:

```bash
uv add "pypums[spatial]"
```

## Census API Key

You need a free Census API key. [Request one here](https://api.census.gov/data/key_signup.html), then:

```bash
export CENSUS_API_KEY="your-key-here"
```

Or set it in Python:

```python
import pypums
pypums.census_api_key("your-key-here")
```

## Documentation

Full documentation: [https://pypums.readthedocs.io](https://pypums.readthedocs.io)

## Development

To contribute to this library, first checkout the code. Then install [uv](https://docs.astral.sh/uv/) and set up the project:

```bash
cd pypums
uv sync --extra test
```

To run the tests:

```bash
uv run pytest
```

To run the linter:

```bash
uvx ruff check .
uvx ruff format --check .
```

## Citation

```
@misc{pypums,
  author = {Sergio Sanchez Zavala},
  title = {PyPUMS: Python interface to the US Census Bureau API},
  year = {2019},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/chekos/pypums}}
}
```
