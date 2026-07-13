"""
Test script for PDF text extraction: verifies it against the real
Carelon PDF (row 94.1) already downloaded into source_documents/,
plus a negative case (a file that doesn't exist).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pdf_text import extract_text_from_pdf

REAL_PDF_PATH = "source_documents/019df8f8-374c-7409-a6f3-d3b32d201221.pdf"


def preview(text, length=200):
    if not text:
        return "(EMPTY)"
    flat = text.replace("\n", " \\n ")
    if len(flat) <= length:
        return flat
    return flat[:length] + "..."


def main():
    print("--- CASO 1: PDF real de Carelon (fila 94.1) ---")
    result = extract_text_from_pdf(REAL_PDF_PATH)
    print("Success:", result["success"])
    print("Page count:", result.get("page_count"))
    if result["success"]:
        print("Text length:", len(result["text"]), "chars")
        print("Preview:", preview(result["text"]))
    else:
        print("Reason:", result.get("reason"))
    print()

    print("--- CASO 2: archivo que no existe ---")
    result2 = extract_text_from_pdf("source_documents/no-existe.pdf")
    print(result2)


if __name__ == "__main__":
    main()