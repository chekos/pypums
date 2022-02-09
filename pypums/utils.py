"""Utility functions."""
import us
import time
import httpx
from zipfile import ZipFile
from tqdm.auto import tqdm

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
    _survey = _survey.lower()
    if _year <= 2006:
        if _survey != "1-year":
            print("Prior to 2007, only 1-Year ACS are available, defaulting to 1-Year")
        return ""
    elif _year >= 2007 and _year <= 2008:
        if _survey == "5-year":
            print(f"There is no 5-Year ACS for {_year}, defaulting to 3-Year")
            return "3-year/"
    elif _year >= 2014:
        if _survey == "3-year":
            print(f"There is no 3-Year ACS for {_year}, defaulting to 5-Year")
            return "5-year/"
    return f"{_survey}/"


def _check_data_folder(
    path: str = "../data/raw/",
    extract_path: str = None,
) -> None:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    if extract_path is not None:
        extract_path = Path(extract_path)
        extract_path.mkdir(parents=True, exist_ok=True)

    return None


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


def download_acs_data(
    url: str,
    download_path: str = "../data/raw/",
    extract: bool = True,
    extract_path: str = "../data/interim/",
) -> None:
    """
    Downloads ACS 1-, 3-, or 5- estimates from a US Census Bureau's FTP-server URL.
    """

    # Checks download_path and extract_path exists
    _check_data_folder(
        path=download_path, extract_path=extract_path if extract else None
    )

    # Downloads Data
    BASE_URL = "https://www2.census.gov/programs-surveys/acs/data/pums/"
    if url[:55] != BASE_URL:
        raise ValueError(
            "Census FPT-server url's start with 'https://www2.census.gov/programs-surveys/acs/data/pums/'"
        )

    state = url.split("/")[-1].split(".")[0][-2:]

    r = httpx.get(url, stream=True)

    # content-lenght was dropped from their headers so try or use default 40 mb
    total_size = int(r.headers.get("content-length", 40000000))

    ### Checks
    download_path = Path(download_path)
    extract_path = Path(extract_path)

    if download_path.is_file():
        raise ValueError(
            "You provided a path to a file. You need to provide a path to a directory."
        )
    # if not download_path.is_dir():
    #     raise ValueError("You need to provide a path to a directory.")
    if not download_path.exists():
        download_path.mkdir()

    ### downloads data
    filename = url.split("/")[-1]

    with open(download_path / filename, "wb") as f:
        print(f"Downloading at {download_path / filename}.")
        chunk_size = 1024

        for data in tqdm(
            iterable=r.iter_content(chunk_size=chunk_size),
            total=total_size / chunk_size,
            unit="KB",
        ):
            f.write(data)

    print("Download complete!")

    ## Extract file
    if extract:
        year = url.split("/")[7]
        extract_folder = f"ACS_{year}"

        final_extraction_folder = extract_path / extract_folder.upper() / state

        if extract_path.is_file():
            raise ValueError(
                "You provided a path to a file. You need to provide a path to a directory."
            )
        # if not extract_path.is_dir():
        #     raise ValueError("You need to provide a path to a directory.")
        if not extract_path.exists():
            extract_path.mkdir()

        # remove dir if it exists
        if final_extraction_folder.exists():
            for item in final_extraction_folder.glob("*"):
                item.unlink()
            final_extraction_folder.rmdir()

        # create dir
        if not Path(extract_path / extract_folder.upper()).exists():
            Path(extract_path / extract_folder.upper()).mkdir()
        final_extraction_folder.mkdir()

        # extracts data
        content_file = ZipFile(download_path / filename)

        ## for progress bar
        file_size = 0
        for file_info in content_file.infolist():
            file_size += int(file_info.file_size)

        extract_folder_size = sum(
            item.stat().st_size for item in final_extraction_folder.iterdir()
        )
        expected_final_size = extract_folder_size + file_size

        ## Start extraction:
        print(f"Extracting to {final_extraction_folder}")
        content_file.extractall(final_extraction_folder)
        while extract_folder_size < expected_final_size:
            extract_folder_size = sum(
                item.stat().st_size for item in final_extraction_folder.iterdir()
            )
            print(
                f"Extracting files to {final_extraction_folder}: {(extract_folder_size / file_size) :.2%}",
                end="\r",
            )
            time.sleep(0.5)
            break

        print(f"Files extracted successfully at {final_extraction_folder}")
