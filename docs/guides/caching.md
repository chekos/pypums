# Caching

PyPUMS includes a built-in file cache that stores Census API responses and
variable tables on disk. Caching speeds up repeated queries, reduces load on
the Census Bureau servers, and makes iterative analysis much smoother.

---

## Quick start

Enable caching by passing a single parameter to any data retrieval function:

=== "API response caching"

    ```python
    import pypums

    # First call hits the Census API and saves the result.
    df = pypums.get_acs(
        geography="county",
        variables="B01001_001",
        state="TX",
        year=2023,
        cache_table=True,
    )

    # Second call returns instantly from the cache.
    df = pypums.get_acs(
        geography="county",
        variables="B01001_001",
        state="TX",
        year=2023,
        cache_table=True,
    )
    ```

=== "Variable table caching"

    ```python
    import pypums

    # First call downloads and caches the variable list.
    vars_df = pypums.load_variables(2023, "acs5", cache=True)

    # Second call is instant (served from memory or disk).
    vars_df = pypums.load_variables(2023, "acs5", cache=True)
    ```

---

## Which functions support caching?

| Function          | Parameter       | What is cached                    |
|-------------------|-----------------|-----------------------------------|
| `get_acs()`       | `cache_table=True` | Full API response DataFrame    |
| `get_decennial()` | `cache_table=True` | Full API response DataFrame    |
| `get_pums()`      | `cache_table=True` | Full API response DataFrame    |
| `get_estimates()`  | `cache_table=True` | Full API response DataFrame    |
| `get_flows()`     | `cache_table=True` | Full API response DataFrame    |
| `load_variables()`| `cache=True`       | Variable metadata DataFrame    |

---

## How it works

### Storage format: Parquet

All cached DataFrames are stored as **Parquet** files. Parquet was chosen over
pickle for two important reasons:

1. **Security** -- Parquet files are safe to deserialize from untrusted sources.
   Pickle files can execute arbitrary code when loaded, which is a well-known
   security risk.
2. **Efficiency** -- Parquet is a columnar format with built-in compression.
   Cached files are typically much smaller than equivalent CSV files and load
   faster than pickle.

### Cache keys: SHA-256 hashing

Each query is turned into a unique cache key based on all parameters that
affect the result (year, survey, geography, state, variables, etc.). PyPUMS
hashes this key with **SHA-256** to produce a fixed-length, filesystem-safe
filename. Two queries with identical parameters always produce the same hash
and therefore hit the same cache entry.

### Time-to-live (TTL)

API response caches have a default TTL of **24 hours (86,400 seconds)**. After
the TTL expires, the next call re-fetches from the Census API and refreshes
the cache.

Each cached entry consists of two files:

- `<hash>.parquet` -- the cached DataFrame
- `<hash>.meta.json` -- metadata including creation timestamp and TTL

The `.meta.json` file is checked on every cache read. If the entry has
expired, both files are deleted and a fresh API call is made.

!!! note
    Variable table caches created by `load_variables(cache=True)` have no TTL
    by default. Variable definitions rarely change mid-year, so indefinite
    caching is reasonable.

---

## Cache directory layout

All cache files live under `~/.pypums/cache/` with the following subdirectory
structure:

```
~/.pypums/cache/
    api/            # API response cache (get_acs, get_decennial, etc.)
    variables/      # Variable table cache (load_variables)
    pums_vars/      # PUMS variable dictionary cache
    geography/      # Geometry / shapefile cache
```

You can inspect the cache directory at any time:

```bash
ls -la ~/.pypums/cache/api/
```

Each entry is a pair of files:

```
a1b2c3d4...f5.parquet       # cached DataFrame
a1b2c3d4...f5.meta.json     # metadata (created_at, ttl_seconds)
```

---

## In-memory caching for `load_variables()`

`load_variables()` has an additional **in-memory cache** at the module level.
When you call `load_variables(2023, "acs5", cache=True)`, the result is stored
in both:

1. A Python dictionary in memory (instant lookup for the rest of your session)
2. A Parquet file on disk (persists across sessions)

On subsequent calls with the same `year` and `dataset`, the in-memory dict is
checked first (fastest), then the disk cache, and only then the Census API.

```python
import pypums

# Call 1: fetches from API, stores in memory + disk.
vars_df = pypums.load_variables(2023, "acs5", cache=True)

# Call 2: returns from in-memory dict (no disk I/O).
vars_df = pypums.load_variables(2023, "acs5", cache=True)
```

---

## Clearing the cache

### Clear all cached data

Use the `CensusCache` class to clear a specific cache directory:

```python
from pathlib import Path
from pypums.cache import CensusCache

# Clear all API response caches.
cache = CensusCache(Path.home() / ".pypums" / "cache" / "api")
cache.clear()

# Clear variable table caches.
cache = CensusCache(Path.home() / ".pypums" / "cache" / "variables")
cache.clear()
```

### Delete individual cache files

Since cache files are just `.parquet` and `.meta.json` files, you can also
delete them manually from the filesystem:

=== "macOS / Linux"

    ```bash
    # Remove all API cache files.
    rm -rf ~/.pypums/cache/api/*

    # Remove everything.
    rm -rf ~/.pypums/cache/
    ```

=== "Python"

    ```python
    from pathlib import Path
    import shutil

    cache_dir = Path.home() / ".pypums" / "cache"
    shutil.rmtree(cache_dir, ignore_errors=True)
    ```

!!! tip
    Deleting the cache directory is safe. PyPUMS will recreate it
    automatically the next time caching is enabled.

---

## The `CensusCache` class

For advanced usage, you can interact with the cache directly:

```python
from pathlib import Path
from pypums.cache import CensusCache
import pandas as pd

cache = CensusCache(Path.home() / ".pypums" / "cache" / "api")

# Store a DataFrame with a 1-hour TTL.
cache.set("my_custom_key", df, ttl_seconds=3600)

# Retrieve it (returns None if expired or missing).
result = cache.get("my_custom_key")

# Clear everything in this cache directory.
cache.clear()
```

**Constructor:**

```python
CensusCache(cache_dir: Path)
```

**Methods:**

| Method                               | Description                                      |
|--------------------------------------|--------------------------------------------------|
| `set(key, df, ttl_seconds=None)`     | Store a DataFrame. `None` TTL means no expiration |
| `get(key) -> DataFrame or None`      | Retrieve a cached entry, or `None` if expired/missing |
| `clear()`                            | Remove all entries in this cache directory        |

---

## When to use caching

Caching is most valuable in these scenarios:

!!! success "Good candidates for caching"

    - **Iterative development** -- You are tweaking a visualization or analysis
      and re-running the same query repeatedly. Caching avoids waiting for the
      API on every run.
    - **Large datasets** -- Tract-level or block-group-level queries can return
      tens of thousands of rows. Caching avoids re-downloading them.
    - **Variable table browsing** -- `load_variables()` returns thousands of
      variable definitions. Caching with `cache=True` makes searching and
      filtering instant after the first call.
    - **Multi-year analysis** -- When pulling the same variables for many years
      in a loop, caching prevents hitting API rate limits.
    - **Workshops and demos** -- Guaranteed fast responses even if the Census
      API is slow or temporarily unavailable.

!!! warning "When to skip caching"

    - **One-off production scripts** -- If you run a query exactly once, the
      overhead of writing to disk is unnecessary.
    - **Rapidly changing data** -- If you need the absolute latest data (for
      example, during a Census Bureau data release), disable caching or clear
      it first so you get fresh results.

---

## See Also

- [API Reference](../reference/api.md) — Full `CensusCache` class reference and constructor details
