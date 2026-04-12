""" 
This module provides a function to validate the structural quality and integrity of a markdown document. 
It checks for the presence and content of core sections (Installation, Usage, Example) and optional sections (Overview, Requirements, Contributing, License). 
The validation results include a score and lists of any critical errors or warnings found in the document.

Scoring:
    - Starts from 100
    - -20 for each missing core section
    - -10 for each empty core section
    - Minimum score is 0

Args:
    file_path (str): The path to the markdown file to validate.

Returns:
    dict: A dictionary containing the validation results, including:
        - file: The path of the validated file.
        - score: A numerical score (0-100) representing the structural quality.
        - errors: A dictionary of critical issues found (missing/empty core sections).
        - warnings: A dictionary of non-critical issues (missing/empty optional sections).
 """

import re

# Define core sections that must be present and non-empty
CORE_SECTIONS = ["Installation", "Usage", "Example"]
# Define optional sections that are nice to have but not mandatory
OPTIONAL_SECTIONS = ["Overview", "Requirements", "Contributing", "License"]


def _extract_sections(content: str) -> dict:
    """
    Internal helper fuction
    Extract markdown sections into a dict:
    {
        "Section Name": "content under that section"
    }
    """
    sections = {}
    current_section = None
    buffer = []

    lines = content.splitlines()

    for line in lines:
        match = re.match(r"^##\s+(.*)", line)

        if match:
            if current_section:
                sections[current_section] = "\n".join(buffer).strip()
                buffer = []

            current_section = match.group(1).strip()
        else:
            if current_section:
                buffer.append(line)

    if current_section:
        sections[current_section] = "\n".join(buffer).strip()

    return sections


def validate_structure(file_path: str) -> dict:
    """
    Validate the structural quality and integrity of the markdown document.
    - Core sectiopn (Installation, Usage, Example)
    - Optional sections (Overview, Requirements, Contributing, License)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {
            "file": file_path,
            "error": str(e)
        }

    sections = _extract_sections(content)

    missing_core = []
    empty_core = []

    missing_optional = []
    empty_optional = []

    # --- Check CORE sections (strict) ---
    for required in CORE_SECTIONS:
        found = False

        for section_name in sections.keys():
            if required.lower() in section_name.lower():
                found = True

                if not sections[section_name] or sections[section_name].lower() in ["todo", "tbd"]:
                    empty_core.append(section_name)

        if not found:
            missing_core.append(required)

    # --- Check OPTIONAL sections (warnings only) ---
    for optional in OPTIONAL_SECTIONS:
        found = False

        for section_name in sections.keys():
            if optional.lower() in section_name.lower():
                found = True

                if not sections[section_name] or sections[section_name].lower() in ["todo", "tbd"]:
                    empty_optional.append(section_name)

        if not found:
            missing_optional.append(optional)

    # --- Scoring (CORE only) ---
    score = 100
    score -= 20 * len(missing_core)
    score -= 10 * len(empty_core)
    score = max(score, 0)

    return {
        "file": file_path,
        "score": score,
        "errors": {
            "missing_core_sections": missing_core,
            "empty_core_sections": empty_core
        },
        "warnings": {
            "missing_optional_sections": missing_optional,
            "empty_optional_sections": empty_optional
        }
    }