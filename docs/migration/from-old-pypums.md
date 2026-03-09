# Migrating from Old PyPUMS

If you used PyPUMS before version 0.2, you were working with the `ACS` class and FTP-based data downloads. The library has been completely reworked to use the Census API directly, with a function-based interface that matches the R tidycensus workflow.

## What Changed

| Old PyPUMS (< 0.2) | New PyPUMS (0.2+) |
|--------------------|--------------------|
| `ACS()` class | `get_acs()`, `get_pums()` functions |
| FTP file downloads | Direct Census API queries |
| Person-level CSV files | API returns JSON, converted to DataFrame |
| Manual data management | Built-in caching |
| 2 CLI commands | 5+ CLI commands |
| PUMS data only | ACS, Decennial, Estimates, Flows, PUMS |

## Migration Examples

### Before: ACS class

```python
# Old way (deprecated)
from pypums import ACS

ca_2022 = ACS(year=2022, state="California")
ca_2022.download(data_directory="./data/")
df = ca_2022.as_dataframe()
```

### After: get_acs() for summary data

```python
# New way: summary statistics from the API
import pypums

df = pypums.get_acs(
    geography="county",
    variables=["B19013_001"],
    state="CA",
    year=2022,
)
```

### After: get_pums() for microdata

```python
# New way: PUMS microdata from the API
import pypums

pums = pypums.get_pums(
    variables=["AGEP", "SEX", "WAGP"],
    state="CA",
    year=2022,
    recode=True,
)
```

## CLI Changes

### Before

```bash
# Old commands (still available but deprecated)
pypums acs-url --year 2022 --state california
pypums download-acs --year 2022 --state california
```

### After

```bash
# New commands
pypums config YOUR_API_KEY
pypums acs county -v B19013_001 -s CA -y 2022
pypums decennial state -v P1_001N
pypums variables --search "median income"
pypums estimates state -s CA
```

## Why the Change?

1. **No more large file downloads** — The Census API returns exactly the data you need, not gigabyte-sized CSV files
2. **More data sources** — Access ACS summary tables, Decennial Census, population estimates, and migration flows in addition to PUMS microdata
3. **Geometry support** — Get GeoDataFrames with TIGER/Line boundaries in a single call
4. **Feature parity with tidycensus** — If you can do it in R with tidycensus, you can now do it in Python with PyPUMS

## The ACS Class Still Works (For Now)

The `ACS` class is deprecated but not removed. You'll see a deprecation warning when you use it. We recommend migrating to the new functions, which are more powerful and don't require downloading files.

```python
# This still works but will show a deprecation warning
from pypums import ACS
```
