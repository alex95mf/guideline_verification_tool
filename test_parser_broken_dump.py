"""
Positive test for the Module 1 error-handling update: feeds the parser
a deliberately malformed dump (missing Payer field, missing ICD-10
Codes header entirely) to confirm that parsing_warnings actually
fires when something is wrong, not just that it stays silent on
well-formed dumps.

Also confirms the key distinction: HCPCS Codes is empty in this dump
too, but its header IS present, so it should NOT produce a warning
(legitimately empty vs. missing header).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from parser import parse_raw_dump

BROKEN_DUMP = """Some Title Without Breadcrumb
Basic Information
Title
Some Test Guideline
Guideline ID
abc-123
URL
https://example.com/doc
Medical Codes
CPT Codes
12345
HCPCS Codes
Markdown Content
Some content here.
Backoffice
Administration Panel
"""


def main():
    parsed = parse_raw_dump(BROKEN_DUMP)

    print("Payer:", repr(parsed.payer))
    print("HCPCS Codes:", parsed.hcpcs_codes)
    print("ICD-10 Codes:", parsed.icd10_codes)
    print()
    print("Warnings found:")
    for warning in parsed.parsing_warnings:
        print(f"  - {warning}")
    print()

    expected_warnings_count = 2
    has_payer_warning = any("Payer" in w for w in parsed.parsing_warnings)
    has_icd10_warning = any("ICD-10 Codes" in w for w in parsed.parsing_warnings)
    has_hcpcs_warning = any("HCPCS Codes" in w for w in parsed.parsing_warnings)

    if has_payer_warning and has_icd10_warning and not has_hcpcs_warning:
        print("PASS: detecto Payer faltante e ICD-10 Codes faltante, sin falso positivo en HCPCS vacio legitimo")
    else:
        print("FAIL: revisar logica de warnings")


if __name__ == "__main__":
    main()