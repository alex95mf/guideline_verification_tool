"""
Test script for automatic document download: verifies three scenarios
against the get_source_document flow.

1. Manual-access payer (Humana) -> should be rejected immediately
   without attempting a network call.
2. Public payer with a real, working URL (Carelon, row 94.1) -> should
   download successfully and register it in the local library.
3. Calling it again for the same guideline_id -> should now find it in
   the local library instead of downloading again.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from source_library import load_index, get_source_document

CARELON_GUIDELINE_ID = "019df8f8-374c-7409-a6f3-d3b32d201221"
CARELON_URL = "https://guidelines.carelonmedicalbenefitsmanagement.com/wp-content/uploads/2025/12/Upper-Gastrointestinal-Endoscopy-Esophagogastroduodenoscopy-2026-04-04.pdf"


def main():
    index = load_index()

    print("--- CASO 1: Humana (deberia rechazar sin intentar descarga) ---")
    result_humana = get_source_document(
        guideline_id="fake-humana-id",
        source_url="https://dctm.humana.com/fake-url",
        payer="humana",
        index=index,
    )
    print(result_humana)
    print()

    print("--- CASO 2: Carelon real (deberia descargar exitosamente) ---")
    result_carelon = get_source_document(
        guideline_id=CARELON_GUIDELINE_ID,
        source_url=CARELON_URL,
        payer="anthem",
        index=index,
    )
    print(result_carelon)

    if result_carelon.get("success") and "index" in result_carelon:
        index = result_carelon["index"]
    print()

    print("--- CASO 3: mismo guideline_id de nuevo (deberia usar libreria local) ---")
    result_again = get_source_document(
        guideline_id=CARELON_GUIDELINE_ID,
        source_url=CARELON_URL,
        payer="anthem",
        index=index,
    )
    print(result_again)


if __name__ == "__main__":
    main()