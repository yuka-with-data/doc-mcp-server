import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools.validate_structure import validate_structure


def test_missing_core_sections(tmp_path):
    file = tmp_path / "README.md"
    file.write_text("# Project\n\n## Usage\nSome usage here")

    result = validate_structure(str(file))

    assert "Installation" in result["errors"]["missing_core_sections"]
    assert "Example" in result["errors"]["missing_core_sections"]
    assert result["score"] < 100


def test_empty_core_section(tmp_path):
    file = tmp_path / "README.md"
    file.write_text("""
# Project

## Installation
TODO

## Usage
Valid usage content

## Example
Example here
""")

    result = validate_structure(str(file))

    assert "Installation" in result["errors"]["empty_core_sections"]
    assert result["score"] < 100


def test_optional_sections_warning(tmp_path):
    file = tmp_path / "README.md"
    file.write_text("""
# Project

## Installation
Install steps

## Usage
Usage steps

## Example
Example here
""")

    result = validate_structure(str(file))

    # Optional sections should appear as warnings
    assert "Overview" in result["warnings"]["missing_optional_sections"]
    assert "License" in result["warnings"]["missing_optional_sections"]

    # Score should NOT be penalized
    assert result["score"] == 100


def test_all_sections_present(tmp_path):
    file = tmp_path / "README.md"
    file.write_text("""
# Project

## Overview
Intro

## Installation
Install steps

## Usage
Usage steps

## Example
Example here

## Requirements
Python 3.10+

## Contributing
PRs welcome

## License
MIT
""")

    result = validate_structure(str(file))

    assert result["score"] == 100
    assert result["errors"]["missing_core_sections"] == []
    assert result["errors"]["empty_core_sections"] == []


def test_file_read_error():
    result = validate_structure("non_existent_file.md")

    assert "error" in result


def test_score_calculation(tmp_path):
    file = tmp_path / "README.md"
    file.write_text("""
# Project

## Usage
Some usage

## Example
Example here
""")

    result = validate_structure(str(file))

    # Missing: Installation → -20
    # No empty sections
    expected_score = 80

    assert result["score"] == expected_score

def test_flexible_section_names(tmp_path):
    # Edge case
    file = tmp_path / "README.md"
    file.write_text("""
# Project

## Installation Guide
Steps here

## Usage Instructions
How to use

## Example Usage
Example here
""")

    result = validate_structure(str(file))

    # Should NOT count as missing (fuzzy match works)
    assert result["errors"]["missing_core_sections"] == []
    assert result["score"] == 100