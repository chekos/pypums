import re

import pytest
from typer.testing import CliRunner

from pypums import __app_name__, __version__, cli

runner = CliRunner()


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


@pytest.mark.parametrize(
    "options",
    (
        ["-v"],
        ["--version"],
    ),
)
def test_version(options):
    result = CliRunner().invoke(cli.cli, options)
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}" in result.output


@pytest.mark.parametrize(
    "options",
    (["--help"],),
)
def test_help(options):
    result = CliRunner().invoke(cli.cli, options)
    output = strip_ansi(result.output)
    assert result.exit_code == 0
    assert "Usage:" in output
    assert "--help" in output
