"""Command-line interface for json-mapper."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json_file(file_path: str) -> dict[str, Any]:
    """Load and parse a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data as a dictionary

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with path.open("r") as f:
        data = json.load(f)
        if not isinstance(data, dict):
            raise TypeError(f"Expected JSON object, got {type(data).__name__}")
        return data


def save_json_file(data: dict[str, Any], file_path: str, indent: int = 2) -> None:
    """Save data to a JSON file.

    Args:
        data: Dictionary to save as JSON
        file_path: Path where the JSON file should be saved
        indent: Number of spaces for indentation (default: 2)
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w") as f:
        json.dump(data, f, indent=indent)


def map_json(input_data: dict[str, Any], mapping_config: dict[str, Any]) -> dict[str, Any]:
    """Map JSON data according to a mapping configuration.

    Args:
        input_data: The input JSON data to transform
        mapping_config: The mapping configuration that defines the transformation

    Returns:
        Transformed JSON data
    """
    # Placeholder implementation - this is where your mapping logic would go
    # For now, just return the input data
    return input_data


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
  json-mapper --version
        """,
    )

    # Version argument
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    # Input file argument
    parser.add_argument("input", nargs="?", help="Input JSON file (use '-' or omit for stdin)")

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
        "--compact", action="store_true", help="Output compact JSON (no indentation)"
    )

    # Verbose output
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    return parser


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()
    args = parser.parse_args()

    try:
        # Load mapping configuration
        if args.verbose:
            print(f"Loading mapping config from: {args.mapping}", file=sys.stderr)
        mapping_config = load_json_file(args.mapping)

        # Load input data
        if args.input and args.input != "-":
            if args.verbose:
                print(f"Loading input from: {args.input}", file=sys.stderr)
            input_data = load_json_file(args.input)
        else:
            if args.verbose:
                print("Reading input from stdin", file=sys.stderr)
            input_data = json.load(sys.stdin)

        # Perform the mapping
        if args.verbose:
            print("Performing JSON mapping...", file=sys.stderr)
        output_data = map_json(input_data, mapping_config)

        # Determine indentation
        indent = None if args.compact else args.indent

        # Write output
        if args.output:
            if args.verbose:
                print(f"Writing output to: {args.output}", file=sys.stderr)
            save_json_file(output_data, args.output, indent=indent or 2)
        else:
            json.dump(output_data, sys.stdout, indent=indent)
            print()  # Add newline at the end

        if args.verbose:
            print("Success!", file=sys.stderr)

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
