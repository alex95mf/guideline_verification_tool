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
from report_generator import generate_report_es, generate_report_en, build_filename
from datetime import datetime

OUTPUT_FOLDER = "output"


def generate_comparison_view(dump_file_path, row_id=None):
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

    print()
    print("--- GENERANDO REPORTES ES/EN ---")

    markdown_result_es = "BUG" if eval_result["result"] == "bug" else (
        "Correcto" if eval_result["result"] == "correct" else "PENDIENTE"
    )
    markdown_result_en = "BUG" if eval_result["result"] == "bug" else (
        "Correct" if eval_result["result"] == "correct" else "PENDING"
    )

    first_cpt = parsed.cpt_codes[0] if parsed.cpt_codes else "00000"
    short_name = parsed.title.split(">")[-1].strip().replace(" ", "")[:30]
    resolved_row_id = row_id if row_id else parsed.guideline_id[:8]

    report_data = {
        "row_id": resolved_row_id,
        "payer": parsed.payer,
        "date": datetime.now().strftime("%d de %B de %Y"),
        "date_en": datetime.now().strftime("%B %d, %Y"),
        "title": parsed.title,
        "backoffice_url": f"(pendiente: URL del backoffice para este guideline)",
        "source_url": parsed.source_url,
        "subsection": parsed.title.split(">")[-1].strip() if ">" in parsed.title else "documento completo",
        "subsection_en": parsed.title.split(">")[-1].strip() if ">" in parsed.title else "full document",
        "codes_overall": "PENDIENTE",
        "codes_overall_en": "PENDING",
        "cpt_result": "PENDIENTE", "cpt_finding": "Verificacion manual pendiente.",
        "cpt_result_en": "PENDING", "cpt_finding_en": "Manual verification pending.",
        "hcpcs_result": "PENDIENTE", "hcpcs_finding": "Verificacion manual pendiente.",
        "hcpcs_result_en": "PENDING", "hcpcs_finding_en": "Manual verification pending.",
        "icd10_result": "PENDIENTE", "icd10_finding": "Verificacion manual pendiente.",
        "icd10_result_en": "PENDING", "icd10_finding_en": "Manual verification pending.",
        "markdown_result": markdown_result_es, "markdown_finding": eval_result["finding"],
        "markdown_result_en": markdown_result_en, "markdown_finding_en": eval_result["finding"],
        "tree_result": "PENDIENTE", "tree_finding": "Evaluacion automatica del arbol aun no implementada.",
        "tree_result_en": "PENDING", "tree_finding_en": "Automatic tree evaluation not yet implemented.",
        "notes": [
            "Reporte generado automaticamente por la herramienta. Los campos PENDIENTE requieren verificacion manual.",
        ],
    }

    os.makedirs("reports/es", exist_ok=True)
    os.makedirs("reports/en", exist_ok=True)

    filename_es = build_filename(report_data["row_id"], first_cpt, short_name, "es")
    filename_en = build_filename(report_data["row_id"], first_cpt, short_name, "en")

    with open(f"reports/es/{filename_es}", "w", encoding="utf-8") as f:
        f.write(generate_report_es(report_data))
    with open(f"reports/en/{filename_en}", "w", encoding="utf-8") as f:
        f.write(generate_report_en(report_data))

    print(f"Reporte ES guardado en: reports/es/{filename_es}")
    print(f"Reporte EN guardado en: reports/en/{filename_en}")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print("Uso: py generate_comparison_view.py <ruta_al_dump.txt> [id_de_fila]")
        sys.exit(1)

    row_id_arg = sys.argv[2] if len(sys.argv) == 3 else None
    generate_comparison_view(sys.argv[1], row_id_arg)
