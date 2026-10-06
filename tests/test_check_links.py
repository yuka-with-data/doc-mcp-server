"""
Tests for the documentation link checker.
"""

from pathlib import Path
import pytest
from doc_mcp_server.tools.check_links import (
    check_external_link,
    check_file_exists,
    check_links,
    check_local_link,
    classify_link,
    find_markdown_links,
    find_raw_urls,
    normalize_links,
    read_documentation,
)

# ============================================================================
# File Handling Tests
# ============================================================================

def test_check_file_exists(tmp_path: Path) -> None:
    """
    Test that check_file_exists() correctly identifies existing files.
    Args:
        tmp_path (Path): Pytest fixture providing a temporary directory.
    """

    # Create a temporary documentation file for the test.
    documentation_file = tmp_path / "README.md"
    documentation_file.write_text("# Test Documentation", encoding="utf-8")

    # Verify that the function recognizes the existing file.
    assert check_file_exists(str(documentation_file)) is True


def test_check_file_exists_missing_file(tmp_path: Path) -> None:
    """
    Test that check_file_exists() returns False for a missing file.
    Args:
        tmp_path (Path): Pytest fixture providing a temporary directory.
    """

    # Create a path to a file that does not exist.
    documentation_file = tmp_path / "missing.md"

    # Verify that the function recognizes the missing file.
    assert check_file_exists(str(documentation_file)) is False


def test_read_documentation(tmp_path: Path) -> None:
    """
    Test that read_documentation() correctly reads file content.
    Args:
        tmp_path (Path): Pytest fixture providing a temporary directory.
    """

    # Create a temporary documentation file with known content.
    documentation_file = tmp_path / "README.md"
    documentation_file.write_text(
        "# Test Documentation\n\nThis is a test.",
        encoding="utf-8",
    )

    # Read the documentation using the function under test.
    content = read_documentation(str(documentation_file))

    # Verify that the returned content matches the original file.
    assert content == "# Test Documentation\n\nThis is a test."


# ============================================================================
# Link Extraction Tests
# ============================================================================

def test_find_markdown_links() -> None:
    """
    Test that Markdown links are correctly extracted.
    """

    # Provide documentation containing two Markdown links.
    content = (
        "[Python](https://python.org) "
        "[GitHub](https://github.com)"
    )

    # Extract the Markdown links from the documentation.
    links = find_markdown_links(content)

    # Verify that both URLs were found.
    assert links == ["https://python.org", "https://github.com"]


def test_find_raw_urls() -> None:
    """
    Test that raw HTTP and HTTPS URLs are correctly extracted.
    """

    # Provide documentation containing raw URLs.
    content = "Visit https://python.org and https://github.com for more information."

    # Extract the raw URLs from the documentation.
    links = find_raw_urls(content)

    # Verify that both URLs were found.
    assert links == ["https://python.org", "https://github.com"]


def test_find_links_with_no_links() -> None:
    """
    Test that link extraction returns an empty list when no links exist.
    """

    # Provide documentation without any links.
    content = "# Documentation\n\nThere are no links here."

    # Run both link extraction functions.
    markdown_links = find_markdown_links(content)
    raw_urls = find_raw_urls(content)

    # Verify that neither function found any links.
    assert markdown_links == []
    assert raw_urls == []


# ============================================================================
# Link Classification Tests
# ============================================================================

def test_classify_external_link() -> None:
    """
    Test that HTTP and HTTPS URLs are classified as external links.
    """

    # Verify that HTTP URLs are classified as external.
    assert classify_link("http://example.com") == "external"

    # Verify that HTTPS URLs are classified as external.
    assert classify_link("https://example.com") == "external"


def test_classify_local_link() -> None:
    """
    Test that local paths are classified as local links.
    """

    # Verify that a relative file path is classified as local.
    assert classify_link("docs/guide.md") == "local"


# ============================================================================
# Link Checking Tests
# ============================================================================

def test_check_local_link_valid(tmp_path: Path) -> None:
    """
    Test that check_local_link() identifies an existing local file.
    Args:
        tmp_path (Path): Pytest fixture providing a temporary directory.
    """

    # Create the documentation file and its linked target file.
    documentation_file = tmp_path / "README.md"
    linked_file = tmp_path / "guide.md"

    documentation_file.write_text("# Documentation", encoding="utf-8")
    linked_file.write_text("# Guide", encoding="utf-8")

    # Check the local link from the documentation file.
    result = check_local_link("guide.md", str(documentation_file))

    # Verify that the existing target is considered valid.
    assert result == "valid"


def test_check_local_link_broken(tmp_path: Path) -> None:
    """
    Test that check_local_link() identifies a missing local file.
    Args:
        tmp_path (Path): Pytest fixture providing a temporary directory.
    """

    # Create the documentation file without creating its linked target.
    documentation_file = tmp_path / "README.md"
    documentation_file.write_text("# Documentation", encoding="utf-8")

    # Check the missing local link.
    result = check_local_link("missing.md", str(documentation_file))

    # Verify that the missing target is considered broken.
    assert result == "broken"


def test_check_external_link_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that check_external_link() identifies a successful response.
    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest fixture for replacing objects.
    """

    class MockResponse:
        """Provide a minimal mock HTTP response."""

        status = 200

        def __enter__(self):
            # Return the mock response when entering the context manager.
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            # Do not suppress exceptions raised inside the context manager.
            return False

    def mock_urlopen(*args, **kwargs):
        # Return a successful mock response without making a network request.
        return MockResponse()

    # Replace urlopen with the controlled mock function.
    monkeypatch.setattr(
        "doc_mcp_server.tools.check_links.urlopen",
        mock_urlopen,
    )

    # Check the external URL.
    result = check_external_link("https://example.com")

    # Verify that a successful response is considered valid.
    assert result == "valid"


def test_check_external_link_broken(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that check_external_link() identifies an HTTP error.
    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest fixture for replacing objects.
    """

    def mock_urlopen(*args, **kwargs):
        # Simulate a server returning an HTTP error such as 404.
        from urllib.error import HTTPError

        raise HTTPError(
            "https://example.com",
            404,
            "Not Found",
            {},
            None,
        )

    # Replace urlopen with the controlled error-producing mock.
    monkeypatch.setattr(
        "doc_mcp_server.tools.check_links.urlopen",
        mock_urlopen,
    )

    # Check the external URL.
    result = check_external_link("https://example.com/missing")

    # Verify that the HTTP error is considered broken.
    assert result == "broken"


def test_check_external_link_unverified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Test that check_external_link() handles connection errors.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest fixture for replacing objects.
    """

    from urllib.error import URLError

    def mock_urlopen(*args, **kwargs):
        # Simulate a network failure such as a connection or DNS error.
        raise URLError("Connection failed")

    # Replace urlopen with the controlled error-producing mock.
    monkeypatch.setattr(
        "doc_mcp_server.tools.check_links.urlopen",
        mock_urlopen,
    )

    # Check the external URL.
    result = check_external_link("https://example.com")

    # Verify that the failed request is considered unverified.
    assert result == "unverified"


# ============================================================================
# Link Normalization Tests
# ============================================================================

def test_normalize_links() -> None:
    """
    Test that links are combined and duplicates are removed.
    """

    # Provide overlapping Markdown and raw URL lists.
    markdown_links = [
        "https://python.org",
        "https://github.com",
    ]
    raw_urls = [
        "https://github.com",
        "https://example.com",
    ]

    # Normalize and deduplicate the links.
    links = normalize_links(markdown_links, raw_urls)

    # Verify that duplicates are removed while order is preserved.
    assert links == [
        "https://python.org",
        "https://github.com",
        "https://example.com",
    ]


# ============================================================================
# Main Workflow Tests
# ============================================================================

def test_check_links(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test the complete documentation link-checking workflow.

    Args:
        tmp_path (Path): Pytest fixture providing a temporary directory.
        monkeypatch (pytest.MonkeyPatch): Pytest fixture for replacing objects.
    """

    # Create a local documentation file and a valid local target.
    documentation_file = tmp_path / "README.md"
    linked_file = tmp_path / "guide.md"

    linked_file.write_text("# Guide", encoding="utf-8")

    # Include both a valid local link and an external link.
    documentation_file.write_text(
        "# Documentation\n\n"
        "[Guide](guide.md)\n\n"
        "https://example.com",
        encoding="utf-8",
    )

    class MockResponse:
        """Provide a minimal mock HTTP response."""

        status = 200

        def __enter__(self):
            # Return the mock response when entering the context manager.
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            # Do not suppress exceptions raised inside the context manager.
            return False

    def mock_urlopen(*args, **kwargs):
        # Return a successful mock response without making a network request.
        return MockResponse()

    # Replace external HTTP requests with the controlled mock.
    monkeypatch.setattr(
        "doc_mcp_server.tools.check_links.urlopen",
        mock_urlopen,
    )

    # Run the complete link-checking workflow.
    result = check_links(str(documentation_file))

    # Verify the overall link counts.
    assert result["total_links"] == 2
    assert result["valid"] == 2
    assert result["broken"] == 0
    assert result["unverified"] == 0

    # Verify the detailed results.
    assert len(result["details"]) == 2


def test_check_links_missing_file(tmp_path: Path) -> None:
    """
    Test the complete workflow with a missing documentation file.

    Args:
        tmp_path (Path): Pytest fixture providing a temporary directory.
    """

    # Create a path to a documentation file that does not exist.
    documentation_file = tmp_path / "missing.md"

    # Run the complete link-checking workflow.
    result = check_links(str(documentation_file))

    # Verify that the workflow returns an appropriate error.
    assert result["file"] == str(documentation_file)
    assert "error" in result
