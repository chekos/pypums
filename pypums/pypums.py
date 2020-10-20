# -*- coding: utf-8 -*-

"""Main module."""
# imports
from pathlib import Path
from typing import Union
from tqdm.auto import tqdm
from zipfile import ZipFile
import requests
import time
import us

import pypums
from pypums.download import download_acs_data
from pypums.url_builder import build_acs_url


def get_data(
    year: Union[int, str] = "2018",
    survey: Union[str, int] = "1-Year",
    person_or_household: str = "person",
    state: str = "California",
    download_path: str = "../data/raw/",
    extract: bool = True,
    extract_path: str = "../data/interim/",
):
    """
    Builds URL and downloads ACS 1-Year or 5-Year state PUMS estimates into a specified folder (defaults to ../data/raw/).
    """

    # builds URL
    URL = build_acs_url(
        year=year, survey=survey, person_or_household=person_or_household, state=state
    )

    # download data
    download_acs_data(
        url=URL, download_path=download_path, extract=extract, extract_path=extract_path
    )

    return None


def tree(directory):
    """
    Displays a directory's tree.
    """
    directory = Path(directory)
    print(f'+ {directory}')
    for path in sorted(directory.rglob('[!.]*')):
        depth = len(path.relative_to(directory).parts)
        spacer = '    ' * depth
        print(f'{spacer}+ {path.name}')


if __name__ == "__main__":
    get_data()
