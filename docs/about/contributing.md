# Contributing

Contributions are welcome! Every bit helps, and credit will always be given.

## Ways to Contribute

### Report Bugs

Report bugs at [github.com/chekos/pypums/issues](https://github.com/chekos/pypums/issues).

When reporting a bug, please include:

- Your operating system and Python version
- The exact code that produced the error
- The full traceback
- What you expected to happen

### Fix Bugs

Look through the [GitHub issues](https://github.com/chekos/pypums/issues) for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the [GitHub issues](https://github.com/chekos/pypums/issues) for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

### Write Documentation

PyPUMS can always use better documentation, whether it's improving existing guides, adding new examples, or writing blog posts.

### Submit Feedback

File an issue at [github.com/chekos/pypums/issues](https://github.com/chekos/pypums/issues).

If you're proposing a feature:

- Explain in detail how it would work
- Keep the scope as narrow as possible
- Remember that this is a volunteer-driven project

## Development Setup

1. Fork the [pypums repo](https://github.com/chekos/pypums) on GitHub.

2. Clone your fork locally:

    ```bash
    git clone git@github.com:your-username/pypums.git
    cd pypums
    ```

3. Install [uv](https://docs.astral.sh/uv/) and set up the project:

    ```bash
    uv sync --extra test
    ```

    For working on documentation:

    ```bash
    uv sync --extra docs
    ```

    For spatial features:

    ```bash
    uv sync --extra spatial
    ```

4. Create a branch for your changes:

    ```bash
    git checkout -b name-of-your-bugfix-or-feature
    ```

5. Make your changes and run the tests:

    ```bash
    uv run pytest
    ```

    Run specific test phases:

    ```bash
    uv run pytest -m phase0    # Foundation tests
    uv run pytest -m phase1    # Core data function tests
    uv run pytest -m phase2    # MOE, spatial, PUMS tests
    uv run pytest -m phase3    # Estimates, flows, survey tests
    ```

6. Check code style:

    ```bash
    uvx ruff check .
    uvx ruff format --check .
    ```

7. Commit your changes and push:

    ```bash
    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature
    ```

8. Submit a pull request through GitHub.

## Pull Request Guidelines

Before you submit a pull request:

1. The pull request should include tests.
2. If the pull request adds functionality, update the docs. Add a docstring to any new public function.
3. The pull request should work for Python 3.10+.
4. Make sure the tests pass by checking the GitHub Actions results.

## Code Style

- We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
- Target Python 3.10+
- NumPy-style docstrings for all public functions
- Type hints throughout
