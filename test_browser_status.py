"""
Isolated test for get_processing_status: checks two known documents -
one we know is processed (Anthem Colorado, Upper GI Endoscopy) and
one we know is unprocessed, to confirm the status detection works
correctly for both cases.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from browser_automation import open_browser_context, get_processing_status

KNOWN_PROCESSED_URL = "https://ethermed-dev.ethermed.run/backoffice/source_documents/268650eb-aa7c-4fbb-8e28-c1d7527e9d9a"
KNOWN_UNPROCESSED_URL = "https://ethermed-dev.ethermed.run/backoffice/source_documents/6ea4114e-9646-43ee-aba9-ed803dc3ee65"


def main():
    playwright, context, page = open_browser_context(headless=False)

    try:
        status_processed = get_processing_status(page, KNOWN_PROCESSED_URL)
        print(f"Documento conocido PROCESADO -> detectado como: {status_processed}")

        status_unprocessed = get_processing_status(page, KNOWN_UNPROCESSED_URL)
        print(f"Documento conocido SIN PROCESAR -> detectado como: {status_unprocessed}")

        input("\nRevisa el navegador si quieres. Presiona Enter para cerrar...")
    finally:
        context.close()
        playwright.stop()


if __name__ == "__main__":
    main()