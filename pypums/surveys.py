from dataclasses import dataclass, field
from typing import Union
import us

@dataclass
class Survey:
    year: Union[int, str] = 2017
    state: str = field(default = 'California')
    survey: Union[int, str] = field(default = '1-Year', init = False)
    person_or_household: str = 'person'
    BASE_URL: str = field(default = "https://www2.census.gov/programs-surveys/", repr = False)

@dataclass
class ACS(Survey):
    _BASE_URL = Survey.BASE_URL + "acs/data/pums/"

    def _make_survey_uri(self):
        survey = str(self.survey)
        if '5' in survey:
            return '5-Year'
        elif '3' in survey:
            return '3-Year'
        else:
            return '1-Year'
    
    year = Survey.year
    _unit = Survey.person_or_household[0].lower()
    _survey = _make_survey_uri(Survey)
    _state_abbr = us.states.lookup(Survey.state).abbr.lower()

    SURVEY_URL = _BASE_URL + str(year) +"/"+ _survey +"/"+ f"csv_{_unit}{_state_abbr}" + ".zip"
