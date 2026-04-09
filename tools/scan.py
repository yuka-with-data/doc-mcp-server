import os
from typing import List

def scan_docs_structure(repo_path: str) -> List[str]:
    """
    Scan a repository and return all Markdown files.
    Args:
        repo_path (str): The path to the repository.
    Returns:
        List[str]: A list of paths to Markdown files.

    Expected Ouput:
    [
        "repo_path/docs/file1.md",
        "repo_path/docs/subdir/file2.md",
        ...
    ]
    """
    md_files = []

    if not os.path.exists(repo_path):
        return []
    
    for root, dirs, files in os.walk(repo_path):
        # Skip common unwanted directories
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]

        for file in files:
            if file.lower().endswith('.md'):
                full_path = os.path.join(root, file)
                md_files.append(os.path.join(root, file))

    return md_files
    