# -*- coding: utf-8 -*-
"""
Cliente Flask para pruebas con acceso directo al test_client.
Gestiona autenticación, sesiones y contexto de aplicación.
"""
import sys
import os
import pytest

# Asegurar que evidence_system y el proyecto raíz estén en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import ADMIN_USERNAME, ADMIN_PASSWORD

from app import app, db, User, Student, Attendance
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='function')
def test_app():
    """Configura la app Flask con BD en memoria para tests aislados."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'evidence_test_key'
    return app


@pytest.fixture(scope='function')
def client(test_app):
    """Cliente HTTP de prueba con BD limpia."""
    with test_app.app_context():
        db.create_all()
        _create_admin()
        yield test_app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def auth_client(client):
    """Cliente ya autenticado como admin."""
    client.post('/login', data={
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD,
    }, follow_redirects=True)
    return client


@pytest.fixture(scope='function')
def auth_client_with_student(auth_client):
    """Cliente autenticado con un estudiante de prueba precargado."""
    with app.app_context():
        s = Student(
            student_code='20210001',
            first_name='Juan',
            last_name='Pérez López',
            career='Ingeniería de Sistemas',
            email='juan.perez@unsa.edu.pe'
        )
        db.session.add(s)
        db.session.commit()
    return auth_client


def _create_admin():
    """Crea el usuario administrador de pruebas."""
    if not User.query.filter_by(username=ADMIN_USERNAME).first():
        u = User(
            username=ADMIN_USERNAME,
            password_hash=generate_password_hash(ADMIN_PASSWORD)
        )
        db.session.add(u)
        db.session.commit()
