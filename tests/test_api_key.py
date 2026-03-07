"""Tests for Census API key management.

Phase 0 — Foundation.

These tests define the contract for ``census_api_key()``:
* Set a key and retrieve it back within the same session.
* Read a key from the ``CENSUS_API_KEY`` environment variable.
* Raise a clear error when no key is configured.
"""

import os

import pytest

from pypums import census_api_key

pytestmark = pytest.mark.phase0


def test_census_api_key_set_and_get(monkeypatch, fake_api_key):
    """Setting a key stores it so a subsequent call retrieves it."""
    # Clear any pre-existing env var so we're testing in-memory storage.
    monkeypatch.delenv("CENSUS_API_KEY", raising=False)

    census_api_key(fake_api_key)
    assert census_api_key() == fake_api_key


def test_census_api_key_from_env(monkeypatch, fake_api_key):
    """When no key is explicitly set, fall back to the env var."""
    monkeypatch.setenv("CENSUS_API_KEY", fake_api_key)

    assert census_api_key() == fake_api_key


def test_census_api_key_missing_raises(monkeypatch):
    """When no key is available anywhere, raise a helpful error."""
    monkeypatch.delenv("CENSUS_API_KEY", raising=False)

    with pytest.raises((ValueError, OSError)):
        census_api_key()
