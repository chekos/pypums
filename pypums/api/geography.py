"""Census geography hierarchy definitions and query building."""

GEOGRAPHY_HIERARCHY: dict[str, dict] = {
    "us": {"for": "us:1", "requires": []},
    "region": {"for": "region:*", "requires": []},
    "division": {"for": "division:*", "requires": []},
    "state": {"for": "state:*", "requires": []},
    "county": {"for": "county:*", "requires": ["state"]},
    "county subdivision": {
        "for": "county subdivision:*",
        "requires": ["state", "county"],
    },
    "tract": {"for": "tract:*", "requires": ["state", "county"]},
    "block group": {
        "for": "block group:*",
        "requires": ["state", "county"],
    },
    "block": {"for": "block:*", "requires": ["state", "county"]},
    "place": {"for": "place:*", "requires": ["state"]},
    "congressional district": {
        "for": "congressional district:*",
        "requires": ["state"],
    },
    "state legislative district (upper)": {
        "for": "state legislative district (upper chamber):*",
        "requires": ["state"],
    },
    "state legislative district (lower)": {
        "for": "state legislative district (lower chamber):*",
        "requires": ["state"],
    },
    "zcta": {"for": "zip code tabulation area:*", "requires": []},
    "school district (unified)": {
        "for": "school district (unified):*",
        "requires": ["state"],
    },
    "school district (elementary)": {
        "for": "school district (elementary):*",
        "requires": ["state"],
    },
    "school district (secondary)": {
        "for": "school district (secondary):*",
        "requires": ["state"],
    },
    "cbsa": {
        "for": "metropolitan statistical area/micropolitan statistical area:*",
        "requires": [],
    },
    "csa": {"for": "combined statistical area:*", "requires": []},
    "puma": {"for": "public use microdata area:*", "requires": ["state"]},
    "american indian area/alaska native area/hawaiian home land": {
        "for": "american indian area/alaska native area/hawaiian home land:*",
        "requires": [],
    },
}


def build_geography_query(
    geography: str,
    state: str | None = None,
    county: str | None = None,
) -> tuple[str, str | None]:
    """Convert geography + state/county to Census API ``for`` and ``in`` params.

    Parameters
    ----------
    geography
        Geography level name (e.g. ``"state"``, ``"county"``, ``"tract"``).
    state
        State FIPS code (e.g. ``"06"`` for California).
    county
        County FIPS code (e.g. ``"037"`` for Los Angeles County).

    Returns
    -------
    tuple[str, str | None]
        A ``(for_clause, in_clause)`` pair for the Census API query.

    Raises
    ------
    ValueError
        If the geography is unknown or required parent geographies are missing.
    """
    geo = geography.lower()
    if geo not in GEOGRAPHY_HIERARCHY:
        raise ValueError(
            f"Unknown geography: {geography!r}. "
            f"Valid options: {sorted(GEOGRAPHY_HIERARCHY)}"
        )

    spec = GEOGRAPHY_HIERARCHY[geo]
    required = spec["requires"]

    if "state" in required and state is None:
        raise ValueError(
            f"Geography {geography!r} requires a state FIPS code. "
            "Pass state='XX' (e.g. state='06' for California)."
        )
    if "county" in required and county is None:
        raise ValueError(
            f"Geography {geography!r} requires a county FIPS code. "
            "Pass county='XXX' (e.g. county='037' for Los Angeles County)."
        )

    for_clause = spec["for"]

    # Build the "in" clause from required parents
    in_parts = []
    if "state" in required and state is not None:
        in_parts.append(f"state:{state}")
    if "county" in required and county is not None:
        in_parts.append(f"county:{county}")

    in_clause = "+".join(in_parts) if in_parts else None

    return for_clause, in_clause
