# -*- coding: utf-8 -*-
"""
Constructores de payloads para cada tipo de prueba.
"""
import datetime


def student_payload(code='20210099', first_name='Test', last_name='Alumno',
                    career='Ingeniería de Sistemas', email='test@unsa.edu.pe'):
    """Payload base para crear/editar estudiante."""
    return {
        'student_code': code,
        'first_name': first_name,
        'last_name': last_name,
        'career': career,
        'email': email,
    }


def login_payload(username='admin', password='admin123'):
    """Payload base para login."""
    return {'username': username, 'password': password}


def attendance_payload(student_id, status='Presente', date=None):
    """Payload base para registro de asistencia."""
    if date is None:
        date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    return {
        'attendance_date': date,
        f'status_{student_id}': status,
    }


def api_check_payload(field='student_code', value='20210001'):
    """Payload JSON para /api/check-availability."""
    return {'field': field, 'value': value}
