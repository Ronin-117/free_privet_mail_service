/**
 * Dashboard JavaScript
 * 
 * Author: AI Assistant
 * Created: 2025-12-02
 */

// Check authentication
const token = localStorage.getItem('token');
if (!token) {
    window.location.href = '/login';
}

// API helper function
async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };

    const response = await fetch(endpoint, { ...defaultOptions, ...options });

    if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
        return;
    }

    return await response.json();
}

// Load dashboard data
async function loadDashboard() {
    await Promise.all([
        loadStats(),
        loadApiKeys()
    ]);
}

// Load statistics
async function loadStats() {
    try {
        const data = await apiRequest('/api/stats');

        if (data.success) {
            document.getElementById('stat-total-keys').textContent = data.data.total_api_keys;
            document.getElementById('stat-active-keys').textContent = data.data.active_api_keys;
            document.getElementById('stat-total-submissions').textContent = data.data.total_submissions;
            document.getElementById('stat-recent-submissions').textContent = data.data.recent_submissions;
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Load API keys
async function loadApiKeys() {
    try {
        const data = await apiRequest('/api/keys');

        if (data.success) {
            renderApiKeys(data.data);
        }
    } catch (error) {
        console.error('Failed to load API keys:', error);
    }
}

// Render API keys table
function renderApiKeys(keys) {
    const tbody = document.getElementById('api-keys-table');

    if (keys.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    No API keys yet. Create your first one!
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = keys.map(key => `
        <tr>
            <td><strong>${escapeHtml(key.name)}</strong></td>
            <td>
                <code style="font-size: 0.75rem;">${key.key.substring(0, 20)}...</code>
                <button class="btn btn-sm btn-secondary" onclick="viewApiKey('${key.key}', '${escapeHtml(key.name)}')">
                    View
                </button>
            </td>
            <td>${escapeHtml(key.recipient_email)}</td>
            <td>
                <span class="text-muted">${key.usage_count} submissions</span>
            </td>
            <td>
                <span class="badge ${key.is_active ? 'badge-success' : 'badge-error'}">
                    ${key.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-secondary" onclick="toggleApiKey(${key.id}, ${!key.is_active})">
                    ${key.is_active ? 'Deactivate' : 'Activate'}
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteApiKey(${key.id}, '${escapeHtml(key.name)}')">
                    Delete
                </button>
            </td>
        </tr>
    `).join('');
}

// Create API key modal
function openCreateKeyModal() {
    document.getElementById('create-key-modal').classList.add('active');
}

function closeCreateKeyModal() {
    document.getElementById('create-key-modal').classList.remove('active');
    document.getElementById('create-key-form').reset();
}

// Handle create API key form
document.getElementById('create-key-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        name: document.getElementById('key-name').value,
        recipient_email: document.getElementById('key-email').value,
        description: document.getElementById('key-description').value
    };

    try {
        const data = await apiRequest('/api/keys', {
            method: 'POST',
            body: JSON.stringify(formData)
        });

        if (data.success) {
            closeCreateKeyModal();
            await loadDashboard();
            alert('API key created successfully!');
        } else {
            alert(data.message || 'Failed to create API key');
        }
    } catch (error) {
        console.error('Failed to create API key:', error);
        alert('An error occurred. Please try again.');
    }
});

// View API key details
function viewApiKey(apiKey, name) {
    const endpoint = `${window.location.origin}/api/v1/submit/${apiKey}`;

    document.getElementById('api-endpoint').value = endpoint;

    const exampleCode = `<form action="${endpoint}" method="POST" enctype="multipart/form-data">
  <input type="text" name="name" placeholder="Your Name" required>
  <input type="email" name="email" placeholder="Your Email" required>
  <textarea name="message" placeholder="Your Message" required></textarea>
  <input type="file" name="attachment">
  <button type="submit">Submit</button>
</form>`;

    document.getElementById('example-code').value = exampleCode;
    document.getElementById('view-key-modal').classList.add('active');
}

function closeViewKeyModal() {
    document.getElementById('view-key-modal').classList.remove('active');
}

// Toggle API key status
async function toggleApiKey(keyId, activate) {
    try {
        const data = await apiRequest(`/api/keys/${keyId}`, {
            method: 'PUT',
            body: JSON.stringify({ is_active: activate })
        });

        if (data.success) {
            await loadApiKeys();
        } else {
            alert(data.message || 'Failed to update API key');
        }
    } catch (error) {
        console.error('Failed to toggle API key:', error);
        alert('An error occurred. Please try again.');
    }
}

// Delete API key
async function deleteApiKey(keyId, name) {
    if (!confirm(`Are you sure you want to delete "${name}"? This will also delete all associated submissions.`)) {
        return;
    }

    try {
        const data = await apiRequest(`/api/keys/${keyId}`, {
            method: 'DELETE'
        });

        if (data.success) {
            await loadDashboard();
        } else {
            alert(data.message || 'Failed to delete API key');
        }
    } catch (error) {
        console.error('Failed to delete API key:', error);
        alert('An error occurred. Please try again.');
    }
}

// Logout
document.getElementById('logout-btn').addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('token');
    window.location.href = '/login';
});

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Load dashboard on page load
loadDashboard();
