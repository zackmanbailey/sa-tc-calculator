PROFILE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge - My Profile</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #0F172A; color: #e5e7eb;
        }
        .profile-container { max-width: 800px; margin: 0 auto; padding: 40px 24px; }
        .page-header { margin-bottom: 32px; }
        .page-title { font-size: 28px; font-weight: 700; color: #f3f4f6; margin-bottom: 6px; }
        .page-subtitle { font-size: 14px; color: #9ca3af; }

        .profile-card {
            background: rgba(30, 41, 59, 0.6); border: 1px solid #1E40AF;
            border-radius: 8px; padding: 28px; margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .card-title {
            font-size: 16px; font-weight: 600; color: #F59E0B; margin-bottom: 20px;
            padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.08);
        }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
        .form-group { display: flex; flex-direction: column; }
        .form-group label {
            font-size: 12px; font-weight: 600; color: #d1d5db; margin-bottom: 6px;
            text-transform: uppercase; letter-spacing: 0.5px;
        }
        .form-group input, .form-group textarea {
            padding: 10px 12px; border: 1px solid #374151; border-radius: 6px;
            background: rgba(15, 23, 42, 0.8); color: #f3f4f6;
            font-size: 14px; font-family: inherit; transition: all 0.3s ease;
        }
        .form-group input:focus, .form-group textarea:focus {
            outline: none; border-color: #1E40AF;
            box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
        }
        .form-group input:read-only {
            background: rgba(15, 23, 42, 0.4); color: #9ca3af; cursor: not-allowed;
        }
        .form-group textarea { min-height: 60px; resize: vertical; }
        .form-group input::placeholder, .form-group textarea::placeholder { color: #6b7280; }
        .role-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
        .role-chip {
            display: inline-block; padding: 4px 10px; border-radius: 12px;
            font-size: 11px; font-weight: 600; text-transform: uppercase;
            background: rgba(245, 158, 11, 0.15); color: #F59E0B;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .btn {
            padding: 10px 24px; border: none; border-radius: 6px;
            font-size: 14px; font-weight: 600; cursor: pointer;
            transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 0.5px;
        }
        .btn-primary { background: #1E40AF; color: white; }
        .btn-primary:hover { background: #1e3a8a; box-shadow: 0 4px 12px rgba(30,64,175,0.3); }
        .btn-primary:disabled { background: #4b5563; cursor: not-allowed; opacity: 0.6; }
        .btn-secondary { background: rgba(107,114,128,0.2); color: #d1d5db; border: 1px solid #374151; }
        .btn-secondary:hover { background: rgba(107,114,128,0.3); }
        .btn-actions { display: flex; gap: 12px; margin-top: 20px; }
        .status-msg {
            display: none; padding: 10px 14px; border-radius: 6px;
            font-size: 13px; margin-bottom: 16px;
        }
        .status-msg.error { background: rgba(220,38,38,0.15); color: #fca5a5; border: 1px solid #dc2626; }
        .status-msg.success { background: rgba(34,197,94,0.15); color: #86efac; border: 1px solid #22c55e; }
        .status-msg.show { display: block; }

        .pw-section { margin-top: 8px; }
        .pw-requirements { font-size: 11px; color: #6b7280; margin-top: 6px; line-height: 1.6; }
        .pw-requirements span { display: block; }
        .pw-requirements span.met { color: #22c55e; }
        .meta-info { display: flex; gap: 24px; margin-top: 8px; font-size: 13px; color: #6b7280; }
        @media (max-width: 600px) { .form-row { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="profile-container">
        <div class="page-header">
            <h1 class="page-title">My Profile</h1>
            <p class="page-subtitle">View and update your account information</p>
        </div>

        <!-- Profile Info Card -->
        <div class="profile-card">
            <div class="card-title">Personal Information</div>
            <div class="status-msg" id="profileStatus"></div>

            <div class="form-row">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" id="pUsername" readonly>
                </div>
                <div class="form-group">
                    <label>Display Name</label>
                    <input type="text" id="pDisplayName" placeholder="Your name" maxlength="100">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="pEmail" placeholder="you@company.com" maxlength="254">
                </div>
                <div class="form-group">
                    <label>Phone</label>
                    <input type="tel" id="pPhone" placeholder="(555) 123-4567" maxlength="20">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Company Role</label>
                    <input type="text" id="pCompanyRole" placeholder="Your role at the company" maxlength="100">
                </div>
                <div class="form-group">
                    <label>System Roles</label>
                    <div class="role-chips" id="pRoles"></div>
                </div>
            </div>
            <div class="form-group">
                <label>Address</label>
                <textarea id="pAddress" placeholder="Street address, city, state, zip" maxlength="300"></textarea>
            </div>
            <div class="meta-info">
                <span>Member since: <strong id="pCreatedAt">-</strong></span>
                <span>Last login: <strong id="pLastLogin">-</strong></span>
            </div>
            <div class="btn-actions">
                <button class="btn btn-primary" onclick="saveProfile()">Save Changes</button>
            </div>
        </div>

        <!-- Change Password Card -->
        <div class="profile-card">
            <div class="card-title">Change Password</div>
            <div class="status-msg" id="pwStatus"></div>

            <div class="form-group">
                <label>Current Password</label>
                <input type="password" id="pwCurrent" placeholder="Enter current password" autocomplete="current-password">
            </div>
            <div class="form-group pw-section">
                <label>New Password</label>
                <input type="password" id="pwNew" placeholder="Enter new password" autocomplete="new-password">
                <div class="pw-requirements">
                    <span id="pwLen">Min 8 characters</span>
                    <span id="pwUpper">At least one uppercase letter</span>
                    <span id="pwLower">At least one lowercase letter</span>
                    <span id="pwNum">At least one number</span>
                </div>
            </div>
            <div class="form-group">
                <label>Confirm New Password</label>
                <input type="password" id="pwConfirm" placeholder="Re-enter new password" autocomplete="new-password">
            </div>
            <div class="btn-actions">
                <button class="btn btn-primary" onclick="changePassword()">Change Password</button>
            </div>
        </div>
    </div>

    <script>
        // ── Load profile on page load ──
        document.addEventListener('DOMContentLoaded', loadProfile);

        function loadProfile() {
            fetch('/api/profile')
                .then(r => r.json())
                .then(data => {
                    if (!data.ok) return;
                    const p = data.profile;
                    document.getElementById('pUsername').value = p.username || '';
                    document.getElementById('pDisplayName').value = p.display_name || '';
                    document.getElementById('pEmail').value = p.email || '';
                    document.getElementById('pPhone').value = p.phone || '';
                    document.getElementById('pCompanyRole').value = p.company_role || '';
                    document.getElementById('pAddress').value = p.address || '';
                    document.getElementById('pCreatedAt').textContent = formatDate(p.created_at);
                    document.getElementById('pLastLogin').textContent = formatDate(p.last_login);
                    // Role chips
                    const roles = p.roles || [];
                    document.getElementById('pRoles').innerHTML = roles.map(r =>
                        '<span class="role-chip">' + r.replace(/_/g, ' ') + '</span>'
                    ).join('');
                });
        }

        function saveProfile() {
            const statusDiv = document.getElementById('profileStatus');
            statusDiv.classList.remove('show', 'error', 'success');

            fetch('/api/profile/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    display_name: document.getElementById('pDisplayName').value.trim(),
                    email: document.getElementById('pEmail').value.trim(),
                    phone: document.getElementById('pPhone').value.trim(),
                    company_role: document.getElementById('pCompanyRole').value.trim(),
                    address: document.getElementById('pAddress').value.trim(),
                })
            })
            .then(r => r.json())
            .then(data => {
                statusDiv.textContent = data.ok ? 'Profile updated.' : (data.error || 'Update failed.');
                statusDiv.classList.add('show', data.ok ? 'success' : 'error');
                if (data.ok) setTimeout(() => statusDiv.classList.remove('show'), 3000);
            })
            .catch(() => {
                statusDiv.textContent = 'Network error.';
                statusDiv.classList.add('show', 'error');
            });
        }

        // ── Password strength feedback ──
        document.getElementById('pwNew').addEventListener('input', function() {
            const v = this.value;
            document.getElementById('pwLen').className = v.length >= 8 ? 'met' : '';
            document.getElementById('pwUpper').className = /[A-Z]/.test(v) ? 'met' : '';
            document.getElementById('pwLower').className = /[a-z]/.test(v) ? 'met' : '';
            document.getElementById('pwNum').className = /[0-9]/.test(v) ? 'met' : '';
        });

        function changePassword() {
            const statusDiv = document.getElementById('pwStatus');
            statusDiv.classList.remove('show', 'error', 'success');

            const current = document.getElementById('pwCurrent').value;
            const newPw = document.getElementById('pwNew').value;
            const confirm = document.getElementById('pwConfirm').value;

            if (!current || !newPw) {
                statusDiv.textContent = 'Please fill in all password fields.';
                statusDiv.classList.add('show', 'error');
                return;
            }
            if (newPw !== confirm) {
                statusDiv.textContent = 'New passwords do not match.';
                statusDiv.classList.add('show', 'error');
                return;
            }

            fetch('/api/profile/change-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ current_password: current, new_password: newPw })
            })
            .then(r => r.json())
            .then(data => {
                statusDiv.textContent = data.ok ? 'Password changed successfully.' : (data.error || 'Failed.');
                statusDiv.classList.add('show', data.ok ? 'success' : 'error');
                if (data.ok) {
                    document.getElementById('pwCurrent').value = '';
                    document.getElementById('pwNew').value = '';
                    document.getElementById('pwConfirm').value = '';
                    document.querySelectorAll('.pw-requirements span').forEach(s => s.className = '');
                }
            })
            .catch(() => {
                statusDiv.textContent = 'Network error.';
                statusDiv.classList.add('show', 'error');
            });
        }

        function formatDate(d) {
            if (!d) return '-';
            return new Date(d).toLocaleDateString('en-US', { year:'numeric', month:'short', day:'numeric' });
        }
    </script>
</body>
</html>
"""
