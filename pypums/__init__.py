# -*- coding: utf-8 -*-

"""Top-level package for pypums."""

__author__ = """Sergio Sánchez Zavala"""
__email__ = "sergio@cimarron.io"
__version__ = "0.0.5"


from pypums.pypums import *
from pypums.surveys import ACS

if __name__ == "__main__":
    pypums.get_data()
