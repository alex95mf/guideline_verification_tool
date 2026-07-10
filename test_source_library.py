"""
Test script for the source library module: confirms the basic cycle
works correctly - empty index at first, registering a document,
finding it afterwards, and correctly NOT finding a guideline_id that
was never registered.

Uses row 94.1 (Carelon Upper GI Endoscopy) as the example, since we
already worked with its real guideline_id and source_url earlier.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from source_library import load_index, find_local_document, register_document

TEST_GUIDELINE_ID = "019df8f8-374c-7409-a6f3-d3b32d201221"
TEST_SOURCE_URL = "https://guidelines.carelonmedicalbenefitsmanagement.com/wp-content/uploads/2025/12/Upper-Gastrointestinal-Endoscopy-Esophagogastroduodenoscopy-2026-04-04.pdf"
TEST_LOCAL_FILENAME = f"{TEST_GUIDELINE_ID}.txt"


def main():
    index = load_index()
    print("Index at start:", index)

    # Simulate that we already have the document saved locally
    documents_folder = os.path.join(os.path.dirname(__file__), "source_documents")
    with open(os.path.join(documents_folder, TEST_LOCAL_FILENAME), "w", encoding="utf-8") as file:
        file.write("simulated PDF content for testing purposes")

    index = register_document(
        guideline_id=TEST_GUIDELINE_ID,
        source_url=TEST_SOURCE_URL,
        payer="anthem",
        local_filename=TEST_LOCAL_FILENAME,
        index=index,
    )
    print("Index after registering:", index)

    found = find_local_document(TEST_GUIDELINE_ID, index)
    print("Found existing guideline_id:", found)

    not_found = find_local_document("made-up-id-that-does-not-exist", index)
    print("Found made-up guideline_id (should be None):", not_found)

    if found and not_found is None:
        print()
        print("PASS: encontro el documento registrado y no encontro el id inventado")
    else:
        print()
        print("FAIL: revisar logica de la libreria")


if __name__ == "__main__":
    main()