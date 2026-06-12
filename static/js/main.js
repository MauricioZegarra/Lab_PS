/**
 * AsistPro - Sistema de Registro y Control de Asistencia
 * Client-side script file
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-fade out flash notifications after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 1b. Auto-open "Registrar Estudiante" modal if redirected from dashboard
    if (sessionStorage.getItem('openAddModal') === '1') {
        sessionStorage.removeItem('openAddModal');
        const addModal = document.getElementById('addStudentModal');
        if (addModal && typeof bootstrap !== 'undefined') {
            const bsModal = new bootstrap.Modal(addModal);
            bsModal.show();
        }
    }

    // 2. Edit Student Modal Populator
    // We listen to the show.bs.modal event of the edit student modal to populate it with attributes of the button clicked.
    const editStudentModal = document.getElementById('editStudentModal');
    if (editStudentModal) {
        editStudentModal.addEventListener('show.bs.modal', (event) => {
            const button = event.relatedTarget;
            
            // Extract info from data-attributes
            const studentId = button.getAttribute('data-id');
            const code = button.getAttribute('data-code');
            const firstName = button.getAttribute('data-firstname');
            const lastName = button.getAttribute('data-lastname');
            const career = button.getAttribute('data-career');
            const email = button.getAttribute('data-email');
            
            // Get form elements
            const form = editStudentModal.querySelector('#editStudentForm');
            const inputId = editStudentModal.querySelector('#edit_id');
            const inputCode = editStudentModal.querySelector('#edit_student_code');
            const inputFirstName = editStudentModal.querySelector('#edit_first_name');
            const inputLastName = editStudentModal.querySelector('#edit_last_name');
            const inputCareer = editStudentModal.querySelector('#edit_career');
            const inputEmail = editStudentModal.querySelector('#edit_email');
            
            // Update values
            form.action = `/students/edit/${studentId}`;
            inputId.value = studentId;
            inputCode.value = code;
            inputFirstName.value = firstName;
            inputLastName.value = lastName;
            inputCareer.value = career;
            inputEmail.value = email;
        });
    }

    // 3. Client-Side Form Validations (UX check before server submit)
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // 4. Real-time form validations (Google Forms style with is-valid / is-invalid)
    const setupRealTimeValidation = (input, validationFn, feedbackMessage) => {
        const validate = () => {
            const value = input.value.trim();
            const isValid = validationFn(value);
            const feedbackContainer = input.nextElementSibling;
            
            if (isValid) {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
                input.setCustomValidity('');
            } else {
                input.classList.remove('is-valid');
                input.classList.add('is-invalid');
                input.setCustomValidity(feedbackMessage);
                if (feedbackContainer && feedbackContainer.classList.contains('invalid-feedback')) {
                    feedbackContainer.textContent = feedbackMessage;
                }
            }
        };

        input.addEventListener('input', validate);
        input.addEventListener('blur', validate);
    };

    // Validation definitions matching Flask backend rules
    const isValidCode = (val) => /^\d{8}$/.test(val);
    const isValidName = (val) => val.length > 0 && val.length <= 50 && /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$/.test(val);
    const isValidLastName = (val) => val.length > 0 && val.length <= 75 && /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$/.test(val);
    const isValidEmail = (val) => val.length > 0 && val.length <= 120 && /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,6}$/.test(val);

    // Apply validation to Add Student form
    const codeInput = document.getElementById('student_code');
    const firstNameInput = document.getElementById('first_name');
    const lastNameInput = document.getElementById('last_name');
    const emailInput = document.getElementById('email');

    if (codeInput) setupRealTimeValidation(codeInput, isValidCode, 'El código universitario debe tener exactamente 8 dígitos numéricos.');
    if (firstNameInput) setupRealTimeValidation(firstNameInput, isValidName, 'Nombre inválido (solo letras, espacios y guiones, máx. 50 caracteres).');
    if (lastNameInput) setupRealTimeValidation(lastNameInput, isValidLastName, 'Apellido inválido (solo letras, espacios y guiones, máx. 75 caracteres).');
    if (emailInput) setupRealTimeValidation(emailInput, isValidEmail, 'Ingrese un correo electrónico válido (ej: usuario@dominio.com).');

    // Apply validation to Edit Student form
    const editCodeInput = document.getElementById('edit_student_code');
    const editFirstNameInput = document.getElementById('edit_first_name');
    const editLastNameInput = document.getElementById('edit_last_name');
    const editEmailInput = document.getElementById('edit_email');

    if (editCodeInput) setupRealTimeValidation(editCodeInput, isValidCode, 'El código universitario debe tener exactamente 8 dígitos numéricos.');
    if (editFirstNameInput) setupRealTimeValidation(editFirstNameInput, isValidName, 'Nombre inválido (solo letras, espacios y guiones, máx. 50 caracteres).');
    if (editLastNameInput) setupRealTimeValidation(editLastNameInput, isValidLastName, 'Apellido inválido (solo letras, espacios y guiones, máx. 75 caracteres).');
    if (editEmailInput) setupRealTimeValidation(editEmailInput, isValidEmail, 'Ingrese un correo electrónico válido (ej: usuario@dominio.com).');
});
