"""
Test script for Module 2: verifies that detect_icd10_parent_bugs
correctly flags the Z01 parent code using row 92.1 as the golden
set (already confirmed by the team as a systematic bug).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from parser import parse_raw_dump
from rules_engine import detect_icd10_parent_bugs


TEST_FILE_PATH = "test_cases/row_92_1.txt"


def main():
    with open(TEST_FILE_PATH, "r", encoding="utf-8") as file:
        raw_text = file.read()

    parsed = parse_raw_dump(raw_text)

    print("ICD-10 Codes extracted:", parsed.icd10_codes)

    bugs = detect_icd10_parent_bugs(parsed.icd10_codes)

    print("Parent code bugs detected:", bugs)
    print()

    expected = ["Z01"]
    if bugs == expected:
        print(f"PASS: expected {expected}, got {bugs}")
    else:
        print(f"FAIL: expected {expected}, got {bugs}")


if __name__ == "__main__":
    main()