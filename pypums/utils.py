"""Utility functions."""
import us

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

    def _ONE_THREE_OR_FIVE_YEAR(_survey: str = SURVEY, _year: int = YEAR) -> str:
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

    SURVEY = f"{_ONE_THREE_OR_FIVE_YEAR(SURVEY, YEAR)}"

    SURVEY_URL = f"{BASE_URL}{YEAR}/{SURVEY}csv_{UNIT}{STATE_ABBR}.zip"
    return SURVEY_URL
