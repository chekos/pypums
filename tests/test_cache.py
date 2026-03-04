"""Tests for the local caching layer.

Phase 0 — Foundation.

The cache stores API responses and variable tables locally so repeated
queries don't hit the Census API.  Tests here verify the round-trip
store → retrieve contract, TTL expiration, and clearing.
"""

import time

import pandas as pd
import pytest

from pypums.cache import CensusCache

pytestmark = pytest.mark.phase0


@pytest.fixture()
def cache(cache_dir):
    """A CensusCache instance backed by a temporary directory."""
    return CensusCache(cache_dir)


def test_cache_stores_and_retrieves(cache):
    """Storing a DataFrame under a key and retrieving it returns equal data."""
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    cache.set("test_key", df)
    result = cache.get("test_key")
    assert result is not None
    pd.testing.assert_frame_equal(result, df)


def test_cache_miss_returns_none(cache):
    """Getting a key that was never stored returns None."""
    assert cache.get("nonexistent_key") is None


def test_cache_respects_ttl(cache):
    """An entry older than its TTL should not be returned."""
    df = pd.DataFrame({"a": [1]})
    cache.set("short_lived", df, ttl_seconds=0)
    # Even a TTL of 0 means "already expired"
    time.sleep(0.05)
    assert cache.get("short_lived") is None


def test_cache_clear(cache):
    """Clearing the cache removes all stored entries."""
    df = pd.DataFrame({"a": [1]})
    cache.set("key1", df)
    cache.set("key2", df)
    cache.clear()
    assert cache.get("key1") is None
    assert cache.get("key2") is None
