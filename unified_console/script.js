// Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Global variables
let accessToken = null;
let refreshToken = null;
let currentUser = null;
let loginModal = null;
let createTenantModal = null;
let createUserModal = null;
let createTokenModal = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeModals();
    hideMainContent();
    checkAuthStatus();
});

// Initialize Bootstrap modals
function initializeModals() {
    loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    createTenantModal = new bootstrap.Modal(document.getElementById('createTenantModal'));
    createUserModal = new bootstrap.Modal(document.getElementById('createUserModal'));
    createTokenModal = new bootstrap.Modal(document.getElementById('createTokenModal'));
    
    // Handle login form submission
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
}

// Hide main content and show login page
function hideMainContent() {
    // Hide all dashboards
    document.getElementById('adminDashboard').classList.add('d-none');
    document.getElementById('tenantDashboard').classList.add('d-none');
    
    // Show a clean login page
    const loginPage = document.createElement('div');
    loginPage.id = 'loginPage';
    loginPage.className = 'container-fluid d-flex align-items-center justify-content-center';
    loginPage.style.minHeight = '100vh';
    loginPage.innerHTML = `
        <div class="text-center">
            <div class="mb-4">
                <i class="bi bi-gear-wide-connected fs-1 text-primary"></i>
            </div>
            <h2 class="mb-4">SaaS Console</h2>
            <p class="text-muted mb-4">Please log in to access your dashboard</p>
            <button class="btn btn-primary btn-lg" onclick="showLoginModal()">
                <i class="bi bi-box-arrow-in-right"></i> Click here to login
            </button>
        </div>
    `;
    
    // Insert the login page before the dashboards
    const adminDashboard = document.getElementById('adminDashboard');
    adminDashboard.parentNode.insertBefore(loginPage, adminDashboard);
}

// Show login modal
function showLoginModal() {
    loginModal.show();
}

// Check if user is already authenticated
function checkAuthStatus() {
    const savedToken = localStorage.getItem('unifiedAccessToken');
    if (savedToken) {
        accessToken = savedToken;
        // Verify token is still valid by making a test request
        verifyTokenAndLoadUser();
    }
}

// Verify token and load user data
async function verifyTokenAndLoadUser() {
    try {
        const response = await makeAuthenticatedRequest(`${API_BASE_URL}/auth/me`);
        if (response.ok) {
            currentUser = await response.json();
            routeUserToAppropriateDashboard();
        } else {
            // Token is invalid, clear it
            localStorage.removeItem('unifiedAccessToken');
            accessToken = null;
        }
    } catch (error) {
        console.error('Error verifying token:', error);
        localStorage.removeItem('unifiedAccessToken');
        accessToken = null;
    }
}

// Route user to appropriate dashboard based on role
function routeUserToAppropriateDashboard() {
    if (currentUser.role === 'SUPER_ADMIN') {
        showAdminDashboard();
    } else if (currentUser.role === 'USER') {
        showTenantDashboard();
    } else {
        // Unknown role, show error
        showToast('Unknown user role. Please contact administrator.', 'error');
        logout();
    }
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
        });
        
        if (response.ok) {
            const data = await response.json();
            accessToken = data.access_token;
            refreshToken = data.refresh_token;
            
            // Store tokens (use different key for unified console)
            localStorage.setItem('unifiedAccessToken', accessToken);
            localStorage.setItem('unifiedRefreshToken', refreshToken);
            
            // Get user details
            const userResponse = await makeAuthenticatedRequest(`${API_BASE_URL}/auth/me`);
            if (userResponse.ok) {
                currentUser = await userResponse.json();
                
                // Route user to appropriate dashboard
                routeUserToAppropriateDashboard();
                loginModal.hide();
                showToast('Login successful!', 'success');
            }
        } else {
            const errorData = await response.json();
            showToast(errorData.detail || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Login failed. Please try again.', 'error');
    }
}

// Show admin dashboard
function showAdminDashboard() {
    // Hide the login page
    const loginPage = document.getElementById('loginPage');
    if (loginPage) {
        loginPage.remove();
    }
    
    // Hide tenant dashboard
    document.getElementById('tenantDashboard').classList.add('d-none');
    
    // Show the admin dashboard
    document.getElementById('adminDashboard').classList.remove('d-none');
    document.getElementById('adminDashboard').classList.add('fade-in');
    
    // Load initial data
    loadTenants();
}

// Show tenant dashboard
function showTenantDashboard() {
    // Hide the login page
    const loginPage = document.getElementById('loginPage');
    if (loginPage) {
        loginPage.remove();
    }
    
    // Hide admin dashboard
    document.getElementById('adminDashboard').classList.add('d-none');
    
    // Show the tenant dashboard
    document.getElementById('tenantDashboard').classList.remove('d-none');
    document.getElementById('tenantDashboard').classList.add('fade-in');
    
    // Update user information
    if (currentUser) {
        document.getElementById('userName').textContent = currentUser.email;
        document.getElementById('userGreeting').textContent = currentUser.email.split('@')[0]; // Show first part of email
        document.getElementById('tenantName').textContent = currentUser.tenant?.name || 'Your Tenant';
    }
}

// Logout
function logout() {
    accessToken = null;
    refreshToken = null;
    currentUser = null;
    localStorage.removeItem('unifiedAccessToken');
    localStorage.removeItem('unifiedRefreshToken');
    
    // Hide all dashboards and show login page
    hideMainContent();
    
    showToast('Logged out successfully', 'info');
}

// Make authenticated request
async function makeAuthenticatedRequest(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    if (response.status === 401) {
        // Token expired, try to refresh
        if (refreshToken) {
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
                    localStorage.setItem('unifiedAccessToken', accessToken);
                    
                    // Retry the original request
                    headers['Authorization'] = `Bearer ${accessToken}`;
                    return await fetch(url, {
                        ...options,
                        headers
                    });
                } else {
                    // Refresh failed, logout
                    logout();
                    return response;
                }
            } catch (error) {
                console.error('Token refresh error:', error);
                logout();
                return response;
            }
        } else {
            logout();
            return response;
        }
    }
    
    return response;
}

// Show different sections (Admin only)
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
    } else if (sectionName === 'tokens') {
        loadTokens();
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
    const recentActivity = tenants.filter(t => {
        const created = new Date(t.created_at);
        const now = new Date();
        const diffDays = (now - created) / (1000 * 60 * 60 * 24);
        return diffDays <= 7;
    }).length;
    
    document.getElementById('totalTenants').textContent = totalTenants;
    document.getElementById('activeTenants').textContent = activeTenants;
    document.getElementById('recentActivity').textContent = recentActivity;
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
                    ${user.role === 'SUPER_ADMIN' ? 'SUPER ADMIN' : user.role === 'USER' ? 'TENANT USER' : user.role}
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
    const tenantUsers = users.filter(u => u.role === 'USER').length;
    const superAdmins = users.filter(u => u.role === 'SUPER_ADMIN').length;
    const activeUsers = users.filter(u => u.is_active).length;
    
    document.getElementById('totalUsers').textContent = totalUsers;
    document.getElementById('apiUsers').textContent = tenantUsers;
    document.getElementById('superAdmins').textContent = superAdmins;
    document.getElementById('activeUsers').textContent = activeUsers;
}

// Get role badge class
function getRoleBadgeClass(role) {
    switch (role) {
        case 'SUPER_ADMIN': return 'bg-danger';
        case 'USER': return 'bg-primary';
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





// Load tokens
async function loadTokens() {
    try {
        // For now, show placeholder since token system is not implemented
        showToast('Token management coming soon...', 'info');
    } catch (error) {
        console.error('Error loading tokens:', error);
        showToast('Failed to load tokens', 'error');
    }
}

// Update tokens table
function updateTokensTable(tokens) {
    const tbody = document.getElementById('tokensTableBody');
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="text-center text-muted py-4">
                <i class="bi bi-key fs-1"></i>
                <p class="mt-2">Token management coming soon...</p>
            </td>
        </tr>
    `;
}

// Update token stats
function updateTokenStats(tokens) {
    document.getElementById('totalTokens').textContent = '0';
    document.getElementById('activeTokens').textContent = '0';
    document.getElementById('expiredTokens').textContent = '0';
    document.getElementById('tenantsWithTokens').textContent = '0';
}

// Show create token modal
function showCreateTokenModal() {
    showToast('Token creation coming soon...', 'info');
}

// Load tenants for token modal
async function loadTenantsForTokenModal() {
    // Placeholder for future implementation
}

// Create token
async function createToken() {
    showToast('Token creation coming soon...', 'info');
}

// Placeholder functions for future implementation
function editTenant(tenantId) {
    showToast('Edit tenant coming soon...', 'info');
}

function deleteTenant(tenantId) {
    showToast('Delete tenant coming soon...', 'info');
}

function editUser(userId) {
    showToast('Edit user coming soon...', 'info');
}

function deleteUser(userId) {
    showToast('Delete user coming soon...', 'info');
}

function showCreateProductModal() {
    showToast('Product management coming soon...', 'info');
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${getToastBgClass(type)} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi ${getToastIcon(type)} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Get toast background class
function getToastBgClass(type) {
    switch (type) {
        case 'success': return 'success';
        case 'error': return 'danger';
        case 'warning': return 'warning';
        default: return 'primary';
    }
}

// Get toast icon
function getToastIcon(type) {
    switch (type) {
        case 'success': return 'bi-check-circle';
        case 'error': return 'bi-exclamation-triangle';
        case 'warning': return 'bi-exclamation-triangle';
        default: return 'bi-info-circle';
    }
} 