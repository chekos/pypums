from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from typer import get_app_dir

__app_name__ = "pypums"

try:
    __version__ = version(__app_name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

app_dir = Path(get_app_dir(__app_name__, force_posix=True))
data_dir = app_dir.joinpath("data")
data_dir.mkdir(parents=True, exist_ok=True)

SURVEYS_BASE_URL = "https://www2.census.gov/programs-surveys/"
ACS_PUMS_URL = SURVEYS_BASE_URL + "acs/data/pums/"
