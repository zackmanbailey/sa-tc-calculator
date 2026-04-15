"""
TitanForge v3.0 Backend Handlers
Complete rewrite of handler classes for the steel fabrication shop management system.
Includes: Auth (4-tier roles), Calculation, Inventory, Projects, Documents, Status tracking.
"""

import os, sys, json, io, datetime, hashlib, uuid, secrets, re, glob, time, shutil
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
# Use TITANFORGE_DATA_DIR env var for persistent storage on Railway.
# Falls back to ./data for local development.
# On Railway: set TITANFORGE_DATA_DIR to a mounted volume path (e.g. /data)
DATA_DIR = os.environ.get("TITANFORGE_DATA_DIR", os.path.join(BASE_DIR, "data"))

# Ensure data directories exist on first run (critical for persistent volumes)
for _subdir in ["projects", "certs", "quotes", "qc", "shop_drawings", "customer_docs"]:
    os.makedirs(os.path.join(DATA_DIR, _subdir), exist_ok=True)

# Seed default files if they don't exist (first deploy with new volume)
_DEFAULT_DATA_DIR = os.path.join(BASE_DIR, "data")
for _seed_file in ["inventory.json", "users.json", "customers.json", "traceability_index.json"]:
    _target = os.path.join(DATA_DIR, _seed_file)
    _source = os.path.join(_DEFAULT_DATA_DIR, _seed_file)
    if not os.path.isfile(_target) and os.path.isfile(_source):
        import shutil
        shutil.copy2(_source, _target)
        print(f"  [INIT] Seeded {_seed_file} from defaults")

INVENTORY_PATH = os.path.join(DATA_DIR, "inventory.json")
USERS_PATH = os.path.join(DATA_DIR, "users.json")
CERTS_DIR = os.path.join(DATA_DIR, "certs")
PROJECTS_DIR = os.path.join(DATA_DIR, "projects")
CUSTOMERS_PATH = os.path.join(DATA_DIR, "customers.json")
QUOTES_DIR = os.path.join(DATA_DIR, "quotes")
QC_DIR = os.path.join(DATA_DIR, "qc")
SHOP_DRAWINGS_DIR = os.path.join(DATA_DIR, "shop_drawings")
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

# ─────────────────────────────────────────────
# CUSTOMER DATABASE FILE MANAGEMENT
# ─────────────────────────────────────────────

def load_customers():
    """Load customers from JSON."""
    if not os.path.isfile(CUSTOMERS_PATH):
        os.makedirs(os.path.dirname(CUSTOMERS_PATH), exist_ok=True)
        with open(CUSTOMERS_PATH, "w") as f:
            json.dump([], f)
        return []
    with open(CUSTOMERS_PATH, "r") as f:
        return json.load(f)

def save_customers(data):
    """Save customers to JSON."""
    os.makedirs(os.path.dirname(CUSTOMERS_PATH), exist_ok=True)
    with open(CUSTOMERS_PATH, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────────────────────
# QUOTE DATA FILE MANAGEMENT
# ─────────────────────────────────────────────

def load_quote_data(job_code):
    """Load quote data for a project."""
    safe = re.sub(r'[^A-Za-z0-9_-]', '_', job_code)
    qpath = os.path.join(QUOTES_DIR, f"{safe}.json")
    if os.path.isfile(qpath):
        with open(qpath) as f:
            return json.load(f)
    return None

def save_quote_data(job_code, data):
    """Save quote data for a project."""
    os.makedirs(QUOTES_DIR, exist_ok=True)
    safe = re.sub(r'[^A-Za-z0-9_-]', '_', job_code)
    qpath = os.path.join(QUOTES_DIR, f"{safe}.json")
    data["updated_at"] = datetime.datetime.now().isoformat()
    with open(qpath, "w") as f:
        json.dump(data, f, indent=2)

DEFAULT_QUOTE_TEMPLATE = {
    "project_overview": {
        "company_name": "Titan Carports LLC",
        "company_address": "",
        "company_phone": "",
        "company_email": "",
        "estimator_name": "",
        "estimator_phone": "",
        "estimator_email": "",
        "customer_name": "",
        "customer_company": "",
        "job_address": "",
        "job_city": "",
        "job_state": "",
        "job_zip": "",
        "project_description": "",
        "quote_date": "",
        "quote_number": "",
        "valid_days": 30,
    },
    "pricing": {
        "base_items": [
            {"description": "Steel Canopies", "amount": 0},
            {"description": "Engineering", "amount": 0},
        ],
        "options": [],
        "base_total": 0,
    },
    "inclusions": [
        "Fabrication of steel components per approved engineering drawings",
        "Delivery to job site",
        "Standard primer finish on all steel",
        "Stamped engineering drawings by licensed PE",
    ],
    "exclusions_categorized": {
        "Site Work": [
            "Grading, compaction, or earthwork",
            "Excavation or backfill",
            "Erosion control or SWPPP",
            "Demolition of existing structures",
        ],
        "Electrical": [
            "Electrical work of any kind",
            "Wiring, conduit, or panel upgrades",
            "Lighting or lighting design",
        ],
        "Permits & Inspections": [
            "Building permits and associated fees",
            "Inspections beyond standard structural",
            "Special inspections (welding, concrete, soils)",
        ],
        "Structural": [
            "Foundation design (by others)",
            "Concrete work of any kind",
            "Masonry or CMU work",
            "Wood framing or carpentry",
        ],
        "MEP": [
            "Plumbing of any kind",
            "HVAC systems or ductwork",
            "Fire protection or sprinkler systems",
        ],
        "General": [
            "Landscaping or irrigation",
            "Fencing or gates",
            "Signage",
            "Painting beyond standard primer",
            "Sales tax (unless specified)",
            "Prevailing wage labor",
            "Any work not specifically included in this proposal",
        ],
    },
    "general_project_overview": {
        "description": "",
        "specs": {},
        "photos": [],
    },
    "payment_terms": {
        "method": "monthly_milestone",
        "engineering_fee_note": "Engineering fees are due upon contract execution and are non-refundable.",
        "billing_description": "Progress billings will be submitted monthly based on the percentage of work completed during the billing period. Each invoice will reflect the actual milestones achieved and corresponding percentage of the total contract value.",
        "milestones": [
            {"label": "Mobilization & Material Procurement", "percent": 25},
            {"label": "Steel Fabrication Complete", "percent": 25},
            {"label": "Steel Erection Complete", "percent": 20},
            {"label": "Panel Installation Complete", "percent": 15},
            {"label": "Punch List & Final Completion", "percent": 10},
            {"label": "Final Acceptance & Close-out", "percent": 5},
        ],
        "net_days": 30,
        "late_fee_percent": 1.5,
        "retainage_percent": 0,
    },
    "signature_block": {
        "company_signer_name": "",
        "company_signer_title": "",
        "customer_signer_name": "",
        "customer_signer_title": "",
    },
    "standard_qualifications": [
        "All work to be performed during normal business hours (Mon-Fri 7AM-5PM).",
        "Pricing is based on current material costs and is subject to change if not accepted within the validity period.",
        "Customer to provide clear and level access to the job site for delivery vehicles and equipment.",
        "Any changes to the scope of work after contract execution may result in additional charges.",
        "Titan Carports LLC is not responsible for delays caused by weather, material shortages, or other conditions beyond our control.",
        "Engineering is based on site-specific wind and snow loads per local building code requirements.",
        "All structural steel to meet ASTM A500 Grade B/C or ASTM A572 Grade 50 specifications.",
    ],
    "conditions_of_contract": [
        "This proposal is valid for {{valid_days}} days from the date of issue.",
        "A signed copy of this proposal along with the required deposit constitutes a binding contract.",
        "All engineering drawings must be approved by the customer before fabrication begins.",
        "Changes to approved engineering drawings may result in additional charges and schedule delays.",
        "Customer is responsible for ensuring all site conditions are suitable for installation.",
        "Titan Carports LLC shall not be liable for damage to underground utilities not properly marked.",
        "Payment terms are net due upon receipt of invoice unless otherwise specified.",
        "Late payments are subject to a 1.5% monthly finance charge.",
        "Customer is responsible for obtaining all necessary permits and approvals.",
        "Titan Carports LLC warrants all workmanship for a period of one (1) year from date of completion.",
    ],
    "terms_of_contract": [
        "All materials remain property of Titan Carports LLC until paid in full.",
        "Customer agrees to provide adequate storage area for materials upon delivery.",
        "Work stoppage due to customer delay may result in additional mobilization charges.",
        "Titan Carports LLC reserves the right to subcontract portions of the work.",
        "Neither party shall be liable for delays due to force majeure events.",
        "Any disputes shall be resolved through binding arbitration in the state of New Mexico.",
        "This agreement constitutes the entire understanding between the parties.",
        "Modifications must be in writing and signed by both parties.",
        "Concrete costs are based on standard mix design. Specialty mixes are additional.",
        "Drilling costs are based on standard soil conditions. Rock or unusual conditions may incur additional charges.",
    ],
}


# ─────────────────────────────────────────────
# AISC QC MODULE — DATA MODELS & UTILITIES
# ─────────────────────────────────────────────

# AISC 360 Chapter N / AISC 341 (Seismic) inspection types
AISC_INSPECTION_TYPES = {
    "bolt_inspection": {
        "label": "Bolt Installation Inspection",
        "standard": "AISC 360 Section J3 / RCSC Specification",
        "checklist": [
            {"key": "bolt_grade", "label": "Bolt grade verified (A325/A490/F1852/F2280)", "type": "check"},
            {"key": "surface_condition", "label": "Faying surface condition meets Class A/B requirements", "type": "check"},
            {"key": "snug_tight", "label": "Snug-tight condition achieved per RCSC Table 8.1", "type": "check"},
            {"key": "pretension_method", "label": "Pretensioning method verified (Turn-of-Nut/TC/DTI/Calibrated Wrench)", "type": "select",
             "options": ["Turn-of-Nut", "Twist-off TC", "Direct Tension Indicator", "Calibrated Wrench", "N/A - Snug Tight Only"]},
            {"key": "lot_number", "label": "Bolt lot number recorded", "type": "text"},
            {"key": "dtc_verification", "label": "Daily TC bolt verification test performed", "type": "check"},
            {"key": "hole_type", "label": "Hole type verified (STD/OVS/SSL/LSL)", "type": "select",
             "options": ["Standard (STD)", "Oversized (OVS)", "Short Slot (SSL)", "Long Slot (LSL)"]},
            {"key": "washers", "label": "Washers installed per RCSC requirements", "type": "check"},
            {"key": "rotation_check", "label": "Nut rotation verified within tolerance", "type": "check"},
        ],
    },
    "weld_visual": {
        "label": "Weld Visual Inspection (VT)",
        "standard": "AWS D1.1 Table 6.1 / AISC 360 Chapter J2",
        "checklist": [
            {"key": "wps_available", "label": "WPS (Welding Procedure Specification) available and followed", "type": "check"},
            {"key": "welder_qualified", "label": "Welder qualification current and applicable", "type": "check"},
            {"key": "filler_metal", "label": "Filler metal matches WPS requirements (E70XX, etc.)", "type": "text"},
            {"key": "preheat", "label": "Preheat temperature met per WPS", "type": "check"},
            {"key": "interpass_temp", "label": "Interpass temperature within limits", "type": "check"},
            {"key": "weld_size", "label": "Weld size meets drawing requirements", "type": "check"},
            {"key": "weld_length", "label": "Weld length meets drawing requirements", "type": "check"},
            {"key": "profile_acceptable", "label": "Weld profile acceptable per AWS D1.1 Figure 5.4", "type": "check"},
            {"key": "undercut", "label": "Undercut within acceptable limits (1/32\" max)", "type": "check"},
            {"key": "porosity", "label": "No visible porosity beyond limits", "type": "check"},
            {"key": "cracks", "label": "No cracks detected", "type": "check"},
            {"key": "overlap", "label": "No overlap or cold lap", "type": "check"},
            {"key": "arc_strikes", "label": "No arc strikes on base metal", "type": "check"},
            {"key": "spatter", "label": "Spatter cleaned / acceptable", "type": "check"},
        ],
    },
    "dimensional": {
        "label": "Dimensional / Fit-Up Inspection",
        "standard": "AISC Code of Standard Practice (COSP) / AISC 303",
        "checklist": [
            {"key": "member_length", "label": "Member length within tolerance (AISC 303 Sec 6.4.1)", "type": "check"},
            {"key": "sweep_camber", "label": "Sweep and camber within tolerance", "type": "check"},
            {"key": "cross_section", "label": "Cross-section dimensions verified", "type": "check"},
            {"key": "hole_location", "label": "Hole locations within 1/16\" tolerance", "type": "check"},
            {"key": "hole_diameter", "label": "Hole diameters per specification", "type": "check"},
            {"key": "fit_up_gap", "label": "Fit-up gap within WPS limits (root opening)", "type": "check"},
            {"key": "alignment", "label": "Member alignment and squareness verified", "type": "check"},
            {"key": "bearing", "label": "Bearing surfaces in full contact", "type": "check"},
        ],
    },
    "surface_prep": {
        "label": "Surface Preparation & Coating Inspection",
        "standard": "SSPC / AISC 360 Chapter M3",
        "checklist": [
            {"key": "blast_profile", "label": "Surface profile meets SSPC-SP requirements", "type": "check"},
            {"key": "cleanliness", "label": "Surface cleanliness verified (SSPC-SP6/SP10)", "type": "select",
             "options": ["SSPC-SP6 (Commercial)", "SSPC-SP10 (Near-White)", "SSPC-SP5 (White Metal)", "N/A"]},
            {"key": "dft_primer", "label": "Primer DFT (dry film thickness) within spec", "type": "text"},
            {"key": "dft_topcoat", "label": "Topcoat DFT within spec (if applicable)", "type": "text"},
            {"key": "coverage", "label": "Full coverage with no holidays", "type": "check"},
            {"key": "galvanizing", "label": "Hot-dip galvanizing meets ASTM A123 (if applicable)", "type": "check"},
            {"key": "cure_time", "label": "Adequate cure/recoat time observed", "type": "check"},
        ],
    },
    "nde": {
        "label": "Non-Destructive Examination (NDE)",
        "standard": "AWS D1.1 Chapter 6 / AISC 341 (Seismic)",
        "checklist": [
            {"key": "nde_method", "label": "NDE method", "type": "select",
             "options": ["Ultrasonic (UT)", "Magnetic Particle (MT)", "Radiographic (RT)", "Penetrant (PT)", "Phased Array (PAUT)"]},
            {"key": "technician_certified", "label": "NDE technician certified (ASNT Level II minimum)", "type": "check"},
            {"key": "procedure_followed", "label": "Written NDE procedure followed", "type": "check"},
            {"key": "acceptance_criteria", "label": "Acceptance criteria identified (AWS D1.1 Table 6.2)", "type": "check"},
            {"key": "joint_location", "label": "Joint/weld location documented", "type": "text"},
            {"key": "indication_found", "label": "Rejectable indications found", "type": "select",
             "options": ["None — Acceptable", "Minor — Within limits", "Rejectable — See NCR"]},
            {"key": "report_number", "label": "NDE report number", "type": "text"},
        ],
    },
    "material_receiving": {
        "label": "Material Receiving Inspection",
        "standard": "AISC 360 Chapter A3 / ASTM Standards",
        "checklist": [
            {"key": "mtrs_received", "label": "Mill Test Reports (MTRs) received and reviewed", "type": "check"},
            {"key": "heat_number", "label": "Heat number matches MTR", "type": "check"},
            {"key": "grade_verified", "label": "Material grade verified (A36/A572/A500/A992)", "type": "text"},
            {"key": "dimensions_checked", "label": "Material dimensions verified against PO", "type": "check"},
            {"key": "surface_condition", "label": "Surface condition acceptable (no excessive rust/pitting/damage)", "type": "check"},
            {"key": "quantity_verified", "label": "Quantity matches packing list and PO", "type": "check"},
            {"key": "marking_legible", "label": "Mill marking legible and matches MTR", "type": "check"},
            {"key": "stored_properly", "label": "Material stored properly (off ground, protected)", "type": "check"},
        ],
    },
}

# NCR severity levels
NCR_SEVERITY = ["minor", "major", "critical"]
NCR_STATUS = ["open", "under_review", "corrective_action", "re_inspect", "closed", "voided"]


def load_project_qc(job_code):
    """Load all QC data for a project."""
    safe = re.sub(r'[^A-Za-z0-9_-]', '_', job_code)
    qc_path = os.path.join(QC_DIR, f"{safe}.json")
    if os.path.isfile(qc_path):
        with open(qc_path) as f:
            return json.load(f)
    return {"inspections": [], "ncrs": [], "traceability": []}

def save_project_qc(job_code, data):
    """Save QC data for a project."""
    os.makedirs(QC_DIR, exist_ok=True)
    safe = re.sub(r'[^A-Za-z0-9_-]', '_', job_code)
    qc_path = os.path.join(QC_DIR, f"{safe}.json")
    data["updated_at"] = datetime.datetime.now().isoformat()
    with open(qc_path, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────────────────────
# MATERIAL TRACEABILITY — HEAT NUMBER TRACKING
# ─────────────────────────────────────────────

def load_traceability_index():
    """Load the global traceability index (heat number → coils → projects → members)."""
    tpath = os.path.join(DATA_DIR, "traceability_index.json")
    if os.path.isfile(tpath):
        with open(tpath) as f:
            return json.load(f)
    return {"heat_numbers": {}}

def save_traceability_index(data):
    """Save the global traceability index."""
    tpath = os.path.join(DATA_DIR, "traceability_index.json")
    with open(tpath, "w") as f:
        json.dump(data, f, indent=2)

def register_heat_number(heat_number, coil_tag, material_spec, mill_name="", mtr_path=""):
    """Register a heat number in the traceability index when a coil is received."""
    idx = load_traceability_index()
    if heat_number not in idx["heat_numbers"]:
        idx["heat_numbers"][heat_number] = {
            "material_spec": material_spec,
            "mill_name": mill_name,
            "mtr_path": mtr_path,
            "coils": [],
            "members": [],
            "registered_at": datetime.datetime.now().isoformat(),
        }
    # Add coil if not already tracked
    coil_tags = [c["coil_tag"] for c in idx["heat_numbers"][heat_number]["coils"]]
    if coil_tag not in coil_tags:
        idx["heat_numbers"][heat_number]["coils"].append({
            "coil_tag": coil_tag,
            "added_at": datetime.datetime.now().isoformat(),
        })
    save_traceability_index(idx)
    return idx["heat_numbers"][heat_number]

def assign_member_to_heat(heat_number, job_code, member_mark, description=""):
    """Track that a specific member was fabricated from a specific heat number."""
    idx = load_traceability_index()
    if heat_number not in idx["heat_numbers"]:
        idx["heat_numbers"][heat_number] = {
            "material_spec": "",
            "mill_name": "",
            "coils": [],
            "members": [],
            "registered_at": datetime.datetime.now().isoformat(),
        }
    idx["heat_numbers"][heat_number]["members"].append({
        "job_code": job_code,
        "member_mark": member_mark,
        "description": description,
        "assigned_at": datetime.datetime.now().isoformat(),
    })
    save_traceability_index(idx)

    # Also save to project QC data
    qc = load_project_qc(job_code)
    qc["traceability"].append({
        "heat_number": heat_number,
        "member_mark": member_mark,
        "description": description,
        "assigned_at": datetime.datetime.now().isoformat(),
    })
    save_project_qc(job_code, qc)


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

    def render_with_nav(self, html: str, active_page: str = "",
                        job_code: str = ""):
        """Render HTML with the unified sidebar navigation injected.

        Args:
            html: Raw HTML string from template
            active_page: Which sidebar item to highlight
            job_code: If set, shows project sub-nav in sidebar
        """
        from templates.shared_nav import inject_nav

        user = self.get_current_user() or "local"
        role = self.get_user_role() or "admin"
        users = load_users()
        display = users.get(user, {}).get("display_name", user) if user != "local" else "Admin"

        result = inject_nav(html, active_page=active_page, job_code=job_code,
                            user_name=display, user_role=role)
        self.set_header("Content-Type", "text/html")
        self.write(result)


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
        self.render_with_nav(ADMIN_HTML, active_page="admin")


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


class UserEditHandler(BaseHandler):
    """POST /auth/users/edit — Edit a user's display_name, role, or password (admin only)."""
    required_roles = ["admin"]

    def post(self):
        body = json_decode(self.request.body)
        username = body.get("username", "").strip().lower()
        if not username:
            self.write(json_encode({"ok": False, "error": "Username required"}))
            return

        users = load_users()
        if username not in users:
            self.write(json_encode({"ok": False, "error": "User not found"}))
            return

        if "display_name" in body and body["display_name"].strip():
            users[username]["display_name"] = body["display_name"].strip()
        if "role" in body and body["role"] in ROLE_PERMISSIONS:
            users[username]["role"] = body["role"]
        if "password" in body and body["password"]:
            users[username]["password"] = hash_password(body["password"])

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
        user = self.get_current_user() or "local"
        users_db = load_users()
        role = users_db.get(user, {}).get("role", "viewer") if user != "local" else "admin"
        display = users_db.get(user, {}).get("display_name", user) if user != "local" else "Admin"
        html = DASHBOARD_HTML.replace("{{USER_ROLE}}", role).replace("{{USER_NAME}}", display)
        self.render_with_nav(html, active_page="dashboard")


class GettingStartedHandler(BaseHandler):
    """GET /getting-started — Role-based onboarding guide."""
    def get(self):
        from templates.getting_started import GETTING_STARTED_HTML
        user = self.get_current_user() or "local"
        users_db = load_users()
        role = users_db.get(user, {}).get("role", "shop") if user != "local" else "admin"
        html = GETTING_STARTED_HTML.replace("{{USER_ROLE}}", role)
        self.set_header("Content-Type", "text/html")
        self.write(html)


class HelpBundleHandler(BaseHandler):
    """GET /api/help-bundle — Returns tooltip CSS+JS+glossary for injection into any page."""
    def get(self):
        from templates.help_tooltips import get_tooltip_bundle
        from templates.error_handling import get_error_bundle
        bundle = get_tooltip_bundle() + "\n" + get_error_bundle()
        self.set_header("Content-Type", "text/html")
        self.write(bundle)


class SACalcHandler(BaseHandler):
    """GET /sa — Structures America Estimator."""
    def get(self):
        self.render_with_nav(MAIN_HTML, active_page="sa")


class TCQuoteHandler(BaseHandler):
    """GET /tc — Titan Carports Estimator."""
    def get(self):
        self.render_with_nav(TC_HTML, active_page="tc")


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
# INVENTORY V2 API HANDLERS (for new inventory page)
# ─────────────────────────────────────────────

class InventoryConfigHandler(BaseHandler):
    """GET /api/inventory/inv-config — Return config for inventory dropdowns."""
    def get(self):
        self.write(json_encode({
            "coil_gauges": ["10GA", "12GA", "14GA", "16GA", "18GA", "20GA", "22GA", "24GA", "26GA"],
            "material_grades": ["A500 Gr B", "A500 Gr C", "A572 Gr 50", "A36", "Galvalume", "Galvanized"],
            "inventory_statuses": ["active", "low_stock", "depleted", "on_hold"],
            "suppliers": ["Skyline Steel", "Steel Technologies", "Nucor", "Olympic Steel", "BlueScope"],
        }))


class InventorySummaryHandler(BaseHandler):
    """GET /api/inventory/summary — Return summary stats for dashboard."""
    def get(self):
        inv = load_inventory()
        coils = inv.get("coils", {})
        total_coils = len(coils)
        total_stock = 0
        total_committed = 0
        low_stock_count = 0
        depleted_count = 0
        active_count = 0
        total_value = 0
        stock_by_gauge = {}

        for cid, c in coils.items():
            stock = float(c.get("stock_lbs", 0) or 0)
            committed = float(c.get("committed_lbs", 0) or 0)
            avail = stock - committed
            price = float(c.get("price_per_lb", 0) or 0)
            min_stock = float(c.get("min_stock_lbs", c.get("min_order_lbs", 2000)) or 2000)
            gauge = c.get("gauge", "Unknown")

            total_stock += stock
            total_committed += committed
            total_value += stock * price
            stock_by_gauge[gauge] = stock_by_gauge.get(gauge, 0) + stock

            if avail <= 0:
                depleted_count += 1
            elif avail < min_stock:
                low_stock_count += 1
            else:
                active_count += 1

        self.write(json_encode({
            "ok": True,
            "summary": {
                "total_coils": total_coils,
                "total_stock_lbs": round(total_stock, 2),
                "total_committed_lbs": round(total_committed, 2),
                "total_available_lbs": round(total_stock - total_committed, 2),
                "low_stock_count": low_stock_count,
                "total_value": round(total_value, 2),
                "stock_by_gauge": stock_by_gauge,
                "stock_by_status": {
                    "active_count": active_count,
                    "low_stock_count": low_stock_count,
                    "depleted_count": depleted_count,
                },
            }
        }))


class InventoryCoilsHandler(BaseHandler):
    """GET /api/inventory/coils — Return list of coils with filtering."""
    def get(self):
        inv = load_inventory()
        coils_dict = inv.get("coils", {})
        gauge_filter = self.get_query_argument("gauge", "")
        grade_filter = self.get_query_argument("grade", "")
        status_filter = self.get_query_argument("status", "")

        result = []
        for cid, c in coils_dict.items():
            stock = float(c.get("stock_lbs", 0) or 0)
            committed = float(c.get("committed_lbs", 0) or 0)
            avail = stock - committed
            min_stock = float(c.get("min_stock_lbs", c.get("min_order_lbs", 2000)) or 2000)

            if avail <= 0:
                status = "depleted"
            elif avail < min_stock:
                status = "low_stock"
            else:
                status = "active"

            if gauge_filter and c.get("gauge", "") != gauge_filter:
                continue
            if grade_filter and c.get("grade", "") != grade_filter:
                continue
            if status_filter and status != status_filter:
                continue

            result.append({
                "coil_id": cid,
                "name": c.get("name", cid),
                "gauge": c.get("gauge", ""),
                "grade": c.get("grade", ""),
                "supplier": c.get("supplier", ""),
                "stock_lbs": round(stock, 2),
                "committed_lbs": round(committed, 2),
                "available_lbs": round(avail, 2),
                "status": status,
                "price_per_lb": c.get("price_per_lb", 0),
                "min_stock_lbs": min_stock,
            })

        self.write(json_encode({"ok": True, "coils": result}))


class InventoryCoilCreateHandler(BaseHandler):
    """POST /api/inventory/coil/create — Create a new coil."""
    def post(self):
        body = json_decode(self.request.body)
        coil_id = body.get("coil_id", "").strip()
        if not coil_id:
            self.write(json_encode({"ok": False, "error": "coil_id is required"}))
            return
        inv = load_inventory()
        coils = inv.setdefault("coils", {})
        if coil_id in coils:
            self.write(json_encode({"ok": False, "error": "Coil ID already exists"}))
            return
        coils[coil_id] = {
            "name": body.get("name", coil_id),
            "gauge": body.get("gauge", ""),
            "grade": body.get("grade", ""),
            "supplier": body.get("supplier", ""),
            "stock_lbs": float(body.get("stock_lbs", 0) or 0),
            "committed_lbs": 0,
            "min_stock_lbs": float(body.get("min_order_lbs", 2000) or 2000),
            "min_order_lbs": float(body.get("min_order_lbs", 2000) or 2000),
            "lead_time_weeks": int(body.get("lead_time_weeks", 8) or 8),
            "price_per_lb": float(body.get("price_per_lb", 0) or 0),
            "lbs_per_lft": float(body.get("lbs_per_lft", 0) or 0),
            "coil_max_lbs": float(body.get("weight_lbs", 8000) or 8000),
            "width_in": float(body.get("width_in", 0) or 0),
            "heat_num": body.get("heat_num", ""),
            "orders": [],
        }
        save_inventory(inv)
        self.write(json_encode({"ok": True, "coil_id": coil_id}))


class InventoryTransactionsHandler(BaseHandler):
    """GET /api/inventory/transactions — Return transaction history."""
    def get(self):
        coil_filter = self.get_query_argument("coil_id", "")
        type_filter = self.get_query_argument("type", "")
        tx_path = os.path.join(DATA_DIR, "inventory_transactions.json")
        txns = []
        if os.path.isfile(tx_path):
            with open(tx_path) as f:
                txns = json.load(f)
        if coil_filter:
            txns = [t for t in txns if t.get("coil_id") == coil_filter]
        if type_filter:
            txns = [t for t in txns if t.get("type") == type_filter]
        self.write(json_encode({"ok": True, "transactions": txns[-100:]}))


class InventoryAllocationsHandler(BaseHandler):
    """GET /api/inventory/allocations — Return active allocations."""
    def get(self):
        alloc_path = os.path.join(DATA_DIR, "inventory_allocations.json")
        allocs = []
        if os.path.isfile(alloc_path):
            with open(alloc_path) as f:
                allocs = json.load(f)
        self.write(json_encode({"ok": True, "allocations": allocs}))


class InventoryAllocateHandler(BaseHandler):
    """POST /api/inventory/allocate — Allocate stock to a job."""
    def post(self):
        body = json_decode(self.request.body)
        coil_id = body.get("coil_id", "")
        job_code = body.get("job_code", "")
        qty = float(body.get("quantity_lbs", 0) or 0)
        if not coil_id or not job_code or qty <= 0:
            self.write(json_encode({"ok": False, "error": "coil_id, job_code, and quantity_lbs required"}))
            return

        inv = load_inventory()
        coils = inv.get("coils", {})
        if coil_id not in coils:
            self.write(json_encode({"ok": False, "error": "Coil not found"}))
            return

        coil = coils[coil_id]
        stock = float(coil.get("stock_lbs", 0))
        committed = float(coil.get("committed_lbs", 0))
        if stock - committed < qty:
            self.write(json_encode({"ok": False, "error": "Insufficient available stock"}))
            return

        coil["committed_lbs"] = committed + qty
        save_inventory(inv)

        alloc_path = os.path.join(DATA_DIR, "inventory_allocations.json")
        allocs = []
        if os.path.isfile(alloc_path):
            with open(alloc_path) as f:
                allocs = json.load(f)
        import datetime
        alloc_id = f"ALLOC-{len(allocs)+1:04d}"
        allocs.append({
            "allocation_id": alloc_id,
            "coil_id": coil_id,
            "job_code": job_code,
            "quantity_lbs": qty,
            "consumed_lbs": 0,
            "status": "active",
            "work_order_ref": body.get("work_order_ref", ""),
            "notes": body.get("notes", ""),
            "date": datetime.datetime.now().isoformat(),
        })
        with open(alloc_path, "w") as f:
            json.dump(allocs, f, indent=2)

        self._log_transaction(coil_id, "allocate", qty, job_code, f"Allocation {alloc_id}")
        self.write(json_encode({"ok": True, "allocation_id": alloc_id}))

    def _log_transaction(self, coil_id, tx_type, qty, job_code, ref):
        import datetime
        tx_path = os.path.join(DATA_DIR, "inventory_transactions.json")
        txns = []
        if os.path.isfile(tx_path):
            with open(tx_path) as f:
                txns = json.load(f)
        txns.append({
            "transaction_id": f"TX-{len(txns)+1:05d}",
            "coil_id": coil_id,
            "type": tx_type,
            "quantity_lbs": qty,
            "job_code": job_code,
            "reference": ref,
            "notes": "",
            "date": datetime.datetime.now().isoformat(),
        })
        with open(tx_path, "w") as f:
            json.dump(txns, f, indent=2)


class InventoryAllocateReleaseHandler(BaseHandler):
    """POST /api/inventory/allocate/release — Release an allocation."""
    def post(self):
        body = json_decode(self.request.body)
        alloc_id = body.get("allocation_id", "")
        alloc_path = os.path.join(DATA_DIR, "inventory_allocations.json")
        allocs = []
        if os.path.isfile(alloc_path):
            with open(alloc_path) as f:
                allocs = json.load(f)
        found = None
        for a in allocs:
            if a.get("allocation_id") == alloc_id:
                found = a
                break
        if not found:
            self.write(json_encode({"ok": False, "error": "Allocation not found"}))
            return

        remaining = found.get("quantity_lbs", 0) - found.get("consumed_lbs", 0)
        found["status"] = "released"
        with open(alloc_path, "w") as f:
            json.dump(allocs, f, indent=2)

        if remaining > 0:
            inv = load_inventory()
            coil = inv.get("coils", {}).get(found["coil_id"], {})
            coil["committed_lbs"] = max(0, float(coil.get("committed_lbs", 0)) - remaining)
            save_inventory(inv)

        self.write(json_encode({"ok": True}))


class InventoryReceivingHandler(BaseHandler):
    """GET /api/inventory/receiving — Return receiving records."""
    def get(self):
        rcv_path = os.path.join(DATA_DIR, "inventory_receiving.json")
        records = []
        if os.path.isfile(rcv_path):
            with open(rcv_path) as f:
                records = json.load(f)
        self.write(json_encode({"ok": True, "receiving": records[-100:]}))


class InventoryReceiveHandler(BaseHandler):
    """POST /api/inventory/receive — Receive stock into inventory."""
    def post(self):
        body = json_decode(self.request.body)
        coil_id = body.get("coil_id", "")
        qty = float(body.get("quantity_lbs", 0) or 0)
        if not coil_id or qty <= 0:
            self.write(json_encode({"ok": False, "error": "coil_id and quantity_lbs required"}))
            return

        inv = load_inventory()
        coils = inv.get("coils", {})
        if coil_id not in coils:
            self.write(json_encode({"ok": False, "error": "Coil not found"}))
            return

        coils[coil_id]["stock_lbs"] = float(coils[coil_id].get("stock_lbs", 0)) + qty
        save_inventory(inv)

        import datetime
        rcv_path = os.path.join(DATA_DIR, "inventory_receiving.json")
        records = []
        if os.path.isfile(rcv_path):
            with open(rcv_path) as f:
                records = json.load(f)
        rcv_id = f"RCV-{len(records)+1:04d}"
        records.append({
            "receiving_id": rcv_id,
            "coil_id": coil_id,
            "supplier": body.get("supplier", ""),
            "quantity_lbs": qty,
            "po_number": body.get("po_number", ""),
            "bol_number": body.get("bol_number", ""),
            "heat_number": body.get("heat_number", ""),
            "condition_notes": body.get("condition_notes", ""),
            "date": datetime.datetime.now().isoformat(),
        })
        with open(rcv_path, "w") as f:
            json.dump(records, f, indent=2)

        self.write(json_encode({"ok": True, "receiving_id": rcv_id}))


class InventoryAlertsHandler(BaseHandler):
    """GET /api/inventory/alerts — Return inventory alerts."""
    def get(self):
        ack_filter = self.get_query_argument("acknowledged", "false")
        inv = load_inventory()
        coils = inv.get("coils", {})
        alerts = []
        import datetime
        for cid, c in coils.items():
            stock = float(c.get("stock_lbs", 0) or 0)
            committed = float(c.get("committed_lbs", 0) or 0)
            avail = stock - committed
            min_stock = float(c.get("min_stock_lbs", c.get("min_order_lbs", 2000)) or 2000)

            if avail <= 0:
                alerts.append({
                    "alert_id": f"ALT-{cid}",
                    "level": "critical",
                    "coil_id": cid,
                    "message": f"{c.get('name', cid)} is OUT OF STOCK ({avail:,.0f} lbs available)",
                    "date": datetime.datetime.now().isoformat(),
                })
            elif avail < min_stock:
                alerts.append({
                    "alert_id": f"ALT-{cid}",
                    "level": "warning",
                    "coil_id": cid,
                    "message": f"{c.get('name', cid)} is LOW ({avail:,.0f} lbs available, min {min_stock:,.0f})",
                    "date": datetime.datetime.now().isoformat(),
                })
        self.write(json_encode({"ok": True, "alerts": alerts}))


class InventoryAlertAcknowledgeHandler(BaseHandler):
    """POST /api/inventory/alerts/acknowledge — Acknowledge an alert."""
    def post(self):
        self.write(json_encode({"ok": True}))


# ─────────────────────────────────────────────
# INVENTORY & TRACEABILITY PAGE HANDLERS
# ─────────────────────────────────────────────

class InventoryPageHandler(BaseHandler):
    """GET /inventory — Coil Inventory page."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        from templates.inventory_page import INVENTORY_PAGE_HTML
        self.render_with_nav(INVENTORY_PAGE_HTML, active_page="inventory")


class TraceabilityPageHandler(BaseHandler):
    """GET /inventory/traceability — Material Traceability page."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        # Render a traceability-focused view of inventory data
        html = """
        <div style="padding:24px;max-width:1200px;margin:0 auto">
          <h1 style="color:#F6AE2D;margin-bottom:8px">Material Traceability</h1>
          <p style="color:#94A3B8;margin-bottom:24px">Track material heat numbers, mill certifications, and coil assignments across all jobs.</p>
          <div id="traceApp" style="color:#CBD5E1">
            <div style="display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap">
              <input type="text" id="traceSearch" placeholder="Search by heat #, coil ID, or job code..."
                style="flex:1;min-width:250px;padding:10px 14px;background:#1E293B;border:1px solid #334155;
                border-radius:8px;color:#F1F5F9;font-size:14px" oninput="filterTrace()">
              <button onclick="loadTraceData()" style="padding:10px 20px;background:#1E40AF;color:#FFF;
                border:none;border-radius:8px;font-weight:600;cursor:pointer">Refresh</button>
            </div>
            <div id="traceTable" style="background:#1E293B;border-radius:12px;overflow:hidden">
              <div style="padding:40px;text-align:center;color:#64748B">Loading traceability data...</div>
            </div>
          </div>
        </div>
        <script>
        var traceData = [];
        function loadTraceData() {
          tfFetch('/api/traceability').then(function(d) {
            traceData = d.entries || [];
            renderTrace(traceData);
          });
        }
        function filterTrace() {
          var q = document.getElementById('traceSearch').value.toLowerCase();
          var filtered = traceData.filter(function(e) {
            return (e.heat_num||'').toLowerCase().indexOf(q)>=0
              || (e.coil_id||'').toLowerCase().indexOf(q)>=0
              || (e.job_code||'').toLowerCase().indexOf(q)>=0;
          });
          renderTrace(filtered);
        }
        function renderTrace(entries) {
          if (!entries.length) {
            document.getElementById('traceTable').innerHTML =
              '<div style="padding:40px;text-align:center;color:#64748B">No traceability records found.</div>';
            return;
          }
          var h = '<table style="width:100%;border-collapse:collapse;font-size:14px">'
            + '<tr style="background:#0F172A;color:#94A3B8;text-align:left">'
            + '<th style="padding:12px">Heat #</th><th style="padding:12px">Coil ID</th>'
            + '<th style="padding:12px">Job Code</th><th style="padding:12px">Ship Mark</th>'
            + '<th style="padding:12px">Date</th></tr>';
          entries.forEach(function(e) {
            h += '<tr style="border-top:1px solid #334155">'
              + '<td style="padding:10px 12px;color:#F6AE2D;font-weight:600">' + (e.heat_num||'—') + '</td>'
              + '<td style="padding:10px 12px">' + (e.coil_id||'—') + '</td>'
              + '<td style="padding:10px 12px">' + (e.job_code||'—') + '</td>'
              + '<td style="padding:10px 12px">' + (e.ship_mark||'—') + '</td>'
              + '<td style="padding:10px 12px;color:#64748B">' + (e.date||'—') + '</td>'
              + '</tr>';
          });
          h += '</table>';
          document.getElementById('traceTable').innerHTML = h;
        }
        loadTraceData();
        </script>
        """
        self.render_with_nav(html, active_page="traceability")


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


class ProjectAssetsHandler(BaseHandler):
    """GET /api/project/assets?job_code=XXX — Check what assets exist for a project."""

    def get(self):
        try:
            job_code = self.get_query_argument("job_code", "").strip()
            if not job_code:
                self.set_header("Content-Type", "application/json")
                self.write(json_encode({"ok": False, "error": "No job_code provided"}))
                return

            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            project_dir = os.path.join(PROJECTS_DIR, safe_name)

            assets = {
                "sa_estimator": {"saved": False},
                "tc_estimator": {"saved": False},
                "bom": {"saved": False},
                "quote_editor": {"saved": False},
                "shop_drawings": {"saved": False, "count": 0},
                "work_orders": {"saved": False, "count": 0},
                "field_ops": {"saved": False},
                "shipping": {"saved": False}
            }

            # ── SA Estimator / BOM (current.json) ──
            current_path = os.path.join(project_dir, "current.json")
            if os.path.isfile(current_path):
                try:
                    with open(current_path, "r") as f:
                        data = json.load(f)
                    version = data.get("version")
                    assets["sa_estimator"]["saved"] = True
                    if version is not None:
                        assets["sa_estimator"]["version"] = version

                    # Sum n_struct_cols across all buildings
                    total_cols = 0
                    buildings = data.get("buildings", [])
                    if isinstance(buildings, list):
                        for b in buildings:
                            if isinstance(b, dict):
                                geo = b.get("geometry", {})
                                if isinstance(geo, dict):
                                    total_cols += int(geo.get("n_struct_cols", 0) or 0)
                                if total_cols == 0:
                                    total_cols += int(b.get("n_struct_cols", 0) or 0)
                    assets["sa_estimator"]["total_columns"] = total_cols
                    assets["bom"]["saved"] = True
                    if version is not None:
                        assets["bom"]["version"] = version
                except Exception:
                    assets["sa_estimator"]["saved"] = True

            # ── TC Estimator (tc_quote.json) ──
            if os.path.isfile(os.path.join(project_dir, "tc_quote.json")):
                assets["tc_estimator"]["saved"] = True

            # ── Quote Editor (quote_data.json) ──
            if os.path.isfile(os.path.join(project_dir, "quote_data.json")):
                assets["quote_editor"]["saved"] = True

            # ── Shop Drawings (shop_drawings/*.pdf) ──
            sd_dir = os.path.join(project_dir, "shop_drawings")
            if os.path.isdir(sd_dir):
                pdfs = glob.glob(os.path.join(sd_dir, "*.pdf"))
                if pdfs:
                    assets["shop_drawings"]["saved"] = True
                    assets["shop_drawings"]["count"] = len(pdfs)

            # ── Work Orders (work_orders/*.json) ──
            wo_dir = os.path.join(project_dir, "work_orders")
            if os.path.isdir(wo_dir):
                jsons = glob.glob(os.path.join(wo_dir, "*.json"))
                if jsons:
                    assets["work_orders"]["saved"] = True
                    assets["work_orders"]["count"] = len(jsons)

            # ── Field Ops ──
            if os.path.isfile(os.path.join(project_dir, "field_ops.json")):
                assets["field_ops"]["saved"] = True

            # ── Shipping ──
            if os.path.isfile(os.path.join(project_dir, "shipping.json")):
                assets["shipping"]["saved"] = True

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "assets": assets}))

        except Exception as e:
            import traceback
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": False, "error": str(e), "trace": traceback.format_exc()}))


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
# PROJECT CREATE & FULL PROJECT PAGE HANDLERS
# ─────────────────────────────────────────────

# Default document categories for new projects
DEFAULT_DOC_CATEGORIES = [
    {"key": "quotes",        "label": "Quotes",        "icon": "doc_quote"},
    {"key": "contracts",     "label": "Contracts",      "icon": "doc_contract"},
    {"key": "engineering",   "label": "Engineering",    "icon": "doc_engineering"},
    {"key": "calcs",         "label": "Calcs",          "icon": "doc_calcs"},
    {"key": "shop_drawings", "label": "Shop Drawings",  "icon": "doc_shop"},
    {"key": "mill_certs",    "label": "Mill Certs",     "icon": "doc_certs"},
    {"key": "photos",        "label": "Photos",         "icon": "doc_photos"},
    {"key": "other",         "label": "Other",          "icon": "doc_other"},
]

# Stage-aware next-steps templates
STAGE_NEXT_STEPS = {
    "quote": [
        {"text": "Calculate BOM in Structures America Estimator", "key": "calc_bom"},
        {"text": "Review pricing and markup", "key": "review_pricing"},
        {"text": "Generate PDF quote", "key": "gen_quote_pdf"},
        {"text": "Send quote to customer", "key": "send_quote"},
    ],
    "contract": [
        {"text": "Upload signed contract", "key": "upload_contract"},
        {"text": "Submit for engineering", "key": "submit_eng"},
        {"text": "Order long-lead materials", "key": "order_materials"},
        {"text": "Verify deposit received", "key": "verify_deposit"},
    ],
    "engineering": [
        {"text": "Upload engineering drawings", "key": "upload_eng"},
        {"text": "Review calcs and connections", "key": "review_calcs"},
        {"text": "Check material availability", "key": "check_materials"},
        {"text": "Approve engineering for shop drawings", "key": "approve_eng"},
    ],
    "shop_drawings": [
        {"text": "Create shop drawings", "key": "create_shop_dwg"},
        {"text": "Upload shop drawings for review", "key": "upload_shop_dwg"},
        {"text": "Get customer/engineer approval", "key": "get_approval"},
        {"text": "Release to fabrication", "key": "release_fab"},
    ],
    "fabrication": [
        {"text": "Generate shop labels", "key": "gen_labels"},
        {"text": "Print cut lists", "key": "print_cuts"},
        {"text": "Verify inventory for job", "key": "verify_inv"},
        {"text": "Complete fabrication QC check", "key": "fab_qc"},
    ],
    "shipping": [
        {"text": "Create load list (erection sequence)", "key": "load_list"},
        {"text": "Schedule delivery", "key": "schedule_delivery"},
        {"text": "Confirm delivery address", "key": "confirm_address"},
        {"text": "Ship and update tracking", "key": "ship_update"},
    ],
    "install": [
        {"text": "Confirm crew scheduled", "key": "confirm_crew"},
        {"text": "Verify all materials on site", "key": "verify_onsite"},
        {"text": "Complete installation", "key": "complete_install"},
        {"text": "Upload completion photos", "key": "upload_photos"},
    ],
    "complete": [
        {"text": "Upload final inspection report", "key": "final_inspect"},
        {"text": "Send final invoice", "key": "final_invoice"},
        {"text": "Collect final payment", "key": "final_payment"},
        {"text": "Archive project", "key": "archive"},
    ],
}


class ProjectNextCodeHandler(BaseHandler):
    """GET /api/project/next-code — Generate next available job code."""
    def get(self):
        year = datetime.datetime.now().year
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        existing = os.listdir(PROJECTS_DIR)
        max_num = 0
        prefix = f"{year}-"
        for d in existing:
            if d.startswith(prefix):
                try:
                    num = int(d.split("-", 1)[1])
                    max_num = max(max_num, num)
                except (ValueError, IndexError):
                    pass
        next_code = f"{year}-{max_num + 1:04d}"
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "job_code": next_code}))


class ProjectCreateHandler(BaseHandler):
    """POST /api/project/create — Create a new project with metadata."""
    required_roles = ["admin", "estimator"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()

            if not job_code:
                self.write(json_encode({"ok": False, "error": "Job code is required"}))
                return

            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            proj_dir = os.path.join(PROJECTS_DIR, safe_name)

            # Check if project already exists
            if os.path.isdir(proj_dir) and os.path.isfile(os.path.join(proj_dir, "metadata.json")):
                self.write(json_encode({"ok": False, "error": f"Project {job_code} already exists"}))
                return

            os.makedirs(proj_dir, exist_ok=True)

            # Create document category folders
            docs_dir = os.path.join(proj_dir, "docs")
            categories = body.get("doc_categories", DEFAULT_DOC_CATEGORIES)
            for cat in categories:
                os.makedirs(os.path.join(docs_dir, cat["key"]), exist_ok=True)

            # Build metadata
            now = datetime.datetime.now().isoformat()
            stage = body.get("stage", "quote")
            if stage not in PROJECT_STAGES:
                stage = "quote"

            metadata = {
                "job_code": job_code,
                "project_name": body.get("project_name", "").strip(),
                "customer": {
                    "name":  body.get("customer_name", "").strip(),
                    "phone": body.get("customer_phone", "").strip(),
                    "email": body.get("customer_email", "").strip(),
                },
                "location": {
                    "street":  body.get("location_street", "").strip(),
                    "city":    body.get("location_city", "").strip(),
                    "state":   body.get("location_state", "").strip(),
                    "zip":     body.get("location_zip", "").strip(),
                },
                "stage": stage,
                "notes": body.get("notes", "").strip(),
                "doc_categories": categories,
                "checklist": {},
                "created_at": now,
                "created_by": self.get_current_user() or "unknown",
                "updated_at": now,
                "archived": False,
            }

            # Save metadata
            with open(os.path.join(proj_dir, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)

            # Save initial status
            status_data = {
                "job_code": job_code,
                "stage": stage,
                "updated_at": now,
                "updated_by": self.get_current_user() or "unknown",
            }
            with open(os.path.join(proj_dir, "status.json"), "w") as f:
                json.dump(status_data, f, indent=2)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "job_code": job_code, "metadata": metadata}))

        except Exception as e:
            import traceback
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class ProjectDeleteHandler(BaseHandler):
    """POST /api/project/delete — Delete a project permanently. Admin only.

    Requires:
      - Admin role
      - job_code in request body
      - confirm: true flag (safety check)

    Deletes the entire project directory including all documents,
    shop drawings, work orders, and metadata.
    """
    required_roles = ["admin"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            confirm = body.get("confirm", False)

            if not job_code:
                self.set_header("Content-Type", "application/json")
                self.write(json_encode({"ok": False, "error": "Job code is required"}))
                return

            if not confirm:
                self.set_header("Content-Type", "application/json")
                self.write(json_encode({
                    "ok": False,
                    "error": "Deletion requires confirm: true. This action is permanent.",
                }))
                return

            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            proj_dir = os.path.join(PROJECTS_DIR, safe_name)

            if not os.path.isdir(proj_dir):
                # Also check for legacy single-file project
                legacy_path = os.path.join(PROJECTS_DIR, f"{safe_name}.json")
                if os.path.isfile(legacy_path):
                    os.remove(legacy_path)
                    self.set_header("Content-Type", "application/json")
                    self.write(json_encode({
                        "ok": True,
                        "deleted": job_code,
                        "deleted_by": self.get_current_user() or "unknown",
                    }))
                    return
                self.set_header("Content-Type", "application/json")
                self.write(json_encode({"ok": False, "error": f"Project '{job_code}' not found"}))
                return

            # Safety: verify the path is actually under PROJECTS_DIR
            real_proj = os.path.realpath(proj_dir)
            real_base = os.path.realpath(PROJECTS_DIR)
            if not real_proj.startswith(real_base):
                self.set_status(403)
                self.set_header("Content-Type", "application/json")
                self.write(json_encode({"ok": False, "error": "Invalid project path"}))
                return

            # Log the deletion before removing
            deleted_by = self.get_current_user() or "unknown"
            deleted_at = datetime.datetime.now().isoformat()

            # Remove the entire project directory
            shutil.rmtree(proj_dir)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "deleted": job_code,
                "deleted_by": deleted_by,
                "deleted_at": deleted_at,
            }))

        except Exception as e:
            import traceback
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class ProjectMetadataHandler(BaseHandler):
    """GET/POST /api/project/metadata — Get or update project metadata."""
    def get(self):
        job_code = self.get_query_argument("job_code", "").strip()
        if not job_code:
            self.write(json_encode({"ok": False, "error": "No job_code"}))
            return
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
        meta_path = os.path.join(PROJECTS_DIR, safe_name, "metadata.json")
        if not os.path.isfile(meta_path):
            self.write(json_encode({"ok": False, "error": "Project not found"}))
            return
        with open(meta_path) as f:
            metadata = json.load(f)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "metadata": metadata}))

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            if not job_code:
                self.write(json_encode({"ok": False, "error": "No job_code"}))
                return
            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            meta_path = os.path.join(PROJECTS_DIR, safe_name, "metadata.json")
            if not os.path.isfile(meta_path):
                self.write(json_encode({"ok": False, "error": "Project not found"}))
                return

            with open(meta_path) as f:
                metadata = json.load(f)

            # Update allowed fields
            updates = body.get("updates", {})
            for key in ["project_name", "notes", "stage", "doc_categories", "archived"]:
                if key in updates:
                    metadata[key] = updates[key]
            if "customer" in updates:
                metadata["customer"].update(updates["customer"])
            if "location" in updates:
                metadata["location"].update(updates["location"])
            if "checklist" in updates:
                metadata["checklist"].update(updates["checklist"])

            metadata["updated_at"] = datetime.datetime.now().isoformat()

            with open(meta_path, "w") as f:
                json.dump(metadata, f, indent=2)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "metadata": metadata}))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class ProjectChecklistHandler(BaseHandler):
    """POST /api/project/checklist — Update checklist items for a project."""
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            item_key = body.get("item_key", "").strip()
            checked = body.get("checked", False)

            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            meta_path = os.path.join(PROJECTS_DIR, safe_name, "metadata.json")
            if not os.path.isfile(meta_path):
                self.write(json_encode({"ok": False, "error": "Project not found"}))
                return

            with open(meta_path) as f:
                metadata = json.load(f)

            checklist = metadata.get("checklist", {})
            if checked:
                checklist[item_key] = {
                    "completed_at": datetime.datetime.now().isoformat(),
                    "completed_by": self.get_current_user() or "unknown",
                }
            else:
                checklist.pop(item_key, None)

            metadata["checklist"] = checklist
            metadata["updated_at"] = datetime.datetime.now().isoformat()

            with open(meta_path, "w") as f:
                json.dump(metadata, f, indent=2)

            # Calculate completion percentage
            stage = metadata.get("stage", "quote")
            steps = STAGE_NEXT_STEPS.get(stage, [])
            total = len(steps)
            done = sum(1 for s in steps if s["key"] in checklist)
            pct = int((done / total) * 100) if total > 0 else 0

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "checklist": checklist, "completion_pct": pct}))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class ProjectNextStepsHandler(BaseHandler):
    """GET /api/project/next-steps — Get stage-aware next steps for a project."""
    def get(self):
        job_code = self.get_query_argument("job_code", "").strip()
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
        meta_path = os.path.join(PROJECTS_DIR, safe_name, "metadata.json")

        stage = "quote"
        checklist = {}
        if os.path.isfile(meta_path):
            with open(meta_path) as f:
                meta = json.load(f)
            stage = meta.get("stage", "quote")
            checklist = meta.get("checklist", {})

        steps = STAGE_NEXT_STEPS.get(stage, STAGE_NEXT_STEPS["quote"])
        result = []
        for s in steps:
            result.append({
                "text": s["text"],
                "key": s["key"],
                "completed": s["key"] in checklist,
                "completed_at": checklist.get(s["key"], {}).get("completed_at"),
                "completed_by": checklist.get(s["key"], {}).get("completed_by"),
            })

        total = len(steps)
        done = sum(1 for r in result if r["completed"])
        pct = int((done / total) * 100) if total > 0 else 0

        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True, "stage": stage, "steps": result,
            "completion_pct": pct, "done": done, "total": total,
        }))


class ProjectPageHandler(BaseHandler):
    """GET /project/{job_code} — Full project page."""
    def get(self, job_code):
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
        meta_path = os.path.join(PROJECTS_DIR, safe_name, "metadata.json")

        if not os.path.isfile(meta_path):
            self.set_status(404)
            self.write(f"<h2>Project '{job_code}' not found</h2><a href='/'>Back to Dashboard</a>")
            return

        with open(meta_path) as f:
            metadata = json.load(f)

        role = self.get_user_role() or "viewer"
        display = "User"
        if AUTH_ENABLED:
            user = self.get_current_user()
            users = load_users()
            display = users.get(user, {}).get("display_name", user or "User")

        html = PROJECT_PAGE_HTML
        html = html.replace("{{JOB_CODE}}", job_code)
        html = html.replace("{{METADATA_JSON}}", json.dumps(metadata))
        html = html.replace("{{USER_ROLE}}", role)
        html = html.replace("{{USER_NAME}}", display)
        html = html.replace("{{STAGES_JSON}}", json.dumps(PROJECT_STAGES))
        html = html.replace("{{NEXT_STEPS_JSON}}", json.dumps(STAGE_NEXT_STEPS))
        html = html.replace("{{DOC_CATEGORIES_JSON}}", json.dumps(DEFAULT_DOC_CATEGORIES))

        self.render_with_nav(html, active_page="project", job_code=job_code)


class ProjectArchiveDocHandler(BaseHandler):
    """POST /api/project/docs/archive — Archive a document (move to archive subfolder)."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            category = body.get("category", "").lower()
            filename = body.get("filename", "").strip()

            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            src = os.path.join(PROJECTS_DIR, safe_name, "docs", category, filename)
            archive_dir = os.path.join(PROJECTS_DIR, safe_name, "docs", category, "_archive")
            os.makedirs(archive_dir, exist_ok=True)

            if not os.path.isfile(src):
                self.write(json_encode({"ok": False, "error": "File not found"}))
                return

            # Add timestamp to archived filename to prevent overwrites
            ts = int(time.time())
            base, ext = os.path.splitext(filename)
            archived_name = f"{base}_archived_{ts}{ext}"
            dst = os.path.join(archive_dir, archived_name)

            os.rename(src, dst)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "archived_as": archived_name}))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({"error": str(e), "trace": traceback.format_exc()}))


class ProjectArchivedDocsHandler(BaseHandler):
    """POST /api/project/docs/archived — List archived documents for a category."""
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            category = body.get("category", "").lower()

            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            archive_dir = os.path.join(PROJECTS_DIR, safe_name, "docs", category, "_archive")

            files = []
            if os.path.isdir(archive_dir):
                for fname in sorted(os.listdir(archive_dir), reverse=True):
                    fpath = os.path.join(archive_dir, fname)
                    if os.path.isfile(fpath):
                        stat = os.stat(fpath)
                        files.append({
                            "filename": fname,
                            "category": category,
                            "size": stat.st_size,
                            "url": f"/project-files/{safe_name}/{category}/_archive/{fname}",
                            "archived_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        })

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "files": files}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"error": str(e)}))


# ─────────────────────────────────────────────
# ENHANCED PROJECT LIST (includes metadata)
# ─────────────────────────────────────────────

class ProjectListEnhancedHandler(BaseHandler):
    """GET /api/projects/full — List all projects with full metadata."""
    def get(self):
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        show_archived = self.get_query_argument("archived", "false").lower() == "true"
        result = []

        for d in sorted(os.listdir(PROJECTS_DIR), reverse=True):
            dpath = os.path.join(PROJECTS_DIR, d)
            if not os.path.isdir(dpath):
                continue

            meta_path = os.path.join(dpath, "metadata.json")
            if os.path.isfile(meta_path):
                try:
                    with open(meta_path) as f:
                        meta = json.load(f)
                    if meta.get("archived", False) and not show_archived:
                        continue
                    # Count documents
                    docs_dir = os.path.join(dpath, "docs")
                    doc_count = 0
                    if os.path.isdir(docs_dir):
                        for cat in os.listdir(docs_dir):
                            cat_path = os.path.join(docs_dir, cat)
                            if os.path.isdir(cat_path):
                                doc_count += len([f for f in os.listdir(cat_path)
                                                  if os.path.isfile(os.path.join(cat_path, f))
                                                  and not f.startswith(".")])
                    # Count versions
                    n_versions = len(glob.glob(os.path.join(dpath, "v*.json")))
                    meta["doc_count"] = doc_count
                    meta["n_versions"] = n_versions
                    result.append(meta)
                except Exception:
                    pass
            else:
                # Legacy project (no metadata.json) — build minimal entry
                cpath = os.path.join(dpath, "current.json")
                if os.path.isfile(cpath):
                    try:
                        with open(cpath) as f:
                            data = json.load(f)
                        result.append({
                            "job_code": data.get("job_code", d),
                            "project_name": data.get("project", {}).get("name", ""),
                            "customer": {"name": data.get("project", {}).get("customer_name", "")},
                            "stage": "quote",
                            "created_at": data.get("saved_at", ""),
                            "updated_at": data.get("saved_at", ""),
                            "archived": False,
                            "n_versions": len(glob.glob(os.path.join(dpath, "v*.json"))),
                            "doc_count": 0,
                        })
                    except Exception:
                        pass

        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "projects": result}))


# ─────────────────────────────────────────────
# CUSTOMER DATABASE HANDLERS
# ─────────────────────────────────────────────

class CustomerListHandler(BaseHandler):
    """GET /api/customers — List all customers with optional search."""
    def get(self):
        customers = load_customers()
        q = self.get_query_argument("q", "").strip().lower()
        tag = self.get_query_argument("tag", "").strip().lower()
        if q:
            customers = [c for c in customers
                         if q in c.get("company","").lower()
                         or q in c.get("primary_contact",{}).get("name","").lower()
                         or q in c.get("primary_contact",{}).get("email","").lower()
                         or any(q in ct.get("name","").lower() for ct in c.get("contacts",[]))]
        if tag:
            customers = [c for c in customers if tag in [t.lower() for t in c.get("tags",[])]]
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "customers": customers}))

class CustomerCreateHandler(BaseHandler):
    """POST /api/customers/create — Create a new customer."""
    required_roles = ["admin", "estimator"]
    def post(self):
        body = json_decode(self.request.body)
        customers = load_customers()
        cid = "CUS-" + datetime.datetime.now().strftime("%Y%m%d") + "-" + secrets.token_hex(3).upper()
        now = datetime.datetime.now().isoformat()
        customer = {
            "id": cid,
            "company": body.get("company", ""),
            "primary_contact": body.get("primary_contact", {}),
            "contacts": body.get("contacts", []),
            "address": body.get("address", {}),
            "tags": body.get("tags", []),
            "notes": body.get("notes", ""),
            "payment_terms": body.get("payment_terms", "Net 30"),
            "credit_limit": body.get("credit_limit", ""),
            "tax_id": body.get("tax_id", ""),
            "insurance_info": body.get("insurance_info", ""),
            "credit_terms": body.get("credit_terms", ""),
            "created_at": now,
            "updated_at": now,
        }
        customers.append(customer)
        save_customers(customers)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "customer": customer}))

class CustomerUpdateHandler(BaseHandler):
    """POST /api/customers/update — Update a customer record."""
    required_roles = ["admin", "estimator"]
    def post(self):
        body = json_decode(self.request.body)
        cid = body.get("id", "")
        customers = load_customers()
        found = False
        for i, c in enumerate(customers):
            if c["id"] == cid:
                for k, v in body.items():
                    if k != "id":
                        customers[i][k] = v
                customers[i]["updated_at"] = datetime.datetime.now().isoformat()
                found = True
                break
        if not found:
            self.write(json_encode({"ok": False, "error": "Customer not found"}))
            return
        save_customers(customers)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "customer": customers[i]}))

class CustomerDeleteHandler(BaseHandler):
    """POST /api/customers/delete — Delete a customer record."""
    required_roles = ["admin"]
    def post(self):
        body = json_decode(self.request.body)
        cid = body.get("id", "")
        customers = load_customers()
        customers = [c for c in customers if c["id"] != cid]
        save_customers(customers)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True}))

class CustomerDetailHandler(BaseHandler):
    """GET /api/customers/detail — Get single customer with project history."""
    def get(self):
        cid = self.get_query_argument("id", "")
        customers = load_customers()
        customer = next((c for c in customers if c["id"] == cid), None)
        if not customer:
            self.write(json_encode({"ok": False, "error": "Not found"}))
            return
        # Attach project history
        projects = []
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        cname = customer.get("company", "").lower()
        for d in sorted(os.listdir(PROJECTS_DIR), reverse=True):
            mpath = os.path.join(PROJECTS_DIR, d, "metadata.json")
            if os.path.isfile(mpath):
                try:
                    with open(mpath) as f:
                        meta = json.load(f)
                    pname = meta.get("customer", {}).get("name", "").lower()
                    if cname and cname in pname:
                        projects.append({
                            "job_code": meta.get("job_code", d),
                            "project_name": meta.get("project_name", ""),
                            "stage": meta.get("stage", ""),
                            "created_at": meta.get("created_at", ""),
                        })
                except Exception:
                    pass
        customer["projects"] = projects
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "customer": customer}))

class CustomerDocUploadHandler(BaseHandler):
    """POST /api/customers/docs/upload — Upload a document for a customer."""
    required_roles = ["admin", "estimator"]
    def post(self):
        cid = self.get_argument("customer_id", "")
        doc_type = self.get_argument("doc_type", "other")  # contract, insurance, tax_id, credit_terms, other
        if not cid:
            self.write(json_encode({"ok": False, "error": "customer_id required"}))
            return
        safe_cid = re.sub(r'[^A-Za-z0-9_-]', '_', cid)
        docs_dir = os.path.join(DATA_DIR, "customer_docs", safe_cid, doc_type)
        os.makedirs(docs_dir, exist_ok=True)
        uploaded = []
        for field_name, files in self.request.files.items():
            for finfo in files:
                fname = re.sub(r'[^A-Za-z0-9._-]', '_', finfo["filename"])
                fpath = os.path.join(docs_dir, fname)
                with open(fpath, "wb") as f:
                    f.write(finfo["body"])
                uploaded.append({"name": fname, "type": doc_type, "size": len(finfo["body"])})
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "uploaded": uploaded}))

class CustomerDocListHandler(BaseHandler):
    """GET /api/customers/docs — List documents for a customer."""
    def get(self):
        cid = self.get_query_argument("customer_id", "")
        safe_cid = re.sub(r'[^A-Za-z0-9_-]', '_', cid)
        base = os.path.join(DATA_DIR, "customer_docs", safe_cid)
        docs = {}
        if os.path.isdir(base):
            for dtype in os.listdir(base):
                dpath = os.path.join(base, dtype)
                if os.path.isdir(dpath):
                    docs[dtype] = []
                    for f in os.listdir(dpath):
                        fpath = os.path.join(dpath, f)
                        if os.path.isfile(fpath):
                            docs[dtype].append({
                                "name": f,
                                "size": os.path.getsize(fpath),
                                "url": f"/customer-files/{safe_cid}/{dtype}/{f}",
                            })
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "docs": docs}))

class CustomerDocServeHandler(tornado.web.RequestHandler):
    """GET /customer-files/{cid}/{type}/{filename} — Serve customer document."""
    def get(self, cid, dtype, fname):
        fpath = os.path.join(DATA_DIR, "customer_docs", cid, dtype, fname)
        if not os.path.isfile(fpath):
            self.set_status(404)
            self.write("Not found")
            return
        import mimetypes
        ct = mimetypes.guess_type(fname)[0] or "application/octet-stream"
        self.set_header("Content-Type", ct)
        self.set_header("Content-Disposition", f'inline; filename="{fname}"')
        with open(fpath, "rb") as f:
            self.write(f.read())

class CustomerPageHandler(BaseHandler):
    """GET /customers — Customer database page."""
    def get(self):
        self.render_with_nav(CUSTOMERS_HTML, active_page="customers")


# ─────────────────────────────────────────────
# GLOBAL SEARCH HANDLER
# ─────────────────────────────────────────────

class GlobalSearchHandler(BaseHandler):
    """GET /api/search — Search across projects, customers, and inventory."""
    def get(self):
        q = self.get_query_argument("q", "").strip().lower()
        if not q or len(q) < 2:
            self.write(json_encode({"ok": True, "results": []}))
            return
        results = []
        # Search projects
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        for d in os.listdir(PROJECTS_DIR):
            mpath = os.path.join(PROJECTS_DIR, d, "metadata.json")
            if os.path.isfile(mpath):
                try:
                    with open(mpath) as f:
                        meta = json.load(f)
                    searchable = " ".join([
                        meta.get("job_code", ""),
                        meta.get("project_name", ""),
                        meta.get("customer", {}).get("name", ""),
                        meta.get("customer", {}).get("email", ""),
                        meta.get("location", {}).get("city", ""),
                        meta.get("location", {}).get("state", ""),
                        meta.get("notes", ""),
                    ]).lower()
                    if q in searchable:
                        results.append({
                            "type": "project",
                            "title": meta.get("project_name", d),
                            "subtitle": f'{meta.get("job_code","")} — {meta.get("customer",{}).get("name","")}',
                            "stage": meta.get("stage", ""),
                            "url": f'/project/{meta.get("job_code", d)}',
                            "icon": "project",
                        })
                except Exception:
                    pass
        # Search customers
        customers = load_customers()
        for c in customers:
            searchable = " ".join([
                c.get("company", ""),
                c.get("primary_contact", {}).get("name", ""),
                c.get("primary_contact", {}).get("email", ""),
                c.get("primary_contact", {}).get("phone", ""),
                c.get("notes", ""),
                " ".join(c.get("tags", [])),
            ]).lower()
            if q in searchable:
                results.append({
                    "type": "customer",
                    "title": c.get("company", "Unknown"),
                    "subtitle": c.get("primary_contact", {}).get("name", ""),
                    "url": f'/customers?id={c.get("id","")}',
                    "icon": "customer",
                })
        # Search inventory
        try:
            inv = load_inventory()
            for coil in inv:
                searchable = " ".join([
                    coil.get("coil_tag", ""),
                    coil.get("gauge", ""),
                    coil.get("color", ""),
                    coil.get("width", ""),
                    coil.get("manufacturer", ""),
                    coil.get("po_number", ""),
                ]).lower()
                if q in searchable:
                    results.append({
                        "type": "inventory",
                        "title": f'{coil.get("gauge","")} ga {coil.get("color","")} — {coil.get("width","")}',
                        "subtitle": f'Tag: {coil.get("coil_tag","")} | {coil.get("weight_lbs",0)} lbs',
                        "url": f'/coil/{coil.get("coil_tag","")}',
                        "icon": "inventory",
                    })
        except Exception:
            pass
        # Cap results
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "results": results[:50]}))


# ─────────────────────────────────────────────
# QUOTE EDITOR / GENERATOR HANDLERS
# ─────────────────────────────────────────────

class QuoteDataHandler(BaseHandler):
    """GET/POST /api/quote/data — Load or save quote data for a project."""
    def get(self):
        job_code = self.get_query_argument("job_code", "")
        if not job_code:
            self.write(json_encode({"ok": False, "error": "job_code required"}))
            return
        data = load_quote_data(job_code)
        if not data:
            # Build from template + project metadata
            import copy
            data = copy.deepcopy(DEFAULT_QUOTE_TEMPLATE)
            # Try to populate from project metadata
            safe = re.sub(r'[^A-Za-z0-9_-]', '_', job_code)
            mpath = os.path.join(PROJECTS_DIR, safe, "metadata.json")
            if os.path.isfile(mpath):
                try:
                    with open(mpath) as f:
                        meta = json.load(f)
                    data["project_overview"]["customer_name"] = meta.get("customer", {}).get("name", "")
                    data["project_overview"]["customer_company"] = meta.get("customer", {}).get("name", "")
                    data["project_overview"]["job_address"] = meta.get("location", {}).get("street", "")
                    data["project_overview"]["job_city"] = meta.get("location", {}).get("city", "")
                    data["project_overview"]["job_state"] = meta.get("location", {}).get("state", "")
                    data["project_overview"]["job_zip"] = meta.get("location", {}).get("zip", "")
                    data["project_overview"]["quote_number"] = job_code
                    data["project_overview"]["project_description"] = meta.get("project_name", "")
                except Exception:
                    pass
            data["project_overview"]["quote_date"] = datetime.datetime.now().strftime("%m/%d/%Y")
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "data": data}))

    def post(self):
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "")
        data = body.get("data", {})
        if not job_code:
            self.write(json_encode({"ok": False, "error": "job_code required"}))
            return
        save_quote_data(job_code, data)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True}))


class QuotePDFHandler(BaseHandler):
    """POST /api/quote/pdf — Generate a professional PDF quote."""
    required_roles = ["admin", "estimator"]
    def post(self):
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "")
        data = body.get("data")
        if not data:
            data = load_quote_data(job_code)
        if not data:
            self.write(json_encode({"ok": False, "error": "No quote data found"}))
            return

        try:
            pdf_bytes = generate_titan_quote_pdf(data, job_code)
            self.set_header("Content-Type", "application/pdf")
            fname = f"Quote_{job_code}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
            self.set_header("Content-Disposition", f'attachment; filename="{fname}"')
            self.write(pdf_bytes)
        except Exception as e:
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": False, "error": str(e)}))


class QuoteEditorPageHandler(BaseHandler):
    """GET /quote/{job_code} — Quote editor page."""
    def get(self, job_code):
        html = QUOTE_EDITOR_HTML.replace("{{JOB_CODE}}", job_code)
        html = html.replace("{{USER_ROLE}}", self.get_user_role() or "viewer")
        html = html.replace("{{USER_NAME}}", self.get_current_user() or "")
        self.render_with_nav(html, active_page="quote", job_code=job_code)


# ─────────────────────────────────────────────
# QUOTE PDF GENERATION (ReportLab)
# ─────────────────────────────────────────────

def generate_titan_quote_pdf(data, job_code=""):
    """Generate a professional Titan Carports quote PDF using ReportLab."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.75*inch, bottomMargin=0.75*inch,
                            leftMargin=0.75*inch, rightMargin=0.75*inch)

    styles = getSampleStyleSheet()
    navy = HexColor("#0F172A")
    blue = HexColor("#1E40AF")
    amber = HexColor("#F59E0B")
    gray = HexColor("#64748B")
    light_bg = HexColor("#F8FAFC")
    border_color = HexColor("#E2E8F0")

    # Custom styles
    title_style = ParagraphStyle('QuoteTitle', parent=styles['Title'],
        fontSize=22, textColor=navy, spaceAfter=4, fontName='Helvetica-Bold')
    h1_style = ParagraphStyle('H1', parent=styles['Heading1'],
        fontSize=14, textColor=navy, spaceBefore=16, spaceAfter=8,
        fontName='Helvetica-Bold', borderWidth=0, borderPadding=0)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
        fontSize=12, textColor=blue, spaceBefore=12, spaceAfter=6,
        fontName='Helvetica-Bold')
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=10, leading=14, textColor=HexColor("#334155"),
        fontName='Helvetica')
    small_style = ParagraphStyle('Small', parent=styles['Normal'],
        fontSize=8.5, leading=11, textColor=gray, fontName='Helvetica')
    bold_body = ParagraphStyle('BoldBody', parent=body_style,
        fontName='Helvetica-Bold')

    story = []
    po = data.get("project_overview", {})

    # ── HEADER ──
    header_data = [
        [Paragraph('<b>TITAN CARPORTS LLC</b>', ParagraphStyle('HC', parent=title_style, fontSize=18, textColor=white)),
         Paragraph(f'<b>PROPOSAL</b><br/><font size="9">Quote #: {po.get("quote_number", job_code)}<br/>Date: {po.get("quote_date","")}</font>',
                   ParagraphStyle('HR', parent=body_style, alignment=TA_RIGHT, textColor=white))],
    ]
    header_table = Table(header_data, colWidths=[4*inch, 3*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), navy),
        ('TEXTCOLOR', (0,0), (-1,-1), white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (0,-1), 16),
        ('RIGHTPADDING', (-1,0), (-1,-1), 16),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 16))

    # ── Section 1.1: Project Overview ──
    story.append(Paragraph("1.1 Project Overview", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=border_color, spaceAfter=8))

    info_data = [
        [Paragraph('<b>Customer:</b>', bold_body), Paragraph(po.get("customer_name",""), body_style),
         Paragraph('<b>Estimator:</b>', bold_body), Paragraph(po.get("estimator_name",""), body_style)],
        [Paragraph('<b>Company:</b>', bold_body), Paragraph(po.get("customer_company",""), body_style),
         Paragraph('<b>Phone:</b>', bold_body), Paragraph(po.get("estimator_phone",""), body_style)],
        [Paragraph('<b>Job Address:</b>', bold_body), Paragraph(po.get("job_address",""), body_style),
         Paragraph('<b>Email:</b>', bold_body), Paragraph(po.get("estimator_email",""), body_style)],
        [Paragraph('<b>City/State/Zip:</b>', bold_body),
         Paragraph(f'{po.get("job_city","")} {po.get("job_state","")} {po.get("job_zip","")}', body_style),
         Paragraph('<b>Valid For:</b>', bold_body), Paragraph(f'{po.get("valid_days",30)} days', body_style)],
    ]
    info_table = Table(info_data, colWidths=[1.2*inch, 2.3*inch, 1.0*inch, 2.5*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # ── Section 1.2: Pricing ──
    story.append(Paragraph("1.2 Pricing", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=border_color, spaceAfter=8))

    pricing = data.get("pricing", {})
    # Base pricing table
    price_rows = [[
        Paragraph('<b>Description</b>', bold_body),
        Paragraph('<b>Amount</b>', ParagraphStyle('R', parent=bold_body, alignment=TA_RIGHT)),
    ]]
    base_total = 0
    for item in pricing.get("base_items", []):
        amt = item.get("amount", 0)
        base_total += amt
        price_rows.append([
            Paragraph(item.get("description", ""), body_style),
            Paragraph(f'${amt:,.2f}', ParagraphStyle('R', parent=body_style, alignment=TA_RIGHT)),
        ])
    price_rows.append([
        Paragraph('<b>BASE TOTAL</b>', bold_body),
        Paragraph(f'<b>${base_total:,.2f}</b>', ParagraphStyle('R', parent=bold_body, alignment=TA_RIGHT)),
    ])
    price_table = Table(price_rows, colWidths=[5*inch, 2*inch])
    price_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('BACKGROUND', (0,-1), (-1,-1), HexColor("#DBEAFE")),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(price_table)
    story.append(Spacer(1, 10))

    # Options table
    options = pricing.get("options", [])
    if options:
        story.append(Paragraph("<b>Options (not included in base price):</b>", bold_body))
        story.append(Spacer(1, 4))
        opt_rows = [[Paragraph('<b>Option</b>', bold_body),
                     Paragraph('<b>Amount</b>', ParagraphStyle('R', parent=bold_body, alignment=TA_RIGHT))]]
        for opt in options:
            opt_rows.append([
                Paragraph(opt.get("description", ""), body_style),
                Paragraph(f'${opt.get("amount",0):,.2f}', ParagraphStyle('R', parent=body_style, alignment=TA_RIGHT)),
            ])
        opt_table = Table(opt_rows, colWidths=[5*inch, 2*inch])
        opt_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor("#475569")),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(opt_table)
    story.append(Spacer(1, 10))

    # ── Inclusions ──
    inclusions = data.get("inclusions", [])
    if inclusions:
        story.append(Paragraph("<b>Inclusions:</b>", bold_body))
        for inc in inclusions:
            story.append(Paragraph(f"&bull; {inc}", body_style))
        story.append(Spacer(1, 8))

    # ── Exclusions (short list on page 1) ──
    excl = data.get("exclusions_categorized", {})
    if excl:
        short_excl = []
        for cat, items in excl.items():
            short_excl.extend(items[:2])
        if short_excl:
            story.append(Paragraph("<b>Exclusions (see full list in Section 2.2):</b>", bold_body))
            for e in short_excl[:8]:
                story.append(Paragraph(f"&bull; {e}", body_style))
            if sum(len(v) for v in excl.values()) > 8:
                story.append(Paragraph("<i>...see Section 2.2 for complete exclusions list</i>", small_style))
        story.append(Spacer(1, 8))

    story.append(Paragraph(f"<i>This proposal is valid for {po.get('valid_days',30)} days from date of issue. "
                           f"Pricing subject to material cost changes after expiration.</i>", small_style))
    story.append(PageBreak())

    # ── Section 1.4: General Project Overview ──
    gpo = data.get("general_project_overview", {})
    if gpo.get("description") or gpo.get("specs"):
        story.append(Paragraph("1.4 General Project Overview", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=border_color, spaceAfter=8))
        if gpo.get("description"):
            story.append(Paragraph(gpo["description"], body_style))
            story.append(Spacer(1, 8))
        specs = gpo.get("specs", {})
        if specs:
            spec_rows = [[Paragraph('<b>Specification</b>', bold_body), Paragraph('<b>Value</b>', bold_body)]]
            for k, v in specs.items():
                spec_rows.append([Paragraph(k, body_style), Paragraph(str(v), body_style)])
            spec_table = Table(spec_rows, colWidths=[3.5*inch, 3.5*inch])
            spec_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), light_bg),
                ('GRID', (0,0), (-1,-1), 0.5, border_color),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(spec_table)
        story.append(Spacer(1, 12))

    # ── Section 1.6: Payment Terms ──
    pt = data.get("payment_terms", {})
    story.append(Paragraph("1.6 Payment Terms", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=border_color, spaceAfter=8))

    if pt.get("engineering_fee_note"):
        story.append(Paragraph(pt["engineering_fee_note"], body_style))
        story.append(Spacer(1, 6))

    if pt.get("billing_description"):
        story.append(Paragraph(pt["billing_description"], body_style))
        story.append(Spacer(1, 8))

    net_days = pt.get("net_days", 30)
    late_fee = pt.get("late_fee_percent", 1.5)
    retainage = pt.get("retainage_percent", 0)
    story.append(Paragraph(f"<b>Payment Terms:</b> Net {net_days} days from date of invoice. "
                           f"Late payments subject to {late_fee}% monthly finance charge.", body_style))
    if retainage:
        story.append(Paragraph(f"<b>Retainage:</b> {retainage}% retainage held until final completion.", body_style))
    story.append(Spacer(1, 8))

    milestones = pt.get("milestones", [])
    if milestones:
        story.append(Paragraph("<b>Monthly Progress Billing Schedule:</b>", bold_body))
        story.append(Spacer(1, 4))
        ms_rows = [[Paragraph('<b>Milestone</b>', bold_body),
                    Paragraph('<b>% of Contract</b>', ParagraphStyle('R', parent=bold_body, alignment=TA_CENTER)),
                    Paragraph('<b>Amount</b>', ParagraphStyle('R', parent=bold_body, alignment=TA_RIGHT)),
                    Paragraph('<b>Cumulative</b>', ParagraphStyle('R', parent=bold_body, alignment=TA_RIGHT))]]
        cumulative = 0
        for ms in milestones:
            pct = ms.get("percent", 0)
            amt = base_total * pct / 100
            cumulative += amt
            ms_rows.append([
                Paragraph(ms.get("label", ""), body_style),
                Paragraph(f'{pct}%', ParagraphStyle('R', parent=body_style, alignment=TA_CENTER)),
                Paragraph(f'${amt:,.2f}', ParagraphStyle('R', parent=body_style, alignment=TA_RIGHT)),
                Paragraph(f'${cumulative:,.2f}', ParagraphStyle('R', parent=body_style, alignment=TA_RIGHT)),
            ])
        ms_rows.append([
            Paragraph('<b>TOTAL</b>', bold_body),
            Paragraph('<b>100%</b>', ParagraphStyle('R', parent=bold_body, alignment=TA_CENTER)),
            Paragraph(f'<b>${base_total:,.2f}</b>', ParagraphStyle('R', parent=bold_body, alignment=TA_RIGHT)),
            Paragraph('', body_style),
        ])
        ms_table = Table(ms_rows, colWidths=[3.2*inch, 1.2*inch, 1.3*inch, 1.3*inch])
        ms_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), navy),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('BACKGROUND', (0,-1), (-1,-1), HexColor("#DBEAFE")),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-2), [white, light_bg]),
        ]))
        story.append(ms_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph("<i>Invoices are submitted monthly based on percentage of milestones completed "
                           "during the billing period. Payment is due within the net terms specified above.</i>", small_style))
    story.append(Spacer(1, 20))

    # ── Signature Block ──
    sig = data.get("signature_block", {})
    story.append(Paragraph("Acceptance", h2_style))
    sig_data = [
        [Paragraph("<b>TITAN CARPORTS LLC</b>", bold_body), Paragraph("", body_style),
         Paragraph("<b>CUSTOMER</b>", bold_body), Paragraph("", body_style)],
        [Paragraph("Signature: ____________________", body_style), Paragraph("", body_style),
         Paragraph("Signature: ____________________", body_style), Paragraph("", body_style)],
        [Paragraph(f"Name: {sig.get('company_signer_name','')}", body_style), Paragraph("", body_style),
         Paragraph(f"Name: {sig.get('customer_signer_name','')}", body_style), Paragraph("", body_style)],
        [Paragraph(f"Title: {sig.get('company_signer_title','')}", body_style), Paragraph("", body_style),
         Paragraph(f"Title: {sig.get('customer_signer_title','')}", body_style), Paragraph("", body_style)],
        [Paragraph("Date: ____________________", body_style), Paragraph("", body_style),
         Paragraph("Date: ____________________", body_style), Paragraph("", body_style)],
    ]
    sig_table = Table(sig_data, colWidths=[3*inch, 0.5*inch, 3*inch, 0.5*inch])
    sig_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,0), 1, navy),
    ]))
    story.append(sig_table)
    story.append(PageBreak())

    # ── Section 2.1: Standard Qualifications ──
    quals = data.get("standard_qualifications", [])
    if quals:
        story.append(Paragraph("2.1 Standard Qualifications", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=border_color, spaceAfter=8))
        for i, q in enumerate(quals, 1):
            story.append(Paragraph(f"{i}. {q}", body_style))
            story.append(Spacer(1, 3))
        story.append(Spacer(1, 12))

    # ── Section 2.2: Exclusions (full, categorized) ──
    if excl:
        story.append(Paragraph("2.2 Exclusions", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=border_color, spaceAfter=8))
        num = 1
        for cat_name, items in excl.items():
            story.append(Paragraph(f"<b>{cat_name}</b>", h2_style))
            for item in items:
                story.append(Paragraph(f"{num}. {item}", body_style))
                num += 1
            story.append(Spacer(1, 4))
        story.append(PageBreak())

    # ── Section 3.1: Conditions of Contract ──
    conds = data.get("conditions_of_contract", [])
    if conds:
        story.append(Paragraph("3.1 Conditions of Contract", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=border_color, spaceAfter=8))
        for i, c in enumerate(conds, 1):
            text = c.replace("{{valid_days}}", str(po.get("valid_days", 30)))
            story.append(Paragraph(f"{i}. {text}", body_style))
            story.append(Spacer(1, 3))
        story.append(Spacer(1, 12))

    # ── Section 3.2: Terms of Contract ──
    terms = data.get("terms_of_contract", [])
    if terms:
        story.append(Paragraph("3.2 Terms of Contract", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=border_color, spaceAfter=8))
        for i, t in enumerate(terms, 1):
            story.append(Paragraph(f"{i}. {t}", body_style))
            story.append(Spacer(1, 3))

    # ── Footer ──
    def add_footer(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(HexColor("#94A3B8"))
        canvas_obj.drawString(0.75*inch, 0.5*inch,
            f"Titan Carports LLC — Proposal {po.get('quote_number', job_code)}")
        canvas_obj.drawRightString(7.75*inch, 0.5*inch,
            f"Page {doc_obj.page}")
        canvas_obj.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    return buf.getvalue()


# ─────────────────────────────────────────────
# AISC QC MODULE HANDLERS
# ─────────────────────────────────────────────

class QCInspectionTypesHandler(BaseHandler):
    """GET /api/qc/types — Return AISC inspection type definitions."""
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "types": AISC_INSPECTION_TYPES}))


class QCDataHandler(BaseHandler):
    """GET/POST /api/qc/data — Load or save QC data for a project."""
    def get(self):
        job_code = self.get_query_argument("job_code", "")
        if not job_code:
            self.write(json_encode({"ok": False, "error": "job_code required"}))
            return
        data = load_project_qc(job_code)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "data": data}))

    def post(self):
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "")
        data = body.get("data", {})
        if not job_code:
            self.write(json_encode({"ok": False, "error": "job_code required"}))
            return
        save_project_qc(job_code, data)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True}))


class QCInspectionCreateHandler(BaseHandler):
    """POST /api/qc/inspection/create — Create a new inspection record."""
    required_roles = ["admin", "estimator", "shop"]
    def post(self):
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "")
        insp_type = body.get("type", "")
        if not job_code or not insp_type:
            self.write(json_encode({"ok": False, "error": "job_code and type required"}))
            return
        if insp_type not in AISC_INSPECTION_TYPES:
            self.write(json_encode({"ok": False, "error": f"Unknown inspection type: {insp_type}"}))
            return

        qc = load_project_qc(job_code)
        now = datetime.datetime.now()
        inspection = {
            "id": "INS-" + now.strftime("%Y%m%d%H%M%S") + "-" + secrets.token_hex(3).upper(),
            "type": insp_type,
            "type_label": AISC_INSPECTION_TYPES[insp_type]["label"],
            "standard": AISC_INSPECTION_TYPES[insp_type]["standard"],
            "status": "in_progress",  # in_progress, passed, failed, incomplete
            "inspector": body.get("inspector", self.get_current_user() or ""),
            "location": body.get("location", ""),
            "member_marks": body.get("member_marks", []),
            "items": {},  # checklist item responses
            "notes": body.get("notes", ""),
            "photos": [],
            "created_at": now.isoformat(),
            "completed_at": None,
        }
        qc["inspections"].append(inspection)
        save_project_qc(job_code, qc)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "inspection": inspection}))


class QCInspectionUpdateHandler(BaseHandler):
    """POST /api/qc/inspection/update — Update an inspection record (checklist items, status, notes)."""
    required_roles = ["admin", "estimator", "shop"]
    def post(self):
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "")
        insp_id = body.get("inspection_id", "")
        qc = load_project_qc(job_code)
        found = False
        for i, insp in enumerate(qc["inspections"]):
            if insp["id"] == insp_id:
                for k in ["items", "notes", "status", "location", "member_marks", "photos"]:
                    if k in body:
                        qc["inspections"][i][k] = body[k]
                if body.get("status") in ["passed", "failed"]:
                    qc["inspections"][i]["completed_at"] = datetime.datetime.now().isoformat()
                found = True
                break
        if not found:
            self.write(json_encode({"ok": False, "error": "Inspection not found"}))
            return
        save_project_qc(job_code, qc)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True}))


class NCRCreateHandler(BaseHandler):
    """POST /api/qc/ncr/create — Create a Non-Conformance Report."""
    required_roles = ["admin", "estimator", "shop"]
    def post(self):
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "")
        if not job_code:
            self.write(json_encode({"ok": False, "error": "job_code required"}))
            return

        qc = load_project_qc(job_code)
        now = datetime.datetime.now()
        ncr_num = len(qc["ncrs"]) + 1
        ncr = {
            "id": f"NCR-{job_code}-{ncr_num:03d}",
            "number": ncr_num,
            "severity": body.get("severity", "minor"),  # minor, major, critical
            "status": "open",
            "title": body.get("title", ""),
            "description": body.get("description", ""),
            "member_marks": body.get("member_marks", []),
            "inspection_id": body.get("inspection_id", ""),
            "root_cause": "",
            "corrective_action": "",
            "preventive_action": "",
            "disposition": "",  # rework, accept-as-is, reject, repair
            "reported_by": body.get("reported_by", self.get_current_user() or ""),
            "assigned_to": body.get("assigned_to", ""),
            "photos": [],
            "created_at": now.isoformat(),
            "closed_at": None,
            "history": [
                {"action": "created", "by": self.get_current_user() or "", "at": now.isoformat()}
            ],
        }
        qc["ncrs"].append(ncr)
        save_project_qc(job_code, qc)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "ncr": ncr}))


class NCRUpdateHandler(BaseHandler):
    """POST /api/qc/ncr/update — Update an NCR (status, corrective action, disposition, etc.)."""
    required_roles = ["admin", "estimator", "shop"]
    def post(self):
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "")
        ncr_id = body.get("ncr_id", "")
        qc = load_project_qc(job_code)
        found = False
        for i, ncr in enumerate(qc["ncrs"]):
            if ncr["id"] == ncr_id:
                for k in ["severity", "status", "title", "description", "root_cause",
                           "corrective_action", "preventive_action", "disposition",
                           "assigned_to", "member_marks", "photos"]:
                    if k in body:
                        qc["ncrs"][i][k] = body[k]
                if body.get("status") == "closed":
                    qc["ncrs"][i]["closed_at"] = datetime.datetime.now().isoformat()
                qc["ncrs"][i]["history"].append({
                    "action": f"updated ({', '.join(k for k in body if k not in ['job_code','ncr_id'])})",
                    "by": self.get_current_user() or "",
                    "at": datetime.datetime.now().isoformat(),
                })
                found = True
                break
        if not found:
            self.write(json_encode({"ok": False, "error": "NCR not found"}))
            return
        save_project_qc(job_code, qc)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True}))


# ─────────────────────────────────────────────
# MATERIAL TRACEABILITY HANDLERS
# ─────────────────────────────────────────────

class TraceabilityIndexHandler(BaseHandler):
    """GET /api/traceability — Get full traceability index (all heat numbers)."""
    def get(self):
        q = self.get_query_argument("q", "").strip().lower()
        idx = load_traceability_index()
        if q:
            filtered = {}
            for hn, data in idx["heat_numbers"].items():
                searchable = " ".join([
                    hn.lower(),
                    data.get("material_spec", "").lower(),
                    data.get("mill_name", "").lower(),
                    " ".join(c.get("coil_tag", "").lower() for c in data.get("coils", [])),
                ]).lower()
                if q in searchable:
                    filtered[hn] = data
            idx["heat_numbers"] = filtered
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "index": idx}))


class TraceabilityRegisterHandler(BaseHandler):
    """POST /api/traceability/register — Register a heat number with a coil."""
    required_roles = ["admin", "estimator", "shop"]
    def post(self):
        body = json_decode(self.request.body)
        heat_number = body.get("heat_number", "").strip()
        coil_tag = body.get("coil_tag", "").strip()
        if not heat_number or not coil_tag:
            self.write(json_encode({"ok": False, "error": "heat_number and coil_tag required"}))
            return
        result = register_heat_number(
            heat_number, coil_tag,
            material_spec=body.get("material_spec", ""),
            mill_name=body.get("mill_name", ""),
            mtr_path=body.get("mtr_path", ""),
        )
        # Also update the coil in inventory with the heat number
        try:
            inv = load_inventory()
            for c in inv:
                if c.get("coil_tag", "") == coil_tag:
                    c["heat_number"] = heat_number
                    c["material_spec"] = body.get("material_spec", c.get("material_spec", ""))
                    c["mill_name"] = body.get("mill_name", c.get("mill_name", ""))
                    break
            save_inventory(inv)
        except Exception:
            pass
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "heat": result}))


class TraceabilityAssignHandler(BaseHandler):
    """POST /api/traceability/assign — Assign a member to a heat number."""
    required_roles = ["admin", "estimator", "shop"]
    def post(self):
        body = json_decode(self.request.body)
        heat_number = body.get("heat_number", "")
        job_code = body.get("job_code", "")
        member_mark = body.get("member_mark", "")
        if not heat_number or not job_code or not member_mark:
            self.write(json_encode({"ok": False, "error": "heat_number, job_code, and member_mark required"}))
            return
        assign_member_to_heat(heat_number, job_code, member_mark,
                              description=body.get("description", ""))
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True}))


class TraceabilityReportHandler(BaseHandler):
    """GET /api/traceability/report — Generate a traceability report for a project or heat number."""
    def get(self):
        job_code = self.get_query_argument("job_code", "")
        heat_number = self.get_query_argument("heat_number", "")
        idx = load_traceability_index()

        if heat_number:
            # Report for a specific heat number
            data = idx["heat_numbers"].get(heat_number, {})
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "report_type": "heat_number",
                "heat_number": heat_number,
                "data": data,
            }))
        elif job_code:
            # Report for a project — find all heat numbers used
            qc = load_project_qc(job_code)
            # Also scan the traceability index for members in this project
            project_heats = {}
            for hn, data in idx["heat_numbers"].items():
                for member in data.get("members", []):
                    if member.get("job_code") == job_code:
                        if hn not in project_heats:
                            project_heats[hn] = {
                                "material_spec": data.get("material_spec", ""),
                                "mill_name": data.get("mill_name", ""),
                                "coils": data.get("coils", []),
                                "members": [],
                            }
                        project_heats[hn]["members"].append(member)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "report_type": "project",
                "job_code": job_code,
                "heat_numbers": project_heats,
                "qc_traceability": qc.get("traceability", []),
            }))
        else:
            self.write(json_encode({"ok": False, "error": "Provide job_code or heat_number"}))


# ─────────────────────────────────────────────
# QA / QC HUB & DOCUMENTATION HANDLERS
# ─────────────────────────────────────────────

class QAHubHandler(BaseHandler):
    """GET /qa — QA/QC Hub landing page."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        from templates.qa_hub import QA_HUB_HTML
        self.render_with_nav(QA_HUB_HTML, active_page="qa")


class QAStatsHandler(BaseHandler):
    """GET /api/qa/stats — Aggregated QA statistics for the hub dashboard."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            from shop_drawings.qa_system import get_qa_stats
            stats = get_qa_stats(SHOP_DRAWINGS_DIR)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(stats))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class WPSLibraryHandler(BaseHandler):
    """GET /api/qa/wps — List all WPS. POST to save/update a WPS."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            from shop_drawings.qa_system import get_wps_library
            sd_dir = SHOP_DRAWINGS_DIR
            wps = get_wps_library(sd_dir)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "wps": wps}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))

    def post(self):
        try:
            from shop_drawings.qa_system import save_wps
            sd_dir = SHOP_DRAWINGS_DIR
            body = json_decode(self.request.body)
            wps_id = body.get("wps_id", "")
            if not wps_id:
                self.write(json_encode({"ok": False, "error": "Missing wps_id"}))
                return
            save_wps(sd_dir, wps_id, body)
            self.write(json_encode({"ok": True, "saved": wps_id}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class WPSPageHandler(BaseHandler):
    """GET /qa/wps — WPS Library page."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        # Serve a simple page that loads WPS data via API
        html = """<div style="padding:24px;max-width:1100px;">
        <h1 style="font-size:24px;font-weight:800;color:#FFF;margin-bottom:8px;">WPS Library</h1>
        <p style="color:#94A3B8;font-size:14px;margin-bottom:24px;">
          Welding Procedure Specifications per AWS D1.1. Each WPS defines the qualified parameters
          for a specific joint type used in production.
        </p>
        <div id="wpsCards" style="display:grid;grid-template-columns:1fr;gap:16px;"></div>
        </div>
        <script>
        fetch('/api/qa/wps').then(r=>r.json()).then(function(d){
          if(!d.ok) return;
          var html='';
          Object.values(d.wps).forEach(function(w){
            html+='<div style="background:#111827;border:1px solid #1E293B;border-radius:12px;padding:24px;">'
              +'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">'
              +'<h3 style="font-size:18px;font-weight:700;color:#C89A2E;">'+w.wps_id+' — '+w.title+'</h3>'
              +'<span style="padding:4px 12px;border-radius:12px;font-size:11px;font-weight:600;'
              +(w.status==='active'?'background:#14532D;color:#10B981':'background:#7F1D1D;color:#DC2626')
              +'">'+w.status.toUpperCase()+'</span></div>'
              +'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;font-size:13px;">';
            var fields=[
              ['Standard',w.standard],['Process',w.process],['Joint Type',w.joint_type],
              ['Filler Metal',w.filler_metal],['Shielding Gas',w.shielding_gas],['Base Metal',w.base_metal],
              ['Thickness',w.thickness_range],['Position',w.position],['Preheat',w.preheat],
              ['Voltage',w.voltage],['Amperage',w.amperage],['Wire Speed',w.wire_speed],
              ['Travel Speed',w.travel_speed],['Weld Size',w.weld_size],['Pattern',w.stitch_pattern],
            ];
            fields.forEach(function(f){
              html+='<div style="background:#0F172A;padding:10px 12px;border-radius:8px;">'
                +'<div style="font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:0.5px;">'+f[0]+'</div>'
                +'<div style="color:#E2E8F0;font-weight:600;margin-top:2px;">'+f[1]+'</div></div>';
            });
            html+='</div>';
            html+='<div style="margin-top:12px;padding:12px;background:#0F172A;border-radius:8px;font-size:13px;">'
              +'<strong style="color:#64748B;">Acceptance: </strong><span style="color:#CBD5E1;">'+w.acceptance_criteria+'</span></div>';
            if(w.notes) html+='<div style="margin-top:8px;font-size:12px;color:#94A3B8;font-style:italic;">'+w.notes+'</div>';
            html+='<div style="margin-top:12px;font-size:11px;color:#475569;">PQR: '+w.pqr_ref+' | Approved: '+w.approved_by+' ('+w.approved_date+')</div>';
            html+='</div>';
          });
          document.getElementById('wpsCards').innerHTML=html;
        });
        </script>"""
        self.render_with_nav(html, active_page="wps")


class WelderCertsPageHandler(BaseHandler):
    """GET /qa/welder-certs — Welder Certifications page."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        html = """<div style="padding:24px;max-width:1100px;">
        <h1 style="font-size:24px;font-weight:800;color:#FFF;margin-bottom:8px;">Welder Certifications</h1>
        <p style="color:#94A3B8;font-size:14px;margin-bottom:16px;">
          Welder qualification records per AWS D1.1 §4.19. Tracks test dates, qualified positions,
          welding process, expiration, and 6-month continuity.
        </p>
        <div style="margin-bottom:16px;">
          <button onclick="showAddForm()" style="padding:10px 20px;background:#1E40AF;color:#FFF;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;">+ Add Welder</button>
        </div>
        <div id="welderList"></div>
        <div id="addForm" style="display:none;background:#111827;border:1px solid #1E293B;border-radius:12px;padding:24px;margin-bottom:16px;">
          <h3 style="color:#FFF;margin-bottom:12px;">Add Welder Certification</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div><label style="font-size:12px;color:#64748B;">Welder Name</label><input id="fName" style="width:100%;padding:8px;background:#0F172A;border:1px solid #334155;border-radius:6px;color:#FFF;"></div>
            <div><label style="font-size:12px;color:#64748B;">Employee ID</label><input id="fEmpId" style="width:100%;padding:8px;background:#0F172A;border:1px solid #334155;border-radius:6px;color:#FFF;"></div>
            <div><label style="font-size:12px;color:#64748B;">Process</label><select id="fProcess" style="width:100%;padding:8px;background:#0F172A;border:1px solid #334155;border-radius:6px;color:#FFF;">
              <option value="GMAW">GMAW (MIG)</option><option value="FCAW">FCAW (Flux Core)</option><option value="SMAW">SMAW (Stick)</option></select></div>
            <div><label style="font-size:12px;color:#64748B;">Positions Qualified</label><input id="fPositions" placeholder="1G, 2G, 3G" style="width:100%;padding:8px;background:#0F172A;border:1px solid #334155;border-radius:6px;color:#FFF;"></div>
            <div><label style="font-size:12px;color:#64748B;">Test Date</label><input id="fTestDate" type="date" style="width:100%;padding:8px;background:#0F172A;border:1px solid #334155;border-radius:6px;color:#FFF;"></div>
            <div><label style="font-size:12px;color:#64748B;">Expiration Date</label><input id="fExpDate" type="date" style="width:100%;padding:8px;background:#0F172A;border:1px solid #334155;border-radius:6px;color:#FFF;"></div>
          </div>
          <div style="margin-top:12px;display:flex;gap:8px;">
            <button onclick="saveWelder()" style="padding:8px 20px;background:#10B981;color:#FFF;border:none;border-radius:6px;font-weight:600;cursor:pointer;">Save</button>
            <button onclick="document.getElementById('addForm').style.display='none'" style="padding:8px 20px;background:#334155;color:#CBD5E1;border:none;border-radius:6px;cursor:pointer;">Cancel</button>
          </div>
        </div>
        </div>
        <script>
        function showAddForm(){ document.getElementById('addForm').style.display='block'; }
        function saveWelder(){
          var cert={welder_name:document.getElementById('fName').value,employee_id:document.getElementById('fEmpId').value,
            process:document.getElementById('fProcess').value,positions:document.getElementById('fPositions').value,
            test_date:document.getElementById('fTestDate').value,expiration_date:document.getElementById('fExpDate').value,status:'active'};
          fetch('/api/qa/welder-certs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cert)})
            .then(r=>r.json()).then(function(d){ if(d.ok){ loadWelders(); document.getElementById('addForm').style.display='none'; }});
        }
        function loadWelders(){
          fetch('/api/qa/welder-certs').then(r=>r.json()).then(function(d){
            if(!d.ok) return;
            var html='';
            d.welders.forEach(function(w){
              var expColor='#10B981'; var expText='Valid';
              if(w.days_left!==undefined && w.days_left<=0){ expColor='#DC2626'; expText='EXPIRED'; }
              else if(w.days_left!==undefined && w.days_left<=30){ expColor='#F59E0B'; expText='Expiring'; }
              html+='<div style="background:#111827;border:1px solid #1E293B;border-radius:10px;padding:16px;margin-bottom:10px;display:flex;align-items:center;gap:16px;">'
                +'<div style="width:48px;height:48px;border-radius:10px;background:#1E3A5F;display:flex;align-items:center;justify-content:center;font-size:20px;">&#128119;</div>'
                +'<div style="flex:1;"><div style="font-size:16px;font-weight:700;color:#FFF;">'+w.welder_name+'</div>'
                +'<div style="font-size:12px;color:#94A3B8;">'+w.process+' | Positions: '+w.positions+' | ID: '+(w.employee_id||'—')+'</div></div>'
                +'<div style="text-align:right;"><div style="font-size:12px;color:#64748B;">Expires</div>'
                +'<div style="font-size:14px;font-weight:600;color:'+expColor+';">'+w.expiration_date+'</div></div>'
                +'</div>';
            });
            document.getElementById('welderList').innerHTML=html||'<div style="color:#475569;padding:20px;text-align:center;">No welder certifications yet. Click + Add Welder to get started.</div>';
          });
        }
        loadWelders();
        </script>"""
        self.render_with_nav(html, active_page="weldercerts")


class WelderCertsAPIHandler(BaseHandler):
    """GET/POST /api/qa/welder-certs — CRUD for welder certifications."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            from shop_drawings.qa_system import get_welder_certs, check_welder_expirations
            sd_dir = SHOP_DRAWINGS_DIR
            welders = get_welder_certs(sd_dir)
            alerts = {a.get("cert_id"): a for a in check_welder_expirations(sd_dir)}
            for w in welders:
                if w.get("cert_id") in alerts:
                    w["days_left"] = alerts[w["cert_id"]].get("days_left")
                    w["alert"] = alerts[w["cert_id"]].get("alert")
            self.write(json_encode({"ok": True, "welders": welders}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))

    def post(self):
        try:
            from shop_drawings.qa_system import save_welder_cert
            sd_dir = SHOP_DRAWINGS_DIR
            body = json_decode(self.request.body)
            cert = save_welder_cert(sd_dir, body)
            self.write(json_encode({"ok": True, "cert": cert}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ProceduresPageHandler(BaseHandler):
    """GET /qa/procedures — Procedures & Quality Manual page."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        html = """<div style="padding:24px;max-width:1100px;">
        <h1 style="font-size:24px;font-weight:800;color:#FFF;margin-bottom:8px;">Procedures & Quality Manual</h1>
        <p style="color:#94A3B8;font-size:14px;margin-bottom:24px;">
          Standard Operating Procedures (SOPs) covering all fabrication, inspection, and quality management processes.
          Required by AISC Chapter M and the company Quality Manual.
        </p>
        <div id="procList"></div>
        </div>
        <script>
        fetch('/api/qa/procedures').then(r=>r.json()).then(function(d){
          if(!d.ok) return;
          var cats={quality_manual:'Quality Management',inspection:'Inspection',welding:'Welding',fabrication:'Fabrication',calibration:'Calibration'};
          var groups={};
          d.procedures.forEach(function(p){
            var c=p.category||'other';
            if(!groups[c]) groups[c]=[];
            groups[c].push(p);
          });
          var html='';
          Object.keys(cats).forEach(function(k){
            var procs=groups[k]||[];
            if(!procs.length) return;
            html+='<div style="margin-bottom:24px;">'
              +'<h3 style="font-size:14px;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">'+cats[k]+'</h3>';
            procs.forEach(function(p){
              html+='<div style="background:#111827;border:1px solid #1E293B;border-radius:10px;padding:16px;margin-bottom:8px;">'
                +'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                +'<div><div style="font-size:15px;font-weight:700;color:#FFF;">'+p.proc_id+' — '+p.title+'</div>'
                +'<div style="font-size:13px;color:#94A3B8;margin-top:4px;line-height:1.5;">'+p.description+'</div></div>'
                +'<div style="text-align:right;flex-shrink:0;margin-left:16px;">'
                +'<div style="padding:3px 10px;background:#14532D;color:#10B981;border-radius:10px;font-size:11px;font-weight:600;">Rev '+p.revision+'</div>'
                +'<div style="font-size:11px;color:#475569;margin-top:4px;">'+p.standard_ref+'</div></div></div></div>';
            });
            html+='</div>';
          });
          document.getElementById('procList').innerHTML=html;
        });
        </script>"""
        self.render_with_nav(html, active_page="procedures")


class ProceduresAPIHandler(BaseHandler):
    """GET/POST /api/qa/procedures — CRUD for procedures."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            from shop_drawings.qa_system import get_procedures
            sd_dir = SHOP_DRAWINGS_DIR
            procs = get_procedures(sd_dir)
            self.write(json_encode({"ok": True, "procedures": procs}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))

    def post(self):
        try:
            from shop_drawings.qa_system import save_procedure
            sd_dir = SHOP_DRAWINGS_DIR
            body = json_decode(self.request.body)
            proc = save_procedure(sd_dir, body)
            self.write(json_encode({"ok": True, "procedure": proc}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class CalibrationPageHandler(BaseHandler):
    """GET /qa/calibration — Calibration Log page."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        html = """<div style="padding:24px;max-width:1100px;">
        <h1 style="font-size:24px;font-weight:800;color:#FFF;margin-bottom:8px;">Calibration Log</h1>
        <p style="color:#94A3B8;font-size:14px;margin-bottom:16px;">
          Equipment calibration records per AISC QM §7.6. Tracks all measuring and testing tools,
          calibration dates, due dates, and certificates. Tools out of calibration cannot be used for QC inspections.
        </p>
        <div style="margin-bottom:16px;">
          <button onclick="document.getElementById('calForm').style.display='block'" style="padding:10px 20px;background:#1E40AF;color:#FFF;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;">+ Add Tool</button>
        </div>
        <div id="calForm" style="display:none;background:#111827;border:1px solid #1E293B;border-radius:12px;padding:24px;margin-bottom:16px;">
          <h3 style="color:#FFF;margin-bottom:12px;">Add Calibration Record</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div><label style="font-size:12px;color:#64748B;">Tool Name</label><input id="cName" placeholder="e.g. Fillet Gauge Set #1" style="width:100%;padding:8px;background:#0F172A;border:1px solid #334155;border-radius:6px;color:#FFF;"></div>
            <div><label style="font-size:12px;color:#64748B;">Serial Number</label><input id="cSerial" style="width:100%;padding:8px;background:#0F172A;border:1px solid #334155;border-radius:6px;color:#FFF;"></div>
            <div><label style="font-size:12px;color:#64748B;">Last Cal Date</label><input id="cLastDate" type="date" style="width:100%;padding:8px;background:#0F172A;border:1px solid #334155;border-radius:6px;color:#FFF;"></div>
            <div><label style="font-size:12px;color:#64748B;">Next Cal Due</label><input id="cNextDate" type="date" style="width:100%;padding:8px;background:#0F172A;border:1px solid #334155;border-radius:6px;color:#FFF;"></div>
          </div>
          <div style="margin-top:12px;display:flex;gap:8px;">
            <button onclick="saveCal()" style="padding:8px 20px;background:#10B981;color:#FFF;border:none;border-radius:6px;font-weight:600;cursor:pointer;">Save</button>
            <button onclick="document.getElementById('calForm').style.display='none'" style="padding:8px 20px;background:#334155;color:#CBD5E1;border:none;border-radius:6px;cursor:pointer;">Cancel</button>
          </div>
        </div>
        <div id="calList"></div>
        </div>
        <script>
        function saveCal(){
          var rec={tool_name:document.getElementById('cName').value,serial_number:document.getElementById('cSerial').value,
            last_cal_date:document.getElementById('cLastDate').value,next_cal_date:document.getElementById('cNextDate').value,status:'active'};
          fetch('/api/qa/calibration',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(rec)})
            .then(r=>r.json()).then(function(d){ if(d.ok){ loadCal(); document.getElementById('calForm').style.display='none'; }});
        }
        function loadCal(){
          fetch('/api/qa/calibration').then(r=>r.json()).then(function(d){
            if(!d.ok) return;
            var html='';
            d.tools.forEach(function(t){
              var color='#10B981', label='In Cal';
              if(t.alert==='OVERDUE'){color='#DC2626';label='OVERDUE';}
              else if(t.alert==='DUE_SOON'){color='#F59E0B';label='Due Soon';}
              html+='<div style="background:#111827;border:1px solid #1E293B;border-radius:10px;padding:16px;margin-bottom:8px;display:flex;align-items:center;gap:16px;">'
                +'<div style="width:44px;height:44px;border-radius:10px;background:#3B0764;display:flex;align-items:center;justify-content:center;font-size:18px;">&#128295;</div>'
                +'<div style="flex:1;"><div style="font-size:15px;font-weight:700;color:#FFF;">'+t.tool_name+'</div>'
                +'<div style="font-size:12px;color:#94A3B8;">S/N: '+(t.serial_number||'—')+' | Last Cal: '+(t.last_cal_date||'—')+'</div></div>'
                +'<div style="text-align:right;"><div style="font-size:11px;color:#64748B;">Next Cal</div>'
                +'<div style="font-size:14px;font-weight:600;color:'+color+';">'+(t.next_cal_date||'—')+'</div>'
                +'<div style="font-size:11px;font-weight:600;color:'+color+';">'+label+'</div></div></div>';
            });
            document.getElementById('calList').innerHTML=html||'<div style="color:#475569;padding:20px;text-align:center;">No calibration records yet. Click + Add Tool to get started.</div>';
          });
        }
        loadCal();
        </script>"""
        self.render_with_nav(html, active_page="calibration")


class CalibrationAPIHandler(BaseHandler):
    """GET/POST /api/qa/calibration — CRUD for calibration records."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            from shop_drawings.qa_system import get_calibration_log, check_calibration_due
            sd_dir = SHOP_DRAWINGS_DIR
            tools = get_calibration_log(sd_dir)
            alerts = {a.get("tool_id"): a for a in check_calibration_due(sd_dir)}
            for t in tools:
                if t.get("tool_id") in alerts:
                    t["alert"] = alerts[t["tool_id"]].get("alert")
                    t["days_left"] = alerts[t["tool_id"]].get("days_left")
            self.write(json_encode({"ok": True, "tools": tools}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))

    def post(self):
        try:
            from shop_drawings.qa_system import save_calibration_record
            sd_dir = SHOP_DRAWINGS_DIR
            body = json_decode(self.request.body)
            rec = save_calibration_record(sd_dir, body)
            self.write(json_encode({"ok": True, "record": rec}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class NCRLogPageHandler(BaseHandler):
    """GET /qa/ncr-log — Global NCR log across all projects."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        html = """<div style="padding:24px;max-width:1100px;">
        <h1 style="font-size:24px;font-weight:800;color:#FFF;margin-bottom:8px;">NCR Log</h1>
        <p style="color:#94A3B8;font-size:14px;margin-bottom:24px;">
          Non-Conformance Reports across all projects. Tracks quality deviations, root cause analysis,
          corrective actions, and closure. Required for AISC audit trail (QM §8.3).
        </p>
        <div id="ncrList"><div style="color:#475569;padding:40px;text-align:center;">Loading NCRs...</div></div>
        </div>
        <script>
        // Load NCRs from all project QC files
        fetch('/api/qa/ncr-log').then(r=>r.json()).then(function(d){
          if(!d.ok){document.getElementById('ncrList').innerHTML='<div style="color:#DC2626;">Error loading NCRs</div>';return;}
          var html='';
          var sevColors={critical:'#DC2626',major:'#F59E0B',minor:'#3B82F6'};
          var statColors={open:'#DC2626',under_review:'#F59E0B',corrective_action:'#3B82F6',closed:'#10B981',voided:'#475569'};
          d.ncrs.forEach(function(n){
            var sc=sevColors[n.severity]||'#64748B';
            var stc=statColors[n.status]||'#64748B';
            html+='<div style="background:#111827;border:1px solid #1E293B;border-left:3px solid '+sc+';border-radius:0 10px 10px 0;padding:16px;margin-bottom:8px;">'
              +'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
              +'<div><div style="font-size:15px;font-weight:700;color:#FFF;">'+(n.ncr_id||'—')+' — '+(n.title||'Untitled')+'</div>'
              +'<div style="font-size:12px;color:#94A3B8;margin-top:4px;">Job: '+(n.job_code||'—')+' | Reported: '+(n.created_at||'—').slice(0,10)+'</div></div>'
              +'<div style="display:flex;gap:6px;">'
              +'<span style="padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600;background:'+sc+'22;color:'+sc+';">'+(n.severity||'—').toUpperCase()+'</span>'
              +'<span style="padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600;background:'+stc+'22;color:'+stc+';">'+(n.status||'—').replace('_',' ').toUpperCase()+'</span>'
              +'</div></div>';
            if(n.description) html+='<div style="font-size:13px;color:#94A3B8;margin-top:8px;">'+n.description+'</div>';
            html+='</div>';
          });
          document.getElementById('ncrList').innerHTML=html||'<div style="color:#475569;padding:40px;text-align:center;">No NCRs found. That\\'s a good thing!</div>';
        });
        </script>"""
        self.render_with_nav(html, active_page="ncrlog")


class NCRLogAPIHandler(BaseHandler):
    """GET /api/qa/ncr-log — All NCRs across all projects."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            qc_dir = QC_DIR
            all_ncrs = []
            if os.path.isdir(qc_dir):
                for fname in os.listdir(qc_dir):
                    if not fname.endswith(".json"):
                        continue
                    job = fname.replace(".json", "")
                    with open(os.path.join(qc_dir, fname)) as f:
                        data = json.load(f)
                    for ncr in data.get("ncrs", []):
                        ncr["job_code"] = job
                        all_ncrs.append(ncr)
            all_ncrs.sort(key=lambda n: n.get("created_at", ""), reverse=True)
            self.write(json_encode({"ok": True, "ncrs": all_ncrs}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class QCPageHandler(BaseHandler):
    """GET /qc/{job_code} — QC Dashboard page for a project."""
    def get(self, job_code):
        html = QC_PAGE_HTML.replace("{{JOB_CODE}}", job_code)
        html = html.replace("{{USER_ROLE}}", self.get_user_role() or "viewer")
        html = html.replace("{{USER_NAME}}", self.get_current_user() or "")
        self.render_with_nav(html, active_page="qc", job_code=job_code)


# ─────────────────────────────────────────────
# SHOP DRAWING SYSTEM
# ─────────────────────────────────────────────

# SHOP_DRAWINGS_DIR is defined near the top of this file using DATA_DIR

try:
    from shop_drawings.config import ShopDrawingConfig
    from shop_drawings.master import generate_all_shop_drawings
    from shop_drawings.work_orders import (
        WorkOrder, WorkOrderItem, STATUS_QUEUED, STATUS_APPROVED,
        STATUS_STICKERS_PRINTED, STATUS_IN_PROGRESS, STATUS_COMPLETE,
        STATUS_ON_HOLD, STATUS_FLOW, STATUS_LABELS, VALID_STATUSES,
        create_work_order, save_work_order, load_work_order,
        list_work_orders, list_all_work_orders, load_all_active_items,
        find_work_order_by_item,
        qr_scan_start, qr_scan_finish,
    )
    from shop_drawings.wo_stickers import (
        generate_wo_sticker_pdf, generate_wo_sticker_zpl,
        generate_wo_sticker_csv,
    )
    HAS_SHOP_DRAWINGS = True
except Exception:
    HAS_SHOP_DRAWINGS = False


def _shop_drawing_project_dir(job_code):
    """Get or create the shop drawing directory for a project."""
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
    d = os.path.join(SHOP_DRAWINGS_DIR, safe)
    os.makedirs(d, exist_ok=True)
    return d


def _load_shop_config(job_code):
    """Load saved ShopDrawingConfig for a project, or return None."""
    d = _shop_drawing_project_dir(job_code)
    cfg_path = os.path.join(d, "config.json")
    if os.path.isfile(cfg_path):
        with open(cfg_path) as f:
            return json.load(f)
    return None


def _save_shop_config(job_code, cfg_dict):
    """Save ShopDrawingConfig dict for a project."""
    d = _shop_drawing_project_dir(job_code)
    cfg_path = os.path.join(d, "config.json")
    with open(cfg_path, "w") as f:
        json.dump(cfg_dict, f, indent=2, default=str)


def _load_generation_log(job_code):
    """Load the most recent generation log, if any."""
    d = _shop_drawing_project_dir(job_code)
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
    log_path = os.path.join(d, "pdfs", f"{job_code}_generation_log.json")
    if os.path.isfile(log_path):
        with open(log_path) as f:
            return json.load(f)
    # Fallback: scan for any generation_log.json
    pdfs_dir = os.path.join(d, "pdfs")
    if os.path.isdir(pdfs_dir):
        for fname in os.listdir(pdfs_dir):
            if fname.endswith("_generation_log.json"):
                with open(os.path.join(pdfs_dir, fname)) as f:
                    return json.load(f)
    return None


def _load_revisions(job_code):
    """Load revision history for a project."""
    d = _shop_drawing_project_dir(job_code)
    rev_path = os.path.join(d, "revisions.json")
    if os.path.isfile(rev_path):
        with open(rev_path) as f:
            return json.load(f)
    return []


def _save_revision(job_code, rev_entry):
    """Append a revision entry."""
    d = _shop_drawing_project_dir(job_code)
    rev_path = os.path.join(d, "revisions.json")
    revisions = _load_revisions(job_code)
    revisions.insert(0, rev_entry)
    with open(rev_path, "w") as f:
        json.dump(revisions, f, indent=2, default=str)
    return revisions


def _derive_bom_config(job_code):
    """Try to load BOM data for a project and derive ShopDrawingConfig from it."""
    if not HAS_SHOP_DRAWINGS:
        return {}
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
    proj_dir = os.path.join(PROJECTS_DIR, safe)

    # Look for the latest saved version with BOM data
    versions_dir = os.path.join(proj_dir, "versions")
    if not os.path.isdir(versions_dir):
        return {}

    # Find most recent version file
    version_files = sorted(
        [f for f in os.listdir(versions_dir) if f.endswith(".json")],
        reverse=True
    )

    for vf in version_files:
        try:
            with open(os.path.join(versions_dir, vf)) as f:
                data = json.load(f)
            bom_result = data.get("bom_result") or data.get("results", {})
            if bom_result and "geometry" in bom_result:
                # Load project metadata for project_info
                meta_path = os.path.join(proj_dir, "metadata.json")
                project_info = {}
                if os.path.isfile(meta_path):
                    with open(meta_path) as mf:
                        meta = json.load(mf)
                    project_info = {
                        "job_code": job_code,
                        "project_name": meta.get("project_name", ""),
                        "customer_name": meta.get("customer_name", ""),
                        "location": meta.get("location", ""),
                    }
                cfg = ShopDrawingConfig.from_bom_data(bom_result, project_info)
                return cfg.to_dict()
        except Exception:
            continue

    return {}


class ColumnInteractiveHandler(BaseHandler):
    """GET /shop-drawings/{job_code}/column — Interactive Column Drawing."""
    def get(self, job_code):
        from templates.column_interactive import COLUMN_DRAWING_HTML

        # Load project config from saved BOM
        config_dict = _load_shop_config_for_project(job_code)
        if not config_dict:
            config_dict = {"job_code": job_code}
        config_dict.setdefault("job_code", job_code)

        # Load project metadata
        proj_dir = os.path.join(PROJECTS_DIR, job_code)
        meta_path = os.path.join(proj_dir, "metadata.json")
        if os.path.isfile(meta_path):
            with open(meta_path) as f:
                meta = json.load(f)
            config_dict.setdefault("project_name", meta.get("project_name", ""))
            config_dict.setdefault("customer_name", meta.get("customer_name", ""))

        html = COLUMN_DRAWING_HTML
        html = html.replace("{{JOB_CODE}}", job_code)
        html = html.replace("{{COLUMN_CONFIG_JSON}}", json.dumps(config_dict))
        self.set_header("Content-Type", "text/html")
        self.write(html)


class RafterInteractiveHandler(BaseHandler):
    """GET /shop-drawings/{job_code}/rafter — Interactive Rafter Drawing."""
    def get(self, job_code):
        # Placeholder — serve rafter drawing if template exists
        try:
            from templates.rafter_interactive import RAFTER_DRAWING_HTML
            config_dict = _load_shop_config_for_project(job_code)
            if not config_dict:
                config_dict = {"job_code": job_code}
            config_dict.setdefault("job_code", job_code)
            html = RAFTER_DRAWING_HTML
            html = html.replace("{{JOB_CODE}}", job_code)
            html = html.replace("{{RAFTER_CONFIG_JSON}}", json.dumps(config_dict))
            self.set_header("Content-Type", "text/html")
            self.write(html)
        except ImportError:
            self.set_status(404)
            self.write("Rafter interactive drawing not yet available")


class SaveInteractivePDFHandler(BaseHandler):
    """POST /api/shop-drawings/save-interactive-pdf — Save PDF from interactive drawing."""
    def post(self):
        job_code = self.get_argument("job_code", "")
        drawing_type = self.get_argument("drawing_type", "column")
        if not job_code:
            self.write(json_encode({"ok": False, "error": "job_code required"}))
            return
        try:
            pdf_file = self.request.files.get("pdf_file", [None])[0]
            if not pdf_file:
                self.write(json_encode({"ok": False, "error": "No PDF file"}))
                return
            # Save to project shop_drawings directory
            sd_dir = os.path.join(PROJECTS_DIR, job_code, "shop_drawings")
            os.makedirs(sd_dir, exist_ok=True)
            filename = pdf_file.get("filename", f"{job_code}_{drawing_type}_interactive.pdf")
            out_path = os.path.join(sd_dir, filename)
            with open(out_path, "wb") as f:
                f.write(pdf_file["body"])
            self.write(json_encode({"ok": True, "filename": filename, "path": out_path}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class ShopDrawingsPageHandler(BaseHandler):
    """GET /shop-drawings/{job_code} — Shop Drawing Dashboard page."""
    def get(self, job_code):
        role = self.get_user_role() or "viewer"
        display = "User"
        if AUTH_ENABLED:
            user = self.get_current_user()
            users_db = load_users()
            display = users_db.get(user, {}).get("display_name", user or "User")

        html = SHOP_DRAWINGS_HTML
        html = html.replace("{{JOB_CODE}}", job_code)
        html = html.replace("{{USER_ROLE}}", role)
        html = html.replace("{{USER_NAME}}", display)
        self.render_with_nav(html, active_page="shopdrw", job_code=job_code)


class ShopDrawingsConfigHandler(BaseHandler):
    """
    GET  /api/shop-drawings/config?job_code=XXX  — Load config + drawings + revisions
    POST /api/shop-drawings/config               — Save config
    """
    def get(self):
        try:
            job_code = self.get_query_argument("job_code", "").strip()
            if not job_code:
                self.write(json_encode({"ok": False, "error": "Missing job_code"}))
                return

            # Load saved config, or derive from BOM
            saved_config = _load_shop_config(job_code)
            bom_config = _derive_bom_config(job_code)

            if saved_config is None and bom_config:
                saved_config = dict(bom_config)
                _save_shop_config(job_code, saved_config)
            elif saved_config is None:
                # No BOM data either — return defaults
                if HAS_SHOP_DRAWINGS:
                    cfg = ShopDrawingConfig()
                    cfg.job_code = job_code
                    saved_config = cfg.to_dict()
                else:
                    saved_config = {"job_code": job_code}

            # Load generation log and file list
            gen_log = _load_generation_log(job_code)
            drawings = []
            if gen_log and "files" in gen_log:
                drawings = gen_log["files"]

            revisions = _load_revisions(job_code)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "config": saved_config,
                "bom_config": bom_config,
                "drawings": drawings,
                "revisions": revisions,
                "generation_log": gen_log,
            }))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e),
                                    "trace": traceback.format_exc()}))

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            cfg_dict = body.get("config", {})
            if not job_code:
                self.write(json_encode({"ok": False, "error": "Missing job_code"}))
                return

            cfg_dict["job_code"] = job_code
            _save_shop_config(job_code, cfg_dict)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ShopDrawingsSyncBOMHandler(BaseHandler):
    """POST /api/shop-drawings/sync-bom — Re-derive config from BOM and save.

    Body options:
      {"job_code": "...", "mode": "full"}            — Overwrite entire config with BOM values
      {"job_code": "...", "mode": "partial",
       "accept_fields": ["building_width_ft", ...]}  — Accept only specific BOM fields, keep rest
    """
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            mode = body.get("mode", "full")
            accept_fields = body.get("accept_fields", [])

            if not job_code:
                self.write(json_encode({"ok": False, "error": "Missing job_code"}))
                return

            bom_config = _derive_bom_config(job_code)
            if not bom_config:
                self.write(json_encode({"ok": False, "error": "No BOM data found"}))
                return

            if mode == "partial" and accept_fields:
                # Merge only accepted fields from BOM into current config
                current = _load_shop_config(job_code) or {}
                for field in accept_fields:
                    if field in bom_config:
                        current[field] = bom_config[field]
                _save_shop_config(job_code, current)
                final_config = current
            else:
                # Full overwrite
                _save_shop_config(job_code, bom_config)
                final_config = bom_config

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "bom_config": bom_config,
                "config": final_config,
            }))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


# Human-readable labels for config fields (used in conflict resolution UI)
_FIELD_LABELS = {
    "building_width_ft": "Building Width (ft)",
    "building_length_ft": "Building Length (ft)",
    "clear_height_ft": "Clear Height (ft)",
    "roof_pitch_deg": "Roof Pitch (deg)",
    "n_frames": "Number of Frames",
    "frame_type": "Frame Type",
    "bay_sizes": "Bay Sizes",
    "overhang_ft": "Overhang (ft)",
    "embedment_ft": "Embedment (ft)",
    "footing_depth_ft": "Footing Depth (ft)",
    "column_buffer_ft": "Column Buffer (ft)",
    "col_material_grade": "Column Material Grade",
    "col_reinforced": "Column Reinforced",
    "col_rebar_size": "Column Rebar Size",
    "raft_reinforced": "Rafter Reinforced",
    "raft_rebar_size": "Rafter Rebar Size",
    "raft_roofing_overhang_ft": "Roofing Overhang (ft)",
    "raft_purlin_type": "Purlin Type",
    "purlin_type": "Purlin Type",
    "purlin_gauge": "Purlin Gauge",
    "purlin_spacing_ft": "Purlin Spacing (ft)",
    "purlin_overhang_ft": "Purlin Overhang (ft)",
    "has_back_wall": "Back Wall",
    "has_side_walls": "Side Walls",
}


class ShopDrawingsDiffHandler(BaseHandler):
    """POST /api/shop-drawings/diff — Compare current config vs fresh BOM-derived config.

    Returns per-field diffs with labels, current values, and BOM values.
    Used by the conflict resolution popup.
    """
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            if not job_code:
                self.write(json_encode({"ok": False, "error": "Missing job_code"}))
                return

            current = _load_shop_config(job_code) or {}
            bom_config = _derive_bom_config(job_code)

            if not bom_config:
                self.write(json_encode({
                    "ok": True,
                    "has_changes": False,
                    "diffs": [],
                    "message": "No BOM data available for comparison",
                }))
                return

            # Compare only BOM-derived fields (not user-only fields like drawn_by)
            bom_comparable_fields = [
                "building_width_ft", "building_length_ft", "clear_height_ft",
                "roof_pitch_deg", "n_frames", "frame_type", "overhang_ft",
                "embedment_ft", "footing_depth_ft", "column_buffer_ft",
                "purlin_spacing_ft", "has_back_wall", "has_side_walls",
                "col_reinforced", "raft_reinforced",
            ]

            diffs = []
            for field in bom_comparable_fields:
                bom_val = bom_config.get(field)
                cur_val = current.get(field)

                if bom_val is None:
                    continue

                # Normalize for comparison
                if isinstance(bom_val, float) and isinstance(cur_val, (int, float)):
                    changed = abs(float(bom_val) - float(cur_val)) > 0.001
                elif isinstance(bom_val, bool) or isinstance(cur_val, bool):
                    changed = bool(bom_val) != bool(cur_val)
                else:
                    changed = str(bom_val) != str(cur_val)

                if changed:
                    diffs.append({
                        "field": field,
                        "label": _FIELD_LABELS.get(field, field),
                        "current_value": cur_val,
                        "bom_value": bom_val,
                    })

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "has_changes": len(diffs) > 0,
                "diffs": diffs,
                "total_changes": len(diffs),
            }))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e),
                                    "trace": traceback.format_exc()}))


class ShopDrawingsGenerateHandler(BaseHandler):
    """POST /api/shop-drawings/generate — Generate all shop drawings for a project."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        try:
            if not HAS_SHOP_DRAWINGS:
                self.write(json_encode({
                    "ok": False,
                    "error": "Shop drawing module not available"
                }))
                return

            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            cfg_dict = body.get("config", {})

            if not job_code:
                self.write(json_encode({"ok": False, "error": "Missing job_code"}))
                return

            cfg_dict["job_code"] = job_code
            _save_shop_config(job_code, cfg_dict)

            # Build ShopDrawingConfig (from_dict handles string→number coercion)
            cfg = ShopDrawingConfig.from_dict(cfg_dict)
            # Belt-and-suspenders: force all numeric fields to correct types
            cfg.ensure_numeric()

            # Determine revision
            revisions = _load_revisions(job_code)
            if not revisions:
                revision = "-"
            else:
                last_rev = revisions[0].get("revision", "-")
                if last_rev == "-":
                    revision = "A"
                elif len(last_rev) == 1 and last_rev.isalpha():
                    revision = chr(ord(last_rev) + 1) if last_rev < "Z" else "Z+"
                else:
                    revision = last_rev + "+"

            # Generate
            d = _shop_drawing_project_dir(job_code)
            output_dir = os.path.join(d, "pdfs")
            os.makedirs(output_dir, exist_ok=True)

            result = generate_all_shop_drawings(
                cfg, output_dir, revision=revision,
                include_stickers=True, include_manifest=True
            )

            # Save revision entry
            rev_entry = {
                "revision": revision,
                "generated_at": result["summary"]["timestamp"],
                "total_files": result["summary"]["total_files"],
                "total_bytes": result["summary"]["total_bytes"],
                "errors": result["summary"]["errors"],
            }
            _save_revision(job_code, rev_entry)

            # Return file list (without full paths)
            files = []
            for f in result["files"]:
                files.append({
                    "filename": f["filename"],
                    "type": f["type"],
                    "description": f["description"],
                    "size_bytes": f["size_bytes"],
                })

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "files": files,
                "summary": {
                    "total_files": result["summary"]["total_files"],
                    "total_bytes": result["summary"]["total_bytes"],
                    "total_kb": result["summary"]["total_kb"],
                    "timestamp": result["summary"]["timestamp"],
                    "revision": revision,
                },
                "revision_entry": rev_entry,
                "errors": result["errors"],
            }))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({
                "ok": False,
                "error": str(e),
                "trace": traceback.format_exc()
            }))


class ShopDrawingsFileHandler(BaseHandler):
    """GET /api/shop-drawings/file?job_code=XXX&filename=YYY — Serve a single PDF."""
    def get(self):
        try:
            job_code = self.get_query_argument("job_code", "").strip()
            filename = self.get_query_argument("filename", "").strip()
            download = self.get_query_argument("download", "0") == "1"

            if not job_code or not filename:
                self.set_status(400)
                self.write("Missing job_code or filename")
                return

            # Sanitize filename to prevent path traversal
            filename = os.path.basename(filename)
            d = _shop_drawing_project_dir(job_code)
            fpath = os.path.join(d, "pdfs", filename)

            if not os.path.isfile(fpath):
                self.set_status(404)
                self.write("File not found")
                return

            self.set_header("Content-Type", "application/pdf")
            if download:
                self.set_header("Content-Disposition",
                                f'attachment; filename="{filename}"')
            else:
                self.set_header("Content-Disposition",
                                f'inline; filename="{filename}"')

            with open(fpath, "rb") as f:
                self.write(f.read())
        except Exception as e:
            self.set_status(500)
            self.write(str(e))


class ShopDrawingsZipHandler(BaseHandler):
    """GET /api/shop-drawings/zip?job_code=XXX — Download all PDFs as a ZIP."""
    def get(self):
        import zipfile
        try:
            job_code = self.get_query_argument("job_code", "").strip()
            if not job_code:
                self.set_status(400)
                self.write("Missing job_code")
                return

            d = _shop_drawing_project_dir(job_code)
            pdfs_dir = os.path.join(d, "pdfs")

            if not os.path.isdir(pdfs_dir):
                self.set_status(404)
                self.write("No drawings found")
                return

            pdf_files = [f for f in os.listdir(pdfs_dir) if f.endswith(".pdf")]
            if not pdf_files:
                self.set_status(404)
                self.write("No PDF files found")
                return

            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname in sorted(pdf_files):
                    fpath = os.path.join(pdfs_dir, fname)
                    zf.write(fpath, fname)

            zip_bytes = buf.getvalue()
            zip_name = f"{job_code}_ShopDrawings.zip"

            self.set_header("Content-Type", "application/zip")
            self.set_header("Content-Disposition",
                            f'attachment; filename="{zip_name}"')
            self.write(zip_bytes)
        except Exception as e:
            self.set_status(500)
            self.write(str(e))


# ─────────────────────────────────────────────
# WORK ORDER HANDLERS
# ─────────────────────────────────────────────

class WorkOrderPageHandler(BaseHandler):
    """GET /work-orders/{job_code} — Work order tracking page."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self, job_code):
        from templates.work_orders import WORK_ORDERS_HTML
        html = WORK_ORDERS_HTML.replace("{{JOB_CODE}}", job_code)
        self.render_with_nav(html, active_page="workorders", job_code=job_code)


class WorkOrderCreateHandler(BaseHandler):
    """POST /api/work-orders/create — Create a new work order from shop drawings."""
    required_roles = ["admin", "estimator"]

    def post(self):
        try:
            if not HAS_SHOP_DRAWINGS:
                self.write(json_encode({"ok": False, "error": "Shop drawing module not available"}))
                return

            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            if not job_code:
                self.write(json_encode({"ok": False, "error": "Missing job_code"}))
                return

            # Get latest revision from generation history
            revisions = _load_revisions(job_code)
            revision = revisions[0].get("revision", "-") if revisions else "-"

            # Get current config for component counts
            cfg_dict = _load_shop_config(job_code) or _derive_bom_config(job_code)
            if not cfg_dict:
                self.write(json_encode({"ok": False, "error": "No config found — generate shop drawings first"}))
                return

            # Get drawing files list
            d = _shop_drawing_project_dir(job_code)
            pdfs_dir = os.path.join(d, "pdfs")
            drawing_files = []
            if os.path.isdir(pdfs_dir):
                drawing_files = [{"filename": f} for f in os.listdir(pdfs_dir) if f.endswith(".pdf")]

            created_by = body.get("created_by", self.get_current_user() or "system")

            wo = create_work_order(
                job_code=job_code,
                revision=revision,
                created_by=created_by,
                drawing_files=drawing_files,
                config_dict=cfg_dict,
            )

            save_work_order(SHOP_DRAWINGS_DIR, wo)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "work_order": wo.to_dict(),
                "summary": wo.summary(),
            }))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e), "trace": traceback.format_exc()}))


class WorkOrderListHandler(BaseHandler):
    """GET /api/work-orders/list?job_code=XXX — List all work orders for a project."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            job_code = self.get_query_argument("job_code", "").strip()
            if not job_code:
                self.write(json_encode({"ok": False, "error": "Missing job_code"}))
                return

            summaries = list_work_orders(SHOP_DRAWINGS_DIR, job_code)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "work_orders": summaries}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class WorkOrderDetailHandler(BaseHandler):
    """GET /api/work-orders/detail?job_code=XXX&wo_id=YYY — Get full work order with items."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            job_code = self.get_query_argument("job_code", "").strip()
            wo_id = self.get_query_argument("wo_id", "").strip()
            if not job_code or not wo_id:
                self.write(json_encode({"ok": False, "error": "Missing job_code or wo_id"}))
                return

            wo = load_work_order(SHOP_DRAWINGS_DIR, job_code, wo_id)
            if wo is None:
                self.set_status(404)
                self.write(json_encode({"ok": False, "error": "Work order not found"}))
                return

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "work_order": wo.to_dict(), "summary": wo.summary()}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class WorkOrderApproveHandler(BaseHandler):
    """POST /api/work-orders/approve — Approve a work order for fabrication."""
    required_roles = ["admin", "estimator"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            wo_id = body.get("wo_id", "").strip()
            if not job_code or not wo_id:
                self.write(json_encode({"ok": False, "error": "Missing job_code or wo_id"}))
                return

            wo = load_work_order(SHOP_DRAWINGS_DIR, job_code, wo_id)
            if wo is None:
                self.write(json_encode({"ok": False, "error": "Work order not found"}))
                return

            if wo.status != STATUS_QUEUED:
                self.write(json_encode({"ok": False, "error": f"Cannot approve — status is '{STATUS_LABELS.get(wo.status, wo.status)}'"}))
                return

            wo.status = STATUS_APPROVED
            wo.approved_at = datetime.datetime.now().isoformat()
            wo.approved_by = body.get("approved_by", self.get_current_user() or "system")
            save_work_order(SHOP_DRAWINGS_DIR, wo)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "work_order": wo.to_dict(), "summary": wo.summary()}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class WorkOrderStickersPrintedHandler(BaseHandler):
    """POST /api/work-orders/stickers-printed — Mark stickers as printed."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            wo_id = body.get("wo_id", "").strip()
            if not job_code or not wo_id:
                self.write(json_encode({"ok": False, "error": "Missing job_code or wo_id"}))
                return

            wo = load_work_order(SHOP_DRAWINGS_DIR, job_code, wo_id)
            if wo is None:
                self.write(json_encode({"ok": False, "error": "Work order not found"}))
                return

            if wo.status != STATUS_APPROVED:
                self.write(json_encode({"ok": False, "error": f"Cannot mark printed — status is '{STATUS_LABELS.get(wo.status, wo.status)}'"}))
                return

            wo.status = STATUS_STICKERS_PRINTED
            wo.stickers_printed_at = datetime.datetime.now().isoformat()
            save_work_order(SHOP_DRAWINGS_DIR, wo)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "work_order": wo.to_dict(), "summary": wo.summary()}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class WorkOrderHoldHandler(BaseHandler):
    """POST /api/work-orders/hold — Put a work order on hold or resume it."""
    required_roles = ["admin", "estimator"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            wo_id = body.get("wo_id", "").strip()
            action = body.get("action", "hold")  # "hold" or "resume"
            if not job_code or not wo_id:
                self.write(json_encode({"ok": False, "error": "Missing job_code or wo_id"}))
                return

            wo = load_work_order(SHOP_DRAWINGS_DIR, job_code, wo_id)
            if wo is None:
                self.write(json_encode({"ok": False, "error": "Work order not found"}))
                return

            if action == "hold":
                if wo.status == STATUS_ON_HOLD:
                    self.write(json_encode({"ok": False, "error": "Already on hold"}))
                    return
                if wo.status == STATUS_COMPLETE:
                    self.write(json_encode({"ok": False, "error": "Cannot hold a completed WO"}))
                    return
                wo.notes = f"[ON HOLD] Previous status: {wo.status}. " + wo.notes
                wo.status = STATUS_ON_HOLD
            elif action == "resume":
                if wo.status != STATUS_ON_HOLD:
                    self.write(json_encode({"ok": False, "error": "Not currently on hold"}))
                    return
                # Resume to queued (admin can re-approve)
                wo.status = STATUS_QUEUED
            else:
                self.write(json_encode({"ok": False, "error": f"Unknown action: {action}"}))
                return

            save_work_order(SHOP_DRAWINGS_DIR, wo)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "work_order": wo.to_dict(), "summary": wo.summary()}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class WorkOrderQRScanHandler(BaseHandler):
    """POST /api/work-orders/qr-scan — Process a QR code scan (start or finish)."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            item_id = body.get("item_id", "").strip()
            action = body.get("action", "").strip()  # "start" or "finish"
            scanned_by = body.get("scanned_by", self.get_current_user() or "shop")

            if not job_code or not item_id or not action:
                self.write(json_encode({"ok": False, "error": "Missing job_code, item_id, or action"}))
                return

            if action == "start":
                result = qr_scan_start(SHOP_DRAWINGS_DIR, job_code, item_id, scanned_by)
            elif action == "finish":
                result = qr_scan_finish(SHOP_DRAWINGS_DIR, job_code, item_id, scanned_by)
                # ── Record completion in gamification engine ──
                if result.get("ok"):
                    try:
                        from shop_drawings.gamification import record_completion
                        dur = result.get("duration_minutes", 0)
                        machine = result.get("machine", "")
                        comp_type = result.get("component_type", "")
                        gam = record_completion(
                            SHOP_DRAWINGS_DIR, scanned_by, dur,
                            machine=machine, component_type=comp_type
                        )
                        result["gamification"] = gam
                    except Exception:
                        pass  # Don't break the scan if gamification fails
            else:
                self.write(json_encode({"ok": False, "error": f"Unknown action: {action}. Use 'start' or 'finish'."}))
                return

            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e), "trace": traceback.format_exc()}))


class WorkOrderItemNotesHandler(BaseHandler):
    """POST /api/work-orders/item-notes — Add notes to a work order item."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            item_id = body.get("item_id", "").strip()
            notes = body.get("notes", "").strip()

            if not job_code or not item_id:
                self.write(json_encode({"ok": False, "error": "Missing job_code or item_id"}))
                return

            wo, item = find_work_order_by_item(SHOP_DRAWINGS_DIR, job_code, item_id)
            if wo is None or item is None:
                self.write(json_encode({"ok": False, "error": "Item not found"}))
                return

            item.notes = notes
            save_work_order(SHOP_DRAWINGS_DIR, wo)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "item": item.to_dict()}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class WorkOrderStickerPDFHandler(BaseHandler):
    """GET /api/work-orders/stickers/pdf?job_code=X&wo_id=Y — Generate sticker PDF."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            job_code = self.get_query_argument("job_code", "").strip()
            wo_id = self.get_query_argument("wo_id", "").strip()
            if not job_code or not wo_id:
                self.set_status(400)
                self.write("Missing job_code or wo_id")
                return

            wo = load_work_order(SHOP_DRAWINGS_DIR, job_code, wo_id)
            if wo is None:
                self.set_status(404)
                self.write("Work order not found")
                return

            # Get base URL from request
            app_base_url = f"{self.request.protocol}://{self.request.host}"

            pdf_bytes = generate_wo_sticker_pdf(
                wo.to_dict(),
                app_base_url=app_base_url,
            )

            filename = f"{wo_id}_stickers.pdf"
            self.set_header("Content-Type", "application/pdf")
            self.set_header("Content-Disposition", f'inline; filename="{filename}"')
            self.write(pdf_bytes)
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(str(e))


class WorkOrderStickerZPLHandler(BaseHandler):
    """GET /api/work-orders/stickers/zpl?job_code=X&wo_id=Y — Generate ZPL for Zebra printers."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            job_code = self.get_query_argument("job_code", "").strip()
            wo_id = self.get_query_argument("wo_id", "").strip()
            if not job_code or not wo_id:
                self.set_status(400)
                self.write("Missing job_code or wo_id")
                return

            wo = load_work_order(SHOP_DRAWINGS_DIR, job_code, wo_id)
            if wo is None:
                self.set_status(404)
                self.write("Work order not found")
                return

            app_base_url = f"{self.request.protocol}://{self.request.host}"

            zpl_str = generate_wo_sticker_zpl(
                wo.to_dict(),
                app_base_url=app_base_url,
            )

            filename = f"{wo_id}_stickers.zpl"
            self.set_header("Content-Type", "text/plain")
            self.set_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.write(zpl_str)
        except Exception as e:
            self.set_status(500)
            self.write(str(e))


class WorkOrderStickerCSVHandler(BaseHandler):
    """GET /api/work-orders/stickers/csv?job_code=X&wo_id=Y — Export sticker data as CSV."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            job_code = self.get_query_argument("job_code", "").strip()
            wo_id = self.get_query_argument("wo_id", "").strip()
            if not job_code or not wo_id:
                self.set_status(400)
                self.write("Missing job_code or wo_id")
                return

            wo = load_work_order(SHOP_DRAWINGS_DIR, job_code, wo_id)
            if wo is None:
                self.set_status(404)
                self.write("Work order not found")
                return

            app_base_url = f"{self.request.protocol}://{self.request.host}"

            csv_bytes = generate_wo_sticker_csv(
                wo.to_dict(),
                app_base_url=app_base_url,
            )

            filename = f"{wo_id}_stickers.csv"
            self.set_header("Content-Type", "text/csv")
            self.set_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.write(csv_bytes)
        except Exception as e:
            self.set_status(500)
            self.write(str(e))


class WorkOrderSingleStickerHandler(BaseHandler):
    """GET /api/work-orders/stickers/single?job_code=X&item_id=Y — Single item sticker PDF."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            job_code = self.get_query_argument("job_code", "").strip()
            item_id = self.get_query_argument("item_id", "").strip()
            if not job_code or not item_id:
                self.set_status(400)
                self.write("Missing job_code or item_id")
                return

            wo, item = find_work_order_by_item(SHOP_DRAWINGS_DIR, job_code, item_id)
            if wo is None or item is None:
                self.set_status(404)
                self.write("Item not found")
                return

            app_base_url = f"{self.request.protocol}://{self.request.host}"

            pdf_bytes = generate_wo_sticker_pdf(
                wo.to_dict(),
                items=[item.to_dict()],
                app_base_url=app_base_url,
            )

            filename = f"{item.ship_mark}_sticker.pdf"
            self.set_header("Content-Type", "application/pdf")
            self.set_header("Content-Disposition", f'inline; filename="{filename}"')
            self.write(pdf_bytes)
        except Exception as e:
            self.set_status(500)
            self.write(str(e))


# ─────────────────────────────────────────────
# SHOP FLOOR DASHBOARD HANDLERS
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# GAMIFICATION, SMART QUEUE & TV DASHBOARD
# ─────────────────────────────────────────────

class TVDashboardPageHandler(BaseHandler):
    """GET /tv-dashboard — Full-screen live production dashboard for shop floor TVs."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        from templates.tv_dashboard import TV_DASHBOARD_HTML
        self.set_header("Content-Type", "text/html")
        self.write(TV_DASHBOARD_HTML)


class GamificationLeaderboardHandler(BaseHandler):
    """GET /api/gamification/leaderboard — Worker leaderboard."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            from shop_drawings.gamification import get_leaderboard
            period = self.get_argument("period", "today")
            lb = get_leaderboard(SHOP_DRAWINGS_DIR, period)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "leaderboard": lb, "period": period}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class GamificationStatsHandler(BaseHandler):
    """GET /api/gamification/stats — Worker's own stats + badges."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            from shop_drawings.gamification import get_worker_stats
            worker = self.get_argument("worker", self.get_current_user() or "shop")
            stats = get_worker_stats(SHOP_DRAWINGS_DIR, worker)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, **stats}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class GamificationTargetsHandler(BaseHandler):
    """GET /api/gamification/targets — Daily production targets."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            from shop_drawings.gamification import get_daily_targets
            targets = get_daily_targets(SHOP_DRAWINGS_DIR)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, **targets}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class SmartQueueHandler(BaseHandler):
    """GET /api/smart-queue — Priority-sorted items for a job."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            from shop_drawings.smart_queue import prioritize_queue
            from shop_drawings.config import MACHINES

            job_code = self.get_argument("job_code", "").strip()
            due_date = self.get_argument("due_date", None)

            if not job_code:
                self.write(json_encode({"ok": False, "error": "Missing job_code"}))
                return

            wos = list_work_orders(SHOP_DRAWINGS_DIR, job_code)
            all_items = []
            for wo in wos:
                for it in (wo.items if hasattr(wo, 'items') else []):
                    d = it.to_dict() if hasattr(it, 'to_dict') else it
                    d["work_order_id"] = wo.work_order_id if hasattr(wo, 'work_order_id') else wo.get("work_order_id", "")
                    all_items.append(d)

            machine_status = {}
            for mid, mconf in MACHINES.items():
                machine_status[mid] = {"in_progress": 0, "queued": 0, "name": mconf.get("name", mid)}
            for it in all_items:
                m = it.get("machine", "")
                if m in machine_status:
                    if it.get("status") == "in_progress":
                        machine_status[m]["in_progress"] += 1
                    elif it.get("status") in ("queued", "approved", "stickers_printed"):
                        machine_status[m]["queued"] += 1

            prioritized = prioritize_queue(all_items, due_date, machine_status)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "items": prioritized, "total": len(prioritized)}))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e), "trace": traceback.format_exc()}))


class AlertsHandler(BaseHandler):
    """GET /api/alerts — Active shop floor alerts. POST to dismiss."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            from shop_drawings.smart_queue import generate_alerts
            from shop_drawings.config import MACHINES
            from shop_drawings.gamification import get_daily_targets

            wos = list_work_orders(SHOP_DRAWINGS_DIR, "*")
            all_items = []
            for wo in wos:
                for it in (wo.items if hasattr(wo, 'items') else []):
                    d = it.to_dict() if hasattr(it, 'to_dict') else it
                    all_items.append(d)

            machines = {}
            for mid, mconf in MACHINES.items():
                machines[mid] = {"in_progress": 0, "queued": 0, "name": mconf.get("name", mid)}
            for it in all_items:
                m = it.get("machine", "")
                if m in machines:
                    if it.get("status") == "in_progress":
                        machines[m]["in_progress"] += 1
                    elif it.get("status") in ("queued", "approved", "stickers_printed"):
                        machines[m]["queued"] += 1

            targets = get_daily_targets(SHOP_DRAWINGS_DIR)
            alerts = generate_alerts(
                SHOP_DRAWINGS_DIR, machines, all_items,
                targets.get("shop_target", 15), targets.get("shop_completed", 0)
            )
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "alerts": alerts}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))

    def post(self):
        try:
            from shop_drawings.smart_queue import dismiss_alert
            body = json_decode(self.request.body)
            idx = body.get("index", -1)
            ok = dismiss_alert(SHOP_DRAWINGS_DIR, idx)
            self.write(json_encode({"ok": ok}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ShopFloorPageHandler(BaseHandler):
    """GET /shop-floor — Shop floor fabrication dashboard."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        from templates.shop_floor import SHOP_FLOOR_HTML
        self.render_with_nav(SHOP_FLOOR_HTML, active_page="shopfloor")


class ShopFloorDataHandler(BaseHandler):
    """GET /api/shop-floor/data — Aggregated shop floor metrics."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            from shop_drawings.config import MACHINES

            # All work orders across all projects
            all_wos = list_all_work_orders(SHOP_DRAWINGS_DIR)
            all_items = load_all_active_items(SHOP_DRAWINGS_DIR)

            # ── Work order summaries by status ──
            status_counts = {}
            for wo in all_wos:
                s = wo.get("status", "queued")
                status_counts[s] = status_counts.get(s, 0) + 1

            # ── Active work orders (not complete) ──
            active_wos = [wo for wo in all_wos if wo.get("status") != "complete"]

            # ── Item metrics ──
            total_items = len(all_items)
            completed_items = [i for i in all_items if i.get("status") == "complete"]
            in_progress_items = [i for i in all_items if i.get("status") == "in_progress"]
            queued_items = [i for i in all_items if i.get("status") not in ("complete", "in_progress")]

            # ── Machine utilization ──
            machines = {}
            for m_id, m_info in MACHINES.items():
                machines[m_id] = {
                    "name": m_info["name"],
                    "location": m_info.get("location", ""),
                    "in_progress": 0,
                    "queued": 0,
                    "completed": 0,
                    "total_fab_minutes": 0.0,
                    "active_items": [],
                }

            for item in all_items:
                m = item.get("machine", "")
                if m not in machines:
                    continue
                if item.get("status") == "in_progress":
                    machines[m]["in_progress"] += 1
                    machines[m]["active_items"].append({
                        "item_id": item.get("item_id", ""),
                        "ship_mark": item.get("ship_mark", ""),
                        "job_code": item.get("job_code", ""),
                        "description": item.get("description", ""),
                        "started_at": item.get("started_at", ""),
                        "started_by": item.get("started_by", ""),
                    })
                elif item.get("status") == "complete":
                    machines[m]["completed"] += 1
                    machines[m]["total_fab_minutes"] += item.get("duration_minutes", 0)
                else:
                    machines[m]["queued"] += 1

            # ── Throughput (completed items with duration) ──
            total_fab_minutes = sum(i.get("duration_minutes", 0) for i in completed_items)
            avg_fab_minutes = (total_fab_minutes / len(completed_items)) if completed_items else 0

            # ── Today's activity ──
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            today_completed = [i for i in completed_items
                               if i.get("finished_at", "").startswith(today)]
            today_started = [i for i in all_items
                             if i.get("started_at", "").startswith(today)]

            # ── Recent activity feed (last 20 events) ──
            events = []
            for item in all_items:
                if item.get("started_at"):
                    events.append({
                        "type": "started",
                        "time": item["started_at"],
                        "ship_mark": item.get("ship_mark", ""),
                        "job_code": item.get("job_code", ""),
                        "machine": item.get("machine", ""),
                        "by": item.get("started_by", ""),
                    })
                if item.get("finished_at"):
                    events.append({
                        "type": "finished",
                        "time": item["finished_at"],
                        "ship_mark": item.get("ship_mark", ""),
                        "job_code": item.get("job_code", ""),
                        "machine": item.get("machine", ""),
                        "by": item.get("finished_by", ""),
                        "duration": item.get("duration_minutes", 0),
                    })

            events.sort(key=lambda x: x.get("time", ""), reverse=True)
            events = events[:20]

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "summary": {
                    "total_work_orders": len(all_wos),
                    "active_work_orders": len(active_wos),
                    "status_counts": status_counts,
                    "total_items": total_items,
                    "completed_items": len(completed_items),
                    "in_progress_items": len(in_progress_items),
                    "queued_items": len(queued_items),
                    "total_fab_minutes": round(total_fab_minutes, 1),
                    "avg_fab_minutes": round(avg_fab_minutes, 1),
                    "today_completed": len(today_completed),
                    "today_started": len(today_started),
                },
                "machines": machines,
                "active_wos": active_wos[:20],
                "events": events,
            }))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e), "trace": traceback.format_exc()}))


# ─────────────────────────────────────────────
# WORK STATION HANDLERS (tablet/phone interface)
# ─────────────────────────────────────────────

class WorkStationPageHandler(BaseHandler):
    """GET /work-station/{job_code} — Digital work station for shop floor workers."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self, job_code):
        from templates.work_station import WORK_STATION_HTML
        user = self.get_current_user() or "local"
        html = (WORK_STATION_HTML
                .replace("{{JOB_CODE}}", job_code)
                .replace("{{USER_NAME}}", user))
        self.render_with_nav(html, active_page="workstation", job_code=job_code)


class WorkStationDataHandler(BaseHandler):
    """GET /api/work-station/data — Items + machine info for a job's work station."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            from shop_drawings.config import MACHINES

            job_code = self.get_argument("job_code", "")
            if not job_code:
                self.write(json_encode({"ok": False, "error": "Missing job_code"}))
                return

            wos = list_work_orders(SHOP_DRAWINGS_DIR, job_code)
            if not wos:
                self.write(json_encode({
                    "ok": True, "items": [], "machines": {},
                    "work_orders": [],
                }))
                return

            # Flatten all items from all WOs for this job
            all_items = []
            wo_summaries = []
            for wo_summary in wos:
                wo = load_work_order(SHOP_DRAWINGS_DIR, job_code,
                                     wo_summary["work_order_id"])
                if wo is None:
                    continue
                wo_summaries.append(wo.summary())
                for item in wo.items:
                    d = item.to_dict()
                    d["work_order_id"] = wo.work_order_id
                    all_items.append(d)

            # Build machine summary
            machines = {}
            for m_id, m_info in MACHINES.items():
                machines[m_id] = {
                    "name": m_info["name"],
                    "location": m_info.get("location", ""),
                    "item_count": 0,
                    "in_progress": 0,
                    "completed": 0,
                    "queued": 0,
                }

            for item in all_items:
                m = item.get("machine", "")
                if m in machines:
                    machines[m]["item_count"] += 1
                    if item.get("status") == "in_progress":
                        machines[m]["in_progress"] += 1
                    elif item.get("status") == "complete":
                        machines[m]["completed"] += 1
                    else:
                        machines[m]["queued"] += 1

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "items": all_items,
                "machines": machines,
                "work_orders": wo_summaries,
            }))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e),
                                    "trace": traceback.format_exc()}))


class WorkStationStepsHandler(BaseHandler):
    """GET /api/work-station/steps — Fab steps for a specific item."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            from shop_drawings.fab_steps import get_steps_for_item

            job_code = self.get_argument("job_code", "")
            item_id = self.get_argument("item_id", "")

            if not job_code or not item_id:
                self.write(json_encode({"ok": False, "error": "Missing params"}))
                return

            wo, item = find_work_order_by_item(SHOP_DRAWINGS_DIR, job_code, item_id)
            if wo is None or item is None:
                self.write(json_encode({"ok": False, "error": "Item not found"}))
                return

            item_dict = item.to_dict()
            steps = get_steps_for_item(item_dict, SHOP_DRAWINGS_DIR, job_code)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "item": item_dict,
                "steps": steps,
            }))
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e),
                                    "trace": traceback.format_exc()}))


class WorkStationStepOverrideHandler(BaseHandler):
    """POST /api/work-station/steps/override — Save custom fab steps for a component type."""
    required_roles = ["admin"]

    def post(self):
        try:
            from shop_drawings.fab_steps import save_step_override

            data = json.loads(self.request.body)
            template_key = data.get("template_key", "")
            steps = data.get("steps", [])
            job_code = data.get("job_code", "")  # Optional: job-specific override

            if not template_key or not steps:
                self.write(json_encode({"ok": False, "error": "Missing template_key or steps"}))
                return

            filepath = save_step_override(SHOP_DRAWINGS_DIR, template_key,
                                          steps, job_code=job_code)
            self.write(json_encode({"ok": True, "saved": filepath}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class QRScannerPageHandler(BaseHandler):
    """GET /scan/{job_code} — Mobile-optimized QR scanner page for shop floor."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self, job_code):
        from templates.qr_scanner import QR_SCANNER_HTML
        user = self.get_current_user() or "shop"
        html = (QR_SCANNER_HTML
                .replace("{{JOB_CODE}}", job_code)
                .replace("{{USER_NAME}}", user))
        self.set_header("Content-Type", "text/html")
        self.write(html)


class WorkOrderItemDetailHandler(BaseHandler):
    """GET /api/work-orders/detail — Look up a single item by item_id for the scanner."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            job_code = self.get_argument("job_code", "").strip()
            item_id = self.get_argument("item_id", "").strip()

            if not job_code or not item_id:
                self.write(json_encode({"ok": False, "error": "Missing job_code or item_id"}))
                return

            wos = list_work_orders(SHOP_DRAWINGS_DIR, job_code)
            for wo in wos:
                for it in (wo.items if hasattr(wo, 'items') else []):
                    it_dict = it.to_dict() if hasattr(it, 'to_dict') else it
                    if it_dict.get("item_id") == item_id:
                        wo_dict = wo.to_dict() if hasattr(wo, 'to_dict') else wo
                        self.write(json_encode({
                            "ok": True,
                            "item": it_dict,
                            "work_order": {
                                "work_order_id": wo_dict.get("work_order_id", ""),
                                "status": wo_dict.get("status", ""),
                            }
                        }))
                        return

            self.write(json_encode({"ok": False, "error": f"Item '{item_id}' not found in job {job_code}"}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class WorkOrderPacketPDFHandler(BaseHandler):
    """GET /api/work-orders/packet/pdf — Generate printable work order packet PDF."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        try:
            from shop_drawings.wo_packets import generate_wo_packet_pdf
            from shop_drawings.fab_steps import get_steps_for_item

            job_code = self.get_argument("job_code", "")
            wo_id = self.get_argument("wo_id", "")
            base_url = self.get_argument("base_url", "http://localhost:8080")

            if not job_code or not wo_id:
                self.set_status(400)
                self.write("Missing job_code or wo_id")
                return

            wo = load_work_order(SHOP_DRAWINGS_DIR, job_code, wo_id)
            if wo is None:
                self.set_status(404)
                self.write("Work order not found")
                return

            # Build steps for each item
            steps_by_item = {}
            for item in wo.items:
                item_dict = item.to_dict()
                steps_by_item[item.item_id] = get_steps_for_item(
                    item_dict, SHOP_DRAWINGS_DIR, job_code)

            pdf_bytes = generate_wo_packet_pdf(wo.to_dict(), steps_by_item,
                                               base_url=base_url)

            self.set_header("Content-Type", "application/pdf")
            self.set_header("Content-Disposition",
                            f'inline; filename="WO_Packet_{wo_id}.pdf"')
            self.write(pdf_bytes)
        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(f"Error: {e}\n{traceback.format_exc()}")


# ─────────────────────────────────────────────
# LOAD BUILDER
# ─────────────────────────────────────────────

LOAD_BUILDER_PATH = os.path.join(DATA_DIR, "load_builder.json")


def _load_builder_data():
    if os.path.isfile(LOAD_BUILDER_PATH):
        with open(LOAD_BUILDER_PATH) as f:
            return json.load(f)
    return {"loads": []}


def _save_builder_data(data):
    with open(LOAD_BUILDER_PATH, "w") as f:
        json.dump(data, f, indent=2)


class LoadBuilderPageHandler(BaseHandler):
    """GET /load-builder — Load Builder page."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        from templates.load_builder import LOAD_BUILDER_HTML
        self.render_with_nav(LOAD_BUILDER_HTML, active_page="shipping")


class LoadBuilderListHandler(BaseHandler):
    """GET /api/load-builder/loads — List active loads."""
    def get(self):
        data = _load_builder_data()
        self.write(json_encode({"ok": True, "loads": data.get("loads", [])}))


class LoadBuilderCreateHandler(BaseHandler):
    """POST /api/load-builder/create — Create a new load."""
    def post(self):
        import datetime
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "")
        if not job_code:
            self.write(json_encode({"ok": False, "error": "job_code required"}))
            return

        data = _load_builder_data()
        loads = data.get("loads", [])
        load_id = f"LOAD-{len(loads)+1:04d}"
        new_load = {
            "load_id": load_id,
            "job_code": job_code,
            "truck_number": body.get("truck_number", ""),
            "trailer_number": body.get("trailer_number", ""),
            "driver": body.get("driver", ""),
            "date": body.get("date", datetime.datetime.now().strftime("%Y-%m-%d")),
            "status": "building",
            "items": [],
            "created_at": datetime.datetime.now().isoformat(),
        }
        loads.append(new_load)
        data["loads"] = loads
        _save_builder_data(data)
        self.write(json_encode({"ok": True, "load": new_load}))


class LoadBuilderAddItemHandler(BaseHandler):
    """POST /api/load-builder/add-item — Add item to a load."""
    def post(self):
        body = json_decode(self.request.body)
        load_id = body.get("load_id", "")
        item = body.get("item", {})
        if not load_id or not item:
            self.write(json_encode({"ok": False, "error": "load_id and item required"}))
            return

        data = _load_builder_data()
        for load in data.get("loads", []):
            if load["load_id"] == load_id:
                import datetime
                item.setdefault("added_at", datetime.datetime.now().isoformat())
                load["items"].append(item)
                _save_builder_data(data)
                self.write(json_encode({"ok": True}))
                return
        self.write(json_encode({"ok": False, "error": "Load not found"}))


class LoadBuilderRemoveItemHandler(BaseHandler):
    """POST /api/load-builder/remove-item — Remove item from a load."""
    def post(self):
        body = json_decode(self.request.body)
        load_id = body.get("load_id", "")
        item_id = body.get("item_id", "")
        data = _load_builder_data()
        for load in data.get("loads", []):
            if load["load_id"] == load_id:
                load["items"] = [i for i in load["items"] if i.get("item_id") != item_id]
                _save_builder_data(data)
                self.write(json_encode({"ok": True}))
                return
        self.write(json_encode({"ok": False, "error": "Load not found"}))


class LoadBuilderFinalizeHandler(BaseHandler):
    """POST /api/load-builder/finalize — Finalize a load."""
    def post(self):
        body = json_decode(self.request.body)
        load_id = body.get("load_id", "")
        data = _load_builder_data()
        for load in data.get("loads", []):
            if load["load_id"] == load_id:
                load["status"] = "ready"
                _save_builder_data(data)
                self.write(json_encode({"ok": True}))
                return
        self.write(json_encode({"ok": False, "error": "Load not found"}))


class LoadBuilderDeleteHandler(BaseHandler):
    """DELETE/POST /api/load-builder/delete — Delete a load."""
    def post(self):
        body = json_decode(self.request.body)
        load_id = body.get("load_id", "")
        data = _load_builder_data()
        data["loads"] = [l for l in data.get("loads", []) if l["load_id"] != load_id]
        _save_builder_data(data)
        self.write(json_encode({"ok": True}))


# ─────────────────────────────────────────────
# SHIPPING DOCUMENT HANDLERS
# ─────────────────────────────────────────────

class ShippingPageHandler(BaseHandler):
    """GET /shipping/{job_code} — Shipping Hub page."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self, job_code):
        from templates.shipping_page import SHIPPING_PAGE_HTML
        html = SHIPPING_PAGE_HTML.replace("{{JOB_CODE}}", job_code)
        self.render_with_nav(html, active_page="shipping")


class ShippingPackingListHandler(BaseHandler):
    """POST /api/shipping/packing-list — Generate a packing list."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        from shop_drawings.shipping_docs import generate_packing_list, save_shipping_doc
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "")
        if not job_code:
            self.write(json_encode({"ok": False, "error": "job_code required"}))
            return
        wo_dict = body.get("work_order", {})
        result = generate_packing_list(
            job_code, wo_dict,
            items_filter=body.get("items_filter"),
            ship_date=body.get("ship_date"),
            truck_info=body.get("truck_info")
        )
        save_shipping_doc(SHOP_DRAWINGS_DIR, job_code, "packing_list", result)
        self.write(json_encode({"ok": True, "data": result}))

    def get(self):
        from shop_drawings.shipping_docs import load_shipping_docs
        job_code = self.get_argument("job_code", "")
        docs = load_shipping_docs(SHOP_DRAWINGS_DIR, job_code, "packing_list")
        self.write(json_encode({"ok": True, "docs": docs}))


class ShippingBOLHandler(BaseHandler):
    """POST /api/shipping/bol — Generate a Bill of Lading."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        from shop_drawings.shipping_docs import generate_bill_of_lading, save_shipping_doc
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "")
        if not job_code:
            self.write(json_encode({"ok": False, "error": "job_code required"}))
            return
        result = generate_bill_of_lading(
            job_code, body.get("work_order", {}),
            carrier_info=body.get("carrier_info"),
            consignee=body.get("consignee")
        )
        save_shipping_doc(SHOP_DRAWINGS_DIR, job_code, "bol", result)
        self.write(json_encode({"ok": True, "data": result}))

    def get(self):
        from shop_drawings.shipping_docs import load_shipping_docs
        job_code = self.get_argument("job_code", "")
        docs = load_shipping_docs(SHOP_DRAWINGS_DIR, job_code, "bol")
        self.write(json_encode({"ok": True, "docs": docs}))


class ShippingManifestHandler(BaseHandler):
    """POST /api/shipping/manifest — Generate a shipping manifest."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        from shop_drawings.shipping_docs import generate_shipping_manifest, save_shipping_doc
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "")
        result = generate_shipping_manifest(job_code, loads=body.get("loads"))
        save_shipping_doc(SHOP_DRAWINGS_DIR, job_code, "manifest", result)
        self.write(json_encode({"ok": True, "data": result}))

    def get(self):
        from shop_drawings.shipping_docs import load_shipping_docs
        job_code = self.get_argument("job_code", "")
        docs = load_shipping_docs(SHOP_DRAWINGS_DIR, job_code, "manifest")
        self.write(json_encode({"ok": True, "docs": docs}))


class ShippingPurchaseOrderHandler(BaseHandler):
    """POST /api/shipping/purchase-order — Generate a purchase order."""
    required_roles = ["admin", "estimator"]

    def post(self):
        from shop_drawings.shipping_docs import generate_purchase_order, save_shipping_doc
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "general")
        result = generate_purchase_order(
            po_number=body.get("po_number"),
            vendor=body.get("vendor"),
            line_items=body.get("line_items", []),
            delivery_date=body.get("delivery_date"),
            notes=body.get("notes")
        )
        save_shipping_doc(SHOP_DRAWINGS_DIR, job_code, "purchase_order", result)
        self.write(json_encode({"ok": True, "data": result}))

    def get(self):
        from shop_drawings.shipping_docs import load_shipping_docs
        job_code = self.get_argument("job_code", "general")
        docs = load_shipping_docs(SHOP_DRAWINGS_DIR, job_code, "purchase_order")
        self.write(json_encode({"ok": True, "docs": docs}))


class ShippingReorderHandler(BaseHandler):
    """GET /api/shipping/reorder-alerts — Check inventory reorder points."""
    required_roles = ["admin", "estimator"]

    def get(self):
        from shop_drawings.shipping_docs import check_reorder_points
        inv = load_inventory()
        alerts = check_reorder_points(inv)
        self.write(json_encode({"ok": True, "alerts": alerts}))


class ShippingDocsListHandler(BaseHandler):
    """GET /api/shipping/docs — List all shipping docs for a job."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        from shop_drawings.shipping_docs import load_shipping_docs
        job_code = self.get_argument("job_code", "")
        doc_type = self.get_argument("type", None)
        docs = load_shipping_docs(SHOP_DRAWINGS_DIR, job_code, doc_type)
        self.write(json_encode({"ok": True, "docs": docs}))


# ─────────────────────────────────────────────
# QC PHOTO HANDLERS
# ─────────────────────────────────────────────

class QCPhotoUploadHandler(BaseHandler):
    """POST /api/qc/photos/upload — Upload photo to QC inspection or NCR."""
    required_roles = ["admin", "estimator", "shop"]

    def post(self):
        from shop_drawings.qc_photos import save_qc_photo
        job_code = self.get_argument("job_code", "")
        record_type = self.get_argument("record_type", "")
        record_id = self.get_argument("record_id", "")
        caption = self.get_argument("caption", "")

        if not job_code or not record_type or not record_id:
            self.write(json_encode({"ok": False, "error": "job_code, record_type, record_id required"}))
            return

        if "photo" not in self.request.files:
            self.write(json_encode({"ok": False, "error": "No photo file uploaded"}))
            return

        file_info = self.request.files["photo"][0]
        user = self.get_current_user() or "local"
        result = save_qc_photo(
            QC_DIR, job_code, record_type, record_id,
            file_info["body"], file_info["filename"],
            caption=caption, uploaded_by=user
        )
        self.write(json_encode({"ok": True, "photo": result}))


class QCPhotoListHandler(BaseHandler):
    """GET /api/qc/photos — List photos for a QC record."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        from shop_drawings.qc_photos import list_qc_photos
        job_code = self.get_argument("job_code", "")
        record_type = self.get_argument("record_type", None)
        record_id = self.get_argument("record_id", None)
        photos = list_qc_photos(QC_DIR, job_code, record_type, record_id)
        self.write(json_encode({"ok": True, "photos": photos}))


class QCPhotoDeleteHandler(BaseHandler):
    """POST /api/qc/photos/delete — Delete a QC photo."""
    required_roles = ["admin", "estimator"]

    def post(self):
        from shop_drawings.qc_photos import delete_qc_photo
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "")
        photo_id = body.get("photo_id", "")
        ok = delete_qc_photo(QC_DIR, job_code, photo_id)
        self.write(json_encode({"ok": ok}))


class QCPhotoServeHandler(BaseHandler):
    """GET /qc-photos/{job_code}/{record_id}/{filename} — Serve a QC photo file."""

    def get(self, job_code, record_id, filename):
        from shop_drawings.qc_photos import get_photo_path
        import mimetypes
        path = get_photo_path(QC_DIR, job_code, record_id, filename)
        if not path or not os.path.isfile(path):
            self.set_status(404)
            self.write("Photo not found")
            return
        content_type = mimetypes.guess_type(filename)[0] or "image/jpeg"
        self.set_header("Content-Type", content_type)
        self.set_header("Cache-Control", "public, max-age=86400")
        with open(path, "rb") as f:
            self.write(f.read())


# ─────────────────────────────────────────────
# GANTT / SCHEDULING HANDLERS
# ─────────────────────────────────────────────

class GanttPageHandler(BaseHandler):
    """GET /schedule — Production schedule / Gantt view."""
    required_roles = ["admin", "estimator"]

    def get(self):
        from templates.gantt_view import GANTT_VIEW_HTML
        self.render_with_nav(GANTT_VIEW_HTML, active_page="schedule")


class GanttDataHandler(BaseHandler):
    """GET /api/gantt/data — Gantt chart data for all active jobs."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        from shop_drawings.scheduling import get_gantt_data
        data = get_gantt_data(SHOP_DRAWINGS_DIR, PROJECTS_DIR)
        self.write(json_encode({"ok": True, "data": data}))


class MachineUtilizationHandler(BaseHandler):
    """GET /api/gantt/machines — Machine utilization data."""
    required_roles = ["admin", "estimator", "shop"]

    def get(self):
        from shop_drawings.scheduling import get_machine_utilization
        days = int(self.get_argument("days", "14"))
        data = get_machine_utilization(SHOP_DRAWINGS_DIR, days_ahead=days)
        self.write(json_encode({"ok": True, "data": data}))


# ─────────────────────────────────────────────
# PWA SUPPORT HANDLERS
# ─────────────────────────────────────────────

class PWAManifestHandler(tornado.web.RequestHandler):
    """GET /static/manifest.json — PWA web app manifest."""
    def get(self):
        from templates.pwa_support import get_pwa_bundle
        bundle = get_pwa_bundle()
        self.set_header("Content-Type", "application/manifest+json")
        self.write(bundle["manifest_json_str"])


class PWAServiceWorkerHandler(tornado.web.RequestHandler):
    """GET /static/service-worker.js — PWA service worker."""
    def get(self):
        from templates.pwa_support import get_pwa_bundle
        bundle = get_pwa_bundle()
        self.set_header("Content-Type", "application/javascript")
        self.set_header("Service-Worker-Allowed", "/")
        self.write(bundle["service_worker_js"])


class PWAOfflineHandler(tornado.web.RequestHandler):
    """GET /offline — Offline fallback page."""
    def get(self):
        from templates.pwa_support import get_pwa_bundle
        bundle = get_pwa_bundle()
        self.set_header("Content-Type", "text/html")
        self.write(bundle["offline_html"])


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
        (r"/auth/users/edit",    UserEditHandler),
        (r"/auth/users/delete",  UserDeleteHandler),

        # ── App routes (Dashboard + Calculators) ────────────────
        (r"/",                      DashboardHandler),
        (r"/sa",                    SACalcHandler),
        (r"/tc",                    TCQuoteHandler),
        (r"/getting-started",       GettingStartedHandler),
        (r"/api/help-bundle",       HelpBundleHandler),

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
        (r"/api/inventory/inv-config",   InventoryConfigHandler),
        (r"/api/inventory/summary",      InventorySummaryHandler),
        (r"/api/inventory/coils",        InventoryCoilsHandler),
        (r"/api/inventory/coil/create",  InventoryCoilCreateHandler),
        (r"/api/inventory/transactions", InventoryTransactionsHandler),
        (r"/api/inventory/allocations",  InventoryAllocationsHandler),
        (r"/api/inventory/allocate/release", InventoryAllocateReleaseHandler),
        (r"/api/inventory/allocate",     InventoryAllocateHandler),
        (r"/api/inventory/receiving",    InventoryReceivingHandler),
        (r"/api/inventory/receive",      InventoryReceiveHandler),
        (r"/api/inventory/alerts/acknowledge", InventoryAlertAcknowledgeHandler),
        (r"/api/inventory/alerts",       InventoryAlertsHandler),
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
        (r"/api/project/docs/archive",   ProjectArchiveDocHandler),
        (r"/api/project/docs/archived",  ProjectArchivedDocsHandler),
        (r"/project-files/([^/]+)/([^/]+)/([^/]+)", ProjectDocServeHandler),

        # ── API - Project Status (NEW) ────────────────────────
        (r"/api/project/status",         ProjectStatusHandler),
        (r"/api/project/assets",         ProjectAssetsHandler),

        # ── API - Enhanced Project System ─────────────────────
        (r"/api/project/next-code",      ProjectNextCodeHandler),
        (r"/api/project/create",         ProjectCreateHandler),
        (r"/api/project/delete",         ProjectDeleteHandler),
        (r"/api/project/metadata",       ProjectMetadataHandler),
        (r"/api/project/checklist",      ProjectChecklistHandler),
        (r"/api/project/next-steps",     ProjectNextStepsHandler),
        (r"/api/projects/full",          ProjectListEnhancedHandler),

        # ── Project Page ──────────────────────────────────────
        (r"/project/([^/]+)",            ProjectPageHandler),

        # ── Shop Drawings ─────────────────────────────────────
        (r"/shop-drawings/([^/]+)/column",       ColumnInteractiveHandler),
        (r"/shop-drawings/([^/]+)/rafter",       RafterInteractiveHandler),
        (r"/shop-drawings/([^/]+)",              ShopDrawingsPageHandler),
        (r"/api/shop-drawings/config",           ShopDrawingsConfigHandler),
        (r"/api/shop-drawings/save-interactive-pdf", SaveInteractivePDFHandler),
        (r"/api/shop-drawings/sync-bom",         ShopDrawingsSyncBOMHandler),
        (r"/api/shop-drawings/diff",             ShopDrawingsDiffHandler),
        (r"/api/shop-drawings/generate",         ShopDrawingsGenerateHandler),
        (r"/api/shop-drawings/file",             ShopDrawingsFileHandler),
        (r"/api/shop-drawings/zip",              ShopDrawingsZipHandler),

        # ── Work Orders ──────────────────────────────────────
        (r"/work-orders/([^/]+)",                WorkOrderPageHandler),
        (r"/api/work-orders/create",             WorkOrderCreateHandler),
        (r"/api/work-orders/list",               WorkOrderListHandler),
        (r"/api/work-orders/detail",             WorkOrderDetailHandler),
        (r"/api/work-orders/approve",            WorkOrderApproveHandler),
        (r"/api/work-orders/stickers-printed",   WorkOrderStickersPrintedHandler),
        (r"/api/work-orders/hold",               WorkOrderHoldHandler),
        (r"/api/work-orders/qr-scan",            WorkOrderQRScanHandler),
        (r"/api/work-orders/item-notes",         WorkOrderItemNotesHandler),
        (r"/api/work-orders/stickers/pdf",       WorkOrderStickerPDFHandler),
        (r"/api/work-orders/stickers/zpl",       WorkOrderStickerZPLHandler),
        (r"/api/work-orders/stickers/csv",       WorkOrderStickerCSVHandler),
        (r"/api/work-orders/stickers/single",    WorkOrderSingleStickerHandler),

        # ── Shop Floor Dashboard ─────────────────────────────
        (r"/shop-floor",                         ShopFloorPageHandler),
        (r"/api/shop-floor/data",                ShopFloorDataHandler),

        # ── Work Station (tablet/phone) ───────────────────────
        (r"/work-station/([^/]+)",               WorkStationPageHandler),
        (r"/api/work-station/data",              WorkStationDataHandler),
        (r"/api/work-station/steps",             WorkStationStepsHandler),
        (r"/api/work-station/steps/override",    WorkStationStepOverrideHandler),
        (r"/api/work-orders/packet/pdf",         WorkOrderPacketPDFHandler),

        # ── Mobile QR Scanner ─────────────────────────────────
        (r"/scan/([^/]+)",                       QRScannerPageHandler),
        (r"/api/work-orders/detail",             WorkOrderItemDetailHandler),

        # ── TV Dashboard & Gamification ───────────────────────
        (r"/tv-dashboard",                       TVDashboardPageHandler),
        (r"/api/gamification/leaderboard",       GamificationLeaderboardHandler),
        (r"/api/gamification/stats",             GamificationStatsHandler),
        (r"/api/gamification/targets",           GamificationTargetsHandler),

        # ── Smart Queue & Alerts ──────────────────────────────
        (r"/api/smart-queue",                    SmartQueueHandler),
        (r"/api/alerts",                         AlertsHandler),

        # ── Customer Database ─────────────────────────────────
        (r"/customers",                      CustomerPageHandler),
        (r"/api/customers",                  CustomerListHandler),
        (r"/api/customers/create",           CustomerCreateHandler),
        (r"/api/customers/update",           CustomerUpdateHandler),
        (r"/api/customers/delete",           CustomerDeleteHandler),
        (r"/api/customers/detail",           CustomerDetailHandler),
        (r"/api/customers/docs/upload",      CustomerDocUploadHandler),
        (r"/api/customers/docs",             CustomerDocListHandler),
        (r"/customer-files/([^/]+)/([^/]+)/([^/]+)", CustomerDocServeHandler),

        # ── Global Search ─────────────────────────────────────
        (r"/api/search",                     GlobalSearchHandler),

        # ── Quote Editor / PDF Generator ──────────────────────
        (r"/quote/([^/]+)",                  QuoteEditorPageHandler),
        (r"/api/quote/data",                 QuoteDataHandler),
        (r"/api/quote/pdf",                  QuotePDFHandler),

        # ── AISC QC Module ─────────────────────────────────────
        (r"/qc/([^/]+)",                     QCPageHandler),
        (r"/api/qc/types",                   QCInspectionTypesHandler),
        (r"/api/qc/data",                    QCDataHandler),
        (r"/api/qc/inspection/create",       QCInspectionCreateHandler),
        (r"/api/qc/inspection/update",       QCInspectionUpdateHandler),
        (r"/api/qc/ncr/create",              NCRCreateHandler),
        (r"/api/qc/ncr/update",              NCRUpdateHandler),

        # ── Material Traceability ──────────────────────────────
        (r"/api/traceability",               TraceabilityIndexHandler),
        (r"/api/traceability/register",      TraceabilityRegisterHandler),
        (r"/api/traceability/assign",        TraceabilityAssignHandler),
        (r"/api/traceability/report",        TraceabilityReportHandler),

        # ── QA/QC Hub & AISC Documentation ───────────────────
        (r"/qa",                         QAHubHandler),
        (r"/api/qa/stats",               QAStatsHandler),
        (r"/qa/wps",                     WPSPageHandler),
        (r"/api/qa/wps",                 WPSLibraryHandler),
        (r"/qa/welder-certs",            WelderCertsPageHandler),
        (r"/api/qa/welder-certs",        WelderCertsAPIHandler),
        (r"/qa/procedures",              ProceduresPageHandler),
        (r"/api/qa/procedures",          ProceduresAPIHandler),
        (r"/qa/calibration",             CalibrationPageHandler),
        (r"/api/qa/calibration",         CalibrationAPIHandler),
        (r"/qa/ncr-log",                 NCRLogPageHandler),
        (r"/api/qa/ncr-log",             NCRLogAPIHandler),

        # ── Inventory Page ────────────────────────────────────
        (r"/inventory",                  InventoryPageHandler),
        (r"/inventory/traceability",     TraceabilityPageHandler),

        # ── Shipping Documents ────────────────────────────────
        # ── Load Builder ──────────────────────────────────────
        (r"/load-builder",                       LoadBuilderPageHandler),
        (r"/api/load-builder/loads",             LoadBuilderListHandler),
        (r"/api/load-builder/create",            LoadBuilderCreateHandler),
        (r"/api/load-builder/add-item",          LoadBuilderAddItemHandler),
        (r"/api/load-builder/remove-item",       LoadBuilderRemoveItemHandler),
        (r"/api/load-builder/finalize",          LoadBuilderFinalizeHandler),
        (r"/api/load-builder/delete",            LoadBuilderDeleteHandler),

        # ── Shipping ─────────────────────────────────────────
        (r"/shipping/([^/]+)",                   ShippingPageHandler),
        (r"/api/shipping/packing-list",          ShippingPackingListHandler),
        (r"/api/shipping/bol",                   ShippingBOLHandler),
        (r"/api/shipping/manifest",              ShippingManifestHandler),
        (r"/api/shipping/purchase-order",        ShippingPurchaseOrderHandler),
        (r"/api/shipping/reorder-alerts",        ShippingReorderHandler),
        (r"/api/shipping/docs",                  ShippingDocsListHandler),

        # ── QC Photos ─────────────────────────────────────────
        (r"/api/qc/photos/upload",               QCPhotoUploadHandler),
        (r"/api/qc/photos",                      QCPhotoListHandler),
        (r"/api/qc/photos/delete",               QCPhotoDeleteHandler),
        (r"/qc-photos/([^/]+)/([^/]+)/([^/]+)",  QCPhotoServeHandler),

        # ── Production Schedule / Gantt ───────────────────────
        (r"/schedule",                           GanttPageHandler),
        (r"/api/gantt/data",                     GanttDataHandler),
        (r"/api/gantt/machines",                 MachineUtilizationHandler),

        # ── PWA Support ───────────────────────────────────────
        (r"/static/manifest.json",               PWAManifestHandler),
        (r"/static/service-worker.js",           PWAServiceWorkerHandler),
        (r"/offline",                            PWAOfflineHandler),

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
from templates.project_page import PROJECT_PAGE_HTML
from templates.customers import CUSTOMERS_HTML
from templates.quote_editor import QUOTE_EDITOR_HTML
from templates.qc_page import QC_PAGE_HTML
from templates.shop_drawings import SHOP_DRAWINGS_HTML
from templates.work_orders import WORK_ORDERS_HTML
from templates.shop_floor import SHOP_FLOOR_HTML
from templates.work_station import WORK_STATION_HTML

# Aliases used by handlers
MAIN_HTML = SA_CALC_HTML
TC_HTML = TC_QUOTE_HTML
