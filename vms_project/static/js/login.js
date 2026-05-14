// Login page JavaScript

// Toggle password visibility
function togglePassword(button) {
    const input = button.previousElementSibling;
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Clean up form initialization
document.addEventListener('DOMContentLoaded', function() {
    // Add form-control class to all inputs if not present
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"], input[type="email"]');
    inputs.forEach(input => {
        if (!input.classList.contains('form-control')) {
            input.classList.add('form-control');
        }
        
        // Remove Bootstrap validation classes which might interfere with custom styling
        input.classList.remove('is-invalid', 'is-valid');
    });
    
    // Remove validation classes from parent form
    const form = document.querySelector('form');
    if (form) {
        form.classList.remove('was-validated');
        form.addEventListener('submit', function() {
            // Ensure no validation classes are added on submit
            inputs.forEach(input => {
                input.classList.remove('is-invalid', 'is-valid');
            });
        });
    }
});