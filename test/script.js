/**
 * Job Application Form Script
 * Integrates with Form Service API
 */

// ⚠️ REPLACE THIS WITH YOUR ACTUAL API KEY FROM THE DASHBOARD
const API_KEY = '8OPfFWA1v2hLoo9AzdvKewSSV1cYgqq60LiX8juiklmFpbrw';
const API_ENDPOINT = `https://nj-mail-services.onrender.com/api/v1/submit/${API_KEY}`;

// For local testing, uncomment this:
// const API_ENDPOINT = `http://localhost:5000/api/v1/submit/${API_KEY}`;

// Get form elements
const form = document.getElementById('application-form');
const submitBtn = document.getElementById('submitBtn');
const submitText = document.getElementById('submitText');
const submitSpinner = document.getElementById('submitSpinner');
const alertContainer = document.getElementById('alert-container');

// File input handlers
const resumeInput = document.getElementById('resume');
const additionalInput = document.getElementById('additional');

// Update file input display when file is selected
function setupFileInput(input) {
    input.addEventListener('change', function () {
        const fileDisplay = this.parentElement.querySelector('.file-text');
        if (this.files.length > 0) {
            const fileName = this.files[0].name;
            const fileSize = (this.files[0].size / 1024 / 1024).toFixed(2);
            fileDisplay.textContent = `${fileName} (${fileSize} MB)`;
            fileDisplay.style.color = 'var(--primary-color)';
        }
    });
}

setupFileInput(resumeInput);
setupFileInput(additionalInput);

// Show alert message
function showAlert(message, type = 'success') {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
    const icon = type === 'success' ? '✓' : '✗';

    alertContainer.innerHTML = `
        <div class="alert ${alertClass}">
            <span style="font-size: 1.5rem;">${icon}</span>
            <span>${message}</span>
        </div>
    `;

    // Scroll to alert
    alertContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            alertContainer.innerHTML = '';
        }, 5000);
    }
}

// Validate form before submission
function validateForm() {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    let firstInvalidField = null;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.style.borderColor = 'var(--error-color)';
            if (!firstInvalidField) {
                firstInvalidField = field;
            }
        } else {
            field.style.borderColor = 'var(--border-color)';
        }
    });

    if (!isValid && firstInvalidField) {
        firstInvalidField.focus();
        firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        showAlert('Please fill in all required fields', 'error');
    }

    return isValid;
}

// Validate file size
function validateFileSize(file, maxSizeMB = 5) {
    const fileSizeMB = file.size / 1024 / 1024;
    return fileSizeMB <= maxSizeMB;
}

// Handle form submission
form.addEventListener('submit', async function (e) {
    e.preventDefault();

    // Check if API key is set
    if (API_KEY === 'YOUR_API_KEY_HERE') {
        showAlert('⚠️ Please update the API_KEY in script.js with your actual API key from the dashboard!', 'error');
        return;
    }

    // Validate form
    if (!validateForm()) {
        return;
    }

    // Validate resume file
    if (resumeInput.files.length > 0) {
        if (!validateFileSize(resumeInput.files[0], 5)) {
            showAlert('Resume file size must be less than 5MB', 'error');
            return;
        }
    }

    // Show loading state
    submitBtn.disabled = true;
    submitText.classList.add('hidden');
    submitSpinner.classList.remove('hidden');
    alertContainer.innerHTML = '';

    try {
        // Create FormData object
        const formData = new FormData(form);

        // Submit to API
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // Success!
            showAlert('🎉 Application submitted successfully! We\'ll review your application and get back to you within 48 hours.', 'success');

            // Reset form after 2 seconds
            setTimeout(() => {
                form.reset();
                // Reset file input displays
                document.querySelectorAll('.file-text').forEach(el => {
                    if (el.textContent.includes('MB')) {
                        el.textContent = el.parentElement.querySelector('input').id === 'resume'
                            ? 'Choose file or drag here'
                            : 'Portfolio, certificates, etc.';
                        el.style.color = '';
                    }
                });
            }, 2000);
        } else {
            // Error from API
            showAlert(`Error: ${data.message || 'Failed to submit application. Please try again.'}`, 'error');
        }

    } catch (error) {
        console.error('Submission error:', error);
        showAlert('Network error: Unable to submit application. Please check your connection and try again.', 'error');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        submitText.classList.remove('hidden');
        submitSpinner.classList.add('hidden');
    }
});

// Add input validation on blur
form.querySelectorAll('input[required], select[required], textarea[required]').forEach(field => {
    field.addEventListener('blur', function () {
        if (!this.value.trim()) {
            this.style.borderColor = 'var(--error-color)';
        } else {
            this.style.borderColor = 'var(--border-color)';
        }
    });

    field.addEventListener('input', function () {
        if (this.value.trim()) {
            this.style.borderColor = 'var(--border-color)';
        }
    });
});

// Email validation
const emailInput = document.getElementById('email');
emailInput.addEventListener('blur', function () {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (this.value && !emailRegex.test(this.value)) {
        this.style.borderColor = 'var(--error-color)';
        showAlert('Please enter a valid email address', 'error');
    }
});

// Phone validation (basic)
const phoneInput = document.getElementById('phone');
phoneInput.addEventListener('blur', function () {
    const phoneRegex = /^[\d\s\-\+\(\)]+$/;
    if (this.value && !phoneRegex.test(this.value)) {
        this.style.borderColor = 'var(--error-color)';
        showAlert('Please enter a valid phone number', 'error');
    }
});

// Drag and drop for file inputs
function setupDragDrop(input) {
    const wrapper = input.parentElement;
    const display = wrapper.querySelector('.file-input-display');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        wrapper.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        wrapper.addEventListener(eventName, () => {
            display.style.borderColor = 'var(--primary-color)';
            display.style.background = 'rgba(37, 99, 235, 0.1)';
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        wrapper.addEventListener(eventName, () => {
            display.style.borderColor = 'var(--border-color)';
            display.style.background = 'var(--bg-secondary)';
        });
    });

    wrapper.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        input.files = files;

        // Trigger change event
        const event = new Event('change', { bubbles: true });
        input.dispatchEvent(event);
    });
}

setupDragDrop(resumeInput);
setupDragDrop(additionalInput);

console.log('📋 Job Application Form loaded successfully!');
console.log('⚠️ Remember to update the API_KEY in script.js with your actual API key!');
