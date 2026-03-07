"""File-based caching for Census API responses and variable tables."""

import json
import pickle
import shutil
import time
from pathlib import Path

import pandas as pd


class CensusCache:
    """Cache Census API responses with optional TTL.

    Parameters
    ----------
    cache_dir
        Directory to store cached files.
    """

    def __init__(self, cache_dir: Path) -> None:
        self._dir = Path(cache_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _data_path(self, key: str) -> Path:
        return self._dir / f"{key}.pkl"

    def _meta_path(self, key: str) -> Path:
        return self._dir / f"{key}.meta.json"

    def set(
        self,
        key: str,
        df: pd.DataFrame,
        ttl_seconds: int | float | None = None,
    ) -> None:
        """Store a DataFrame in the cache.

        Parameters
        ----------
        key
            Cache key identifier.
        df
            DataFrame to cache.
        ttl_seconds
            Time-to-live in seconds. ``None`` means no expiration.
        """
        with open(self._data_path(key), "wb") as f:
            pickle.dump(df, f)
        meta = {"created_at": time.time(), "ttl_seconds": ttl_seconds}
        self._meta_path(key).write_text(json.dumps(meta))

    def get(self, key: str) -> pd.DataFrame | None:
        """Retrieve a cached DataFrame, or ``None`` if missing/expired."""
        data_path = self._data_path(key)
        meta_path = self._meta_path(key)

        if not data_path.exists() or not meta_path.exists():
            return None

        meta = json.loads(meta_path.read_text())
        ttl = meta.get("ttl_seconds")

        if ttl is not None:
            age = time.time() - meta["created_at"]
            if age > ttl:
                data_path.unlink(missing_ok=True)
                meta_path.unlink(missing_ok=True)
                return None

        with open(data_path, "rb") as f:
            return pickle.load(f)  # noqa: S301

    def clear(self) -> None:
        """Remove all cached entries."""
        for path in self._dir.iterdir():
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
