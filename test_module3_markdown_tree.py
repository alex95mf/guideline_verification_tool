"""
Test script for Module 3: verifies that extract_markdown_content and
extract_decision_tree_raw correctly split the markdown and decision
tree sections across all 6 existing test cases.

Special case to watch: row_27.txt (MCG PIPA) has no decision tree at
all in the dump, so decision_tree_raw should come back empty for it,
while markdown_content should still be fully populated.
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


def preview(text, length=80):
    if not text:
        return "(EMPTY)"
    flat = text.replace("\n", " \\n ")
    if len(flat) <= length:
        return flat
    return flat[:length] + "..."


def main():
    for file_path in TEST_FILES:
        with open(file_path, "r", encoding="utf-8") as file:
            raw_text = file.read()

        parsed = parse_raw_dump(raw_text)

        print(f"--- {file_path} ---")
        print(f"Markdown length: {len(parsed.markdown_content)} chars")
        print(f"Markdown preview: {preview(parsed.markdown_content)}")
        print()
        print(f"Decision tree length: {len(parsed.decision_tree_raw)} chars")
        print(f"Decision tree preview: {preview(parsed.decision_tree_raw)}")
        print()


if __name__ == "__main__":
    main()