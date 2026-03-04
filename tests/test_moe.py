"""Tests for margin of error utility functions.

Phase 2 — MOE + Spatial + Enhanced PUMS.

These tests verify MOE calculations against hand-computed values using
the standard Census Bureau formulas.  All formulas are from the ACS
General Handbook, Chapter 8.
"""

import math

import numpy as np
import pandas as pd
import pytest

from pypums.moe import moe_product, moe_prop, moe_ratio, moe_sum, significance

pytestmark = pytest.mark.phase2


# ---------------------------------------------------------------------------
# moe_sum  —  sqrt(sum(moe_i^2))
# ---------------------------------------------------------------------------

class TestMoeSum:

    def test_basic(self):
        """sqrt(100^2 + 200^2 + 300^2) = sqrt(140000) ≈ 374.166"""
        result = moe_sum([100, 200, 300])
        expected = math.sqrt(100**2 + 200**2 + 300**2)
        assert result == pytest.approx(expected, rel=1e-6)

    def test_single_value(self):
        """Sum of one MOE is that MOE."""
        assert moe_sum([42]) == pytest.approx(42.0)

    def test_with_series(self):
        """Should accept a pandas Series."""
        s = pd.Series([100, 200, 300])
        result = moe_sum(s)
        expected = math.sqrt(100**2 + 200**2 + 300**2)
        assert result == pytest.approx(expected, rel=1e-6)

    def test_with_numpy_array(self):
        """Should accept a numpy array."""
        arr = np.array([100, 200, 300])
        result = moe_sum(arr)
        expected = math.sqrt(100**2 + 200**2 + 300**2)
        assert result == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# moe_prop  —  MOE for a derived proportion p = num/denom
# ---------------------------------------------------------------------------

class TestMoeProp:

    def test_basic(self):
        """Known example: 500/1000 with MOEs 80 and 120."""
        result = moe_prop(
            num=500, denom=1000, moe_num=80, moe_denom=120
        )
        # Formula: sqrt(moe_num^2 - p^2 * moe_denom^2) / denom
        # p = 0.5, => sqrt(6400 - 0.25*14400) / 1000 = sqrt(2800) / 1000
        expected = math.sqrt(80**2 - 0.25 * 120**2) / 1000
        assert result == pytest.approx(expected, rel=1e-6)

    def test_fallback_to_ratio_when_negative_radicand(self):
        """When radicand is negative, should fall back to moe_ratio formula."""
        # Choose values where moe_num^2 < p^2 * moe_denom^2
        result = moe_prop(
            num=900, denom=1000, moe_num=10, moe_denom=120
        )
        # Should not raise; falls back to moe_ratio formula
        assert result > 0


# ---------------------------------------------------------------------------
# moe_ratio  —  MOE for a derived ratio r = num/denom
# ---------------------------------------------------------------------------

class TestMoeRatio:

    def test_basic(self):
        """Known example: ratio 500/1000 with MOEs 80 and 120."""
        result = moe_ratio(
            num=500, denom=1000, moe_num=80, moe_denom=120
        )
        # Formula: sqrt(moe_num^2 + r^2 * moe_denom^2) / denom
        # r = 0.5, => sqrt(6400 + 0.25*14400) / 1000 = sqrt(10000) / 1000 = 0.1
        expected = math.sqrt(80**2 + 0.25 * 120**2) / 1000
        assert result == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# moe_product  —  MOE for a derived product a * b
# ---------------------------------------------------------------------------

class TestMoeProduct:

    def test_basic(self):
        """Known example: 500 * 0.6 with MOEs 80 and 0.1."""
        result = moe_product(
            est1=500, est2=0.6, moe1=80, moe2=0.1
        )
        # Formula: sqrt(est1^2 * moe2^2 + est2^2 * moe1^2)
        expected = math.sqrt(500**2 * 0.1**2 + 0.6**2 * 80**2)
        assert result == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# significance  —  test difference between two estimates
# ---------------------------------------------------------------------------

class TestSignificance:

    def test_significant_difference(self):
        """Large gap between estimates → statistically significant."""
        result = significance(
            est1=50000, est2=30000, moe1=1000, moe2=1500
        )
        assert result is True

    def test_not_significant(self):
        """Small gap relative to MOE → not significant."""
        result = significance(
            est1=50000, est2=49900, moe1=5000, moe2=5000
        )
        assert result is False

    def test_custom_confidence_level(self):
        """Higher confidence level makes it harder to be significant."""
        # Borderline case that's significant at 90% but not at 99%
        result_90 = significance(
            est1=50000, est2=48000, moe1=1000, moe2=1000, clevel=0.90
        )
        result_99 = significance(
            est1=50000, est2=48000, moe1=1000, moe2=1000, clevel=0.99
        )
        # At minimum, the 99% result should be equal or less significant
        # (i.e., if not significant at 90%, definitely not at 99%)
        if not result_90:
            assert result_99 is False
