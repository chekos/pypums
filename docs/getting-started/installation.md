# Installation

## Requirements

- **Python 3.10** or newer
- A **Census API key** (free, instructions below)

## Install PyPUMS

```bash
uv add pypums
```

This installs PyPUMS and its core dependencies:

| Package   | Purpose                                   |
|-----------|-------------------------------------------|
| `httpx`   | HTTP client for Census API requests       |
| `pandas`  | DataFrames for tabular data               |
| `pyarrow` | Parquet support and fast columnar storage |
| `rich`    | Pretty terminal output                    |
| `typer`   | CLI framework                             |
| `us`      | US state abbreviations and FIPS codes     |

### Spatial extras

If you plan to work with shapefiles, choropleths, or any geometry (the `geometry=True` parameter), install the spatial extras:

```bash
uv add "pypums[spatial]"
```

This adds [`geopandas`](https://geopandas.org/) and its dependencies (`shapely`, `pyproj`, `fiona`), which enable PyPUMS to fetch TIGER/Line shapefiles and return `GeoDataFrame` objects.

## Get a Census API key

The Census Bureau requires a free API key for most data requests. Getting one takes about 30 seconds:

1. Go to [https://api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html)
2. Fill in your name and email address
3. Check your inbox and click the activation link
4. Copy the key from the confirmation email

!!! tip "No key needed for small tests"
    The Census API allows a limited number of unauthenticated requests. For
    anything beyond quick exploration, you will want a key.

## Configure your API key

PyPUMS looks for your Census API key in this order:

1. **Explicit `key` parameter** passed to any function call
2. **`CENSUS_API_KEY` environment variable**
3. **Session key** set via `census_api_key()` in Python

Choose whichever method fits your workflow.

### Option 1: Environment variable (recommended)

Set the `CENSUS_API_KEY` environment variable so every tool on your system can find it.

=== "macOS / Linux"

    Add this line to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

    ```bash
    export CENSUS_API_KEY="YOUR_KEY_HERE"
    ```

    Then reload your shell:

    ```bash
    source ~/.zshrc   # or ~/.bashrc
    ```

=== "Windows (PowerShell)"

    ```powershell
    [System.Environment]::SetEnvironmentVariable('CENSUS_API_KEY', 'YOUR_KEY_HERE', 'User')
    ```

    Restart your terminal for the change to take effect.

### Option 2: CLI command

Use the built-in `pypums config` command to set the key for the current session:

```bash
pypums config YOUR_KEY_HERE
```

!!! note
    This stores the key in the `CENSUS_API_KEY` environment variable for the
    duration of your shell session. It does not persist across terminal restarts.
    For permanent storage, use Option 1.

### Option 3: Python

Set the key at the top of your script or notebook:

```python
import pypums

pypums.census_api_key("YOUR_KEY_HERE")
```

This stores the key in the `CENSUS_API_KEY` environment variable for the current process. All subsequent PyPUMS calls will use it automatically.

You can also pass the key directly to any function:

```python
df = pypums.get_acs(
    geography="state",
    variables="B01001_001",
    key="YOUR_KEY_HERE",
)
```

## Verify your installation

Run this in your terminal to confirm PyPUMS is installed:

```bash
python -c "import pypums; print(pypums.__version__)"
```

You should see the version number printed (e.g. `0.2`).

To verify the CLI is available:

```bash
pypums --version
```

To confirm your API key is configured correctly:

```python
python -c "import pypums; print(pypums.census_api_key())"
```

If this prints your key without raising an error, you are ready to go.

## Troubleshooting

??? question "I get `ModuleNotFoundError: No module named 'pypums'`"
    Make sure you installed PyPUMS in the same Python environment you are
    running. Check with:

    ```bash
    uv pip show pypums
    ```

    If nothing is printed, install it again:

    ```bash
    uv add pypums
    ```

??? question "I get `ValueError: No Census API key found`"
    PyPUMS could not locate your key. Double-check that the environment
    variable is set:

    ```bash
    echo $CENSUS_API_KEY
    ```

    If empty, follow the [configuration steps](#configure-your-api-key) above.

??? question "I get `ImportError: geopandas` when using `geometry=True`"
    You need the spatial extras. Install them with:

    ```bash
    uv add "pypums[spatial]"
    ```

## Next steps

- [Quick Start](quickstart.md) -- run your first three queries
- [Census 101](census-101.md) -- learn which dataset to use
