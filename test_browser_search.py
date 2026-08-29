"""
Isolated test for search_source_documents: opens the persistent
browser, searches for a known document, and prints what was found.
This is the first real test of the browser_automation module against
the live site, so the goal is just to see whether the generic table
locator finds the right rows - adjustments are expected here.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from browser_automation import open_browser_context, search_source_documents


def main():
    playwright, context, page = open_browser_context(headless=False)

    try:
        results = search_source_documents(page, "Upper Gastrointestinal Endoscopy")

        print(f"Encontrados {len(results)} resultados:")
        for i, r in enumerate(results, start=1):
            print(f"{i}. {r['name']}")
            print(f"   URL: {r['detail_url']}")

        input("\nRevisa la ventana del navegador si quieres. Presiona Enter para cerrar...")
    finally:
        context.close()
        playwright.stop()


if __name__ == "__main__":
    main()