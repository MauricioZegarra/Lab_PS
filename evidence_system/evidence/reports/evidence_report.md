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

# Reporte de Evidencia QA — AsistPro

**Total de casos ejecutados:** 13
**PASS:** 5 | **FAIL:** 6 | **EXCEPTION:** 2
**Tasa de defectos:** 61.5%

---

## Resumen Ejecutivo

Se ejecutaron 13 casos de prueba derivados de la auditoría de cobertura PE/AVL. De estos, 8 resultaron en defectos confirmados (FAIL o EXCEPTION), arrojando una tasa de detección del 61.5%.

## Matriz de Bugs Confirmados

| BUG ID | TC     | Severidad | Estado    |
| :----- | :----- | :-------- | :-------- |
| BUG-01 | TC-002 | P2        | FAIL      |
| BUG-02 | TC-003 | P3        | FAIL      |
| BUG-03 | TC-004 | P1        | EXCEPTION |
| BUG-04 | TC-006 | P3        | FAIL      |
| BUG-05 | TC-009 | P3        | FAIL      |
| BUG-06 | TC-010 | P1        | FAIL      |
| BUG-07 | TC-011 | P2        | EXCEPTION |
| BUG-08 | TC-012 | P3        | FAIL      |

**P1 (Crítico):** 2 | **P2 (Alto):** 2 | **P3 (Medio):** 4

---

## Detalle de Ejecución por Test Case

### TC-001

- **Estado:** PASS
- **Input:** `['user@dom!ain.com', 'user@domain@com.pe']`
- **Esperado:** Rechazo — formato RFC inválido
- **Obtenido:** Rechazado correctamente por el regex
- **Análisis:** El regex del backend descarta correctamente caracteres ! y doble @.
- **Log:** `logs/TC-001.log`
- **Response:** `responses/TC-001.json`

### TC-002

- **Estado:** FAIL
- **Input:** `student_code="٢٠٢١٠٠١٢" (dígitos árabes Unicode)`
- **Esperado:** Rechazo — solo dígitos ASCII [0-9] válidos
- **Obtenido:** Aceptado por .isdigit() — bypass Unicode confirmado
- **Bug asociado:** BUG-01 (P2)
- **Análisis:** Python .isdigit() retorna True para caracteres Unicode categoría Nd, incluyendo dígitos árabes, hindúes, etc. Esto permite corromper IDs.

  Básicamente, el sistema intenta verificar que el código de estudiante tenga solo números usando una función muy básica (`.isdigit()`). Sin embargo, un atacante puede usar "números" de otros idiomas (como el árabe o caracteres especiales) y el sistema los dejará pasar como si fueran números normales, lo que podría corromper la base de datos o causar errores en otros módulos.

- **Log:** `logs/TC-002.log`
- **Response:** `responses/TC-002.json`

### TC-003

- **Estado:** FAIL
- **Input:** `first_name="---" (solo guiones, sin letras)`
- **Esperado:** Rechazo — un nombre debe contener al menos una letra
- **Obtenido:** Aceptado como nombre válido — falta requisito de letras
- **Bug asociado:** BUG-02 (P3)
- **Análisis:** El regex ^[a-zA-Z...\s\-]+$ acepta combinaciones exclusivas de sus modificadores, permitiendo nombres sin contenido alfabético.
  **Detalle del impacto:** La regla de validación que crearon para los nombres permite letras, espacios y guiones, pero _olvidaron obligar a que haya al menos una letra_. Esto significa que un usuario puede registrarse llamándose "---" o " ", lo cual es un error lógico de negocio evidente.
- **Log:** `logs/TC-003.log`
- **Response:** `responses/TC-003.json`

### TC-004

- **Estado:** EXCEPTION
- **Input:** `first_name="Juan\nPerez" (salto de línea inyectado)`
- **Esperado:** Rechazo — carácter de control inválido en nombre
- **Obtenido:** Aceptado — \s en regex incluye \n, produce SyntaxError en reports.html
- **Bug asociado:** BUG-03 (P1)
- **Análisis:** \s en regex incluye \n. El dato persiste y al renderizarse en reports.html con {{ student_stats_json | safe }}, se produce SyntaxError en JavaScript que destruye el módulo completo de reportes.
  **Detalle del impacto:** El formulario permite que un usuario presione la tecla "Enter" (salto de línea) dentro de su propio nombre. Cuando ese nombre con "Enter" se guarda y luego el administrador intenta ver la pantalla de Reportes, ese "Enter" escondido rompe por completo el código interno (JavaScript) de esa pantalla, dejándola en blanco para todos. Es un tipo de ataque de inyección.
- **Log:** `logs/TC-004.log`
- **Response:** `responses/TC-004.json`

### TC-005

- **Estado:** PASS
- **Input:** `date="25-05-2024" (formato DD-MM-YYYY)`
- **Esperado:** Rechazo o redirección segura a fecha actual
- **Obtenido:** HTTP 200 — redirección segura ejecutada
- **Análisis:** El bloque try/except en app.py:498 captura el ValueError y redirige a la fecha actual sin crashear.
- **Log:** `logs/TC-005.log`
- **Response:** `responses/TC-005.json`

### TC-006

- **Estado:** FAIL
- **Input:** `attendance_date="0001-01-01" (límite inferior absoluto)`
- **Esperado:** Rechazo — fecha fuera de rango operativo razonable
- **Obtenido:** Aceptado — no existe límite temporal inferior
- **Bug asociado:** BUG-04 (P3)
- **Análisis:** validate_date_not_future() solo verifica date <= today. No existe umbral mínimo, permitiendo fechas históricamente absurdas.
  **Detalle del impacto:** El sistema verifica correctamente que no puedas registrar asistencias en el futuro (ej. mañana), pero olvidaron ponerle un límite hacia el pasado. Esto permite registrar asistencias, por ejemplo, en el año 0001, lo cual pierde todo sentido lógico para un sistema universitario.
- **Log:** `logs/TC-006.log`
- **Response:** `responses/TC-006.json`

### TC-007

- **Estado:** PASS
- **Input:** `4 intentos fallidos consecutivos de login`
- **Esperado:** Cuenta NO bloqueada — el lockout debe activarse al 5.° intento
- **Obtenido:** Cuenta habilitada tras 4 intentos fallidos — comportamiento correcto
- **Análisis:** El sistema bloquea la cuenta en el 5.° intento fallido consecutivo. En el 4.°, la cuenta permanece habilitada, cumpliendo la frontera AVL.
- **Log:** `logs/TC-007.log`
- **Response:** `responses/TC-007.json`

### TC-008

- **Estado:** PASS
- **Input:** `page=999999999 en GET /reports`
- **Esperado:** HTTP 200 — tabla vacía, sin crasheo por offset SQL
- **Obtenido:** HTTP 200 — tabla vacía sin error de servidor
- **Análisis:** SQLAlchemy resuelve el offset fuera de rango retornando una lista vacía. La interfaz renderiza la tabla correctamente sin excepciones.
- **Log:** `logs/TC-008.log`
- **Response:** `responses/TC-008.json`

### TC-009

- **Estado:** FAIL
- **Input:** `career="Ingeniería de Hacking" vía manipulación DOM/POST`
- **Esperado:** Rechazo — valor fuera del catálogo institucional de carreras
- **Obtenido:** Estudiante creado con career="Ingeniería de Hacking" — backend no valida enum
- **Bug asociado:** BUG-05 (P3)
- **Análisis:** El backend usa validate_name() para carreras, que solo verifica formato de texto y longitud. No existe validación de pertenencia a un catálogo (Enum) definido.
  **Detalle del impacto:** Aunque en la pantalla visualmente solo hay una lista desplegable con las carreras válidas, un usuario con conocimientos básicos puede manipular la petición enviada al servidor por detrás y registrarse en una carrera inventada como "Ingeniería de Hacking". El servidor confía ciegamente en lo que le envían y lo guarda.
- **Log:** `logs/TC-009.log`
- **Response:** `responses/TC-009.json`

### TC-010

- **Estado:** FAIL
- **Input:** `POST /students/delete/1 sin token CSRF`
- **Esperado:** HTTP 403 Forbidden — token CSRF ausente o inválido
- **Obtenido:** Estudiante eliminado exitosamente sin token CSRF — vulnerabilidad confirmada
- **Bug asociado:** BUG-06 (P1)
- **Análisis:** Los formularios POST del sistema carecen completamente de protección CSRF (no usan Flask-WTF ni csrf_token()). Cualquier sitio externo puede ejecutar operaciones destructivas aprovechando la sesión activa.
  **Detalle del impacto:** El sistema no tiene protección contra falsificación de peticiones (CSRF). Esto significa que si el profesor o administrador inicia sesión y, sin querer, visita una página web maliciosa en otra pestaña, esa página externa podría enviar comandos "invisibles" para borrar estudiantes del sistema AsistPro sin que el administrador se dé cuenta.
- **Log:** `logs/TC-010.log`
- **Response:** `responses/TC-010.json`

### TC-011

- **Estado:** EXCEPTION
- **Input:** `POST /api/check-availability con body vacío (Content-Type: application/json)`
- **Esperado:** HTTP 400 — respuesta JSON con descripción del error
- **Obtenido:** Excepción no controlada: AttributeError: 'NoneType' object has no attribute 'get'
- **Bug asociado:** BUG-07 (P2)
- **Análisis:** request.get_json() sin silent=True lanza excepción cuando el body es nulo. Al intentar .get("field") sobre NoneType, se produce AttributeError que resulta en HTTP 500.
  **Detalle del impacto:** Encontramos una forma de "tumbar" o "crashear" el servidor enviándole una petición vacía (sin datos) a uno de sus servicios internos (API). El sistema no sabe cómo manejar ese vacío, entra en pánico y lanza un error interno general (Error 500). Un atacante podría usar esto repetidamente para hacer un ataque y botar el sistema.
- **Log:** `logs/TC-011.log`
- **Response:** `responses/TC-011.json`

### TC-012

- **Estado:** FAIL
- **Input:** `first_name="A"*50 (50 chars)`
- **Esperado:** Guardado exitoso — el límite backend es 50
- **Obtenido:** Backend acepta 50 chars por POST directo, pero el HTML usa maxlength restrictivo que bloquea al usuario
- **Bug asociado:** BUG-08 (P3)
- **Análisis:** El formulario HTML restringe el campo con maxlength inferior al valor real aceptado por el backend, impidiendo a usuarios legítimos registrar nombres completos.
  **Detalle del impacto:** Hay una falta de comunicación entre el diseño visual y la base de datos. La base de datos puede guardar nombres largos sin problema, pero la cajita de texto en la pantalla está bloqueada para dejar escribir muy poco. Esto frustrará a estudiantes reales que tengan nombres largos, ya que la pantalla no les dejará escribirlos completos a pesar de que el sistema sí podría soportarlo.
- **Log:** `logs/TC-012.log`
- **Response:** `responses/TC-012.json`

### TC-013

- **Estado:** PASS
- **Input:** `POST /students/edit/2 con student_code="20210001" (de otro estudiante)`
- **Esperado:** Error de colisión — actualización rechazada
- **Obtenido:** Colisión prevenida — el ORM detectó duplicado
- **Análisis:** El sistema verifica Student.id != id antes de aceptar el código, previniendo colisiones en la edición.
- **Log:** `logs/TC-013.log`
- **Response:** `responses/TC-013.json`

---

## Tabla Consolidada

| TC     | Tipo        | Estado    | Hallazgo | Severidad |
| :----- | :---------- | :-------- | :------- | :-------- |
| TC-001 | PE          | PASS      | Ninguno  | N/A       |
| TC-002 | PE          | FAIL      | BUG-01   | P2        |
| TC-003 | PE          | FAIL      | BUG-02   | P3        |
| TC-004 | PE          | EXCEPTION | BUG-03   | P1        |
| TC-005 | PE          | PASS      | Ninguno  | N/A       |
| TC-006 | AVL         | FAIL      | BUG-04   | P3        |
| TC-007 | AVL         | PASS      | Ninguno  | N/A       |
| TC-008 | AVL         | PASS      | Ninguno  | N/A       |
| TC-009 | Negativa    | FAIL      | BUG-05   | P3        |
| TC-010 | Negativa    | FAIL      | BUG-06   | P1        |
| TC-011 | Error       | EXCEPTION | BUG-07   | P2        |
| TC-012 | Restricción | FAIL      | BUG-08   | P3        |
| TC-013 | Negocio     | PASS      | Ninguno  | N/A       |

---
