"""
PDF text extraction module: converts a downloaded/pasted source
document (PDF) into plain text so it can be compared against the
extracted markdown_content and decision_tree_raw.
"""

import pypdf


def extract_text_from_pdf(pdf_path):
    """
    Extract all text from a PDF file, page by page, joined with a
    page-break marker so downstream comparison can still tell where
    one page ends and the next begins if that ever matters.

    Returns a dict with:
        - success: bool
        - text: full extracted text (empty string if failed)
        - page_count: number of pages found
        - reason: only present if success is False
    """
    try:
        reader = pypdf.PdfReader(pdf_path)
    except Exception as exc:
        return {
            "success": False,
            "text": "",
            "page_count": 0,
            "reason": f"Could not open PDF: {exc}",
        }

    page_texts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        page_texts.append(page_text)

    full_text = "\n\n--- PAGE BREAK ---\n\n".join(page_texts)

    if not full_text.strip():
        return {
            "success": False,
            "text": "",
            "page_count": len(reader.pages),
            "reason": "PDF opened but no extractable text was found (likely a scanned/image-only PDF).",
        }

    return {
        "success": True,
        "text": full_text,
        "page_count": len(reader.pages),
    }