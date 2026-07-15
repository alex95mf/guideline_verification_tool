"""
Markdown evaluator module (Module 4, Option C - first scope: markdown
only). Compares the extracted markdown_content against the original
source document text and returns a structured evaluation.

MOCK MODE: when no ANTHROPIC_API_KEY environment variable is set,
evaluate_markdown() returns a clearly-labeled mock response instead of
calling the real API. This lets the rest of the tool (and this module's
own integration) be built and tested before an API key is available.
Once a real key exists, real calls happen automatically - no code
changes needed elsewhere.
"""

import os
import json

SYSTEM_PROMPT = """You are a QA validation assistant for a medical guideline extraction project.

Your job: compare an extracted markdown excerpt (pulled from a backoffice system) against the
relevant section of the original source policy document, and judge whether the extraction is
correct.

Rules to apply:
- The markdown must correspond ONLY to the specific subsection indicated by the breadcrumb title
  (e.g. "Guideline Name > Category > Specific Subsection"). Content from sibling subsections of the
  same document is NOT acceptable and should be flagged as a bug.
- Description, Clinical Background sections, and appendices ARE acceptable inclusions, even if not
  directly referenced by the coverage criteria, as long as they don't appear to introduce unrelated
  or contradictory coverage logic.
- Administrative notes and references to other documents are acceptable inclusions.
- The extraction should represent the FULL relevant medical necessity criteria of that subsection,
  not a summary. If key coverage criteria from the subsection are missing, that is a bug.
- If the source uses conditional "Not Covered if used to report X" language, and X describes the
  entire scope of the guideline (not a specific carved-out case), that condition is effectively
  absolute and should be reflected as such.

Respond with ONLY a JSON object, no other text, in this exact shape:
{"result": "correct" | "bug" | "uncertain", "finding": "<brief explanation in English, 1-3 sentences>"}
"""


def _build_user_prompt(breadcrumb_title, markdown_content, source_text):
    return f"""BREADCRUMB TITLE (defines the exact subsection to validate against):
{breadcrumb_title}

EXTRACTED MARKDOWN (from the backoffice system):
{markdown_content}

ORIGINAL SOURCE DOCUMENT TEXT (full document, find the relevant subsection yourself):
{source_text}
"""


def _mock_response(breadcrumb_title):
    """Returns a clearly-labeled mock response, used when no API key is configured."""
    return {
        "result": "uncertain",
        "finding": (
            "[MOCK RESPONSE - no ANTHROPIC_API_KEY configured] "
            f"This is a placeholder response for '{breadcrumb_title}'. "
            "Set the ANTHROPIC_API_KEY environment variable to get a real evaluation."
        ),
        "mock": True,
    }


def _call_real_api(system_prompt, user_prompt):
    import anthropic

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    response_text = message.content[0].text
    return json.loads(response_text)


def evaluate_markdown(breadcrumb_title, markdown_content, source_text):
    """
    Main entry point. Returns a dict:
        {"result": "correct" | "bug" | "uncertain", "finding": "...", "mock": bool}

    Runs in mock mode automatically if ANTHROPIC_API_KEY is not set in
    the environment, so the rest of the pipeline can be built/tested
    without a real key.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return _mock_response(breadcrumb_title)

    user_prompt = _build_user_prompt(breadcrumb_title, markdown_content, source_text)
    try:
        result = _call_real_api(SYSTEM_PROMPT, user_prompt)
        result["mock"] = False
        return result
    except Exception as exc:
        return {
            "result": "uncertain",
            "finding": f"API call failed: {exc}",
            "mock": False,
            "error": True,
        }