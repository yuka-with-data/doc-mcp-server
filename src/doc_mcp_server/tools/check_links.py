""" Tool to check links in the documentation. """

import re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ==============================================================
# File Handling
# ===============================================================

def check_file_exists(file_path: str) -> bool:
    """
    Check if a file exists at the given path.
    Args:
        file_path (str): The path to the file.
    Returns:
        bool: True if the file exists, False otherwise.
    """
    # Verify that the provided path points to an existing file
    path = Path(file_path)

    # Return True only when the path exists and is a regular file.
    return path.is_file()

def read_documentation(file_path: str) -> str:
    """
    Read and return the content of a documentation file.
    Args:
        file_path (str): The path to the documentation file.
    Returns:
        str: The content of the file as a string.
    """
    path = Path(file_path)

    return path.read_text(encoding='utf-8')

# ==================================================================
# Link Extraction
# ==================================================================

def find_markdown_links(content: str) -> list[str]:
    """
    Find URLs contained in Markdown links.
    Args:
        content (str): The documentation content to search.
    Returns:
        list[str]: A list of URLs found inside Markdown links.
    """
    # Match Markdown links such as [Example](https://example.com).
    pattern = r"\[.*?\]\((https?://[^)\s]+|[^)\s]+)\)"

    # Return only the URL portion of each Markdown link.
    return re.findall(pattern, content)

def find_raw_urls(content: str) -> list[str]:
    """
    Find raw HTTP and HTTPS URLs in documentation.
    Args:
        content (str): The documentation content to search.
    Returns:
        list[str]: A list of raw HTTP and HTTPS URLs found.
    """
    # Match URLs written directly in the documentation.
    pattern = r"https?://[^\s<>\"]+"

    # Return every raw HTTP or HTTPS URL found.
    return re.findall(pattern, content)

# =========================================================
# Link Classification
# ======================================================

def classify_link(link: str) -> str:
    """
    Determine whether a link is an external URL or a local path.
    Args:
        link (str): The link to classify.
    Returns:
        str: "external" for HTTP/HTTPS URLs, or "local" for local paths.
    """
    # Parse the link so we can inspect its URL scheme.
    parsed_link = urlparse(link)

    # HTTP and HTTPS links point to external web resources.
    if parsed_link.scheme in ("http", "https"):
        return "external"

    # Links without an HTTP/HTTPS scheme are treated as local paths.
    return "local"

# ==============================================================
# Link Checking
# =============================================================

def check_local_link(link: str, documentation_file: str) -> str:
    """
    Check whether a local documentation link points to an existing file.
    Args:
        link (str): The local file path referenced by the documentation.
        documentation_file (str): The path to the documentation file containing the link.
    Returns:
        str: "valid" if the linked file exists, otherwise "broken".
    """
    # Resolve the documentation file so relative links are based on its directory.
    documentation_path = Path(documentation_file).resolve()

    # Build the full path to the linked local file.
    target_path = documentation_path.parent / link

    # Return a status string consistent with the external link checker.
    if target_path.is_file():
        return "valid"

    # The target does not exist, so the link is broken.
    return "broken"

def check_external_link(link: str, timeout: int = 10) -> str:
    """
    Check whether an external URL can be reached.
    Args:
        link (str): The HTTP or HTTPS URL to check.
        timeout (int): Maximum number of seconds to wait for a response.
    Returns:
        str: "valid" if the URL responds successfully,
            "broken" if the server returns an HTTP error,
            or "unverified" if the URL could not be reached.
    """
    # Create a request with a user agent so servers can identify the request.
    request = Request(link, headers={"User-Agent": "doc-mcp-server-link-checker"})

    try:
        # Send the request and follow redirects automatically.
        with urlopen(request, timeout=timeout) as response:
            # Treat successful 2xx and redirected 3xx responses as valid.
            if 200 <= response.status < 400:
                return "valid"

    # A server response such as 404 or 500 indicates a broken link.
    except HTTPError:
        return "broken"

    # Connection, DNS, timeout, or other URL errors cannot be verified.
    except URLError:
        return "unverified"

    return "unverified"

# =============================================================
# Link Normalization
# ============================================================

def normalize_links(markdown_links: list[str], raw_urls: list[str]) -> list[str]:
    """
    Combine and deduplicate Markdown links and raw URLs.
    Args:
        markdown_links (list[str]): URLs found inside Markdown links.
        raw_urls (list[str]): URLs found directly in the documentation.
    Returns:
        list[str]: A deduplicated list of links.
    """
    # Combine both types of discovered links into one list.
    all_links = markdown_links + raw_urls

    # Remove duplicates while preserving the original order.
    return list(dict.fromkeys(all_links))

# =================================================================
# Main Link Checking Workflow
# ==================================================================

def check_links(file_path: str) -> dict:
    """
    Check all links found in a documentation file.
    Args:
        file_path (str): The path to the documentation file.
    Returns:
        dict: A structured report containing link-checking results.
    """
    # Stop early if the documentation file does not exist.
    if not check_file_exists(file_path):
        return {
            "file": file_path,
            "error": "Documentation file does not exist.",
        }

    # Read the documentation so we can extract its links.
    content = read_documentation(file_path)

    # Find both Markdown links and raw URLs in the documentation.
    markdown_links = find_markdown_links(content)
    raw_urls = find_raw_urls(content)

    # Combine the discovered links and remove duplicates.
    links = normalize_links(markdown_links, raw_urls)

    # Store the result for each link.
    details = []

    # Check every discovered link according to its type.
    for link in links:
        link_type = classify_link(link)

        # Use the appropriate checker based on the link type.
        if link_type == "external":
            status = check_external_link(link)
        else:
            status = check_local_link(link, file_path)

        # Record the link, its type, and its checking result.
        details.append({
            "link": link,
            "type": link_type,
            "status": status,
        })

    # Count the number of links in each status category.
    valid_count = sum(detail["status"] == "valid" for detail in details)
    broken_count = sum(detail["status"] == "broken" for detail in details)
    unverified_count = sum(
        detail["status"] == "unverified" for detail in details
    )

    # Return a structured report containing summary and detailed results.
    return {
        "file": file_path,
        "total_links": len(details),
        "valid": valid_count,
        "broken": broken_count,
        "unverified": unverified_count,
        "details": details,
    }
