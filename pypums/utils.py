"""Utility functions."""
import io
from pathlib import Path
from zipfile import ZipFile

import httpx
import pandas as pd
import rich.progress
import us
from rich import print
from typer import get_app_dir

from . import __app_name__

app_dir = Path(get_app_dir(__app_name__))
data_dir = app_dir.joinpath("data")
data_dir.mkdir(parents = True)

SURVEYS_BASE_URL = "https://www2.census.gov/programs-surveys/"

ONE_OR_THREE_YEARS = list(range(2000, 2009))
ONE_THREE_FIVE_YEARS = list(range(2009, 2014))
ONE_OR_FIVE = list(range(2014, 2020))


def _clean_year(year: int) -> int:
    if (year >= 0) & (year <= 19):
        year += 2000

    if not (year >= 2000) & (year <= 2019):
        raise ValueError("Year must be between 2000 and 2018.")
    return year


def _ONE_THREE_OR_FIVE_YEAR(_survey: str, _year: int) -> str:
    """
    Fixes URL part for survey. Some years don't have 3-Year surveys.
    If year <= 2006, _survey == ''.
    From 2007-2008, _survey can be either 1 or 3 years.
    From 2009-2013, _survey can be either 1, 3, or 5 years.
    From 2013 onward, only 1 or 5 years.
    """
    _survey = _survey.title()
    if _year <= 2006:
        if _survey != "1-Year":
            print("Prior to 2007, only 1-Year ACS are available, defaulting to 1-Year")
        return ""
    elif _year >= 2007 and _year <= 2008:
        if _survey == "5-Year":
            print(f"There is no 5-Year ACS for {_year}, defaulting to 3-Year")
            return "3-Year/"
    elif _year >= 2014:
        if _survey == "3-Year":
            print(f"There is no 3-Year ACS for {_year}, defaulting to 5-Year")
            return "5-Year/"
    return f"{_survey}/"


def _check_data_dirs(data_directory: data_dir) -> Path:
    """
    Validates data directory exists. If it doesn't exists, it creates it and creates 'raw/' and 'interim/' directories.
    """
    # set directory's values
    _raw_data_directory = data_directory.joinpath("raw/")
    _interim_data_directory = data_directory.joinpath("interim/")

    # make sure they exists
    if not data_directory.exists():
        data_directory.mkdir()
    if not _raw_data_directory.exists():
        _raw_data_directory.mkdir()
    if not _interim_data_directory.exists():
        _interim_data_directory.mkdir()

    return data_directory


def _extract_data(downloaded_file: Path, extract_dir: Path):
    """Extract survey data downloaded from Census server."""
    *_, survey_year, _ = downloaded_file.parts
    state = downloaded_file.stem[-2:]

    full_extract_dir_path = extract_dir.joinpath(survey_year)
    if not full_extract_dir_path.exists():
        full_extract_dir_path.mkdir()
    full_extract_path = full_extract_dir_path.joinpath(state)
    if not full_extract_path.exists():
        full_extract_path.mkdir()
    CONTENT_FILE = ZipFile(downloaded_file)

    for file in rich.progress.track(
        CONTENT_FILE.filelist,
        description="Extracting...",
    ):
        CONTENT_FILE.extract(file, str(full_extract_path))

    print(f"Files extracted successfully at [magenta]{full_extract_path}[/magenta]")


def _download_data(
    url: str,
    name: str,
    data_directory: data_dir,
    extract: bool = True,
) -> None:
    """
    Downloads a file from Census FTP server.
    """

    data_directory = _check_data_dirs(data_directory=data_directory)
    _download_path = data_directory.joinpath("raw/")
    _extract_path = data_directory.joinpath("interim/")

    *_, year, _, _filename = url.split("/")
    year = year[-2:]
    _survey_dir = _download_path.joinpath(f"{name}_{year}/")

    if not _survey_dir.exists():
        _survey_dir.mkdir()

    _full_download_path = _survey_dir.joinpath(_filename)

    with open(_full_download_path, "wb") as file:
        with httpx.stream("GET", url) as response:
            total = int(response.headers["Content-Length"])

            with rich.progress.Progress(
                "[progress.percentage]{task.percentage:>3.0f}%",
                rich.progress.BarColumn(bar_width=None),
                rich.progress.DownloadColumn(),
                rich.progress.TransferSpeedColumn(),
            ) as progress:
                download_task = progress.add_task("Download", total=total)
                for chunk in response.iter_bytes():
                    file.write(chunk)
                    progress.update(
                        download_task, completed=response.num_bytes_downloaded
                    )
            print(
                f"File downloaded successfully at [magenta]{_full_download_path}[/magenta]"
            )

    if extract:
        _extract_data(_full_download_path, _extract_path)


def _download_as_dataframe(URL: str) -> pd.DataFrame:
    """Downloads zip file from URL containing one CSV file and returns it as a pandas.DataFrame

    Parameters
    ----------
    URL : str
        URL to retrieve zip file from

    Returns
    -------
    pd.DataFrame
        DataFrame containing data from CSV
    """
    _GET_DATA_REQUEST = httpx.get(URL)

    with ZipFile(io.BytesIO(_GET_DATA_REQUEST.content)) as thezip:
        csv_files = [
            file for file in thezip.infolist() if file.filename.endswith(".csv")
        ]
        # should be only 1
        assert len(csv_files) == 1
        with thezip.open(csv_files[0]) as thefile:
            data = pd.read_csv(thefile)
    return data


def build_acs_url(
    year: int = 2018,
    survey: str = "1-year",
    sample_unit: str = "person",
    state: str = "California",
) -> str:
    """Builds Census FTP server URL where you can download ACS 1-, 3-, or 5-year estimates.

    Parameters
    ----------
    year : int, optional
        Year of survey, by default 2018
    survey : str, optional
        One of '1-year', '3-year', or '5-year', by default '1-year'
    sample_unit : str, optional
        Person-level or Household-level estimates, by default 'person'
    state : str, optional
        Name or abbreviation of state, by default 'California'

    Returns
    -------
    str
        URL to retrieve data from.
    """

    BASE_URL = SURVEYS_BASE_URL + "acs/data/pums/"
    UNIT = sample_unit[0].lower()
    STATE_ABBR = us.states.lookup(state).abbr.lower()

    if "5" in survey:
        SURVEY = "5-Year"
    elif "3" in survey:
        SURVEY = "3-Year"
    else:
        SURVEY = "1-Year"

    YEAR = _clean_year(year)

    SURVEY = f"{_ONE_THREE_OR_FIVE_YEAR(SURVEY, YEAR)}"

    SURVEY_URL = f"{BASE_URL}{YEAR}/{SURVEY}csv_{UNIT}{STATE_ABBR}.zip"
    return SURVEY_URL
