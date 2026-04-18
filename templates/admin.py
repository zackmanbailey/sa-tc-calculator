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

        .role-god_mode { background: rgba(239, 68, 68, 0.25); color: #FCA5A5; border: 1px solid #EF4444; }
        .role-admin { background: rgba(245, 158, 11, 0.2); color: #F59E0B; border: 1px solid #F59E0B; }
        .role-project_manager { background: rgba(168, 85, 247, 0.2); color: #C4B5FD; border: 1px solid #A855F7; }
        .role-estimator { background: rgba(30, 64, 175, 0.2); color: #60a5fa; border: 1px solid #60a5fa; }
        .role-sales { background: rgba(236, 72, 153, 0.2); color: #F9A8D4; border: 1px solid #EC4899; }
        .role-purchasing { background: rgba(251, 146, 60, 0.2); color: #FDBA74; border: 1px solid #FB923C; }
        .role-inventory_manager { background: rgba(20, 184, 166, 0.2); color: #5EEAD4; border: 1px solid #14B8A6; }
        .role-accounting { background: rgba(99, 102, 241, 0.2); color: #A5B4FC; border: 1px solid #6366F1; }
        .role-shop_foreman { background: rgba(34, 197, 94, 0.2); color: #86efac; border: 1px solid #22C55E; }
        .role-qc_inspector { background: rgba(6, 182, 212, 0.2); color: #67E8F9; border: 1px solid #06B6D4; }
        .role-engineer { background: rgba(59, 130, 246, 0.2); color: #93C5FD; border: 1px solid #3B82F6; }
        .role-roll_forming_operator { background: rgba(132, 204, 22, 0.2); color: #BEF264; border: 1px solid #84CC16; }
        .role-welder { background: rgba(249, 115, 22, 0.2); color: #FDBA74; border: 1px solid #F97316; }
        .role-shipping_coordinator { background: rgba(14, 165, 233, 0.2); color: #7DD3FC; border: 1px solid #0EA5E9; }
        .role-laborer { background: rgba(107, 114, 128, 0.2); color: #D1D5DB; border: 1px solid #6B7280; }
        .role-field_crew { background: rgba(101, 163, 13, 0.2); color: #BEF264; border: 1px solid #65A30D; }
        .role-safety_officer { background: rgba(234, 179, 8, 0.2); color: #FDE047; border: 1px solid #EAB308; }
        .role-customer { background: rgba(148, 163, 184, 0.15); color: #CBD5E1; border: 1px solid #94A3B8; }
        .role-shop { background: rgba(34, 197, 94, 0.2); color: #86efac; border: 1px solid #86efac; }
        .role-viewer { background: rgba(107, 114, 128, 0.2); color: #d1d5db; border: 1px solid #6b7280; }
        .role-tc_limited { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid #fbbf24; }

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
                            <select id="newRole" multiple required size="6" style="min-height:140px;">
                                <optgroup label="Management">
                                    <option value="god_mode">God Mode (Full Access)</option>
                                    <option value="admin">Admin</option>
                                    <option value="project_manager">Project Manager</option>
                                </optgroup>
                                <optgroup label="Office">
                                    <option value="estimator">Estimator</option>
                                    <option value="sales">Sales / Business Dev</option>
                                    <option value="purchasing">Purchasing</option>
                                    <option value="accounting">Accounting</option>
                                    <option value="engineer">Engineer / Detailer</option>
                                </optgroup>
                                <optgroup label="Shop Floor">
                                    <option value="shop_foreman">Shop Foreman</option>
                                    <option value="qc_inspector">QA/QC Inspector</option>
                                    <option value="roll_forming_operator">Roll Forming Operator</option>
                                    <option value="welder">Welder</option>
                                    <option value="laborer">Laborer</option>
                                    <option value="inventory_manager">Inventory Manager</option>
                                    <option value="shipping_coordinator">Shipping Coordinator</option>
                                </optgroup>
                                <optgroup label="Field &amp; Safety">
                                    <option value="field_crew">Field Crew</option>
                                    <option value="safety_officer">Safety Officer</option>
                                </optgroup>
                                <optgroup label="External">
                                    <option value="customer">Customer Portal</option>
                                </optgroup>
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

    <!-- Edit User Modal -->
    <div id="editUserModal" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);z-index:1000;align-items:center;justify-content:center;">
        <div style="background:#1E293B;border:1px solid #334155;border-radius:12px;padding:28px;width:420px;max-width:90vw;">
            <h3 style="color:#FFF;margin-bottom:16px;font-size:18px;">Edit User</h3>
            <div id="editUserError" style="display:none;background:#7F1D1D;color:#FCA5A5;padding:10px;border-radius:8px;margin-bottom:12px;font-size:13px;"></div>
            <div id="editUserSuccess" style="display:none;background:#14532D;color:#6EE7B7;padding:10px;border-radius:8px;margin-bottom:12px;font-size:13px;"></div>
            <input type="hidden" id="editUsername">
            <div style="margin-bottom:12px;">
                <label style="display:block;font-size:12px;color:#94A3B8;margin-bottom:4px;">Username</label>
                <div id="editUsernameDisplay" style="padding:8px 12px;background:#0F172A;border:1px solid #334155;border-radius:6px;color:#64748B;font-size:14px;"></div>
            </div>
            <div style="margin-bottom:12px;">
                <label style="display:block;font-size:12px;color:#94A3B8;margin-bottom:4px;">Display Name</label>
                <input id="editDisplayName" style="width:100%;padding:8px 12px;background:#0F172A;border:1px solid #334155;border-radius:6px;color:#FFF;font-size:14px;">
            </div>
            <div style="margin-bottom:12px;">
                <label style="display:block;font-size:12px;color:#94A3B8;margin-bottom:4px;">Role</label>
                <select id="editRole" multiple size="6" style="width:100%;padding:8px 12px;background:#0F172A;border:1px solid #334155;border-radius:6px;color:#FFF;font-size:14px;min-height:140px;">
                    <optgroup label="Management">
                        <option value="god_mode">God Mode (Full Access)</option>
                        <option value="admin">Admin</option>
                        <option value="project_manager">Project Manager</option>
                    </optgroup>
                    <optgroup label="Office">
                        <option value="estimator">Estimator</option>
                        <option value="sales">Sales / Business Dev</option>
                        <option value="purchasing">Purchasing</option>
                        <option value="accounting">Accounting</option>
                        <option value="engineer">Engineer / Detailer</option>
                    </optgroup>
                    <optgroup label="Shop Floor">
                        <option value="shop_foreman">Shop Foreman</option>
                        <option value="qc_inspector">QA/QC Inspector</option>
                        <option value="roll_forming_operator">Roll Forming Operator</option>
                        <option value="welder">Welder</option>
                        <option value="laborer">Laborer</option>
                        <option value="inventory_manager">Inventory Manager</option>
                        <option value="shipping_coordinator">Shipping Coordinator</option>
                    </optgroup>
                    <optgroup label="Field &amp; Safety">
                        <option value="field_crew">Field Crew</option>
                        <option value="safety_officer">Safety Officer</option>
                    </optgroup>
                    <optgroup label="External">
                        <option value="customer">Customer Portal</option>
                    </optgroup>
                </select>
            </div>
            <div style="margin-bottom:16px;">
                <label style="display:block;font-size:12px;color:#94A3B8;margin-bottom:4px;">New Password <span style="color:#64748B;">(leave blank to keep current)</span></label>
                <input id="editPassword" type="password" placeholder="Enter new password" style="width:100%;padding:8px 12px;background:#0F172A;border:1px solid #334155;border-radius:6px;color:#FFF;font-size:14px;">
            </div>
            <div style="display:flex;gap:10px;justify-content:flex-end;">
                <button onclick="closeEditModal()" style="padding:8px 18px;background:#334155;color:#E2E8F0;border:none;border-radius:6px;cursor:pointer;font-size:14px;">Cancel</button>
                <button id="saveEditBtn" onclick="saveEditUser()" style="padding:8px 18px;background:#1E40AF;color:#FFF;border:none;border-radius:6px;cursor:pointer;font-size:14px;font-weight:600;">Save Changes</button>
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
                    const usersObj = data.users || {};
                    // Backend returns {username: {display_name, role, created}} object
                    const users = Array.isArray(usersObj) ? usersObj :
                        Object.entries(usersObj).map(([username, info]) => ({
                            username,
                            display_name: info.display_name || '',
                            role: info.role || 'viewer',
                            roles: info.roles || (info.role ? [info.role] : ['viewer']),
                            created_at: info.created || ''
                        }));
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

            tbody.innerHTML = users.map(user => {
                const roleList = user.roles || (user.role ? [user.role] : []);
                const roleStr = roleList.join(',');
                const roleBadges = roleList.map(r => `<span class="role-badge role-${r}">${escapeHtml(r)}</span>`).join(' ');
                return `
                <tr>
                    <td><strong>${escapeHtml(user.username)}</strong></td>
                    <td>${escapeHtml(user.display_name || '-')}</td>
                    <td>${roleBadges}</td>
                    <td>${formatDate(user.created_at)}</td>
                    <td>
                        <button class="btn btn-primary" style="margin-right:6px;padding:6px 14px;font-size:13px;" onclick="openEditUser('${escapeHtml(user.username)}','${escapeHtml(user.display_name)}','${escapeHtml(roleStr)}')">Edit</button>
                        <button class="btn btn-danger" style="padding:6px 14px;font-size:13px;" onclick="deleteUser('${escapeHtml(user.username)}')">Delete</button>
                    </td>
                </tr>
                `;
            }).join('');
        }

        function addUser() {
            const username = document.getElementById('newUsername').value.trim();
            const displayName = document.getElementById('newDisplayName').value.trim();
            const password = document.getElementById('newPassword').value;
            const roles = Array.from(document.getElementById('newRole').selectedOptions).map(o => o.value);

            const errorDiv = document.getElementById('addUserError');
            const successDiv = document.getElementById('addUserSuccess');
            errorDiv.classList.remove('show');
            successDiv.classList.remove('show');

            if (!username || !displayName || !password || roles.length === 0) {
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
                    roles: roles
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

            fetch('/auth/users/delete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username})
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

        function openEditUser(username, displayName, role) {
            document.getElementById('editUsername').value = username;
            document.getElementById('editUsernameDisplay').textContent = username;
            document.getElementById('editDisplayName').value = displayName;
            // Support multi-role: role may be comma-separated or a single value
            const editSelect = document.getElementById('editRole');
            const userRoles = (role || '').split(',').map(r => r.trim());
            Array.from(editSelect.options).forEach(opt => {
                opt.selected = userRoles.includes(opt.value);
            });
            document.getElementById('editPassword').value = '';
            document.getElementById('editUserError').style.display = 'none';
            document.getElementById('editUserSuccess').style.display = 'none';
            const modal = document.getElementById('editUserModal');
            modal.style.display = 'flex';
        }

        function closeEditModal() {
            document.getElementById('editUserModal').style.display = 'none';
        }

        function saveEditUser() {
            const username = document.getElementById('editUsername').value;
            const displayName = document.getElementById('editDisplayName').value.trim();
            const roles = Array.from(document.getElementById('editRole').selectedOptions).map(o => o.value);
            const password = document.getElementById('editPassword').value;
            const errDiv = document.getElementById('editUserError');
            const okDiv = document.getElementById('editUserSuccess');
            errDiv.style.display = 'none';
            okDiv.style.display = 'none';

            if (!displayName) {
                errDiv.textContent = 'Display name is required';
                errDiv.style.display = 'block';
                return;
            }
            if (roles.length === 0) {
                errDiv.textContent = 'At least one role is required';
                errDiv.style.display = 'block';
                return;
            }

            const payload = { username, display_name: displayName, roles };
            if (password) payload.password = password;

            const btn = document.getElementById('saveEditBtn');
            btn.disabled = true;
            btn.textContent = 'Saving...';

            fetch('/auth/users/edit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            })
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    okDiv.textContent = 'User updated successfully';
                    okDiv.style.display = 'block';
                    loadUsers();
                    setTimeout(closeEditModal, 800);
                } else {
                    errDiv.textContent = data.error || 'Failed to update user';
                    errDiv.style.display = 'block';
                }
            })
            .catch(err => {
                errDiv.textContent = 'Network error: ' + err.message;
                errDiv.style.display = 'block';
            })
            .finally(() => {
                btn.disabled = false;
                btn.textContent = 'Save Changes';
            });
        }

        // Close modal on backdrop click
        document.getElementById('editUserModal').addEventListener('click', function(e) {
            if (e.target === this) closeEditModal();
        });
    </script>
</body>
</html>
"""
