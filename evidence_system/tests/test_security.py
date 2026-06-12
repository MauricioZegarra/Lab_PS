# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════
  PRUEBAS DE SEGURIDAD — CASOS FALTANTES
  TC-010, TC-011
  Referencia: INFORME_FINAL_QA_ASISTPRO_UNSA.md §6
═══════════════════════════════════════════════════════════════
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
import json
from app import app, db, Student
from clients.flask_test_client import client, test_app, auth_client, auth_client_with_student
from utils.logger import get_tc_logger, save_response, build_evidence_record

evidence_results = []


class TestSecurity:
    """Pruebas de Seguridad — Hallazgos críticos."""

    # ──────────────────────────────────────────────────
    # TC-010: CSRF en eliminación de estudiantes
    # RESULTADO ESPERADO: FAIL (BUG-06, P1)
    # ──────────────────────────────────────────────────
    def test_tc010_csrf_delete_student(self, auth_client_with_student):
        tc_id = 'TC-010'
        log = get_tc_logger(tc_id)
        log.info(f'Iniciando {tc_id}: CSRF en eliminación de estudiantes')

        with app.app_context():
            s = Student.query.first()
            sid = s.id
            log.info(f'Estudiante objetivo: id={sid}, code={s.student_code}')

        # Enviar POST sin ningún token CSRF
        log.info('Enviando POST /students/delete sin token CSRF')
        r = auth_client_with_student.post(
            f'/students/delete/{sid}',
            follow_redirects=True
        )
        log.info(f'POST /students/delete/{sid}: status={r.status_code}')

        with app.app_context():
            deleted = Student.query.get(sid)
            if deleted is None:
                status = 'FAIL'
                actual = 'Estudiante eliminado exitosamente sin token CSRF — vulnerabilidad confirmada'
                log.critical('BUG-06 CONFIRMADO: Eliminación sin CSRF exitosa')
            else:
                status = 'PASS'
                actual = 'Eliminación rechazada — protección CSRF activa'

        record = build_evidence_record(
            tc_id, status,
            input_data=f'POST /students/delete/{sid} sin token CSRF',
            expected='HTTP 403 Forbidden — token CSRF ausente o inválido',
            actual=actual,
            analysis='Los formularios POST del sistema carecen completamente de protección '
                     'CSRF (no usan Flask-WTF ni csrf_token()). Cualquier sitio externo '
                     'puede ejecutar operaciones destructivas aprovechando la sesión activa.',
            bug_id='BUG-06', severity='P1'
        )
        save_response(tc_id, record)
        evidence_results.append(record)

    # ──────────────────────────────────────────────────
    # TC-011: API crash con payload nulo
    # RESULTADO ESPERADO: EXCEPTION (BUG-07, P2)
    # ──────────────────────────────────────────────────
    def test_tc011_api_null_payload(self, auth_client):
        tc_id = 'TC-011'
        log = get_tc_logger(tc_id)
        log.info(f'Iniciando {tc_id}: API crash con payload nulo')

        # Enviar body vacío/nulo al endpoint JSON
        log.info('Enviando POST /api/check-availability con body vacío')

        try:
            r = auth_client.post(
                '/api/check-availability',
                data='null',
                content_type='application/json'
            )
            log.info(f'Response status: {r.status_code}')

            if r.status_code == 500:
                status = 'EXCEPTION'
                actual = f'HTTP 500 — crasheo del servidor por AttributeError'
                log.critical('BUG-07 CONFIRMADO: API crashea con payload nulo')
            elif r.status_code == 400:
                status = 'PASS'
                actual = 'HTTP 400 — error manejado correctamente'
            else:
                status = 'FAIL'
                actual = f'HTTP {r.status_code} — comportamiento inesperado'

        except Exception as e:
            status = 'EXCEPTION'
            actual = f'Excepción no controlada: {type(e).__name__}: {str(e)}'
            log.critical(f'Excepción capturada: {actual}')

        record = build_evidence_record(
            tc_id, status,
            input_data='POST /api/check-availability con body vacío (Content-Type: application/json)',
            expected='HTTP 400 — respuesta JSON con descripción del error',
            actual=actual,
            analysis='request.get_json() sin silent=True lanza excepción cuando el body es nulo. '
                     'Al intentar .get("field") sobre NoneType, se produce AttributeError '
                     'que resulta en HTTP 500.',
            bug_id='BUG-07', severity='P2'
        )
        save_response(tc_id, record)
        evidence_results.append(record)

        # Test adicional: body como array vacío
        log.info('Probando con body como array vacío: []')
        try:
            r2 = auth_client.post(
                '/api/check-availability',
                data=json.dumps([]),
                content_type='application/json'
            )
            log.info(f'Response con []: status={r2.status_code}')
        except Exception as e2:
            log.critical(f'Excepción con array vacío: {type(e2).__name__}: {str(e2)}')
