"""
TitanForge v3.0 Backend Handlers
Complete rewrite of handler classes for the steel fabrication shop management system.
Includes: Auth (4-tier roles), Calculation, Inventory, Projects, Documents, Status tracking.
"""

import os, sys, json, io, datetime, hashlib, uuid, secrets, re, glob, time
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

# ── TC Outputs (PDF + EXCEL) ─────────────────────────────────────────
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
# FILE PATHS & CONSTANTS
# ─────────────────────────────────────────────

INVENTORY_PATH = os.path.join(BASE_DIR, "data", "inventory.json")
USERS_PATH = os.path.join(BASE_DIR, "data", "users.json")
CERTS_DIR = os.path.join(BASE_DIR, "data", "certs")
PROJECTS_DIR = os.path.join(BASE_DIR, "data", "projects")
COOKIE_SECRET = None   # Set at startup from env or auto-generated

# Auth is enabled by default for hosted deployments; disabled for localhost dev.
AUTH_ENABLED = False   # Set at startup

# 4-Tier Role System
ROLE_PERMISSIONS = {
    "admin": [
        "quotes", "pricing", "bom", "inventory", "projects", "labels",
        "price_overrides", "user_management", "project_documents", "project_status"
    ],
    "estimator": [
        "quotes", "pricing", "bom", "inventory", "projects", "labels", "price_overrides"
    ],
    "shop": [
        "work_orders", "inventory", "quality", "labels", "project_documents"
    ],
    "viewer": [
        "quotes", "bom", "projects", "labels"
    ],
    "tc_limited": [
        "project_status", "shipping", "install_schedules"
    ]
}

PROJECT_DOC_CATEGORIES = [
    "quotes", "contracts", "engineering", "shop_drawings",
    "mill_certs", "photos", "other"
]

PROJECT_STAGES = [
    "quote", "contract", "engineering", "shop_drawings",
    "fabrication", "shipping", "install", "complete"
]


# ─────────────────────────────────────────────
# INVENTORY & USERS FILE MANAGEMENT
# ─────────────────────────────────────────────

def load_inventory():
    """Load inventory from JSON."""
    with open(INVENTORY_PATH, "r") as f:
        return json.load(f)

def save_inventory(data):
    """Save inventory to JSON."""
    with open(INVENTORY_PATH, "w") as f:
        json.dump(data, f, indent=2)

def load_users():
    """Load users from JSON. Creates default users if file doesn't exist."""
    if not os.path.isfile(USERS_PATH):
        _ensure_users_file()
    with open(USERS_PATH, "r") as f:
        return json.load(f)

def save_users(data):
    """Save users to JSON."""
    with open(USERS_PATH, "w") as f:
        json.dump(data, f, indent=2)

def _ensure_users_file():
    """Create users.json with default admin account if it doesn't exist."""
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
            "role": "estimator",
            "created": datetime.datetime.now().isoformat(),
        },
    }
    os.makedirs(os.path.dirname(USERS_PATH), exist_ok=True)
    with open(USERS_PATH, "w") as f:
        json.dump(users, f, indent=2)
    print(f"  [AUTH] Created default users file: {USERS_PATH}")
    print(f"  [AUTH] Default login  →  admin / titan2026")
    print(f"  [AUTH]                →  brad  / brad2026")

def verify_password(stored_hash: str, password: str) -> bool:
    """Verify password against stored hash (bcrypt or SHA256)."""
    if HAS_BCRYPT and stored_hash.startswith("$2"):
        return bcrypt.checkpw(password.encode(), stored_hash.encode())
    return stored_hash == hashlib.sha256(password.encode()).hexdigest()

def hash_password(password: str) -> str:
    """Hash password using bcrypt or SHA256."""
    if HAS_BCRYPT:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return hashlib.sha256(password.encode()).hexdigest()

def check_role(user_role: str, required_roles: list) -> bool:
    """Check if user role has permission for required roles."""
    return user_role in required_roles

def get_user_permissions(user_role: str) -> list:
    """Get list of permissions for a user role."""
    return ROLE_PERMISSIONS.get(user_role, [])


# ─────────────────────────────────────────────
# BASE AUTHENTICATED HANDLER WITH ROLE CHECKING
# ─────────────────────────────────────────────

class BaseHandler(tornado.web.RequestHandler):
    """Base handler that checks authentication and role permissions."""
    required_roles = None  # Override in subclasses. None = no role check.

    def get_current_user(self):
        """Get current authenticated user (username or 'local' in dev mode)."""
        if not AUTH_ENABLED:
            return "local"
        cookie = self.get_secure_cookie("sa_user")
        if cookie:
            return cookie.decode("utf-8")
        return None

    def get_user_role(self):
        """Get current user's role."""
        if not AUTH_ENABLED:
            return "admin"
        current = self.get_current_user()
        if not current:
            return None
        users = load_users()
        return users.get(current, {}).get("role", "viewer")

    def check_permission(self, permission: str) -> bool:
        """Check if current user has a specific permission."""
        role = self.get_user_role()
        if not role:
            return False
        return permission in get_user_permissions(role)

    def prepare(self):
        """Check auth before handling request."""
        if not AUTH_ENABLED:
            return
        path = self.request.path
        if path.startswith("/auth/") or path.startswith("/static/"):
            return

        current = self.get_current_user()
        if not current:
            if self.request.method == "GET":
                self.redirect("/auth/login")
            else:
                self.set_status(401)
                self.write(json_encode({"error": "Not authenticated"}))
            raise tornado.web.Finish()

        # Check role permissions if required
        if self.required_roles is not None:
            role = self.get_user_role()
            if not check_role(role, self.required_roles):
                self.set_status(403)
                self.write(json_encode({"error": "Insufficient permissions for this action"}))
                raise tornado.web.Finish()


# ─────────────────────────────────────────────
# AUTH HANDLERS
# ─────────────────────────────────────────────

class LoginHandler(tornado.web.RequestHandler):
    """POST /auth/login — Authenticate user and set secure cookie."""
    def get(self):
        # If already logged in, redirect to dashboard
        if self.get_secure_cookie("sa_user"):
            self.redirect("/")
            return
        # HTML served from external module (will be imported)
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
    """GET /auth/logout — Clear session and redirect to login."""
    def get(self):
        self.clear_cookie("sa_user")
        self.redirect("/auth/login")


class AdminPageHandler(BaseHandler):
    """GET /admin — User management page (admin only)."""
    required_roles = ["admin"]

    def get(self):
        self.set_header("Content-Type", "text/html")
        self.write(ADMIN_HTML)


class UsersListHandler(BaseHandler):
    """GET /auth/users — List all users (admin only)."""
    required_roles = ["admin"]

    def get(self):
        users = load_users()
        safe = {}
        for uname, udata in users.items():
            safe[uname] = {
                "display_name": udata.get("display_name", ""),
                "role": udata.get("role", "viewer"),
                "created": udata.get("created", ""),
            }
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"users": safe}))


class UserAddHandler(BaseHandler):
    """POST /auth/users/add — Add a new user (admin only)."""
    required_roles = ["admin"]

    def post(self):
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
            "role": body.get("role", "viewer"),
            "created": datetime.datetime.now().isoformat(),
        }
        save_users(users)
        self.write(json_encode({"ok": True}))


class UserDeleteHandler(BaseHandler):
    """POST /auth/users/delete — Delete a user (admin only)."""
    required_roles = ["admin"]

    def post(self):
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
# APP PAGE HANDLERS (Dashboard, Calculators)
# ─────────────────────────────────────────────

class DashboardHandler(BaseHandler):
    """GET / — Main TitanForge dashboard."""
    def get(self):
        self.set_header("Content-Type", "text/html")
        # Inject user role and name into the dashboard template
        user = self.get_current_user() or "local"
        users = load_users()
        role = users.get(user, {}).get("role", "viewer") if user != "local" else "admin"
        display = users.get(user, {}).get("display_name", user) if user != "local" else "Admin"
        html = DASHBOARD_HTML.replace("{{USER_ROLE}}", role).replace("{{USER_NAME}}", display)
        self.write(html)


class SACalcHandler(BaseHandler):
    """GET /sa — SA Calculator (Structures America)."""
    def get(self):
        self.set_header("Content-Type", "text/html")
        self.write(MAIN_HTML)


class TCQuoteHandler(BaseHandler):
    """GET /tc — TC Quote Calculator (Titan Carports)."""
    def get(self):
        self.set_header("Content-Type", "text/html")
        self.write(TC_HTML)


# ─────────────────────────────────────────────
# CALCULATION & EXPORT HANDLERS
# ─────────────────────────────────────────────

class CalculateHandler(BaseHandler):
    """POST /api/calculate — Calculate BOM from project/building data."""
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
    """POST /api/excel — Export BOM as Excel."""
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
    """POST /api/pdf — Export BOM as PDF."""
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


# ─────────────────────────────────────────────
# LABELS HANDLERS
# ─────────────────────────────────────────────

def _build_labels_from_request(body: dict):
    """Shared helper: parse request body and return labels list."""
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
    """POST /api/labels — Generate shop fabrication labels."""
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
    """POST /api/labels/pdf — Export labels as PDF."""
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
    """POST /api/labels/csv — Export labels as CSV."""
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


# ─────────────────────────────────────────────
# INVENTORY HANDLERS
# ─────────────────────────────────────────────

class InventoryHandler(BaseHandler):
    """GET /api/inventory — Fetch current inventory."""
    def get(self):
        data = load_inventory()
        self.set_header("Content-Type", "application/json")
        self.write(json_encode(data))


class InventoryUpdateHandler(BaseHandler):
    """POST /api/inventory/update — Update coil stock."""
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
    """POST /api/inventory/save — Save full inventory JSON."""
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
    """POST /api/inventory/cert — Add mill certificate (legacy JSON-only)."""
    def post(self):
        cert = json_decode(self.request.body)
        data = load_inventory()
        data.setdefault("mill_certs", []).append(cert)
        save_inventory(data)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True}))


class InventoryCertUploadHandler(BaseHandler):
    """POST /api/inventory/cert/upload — Upload mill certificate PDF + metadata."""
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
                    safe_coil = re.sub(r"[^a-zA-Z0-9_-]", "", coil_id)[:20]
                    safe_heat = re.sub(r"[^a-zA-Z0-9_-]", "", heat)[:20]
                    ts = int(time.time())
                    filename = f"{safe_coil}_{safe_heat}_{ts}.pdf"
                    os.makedirs(CERTS_DIR, exist_ok=True)
                    with open(os.path.join(CERTS_DIR, filename), "wb") as f:
                        f.write(file_info["body"])

            cert = {
                "coil_id":  coil_id,
                "heat":     heat,
                "mill":     mill,
                "date":     cert_date,
                "filename": filename,
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
    """GET /certs/{filename} — Serve mill cert PDF."""
    def get(self, filename):
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
# COIL MANAGEMENT HANDLERS
# ─────────────────────────────────────────────

class CoilDeleteHandler(BaseHandler):
    """POST /api/inventory/delete — Delete coil and associated certs."""
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

            del coils[coil_id]

            # Remove associated mill certs and delete their PDF files
            old_certs = data.get("mill_certs", [])
            kept_certs = []
            for cert in old_certs:
                if (cert.get("coil_id") or cert.get("material", "")) == coil_id:
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


class CoilStickerHandler(BaseHandler):
    """POST /api/inventory/sticker — Generate coil sticker (PDF/ZPL/CSV)."""
    def post(self):
        try:
            body = json_decode(self.request.body)
            fmt  = body.get("format", self.get_query_argument("format", "pdf")).lower()

            coil_id    = body.get("coil_id", "")
            coil_extra = body.get("coil", {})

            inv = load_inventory()
            coils = inv.get("coils", {})

            base = dict(coils.get(coil_id, {}))
            base["coil_id"] = coil_id
            base.setdefault("name", base.get("description", coil_id))
            base["description"] = base.get("name", coil_id)
            for k, v in coil_extra.items():
                if v not in ("", None):
                    base[k] = v

            # Optional: create new coil entry if requested
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


class CoilDetailHandler(BaseHandler):
    """GET /coil/{coil_id} — Mobile coil status page (linked from QR code)."""
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
        mill_certs = inv.get("mill_certs", [])
        if isinstance(mill_certs, dict):
            mill_certs = list(mill_certs.values())
        coil_certs = [c for c in mill_certs
                      if c.get("coil_id") == coil_id]
        if coil_certs:
            cert_rows = "".join(
                f'<div class="cert-row">'
                f'<strong>Heat: {c.get("heat_num", c.get("heat", "—"))}</strong>'
                f' &nbsp;|&nbsp; Date: {(c.get("uploaded_at") or c.get("date") or c.get("added") or "—")[:10]}'
                + (f' &nbsp;|&nbsp; <a href="/certs/{c["filename"]}" target="_blank">📄 VIEW PDF</a>'
                   if c.get("filename") else '')
                + f'</div>'
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
# PROJECT HANDLERS (Save, Load, Versions)
# ─────────────────────────────────────────────

class ProjectSaveHandler(BaseHandler):
    """POST /api/project/save — Save project with auto-versioning."""
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            if not job_code:
                self.write(json_encode({"ok": False, "error": "No job_code"}))
                return
            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            proj_dir = os.path.join(PROJECTS_DIR, safe_name)
            os.makedirs(proj_dir, exist_ok=True)

            # Find next version number
            existing = glob.glob(os.path.join(proj_dir, "v*.json"))
            max_v = 0
            for fp in existing:
                bn = os.path.basename(fp)
                try:
                    v = int(bn.replace("v", "").replace(".json", ""))
                    max_v = max(max_v, v)
                except ValueError:
                    pass
            next_v = max_v + 1

            body["saved_at"] = datetime.datetime.now().isoformat()
            body["version"] = next_v
            body["saved_by"] = self.get_current_user() or "unknown"

            # Save versioned file
            vpath = os.path.join(proj_dir, f"v{next_v}.json")
            with open(vpath, "w") as f:
                json.dump(body, f, indent=2)

            # Also save as current.json
            cpath = os.path.join(proj_dir, "current.json")
            with open(cpath, "w") as f:
                json.dump(body, f, indent=2)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "version": next_v,
                "file": f"{safe_name}/v{next_v}.json",
            }))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class ProjectLoadHandler(BaseHandler):
    """POST /api/project/load — Load saved project by job_code + optional version."""
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            version = body.get("version", None)
            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            proj_dir = os.path.join(PROJECTS_DIR, safe_name)

            # Support both new versioned and legacy flat format
            if os.path.isdir(proj_dir):
                if version:
                    fpath = os.path.join(proj_dir, f"v{version}.json")
                else:
                    fpath = os.path.join(proj_dir, "current.json")
            else:
                fpath = os.path.join(PROJECTS_DIR, f"{safe_name}.json")

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


class ProjectRevisionsHandler(BaseHandler):
    """POST /api/project/revisions — List all versions of a project."""
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            proj_dir = os.path.join(PROJECTS_DIR, safe_name)
            revisions = []
            if os.path.isdir(proj_dir):
                for fp in sorted(glob.glob(os.path.join(proj_dir, "v*.json"))):
                    bn = os.path.basename(fp)
                    try:
                        v = int(bn.replace("v", "").replace(".json", ""))
                        with open(fp) as f:
                            data = json.load(f)
                        revisions.append({
                            "version": v,
                            "saved_at": data.get("saved_at", ""),
                            "saved_by": data.get("saved_by", ""),
                            "total_sell": data.get("bom_data", {}).get("total_sell_price", 0),
                            "n_manual": len(data.get("manual_items", [])),
                            "n_overrides": sum(len(v) for v in (data.get("price_overrides") or {}).values())
                                           if isinstance(data.get("price_overrides"), dict) else 0,
                        })
                    except Exception:
                        pass
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "revisions": revisions}))
        except Exception as e:
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e)}))


class ProjectCompareHandler(BaseHandler):
    """POST /api/project/compare — Compare two project versions."""
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            va = int(body.get("version_a", 1))
            vb = int(body.get("version_b", 2))
            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            proj_dir = os.path.join(PROJECTS_DIR, safe_name)

            def load_version(v):
                fp = os.path.join(proj_dir, f"v{v}.json")
                if not os.path.isfile(fp):
                    return None
                with open(fp) as f:
                    return json.load(f)

            data_a = load_version(va)
            data_b = load_version(vb)
            if not data_a or not data_b:
                self.write(json_encode({"ok": False, "error": "One or both versions not found"}))
                return

            diffs = []

            # Compare BOM line items
            bldgs_a = (data_a.get("bom_data") or {}).get("buildings", [])
            bldgs_b = (data_b.get("bom_data") or {}).get("buildings", [])
            overrides_a = data_a.get("price_overrides") or {}
            overrides_b = data_b.get("price_overrides") or {}
            markup_a = ((data_a.get("project") or data_a.get("bom_data", {}).get("project", {})).get("markup_pct", 35)) / 100
            markup_b = ((data_b.get("project") or data_b.get("bom_data", {}).get("project", {})).get("markup_pct", 35)) / 100

            max_bldgs = max(len(bldgs_a), len(bldgs_b))
            for bi in range(max_bldgs):
                ba = bldgs_a[bi] if bi < len(bldgs_a) else None
                bb = bldgs_b[bi] if bi < len(bldgs_b) else None
                bname = (bb or ba or {}).get("building_name", f"Building {bi+1}")
                items_a = (ba or {}).get("line_items", [])
                items_b = (bb or {}).get("line_items", [])
                max_items = max(len(items_a), len(items_b))
                for li in range(max_items):
                    ia = items_a[li] if li < len(items_a) else {}
                    ib = items_b[li] if li < len(items_b) else {}
                    ov_a = (overrides_a.get(str(bi)) or {}).get(str(li))
                    ov_b = (overrides_b.get(str(bi)) or {}).get(str(li))
                    cost_a = (ov_a or {}).get("cost", ia.get("total_cost", 0)) if ov_a else ia.get("total_cost", 0)
                    cost_b = (ov_b or {}).get("cost", ib.get("total_cost", 0)) if ov_b else ib.get("total_cost", 0)
                    sell_a = (ov_a or {}).get("sell", cost_a * (1 + markup_a)) if ov_a else cost_a * (1 + markup_a)
                    sell_b = (ov_b or {}).get("sell", cost_b * (1 + markup_b)) if ov_b else cost_b * (1 + markup_b)
                    desc = ib.get("description") or ia.get("description") or "?"
                    if abs(cost_a - cost_b) > 0.01 or abs(sell_a - sell_b) > 0.01:
                        diffs.append({
                            "type": "line_item",
                            "building": bname,
                            "description": desc,
                            "cost_a": round(cost_a, 2), "cost_b": round(cost_b, 2),
                            "sell_a": round(sell_a, 2), "sell_b": round(sell_b, 2),
                        })

            # Compare manual items
            man_a = data_a.get("manual_items", [])
            man_b = data_b.get("manual_items", [])
            all_descs = set()
            for m in man_a + man_b:
                all_descs.add(m.get("description", "?"))
            for desc in sorted(all_descs):
                a_item = next((m for m in man_a if m.get("description") == desc), None)
                b_item = next((m for m in man_b if m.get("description") == desc), None)
                ext_a = (a_item["qty"] * a_item["sell_price"]) if a_item else 0
                ext_b = (b_item["qty"] * b_item["sell_price"]) if b_item else 0
                if abs(ext_a - ext_b) > 0.01 or (a_item is None) != (b_item is None):
                    diffs.append({
                        "type": "manual",
                        "description": desc,
                        "category": (b_item or a_item or {}).get("category", ""),
                        "ext_a": round(ext_a, 2), "ext_b": round(ext_b, 2),
                        "added": a_item is None,
                        "removed": b_item is None,
                    })

            total_a = (data_a.get("bom_data") or {}).get("total_sell_price", 0)
            total_b = (data_b.get("bom_data") or {}).get("total_sell_price", 0)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "version_a": va, "version_b": vb,
                "total_sell_a": round(total_a, 2),
                "total_sell_b": round(total_b, 2),
                "diffs": diffs,
            }))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class ProjectListHandler(BaseHandler):
    """GET /api/projects — List all saved projects."""
    def get(self):
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        result = []
        # New versioned format: subdirectories with current.json
        for d in sorted(os.listdir(PROJECTS_DIR), reverse=True):
            dpath = os.path.join(PROJECTS_DIR, d)
            if os.path.isdir(dpath):
                cpath = os.path.join(dpath, "current.json")
                if os.path.isfile(cpath):
                    try:
                        with open(cpath) as f:
                            data = json.load(f)
                        n_versions = len(glob.glob(os.path.join(dpath, "v*.json")))
                        result.append({
                            "job_code": data.get("job_code", d),
                            "project_name": data.get("project", {}).get("name", ""),
                            "customer": data.get("project", {}).get("customer_name", ""),
                            "saved_at": data.get("saved_at", ""),
                            "version": data.get("version", 1),
                            "n_versions": n_versions,
                            "file": d,
                        })
                    except Exception:
                        pass
            elif d.endswith(".json"):
                # Legacy flat format
                try:
                    with open(dpath) as f:
                        data = json.load(f)
                    result.append({
                        "job_code": data.get("job_code", d.replace(".json", "")),
                        "project_name": data.get("project", {}).get("name", ""),
                        "customer": data.get("project", {}).get("customer_name", ""),
                        "saved_at": data.get("saved_at", ""),
                        "version": 1,
                        "n_versions": 1,
                        "file": d,
                    })
                except Exception:
                    pass
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"projects": result}))


# ─────────────────────────────────────────────
# PROJECT DOCUMENT HANDLERS (NEW)
# ─────────────────────────────────────────────

class ProjectDocUploadHandler(BaseHandler):
    """POST /api/project/docs/upload — Upload file to project documents."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        try:
            job_code = self.get_body_argument("job_code", "").strip()
            category = self.get_body_argument("category", "other").lower()

            if not job_code:
                self.write(json_encode({"ok": False, "error": "No job_code"}))
                return

            if category not in PROJECT_DOC_CATEGORIES:
                self.write(json_encode({"ok": False, "error": f"Invalid category: {category}"}))
                return

            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            doc_dir = os.path.join(PROJECTS_DIR, safe_name, "docs", category)
            os.makedirs(doc_dir, exist_ok=True)

            filename = None
            if "file" in self.request.files:
                file_info = self.request.files["file"][0]
                if file_info["body"]:
                    orig_name = file_info["filename"]
                    safe_file = re.sub(r"[^a-zA-Z0-9_.-]", "_", orig_name)
                    filename = safe_file
                    filepath = os.path.join(doc_dir, filename)
                    with open(filepath, "wb") as f:
                        f.write(file_info["body"])

            if not filename:
                self.set_status(400)
                self.write(json_encode({"ok": False, "error": "No file uploaded"}))
                return

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "filename": filename,
                "category": category,
                "url": f"/project-files/{safe_name}/{category}/{filename}"
            }))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class ProjectDocListHandler(BaseHandler):
    """POST /api/project/docs — List files in project documents (with optional category filter)."""
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            category = body.get("category", None)  # None = all categories

            if not job_code:
                self.write(json_encode({"ok": False, "error": "No job_code"}))
                return

            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            docs_base = os.path.join(PROJECTS_DIR, safe_name, "docs")

            files = []
            if os.path.isdir(docs_base):
                categories_to_scan = [category] if category else PROJECT_DOC_CATEGORIES
                for cat in categories_to_scan:
                    cat_dir = os.path.join(docs_base, cat)
                    if os.path.isdir(cat_dir):
                        for fname in os.listdir(cat_dir):
                            fpath = os.path.join(cat_dir, fname)
                            if os.path.isfile(fpath):
                                stat = os.stat(fpath)
                                files.append({
                                    "filename": fname,
                                    "category": cat,
                                    "size": stat.st_size,
                                    "url": f"/project-files/{safe_name}/{cat}/{fname}",
                                    "uploaded_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                                })

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "files": files}))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class ProjectDocDeleteHandler(BaseHandler):
    """POST /api/project/docs/delete — Delete a project document."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            category = body.get("category", "").lower()
            filename = body.get("filename", "").strip()

            if not all([job_code, category, filename]):
                self.write(json_encode({"ok": False, "error": "Missing job_code, category, or filename"}))
                return

            if category not in PROJECT_DOC_CATEGORIES:
                self.write(json_encode({"ok": False, "error": "Invalid category"}))
                return

            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            filepath = os.path.join(PROJECTS_DIR, safe_name, "docs", category, filename)

            # Safety: prevent path traversal
            if not filepath.startswith(os.path.join(PROJECTS_DIR, safe_name)):
                self.set_status(403)
                self.write(json_encode({"ok": False, "error": "Path traversal attempt blocked"}))
                return

            if os.path.isfile(filepath):
                os.remove(filepath)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True}))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class ProjectDocServeHandler(BaseHandler):
    """GET /project-files/{job_code}/{category}/{filename} — Serve uploaded document."""
    def get(self, job_code, category, filename):
        try:
            safe_job = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            safe_cat = re.sub(r"[^a-zA-Z0-9_-]", "", category)
            safe_file = re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)

            filepath = os.path.join(PROJECTS_DIR, safe_job, "docs", safe_cat, safe_file)

            # Safety: prevent path traversal
            if not filepath.startswith(os.path.join(PROJECTS_DIR, safe_job)):
                self.set_status(403)
                self.write("Path traversal attempt blocked")
                return

            if not os.path.isfile(filepath):
                self.set_status(404)
                self.write("File not found")
                return

            # Determine MIME type from extension
            ext = os.path.splitext(filename)[1].lower()
            mime_types = {
                ".pdf": "application/pdf",
                ".doc": "application/msword",
                ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ".xls": "application/vnd.ms-excel",
                ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".txt": "text/plain",
                ".dwg": "application/vnd.autodesk.autocad.drawing",
                ".dxf": "application/dxf",
            }
            mime = mime_types.get(ext, "application/octet-stream")

            self.set_header("Content-Type", mime)
            self.set_header("Content-Disposition", f'attachment; filename="{filename}"')
            with open(filepath, "rb") as f:
                self.write(f.read())
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(f"Error serving file: {e}\n{traceback.format_exc()}")


# ─────────────────────────────────────────────
# PROJECT STATUS HANDLER (NEW)
# ─────────────────────────────────────────────

class ProjectStatusHandler(BaseHandler):
    """POST /api/project/status — Update project stage."""
    required_roles = ["admin", "estimator", "shop", "tc_limited"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            stage = body.get("stage", "").lower()

            if not job_code:
                self.write(json_encode({"ok": False, "error": "No job_code"}))
                return

            if stage not in PROJECT_STAGES:
                self.write(json_encode({"ok": False, "error": f"Invalid stage: {stage}"}))
                return

            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            status_file = os.path.join(PROJECTS_DIR, safe_name, "status.json")
            os.makedirs(os.path.dirname(status_file), exist_ok=True)

            status_data = {
                "job_code": job_code,
                "stage": stage,
                "updated_at": datetime.datetime.now().isoformat(),
                "updated_by": self.get_current_user() or "unknown"
            }

            with open(status_file, "w") as f:
                json.dump(status_data, f, indent=2)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "stage": stage}))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


# ─────────────────────────────────────────────
# TC EXPORT HANDLERS
# ─────────────────────────────────────────────

class TCExportPDFHandler(BaseHandler):
    """POST /tc/export/pdf — Export TC Quote as PDF."""
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
    """POST /tc/export/excel — Export TC Quote as Excel."""
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
# ROUTE TABLE (returned by get_routes())
# ─────────────────────────────────────────────

def get_routes():
    """Return list of (pattern, handler) tuples for tornado.web.Application."""
    static_path = os.path.join(BASE_DIR, "static")
    return [
        # ── Auth routes ────────────────────────────────────────
        (r"/auth/login",         LoginHandler),
        (r"/auth/logout",        LogoutHandler),
        (r"/admin",              AdminPageHandler),
        (r"/auth/users",         UsersListHandler),
        (r"/auth/users/add",     UserAddHandler),
        (r"/auth/users/delete",  UserDeleteHandler),

        # ── App routes (Dashboard + Calculators) ────────────────
        (r"/",                      DashboardHandler),
        (r"/sa",                    SACalcHandler),
        (r"/tc",                    TCQuoteHandler),

        # ── API - Calculation & Export ─────────────────────────
        (r"/api/calculate",         CalculateHandler),
        (r"/api/excel",             ExcelHandler),
        (r"/api/pdf",               PDFHandler),

        # ── API - Labels ───────────────────────────────────────
        (r"/api/labels",            LabelsHandler),
        (r"/api/labels/pdf",        LabelsPDFHandler),
        (r"/api/labels/csv",        LabelsCsvHandler),

        # ── API - Inventory ────────────────────────────────────
        (r"/api/inventory",              InventoryHandler),
        (r"/api/inventory/update",       InventoryUpdateHandler),
        (r"/api/inventory/save",         InventorySaveHandler),
        (r"/api/inventory/cert",         InventoryCertHandler),
        (r"/api/inventory/cert/upload",  InventoryCertUploadHandler),
        (r"/certs/([^/]+)",              CertFileHandler),
        (r"/api/inventory/delete",       CoilDeleteHandler),
        (r"/api/inventory/sticker",      CoilStickerHandler),
        (r"/coil/([^/]+)",               CoilDetailHandler),

        # ── API - Projects (versioned system) ───────────────────
        (r"/api/project/save",           ProjectSaveHandler),
        (r"/api/project/load",           ProjectLoadHandler),
        (r"/api/project/revisions",      ProjectRevisionsHandler),
        (r"/api/project/compare",        ProjectCompareHandler),
        (r"/api/projects",               ProjectListHandler),

        # ── API - Project Documents (NEW) ──────────────────────
        (r"/api/project/docs/upload",    ProjectDocUploadHandler),
        (r"/api/project/docs",           ProjectDocListHandler),
        (r"/api/project/docs/delete",    ProjectDocDeleteHandler),
        (r"/project-files/([^/]+)/([^/]+)/([^/]+)", ProjectDocServeHandler),

        # ── API - Project Status (NEW) ────────────────────────
        (r"/api/project/status",         ProjectStatusHandler),

        # ── TC Export ──────────────────────────────────────────
        (r"/tc/export/pdf",              TCExportPDFHandler),
        (r"/tc/export/excel",            TCExportExcelHandler),

        # ── Static files ───────────────────────────────────────
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static_path}),
    ]


# ─────────────────────────────────────────────
# HTML TEMPLATES (imported from templates package)
# ─────────────────────────────────────────────

from templates.login import LOGIN_HTML
from templates.admin import ADMIN_HTML
from templates.dashboard import DASHBOARD_HTML
from templates.sa_calc import SA_CALC_HTML
from templates.tc_quote import TC_QUOTE_HTML, COIL_DETAIL_HTML

# Aliases used by handlers
MAIN_HTML = SA_CALC_HTML
TC_HTML = TC_QUOTE_HTML
