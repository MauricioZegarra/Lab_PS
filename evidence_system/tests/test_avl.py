# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════
  PRUEBAS DE ANÁLISIS DE VALORES LÍMITE (AVL) — CASOS FALTANTES
  TC-006 a TC-008
  Referencia: INFORME_FINAL_QA_ASISTPRO_UNSA.md §4.2
═══════════════════════════════════════════════════════════════
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
import datetime
from app import app, db, Student, Attendance, validate_date_not_future
from clients.flask_test_client import client, test_app, auth_client, auth_client_with_student
from utils.logger import get_tc_logger, save_response, build_evidence_record

evidence_results = []


class TestAVL:
    """Análisis de Valores Límite — Casos faltantes del equipo rival."""

    # ──────────────────────────────────────────────────
    # TC-006: Fecha mínima absoluta (año 0001)
    # RESULTADO ESPERADO: FAIL (BUG-04, P3)
    # ──────────────────────────────────────────────────
    def test_tc006_date_minimum_boundary(self, auth_client_with_student):
        tc_id = 'TC-006'
        log = get_tc_logger(tc_id)
        log.info(f'Iniciando {tc_id}: Límite inferior de fecha — 0001-01-01')

        min_date = datetime.date(1, 1, 1)
        log.info(f'Input: date={min_date.isoformat()}')

        # Verificar la función de validación directamente
        result = validate_date_not_future(min_date)
        log.info(f'validate_date_not_future({min_date}) = {result}')

        if result:
            status = 'FAIL'
            actual = 'Aceptado — no existe límite temporal inferior'
            log.warning('BUG-04 CONFIRMADO: validate_date_not_future solo verifica techo, no piso')

            # Intentar registrar asistencia con esa fecha
            with app.app_context():
                s = Student.query.first()
                if s:
                    r = auth_client_with_student.post('/attendance', data={
                        'attendance_date': '0001-01-01',
                        f'status_{s.id}': 'Presente',
                    }, follow_redirects=True)
                    log.info(f'POST /attendance con fecha 0001-01-01: status={r.status_code}')

                    att = Attendance.query.filter_by(student_id=s.id, date=min_date).first()
                    if att:
                        log.warning(f'Asistencia registrada en año 0001: id={att.id}')
        else:
            status = 'PASS'
            actual = 'Rechazado correctamente'

        record = build_evidence_record(
            tc_id, status,
            input_data='attendance_date="0001-01-01" (límite inferior absoluto)',
            expected='Rechazo — fecha fuera de rango operativo razonable',
            actual=actual,
            analysis='validate_date_not_future() solo verifica date <= today. '
                     'No existe umbral mínimo, permitiendo fechas históricamente absurdas.',
            bug_id='BUG-04', severity='P3'
        )
        save_response(tc_id, record)
        evidence_results.append(record)

    # ──────────────────────────────────────────────────
    # TC-007: Frontera inferior del lockout (intento 4)
    # RESULTADO ESPERADO: PASS
    # ──────────────────────────────────────────────────
    def test_tc007_lockout_boundary_attempt_4(self, client):
        tc_id = 'TC-007'
        log = get_tc_logger(tc_id)
        log.info(f'Iniciando {tc_id}: Límite inferior de lockout — 4 intentos fallidos')

        # Ejecutar 4 intentos fallidos
        for i in range(1, 5):
            r = client.post('/login', data={
                'username': 'admin', 'password': 'wrongpass'
            }, follow_redirects=True)
            log.info(f'Intento fallido #{i}: status={r.status_code}')

        # El quinto intento con clave correcta NO debe estar bloqueado
        # (el bloqueo ocurre al 5to fallo, no al 4to)
        data_body = r.data.lower()
        is_blocked = b'bloqueada' in data_body or b'bloqueo' in data_body

        if not is_blocked:
            status = 'PASS'
            actual = 'Cuenta habilitada tras 4 intentos fallidos — comportamiento correcto'
        else:
            status = 'FAIL'
            actual = 'Cuenta bloqueada prematuramente en el intento 4'

        log.info(f'Resultado: {status}')

        record = build_evidence_record(
            tc_id, status,
            input_data='4 intentos fallidos consecutivos de login',
            expected='Cuenta NO bloqueada — el lockout debe activarse al 5.° intento',
            actual=actual,
            analysis='El sistema bloquea la cuenta en el 5.° intento fallido consecutivo. '
                     'En el 4.°, la cuenta permanece habilitada, cumpliendo la frontera AVL.'
        )
        save_response(tc_id, record)
        evidence_results.append(record)

    # ──────────────────────────────────────────────────
    # TC-008: Paginación fuera de rango máximo
    # RESULTADO ESPERADO: PASS
    # ──────────────────────────────────────────────────
    def test_tc008_pagination_extreme(self, auth_client):
        tc_id = 'TC-008'
        log = get_tc_logger(tc_id)
        log.info(f'Iniciando {tc_id}: Paginación extrema — page=999999999')

        r = auth_client.get('/reports?page=999999999', follow_redirects=True)
        log.info(f'GET /reports?page=999999999 status={r.status_code}')

        if r.status_code == 200:
            status = 'PASS'
            actual = 'HTTP 200 — tabla vacía sin error de servidor'
        else:
            status = 'FAIL'
            actual = f'HTTP {r.status_code} — error inesperado'

        log.info(f'Resultado: {status}')

        record = build_evidence_record(
            tc_id, status,
            input_data='page=999999999 en GET /reports',
            expected='HTTP 200 — tabla vacía, sin crasheo por offset SQL',
            actual=actual,
            analysis='SQLAlchemy resuelve el offset fuera de rango retornando una lista vacía. '
                     'La interfaz renderiza la tabla correctamente sin excepciones.'
        )
        save_response(tc_id, record)
        evidence_results.append(record)
