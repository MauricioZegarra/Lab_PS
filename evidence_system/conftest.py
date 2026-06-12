# -*- coding: utf-8 -*-
"""
conftest.py — Configuración global de pytest para el sistema de evidencia.
Importa las fixtures del flask_test_client para disponibilidad global.
"""
import sys
import os

# Asegurar paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar todas las fixtures para hacerlas disponibles globalmente
from clients.flask_test_client import (
    test_app,
    client,
    auth_client,
    auth_client_with_student,
)
