"""
Parser module: converts a raw backoffice copy-paste dump (Ctrl+A)
into a structured ParsedGuideline object, stripping UI noise,
sidebar navigation, and technical metadata not needed for validation.
"""

from dataclasses import dataclass, field


# Sidebar navigation items that always appear at the end of a raw dump.
# Used as an anchor to cut off everything from "Backoffice" onward.
SIDEBAR_MARKER = "Backoffice"

# UI labels that precede a field value on their own line.
FIELD_LABELS = [
    "Title",
    "Payer",
    "Organization",
    "Source",
    "Status",
    "Guideline ID",
    "Guideline Version",
    "Algorithm Version",
    "Prompt Version",
    "URL",
]

CODE_SECTION_HEADERS = ["CPT Codes", "HCPCS Codes", "ICD-10 Codes"]


@dataclass
class ParsedGuideline:
    title: str = ""
    payer: str = ""
    guideline_id: str = ""
    source_url: str = ""
    cpt_codes: list[str] = field(default_factory=list)
    hcpcs_codes: list[str] = field(default_factory=list)
    icd10_codes: list[str] = field(default_factory=list)
    markdown_content: str = ""
    decision_tree_raw: str = ""
    parsing_warnings: list[str] = field(default_factory=list)


def strip_sidebar(raw_text: str) -> str:
    """Remove the backoffice sidebar navigation block from the end of the dump."""
    marker_index = raw_text.rfind(SIDEBAR_MARKER)
    if marker_index == -1:
        return raw_text
    return raw_text[:marker_index].rstrip()


def extract_field(lines: list[str], label: str) -> str:
    """Return the value on the line right after a field label, if present."""
    for i, line in enumerate(lines):
        if line.strip() == label and i + 1 < len(lines):
            return lines[i + 1].strip()
    return ""


def section_header_exists(lines: list[str], section_header: str) -> bool:
    """Check whether a section header line is present in the dump at all,
    regardless of whether it has any codes listed under it."""
    return any(line.strip() == section_header for line in lines)


def extract_code_section(lines: list[str], section_header: str, next_headers: list[str]) -> list[str]:
    """
    Collect lines between a code section header (e.g. "CPT Codes")
    and the next known header, treating each non-empty line as one code.
    """
    codes: list[str] = []
    collecting = False

    for line in lines:
        stripped = line.strip()

        if stripped == section_header:
            collecting = True
            continue

        if collecting and stripped in next_headers:
            break

        if collecting and stripped:
            codes.append(stripped)

    return codes


MARKDOWN_END_MARKERS = ["version history"]
DECISION_TREE_START_MARKERS = ["start"]


def extract_markdown_content(lines: list[str]) -> str:
    """
    Collect the raw markdown text between the "Click to view raw markdown"
    anchor and whichever comes first: a "Version History" marker or a
    "start"/"Start" marker (decision tree beginning). Matching against
    these markers is case-insensitive since capitalization is inconsistent
    across payers (e.g. Aetna uses "Start", others use "start").

    If neither marker is ever found, the markdown runs to the end of the
    cleaned text (e.g. MCG PIPA dumps that have no decision tree at all).
    """
    anchor = "Click to view raw markdown"
    collecting = False
    content_lines: list[str] = []

    for line in lines:
        stripped = line.strip()

        if not collecting:
            if stripped == anchor:
                collecting = True
            continue

        lowered = stripped.lower()
        if lowered in MARKDOWN_END_MARKERS or lowered in DECISION_TREE_START_MARKERS:
            break

        content_lines.append(line)

    return "\n".join(content_lines).strip()


def extract_decision_tree_raw(lines: list[str]) -> str:
    """
    Collect the raw decision tree text starting right after a
    "start"/"Start" marker line, through the end of the cleaned text
    (the sidebar has already been stripped by strip_sidebar, so this
    naturally includes the terminal "Procedure Medically Necessary"
    result node).

    If no "start" marker is found, returns an empty string (e.g. MCG
    PIPA dumps that have no decision tree).
    """
    collecting = False
    tree_lines: list[str] = []

    for line in lines:
        stripped = line.strip()

        if not collecting:
            if stripped.lower() in DECISION_TREE_START_MARKERS:
                collecting = True
            continue

        tree_lines.append(line)

    return "\n".join(tree_lines).strip()


def parse_raw_dump(raw_text: str) -> ParsedGuideline:
    """Parse a raw backoffice Ctrl+A dump into a ParsedGuideline object."""
    cleaned_text = strip_sidebar(raw_text)
    lines = cleaned_text.splitlines()

    parsed = ParsedGuideline()
    parsed.title = extract_field(lines, "Title")
    parsed.payer = extract_field(lines, "Payer")
    parsed.guideline_id = extract_field(lines, "Guideline ID")
    parsed.source_url = extract_field(lines, "URL")

    required_fields = {
        "Title": parsed.title,
        "Payer": parsed.payer,
        "Guideline ID": parsed.guideline_id,
        "URL": parsed.source_url,
    }
    for field_name, value in required_fields.items():
        if not value:
            parsed.parsing_warnings.append(
                f"Required field '{field_name}' came back empty. "
                f"This usually means the backoffice format changed or "
                f"the dump is incomplete, not that the field is legitimately blank."
            )

    parsed.cpt_codes = extract_code_section(lines, "CPT Codes", ["HCPCS Codes"])
    parsed.hcpcs_codes = extract_code_section(lines, "HCPCS Codes", ["ICD-10 Codes"])
    parsed.icd10_codes = extract_code_section(lines, "ICD-10 Codes", ["Markdown Content"])

    code_sections = {
        "CPT Codes": parsed.cpt_codes,
        "HCPCS Codes": parsed.hcpcs_codes,
        "ICD-10 Codes": parsed.icd10_codes,
    }
    for section_name, codes in code_sections.items():
        if not codes and not section_header_exists(lines, section_name):
            parsed.parsing_warnings.append(
                f"Section header '{section_name}' was not found in the dump at all. "
                f"An empty list here is likely a parsing failure, not a legitimately "
                f"empty section (compare to a case where the header exists but has "
                f"no codes underneath, which is fine)."
            )

    parsed.markdown_content = extract_markdown_content(lines)
    parsed.decision_tree_raw = extract_decision_tree_raw(lines)

    return parsed