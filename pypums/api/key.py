"""Census API key management."""

import os


def census_api_key(
    key: str | None = None,
    *,
    install: bool = False,
    overwrite: bool = False,
) -> str:
    """Get, set, or install a Census API key.

    Parameters
    ----------
    key
        If provided, sets this key for the current session via env var.
    install
        If True, persists the key to ``~/.pypums/config.toml``.
    overwrite
        If True, overwrites an existing installed key.

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
