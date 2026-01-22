"""Command-line interface for json-mapper."""

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any

from json_mapper.transform import transform_from_mapping
from json_mapper.utils import load_json_file, save_json_file

# ############################################################
# CLI Arguments and Parser
# ############################################################


@dataclass
class CliArgs:
    """Dataclass representing parsed CLI arguments."""

    mapping: str
    input: str
    output: str | None = None
    indent: int = 2

    @classmethod
    def from_namespace(cls, args: argparse.Namespace) -> "CliArgs":
        """Create CliArgs from argparse.Namespace.

        Args:
            args: Parsed arguments from argparse

        Returns:
            CliArgs instance
        """
        return cls(
            mapping=args.mapping,
            input=args.input,
            output=args.output,
            indent=args.indent,
        )


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="json-mapper",
        description="Translate JSON values from one format to another using a declarative mapping config",  # noqa: E501
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
# Map a JSON file using a mapping config
json-mapper input.json -m mapping.json -o output.json

# Display version information
json-mapper --version""",
    )

    # Version argument
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    # Input file argument
    parser.add_argument("input", help="Input JSON file")

    # Mapping configuration
    parser.add_argument(
        "-m",
        "--mapping",
        required=True,
        help="Mapping configuration file (JSON format)",
    )

    # Output file
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")

    # Formatting options
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Number of spaces for JSON indentation (default: 2)",
    )

    return parser


# ############################################################
# Transformation Steps
# ############################################################


def load_mapping(args: CliArgs) -> dict[str, Any]:
    """Load the mapping configuration file.

    Args:
        args: Parsed CLI arguments

    Returns:
        Mapping configuration dictionary
    """
    return load_json_file(args.mapping)


def load_input(args: CliArgs) -> dict[str, Any]:
    """Load input data from file.

    Args:
        args: Parsed CLI arguments

    Returns:
        Input data dictionary
    """
    return load_json_file(args.input)


def transform_input(
    data: dict[str, Any],
    mapping: dict[str, Any],
) -> dict[str, Any]:
    """Transform input data using the mapping configuration.

    Args:
        data: Input data to transform
        mapping: Mapping configuration

    Returns:
        Transformed data dictionary
    """
    return transform_from_mapping(data, mapping)


def write_output(data: dict[str, Any], args: CliArgs) -> None:
    """Write output data to file or stdout.

    Args:
        data: Output data to write
        args: Parsed CLI arguments
    """
    if args.output:
        save_json_file(data, args.output, indent=args.indent)
    else:
        json.dump(data, sys.stdout, indent=args.indent)
        print()  # Add newline at the end


# ############################################################
# Main Entry Point
# ############################################################


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        # Parse arguments
        parser = create_parser()
        namespace = parser.parse_args()
        args = CliArgs.from_namespace(namespace)

        # load input data and mapping configuration
        mapping_config = load_mapping(args)
        input_data = load_input(args)

        # transform the input data using the mapping configuration
        output_data = transform_input(
            data=input_data,
            mapping=mapping_config,
        )

        # write the output data to the output file or stdout
        write_output(output_data, args)
        return 0

    # handle errors
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file - {e.msg}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
