"""Surveys module."""
import io
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

from typing import Union

import pandas as pd
import httpx
import us
from tqdm.auto import tqdm

from pypums.utils import _clean_year, _ONE_THREE_OR_FIVE_YEAR, build_acs_url


def _check_data_dirs(data_directory: Union[str, Path] = Path("../data/")) -> Path:
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
    data_directory: Union[str, Path] = Path("../data/"),
    extract: bool = True,
) -> None:
    """
    Downloads a file from Census FTP server.
    """

    data_directory = _check_data_dirs(data_directory=data_directory)
    _request = httpx.get(url, stream=True)
    TOTAL_SIZE = len(_request.content)
    _filename = url.split("/")[-1]
    _download_path = data_directory.joinpath("raw/")
    _extract_path = data_directory.joinpath("interim/")
    _full_download_path = _download_path / _filename

    # download fileacs
    with open(_full_download_path, "wb") as f:
        print(f"Downloading at {_full_download_path} ")
        CHUNK_SIZE = 1024
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
            CONTENT_FILE.extract(item, str(_full_extract_path))
        print(f"Files extracted successfully at {_full_extract_path}")


@dataclass
class ACS:
    year: int = 2018
    state: str = "California"
    survey: str = "1-Year"
    sample_unit: str = "person"

    def __post_init__(self):
        self._year = _clean_year(self.year)
        self._survey = _ONE_THREE_OR_FIVE_YEAR(self.survey, self._year)
        self._sample_unit = self.sample_unit[0].lower()
        self._state_abbr = us.states.lookup(self.state).abbr.lower()
        self._SURVEY_URL = build_acs_url(
            self._year, self._survey, self._sample_unit, self._state_abbr
        )
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
        _GET_DATA_REQUEST = httpx.get(self._SURVEY_URL)

        with ZipFile(io.BytesIO(_GET_DATA_REQUEST.content)) as thezip:
            csv_files = [
                file for file in thezip.infolist() if file.filename.endswith(".csv")
            ]
            # should be only 1
            assert len(csv_files) == 1
            with thezip.open(csv_files[0]) as thefile:
                data = pd.read_csv(thefile)
        return data
