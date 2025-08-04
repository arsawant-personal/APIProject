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

// Session management variables
let sessionTimeout = null;
let inactivityTimeout = null;
let lastActivity = Date.now();
const SESSION_TIMEOUT_MINUTES = 10; // Configurable timeout
const WARNING_TIME_MINUTES = 9; // Show warning at 9 minutes
const HEALTH_CHECK_INTERVAL = 30000; // 30 seconds
let healthCheckInterval = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeModals();
    hideMainContent();
    checkAuthStatus();
    setupActivityTracking();
});

// Initialize Bootstrap modals
function initializeModals() {
    createTenantModal = new bootstrap.Modal(document.getElementById('createTenantModal'));
    createUserModal = new bootstrap.Modal(document.getElementById('createUserModal'));
    createTokenModal = new bootstrap.Modal(document.getElementById('createTokenModal'));
    
    // Handle login form submission (inline form only)
    document.addEventListener('submit', function(event) {
        if (event.target.id === 'loginFormInline') {
            event.preventDefault();
            handleLogin(event);
        }
    });
}

// Setup activity tracking for session management
function setupActivityTracking() {
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    events.forEach(event => {
        document.addEventListener(event, updateActivity);
    });
}

// Update last activity timestamp
function updateActivity() {
    lastActivity = Date.now();
    resetInactivityTimer();
}

// Reset inactivity timer
function resetInactivityTimer() {
    if (inactivityTimeout) {
        clearTimeout(inactivityTimeout);
    }
    
    // Set warning timeout (9 minutes)
    inactivityTimeout = setTimeout(() => {
        showSessionWarning();
    }, WARNING_TIME_MINUTES * 60 * 1000);
    
    // Set logout timeout (10 minutes)
    sessionTimeout = setTimeout(() => {
        logout();
    }, SESSION_TIMEOUT_MINUTES * 60 * 1000);
}

// Show session warning
function showSessionWarning() {
    const warningModal = new bootstrap.Modal(document.createElement('div'));
    const modalHtml = `
        <div class="modal fade" id="sessionWarningModal" tabindex="-1">
            <div class="modal-dialog modal-sm">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title">
                            <i class="bi bi-exclamation-triangle"></i> Session Timeout Warning
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <p class="mb-3">Your session will expire in <strong>1 minute</strong> due to inactivity.</p>
                        <p class="text-muted small">Click anywhere or press any key to extend your session.</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="extendSession()">
                            <i class="bi bi-clock"></i> Extend Session
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('sessionWarningModal'));
    modal.show();
    
    // Auto-hide after 1 minute
    setTimeout(() => {
        modal.hide();
        logout();
    }, 60000);
}

// Extend session
function extendSession() {
    updateActivity();
    const modal = bootstrap.Modal.getInstance(document.getElementById('sessionWarningModal'));
    if (modal) {
        modal.hide();
    }
    showToast('Session extended successfully!', 'success');
}

// Start health check interval
function startHealthCheck() {
    if (healthCheckInterval) {
        clearInterval(healthCheckInterval);
    }
    
    healthCheckInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/health`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                console.log('Server health check failed, logging out...');
                logout();
            }
        } catch (error) {
            console.log('Server unreachable, logging out...');
            logout();
        }
    }, HEALTH_CHECK_INTERVAL);
}

// Stop health check interval
function stopHealthCheck() {
    if (healthCheckInterval) {
        clearInterval(healthCheckInterval);
        healthCheckInterval = null;
    }
}

// Hide main content and show login page
function hideMainContent() {
    // Hide all dashboards
    const adminDashboard = document.getElementById('adminDashboard');
    const tenantDashboard = document.getElementById('tenantDashboard');
    
    if (adminDashboard) {
        adminDashboard.classList.add('d-none');
    }
    if (tenantDashboard) {
        tenantDashboard.classList.add('d-none');
    }
    
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
            <div class="card login-card">
                <div class="card-body">
                    <form id="loginFormInline">
                        <div class="mb-3">
                            <label for="emailInline" class="form-label">Email</label>
                            <input type="email" class="form-control login-input" id="emailInline" value="admin@yourcompany.com" required>
                        </div>
                        <div class="mb-3">
                            <label for="passwordInline" class="form-label">Password</label>
                            <input type="password" class="form-control login-input" id="passwordInline" value="your-super-admin-password" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">
                                <i class="bi bi-box-arrow-in-right"></i> Login
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    // Insert the login page before the dashboards
    if (adminDashboard) {
        adminDashboard.parentNode.insertBefore(loginPage, adminDashboard);
    } else {
        // Fallback: append to body
        document.body.appendChild(loginPage);
    }
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
    
    // Start session management after successful login
    resetInactivityTimer();
    startHealthCheck();
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    
    // Get form data from inline form only
    const email = document.getElementById('emailInline')?.value;
    const password = document.getElementById('passwordInline')?.value;
    
    if (!email || !password) {
        showToast('Please enter both email and password', 'error');
        return;
    }
    
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
                
                // Clear default credentials after successful login
                const emailInput = document.getElementById('emailInline');
                const passwordInput = document.getElementById('passwordInline');
                if (emailInput) emailInput.value = '';
                if (passwordInput) passwordInput.value = '';
                
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
    // Stop session management
    if (sessionTimeout) {
        clearTimeout(sessionTimeout);
        sessionTimeout = null;
    }
    if (inactivityTimeout) {
        clearTimeout(inactivityTimeout);
        inactivityTimeout = null;
    }
    stopHealthCheck();
    
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
function showSection(sectionName, event = null) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.add('d-none');
        section.style.display = 'none';
        section.style.visibility = 'hidden';
        section.style.opacity = '0';
    });
    
    // Remove active class from all nav items
    document.querySelectorAll('.list-group-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected section
    const sectionElement = document.getElementById(`${sectionName}Section`);
    if (sectionElement) {
        sectionElement.classList.remove('d-none');
        sectionElement.style.display = 'block';
        sectionElement.style.visibility = 'visible';
        sectionElement.style.opacity = '1';
        sectionElement.style.width = '100%';
    }
    
    // Add active class to clicked nav item (if event is available and target exists)
    if (event && event.target && event.target.classList) {
        event.target.classList.add('active');
    } else {
        // Fallback: find the nav item by section name and activate it
        const navItems = document.querySelectorAll('.list-group-item');
        navItems.forEach(item => {
            if (item.getAttribute('onclick') && item.getAttribute('onclick').includes(sectionName)) {
                item.classList.add('active');
            }
        });
    }
    
    // Load data for the section
    if (sectionName === 'tenants') {
        loadTenants();
    } else if (sectionName === 'users') {
        loadUsers();
    } else if (sectionName === 'tokens') {
        loadTokens();
    } else if (sectionName === 'api-tracking') {
        // API tracking is handled by direct integration
        const apiTrackingSection = document.getElementById('apiTrackingSection');
        if (apiTrackingSection) {
            // Properly remove the d-none class and force visibility
            apiTrackingSection.classList.remove('d-none');
            apiTrackingSection.style.display = 'block';
            apiTrackingSection.style.visibility = 'visible';
            apiTrackingSection.style.opacity = '1';
            apiTrackingSection.style.width = '100%';
        }
        
        // Add a small delay to ensure the section is visible
        setTimeout(() => {
            loadApiCallsDirect();
        }, 100);
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
        
        // Only show action buttons for non-SUPER_ADMIN users
        const actionButtons = user.role === 'SUPER_ADMIN' ? 
            '<span class="text-muted">No actions available</span>' :
            `<div class="btn-group btn-group-sm" role="group">
                <button class="btn btn-outline-primary" onclick="editUser(${user.id})" title="Edit">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-outline-danger" onclick="deleteUser(${user.id})" title="Delete">
                    <i class="bi bi-trash"></i>
                </button>
            </div>`;
        
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





// Global pagination state for tokens
let currentTokenPage = 1;
let tokenPageSize = 10;
let totalTokenRecords = 0;

// Load tokens with pagination
async function loadTokens(page = 1, size = 10) {
    try {
        // Update global state
        currentTokenPage = page;
        tokenPageSize = size;
        
        const url = `http://localhost:8000/api/v1/tokens/?page=${page}&size=${size}`;
        const response = await makeAuthenticatedRequest(url);
        
        if (response.ok) {
            const data = await response.json();
            
            // Handle paginated response
            let tokens, total;
            if (data.items && data.total !== undefined) {
                // New paginated format
                tokens = data.items;
                total = data.total;
                totalTokenRecords = total;
            } else if (Array.isArray(data)) {
                // Fallback for array format
                tokens = data;
                total = data.length;
                totalTokenRecords = total;
            } else {
                // Fallback for other formats
                tokens = data.items || data.results || [];
                total = data.total || data.count || tokens.length;
                totalTokenRecords = total;
            }
            
            updateTokensTable(tokens, total, page, size);
            updateTokenStats(tokens);
        } else {
            console.error('Failed to load tokens:', response.status);
            showToast('Failed to load tokens', 'error');
        }
    } catch (error) {
        console.error('Error loading tokens:', error);
        showToast('Failed to load tokens', 'error');
    }
}

// Update tokens table with pagination
function updateTokensTable(tokens, total, page, size) {
    const tbody = document.getElementById('tokensTableBody');
    
    if (!tokens || tokens.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-4">
                    <i class="bi bi-key fs-1"></i>
                    <p class="mt-2">No tokens found</p>
                </td>
            </tr>
        `;
        return;
    }
    
    // Add pagination above the table card
    const tokensSection = document.querySelector('#tokensSection');
    const tableCard = tokensSection.querySelector('.card');
    
    if (tokensSection && tableCard) {
        // Remove existing pagination if it exists
        const existingPagination = tokensSection.querySelector('.pagination-controls');
        if (existingPagination) {
            existingPagination.remove();
        }
        // Calculate pagination info
        const totalPages = Math.ceil(total / size);
        const startRecord = (page - 1) * size + 1;
        const endRecord = Math.min(page * size, total);
        
        // Build pagination controls
        let paginationHTML = '<div class="pagination-controls mb-3" style="display: flex; justify-content: space-between; align-items: center; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">';
        paginationHTML += '<div class="pagination-info text-muted">';
        paginationHTML += `Showing ${startRecord} to ${endRecord} of ${total} tokens`;
        paginationHTML += '</div>';
        paginationHTML += '<div class="pagination-controls-inner d-flex align-items-center gap-2">';
        
        // Page size selector
        paginationHTML += '<div class="d-flex align-items-center gap-2">';
        paginationHTML += '<label for="tokenPageSize" class="mb-0 small">Tokens per page:</label>';
        paginationHTML += '<select id="tokenPageSize" class="form-select form-select-sm" style="width: auto;" onchange="changeTokenPageSize(this.value)">';
        paginationHTML += `<option value="10" ${size === 10 ? 'selected' : ''}>10</option>`;
        paginationHTML += `<option value="25" ${size === 25 ? 'selected' : ''}>25</option>`;
        paginationHTML += `<option value="50" ${size === 50 ? 'selected' : ''}>50</option>`;
        paginationHTML += `<option value="100" ${size === 100 ? 'selected' : ''}>100</option>`;
        paginationHTML += '</select>';
        paginationHTML += '</div>';
        
        // Navigation buttons (only show if multiple pages)
        if (totalPages > 1) {
            paginationHTML += '<div class="pagination-buttons d-flex gap-1">';
            
            // Previous button
            const prevDisabled = page <= 1 ? 'disabled' : '';
            paginationHTML += `<button class="btn btn-sm btn-outline-primary" onclick="changeTokenPage(${page - 1})" ${prevDisabled}>Previous</button>`;
            
            // Page numbers
            const startPage = Math.max(1, page - 2);
            const endPage = Math.min(totalPages, page + 2);
            
            if (startPage > 1) {
                paginationHTML += `<button class="btn btn-sm btn-outline-primary" onclick="changeTokenPage(1)">1</button>`;
                if (startPage > 2) {
                    paginationHTML += '<span class="px-2">...</span>';
                }
            }
            
            for (let i = startPage; i <= endPage; i++) {
                const active = i === page ? 'btn-primary' : 'btn-outline-primary';
                paginationHTML += `<button class="btn btn-sm ${active}" onclick="changeTokenPage(${i})">${i}</button>`;
            }
            
            if (endPage < totalPages) {
                if (endPage < totalPages - 1) {
                    paginationHTML += '<span class="px-2">...</span>';
                }
                paginationHTML += `<button class="btn btn-sm btn-outline-primary" onclick="changeTokenPage(${totalPages})">${totalPages}</button>`;
            }
            
            // Next button
            const nextDisabled = page >= totalPages ? 'disabled' : '';
            paginationHTML += `<button class="btn btn-sm btn-outline-primary" onclick="changeTokenPage(${page + 1})" ${nextDisabled}>Next</button>`;
            
            paginationHTML += '</div>';
        }
        
        paginationHTML += '</div></div>';
        
        // Insert pagination before the table card
        tableCard.insertAdjacentHTML('beforebegin', paginationHTML);
    }
    
    // Update the table body
    tbody.innerHTML = tokens.map(token => `
        <tr>
            <td>${token.id}</td>
            <td>${token.name}</td>
            <td>${token.tenant_name}</td>
            <td>
                <code class="text-break" style="font-size: 0.8em;">${token.token_hash.substring(0, 20)}...</code>
                <button class="btn btn-sm btn-outline-secondary ms-1" onclick="copyToClipboard('${token.token_hash}')" title="Copy full token">
                    <i class="bi bi-clipboard"></i>
                </button>
            </td>
            <td>
                <div class="d-flex flex-wrap gap-1">
                    ${token.scopes.map(scope => `<span class="badge bg-info">${scope}</span>`).join('')}
                </div>
            </td>
            <td>
                <span class="badge ${token.is_active ? 'bg-success' : 'bg-secondary'}">
                    ${token.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>${formatDate(token.created_at)}</td>
            <td>${token.expires_at ? formatDate(token.expires_at) : 'Never'}</td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-outline-primary btn-sm" onclick="editToken(${token.id})" title="Edit">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-danger btn-sm" onclick="deleteToken(${token.id})" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Update token stats
function updateTokenStats(tokens) {
    if (!tokens) {
        document.getElementById('totalTokens').textContent = '0';
        document.getElementById('activeTokens').textContent = '0';
        document.getElementById('expiredTokens').textContent = '0';
        document.getElementById('tenantsWithTokens').textContent = '0';
        return;
    }
    
    const totalTokens = tokens.length;
    const activeTokens = tokens.filter(t => t.is_active).length;
    const expiredTokens = tokens.filter(t => t.expires_at && new Date(t.expires_at) < new Date()).length;
    const tenantsWithTokens = new Set(tokens.map(t => t.tenant_id)).size;
    
    document.getElementById('totalTokens').textContent = totalTokens;
    document.getElementById('activeTokens').textContent = activeTokens;
    document.getElementById('expiredTokens').textContent = expiredTokens;
    document.getElementById('tenantsWithTokens').textContent = tenantsWithTokens;
}

// Multi-step token creation variables
let currentTokenStep = 1;
let tokenFormData = {};

// Show create token modal
async function showCreateTokenModal() {
    try {
        // Reset form and step
        currentTokenStep = 1;
        tokenFormData = {};
        resetTokenForm();
        
        // Load tenants for the dropdown
        const tenantsResponse = await makeAuthenticatedRequest('http://localhost:8000/api/v1/admin/tenants/');
        if (tenantsResponse.ok) {
            const tenants = await tenantsResponse.json();
            const tenantSelect = document.getElementById('tokenTenant');
            tenantSelect.innerHTML = '<option value="">Select a tenant...</option>';
            tenants.forEach(tenant => {
                tenantSelect.innerHTML += `<option value="${tenant.id}">${tenant.name}</option>`;
            });
        }
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('createTokenModal'));
        modal.show();
        showTokenStep(1);
    } catch (error) {
        console.error('Error loading tenants for token modal:', error);
        showToast('Failed to load tenants', 'error');
    }
}

// Multi-step token creation functions
function showTokenStep(step) {
    // Hide all steps
    document.querySelectorAll('.token-step').forEach(el => el.classList.add('d-none'));
    
    // Show current step
    document.getElementById(`step${step}`).classList.remove('d-none');
    
    // Update buttons
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const createBtn = document.getElementById('createBtn');
    
    prevBtn.classList.toggle('d-none', step === 1);
    nextBtn.classList.toggle('d-none', step === 3 || step === 4);
    createBtn.classList.toggle('d-none', step !== 3);
    
    // Update button text
    if (step === 2) {
        nextBtn.innerHTML = 'Next <i class="bi bi-arrow-right"></i>';
    } else if (step === 3) {
        nextBtn.innerHTML = 'Create Token <i class="bi bi-check-circle"></i>';
    }
}

function nextStep() {
    if (currentTokenStep === 1) {
        if (validateStep1()) {
            saveStep1Data();
            currentTokenStep = 2;
            showTokenStep(2);
        }
    } else if (currentTokenStep === 2) {
        if (validateStep2()) {
            saveStep2Data();
            currentTokenStep = 3;
            showTokenStep(3);
            populateConfirmation();
        }
    } else if (currentTokenStep === 3) {
        createToken();
    }
}

function previousStep() {
    if (currentTokenStep > 1) {
        currentTokenStep--;
        showTokenStep(currentTokenStep);
    }
}

function validateStep1() {
    const name = document.getElementById('tokenName').value.trim();
    const tenant = document.getElementById('tokenTenant').value;
    
    if (!name) {
        showToast('Token name is required', 'error');
        return false;
    }
    
    if (!tenant) {
        showToast('Please select a tenant', 'error');
        return false;
    }
    
    return true;
}

function validateStep2() {
    const selectedScopes = getSelectedScopes();
    
    if (selectedScopes.length === 0) {
        showToast('Please select at least one scope', 'error');
        return false;
    }
    
    return true;
}

function saveStep1Data() {
    const tenantSelect = document.getElementById('tokenTenant');
    const selectedOption = tenantSelect.options[tenantSelect.selectedIndex];
    
    tokenFormData = {
        name: document.getElementById('tokenName').value.trim(),
        tenant_id: parseInt(document.getElementById('tokenTenant').value),
        tenant_name: selectedOption.text,
        expiry: document.getElementById('tokenExpiry').value,
        active: document.getElementById('tokenActive').checked
    };
}

function saveStep2Data() {
    tokenFormData.scopes = getSelectedScopes();
}

function getSelectedScopes() {
    const selectedScopes = [];
    document.querySelectorAll('input[type="checkbox"][id^="scope_"]:checked').forEach(checkbox => {
        selectedScopes.push(checkbox.value);
    });
    return selectedScopes;
}

function populateConfirmation() {
    document.getElementById('confirmName').textContent = tokenFormData.name;
    document.getElementById('confirmTenant').textContent = tokenFormData.tenant_name;
    document.getElementById('confirmStatus').textContent = tokenFormData.active ? 'Active' : 'Inactive';
    document.getElementById('confirmExpiry').textContent = tokenFormData.expiry || 'Never';
    
    const scopesList = document.getElementById('confirmScopes');
    scopesList.innerHTML = '';
    tokenFormData.scopes.forEach(scope => {
        const li = document.createElement('li');
        li.innerHTML = `<code>${scope}</code>`;
        scopesList.appendChild(li);
    });
}

function resetTokenForm() {
    document.getElementById('tokenName').value = '';
    document.getElementById('tokenTenant').selectedIndex = 0;
    document.getElementById('tokenExpiry').value = '';
    document.getElementById('tokenActive').checked = true;
    
    // Clear all scopes
    document.querySelectorAll('input[type="checkbox"][id^="scope_"]').forEach(checkbox => {
        checkbox.checked = false;
    });
}

function selectAllScopes() {
    document.querySelectorAll('input[type="checkbox"][id^="scope_"]').forEach(checkbox => {
        checkbox.checked = true;
    });
}

function clearAllScopes() {
    document.querySelectorAll('input[type="checkbox"][id^="scope_"]').forEach(checkbox => {
        checkbox.checked = false;
    });
}

// Load tenants for token modal
async function loadTenantsForTokenModal() {
    try {
        const response = await makeAuthenticatedRequest('http://localhost:8000/api/v1/admin/tenants/');
        if (response.ok) {
            const tenants = await response.json();
            const tenantSelect = document.getElementById('tokenTenant');
            tenantSelect.innerHTML = '<option value="">Select a tenant...</option>';
            tenants.forEach(tenant => {
                tenantSelect.innerHTML += `<option value="${tenant.id}">${tenant.name}</option>`;
            });
        }
    } catch (error) {
        console.error('Error loading tenants:', error);
        showToast('Failed to load tenants', 'error');
    }
}

// Create token
async function createToken() {
    try {
        const tokenData = {
            name: tokenFormData.name,
            tenant_id: tokenFormData.tenant_id,
            user_id: null, // No user required
            scopes: tokenFormData.scopes,
            is_active: tokenFormData.active,
            expires_at: tokenFormData.expiry ? new Date(tokenFormData.expiry).toISOString() : null
        };
        
        const response = await makeAuthenticatedRequest('http://localhost:8000/api/v1/tokens/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tokenData)
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // Show step 4 with the created token
            currentTokenStep = 4;
            showTokenStep(4);
            
            // Populate the final step
            document.getElementById('createdToken').value = result.token;
            document.getElementById('finalName').textContent = tokenFormData.name;
            document.getElementById('finalTenant').textContent = tokenFormData.tenant_name;
            document.getElementById('finalScopes').textContent = tokenFormData.scopes.join(', ');
            document.getElementById('finalStatus').textContent = tokenFormData.active ? 'Active' : 'Inactive';
            
            // Reload tokens
            loadTokens();
            
            showToast('Token created successfully!', 'success');
        } else {
            const error = await response.json();
            showToast(`Failed to create token: ${error.detail}`, 'error');
        }
    } catch (error) {
        console.error('Error creating token:', error);
        showToast('Failed to create token', 'error');
    }
}

// Token management functions
async function editToken(tokenId) {
    try {
        const response = await makeAuthenticatedRequest(`http://localhost:8000/api/v1/tokens/${tokenId}`);
        if (response.ok) {
            const token = await response.json();
            showEditTokenModal(token);
        } else {
            showToast('Failed to load token details', 'error');
        }
    } catch (error) {
        console.error('Error loading token:', error);
        showToast('Failed to load token details', 'error');
    }
}

async function deleteToken(tokenId) {
    if (!confirm('Are you sure you want to delete this token? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await makeAuthenticatedRequest(`http://localhost:8000/api/v1/tokens/${tokenId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Token deleted successfully', 'success');
            loadTokens();
        } else {
            showToast('Failed to delete token', 'error');
        }
    } catch (error) {
        console.error('Error deleting token:', error);
        showToast('Failed to delete token', 'error');
    }
}

// Placeholder for edit token modal (to be implemented)
function showEditTokenModal(token) {
    showToast('Token editing coming soon...', 'info');
}

function copyToken() {
    const tokenInput = document.getElementById('createdToken');
    tokenInput.select();
    tokenInput.setSelectionRange(0, 99999); // For mobile devices
    document.execCommand('copy');
    showToast('Token copied to clipboard!', 'success');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Token copied to clipboard!', 'success');
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Token copied to clipboard!', 'success');
    });
}

function showEditTokenModal(token) {
    // Implementation for editing token (scopes only)
    showToast('Token editing coming soon...', 'info');
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

// Global pagination state
let currentPage = 1;
let pageSize = 25;
let totalRecords = 0;

function loadApiCallsDirect(page = 1, size = pageSize) {
    const token = localStorage.getItem('unifiedAccessToken');
    
    if (!token) {
        const container = document.getElementById('api-calls-content-direct');
        if (container) {
            container.innerHTML = '<div class="no-data" style="text-align: center; padding: 40px; color: #666; font-style: italic;">Authentication required. Please log in.</div>';
        }
        return;
    }
    
    const container = document.getElementById('api-calls-content-direct');
    
    if (!container) {
        return;
    }
    
    // Update global state
    currentPage = page;
    pageSize = size;
    
    const offset = (page - 1) * size;
    const url = `http://localhost:8000/api/v1/admin/api-calls/?limit=${size}&offset=${offset}`;
    
    container.innerHTML = '<div class="loading" style="text-align: center; padding: 40px; color: #666;">Loading API calls...</div>';
    
    fetch(url, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        // Handle the new paginated response format
        let apiCalls, total;
        if (data.items && data.total !== undefined) {
            // New paginated format
            apiCalls = data.items;
            total = data.total;
        } else if (Array.isArray(data)) {
            // Fallback for array format
            apiCalls = data;
            total = data.length;
        } else {
            // Fallback for other formats
            apiCalls = data.items || data.results || [];
            total = data.total || data.count || apiCalls.length;
        }
        totalRecords = total;
        displayApiCallsDirect(apiCalls, total, page, size);
    })
    .catch(error => {
        if (container) {
            container.innerHTML = '<div class="no-data" style="text-align: center; padding: 40px; color: #666; font-style: italic;">Error loading API calls: ' + error.message + '</div>';
        }
    });
}

function displayApiCallsDirect(apiCalls, total, page, size) {
    const container = document.getElementById('api-calls-content-direct');
    
    if (!container) {
        return;
    }
    
    if (!apiCalls || apiCalls.length === 0) {
        container.innerHTML = '<div class="no-data" style="text-align: center; padding: 40px; color: #666; font-style: italic;">No API calls found</div>';
        return;
    }
    
    // Calculate pagination info
    const totalPages = Math.ceil(total / size);
    const startRecord = (page - 1) * size + 1;
    const endRecord = Math.min(page * size, total);
    
    // Build pagination controls
    let paginationHtml = '<div class="d-flex justify-content-between align-items-center mb-3">';
    paginationHtml += '<div class="text-muted">';
    paginationHtml += `Showing ${startRecord} to ${endRecord} of ${total} records`;
    paginationHtml += '</div>';
    paginationHtml += '<div class="d-flex align-items-center gap-2">';
    
    // Page size selector
    paginationHtml += '<div class="d-flex align-items-center gap-2">';
    paginationHtml += '<label for="pageSize" class="form-label mb-0">Records per page:</label>';
    paginationHtml += '<select id="pageSize" class="form-select form-select-sm" style="width: auto;" onchange="changePageSize(this.value)">';
    paginationHtml += `<option value="10" ${size === 10 ? 'selected' : ''}>10</option>`;
    paginationHtml += `<option value="25" ${size === 25 ? 'selected' : ''}>25</option>`;
    paginationHtml += `<option value="50" ${size === 50 ? 'selected' : ''}>50</option>`;
    paginationHtml += `<option value="100" ${size === 100 ? 'selected' : ''}>100</option>`;
    paginationHtml += '</select>';
    paginationHtml += '</div>';
    
    // Navigation buttons (only show if multiple pages)
    if (totalPages > 1) {
        paginationHtml += '<nav><ul class="pagination pagination-sm mb-0">';
        
        // Previous button
        const prevDisabled = page <= 1 ? 'disabled' : '';
        paginationHtml += `<li class="page-item ${prevDisabled}">`;
        paginationHtml += `<a class="page-link" href="#" onclick="changePage(${page - 1})" ${prevDisabled}>Previous</a>`;
        paginationHtml += '</li>';
        
        // Page numbers
        const startPage = Math.max(1, page - 2);
        const endPage = Math.min(totalPages, page + 2);
        
        if (startPage > 1) {
            paginationHtml += '<li class="page-item"><a class="page-link" href="#" onclick="changePage(1)">1</a></li>';
            if (startPage > 2) {
                paginationHtml += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const active = i === page ? 'active' : '';
            paginationHtml += `<li class="page-item ${active}">`;
            paginationHtml += `<a class="page-link" href="#" onclick="changePage(${i})">${i}</a>`;
            paginationHtml += '</li>';
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHtml += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
            paginationHtml += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(${totalPages})">${totalPages}</a></li>`;
        }
        
        // Next button
        const nextDisabled = page >= totalPages ? 'disabled' : '';
        paginationHtml += `<li class="page-item ${nextDisabled}">`;
        paginationHtml += `<a class="page-link" href="#" onclick="changePage(${page + 1})" ${nextDisabled}>Next</a>`;
        paginationHtml += '</li>';
        
        paginationHtml += '</ul></nav>';
    }
    
    paginationHtml += '</div></div>';
    
    // Use Bootstrap table classes for better styling
    let html = paginationHtml;
    html += '<div class="table-responsive"><table class="table table-hover table-striped">';
    html += '<thead class="table-light"><tr>';
    html += '<th>Time</th>';
    html += '<th>Method</th>';
    html += '<th>Endpoint</th>';
    html += '<th>Status</th>';
    html += '<th>Duration</th>';
    html += '<th>Size</th>';
    html += '<th>Tenant</th>';
    html += '<th>User</th>';
    html += '</tr></thead>';
    html += '<tbody>';
    
    apiCalls.forEach(call => {
        const created_at = call.created_at ? new Date(call.created_at).toLocaleString() : 'N/A';
        const method = call.method || 'N/A';
        const endpoint = call.endpoint || 'N/A';
        const response_status = call.response_status || 'N/A';
        const processing_time = call.processing_time ? `${(call.processing_time * 1000).toFixed(1)}ms` : 'N/A';
        const response_size = call.response_size ? formatBytes(call.response_size) : 'N/A';
        const tenant_name = call.tenant_name || call.tenant_id || 'N/A';
        const user_email = call.user_email || call.user_id || 'N/A';
        
        // Determine status class
        let statusClass = '';
        if (response_status >= 200 && response_status < 300) statusClass = 'text-success fw-bold';
        else if (response_status >= 400 && response_status < 500) statusClass = 'text-warning fw-bold';
        else if (response_status >= 500) statusClass = 'text-danger fw-bold';
        
        html += `<tr>
            <td>${created_at}</td>
            <td><strong>${method}</strong></td>
            <td>${endpoint}</td>
            <td class="${statusClass}">${response_status}</td>
            <td>${processing_time}</td>
            <td>${response_size}</td>
            <td>${tenant_name}</td>
            <td>${user_email}</td>
        </tr>`;
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Listen for messages from iframe to resize it (legacy - no longer used)
window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'resize-iframe') {
        // Handle legacy resize message
        // No longer needed since we're using direct integration
    }
});

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

// Pagination helper functions
function changePage(page) {
    if (page >= 1) {
        loadApiCallsDirect(page, pageSize);
    }
}

function changePageSize(size) {
    const newSize = parseInt(size);
    if (newSize > 0) {
        loadApiCallsDirect(1, newSize);
    }
}

// Token pagination helper functions
function changeTokenPage(page) {
    if (page >= 1) {
        loadTokens(page, tokenPageSize);
    }
}

function changeTokenPageSize(size) {
    const newSize = parseInt(size);
    if (newSize > 0) {
        loadTokens(1, newSize);
    }
}

// Refresh API tracking data
function refreshApiTracking() {
    loadApiCallsDirect(currentPage, pageSize);
} 