# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════
  RUN_ALL.PY — Ejecutor Principal de toda la Suite de Evidencia
  
  Ejecuta secuencialmente:
    1. Tests PE (TC-001 a TC-005)
    2. Tests AVL (TC-006 a TC-008)
    3. Tests Negativos (TC-009, TC-012, TC-013)
    4. Tests de Seguridad (TC-010, TC-011)
  
  Genera:
    - Logs individuales por TC en evidence/logs/
    - Respuestas JSON en evidence/responses/
    - Reporte consolidado en evidence/reports/evidence_report.md
═══════════════════════════════════════════════════════════════
"""
import sys
import os
import subprocess
import json
import datetime

# Configurar path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SYSTEM_DIR)

from config import EVIDENCE_DIR, LOGS_DIR, RESPONSES_DIR, REPORTS_DIR
from utils.report_generator import generate_evidence_report


def run_pytest_suite(test_file, label):
    """Ejecuta un archivo de tests con pytest y retorna el exit code."""
    print(f'\n{"="*60}')
    print(f'  Ejecutando: {label}')
    print(f'  Archivo: {test_file}')
    print(f'{"="*60}\n')

    # Usar 'py -3' en Windows para localizar el Python con pytest
    python_cmd = ['py', '-3'] if os.name == 'nt' else [sys.executable]
    result = subprocess.run(
        python_cmd + ['-m', 'pytest', test_file, '-v', '--tb=short', '-x'],
        cwd=SYSTEM_DIR,
        capture_output=False
    )
    return result.returncode


def collect_evidence():
    """Recolecta todos los archivos JSON de evidencia generados."""
    results = []
    for filename in sorted(os.listdir(RESPONSES_DIR)):
        if filename.endswith('.json'):
            filepath = os.path.join(RESPONSES_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.append(data)
    return results


def print_summary(results):
    """Imprime resumen final en consola."""
    total = len(results)
    passed = sum(1 for r in results if r['STATUS'] == 'PASS')
    failed = sum(1 for r in results if r['STATUS'] == 'FAIL')
    exceptions = sum(1 for r in results if r['STATUS'] == 'EXCEPTION')
    fail_rate = round(((failed + exceptions) / total) * 100, 1) if total else 0

    print(f'\n{"="*60}')
    print(f'  RESUMEN FINAL DE EJECUCIÓN')
    print(f'{"="*60}')
    print(f'  Total ejecutados : {total}')
    print(f'  PASS             : {passed}')
    print(f'  FAIL             : {failed}')
    print(f'  EXCEPTION        : {exceptions}')
    print(f'  Tasa de defectos : {fail_rate}%')
    print(f'{"="*60}')

    bugs = [r for r in results if r.get('BUG_ID')]
    if bugs:
        print(f'\n  BUGS CONFIRMADOS:')
        for b in bugs:
            print(f'    [{b["SEVERITY"]}] {b["BUG_ID"]} — {b["TEST_ID"]}: {b["STATUS"]}')

    print(f'\n  Evidencia en: {EVIDENCE_DIR}')
    print(f'{"="*60}\n')


def main():
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'\n{"#"*60}')
    print(f'  SISTEMA DE EVIDENCIA QA — AsistPro')
    print(f'  Ejecución iniciada: {timestamp}')
    print(f'{"#"*60}')

    tests_dir = os.path.join(SYSTEM_DIR, 'tests')

    suites = [
        (os.path.join(tests_dir, 'test_pe.py'), 'Partición de Equivalencia (PE)'),
        (os.path.join(tests_dir, 'test_avl.py'), 'Análisis de Valores Límite (AVL)'),
        (os.path.join(tests_dir, 'test_negative.py'), 'Pruebas Negativas y Restricciones'),
        (os.path.join(tests_dir, 'test_security.py'), 'Pruebas de Seguridad'),
    ]

    exit_codes = []
    for test_file, label in suites:
        if os.path.exists(test_file):
            code = run_pytest_suite(test_file, label)
            exit_codes.append(code)
        else:
            print(f'[!] Archivo no encontrado: {test_file}')

    # Recolectar toda la evidencia generada
    results = collect_evidence()

    if results:
        # Generar reporte consolidado
        report_path = generate_evidence_report(results)
        # Imprimir resumen
        print_summary(results)
    else:
        print('\n[!] No se generaron archivos de evidencia.')
        print('    Verifique que los tests se ejecutaron correctamente.')

    end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'  Ejecución finalizada: {end_time}')


if __name__ == '__main__':
    main()
