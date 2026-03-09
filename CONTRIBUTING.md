# How to Contribute

To contribute to this library, first checkout the code. Then install [uv](https://docs.astral.sh/uv/) and set up the project:

```bash
cd pypums
uv sync --extra test
```

To run the tests:

```bash
uv run pytest
```

To run the linter:

```bash
uvx ruff check .
uvx ruff format --check .
```

## Before Submitting

Before submitting your code please do the following steps:

1. Add any changes you want
2. Add tests for the new changes
3. Edit documentation if you have changed something significant
4. Make sure all tests pass with `uv run pytest`
5. Make sure code style is clean with `uvx ruff check .`

## Other Help

You can contribute by spreading a word about this library. It would also be a huge contribution to write a short article on how you are using this project. You can also share your best practices with us.

See the full [contributing guide](https://chekos.github.io/pypums/about/contributing/) for more details.
