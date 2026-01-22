"""Tests for the CLI module."""

import json
import tempfile
from pathlib import Path

import pytest

from json_mapper.cli import load_json_file, save_json_file, map_json, create_parser


class TestLoadJsonFile:
    """Tests for load_json_file function."""

    def test_load_valid_json(self, tmp_path: Path) -> None:
        """Test loading a valid JSON file."""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "number": 42}
        test_file.write_text(json.dumps(test_data))

        result = load_json_file(str(test_file))
        assert result == test_data

    def test_load_nonexistent_file(self) -> None:
        """Test loading a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_json_file("nonexistent.json")

    def test_load_invalid_json(self, tmp_path: Path) -> None:
        """Test loading a file with invalid JSON."""
        test_file = tmp_path / "invalid.json"
        test_file.write_text("not valid json {")

        with pytest.raises(json.JSONDecodeError):
            load_json_file(str(test_file))


class TestSaveJsonFile:
    """Tests for save_json_file function."""

    def test_save_json(self, tmp_path: Path) -> None:
        """Test saving JSON to a file."""
        test_file = tmp_path / "output.json"
        test_data = {"key": "value", "nested": {"data": [1, 2, 3]}}

        save_json_file(test_data, str(test_file))

        assert test_file.exists()
        loaded_data = json.loads(test_file.read_text())
        assert loaded_data == test_data

    def test_save_creates_directories(self, tmp_path: Path) -> None:
        """Test that save_json_file creates parent directories."""
        test_file = tmp_path / "subdir" / "nested" / "output.json"
        test_data = {"test": "data"}

        save_json_file(test_data, str(test_file))

        assert test_file.exists()
        assert test_file.parent.exists()


class TestMapJson:
    """Tests for map_json function."""

    def test_map_json_placeholder(self) -> None:
        """Test the placeholder map_json implementation."""
        input_data = {"key": "value"}
        mapping_config = {"fields": {}}

        result = map_json(input_data, mapping_config)

        # Currently just returns input data unchanged
        assert result == input_data


class TestCreateParser:
    """Tests for create_parser function."""

    def test_parser_creation(self) -> None:
        """Test that parser is created successfully."""
        parser = create_parser()
        assert parser.prog == "json-mapper"

    def test_parser_required_arguments(self) -> None:
        """Test that mapping argument is required."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_parser_with_mapping(self) -> None:
        """Test parser with required mapping argument."""
        parser = create_parser()
        args = parser.parse_args(["-m", "mapping.json"])

        assert args.mapping == "mapping.json"
        assert args.input is None
        assert args.output is None
        assert not args.verbose
        assert not args.compact

    def test_parser_all_arguments(self) -> None:
        """Test parser with all arguments."""
        parser = create_parser()
        args = parser.parse_args(
            [
                "input.json",
                "-m",
                "mapping.json",
                "-o",
                "output.json",
                "-v",
                "--compact",
                "--indent",
                "4",
            ]
        )

        assert args.input == "input.json"
        assert args.mapping == "mapping.json"
        assert args.output == "output.json"
        assert args.verbose
        assert args.compact
        assert args.indent == 4
