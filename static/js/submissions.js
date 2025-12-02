/**
 * Submissions Page JavaScript
 * 
 * Author: AI Assistant
 * Created: 2025-12-02
 */

// Check authentication
const token = localStorage.getItem('token');
if (!token) {
    window.location.href = '/login';
}

let currentPage = 1;
let currentApiKeyFilter = '';
let apiKeys = [];

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

// Load API keys for filter
async function loadApiKeys() {
    try {
        const data = await apiRequest('/api/keys');

        if (data.success) {
            apiKeys = data.data;
            renderApiKeyFilter();
        }
    } catch (error) {
        console.error('Failed to load API keys:', error);
    }
}

// Render API key filter dropdown
function renderApiKeyFilter() {
    const select = document.getElementById('filter-api-key');

    select.innerHTML = '<option value="">All API Keys</option>' +
        apiKeys.map(key => `
            <option value="${key.id}">${escapeHtml(key.name)}</option>
        `).join('');
}

// Load submissions
async function loadSubmissions(page = 1) {
    currentPage = page;
    currentApiKeyFilter = document.getElementById('filter-api-key').value;

    try {
        let url = `/api/submissions?page=${page}&per_page=20`;
        if (currentApiKeyFilter) {
            url += `&api_key_id=${currentApiKeyFilter}`;
        }

        const data = await apiRequest(url);

        if (data.success) {
            renderSubmissions(data.data.submissions);
            renderPagination(data.data.page, data.data.pages);
        }
    } catch (error) {
        console.error('Failed to load submissions:', error);
    }
}

// Render submissions table
function renderSubmissions(submissions) {
    const tbody = document.getElementById('submissions-table');

    if (submissions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    No submissions found.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = submissions.map(sub => {
        const date = new Date(sub.created_at);
        const apiKey = apiKeys.find(k => k.id === sub.api_key_id);
        const apiKeyName = apiKey ? apiKey.name : 'Unknown';

        // Get first few fields for preview
        const dataPreview = Object.entries(sub.data)
            .slice(0, 2)
            .map(([key, value]) => `${key}: ${String(value).substring(0, 30)}...`)
            .join(', ');

        return `
            <tr>
                <td>
                    <div>${date.toLocaleDateString()}</div>
                    <div class="text-small text-muted">${date.toLocaleTimeString()}</div>
                </td>
                <td>${escapeHtml(apiKeyName)}</td>
                <td>
                    <span class="text-small">${escapeHtml(dataPreview)}</span>
                </td>
                <td>
                    ${sub.files && sub.files.length > 0
                ? `<span class="badge badge-info">📎 ${sub.files.length}</span>`
                : '-'
            }
                </td>
                <td>
                    <span class="badge ${sub.email_sent ? 'badge-success' : 'badge-error'}">
                        ${sub.email_sent ? '✓ Sent' : '✗ Failed'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="viewSubmission(${sub.id})">
                        View
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Render pagination
function renderPagination(currentPage, totalPages) {
    const container = document.getElementById('pagination');

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';

    // Previous button
    if (currentPage > 1) {
        html += `<button class="btn btn-sm btn-secondary" onclick="loadSubmissions(${currentPage - 1})">Previous</button>`;
    }

    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === currentPage) {
            html += `<button class="btn btn-sm btn-primary">${i}</button>`;
        } else if (i === 1 || i === totalPages || Math.abs(i - currentPage) <= 2) {
            html += `<button class="btn btn-sm btn-secondary" onclick="loadSubmissions(${i})">${i}</button>`;
        } else if (Math.abs(i - currentPage) === 3) {
            html += `<span class="btn btn-sm">...</span>`;
        }
    }

    // Next button
    if (currentPage < totalPages) {
        html += `<button class="btn btn-sm btn-secondary" onclick="loadSubmissions(${currentPage + 1})">Next</button>`;
    }

    container.innerHTML = html;
}

// View submission details
async function viewSubmission(submissionId) {
    try {
        const data = await apiRequest(`/api/submissions/${submissionId}`);

        if (data.success) {
            renderSubmissionDetails(data.data);
            document.getElementById('view-submission-modal').classList.add('active');

            // Set up delete button
            document.getElementById('delete-submission-btn').onclick = () => deleteSubmission(submissionId);
        }
    } catch (error) {
        console.error('Failed to load submission:', error);
        alert('Failed to load submission details');
    }
}

// Render submission details
function renderSubmissionDetails(submission) {
    const date = new Date(submission.created_at);
    const apiKey = apiKeys.find(k => k.id === submission.api_key_id);
    const apiKeyName = apiKey ? apiKey.name : 'Unknown';

    let html = `
        <div class="form-group">
            <label class="form-label">API Key</label>
            <div>${escapeHtml(apiKeyName)}</div>
        </div>
        
        <div class="form-group">
            <label class="form-label">Submitted At</label>
            <div>${date.toLocaleString()}</div>
        </div>
        
        <div class="form-group">
            <label class="form-label">IP Address</label>
            <div>${submission.ip_address || 'N/A'}</div>
        </div>
        
        <div class="form-group">
            <label class="form-label">Email Status</label>
            <div>
                <span class="badge ${submission.email_sent ? 'badge-success' : 'badge-error'}">
                    ${submission.email_sent ? '✓ Email Sent' : '✗ Email Failed'}
                </span>
                ${submission.email_error ? `<div class="text-small text-muted mt-1">${escapeHtml(submission.email_error)}</div>` : ''}
            </div>
        </div>
        
        <div class="form-group">
            <label class="form-label">Form Data</label>
            <div style="background: var(--bg-secondary); padding: 1rem; border-radius: var(--radius-md);">
    `;

    for (const [key, value] of Object.entries(submission.data)) {
        html += `
            <div style="margin-bottom: 0.5rem;">
                <strong>${escapeHtml(key)}:</strong> ${escapeHtml(String(value))}
            </div>
        `;
    }

    html += `</div></div>`;

    // Files
    if (submission.files && submission.files.length > 0) {
        html += `
            <div class="form-group">
                <label class="form-label">Attached Files</label>
                <div>
        `;

        for (const file of submission.files) {
            html += `
                <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: var(--radius-md); margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div><strong>${escapeHtml(file.original_filename)}</strong></div>
                        <div class="text-small text-muted">${formatFileSize(file.file_size)}</div>
                    </div>
                    <a href="/api/files/${file.id}/download" class="btn btn-sm btn-secondary">Download</a>
                </div>
            `;
        }

        html += `</div></div>`;
    }

    document.getElementById('submission-details').innerHTML = html;
}

// Delete submission
async function deleteSubmission(submissionId) {
    if (!confirm('Are you sure you want to delete this submission?')) {
        return;
    }

    try {
        const data = await apiRequest(`/api/submissions/${submissionId}`, {
            method: 'DELETE'
        });

        if (data.success) {
            closeViewSubmissionModal();
            await loadSubmissions(currentPage);
        } else {
            alert(data.message || 'Failed to delete submission');
        }
    } catch (error) {
        console.error('Failed to delete submission:', error);
        alert('An error occurred. Please try again.');
    }
}

function closeViewSubmissionModal() {
    document.getElementById('view-submission-modal').classList.remove('active');
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Filter change handler
document.getElementById('filter-api-key').addEventListener('change', () => {
    loadSubmissions(1);
});

// Load data on page load
(async () => {
    await loadApiKeys();
    await loadSubmissions(1);
})();
