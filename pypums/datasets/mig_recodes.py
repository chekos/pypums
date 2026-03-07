"""Migration flow characteristic recode labels.

Provides human-readable labels for the coded breakdown dimensions
returned by the ACS Migration Flows API (``/acs/flows``).
"""

import pandas as pd

# Migration flow recode labels by dimension.
# These map numeric codes to human-readable descriptions for the
# characteristic breakdowns available in ACS flow data.
_MIG_RECODE_DATA: dict[str, dict[str, str]] = {
    "MOTEFG": {
        "00": "Not identified",
        "01": "Metro to metro",
        "02": "Metro to micro",
        "03": "Metro to noncore",
        "04": "Micro to metro",
        "05": "Micro to micro",
        "06": "Micro to noncore",
        "07": "Noncore to metro",
        "08": "Noncore to micro",
        "09": "Noncore to noncore",
    },
    "AGE_GROUP": {
        "001": "All ages",
        "002": "1 to 4 years",
        "003": "5 to 17 years",
        "004": "18 to 24 years",
        "005": "25 to 34 years",
        "006": "35 to 44 years",
        "007": "45 to 54 years",
        "008": "55 to 64 years",
        "009": "65 to 74 years",
        "010": "75 years and over",
    },
    "RACE_GROUP": {
        "00": "All races",
        "01": "White alone",
        "02": "Black or African American alone",
        "03": "American Indian and Alaska Native alone",
        "04": "Asian alone",
        "05": "Native Hawaiian and Other Pacific Islander alone",
        "06": "Some other race alone",
        "07": "Two or more races",
    },
    "SEX_GROUP": {
        "0": "Both sexes",
        "1": "Male",
        "2": "Female",
    },
    "HISP_GROUP": {
        "0": "Both Hispanic origins",
        "1": "Non-Hispanic",
        "2": "Hispanic or Latino",
    },
}

# Flat DataFrame version for easy lookup.
_rows = []
for dimension, codes in _MIG_RECODE_DATA.items():
    for code, label in codes.items():
        _rows.append(
            {
                "dimension": dimension,
                "code": code,
                "label": label,
            }
        )

mig_recodes: pd.DataFrame = pd.DataFrame(_rows)
"""DataFrame of migration flow recode labels.

Columns: ``dimension``, ``code``, ``label``.
"""

# Also expose the raw dict for programmatic lookups.
MIG_RECODE_LABELS: dict[str, dict[str, str]] = _MIG_RECODE_DATA
