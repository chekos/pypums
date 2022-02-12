"""Utility functions."""
import io
import us
import httpx
import pandas as pd
import rich.progress
from rich import print
from zipfile import ZipFile

from pathlib import Path


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


def _check_data_dirs(data_directory: Path = Path("../data/")) -> Path:
    """
    Validates data directory exists. If it doesn't exists, it creates it and creates 'raw/' and 'interim/' directories.
    """
    # set directory's values
    _data_directory = Path(data_directory)
    _raw_data_directory = _data_directory.joinpath("raw/")
    _interim_data_directory = _data_directory.joinpath("interim/")

    # make sure they exists
    if not _data_directory.exists():
        _data_directory.mkdir()
    if not _raw_data_directory.exists():
        _raw_data_directory.mkdir()
    if not _interim_data_directory.exists():
        _interim_data_directory.mkdir()

    return _data_directory


def _download_data(
    url: str,
    year: int,
    name: str,
    state: str,
    data_directory: Path = Path("../data/"),
    extract: bool = True,
) -> None:
    """
    Downloads a file from Census FTP server.
    """

    data_directory = _check_data_dirs(data_directory=data_directory)
    _filename = url.split("/")[-1]
    _download_path = data_directory.joinpath("raw/")
    _extract_path = data_directory.joinpath("interim/")
    _full_download_path = _download_path / _filename

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
            print("Download complete!")

    if extract:
        _year = str(year)[-2:]
        _state = us.states.lookup(state).abbr.upper()
        _extract__folder = f"{name}_{_year}/"
        _extract_path_and_folder = _extract_path.joinpath(_extract__folder)
        if not _extract_path_and_folder.exists():
            _extract_path_and_folder.mkdir()
        _full_extract_path = _extract_path_and_folder.joinpath(_state)
        if not _full_extract_path.exists():
            _full_extract_path.mkdir()
        CONTENT_FILE = ZipFile(_full_download_path)

        for file in rich.progress.track(
            CONTENT_FILE.filelist,
            description="Extracting...",
        ):
            CONTENT_FILE.extract(file, str(_full_extract_path))

        print(f"Files extracted successfully at {_full_extract_path}")


def _as_dataframe(URL: str) -> pd.DataFrame:
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
