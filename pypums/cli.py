from pathlib import Path

import typer
import us
from rich.console import Console

from . import __app_name__, __version__
from .utils import (
    _check_data_dirs,
    _download_data,
    _extract_data,
    build_acs_url,
    data_dir,
)

console = Console()

cli = typer.Typer()


@cli.command()
def acs_url(
    year: int = typer.Argument(
        ...,
        help="Year of survey (2000 - 2019)",
    ),
    state: str = typer.Argument(
        ..., help="One of the 50 US States or District of Columbia"
    ),
    survey: str = typer.Argument("1-year", help="One of '1-', '3-' or '5-year'"),
    sample_unit: str = typer.Argument(
        "person", help="Unit of observation (person or household)"
    ),
):
    """
    Builds URL pointing to the Census Bureau's FTP server containing
    the data for the desired ACS.
    """
    url = build_acs_url(year, survey, sample_unit, state)
    console.print(url)


@cli.command()
def download_acs(
    year: int = typer.Argument(
        ...,
        help="Year of survey (2000 - 2019)",
    ),
    state: str = typer.Argument(
        ..., help="One of the 50 US States or District of Columbia"
    ),
    survey: str = typer.Argument("1-year", help="One of '1-', '3-' or '5-year'"),
    sample_unit: str = typer.Argument(
        "person", help="Unit of observation (person or household)"
    ),
    data_directory: Path = typer.Option(data_dir, file_okay=False, dir_okay=True),
    extract: bool = typer.Option(
        True, "-e", "--extract", help="Extract the downloaded zip file?"
    ),
    overwrite_download: bool = typer.Option(
        False,
        help="Overwrite previously downloaded version of this data",
    ),
    overwrite_extract: bool = typer.Option(
        False,
        help="Overwrite previously extracted version of this data",
    ),
):
    """
    Downloads and, optionally, extracts data related to the specified ACS
    into a specified directory.
    """
    url = build_acs_url(year, survey, sample_unit, state)
    data_directory = _check_data_dirs(data_directory)
    state_abbr = us.states.lookup(state).abbr.lower()
    full_download_path = data_directory.joinpath(
        f"raw/csv_{sample_unit[0]}{state_abbr}.zip"
    )

    if full_download_path.exists():
        if overwrite_extract:
            _extract_data(full_download_path, data_directory.joinpath("interim"))
            raise typer.Exit()
        if overwrite_download:
            _download_data(url, "acs", data_directory, extract)
        else:
            console.print(
                "File has been previously downloaded! If you want to download again make sure to include [yellow]--overwrite-download[/yellow]"
            )
    else:
        _download_data(url, "acs", data_directory, extract)
