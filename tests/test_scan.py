# tests/test_scan.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools.scan import scan_docs_structure

def test_scan_docs_structure_finds_markdown_files(tmp_path):
    # Create test files
    (tmp_path / "README.md").write_text("# Readme")
    (tmp_path / "notes.MD").write_text("# Notes")  # case-insensitive
    (tmp_path / "script.py").write_text("print('hello')")

    results = scan_docs_structure(str(tmp_path))

    assert len(results) == 2
    assert any("README.md" in path for path in results)
    assert any("notes.MD" in path for path in results)


def test_scan_docs_structure_ignores_unwanted_dirs(tmp_path):
    # Create ignored directory
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
    nested = tmp_path / "docs" / "guide"
    nested.mkdir(parents=True)
    (nested / "example.md").write_text("example")

    results = scan_docs_structure(str(tmp_path))

    assert len(results) == 1
    assert any("example.md" in path for path in results)


def test_scan_docs_structure_invalid_path():
    results = scan_docs_structure("non_existent_path")

    # Depending on your implementation, adjust this if needed
    assert results == []