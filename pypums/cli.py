from pathlib import Path

import typer
import us
from rich.console import Console

from .constants import __app_name__, __version__
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
    year: int = typer.Option(
        ...,
        "--year",
        help="Year of survey (2000 - 2024)",
    ),
    state: str = typer.Option(
        ..., "--state", help="One of the 50 US States or District of Columbia"
    ),
    survey: str = typer.Option(
        "1-year", "--survey", help="One of '1-', '3-' or '5-year'"
    ),
    sample_unit: str = typer.Option(
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
    year: int = typer.Option(
        ...,
        help="Year of survey (2000 - 2024)",
    ),
    state: str = typer.Option(
        ..., help="One of the 50 US States or District of Columbia"
    ),
    survey: str = typer.Option("1-year", help="One of '1-', '3-' or '5-year'"),
    sample_unit: str = typer.Option(
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
        f"raw/acs_{str(year)[-2:]}/csv_{sample_unit[0]}{state_abbr}.zip"
    )

    if full_download_path.exists():
        if overwrite_extract:
            _extract_data(full_download_path, data_directory.joinpath("interim"))
            raise typer.Exit()
        if overwrite_download:
            _download_data(url, "acs", data_directory, extract)
        else:
            console.print(
                "File has been previously downloaded!"
                " If you want to download again make sure to include"
                " [yellow]--overwrite-download[/yellow]"
            )
    else:
        _download_data(url, "acs", data_directory, extract)


@cli.command("config")
def config_set_key(
    key: str = typer.Argument(..., help="Census API key to store"),
    install: bool = typer.Option(
        True, "--install/--no-install", help="Save key to environment"
    ),
):
    """Set your Census API key."""
    import os

    from .api.key import census_api_key

    os.environ["CENSUS_API_KEY"] = key
    census_api_key(key)
    console.print("[green]Census API key set successfully.[/green]")
    if install:
        console.print(
            "Key stored in environment variable CENSUS_API_KEY for this session."
        )


@cli.command("acs")
def acs_data(
    geography: str = typer.Argument(
        ..., help="Geography level (e.g. 'state', 'county')"
    ),
    variables: str = typer.Option(
        None, "--variables", "-v", help="Comma-separated variable IDs"
    ),
    table: str = typer.Option(None, "--table", "-t", help="Census table ID"),
    state_opt: str = typer.Option(
        None, "--state", "-s", help="State FIPS or abbreviation"
    ),
    county_opt: str = typer.Option(None, "--county", help="County FIPS code"),
    year_opt: int = typer.Option(2023, "--year", "-y", help="Data year"),
    survey_opt: str = typer.Option("acs5", "--survey", help="Survey: acs1 or acs5"),
    output: str = typer.Option("tidy", "--output", "-o", help="Output: tidy or wide"),
    key: str = typer.Option(None, "--key", "-k", help="Census API key"),
):
    """Fetch ACS data from the Census API."""
    from .acs import get_acs

    var_list = variables.split(",") if variables else None
    df = get_acs(
        geography=geography,
        variables=var_list,
        table=table,
        state=state_opt,
        county=county_opt,
        year=year_opt,
        survey=survey_opt,
        output=output,
        key=key,
    )
    console.print(df.to_string())


@cli.command("decennial")
def decennial_data(
    geography: str = typer.Argument(
        ..., help="Geography level (e.g. 'state', 'county')"
    ),
    variables: str = typer.Option(
        None, "--variables", "-v", help="Comma-separated variable IDs"
    ),
    table: str = typer.Option(None, "--table", "-t", help="Census table ID"),
    state_opt: str = typer.Option(
        None, "--state", "-s", help="State FIPS or abbreviation"
    ),
    county_opt: str = typer.Option(None, "--county", help="County FIPS code"),
    year_opt: int = typer.Option(2020, "--year", "-y", help="Census year"),
    output: str = typer.Option("tidy", "--output", "-o", help="Output: tidy or wide"),
    key: str = typer.Option(None, "--key", "-k", help="Census API key"),
):
    """Fetch Decennial Census data from the Census API."""
    from .decennial import get_decennial

    var_list = variables.split(",") if variables else None
    df = get_decennial(
        geography=geography,
        variables=var_list,
        table=table,
        state=state_opt,
        county=county_opt,
        year=year_opt,
        output=output,
        key=key,
    )
    console.print(df.to_string())


@cli.command("variables")
def variables_cmd(
    year_opt: int = typer.Option(2023, "--year", "-y", help="Data year"),
    dataset: str = typer.Option("acs5", "--dataset", "-d", help="Dataset identifier"),
    search: str = typer.Option(None, "--search", help="Filter by name/label/concept"),
    cache: bool = typer.Option(False, "--cache", help="Cache results"),
):
    """Search/browse Census variables."""
    from .variables import load_variables

    df = load_variables(year=year_opt, dataset=dataset, cache=cache)
    if search:
        mask = (
            df["name"].str.contains(search, case=False, na=False)
            | df["label"].str.contains(search, case=False, na=False)
            | df["concept"].str.contains(search, case=False, na=False)
        )
        df = df[mask]
    console.print(df.to_string())


@cli.command("estimates")
def estimates_cmd(
    geography: str = typer.Argument(
        ..., help="Geography level (e.g. 'state', 'county')"
    ),
    product: str = typer.Option(
        "population", "--product", "-p", help="Estimates product"
    ),
    variables: str = typer.Option(
        None, "--variables", "-v", help="Comma-separated variable IDs"
    ),
    state_opt: str = typer.Option(
        None, "--state", "-s", help="State FIPS or abbreviation"
    ),
    county_opt: str = typer.Option(None, "--county", help="County FIPS code"),
    vintage: int = typer.Option(2023, "--vintage", help="Vintage year"),
    output: str = typer.Option("tidy", "--output", "-o", help="Output: tidy or wide"),
    key: str = typer.Option(None, "--key", "-k", help="Census API key"),
):
    """Fetch population estimates from the Census API."""
    from .estimates import get_estimates

    var_list = variables.split(",") if variables else None
    df = get_estimates(
        geography=geography,
        product=product,
        variables=var_list,
        state=state_opt,
        county=county_opt,
        vintage=vintage,
        output=output,
        key=key,
    )
    console.print(df.to_string())


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@cli.callback()
def pypums(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    return
