# Coming from Census FTP Downloads

If you've been downloading PUMS CSV files directly from the Census Bureau's FTP server, PyPUMS can simplify your workflow significantly.

## The Old Way

Typical workflow for getting PUMS data from the FTP server:

1. Navigate to `https://www2.census.gov/programs-surveys/acs/data/pums/`
2. Find the right year and survey type directory
3. Download the correct ZIP file (often 500 MB - 2 GB)
4. Extract the CSV files
5. Load into pandas (slow for large files)
6. Filter to your state/variables of interest
7. Manually manage replicate weight columns
8. Hope you got the right file

## The New Way

PyPUMS queries the Census API directly, which means:

- **Server-side filtering** — Only download the variables and states you need
- **No file management** — No ZIP files, no extraction, no disk space concerns
- **Instant results** — API responses are fast for targeted queries
- **Built-in caching** — Cache results locally for repeated access

### Before: Manual FTP download

```python
import pandas as pd

# Download the ~1 GB CSV file, wait 10 minutes...
df = pd.read_csv(
    "csv_pca.csv",
    usecols=["SERIALNO", "SPORDER", "PWGTP", "ST", "PUMA", "AGEP", "SEX", "WAGP"],
    dtype=str,
)

# Filter to California
df = df[df["ST"] == "06"]

# Convert numeric columns
df["AGEP"] = pd.to_numeric(df["AGEP"])
df["WAGP"] = pd.to_numeric(df["WAGP"])
df["PWGTP"] = pd.to_numeric(df["PWGTP"])
```

### After: PyPUMS API query

```python
import pypums

df = pypums.get_pums(
    variables=["AGEP", "SEX", "WAGP"],
    state="CA",
    year=2022,
    recode=True,
)
# Done. Filtered, typed, and labeled.
```

## Feature Comparison

| Feature | FTP Download | PyPUMS |
|---------|-------------|---------|
| **Download size** | 500 MB - 2 GB per file | Only requested variables |
| **Filtering** | After download (client-side) | Before download (server-side) |
| **Variable selection** | Load all, then filter columns | Request only what you need |
| **State filtering** | Download national file, filter rows | API returns only your state |
| **Data types** | Manual conversion | Automatic numeric conversion |
| **Replicate weights** | Manually manage 80 columns | `rep_weights="person"` |
| **Value labels** | Manual recode using data dictionary | `recode=True` |
| **Survey design** | Manual SDR calculation | `to_survey()` helper |
| **Caching** | Manage files yourself | Built-in with TTL |
| **Summary tables** | Not available (PUMS only) | `get_acs()` for pre-tabulated data |
| **Geometry** | Separate TIGER/Line download | `geometry=True` parameter |

## When You Still Need FTP

The Census API has some limitations compared to raw FTP files:

- **Very large queries** — If you need all variables for all states, the FTP file may be faster
- **Historical data** — Some older years may not be available via the API
- **Custom file processing** — If you need the raw CSV format for a specific pipeline

For these cases, the legacy `pypums download-acs` CLI command still works:

```bash
pypums download-acs --year 2022 --state california --survey 1-year
```

## Replicate Weights

Getting replicate weights is much simpler with the API:

```python
# Automatically includes PWGTP1 through PWGTP80
pums = pypums.get_pums(
    variables=["AGEP", "WAGP"],
    state="CA",
    year=2022,
    rep_weights="person",
)

# Convert to survey design object
design = pypums.to_survey(pums)

# Compute weighted estimate with standard error
estimate = design.weighted_estimate("WAGP")
se = design.standard_error("WAGP")
```
