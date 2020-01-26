from typing import Union
import us

from pypums.surveys import _clean_year

BASE_URL = "https://www2.census.gov/programs-surveys/"


def build_acs_url(
    year: Union[int, str] = "2017",
    survey: Union[str, int] = "1-Year",
    person_or_household: str = "person",
    state: str = "California",
):
    """
    Builds CENSUS FTP-server URL where you can download ACS 1-, 3-, or 5- year estimates. 
    """
    _BASE_URL = BASE_URL + "acs/data/pums/"
    _unit = person_or_household[0].lower()
    _state_abbr = us.states.lookup(state).abbr.lower()

    if "5" in str(survey):
        _survey = "5-Year"
    elif "3" in str(survey):
        _survey = "3-Year"
    else:
        _survey = "1-Year"
    _year = _clean_year(year)

    def _ONE_THREE_OR_FIVE_YEAR(_survey: str = _survey, _year: int = _year) -> str:
        """
        Fixes URL part for survey. Some years don't have 3-Year surveys.
        If year <= 2006, _survey == ''.
        From 2007-2008, _survey can be either 1 or 3 years.
        From 2009-2013, _survey can be either 1, 3, or 5 years.
        From 2013 onward, only 1 or 5 years.
        """
        if _year <= 2006:
            if _survey != "1-Year":
                print(
                    "Prior to 2007, only 1-Year ACS are available, defaulting to 1-Year"
                )
                _survey = ""
        elif (2007 <= _year) and (_year <= 2008):
            if _survey == "5-Year":
                print(f"There is no 5-Year ACS for {_year}, defaulting to 3-Year")
                _survey = "3-Year"
        elif _year >= 2014:
            if _survey == "3-Year":
                print(f"There is no 3-Year ACS for {_year}, defaulting to 5-Year")
                _survey = "5-Year"
        return _survey

    _survey = _ONE_THREE_OR_FIVE_YEAR(_survey, _year)

    SURVEY_URL = (
        _BASE_URL
        + str(_year)
        + "/"
        + _survey
        + "/"
        + f"csv_{_unit}{_state_abbr}"
        + ".zip"
    )
    return SURVEY_URL
