"""
TitanForge — My Profile Page
User profile settings: display name, password, language, notification prefs.
"""

PROFILE_PAGE_HTML = r"""
<style>
:root {
    --pf-bg: #0F172A;
    --pf-surface: #1E293B;
    --pf-border: #334155;
    --pf-text: #E2E8F0;
    --pf-muted: #94A3B8;
    --pf-blue: #3B82F6;
    --pf-green: #22C55E;
    --pf-red: #EF4444;
    --pf-amber: #F59E0B;
}
body { background: var(--pf-bg); color: var(--pf-text); font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }

.profile-container {
    max-width: 720px;
    margin: 32px auto;
    padding: 0 24px;
}
.profile-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 32px;
}
.profile-avatar {
    width: 72px; height: 72px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3B82F6, #8B5CF6);
    display: flex; align-items: center; justify-content: center;
    font-size: 28px; font-weight: 700; color: #fff;
    flex-shrink: 0;
}
.profile-header-info h1 {
    margin: 0 0 4px 0;
    font-size: 24px;
    font-weight: 700;
    color: #F8FAFC;
}
.profile-header-info p {
    margin: 0;
    color: var(--pf-muted);
    font-size: 14px;
}

.profile-card {
    background: var(--pf-surface);
    border: 1px solid var(--pf-border);
    border-radius: 12px;
    margin-bottom: 20px;
    overflow: hidden;
}
.profile-card-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--pf-border);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.profile-card-header h2 {
    margin: 0;
    font-size: 16px;
    font-weight: 700;
    color: #F8FAFC;
}
.profile-card-body {
    padding: 20px;
}

.pf-field {
    margin-bottom: 16px;
}
.pf-field:last-child { margin-bottom: 0; }
.pf-label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: var(--pf-muted);
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.pf-input {
    width: 100%;
    padding: 10px 14px;
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--pf-border);
    border-radius: 8px;
    color: var(--pf-text);
    font-size: 14px;
    transition: border-color 0.15s;
    box-sizing: border-box;
}
.pf-input:focus {
    outline: none;
    border-color: var(--pf-blue);
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15);
}
.pf-input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
.pf-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.pf-btn {
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: all 0.15s;
}
.pf-btn-primary {
    background: var(--pf-blue);
    color: #fff;
}
.pf-btn-primary:hover { background: #2563EB; }
.pf-btn-secondary {
    background: rgba(255,255,255,0.08);
    color: var(--pf-text);
    border: 1px solid var(--pf-border);
}
.pf-btn-secondary:hover { background: rgba(255,255,255,0.12); }

.pf-toggle-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.pf-toggle-row:last-child { border-bottom: none; }
.pf-toggle-label {
    font-size: 14px;
    color: var(--pf-text);
}
.pf-toggle-desc {
    font-size: 12px;
    color: var(--pf-muted);
    margin-top: 2px;
}

/* Toggle Switch */
.pf-switch {
    position: relative;
    width: 44px; height: 24px;
    flex-shrink: 0;
}
.pf-switch input { opacity: 0; width: 0; height: 0; }
.pf-switch .slider {
    position: absolute; inset: 0;
    background: #475569;
    border-radius: 12px;
    cursor: pointer;
    transition: background 0.2s;
}
.pf-switch .slider:before {
    content: '';
    position: absolute;
    width: 18px; height: 18px;
    left: 3px; top: 3px;
    background: #fff;
    border-radius: 50%;
    transition: transform 0.2s;
}
.pf-switch input:checked + .slider { background: var(--pf-blue); }
.pf-switch input:checked + .slider:before { transform: translateX(20px); }

/* Language selector */
.pf-lang-options {
    display: flex;
    gap: 12px;
}
.pf-lang-btn {
    flex: 1;
    padding: 12px;
    background: rgba(255,255,255,0.04);
    border: 2px solid var(--pf-border);
    border-radius: 10px;
    cursor: pointer;
    text-align: center;
    transition: all 0.15s;
    color: var(--pf-text);
}
.pf-lang-btn:hover {
    background: rgba(255,255,255,0.08);
}
.pf-lang-btn.active {
    border-color: var(--pf-blue);
    background: rgba(59,130,246,0.08);
}
.pf-lang-flag {
    font-size: 28px;
    display: block;
    margin-bottom: 6px;
}
.pf-lang-name {
    font-size: 13px;
    font-weight: 600;
}
.pf-lang-native {
    font-size: 11px;
    color: var(--pf-muted);
}

.pf-toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    color: #fff;
    z-index: 10000;
    opacity: 0;
    transform: translateY(12px);
    transition: all 0.3s;
    pointer-events: none;
}
.pf-toast.show {
    opacity: 1;
    transform: translateY(0);
}
.pf-toast.success { background: var(--pf-green); }
.pf-toast.error { background: var(--pf-red); }

.pf-info-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 0;
    font-size: 13px;
}
.pf-info-label {
    color: var(--pf-muted);
    min-width: 120px;
}
.pf-info-value {
    color: var(--pf-text);
    font-weight: 500;
}
.pf-role-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    background: rgba(59,130,246,0.15);
    color: var(--pf-blue);
}

@media (max-width: 640px) {
    .profile-container { padding: 0 12px; margin: 16px auto; }
    .profile-header { gap: 12px; }
    .profile-avatar { width: 56px; height: 56px; font-size: 22px; }
    .profile-header-info h1 { font-size: 18px; }
    .pf-row { grid-template-columns: 1fr; }
    .pf-lang-options { flex-direction: column; }
}
</style>

<div class="profile-container">
    <!-- Header -->
    <div class="profile-header">
        <div class="profile-avatar" id="pfAvatar">U</div>
        <div class="profile-header-info">
            <h1 id="pfHeaderName" data-i18n="My Profile">My Profile</h1>
            <p id="pfHeaderRole"></p>
        </div>
    </div>

    <!-- Account Info Card -->
    <div class="profile-card">
        <div class="profile-card-header">
            <h2 data-i18n="Account Information">Account Information</h2>
        </div>
        <div class="profile-card-body">
            <div class="pf-row">
                <div class="pf-field">
                    <label class="pf-label" data-i18n="Display Name">Display Name</label>
                    <input type="text" class="pf-input" id="pfDisplayName" placeholder="Your name">
                </div>
                <div class="pf-field">
                    <label class="pf-label" data-i18n="Email">Email</label>
                    <input type="email" class="pf-input" id="pfEmail" placeholder="email@company.com">
                </div>
            </div>
            <div class="pf-row">
                <div class="pf-field">
                    <label class="pf-label" data-i18n="Username">Username</label>
                    <input type="text" class="pf-input" id="pfUsername" disabled>
                </div>
                <div class="pf-field">
                    <label class="pf-label" data-i18n="Role">Role</label>
                    <input type="text" class="pf-input" id="pfRole" disabled>
                </div>
            </div>
            <div style="margin-top:16px;display:flex;gap:12px;">
                <button class="pf-btn pf-btn-primary" onclick="saveProfile()" data-i18n="Save Changes">Save Changes</button>
            </div>
        </div>
    </div>

    <!-- Change Password Card -->
    <div class="profile-card">
        <div class="profile-card-header">
            <h2 data-i18n="Change Password">Change Password</h2>
        </div>
        <div class="profile-card-body">
            <div class="pf-field">
                <label class="pf-label" data-i18n="Current Password">Current Password</label>
                <input type="password" class="pf-input" id="pfCurrentPw" placeholder="Enter current password">
            </div>
            <div class="pf-row">
                <div class="pf-field">
                    <label class="pf-label" data-i18n="New Password">New Password</label>
                    <input type="password" class="pf-input" id="pfNewPw" placeholder="Enter new password">
                </div>
                <div class="pf-field">
                    <label class="pf-label" data-i18n="Confirm Password">Confirm Password</label>
                    <input type="password" class="pf-input" id="pfConfirmPw" placeholder="Confirm new password">
                </div>
            </div>
            <div style="margin-top:16px;">
                <button class="pf-btn pf-btn-primary" onclick="changePassword()" data-i18n="Update Password">Update Password</button>
            </div>
        </div>
    </div>

    <!-- Language Card -->
    <div class="profile-card">
        <div class="profile-card-header">
            <h2 data-i18n="Language">Language</h2>
        </div>
        <div class="profile-card-body">
            <div class="pf-lang-options">
                <div class="pf-lang-btn" id="langEn" onclick="setProfileLang('en')">
                    <span class="pf-lang-flag">&#127482;&#127480;</span>
                    <span class="pf-lang-name">English</span>
                    <span class="pf-lang-native">English</span>
                </div>
                <div class="pf-lang-btn" id="langEs" onclick="setProfileLang('es')">
                    <span class="pf-lang-flag">&#127474;&#127485;</span>
                    <span class="pf-lang-name" data-i18n="Spanish">Spanish</span>
                    <span class="pf-lang-native">Español</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Notification Preferences Card -->
    <div class="profile-card">
        <div class="profile-card-header">
            <h2 data-i18n="Notifications">Notification Preferences</h2>
        </div>
        <div class="profile-card-body">
            <div class="pf-toggle-row">
                <div>
                    <div class="pf-toggle-label" data-i18n="Work Order Updates">Work Order Updates</div>
                    <div class="pf-toggle-desc" data-i18n="Get notified when work orders are created or status changes">Get notified when work orders are created or status changes</div>
                </div>
                <label class="pf-switch"><input type="checkbox" id="notifWO" checked><span class="slider"></span></label>
            </div>
            <div class="pf-toggle-row">
                <div>
                    <div class="pf-toggle-label" data-i18n="QC Inspections">QC Inspections</div>
                    <div class="pf-toggle-desc" data-i18n="Alerts for inspection results and NCRs">Alerts for inspection results and NCRs</div>
                </div>
                <label class="pf-switch"><input type="checkbox" id="notifQC" checked><span class="slider"></span></label>
            </div>
            <div class="pf-toggle-row">
                <div>
                    <div class="pf-toggle-label" data-i18n="Shipping Updates">Shipping Updates</div>
                    <div class="pf-toggle-desc" data-i18n="Notifications when loads are built or shipped">Notifications when loads are built or shipped</div>
                </div>
                <label class="pf-switch"><input type="checkbox" id="notifShip" checked><span class="slider"></span></label>
            </div>
            <div class="pf-toggle-row">
                <div>
                    <div class="pf-toggle-label" data-i18n="Inventory Alerts">Inventory Alerts</div>
                    <div class="pf-toggle-desc" data-i18n="Low stock warnings and receiving notifications">Low stock warnings and receiving notifications</div>
                </div>
                <label class="pf-switch"><input type="checkbox" id="notifInv" checked><span class="slider"></span></label>
            </div>
            <div class="pf-toggle-row">
                <div>
                    <div class="pf-toggle-label" data-i18n="Safety Incidents">Safety Incidents</div>
                    <div class="pf-toggle-desc" data-i18n="Immediate alerts for safety incidents and near misses">Immediate alerts for safety incidents and near misses</div>
                </div>
                <label class="pf-switch"><input type="checkbox" id="notifSafety" checked><span class="slider"></span></label>
            </div>
            <div style="margin-top:16px;">
                <button class="pf-btn pf-btn-primary" onclick="saveNotifPrefs()" data-i18n="Save Preferences">Save Preferences</button>
            </div>
        </div>
    </div>
</div>

<!-- Toast notification -->
<div class="pf-toast" id="pfToast"></div>

<script>
(function(){
    // Load current user info
    async function loadProfile() {
        try {
            // Get user data from API
            var resp = await fetch('/api/auth/me');
            if (resp.ok) {
                var data = await resp.json();
                if (data.ok) {
                    var user = data.user || {};
                    document.getElementById('pfDisplayName').value = user.display_name || user.username || '';
                    document.getElementById('pfEmail').value = user.email || '';
                    document.getElementById('pfUsername').value = user.username || '';
                    document.getElementById('pfRole').value = (user.roles || [user.role || 'admin']).join(', ').replace(/_/g, ' ');
                    var initials = (user.display_name || user.username || 'U').split(' ').map(function(w){ return w[0]; }).join('').toUpperCase().slice(0,2);
                    document.getElementById('pfAvatar').textContent = initials;
                    document.getElementById('pfHeaderName').textContent = user.display_name || user.username || 'My Profile';
                    document.getElementById('pfHeaderRole').textContent = (user.roles || [user.role || '']).join(', ').replace(/_/g, ' ').replace(/\b\w/g, function(l){ return l.toUpperCase(); });
                }
            }
        } catch(e) {
            console.debug('Profile load failed', e);
            // Fallback: read from cookie or page
            var nameEl = document.querySelector('.user-name');
            if (nameEl) {
                document.getElementById('pfDisplayName').value = nameEl.textContent.trim();
                document.getElementById('pfAvatar').textContent = nameEl.textContent.trim().slice(0,2).toUpperCase();
            }
        }

        // Load notification preferences
        try {
            var resp2 = await fetch('/api/notifications/settings');
            if (resp2.ok) {
                var prefs = await resp2.json();
                if (prefs.ok && prefs.settings) {
                    var s = prefs.settings;
                    document.getElementById('notifWO').checked = s.work_orders !== false;
                    document.getElementById('notifQC').checked = s.qc !== false;
                    document.getElementById('notifShip').checked = s.shipping !== false;
                    document.getElementById('notifInv').checked = s.inventory !== false;
                    document.getElementById('notifSafety').checked = s.safety !== false;
                }
            }
        } catch(e) { console.debug('Notif prefs load failed', e); }

        // Set language highlight
        var m = document.cookie.match(/(?:^|;\s*)tf_lang=([^;]+)/);
        var lang = m ? m[1] : 'en';
        document.getElementById('langEn').classList.toggle('active', lang === 'en');
        document.getElementById('langEs').classList.toggle('active', lang === 'es');
    }

    // Save profile info
    window.saveProfile = async function() {
        var displayName = document.getElementById('pfDisplayName').value.trim();
        var email = document.getElementById('pfEmail').value.trim();
        if (!displayName) { showToast('Name is required', 'error'); return; }
        try {
            var resp = await fetch('/api/auth/me', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ display_name: displayName, email: email })
            });
            var data = await resp.json();
            if (data.ok) {
                showToast(window.t ? t('Successfully saved') : 'Successfully saved', 'success');
                // Update sidebar name
                document.querySelectorAll('.user-name').forEach(function(el){ el.textContent = displayName; });
            } else {
                showToast(data.error || 'Save failed', 'error');
            }
        } catch(e) {
            showToast('Save failed: ' + e.message, 'error');
        }
    };

    // Change password
    window.changePassword = async function() {
        var current = document.getElementById('pfCurrentPw').value;
        var newPw = document.getElementById('pfNewPw').value;
        var confirm = document.getElementById('pfConfirmPw').value;
        if (!current || !newPw) { showToast('Please fill in all password fields', 'error'); return; }
        if (newPw !== confirm) { showToast('New passwords do not match', 'error'); return; }
        if (newPw.length < 8) { showToast('Password must be at least 8 characters', 'error'); return; }
        try {
            var resp = await fetch('/api/auth/change-password', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ current_password: current, new_password: newPw })
            });
            var data = await resp.json();
            if (data.ok) {
                showToast(window.t ? t('Successfully updated') : 'Password updated', 'success');
                document.getElementById('pfCurrentPw').value = '';
                document.getElementById('pfNewPw').value = '';
                document.getElementById('pfConfirmPw').value = '';
            } else {
                showToast(data.error || 'Password change failed', 'error');
            }
        } catch(e) {
            showToast('Error: ' + e.message, 'error');
        }
    };

    // Set language
    window.setProfileLang = function(lang) {
        document.cookie = 'tf_lang=' + lang + ';path=/;max-age=31536000;SameSite=Lax';
        document.getElementById('langEn').classList.toggle('active', lang === 'en');
        document.getElementById('langEs').classList.toggle('active', lang === 'es');
        // Reload to apply
        window.location.reload();
    };

    // Save notification preferences
    window.saveNotifPrefs = async function() {
        var settings = {
            work_orders: document.getElementById('notifWO').checked,
            qc: document.getElementById('notifQC').checked,
            shipping: document.getElementById('notifShip').checked,
            inventory: document.getElementById('notifInv').checked,
            safety: document.getElementById('notifSafety').checked
        };
        try {
            var resp = await fetch('/api/notifications/settings', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ settings: settings })
            });
            var data = await resp.json();
            if (data.ok) {
                showToast(window.t ? t('Successfully saved') : 'Preferences saved', 'success');
            } else {
                showToast(data.error || 'Save failed', 'error');
            }
        } catch(e) {
            showToast('Error: ' + e.message, 'error');
        }
    };

    function showToast(msg, type) {
        var toast = document.getElementById('pfToast');
        toast.textContent = msg;
        toast.className = 'pf-toast ' + (type || 'success') + ' show';
        setTimeout(function(){ toast.classList.remove('show'); }, 3000);
    }

    loadProfile();
})();
</script>
"""
