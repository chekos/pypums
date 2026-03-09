"""Surveys module."""

import warnings
from dataclasses import dataclass
from pathlib import Path

import us
from pandas import read_csv

from .utils import (
    _clean_survey,
    _clean_year,
    _download_as_dataframe,
    _download_data,
    build_acs_url,
    data_dir,
)


@dataclass
class ACS:
    """American Community Survey base class.

    .. deprecated:: 0.2
        Use :func:`pypums.get_pums` for PUMS microdata or
        :func:`pypums.get_acs` for ACS summary tables instead.
    """

    year: int = 2023
    state: str = "California"
    survey: str = "1-Year"
    sample_unit: str = "person"

    def __post_init__(self):
        warnings.warn(
            "ACS() is deprecated. Use get_pums() for PUMS microdata "
            "or get_acs() for ACS summary tables.",
            DeprecationWarning,
            stacklevel=3,
        )
        self._year = _clean_year(self.year)
        self._survey = _clean_survey(self.survey, self._year)
        self._sample_unit = self.sample_unit[0].lower()
        self._state_abbr = us.states.lookup(self.state).abbr.lower()
        self._survey_url = build_acs_url(
            self._year, self._survey, self._sample_unit, self._state_abbr
        )
        self.name = "ACS"
        self._data_dir = None
        self._extracted = None
        self._extract_folder = None
        self._download_folder = None

    def download(
        self,
        data_directory: Path = data_dir,
        extract: bool = True,
        overwrite: bool = False,
    ) -> None:
        """
        Downloads PUMS file from Census FTP server.
        """
        self._data_dir = data_directory
        self._extracted = extract
        self._extract_folder = data_directory.joinpath(
            f"interim/acs_{str(self._year)[-2:]}/{self._state_abbr}/"
        )
        self._download_folder = data_directory.joinpath(
            f"raw/acs_{str(self._year)[-2:]}/"
        )

        if self._download_folder.joinpath(
            f"csv_{self._sample_unit}{self._state_abbr}.zip"
        ).exists():
            if overwrite:
                _download_data(
                    url=self._survey_url,
                    name=self.name.lower(),
                    data_directory=data_directory,
                    extract=extract,
                )
            else:
                print(
                    "This was previously downloaded, to read it"
                    " as a dataframe use `.as_dataframe()` or"
                    " set `overwrite` to True."
                )
        else:
            _download_data(
                url=self._survey_url,
                name=self.name.lower(),
                data_directory=data_directory,
                extract=extract,
            )

    def as_dataframe(self):
        """
        Retrieves ACS PUMS csv file and returns a Pandas dataframe.
        """
        if self._extracted:
            extracted_file = list(self._extract_folder.glob("*.csv"))[0]
            return read_csv(extracted_file)
        else:
            return _download_as_dataframe(self._survey_url)
