# -*- coding: utf-8 -*-
"""
Helpers de aserción personalizados para el sistema de evidencia QA.
"""


def assert_status_code(response, expected, tc_id=''):
    """Verifica que el status code sea el esperado."""
    actual = response.status_code
    assert actual == expected, (
        f'[{tc_id}] Status code esperado {expected}, obtenido {actual}'
    )


def assert_contains(data: bytes, substring: str, tc_id=''):
    """Verifica que data contenga el substring (case-insensitive en bytes)."""
    assert substring.encode('utf-8') in data or substring.lower().encode('utf-8') in data.lower(), (
        f'[{tc_id}] No se encontró "{substring}" en la respuesta'
    )


def assert_not_contains(data: bytes, substring: str, tc_id=''):
    """Verifica que data NO contenga el substring."""
    assert substring.encode('utf-8') not in data, (
        f'[{tc_id}] Se encontró "{substring}" inesperadamente en la respuesta'
    )


def assert_db_exists(model, tc_id='', **filters):
    """Verifica que un registro exista en la BD."""
    result = model.query.filter_by(**filters).first()
    assert result is not None, (
        f'[{tc_id}] No se encontró registro con filtros {filters}'
    )
    return result


def assert_db_not_exists(model, tc_id='', **filters):
    """Verifica que un registro NO exista en la BD."""
    result = model.query.filter_by(**filters).first()
    assert result is None, (
        f'[{tc_id}] Se encontró registro inesperado con filtros {filters}'
    )
