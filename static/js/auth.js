/**
 * Authentication JavaScript
 * 
 * Author: AI Assistant
 * Created: 2025-12-02
 */

// Check if user is already logged in
if (localStorage.getItem('token')) {
    window.location.href = '/';
}

// Handle login form submission
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    // Show loading state
    document.getElementById('login-text').classList.add('hidden');
    document.getElementById('login-spinner').classList.remove('hidden');
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Store token
            localStorage.setItem('token', data.data.access_token);
            
            // Show success message
            showAlert('Login successful! Redirecting...', 'success');
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            showAlert(data.message || 'Login failed', 'error');
            resetLoginButton();
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('An error occurred. Please try again.', 'error');
        resetLoginButton();
    }
});

function resetLoginButton() {
    document.getElementById('login-text').classList.remove('hidden');
    document.getElementById('login-spinner').classList.add('hidden');
}

function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
    const icon = type === 'success' ? '✓' : '✗';
    
    alertContainer.innerHTML = `
        <div class="alert ${alertClass}">
            <span>${icon}</span>
            <span>${message}</span>
        </div>
    `;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        alertContainer.innerHTML = '';
    }, 5000);
}
