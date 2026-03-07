"""Census API key management."""

import os


def census_api_key(key: str | None = None) -> str:
    """Get or set a Census API key for the current session.

    Parameters
    ----------
    key
        If provided, sets this key for the current session via env var.

    Returns
    -------
    str
        The active Census API key.

    Raises
    ------
    ValueError
        If no key is available from any source.
    """
    if key is not None:
        os.environ["CENSUS_API_KEY"] = key
        return key

    env_key = os.environ.get("CENSUS_API_KEY")
    if env_key is not None:
        return env_key

    raise ValueError(
        "No Census API key found. Set one with census_api_key('your-key') "
        "or set the CENSUS_API_KEY environment variable. "
        "Request a key at https://api.census.gov/data/key_signup.html"
    )
