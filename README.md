# JSON Mapper

A Python CLI tool that translates JSON values from one format to another using a declarative mapping configuration.

## Installation

```bash
# Install with poetry
poetry install

# Or install in development mode
pip install -e .
```

## Usage

### Basic Usage

```bash
# Map a JSON file using a mapping configuration
json-mapper input.json -m mapping.json -o output.json

# Read from stdin, write to stdout
cat input.json | json-mapper -m mapping.json

# Use verbose mode to see what's happening
json-mapper input.json -m mapping.json -o output.json -v
```

### Command-Line Options

```
positional arguments:
  input                 Input JSON file (use '-' or omit for stdin)

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -m MAPPING, --mapping MAPPING
                        Mapping configuration file (JSON format)
  -o OUTPUT, --output OUTPUT
                        Output file (default: stdout)
  --indent INDENT       Number of spaces for JSON indentation (default: 2)
  --compact             Output compact JSON (no indentation)
  -v, --verbose         Enable verbose output
```

## Examples

### Example 1: Simple JSON Mapping

**input.json:**
```json
{
  "name": "John Doe",
  "age": 30,
  "email": "john@example.com"
}
```

**mapping.json:**
```json
{
  "fields": {
    "name": "fullName",
    "email": "emailAddress"
  }
}
```

**Command:**
```bash
json-mapper input.json -m mapping.json -o output.json
```

### Example 2: Pipeline Usage

```bash
# Use in a data processing pipeline
curl https://api.example.com/data.json | json-mapper -m mapping.json | jq '.results'
```

## Development

### Quick Start

```bash
# Install dependencies
make install

# Run all checks (formatting, linting, type-checking, and tests with coverage)
make checks
```

### Individual Commands

```bash
# Format code with black
make format

# Lint code with ruff
make lint

# Run type checking with mypy
make type-check

# Run tests
make test

# Run tests with coverage report
make test-cov

# Clean build artifacts
make clean
```

### Manual Commands

If you prefer to run commands directly:

```bash
# Format code
poetry run black json_mapper/

# Lint code
poetry run ruff check json_mapper/

# Type check
poetry run mypy json_mapper/

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=json_mapper --cov-report=term-missing --cov-report=html
```

## Project Structure

```
sample-python-tool/
├── json_mapper/
│   ├── __init__.py       # Package initialization
│   └── cli.py            # CLI implementation with argparse
├── pyproject.toml        # Project configuration and dependencies
├── poetry.lock           # Locked dependencies
└── README.md            # This file
```

## License

MIT
