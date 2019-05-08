#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pypums` package."""


import unittest
from click.testing import CliRunner

from pypums import pypums
from pypums import cli


class TestPypums(unittest.TestCase):
    """Tests for `pypums` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert "Download complete!" in result.output
        help_result = runner.invoke(cli.main, ["--help"])
        assert help_result.exit_code == 0
        assert "Usage: main [OPTIONS]\n\n  Download" in help_result.output
