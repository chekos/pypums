"""Surveys module."""
from dataclasses import dataclass

import us

from pypums.utils import (
    _ONE_THREE_OR_FIVE_YEAR,
    _as_dataframe,
    _clean_year,
    _download_data,
    build_acs_url,
    data_dir,
)


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

    def download_data(self, data_directory: data_dir, extract: bool = True) -> None:
        """
        Downloads PUMS file from Census FTP server.
        """
        _download_data(
            url=self._SURVEY_URL,
            name=self.NAME,
            data_directory=data_directory,
            extract=extract,
        )

    def as_dataframe(self):
        """
        Retrieves ACS PUMS csv file and returns a Pandas dataframe.
        """
        return _as_dataframe(self._SURVEY_URL)
