"""
Rules engine module: deterministic bug detection rules that operate
directly on parsed guideline data, without needing to read the
original payer document. These rules encode systematic bugs that
have already been confirmed by the team (Ben Beidler / Uzoma Abakporo).
"""


def detect_icd10_parent_bugs(icd10_codes: list[str]) -> list[str]:
    """
    Detect ICD-10 'parent' codes (3 characters, no extension) that
    appear alongside more specific codes sharing the same root
    (e.g. Z01 next to Z01.810, Z01.811...).

    These parent codes are not billable on their own, and their
    presence in the extraction is a systematic over-inclusion bug
    (Bug #1: ICD-10 header/parent codes no billables).
    """
    bugs = []
    for code in icd10_codes:
        is_parent_shaped = len(code) == 3 and "." not in code
        if not is_parent_shaped:
            continue

        has_extended_sibling = any(
            other != code and other.startswith(code + ".")
            for other in icd10_codes
        )
        if has_extended_sibling:
            bugs.append(code)

    return bugs


def detect_j15_jurisdiction_suspect(parsed) -> dict:
    """
    Flags suspected J15 jurisdiction-vs-ICD10 confusion in Humana
    Medicare Advantage guidelines (systematic Bug #2).

    Unlike detect_icd10_parent_bugs (Z01), this is a PATTERN-BASED
    SUSPICION, not a confirmed bug: it cannot be confirmed from the
    extracted codes alone and requires manual verification against
    the source document.

    Triggers when ALL of the following hold:
    - payer is Humana
    - title indicates a Medicare Advantage document
    - at least one ICD-10 code has the "J15" prefix (J15 or J15.x)
    """
    is_humana = parsed.payer.strip().lower() == "humana"
    is_medicare_advantage = "medicare advantage" in parsed.title.lower()

    if not (is_humana and is_medicare_advantage):
        return {
            "suspected_codes": [],
            "confidence": "not_applicable",
            "reason": "Document is not Humana Medicare Advantage.",
        }

    suspected_codes = [
        code for code in parsed.icd10_codes
        if code == "J15" or code.startswith("J15.")
    ]

    if not suspected_codes:
        return {
            "suspected_codes": [],
            "confidence": "not_applicable",
            "reason": "No J15-prefixed ICD-10 codes found.",
        }

    return {
        "suspected_codes": suspected_codes,
        "confidence": "requires_manual_verification",
        "reason": (
            "Humana Medicare Advantage document with J15-prefixed "
            "ICD-10 codes; verify against source document that "
            "these are not the Medicare jurisdiction reference "
            "rather than the ICD-10 pneumonia code."
        ),
    }