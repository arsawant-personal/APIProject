// SaaS Admin Console JavaScript

// Global variables
let accessToken = null;
let refreshToken = null;
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Bootstrap modal instances
let loginModal;
let createTenantModal;
let createUserModal;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeModals();
    checkAuthStatus();
});

// Initialize Bootstrap modals
function initializeModals() {
    loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    createTenantModal = new bootstrap.Modal(document.getElementById('createTenantModal'));
    createUserModal = new bootstrap.Modal(document.getElementById('createUserModal'));
    
    // Show login modal on page load
    loginModal.show();
    
    // Handle login form submission
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
}

// Check if user is already authenticated
function checkAuthStatus() {
    const savedToken = localStorage.getItem('accessToken');
    if (savedToken) {
        accessToken = savedToken;
        showDashboard();
        loadTenants();
    }
}

// Handle login
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginButton = event.target.querySelector('button[type="submit"]');
    const errorDiv = document.getElementById('loginError');
    
    // Show loading state
    loginButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Logging in...';
    loginButton.disabled = true;
    errorDiv.classList.add('d-none');
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });
        
        if (response.ok) {
            const data = await response.json();
            accessToken = data.access_token;
            refreshToken = data.refresh_token;
            
            // Store tokens
            localStorage.setItem('accessToken', accessToken);
            localStorage.setItem('refreshToken', refreshToken);
            
            // Hide login modal and show dashboard
            loginModal.hide();
            showDashboard();
            loadTenants();
            
            showToast('Login successful!', 'success');
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        errorDiv.textContent = error.message || 'Login failed. Please check your credentials.';
        errorDiv.classList.remove('d-none');
    } finally {
        loginButton.innerHTML = '<i class="bi bi-box-arrow-in-right"></i> Login';
        loginButton.disabled = false;
    }
}

// Show dashboard
function showDashboard() {
    document.getElementById('dashboard').classList.remove('d-none');
    document.getElementById('dashboard').classList.add('fade-in');
}

// Logout
function logout() {
    accessToken = null;
    refreshToken = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    
    document.getElementById('dashboard').classList.add('d-none');
    loginModal.show();
    
    showToast('Logged out successfully', 'info');
}

// Show different sections
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.add('d-none');
    });
    
    // Remove active class from all nav items
    document.querySelectorAll('.list-group-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(`${sectionName}Section`).classList.remove('d-none');
    document.getElementById(`${sectionName}Section`).classList.add('slide-in');
    
    // Add active class to clicked nav item
    event.target.classList.add('active');
    
    // Load data for the section
    if (sectionName === 'tenants') {
        loadTenants();
    } else if (sectionName === 'users') {
        loadUsers();
    }
}

// Load tenants
async function loadTenants() {
    try {
        const response = await makeAuthenticatedRequest(`${API_BASE_URL}/admin/tenants/`);
        const tenants = await response.json();
        
        updateTenantsTable(tenants);
        updateStats(tenants);
    } catch (error) {
        console.error('Error loading tenants:', error);
        showToast('Failed to load tenants', 'error');
    }
}

// Update tenants table
function updateTenantsTable(tenants) {
    const tbody = document.getElementById('tenantsTableBody');
    tbody.innerHTML = '';
    
    if (tenants.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted py-4">
                    <i class="bi bi-inbox fs-1"></i>
                    <p class="mt-2">No tenants found</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tenants.forEach(tenant => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${tenant.id}</td>
            <td>
                <div class="d-flex align-items-center">
                    <i class="bi bi-building me-2 text-primary"></i>
                    <strong>${tenant.name}</strong>
                </div>
            </td>
            <td>
                <span class="badge bg-light text-dark">${tenant.domain}</span>
            </td>
            <td>
                <span class="badge ${tenant.is_active ? 'bg-success' : 'bg-danger'}">
                    ${tenant.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>${formatDate(tenant.created_at)}</td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-outline-primary" onclick="editTenant(${tenant.id})" title="Edit">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteTenant(${tenant.id})" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Update stats
function updateStats(tenants) {
    const totalTenants = tenants.length;
    const activeTenants = tenants.filter(t => t.is_active).length;
    
    document.getElementById('totalTenants').textContent = totalTenants;
    document.getElementById('activeTenants').textContent = activeTenants;
    document.getElementById('recentActivity').textContent = Math.floor(Math.random() * 10) + 1; // Mock data
}

// Show create tenant modal
function showCreateTenantModal() {
    document.getElementById('createTenantForm').reset();
    document.getElementById('createTenantError').classList.add('d-none');
    document.getElementById('createTenantSuccess').classList.add('d-none');
    createTenantModal.show();
}

// Create tenant
async function createTenant() {
    const name = document.getElementById('tenantName').value;
    const domain = document.getElementById('tenantDomain').value;
    const isActive = document.getElementById('tenantActive').checked;
    
    if (!name || !domain) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    const createButton = document.querySelector('#createTenantModal .btn-primary');
    const originalText = createButton.innerHTML;
    
    try {
        createButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creating...';
        createButton.disabled = true;
        
        const response = await makeAuthenticatedRequest(`${API_BASE_URL}/admin/tenants/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                domain: domain,
                is_active: isActive
            })
        });
        
        if (response.ok) {
            const newTenant = await response.json();
            createTenantModal.hide();
            loadTenants(); // Reload the list
            showToast('Tenant created successfully!', 'success');
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create tenant');
        }
    } catch (error) {
        console.error('Error creating tenant:', error);
        const errorDiv = document.getElementById('createTenantError');
        errorDiv.textContent = error.message || 'Failed to create tenant';
        errorDiv.classList.remove('d-none');
    } finally {
        createButton.innerHTML = originalText;
        createButton.disabled = false;
    }
}

// Edit tenant (placeholder for future implementation)
function editTenant(tenantId) {
    showToast('Edit functionality coming soon!', 'info');
}

// Delete tenant (placeholder for future implementation)
function deleteTenant(tenantId) {
    if (confirm('Are you sure you want to delete this tenant?')) {
        showToast('Delete functionality coming soon!', 'info');
    }
}

// Make authenticated request with token refresh
async function makeAuthenticatedRequest(url, options = {}) {
    if (!accessToken) {
        throw new Error('No access token available');
    }
    
    const requestOptions = {
        ...options,
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            ...options.headers
        }
    };
    
    let response = await fetch(url, requestOptions);
    
    // If token is expired, try to refresh
    if (response.status === 401 && refreshToken) {
        try {
            const refreshResponse = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    refresh_token: refreshToken
                })
            });
            
            if (refreshResponse.ok) {
                const refreshData = await refreshResponse.json();
                accessToken = refreshData.access_token;
                localStorage.setItem('accessToken', accessToken);
                
                // Retry the original request
                requestOptions.headers['Authorization'] = `Bearer ${accessToken}`;
                response = await fetch(url, requestOptions);
            } else {
                // Refresh failed, redirect to login
                logout();
                throw new Error('Session expired. Please login again.');
            }
        } catch (error) {
            logout();
            throw error;
        }
    }
    
    return response;
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Show toast notification
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="bi bi-${getToastIcon(type)} me-2"></i>
                <strong class="me-auto">Admin Console</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Get toast icon based on type
function getToastIcon(type) {
    switch (type) {
        case 'success': return 'check-circle-fill';
        case 'error': return 'exclamation-triangle-fill';
        case 'warning': return 'exclamation-triangle-fill';
        case 'info': return 'info-circle-fill';
        default: return 'info-circle-fill';
    }
}

// Add some sample data for demonstration
function addSampleData() {
    const sampleTenants = [
        {
            id: 1,
            name: "Acme Corporation",
            domain: "acme.com",
            is_active: true,
            created_at: "2024-01-15T10:30:00Z"
        },
        {
            id: 2,
            name: "TechStart Inc",
            domain: "techstart.io",
            is_active: true,
            created_at: "2024-01-20T14:45:00Z"
        },
        {
            id: 3,
            name: "Global Solutions",
            domain: "globalsolutions.net",
            is_active: false,
            created_at: "2024-01-25T09:15:00Z"
        }
    ];
    
    updateTenantsTable(sampleTenants);
    updateStats(sampleTenants);
}

// Load users
async function loadUsers() {
    try {
        const response = await makeAuthenticatedRequest(`${API_BASE_URL}/admin/users/`);
        const users = await response.json();
        
        updateUsersTable(users);
        updateUserStats(users);
    } catch (error) {
        console.error('Error loading users:', error);
        showToast('Failed to load users', 'error');
    }
}

// Update users table
function updateUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    tbody.innerHTML = '';
    
    if (users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    <i class="bi bi-people fs-1"></i>
                    <p class="mt-2">No users found</p>
                </td>
            </tr>
        `;
        return;
    }
    
    users.forEach(user => {
        const row = document.createElement('tr');
        const actionButtons = `
            <div class="btn-group btn-group-sm" role="group">
                <button class="btn btn-outline-primary" onclick="editUser(${user.id})" title="Edit">
                    <i class="bi bi-pencil"></i>
                </button>
                ${user.role === 'api_user' ? `
                    <button class="btn btn-outline-success" onclick="generateUserToken(${user.id})" title="Generate Token">
                        <i class="bi bi-key"></i>
                    </button>
                ` : ''}
                <button class="btn btn-outline-danger" onclick="deleteUser(${user.id})" title="Delete">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        
        row.innerHTML = `
            <td>${user.id}</td>
            <td>
                <div class="d-flex align-items-center">
                    <i class="bi bi-person me-2 text-primary"></i>
                    <strong>${user.full_name}</strong>
                </div>
            </td>
            <td>${user.email}</td>
            <td>
                <span class="badge ${getRoleBadgeClass(user.role)}">
                    ${user.role.replace('_', ' ').toUpperCase()}
                </span>
            </td>
            <td>${user.tenant_id || 'N/A'}</td>
            <td>
                <span class="badge ${user.is_active ? 'bg-success' : 'bg-danger'}">
                    ${user.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>${formatDate(user.created_at)}</td>
            <td>${actionButtons}</td>
        `;
        tbody.appendChild(row);
    });
}

// Update user stats
function updateUserStats(users) {
    const totalUsers = users.length;
    const apiUsers = users.filter(u => u.role === 'api_user').length;
    const activeUsers = users.filter(u => u.is_active).length;
    
    document.getElementById('totalUsers').textContent = totalUsers;
    document.getElementById('apiUsers').textContent = apiUsers;
    document.getElementById('activeUsers').textContent = activeUsers;
}

// Get role badge class
function getRoleBadgeClass(role) {
    switch (role) {
        case 'super_admin': return 'bg-danger';
        case 'tenant_admin': return 'bg-warning';
        case 'api_user': return 'bg-info';
        case 'user': return 'bg-secondary';
        default: return 'bg-secondary';
    }
}

// Show create user modal
function showCreateUserModal() {
    document.getElementById('createUserForm').reset();
    document.getElementById('createUserError').classList.add('d-none');
    document.getElementById('createUserSuccess').classList.add('d-none');
    
    // Load tenants for the dropdown
    loadTenantsForUserModal();
    
    createUserModal.show();
}

// Load tenants for user creation modal
async function loadTenantsForUserModal() {
    try {
        const response = await makeAuthenticatedRequest(`${API_BASE_URL}/admin/tenants/`);
        const tenants = await response.json();
        
        const select = document.getElementById('userTenant');
        select.innerHTML = '<option value="">Select a tenant...</option>';
        
        tenants.forEach(tenant => {
            const option = document.createElement('option');
            option.value = tenant.id;
            option.textContent = tenant.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading tenants for user modal:', error);
    }
}

// Create user
async function createUser() {
    const fullName = document.getElementById('userFullName').value;
    const email = document.getElementById('userEmail').value;
    const password = document.getElementById('userPassword').value;
    const role = document.getElementById('userRole').value;
    const tenantId = document.getElementById('userTenant').value;
    const isActive = document.getElementById('userActive').checked;
    
    if (!fullName || !email || !password || !role || !tenantId) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    const createButton = document.querySelector('#createUserModal .btn-primary');
    const originalText = createButton.innerHTML;
    
    try {
        createButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creating...';
        createButton.disabled = true;
        
        const response = await makeAuthenticatedRequest(`${API_BASE_URL}/admin/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                full_name: fullName,
                email: email,
                password: password,
                role: role,
                tenant_id: parseInt(tenantId),
                is_active: isActive
            })
        });
        
        if (response.ok) {
            const newUser = await response.json();
            createUserModal.hide();
            loadUsers(); // Reload the list
            showToast('User created successfully!', 'success');
            
            // If it's an API user, offer to generate token
            if (role === 'api_user') {
                setTimeout(() => {
                    if (confirm('API user created! Would you like to generate a bearer token for this user?')) {
                        generateUserToken(newUser.id);
                    }
                }, 500);
            }
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create user');
        }
    } catch (error) {
        console.error('Error creating user:', error);
        const errorDiv = document.getElementById('createUserError');
        errorDiv.textContent = error.message || 'Failed to create user';
        errorDiv.classList.remove('d-none');
    } finally {
        createButton.innerHTML = originalText;
        createButton.disabled = false;
    }
}

// Generate token for API user
async function generateUserToken(userId) {
    try {
        const response = await makeAuthenticatedRequest(`${API_BASE_URL}/admin/users/${userId}/generate-token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const tokenData = await response.json();
            showTokenModal(tokenData);
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate token');
        }
    } catch (error) {
        console.error('Error generating token:', error);
        showToast('Failed to generate token: ' + error.message, 'error');
    }
}

// Show token modal with generated token
function showTokenModal(tokenData) {
    document.getElementById('generatedToken').value = tokenData.access_token;
    document.getElementById('tokenUserEmail').textContent = tokenData.email;
    document.getElementById('tokenUserRole').textContent = tokenData.role;
    document.getElementById('tokenUserTenant').textContent = tokenData.tenant_id || 'N/A';
    document.getElementById('tokenUserId').textContent = tokenData.user_id;
    document.getElementById('tokenExample').textContent = tokenData.access_token;
    
    const tokenModal = new bootstrap.Modal(document.getElementById('tokenModal'));
    tokenModal.show();
}

// Copy token to clipboard
function copyToken() {
    const tokenInput = document.getElementById('generatedToken');
    tokenInput.select();
    tokenInput.setSelectionRange(0, 99999); // For mobile devices
    
    try {
        document.execCommand('copy');
        showToast('Token copied to clipboard!', 'success');
    } catch (err) {
        // Fallback for modern browsers
        navigator.clipboard.writeText(tokenInput.value).then(() => {
            showToast('Token copied to clipboard!', 'success');
        }).catch(() => {
            showToast('Failed to copy token', 'error');
        });
    }
}

// Edit user (placeholder for future implementation)
function editUser(userId) {
    showToast('Edit functionality coming soon!', 'info');
}

// Delete user (placeholder for future implementation)
function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        showToast('Delete functionality coming soon!', 'info');
    }
}

// Export functions for global access
window.showSection = showSection;
window.showCreateTenantModal = showCreateTenantModal;
window.createTenant = createTenant;
window.editTenant = editTenant;
window.deleteTenant = deleteTenant;
window.showCreateUserModal = showCreateUserModal;
window.createUser = createUser;
window.editUser = editUser;
window.deleteUser = deleteUser;
window.generateUserToken = generateUserToken;
window.copyToken = copyToken;
window.logout = logout; 