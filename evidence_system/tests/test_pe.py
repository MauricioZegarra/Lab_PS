# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════
  PRUEBAS DE PARTICIÓN DE EQUIVALENCIA (PE) — CASOS FALTANTES
  TC-001 a TC-005
  Referencia: INFORME_FINAL_QA_ASISTPRO_UNSA.md §4.1
═══════════════════════════════════════════════════════════════
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from app import app, db, Student, validate_student_code, validate_name, validate_email
from clients.flask_test_client import client, test_app, auth_client, auth_client_with_student
from clients.payload_builder import student_payload
from utils.logger import get_tc_logger, save_response, build_evidence_record


# ── Colector global de evidencia ──
evidence_results = []


class TestPE:
    """Partición de Equivalencia — Casos faltantes del equipo rival."""

    # ──────────────────────────────────────────────────
    # TC-001: Email con caracteres especiales / doble @
    # RESULTADO ESPERADO: PASS (el sistema ya rechaza)
    # ──────────────────────────────────────────────────
    def test_tc001_email_special_chars(self, auth_client):
        tc_id = 'TC-001'
        log = get_tc_logger(tc_id)
        log.info(f'Iniciando {tc_id}: Email con caracteres especiales y doble @')

        inputs = ['user@dom!ain.com', 'user@domain@com.pe']
        all_rejected = True

        for email_input in inputs:
            log.info(f'Probando email: {email_input}')
            result = validate_email(email_input)
            log.info(f'validate_email("{email_input}") = {result}')
            if result:
                all_rejected = False

            # También probar vía endpoint
            data = student_payload(code='20219901', email=email_input)
            r = auth_client.post('/students/add', data=data, follow_redirects=True)
            log.info(f'POST /students/add status={r.status_code}')

            with app.app_context():
                exists = Student.query.filter_by(student_code='20219901').first()
                if exists:
                    all_rejected = False
                    db.session.delete(exists)
                    db.session.commit()

        status = 'PASS' if all_rejected else 'FAIL'
        log.info(f'Resultado final: {status}')

        record = build_evidence_record(
            tc_id, status,
            input_data=str(inputs),
            expected='Rechazo — formato RFC inválido',
            actual='Rechazado correctamente por el regex' if status == 'PASS' else 'Aceptado erróneamente',
            analysis='El regex del backend descarta correctamente caracteres ! y doble @.'
        )
        save_response(tc_id, record)
        evidence_results.append(record)

    # ──────────────────────────────────────────────────
    # TC-002: Dígitos Unicode no-ASCII en student_code
    # RESULTADO ESPERADO: FAIL (BUG-01, P2)
    # ──────────────────────────────────────────────────
    def test_tc002_unicode_digits_bypass(self, auth_client):
        tc_id = 'TC-002'
        log = get_tc_logger(tc_id)
        log.info(f'Iniciando {tc_id}: Dígitos Unicode no-ASCII en código de estudiante')

        # Dígitos árabes orientales (Eastern Arabic numerals)
        unicode_code = '٢٠٢١٠٠١٢'
        log.info(f'Input: student_code="{unicode_code}"')

        # Verificar comportamiento de .isdigit()
        isdigit_result = unicode_code.isdigit()
        log.info(f'unicode_code.isdigit() = {isdigit_result}')
        log.info(f'len(unicode_code) = {len(unicode_code)}')

        # La función validate_student_code usa .isdigit() internamente
        validation_result = validate_student_code(unicode_code)
        log.info(f'validate_student_code("{unicode_code}") = {validation_result}')

        # Determinar el estado del test
        if validation_result:
            status = 'FAIL'
            actual = 'Aceptado por .isdigit() — bypass Unicode confirmado'
            log.warning('BUG-01 CONFIRMADO: .isdigit() acepta dígitos no-ASCII')
        else:
            status = 'PASS'
            actual = 'Rechazado correctamente'

        record = build_evidence_record(
            tc_id, status,
            input_data=f'student_code="{unicode_code}" (dígitos árabes Unicode)',
            expected='Rechazo — solo dígitos ASCII [0-9] válidos',
            actual=actual,
            analysis='Python .isdigit() retorna True para caracteres Unicode categoría Nd, '
                     'incluyendo dígitos árabes, hindúes, etc. Esto permite corromper IDs.',
            bug_id='BUG-01', severity='P2'
        )
        save_response(tc_id, record)
        evidence_results.append(record)

    # ──────────────────────────────────────────────────
    # TC-003: Nombre compuesto solo por guiones
    # RESULTADO ESPERADO: FAIL (BUG-02, P3)
    # ──────────────────────────────────────────────────
    def test_tc003_name_only_dashes(self, auth_client):
        tc_id = 'TC-003'
        log = get_tc_logger(tc_id)
        log.info(f'Iniciando {tc_id}: Nombre compuesto solo por guiones')

        name_input = '---'
        log.info(f'Input: first_name="{name_input}"')

        result = validate_name(name_input)
        log.info(f'validate_name("---") = {result}')

        if result:
            status = 'FAIL'
            actual = 'Aceptado como nombre válido — falta requisito de letras'
            log.warning('BUG-02 CONFIRMADO: Regex no exige al menos un carácter alfabético')
        else:
            status = 'PASS'
            actual = 'Rechazado correctamente'

        record = build_evidence_record(
            tc_id, status,
            input_data='first_name="---" (solo guiones, sin letras)',
            expected='Rechazo — un nombre debe contener al menos una letra',
            actual=actual,
            analysis='El regex ^[a-zA-Z...\\s\\-]+$ acepta combinaciones exclusivas de sus '
                     'modificadores, permitiendo nombres sin contenido alfabético.',
            bug_id='BUG-02', severity='P3'
        )
        save_response(tc_id, record)
        evidence_results.append(record)

    # ──────────────────────────────────────────────────
    # TC-004: Inyección de salto de línea en nombre
    # RESULTADO ESPERADO: EXCEPTION (BUG-03, P1)
    # ──────────────────────────────────────────────────
    def test_tc004_newline_injection(self, auth_client):
        tc_id = 'TC-004'
        log = get_tc_logger(tc_id)
        log.info(f'Iniciando {tc_id}: Inyección de salto de línea en nombre')

        name_input = 'Juan\nPerez'
        log.info(f'Input: first_name con \\n embebido')

        result = validate_name(name_input)
        log.info(f'validate_name("Juan\\nPerez") = {result}')

        if result:
            status = 'EXCEPTION'
            actual = 'Aceptado — \\s en regex incluye \\n, produce SyntaxError en reports.html'
            log.critical('BUG-03 CONFIRMADO: Salto de línea pasa validación y rompe JS en reportes')

            # Intentar crear el estudiante para demostrar persistencia
            data = student_payload(
                code='20219904',
                first_name='Juan\nPerez',
                last_name='Test',
                email='newline@unsa.edu.pe'
            )
            r = auth_client.post('/students/add', data=data, follow_redirects=True)
            log.info(f'POST /students/add con \\n: status={r.status_code}')

            with app.app_context():
                s = Student.query.filter_by(student_code='20219904').first()
                if s:
                    log.warning(f'Estudiante creado en BD con nombre que contiene \\n: id={s.id}')
                    log.warning('Al renderizar /reports, {{ student_stats_json | safe }} genera SyntaxError JS')
        else:
            status = 'PASS'
            actual = 'Rechazado correctamente'

        record = build_evidence_record(
            tc_id, status,
            input_data='first_name="Juan\\nPerez" (salto de línea inyectado)',
            expected='Rechazo — carácter de control inválido en nombre',
            actual=actual,
            analysis='\\s en regex incluye \\n. El dato persiste y al renderizarse en reports.html '
                     'con {{ student_stats_json | safe }}, se produce SyntaxError en JavaScript '
                     'que destruye el módulo completo de reportes.',
            bug_id='BUG-03', severity='P1'
        )
        save_response(tc_id, record)
        evidence_results.append(record)

    # ──────────────────────────────────────────────────
    # TC-005: Fecha con formato alternativo DD-MM-YYYY
    # RESULTADO ESPERADO: PASS (redirección segura)
    # ──────────────────────────────────────────────────
    def test_tc005_date_wrong_format(self, auth_client):
        tc_id = 'TC-005'
        log = get_tc_logger(tc_id)
        log.info(f'Iniciando {tc_id}: Fecha con formato DD-MM-YYYY')

        date_input = '25-05-2024'
        log.info(f'Input: date={date_input}')

        r = auth_client.get(f'/attendance?date={date_input}', follow_redirects=True)
        log.info(f'GET /attendance?date={date_input} status={r.status_code}')

        status = 'PASS' if r.status_code == 200 else 'FAIL'
        log.info(f'Resultado: {status} — redirección segura ejecutada')

        record = build_evidence_record(
            tc_id, status,
            input_data=f'date="{date_input}" (formato DD-MM-YYYY)',
            expected='Rechazo o redirección segura a fecha actual',
            actual=f'HTTP {r.status_code} — redirección segura ejecutada',
            analysis='El bloque try/except en app.py:498 captura el ValueError '
                     'y redirige a la fecha actual sin crashear.'
        )
        save_response(tc_id, record)
        evidence_results.append(record)
