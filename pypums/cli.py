# -*- coding: utf-8 -*-

"""Console script for acs_download."""
import sys
import click

from pypums import pypums


@click.command(
    help="Download ACS PUMS entire data files from US Census Bureau's FTP server."
)
@click.option(
    "--year",
    required=True,
    prompt="2000-2018",
    default=2018,
    show_default=True,
    type=click.IntRange(min=2000, max=2018, clamp=True),
)
@click.option(
    "--state",
    required=True,
    prompt="State",
    default="Alaska",
    show_default=True,
    type=click.STRING,
)
@click.option(
    "--survey",
    prompt="1-, 3-, or 5-year",
    default="1-year",
    show_default=True,
    type=click.Choice(choices=("1-year", "3-year", "5-year"), case_sensitive=False),
)
@click.option(
    "--person-or-household",
    prompt="person or household",
    default="person",
    show_default=True,
    type=click.Choice(choices=("person", "household")),
)
@click.option(
    "--download-path",
    prompt="path to download files to",
    default="../data/raw/",
    show_default=True,
    type=click.Path(exists=False, file_okay=False, writable=True),
)
@click.option(
    "--extract",
    prompt="extract zipped files?",
    default=True,
    show_default=True,
    type=click.BOOL,
)
@click.option(
    "--extract-path",
    prompt="path to extract contents to",
    default="../data/interim/",
    show_default=True,
    type=click.Path(exists=False, file_okay=False, writable=True),
)
def main(
    year, state, survey, person_or_household, download_path, extract, extract_path
):
    """Console script for acs_download."""
    pypums.get_data(
        year=year,
        state=state,
        survey=survey,
        person_or_household=person_or_household,
        download_path=download_path,
        extract=extract,
        extract_path=extract_path,
    )

    return print("Done!")


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
