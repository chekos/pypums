# type: ignore[attr-defined]
"""Download Public Use Micro Sample (PUMS) data files from the US Census Bureau's FTP server."""

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

__app_name__ = "pypums"

from pypums.surveys import ACS
