# Built-in Datasets

PyPUMS includes several reference datasets for FIPS code lookups, variable discovery, and migration flow labels.

All datasets are available from `pypums.datasets`:

```python
from pypums.datasets import (
    fips_codes,
    lookup_fips,
    lookup_name,
    mig_recodes,
    pums_variables,
    acs5_geography,
)
```

## FIPS Codes

### fips_codes

A pandas DataFrame containing FIPS codes for all US states and counties.

```python
from pypums.datasets import fips_codes

print(fips_codes.head())
```

**Columns:**

| Column | Description | Example |
|--------|-------------|---------|
| `state` | State name | California |
| `state_code` | 2-digit state FIPS | 06 |
| `county` | County name | Los Angeles County |
| `county_code` | 3-digit county FIPS | 037 |

### lookup_fips

Look up a FIPS code from a state or county name.

```python
from pypums.datasets import lookup_fips

# State FIPS code
lookup_fips(state="California")
# '06'

# State + county FIPS code
lookup_fips(state="California", county="Los Angeles County")
# '06037'
```

**Parameters:**

- `state` (str) — State name (e.g., `"California"`)
- `county` (str, optional) — County name (e.g., `"Los Angeles County"`). Requires `state`.

### lookup_name

Look up a state or county name from FIPS codes.

```python
from pypums.datasets import lookup_name

# State name from code
lookup_name(state_code="06")
# 'California'

# County name from codes
lookup_name(state_code="06", county_code="037")
# 'Los Angeles County, California'
```

**Parameters:**

- `state_code` (str) — 2-digit state FIPS (e.g., `"06"`)
- `county_code` (str, optional) — 3-digit county FIPS (e.g., `"037"`). Requires `state_code`.

---

## Migration Recodes

### mig_recodes

A reference dataset with human-readable labels for migration flow breakdown codes.

```python
from pypums.datasets import mig_recodes
```

Used internally by `get_flows(breakdown_labels=True)` to convert coded breakdown dimensions into readable labels.

---

## PUMS Variables

### pums_variables

A function that returns the PUMS variable dictionary for a given year and survey.

```python
from pypums.datasets import pums_variables

vars_df = pums_variables()
print(vars_df.head())
```

The dictionary includes variable names, labels, and data types for all PUMS variables available through the Census API.

---

## ACS Geography Reference

### acs5_geography

Returns the available geographies for the ACS 5-year survey.

```python
from pypums.datasets import acs5_geography

geo_df = acs5_geography()
print(geo_df.head())
```

This is useful for discovering which geography levels are available and what parent geographies they require.
