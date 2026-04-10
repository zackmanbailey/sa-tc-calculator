ADMIN_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge - User Management</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #0F172A;
            color: #e5e7eb;
        }

        /* Navigation Bar */
        .navbar {
            background: linear-gradient(to bottom, rgba(30, 41, 59, 0.98), rgba(15, 23, 42, 0.95));
            border-bottom: 1px solid #1E40AF;
            padding: 0 24px;
            height: 64px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        .nav-left {
            display: flex;
            align-items: center;
            gap: 40px;
        }

        .nav-logo {
            font-size: 18px;
            font-weight: 900;
            letter-spacing: 1.5px;
            color: #F59E0B;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .nav-links {
            display: flex;
            gap: 24px;
            align-items: center;
        }

        .nav-links a {
            color: #d1d5db;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
            padding: 8px 12px;
            border-radius: 4px;
        }

        .nav-links a:hover {
            color: #F59E0B;
            background: rgba(245, 158, 11, 0.1);
        }

        .nav-links a.active {
            color: #F59E0B;
            border-bottom: 2px solid #F59E0B;
        }

        .nav-right {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .user-badge {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 12px;
            background: rgba(30, 64, 175, 0.2);
            border: 1px solid #1E40AF;
            border-radius: 6px;
            font-size: 13px;
        }

        .user-avatar {
            width: 32px;
            height: 32px;
            background: #1E40AF;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 14px;
        }

        .logout-btn {
            background: #dc2626;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .logout-btn:hover {
            background: #991b1b;
            box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
        }

        /* Main Content */
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 24px;
        }

        .page-header {
            margin-bottom: 40px;
        }

        .page-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
            color: #f3f4f6;
        }

        .page-subtitle {
            font-size: 14px;
            color: #9ca3af;
        }

        /* Add User Section */
        .section {
            margin-bottom: 48px;
        }

        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #f3f4f6;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .section-title::before {
            content: '';
            width: 4px;
            height: 20px;
            background: #F59E0B;
            border-radius: 2px;
        }

        .form-card {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid #1E40AF;
            border-radius: 8px;
            padding: 28px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }

        .form-row.full {
            grid-template-columns: 1fr;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-group label {
            font-size: 13px;
            font-weight: 600;
            color: #d1d5db;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .form-group input,
        .form-group select {
            padding: 12px 14px;
            border: 1px solid #374151;
            border-radius: 6px;
            background: rgba(15, 23, 42, 0.8);
            color: #f3f4f6;
            font-size: 14px;
            transition: all 0.3s ease;
            font-family: inherit;
        }

        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #1E40AF;
            background: rgba(15, 23, 42, 0.95);
            box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
        }

        .form-group input::placeholder {
            color: #6b7280;
        }

        .form-actions {
            display: flex;
            gap: 12px;
            margin-top: 24px;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .btn-primary {
            background: #1E40AF;
            color: white;
            flex: 1;
        }

        .btn-primary:hover {
            background: #1e3a8a;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
        }

        .btn-primary:disabled {
            background: #4b5563;
            cursor: not-allowed;
            opacity: 0.6;
        }

        .btn-secondary {
            background: rgba(107, 114, 128, 0.2);
            color: #d1d5db;
            border: 1px solid #374151;
        }

        .btn-secondary:hover {
            background: rgba(107, 114, 128, 0.3);
            border-color: #4b5563;
        }

        .btn-danger {
            background: #dc2626;
            color: white;
            padding: 8px 12px;
            font-size: 12px;
        }

        .btn-danger:hover {
            background: #991b1b;
        }

        /* Users Table */
        .table-container {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid #1E40AF;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        thead {
            background: rgba(30, 64, 175, 0.2);
            border-bottom: 2px solid #1E40AF;
        }

        th {
            padding: 16px 20px;
            text-align: left;
            font-size: 12px;
            font-weight: 700;
            color: #F59E0B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        td {
            padding: 16px 20px;
            border-bottom: 1px solid #1f2937;
            font-size: 14px;
            color: #d1d5db;
        }

        tbody tr:hover {
            background: rgba(30, 64, 175, 0.1);
        }

        .role-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            width: fit-content;
        }

        .role-admin {
            background: rgba(245, 158, 11, 0.2);
            color: #F59E0B;
            border: 1px solid #F59E0B;
        }

        .role-estimator {
            background: rgba(30, 64, 175, 0.2);
            color: #60a5fa;
            border: 1px solid #60a5fa;
        }

        .role-shop {
            background: rgba(34, 197, 94, 0.2);
            color: #86efac;
            border: 1px solid #86efac;
        }

        .role-viewer {
            background: rgba(107, 114, 128, 0.2);
            color: #d1d5db;
            border: 1px solid #6b7280;
        }

        .role-tc_limited {
            background: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid #fbbf24;
        }

        .empty-state {
            text-align: center;
            padding: 48px 20px;
            color: #9ca3af;
        }

        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }

        .empty-state-text {
            font-size: 16px;
            margin-bottom: 8px;
        }

        .success-message {
            background: rgba(34, 197, 94, 0.2);
            border: 1px solid #22c55e;
            color: #86efac;
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-size: 14px;
            display: none;
        }

        .success-message.show {
            display: block;
        }

        .error-message {
            background: rgba(220, 38, 38, 0.2);
            border: 1px solid #dc2626;
            color: #fca5a5;
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-size: 14px;
            display: none;
        }

        .error-message.show {
            display: block;
        }

        @media (max-width: 768px) {
            .nav-links {
                gap: 12px;
            }

            .form-row {
                grid-template-columns: 1fr;
            }

            .page-title {
                font-size: 24px;
            }

            table {
                font-size: 12px;
            }

            th, td {
                padding: 12px 16px;
            }
        }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar">
        <div class="nav-left">
            <div class="nav-logo">TITANFORGE</div>
            <div class="nav-links">
                <a href="/">Dashboard</a>
                <a href="/sa">Structures America Estimator</a>
                <a href="/tc">Titan Carports Estimator</a>
                <a href="/inventory">Inventory</a>
            </div>
        </div>
        <div class="nav-right">
            <div class="user-badge">
                <div class="user-avatar" id="userInitial">A</div>
                <span id="userName">Admin</span>
            </div>
            <button class="logout-btn" onclick="logout()">Logout</button>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="main-container">
        <div class="page-header">
            <h1 class="page-title">User Management</h1>
            <p class="page-subtitle">Manage system users, roles, and permissions</p>
        </div>

        <div class="section">
            <h2 class="section-title">Add New User</h2>
            <div class="form-card">
                <div class="error-message" id="addUserError"></div>
                <div class="success-message" id="addUserSuccess"></div>

                <form id="addUserForm">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="newUsername">Username</label>
                            <input
                                type="text"
                                id="newUsername"
                                placeholder="e.g., jsmith"
                                required
                            >
                        </div>
                        <div class="form-group">
                            <label for="newDisplayName">Display Name</label>
                            <input
                                type="text"
                                id="newDisplayName"
                                placeholder="e.g., John Smith"
                                required
                            >
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="newPassword">Password</label>
                            <input
                                type="password"
                                id="newPassword"
                                placeholder="Enter initial password"
                                required
                            >
                        </div>
                        <div class="form-group">
                            <label for="newRole">Role</label>
                            <select id="newRole" required>
                                <option value="">Select a role</option>
                                <option value="admin">Admin</option>
                                <option value="estimator">Estimator</option>
                                <option value="shop">Shop</option>
                                <option value="viewer">Viewer</option>
                                <option value="tc_limited">TC Limited</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary" id="addUserBtn">Add User</button>
                        <button type="reset" class="btn btn-secondary">Clear</button>
                    </div>
                </form>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Current Users</h2>
            <div class="table-container">
                <table id="usersTable">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Display Name</th>
                            <th>Role</th>
                            <th>Created Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="usersTableBody">
                        <tr>
                            <td colspan="5" class="empty-state">
                                <div class="empty-state-icon">⏳</div>
                                <div class="empty-state-text">Loading users...</div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            loadUsers();
            setupFormHandlers();
        });

        function setupFormHandlers() {
            const addUserForm = document.getElementById('addUserForm');
            addUserForm.addEventListener('submit', function(e) {
                e.preventDefault();
                addUser();
            });
        }

        function loadUsers() {
            fetch('/auth/users')
                .then(response => {
                    if (!response.ok) throw new Error('Failed to load users');
                    return response.json();
                })
                .then(data => {
                    const users = data.users || [];
                    renderUsersTable(users);
                })
                .catch(error => {
                    console.error('Error loading users:', error);
                    const tbody = document.getElementById('usersTableBody');
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="5" class="empty-state">
                                <div class="empty-state-icon">⚠️</div>
                                <div class="empty-state-text">Failed to load users</div>
                            </td>
                        </tr>
                    `;
                });
        }

        function renderUsersTable(users) {
            const tbody = document.getElementById('usersTableBody');

            if (users.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="5" class="empty-state">
                            <div class="empty-state-icon">👥</div>
                            <div class="empty-state-text">No users yet. Add one to get started!</div>
                        </td>
                    </tr>
                `;
                return;
            }

            tbody.innerHTML = users.map(user => `
                <tr>
                    <td><strong>${escapeHtml(user.username)}</strong></td>
                    <td>${escapeHtml(user.display_name || '-')}</td>
                    <td><span class="role-badge role-${user.role}">${escapeHtml(user.role)}</span></td>
                    <td>${formatDate(user.created_at)}</td>
                    <td>
                        <button class="btn btn-danger" onclick="deleteUser('${escapeHtml(user.username)}')">Delete</button>
                    </td>
                </tr>
            `).join('');
        }

        function addUser() {
            const username = document.getElementById('newUsername').value.trim();
            const displayName = document.getElementById('newDisplayName').value.trim();
            const password = document.getElementById('newPassword').value;
            const role = document.getElementById('newRole').value;

            const errorDiv = document.getElementById('addUserError');
            const successDiv = document.getElementById('addUserSuccess');
            errorDiv.classList.remove('show');
            successDiv.classList.remove('show');

            if (!username || !displayName || !password || !role) {
                errorDiv.textContent = 'Please fill in all fields';
                errorDiv.classList.add('show');
                return;
            }

            const addUserBtn = document.getElementById('addUserBtn');
            addUserBtn.disabled = true;
            addUserBtn.textContent = 'Adding...';

            fetch('/auth/users/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    display_name: displayName,
                    password: password,
                    role: role
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Failed to add user');
                    });
                }
                return response.json();
            })
            .then(data => {
                successDiv.textContent = 'User added successfully!';
                successDiv.classList.add('show');
                document.getElementById('addUserForm').reset();
                setTimeout(() => {
                    successDiv.classList.remove('show');
                }, 3000);
                loadUsers();
            })
            .catch(error => {
                errorDiv.textContent = error.message || 'Failed to add user';
                errorDiv.classList.add('show');
            })
            .finally(() => {
                addUserBtn.disabled = false;
                addUserBtn.textContent = 'Add User';
            });
        }

        function deleteUser(username) {
            if (!confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) {
                return;
            }

            fetch(`/auth/users/${encodeURIComponent(username)}`, {
                method: 'DELETE'
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Failed to delete user');
                    });
                }
                return response.json();
            })
            .then(data => {
                loadUsers();
            })
            .catch(error => {
                alert('Error deleting user: ' + (error.message || 'Unknown error'));
            });
        }

        function logout() {
            if (confirm('Are you sure you want to logout?')) {
                window.location.href = '/auth/logout';
            }
        }

        function formatDate(dateString) {
            if (!dateString) return '-';
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
"""
