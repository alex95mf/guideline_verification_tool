"""
First real test against the Ethermed backoffice: uses a persistent
browser profile (separate from your personal Chrome/Edge) so that
once you log in manually the first time, the session is remembered
for future runs.

The profile is stored in browser_profile/ at the project root. This
folder should NEVER be committed to git (it will contain session
cookies), so it must be added to .gitignore.
"""

from playwright.sync_api import sync_playwright

PROFILE_DIR = "browser_profile"


def main():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
        )
        page = context.new_page()
        page.goto("https://ethermed-dev.ethermed.run/backoffice/source_documents")
        print("Page title:", page.title())
        print("Current URL:", page.url)
        input("Revisa la ventana del navegador. Presiona Enter aqui cuando termines...")
        context.close()


if __name__ == "__main__":
    main()