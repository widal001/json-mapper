"""Tests for the utils module."""

import json
from pathlib import Path

import pytest

from json_mapper.utils import load_json_file, save_json_file


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

    def test_load_non_object_json(self, tmp_path: Path) -> None:
        """Test loading JSON that is not an object."""
        test_file = tmp_path / "array.json"
        test_file.write_text("[1, 2, 3]")

        with pytest.raises(TypeError, match="Expected JSON object"):
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

    def test_save_with_custom_indent(self, tmp_path: Path) -> None:
        """Test saving JSON with custom indentation."""
        test_file = tmp_path / "output.json"
        test_data = {"key": "value"}

        save_json_file(test_data, str(test_file), indent=4)

        content = test_file.read_text()
        # Check that the file is indented with 4 spaces
        assert '    "key"' in content
