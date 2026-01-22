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
    input: str | None = None
    output: str | None = None
    indent: int = 2
    compact: bool = False
    verbose: bool = False

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
            compact=args.compact,
            verbose=args.verbose,
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

# Map JSON from stdin and output to stdout
cat input.json | json-mapper -m mapping.json

# Display version information
json-mapper --version""",
    )

    # Version argument
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    # Input file argument
    parser.add_argument(
        "input", nargs="?", help="Input JSON file (use '-' or omit for stdin)"
    )

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

    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output compact JSON (no indentation)",
    )

    # Verbose output
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
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
    if args.verbose:
        print(f"Loading mapping config from: {args.mapping}", file=sys.stderr)
    return load_json_file(args.mapping)


def load_input(args: CliArgs) -> dict[str, Any]:
    """Load input data from file or stdin.

    Args:
        args: Parsed CLI arguments

    Returns:
        Input data dictionary
    """
    if args.input and args.input != "-":
        if args.verbose:
            print(f"Loading input from: {args.input}", file=sys.stderr)
        return load_json_file(args.input)
    else:
        if args.verbose:
            print("Reading input from stdin", file=sys.stderr)
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise TypeError(f"Expected JSON object, got {type(data).__name__}")
        return data


def transform_input(
    data: dict[str, Any],
    mapping: dict[str, Any],
    verbose: bool = False,
) -> dict[str, Any]:
    """Transform input data using the mapping configuration.

    Args:
        data: Input data to transform
        mapping: Mapping configuration
        verbose: Whether to print verbose output

    Returns:
        Transformed data dictionary
    """
    if verbose:
        print("Performing JSON mapping...", file=sys.stderr)
    return transform_from_mapping(data, mapping)


def write_output(data: dict[str, Any], args: CliArgs) -> None:
    """Write output data to file or stdout.

    Args:
        data: Output data to write
        args: Parsed CLI arguments
    """
    indent = None if args.compact else args.indent

    if args.output:
        if args.verbose:
            print(f"Writing output to: {args.output}", file=sys.stderr)
        save_json_file(data, args.output, indent=indent or 2)
    else:
        json.dump(data, sys.stdout, indent=indent)
        print()  # Add newline at the end


# ############################################################
# Run CLI
# ############################################################


def run_cli(args: CliArgs) -> int:
    """Execute the CLI logic with parsed arguments.

    Args:
        args: Parsed CLI arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        mapping_config = load_mapping(args)
        input_data = load_input(args)
        output_data = transform_input(
            data=input_data,
            mapping=mapping_config,
            verbose=args.verbose,
        )
        write_output(output_data, args)

        if args.verbose:
            print("Success!", file=sys.stderr)

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        return 1
    except TypeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


# ############################################################
# Main Entry Point
# ############################################################


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()
    namespace = parser.parse_args()
    args = CliArgs.from_namespace(namespace)
    return run_cli(args)


if __name__ == "__main__":
    sys.exit(main())
