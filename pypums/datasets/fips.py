"""FIPS codes for all US states and counties."""

from pathlib import Path

import pandas as pd

_DATA_DIR = Path(__file__).parent / "data"

fips_codes: pd.DataFrame = pd.read_csv(_DATA_DIR / "fips_codes.csv", dtype=str)
