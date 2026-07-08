"""
Regression test for the Module 1 error-handling update: runs every
existing test case through the parser and reports whether each one
produced any parsing warnings. Used to confirm that adding warning
detection didn't introduce false positives on dumps we already know
are well-formed.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from parser import parse_raw_dump

TEST_FILES = [
    "test_cases/row_92_1.txt",
    "test_cases/row_27.txt",
    "test_cases/row_59_1.txt",
    "test_cases/row_4_1_1.txt",
    "test_cases/row_94_1.txt",
    "test_cases/row_11_1.txt",
]


def main():
    for file_path in TEST_FILES:
        with open(file_path, "r", encoding="utf-8") as file:
            raw_text = file.read()

        parsed = parse_raw_dump(raw_text)

        print(f"--- {file_path} ---")
        if parsed.parsing_warnings:
            print("WARNINGS FOUND:")
            for warning in parsed.parsing_warnings:
                print(f"  - {warning}")
        else:
            print("OK: no warnings")
        print()


if __name__ == "__main__":
    main()