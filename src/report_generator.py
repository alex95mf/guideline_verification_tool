"""
Validation report generator: produces the exact ES/EN gdoc-style text
following the project's strict formatting rules (separators, NOTAS
only in Spanish, no trailing separator after NOTAS, filename
conventions).
"""

SEPARATOR = "═" * 59


def _sep():
    return f"\n{SEPARATOR}\n"


def build_filename(row_id, cpt_code, short_name, language):
    prefix = "Fila" if language == "es" else "Row"
    return f"{prefix}_{row_id}_CPT{cpt_code}_{short_name}.gdoc"


def generate_report_es(data):
    """
    data is a dict expected to contain:
        row_id, payer, date, title, backoffice_url, source_url,
        subsection, codes_result, codes_findings (dict with cpt/hcpcs/icd10
        each having result+finding), markdown_result, markdown_finding,
        tree_result, tree_finding, notes (list of strings)
    """
    codes_overall = data["codes_overall"]  # "Correcto" | "BUG" | "PENDIENTE"

    lines = []
    lines.append(f"INFORME DE VALIDACIÓN — FILA {data['row_id']}")
    lines.append("Proyecto: Ethermed QA")
    lines.append(f"Payer: {data['payer']}")
    lines.append(f"Fecha: {data['date']}")
    lines.append("Validado por: Alexander Martinez")
    lines.append(_sep())
    lines.append("INFORMACIÓN DEL GUIDELINE")
    lines.append(f"Título: {data['title']}")
    lines.append(f"URL Backoffice: {data['backoffice_url']}")
    lines.append(f"URL Documento Original: {data['source_url']}")
    lines.append(f"Payer: {data['payer']}")
    lines.append(f"Subsección validada: {data['subsection']}")
    lines.append(_sep())
    lines.append("RESULTADO GENERAL")
    lines.append(f"Códigos (CPT / HCPCS / ICD-10): {codes_overall}")
    lines.append(f"Markdown: {data['markdown_result']}")
    lines.append(f"Decision Tree: {data['tree_result']}")
    lines.append(_sep())
    lines.append("VALIDACIÓN DE CÓDIGOS")
    lines.append("")
    lines.append("— CPT —")
    lines.append(f"Resultado: {data['cpt_result']}")
    lines.append(f"Hallazgo: {data['cpt_finding']}")
    lines.append("")
    lines.append("— HCPCS —")
    lines.append(f"Resultado: {data['hcpcs_result']}")
    lines.append(f"Hallazgo: {data['hcpcs_finding']}")
    lines.append("")
    lines.append("— ICD-10 —")
    lines.append(f"Resultado: {data['icd10_result']}")
    lines.append(f"Hallazgo: {data['icd10_finding']}")
    lines.append(_sep())
    lines.append("VALIDACIÓN DE MARKDOWN")
    lines.append("")
    lines.append(f"Resultado: {data['markdown_result']}")
    lines.append(f"Hallazgo: {data['markdown_finding']}")
    lines.append(_sep())
    lines.append("VALIDACIÓN DE DECISION TREE")
    lines.append("")
    lines.append(f"Resultado: {data['tree_result']}")
    lines.append(f"Hallazgo: {data['tree_finding']}")
    lines.append(_sep())
    lines.append("NOTAS")
    lines.append("")
    for i, note in enumerate(data["notes"], start=1):
        lines.append(f"{i}. {note}")

    return "\n".join(lines).strip("\n")


def generate_report_en(data):
    codes_overall = data["codes_overall_en"]  # "Correct" | "BUG" | "PENDING"

    lines = []
    lines.append(f"VALIDATION REPORT — ROW {data['row_id']}")
    lines.append("Project: Ethermed QA")
    lines.append(f"Payer: {data['payer']}")
    lines.append(f"Date: {data['date_en']}")
    lines.append("Validated by: Alexander Martinez")
    lines.append(_sep())
    lines.append("GUIDELINE INFORMATION")
    lines.append(f"Title: {data['title']}")
    lines.append(f"Backoffice URL: {data['backoffice_url']}")
    lines.append(f"Source Document URL: {data['source_url']}")
    lines.append(f"Payer: {data['payer']}")
    lines.append(f"Validated section: {data['subsection_en']}")
    lines.append(_sep())
    lines.append("OVERALL RESULTS")
    lines.append(f"Codes (CPT / HCPCS / ICD-10): {codes_overall}")
    lines.append(f"Markdown: {data['markdown_result_en']}")
    lines.append(f"Decision Tree: {data['tree_result_en']}")
    lines.append(_sep())
    lines.append("CODE VALIDATION")
    lines.append("")
    lines.append("— CPT —")
    lines.append(f"Result: {data['cpt_result_en']}")
    lines.append(f"Finding: {data['cpt_finding_en']}")
    lines.append("")
    lines.append("— HCPCS —")
    lines.append(f"Result: {data['hcpcs_result_en']}")
    lines.append(f"Finding: {data['hcpcs_finding_en']}")
    lines.append("")
    lines.append("— ICD-10 —")
    lines.append(f"Result: {data['icd10_result_en']}")
    lines.append(f"Finding: {data['icd10_finding_en']}")
    lines.append(_sep())
    lines.append("MARKDOWN VALIDATION")
    lines.append("")
    lines.append(f"Result: {data['markdown_result_en']}")
    lines.append(f"Finding: {data['markdown_finding_en']}")
    lines.append(_sep())
    lines.append("DECISION TREE VALIDATION")
    lines.append("")
    lines.append(f"Result: {data['tree_result_en']}")
    lines.append(f"Finding: {data['tree_finding_en']}")
    lines.append(_sep())

    return "\n".join(lines).strip("\n")