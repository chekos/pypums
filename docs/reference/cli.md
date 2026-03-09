# CLI Reference

PyPUMS provides a command-line interface for accessing Census data directly from your terminal.

## Overview

After installing PyPUMS, the `pypums` command is available:

```bash
pypums --help
pypums --version
```

## Commands

| Command | Description |
|---------|-------------|
| `pypums config` | Set your Census API key |
| `pypums acs` | Fetch ACS data from the Census API |
| `pypums decennial` | Fetch Decennial Census data |
| `pypums variables` | Search and browse Census variables |
| `pypums estimates` | Fetch population estimates |
| `pypums acs-url` | Build a URL to the Census FTP server (legacy) |
| `pypums download-acs` | Download PUMS data files (legacy) |

## Quick Examples

### Set your API key

```bash
pypums config YOUR_CENSUS_API_KEY
```

### Fetch ACS data

```bash
# State-level total population
pypums acs state -v B01003_001

# County-level median income for California
pypums acs county -v B19013_001 -s CA -y 2022

# Full table in wide format
pypums acs state -t B01001 -o wide
```

### Fetch Decennial Census data

```bash
# State-level population from 2020 Census
pypums decennial state -v P1_001N

# County-level for California
pypums decennial county -v P1_001N -s CA -y 2020
```

### Search for variables

```bash
# Search for income-related variables
pypums variables --search "median income"

# Search in a specific dataset and year
pypums variables --dataset acs1 --year 2022 --search "housing"

# Cache results for faster subsequent searches
pypums variables --search "poverty" --cache
```

### Fetch population estimates

```bash
# State-level population estimates
pypums estimates state

# County-level for Texas
pypums estimates county -s TX --vintage 2023
```

## Full Command Reference

::: mkdocs-typer
    :module: pypums.cli
    :command: cli
