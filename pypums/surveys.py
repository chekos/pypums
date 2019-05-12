from dataclasses import dataclass, field
from typing import Union
from pathlib import Path
from tqdm.auto import tqdm
from zipfile import ZipFile
import pandas as pd
import requests
import time
import us
import io

_BASE_URL = "https://www2.census.gov/programs-surveys/"

# @dataclass
# class Survey:
#     year: Union[int, str]
#     state: str
#     survey: Union[int, str]
#     person_or_household: str


def _clean_year(year: Union[int, str]) -> int:
    ## YEAR
    try:
        year = int(year)
    except ValueError:
        raise ValueError("year must be a number.")

    if (0 <= year) & (year <= 17):
        year += 2000

    if not ((2000 <= year) & (year <= 2017)):
        raise ValueError("Year must be between 2000 and 2017.")
    return year


def _check_data_dirs(data_directory: str = "../data/",):
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
    data_directory: str = "../data/",
    extract: bool = True,
) -> None:
    """
    Downloads a file from Census FTP server.
    """

    data_directory = _check_data_dirs(data_directory=data_directory)
    _request = requests.get(url, stream=True)
    CHUNK_SIZE = 1024
    TOTAL_SIZE = len(_request.content)
    _filename = url.split("/")[-1]
    _download_path = data_directory.joinpath("raw/")
    _extract_path = data_directory.joinpath("interim/")
    _full_download_path = _download_path / _filename

    # download fileacs
    with open(_full_download_path, "wb") as f:
        print(f"Downloading at {_full_download_path} ")
        for data in tqdm(
            iterable=_request.iter_content(chunk_size=CHUNK_SIZE),
            total=TOTAL_SIZE / CHUNK_SIZE,
            unit="KB",
        ):
            f.write(data)
    print("Download complete!")

    # extract file
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
        print("Extracting files...")
        CONTENT_FILE = ZipFile(_full_download_path)
        for item in tqdm(iterable=CONTENT_FILE.filelist):
            CONTENT_FILE.extract(item, _full_extract_path)
        print(f"Files extracted successfully at {_full_extract_path}")


@dataclass
class ACS:
    year: Union[int, str] = 2017
    state: str = "California"
    survey: Union[int, str] = "1-Year"
    person_or_household: str = "person"
    _BASE_URL: str = field(default=_BASE_URL + "acs/data/pums/", repr=False)

    def _SURVEY_URL_MAKER(self):
        """
        Builds url from which to retrieve data from Census FTP server.
        """
        _unit = self.person_or_household[0].lower()
        _state_abbr = us.states.lookup(self.state).abbr.lower()

        if "5" in str(self.survey):
            _survey = "5-Year"
        elif "3" in str(self.survey):
            _survey = "3-Year"
        else:
            _survey = "1-Year"
        __year = _clean_year(self.year)

        def _ONE_THREE_OR_FIVE_YEAR(_survey: str = _survey, __year: int = __year) -> str:
            """
            Fixes URL part for survey. Some years don't have 3-Year surveys.
            If year <= 2006, _survey == ''.
            From 2007-2008, _survey can be either 1 or 3 years.
            From 2009-2013, _survey can be either 1, 3, or 5 years.
            From 2013 onward, only 1 or 5 years.
            """
            if __year <= 2006:
                if _survey != "1-Year":
                    print(
                        "Prior to 2007, only 1-Year ACS are available, defaulting to 1-Year"
                    )
                _survey = ""
            elif (2007 <= __year) and (__year <= 2008):
                if _survey == "5-Year":
                    print(f"There is no 5-Year ACS for {__year}, defaulting to 3-Year")
                    _survey = "3-Year"
            elif __year >= 2014:
                if _survey == "3-Year":
                    print(f"There is no 3-Year ACS for {__year}, defaulting to 5-Year")
                    _survey = "5-Year"
            return _survey

        self._survey = _ONE_THREE_OR_FIVE_YEAR(_survey, __year)

        self._SURVEY_URL = (
            self._BASE_URL
            + str(__year)
            + "/"
            + self._survey
            + "/"
            + f"csv_{_unit}{_state_abbr}"
            + ".zip"
        ).replace("//csv", "/csv")
        return None

    def __post_init__(self):
        self._SURVEY_URL_MAKER()
        self._year = _clean_year(self.year)
        self.NAME = "ACS"

    def download_data(
        self, data_directory: str = "../data/", extract: bool = True
    ) -> None:
        """
        Downloads PUMS file from Census FTP server.
        """
        _download_data(
            url=self._SURVEY_URL,
            year=self._year,
            name=self.NAME,
            state=self.state,
            data_directory=data_directory,
            extract=extract,
        )

    def as_dataframe(self) -> pd.DataFrame:
        """
        Retrieves ACS PUMS csv file and returns a Pandas dataframe.
        """
        _GET_DATA_REQUEST = requests.get(self._SURVEY_URL)

        with ZipFile(io.BytesIO(_GET_DATA_REQUEST.content)) as thezip:
            csv_files = [
                file for file in thezip.infolist() if file.filename.endswith(".csv")
            ]
            # should be only 1
            assert len(csv_files) == 1
            with thezip.open(csv_files[0]) as thefile:
                data = pd.read_csv(thefile)
        return data
