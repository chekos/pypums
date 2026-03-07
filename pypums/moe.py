"""Margin of error utility functions.

Implements the standard Census Bureau formulas from the ACS General
Handbook, Chapter 8, for combining margins of error from derived
estimates (sums, proportions, ratios, and products).
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd

# Z-scores for confidence levels used in significance testing.
_Z_SCORES: dict[float, float] = {
    0.90: 1.645,
    0.95: 1.960,
    0.99: 2.576,
}


def moe_sum(
    moe: list[float] | pd.Series | np.ndarray,
) -> float:
    """Calculate the MOE for a derived sum.

    Formula: ``sqrt(sum(moe_i ** 2))``

    Parameters
    ----------
    moe
        Individual margins of error to combine.

    Returns
    -------
    float
        Combined margin of error for the sum.
    """
    return math.sqrt(sum(m**2 for m in moe))


def moe_ratio(
    num: float,
    denom: float,
    moe_num: float,
    moe_denom: float,
) -> float:
    """Calculate the MOE for a derived ratio ``num / denom``.

    Formula: ``sqrt(moe_num**2 + (num/denom)**2 * moe_denom**2) / denom``

    Parameters
    ----------
    num
        Numerator estimate.
    denom
        Denominator estimate.
    moe_num
        MOE of the numerator.
    moe_denom
        MOE of the denominator.

    Returns
    -------
    float
        Margin of error for the ratio.
    """
    if denom == 0:
        raise ValueError("denom must be non-zero for moe_ratio.")
    r = num / denom
    return math.sqrt(moe_num**2 + r**2 * moe_denom**2) / denom


def moe_prop(
    num: float,
    denom: float,
    moe_num: float,
    moe_denom: float,
) -> float:
    """Calculate the MOE for a derived proportion ``num / denom``.

    Formula: ``sqrt(moe_num**2 - (num/denom)**2 * moe_denom**2) / denom``

    Falls back to :func:`moe_ratio` when the radicand is negative
    (i.e. when ``moe_num**2 < p**2 * moe_denom**2``).

    Parameters
    ----------
    num
        Numerator estimate (subset count).
    denom
        Denominator estimate (total count).
    moe_num
        MOE of the numerator.
    moe_denom
        MOE of the denominator.

    Returns
    -------
    float
        Margin of error for the proportion.
    """
    if denom == 0:
        raise ValueError("denom must be non-zero for moe_prop.")
    p = num / denom
    radicand = moe_num**2 - p**2 * moe_denom**2

    if radicand < 0:
        return moe_ratio(num, denom, moe_num, moe_denom)

    return math.sqrt(radicand) / denom


def moe_product(
    est1: float,
    est2: float,
    moe1: float,
    moe2: float,
) -> float:
    """Calculate the MOE for a derived product ``est1 * est2``.

    Formula: ``sqrt(est1**2 * moe2**2 + est2**2 * moe1**2)``

    Parameters
    ----------
    est1
        First estimate.
    est2
        Second estimate.
    moe1
        MOE of the first estimate.
    moe2
        MOE of the second estimate.

    Returns
    -------
    float
        Margin of error for the product.
    """
    return math.sqrt(est1**2 * moe2**2 + est2**2 * moe1**2)


def significance(
    est1: float,
    est2: float,
    moe1: float,
    moe2: float,
    *,
    clevel: float = 0.90,
) -> bool:
    """Test whether the difference between two estimates is statistically significant.

    Converts MOEs (at 90 % confidence) to standard errors, then checks
    whether ``|est1 - est2|`` exceeds the critical value times the SE
    of the difference.

    Parameters
    ----------
    est1
        First estimate.
    est2
        Second estimate.
    moe1
        MOE of the first estimate (at 90 % confidence).
    moe2
        MOE of the second estimate (at 90 % confidence).
    clevel
        Confidence level for the test: 0.90, 0.95, or 0.99 (default 0.90).

    Returns
    -------
    bool
        True if the difference is statistically significant.

    Raises
    ------
    ValueError
        If *clevel* is not one of the supported confidence levels.
    """
    if clevel not in _Z_SCORES:
        raise ValueError(
            f"clevel must be one of {sorted(_Z_SCORES)}, got {clevel!r}"
        )
    z_90 = _Z_SCORES[0.90]
    z = _Z_SCORES[clevel]

    # Convert 90 % MOEs to standard errors.
    se1 = moe1 / z_90
    se2 = moe2 / z_90

    se_diff = math.sqrt(se1**2 + se2**2)

    return abs(est1 - est2) > z * se_diff
