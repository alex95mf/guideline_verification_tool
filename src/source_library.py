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