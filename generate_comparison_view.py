"""
Comparison view generator (Module 4, Option A): ties together the
parser, rules engine, source library, and PDF text extractor into a
single flow. For a given raw backoffice dump, it:

1. Parses the dump (Module 1)
2. Runs the automatic bug detection rules (Module 2)
3. Finds or downloads the original source document (source_library)
4. Extracts the source document's text (pdf_text)
5. Saves the full source text to a standalone .txt file (too long to
   print usefully in the terminal)
6. Prints a structured summary: codes, detected bugs, markdown,
   decision tree, and a pointer to the full source text file - ready
   for manual side-by-side comparison.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from parser import parse_raw_dump
from rules_engine import detect_icd10_parent_bugs, detect_j15_jurisdiction_suspect
from source_library import load_index, get_source_document
from pdf_text import extract_text_from_pdf
from markdown_evaluator import evaluate_markdown

OUTPUT_FOLDER = "output"


def generate_comparison_view(dump_file_path):
    with open(dump_file_path, "r", encoding="utf-8") as file:
        raw_text = file.read()

    parsed = parse_raw_dump(raw_text)

    print("=" * 60)
    print(f"GUIDELINE: {parsed.title}")
    print(f"PAYER: {parsed.payer}")
    print("=" * 60)

    if parsed.parsing_warnings:
        print()
        print("PARSING WARNINGS:")
        for warning in parsed.parsing_warnings:
            print(f"  - {warning}")

    print()
    print("--- CODIGOS EXTRAIDOS ---")
    print("CPT:", parsed.cpt_codes)
    print("HCPCS:", parsed.hcpcs_codes)
    print("ICD-10:", parsed.icd10_codes)

    print()
    print("--- BUGS DETECTADOS AUTOMATICAMENTE (Modulo 2) ---")
    z01_bugs = detect_icd10_parent_bugs(parsed.icd10_codes)
    print("Z01 parent bugs (confirmados):", z01_bugs if z01_bugs else "ninguno")
    j15_result = detect_j15_jurisdiction_suspect(parsed)
    print("J15 sospecha:", j15_result)

    print()
    print("--- MARKDOWN EXTRAIDO (del backoffice) ---")
    print(parsed.markdown_content)

    print()
    print("--- DECISION TREE EXTRAIDO ---")
    print(parsed.decision_tree_raw)

    print()
    print("--- DOCUMENTO ORIGINAL ---")
    index = load_index()
    doc_result = get_source_document(
        guideline_id=parsed.guideline_id,
        source_url=parsed.source_url,
        payer=parsed.payer,
        index=index,
    )

    if not doc_result["success"]:
        print(f"NO SE PUDO OBTENER EL DOCUMENTO ORIGINAL: {doc_result['reason']}")
        print(f"Detalle: {doc_result.get('detail', '(sin detalle)')}")
        return

    print(f"Documento obtenido de: {doc_result['source']}")
    print(f"Ruta local: {doc_result['path']}")

    text_result = extract_text_from_pdf(doc_result["path"])
    if not text_result["success"]:
        print(f"NO SE PUDO EXTRAER TEXTO DEL DOCUMENTO: {text_result['reason']}")
        return

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    output_filename = f"{parsed.guideline_id}_source_text.txt"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(text_result["text"])

    print(f"Texto completo del documento original ({text_result['page_count']} paginas, "
          f"{len(text_result['text'])} caracteres) guardado en:")
    print(f"  {output_path}")
    print("Abrelo en VS Code para hacer Ctrl+F y comparar contra el markdown/arbol de arriba.")

    print()
    print("--- EVALUACION AUTOMATICA DEL MARKDOWN (Modulo 4) ---")
    eval_result = evaluate_markdown(
        breadcrumb_title=parsed.title,
        markdown_content=parsed.markdown_content,
        source_text=text_result["text"],
    )
    print(f"Resultado: {eval_result['result']}")
    print(f"Hallazgo: {eval_result['finding']}")
    if eval_result.get("mock"):
        print("(NOTA: esta es una respuesta simulada, no una evaluacion real de IA)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: py generate_comparison_view.py <ruta_al_dump.txt>")
        sys.exit(1)

    generate_comparison_view(sys.argv[1])