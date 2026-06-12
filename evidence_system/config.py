# -*- coding: utf-8 -*-
"""
Configuración centralizada del sistema de evidencia QA.
"""
import os
import sys

# ── Rutas del proyecto ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)  # AsistPro/
EVIDENCE_DIR = os.path.join(BASE_DIR, 'evidence')
LOGS_DIR = os.path.join(EVIDENCE_DIR, 'logs')
RESPONSES_DIR = os.path.join(EVIDENCE_DIR, 'responses')
REPORTS_DIR = os.path.join(EVIDENCE_DIR, 'reports')

# Garantizar que los directorios existan
for d in [EVIDENCE_DIR, LOGS_DIR, RESPONSES_DIR, REPORTS_DIR]:
    os.makedirs(d, exist_ok=True)

# Agregar raíz del proyecto al path para importar app
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# ── Credenciales del sistema bajo prueba ──
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# ── Constantes esperadas según el documento técnico ──
MAX_FIRST_NAME_LENGTH = 50
MAX_LAST_NAME_LENGTH = 75
MAX_CAREER_LENGTH = 100
MAX_EMAIL_LENGTH = 120
STUDENT_CODE_LENGTH = 8
MAX_USERNAME_LENGTH = 50
MAX_PASSWORD_LENGTH = 256
LOCKOUT_THRESHOLD = 5
VALID_STATUSES = {'Presente', 'Tardanza', 'Falta'}
