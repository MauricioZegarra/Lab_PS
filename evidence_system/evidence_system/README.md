# Sistema de Evidencia QA — AsistPro

Sistema de pruebas y de evidencia para la auditoría de calidad del sistema AsistPro, en el contexto de la práctica **"Guerra de Testers"**.

## Estructura del proyecto

```
evidence_system/
├── README.md
├── requirements.txt
├── config.py
├── conftest.py
│
├── runners/
│   └── run_all.py
│
├── tests/
│   ├── test_pe.py          # TC-001 a TC-005
│   ├── test_avl.py         # TC-006 a TC-008
│   ├── test_negative.py    # TC-009, TC-012, TC-013
│   └── test_security.py    # TC-010, TC-011
│
├── clients/
│   ├── flask_test_client.py
│   └── payload_builder.py
│
├── utils/
│   ├── logger.py
│   ├── assert_helpers.py
│   └── report_generator.py
│
└── evidence/
    ├── logs/          # Un .log por cada TC ejecutado
    ├── responses/     # Un .json por cada TC con evidencia estructurada
    └── reports/       # Reporte consolidado evidence_report.md
```

## Requisitos previos

```bash
pip install pytest flask flask-sqlalchemy werkzeug requests
```

## Ejecución completa

```bash
cd evidence_system
python runners/run_all.py
```

## Ejecución por categoría

```bash
cd evidence_system
pytest tests/test_pe.py -v           # Partición de Equivalencia
pytest tests/test_avl.py -v          # Valores Límite
pytest tests/test_negative.py -v     # Pruebas Negativas
pytest tests/test_security.py -v     # Seguridad
```

## Salida

Tras la ejecución, la carpeta `evidence/` contendrá:

- **`logs/TC-XXX.log`** — Log detallado de cada test case
- **`responses/TC-XXX.json`** — Evidencia estructurada en JSON
- **`reports/evidence_report.md`** — Reporte consolidado Markdown

## Trazabilidad

Cada test case está mapeado directamente a un bug del informe:

| Test Case | Bug ID | Severidad | Técnica     |
| --------- | ------ | --------- | ----------- |
| TC-002    | BUG-01 | P2        | PE          |
| TC-003    | BUG-02 | P3        | PE          |
| TC-004    | BUG-03 | P1        | PE          |
| TC-006    | BUG-04 | P3        | AVL         |
| TC-009    | BUG-05 | P3        | Negativa    |
| TC-010    | BUG-06 | P1        | Seguridad   |
| TC-011    | BUG-07 | P2        | Seguridad   |
| TC-012    | BUG-08 | P3        | Restricción |
