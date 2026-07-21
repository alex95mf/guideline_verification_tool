"""
Basic sanity test for Playwright: opens a visible browser, navigates
to a simple page, and confirms the page title loaded correctly.
Doesn't touch the Ethermed backoffice yet - just confirms the whole
Playwright stack (browser + automation) works on this machine.
"""

from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://example.com")
        print("Page title:", page.title())
        input("Presiona Enter para cerrar el navegador...")
        browser.close()


if __name__ == "__main__":
    main()