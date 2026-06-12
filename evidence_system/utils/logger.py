# -*- coding: utf-8 -*-
"""
Logger estructurado para el sistema de evidencia QA.
Genera archivos .log por cada test case ejecutado.
"""
import logging
import os
import json
import datetime
from config import LOGS_DIR, RESPONSES_DIR


def get_tc_logger(tc_id: str) -> logging.Logger:
    """Retorna un logger dedicado a un Test Case específico."""
    logger = logging.getLogger(tc_id)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    log_path = os.path.join(LOGS_DIR, f'{tc_id}.log')
    fh = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger


def save_response(tc_id: str, data: dict):
    """Guarda la respuesta HTTP como JSON estructurado."""
    path = os.path.join(RESPONSES_DIR, f'{tc_id}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def build_evidence_record(tc_id, status, input_data, expected, actual,
                          analysis='', bug_id=None, severity=None):
    """Construye un diccionario de evidencia estandarizado."""
    record = {
        'TEST_ID': tc_id,
        'TIMESTAMP': datetime.datetime.now().isoformat(),
        'STATUS': status,
        'INPUT': input_data,
        'EXPECTED': expected,
        'ACTUAL': actual,
        'EVIDENCE_FILES': {
            'log': f'logs/{tc_id}.log',
            'response': f'responses/{tc_id}.json',
        },
        'ANALYSIS': analysis,
    }
    if bug_id:
        record['BUG_ID'] = bug_id
        record['SEVERITY'] = severity
    return record
