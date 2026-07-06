"""
Entry point script: reads a raw backoffice dump from a test case file
and runs it through the parser to inspect the extracted fields.
"""

from parser import parse_raw_dump


TEST_FILE_PATH = "../test_cases/row_94_1.txt"


def main():
    with open(TEST_FILE_PATH, "r", encoding="utf-8") as file:
        raw_text = file.read()

    parsed = parse_raw_dump(raw_text)

    print("Title:", parsed.title)
    print("Payer:", parsed.payer)
    print("Guideline ID:", parsed.guideline_id)
    print("Source URL:", parsed.source_url)
    print()
    print("CPT Codes:", parsed.cpt_codes)
    print("HCPCS Codes:", parsed.hcpcs_codes)
    print("ICD-10 Codes:", parsed.icd10_codes)


if __name__ == "__main__":
    main()