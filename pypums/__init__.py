# -*- coding: utf-8 -*-

"""Top-level package for pypums."""

__author__ = """Sergio Sánchez Zavala"""
__email__ = "sergio@cimarron.io"
__version__ = "0.0.1"

"""Main module."""
# imports
# from pathlib import Path
# from typing import Union
# from tqdm.auto import tqdm
# from zipfile import ZipFile
# import requests
# import time
# import us

from pypums.pypums import *

if __name__ == "__main__":
    pypums.get_data()
