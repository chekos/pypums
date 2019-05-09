from dataclasses import dataclass, field
from typing import Union
import us

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
    

@dataclass
class ACS:
    year: Union[int, str] = 2017
    state: str = 'California'
    survey: Union[int, str] = '1-Year'
    person_or_household: str = 'person'
    _BASE_URL: str =  field(default = _BASE_URL + "acs/data/pums/", repr = False)


    def _SURVEY_URL_MAKER(self):
        """
        Builds url from which to retrieve data from Census FTP server.
        """

        if '5' in str(self.survey):
            _survey =  '5-Year'
        elif '3' in str(self.survey):
            _survey = '3-Year'
        else:
            _survey = '1-Year'
        
        
        _unit = self.person_or_household[0].lower() 
        _state_abbr = us.states.lookup(self.state).abbr.lower()
        _year = _clean_year(self.year)

        ## if year < 2006 : survey == ''
        ## if year 2007 or 08: 1 or 3 years
        ## if year 2009-2013: 1, 3, 5
        ## year >2014 :1, 5
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
                    print("Prior to 2007, only 1-Year ACS are available, defaulting to 1-Year")
                    _survey = ""
            elif (2007 <= _year) and (_year <= 2008):
                if _survey == '5-Year':
                    print(f"There is no 5-Year ACS for {_year}, defaulting to 3-Year")
                    _survey = "3-Year"
            elif _year >= 2014:
                if _survey == "3-Year":
                    print(f"There is no 3-Year ACS for {_year}, defaulting to 5-Year")
                    _survey = "5-Year"
            return _survey

        _survey = _ONE_THREE_OR_FIVE_YEAR(_survey, _year)

        self._SURVEY_URL = _BASE_URL + str(_year) +"/"+ _survey +"/"+ f"csv_{_unit}{_state_abbr}" + ".zip"
        return None

    def __post_init__(self):
        self._SURVEY_URL_MAKER()