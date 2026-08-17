""" Tests for the documentation scanning tool."""
import sys
import os
# Add the project root to the import path so tests can import tools.scan.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the tool under test.
from tools.scan import scan_docs_structure # pylint: disable=wrong-import-position

def test_scan_docs_structure_finds_markdown_files(tmp_path):
    """ Test that scan_docs_structure finds markdown files in the given directory."""
    (tmp_path / "README.md").write_text("# Readme")
    (tmp_path / "notes.MD").write_text("# Notes")  # case-insensitive
    (tmp_path / "script.py").write_text("print('hello')")

    results = scan_docs_structure(str(tmp_path))

    assert len(results) == 2
    assert any("README.md" in path for path in results)
    assert any("notes.MD" in path for path in results)


def test_scan_docs_structure_ignores_unwanted_dirs(tmp_path):
    """ Test that scan_docs_structure ignores unwanted directories."""
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "ignored.md").write_text("ignore me")

    # Create valid file
    (tmp_path / "valid.md").write_text("valid")

    results = scan_docs_structure(str(tmp_path))

    assert len(results) == 1
    assert any("valid.md" in path for path in results)
    assert all("node_modules" not in path for path in results)


def test_scan_docs_structure_nested_directories(tmp_path):
    """ Test that scan_docs_structure finds markdown files in nested directories."""
    nested = tmp_path / "docs" / "guide"
    nested.mkdir(parents=True)
    (nested / "example.md").write_text("example")

    results = scan_docs_structure(str(tmp_path))

    assert len(results) == 1
    assert any("example.md" in path for path in results)


def test_scan_docs_structure_invalid_path():
    """ Test that scan_docs_structure handles invalid paths gracefully."""
    results = scan_docs_structure("non_existent_path")

    assert not results  # Should return an empty list for non-existent paths
