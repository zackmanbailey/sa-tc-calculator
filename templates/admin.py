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

        .role-select {
            background: rgba(255,255,255,0.08);
            color: #F59E0B;
            border: 1px solid rgba(245, 158, 11, 0.4);
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            cursor: pointer;
            min-width: 160px;
        }
        .role-select:hover { border-color: #F59E0B; }
        .role-select:disabled { opacity: 0.5; cursor: not-allowed; }
        .role-select option { background: #1a1a2e; color: #e2e8f0; }

        /* Multi-role chips */
        .role-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            align-items: center;
        }
        .role-chip {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            background: rgba(245, 158, 11, 0.15);
            color: #F59E0B;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .role-chip.primary {
            background: rgba(30, 64, 175, 0.3);
            color: #60a5fa;
            border-color: rgba(96, 165, 250, 0.4);
        }
        .edit-roles-btn {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            background: rgba(255,255,255,0.06);
            color: rgba(255,255,255,0.5);
            border: 1px dashed rgba(255,255,255,0.2);
            cursor: pointer;
            transition: all 0.2s;
        }
        .edit-roles-btn:hover {
            background: rgba(245, 158, 11, 0.1);
            color: #F59E0B;
            border-color: rgba(245, 158, 11, 0.4);
        }

        /* Role picker modal */
        .role-modal-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.7);
            z-index: 9999;
            align-items: center;
            justify-content: center;
        }
        .role-modal-overlay.show { display: flex; }
        .role-modal {
            background: #1e293b;
            border: 1px solid #1E40AF;
            border-radius: 12px;
            padding: 28px;
            width: 480px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        .role-modal h3 {
            font-size: 18px;
            color: #f3f4f6;
            margin-bottom: 4px;
        }
        .role-modal .modal-subtitle {
            font-size: 13px;
            color: #9ca3af;
            margin-bottom: 20px;
        }
        .role-checkbox-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 24px;
        }
        .role-checkbox-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid #374151;
            cursor: pointer;
            transition: all 0.2s;
        }
        .role-checkbox-item:hover { background: rgba(245, 158, 11, 0.08); border-color: #4b5563; }
        .role-checkbox-item.checked { background: rgba(245, 158, 11, 0.12); border-color: rgba(245, 158, 11, 0.4); }
        .role-checkbox-item input[type="checkbox"] {
            accent-color: #F59E0B;
            width: 16px;
            height: 16px;
        }
        .role-checkbox-item label {
            font-size: 12px;
            font-weight: 500;
            color: #d1d5db;
            cursor: pointer;
            text-transform: capitalize;
        }
        .role-modal-actions {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
        }
        .role-modal-actions .btn { padding: 10px 20px; font-size: 13px; }

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
                            <label>Roles (select one or more)</label>
                            <div id="newRoleCheckboxes" class="role-checkbox-grid">
                                <!-- filled by JS -->
                            </div>
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
                            <th>Roles</th>
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

        <!-- Pending Registrations Section -->
        <div class="section">
            <h2 class="section-title">Pending Access Requests <span id="pendingCount" style="background:#F59E0B;color:#0F172A;padding:2px 8px;border-radius:10px;font-size:13px;margin-left:8px;display:none;">0</span></h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Username</th>
                            <th>Email / Phone</th>
                            <th>Company Role</th>
                            <th>Submitted</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="pendingTableBody">
                        <tr><td colspan="6" class="empty-state">
                            <div class="empty-state-text">Loading...</div>
                        </td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Approve Modal -->
    <div class="role-modal-overlay" id="approveModalOverlay" onclick="if(event.target===this)closeApproveModal()">
        <div class="role-modal">
            <h3 id="approveModalTitle">Approve Registration</h3>
            <div class="modal-subtitle">Select roles to assign to this user</div>
            <div class="role-checkbox-grid" id="approveRoleCheckboxes"></div>
            <div class="form-group" style="margin-bottom:20px;">
                <label style="font-size:12px;font-weight:600;color:#d1d5db;margin-bottom:6px;display:block;">Notes (optional)</label>
                <input type="text" id="approveNotes" placeholder="Approval notes..." style="width:100%;padding:8px 12px;border:1px solid #374151;border-radius:6px;background:rgba(15,23,42,0.8);color:#f3f4f6;font-size:13px;">
            </div>
            <div class="role-modal-actions">
                <button class="btn btn-secondary" onclick="closeApproveModal()">Cancel</button>
                <button class="btn btn-primary" onclick="confirmApprove()">Approve</button>
            </div>
        </div>
    </div>

    <!-- Role Picker Modal -->
    <div class="role-modal-overlay" id="roleModalOverlay" onclick="if(event.target===this)closeRoleModal()">
        <div class="role-modal">
            <h3 id="roleModalTitle">Edit Roles</h3>
            <div class="modal-subtitle" id="roleModalSubtitle">Select one or more roles for this user</div>
            <div class="role-checkbox-grid" id="roleModalCheckboxes"></div>
            <div class="role-modal-actions">
                <button class="btn btn-secondary" onclick="closeRoleModal()">Cancel</button>
                <button class="btn btn-primary" onclick="saveRoles()">Save Roles</button>
            </div>
        </div>
    </div>

    <script>
        const ALL_ROLES = [
            { id: 'god_mode', label: 'God Mode' },
            { id: 'admin', label: 'Admin' },
            { id: 'project_manager', label: 'Project Manager' },
            { id: 'estimator', label: 'Estimator' },
            { id: 'sales', label: 'Sales / Business Dev' },
            { id: 'purchasing', label: 'Purchasing' },
            { id: 'inventory_manager', label: 'Inventory Manager' },
            { id: 'accounting', label: 'Accounting' },
            { id: 'shop_foreman', label: 'Shop Foreman' },
            { id: 'qc_inspector', label: 'QA/QC Inspector' },
            { id: 'engineer', label: 'Engineer / Detailer' },
            { id: 'roll_forming_operator', label: 'Roll Forming Operator' },
            { id: 'welder', label: 'Welder' },
            { id: 'shipping_coordinator', label: 'Shipping Coordinator' },
            { id: 'laborer', label: 'Laborer' },
            { id: 'field_crew', label: 'Field Crew' },
            { id: 'safety_officer', label: 'Safety Officer' },
            { id: 'customer', label: 'Customer' },
        ];

        let editingUsername = null;
        let approvingRequestId = null;
        let currentUsername = null;

        // ── Init ──
        document.addEventListener('DOMContentLoaded', function() {
            // Get current user's username for self-delete protection
            fetch('/api/profile').then(r => r.json()).then(d => {
                if (d.ok) currentUsername = d.profile.username;
            }).catch(() => {});
            loadUsers();
            loadPendingRegistrations();
            setupFormHandlers();
            buildNewUserRoleCheckboxes();
        });

        function setupFormHandlers() {
            document.getElementById('addUserForm').addEventListener('submit', function(e) {
                e.preventDefault();
                addUser();
            });
        }

        // ── Build role checkboxes for the Add User form ──
        function buildNewUserRoleCheckboxes() {
            const container = document.getElementById('newRoleCheckboxes');
            container.innerHTML = ALL_ROLES.map(r => `
                <div class="role-checkbox-item" onclick="toggleCheckbox(this)">
                    <input type="checkbox" id="newRole_${r.id}" value="${r.id}">
                    <label for="newRole_${r.id}">${r.label}</label>
                </div>
            `).join('');
        }

        function toggleCheckbox(item) {
            const cb = item.querySelector('input[type="checkbox"]');
            cb.checked = !cb.checked;
            item.classList.toggle('checked', cb.checked);
        }

        function getCheckedNewRoles() {
            const checks = document.querySelectorAll('#newRoleCheckboxes input[type="checkbox"]:checked');
            return Array.from(checks).map(c => c.value);
        }

        // ── Load & Render Users ──
        function loadUsers() {
            fetch('/auth/users')
                .then(response => {
                    if (!response.ok) throw new Error('Failed to load users');
                    return response.json();
                })
                .then(data => {
                    renderUsersTable(data.users || []);
                })
                .catch(error => {
                    console.error('Error loading users:', error);
                    document.getElementById('usersTableBody').innerHTML = `
                        <tr><td colspan="5" class="empty-state">
                            <div class="empty-state-icon">&#9888;&#65039;</div>
                            <div class="empty-state-text">Failed to load users</div>
                        </td></tr>`;
                });
        }

        function renderUsersTable(users) {
            const tbody = document.getElementById('usersTableBody');
            if (users.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="empty-state">
                    <div class="empty-state-icon">&#128101;</div>
                    <div class="empty-state-text">No users yet. Add one to get started!</div>
                </td></tr>`;
                return;
            }

            tbody.innerHTML = users.map(user => {
                const roles = user.roles || [user.role || 'viewer'];
                const chips = roles.map((r, i) =>
                    `<span class="role-chip ${i === 0 ? 'primary' : ''}">${r.replace(/_/g, ' ')}</span>`
                ).join('');
                return `<tr>
                    <td><strong>${escapeHtml(user.username)}</strong></td>
                    <td>${escapeHtml(user.display_name || '-')}</td>
                    <td>
                        <div class="role-chips">
                            ${chips}
                            <button class="edit-roles-btn" onclick="openRoleModal('${escapeHtml(user.username)}', ${escapeHtml(JSON.stringify(JSON.stringify(roles)))})">&#9998; Edit</button>
                        </div>
                    </td>
                    <td>${formatDate(user.created_at)}</td>
                    <td>
                        <button class="btn btn-danger" onclick="deleteUser('${escapeHtml(user.username)}')" ${user.username === currentUsername ? 'disabled title="Cannot delete yourself"' : ''}>Delete</button>
                    </td>
                </tr>`;
            }).join('');
        }

        // ── Role Modal (edit existing user) ──
        function openRoleModal(username, rolesJson) {
            editingUsername = username;
            const currentRoles = JSON.parse(rolesJson);
            document.getElementById('roleModalTitle').textContent = 'Edit Roles: ' + username;
            const container = document.getElementById('roleModalCheckboxes');
            container.innerHTML = ALL_ROLES.map(r => {
                const checked = currentRoles.includes(r.id);
                return `<div class="role-checkbox-item ${checked ? 'checked' : ''}" onclick="toggleCheckbox(this)">
                    <input type="checkbox" value="${r.id}" ${checked ? 'checked' : ''}>
                    <label>${r.label}</label>
                </div>`;
            }).join('');
            document.getElementById('roleModalOverlay').classList.add('show');
        }

        function closeRoleModal() {
            document.getElementById('roleModalOverlay').classList.remove('show');
            editingUsername = null;
        }

        function saveRoles() {
            if (!editingUsername) return;
            const checks = document.querySelectorAll('#roleModalCheckboxes input[type="checkbox"]:checked');
            const roles = Array.from(checks).map(c => c.value);
            if (roles.length === 0) {
                alert('Please select at least one role.');
                return;
            }
            fetch('/auth/users/update-role', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: editingUsername, roles: roles })
            })
            .then(r => r.json())
            .then(data => {
                if (!data.ok) {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
                closeRoleModal();
                loadUsers();
            })
            .catch(err => {
                alert('Error: ' + err.message);
                closeRoleModal();
                loadUsers();
            });
        }

        // ── Add User ──
        function addUser() {
            const username = document.getElementById('newUsername').value.trim();
            const displayName = document.getElementById('newDisplayName').value.trim();
            const password = document.getElementById('newPassword').value;
            const roles = getCheckedNewRoles();

            const errorDiv = document.getElementById('addUserError');
            const successDiv = document.getElementById('addUserSuccess');
            errorDiv.classList.remove('show');
            successDiv.classList.remove('show');

            if (!username || !displayName || !password || roles.length === 0) {
                errorDiv.textContent = 'Please fill in all fields and select at least one role';
                errorDiv.classList.add('show');
                return;
            }

            const addUserBtn = document.getElementById('addUserBtn');
            addUserBtn.disabled = true;
            addUserBtn.textContent = 'Adding...';

            fetch('/auth/users/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: username,
                    display_name: displayName,
                    password: password,
                    roles: roles,
                    role: roles[0]
                })
            })
            .then(response => {
                if (!response.ok) return response.json().then(d => { throw new Error(d.error || 'Failed'); });
                return response.json();
            })
            .then(data => {
                successDiv.textContent = 'User added successfully!';
                successDiv.classList.add('show');
                document.getElementById('addUserForm').reset();
                // Uncheck all role checkboxes
                document.querySelectorAll('#newRoleCheckboxes .role-checkbox-item').forEach(item => {
                    item.classList.remove('checked');
                    item.querySelector('input').checked = false;
                });
                setTimeout(() => successDiv.classList.remove('show'), 3000);
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

        // ── Delete User ──
        function deleteUser(username) {
            if (!confirm('Are you sure you want to delete user "' + username + '"? This cannot be undone.')) return;
            fetch('/auth/users/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: username })
            })
            .then(r => r.json())
            .then(data => {
                if (!data.ok) alert('Error: ' + (data.error || 'Failed'));
                else loadUsers();
            })
            .catch(err => alert('Error: ' + err.message));
        }

        // ── Pending Registrations ──
        function loadPendingRegistrations() {
            fetch('/auth/registrations/pending')
                .then(r => r.json())
                .then(data => {
                    const regs = data.registrations || [];
                    const tbody = document.getElementById('pendingTableBody');
                    const badge = document.getElementById('pendingCount');
                    if (regs.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><div class="empty-state-text">No pending requests</div></td></tr>';
                        badge.style.display = 'none';
                        return;
                    }
                    badge.textContent = regs.length;
                    badge.style.display = 'inline';
                    tbody.innerHTML = regs.map(r => `<tr>
                        <td><strong>${escapeHtml(r.display_name)}</strong></td>
                        <td>${escapeHtml(r.username)}</td>
                        <td>${escapeHtml(r.email || '-')}<br><small style="color:#9ca3af">${escapeHtml(r.phone || '')}</small></td>
                        <td>${escapeHtml(r.company_role || '-')}</td>
                        <td>${formatDate(r.submitted_at)}</td>
                        <td style="display:flex;gap:6px;">
                            <button class="btn btn-primary" style="padding:6px 12px;font-size:11px;" onclick="openApproveModal('${escapeHtml(r.request_id)}', '${escapeHtml(r.display_name)}')">Approve</button>
                            <button class="btn btn-danger" onclick="rejectRegistration('${escapeHtml(r.request_id)}', '${escapeHtml(r.display_name)}')">Reject</button>
                        </td>
                    </tr>`).join('');
                })
                .catch(() => {
                    document.getElementById('pendingTableBody').innerHTML =
                        '<tr><td colspan="6" class="empty-state"><div class="empty-state-text">Failed to load</div></td></tr>';
                });
        }

        function openApproveModal(requestId, name) {
            approvingRequestId = requestId;
            document.getElementById('approveModalTitle').textContent = 'Approve: ' + name;
            const container = document.getElementById('approveRoleCheckboxes');
            container.innerHTML = ALL_ROLES.map(r => `
                <div class="role-checkbox-item" onclick="toggleCheckbox(this)">
                    <input type="checkbox" value="${r.id}" ${r.id === 'laborer' ? 'checked' : ''}>
                    <label>${r.label}</label>
                </div>`).join('');
            // Pre-check laborer
            container.querySelector('.role-checkbox-item').classList.add('checked');
            document.getElementById('approveNotes').value = '';
            document.getElementById('approveModalOverlay').classList.add('show');
        }

        function closeApproveModal() {
            document.getElementById('approveModalOverlay').classList.remove('show');
            approvingRequestId = null;
        }

        function confirmApprove() {
            if (!approvingRequestId) return;
            const checks = document.querySelectorAll('#approveRoleCheckboxes input[type="checkbox"]:checked');
            const roles = Array.from(checks).map(c => c.value);
            if (roles.length === 0) { alert('Select at least one role.'); return; }
            const notes = document.getElementById('approveNotes').value;

            fetch('/auth/registrations/approve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ request_id: approvingRequestId, roles: roles, notes: notes })
            })
            .then(r => r.json())
            .then(data => {
                if (!data.ok) alert('Error: ' + (data.error || 'Failed'));
                closeApproveModal();
                loadPendingRegistrations();
                loadUsers();
            })
            .catch(err => { alert('Error: ' + err.message); closeApproveModal(); });
        }

        function rejectRegistration(requestId, name) {
            const notes = prompt('Reason for rejecting ' + name + '? (optional)');
            if (notes === null) return; // cancelled
            fetch('/auth/registrations/reject', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ request_id: requestId, notes: notes })
            })
            .then(r => r.json())
            .then(data => {
                if (!data.ok) alert('Error: ' + (data.error || 'Failed'));
                loadPendingRegistrations();
            })
            .catch(err => alert('Error: ' + err.message));
        }

        // ── Logout ──
        function logout() {
            if (confirm('Are you sure you want to logout?')) {
                window.location.href = '/auth/logout';
            }
        }

        // ── Helpers ──
        function formatDate(dateString) {
            if (!dateString) return '-';
            const d = new Date(dateString);
            return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
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
