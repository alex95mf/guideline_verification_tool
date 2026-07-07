"""
Test script for Module 2: verifies that detect_j15_jurisdiction_suspect
correctly flags the J15 pattern using row 11.1 as the positive golden
set (Humana Medicare Advantage, confirmed bug), plus a negative
control case to confirm no false positives.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from parser import parse_raw_dump
from rules_engine import detect_j15_jurisdiction_suspect


TEST_FILE_PATH = "test_cases/row_11_1.txt"


def test_positive_case():
    with open(TEST_FILE_PATH, "r", encoding="utf-8") as file:
        raw_text = file.read()

    parsed = parse_raw_dump(raw_text)
    result = detect_j15_jurisdiction_suspect(parsed)

    print("--- CASO POSITIVO (fila 11.1, Humana Medicare Advantage) ---")
    print("Payer:", parsed.payer)
    print("Title:", parsed.title)
    print("Suspected codes:", result["suspected_codes"])
    print("Confidence:", result["confidence"])
    print()

    expected_confidence = "requires_manual_verification"
    if result["confidence"] == expected_confidence and "J15" in result["suspected_codes"]:
        print(f"PASS: se detecto la sospecha J15 correctamente")
    else:
        print(f"FAIL: se esperaba confidence={expected_confidence} con J15 en la lista")


def test_negative_case_different_payer():
    class FakeParsed:
        payer = "aetna"
        title = "Some Aetna CPB > Medicare Advantage mention"
        icd10_codes = ["J15", "J15.0", "J15.9"]

    result = detect_j15_jurisdiction_suspect(FakeParsed())

    print("--- CASO NEGATIVO (payer distinto a Humana) ---")
    print("Suspected codes:", result["suspected_codes"])
    print("Confidence:", result["confidence"])
    print()

    if result["confidence"] == "not_applicable":
        print("PASS: no se disparo la sospecha con payer distinto a Humana")
    else:
        print("FAIL: se esperaba confidence=not_applicable")


def test_negative_case_not_medicare_advantage():
    class FakeParsed:
        payer = "humana"
        title = "Some Humana Commercial Pneumonia Guideline"
        icd10_codes = ["J15", "J15.0", "J15.9"]

    result = detect_j15_jurisdiction_suspect(FakeParsed())

    print("--- CASO NEGATIVO (Humana pero no Medicare Advantage) ---")
    print("Suspected codes:", result["suspected_codes"])
    print("Confidence:", result["confidence"])
    print()

    if result["confidence"] == "not_applicable":
        print("PASS: no se disparo la sospecha sin 'Medicare Advantage' en el titulo")
    else:
        print("FAIL: se esperaba confidence=not_applicable")


if __name__ == "__main__":
    test_positive_case()
    test_negative_case_different_payer()
    test_negative_case_not_medicare_advantage()