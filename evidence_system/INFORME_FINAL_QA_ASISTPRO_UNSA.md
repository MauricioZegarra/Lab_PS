<style>
body { font-family: 'Georgia', 'Times New Roman', serif; color: #1a1a1a; line-height: 1.8; text-align: justify; max-width: 900px; margin: 0 auto; padding: 40px; background-color: #ffffff; }
h1 { color: #720000; text-align: center; font-size: 2.2em; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 30px; border-bottom: none; }
h2 { color: #720000; border-bottom: 2px solid #720000; padding-bottom: 8px; margin-top: 40px; font-size: 1.6em; }
h3 { color: #4a4a4a; margin-top: 30px; font-family: 'Segoe UI', Arial, sans-serif; }
p { margin-bottom: 20px; }
table { width: 100%; border-collapse: collapse; margin: 30px 0; font-family: 'Segoe UI', Arial, sans-serif; font-size: 0.95em; box-shadow: 0 4px 8px rgba(0,0,0,0.05); border-radius: 8px; overflow: hidden; }
th, td { padding: 15px 18px; border-bottom: 1px solid #eeeeee; text-align: left; }
th { background-color: #720000; color: #ffffff; text-transform: uppercase; font-size: 0.85em; letter-spacing: 0.5px; }
tr:nth-child(even) { background-color: #fafafa; }
tr:hover { background-color: #f1f1f1; }
blockquote { border-left: 6px solid #720000; background-color: #fcf4f4; padding: 20px 25px; margin: 30px 0; font-style: italic; border-radius: 0 8px 8px 0; }
strong { color: #5a0000; }
ul, ol { margin-bottom: 20px; padding-left: 30px; }
li { margin-bottom: 10px; }
</style>

---

# UNIVERSIDAD NACIONAL DE SAN AGUSTÍN DE AREQUIPA

**FACULTAD DE INGENIERÍA DE PRODUCCIÓN Y SERVICIOS**
**ESCUELA PROFESIONAL DE INGENIERÍA DE SISTEMAS**

---

|                 |                                                         |
| --------------- | ------------------------------------------------------- |
| **Curso**       | Pruebas de Software                                     |
| **Práctica**    | Pruebas de Caja Negra – Partición de Equivalencia y AVL |
| **Título**      | Guerra de Testers – Auditoría QA sobre AsistPro         |
| **Docente**     | Diego Alonso Iquira Becerra                             |
| **Año lectivo** | 2026                                                    |

**Integrantes del equipo evaluador:**

| Apellidos y Nombres                |
| ---------------------------------- |
| Zegarra Puma, Mauricio Eduardo     |
| Lopez Arela, Ower Frank            |
| Meza Vizcarra, Cielo Cristal       |
| Zuñiga Villacorta, Peter Sebastian |

---

## 1. RESUMEN EJECUTIVO

El presente documento constituye el informe técnico de auditoría de calidad aplicado al sistema **AsistPro** — sistema de registro y control de asistencia universitaria, desarrollado en Python/Flask con SQLite — en el contexto de la práctica académica _"Guerra de Testers"_.

La evaluación fue realizada bajo la metodología de **Pruebas de Caja Negra**, empleando Partición de Equivalencia (PE), Análisis de Valores Límite (AVL), Pruebas Negativas y Testing Exploratorio. El alcance cubrió la totalidad de los módulos expuestos: Autenticación, Gestión de Estudiantes, Registro de Asistencia, Reportes y la API AJAX de disponibilidad.

Se ejecutaron un total de **13 casos de prueba diseñados para cubrir brechas de cobertura** detectadas en la suite de automatización del equipo rival. Como resultado, se confirmaron **8 defectos funcionales reproducibles**, incluyendo dos vulnerabilidades de severidad **P1** (CSRF y Corrupción del Motor de Reportes), dos de severidad **P2** (crasheo de API y evasión Unicode) y cuatro de severidad **P3** (lógica de negocio y calidad de datos).

**Veredicto de calidad:** El sistema evaluado se cataloga como **No apto para entornos de producción** en su estado actual.

---

## 2. METODOLOGÍA

La auditoría siguió un proceso secuencial de tres fases:

- **Fase 1 – Análisis Documental:** Se revisó el `README.md`, el documento técnico oficial, los casos de prueba entregados (`test_asistpro.py`) y el código fuente (`app.py`, plantillas HTML) para levantar un inventario de validaciones, restricciones y reglas de negocio declaradas.
- **Fase 2 – Auditoría de Cobertura:** Se contrastó el conjunto de pruebas del equipo rival contra todas las validaciones identificadas, detectando brechas en la cobertura PE/AVL.
- **Fase 3 – Ejecución de Casos Faltantes:** Se diseñaron y ejecutaron 13 casos de prueba orientados exclusivamente a cubrir las brechas identificadas.

Las técnicas empleadas fueron:

| Técnica                              | Descripción                                                                                                                            |
| :----------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------- |
| **Black Box Testing**                | Evaluación de comportamiento del sistema a través de entradas y salidas, sin inspección del código interno durante el diseño de casos. |
| **Partición de Equivalencia (PE)**   | División del dominio de entrada en clases válidas e inválidas, asegurando representatividad con un número mínimo de casos.             |
| **Análisis de Valores Límite (AVL)** | Evaluación de los puntos frontera de cada restricción (Límite−1, Límite exacto, Límite+1).                                             |
| **Pruebas Negativas**                | Inyección deliberada de datos malformados, flujos prohibidos y manipulación de peticiones HTTP.                                        |
| **Testing Exploratorio**             | Evaluación heurística no secuencial orientada a descubrir comportamientos inesperados en la integración UI/API.                        |
| **Validación de Requisitos**         | Verificación de la coherencia entre el comportamiento real del sistema y las reglas declaradas en el documento técnico.                |

---

## 3. AUDITORÍA DE COBERTURA DEL EQUIPO RIVAL

### 3.1 Análisis de la Suite Automatizada (`test_asistpro.py`)

La suite de automatización del equipo rival contiene aproximadamente **148 casos de prueba** organizados por módulos (auth, students, attendance, reports, validations, security). Se constató lo siguiente:

| Dimensión              | Evaluación                                                                                                                 |
| :--------------------- | :------------------------------------------------------------------------------------------------------------------------- |
| **PE entregados**      | Correctos para clases obvias: email sin `@`, nombre con XSS, código con letras. Orientados al "Happy Path".                |
| **AVL entregados**     | Cubrieron límites de longitud de campos (Límite−1, Límite, Límite+1) y el umbral de bloqueo de fuerza bruta (5.° intento). |
| **Casos negativos**    | Escasos. Limitados a SQLi básico, credenciales inválidas y XSS en nombres.                                                 |
| **Integración UI/API** | Ausente. Todas las pruebas interactúan directamente con el servidor sin validar lo que el HTML restringe.                  |
| **Manejo de errores**  | No verificado. Ningún test envía payloads nulos o malformados a los endpoints de la API.                                   |

### 3.2 Brechas de Cobertura Identificadas

| Categoría                       | Brecha detectada                                                                                                                                                |
| :------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **PE faltante**                 | Dígitos Unicode no-ASCII aceptados por `.isdigit()`. Nombres compuestos al 100% por caracteres especiales permitidos. Salto de línea (`\n`) en campos de texto. |
| **AVL faltante**                | Frontera temporal inferior (año mínimo en fechas). Verificación positiva de Límite−1 en lockout (intento 4 debe pasar sin bloqueo).                             |
| **Negativo faltante**           | Peticiones POST sin token CSRF. Payload nulo a la API AJAX. Manipulación del campo `career` fuera del `<select>` del navegador.                                 |
| **Regla de negocio no probada** | Asimetría `maxlength` HTML (30) vs constante Python `MAX_FIRST_NAME_LENGTH` (50).                                                                               |

---

## 4. CASOS DE PRUEBA EJECUTADOS

### 4.1 Partición de Equivalencia (PE)

| ID     | Entrada                                          | Resultado esperado                         | Resultado obtenido                                              | Estado        |
| :----- | :----------------------------------------------- | :----------------------------------------- | :-------------------------------------------------------------- | :------------ |
| TC-001 | Email: `user@dom!ain.com` / `user@domain@com.pe` | Rechazo — formato RFC inválido             | Rechazado correctamente por el regex.                           | **PASS**      |
| TC-002 | Código: `٢٠٢١٠٠١٢` (dígitos árabes Unicode)      | Rechazo — no son dígitos ASCII [0-9]       | Aceptado y persistido. `.isdigit()` evalúa `True` para Unicode. | **FAIL**      |
| TC-003 | Nombre: `---` (solo guiones, sin letras)         | Rechazo — debe contener al menos una letra | Aceptado como nombre válido de estudiante.                      | **FAIL**      |
| TC-004 | Nombre: valor con `\n` (salto de línea)          | Rechazo — carácter de control inválido     | Aceptado. Produce `SyntaxError` al renderizar `/reports`.       | **EXCEPTION** |
| TC-005 | Fecha: `25-05-2024` (formato `DD-MM-YYYY`)       | Rechazo o redirección segura               | Redirección segura ejecutada; usa fecha actual.                 | **PASS**      |

### 4.2 Análisis de Valores Límite (AVL)

| ID     | Frontera evaluada                      | Entrada                         | Resultado esperado                                 | Resultado obtenido                           | Estado   |
| :----- | :------------------------------------- | :------------------------------ | :------------------------------------------------- | :------------------------------------------- | :------- |
| TC-006 | Límite inferior de fecha               | `0001-01-01` en `/attendance`   | Rechazo — año fuera de rango operativo             | Aceptado y persistido en BD.                 | **FAIL** |
| TC-007 | Límite inferior de lockout (intento 4) | 4 intentos fallidos en `/login` | Cuenta NO bloqueada; error de credencial solamente | Comportamiento correcto — cuenta habilitada. | **PASS** |
| TC-008 | Límite superior de paginación          | `/reports?page=999999999`       | Tabla vacía, sin error de servidor                 | Tabla vacía mostrada sin excepciones.        | **PASS** |

### 4.3 Pruebas Negativas, de Integración y Seguridad

| ID     | Módulo                         | Entrada                                               | Resultado esperado                         | Resultado obtenido                                          | Estado        |
| :----- | :----------------------------- | :---------------------------------------------------- | :----------------------------------------- | :---------------------------------------------------------- | :------------ |
| TC-009 | POST `/students/add`           | `career="Ingeniería de Hacking"` vía manipulación DOM | Rechazo — valor fuera del catálogo         | Aceptado y persistido. Backend no valida contra lista.      | **FAIL**      |
| TC-010 | POST `/students/delete/1`      | Petición desde origen externo (sin token)             | HTTP 403 — CSRF rechazado                  | HTTP 302 — estudiante eliminado exitosamente.               | **FAIL**      |
| TC-011 | POST `/api/check-availability` | Body `null` con `Content-Type: application/json`      | HTTP 400 — error controlado                | HTTP 500 — `AttributeError: NoneType`.                      | **EXCEPTION** |
| TC-012 | Formulario `/students`         | Nombre de 50 caracteres vía interfaz web              | Guardado exitoso (límite backend = 50)     | UI bloquea en 30 caracteres (`maxlength="30"` hardcodeado). | **FAIL**      |
| TC-013 | POST `/students/edit/2`        | `student_code` perteneciente al estudiante ID=1       | Error de colisión; actualización rechazada | Colisión prevenida correctamente por ORM.                   | **PASS**      |

---

## 5. BUGS CONFIRMADOS

Se documentan los **8 defectos funcionales reproducibles** confirmados durante la ejecución de pruebas.

---

### BUG-01 · Evasión de validación numérica mediante Unicode

| Campo            | Detalle                                                                       |
| :--------------- | :---------------------------------------------------------------------------- |
| **Caso**         | TC-002                                                                        |
| **Tipo**         | Lógica de Validación / Calidad de Datos                                       |
| **Evidencia**    | `app.py:131` — `code.isdigit()` retorna `True` para dígitos Unicode no-ASCII. |
| **Reproducción** | Enviar `student_code=٢٠٢١٠٠١٢` en POST a `/students/add`.                     |
| **Esperado**     | Rechazo con mensaje de validación de formato.                                 |
| **Obtenido**     | Registro guardado en base de datos con ID no-ASCII.                           |
| **Severidad**    | **P2**                                                                        |

---

### BUG-02 · Nombre semánticamente vacío aceptado por el validador de texto

| Campo            | Detalle                                                                                      |
| :--------------- | :------------------------------------------------------------------------------------------- |
| **Caso**         | TC-003                                                                                       |
| **Tipo**         | Validación PE Incorrecta                                                                     |
| **Evidencia**    | `app.py:142` — Regex `^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$` no exige presencia de letra alfabética. |
| **Reproducción** | Registrar estudiante con `first_name=---`.                                                   |
| **Esperado**     | Rechazo — el nombre debe contener al menos una letra.                                        |
| **Obtenido**     | Registro creado exitosamente en base de datos.                                               |
| **Severidad**    | **P3**                                                                                       |

---

### BUG-03 · Inyección de salto de línea colapsa el módulo de Reportes

| Campo            | Detalle                                                                                                                        |
| :--------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| **Caso**         | TC-004                                                                                                                         |
| **Tipo**         | Excepción no controlada / Corrupción de interfaz                                                                               |
| **Evidencia**    | `app.py:142` — `\s` en regex incluye `\n`. `reports.html:160` — `{{ student_stats_json \| safe }}` sin serialización `tojson`. |
| **Reproducción** | 1. Registrar estudiante con nombre que contenga el carácter `\n`. 2. Acceder a `/reports`.                                     |
| **Esperado**     | Rechazo del carácter de control por el validador, o escapado seguro en la plantilla.                                           |
| **Obtenido**     | `SyntaxError` en JavaScript del navegador; módulo de reportes y gráficas completamente inoperativo.                            |
| **Severidad**    | **P1**                                                                                                                         |

---

### BUG-04 · Ausencia de límite temporal inferior en el registro de asistencia

| Campo            | Detalle                                                                                             |
| :--------------- | :-------------------------------------------------------------------------------------------------- |
| **Caso**         | TC-006                                                                                              |
| **Tipo**         | AVL Fallido / Lógica de Negocio                                                                     |
| **Evidencia**    | `app.py:151` — `validate_date_not_future()` solo verifica `date <= today`; no define umbral mínimo. |
| **Reproducción** | Enviar POST a `/attendance` con `attendance_date=0001-01-01`.                                       |
| **Esperado**     | Rechazo — fecha fuera del rango operativo razonable del sistema.                                    |
| **Obtenido**     | Asistencia registrada y persistida en base de datos.                                                |
| **Severidad**    | **P3**                                                                                              |

---

### BUG-05 · Campo Carrera no validado contra catálogo en capa backend

| Campo            | Detalle                                                                                                  |
| :--------------- | :------------------------------------------------------------------------------------------------------- |
| **Caso**         | TC-009                                                                                                   |
| **Tipo**         | Restricción de Dominio Incumplida                                                                        |
| **Evidencia**    | `app.py:358` — invoca `validate_name()`, que solo valida formato y longitud, no pertenencia al catálogo. |
| **Reproducción** | Manipular el DOM (F12) para modificar el `<option>` del campo carrera. Enviar formulario.                |
| **Esperado**     | HTTP 400 — valor no pertenece al catálogo institucional de carreras.                                     |
| **Obtenido**     | HTTP 302 — registro persistido con carrera arbitraria.                                                   |
| **Severidad**    | **P3**                                                                                                   |

---

### BUG-06 · Ausencia de protección CSRF en rutas destructivas

| Campo            | Detalle                                                                                              |
| :--------------- | :--------------------------------------------------------------------------------------------------- |
| **Caso**         | TC-010                                                                                               |
| **Tipo**         | Vulnerabilidad de Seguridad                                                                          |
| **Evidencia**    | Formularios en `students.html` y rutas POST equivalentes carecen de `{{ csrf_token() }}`.            |
| **Reproducción** | Desde un origen externo, enviar POST a `http://[host]/students/delete/1` con sesión de admin activa. |
| **Esperado**     | HTTP 403 Forbidden — token CSRF ausente o inválido.                                                  |
| **Obtenido**     | HTTP 302 — estudiante eliminado irreversiblemente; asistencias eliminadas en cascada.                |
| **Severidad**    | **P1**                                                                                               |

---

### BUG-07 · Excepción no controlada en endpoint API ante payload nulo

| Campo            | Detalle                                                                              |
| :--------------- | :----------------------------------------------------------------------------------- |
| **Caso**         | TC-011                                                                               |
| **Tipo**         | Excepción no controlada / Degradación de Servicio                                    |
| **Evidencia**    | `app.py:725` — `request.get_json()` sin parámetro `silent=True`.                     |
| **Reproducción** | POST a `/api/check-availability` con `Content-Type: application/json` y body `null`. |
| **Esperado**     | HTTP 400 — respuesta JSON con descripción del error.                                 |
| **Obtenido**     | HTTP 500 — `AttributeError: 'NoneType' object has no attribute 'get'`.               |
| **Severidad**    | **P2**                                                                               |

---

### BUG-08 · Inconsistencia de longitud máxima entre interfaz HTML y backend

| Campo            | Detalle                                                                                                |
| :--------------- | :----------------------------------------------------------------------------------------------------- |
| **Caso**         | TC-012                                                                                                 |
| **Tipo**         | Inconsistencia Interfaz / Restricción de Negocio                                                       |
| **Evidencia**    | `students.html` — `maxlength="30"` (hardcodeado). `app.py:41` — `MAX_FIRST_NAME_LENGTH = 50`.          |
| **Reproducción** | Intentar ingresar un nombre de 35 caracteres mediante el formulario estándar del navegador.            |
| **Esperado**     | Guardado exitoso — el backend permite hasta 50 caracteres.                                             |
| **Obtenido**     | El formulario HTML bloquea la entrada a 30 caracteres, impidiendo el uso de nombres completos válidos. |
| **Severidad**    | **P3**                                                                                                 |

---

## 6. HALLAZGOS DE SEGURIDAD

### 6.1 Cross-Site Request Forgery (CSRF) — BUG-06 · Severidad P1

La totalidad de las rutas POST del sistema (`/students/add`, `/students/edit/<id>`, `/students/delete/<id>`, `/attendance`) carecen de mecanismo de verificación de origen. Esto permite que un tercero malintencionado construya formularios en sitios externos que ejecuten operaciones destructivas aprovechando la sesión activa del administrador. El impacto más crítico es la eliminación en cascada de registros de estudiantes y asistencia, operación irreversible sin respaldo.

### 6.2 Excepción no Controlada en API AJAX — BUG-07 · Severidad P2

El endpoint `/api/check-availability` no implementa validación defensiva del payload recibido. Una petición con body nulo provoca una excepción Python no capturada (`AttributeError`) que retorna HTTP 500, expone información interna del servidor y representa un vector potencial de Denegación de Servicio (DoS) por saturación de excepciones.

---

## 7. HALLAZGOS DE CALIDAD DE DATOS

| Defecto                             | TC Asociado | Impacto sobre los datos                                                                      |
| :---------------------------------- | :---------- | :------------------------------------------------------------------------------------------- |
| Dígitos Unicode en campos de ID     | TC-002      | IDs no normalizados; exportaciones y reportes producen caracteres ilegibles.                 |
| Nombres sin contenido alfabético    | TC-003      | Registros semánticamente inválidos; búsquedas por nombre retornan ruido.                     |
| Caracteres de control en texto      | TC-004      | Corrupción del renderizado JavaScript de reportes; pérdida de la funcionalidad gráfica.      |
| Carreras sin validación de catálogo | TC-009      | Fragmentación estadística por escuela; agrupaciones incoherentes en reportes.                |
| Asimetría de límites UI / API       | TC-012      | Datos válidos según el backend son rechazados por la UI, bloqueando el uso real del sistema. |

---

## 8. ANÁLISIS DE RIESGOS

| Riesgo                                        | Probabilidad | Impacto | Nivel     |
| :-------------------------------------------- | :----------- | :------ | :-------- |
| Eliminación masiva de datos por CSRF          | Media        | Crítico | **ALTO**  |
| Corrupción de reportes por inyección `\n`     | Baja         | Alto    | **ALTO**  |
| Degradación de servicio por crasheo de API    | Media        | Medio   | **MEDIO** |
| Corrupción de BD por Unicode en IDs           | Baja         | Medio   | **MEDIO** |
| Inconsistencia de datos categóricos           | Alta         | Bajo    | **MEDIO** |
| Asistencia con fechas históricamente absurdas | Baja         | Bajo    | **BAJO**  |

---

## 9. RECOMENDACIONES TÉCNICAS

**Alta prioridad — Implementación inmediata:**

1. **Protección CSRF global:** Integrar `Flask-WTF` con `CSRFProtect(app)` y añadir `{{ form.hidden_tag() }}` en todos los formularios POST. Esfuerzo estimado: bajo.

2. **Validación estricta de IDs numéricos:** Reemplazar `code.isdigit()` por `re.fullmatch(r'[0-9]{6,12}', code)` para garantizar exclusividad de caracteres ASCII. Esfuerzo: mínimo.

3. **Manejo defensivo de payloads en API:** Sustituir `request.get_json()` por `request.get_json(silent=True)` con validación de tipo antes de operar sobre el resultado. Esfuerzo: mínimo.

**Prioridad media:**

4. **Serialización segura en plantillas:** Sustituir `{{ variable | safe }}` por `{{ variable | tojson | safe }}` en todos los bloques `<script>` de `reports.html`.

5. **Sincronización de límites UI/Backend:** Inyectar constantes de Python en las plantillas Jinja: `<input maxlength="{{ MAX_FIRST_NAME_LENGTH }}">`, eliminando valores hardcodeados en HTML.

6. **Validación de Enum para carreras:** Definir `VALID_CAREERS = [...]` en `app.py` y validar `career in VALID_CAREERS` antes de persistir, con el mismo patrón de `validate_status()`.

**Prioridad baja:**

7. **Refinamiento del Regex de nombres:** Modificar el patrón para exigir al menos una letra: `^(?=[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ])[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ \-]+$`, excluyendo `\n`, `\r` y `\t`.

8. **Límite temporal inferior en fechas:** Añadir `date >= datetime.date(2000, 1, 1)` como condición mínima adicional en `validate_date_not_future()`.

---

## 10. CONCLUSIONES

1. La suite de automatización del equipo rival cubre adecuadamente los **flujos nominales** del sistema, incluyendo validaciones de formato, control de duplicados y protección de rutas por sesión.

2. La **cobertura de pruebas negativas es insuficiente**: el equipo no evaluó manipulación deliberada de peticiones HTTP, inyección de caracteres de control ni comportamiento de la API ante payloads anómalos.

3. Existen **dos vulnerabilidades de severidad P1** que descalifican el sistema para producción: la ausencia de protección CSRF y la corrupción del módulo de reportes por inyección de caracteres de control en campos de texto libre.

4. Los **defectos de calidad de datos** representan un riesgo silencioso que se manifestará progresivamente en la degradación de la integridad de la base de datos y en la incoherencia de los reportes estadísticos.

5. La **asimetría UI/Backend** evidencia falta de sincronización entre capas de desarrollo y afecta directamente la experiencia operativa del administrador del sistema.

**Conclusión final:** AsistPro es un sistema funcionalmente completo para el escenario académico propuesto, pero requiere correcciones críticas de seguridad y calidad de datos antes de ser considerado apto para cualquier despliegue institucional real.

---

## APÉNDICE A — Tabla de Severidad Total

| Severidad            | Descripción                                              | Cantidad | Casos Asociados                |
| :------------------- | :------------------------------------------------------- | :------- | :----------------------------- |
| **P1 — Crítico**     | Riesgo de pérdida de datos o caída de módulo principal   | 2        | TC-004, TC-010                 |
| **P2 — Alto**        | Defecto funcional reproducible con impacto significativo | 2        | TC-002, TC-011                 |
| **P3 — Medio**       | Defecto lógico o de calidad que degrada el sistema       | 4        | TC-003, TC-006, TC-009, TC-012 |
| **P4 — Bajo**        | Observación menor sin impacto funcional inmediato        | 0        | —                              |
| **Total confirmado** |                                                          | **8**    |                                |

---

## APÉNDICE B — Resumen de Cobertura de Pruebas Ejecutadas

| Técnica                          | Casos Ejecutados | PASS  | FAIL / EXCEPTION | Tasa de Defectos |
| :------------------------------- | :--------------- | :---- | :--------------- | :--------------- |
| Partición de Equivalencia (PE)   | 5                | 2     | 3                | 60%              |
| Análisis de Valores Límite (AVL) | 3                | 2     | 1                | 33%              |
| Pruebas Negativas / Integración  | 5                | 1     | 4                | 80%              |
| **Total**                        | **13**           | **5** | **8**            | **62%**          |

> La tasa de defectos del **62%** en los casos diseñados para cubrir brechas de cobertura confirma que las zonas no evaluadas por el equipo rival concentran la mayor densidad de errores del sistema evaluado.

---
