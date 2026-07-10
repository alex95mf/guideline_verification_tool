"""
Source library module: manages the permanent local collection of
original payer source documents, indexed by guideline_id so they can
be found regardless of naming or URL duplication across payers.
"""

import json
import os

INDEX_FILENAME = "source_documents_index.json"
DOCUMENTS_FOLDER = "source_documents"


def _index_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), INDEX_FILENAME)


def _documents_folder_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), DOCUMENTS_FOLDER)


def load_index():
    """Load the index mapping guideline_id -> document info.
    Returns an empty dict if the index doesn't exist yet."""
    path = _index_path()
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_index(index):
    """Write the updated index back to disk."""
    path = _index_path()
    with open(path, "w", encoding="utf-8") as file:
        json.dump(index, file, indent=2, ensure_ascii=False)


def find_local_document(guideline_id, index):
    """Check whether guideline_id is in the index AND the local file
    still exists on disk. Returns the local file path, or None."""
    entry = index.get(guideline_id)
    if not entry:
        return None

    local_path = os.path.join(_documents_folder_path(), entry["local_filename"])
    if not os.path.exists(local_path):
        return None

    return local_path


def register_document(guideline_id, source_url, payer, local_filename, index):
    """Add a new entry to the index for a document that was just
    saved (either pasted manually or downloaded)."""
    index[guideline_id] = {
        "source_url": source_url,
        "payer": payer,
        "local_filename": local_filename,
    }
    save_index(index)
    return index


# ---------------------------------------------------------------------------
# Automatic download for publicly accessible payer sources.
# ---------------------------------------------------------------------------

import requests

MANUAL_ACCESS_PAYERS = {"humana", "mcg", "pipa"}

PDF_SIGNATURE = b"%PDF"
LOGIN_PAGE_MARKERS = ["sign in", "log in", "login", "password", "username"]


def _looks_like_login_page(content_bytes):
    """Heuristic check: does this response look like a login page instead
    of the actual document (some sites return 200 OK but serve a login
    form when the real document requires authentication)."""
    if content_bytes.startswith(PDF_SIGNATURE):
        return False
    sample = content_bytes[:5000].decode("utf-8", errors="ignore").lower()
    marker_hits = sum(1 for marker in LOGIN_PAGE_MARKERS if marker in sample)
    return marker_hits >= 2


def download_document(source_url, payer, guideline_id, timeout=15):
    """
    Attempt to download a source document from a public payer URL.
    Returns a dict describing the outcome - never raises for expected
    failure modes (auth required, timeout, unsupported format).
    """
    if payer.strip().lower() in MANUAL_ACCESS_PAYERS:
        return {
            "success": False,
            "reason": "manual_access_required",
            "detail": f"Payer '{payer}' requires manual access (VPN or credentials).",
        }

    browser_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(source_url, headers=browser_headers, timeout=timeout)
    except requests.exceptions.Timeout:
        return {"success": False, "reason": "network_timeout", "detail": str(source_url)}
    except requests.exceptions.RequestException as exc:
        return {"success": False, "reason": "network_error", "detail": str(exc)}

    if response.status_code in (401, 403):
        return {
            "success": False,
            "reason": "auth_required",
            "detail": f"Server returned {response.status_code}.",
        }
    if response.status_code != 200:
        return {
            "success": False,
            "reason": "http_error",
            "detail": f"Server returned {response.status_code}.",
        }

    content = response.content

    if _looks_like_login_page(content):
        return {
            "success": False,
            "reason": "unexpected_login_page",
            "detail": "Response returned 200 but looks like a login page, not the document.",
        }

    if content.startswith(PDF_SIGNATURE):
        extension = ".pdf"
    elif b"<html" in content[:1000].lower():
        extension = ".html"
    else:
        return {
            "success": False,
            "reason": "unsupported_format",
            "detail": "Response content is not a recognized PDF or HTML document.",
        }

    local_filename = f"{guideline_id}{extension}"
    local_path = os.path.join(_documents_folder_path(), local_filename)
    with open(local_path, "wb") as file:
        file.write(content)

    return {"success": True, "local_filename": local_filename}


def get_source_document(guideline_id, source_url, payer, index):
    """
    Main entry point: check the local library first, then attempt
    automatic download if not found. Returns a dict describing where
    the document came from, or why it could not be obtained.
    """
    local_path = find_local_document(guideline_id, index)
    if local_path:
        return {"success": True, "path": local_path, "source": "local_library"}

    download_result = download_document(source_url, payer, guideline_id)
    if not download_result["success"]:
        return download_result

    updated_index = register_document(
        guideline_id=guideline_id,
        source_url=source_url,
        payer=payer,
        local_filename=download_result["local_filename"],
        index=index,
    )
    new_path = os.path.join(_documents_folder_path(), download_result["local_filename"])
    return {"success": True, "path": new_path, "source": "downloaded", "index": updated_index}