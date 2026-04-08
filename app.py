"""
Structures America Material Takeoff Calculator
Main Application — Tornado Web Server
Run: python app.py [--port 8888]
Opens automatically in default browser.
"""

import os, sys, json, io, datetime, webbrowser, threading, argparse, hashlib, uuid, secrets
import tornado.ioloop
import tornado.web
from tornado.escape import json_decode, json_encode

# ── Authentication / User Management ─────────────────────────────────────────
try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

# ── Ensure calc package is importable ─────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from calc.bom import (
    BOMCalculator, ProjectInfo, BuildingConfig,
    bom_to_dict, ProjectBOM
)
from calc.defaults import DEFAULTS, WIND_SPEEDS_BY_STATE, FOOTING_DEPTHS_BY_STATE
from outputs.excel_gen import generate_bom_excel
from outputs.pdf_gen import generate_quote_pdf
from outputs.zpl_gen import (
    generate_labels_from_bom, labels_to_zpl,
    labels_to_preview_html, labels_to_pdf, labels_to_csv,
    make_job_code,
    coil_sticker_to_pdf, coil_sticker_to_zpl, coil_stickers_to_csv,
)

INVENTORY_PATH = os.path.join(BASE_DIR, "data", "inventory.json")

def load_inventory():
    with open(INVENTORY_PATH, "r") as f:
        return json.load(f)

def save_inventory(data):
    with open(INVENTORY_PATH, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────────────────────
# AUTH CONFIG
# ─────────────────────────────────────────────

USERS_PATH = os.path.join(BASE_DIR, "data", "users.json")
COOKIE_SECRET = None   # Set at startup from env or auto-generated

def _ensure_users_file():
    """Create users.json with a default admin account if it doesn't exist."""
    if os.path.isfile(USERS_PATH):
        return
    default_password = "titan2026"
    if HAS_BCRYPT:
        hashed = bcrypt.hashpw(default_password.encode(), bcrypt.gensalt()).decode()
    else:
        hashed = hashlib.sha256(default_password.encode()).hexdigest()
    users = {
        "admin": {
            "password": hashed,
            "display_name": "Admin",
            "role": "admin",
            "created": datetime.datetime.now().isoformat(),
        },
        "brad": {
            "password": bcrypt.hashpw("brad2026".encode(), bcrypt.gensalt()).decode() if HAS_BCRYPT
                        else hashlib.sha256("brad2026".encode()).hexdigest(),
            "display_name": "Brad Spence",
            "role": "user",
            "created": datetime.datetime.now().isoformat(),
        },
    }
    os.makedirs(os.path.dirname(USERS_PATH), exist_ok=True)
    with open(USERS_PATH, "w") as f:
        json.dump(users, f, indent=2)
    print(f"  [AUTH] Created default users file: {USERS_PATH}")
    print(f"  [AUTH] Default login  →  admin / titan2026")
    print(f"  [AUTH]                →  brad  / brad2026")

def load_users():
    if not os.path.isfile(USERS_PATH):
        _ensure_users_file()
    with open(USERS_PATH, "r") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_PATH, "w") as f:
        json.dump(data, f, indent=2)

def verify_password(stored_hash: str, password: str) -> bool:
    if HAS_BCRYPT and stored_hash.startswith("$2"):
        return bcrypt.checkpw(password.encode(), stored_hash.encode())
    return stored_hash == hashlib.sha256(password.encode()).hexdigest()

def hash_password(password: str) -> str:
    if HAS_BCRYPT:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return hashlib.sha256(password.encode()).hexdigest()

# Auth is enabled by default for hosted deployments; disabled for localhost dev.
# Set AUTH_ENABLED=1 env var or --auth CLI flag to force enable.
AUTH_ENABLED = False   # Set at startup


# ── Login Page HTML ───────────────────────────────────────────────────────────

LOGIN_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Login — SA / TC Calculator</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #003A6E 0%, #1a1a2e 100%);
         min-height: 100vh; display: flex; align-items: center; justify-content: center; }
  .login-card { background: #fff; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                padding: 40px 36px; width: 100%; max-width: 380px; }
  .logo-area { text-align: center; margin-bottom: 24px; }
  .logo-area h1 { font-size: 22px; color: #003A6E; margin-top: 8px; }
  .logo-area .sub { font-size: 12px; color: #888; margin-top: 4px; }
  .gold-bar { height: 3px; background: #C89A2E; border-radius: 2px; margin: 16px 0 24px; }
  .form-group { margin-bottom: 16px; }
  .form-group label { display: block; font-size: 11px; font-weight: 700; color: #003A6E;
                      text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 5px; }
  .form-group input { width: 100%; padding: 10px 12px; font-size: 14px; border: 1px solid #ccc;
                      border-radius: 5px; transition: border-color 0.2s; }
  .form-group input:focus { outline: none; border-color: #003A6E; box-shadow: 0 0 0 2px rgba(0,58,110,0.1); }
  .btn-login { width: 100%; padding: 12px; font-size: 14px; font-weight: 700; color: #fff;
               background: #003A6E; border: none; border-radius: 5px; cursor: pointer;
               transition: background 0.2s; letter-spacing: 0.3px; }
  .btn-login:hover { background: #00508C; }
  .error-msg { background: #fdf3f3; color: #9B1C1C; padding: 10px 12px; border-radius: 5px;
               font-size: 13px; margin-bottom: 14px; display: none; border-left: 3px solid #9B1C1C; }
  .footer-text { text-align: center; font-size: 11px; color: #aaa; margin-top: 20px; }
</style>
</head>
<body>
<div class="login-card">
  <div class="logo-area">
    <h1>SA / TC Calculator</h1>
    <div class="sub">Structures America · Titan Carports</div>
  </div>
  <div class="gold-bar"></div>
  <div id="error-msg" class="error-msg"></div>
  <form id="login-form" onsubmit="doLogin(event)">
    <div class="form-group">
      <label>Username</label>
      <input type="text" id="username" autocomplete="username" autofocus required/>
    </div>
    <div class="form-group">
      <label>Password</label>
      <input type="password" id="password" autocomplete="current-password" required/>
    </div>
    <button type="submit" class="btn-login">Sign In</button>
  </form>
  <div class="footer-text">Internal use only · v2.6</div>
</div>
<script>
async function doLogin(e) {
  e.preventDefault();
  const errEl = document.getElementById('error-msg');
  errEl.style.display = 'none';
  const user = document.getElementById('username').value.trim();
  const pass = document.getElementById('password').value;
  const res = await fetch('/auth/login', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({username: user, password: pass}),
  });
  const data = await res.json();
  if (data.ok) {
    window.location.href = data.redirect || '/';
  } else {
    errEl.textContent = data.error || 'Invalid username or password.';
    errEl.style.display = 'block';
  }
}
</script>
</body>
</html>"""


# ── Admin Panel HTML (manage users) ─────────────────────────────────────────

ADMIN_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>User Management — SA / TC Calculator</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Arial, sans-serif; background: #f4f6f9; color: #222; }
  .topbar { background: #003A6E; color: #fff; padding: 14px 20px;
            display: flex; align-items: center; gap: 12px; }
  .topbar h1 { font-size: 18px; }
  .topbar a { color: #C89A2E; text-decoration: none; font-size: 13px; font-weight: bold; }
  .card { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #0001;
          margin: 16px; padding: 18px; }
  .card h2 { font-size: 14px; color: #003A6E; text-transform: uppercase;
             letter-spacing: 0.04em; margin-bottom: 12px;
             border-bottom: 2px solid #C89A2E; padding-bottom: 6px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #eee; }
  th { background: #003A6E; color: #fff; font-size: 11px; text-transform: uppercase; }
  .btn { padding: 6px 14px; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: bold; }
  .btn-primary { background: #003A6E; color: #fff; }
  .btn-red { background: #9B1C1C; color: #fff; }
  .form-row { display: flex; gap: 10px; align-items: flex-end; flex-wrap: wrap; margin-bottom: 16px; }
  .form-group { flex: 1; min-width: 140px; }
  .form-group label { display: block; font-size: 11px; font-weight: 700; color: #003A6E;
                      text-transform: uppercase; margin-bottom: 4px; }
  .form-group input, .form-group select { width: 100%; padding: 7px 10px; font-size: 13px;
                                          border: 1px solid #ccc; border-radius: 4px; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 10px; font-weight: bold; }
  .badge-admin { background: #C89A2E; color: #fff; }
  .badge-user  { background: #d4edda; color: #155724; }
  .status-msg  { font-size: 12px; color: #155724; margin-top: 8px; }
</style>
</head>
<body>
<div class="topbar">
  <h1>User Management</h1>
  <div style="margin-left:auto; display:flex; gap:14px; align-items:center;">
    <a href="/">← SA Calculator</a>
    <a href="/tc">TC Quote →</a>
    <a href="/auth/logout" style="color:#fff;background:#9B1C1C;padding:5px 12px;border-radius:4px">Log Out</a>
  </div>
</div>

<div class="card">
  <h2>Add New User</h2>
  <div class="form-row">
    <div class="form-group"><label>Username</label><input type="text" id="new_user"/></div>
    <div class="form-group"><label>Display Name</label><input type="text" id="new_display"/></div>
    <div class="form-group"><label>Password</label><input type="password" id="new_pass"/></div>
    <div class="form-group"><label>Role</label>
      <select id="new_role"><option value="user">User</option><option value="admin">Admin</option></select>
    </div>
    <button class="btn btn-primary" onclick="addUser()">+ Add User</button>
  </div>
  <div id="add-status" class="status-msg"></div>
</div>

<div class="card">
  <h2>Current Users</h2>
  <div id="users-list"></div>
</div>

<script>
async function loadUsers() {
  const res = await fetch('/auth/users');
  const data = await res.json();
  let html = '<table><tr><th>Username</th><th>Display Name</th><th>Role</th><th>Created</th><th></th></tr>';
  for (const [uname, u] of Object.entries(data.users||{})) {
    const badge = u.role === 'admin' ? 'badge-admin' : 'badge-user';
    html += `<tr>
      <td><strong>${uname}</strong></td>
      <td>${u.display_name||''}</td>
      <td><span class="badge ${badge}">${u.role}</span></td>
      <td style="font-size:11px;color:#888">${(u.created||'').slice(0,10)}</td>
      <td>${uname!=='admin'?`<button class="btn btn-red" onclick="deleteUser('${uname}')">Delete</button>`:''}</td>
    </tr>`;
  }
  html += '</table>';
  document.getElementById('users-list').innerHTML = html;
}

async function addUser() {
  const user = document.getElementById('new_user').value.trim();
  const display = document.getElementById('new_display').value.trim();
  const pass = document.getElementById('new_pass').value;
  const role = document.getElementById('new_role').value;
  if (!user || !pass) { alert('Username and password are required.'); return; }
  const res = await fetch('/auth/users/add', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({username:user, display_name:display, password:pass, role:role}),
  });
  const data = await res.json();
  if (data.ok) {
    document.getElementById('add-status').textContent = '✅ User added!';
    document.getElementById('new_user').value = '';
    document.getElementById('new_display').value = '';
    document.getElementById('new_pass').value = '';
    loadUsers();
  } else {
    alert(data.error || 'Failed to add user.');
  }
}

async function deleteUser(uname) {
  if (!confirm('Delete user "' + uname + '"? This cannot be undone.')) return;
  const res = await fetch('/auth/users/delete', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({username: uname}),
  });
  const data = await res.json();
  if (data.ok) loadUsers();
  else alert(data.error || 'Failed');
}

loadUsers();
</script>
</body>
</html>"""


# ── Base Authenticated Handler ─────────────────────────────────────────────

class BaseHandler(tornado.web.RequestHandler):
    """Base handler that checks for authentication when AUTH_ENABLED."""
    def get_current_user(self):
        if not AUTH_ENABLED:
            return "local"
        cookie = self.get_secure_cookie("sa_user")
        if cookie:
            return cookie.decode("utf-8")
        return None

    def prepare(self):
        # Skip auth check for login/logout and static routes
        if not AUTH_ENABLED:
            return
        path = self.request.path
        if path.startswith("/auth/") or path.startswith("/static/"):
            return
        if not self.get_current_user():
            if self.request.method == "GET":
                self.redirect("/auth/login")
            else:
                self.set_status(401)
                self.write(json_encode({"error": "Not authenticated"}))
            raise tornado.web.Finish()


class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        if self.get_secure_cookie("sa_user"):
            self.redirect("/")
            return
        self.set_header("Content-Type", "text/html")
        self.write(LOGIN_HTML)

    def post(self):
        body     = json_decode(self.request.body)
        username = body.get("username", "").strip().lower()
        password = body.get("password", "")

        users = load_users()
        user  = users.get(username)
        if not user or not verify_password(user["password"], password):
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": False, "error": "Invalid username or password."}))
            return

        self.set_secure_cookie("sa_user", username, expires_days=30)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "redirect": "/"}))


class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie("sa_user")
        self.redirect("/auth/login")


class AdminPageHandler(BaseHandler):
    def get(self):
        if AUTH_ENABLED:
            current = self.get_current_user()
            users = load_users()
            u = users.get(current, {})
            if u.get("role") != "admin" and current != "local":
                self.set_status(403)
                self.write("Admin access required.")
                return
        self.set_header("Content-Type", "text/html")
        self.write(ADMIN_HTML)


class UsersListHandler(BaseHandler):
    def get(self):
        users = load_users()
        safe = {}
        for uname, udata in users.items():
            safe[uname] = {
                "display_name": udata.get("display_name", ""),
                "role": udata.get("role", "user"),
                "created": udata.get("created", ""),
            }
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"users": safe}))


class UserAddHandler(BaseHandler):
    def post(self):
        if AUTH_ENABLED:
            current = self.get_current_user()
            users = load_users()
            if users.get(current, {}).get("role") != "admin" and current != "local":
                self.set_status(403)
                self.write(json_encode({"ok": False, "error": "Admin only"}))
                return

        body = json_decode(self.request.body)
        username = body.get("username", "").strip().lower()
        password = body.get("password", "")
        if not username or not password:
            self.write(json_encode({"ok": False, "error": "Username and password required"}))
            return

        users = load_users()
        if username in users:
            self.write(json_encode({"ok": False, "error": "Username already exists"}))
            return

        users[username] = {
            "password": hash_password(password),
            "display_name": body.get("display_name", username),
            "role": body.get("role", "user"),
            "created": datetime.datetime.now().isoformat(),
        }
        save_users(users)
        self.write(json_encode({"ok": True}))


class UserDeleteHandler(BaseHandler):
    def post(self):
        if AUTH_ENABLED:
            current = self.get_current_user()
            users = load_users()
            if users.get(current, {}).get("role") != "admin" and current != "local":
                self.set_status(403)
                self.write(json_encode({"ok": False, "error": "Admin only"}))
                return

        body = json_decode(self.request.body)
        username = body.get("username", "")
        if username == "admin":
            self.write(json_encode({"ok": False, "error": "Cannot delete the admin account"}))
            return

        users = load_users()
        if username in users:
            del users[username]
            save_users(users)
        self.write(json_encode({"ok": True}))


# ─────────────────────────────────────────────
# STATIC TEMPLATE (inline HTML - no file deps)
# ─────────────────────────────────────────────

MAIN_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Structures America + Titan Carports Calculator v2.6</title>
<style>
:root {
  --sa-dark:#1A1A2E; --sa-blue:#1F4E79; --sa-blue-m:#2E75B6;
  --sa-blue-l:#DEEAF1; --sa-red:#C00000; --sa-gold:#FFC000;
  --sa-green:#375623; --sa-gray:#404040; --sa-light:#F5F7FA;
  --sa-white:#ffffff; --sa-border:#D0D7E2;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:var(--sa-light);color:var(--sa-gray);font-size:13px}
/* Topbar */
#topbar{background:var(--sa-dark);color:#fff;padding:0 20px;display:flex;align-items:center;height:52px;box-shadow:0 2px 8px #0005}
#topbar .logo{font-size:18px;font-weight:700;letter-spacing:1px;color:#fff}
#topbar .logo span{color:var(--sa-red)}
#topbar .subtitle{font-size:11px;color:#aaa;margin-left:16px;margin-top:2px}
#topbar .spacer{flex:1}
#topbar .version{font-size:10px;color:#666}
/* Tabs */
#tabs{background:var(--sa-blue);display:flex;overflow-x:auto}
.tab{padding:10px 20px;color:#aac;cursor:pointer;font-size:12px;font-weight:600;border-bottom:3px solid transparent;white-space:nowrap;transition:all .2s}
.tab:hover{color:#fff;background:rgba(255,255,255,.07)}
.tab.active{color:#fff;border-bottom-color:var(--sa-gold)}
/* Main layout */
#main{display:flex;gap:0;height:calc(100vh - 94px)}
#sidebar{width:310px;min-width:260px;background:#fff;border-right:1px solid var(--sa-border);overflow-y:auto;padding:16px;flex-shrink:0}
#content{flex:1;overflow-y:auto;padding:20px}
/* Cards */
.card{background:#fff;border:1px solid var(--sa-border);border-radius:8px;margin-bottom:16px;overflow:hidden}
.card-hdr{background:var(--sa-blue-m);color:#fff;padding:8px 14px;font-weight:700;font-size:12px;display:flex;align-items:center;gap:8px}
.card-hdr .icon{font-size:15px}
.card-body{padding:14px}
/* Form elements */
.form-group{margin-bottom:12px}
label{display:block;font-size:11px;font-weight:600;color:var(--sa-blue);margin-bottom:4px;text-transform:uppercase;letter-spacing:.4px}
input[type=text],input[type=number],select,textarea{
  width:100%;padding:7px 10px;border:1px solid var(--sa-border);border-radius:4px;
  font-size:13px;color:var(--sa-gray);background:#fff;transition:border .2s}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--sa-blue-m);box-shadow:0 0 0 3px #2E75B615}
input[type=checkbox]{width:auto;margin-right:6px}
.check-label{display:flex;align-items:center;font-size:12px;font-weight:400;text-transform:none;letter-spacing:0;cursor:pointer}
/* Buttons */
.btn{padding:8px 16px;border:none;border-radius:4px;cursor:pointer;font-size:13px;font-weight:600;transition:all .2s;display:inline-flex;align-items:center;gap:6px}
.btn-primary{background:var(--sa-blue);color:#fff}.btn-primary:hover{background:var(--sa-blue-m)}
.btn-red{background:var(--sa-red);color:#fff}.btn-red:hover{opacity:.9}
.btn-green{background:var(--sa-green);color:#fff}.btn-green:hover{opacity:.9}
.btn-gold{background:var(--sa-gold);color:var(--sa-dark)}.btn-gold:hover{opacity:.9}
.btn-outline{background:transparent;border:1px solid var(--sa-blue-m);color:var(--sa-blue-m)}.btn-outline:hover{background:var(--sa-blue-l)}
.btn-sm{padding:5px 11px;font-size:12px}
.btn-group{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
/* Tables */
.bom-table{width:100%;border-collapse:collapse;font-size:12px}
.bom-table th{background:var(--sa-blue);color:#fff;padding:7px 10px;text-align:left;font-weight:600;font-size:11px;position:sticky;top:0}
.bom-table td{padding:6px 10px;border-bottom:1px solid #EEF0F4}
.bom-table tr:nth-child(even) td{background:#F7F9FC}
.bom-table tr:hover td{background:var(--sa-blue-l)}
.cat-row td{background:var(--sa-blue-l)!important;font-weight:700;color:var(--sa-blue);font-size:11px;text-transform:uppercase;letter-spacing:.4px}
.total-row td{background:var(--sa-green)!important;color:#fff!important;font-weight:700}
.sell-row td{background:var(--sa-red)!important;color:#fff!important;font-weight:700;font-size:13px}
/* Summary stats */
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:16px}
.stat-card{background:#fff;border:1px solid var(--sa-border);border-radius:6px;padding:12px 14px;text-align:center}
.stat-label{font-size:10px;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}
.stat-value{font-size:18px;font-weight:700;color:var(--sa-blue)}
.stat-unit{font-size:10px;color:#aaa;margin-top:2px}
/* Building list */
.bldg-item{background:#F7F9FC;border:1px solid var(--sa-border);border-radius:5px;padding:10px 12px;margin-bottom:8px;cursor:pointer;transition:all .2s}
.bldg-item:hover,.bldg-item.active{background:var(--sa-blue-l);border-color:var(--sa-blue-m)}
.bldg-item .bldg-name{font-weight:700;color:var(--sa-blue);font-size:13px}
.bldg-item .bldg-dims{font-size:11px;color:#888;margin-top:2px}
/* Inventory */
.inv-table{width:100%;border-collapse:collapse;font-size:12px}
.inv-table th{background:var(--sa-dark);color:#fff;padding:7px 10px;font-size:11px;text-align:left}
.inv-table td{padding:6px 10px;border-bottom:1px solid #EEF0F4}
.inv-table tr:nth-child(even) td{background:#F7F9FC}
.stock-ok{color:#375623;font-weight:700}
.stock-low{color:orange;font-weight:700}
.stock-out{color:var(--sa-red);font-weight:700}
/* Labels preview */
.labels-wrap{display:flex;flex-wrap:wrap;gap:8px}
/* Alerts */
.alert{padding:10px 14px;border-radius:4px;margin-bottom:12px;font-size:12px}
.alert-info{background:#EEF5FF;border:1px solid #BDD6EE;color:#1F4E79}
.alert-success{background:#E8F5E9;border:1px solid #A5D6A7;color:#2E7D32}
.alert-warn{background:#FFF8E1;border:1px solid #FFE082;color:#E65100}
.alert-error{background:#FFEBEE;border:1px solid #EF9A9A;color:#B71C1C}
/* Section headers */
.section-hdr{font-size:14px;font-weight:700;color:var(--sa-blue);margin-bottom:12px;padding-bottom:6px;border-bottom:2px solid var(--sa-blue-l)}
/* Spinner */
.spinner{display:none;width:20px;height:20px;border:3px solid #ddd;border-top-color:var(--sa-blue-m);border-radius:50%;animation:spin .8s linear infinite;margin:auto}
@keyframes spin{to{transform:rotate(360deg)}}
/* Hidden */
.hidden{display:none}
/* Responsive tweaks */
@media(max-width:768px){#main{flex-direction:column}#sidebar{width:100%;border-right:none;border-bottom:1px solid var(--sa-border)}}
</style>
</head>
<body>

<!-- Topbar -->
<div id="topbar">
  <!-- SA Eagle Logo -->
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 220" width="38" height="38" style="margin-right:10px;flex-shrink:0">
    <polygon points="110,105 20,15 55,80" fill="#aaaaaa"/><polygon points="20,15 55,80 5,60" fill="#cccccc"/>
    <polygon points="5,60 20,15 0,35" fill="#dddddd"/>
    <polygon points="110,105 55,80 45,115" fill="#777777"/><polygon points="55,80 20,15 30,90" fill="#999999"/>
    <polygon points="110,105 45,115 65,130" fill="#666666"/>
    <polygon points="110,105 200,15 165,80" fill="#aaaaaa"/><polygon points="200,15 165,80 215,60" fill="#cccccc"/>
    <polygon points="215,60 200,15 220,35" fill="#dddddd"/>
    <polygon points="110,105 165,80 175,115" fill="#777777"/><polygon points="165,80 200,15 190,90" fill="#999999"/>
    <polygon points="110,105 175,115 155,130" fill="#666666"/>
    <polygon points="95,95 110,70 125,95 110,145" fill="#eeeeee"/>
    <polygon points="100,72 110,55 120,72 110,85" fill="#dddddd"/>
  </svg>
  <div>
    <div class="logo">STRUCTURES <span>AMERICA</span></div>
    <div class="subtitle">Material Takeoff Calculator</div>
  </div>
  <div class="spacer"></div>
  <!-- App Switcher -->
  <div style="display:flex;gap:6px;align-items:center;margin-right:18px">
    <div style="background:rgba(255,255,255,.18);border-radius:4px;padding:5px 12px;font-size:11px;font-weight:700;color:#fff;letter-spacing:.5px">⚙️ SA CALC</div>
    <a href="/tc" style="background:rgba(192,0,0,.25);border:1px solid rgba(192,0,0,.5);border-radius:4px;padding:5px 12px;font-size:11px;font-weight:700;color:#ffaaaa;text-decoration:none;letter-spacing:.5px">🏗️ TC QUOTE →</a>
  </div>
  <!-- TC Logo -->
  <div style="border-left:1px solid #333;padding-left:16px;display:flex;align-items:center;gap:8px;flex-shrink:0">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 180" width="80" height="36" style="flex-shrink:0">
      <polygon points="120,155 80,10 108,148 118,155" fill="#888"/><polygon points="80,10 108,148 90,12" fill="#aaa"/>
      <polygon points="140,155 180,10 152,148 142,155" fill="#888"/><polygon points="180,10 152,148 170,12" fill="#aaa"/>
      <polygon points="118,155 142,155 130,175" fill="#777"/>
      <text x="200" y="85" font-family="Arial Black,Arial" font-weight="900" font-size="62" letter-spacing="4" fill="#888">TITAN</text>
      <text x="200" y="148" font-family="Arial Black,Arial" font-weight="900" font-size="44" letter-spacing="3" fill="#C00000">CARPORTS</text>
    </svg>
  </div>
  <div class="version" style="margin-left:12px">v2.6</div>
  <div id="auth-controls" style="margin-left:auto;display:flex;gap:8px;align-items:center">
    <a href="/admin" style="color:#C89A2E;font-size:11px;font-weight:700;text-decoration:none" title="User Management">👤 Admin</a>
    <a href="/auth/logout" style="background:rgba(155,28,28,.5);border:1px solid rgba(155,28,28,.7);border-radius:4px;padding:4px 10px;font-size:10px;font-weight:700;color:#ffaaaa;text-decoration:none">Log Out</a>
  </div>
</div>

<!-- Tabs -->
<div id="tabs">
  <div class="tab active" onclick="showTab('calc')">⚙️ Calculator</div>
  <div class="tab" onclick="showTab('bom')">📋 Bill of Materials</div>
  <div class="tab" onclick="showTab('pricing')">💰 Price Overrides</div>
  <div class="tab" onclick="showTab('labels')">🏷️ Shop Labels</div>
  <div class="tab" onclick="showTab('inventory')">📦 Inventory</div>
</div>

<!-- Main -->
<div id="main">

  <!-- SIDEBAR: Project + Building Setup -->
  <div id="sidebar">

    <!-- Recent Projects -->
    <div class="card">
      <div class="card-hdr" style="background:var(--sa-gold);color:var(--sa-dark)"><span class="icon">📂</span>Projects</div>
      <div class="card-body" style="padding:10px 14px">
        <div style="display:flex;gap:6px;align-items:center">
          <select id="recent_projects" style="flex:1;font-size:12px;padding:5px 8px" onchange="loadProject(this.value)">
            <option value="">— Recent Projects —</option>
          </select>
          <button class="btn btn-primary btn-sm" onclick="loadRecentProjects()" title="Refresh list" style="padding:5px 8px">🔄</button>
        </div>
        <div style="display:flex;gap:6px;margin-top:6px">
          <button class="btn btn-green btn-sm" style="flex:1;font-size:11px" onclick="saveProjectManual()">💾 Save Project</button>
        </div>
      </div>
    </div>

    <!-- Project Info -->
    <div class="card">
      <div class="card-hdr"><span class="icon">📁</span>Project Info</div>
      <div class="card-body">
        <div class="form-group">
          <label>Project Name</label>
          <input type="text" id="proj_name" placeholder="e.g. Bluegate Boat & RV" oninput="updateJobCode()"/>
        </div>
        <div class="form-group">
          <label>Customer Name</label>
          <input type="text" id="proj_customer" placeholder="Customer / Owner"/>
        </div>
        <div class="form-group">
          <label>Site Address</label>
          <input type="text" id="proj_address" placeholder="123 Main St"/>
        </div>
        <div style="display:grid;grid-template-columns:2fr 1fr 1fr;gap:8px">
          <div class="form-group">
            <label>City</label>
            <input type="text" id="proj_city" placeholder="City" oninput="updateJobCode()"/>
          </div>
          <div class="form-group">
            <label>State</label>
            <select id="proj_state" onchange="onStateChange()">
              <option value="TX" selected>TX</option>
              <option value="NM">NM</option>
              <option value="CO">CO</option>
              <option value="FL">FL</option>
              <option value="CA">CA</option>
              <option value="AZ">AZ</option>
              <option value="NV">NV</option>
              <option value="OK">OK</option>
              <option value="KS">KS</option>
              <option value="NE">NE</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div class="form-group">
            <label>ZIP</label>
            <input type="text" id="proj_zip" placeholder="77302"/>
          </div>
        </div>
        <div class="form-group">
          <label>Job Code</label>
          <input type="text" id="proj_jobcode" placeholder="e.g. BGATN-24"/>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
          <div class="form-group">
            <label>Wind Speed (MPH)</label>
            <input type="number" id="proj_wind" value="115" min="90" max="200"/>
          </div>
          <div class="form-group">
            <label>Footing Depth (ft)</label>
            <input type="number" id="proj_footing" value="10" min="4" max="25" step="0.5"/>
          </div>
        </div>
        <div class="form-group">
          <label>Markup (%)</label>
          <input type="number" id="proj_markup" value="35" min="0" max="100" step="1"/>
        </div>
        <div class="form-group">
          <label>Quote Date</label>
          <input type="text" id="proj_date" placeholder="MM/DD/YYYY"/>
        </div>
      </div>
    </div>

    <!-- Buildings List -->
    <div class="card">
      <div class="card-hdr"><span class="icon">🏗️</span>Buildings</div>
      <div class="card-body">
        <div id="bldg-list"></div>
        <div class="btn-group">
          <button class="btn btn-primary btn-sm" onclick="addBuilding()">➕ Add Building</button>
          <button class="btn btn-outline btn-sm" onclick="removeBuilding()">🗑️ Remove Last</button>
        </div>
      </div>
    </div>

    <!-- Calculate Button -->
    <div style="margin-bottom:16px">
      <button class="btn btn-red" style="width:100%;padding:12px;font-size:14px" onclick="calculate()">
        ⚡ CALCULATE BOM
      </button>
    </div>

  </div>

  <!-- CONTENT AREA -->
  <div id="content">

    <!-- Calculator Tab -->
    <div id="tab-calc" class="tab-content">
      <div class="section-hdr">Building Configuration</div>
      <div id="bldg-forms"></div>
      <div class="alert alert-info">
        Fill in project info and building dimensions in the sidebar, then click <strong>CALCULATE BOM</strong>.
      </div>
    </div>

    <!-- BOM Tab -->
    <div id="tab-bom" class="tab-content hidden">
      <div id="bom-content">
        <div class="alert alert-info">
          Configure your project and click <strong>CALCULATE BOM</strong> to see results.
        </div>
      </div>
    </div>

    <!-- Price Overrides Tab -->
    <div id="tab-pricing" class="tab-content hidden">
      <div class="section-hdr">Price Overrides & Manual Line Items</div>
      <div id="pricing-content">
        <div class="alert alert-info">
          Run <strong>CALCULATE BOM</strong> first, then use this tab to edit prices per line item,
          add manual items (trim, hardware, freight), and see live totals.
        </div>
      </div>
    </div>

    <!-- Labels Tab -->
    <div id="tab-labels" class="tab-content hidden">
      <div class="section-hdr">Shop Fabrication Labels</div>
      <div class="card">
        <div class="card-hdr"><span class="icon">⚙️</span>Label Settings</div>
        <div class="card-body">
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
            <div class="form-group">
              <label>Destination Site</label>
              <input type="text" id="lbl_destination" placeholder="e.g. Sanford, FL"/>
            </div>
            <div class="form-group">
              <label>Fabricator Name</label>
              <input type="text" id="lbl_fabricator" placeholder="e.g. J. Smith"/>
            </div>
            <div class="form-group">
              <label>QR Base URL</label>
              <input type="text" id="lbl_qr_url" value="https://structuresamerica.com/shop"/>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px">
            <div class="form-group">
              <label>Columns/label</label>
              <input type="number" id="grp_column" value="1" min="1"/>
            </div>
            <div class="form-group">
              <label>Rafters/label</label>
              <input type="number" id="grp_rafter" value="1" min="1"/>
            </div>
            <div class="form-group">
              <label>Purlins/label</label>
              <input type="number" id="grp_purlin" value="1" min="1"/>
            </div>
            <div class="form-group">
              <label>Straps/label</label>
              <input type="number" id="grp_strap" value="10" min="1"/>
            </div>
          </div>
          <div class="btn-group">
            <button class="btn btn-primary" onclick="generateLabels()">🏷️ Generate Labels</button>
            <button class="btn btn-green" onclick="downloadZPL()">⬇️ Download ZPL (Zebra)</button>
            <button class="btn btn-red" onclick="downloadLabelsPDF()">📄 Download PDF (4×6 print-ready)</button>
            <button class="btn btn-outline" onclick="downloadLabelsCSV()">📊 Download CSV (NiceLabel / BarTender)</button>
          </div>
        </div>
      </div>
      <div id="labels-preview"></div>
    </div>

    <!-- Inventory Tab -->
    <div id="tab-inventory" class="tab-content hidden">
      <div class="section-hdr">Inventory Management</div>
      <div id="inventory-content">
        <div class="spinner" id="inv-spinner"></div>
      </div>
    </div>

  </div>
</div>

<script>
// ─────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────
let buildings = [];
let currentBOM = null;
let currentLabels = null;

// ── Price Overrides State ──────────────────
// priceOverrides[bldgIdx][lineIdx] = { cost: number, sell: number }
let priceOverrides = {};
// manualItems: array of { category, description, qty, unit, unit_cost, sell_price, notes }
let manualItems = [];
// Auto-save debounce
let _autoSaveTimer = null;

const WIND_BY_STATE = {TX:115,NM:115,CO:115,FL:140,CA:115,AZ:115,NV:115,OK:130,KS:130,NE:130};
const FOOTING_BY_STATE = {TX:10,NM:10,CO:10,FL:12,CA:10,Default:10};

// Initialize with today's date and one building
window.onload = function() {
  const today = new Date();
  const mm = String(today.getMonth()+1).padStart(2,'0');
  const dd = String(today.getDate()).padStart(2,'0');
  const yyyy = today.getFullYear();
  document.getElementById('proj_date').value = `${mm}/${dd}/${yyyy}`;
  addBuilding();
  renderBuildingList();
  loadRecentProjects();
};

// ─────────────────────────────────────────────
// TABS
// ─────────────────────────────────────────────
function showTab(name) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + name).classList.remove('hidden');
  event.target.classList.add('active');
  if (name === 'inventory') loadInventory();
  if (name === 'pricing') renderPricingTab();
}

// ─────────────────────────────────────────────
// PROJECT
// ─────────────────────────────────────────────
function updateJobCode() {
  const city = document.getElementById('proj_city').value.trim().toUpperCase().replace(/\s+/g,'').slice(0,3);
  const state = document.getElementById('proj_state').value.slice(0,2);
  const yr = new Date().getFullYear() % 100;
  if (city && state) document.getElementById('proj_jobcode').value = `${city}${state}-${yr}`;
}

function onStateChange() {
  const st = document.getElementById('proj_state').value;
  if (WIND_BY_STATE[st]) document.getElementById('proj_wind').value = WIND_BY_STATE[st];
  if (FOOTING_BY_STATE[st]) document.getElementById('proj_footing').value = FOOTING_BY_STATE[st];
  updateJobCode();
}

// ─────────────────────────────────────────────
// BUILDINGS
// ─────────────────────────────────────────────
let bldgCounter = 0;

function addBuilding() {
  bldgCounter++;
  buildings.push({
    id: `B${bldgCounter}`,
    building_id: `B${bldgCounter}`,
    building_name: `Building ${bldgCounter}`,
    type: '2post',
    width_ft: 40,
    // Length mode: 'direct' or 'spaces'
    length_mode: 'direct',
    length_ft: 200,
    n_spaces: 0,
    space_width_ft: 12,    // parking stall width; 0 = legacy equal-overhang
    overhang_mode: 'none', // 'none' or '1space'
    clear_height_ft: 14,
    max_bay_ft: 36,
    pitch_key: '1/4:12',
    // Purlin spacing: null = auto-calc
    purlin_spacing_override: null,
    embedment_ft: 4.333,
    column_buffer_ft: 0.5,
    reinforced: true,
    rebar_col_size: 'auto',
    rebar_beam_size: 'auto',
    straps_per_rafter: 4,
    strap_length_in: 28,
    include_back_wall: false,
    include_end_walls: false,
    include_side_walls: false,
    wall_girt_spacing_override: null,
    include_rafter_rebar: false,
    rebar_rafter_size: '#9',
    include_trim: false,
    include_labor: true,
    welding_cost_per_5000sqft: 300,
    coil_prices: {},
  });
  renderBuildingList();
  renderBuildingForms();
}

function removeLastBuilding() {
  if (buildings.length > 1) {
    buildings.pop();
    // Renumber names if they're still at default
    renderBuildingList();
    renderBuildingForms();
  }
}

function removeBuilding() {
  if (buildings.length > 1) { buildings.pop(); renderBuildingList(); renderBuildingForms(); }
}

function renderBuildingList() {
  const el = document.getElementById('bldg-list');
  el.innerHTML = buildings.map((b,i) => `
    <div class="bldg-item ${i===0?'active':''}" onclick="scrollToBldg('${b.id}')">
      <div class="bldg-name">${b.building_name || b.name || 'Building '+(i+1)}</div>
      <div class="bldg-dims">${b.type.toUpperCase()} · ${b.width_ft}'×${b.length_ft}' · Ht:${b.clear_height_ft}'</div>
    </div>
  `).join('');
}

// Auto-calculate purlin spacing from building width
function autoPurlinSpacing(width_ft) {
  if (width_ft <= 30) return 5.0;
  if (width_ft <= 34.333) return 4.0;
  return 3.5;
}

// Auto-calculate purlin row count
function purlinRowCount(width_ft, spacing_ft) {
  return Math.floor(width_ft / spacing_ft) + 1;
}

// Update purlin display when spacing or width changes
function refreshPurlinDisplay(bid) {
  const b = buildings.find(x => x.id === bid);
  if (!b) return;
  const spacing = b.purlin_spacing_override || autoPurlinSpacing(b.width_ft);
  const rows = purlinRowCount(b.width_ft, spacing);
  const autoEl = document.getElementById(bid+'_purlin_auto');
  const rowEl = document.getElementById(bid+'_purlin_rows');
  if (autoEl) autoEl.textContent = b.purlin_spacing_override
    ? `(manual)`
    : `(auto: ${spacing}' OC for ${b.width_ft}' width)`;
  if (rowEl) rowEl.textContent = `${rows} rows`;
}

// Update length when spaces mode is used
function refreshLength(bid) {
  const b = buildings.find(x => x.id === bid);
  if (!b) return;
  if (b.length_mode === 'spaces' && b.n_spaces > 0 && b.space_width_ft > 0) {
    b.length_ft = b.n_spaces * b.space_width_ft;
    const el = document.getElementById(bid+'_length_calc');
    if (el) el.textContent = `= ${b.length_ft}' total`;
    const lenEl = document.getElementById(bid+'_length_display');
    if (lenEl) lenEl.textContent = b.length_ft + "'";
  }
}

function scrollToBldg(id) {
  const el = document.getElementById('bldg-form-'+id);
  if (el) el.scrollIntoView({behavior:'smooth'});
}

function renderBuildingForms() {
  const container = document.getElementById('bldg-forms');
  container.innerHTML = buildings.map(b => buildingFormHTML(b)).join('');
}

// ─────────────────────────────────────────────
// SPACE-BASED COLUMN LAYOUT PREVIEW
// ─────────────────────────────────────────────
function previewColumnLayout(b) {
  const sw = parseFloat(b.space_width_ft) || 0;
  if (sw <= 0) return { positions: null, warning: null, summary: null };

  const length = parseFloat(b.length_ft) || 0;
  const maxBay = parseFloat(b.max_bay_ft) || 36;
  const maxSpPerBay = Math.min(3, Math.max(1, Math.floor(maxBay / sw)));
  const nTotal = Math.round(length / sw);
  const remainder = length % sw;

  const warning = remainder > 0.01
    ? `⚠ ${length}' ÷ ${sw}' = ${(length/sw).toFixed(2)} spaces (not a whole number). Nearest clean length: ${Math.round(length/sw)*sw}'.`
    : null;

  let interiorSpaces, overhang;
  if (b.overhang_mode === '1space') {
    overhang = sw;
    interiorSpaces = Math.max(1, nTotal - 2);
  } else {
    overhang = 0;
    interiorSpaces = nTotal;
  }

  // Build bays
  const nFull = Math.floor(interiorSpaces / maxSpPerBay);
  const shortSp = interiorSpaces % maxSpPerBay;
  const fullBay = maxSpPerBay * sw;
  let bays = [];
  if (shortSp === 0) {
    bays = Array(nFull).fill(fullBay);
  } else {
    const shortBay = shortSp * sw;
    const total = nFull + 1;
    const ci = Math.floor(total / 2);
    for (let i = 0; i < total; i++) bays.push(i === ci ? shortBay : fullBay);
  }

  // Build positions
  let pos = [overhang];
  for (const bay of bays) pos.push(+(pos[pos.length-1] + bay).toFixed(2));

  const bayDesc = [...new Set(bays)].map(bay => {
    const cnt = bays.filter(x => x === bay).length;
    return `${cnt}×${bay}'`;
  }).join(', ');

  const summary = `${pos.length} frames  ·  ${bays.length} bays (${bayDesc})  ·  overhang ${overhang}' each end`;
  const posStr = pos.map(p => p + "'").join(' — ');

  return { positions: posStr, warning, summary };
}

function buildingFormHTML(b) {
  const autoSpacing = autoPurlinSpacing(b.width_ft);
  const effSpacing = b.purlin_spacing_override || autoSpacing;
  const rows = purlinRowCount(b.width_ft, effSpacing);
  const spacingLabel = b.purlin_spacing_override
    ? `(manual)` : `(auto for ${b.width_ft}' width)`;
  const bname = b.building_name || b.name || b.id;

  return `
  <div class="card" id="bldg-form-${b.id}">
    <div class="card-hdr" style="background:var(--sa-blue)"><span class="icon">🏗️</span>
      <input type="text" id="${b.id}_bname" value="${bname}"
        style="background:transparent;border:none;color:#fff;font-weight:700;font-size:13px;width:200px"
        onchange="updateBldg('${b.id}','building_name',this.value)"/>
      <span style="margin-left:auto;font-size:11px;opacity:.7">${b.id}</span>
    </div>
    <div class="card-body">

      <!-- Row 1: Type, Pitch, Width, Clear Height -->
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;margin-bottom:10px">
        <div class="form-group">
          <label>Column Type</label>
          <select onchange="updateBldg('${b.id}','type',this.value)">
            <option value="2post" ${b.type==='2post'?'selected':''}>2-Post</option>
            <option value="tee" ${b.type==='tee'?'selected':''}>Tee (Center Col)</option>
          </select>
        </div>
        <div class="form-group">
          <label>Roof Pitch</label>
          <select onchange="updateBldg('${b.id}','pitch_key',this.value)">
            <option value="1/4:12" ${(b.pitch_key||'1/4:12')==='1/4:12'?'selected':''}>1/4":12 (1.2 deg)</option>
            <option value="5deg" ${b.pitch_key==='5deg'?'selected':''}>5 degrees</option>
            <option value="7.5deg" ${b.pitch_key==='7.5deg'?'selected':''}>7.5 degrees</option>
            <option value="10deg" ${b.pitch_key==='10deg'?'selected':''}>10 degrees</option>
          </select>
        </div>
        <div class="form-group">
          <label>Clear Height (ft)</label>
          <input type="number" value="${b.clear_height_ft}" min="8" max="30" step="0.5"
            onchange="updateBldg('${b.id}','clear_height_ft',parseFloat(this.value))"/>
        </div>
        <div class="form-group">
          <label>Max Bay Size (ft)</label>
          <input type="number" value="${b.max_bay_ft}" min="10" max="60" step="0.5"
            onchange="updateBldg('${b.id}','max_bay_ft',parseFloat(this.value))"/>
        </div>
      </div>

      <!-- Row 2: Width + Length + Column Layout -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
        <div class="form-group">
          <label>Building Width (ft)</label>
          <input type="number" value="${b.width_ft}" min="10" max="200" step="0.5"
            onchange="updateBldg('${b.id}','width_ft',parseFloat(this.value));refreshPurlinDisplay('${b.id}')"/>
        </div>

        <!-- Length mode selector -->
        <div class="form-group">
          <label>Building Length</label>
          <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
            <select style="width:110px" onchange="updateBldg('${b.id}','length_mode',this.value);renderBuildingForms()">
              <option value="direct" ${(b.length_mode||'direct')==='direct'?'selected':''}>Direct (ft)</option>
              <option value="spaces" ${b.length_mode==='spaces'?'selected':''}>Spaces</option>
            </select>
            ${b.length_mode==='spaces' ? `
              <input type="number" placeholder="# spaces" value="${b.n_spaces||''}" min="1" max="500" step="1"
                style="width:80px"
                onchange="updateBldg('${b.id}','n_spaces',parseInt(this.value));refreshLength('${b.id}');renderBuildingForms()"/>
              <span style="font-size:11px">×</span>
              <input type="number" placeholder="ft/space" value="${b.space_width_ft||12}" min="1" step="0.5"
                style="width:70px"
                onchange="updateBldg('${b.id}','space_width_ft',parseFloat(this.value));refreshLength('${b.id}');renderBuildingForms()"/>
              <span id="${b.id}_length_calc" style="font-size:11px;color:var(--sa-blue-m);font-weight:700">
                = ${(b.n_spaces||0)*(b.space_width_ft||12)}' total
              </span>
            ` : `
              <input type="number" value="${b.length_ft}" min="10" max="5000" step="1"
                style="width:100px"
                onchange="updateBldg('${b.id}','length_ft',parseFloat(this.value));renderBuildingForms()"/>
              <span style="font-size:11px;color:#888">ft</span>
            `}
          </div>
        </div>
      </div>

      <!-- Column Placement (Overhang + Space Width) -->
      ${(() => {
        const sw = parseFloat(b.space_width_ft) || 0;
        const layout = previewColumnLayout(b);
        const showSpaceWidth = b.length_mode === 'spaces' || b.overhang_mode === '1space';
        return `
      <div style="background:#F0F7FF;border:1px solid #BDD6EE;border-radius:6px;padding:10px;margin-bottom:10px">
        <div style="font-size:11px;font-weight:700;color:var(--sa-blue);margin-bottom:8px;text-transform:uppercase;letter-spacing:.4px">
          Column Placement
        </div>
        <div style="display:flex;gap:16px;align-items:flex-end;flex-wrap:wrap">
          <div class="form-group" style="margin-bottom:0">
            <label>Overhang Mode</label>
            <select onchange="updateBldg('${b.id}','overhang_mode',this.value);renderBuildingForms()">
              <option value="none" ${(b.overhang_mode||'none')==='none'?'selected':''}>No Overhang</option>
              <option value="1space" ${b.overhang_mode==='1space'?'selected':''}>1 Space Overhang</option>
            </select>
          </div>
          <div class="form-group" style="margin-bottom:0">
            <label>Space Width (ft)</label>
            <input type="number" value="${b.space_width_ft||12}" min="6" max="30" step="0.5"
              style="width:80px"
              onchange="updateBldg('${b.id}','space_width_ft',parseFloat(this.value));renderBuildingForms()"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Parking stall width · 0 = auto</div>
          </div>
        </div>
        ${layout.warning ? `
        <div class="alert alert-warn" style="margin-top:8px;padding:6px 10px;font-size:11px">
          ${layout.warning}
        </div>` : ''}
        ${layout.summary ? `
        <div style="margin-top:8px;font-size:11px;color:var(--sa-blue-m);font-weight:600">
          ${layout.summary}
        </div>
        <div style="font-size:10px;color:#666;margin-top:3px;font-family:monospace;overflow-x:auto;white-space:nowrap">
          Columns: ${layout.positions}
        </div>` : ''}
      </div>`;
      })()}

      <!-- Row 3: Purlin spacing (auto-calc with override) -->
      <div style="background:#F0F4FA;border:1px solid var(--sa-border);border-radius:6px;padding:10px;margin-bottom:10px">
        <div style="font-size:11px;font-weight:700;color:var(--sa-blue);margin-bottom:6px;text-transform:uppercase;letter-spacing:.4px">
          Purlin Spacing
        </div>
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
          <div>
            <span style="font-size:12px">Spacing: </span>
            <input type="number" value="${effSpacing}" min="1" max="10" step="0.5"
              style="width:70px;padding:4px 6px;border:1px solid var(--sa-border);border-radius:4px;font-size:12px"
              onchange="updateBldg('${b.id}','purlin_spacing_override',parseFloat(this.value)||null);refreshPurlinDisplay('${b.id}')"/>
            <span style="font-size:11px;color:#888"> ft OC</span>
            <span id="${b.id}_purlin_auto" style="font-size:10px;color:var(--sa-blue-m);margin-left:4px">${spacingLabel}</span>
          </div>
          <div>
            <span style="font-size:12px">Rows: </span>
            <input type="number" value="${rows}" min="1" max="50" step="1"
              style="width:60px;padding:4px 6px;border:1px solid var(--sa-border);border-radius:4px;font-size:12px"
              onchange="(function(v){const sp=${b.width_ft}/(v-1||1);updateBldg('${b.id}','purlin_spacing_override',parseFloat(sp.toFixed(3)));refreshPurlinDisplay('${b.id}')})(parseInt(this.value))"/>
            <span id="${b.id}_purlin_rows" style="font-size:10px;color:#888"> rows</span>
          </div>
          <button class="btn btn-sm btn-outline" style="font-size:10px;padding:3px 8px"
            onclick="updateBldg('${b.id}','purlin_spacing_override',null);renderBuildingForms()">
            Reset Auto
          </button>
        </div>
      </div>

      <!-- Row 4: Column Details -->
      <details style="margin-bottom:8px">
        <summary style="cursor:pointer;font-size:12px;color:var(--sa-blue-m);font-weight:600;padding:4px 0">
          ▸ Column Details
        </summary>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:10px">
          <div class="form-group">
            <label>Embedment (ft)</label>
            <input type="number" value="${b.embedment_ft||4.333}" min="1" max="15" step="0.083"
              onchange="updateBldg('${b.id}','embedment_ft',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Default: 4'-4" = 4.333'</div>
          </div>
          <div class="form-group">
            <label>Buffer (ft)</label>
            <input type="number" value="${b.column_buffer_ft||0.5}" min="0" max="2" step="0.083"
              onchange="updateBldg('${b.id}','column_buffer_ft',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Default: 6" = 0.5'</div>
          </div>
          <div class="form-group">
            <label>Col Rebar Size</label>
            <select onchange="updateBldg('${b.id}','rebar_col_size',this.value)">
              <option value="auto" ${(!b.rebar_col_size||b.rebar_col_size==='auto')?'selected':''}>Auto</option>
              ${['#5','#6','#7','#8','#9','#10','#11'].map(s=>`<option value="${s}" ${b.rebar_col_size===s?'selected':''}>${s}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label>Beam Rebar Size</label>
            <select onchange="updateBldg('${b.id}','rebar_beam_size',this.value)">
              <option value="auto" ${(!b.rebar_beam_size||b.rebar_beam_size==='auto')?'selected':''}>Auto</option>
              ${['#5','#6','#7','#8','#9','#10','#11'].map(s=>`<option value="${s}" ${b.rebar_beam_size===s?'selected':''}>${s}</option>`).join('')}
            </select>
          </div>
        </div>
        <div style="margin-top:8px">
          <label class="check-label">
            <input type="checkbox" ${(b.reinforced!==false)?'checked':''}
              onchange="updateBldg('${b.id}','reinforced',this.checked)"/>
            Reinforce Columns (rebar = depth + 8') — default
          </label>
          <div style="font-size:10px;color:#888;margin-top:2px;margin-left:20px">
            Unchecked = standard (rebar = depth − embedment)
          </div>
        </div>
      </details>

      <!-- Row 4b: Rafter Details -->
      ${(() => {
        const slopeDeg = {
          '1/4:12': 1.19, '5deg': 5.0, '7.5deg': 7.5, '10deg': 10.0
        }[b.pitch_key||'1/4:12'] || 1.19;
        const halfW = (b.width_ft||40) / 2;
        const slopeRad = slopeDeg * Math.PI / 180;
        const rise = halfW * Math.tan(slopeRad);
        const rafterSlopeFt = 2 * Math.sqrt(halfW*halfW + rise*rise);
        const spliceNeeded = rafterSlopeFt > 53;
        const nRafters = (b.n_frames || 0);
        const nSplice = spliceNeeded ? nRafters * 2 : 0;
        return `
      <details style="margin-bottom:8px">
        <summary style="cursor:pointer;font-size:12px;color:var(--sa-blue-m);font-weight:600;padding:4px 0">
          ▸ Rafter Details
        </summary>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px">
          <div>
            <div style="font-size:11px;font-weight:600;color:var(--sa-blue);text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">Rafter Slope Length</div>
            <div style="font-size:13px;font-weight:700;color:var(--sa-gray)">${rafterSlopeFt.toFixed(2)} ft</div>
            <div style="font-size:10px;color:#888;margin-top:2px">${b.width_ft||40}' wide @ ${slopeDeg}°</div>
          </div>
          <div>
            <div style="font-size:11px;font-weight:600;color:var(--sa-blue);text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">Splice Plates</div>
            ${spliceNeeded ? `
            <div style="font-size:12px;font-weight:700;color:var(--sa-red)">AUTO-TRIGGERED</div>
            <div style="font-size:10px;color:#888;margin-top:2px">${rafterSlopeFt.toFixed(1)}' &gt; 53' · ${nSplice} plates (2 per rafter)</div>
            ` : `
            <div style="font-size:12px;color:#4CAF50;font-weight:600">Not needed</div>
            <div style="font-size:10px;color:#888;margin-top:2px">${rafterSlopeFt.toFixed(1)}' ≤ 53'</div>
            `}
          </div>
          <div>
            <div style="font-size:11px;font-weight:600;color:var(--sa-blue);text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">Rebar Size (auto)</div>
            <div style="font-size:13px;font-weight:700;color:var(--sa-gray)" id="${b.id}_rebar_beam_auto">see below</div>
            <div style="font-size:10px;color:#888;margin-top:2px">Wind speed &amp; bay size driven</div>
          </div>
        </div>
        <div style="margin-top:12px;padding-top:10px;border-top:1px solid var(--sa-border)">
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;align-items:start">
            <div class="form-group" style="margin-bottom:0">
              <label>Beam Rebar Size Override</label>
              <select onchange="updateBldg('${b.id}','rebar_beam_size',this.value)">
                <option value="auto" ${(!b.rebar_beam_size||b.rebar_beam_size==='auto')?'selected':''}>Auto</option>
                ${['#5','#6','#7','#8','#9','#10','#11'].map(s=>`<option value="${s}" ${b.rebar_beam_size===s?'selected':''}>${s}</option>`).join('')}
              </select>
            </div>
            <div style="padding-top:18px">
              <label class="check-label">
                <input type="checkbox" ${b.include_rafter_rebar?'checked':''}
                  onchange="updateBldg('${b.id}','include_rafter_rebar',this.checked);renderBuildingForms()"/>
                Include Rafter Rebar
              </label>
              <div style="font-size:10px;color:#888;margin-top:3px;margin-left:20px">
                Diagonal C-section reinforcement inside rafters
              </div>
            </div>
            ${b.include_rafter_rebar ? `
            <div class="form-group" style="margin-bottom:0">
              <label>Rafter Rebar Size</label>
              <select onchange="updateBldg('${b.id}','rebar_rafter_size',this.value)">
                ${['#5','#6','#7','#8','#9','#10','#11'].map(s=>`<option value="${s}" ${(b.rebar_rafter_size||'#9')===s?'selected':''}>${s}</option>`).join('')}
              </select>
            </div>` : '<div></div>'}
          </div>
        </div>
      </details>`;
      })()}

      <!-- Row 5: Hardware & Connections -->
      <details style="margin-bottom:8px">
        <summary style="cursor:pointer;font-size:12px;color:var(--sa-blue-m);font-weight:600;padding:4px 0">
          ▸ Hardware & Connections
        </summary>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px">
          <div class="form-group">
            <label>Rafter-to-Purlin Straps/Rafter</label>
            <input type="number" value="${b.straps_per_rafter||4}" min="0" max="20"
              onchange="updateBldg('${b.id}','straps_per_rafter',parseInt(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">1 purlin in from each eave × 2 = 4 default</div>
          </div>
          <div class="form-group">
            <label>Strap Length (in)</label>
            <input type="number" value="${b.strap_length_in||28}" min="12" max="60"
              onchange="updateBldg('${b.id}','strap_length_in',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Default: 28"</div>
          </div>
          <div class="form-group">
            <label>Welding Consumables ($/5,000 sqft)</label>
            <input type="number" value="${b.welding_cost_per_5000sqft||300}" min="0" step="10"
              onchange="updateBldg('${b.id}','welding_cost_per_5000sqft',parseFloat(this.value))"/>
            <div style="font-size:10px;color:#888;margin-top:2px">Wire, gas, cold galvanize paint</div>
          </div>
        </div>
        <div style="display:flex;gap:20px;margin-top:8px;flex-wrap:wrap">
          <label class="check-label">
            <input type="checkbox" ${b.include_trim?'checked':''}
              onchange="updateBldg('${b.id}','include_trim',this.checked)"/>
            Include Trim (J-Channel)
          </label>
          <label class="check-label">
            <input type="checkbox" ${b.include_labor?'checked':''}
              onchange="updateBldg('${b.id}','include_labor',this.checked)"/>
            Include Fabrication Labor
          </label>
        </div>
      </details>

      <!-- Row 5b: Wall Options -->
      <details style="margin-bottom:8px">
        <summary style="cursor:pointer;font-size:12px;color:var(--sa-blue-m);font-weight:600;padding:4px 0">
          ▸ Wall Panels & Girts
        </summary>
        <div style="font-size:10px;color:#888;margin-bottom:8px;margin-top:6px">
          Wall height = clear height + 1'-8" (rafter + purlin − ground clearance). End walls use peak height.
          Girt spacing matches roof purlin auto-calc unless overridden.
        </div>
        <div style="display:flex;gap:20px;margin-bottom:10px;flex-wrap:wrap">
          <label class="check-label">
            <input type="checkbox" ${b.include_back_wall?'checked':''}
              onchange="updateBldg('${b.id}','include_back_wall',this.checked)"/>
            Back Wall (1 long rear wall)
          </label>
          <label class="check-label">
            <input type="checkbox" ${b.include_end_walls?'checked':''}
              onchange="updateBldg('${b.id}','include_end_walls',this.checked)"/>
            End Walls (2 short gable ends)
          </label>
          <label class="check-label">
            <input type="checkbox" ${b.include_side_walls?'checked':''}
              onchange="updateBldg('${b.id}','include_side_walls',this.checked)"/>
            Side Walls (both long sides)
          </label>
        </div>
        <div class="form-group" style="max-width:220px">
          <label>Wall Girt Spacing Override (ft OC)</label>
          <input type="number" placeholder="Leave blank = auto (same as roof)" min="1" max="10" step="0.5"
            value="${b.wall_girt_spacing_override||''}"
            onchange="updateBldg('${b.id}','wall_girt_spacing_override',parseFloat(this.value)||null)"/>
        </div>
        </div>
      </details>

      <!-- Row 6: Coil Price Overrides -->
      <details>
        <summary style="cursor:pointer;font-size:12px;color:var(--sa-blue-m);font-weight:600;padding:4px 0">
          ▸ Price/LB Overrides (leave blank to use defaults)
        </summary>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:10px">
          ${[
            ['c_section_23','C1: 23" 10GA','0.82'],
            ['z_purlin_20','C2: 12GA Purlin','0.82'],
            ['angle_4_16ga','C3: 16GA Angle','0.86'],
            ['spartan_rib_48','C4: 29GA Panel','0.795'],
            ['plate_6_10ga','C5: 10GA Plate 6"','0.82'],
            ['plate_9_10ga','C6: 10GA Plate 9"','0.82'],
            ['strap_15_10ga','C7: 10GA Strap','0.82'],
          ].map(([cid,lbl,def]) => `
          <div class="form-group">
            <label style="font-size:10px">${lbl}</label>
            <div style="display:flex;align-items:center;gap:4px">
              <span style="font-size:11px">$</span>
              <input type="number" placeholder="${def}" min="0" step="0.001"
                value="${(b.coil_prices&&b.coil_prices[cid])||''}"
                style="width:70px"
                onchange="(function(v){if(!b.coil_prices)b.coil_prices={};updateBldgCoilPrice('${b.id}','${cid}',v)})(this.value)"/>
              <span style="font-size:10px;color:#888">/lb</span>
            </div>
          </div>`).join('')}
        </div>
      </details>

    </div>
  </div>`;
}

function updateBldg(id, field, value) {
  const b = buildings.find(x => x.id === id);
  if (b) {
    b[field] = value;
    // Keep legacy 'name' in sync with building_name
    if (field === 'building_name') b.name = value;
  }
  renderBuildingList();
}

function updateBldgCoilPrice(id, coilId, val) {
  const b = buildings.find(x => x.id === id);
  if (!b) return;
  if (!b.coil_prices) b.coil_prices = {};
  if (val === '' || val === null) {
    delete b.coil_prices[coilId];
  } else {
    b.coil_prices[coilId] = parseFloat(val);
  }
}

// ─────────────────────────────────────────────
// CALCULATE
// ─────────────────────────────────────────────
async function calculate() {
  const project = {
    name: document.getElementById('proj_name').value || 'Project',
    job_code: document.getElementById('proj_jobcode').value || 'PROJ-00',
    address: document.getElementById('proj_address').value || '',
    city: document.getElementById('proj_city').value || '',
    state: document.getElementById('proj_state').value,
    zip_code: document.getElementById('proj_zip').value || '',
    customer_name: document.getElementById('proj_customer').value || '',
    quote_date: document.getElementById('proj_date').value || '',
    wind_speed_mph: parseFloat(document.getElementById('proj_wind').value) || 115,
    footing_depth_ft: parseFloat(document.getElementById('proj_footing').value) || 10,
    markup_pct: parseFloat(document.getElementById('proj_markup').value) || 35,
  };

  const payload = { project, buildings };

  try {
    const res = await fetch('/api/calculate', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (data.error) {
      alert('Calculation error: ' + data.error);
      return;
    }
    currentBOM = data;
    priceOverrides = {};  // Reset overrides on new calc
    renderBOM(data);
    renderPricingTab();
    // Switch to BOM tab
    document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-bom').classList.remove('hidden');
    document.querySelectorAll('.tab')[1].classList.add('active');
  } catch(e) {
    alert('Error: ' + e.message);
  }
}

// ─────────────────────────────────────────────
// RENDER BOM
// ─────────────────────────────────────────────
function renderBOM(data) {
  const el = document.getElementById('bom-content');

  const totalLaborSell = data.total_labor_sell_price || 0;
  const totalFabDays = data.total_labor_days || 0;
  let html = `
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-label">Project</div>
      <div class="stat-value" style="font-size:14px">${data.project.name || '—'}</div>
      <div class="stat-unit">${data.project.job_code || ''}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Total Weight</div>
      <div class="stat-value">${(data.total_weight_lbs||0).toLocaleString()}</div>
      <div class="stat-unit">LBS</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Material Cost</div>
      <div class="stat-value" style="color:var(--sa-green)">$${(data.total_material_cost||0).toLocaleString('en-US',{minimumFractionDigits:2})}</div>
      <div class="stat-unit">before markup</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Total Sell Price</div>
      <div class="stat-value" style="color:var(--sa-red)">$${(data.total_sell_price||0).toLocaleString('en-US',{minimumFractionDigits:2})}</div>
      <div class="stat-unit">materials + labor</div>
    </div>
    ${totalLaborSell > 0 ? `
    <div class="stat-card">
      <div class="stat-label">Fabrication Labor</div>
      <div class="stat-value" style="color:var(--sa-blue)">$${totalLaborSell.toLocaleString('en-US',{minimumFractionDigits:2})}</div>
      <div class="stat-unit">incl. 10% overhead + markup</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Est. Fab Days</div>
      <div class="stat-value" style="color:var(--sa-blue)">${totalFabDays}</div>
      <div class="stat-unit">shop days (4-man crew)</div>
    </div>
    ` : ''}
    <div class="stat-card">
      <div class="stat-label">Buildings</div>
      <div class="stat-value">${data.buildings.length}</div>
      <div class="stat-unit">total structures</div>
    </div>
  </div>

  <div class="btn-group" style="margin-bottom:16px">
    <button class="btn btn-green" onclick="downloadExcel()">📊 Download Excel BOM</button>
    <button class="btn btn-red" onclick="downloadPDF()">📄 Download PDF Quote</button>
    <button class="btn btn-primary" onclick="saveProjectManual()">💾 Save Project</button>
    <button class="btn btn-gold" style="margin-left:auto" onclick="sendToTCQuote()">🏗️ Send to TC Construction Quote →</button>
  </div>
  `;

  // Per building
  for (let bi = 0; bi < data.buildings.length; bi++) {
    const bldg = data.buildings[bi];
    const geo = bldg.geometry || {};
    const bldgLabel = bldg.building_name || ('Building ' + (bi + 1));
    const purlinAuto = geo.purlin_auto ? ' (auto)' : ' (override)';
    html += `
    <div class="card" style="margin-bottom:20px">
      <div class="card-hdr" style="background:var(--sa-blue)">
        <span class="icon">🏗️</span>
        ${bldgLabel} — ${(bldg.type||'').toUpperCase()}
        <span style="margin-left:auto;font-size:11px;opacity:.85">
          ${bldg.width_ft}' × ${bldg.length_ft}' &nbsp;|&nbsp;
          ${geo.n_frames || '—'} frames · ${geo.n_bays || '—'} bays · bay=${geo.bay_size_ft || '—'}' &nbsp;|&nbsp;
          ${geo.n_struct_cols || '—'} cols · ${geo.n_rafters || '—'} rafters &nbsp;|&nbsp;
          Purlin: ${geo.purlin_spacing_ft || '—'}' OC × ${geo.n_purlin_lines || '—'} lines${purlinAuto} &nbsp;|&nbsp;
          Col Ht: ${geo.col_ht_ft || '—'}' · Pitch: ${geo.slope_deg || '—'}°
        </span>
      </div>
      <div class="card-body" style="padding:0">
        <table class="bom-table">
          <thead>
            <tr>
              <th>Category</th>
              <th>Description</th>
              <th style="text-align:right">Qty</th>
              <th>Unit</th>
              <th style="text-align:right">Wt (LBS)</th>
              <th style="text-align:right">Unit Cost</th>
              <th style="text-align:right">Total Cost</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>`;

    let lastCat = null;
    for (const item of bldg.line_items) {
      if (item.category !== lastCat) {
        lastCat = item.category;
        html += `<tr class="cat-row"><td colspan="8">${item.category}</td></tr>`;
      }
      const qty = typeof item.qty === 'number' ? item.qty.toLocaleString('en-US',{maximumFractionDigits:2}) : item.qty;
      const wt = item.total_weight_lbs ? item.total_weight_lbs.toLocaleString('en-US',{maximumFractionDigits:1}) : '—';
      const uc = item.unit_cost ? '$' + item.unit_cost.toFixed(4) : '—';
      const tc = item.total_cost ? '$' + item.total_cost.toLocaleString('en-US',{minimumFractionDigits:2}) : '—';
      html += `
        <tr>
          <td></td>
          <td>${item.description}</td>
          <td style="text-align:right;font-weight:600">${qty}</td>
          <td>${item.unit}</td>
          <td style="text-align:right">${wt}</td>
          <td style="text-align:right">${uc}</td>
          <td style="text-align:right;font-weight:600">${tc}</td>
          <td style="font-size:10px;color:#888">${item.notes||''}</td>
        </tr>`;
    }

    html += `
          <tr class="total-row">
            <td colspan="4">TOTAL MATERIAL COST</td>
            <td style="text-align:right">${(bldg.total_weight_lbs||0).toLocaleString('en-US',{maximumFractionDigits:0})} LBS</td>
            <td></td>
            <td style="text-align:right">$${(bldg.total_material_cost||0).toLocaleString('en-US',{minimumFractionDigits:2})}</td>
            <td></td>
          </tr>
          ${bldg.labor_sell_price > 0 ? `
          <tr style="background:#EEF5FF!important">
            <td colspan="4" style="color:var(--sa-blue);font-weight:700">
              FABRICATION LABOR
              <span style="font-size:10px;font-weight:400;margin-left:8px;color:#666">
                ${(bldg.geometry.labor||{}).total_fab_days||0} shop days ·
                ${(bldg.geometry.labor||{}).days_columns||0}d columns +
                ${(bldg.geometry.labor||{}).days_rafters||0}d rafters /
                ${(bldg.geometry.labor||{}).days_purlins||0}d purlins /
                ${(bldg.geometry.labor||{}).days_panels||0}d panels /
                ${(bldg.geometry.labor||{}).days_angle||0}d angle
                (max stream = ${(bldg.geometry.labor||{}).box_stream_days||0}d box)
              </span>
            </td>
            <td></td><td></td>
            <td style="text-align:right;color:var(--sa-blue);font-weight:700">$${bldg.labor_raw_cost.toLocaleString('en-US',{minimumFractionDigits:2})}</td>
            <td style="font-size:10px;color:#888">raw (before markup)</td>
          </tr>` : ''}
          <tr class="sell-row">
            <td colspan="6" style="text-align:right">SELL PRICE (materials + labor)</td>
            <td style="text-align:right">$${((bldg.total_sell_price||0)+(bldg.labor_sell_price||0)).toLocaleString('en-US',{minimumFractionDigits:2})}</td>
            <td></td>
          </tr>
        </tbody>
        </table>
      </div>
    </div>`;
  }

  el.innerHTML = html;
}

// ─────────────────────────────────────────────
// SEND TO TC QUOTE
// ─────────────────────────────────────────────
function sendToTCQuote() {
  if (!currentBOM) { alert('Please calculate BOM first.'); return; }
  // Use adjusted totals if price overrides / manual items exist
  const totals = getAdjustedTotals();
  const sellPrice = (Object.keys(priceOverrides).length > 0 || manualItems.length > 0)
    ? totals.grand : (currentBOM.total_sell_price || 0);
  const nCols = (currentBOM.buildings || []).reduce((s, b) => s + (b.geometry?.n_struct_cols || 0), 0);
  const footingDepth = currentBOM.project?.footing_depth_ft || 10;
  const projName = currentBOM.project?.name || '';
  const projCode = currentBOM.project?.job_code || '';
  const width = (currentBOM.buildings || [])[0]?.width_ft || 40;
  const length = (currentBOM.buildings || [])[0]?.length_ft || 180;
  const saQuoteNum = projCode ? 'SA-' + projCode : '';
  const params = new URLSearchParams({
    sa_cost: sellPrice.toFixed(2),
    n_cols: nCols,
    footing: footingDepth,
    proj_name: projName,
    proj_code: projCode,
    sa_quote: saQuoteNum,
    width: width,
    length: length,
  });
  window.open('/tc?' + params.toString(), '_blank');
}

// ─────────────────────────────────────────────
// PRICE OVERRIDES & MANUAL ITEMS
// ─────────────────────────────────────────────

function getAdjustedTotals() {
  // Calculate totals including price overrides and manual items
  if (!currentBOM) return { material: 0, sell: 0, manual: 0, grand: 0 };
  const markup = (parseFloat(document.getElementById('proj_markup')?.value) || 35) / 100;
  let totalMaterial = 0, totalSell = 0;

  for (let bi = 0; bi < currentBOM.buildings.length; bi++) {
    const bldg = currentBOM.buildings[bi];
    for (let li = 0; li < bldg.line_items.length; li++) {
      const item = bldg.line_items[li];
      const key = bi + '_' + li;
      const ov = (priceOverrides[bi] || {})[li];
      if (ov && ov.cost !== undefined) {
        totalMaterial += ov.cost;
        totalSell += (ov.sell !== undefined) ? ov.sell : ov.cost * (1 + markup);
      } else {
        totalMaterial += item.total_cost || 0;
        totalSell += (item.total_cost || 0) * (1 + markup);
      }
    }
    // Add labor
    totalSell += bldg.labor_sell_price || 0;
  }

  // Manual items
  let manualTotal = 0;
  for (const m of manualItems) {
    manualTotal += (m.qty || 0) * (m.sell_price || 0);
  }

  return {
    material: totalMaterial,
    sell: totalSell,
    manual: manualTotal,
    grand: totalSell + manualTotal,
  };
}

function renderPricingTab() {
  const el = document.getElementById('pricing-content');
  if (!currentBOM) {
    el.innerHTML = '<div class="alert alert-info">Run <strong>CALCULATE BOM</strong> first, then use this tab to edit prices.</div>';
    return;
  }

  const markup = (parseFloat(document.getElementById('proj_markup')?.value) || 35) / 100;
  const totals = getAdjustedTotals();

  let html = `
  <div class="stats-grid" id="pricing-summary">
    <div class="stat-card">
      <div class="stat-label">Calculated Material</div>
      <div class="stat-value" style="color:var(--sa-green)">$${(currentBOM.total_material_cost||0).toLocaleString('en-US',{minimumFractionDigits:2})}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Adjusted Material</div>
      <div class="stat-value" style="color:var(--sa-blue)" id="adj-material">$${totals.material.toLocaleString('en-US',{minimumFractionDigits:2})}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Manual Items</div>
      <div class="stat-value" style="color:#7A5C00" id="adj-manual">$${totals.manual.toLocaleString('en-US',{minimumFractionDigits:2})}</div>
    </div>
    <div class="stat-card" style="border:2px solid var(--sa-red)">
      <div class="stat-label">Grand Total (Sell)</div>
      <div class="stat-value" style="color:var(--sa-red)" id="adj-grand">$${totals.grand.toLocaleString('en-US',{minimumFractionDigits:2})}</div>
      <div class="stat-unit">materials + labor + manual</div>
    </div>
  </div>`;

  // Per-building editable table
  for (let bi = 0; bi < currentBOM.buildings.length; bi++) {
    const bldg = currentBOM.buildings[bi];
    const bldgLabel = bldg.building_name || ('Building ' + (bi + 1));
    html += `
    <div class="card" style="margin-bottom:16px">
      <div class="card-hdr" style="background:var(--sa-blue)">
        <span class="icon">🏗️</span> ${bldgLabel} — Price Overrides
      </div>
      <div class="card-body" style="padding:0">
        <table class="bom-table">
          <thead><tr>
            <th>Category</th><th>Description</th>
            <th style="text-align:right">Qty</th><th>Unit</th>
            <th style="text-align:right">Orig Cost</th>
            <th style="text-align:right">New Cost</th>
            <th style="text-align:right">Sell Price</th>
            <th style="text-align:right">Markup %</th>
            <th></th>
          </tr></thead><tbody>`;

    let lastCat = null;
    for (let li = 0; li < bldg.line_items.length; li++) {
      const item = bldg.line_items[li];
      if (item.category !== lastCat) {
        lastCat = item.category;
        html += '<tr class="cat-row"><td colspan="9">' + item.category + '</td></tr>';
      }
      const origCost = item.total_cost || 0;
      const ov = (priceOverrides[bi] || {})[li];
      const isEdited = ov && ov.cost !== undefined;
      const editCost = isEdited ? ov.cost : origCost;
      const editSell = isEdited && ov.sell !== undefined ? ov.sell : editCost * (1 + markup);
      const markupPct = editCost > 0 ? ((editSell / editCost - 1) * 100).toFixed(1) : '—';
      const qty = typeof item.qty === 'number' ? item.qty.toLocaleString('en-US',{maximumFractionDigits:2}) : item.qty;

      html += `<tr${isEdited?' style="background:#FFF8E0"':''}>
        <td></td>
        <td>${item.description}</td>
        <td style="text-align:right">${qty}</td>
        <td>${item.unit}</td>
        <td style="text-align:right;${isEdited?'text-decoration:line-through;color:#bbb':''}">$${origCost.toLocaleString('en-US',{minimumFractionDigits:2})}</td>
        <td style="text-align:right">
          <input type="number" value="${editCost.toFixed(2)}" step="0.01" style="width:100px;padding:3px 6px;font-size:12px;text-align:right;border:1px solid ${isEdited?'#C89A2E':'#ddd'};border-radius:3px"
            onchange="overrideCost(${bi},${li},parseFloat(this.value))" oninput="liveUpdateTotals()"/>
        </td>
        <td style="text-align:right">
          <input type="number" value="${editSell.toFixed(2)}" step="0.01" style="width:100px;padding:3px 6px;font-size:12px;text-align:right;border:1px solid ${isEdited?'#C89A2E':'#ddd'};border-radius:3px"
            onchange="overrideSell(${bi},${li},parseFloat(this.value))" oninput="liveUpdateTotals()"/>
        </td>
        <td style="text-align:right;font-size:11px;color:#888">${markupPct}%</td>
        <td>${isEdited?'<button style="border:none;background:none;cursor:pointer;font-size:14px" title="Reset to calculated" onclick="resetOverride('+bi+','+li+')">↩</button>':''}</td>
      </tr>`;
    }
    html += '</tbody></table></div></div>';
  }

  // ── Manual Line Items Section ──────────────
  html += `
  <div class="card" style="margin-top:16px">
    <div class="card-hdr" style="background:var(--sa-gold);color:#1C1C2E">
      <span class="icon">➕</span> Manual Line Items (Trim, Hardware, Freight, etc.)
    </div>
    <div class="card-body">
      <table class="bom-table" id="manual-items-table">
        <thead><tr>
          <th>Category</th><th>Description</th>
          <th style="text-align:right">Qty</th><th>Unit</th>
          <th style="text-align:right">Unit Price</th>
          <th style="text-align:right">Extended</th>
          <th></th>
        </tr></thead>
        <tbody>`;

  for (let mi = 0; mi < manualItems.length; mi++) {
    const m = manualItems[mi];
    const ext = (m.qty || 0) * (m.sell_price || 0);
    html += `<tr>
      <td>
        <select style="font-size:11px;padding:3px;border:1px solid #ddd;border-radius:3px" onchange="manualItems[${mi}].category=this.value;scheduleSave()">
          <option value="Trim" ${m.category==='Trim'?'selected':''}>Trim</option>
          <option value="Hardware" ${m.category==='Hardware'?'selected':''}>Hardware</option>
          <option value="Freight" ${m.category==='Freight'?'selected':''}>Freight</option>
          <option value="Fasteners" ${m.category==='Fasteners'?'selected':''}>Fasteners</option>
          <option value="Accessories" ${m.category==='Accessories'?'selected':''}>Accessories</option>
          <option value="Other" ${m.category==='Other'?'selected':''}>Other</option>
        </select>
      </td>
      <td><input type="text" value="${(m.description||'').replace(/"/g,'&quot;')}" style="font-size:12px;padding:3px 6px;border:1px solid #ddd;border-radius:3px;width:100%"
        onchange="manualItems[${mi}].description=this.value;scheduleSave()"/></td>
      <td style="text-align:right"><input type="number" value="${m.qty||0}" step="0.01" style="width:70px;font-size:12px;padding:3px 6px;text-align:right;border:1px solid #ddd;border-radius:3px"
        onchange="manualItems[${mi}].qty=parseFloat(this.value)||0;renderPricingTab()" oninput="liveUpdateTotals()"/></td>
      <td>
        <select style="font-size:11px;padding:3px;border:1px solid #ddd;border-radius:3px" onchange="manualItems[${mi}].unit=this.value;scheduleSave()">
          <option value="EA" ${m.unit==='EA'?'selected':''}>EA</option>
          <option value="LF" ${m.unit==='LF'?'selected':''}>LF</option>
          <option value="SQ" ${m.unit==='SQ'?'selected':''}>SQ</option>
          <option value="LOT" ${m.unit==='LOT'?'selected':''}>LOT</option>
          <option value="LBS" ${m.unit==='LBS'?'selected':''}>LBS</option>
        </select>
      </td>
      <td style="text-align:right"><input type="number" value="${(m.sell_price||0).toFixed(2)}" step="0.01" style="width:90px;font-size:12px;padding:3px 6px;text-align:right;border:1px solid #ddd;border-radius:3px"
        onchange="manualItems[${mi}].sell_price=parseFloat(this.value)||0;renderPricingTab()" oninput="liveUpdateTotals()"/></td>
      <td style="text-align:right;font-weight:600">$${ext.toLocaleString('en-US',{minimumFractionDigits:2})}</td>
      <td><button class="btn btn-red btn-sm" style="padding:2px 8px;font-size:11px" onclick="manualItems.splice(${mi},1);renderPricingTab()">✕</button></td>
    </tr>`;
  }

  html += `</tbody></table>
      <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap">
        <button class="btn btn-gold btn-sm" onclick="addManualItem('Trim','','LF')">+ Trim</button>
        <button class="btn btn-gold btn-sm" onclick="addManualItem('Hardware','','EA')">+ Hardware</button>
        <button class="btn btn-gold btn-sm" onclick="addManualItem('Freight','Freight & Delivery','LOT')">+ Freight</button>
        <button class="btn btn-gold btn-sm" onclick="addManualItem('Fasteners','','EA')">+ Fasteners</button>
        <button class="btn btn-outline btn-sm" onclick="addManualItem('Other','','EA')">+ Other</button>
      </div>
    </div>
  </div>`;

  el.innerHTML = html;
}

function overrideCost(bi, li, val) {
  if (!priceOverrides[bi]) priceOverrides[bi] = {};
  const markup = (parseFloat(document.getElementById('proj_markup')?.value) || 35) / 100;
  const existing = priceOverrides[bi][li] || {};
  priceOverrides[bi][li] = { cost: val, sell: existing.sell !== undefined ? existing.sell : val * (1 + markup) };
  scheduleSave();
  // Don't re-render entire tab to preserve focus — just update totals
  liveUpdateTotals();
}

function overrideSell(bi, li, val) {
  if (!priceOverrides[bi]) priceOverrides[bi] = {};
  const existing = priceOverrides[bi][li] || {};
  const item = currentBOM.buildings[bi].line_items[li];
  const cost = existing.cost !== undefined ? existing.cost : (item.total_cost || 0);
  priceOverrides[bi][li] = { cost: cost, sell: val };
  scheduleSave();
  liveUpdateTotals();
}

function resetOverride(bi, li) {
  if (priceOverrides[bi]) {
    delete priceOverrides[bi][li];
    if (Object.keys(priceOverrides[bi]).length === 0) delete priceOverrides[bi];
  }
  scheduleSave();
  renderPricingTab();
}

function addManualItem(category, description, unit) {
  manualItems.push({
    category: category || 'Other',
    description: description || '',
    qty: 1,
    unit: unit || 'EA',
    sell_price: 0,
    notes: '',
  });
  renderPricingTab();
}

function liveUpdateTotals() {
  const totals = getAdjustedTotals();
  const fmt = (n) => '$' + n.toLocaleString('en-US',{minimumFractionDigits:2});
  const matEl = document.getElementById('adj-material');
  const manEl = document.getElementById('adj-manual');
  const grandEl = document.getElementById('adj-grand');
  if (matEl) matEl.textContent = fmt(totals.material);
  if (manEl) manEl.textContent = fmt(totals.manual);
  if (grandEl) grandEl.textContent = fmt(totals.grand);
}

function scheduleSave() {
  clearTimeout(_autoSaveTimer);
  _autoSaveTimer = setTimeout(autoSaveProject, 2000);
}

async function autoSaveProject() {
  if (!currentBOM) return;
  const jobCode = document.getElementById('proj_jobcode')?.value?.trim();
  if (!jobCode) return;
  const payload = {
    job_code: jobCode,
    project: currentBOM.project,
    buildings: buildings,
    bom_data: currentBOM,
    price_overrides: priceOverrides,
    manual_items: manualItems,
  };
  try {
    await fetch('/api/project/save', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload),
    });
    console.log('[AutoSave] Project saved:', jobCode);
  } catch(e) { console.warn('[AutoSave] Failed:', e); }
}

async function saveProjectManual() {
  if (!currentBOM) { alert('Please calculate BOM first.'); return; }
  const jobCode = document.getElementById('proj_jobcode')?.value?.trim();
  if (!jobCode) { alert('Please enter a Job Code first.'); return; }
  await autoSaveProject();
  alert('Project saved: ' + jobCode);
}

async function loadRecentProjects() {
  try {
    const resp = await fetch('/api/projects');
    const data = await resp.json();
    const sel = document.getElementById('recent_projects');
    if (!sel) return;
    sel.innerHTML = '<option value="">— Recent Projects —</option>';
    for (const p of (data.projects || [])) {
      const label = p.job_code + (p.project_name ? ' — ' + p.project_name : '') +
                    (p.saved_at ? ' (' + p.saved_at.slice(0,10) + ')' : '');
      sel.innerHTML += '<option value="' + p.job_code + '">' + label + '</option>';
    }
  } catch(e) { console.warn('Failed to load projects:', e); }
}

async function loadProject(jobCode) {
  if (!jobCode) return;
  try {
    const resp = await fetch('/api/project/load', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ job_code: jobCode }),
    });
    const result = await resp.json();
    if (!result.ok) { alert('Load failed: ' + (result.error||'unknown')); return; }
    const d = result.data;

    // Restore project info fields
    if (d.project) {
      const p = d.project;
      if (p.name) document.getElementById('proj_name').value = p.name;
      if (p.customer_name) document.getElementById('proj_customer').value = p.customer_name;
      if (p.address) document.getElementById('proj_address').value = p.address;
      if (p.city) document.getElementById('proj_city').value = p.city;
      if (p.state) document.getElementById('proj_state').value = p.state;
      if (p.zip_code) document.getElementById('proj_zip').value = p.zip_code;
      if (p.quote_date) document.getElementById('proj_date').value = p.quote_date;
      if (p.wind_speed_mph) document.getElementById('proj_wind').value = p.wind_speed_mph;
      if (p.footing_depth_ft) document.getElementById('proj_footing').value = p.footing_depth_ft;
      if (p.markup_pct) document.getElementById('proj_markup').value = p.markup_pct;
    }
    if (d.job_code) document.getElementById('proj_jobcode').value = d.job_code;

    // Restore buildings
    if (d.buildings && d.buildings.length > 0) {
      buildings = d.buildings;
      bldgCounter = buildings.length;
      renderBuildingList();
      renderBuildingForms();
    }

    // Restore BOM data
    if (d.bom_data) {
      currentBOM = d.bom_data;
      renderBOM(currentBOM);
    }

    // Restore price overrides & manual items
    priceOverrides = d.price_overrides || {};
    manualItems = d.manual_items || [];
    if (currentBOM) renderPricingTab();

    alert('Project loaded: ' + jobCode);
  } catch(e) { alert('Load error: ' + e.message); }
}

// ─────────────────────────────────────────────
// DOWNLOADS
// ─────────────────────────────────────────────
async function downloadExcel() {
  if (!currentBOM) { alert('Please calculate first.'); return; }
  const res = await fetch('/api/excel', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(currentBOM),
  });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `SA_BOM_${currentBOM.project.job_code || 'Quote'}.xlsx`;
  a.click();
}

async function downloadPDF() {
  if (!currentBOM) { alert('Please calculate first.'); return; }
  const res = await fetch('/api/pdf', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(currentBOM),
  });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `SA_Quote_${currentBOM.project.job_code || 'Quote'}.pdf`;
  a.click();
}

// ─────────────────────────────────────────────
// LABELS
// ─────────────────────────────────────────────
async function generateLabels() {
  if (!currentBOM) { alert('Please calculate a BOM first.'); return; }
  const payload = {
    bom: currentBOM,
    destination: document.getElementById('lbl_destination').value,
    fabricator: document.getElementById('lbl_fabricator').value,
    qr_base_url: document.getElementById('lbl_qr_url').value,
    grouping: {
      column: parseInt(document.getElementById('grp_column').value)||1,
      rafter: parseInt(document.getElementById('grp_rafter').value)||1,
      purlin: parseInt(document.getElementById('grp_purlin').value)||1,
      strap: parseInt(document.getElementById('grp_strap').value)||10,
    },
  };
  const res = await fetch('/api/labels', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (data.error) { alert(data.error); return; }
  currentLabels = data;
  document.getElementById('labels-preview').innerHTML = `
    <div class="alert alert-success">✅ Generated ${data.count} labels. ZPL file ready to print on Zebra ZT411.</div>
    <div class="labels-wrap">${data.html}</div>
  `;
}

async function downloadZPL() {
  if (!currentLabels || !currentLabels.zpl) { alert('Please generate labels first.'); return; }
  const blob = new Blob([currentLabels.zpl], {type:'text/plain'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `SA_Labels_${currentBOM?.project?.job_code || 'Job'}.zpl`;
  a.click();
}

async function downloadLabelsPDF() {
  if (!currentBOM) { alert('Please calculate BOM first, then generate labels.'); return; }
  const payload = buildLabelsPayload();
  const res = await fetch('/api/labels/pdf', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });
  if (!res.ok) { alert('PDF export failed: ' + await res.text()); return; }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `SA_Labels_${currentBOM?.project?.job_code || 'Job'}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}

async function downloadLabelsCSV() {
  if (!currentBOM) { alert('Please calculate BOM first, then generate labels.'); return; }
  const payload = buildLabelsPayload();
  const res = await fetch('/api/labels/csv', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });
  if (!res.ok) { alert('CSV export failed: ' + await res.text()); return; }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `SA_Labels_${currentBOM?.project?.job_code || 'Job'}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function buildLabelsPayload() {
  return {
    bom: currentBOM,
    destination: document.getElementById('lbl_destination')?.value || '',
    fabricator:  document.getElementById('lbl_fabricator')?.value || '',
    qr_base_url: document.getElementById('lbl_qr_url')?.value || 'https://structuresamerica.com/shop',
    grouping: {
      column: parseInt(document.getElementById('grp_column')?.value) || 1,
      rafter: parseInt(document.getElementById('grp_rafter')?.value) || 1,
      purlin: parseInt(document.getElementById('grp_purlin')?.value) || 1,
      strap:  parseInt(document.getElementById('grp_strap')?.value)  || 10,
    },
  };
}

// ─────────────────────────────────────────────
// INVENTORY
// ─────────────────────────────────────────────
async function loadInventory() {
  const res = await fetch('/api/inventory');
  const data = await res.json();
  renderInventory(data);
}

function renderInventory(data) {
  const el = document.getElementById('inventory-content');
  let html = `
  <div class="alert alert-info">
    Stock levels are tracked per-coil. Update quantities when material arrives.
    Committed quantities are deducted when a project BOM is locked.
  </div>

  <div class="card">
    <div class="card-hdr"><span class="icon">🔩</span>Coil Inventory</div>
    <div class="card-body" style="padding:0">
    <table class="inv-table">
      <thead>
        <tr>
          <th>Material</th><th>Gauge</th>
          <th style="text-align:right">In Stock (LBS)</th>
          <th style="text-align:right">Committed (LBS)</th>
          <th style="text-align:right">Available (LBS)</th>
          <th style="text-align:right">Price/LB</th>
          <th>Lead Time</th>
          <th>Status</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>`;

  // Build per-coil cert count map
  const certsByCoil = {};
  for (const c of (data.mill_certs || [])) {
    const key = c.coil_id || c.material || '';
    certsByCoil[key] = (certsByCoil[key] || 0) + 1;
  }

  for (const [id, coil] of Object.entries(data.coils || {})) {
    const avail = (coil.stock_lbs || 0) - (coil.committed_lbs || 0);
    const status = avail <= 0 ? 'OUT' : avail < 2000 ? 'LOW' : 'OK';
    const statusClass = status === 'OK' ? 'stock-ok' : status === 'LOW' ? 'stock-low' : 'stock-out';
    const nCerts = certsByCoil[id] || 0;
    const certBadge = nCerts > 0
      ? `<span style="background:#E8F5E9;color:#2E7D32;border-radius:10px;padding:2px 7px;font-size:10px;font-weight:700;cursor:pointer;margin-left:4px"
           onclick="filterCerts('${id}')" title="Show certs for this coil">📜 ${nCerts} cert${nCerts>1?'s':''}</span>`
      : `<span style="color:#bbb;font-size:10px;margin-left:4px">no certs</span>`;
    html += `
      <tr>
        <td>${coil.name} ${certBadge}</td>
        <td>${coil.gauge}</td>
        <td style="text-align:right">${(coil.stock_lbs||0).toLocaleString()}</td>
        <td style="text-align:right">${(coil.committed_lbs||0).toLocaleString()}</td>
        <td style="text-align:right;font-weight:600">${avail.toLocaleString()}</td>
        <td style="text-align:right">$${coil.price_per_lb}</td>
        <td>${coil.lead_time_weeks} wks</td>
        <td><span class="${statusClass}">${status}</span></td>
        <td>
          <input type="number" id="inv_${id}" placeholder="Add LBS" style="width:90px;padding:4px 6px;font-size:11px;border:1px solid #ccc;border-radius:3px"/>
          <button class="btn btn-primary btn-sm" style="padding:4px 8px;font-size:11px"
            onclick="updateStock('${id}')">Update</button>
          <button class="btn btn-gold btn-sm" style="padding:4px 7px;font-size:11px;margin-left:4px" title="Print inventory sticker for this coil"
            onclick="quickPrintSticker('${id}', ${JSON.stringify(coil.name||'').replace(/'/g,"\\'")} )">🏷️</button>
          <button class="btn btn-red btn-sm" style="padding:4px 7px;font-size:11px;margin-left:4px" title="Permanently delete this coil + certs"
            onclick="deleteCoil('${id}', ${JSON.stringify(coil.name||id).replace(/'/g,"\\'")})">🗑️</button>
        </td>
      </tr>`;
  }

  html += `</tbody></table></div></div>`;

  // ── Add New Coil Form ──────────────────────────────────────────────────
  html += `
  <div class="card" style="margin-top:16px">
    <div class="card-hdr" style="background:var(--sa-green);color:#fff"><span class="icon">➕</span>Add New Coil to Inventory</div>
    <div class="card-body">
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px;margin-bottom:12px">
        <div class="form-group">
          <label>Coil ID *</label>
          <div style="display:flex;gap:4px">
            <input type="text" id="new_coil_id" placeholder="COIL-2026-001" style="font-size:12px;flex:1"/>
            <button class="btn btn-outline btn-sm" style="padding:3px 8px;font-size:10px;white-space:nowrap" onclick="document.getElementById('new_coil_id').value=generateCoilId()">Auto</button>
          </div>
        </div>
        <div class="form-group">
          <label>Material Name *</label>
          <input type="text" id="new_coil_name" placeholder='e.g. 23" 10GA C-Section' style="font-size:12px"/>
        </div>
        <div class="form-group">
          <label>Gauge</label>
          <input type="text" id="new_coil_gauge" placeholder="e.g. 10GA" style="font-size:12px"/>
        </div>
        <div class="form-group">
          <label>Stock (LBS)</label>
          <input type="number" id="new_coil_stock" value="0" style="font-size:12px"/>
        </div>
        <div class="form-group">
          <label>Price / LB ($)</label>
          <input type="number" id="new_coil_price" value="0" step="0.01" style="font-size:12px"/>
        </div>
        <div class="form-group">
          <label>LBS / LFT</label>
          <input type="number" id="new_coil_lbs_lft" value="0" step="0.01" style="font-size:12px"/>
        </div>
        <div class="form-group">
          <label>Lead Time (wks)</label>
          <input type="number" id="new_coil_lead" value="8" style="font-size:12px"/>
        </div>
        <div class="form-group">
          <label>Min Order (LBS)</label>
          <input type="number" id="new_coil_min_order" value="5000" style="font-size:12px"/>
        </div>
      </div>
      <div style="display:flex;gap:8px;align-items:center">
        <button class="btn btn-green" onclick="addNewCoil()">➕ Add Coil</button>
        <div id="new-coil-status" style="font-size:12px;color:#666"></div>
      </div>
    </div>
  </div>`;

  // ── Mill Certificates ──────────────────────────────────────────────────
  const allCerts = data.mill_certs || [];
  const coilOptions = Object.entries(data.coils||{})
    .map(([id,c])=>`<option value="${id}">${c.name.slice(0,35)}</option>`).join('');

  html += `
  <div class="card">
    <div class="card-hdr"><span class="icon">📜</span>Mill Certificates (AISC Compliance)</div>
    <div class="card-body">
      <p style="font-size:12px;color:#666;margin-bottom:12px">
        Per AISC requirements, heat numbers and mill certifications must be tracked for each coil.
        Upload the PDF from the mill — it's stored on the server and linked to the coil permanently.
      </p>

      <!-- Add cert form -->
      <div style="background:#F0F4FA;border-radius:6px;padding:14px;margin-bottom:14px">
        <div style="font-size:11px;font-weight:700;color:var(--sa-blue);text-transform:uppercase;margin-bottom:10px;letter-spacing:.4px">➕ Add New Mill Certificate</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;margin-bottom:10px">
          <div class="form-group">
            <label>Coil / Material</label>
            <select id="cert_material" style="font-size:12px">${coilOptions}</select>
          </div>
          <div class="form-group">
            <label>Heat Number</label>
            <input type="text" id="cert_heat" placeholder="e.g. 123456A" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Mill / Supplier</label>
            <input type="text" id="cert_mill" placeholder="e.g. Nucor Steel" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Cert Date</label>
            <input type="text" id="cert_date" placeholder="MM/DD/YYYY" style="font-size:12px"/>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
          <div class="form-group" style="margin:0;flex:1;min-width:240px">
            <label>PDF Certificate File</label>
            <input type="file" id="cert_pdf" accept="application/pdf,.pdf"
              style="width:100%;padding:5px 8px;border:1px dashed var(--sa-blue-m);border-radius:4px;background:#fff;font-size:12px;cursor:pointer"/>
          </div>
          <button class="btn btn-primary" style="margin-top:16px;white-space:nowrap"
            onclick="addMillCert()">📜 Add Cert</button>
          <div id="cert-upload-status" style="font-size:12px;color:#666;margin-top:16px"></div>
        </div>
      </div>

      <!-- Cert list with filter -->
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
        <span style="font-size:11px;font-weight:700;color:var(--sa-blue);text-transform:uppercase">Certificate Log</span>
        <select id="cert_filter_coil" style="font-size:11px;padding:3px 6px;border:1px solid #ccc;border-radius:3px;max-width:200px"
          onchange="renderCertList()">
          <option value="">— All Coils —</option>
          ${coilOptions}
        </select>
        <span id="cert-count-badge" style="font-size:11px;color:#888"></span>
      </div>
      <div id="mill-certs-list">`;

  // Render certs inline (all of them; JS filterCerts will re-render)
  if (allCerts.length === 0) {
    html += `<div class="alert alert-info">No mill certificates recorded yet. Upload your first cert above.</div>`;
  }
  for (const cert of allCerts) {
    const coilName = (data.coils||{})[cert.coil_id||cert.material]?.name || cert.coil_id || cert.material || '?';
    const pdfLink = cert.filename
      ? `<a href="/certs/${cert.filename}" target="_blank"
           style="background:var(--sa-red);color:#fff;border-radius:3px;padding:3px 8px;font-size:10px;font-weight:700;text-decoration:none;margin-left:8px">📄 VIEW PDF</a>`
      : `<span style="color:#bbb;font-size:10px;margin-left:8px">no PDF</span>`;
    html += `
      <div class="alert alert-success" style="display:flex;align-items:center;flex-wrap:wrap;gap:6px"
           data-coil-id="${cert.coil_id||cert.material||''}">
        <span style="font-weight:700">${coilName}</span>
        <span style="color:#555">Heat: <b>${cert.heat||'—'}</b></span>
        <span style="color:#555">Mill: ${cert.mill||'—'}</span>
        <span style="color:#555">Date: ${cert.date||'—'}</span>
        <span style="color:#888;font-size:10px">Added: ${cert.added||''}</span>
        ${pdfLink}
      </div>`;
  }

  html += `</div></div></div>`;

  // ── Coil Sticker Section ──────────────────────────────────────────────────
  html += `
  <div class="card" style="margin-top:16px">
    <div class="card-hdr"><span class="icon">🏷️</span>Print Inventory Sticker</div>
    <div class="card-body">
      <p style="font-size:12px;color:#666;margin-bottom:14px">
        Print a 4"×6" sticker for any coil. The sticker includes grade, gauge, heat number,
        supplier, weight, width, received date, and a <strong>QR code</strong> workers can scan
        to instantly see if the coil has been applied to a job.
        You can also create a new coil entry in inventory at the same time.
      </p>

      <div style="background:#FFF8E8;border:1px solid #C89A2E;border-radius:6px;padding:14px;margin-bottom:14px">
        <div style="font-size:11px;font-weight:700;color:#7A5C00;text-transform:uppercase;margin-bottom:10px;letter-spacing:.4px">🏷️ Sticker Details</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;margin-bottom:10px">
          <div class="form-group">
            <label>Coil / Material *</label>
            <select id="stk_coil_id" style="font-size:12px" onchange="onStickerCoilChange()">
              <option value="">— New coil (fill below) —</option>
              ${coilOptions}
            </select>
          </div>
          <div class="form-group">
            <label>Description</label>
            <input type="text" id="stk_description" placeholder="e.g. G90 Galv 29ga Coil" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Grade</label>
            <input type="text" id="stk_grade" placeholder="e.g. G90" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Gauge</label>
            <input type="text" id="stk_gauge" placeholder="e.g. 29 ga" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Heat Number</label>
            <input type="text" id="stk_heat_num" placeholder="e.g. HT-A12345" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Supplier / Mill</label>
            <input type="text" id="stk_supplier" placeholder="e.g. Nucor Steel" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Weight (lbs)</label>
            <input type="number" id="stk_weight_lbs" placeholder="14500" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Width (in)</label>
            <input type="number" id="stk_width_in" placeholder="48" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Qty On Hand (lbs)</label>
            <input type="number" id="stk_qty_on_hand" placeholder="0" style="font-size:12px"/>
          </div>
          <div class="form-group">
            <label>Received Date</label>
            <input type="text" id="stk_received_date" placeholder="MM/DD/YYYY" style="font-size:12px"/>
          </div>
        </div>

        <!-- New coil creation option -->
        <div id="stk_new_coil_row" style="display:none;background:#fff;border:1px solid #C89A2E;border-radius:5px;padding:10px;margin-bottom:10px">
          <div style="font-size:12px;color:#7A5C00;margin-bottom:6px;font-weight:bold">
            🆕 New Coil Entry
          </div>
          <div style="display:flex;align-items:center;gap:10px">
            <div class="form-group" style="flex:1;margin:0">
              <label>New Coil ID *</label>
              <input type="text" id="stk_new_coil_id" placeholder="e.g. COIL-2026-005"
                style="font-size:12px;width:100%"/>
            </div>
            <label style="font-size:12px;display:flex;align-items:center;gap:5px;margin-top:14px;white-space:nowrap">
              <input type="checkbox" id="stk_create_entry" checked/>
              Add to inventory
            </label>
          </div>
        </div>

        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
          <button class="btn btn-gold" onclick="printCoilSticker('pdf')" style="font-size:12px">
            📄 Download PDF Sticker
          </button>
          <button class="btn btn-green" onclick="printCoilSticker('zpl')" style="font-size:12px">
            ⬇️ Download ZPL (Zebra)
          </button>
          <button class="btn btn-outline" onclick="printCoilSticker('csv')" style="font-size:12px">
            📊 Download CSV (NiceLabel)
          </button>
          <div id="stk-status" style="font-size:12px;color:#666"></div>
        </div>
      </div>
    </div>
  </div>`;

  el.innerHTML = html;
}

async function deleteCoil(coilId, coilName) {
  if (!confirm('⚠️ PERMANENTLY DELETE coil "' + coilName + '" (ID: ' + coilId + ')?\n\nThis will also delete all associated mill certificates and PDF files.\n\nThis cannot be undone.')) return;
  if (!confirm('Are you SURE? Type OK to confirm.\n\nDeleting: ' + coilId)) return;
  try {
    const resp = await fetch('/api/inventory/delete', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ coil_id: coilId }),
    });
    const result = await resp.json();
    if (result.ok) {
      loadInventory();
    } else {
      alert('Delete failed: ' + (result.error || 'unknown error'));
    }
  } catch(e) { alert('Delete error: ' + e.message); }
}

function generateCoilId() {
  const year = new Date().getFullYear();
  // Look at existing coil IDs to find the next number
  const existingIds = [...document.querySelectorAll('#inventory-content .inv-table tbody tr')]
    .map(r => r.querySelector('td')?.textContent || '');
  let maxNum = 0;
  const re = /COIL-(\d{4})-(\d+)/;
  for (const id of existingIds) {
    const m = id.match(re);
    if (m && parseInt(m[1]) === year) maxNum = Math.max(maxNum, parseInt(m[2]));
  }
  return 'COIL-' + year + '-' + String(maxNum + 1).padStart(3, '0');
}

function onStickerCoilChange() {
  const sel  = document.getElementById('stk_coil_id');
  const coilId = sel?.value || '';
  const newRow = document.getElementById('stk_new_coil_row');
  if (newRow) newRow.style.display = coilId ? 'none' : 'block';
}

async function printCoilSticker(fmt) {
  const selEl     = document.getElementById('stk_coil_id');
  const existingId = selEl?.value || '';
  const newIdEl   = document.getElementById('stk_new_coil_id');
  const coilId    = existingId || (newIdEl?.value.trim() || '');

  if (!coilId) {
    alert('Please select an existing coil or enter a New Coil ID.');
    return;
  }

  const createEntry = !existingId && document.getElementById('stk_create_entry')?.checked;

  const coilData = {
    description:   document.getElementById('stk_description')?.value.trim() || '',
    grade:         document.getElementById('stk_grade')?.value.trim()       || '',
    gauge:         document.getElementById('stk_gauge')?.value.trim()       || '',
    heat_num:      document.getElementById('stk_heat_num')?.value.trim()    || '',
    supplier:      document.getElementById('stk_supplier')?.value.trim()    || '',
    weight_lbs:    parseFloat(document.getElementById('stk_weight_lbs')?.value) || '',
    width_in:      parseFloat(document.getElementById('stk_width_in')?.value)   || '',
    qty_on_hand:   parseFloat(document.getElementById('stk_qty_on_hand')?.value) || '',
    received_date: document.getElementById('stk_received_date')?.value.trim() || '',
    create_entry:  createEntry,
  };

  const status = document.getElementById('stk-status');
  if (status) status.textContent = 'Generating…';

  try {
    const resp = await fetch('/api/inventory/sticker', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ coil_id: coilId, format: fmt, coil: coilData }),
    });
    if (!resp.ok) { alert('Sticker error: ' + await resp.text()); return; }
    const blob = await resp.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    const exts = {pdf:'pdf', zpl:'zpl', csv:'csv'};
    a.href     = url;
    a.download = `Coil_Sticker_${coilId}.${exts[fmt] || fmt}`;
    a.click();
    URL.revokeObjectURL(url);
    if (status) status.textContent = '✅ Downloaded!';
    if (createEntry) { setTimeout(loadInventory, 800); }
  } catch(e) {
    alert('Failed: ' + e);
    if (status) status.textContent = '';
  }
}

function filterCerts(coilId) {
  // Select that coil in the filter dropdown and re-render
  const sel = document.getElementById('cert_filter_coil');
  if (sel) { sel.value = coilId; renderCertList(); }
}

function renderCertList() {
  const filterCoil = document.getElementById('cert_filter_coil')?.value || '';
  const rows = document.querySelectorAll('#mill-certs-list [data-coil-id]');
  let shown = 0;
  rows.forEach(row => {
    const match = !filterCoil || row.dataset.coilId === filterCoil;
    row.style.display = match ? '' : 'none';
    if (match) shown++;
  });
  const badge = document.getElementById('cert-count-badge');
  if (badge) badge.textContent = shown + ' cert' + (shown !== 1 ? 's' : '') + (filterCoil ? ' for this coil' : ' total');
}

async function updateStock(coilId) {
  const input = document.getElementById('inv_' + coilId);
  const lbs = parseFloat(input.value);
  if (isNaN(lbs) || lbs === 0) return;
  await fetch('/api/inventory/update', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({coil_id: coilId, add_lbs: lbs}),
  });
  input.value = '';
  loadInventory();
}

async function quickPrintSticker(coilId, coilName) {
  // One-click PDF sticker from the coil row — uses whatever is in inventory for that coil
  const resp = await fetch('/api/inventory/sticker', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ coil_id: coilId, format: 'pdf', coil: {} }),
  });
  if (!resp.ok) { alert('Sticker error: ' + await resp.text()); return; }
  const blob = await resp.blob();
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `Coil_Sticker_${coilId}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}

async function addNewCoil() {
  const coilId = document.getElementById('new_coil_id')?.value.trim();
  const name   = document.getElementById('new_coil_name')?.value.trim();
  if (!coilId || !name) { alert('Coil ID and Material Name are required.'); return; }

  const statusEl = document.getElementById('new-coil-status');
  if (statusEl) statusEl.textContent = 'Adding...';

  const newCoil = {
    coil_id: coilId,
    format: 'pdf',
    coil: {
      description:   name,
      gauge:         document.getElementById('new_coil_gauge')?.value.trim() || '',
      qty_on_hand:   parseFloat(document.getElementById('new_coil_stock')?.value) || 0,
      create_entry:  true,
    }
  };

  // Use the sticker endpoint to create entry (it handles creation)
  // But we also need price_per_lb etc. so let's use a direct inventory update approach
  try {
    const invResp = await fetch('/api/inventory');
    const inv = await invResp.json();
    if (inv.coils && inv.coils[coilId]) {
      alert('Coil ID "' + coilId + '" already exists. Choose a different ID.');
      if (statusEl) statusEl.textContent = '';
      return;
    }
    inv.coils = inv.coils || {};
    inv.coils[coilId] = {
      name:           name,
      gauge:          document.getElementById('new_coil_gauge')?.value.trim() || '',
      stock_lbs:      parseFloat(document.getElementById('new_coil_stock')?.value) || 0,
      stock_lft:      0,
      committed_lbs:  0,
      min_order_lbs:  parseFloat(document.getElementById('new_coil_min_order')?.value) || 5000,
      lead_time_weeks: parseInt(document.getElementById('new_coil_lead')?.value) || 8,
      price_per_lb:   parseFloat(document.getElementById('new_coil_price')?.value) || 0,
      lbs_per_lft:    parseFloat(document.getElementById('new_coil_lbs_lft')?.value) || 0,
      coil_max_lbs:   8000,
      orders:         [],
    };
    // Save via a direct PUT-style update to inventory
    await fetch('/api/inventory/save', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(inv),
    });
    if (statusEl) statusEl.textContent = '✅ Coil added!';
    // Clear form
    document.getElementById('new_coil_id').value = '';
    document.getElementById('new_coil_name').value = '';
    document.getElementById('new_coil_gauge').value = '';
    document.getElementById('new_coil_stock').value = '0';
    document.getElementById('new_coil_price').value = '0';
    document.getElementById('new_coil_lbs_lft').value = '0';
    setTimeout(() => { if (statusEl) statusEl.textContent = ''; }, 3000);
    loadInventory();
  } catch(e) {
    if (statusEl) statusEl.textContent = '❌ Error: ' + e.message;
  }
}

async function addMillCert() {
  const coilId  = document.getElementById('cert_material').value;
  const heat    = document.getElementById('cert_heat').value.trim();
  const mill    = document.getElementById('cert_mill').value.trim();
  const date    = document.getElementById('cert_date').value.trim();
  const pdfFile = document.getElementById('cert_pdf').files[0];

  if (!heat) { alert('Please enter a Heat Number.'); return; }

  const statusEl = document.getElementById('cert-upload-status');
  statusEl.textContent = '⏳ Uploading...';

  // Always use multipart upload so the PDF (if any) goes with the metadata
  const fd = new FormData();
  fd.append('coil_id', coilId);
  fd.append('heat', heat);
  fd.append('mill', mill);
  fd.append('date', date);
  if (pdfFile) fd.append('pdf_file', pdfFile);

  try {
    const resp = await fetch('/api/inventory/cert/upload', { method: 'POST', body: fd });
    const result = await resp.json();
    if (result.ok) {
      statusEl.textContent = result.filename
        ? `✅ Cert + PDF saved (${result.filename})`
        : '✅ Cert saved (no PDF attached)';
      // Clear form
      document.getElementById('cert_heat').value = '';
      document.getElementById('cert_mill').value = '';
      document.getElementById('cert_date').value = '';
      document.getElementById('cert_pdf').value = '';
      setTimeout(() => { statusEl.textContent = ''; }, 4000);
      loadInventory();
    } else {
      statusEl.textContent = '❌ Error: ' + (result.error || 'unknown');
    }
  } catch(e) {
    statusEl.textContent = '❌ Upload failed: ' + e.message;
  }
}
</script>
</body>
</html>
"""


# ─────────────────────────────────────────────
# TC CONSTRUCTION QUOTE PAGE (served at /tc)
# ─────────────────────────────────────────────

TC_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Titan Carports — Construction Quote v2.6</title>
<style>
:root {
  --tc-dark:#1C1C2E; --tc-red:#C00000; --tc-red-l:#FFF0F0;
  --tc-blue:#1F4E79; --tc-blue-m:#2E75B6; --tc-blue-l:#DEEAF1;
  --tc-gold:#FFC000; --tc-green:#375623; --tc-gray:#404040;
  --tc-light:#F5F7FA; --tc-white:#ffffff; --tc-border:#D0D7E2;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:var(--tc-light);color:var(--tc-gray);font-size:13px}
#topbar{background:var(--tc-dark);color:#fff;padding:0 20px;display:flex;align-items:center;height:52px;box-shadow:0 2px 8px #0005}
#topbar .logo{font-size:17px;font-weight:700;letter-spacing:1px;color:#fff}
#topbar .logo span{color:var(--tc-red)}
#topbar .spacer{flex:1}
#topbar .version{font-size:10px;color:#666}
#tabs{background:var(--tc-blue);display:flex;overflow-x:auto}
.tab{padding:10px 20px;color:#aac;cursor:pointer;font-size:12px;font-weight:600;border-bottom:3px solid transparent;white-space:nowrap;transition:all .2s}
.tab:hover{color:#fff;background:rgba(255,255,255,.07)}
.tab.active{color:#fff;border-bottom-color:var(--tc-gold)}
#main{display:flex;gap:0;height:calc(100vh - 94px)}
#sidebar{width:320px;min-width:270px;background:#fff;border-right:1px solid var(--tc-border);overflow-y:auto;padding:16px;flex-shrink:0}
#content{flex:1;overflow-y:auto;padding:20px}
.card{background:#fff;border:1px solid var(--tc-border);border-radius:8px;margin-bottom:14px;overflow:hidden}
.card-hdr{padding:9px 14px;font-weight:700;font-size:12px;display:flex;align-items:center;gap:8px;text-transform:uppercase;letter-spacing:.4px}
.card-hdr.red{background:var(--tc-red);color:#fff}
.card-hdr.blue{background:var(--tc-blue-m);color:#fff}
.card-hdr.gold{background:var(--tc-gold);color:#1C1C2E}
.card-hdr.green{background:var(--tc-green);color:#fff}
.card-hdr.gray{background:#555;color:#fff}
.card-hdr.dark{background:var(--tc-dark);color:#fff}
.card-body{padding:14px}
.form-group{margin-bottom:10px}
label{display:block;font-size:11px;font-weight:600;color:var(--tc-blue);margin-bottom:4px;text-transform:uppercase;letter-spacing:.4px}
input[type=text],input[type=number],select,textarea{width:100%;padding:6px 10px;border:1px solid var(--tc-border);border-radius:4px;font-size:13px;color:var(--tc-gray);background:#fff;transition:border .2s}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--tc-blue-m);box-shadow:0 0 0 3px #2E75B615}
input[type=checkbox]{width:auto;margin-right:6px}
.check-label{display:flex;align-items:center;font-size:12px;font-weight:400;text-transform:none;letter-spacing:0;cursor:pointer}
.btn{padding:7px 14px;border:none;border-radius:4px;cursor:pointer;font-size:12px;font-weight:600;transition:all .2s;display:inline-flex;align-items:center;gap:5px}
.btn-red{background:var(--tc-red);color:#fff}.btn-red:hover{opacity:.9}
.btn-blue{background:var(--tc-blue-m);color:#fff}.btn-blue:hover{opacity:.85}
.btn-gold{background:var(--tc-gold);color:var(--tc-dark)}.btn-gold:hover{opacity:.9}
.btn-green{background:var(--tc-green);color:#fff}.btn-green:hover{opacity:.9}
.btn-outline{background:transparent;border:1px solid var(--tc-border);color:var(--tc-gray)}.btn-outline:hover{background:var(--tc-blue-l)}
.btn-sm{padding:4px 10px;font-size:11px}
.btn-danger{background:#f44;color:#fff}.btn-danger:hover{opacity:.85}
.btn-group{display:flex;gap:8px;flex-wrap:wrap}
.li-table{width:100%;border-collapse:collapse;font-size:12px;margin-top:8px}
.li-table th{background:var(--tc-blue);color:#fff;padding:6px 8px;text-align:left;font-size:11px;font-weight:600}
.li-table td{padding:5px 8px;border-bottom:1px solid #eee;vertical-align:middle}
.li-table tr:hover td{background:#f9f9f9}
.li-table .total-row td{background:#FFF8E1;font-weight:700;border-top:2px solid var(--tc-gold)}
.li-table input{padding:4px 6px;font-size:12px;border:1px solid #ddd;border-radius:3px}
.summary-table{width:100%;border-collapse:collapse;font-size:13px}
.summary-table td{padding:8px 12px;border-bottom:1px solid #eee}
.summary-table .section-lbl td{background:var(--tc-blue-l);font-weight:700;color:var(--tc-blue);font-size:11px;text-transform:uppercase;letter-spacing:.4px}
.summary-table .total-row td{background:var(--tc-red);color:#fff;font-weight:700;font-size:15px}
.summary-table .markup-row td{background:#FFF8E1;font-weight:600}
.summary-table .subtotal-row td{background:#f0f4f0;font-weight:700}
.stat-cards{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px}
.stat{background:#fff;border:1px solid var(--tc-border);border-radius:8px;padding:12px 16px;min-width:140px;flex:1}
.stat .val{font-size:20px;font-weight:700;color:var(--tc-blue)}
.stat .lbl{font-size:10px;color:#888;text-transform:uppercase;margin-top:2px}
.alert{border-radius:4px;padding:8px 12px;font-size:12px;margin-bottom:10px}
.alert-info{background:#E3F2FD;border-left:4px solid #2196F3;color:#1565C0}
.alert-warn{background:#FFF8E1;border-left:4px solid var(--tc-gold);color:#795548}
.alert-success{background:#E8F5E9;border-left:4px solid #4CAF50;color:#2E7D32}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
.grid4{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px}
@media(max-width:768px){#main{flex-direction:column}#sidebar{width:100%}}
</style>
</head>
<body>

<!-- Topbar -->
<div id="topbar">
  <!-- SA Logo -->
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 220" width="36" height="36" style="flex-shrink:0">
    <polygon points="110,105 20,15 55,80" fill="#777"/><polygon points="20,15 55,80 5,60" fill="#999"/>
    <polygon points="110,105 55,80 45,115" fill="#555"/><polygon points="110,105 45,115 65,130" fill="#444"/>
    <polygon points="110,105 200,15 165,80" fill="#777"/><polygon points="200,15 165,80 215,60" fill="#999"/>
    <polygon points="110,105 165,80 175,115" fill="#555"/><polygon points="110,105 175,115 155,130" fill="#444"/>
    <polygon points="95,95 110,70 125,95 110,145" fill="#ccc"/><polygon points="100,72 110,55 120,72 110,85" fill="#bbb"/>
  </svg>
  <!-- App Switcher -->
  <div style="display:flex;gap:6px;align-items:center;margin:0 12px">
    <a href="/" style="background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);border-radius:4px;padding:5px 12px;font-size:11px;font-weight:700;color:#aaa;text-decoration:none;letter-spacing:.5px">← SA CALC</a>
    <div style="background:rgba(192,0,0,.3);border:1px solid rgba(192,0,0,.5);border-radius:4px;padding:5px 12px;font-size:11px;font-weight:700;color:#fff;letter-spacing:.5px">🏗️ TC QUOTE</div>
  </div>
  <!-- TC Logo + Title -->
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 180" width="80" height="36" style="flex-shrink:0;margin-right:10px">
    <polygon points="120,155 80,10 108,148 118,155" fill="#888"/><polygon points="80,10 108,148 90,12" fill="#aaa"/>
    <polygon points="140,155 180,10 152,148 142,155" fill="#888"/><polygon points="180,10 152,148 170,12" fill="#aaa"/>
    <polygon points="118,155 142,155 130,175" fill="#777"/>
    <text x="200" y="85" font-family="Arial Black,Arial" font-weight="900" font-size="62" letter-spacing="4" fill="#888">TITAN</text>
    <text x="200" y="148" font-family="Arial Black,Arial" font-weight="900" font-size="44" letter-spacing="3" fill="#C00000">CARPORTS</text>
  </svg>
  <div>
    <div class="logo">TITAN <span>CARPORTS</span></div>
    <div style="font-size:11px;color:#aaa">Construction Quote Calculator</div>
  </div>
  <div class="spacer"></div>
  <div class="version">v2.6</div>
</div>

<!-- Tabs -->
<div id="tabs">
  <div class="tab active" onclick="showTab('quote')">📋 Quote Builder</div>
  <div class="tab" onclick="showTab('summary')">💰 Summary</div>
</div>

<!-- Main -->
<div id="main">
  <!-- LEFT SIDEBAR -->
  <div id="sidebar">

    <!-- Salesperson -->
    <div class="card">
      <div class="card-hdr dark"><span>👤</span>Salesperson</div>
      <div class="card-body">
        <div class="grid2">
          <div class="form-group">
            <label>Name</label>
            <input type="text" id="sp_name" value="Brad Spence"/>
          </div>
          <div class="form-group">
            <label>Title</label>
            <input type="text" id="sp_title" value="Sales Manager"/>
          </div>
        </div>
        <div class="grid2">
          <div class="form-group">
            <label>Phone</label>
            <input type="text" id="sp_phone" value="(303) 909-5698"/>
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="text" id="sp_email" value="brad@titancarports.com"/>
          </div>
        </div>
      </div>
    </div>

    <!-- Project Info -->
    <div class="card">
      <div class="card-hdr red"><span>📁</span>Project Info</div>
      <div class="card-body">
        <div class="form-group">
          <label>Project / Job Name</label>
          <input type="text" id="proj_name" value="" placeholder="e.g. Smith RV Canopy"/>
        </div>
        <div class="form-group">
          <label>Job Code</label>
          <input type="text" id="proj_code" value="" placeholder="TC-2026-001"/>
        </div>
        <div class="form-group">
          <label>Customer Name</label>
          <input type="text" id="proj_customer" value=""/>
        </div>
        <div class="form-group">
          <label>Street Address</label>
          <input type="text" id="proj_address" value=""/>
        </div>
        <div class="grid2">
          <div class="form-group">
            <label>City</label>
            <input type="text" id="proj_city" value=""/>
          </div>
          <div class="form-group">
            <label>State</label>
            <select id="proj_state">
              <option>TX</option><option>FL</option><option>CA</option><option>AZ</option>
              <option>NM</option><option>NV</option><option>CO</option><option>OK</option>
              <option>KS</option><option>MO</option><option>AR</option><option>TN</option>
              <option>LA</option><option>MS</option><option>AL</option><option>GA</option>
              <option>SC</option><option>NC</option><option>VA</option><option>MD</option>
              <option>Other</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>Quote Date</label>
          <input type="text" id="proj_date" value=""/>
        </div>
        <div class="form-group">
          <label>Markup %</label>
          <input type="number" id="proj_markup" value="35" min="0" max="200" step="0.5"
            onchange="renderSummary()"/>
        </div>
      </div>
    </div>

    <!-- SA Materials Import -->
    <div class="card">
      <div class="card-hdr blue"><span>🔗</span>Materials (from SA)</div>
      <div class="card-body">
        <div class="alert alert-info" style="font-size:11px">
          Enter SA fabrication quote total. Use the "Send to TC Quote" button on the SA BOM page to auto-fill.
        </div>
        <div class="form-group">
          <label>SA Quote #</label>
          <input type="text" id="sa_quote_num" placeholder="e.g. SA-2026-042"/>
        </div>
        <div class="form-group">
          <label>SA Materials Sell Price ($)</label>
          <input type="number" id="sa_materials_cost" value="0" min="0" step="100"
            onchange="renderSummary()"/>
        </div>
        <div class="grid2">
          <div class="form-group">
            <label># Columns (piers)</label>
            <input type="number" id="sa_n_cols" value="0" min="0"
              onchange="syncConcreteFromSA();renderSummary()"/>
          </div>
          <div class="form-group">
            <label>Footing Depth (ft)</label>
            <input type="number" id="sa_footing_depth" value="10" min="4" max="25" step="0.5"
              onchange="syncConcreteFromSA();renderSummary()"/>
          </div>
        </div>
        <div class="grid2">
          <div class="form-group">
            <label>Building Width (ft)</label>
            <input type="number" id="sa_width" value="40" min="10"
              onchange="renderSummary()"/>
          </div>
          <div class="form-group">
            <label>Building Length (ft)</label>
            <input type="number" id="sa_length" value="180" min="10"
              onchange="renderSummary()"/>
          </div>
        </div>
        <button class="btn btn-blue btn-sm" style="width:100%;margin-top:4px"
          onclick="syncConcreteFromSA()">↻ Sync Concrete from SA Values</button>
      </div>
    </div>

    <div class="btn-group" style="margin-top:8px">
      <button class="btn btn-gold" onclick="showTab('summary')">💰 View Summary</button>
      <button class="btn btn-outline btn-sm" onclick="tcExportPDF()">⬇ PDF</button>
      <button class="btn btn-outline btn-sm" onclick="tcExportExcel()">⬇ Excel</button>
    </div>

  </div><!-- /sidebar -->

  <!-- CONTENT AREA -->
  <div id="content">

    <!-- QUOTE TAB -->
    <div id="tab-quote">

      <!-- Concrete -->
      <div class="card" id="card-concrete">
        <div class="card-hdr gray"><span>🪨</span>Concrete — Pier Footings</div>
        <div class="card-body">
          <div class="grid4" style="margin-bottom:10px">
            <div class="form-group">
              <label># Piers</label>
              <input type="number" id="conc_n_piers" value="0" min="0"
                onchange="calcConcrete();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Hole Dia (in)</label>
              <input type="number" id="conc_dia_in" value="24" min="6" max="60"
                onchange="calcConcrete();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Depth (ft)</label>
              <input type="number" id="conc_depth_ft" value="10" min="4" max="25" step="0.5"
                onchange="calcConcrete();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Price ($/CY)</label>
              <input type="number" id="conc_price_cy" value="165" min="0" step="5"
                onchange="calcConcrete();renderSummary()"/>
            </div>
          </div>
          <div style="background:#F0F4FA;border-radius:6px;padding:10px;display:flex;gap:24px;flex-wrap:wrap">
            <div><span style="font-size:11px;color:#888">Cubic Yards (w/10% waste):</span>
              <span id="conc_qty_display" style="font-weight:700;color:var(--tc-blue);margin-left:6px">—</span></div>
            <div><span style="font-size:11px;color:#888">Material Cost:</span>
              <span id="conc_cost_display" style="font-weight:700;color:var(--tc-red);margin-left:6px">—</span></div>
          </div>
        </div>
      </div>

      <!-- Labor Installation -->
      <div class="card" id="card-labor">
        <div class="card-hdr red"><span>👷</span>Labor — Installation</div>
        <div class="card-body">
          <div class="grid4" style="margin-bottom:10px">
            <div class="form-group">
              <label>Crew Size</label>
              <input type="number" id="lab_crew" value="4" min="1" max="50"
                onchange="calcLabor();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Days On Site</label>
              <input type="number" id="lab_days" value="1" min="0" step="0.5"
                onchange="calcLabor();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Rate ($/hr/person)</label>
              <input type="number" id="lab_rate_hr" value="30" min="0" step="1"
                onchange="calcLabor();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Hours/Day</label>
              <input type="number" id="lab_hrs_day" value="8" min="1" max="24"
                onchange="calcLabor();renderSummary()"/>
            </div>
          </div>
          <div style="background:#FFF0F0;border-radius:6px;padding:10px;display:flex;gap:24px;flex-wrap:wrap">
            <div><span style="font-size:11px;color:#888">Daily Cost:</span>
              <span id="lab_daily_display" style="font-weight:700;color:var(--tc-blue);margin-left:6px">—</span></div>
            <div><span style="font-size:11px;color:#888">Total Labor Cost:</span>
              <span id="lab_total_display" style="font-weight:700;color:var(--tc-red);margin-left:6px">—</span></div>
          </div>
          <div class="form-group" style="margin-top:10px">
            <label>Notes</label>
            <input type="text" id="lab_notes" placeholder="e.g. Steel erection + welding crew"/>
          </div>
        </div>
      </div>

      <!-- Equipment Rental -->
      <div class="card" id="card-equip">
        <div class="card-hdr blue"><span>🏗️</span>Equipment Rental</div>
        <div class="card-body">
          <table class="li-table">
            <thead><tr><th>Description</th><th>Qty</th><th>Unit</th><th>Rate ($)</th><th>Total</th><th></th></tr></thead>
            <tbody id="equip_tbody"></tbody>
          </table>
          <button class="btn btn-outline btn-sm" style="margin-top:8px"
            onclick="addEquipItem()">+ Add Equipment</button>
        </div>
      </div>

      <!-- Drilling -->
      <div class="card" id="card-drill">
        <div class="card-hdr gray"><span>⚙️</span>Drilling</div>
        <div class="card-body">
          <div class="grid3" style="margin-bottom:10px">
            <div class="form-group">
              <label>Drilling Method</label>
              <select id="drill_method" onchange="calcDrilling();renderSummary()">
                <option value="per_hole">Per Hole ($/hole)</option>
                <option value="rental">Rig Rental + Operator</option>
              </select>
            </div>
            <div class="form-group" id="drill_holes_grp">
              <label># Holes</label>
              <input type="number" id="drill_n_holes" value="0" min="0"
                onchange="calcDrilling();renderSummary()"/>
            </div>
            <div class="form-group" id="drill_rate_grp">
              <label id="drill_rate_lbl">Rate ($/hole)</label>
              <input type="number" id="drill_rate" value="50" min="0" step="5"
                onchange="calcDrilling();renderSummary()"/>
            </div>
          </div>
          <div id="drill_rental_row" style="display:none;margin-bottom:10px">
            <div class="grid3">
              <div class="form-group">
                <label>Rig Rental ($/day)</label>
                <input type="number" id="drill_rig_day" value="0" min="0"
                  onchange="calcDrilling();renderSummary()"/>
              </div>
              <div class="form-group">
                <label>Operator ($/day)</label>
                <input type="number" id="drill_op_day" value="0" min="0"
                  onchange="calcDrilling();renderSummary()"/>
              </div>
              <div class="form-group">
                <label>Days</label>
                <input type="number" id="drill_days" value="1" min="1"
                  onchange="calcDrilling();renderSummary()"/>
              </div>
            </div>
          </div>
          <div style="background:#F0F4FA;border-radius:6px;padding:10px">
            <span style="font-size:11px;color:#888">Drilling Total:</span>
            <span id="drill_total_display" style="font-weight:700;color:var(--tc-red);margin-left:6px">—</span>
          </div>
        </div>
      </div>

      <!-- Shipping -->
      <div class="card" id="card-shipping">
        <div class="card-hdr blue"><span>🚛</span>Shipping &amp; Freight</div>
        <div class="card-body">
          <div class="grid3" style="margin-bottom:10px">
            <div class="form-group">
              <label>Method</label>
              <select id="ship_method" onchange="calcShipping();renderSummary()">
                <option value="per_mile">Per Mile (flatbed)</option>
                <option value="flat">Flat Rate</option>
              </select>
            </div>
            <div class="form-group">
              <label>Miles from Factory</label>
              <input type="number" id="ship_miles" value="0" min="0"
                onchange="calcShipping();renderSummary()"/>
            </div>
            <div class="form-group" id="ship_rate_grp">
              <label>Rate ($/mile)</label>
              <input type="number" id="ship_rate" value="4.50" min="0" step="0.10"
                onchange="calcShipping();renderSummary()"/>
            </div>
          </div>
          <div id="ship_flat_row" style="display:none;margin-bottom:10px">
            <div class="form-group" style="max-width:220px">
              <label>Flat Shipping Amount ($)</label>
              <input type="number" id="ship_flat_amt" value="0" min="0"
                onchange="calcShipping();renderSummary()"/>
            </div>
          </div>
          <div style="display:flex;gap:24px;flex-wrap:wrap;margin-bottom:8px">
            <div><span style="font-size:11px;color:#888">Loads:</span>
              <input type="number" id="ship_loads" value="1" min="1" max="20"
                style="width:55px;margin-left:6px;padding:3px 6px;font-size:12px;border:1px solid #ddd;border-radius:3px"
                onchange="calcShipping();renderSummary()"/>
            </div>
            <div><span style="font-size:11px;color:#888">Shipping Total:</span>
              <span id="ship_total_display" style="font-weight:700;color:var(--tc-red);margin-left:6px">—</span></div>
          </div>
          <div class="form-group">
            <label>Notes</label>
            <input type="text" id="ship_notes" placeholder="e.g. 2 flatbeds, Conroe TX to Lubbock TX"/>
          </div>
        </div>
      </div>

      <!-- Fuel -->
      <div class="card" id="card-fuel">
        <div class="card-hdr gold"><span>⛽</span>Fuel &amp; Gas</div>
        <div class="card-body">
          <div class="grid4" style="margin-bottom:10px">
            <div class="form-group">
              <label># Vehicles</label>
              <input type="number" id="fuel_vehicles" value="1" min="0"
                onchange="calcFuel();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Round-Trip Miles</label>
              <input type="number" id="fuel_miles" value="0" min="0"
                onchange="calcFuel();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Avg MPG</label>
              <input type="number" id="fuel_mpg" value="12" min="1" step="0.5"
                onchange="calcFuel();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Gas Price ($/gal)</label>
              <input type="number" id="fuel_price_gal" value="3.50" min="0" step="0.05"
                onchange="calcFuel();renderSummary()"/>
            </div>
          </div>
          <div style="background:#FFF8E1;border-radius:6px;padding:10px;display:flex;gap:24px;flex-wrap:wrap">
            <div><span style="font-size:11px;color:#888">Total Gallons:</span>
              <span id="fuel_gal_display" style="font-weight:700;margin-left:6px">—</span></div>
            <div><span style="font-size:11px;color:#888">Fuel Total:</span>
              <span id="fuel_total_display" style="font-weight:700;color:var(--tc-red);margin-left:6px">—</span></div>
          </div>
        </div>
      </div>

      <!-- Hotels -->
      <div class="card" id="card-hotels">
        <div class="card-hdr blue"><span>🏨</span>Hotels</div>
        <div class="card-body">
          <div class="grid3" style="margin-bottom:10px">
            <div class="form-group">
              <label># Crew</label>
              <input type="number" id="hotel_crew" value="4" min="0"
                onchange="calcHotels();renderSummary()"/>
            </div>
            <div class="form-group">
              <label># Nights</label>
              <input type="number" id="hotel_nights" value="0" min="0"
                onchange="calcHotels();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Rate ($/night/room)</label>
              <input type="number" id="hotel_rate" value="110" min="0" step="5"
                onchange="calcHotels();renderSummary()"/>
            </div>
          </div>
          <div style="background:#F0F4FA;border-radius:6px;padding:10px;display:flex;gap:24px;flex-wrap:wrap">
            <div><span style="font-size:11px;color:#888">Room-Nights:</span>
              <span id="hotel_rooms_display" style="font-weight:700;margin-left:6px">—</span></div>
            <div><span style="font-size:11px;color:#888">Hotel Total:</span>
              <span id="hotel_total_display" style="font-weight:700;color:var(--tc-red);margin-left:6px">—</span></div>
          </div>
        </div>
      </div>

      <!-- Per Diem -->
      <div class="card" id="card-perdiem">
        <div class="card-hdr green"><span>🍽️</span>Per Diem</div>
        <div class="card-body">
          <div class="grid3" style="margin-bottom:10px">
            <div class="form-group">
              <label># Crew</label>
              <input type="number" id="pd_crew" value="4" min="0"
                onchange="calcPerDiem();renderSummary()"/>
            </div>
            <div class="form-group">
              <label># Days</label>
              <input type="number" id="pd_days" value="0" min="0"
                onchange="calcPerDiem();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Rate ($/day/person)</label>
              <input type="number" id="pd_rate" value="75" min="0" step="5"
                onchange="calcPerDiem();renderSummary()"/>
            </div>
          </div>
          <div style="background:#F0F4FA;border-radius:6px;padding:10px">
            <span style="font-size:11px;color:#888">Per Diem Total:</span>
            <span id="pd_total_display" style="font-weight:700;color:var(--tc-red);margin-left:6px">—</span>
          </div>
        </div>
      </div>

      <!-- Transportation of Crew -->
      <div class="card" id="card-transport">
        <div class="card-hdr gray"><span>🚐</span>Transportation of Crew</div>
        <div class="card-body">
          <div class="grid4" style="margin-bottom:10px">
            <div class="form-group">
              <label># Vehicles</label>
              <input type="number" id="trans_vehicles" value="1" min="0"
                onchange="calcTransport();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Round-Trip Miles</label>
              <input type="number" id="trans_miles" value="0" min="0"
                onchange="calcTransport();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Mileage Rate ($/mi)</label>
              <input type="number" id="trans_rate" value="0.67" min="0" step="0.01"
                onchange="calcTransport();renderSummary()"/>
            </div>
            <div class="form-group">
              <label>Trips</label>
              <input type="number" id="trans_trips" value="1" min="1"
                onchange="calcTransport();renderSummary()"/>
            </div>
          </div>
          <div style="background:#F0F4FA;border-radius:6px;padding:10px">
            <span style="font-size:11px;color:#888">Transportation Total:</span>
            <span id="trans_total_display" style="font-weight:700;color:var(--tc-red);margin-left:6px">—</span>
          </div>
          <div class="form-group" style="margin-top:10px">
            <label>Notes</label>
            <input type="text" id="trans_notes" placeholder="e.g. 3 trucks × 400 mi round trip to Austin"/>
          </div>
        </div>
      </div>

      <!-- Miscellaneous -->
      <div class="card" id="card-misc">
        <div class="card-hdr gold"><span>📦</span>Miscellaneous / Other</div>
        <div class="card-body">
          <table class="li-table">
            <thead><tr><th>Description</th><th>Amount ($)</th><th></th></tr></thead>
            <tbody id="misc_tbody"></tbody>
          </table>
          <button class="btn btn-outline btn-sm" style="margin-top:8px"
            onclick="addMiscItem()">+ Add Item</button>
        </div>
      </div>

    </div><!-- /tab-quote -->

    <!-- SUMMARY TAB -->
    <div id="tab-summary" style="display:none">
      <div class="stat-cards" id="stat-cards-summary"></div>
      <div class="card">
        <div class="card-hdr blue"><span>💰</span>Construction Quote Summary</div>
        <div class="card-body">
          <table class="summary-table" id="summary-table"></table>
        </div>
      </div>
    </div>

  </div><!-- /content -->
</div><!-- /main -->

<script>
// ─────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────
const equipItems = [];
const miscItems = [];
let concreteCost = 0, laborCost = 0, drillingCost = 0,
    shippingCost = 0, fuelCost = 0, hotelCost = 0,
    perDiemCost = 0, transportCost = 0;

function fmt(v) {
  return '$' + (v||0).toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2});
}
function numVal(id) { return parseFloat(document.getElementById(id)?.value) || 0; }
function strVal(id) { return (document.getElementById(id)?.value||'').trim(); }

// ─────────────────────────────────────────────
// URL PARAM PRE-FILL (from "Send to TC Quote" button on SA page)
// ─────────────────────────────────────────────
function prefillFromURL() {
  const p = new URLSearchParams(window.location.search);
  if (p.has('sa_cost')) {
    document.getElementById('sa_materials_cost').value = p.get('sa_cost');
  }
  if (p.has('n_cols')) {
    document.getElementById('sa_n_cols').value = p.get('n_cols');
    document.getElementById('conc_n_piers').value = p.get('n_cols');
    document.getElementById('drill_n_holes').value = p.get('n_cols');
  }
  if (p.has('footing')) {
    document.getElementById('sa_footing_depth').value = p.get('footing');
    document.getElementById('conc_depth_ft').value = p.get('footing');
  }
  if (p.has('proj_name')) document.getElementById('proj_name').value = p.get('proj_name');
  if (p.has('proj_code')) {
    document.getElementById('proj_code').value = 'TC-' + p.get('proj_code');
  }
  if (p.has('sa_quote')) document.getElementById('sa_quote_num').value = p.get('sa_quote');
  if (p.has('width')) document.getElementById('sa_width').value = p.get('width');
  if (p.has('length')) document.getElementById('sa_length').value = p.get('length');
}

// ─────────────────────────────────────────────
// TAB SWITCHING
// ─────────────────────────────────────────────
function showTab(t) {
  document.getElementById('tab-quote').style.display = t==='quote' ? '' : 'none';
  document.getElementById('tab-summary').style.display = t==='summary' ? '' : 'none';
  document.querySelectorAll('#tabs .tab').forEach((el,i) => {
    el.classList.toggle('active', (t==='quote' && i===0) || (t==='summary' && i===1));
  });
  if (t === 'summary') renderSummary();
}

// ─────────────────────────────────────────────
// SYNC FROM SA VALUES
// ─────────────────────────────────────────────
function syncConcreteFromSA() {
  const nCols = numVal('sa_n_cols');
  const depth = numVal('sa_footing_depth');
  if (nCols > 0) {
    document.getElementById('conc_n_piers').value = nCols;
  }
  if (depth > 0) document.getElementById('conc_depth_ft').value = depth;
  calcConcrete();
  renderSummary();
}

// ─────────────────────────────────────────────
// CALCULATIONS
// ─────────────────────────────────────────────
function calcConcrete() {
  const n = numVal('conc_n_piers');
  const dia = numVal('conc_dia_in');
  const depth = numVal('conc_depth_ft');
  const priceCY = numVal('conc_price_cy');
  const rFt = (dia / 2) / 12;
  const volCY = Math.PI * rFt * rFt * depth / 27;
  const totalCY = n * volCY * 1.10;
  concreteCost = totalCY * priceCY;
  document.getElementById('conc_qty_display').textContent = totalCY.toFixed(2) + ' CY';
  document.getElementById('conc_cost_display').textContent = fmt(concreteCost);
  renderSummary();
}

function calcLabor() {
  const crew = numVal('lab_crew');
  const days = numVal('lab_days');
  const rate = numVal('lab_rate_hr');
  const hrs = numVal('lab_hrs_day');
  const daily = crew * rate * hrs;
  laborCost = daily * days;
  document.getElementById('lab_daily_display').textContent = fmt(daily) + '/day';
  document.getElementById('lab_total_display').textContent = fmt(laborCost);
  renderSummary();
}

function calcDrilling() {
  const method = document.getElementById('drill_method').value;
  const isRental = method === 'rental';
  document.getElementById('drill_rental_row').style.display = isRental ? '' : 'none';
  if (isRental) {
    drillingCost = (numVal('drill_rig_day') + numVal('drill_op_day')) * numVal('drill_days');
  } else {
    drillingCost = numVal('drill_n_holes') * numVal('drill_rate');
  }
  document.getElementById('drill_total_display').textContent = fmt(drillingCost);
  renderSummary();
}

function calcShipping() {
  const method = document.getElementById('ship_method').value;
  const isFlat = method === 'flat';
  document.getElementById('ship_flat_row').style.display = isFlat ? '' : 'none';
  document.getElementById('ship_rate_grp').style.display = isFlat ? 'none' : '';
  const loads = numVal('ship_loads') || 1;
  if (isFlat) {
    shippingCost = numVal('ship_flat_amt');
  } else {
    shippingCost = numVal('ship_miles') * numVal('ship_rate') * loads;
  }
  document.getElementById('ship_total_display').textContent = fmt(shippingCost);
  renderSummary();
}

function calcFuel() {
  const vehicles = numVal('fuel_vehicles');
  const miles = numVal('fuel_miles');
  const mpg = numVal('fuel_mpg') || 1;
  const priceGal = numVal('fuel_price_gal');
  const totalGal = vehicles * miles / mpg;
  fuelCost = totalGal * priceGal;
  document.getElementById('fuel_gal_display').textContent = totalGal.toFixed(1) + ' gal';
  document.getElementById('fuel_total_display').textContent = fmt(fuelCost);
  renderSummary();
}

function calcHotels() {
  const crew = numVal('hotel_crew');
  const nights = numVal('hotel_nights');
  const rate = numVal('hotel_rate');
  hotelCost = crew * nights * rate;
  document.getElementById('hotel_rooms_display').textContent = (crew * nights) + ' room-nights';
  document.getElementById('hotel_total_display').textContent = fmt(hotelCost);
  renderSummary();
}

function calcPerDiem() {
  const crew = numVal('pd_crew');
  const days = numVal('pd_days');
  const rate = numVal('pd_rate');
  perDiemCost = crew * days * rate;
  document.getElementById('pd_total_display').textContent = fmt(perDiemCost);
  renderSummary();
}

function calcTransport() {
  const vehicles = numVal('trans_vehicles');
  const miles = numVal('trans_miles');
  const rate = numVal('trans_rate');
  const trips = numVal('trans_trips') || 1;
  transportCost = vehicles * miles * rate * trips;
  document.getElementById('trans_total_display').textContent = fmt(transportCost);
  renderSummary();
}

function equipTotal() { return equipItems.reduce((s, i) => s + (i.qty * i.rate), 0); }
function miscTotal()  { return miscItems.reduce((s, i) => s + i.amount, 0); }

// ─────────────────────────────────────────────
// LINE ITEM TABLES
// ─────────────────────────────────────────────
function addEquipItem() {
  equipItems.push({ desc: '', qty: 1, unit: 'day', rate: 0 });
  renderEquipTable();
}
function removeEquipItem(idx) {
  equipItems.splice(idx, 1); renderEquipTable(); renderSummary();
}
function renderEquipTable() {
  const tbody = document.getElementById('equip_tbody');
  tbody.innerHTML = '';
  if (equipItems.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="color:#aaa;text-align:center;padding:10px">No equipment added.</td></tr>';
    renderSummary(); return;
  }
  equipItems.forEach((it, idx) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input type="text" value="${it.desc}" placeholder="e.g. 40-ton Crane"
        style="width:100%" onchange="equipItems[${idx}].desc=this.value;renderSummary()"/></td>
      <td><input type="number" value="${it.qty}" min="0" step="0.5"
        style="width:60px" onchange="equipItems[${idx}].qty=parseFloat(this.value)||0;renderEquipTable();renderSummary()"/></td>
      <td><select onchange="equipItems[${idx}].unit=this.value">
        ${['day','week','trip','ea'].map(u=>`<option${it.unit===u?' selected':''}>${u}</option>`).join('')}
      </select></td>
      <td><input type="number" value="${it.rate}" min="0" step="50"
        style="width:80px" onchange="equipItems[${idx}].rate=parseFloat(this.value)||0;renderEquipTable();renderSummary()"/></td>
      <td style="font-weight:700">${fmt(it.qty * it.rate)}</td>
      <td><button class="btn btn-danger btn-sm" onclick="removeEquipItem(${idx})">✕</button></td>`;
    tbody.appendChild(tr);
  });
  const totalTr = document.createElement('tr');
  totalTr.className = 'total-row';
  totalTr.innerHTML = `<td colspan="4" style="text-align:right">Equipment Total:</td><td colspan="2">${fmt(equipTotal())}</td>`;
  tbody.appendChild(totalTr);
}

function addMiscItem() {
  miscItems.push({ desc: '', amount: 0 }); renderMiscTable();
}
function removeMiscItem(idx) {
  miscItems.splice(idx, 1); renderMiscTable(); renderSummary();
}
function renderMiscTable() {
  const tbody = document.getElementById('misc_tbody');
  tbody.innerHTML = '';
  if (miscItems.length === 0) {
    tbody.innerHTML = '<tr><td colspan="3" style="color:#aaa;text-align:center;padding:10px">No misc items.</td></tr>';
    renderSummary(); return;
  }
  miscItems.forEach((it, idx) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input type="text" value="${it.desc}" placeholder="Description"
        style="width:100%" onchange="miscItems[${idx}].desc=this.value;renderSummary()"/></td>
      <td><input type="number" value="${it.amount}" min="0" step="100"
        style="width:120px" onchange="miscItems[${idx}].amount=parseFloat(this.value)||0;renderSummary()"/></td>
      <td><button class="btn btn-danger btn-sm" onclick="removeMiscItem(${idx})">✕</button></td>`;
    tbody.appendChild(tr);
  });
  const totalTr = document.createElement('tr');
  totalTr.className = 'total-row';
  totalTr.innerHTML = `<td style="text-align:right">Misc Total:</td><td colspan="2">${fmt(miscTotal())}</td>`;
  tbody.appendChild(totalTr);
}

// ─────────────────────────────────────────────
// SUMMARY
// ─────────────────────────────────────────────
function buildQuoteData() {
  const markup = numVal('proj_markup') / 100;
  const mats = numVal('sa_materials_cost');
  const equip = equipTotal();
  const misc = miscTotal();
  const sections = [
    { label: 'Materials (SA Fabrication)', cost: mats, key: 'materials' },
    { label: 'Concrete (Pier Footings)', cost: concreteCost, key: 'concrete' },
    { label: 'Labor — Installation', cost: laborCost, key: 'labor' },
    { label: 'Equipment Rental', cost: equip, key: 'equipment' },
    { label: 'Drilling', cost: drillingCost, key: 'drilling' },
    { label: 'Shipping & Freight', cost: shippingCost, key: 'shipping' },
    { label: 'Fuel & Gas', cost: fuelCost, key: 'fuel' },
    { label: 'Hotels', cost: hotelCost, key: 'hotels' },
    { label: 'Per Diem', cost: perDiemCost, key: 'perdiem' },
    { label: 'Transportation of Crew', cost: transportCost, key: 'transport' },
    { label: 'Miscellaneous', cost: misc, key: 'misc' },
  ];
  const subtotal = sections.reduce((s, x) => s + x.cost, 0);
  const markupAmt = subtotal * markup;
  const total = subtotal + markupAmt;
  return { sections, subtotal, markupAmt, total, markup, markupPct: numVal('proj_markup') };
}

function renderSummary() {
  const q = buildQuoteData();
  const sc = document.getElementById('stat-cards-summary');
  if (sc) sc.innerHTML = `
    <div class="stat"><div class="val">${fmt(q.subtotal)}</div><div class="lbl">Subtotal (cost)</div></div>
    <div class="stat"><div class="val">${fmt(q.markupAmt)}</div><div class="lbl">Markup (${q.markupPct}%)</div></div>
    <div class="stat" style="border-color:var(--tc-red)"><div class="val" style="color:var(--tc-red)">${fmt(q.total)}</div><div class="lbl">Total Sell Price</div></div>
    <div class="stat"><div class="val">${q.sections.filter(s=>s.cost>0).length}</div><div class="lbl">Cost Categories</div></div>`;
  const tbl = document.getElementById('summary-table');
  if (!tbl) return;
  let rows = '';
  q.sections.forEach(s => {
    if (s.cost === 0) return;
    rows += `<tr><td>${s.label}</td><td style="text-align:right;font-weight:600">${fmt(s.cost)}</td></tr>`;
  });
  rows += `
    <tr class="subtotal-row"><td><strong>SUBTOTAL</strong></td><td style="text-align:right"><strong>${fmt(q.subtotal)}</strong></td></tr>
    <tr class="markup-row"><td>Markup (${q.markupPct}%)</td><td style="text-align:right">${fmt(q.markupAmt)}</td></tr>
    <tr class="total-row"><td>TOTAL SELL PRICE</td><td style="text-align:right">${fmt(q.total)}</td></tr>`;
  tbl.innerHTML = rows;
}

// ─────────────────────────────────────────────
// EXPORT PAYLOAD
// ─────────────────────────────────────────────
function buildPayload() {
  const q = buildQuoteData();
  return {
    project: {
      name: strVal('proj_name'), job_code: strVal('proj_code'),
      customer_name: strVal('proj_customer'), address: strVal('proj_address'),
      city: strVal('proj_city'), state: strVal('proj_state'),
      quote_date: strVal('proj_date'), markup_pct: numVal('proj_markup'),
    },
    salesperson: {
      name: strVal('sp_name'), title: strVal('sp_title'),
      phone: strVal('sp_phone'), email: strVal('sp_email'),
    },
    sa: {
      quote_num: strVal('sa_quote_num'), materials_cost: numVal('sa_materials_cost'),
      n_cols: numVal('sa_n_cols'), footing_depth: numVal('sa_footing_depth'),
      width_ft: numVal('sa_width'), length_ft: numVal('sa_length'),
    },
    costs: {
      concrete: { n_piers: numVal('conc_n_piers'), dia_in: numVal('conc_dia_in'),
        depth_ft: numVal('conc_depth_ft'), price_cy: numVal('conc_price_cy'), total: concreteCost },
      labor: { crew: numVal('lab_crew'), days: numVal('lab_days'),
        rate_hr: numVal('lab_rate_hr'), hrs_day: numVal('lab_hrs_day'),
        notes: strVal('lab_notes'), total: laborCost },
      equipment: { items: equipItems, total: equipTotal() },
      drilling: { method: document.getElementById('drill_method').value,
        n_holes: numVal('drill_n_holes'), rate: numVal('drill_rate'),
        rig_day: numVal('drill_rig_day'), op_day: numVal('drill_op_day'),
        days: numVal('drill_days'), total: drillingCost },
      shipping: { method: document.getElementById('ship_method').value,
        miles: numVal('ship_miles'), rate: numVal('ship_rate'),
        flat_amt: numVal('ship_flat_amt'), loads: numVal('ship_loads'),
        notes: strVal('ship_notes'), total: shippingCost },
      fuel: { vehicles: numVal('fuel_vehicles'), miles: numVal('fuel_miles'),
        mpg: numVal('fuel_mpg'), price_gal: numVal('fuel_price_gal'), total: fuelCost },
      hotels: { crew: numVal('hotel_crew'), nights: numVal('hotel_nights'),
        rate: numVal('hotel_rate'), total: hotelCost },
      per_diem: { crew: numVal('pd_crew'), days: numVal('pd_days'),
        rate: numVal('pd_rate'), total: perDiemCost },
      transport: { vehicles: numVal('trans_vehicles'), miles: numVal('trans_miles'),
        rate: numVal('trans_rate'), trips: numVal('trans_trips'),
        notes: strVal('trans_notes'), total: transportCost },
      misc: { items: miscItems, total: miscTotal() },
    },
    summary: q,
  };
}

// ─────────────────────────────────────────────
// EXPORTS
// ─────────────────────────────────────────────
async function tcExportPDF() {
  try {
    const resp = await fetch('/tc/export/pdf', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify(buildPayload())
    });
    if (!resp.ok) { alert('PDF failed: ' + await resp.text()); return; }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = (strVal('proj_code') || 'TC-Quote') + '.pdf';
    a.click();
  } catch(e) { alert('Error: ' + e.message); }
}

async function tcExportExcel() {
  try {
    const resp = await fetch('/tc/export/excel', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify(buildPayload())
    });
    if (!resp.ok) { alert('Excel failed: ' + await resp.text()); return; }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = (strVal('proj_code') || 'TC-Quote') + '.xlsx';
    a.click();
  } catch(e) { alert('Error: ' + e.message); }
}

// ─────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  // Set today's date
  const today = new Date();
  document.getElementById('proj_date').value =
    String(today.getMonth()+1).padStart(2,'0') + '/' +
    String(today.getDate()).padStart(2,'0') + '/' + today.getFullYear();

  renderEquipTable();
  renderMiscTable();
  prefillFromURL();  // pre-fill from SA "Send to TC Quote" button
  calcConcrete(); calcLabor(); calcDrilling();
  calcShipping(); calcFuel(); calcHotels();
  calcPerDiem(); calcTransport(); renderSummary();

  // Sync crew/days
  document.getElementById('lab_crew').addEventListener('change', function() {
    document.getElementById('hotel_crew').value = this.value;
    document.getElementById('pd_crew').value = this.value;
    document.getElementById('trans_vehicles').value = Math.ceil(parseInt(this.value)/4);
    calcHotels(); calcPerDiem(); calcTransport();
  });
  document.getElementById('lab_days').addEventListener('change', function() {
    const days = parseFloat(this.value) || 0;
    if (days > 1) {
      document.getElementById('hotel_nights').value = Math.ceil(days - 1);
      document.getElementById('pd_days').value = Math.ceil(days);
      calcHotels(); calcPerDiem();
    }
  });
});
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
# TC OUTPUTS (PDF + EXCEL)
# ─────────────────────────────────────────────
try:
    from outputs.tc_pdf_gen import generate_construction_quote_pdf as _tc_pdf
    HAS_TC_PDF = True
except Exception:
    HAS_TC_PDF = False

try:
    from outputs.tc_excel_gen import generate_construction_quote_excel as _tc_excel
    HAS_TC_EXCEL = True
except Exception:
    HAS_TC_EXCEL = False


# ─────────────────────────────────────────────
# TORNADO HANDLERS
# ─────────────────────────────────────────────

class MainHandler(BaseHandler):
    def get(self):
        self.set_header("Content-Type", "text/html")
        self.write(MAIN_HTML)


class CalculateHandler(BaseHandler):
    def post(self):
        try:
            body = json_decode(self.request.body)
            proj_data = body["project"]
            bldg_data = body["buildings"]

            project = ProjectInfo(**{
                k: proj_data.get(k, v)
                for k, v in ProjectInfo.__dataclass_fields__.items()
                if k in proj_data
            })

            buildings = []
            for bd in bldg_data:
                bldg = BuildingConfig()
                for k, v in bd.items():
                    if hasattr(bldg, k):
                        setattr(bldg, k, v)
                buildings.append(bldg)

            calc = BOMCalculator(project)
            proj_bom = calc.calculate_project(buildings)
            result = bom_to_dict(proj_bom)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            import traceback
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class ExcelHandler(BaseHandler):
    def post(self):
        try:
            bom_data = json_decode(self.request.body)
            xlsx_bytes = generate_bom_excel(bom_data)
            job = bom_data.get("project", {}).get("job_code", "Quote")
            filename = f"SA_BOM_{job}.xlsx"
            self.set_header("Content-Type",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            self.set_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.write(xlsx_bytes)
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(f"Excel error: {e}\n{traceback.format_exc()}")


class PDFHandler(BaseHandler):
    def post(self):
        try:
            bom_data = json_decode(self.request.body)
            pdf_bytes = generate_quote_pdf(bom_data)
            job = bom_data.get("project", {}).get("job_code", "Quote")
            filename = f"SA_Quote_{job}.pdf"
            self.set_header("Content-Type", "application/pdf")
            self.set_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.write(pdf_bytes)
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(f"PDF error: {e}\n{traceback.format_exc()}")


def _build_labels_from_request(body: dict):
    """Shared helper: parse request body and return a labels list."""
    bom_data   = body["bom"]
    destination = body.get("destination", "")
    fabricator  = body.get("fabricator", "")
    qr_url      = body.get("qr_base_url", "https://structuresamerica.com/shop")
    grouping    = body.get("grouping", {})
    return generate_labels_from_bom(
        bom_data,
        destination=destination,
        fabricator=fabricator,
        qr_base_url=qr_url,
        grouping=grouping,
    )


class LabelsHandler(BaseHandler):
    def post(self):
        try:
            body   = json_decode(self.request.body)
            labels = _build_labels_from_request(body)
            zpl_str  = labels_to_zpl(labels)
            html_str = labels_to_preview_html(labels)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "count": len(labels),
                "zpl": zpl_str,
                "html": html_str,
            }))
        except Exception as e:
            import traceback
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class LabelsPDFHandler(BaseHandler):
    """Export all labels as a 4×6 PDF — one label per page."""
    def post(self):
        try:
            body   = json_decode(self.request.body)
            labels = _build_labels_from_request(body)
            pdf_bytes = labels_to_pdf(labels)
            job = body.get("bom", {}).get("project", {}).get("job_code", "Labels")
            self.set_header("Content-Type", "application/pdf")
            self.set_header("Content-Disposition",
                            f'attachment; filename="SA_Labels_{job}.pdf"')
            self.write(pdf_bytes)
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(f"Label PDF error: {e}\n{traceback.format_exc()}")


class LabelsCsvHandler(BaseHandler):
    """Export label data as CSV — import into NiceLabel / BarTender as data source."""
    def post(self):
        try:
            body   = json_decode(self.request.body)
            labels = _build_labels_from_request(body)
            csv_bytes = labels_to_csv(labels)
            job = body.get("bom", {}).get("project", {}).get("job_code", "Labels")
            self.set_header("Content-Type", "text/csv")
            self.set_header("Content-Disposition",
                            f'attachment; filename="SA_Labels_{job}.csv"')
            self.write(csv_bytes)
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(f"Label CSV error: {e}\n{traceback.format_exc()}")


class InventoryHandler(BaseHandler):
    def get(self):
        data = load_inventory()
        self.set_header("Content-Type", "application/json")
        self.write(json_encode(data))


class InventoryUpdateHandler(BaseHandler):
    def post(self):
        body = json_decode(self.request.body)
        data = load_inventory()
        coil_id = body.get("coil_id")
        add_lbs = float(body.get("add_lbs", 0))
        if coil_id and coil_id in data["coils"]:
            coil = data["coils"][coil_id]
            coil["stock_lbs"] = coil.get("stock_lbs", 0) + add_lbs
            lbs_per_lft = coil.get("lbs_per_lft", 1)
            coil["stock_lft"] = coil["stock_lbs"] / lbs_per_lft if lbs_per_lft else 0
            coil.setdefault("orders", []).append({
                "date": datetime.date.today().isoformat(),
                "lbs_added": add_lbs,
            })
            save_inventory(data)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True}))


class InventorySaveHandler(BaseHandler):
    """POST /api/inventory/save — Save full inventory JSON (used by addNewCoil)."""
    def post(self):
        try:
            body = json_decode(self.request.body)
            save_inventory(body)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True}))
        except Exception as e:
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e)}))


class InventoryCertHandler(BaseHandler):
    """Legacy JSON-only cert add (kept for backward compat)."""
    def post(self):
        cert = json_decode(self.request.body)
        data = load_inventory()
        data.setdefault("mill_certs", []).append(cert)
        save_inventory(data)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True}))


CERTS_DIR = os.path.join(BASE_DIR, "data", "certs")
os.makedirs(CERTS_DIR, exist_ok=True)


class InventoryCertUploadHandler(BaseHandler):
    """
    Multipart POST: PDF file + JSON metadata.
    Fields expected in the multipart body:
      coil_id, heat, mill, date   (text fields)
      pdf_file                    (file field, application/pdf)
    """
    def post(self):
        try:
            coil_id = self.get_body_argument("coil_id", "")
            heat    = self.get_body_argument("heat", "")
            mill    = self.get_body_argument("mill", "")
            cert_date = self.get_body_argument("date", "")

            filename = None
            if "pdf_file" in self.request.files:
                file_info = self.request.files["pdf_file"][0]
                if file_info["body"]:
                    # Build a safe filename: coilid_heat_timestamp.pdf
                    import re, time
                    safe_coil = re.sub(r"[^a-zA-Z0-9_-]", "", coil_id)[:20]
                    safe_heat = re.sub(r"[^a-zA-Z0-9_-]", "", heat)[:20]
                    ts = int(time.time())
                    filename = f"{safe_coil}_{safe_heat}_{ts}.pdf"
                    with open(os.path.join(CERTS_DIR, filename), "wb") as f:
                        f.write(file_info["body"])

            cert = {
                "coil_id":  coil_id,
                "heat":     heat,
                "mill":     mill,
                "date":     cert_date,
                "filename": filename,       # None if no PDF uploaded
                "added":    datetime.date.today().isoformat(),
            }
            data = load_inventory()
            data.setdefault("mill_certs", []).append(cert)
            save_inventory(data)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "filename": filename}))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class CertFileHandler(BaseHandler):
    """Serve a stored mill cert PDF by filename."""
    def get(self, filename):
        import re
        # Safety: only allow plain filenames, no path traversal
        if not re.match(r"^[a-zA-Z0-9_.-]+\.pdf$", filename):
            self.set_status(400)
            self.write("Invalid filename")
            return
        path = os.path.join(CERTS_DIR, filename)
        if not os.path.isfile(path):
            self.set_status(404)
            self.write("Cert PDF not found")
            return
        self.set_header("Content-Type", "application/pdf")
        self.set_header("Content-Disposition",
                        f'inline; filename="{filename}"')
        with open(path, "rb") as f:
            self.write(f.read())


# ─────────────────────────────────────────────
# COIL STICKER HANDLERS
# ─────────────────────────────────────────────

class CoilDeleteHandler(BaseHandler):
    """
    POST /api/inventory/delete
    Body JSON: { coil_id: "xxx" }
    Permanently removes the coil and all associated mill certs + cert PDF files.
    """
    def post(self):
        try:
            body = json_decode(self.request.body)
            coil_id = body.get("coil_id", "").strip()
            if not coil_id:
                self.write(json_encode({"ok": False, "error": "No coil_id provided"}))
                return

            data = load_inventory()
            coils = data.get("coils", {})
            if coil_id not in coils:
                self.write(json_encode({"ok": False, "error": f"Coil '{coil_id}' not found"}))
                return

            # Remove the coil
            del coils[coil_id]

            # Remove associated mill certs and delete their PDF files
            old_certs = data.get("mill_certs", [])
            kept_certs = []
            for cert in old_certs:
                if (cert.get("coil_id") or cert.get("material", "")) == coil_id:
                    # Delete the PDF file if it exists
                    fname = cert.get("filename")
                    if fname:
                        fpath = os.path.join(CERTS_DIR, fname)
                        if os.path.isfile(fpath):
                            os.remove(fpath)
                else:
                    kept_certs.append(cert)
            data["mill_certs"] = kept_certs

            save_inventory(data)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "deleted": coil_id}))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class ProjectSaveHandler(BaseHandler):
    """
    POST /api/project/save
    Saves full project state (project info, buildings, BOM data, price overrides, manual items)
    to data/projects/{job_code}.json
    """
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            if not job_code:
                self.write(json_encode({"ok": False, "error": "No job_code"}))
                return
            import re
            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            projects_dir = os.path.join(BASE_DIR, "data", "projects")
            os.makedirs(projects_dir, exist_ok=True)
            fpath = os.path.join(projects_dir, f"{safe_name}.json")
            body["saved_at"] = datetime.datetime.now().isoformat()
            with open(fpath, "w") as f:
                json.dump(body, f, indent=2)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "file": f"{safe_name}.json"}))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class ProjectLoadHandler(BaseHandler):
    """POST /api/project/load — Load a saved project by job_code."""
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            import re
            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            fpath = os.path.join(BASE_DIR, "data", "projects", f"{safe_name}.json")
            if not os.path.isfile(fpath):
                self.write(json_encode({"ok": False, "error": "Project not found"}))
                return
            with open(fpath) as f:
                data = json.load(f)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "data": data}))
        except Exception as e:
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e)}))


class ProjectListHandler(BaseHandler):
    """GET /api/projects — List all saved projects."""
    def get(self):
        projects_dir = os.path.join(BASE_DIR, "data", "projects")
        os.makedirs(projects_dir, exist_ok=True)
        result = []
        for fname in sorted(os.listdir(projects_dir), reverse=True):
            if fname.endswith(".json"):
                fpath = os.path.join(projects_dir, fname)
                try:
                    with open(fpath) as f:
                        data = json.load(f)
                    result.append({
                        "job_code": data.get("job_code", fname.replace(".json", "")),
                        "project_name": data.get("project", {}).get("name", ""),
                        "customer": data.get("project", {}).get("customer_name", ""),
                        "saved_at": data.get("saved_at", ""),
                        "file": fname,
                    })
                except Exception:
                    pass
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"projects": result}))


class CoilStickerHandler(BaseHandler):
    """
    POST /api/inventory/sticker
    Body JSON:  { coil_id, format: "pdf"|"zpl"|"csv", coil: {...optional overrides} }
    Also accepts format as query param: ?format=pdf
    If the coil dict contains a 'create_entry' flag, a new inventory entry is created.
    """
    def post(self):
        try:
            from outputs.zpl_gen import coil_sticker_to_pdf, coil_sticker_to_zpl, coil_stickers_to_csv
            body = json_decode(self.request.body)
            fmt  = body.get("format", self.get_query_argument("format", "pdf")).lower()

            # Merge inventory record with any overrides from the form
            coil_id    = body.get("coil_id", "")
            coil_extra = body.get("coil", {})

            inv = load_inventory()
            coils = inv.get("coils", {})

            base = dict(coils.get(coil_id, {}))
            base["coil_id"] = coil_id
            base.setdefault("name", base.get("description", coil_id))
            base["description"] = base.get("name", coil_id)
            # merge in any form values
            for k, v in coil_extra.items():
                if v not in ("", None):
                    base[k] = v

            # Optional: create a new coil entry if requested
            if coil_extra.get("create_entry") and coil_id and coil_id not in coils:
                new_entry = {
                    "name":           coil_extra.get("description", coil_id),
                    "gauge":          coil_extra.get("gauge", ""),
                    "grade":          coil_extra.get("grade", ""),
                    "supplier":       coil_extra.get("supplier", ""),
                    "weight_lbs":     coil_extra.get("weight_lbs", 0),
                    "width_in":       coil_extra.get("width_in", 0),
                    "stock_lbs":      coil_extra.get("qty_on_hand", 0),
                    "stock_lft":      0,
                    "committed_lbs":  0,
                    "min_order_lbs":  5000,
                    "lead_time_weeks":8,
                    "price_per_lb":   0.0,
                    "lbs_per_lft":    0.0,
                    "coil_max_lbs":   coil_extra.get("weight_lbs", 8000),
                    "orders":         [],
                    "received_date":  coil_extra.get("received_date", ""),
                    "heat_num":       coil_extra.get("heat_num", ""),
                    "sticker_printed": True,
                }
                coils[coil_id] = new_entry
                inv["coils"] = coils
                save_inventory(inv)
                base.update(new_entry)
                base["coil_id"] = coil_id

            # Map stock_lbs → qty_on_hand for display
            if "qty_on_hand" not in base:
                base["qty_on_hand"] = base.get("stock_lbs", 0)

            if fmt == "pdf":
                data = coil_sticker_to_pdf(base)
                self.set_header("Content-Type", "application/pdf")
                self.set_header("Content-Disposition",
                                f'attachment; filename="Coil_Sticker_{coil_id}.pdf"')
                self.write(data)
            elif fmt == "zpl":
                data = coil_sticker_to_zpl(base)
                self.set_header("Content-Type", "text/plain")
                self.set_header("Content-Disposition",
                                f'attachment; filename="Coil_Sticker_{coil_id}.zpl"')
                self.write(data)
            elif fmt == "csv":
                data = coil_stickers_to_csv([base])
                self.set_header("Content-Type", "text/csv")
                self.set_header("Content-Disposition",
                                f'attachment; filename="Coil_Sticker_{coil_id}.csv"')
                self.write(data)
            else:
                self.set_status(400)
                self.write(json_encode({"error": f"Unknown format: {fmt}"}))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(f"Sticker error: {e}\n{traceback.format_exc()}")


COIL_DETAIL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Coil Status — Structures America</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Arial, sans-serif; background: #f4f6f9; color: #222; }
  .topbar { background: #003A6E; color: #fff; padding: 14px 20px;
            display: flex; align-items: center; gap: 12px; }
  .topbar h1 { font-size: 18px; }
  .topbar .sub { font-size: 12px; color: #aac4e0; margin-top: 2px; }
  .badge { background: #C89A2E; color: #fff; border-radius: 4px;
           padding: 3px 10px; font-size: 12px; font-weight: bold; }
  .card { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #0001;
          margin: 16px; padding: 18px; }
  .card h2 { font-size: 14px; color: #003A6E; text-transform: uppercase;
             letter-spacing: 0.04em; margin-bottom: 12px;
             border-bottom: 2px solid #C89A2E; padding-bottom: 6px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .field label { font-size: 11px; color: #888; text-transform: uppercase;
                 font-weight: bold; display: block; margin-bottom: 2px; }
  .field span { font-size: 15px; font-weight: bold; color: #222; }
  .status-pill { display: inline-block; border-radius: 20px;
                 padding: 5px 16px; font-size: 13px; font-weight: bold; }
  .status-available { background: #d4edda; color: #155724; }
  .status-committed  { background: #fff3cd; color: #856404; }
  .status-out        { background: #f8d7da; color: #721c24; }
  .job-row { display: flex; justify-content: space-between; align-items: center;
             padding: 8px 0; border-bottom: 1px solid #eee; font-size: 14px; }
  .job-row:last-child { border-bottom: none; }
  .cert-row { padding: 8px 0; border-bottom: 1px solid #eee; font-size: 13px; }
  .cert-row a { color: #003A6E; text-decoration: none; font-weight: bold; }
  .cert-row a:hover { text-decoration: underline; }
  .empty { color: #aaa; font-style: italic; font-size: 13px; }
  .back-btn { display: inline-block; margin: 16px; padding: 9px 18px;
              background: #003A6E; color: #fff; border-radius: 5px;
              text-decoration: none; font-size: 13px; font-weight: bold; }
</style>
</head>
<body>
<div class="topbar">
  <div>
    <h1>Coil Status — {{coil_id}}</h1>
    <div class="sub">Structures America · Inventory Tracking</div>
  </div>
  <div style="margin-left:auto">
    <span class="badge">{{status_label}}</span>
  </div>
</div>

<div class="card">
  <h2>Coil Details</h2>
  <div class="grid">
    <div class="field"><label>Coil ID</label><span>{{coil_id}}</span></div>
    <div class="field"><label>Description</label><span>{{description}}</span></div>
    <div class="field"><label>Grade</label><span>{{grade}}</span></div>
    <div class="field"><label>Gauge</label><span>{{gauge}}</span></div>
    <div class="field"><label>Heat #</label><span>{{heat_num}}</span></div>
    <div class="field"><label>Supplier</label><span>{{supplier}}</span></div>
    <div class="field"><label>Weight (lbs)</label><span>{{weight_lbs}}</span></div>
    <div class="field"><label>Width (in)</label><span>{{width_in}}</span></div>
    <div class="field"><label>Received</label><span>{{received_date}}</span></div>
  </div>
</div>

<div class="card">
  <h2>Stock Status</h2>
  <div style="margin-bottom:12px">
    <span class="status-pill {{status_class}}">{{status_label}}</span>
  </div>
  <div class="grid">
    <div class="field"><label>On Hand (lbs)</label><span>{{stock_lbs}}</span></div>
    <div class="field"><label>Committed (lbs)</label><span>{{committed_lbs}}</span></div>
    <div class="field"><label>Available (lbs)</label><span style="color:{{avail_color}}">{{available_lbs}}</span></div>
    <div class="field"><label>Min Order (lbs)</label><span>{{min_order_lbs}}</span></div>
  </div>
</div>

<div class="card">
  <h2>Assigned to Jobs</h2>
  {{jobs_html}}
</div>

<div class="card">
  <h2>Mill Certificates</h2>
  {{certs_html}}
</div>

<a class="back-btn" href="/">← Back to Calculator</a>
</body>
</html>"""


class CoilDetailHandler(BaseHandler):
    """
    GET /coil/{coil_id}
    Mobile-friendly coil status page — linked from the QR code on inventory stickers.
    """
    def get(self, coil_id):
        inv   = load_inventory()
        coils = inv.get("coils", {})
        coil  = coils.get(coil_id)

        if coil is None:
            self.set_status(404)
            self.write(f"<html><body><h2>Coil '{coil_id}' not found</h2>"
                       "<p>This coil ID is not currently in the inventory system.</p>"
                       "<a href='/'>← Back to Calculator</a></body></html>")
            return

        stock_lbs     = coil.get("stock_lbs", 0)
        committed_lbs = coil.get("committed_lbs", 0)
        available_lbs = max(0, stock_lbs - committed_lbs)

        if available_lbs > 0 and committed_lbs == 0:
            status_label = "AVAILABLE"
            status_class = "status-available"
            avail_color  = "#155724"
        elif available_lbs > 0:
            status_label = "PARTIALLY COMMITTED"
            status_class = "status-committed"
            avail_color  = "#856404"
        else:
            status_label = "FULLY COMMITTED / OUT"
            status_class = "status-out"
            avail_color  = "#721c24"

        # Build jobs list
        projects = inv.get("projects", {})
        assigned_jobs = []
        for job_code, proj in projects.items():
            for item in proj.get("materials", []):
                if item.get("coil_id") == coil_id:
                    assigned_jobs.append({
                        "job_code": job_code,
                        "name":     proj.get("name", ""),
                        "lbs":      item.get("lbs_committed", 0),
                    })

        if assigned_jobs:
            rows = "".join(
                f'<div class="job-row">'
                f'<span><strong>{j["job_code"]}</strong> — {j["name"]}</span>'
                f'<span style="color:#888">{j["lbs"]:,} lbs</span>'
                f'</div>'
                for j in assigned_jobs
            )
        else:
            rows = '<p class="empty">No jobs currently assigned to this coil.</p>'

        # Build certs list
        mill_certs = inv.get("mill_certs", {})
        coil_certs = [c for c in mill_certs.values()
                      if c.get("coil_id") == coil_id]
        if coil_certs:
            cert_rows = "".join(
                f'<div class="cert-row">'
                f'<strong>Heat: {c.get("heat_num","—")}</strong>'
                f' &nbsp;|&nbsp; Uploaded: {c.get("uploaded_at","")[:10]}'
                f' &nbsp;|&nbsp; <a href="/certs/{c["filename"]}" target="_blank">📄 VIEW PDF</a>'
                f'</div>'
                for c in coil_certs
            )
        else:
            cert_rows = '<p class="empty">No mill certificates uploaded for this coil.</p>'

        html = COIL_DETAIL_HTML
        replacements = {
            "{{coil_id}}":      coil_id,
            "{{description}}":  coil.get("name", coil_id),
            "{{grade}}":        coil.get("grade", "—"),
            "{{gauge}}":        coil.get("gauge", "—"),
            "{{heat_num}}":     coil.get("heat_num", "—"),
            "{{supplier}}":     coil.get("supplier", "—"),
            "{{weight_lbs}}":   str(coil.get("weight_lbs", "—")),
            "{{width_in}}":     str(coil.get("width_in", "—")),
            "{{received_date}}":coil.get("received_date", "—"),
            "{{stock_lbs}}":    f"{stock_lbs:,}",
            "{{committed_lbs}}":f"{committed_lbs:,}",
            "{{available_lbs}}":f"{available_lbs:,}",
            "{{avail_color}}":  avail_color,
            "{{min_order_lbs}}":f"{coil.get('min_order_lbs', 0):,}",
            "{{status_label}}": status_label,
            "{{status_class}}": status_class,
            "{{jobs_html}}":    rows,
            "{{certs_html}}":   cert_rows,
        }
        for placeholder, value in replacements.items():
            html = html.replace(placeholder, value)

        self.set_header("Content-Type", "text/html")
        self.write(html)


# ─────────────────────────────────────────────
# TC HANDLERS
# ─────────────────────────────────────────────

class TCMainHandler(BaseHandler):
    """Serves the Titan Carports Construction Quote Calculator at /tc"""
    def get(self):
        self.set_header("Content-Type", "text/html")
        self.write(TC_HTML)


class TCExportPDFHandler(BaseHandler):
    def post(self):
        try:
            data = json_decode(self.request.body)
            if HAS_TC_PDF:
                pdf_bytes = _tc_pdf(data)
                job = data.get("project", {}).get("job_code", "TC-Quote")
                self.set_header("Content-Type", "application/pdf")
                self.set_header("Content-Disposition", f'attachment; filename="{job}.pdf"')
                self.write(pdf_bytes)
            else:
                self.set_status(501)
                self.write("TC PDF generation not available (install reportlab: pip install reportlab)")
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(f"TC PDF error: {e}\n{traceback.format_exc()}")


class TCExportExcelHandler(BaseHandler):
    def post(self):
        try:
            data = json_decode(self.request.body)
            if HAS_TC_EXCEL:
                xl_bytes = _tc_excel(data)
                job = data.get("project", {}).get("job_code", "TC-Quote")
                self.set_header("Content-Type",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                self.set_header("Content-Disposition", f'attachment; filename="{job}.xlsx"')
                self.write(xl_bytes)
            else:
                self.set_status(501)
                self.write("TC Excel not available (install openpyxl: pip install openpyxl)")
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(f"TC Excel error: {e}\n{traceback.format_exc()}")


# ─────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────

def make_app():
    global COOKIE_SECRET
    if COOKIE_SECRET is None:
        secret_path = os.path.join(BASE_DIR, "data", ".cookie_secret")
        if os.path.isfile(secret_path):
            with open(secret_path) as f:
                COOKIE_SECRET = f.read().strip()
        else:
            COOKIE_SECRET = secrets.token_hex(32)
            os.makedirs(os.path.dirname(secret_path), exist_ok=True)
            with open(secret_path, "w") as f:
                f.write(COOKIE_SECRET)

    _ensure_users_file()

    static_path = os.path.join(BASE_DIR, "static")
    return tornado.web.Application([
        # ── Auth routes ────────────────────────────────────────
        (r"/auth/login",         LoginHandler),
        (r"/auth/logout",        LogoutHandler),
        (r"/admin",              AdminPageHandler),
        (r"/auth/users",         UsersListHandler),
        (r"/auth/users/add",     UserAddHandler),
        (r"/auth/users/delete",  UserDeleteHandler),
        # ── App routes ─────────────────────────────────────────
        (r"/",                      MainHandler),
        (r"/tc",                    TCMainHandler),
        (r"/api/calculate",         CalculateHandler),
        (r"/api/excel",             ExcelHandler),
        (r"/api/pdf",               PDFHandler),
        (r"/api/labels",            LabelsHandler),
        (r"/api/labels/pdf",        LabelsPDFHandler),
        (r"/api/labels/csv",        LabelsCsvHandler),
        (r"/api/inventory",              InventoryHandler),
        (r"/api/inventory/update",       InventoryUpdateHandler),
        (r"/api/inventory/save",         InventorySaveHandler),
        (r"/api/inventory/cert",         InventoryCertHandler),
        (r"/api/inventory/cert/upload",  InventoryCertUploadHandler),
        (r"/certs/([^/]+)",              CertFileHandler),
        (r"/api/inventory/delete",       CoilDeleteHandler),
        (r"/api/inventory/sticker",      CoilStickerHandler),
        (r"/coil/([^/]+)",               CoilDetailHandler),
        (r"/api/project/save",           ProjectSaveHandler),
        (r"/api/project/load",           ProjectLoadHandler),
        (r"/api/projects",               ProjectListHandler),
        (r"/tc/export/pdf",              TCExportPDFHandler),
        (r"/tc/export/excel",       TCExportExcelHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static_path}),
    ], cookie_secret=COOKIE_SECRET)


def open_browser(port: int, delay: float = 1.5):
    """Open browser after a short delay."""
    import time
    time.sleep(delay)
    webbrowser.open(f"http://localhost:{port}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Structures America + Titan Carports Calculator")
    # Railway/Render set PORT env var; fall back to 8888 for local dev
    default_port = int(os.environ.get("PORT", 8888))
    parser.add_argument("--port", type=int, default=default_port, help="Port to run on (default: 8888)")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    parser.add_argument("--auth", action="store_true",
                        help="Enable login/authentication (required for hosted deployments)")
    args = parser.parse_args()

    # Enable auth if --auth flag is set or AUTH_ENABLED env var is truthy
    AUTH_ENABLED = args.auth or os.environ.get("AUTH_ENABLED", "").lower() in ("1", "true", "yes")

    # Ensure data directories exist
    os.makedirs(os.path.join(BASE_DIR, "data", "certs"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "data", "projects"), exist_ok=True)

    app = make_app()
    # Bind to 0.0.0.0 for cloud hosting (Railway, Render, DigitalOcean)
    bind_addr = os.environ.get("BIND_ADDR", "0.0.0.0" if AUTH_ENABLED else "127.0.0.1")
    app.listen(args.port, address=bind_addr)

    auth_status = "ON — login required" if AUTH_ENABLED else "OFF — open access (local mode)"
    print("=" * 60)
    print("  SA + TC Combined Calculator  v2.6")
    print(f"  SA Material Takeoff:  http://localhost:{args.port}/")
    print(f"  TC Construction Quote: http://localhost:{args.port}/tc")
    if AUTH_ENABLED:
        print(f"  Admin Panel:          http://localhost:{args.port}/admin")
    print(f"  Authentication:       {auth_status}")
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    if not args.no_browser:
        t = threading.Thread(target=open_browser, args=(args.port,), daemon=True)
        t.start()

    tornado.ioloop.IOLoop.current().start()
