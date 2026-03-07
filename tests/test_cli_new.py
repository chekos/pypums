"""Tests for new CLI commands."""

import re
from unittest.mock import patch

import pandas as pd
from typer.testing import CliRunner

from pypums import cli

runner = CliRunner()


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


class TestConfigCommand:
    def test_config_set_key(self):
        result = runner.invoke(cli.cli, ["config", "test_key_12345"])
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "Census API key set successfully" in output


class TestAcsCommand:
    def test_acs_command_exists(self):
        result = runner.invoke(cli.cli, ["acs", "--help"])
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "Fetch ACS data" in output

    def test_acs_command_calls_get_acs(self):
        mock_df = pd.DataFrame(
            {
                "GEOID": ["06037"],
                "NAME": ["LA County"],
                "variable": ["B01001_001"],
                "estimate": [100],
            }
        )
        with patch("pypums.acs.get_acs", return_value=mock_df):
            result = runner.invoke(
                cli.cli,
                [
                    "acs",
                    "county",
                    "--variables",
                    "B01001_001",
                    "--state",
                    "CA",
                    "--key",
                    "fake",
                ],
            )
        assert result.exit_code == 0


class TestDecennialCommand:
    def test_decennial_command_exists(self):
        result = runner.invoke(cli.cli, ["decennial", "--help"])
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "Fetch Decennial" in output


class TestVariablesCommand:
    def test_variables_command_exists(self):
        result = runner.invoke(cli.cli, ["variables", "--help"])
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "Search" in output or "variables" in output.lower()


class TestEstimatesCommand:
    def test_estimates_command_exists(self):
        result = runner.invoke(cli.cli, ["estimates", "--help"])
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "estimates" in output.lower()
