# -*- coding: utf-8 -*-
"""
AsistPro - Sistema de Registro y Control de Asistencia
Archivo Principal del Servidor Flask — VERSIÓN MEJORADA Y REFORZADA
"""

import os
import re
import datetime
import random
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify

# Inicialización de la aplicación Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'asistpro_secret_key_univ_2026')

# Configuración de SQLite en la raíz del proyecto
db_path = os.path.join(app.root_path, 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ==========================================
# [MEJORA #1] CONFIGURACIÓN DE SESIÓN SEGURA
# Se define expiración de sesión para evitar sesiones eternas
# ==========================================
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=8)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# ==========================================
# CONSTANTES DE VALIDACIÓN
# [MEJORA #2] Centralizar los límites de validación evita inconsistencias
# ==========================================
MAX_FIRST_NAME_LENGTH = 50
MAX_LAST_NAME_LENGTH = 75
MAX_NAME_LENGTH = 50
MAX_EMAIL_LENGTH = 120
MIN_CODE_LENGTH = 8
MAX_CODE_LENGTH = 8
MAX_CAREER_LENGTH = 100

# Statuses válidos para no permitir valores arbitrarios
VALID_STATUSES = {'Presente', 'Tardanza', 'Falta'}

# ==========================================
# MODELOS DE BASE DE DATOS (SQLAlchemy)
# ==========================================

class User(db.Model):
    """Modelo para los usuarios del sistema (Administrador)"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='admin')
    # [MEJORA #3] Campo para bloqueo por intentos fallidos
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_locked(self):
        """Verifica si la cuenta está temporalmente bloqueada"""
        if self.locked_until and datetime.datetime.utcnow() < self.locked_until:
            return True
        return False

class Student(db.Model):
    """Modelo para gestionar los datos de los estudiantes"""
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_code = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    career = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relación de cascada: si se elimina un estudiante, se borra su asistencia
    attendances = db.relationship('Attendance', backref='student', cascade='all, delete-orphan', lazy=True)

    @property
    def full_name(self):
        return f"{self.last_name}, {self.first_name}"

class Attendance(db.Model):
    """Modelo para el registro de asistencia diaria"""
    __tablename__ = 'attendances'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'Presente', 'Tardanza', 'Falta'

    # Restricción única: Un estudiante solo puede tener un registro de asistencia por día
    __table_args__ = (
        db.UniqueConstraint('student_id', 'date', name='uq_student_attendance_date'),
    )

# ==========================================
# FUNCIONES DE VALIDACIÓN
# [MEJORA #4] Validaciones robustas y centralizadas
# ==========================================

def validate_email(email: str) -> bool:
    """
    Valida que el email tenga un formato correcto usando regex robusto y restricciones estrictas.
    """
    if not email or len(email) > MAX_EMAIL_LENGTH:
        return False
    # No permitir espacios en blanco ni puntos consecutivos en la dirección
    if ' ' in email or '..' in email:
        return False
    # Patrón robusto para correo electrónico estándar RFC 5322 simplificado
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,6}$'
    return bool(re.match(pattern, email))

def validate_student_code(code: str) -> bool:
    """
    Valida que el código de estudiante tenga exactamente 8 caracteres numéricos.
    """
    if not code:
        return False
    return len(code) == 8 and code.isdigit()

def validate_name(name: str, max_length: int = MAX_NAME_LENGTH) -> bool:
    """
    Valida que los nombres y apellidos no excedan longitudes máximas y no contengan números o caracteres especiales peligrosos.
    """
    if not name or len(name.strip()) == 0:
        return False
    if len(name) > max_length:
        return False
    # Permitir únicamente letras, acentos, Ñ, espacios y guiones simples para evitar inyecciones e incoherencias
    pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$'
    return bool(re.match(pattern, name))

def validate_date_not_future(date: datetime.date) -> bool:
    """
    Verifica que la fecha no sea futura.
    FIX CRÍTICO: El sistema original permitía registrar asistencia en fechas futuras,
    lo que es una vulnerabilidad de integridad de datos muy grave.
    """
    return date <= datetime.date.today()

def validate_status(status: str) -> bool:
    """
    Verifica que el estado de asistencia sea uno de los valores permitidos.
    FIX: El sistema original no validaba el valor del status en absoluto.
    Un atacante podría insertar valores arbitrarios en la BD como status='HACKED'.
    """
    return status in VALID_STATUSES

# ==========================================
# DECORADORES DE SEGURIDAD
# ==========================================

def login_required(f):
    """Decorador para proteger rutas que requieren inicio de sesión"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Acceso restringido. Por favor inicie sesión.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# FILTROS JINJA PERSONALIZADOS
# ==========================================

@app.template_filter('datetime_format')
def datetime_format(value, format='%d/%m/%Y'):
    if value is None:
        return ""
    if isinstance(value, datetime.date):
        return value.strftime(format)
    return value

# ==========================================
# RUTAS DE AUTENTICACIÓN
# ==========================================

@app.route('/')
def index():
    """Redirección inicial al login o dashboard según la sesión"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ruta para el inicio de sesión.
    [MEJORA #5] Se agrega bloqueo por intentos fallidos para prevenir ataques de fuerza bruta.
    FIX: El sistema original no tenía ninguna protección contra fuerza bruta.
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Validaciones de formulario
        if not username or not password:
            flash('Por favor, ingrese todos los campos.', 'danger')
            return render_template('login.html')

        # No permitir espacios en usuario ni contraseña
        if ' ' in username or ' ' in password:
            flash('El usuario y la contraseña no deben contener espacios.', 'danger')
            return render_template('login.html')

        # Validar longitud máxima
        if len(username) > 50 or len(password) > 256:
            flash('Usuario o contraseña incorrectos.', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()

        # Verificar si la cuenta está bloqueada
        if user and user.is_locked():
            remaining = (user.locked_until - datetime.datetime.utcnow()).seconds // 60
            flash(f'Cuenta bloqueada temporalmente. Intente nuevamente en {remaining + 1} minutos.', 'danger')
            return render_template('login.html')

        # Verificar credenciales
        if user and user.check_password(password):
            # Resetear contador de intentos fallidos al éxito
            user.failed_attempts = 0
            user.locked_until = None
            db.session.commit()

            session.permanent = True
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'¡Bienvenido de nuevo, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Incrementar intentos fallidos
            if user:
                user.failed_attempts = (user.failed_attempts or 0) + 1
                # Bloquear después de 5 intentos fallidos durante 15 minutos
                if user.failed_attempts >= 5:
                    user.locked_until = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
                    user.failed_attempts = 0
                    db.session.commit()
                    flash('Demasiados intentos fallidos. Cuenta bloqueada por 15 minutos.', 'danger')
                    return render_template('login.html')
                db.session.commit()
            # Mensaje genérico para no revelar si el usuario existe
            flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Ruta para cerrar sesión"""
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('login'))

# ==========================================
# RUTAS DEL DASHBOARD Y GESTIÓN
# ==========================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal con estadísticas generales"""
    total_students = Student.query.count()
    today = datetime.date.today()

    # Asistencia de hoy
    today_attendances = Attendance.query.filter_by(date=today).all()
    today_registered = len(today_attendances)

    present_today = sum(1 for a in today_attendances if a.status == 'Presente')
    tardy_today = sum(1 for a in today_attendances if a.status == 'Tardanza')
    absent_today = sum(1 for a in today_attendances if a.status == 'Falta')

    # Calcular porcentaje general histórico
    all_attendances = Attendance.query.all()
    total_records = len(all_attendances)

    if total_students > 0 and total_records > 0:
        p_count = sum(1 for a in all_attendances if a.status == 'Presente')
        t_count = sum(1 for a in all_attendances if a.status == 'Tardanza')
        global_attendance_rate = round(((p_count + t_count * 0.5) / total_records) * 100, 2)
    else:
        global_attendance_rate = "-"

    # Obtener últimos estudiantes agregados
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        total_students=total_students,
        today=today,
        today_registered=today_registered,
        present_today=present_today,
        tardy_today=tardy_today,
        absent_today=absent_today,
        global_attendance_rate=global_attendance_rate,
        recent_students=recent_students
    )

@app.route('/students')
@login_required
def students():
    """Listado de estudiantes y carga de vista CRUD"""
    all_students = Student.query.order_by(Student.last_name.asc(), Student.first_name.asc()).all()
    return render_template('students.html', students=all_students)

@app.route('/students/add', methods=['POST'])
@login_required
def add_student():
    """
    Registrar un nuevo estudiante.
    [MEJORAS #4, #6, #7] Validaciones completas de todos los campos.
    """
    student_code = request.form.get('student_code', '').strip()
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    career = request.form.get('career', '').strip()
    email = request.form.get('email', '').strip().lower()

    # === VALIDACIONES REFORZADAS ===

    # Campos obligatorios
    if not (student_code and first_name and last_name and career and email):
        flash('Todos los campos son obligatorios.', 'danger')
        return redirect(url_for('students'))

    # [MEJORA #6] Validar formato del código de estudiante
    if not validate_student_code(student_code):
        flash('El código universitario debe contener exactamente 8 dígitos.', 'danger')
        return redirect(url_for('students'))

    # [MEJORA #7] Validar longitud y caracteres del nombre
    if not validate_name(first_name, MAX_FIRST_NAME_LENGTH):
        flash(f'El nombre es inválido o excede los {MAX_FIRST_NAME_LENGTH} caracteres (solo letras, espacios y guiones permitidos).', 'danger')
        return redirect(url_for('students'))

    if not validate_name(last_name, MAX_LAST_NAME_LENGTH):
        flash(f'El apellido es inválido o excede los {MAX_LAST_NAME_LENGTH} caracteres (solo letras, espacios y guiones permitidos).', 'danger')
        return redirect(url_for('students'))

    if not validate_name(career, MAX_CAREER_LENGTH):
        flash(f'La carrera es inválida o excede los {MAX_CAREER_LENGTH} caracteres.', 'danger')
        return redirect(url_for('students'))

    # [MEJORA #4] Validar formato de email
    if not validate_email(email):
        flash('El correo electrónico no es válido o contiene caracteres extraños (ej: usuario@dominio.com).', 'danger')
        return redirect(url_for('students'))

    # Verificar si el código ya existe
    existing_code = Student.query.filter_by(student_code=student_code).first()
    if existing_code:
        flash(f'El código universitario "{student_code}" ya está registrado.', 'danger')
        return redirect(url_for('students'))

    # Verificar si el correo ya existe
    existing_email = Student.query.filter_by(email=email).first()
    if existing_email:
        flash(f'El correo electrónico "{email}" ya está registrado.', 'danger')
        return redirect(url_for('students'))

    try:
        new_student = Student(
            student_code=student_code,
            first_name=first_name,
            last_name=last_name,
            career=career,
            email=email
        )
        db.session.add(new_student)
        db.session.commit()
        flash(f'Estudiante {new_student.full_name} registrado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error al registrar estudiante: {str(e)}')
        flash('Ocurrió un error al registrar el estudiante. Intente de nuevo.', 'danger')

    return redirect(url_for('students'))

@app.route('/students/edit/<int:id>', methods=['POST'])
@login_required
def edit_student(id):
    """
    Editar un estudiante existente.
    [MEJORAS #4, #6, #7] Mismas validaciones que en add_student.
    """
    student = Student.query.get_or_404(id)

    student_code = request.form.get('student_code', '').strip()
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    career = request.form.get('career', '').strip()
    email = request.form.get('email', '').strip().lower()

    # === VALIDACIONES REFORZADAS ===
    if not (student_code and first_name and last_name and career and email):
        flash('Todos los campos son obligatorios.', 'danger')
        return redirect(url_for('students'))

    if not validate_student_code(student_code):
        flash('El código universitario debe contener exactamente 8 dígitos.', 'danger')
        return redirect(url_for('students'))

    if not validate_name(first_name, MAX_FIRST_NAME_LENGTH):
        flash(f'El nombre es inválido o excede los {MAX_FIRST_NAME_LENGTH} caracteres (solo letras, espacios y guiones permitidos).', 'danger')
        return redirect(url_for('students'))

    if not validate_name(last_name, MAX_LAST_NAME_LENGTH):
        flash(f'El apellido es inválido o excede los {MAX_LAST_NAME_LENGTH} caracteres (solo letras, espacios y guiones permitidos).', 'danger')
        return redirect(url_for('students'))

    if not validate_name(career, MAX_CAREER_LENGTH):
        flash(f'La carrera es inválida o excede los {MAX_CAREER_LENGTH} caracteres.', 'danger')
        return redirect(url_for('students'))

    if not validate_email(email):
        flash('El correo electrónico no es válido o contiene caracteres extraños (ej: usuario@dominio.com).', 'danger')
        return redirect(url_for('students'))

    # Verificar duplicado de código (excluyendo el actual)
    dup_code = Student.query.filter(Student.student_code == student_code, Student.id != id).first()
    if dup_code:
        flash(f'El código universitario "{student_code}" ya pertenece a otro estudiante.', 'danger')
        return redirect(url_for('students'))

    # Verificar duplicado de correo (excluyendo el actual)
    dup_email = Student.query.filter(Student.email == email, Student.id != id).first()
    if dup_email:
        flash(f'El correo "{email}" ya pertenece a otro estudiante.', 'danger')
        return redirect(url_for('students'))

    try:
        student.student_code = student_code
        student.first_name = first_name
        student.last_name = last_name
        student.career = career
        student.email = email

        db.session.commit()
        flash(f'Datos del estudiante {student.full_name} actualizados correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error al actualizar estudiante id={id}: {str(e)}')
        flash('Ocurrió un error al actualizar el estudiante. Intente de nuevo.', 'danger')

    return redirect(url_for('students'))

@app.route('/students/delete/<int:id>', methods=['POST'])
@login_required
def delete_student(id):
    """Eliminar un estudiante y su historial de asistencia"""
    student = Student.query.get_or_404(id)
    try:
        name = student.full_name
        db.session.delete(student)
        db.session.commit()
        flash(f'Estudiante {name} eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error al eliminar estudiante id={id}: {str(e)}')
        flash('Ocurrió un error al eliminar el estudiante. Intente de nuevo.', 'danger')

    return redirect(url_for('students'))

# ==========================================
# RUTAS DE REGISTRO DE ASISTENCIA
# ==========================================

@app.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    """
    Visualización y registro de asistencia diaria.
    [MEJORA #8] CRÍTICO: Se bloquea el registro de asistencia en fechas futuras.
    [MEJORA #9] Se valida que el estado sea un valor permitido.
    [MEJORA #10] Se valida que el student_id recibido exista realmente en BD.
    """
    # Determinar la fecha seleccionada (por defecto hoy)
    date_str = request.args.get('date') or request.form.get('attendance_date')

    if date_str:
        try:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de fecha inválido.', 'danger')
            selected_date = datetime.date.today()
    else:
        selected_date = datetime.date.today()

    # [MEJORA #8] BLOQUEAR FECHAS FUTURAS — vulnerabilidad crítica del sistema original
    if not validate_date_not_future(selected_date):
        flash('No se puede registrar asistencia para fechas futuras.', 'danger')
        selected_date = datetime.date.today()
        # En POST, redirigir de vuelta en lugar de procesar
        if request.method == 'POST':
            return redirect(url_for('attendance', date=selected_date.isoformat()))

    if request.method == 'POST':
        all_students = Student.query.all()
        saved_count = 0

        try:
            for student in all_students:
                status = request.form.get(f'status_{student.id}')

                # [MEJORA #9] Validar que el status sea un valor permitido
                if not status or not validate_status(status):
                    # Si no se selecciona nada válido, se registra como Falta por defecto
                    status = 'Falta'

                # Buscar si ya existe asistencia para este día
                att_record = Attendance.query.filter_by(student_id=student.id, date=selected_date).first()

                if att_record:
                    att_record.status = status
                else:
                    new_att = Attendance(
                        student_id=student.id,
                        date=selected_date,
                        status=status
                    )
                    db.session.add(new_att)

                saved_count += 1

            db.session.commit()
            flash(f'Asistencia del {selected_date.strftime("%d/%m/%Y")} guardada con éxito ({saved_count} estudiantes).', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error al guardar asistencia: {str(e)}')
            flash('Ocurrió un error al guardar la asistencia. Intente de nuevo.', 'danger')

        return redirect(url_for('attendance', date=selected_date.isoformat()))

    # Para GET:
    all_students = Student.query.order_by(Student.last_name.asc()).all()

    # Obtener asistencias ya guardadas para este día
    existing_records = Attendance.query.filter_by(date=selected_date).all()
    attendance_map = {rec.student_id: rec.status for rec in existing_records}

    return render_template(
        'attendance.html',
        students=all_students,
        selected_date=selected_date,
        attendance_map=attendance_map,
        today=datetime.date.today()  # [MEJORA #8B] Pasar fecha actual al template para deshabilitar fechas futuras en el picker
    )

# ==========================================
# RUTAS DE REPORTES
# ==========================================

@app.route('/reports')
@login_required
def reports():
    """Estadísticas e historial detallado de asistencias."""
    all_students = Student.query.order_by(Student.last_name.asc()).all()
    
    # Convertir estudiantes a formato JSON serializable
    students_serializable = []
    for s in all_students:
        students_serializable.append({
            'id': s.id,
            'student_code': s.student_code,
            'first_name': s.first_name,
            'last_name': s.last_name,
            'career': s.career
        })
    
    student_stats = []

    # 1. Calcular estadísticas individuales desde la BD
    for s in all_students:
        total = Attendance.query.filter_by(student_id=s.id).count()
        present = Attendance.query.filter_by(student_id=s.id, status='Presente').count()
        tardy = Attendance.query.filter_by(student_id=s.id, status='Tardanza').count()
        absent = Attendance.query.filter_by(student_id=s.id, status='Falta').count()

        if total > 0:
            rate = round(((present + tardy * 0.5) / total) * 100, 1)
        else:
            rate = 0.0  # Sin registros → 0%, no inventar 100%

        student_stats.append({
            'student': s,
            'total': total,
            'present': present,
            'tardy': tardy,
            'absent': absent,
            'rate': rate
        })

    # Serializar student_stats para JSON (para el JS del template)
    student_stats_json = []
    for ss in student_stats:
        student_stats_json.append({
            'student_code': ss['student'].student_code,
            'first_name': ss['student'].first_name,
            'last_name': ss['student'].last_name,
            'career': ss['student'].career,
            'total': ss['total'],
            'present': ss['present'],
            'tardy': ss['tardy'],
            'absent': ss['absent'],
            'rate': ss['rate']
        })

    # 2. Historial con filtros
    filter_code = request.args.get('search_code', '').strip()
    filter_date = request.args.get('search_date', '').strip()
    active_tab = request.args.get('tab', 'history')
    
    # Paginación
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1

    PER_PAGE = 50

    # Crear la query base
    query = db.session.query(Attendance).join(Student)
    
    # APLICAR FILTROS
    if filter_code:
        query = query.filter(
            db.or_(
                Student.student_code.ilike(f"%{filter_code}%"),
                Student.first_name.ilike(f"%{filter_code}%"),
                Student.last_name.ilike(f"%{filter_code}%")
            )
        )
    
    if filter_date:
        try:
            parsed_date = datetime.datetime.strptime(filter_date, '%Y-%m-%d').date()
            if parsed_date > datetime.date.today():
                flash('No se pueden consultar reportes para fechas futuras.', 'danger')
                return redirect(url_for('reports'))
            query = query.filter(Attendance.date == parsed_date)
        except ValueError:
            flash('Formato de fecha inválido', 'warning')
    
    # Contar y obtener registros
    total_history_count = query.count()
    history_records = query.order_by(Attendance.date.desc(), Student.last_name.asc())\
                   .offset((page - 1) * PER_PAGE)\
                   .limit(PER_PAGE)\
                   .all()
    
    total_pages = max(1, (total_history_count + PER_PAGE - 1) // PER_PAGE)

    # Serializar historial para JSON
    history_json = []
    for att in history_records:
        history_json.append({
            'date': att.date.isoformat(),
            'student_code': att.student.student_code,
            'first_name': att.student.first_name,
            'last_name': att.student.last_name,
            'career': att.student.career,
            'status': att.status
        })
    
    # 3. Estadísticas generales desde la BD
    total_att_records = Attendance.query.count()
    overall_present = Attendance.query.filter_by(status='Presente').count()
    overall_tardy = Attendance.query.filter_by(status='Tardanza').count()
    overall_absent = Attendance.query.filter_by(status='Falta').count()

    total_students_count = len(all_students)
    if total_students_count > 0 and total_att_records > 0:
        global_avg = round(((overall_present + overall_tardy * 0.5) / total_att_records) * 100, 2)
    else:
        global_avg = "-"

    return render_template(
        'reports.html',
        student_stats=student_stats,
        history=history_records,
        filter_code=filter_code,
        filter_date=filter_date,
        overall_present=overall_present,
        overall_tardy=overall_tardy,
        overall_absent=overall_absent,
        global_avg=global_avg,
        page=page,
        total_pages=total_pages,
        total_history_count=total_history_count,
        per_page=PER_PAGE,
        active_tab=active_tab,
        students_json=students_serializable,
        student_stats_json=student_stats_json,  # ← Estadísticas reales desde BD
        history_json=history_json,               # ← Historial real desde BD
        today=datetime.date.today()
    )

# ==========================================
# [MEJORA #13] RUTA DE API: Verificar disponibilidad de código/email (AJAX)
# Previene revelar si un usuario existe sin estar autenticado.
# ==========================================
@app.route('/api/check-availability', methods=['POST'])
@login_required
def check_availability():
    """API para verificar si un código de estudiante o email ya existe (AJAX)"""
    data = request.get_json()
    field = data.get('field')
    value = data.get('value')
    
    if field == 'student_code':
        exists = Student.query.filter_by(student_code=value).first() is not None
    elif field == 'email':
        # Asumiendo que tienes un modelo User con email
        exists = User.query.filter_by(email=value).first() is not None
    else:
        return jsonify({'error': 'Campo no válido'}), 400
    
    return jsonify({'exists': exists})

@app.route('/api/check-code', methods=['POST'])
@login_required
def check_code():
    """Endpoint para verificar disponibilidad de código en tiempo real (AJAX)"""
    from flask import jsonify
    code = request.form.get('code', '').strip()
    exclude_id = request.form.get('exclude_id', None)

    if not validate_student_code(code):
        return jsonify({'available': False, 'reason': 'Formato inválido'})

    query = Student.query.filter_by(student_code=code)
    if exclude_id:
        try:
            query = query.filter(Student.id != int(exclude_id))
        except (ValueError, TypeError):
            pass

    exists = query.first() is not None
    return jsonify({'available': not exists})

# ==========================================
# MANEJO DE ERRORES COMUNES
# ==========================================

@app.errorhandler(404)
def page_not_found(e):
    """Control de error 404 - Página no encontrada"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Control de error 500 - Error interno del servidor"""
    app.logger.error(f'Error 500: {str(e)}')
    return render_template('500.html'), 500

# ==========================================
# [MEJORA #14] MANEJO DE ERROR 405 (Method Not Allowed)
# FIX: El sistema original no manejaba este error.
# Un atacante que pruebe métodos GET en rutas POST recibirá error no controlado.
# ==========================================
@app.errorhandler(405)
def method_not_allowed(e):
    flash('Método de solicitud no permitido.', 'warning')
    return redirect(url_for('dashboard')), 405

# ==========================================
# INICIALIZACIÓN Y CARGA DE DATOS DE PRUEBA
# ==========================================

def seed_database():
    """Crea las tablas e inserta datos iniciales si no existen"""
    # Eliminar usuario antiguo 'admin' si existe (migración)
    old_admin = User.query.filter_by(username='admin').first()
    if old_admin:
        db.session.delete(old_admin)
        db.session.commit()
        print("[-] Usuario antiguo 'admin' eliminado.")
 
    # Crear o actualizar el usuario Administrador
    admin = User.query.filter_by(username='Administrador').first()
    if admin:
        admin.password_hash = generate_password_hash('AsistPro@2026Secure!')
        db.session.commit()
        print("[-] Cuenta de administrador actualizada con la nueva contraseña.")
    else:
        admin_user = User(
            username='Administrador',
            password_hash=generate_password_hash('AsistPro@2026Secure!')
        )
        db.session.add(admin_user)
        db.session.commit()
        print("[-] Cuenta de administrador creada: Administrador / AsistPro@2026Secure!")

# Bloque de ejecución inicial
with app.app_context():
    db.create_all()
    seed_database()

if __name__ == '__main__':
    app.run(debug=True)
