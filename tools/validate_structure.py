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
    Validate markdown structure with:
    - Core enforcement (affects score)
    - Optional warnings (no penalty)
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