---
title: "feat: Replace custom TIGER/Line downloads with pygris"
type: feat
status: active
date: 2026-03-13
---

# feat: Replace custom TIGER/Line downloads with pygris

## Overview

Replace pypums's hand-rolled TIGER/Line cartographic boundary download code in `pypums/spatial.py` with the [pygris](https://github.com/walkerke/pygris) package. pygris is the Python port of R's `tigris` — a well-maintained library purpose-built for downloading Census Bureau shapefiles. This removes ~40 lines of URL-construction logic, gains built-in caching, better year/vintage handling, and broader geography support for free.

## Problem Statement / Motivation

The current `_fetch_tiger_shapes()` function manually constructs Census Bureau URLs from templates and calls `geopandas.read_file(url)`. This works but:

- **Fragile URL construction** — hardcoded URL patterns break when the Census Bureau changes paths across vintages (e.g., ZCTA and PUMA vintage suffixes are hardcoded to 2020, broken for pre-2020 years)
- **No caching** — every `geometry=True` call re-downloads the same shapefile
- **Limited year support** — only works for the modern `GENZ{year}/shp/` URL pattern (roughly 2014+)
- **Reinvents the wheel** — pygris already solves all of this with a maintained, tested codebase

## Proposed Solution

Replace the internals of `_fetch_tiger_shapes()` with calls to the corresponding pygris functions. Keep the public API (`attach_geometry()`, `geometry=True` flag on data functions) completely unchanged.

### Geography mapping

| pypums geography | pygris function | Notes |
|---|---|---|
| `"state"` | `pygris.states(cb=True)` | `cb` defaults True for states already |
| `"county"` | `pygris.counties(state=..., cb=True)` | Pass `state` through for perf |
| `"tract"` | `pygris.tracts(state=..., cb=True)` | `state` required |
| `"block group"` | `pygris.block_groups(state=..., cb=True)` | `state` required |
| `"place"` | `pygris.places(state=..., cb=True)` | |
| `"congressional district"` | `pygris.congressional_districts(cb=True)` | pygris handles congress number internally |
| `"zcta"` | `pygris.zctas(cb=True)` | pygris handles vintage suffix |
| `"puma"` | `pygris.pumas(state=..., cb=True)` | pygris handles vintage suffix |
| `"cbsa"` | `pygris.core_based_statistical_areas(cb=True)` | |
| `"csa"` | `pygris.combined_statistical_areas(cb=True)` | |

### Implementation approach

1. **Preserve `_fetch_tiger_shapes` as a thin wrapper** — replace `_GEO_TO_TIGER` dict with a `_GEO_TO_PYGRIS` dict that maps geography names to pygris callables. The function dispatches to the right pygris function with `cb=True`, `year`, `resolution`, and `state` as applicable.

2. **Normalize GEOID column** — after receiving shapes from pygris, ensure the `GEOID` column exists (pygris may return `GEOID20`, `GEOID10` for some vintages). Add a small normalization step.

3. **Pass `state` through to pygris** for sub-state and county-level geographies to download smaller files (faster). The right-join merge already filters to matching GEOIDs, so results are identical.

4. **Remove dead constants** — delete `_TIGER_BASE` and `_GEO_TO_TIGER` after replacement.

5. **Add `pygris` to the `spatial` optional dependency group** in `pyproject.toml` and run `uv lock`.

## Technical Considerations

- **CRS contract** — docs promise EPSG:4269 (NAD83). Add an assertion or `.to_crs()` call after pygris returns to guarantee this.
- **Caching** — pygris caches shapefiles to `~/Library/Caches/pygris/` (macOS) / `~/.cache/pygris/` (Linux) when `cache=True`. We should pass `cache=True` by default to avoid re-downloading on every call — this is a UX improvement over the current behavior.
- **Error handling** — keep the `ValueError` for unsupported geographies. Let pygris errors for year/network issues propagate naturally; they are descriptive enough.
- **Test mocks** — preserving `_fetch_tiger_shapes` means the existing mock target `"pypums.spatial._fetch_tiger_shapes"` in `tests/test_spatial.py` continues to work unchanged.
- **Network stack change** — pygris uses `requests` instead of geopandas/fiona's urllib. This is generally more robust but could differ for users behind corporate proxies. Low risk.
- **Congressional districts** — pygris handles the congress-number-to-year mapping internally, so we can drop the manual `113 + (year - 2013) // 2` computation.
- **ZCTA/PUMA vintages** — the current code hardcodes 2020 vintage suffixes (`zcta520`, `puma20`), which is broken for pre-2020 years. pygris handles this correctly — a free bug fix.

## Acceptance Criteria

- [x] `_fetch_tiger_shapes` calls pygris functions instead of constructing URLs manually
- [x] `_GEO_TO_TIGER` and `_TIGER_BASE` constants are removed
- [x] New `_GEO_TO_PYGRIS` mapping covers all 10 geography levels
- [x] GEOID column is normalized after pygris returns (handle `GEOID`, `GEOID20`, `GEOID10` variants)
- [x] `pygris` added to `spatial` optional deps in `pyproject.toml`
- [x] `uv lock` run and `uv.lock` updated
- [x] `resolution` parameter still works on `attach_geometry()` and maps to pygris `resolution`
- [x] `state` passed through to pygris for county/sub-state geographies
- [x] CRS assertion added (EPSG:4269)
- [x] Caching enabled by default (`cache=True`)
- [x] Existing tests pass without changes to test code (mock target preserved)
- [x] Module and function docstrings updated to mention pygris
- [x] `docs/guides/spatial.md` updated: mention pygris, caching, installation changes
- [x] Branch: `feat/use-pygris` created from `main`
- [ ] PR created targeting `main`

## Success Metrics

- All existing tests pass (`uv run pytest`)
- `geometry=True` works for all 10 geography levels (manual spot check)
- Repeated calls are faster due to caching
- Docs build cleanly (`uv run mkdocs build --strict`)

## Dependencies & Risks

- **pygris version** — pin to `>=0.1.7` (last version with all 10 geography functions). Current latest is 0.2.1.
- **pygris maintenance** — actively maintained by Kyle Walker (author of R tigris/tidycensus). Low bus-factor risk.
- **New transitive deps** — `requests` and `platformdirs` (both widely used, low risk)
- **Breaking change risk** — low. Public API is unchanged. Only internal implementation changes. The ZCTA/PUMA fix for pre-2020 years is technically a behavior change but corrects a bug.

## Implementation Steps

### Phase 1: Core replacement (`pypums/spatial.py`)

1. Create branch `feat/use-pygris` from `main`
2. Add `pygris>=0.1.7` to `[project.optional-dependencies] spatial` in `pyproject.toml`
3. Run `uv lock`
4. Replace `_GEO_TO_TIGER` dict with `_GEO_TO_PYGRIS` mapping (geography name -> pygris callable)
5. Rewrite `_fetch_tiger_shapes` to dispatch to pygris functions with `cb=True`, `year`, `resolution`, `state`
6. Add GEOID column normalization
7. Add CRS assertion
8. Remove `_TIGER_BASE` and `_GEO_TO_TIGER`
9. Update module docstring and function docstrings

### Phase 2: Tests & docs

10. Run `uv run pytest` — existing tests should pass (mock target preserved)
11. Update `docs/guides/spatial.md`:
    - Update "How it works" to mention pygris
    - Add note about automatic caching
    - Update installation section if needed
    - Update troubleshooting section
12. Run `uv run mkdocs build --strict` to verify docs
13. Run `uv run ruff check --fix . && uv run ruff format .`

### Phase 3: PR & release

14. Commit all changes
15. Push branch and create PR
16. After merge, release as v0.3.1

## Sources & References

- [pygris GitHub](https://github.com/walkerke/pygris)
- [pygris docs — basic usage](https://walker-data.com/pygris/01-basic-usage/)
- [pygris on PyPI](https://pypi.org/project/pygris/)
- Current implementation: `pypums/spatial.py`
- Tests: `tests/test_spatial.py`
- Docs: `docs/guides/spatial.md`
- Callers: `pypums/acs.py:233`, `pypums/decennial.py:175`, `pypums/estimates.py:266`, `pypums/flows.py:251`
