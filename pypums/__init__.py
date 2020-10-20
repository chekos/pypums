# type: ignore[attr-defined]
"""Download Public Use Micro Sample (PUMS) data files from the US Census Bureau's FTP server."""

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

from pypums.pypums import *
from pypums.surveys import ACS

if __name__ == "__main__":
    pypums.get_data()