"""Tests for the CLI module."""

import pytest

from json_mapper.cli import (
    CliArgs,
    create_parser,
    load_input,
    load_mapping,
    transform_input,
)


class TestLoadMapping:
    """Tests for load_mapping function."""

    def test_load_mapping(self, tmp_path) -> None:
        """Test loading a mapping configuration file."""
        import json

        mapping_file = tmp_path / "mapping.json"
        mapping_data = {"field1": {"field": "source_field"}}
        mapping_file.write_text(json.dumps(mapping_data))

        args = CliArgs(mapping=str(mapping_file))
        result = load_mapping(args)

        assert result == mapping_data


class TestLoadInput:
    """Tests for load_input function."""

    def test_load_input_from_file(self, tmp_path) -> None:
        """Test loading input from a file."""
        import json

        input_file = tmp_path / "input.json"
        input_data = {"key": "value"}
        input_file.write_text(json.dumps(input_data))

        args = CliArgs(mapping="mapping.json", input=str(input_file))
        result = load_input(args)

        assert result == input_data


class TestTransformInput:
    """Tests for transform_input function."""

    def test_transform_input(self) -> None:
        """Test transforming input data with a mapping."""
        input_data = {"source_field": "test_value"}
        mapping = {"target_field": {"field": "source_field"}}

        result = transform_input(input_data, mapping)

        assert result == {"target_field": "test_value"}


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


class TestCliArgs:
    """Tests for CliArgs dataclass."""

    def test_from_namespace(self) -> None:
        """Test creating CliArgs from argparse Namespace."""
        parser = create_parser()
        namespace = parser.parse_args(["-m", "mapping.json", "input.json"])
        args = CliArgs.from_namespace(namespace)

        assert args.mapping == "mapping.json"
        assert args.input == "input.json"
        assert args.output is None
        assert args.indent == 2
        assert not args.compact
        assert not args.verbose

    def test_from_namespace_all_options(self) -> None:
        """Test creating CliArgs with all options."""
        parser = create_parser()
        namespace = parser.parse_args(
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
        args = CliArgs.from_namespace(namespace)

        assert args.mapping == "mapping.json"
        assert args.input == "input.json"
        assert args.output == "output.json"
        assert args.indent == 4
        assert args.compact
        assert args.verbose
