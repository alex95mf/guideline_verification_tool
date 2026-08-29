"""
Browser automation module (Module 4): drives a persistent Playwright
browser session against the Ethermed backoffice to search for source
documents and trigger processing on unprocessed ones.

Uses a persistent profile (browser_profile/ at project root) so login
only has to happen once manually; subsequent runs reuse the saved
session.

IMPORTANT - known limitation: the "Status" column in the search
results list is sometimes unreliable (shows "n/a" even for documents
that are actually processed). Until this is clarified with the team,
this module checks the DETAIL page of each candidate document rather
than trusting the list's Status column, which is slower but accurate.
"""

import os
from playwright.sync_api import sync_playwright

BASE_URL = "https://ethermed-dev.ethermed.run"
PROFILE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "browser_profile")


def open_browser_context(headless=False):
    """
    Launches (or reuses) the persistent browser profile. Returns the
    playwright context manager object and the page - caller is
    responsible for closing via context.close().
    """
    playwright = sync_playwright().start()
    context = playwright.chromium.launch_persistent_context(
        PROFILE_DIR,
        headless=headless,
    )
    page = context.new_page()
    return playwright, context, page


import re

PHX_CLICK_URL_PATTERN = re.compile(r'"href":"([^"]+)"')


def search_source_documents(page, search_text):
    """
    Navigates to the Source Documents list filtered by search_text
    and extracts basic info for each result row.

    NOTE: this app uses Phoenix LiveView, so the "Name" column is a
    <td phx-click='[["navigate",{"href":"..."}]]'> rather than a
    normal <a href="...">. We read the phx-click attribute and pull
    the URL out with a regex instead of using a normal link locator.

    Returns a list of dicts:
        {"name": str, "detail_url": str}
    """
    url = f"{BASE_URL}/backoffice/source_documents?search={search_text.replace(' ', '+')}"
    page.goto(url)
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("td[phx-click]", timeout=10000)

    # Every <td> in a row shares the same phx-click URL (the whole row
    # is clickable), so we get one entry per COLUMN, not per row. We
    # group all cell texts by their URL, then pick the longest text
    # in each group as the document name (the "Name" column text is
    # reliably the longest one compared to Status/Version/dates/etc).
    cells = page.locator("td[phx-click]").all()
    texts_by_url = {}

    for cell in cells:
        phx_click_value = cell.get_attribute("phx-click")
        if not phx_click_value:
            continue

        match = PHX_CLICK_URL_PATTERN.search(phx_click_value)
        if not match:
            continue

        href = match.group(1)
        if "/source_documents/" not in href:
            continue

        text = cell.inner_text().strip()
        if not text:
            continue

        clean_href = href.split("?")[0]
        full_url = BASE_URL + clean_href

        texts_by_url.setdefault(full_url, []).append(text)

    results = []
    for url, texts in texts_by_url.items():
        # Exclude URL-looking text (that's the "Uri" column, never the name)
        candidates = [t for t in texts if not t.lower().startswith("http")]
        if not candidates:
            candidates = texts
        best_name = max(candidates, key=len)
        results.append({
            "name": best_name,
            "detail_url": url,
        })
    return results


def get_processing_status(page, detail_url):
    """
    Opens a source document's detail page and determines its status
    by reading the badge next to the title (or its absence).

    Returns one of: "processed", "processing", "not_processed"
    """
    page.goto(detail_url)
    page.wait_for_load_state("networkidle")

    if page.get_by_text("processed", exact=True).count() > 0:
        return "processed"
    if page.get_by_text("processing", exact=True).count() > 0:
        return "processing"
    return "not_processed"


def start_processing(page, detail_url, organization=None):
    """
    Triggers processing for a source document.

    organization: optional string. If provided, selects that
    organization from the modal's dropdown instead of leaving it as
    "All Organizations (Default)".

    Returns True if the confirmation notification appeared, False
    if something looked off (caller should re-check status manually).
    """
    page.goto(detail_url)
    page.wait_for_load_state("networkidle")

    start_button = page.get_by_role("button", name="Start Processing")
    if start_button.is_disabled():
        return False

    start_button.click()

    page.wait_for_selector("text=Start Extraction")

    if organization:
        org_field = page.get_by_text("All Organizations (Default)")
        org_field.click()
        page.get_by_text(organization, exact=False).first.click()

    modal = page.locator("text=Start Extraction").locator("..")
    modal.get_by_role("button", name="Start Processing").click()

    try:
        page.wait_for_selector("text=Started processing", timeout=5000)
        return True
    except Exception:
        return False