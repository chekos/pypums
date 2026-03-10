# CLAUDE.md

Project-level context for Claude Code sessions working on PyPUMS.

## Project overview

PyPUMS is a Python interface to the US Census Bureau API. It provides functions for
ACS, Decennial Census, PUMS microdata, population estimates, and migration flows.
The package returns pandas DataFrames (or GeoDataFrames when `geometry=True`).

- **Package source:** `pypums/`
- **Tests:** `tests/`
- **Docs:** `docs/` (MkDocs Material, hosted on ReadTheDocs)
- **CLI:** `pypums/cli.py` (Typer)

## Common commands

```bash
# Run tests (uses doctest + pytest)
uv run pytest

# Run a specific test file
uv run pytest tests/test_get_acs.py

# Lint and format
uv run ruff check --fix .
uv run ruff format .

# Build docs locally
uv run mkdocs build --strict

# Serve docs locally (live reload)
uv run mkdocs serve
```

## Dependencies and lockfile

This project uses **uv** for dependency management.

**Important:** When you add or change dependencies in `pyproject.toml`, you **must**
run `uv lock` and commit the updated `uv.lock`. ReadTheDocs uses
`uv sync --frozen --extra docs` which requires the lockfile to be in sync with
`pyproject.toml`. Forgetting to update `uv.lock` will cause the docs build to fail
on CI.

Optional dependency groups:
- `spatial` — geopandas (for `geometry=True` support)
- `test` — pytest
- `docs` — mkdocs-material, mkdocstrings, mkdocs-charts-plugin, altair, etc.

## Code style

- **Linter/formatter:** Ruff (config in `pyproject.toml`)
- **Target:** Python 3.10+
- **Pre-commit hooks:** trailing whitespace, end-of-file fixer, check-yaml, check-toml,
  ruff-check, ruff-format

## Docs

The documentation uses **MkDocs Material** with these notable plugins/extensions:

- `mkdocs-charts-plugin` with `pymdownx.superfences` custom fences for rendering
  **Vega-Lite** charts inline. Use ` ```vegalite ` fenced code blocks with a JSON
  Vega-Lite spec to render interactive charts directly in the docs.
- `mkdocstrings[python]` for API reference (numpy-style docstrings).
- `mkdocs-typer` for CLI reference auto-generation.
- Visualizations use **Altair** (not matplotlib). Code examples should use Altair, and
  rendered previews use Vega-Lite JSON specs in `vegalite` fenced blocks.

Rendered Vega-Lite charts in docs should:
- Use inline `"values"` data (not live API calls) so they render without a backend.
- Include all 50 states + DC for choropleth maps.
- Be wrapped in `!!! example "Interactive preview"` admonitions when the rendered chart
  shows a different geographic scale than the code example (e.g., state-level preview
  for a tract-level code example).

## CI pipeline

- **GitHub Actions:** lint (ruff), tests (Python 3.10-3.13)
- **ReadTheDocs:** builds docs from `.readthedocs.yaml` using `uv sync --frozen --extra docs`
- **Pre-commit hooks:** run on every commit (trailing whitespace, ruff, etc.)

## Test markers

```
phase0   — Foundation (API infra, geography, FIPS, cache)
phase1   — Core data functions (get_acs, get_decennial, load_variables)
phase2   — MOE, spatial, enhanced PUMS
phase3   — Estimates, flows, survey
integration — Requires real Census API key and network
spatial     — Requires geopandas
```
