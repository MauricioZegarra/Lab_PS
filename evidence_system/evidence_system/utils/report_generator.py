# -*- coding: utf-8 -*-
"""
Generador de reporte consolidado de evidencia QA.
Produce un archivo Markdown con todos los resultados de ejecución.
"""
import os
import json
import datetime
from config import REPORTS_DIR, RESPONSES_DIR, LOGS_DIR


def generate_evidence_report(results: list):
    """
    Genera evidence/reports/evidence_report.md a partir de una lista
    de diccionarios de evidencia producidos por build_evidence_record().
    """
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    total = len(results)
    passed = sum(1 for r in results if r['STATUS'] == 'PASS')
    failed = sum(1 for r in results if r['STATUS'] == 'FAIL')
    exceptions = sum(1 for r in results if r['STATUS'] == 'EXCEPTION')
    fail_rate = round(((failed + exceptions) / total) * 100, 1) if total else 0

    bugs = [r for r in results if r.get('BUG_ID')]
    p1 = sum(1 for b in bugs if b.get('SEVERITY') == 'P1')
    p2 = sum(1 for b in bugs if b.get('SEVERITY') == 'P2')
    p3 = sum(1 for b in bugs if b.get('SEVERITY') == 'P3')

    lines = []
    lines.append('# Reporte de Evidencia QA — AsistPro')
    lines.append('')
    lines.append(f'**Generado:** {timestamp}')
    lines.append(f'**Total de casos ejecutados:** {total}')
    lines.append(f'**PASS:** {passed} | **FAIL:** {failed} | **EXCEPTION:** {exceptions}')
    lines.append(f'**Tasa de defectos:** {fail_rate}%')
    lines.append('')
    lines.append('---')
    lines.append('')

    # ── Resumen ejecutivo ──
    lines.append('## Resumen Ejecutivo')
    lines.append('')
    lines.append(f'Se ejecutaron {total} casos de prueba derivados de la auditoría de cobertura PE/AVL. '
                 f'De estos, {failed + exceptions} resultaron en defectos confirmados (FAIL o EXCEPTION), '
                 f'arrojando una tasa de detección del {fail_rate}%.')
    lines.append('')

    # ── Matriz de bugs confirmados ──
    lines.append('## Matriz de Bugs Confirmados')
    lines.append('')
    lines.append('| BUG ID | TC | Severidad | Estado |')
    lines.append('| :--- | :--- | :--- | :--- |')
    for b in bugs:
        lines.append(f'| {b["BUG_ID"]} | {b["TEST_ID"]} | {b["SEVERITY"]} | {b["STATUS"]} |')
    lines.append('')
    lines.append(f'**P1 (Crítico):** {p1} | **P2 (Alto):** {p2} | **P3 (Medio):** {p3}')
    lines.append('')
    lines.append('---')
    lines.append('')

    # ── Detalle por TC ──
    lines.append('## Detalle de Ejecución por Test Case')
    lines.append('')

    for r in results:
        lines.append(f'### {r["TEST_ID"]}')
        lines.append('')
        lines.append(f'- **Estado:** {r["STATUS"]}')
        lines.append(f'- **Input:** `{r["INPUT"]}`')
        lines.append(f'- **Esperado:** {r["EXPECTED"]}')
        lines.append(f'- **Obtenido:** {r["ACTUAL"]}')
        if r.get('BUG_ID'):
            lines.append(f'- **Bug asociado:** {r["BUG_ID"]} ({r["SEVERITY"]})')
        lines.append(f'- **Análisis:** {r["ANALYSIS"]}')
        lines.append(f'- **Log:** `{r["EVIDENCE_FILES"]["log"]}`')
        lines.append(f'- **Response:** `{r["EVIDENCE_FILES"]["response"]}`')
        lines.append('')

    # ── Tabla resumen ──
    lines.append('---')
    lines.append('')
    lines.append('## Tabla Consolidada')
    lines.append('')
    lines.append('| TC | Tipo | Estado | Hallazgo | Severidad |')
    lines.append('| :--- | :--- | :--- | :--- | :--- |')

    type_map = {
        'TC-001': 'PE', 'TC-002': 'PE', 'TC-003': 'PE', 'TC-004': 'PE', 'TC-005': 'PE',
        'TC-006': 'AVL', 'TC-007': 'AVL', 'TC-008': 'AVL',
        'TC-009': 'Negativa', 'TC-010': 'Negativa', 'TC-011': 'Error',
        'TC-012': 'Restricción', 'TC-013': 'Negocio',
    }
    for r in results:
        tc_type = type_map.get(r['TEST_ID'], 'N/A')
        bug = r.get('BUG_ID', 'Ninguno')
        sev = r.get('SEVERITY', 'N/A')
        lines.append(f'| {r["TEST_ID"]} | {tc_type} | {r["STATUS"]} | {bug} | {sev} |')

    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append(f'*Reporte generado automáticamente por el sistema de evidencia QA — {timestamp}*')

    report_path = os.path.join(REPORTS_DIR, 'evidence_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f'\n[OK] Reporte de evidencia generado: {report_path}')
    return report_path
