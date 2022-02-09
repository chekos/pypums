"""Main PyPUMS module."""

from pypums.utils import build_acs_url, download_acs_data


def get_data(
    year: int = 2018,
    survey: str = "1-Year",
    sample_unit: str = "person",
    state: str = "California",
    download_path: str = "../data/raw/",
    extract: bool = True,
    extract_path: str = "../data/interim/",
) -> None:
    """
    Builds URL and downloads ACS 1-Year or 5-Year state PUMS estimates into a specified folder (defaults to ../data/raw/).
    """

    # builds URL
    URL = build_acs_url(
        year=year,
        survey=survey,
        sample_unit=sample_unit,
        state=state,
    )

    # download data
    download_acs_data(
        url=URL,
        download_path=download_path,
        extract=extract,
        extract_path=extract_path,
    )

    return None


if __name__ == "__main__":
    get_data()
