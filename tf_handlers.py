"""
TitanForge v4.0 Backend Handlers
Steel fabrication shop management system.
Includes: Auth (18-role RBAC), Calculation, Inventory, Projects, Documents, Status tracking.
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

# ── New RBAC system ───────────────────────────────────────────────────────────
from auth.roles import P, ROLES, ROLE_IDS, get_role, get_role_permissions, list_all_roles
from auth.permissions import PermissionSet, merge_permissions, build_template_context
from auth.middleware import AuthMixin, require_permission, require_any_role, require_financial_access, require_delete_capability
import auth.middleware as auth_middleware
import auth.users as auth_users

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

DATA_DIR = os.path.join(BASE_DIR, "data")
INVENTORY_PATH = os.path.join(BASE_DIR, "data", "inventory.json")
USERS_PATH = os.path.join(BASE_DIR, "data", "users.json")
CERTS_DIR = os.path.join(BASE_DIR, "data", "certs")
PROJECTS_DIR = os.path.join(BASE_DIR, "data", "projects")
CUSTOMERS_PATH = os.path.join(BASE_DIR, "data", "customers.json")
QUOTES_DIR = os.path.join(BASE_DIR, "data", "quotes")
QC_DIR = os.path.join(BASE_DIR, "data", "qc")
COOKIE_SECRET = None   # Set at startup from env or auto-generated

# Auth is enabled by default for hosted deployments; disabled for localhost dev.
AUTH_ENABLED = False   # Set at startup

# ── Legacy 4-Tier Role System (kept for backward compat, new code uses auth.roles) ──
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
    ],
    # Map new roles to legacy permission groups for transition period
    "god_mode": [
        "quotes", "pricing", "bom", "inventory", "projects", "labels",
        "price_overrides", "user_management", "project_documents", "project_status",
        "work_orders", "quality", "shipping", "install_schedules"
    ],
    "project_manager": [
        "quotes", "pricing", "bom", "inventory", "projects", "labels",
        "price_overrides", "project_documents", "project_status", "work_orders"
    ],
    "shop_foreman": [
        "work_orders", "inventory", "quality", "labels", "project_documents"
    ],
    "qc_inspector": ["quality", "labels", "project_documents"],
    "engineer": ["project_documents", "labels"],
    "roll_forming_operator": ["work_orders", "labels"],
    "welder": ["work_orders", "labels"],
    "shipping_coordinator": ["shipping", "labels"],
    "laborer": ["labels"],
    "field_crew": ["project_documents"],
    "safety_officer": [],
    "customer": ["project_status"],
    "accounting": ["quotes", "pricing", "bom", "inventory", "projects"],
    "sales": ["quotes", "projects", "project_status"],
    "purchasing": ["inventory", "pricing"],
    "inventory_manager": ["inventory", "labels"],
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
    tpath = os.path.join(BASE_DIR, "data", "traceability_index.json")
    if os.path.isfile(tpath):
        with open(tpath) as f:
            return json.load(f)
    return {"heat_numbers": {}}

def save_traceability_index(data):
    """Save the global traceability index."""
    tpath = os.path.join(BASE_DIR, "data", "traceability_index.json")
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
    """Create users.json with default users if it doesn't exist. Delegates to new auth module."""
    auth_users.ensure_users_file()

def verify_password(stored_hash: str, password: str) -> bool:
    """Verify password against stored hash (bcrypt or SHA256)."""
    return auth_users.verify_password(stored_hash, password)

def hash_password(password: str) -> str:
    """Hash password using bcrypt or SHA256."""
    return auth_users.hash_password(password)

def check_role(user_role: str, required_roles: list) -> bool:
    """Check if user role has permission for required roles.
    LEGACY: new code should use perm.has_any_role() instead."""
    # Handle both old single-role and new multi-role
    if user_role in required_roles:
        return True
    # Also check new role system mappings
    legacy_to_new = {
        "admin": ["admin", "god_mode"],
        "estimator": ["estimator"],
        "shop": ["shop_foreman"],
        "viewer": ["laborer", "customer"],
    }
    new_roles = legacy_to_new.get(user_role, [user_role])
    return any(nr in required_roles for nr in new_roles)

def get_user_permissions(user_role: str) -> list:
    """Get list of permissions for a user role.
    LEGACY: new code should use auth.roles.get_role_permissions() instead."""
    return ROLE_PERMISSIONS.get(user_role, [])


# ─────────────────────────────────────────────
# BASE AUTHENTICATED HANDLER WITH ROLE CHECKING
# ─────────────────────────────────────────────

class BaseHandler(AuthMixin, tornado.web.RequestHandler):
    """
    Base handler with RBAC authentication and role permissions.

    Now powered by the auth/ package (18-role system with multi-role merging).
    All existing handler subclasses continue to work unchanged.

    New capabilities available to all handlers:
        self.perm              — PermissionSet with .can(), .has_role(), financial checks
        self.user_roles        — list of role IDs
        self.current_user_data — full user dict
        self.template_ctx      — dict with all permission flags for templates
    """
    # Legacy: override in subclasses for old-style role checking
    # New handlers should use @require_permission or @require_any_role instead
    required_roles = None

    def get_current_user(self):
        """Get current authenticated user (username or 'local' in dev mode)."""
        if not AUTH_ENABLED:
            return "local"
        cookie = self.get_secure_cookie("sa_user")
        if cookie:
            return cookie.decode("utf-8")
        return None

    def get_user_role(self):
        """Get current user's primary role (LEGACY — use self.user_roles instead)."""
        if not AUTH_ENABLED:
            return "god_mode"
        current = self.get_current_user()
        if not current:
            return None
        users = load_users()
        user = users.get(current, {})
        # New format: multi-role
        roles = user.get("roles", [])
        if roles:
            return roles[0]
        # Legacy format: single role
        return user.get("role", "laborer")

    def check_permission(self, permission: str) -> bool:
        """Check if current user has a specific permission.
        LEGACY: new handlers should use self.perm.can(permission) instead."""
        # Try new RBAC system first
        if hasattr(self, 'perm') and self.perm:
            return self.perm.can(permission)
        # Fallback to legacy
        role = self.get_user_role()
        if not role:
            return False
        return permission in get_user_permissions(role)

    def prepare(self):
        """Check auth before handling request. Bridges old and new RBAC."""
        # Sync AUTH_ENABLED to auth middleware module
        auth_middleware.AUTH_ENABLED = AUTH_ENABLED

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

        # Check user is active (new RBAC feature)
        user = self.current_user_data
        if user and not user.get("active", True):
            self.clear_cookie("sa_user")
            self.redirect("/auth/login")
            raise tornado.web.Finish()

        # Legacy role check (old handlers use required_roles = ["admin"])
        if self.required_roles is not None:
            role = self.get_user_role()
            if not check_role(role, self.required_roles):
                # Per RULES.md: redirect to dashboard, not 403 page
                if self.request.method == "GET" and not path.startswith("/api/"):
                    self.redirect("/dashboard")
                else:
                    self.set_status(403)
                    self.write(json_encode({"error": "Insufficient permissions"}))
                raise tornado.web.Finish()

    def render_with_nav(self, html: str, active_page: str = "",
                        job_code: str = ""):
        """Render HTML with the unified sidebar navigation injected."""
        from templates.shared_nav import inject_nav

        user = self.get_current_user() or "local"
        role = self.get_user_role() or "god_mode"
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
        try:
            body = json_decode(self.request.body)
        except:
            body = {
                "username": self.get_argument("username", ""),
                "password": self.get_argument("password", "")
            }
        username = body.get("username", "").strip().lower()
        password = body.get("password", "")

        # Check lockout first
        lockout = auth_users.check_lockout(username)
        if lockout:
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": False, "error": "Account locked. Try again later."}))
            return

        users = load_users()
        user = users.get(username)

        # Get the password hash — support both new and legacy field names
        stored_hash = None
        if user:
            stored_hash = user.get("password_hash") or user.get("password")

        if not user or not stored_hash or not verify_password(stored_hash, password):
            # Record failed login
            ip = self.request.remote_ip or ""
            auth_users.record_login(username, False, ip)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": False, "error": "Invalid username or password."}))
            return

        # Check if user is active
        if not user.get("active", True):
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": False, "error": "Account deactivated. Contact admin."}))
            return

        # Record successful login
        ip = self.request.remote_ip or ""
        auth_users.record_login(username, True, ip)

        self.set_secure_cookie("sa_user", username, expires_days=30)
        self.set_header("Content-Type", "application/json")

        # Get user roles for response
        roles = user.get("roles", [user.get("role", "laborer")])
        self.write(json_encode({
            "ok": True,
            "redirect": "/",
            "user": {
                "username": username,
                "display_name": user.get("display_name", username),
                "roles": roles,
            }
        }))


class LogoutHandler(tornado.web.RequestHandler):
    """GET /auth/logout — Clear session and redirect to login."""
    def get(self):
        self.clear_cookie("sa_user")
        self.redirect("/auth/login")


class AdminPageHandler(BaseHandler):
    """GET /admin — User management page (God Mode only)."""
    required_roles = ["admin", "god_mode"]

    def get(self):
        self.render_with_nav(ADMIN_HTML, active_page="admin")


class UsersListHandler(BaseHandler):
    """GET /auth/users — List all users (admin only)."""
    required_roles = ["admin"]

    def get(self):
        users = load_users()
        safe = []
        for uname, udata in users.items():
            safe.append({
                "username": uname,
                "display_name": udata.get("display_name", ""),
                "role": udata.get("role", "viewer"),
                "created_at": udata.get("created", ""),
            })
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


class UserUpdateRoleHandler(BaseHandler):
    """POST /auth/users/update-role — Change a user's role (admin only)."""
    required_roles = ["admin"]

    def post(self):
        body = json_decode(self.request.body)
        username = body.get("username", "").strip().lower()
        new_role = body.get("role", "")

        if not username or not new_role:
            self.write(json_encode({"ok": False, "error": "Username and role required"}))
            return

        users = load_users()
        if username not in users:
            self.write(json_encode({"ok": False, "error": "User not found"}))
            return

        users[username]["role"] = new_role
        # Also update the roles list if present
        users[username]["roles"] = [new_role]
        save_users(users)
        self.write(json_encode({"ok": True, "message": f"Role updated to {new_role}"}))


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
    """GET / — Role-aware TitanForge dashboard."""
    def get(self):
        user = self.get_current_user() or "local"
        users_db = load_users()
        user_data = users_db.get(user, {})
        display = user_data.get("display_name", user) if user != "local" else "Admin"

        # Get role info for template
        roles = self.user_roles
        perm = self.perm
        primary_role = roles[0] if roles else "god_mode"

        # Build role-aware dashboard card JSON for the frontend
        card_groups = perm.get_dashboard_card_groups()
        cards_json = json.dumps({
            group: [{"id": c.id, "title": c.title, "group": c.group,
                     "link": c.link, "icon": c.icon, "priority": c.priority,
                     "requires_financial": c.requires_financial}
                    for c in cards]
            for group, cards in card_groups.items()
        })

        # Build permission flags JSON for frontend conditional rendering
        perm_flags = json.dumps({
            "roles": roles,
            "primary_role": primary_role,
            "show_financial": perm.has_financial_access(),
            "show_bom_pricing": perm.can_see_bom_pricing(),
            "show_margins": perm.can_see_margins(),
            "can_delete": perm.can_delete,
            "can_manage_users": perm.can_manage_users,
            "can_create_projects": perm.can(P.CREATE_PROJECTS),
            "can_run_calculator": perm.can(P.RUN_CALCULATOR),
            "can_view_calculator": perm.can(P.VIEW_CALCULATOR) or perm.can(P.RUN_CALCULATOR),
            "can_view_inventory": perm.can(P.VIEW_INVENTORY),
            "can_edit_inventory": perm.can(P.EDIT_INVENTORY),
            "can_view_projects": perm.can(P.VIEW_PROJECTS),
            "can_view_work_orders": perm.can(P.VIEW_WORK_ORDERS) or perm.can(P.VIEW_OWN_WORK_ITEMS),
            "can_view_shop_drawings": perm.can(P.VIEW_SHOP_DRAWINGS),
            "can_view_qc": perm.can(P.VIEW_QC),
            "can_view_shipping": perm.can(P.VIEW_SHIPPING),
            "can_view_field": perm.can(P.VIEW_FIELD_REPORTS) or perm.can(P.SUBMIT_DAILY_REPORT),
            "can_view_pipeline": perm.can(P.VIEW_PIPELINE),
            "can_submit_receipts": perm.can(P.SUBMIT_RECEIPTS),
            "can_view_customers": perm.can(P.VIEW_CUSTOMER_INFO),
            "mobile_first": perm.mobile_first,
        })

        # Build sidebar section IDs for frontend
        sidebar_ids = json.dumps([s["id"] for s in perm.get_sidebar()])

        html = DASHBOARD_HTML
        html = html.replace("{{USER_ROLE}}", primary_role)
        html = html.replace("{{USER_ROLES}}", json.dumps(roles))
        html = html.replace("{{USER_NAME}}", display)
        html = html.replace("{{CARD_GROUPS}}", cards_json)
        html = html.replace("{{PERM_FLAGS}}", perm_flags)
        html = html.replace("{{SIDEBAR_IDS}}", sidebar_ids)
        self.render_with_nav(html, active_page="dashboard")


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
                        cust_name = data.get("project", {}).get("customer_name", "")
                        result.append({
                            "job_code": data.get("job_code", d),
                            "project_name": data.get("project", {}).get("name", ""),
                            "customer": {"name": cust_name} if cust_name else {"name": ""},
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
                    cust_name = data.get("project", {}).get("customer_name", "")
                    result.append({
                        "job_code": data.get("job_code", d.replace(".json", "")),
                        "project_name": data.get("project", {}).get("name", ""),
                        "customer": {"name": cust_name} if cust_name else {"name": ""},
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


class ProjectDeleteHandler(BaseHandler):
    """POST /api/project/delete — Delete a project and all associated data."""
    required_roles = ["admin"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()

            if not job_code:
                self.write(json_encode({"ok": False, "error": "Job code is required"}))
                return

            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            proj_dir = os.path.join(PROJECTS_DIR, safe_name)

            # Check if project exists
            if not os.path.isdir(proj_dir):
                self.write(json_encode({"ok": False, "error": f"Project {job_code} not found"}))
                return

            # Delete the entire project directory
            try:
                shutil.rmtree(proj_dir)
            except Exception as e:
                self.set_status(500)
                self.write(json_encode({"ok": False, "error": f"Failed to delete project: {str(e)}"}))
                return

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True}))

        except Exception as e:
            import traceback
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": False, "error": str(e), "trace": traceback.format_exc()}))


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
        docs_dir = os.path.join(BASE_DIR, "data", "customer_docs", safe_cid, doc_type)
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
        base = os.path.join(BASE_DIR, "data", "customer_docs", safe_cid)
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
        fpath = os.path.join(BASE_DIR, "data", "customer_docs", cid, dtype, fname)
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
    required_permission = "perform_inspections"
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
    """POST /api/qc/inspection/update — Update an inspection record (checklist items, status, notes).
    Passing/failing requires sign_off_qc permission. Integrates with WO item lifecycle."""
    required_permission = "perform_inspections"
    def post(self):
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "")
        insp_id = body.get("inspection_id", "")
        new_status = body.get("status", "")

        # Sign-off requires elevated permission
        if new_status in ["passed", "failed"]:
            if not self.perm.can("sign_off_qc"):
                self.set_status(403)
                self.write(json_encode({"ok": False, "error": "sign_off_qc permission required to pass/fail inspections"}))
                return

        qc = load_project_qc(job_code)
        found = False
        insp_data = None
        for i, insp in enumerate(qc["inspections"]):
            if insp["id"] == insp_id:
                for k in ["items", "notes", "status", "location", "member_marks", "photos"]:
                    if k in body:
                        qc["inspections"][i][k] = body[k]
                if new_status in ["passed", "failed"]:
                    qc["inspections"][i]["completed_at"] = datetime.datetime.now().isoformat()
                    qc["inspections"][i]["signed_off_by"] = self.current_username or ""
                insp_data = qc["inspections"][i]
                found = True
                break
        if not found:
            self.write(json_encode({"ok": False, "error": "Inspection not found"}))
            return
        save_project_qc(job_code, qc)

        # ── WO Integration: transition linked items on pass/fail ──
        wo_transitions = []
        if new_status in ["passed", "failed"] and insp_data:
            item_ids = body.get("work_order_item_ids", [])
            if item_ids:
                inspector = self.current_username or "qc_system"
                for item_id in item_ids:
                    target = STATUS_QC_APPROVED if new_status == "passed" else STATUS_QC_REJECTED
                    result = transition_item_status(
                        SHOP_DRAWINGS_DIR, job_code, item_id, target, inspector,
                        notes=f"QC inspection {insp_id}: {new_status}")
                    wo_transitions.append({"item_id": item_id, "result": result})

        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "wo_transitions": wo_transitions}))


class NCRCreateHandler(BaseHandler):
    """POST /api/qc/ncr/create — Create a Non-Conformance Report."""
    required_permission = "create_ncr"
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
    required_permission = "create_ncr"
    def post(self):
        body = json_decode(self.request.body)
        job_code = body.get("job_code", "")
        ncr_id = body.get("ncr_id", "")

        # Closing an NCR requires sign_off_qc
        if body.get("status") == "closed":
            if not self.perm.can("sign_off_qc"):
                self.set_status(403)
                self.write(json_encode({"ok": False, "error": "sign_off_qc permission required to close NCRs"}))
                return

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
                    qc["ncrs"][i]["closed_by"] = self.current_username or ""
                qc["ncrs"][i]["history"].append({
                    "action": f"updated ({', '.join(k for k in body if k not in ['job_code','ncr_id'])})",
                    "by": self.current_username or "",
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
    required_permission = "manage_mill_certs"
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
    required_permission = "manage_mill_certs"
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


class QCPageHandler(BaseHandler):
    """GET /qc/{job_code} — QC Dashboard page for a project."""
    required_permission = "view_qc"
    def get(self, job_code):
        html = QC_PAGE_HTML.replace("{{JOB_CODE}}", job_code)
        html = html.replace("{{USER_ROLE}}", self.get_user_role() or "viewer")
        html = html.replace("{{USER_NAME}}", self.get_current_user() or "")
        self.render_with_nav(html, active_page="qc", job_code=job_code)


class QCInspectionQueuePageHandler(BaseHandler):
    """GET /qc-queue — Inspector workspace: all items needing QC across all projects."""
    required_permission = "perform_inspections"
    def get(self):
        from templates.qc_queue_page import QC_QUEUE_PAGE_HTML
        self.render_with_nav(QC_QUEUE_PAGE_HTML, active_page="qc")


class QCInspectionQueueAPIHandler(BaseHandler):
    """GET /api/qc/queue — Returns all WO items needing QC inspection across projects."""
    required_permission = "perform_inspections"
    def get(self):
        try:
            queue_items = []
            # Scan all projects for items needing QC
            if os.path.isdir(SHOP_DRAWINGS_DIR):
                for project_dir in os.listdir(SHOP_DRAWINGS_DIR):
                    wo_dir = os.path.join(SHOP_DRAWINGS_DIR, project_dir, "work_orders")
                    if not os.path.isdir(wo_dir):
                        continue
                    for wo_file in os.listdir(wo_dir):
                        if not wo_file.endswith(".json"):
                            continue
                        wo = load_work_order(SHOP_DRAWINGS_DIR, project_dir,
                                             wo_file.replace(".json", ""))
                        if wo is None:
                            continue
                        for item in wo.items_needing_qc():
                            queue_items.append({
                                "job_code": project_dir,
                                "wo_id": wo.work_order_id,
                                "wo_name": wo.work_order_id,
                                "item_id": item.item_id,
                                "ship_mark": item.ship_mark,
                                "description": item.description,
                                "machine_type": item.machine_type,
                                "status": item.status,
                                "status_label": item.status_label,
                                "fabricated_by": item.assigned_to,
                                "priority": item.priority,
                                "qc_notes": getattr(item, 'qc_notes', ''),
                            })
            # Sort: qc_pending first, then by priority
            queue_items.sort(key=lambda x: (
                0 if x["status"] == STATUS_QC_PENDING else 1,
                x.get("priority", 50)))
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "items": queue_items, "total": len(queue_items)}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class QCSignOffHandler(BaseHandler):
    """POST /api/qc/sign-off — QC inspector signs off (approve/reject) a WO item.
    Creates inspection record AND transitions WO item status in one operation."""
    required_permission = "sign_off_qc"
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            item_id = body.get("item_id", "").strip()
            result = body.get("result", "").strip()  # "passed" or "failed"
            insp_type = body.get("inspection_type", "weld_visual")
            notes = body.get("notes", "")
            checklist_items = body.get("checklist_items", {})

            if not job_code or not item_id or result not in ["passed", "failed"]:
                self.write(json_encode({"ok": False, "error": "job_code, item_id, and result (passed/failed) required"}))
                return

            inspector = self.current_username or "qc_system"
            now = datetime.datetime.now()

            # 1. Create the inspection record
            qc = load_project_qc(job_code)
            inspection = {
                "id": "INS-" + now.strftime("%Y%m%d%H%M%S") + "-" + secrets.token_hex(3).upper(),
                "type": insp_type,
                "type_label": AISC_INSPECTION_TYPES.get(insp_type, {}).get("label", insp_type),
                "standard": AISC_INSPECTION_TYPES.get(insp_type, {}).get("standard", ""),
                "status": result,
                "inspector": inspector,
                "location": body.get("location", ""),
                "member_marks": body.get("member_marks", []),
                "items": checklist_items,
                "notes": notes,
                "photos": [],
                "created_at": now.isoformat(),
                "completed_at": now.isoformat(),
                "signed_off_by": inspector,
                "work_order_item_id": item_id,
            }
            qc["inspections"].append(inspection)

            # 2. If failed, optionally create NCR
            ncr_created = None
            if result == "failed" and body.get("create_ncr", False):
                ncr_num = len(qc["ncrs"]) + 1
                ncr = {
                    "id": f"NCR-{job_code}-{ncr_num:03d}",
                    "number": ncr_num,
                    "severity": body.get("ncr_severity", "major"),
                    "status": "open",
                    "title": body.get("ncr_title", f"QC Rejection: {item_id}"),
                    "description": notes or f"Item {item_id} failed QC inspection {inspection['id']}",
                    "member_marks": body.get("member_marks", []),
                    "inspection_id": inspection["id"],
                    "root_cause": "",
                    "corrective_action": "",
                    "preventive_action": "",
                    "disposition": body.get("disposition", "rework"),
                    "reported_by": inspector,
                    "assigned_to": body.get("assigned_to", ""),
                    "photos": [],
                    "created_at": now.isoformat(),
                    "closed_at": None,
                    "history": [
                        {"action": "created (auto from QC rejection)", "by": inspector, "at": now.isoformat()}
                    ],
                }
                qc["ncrs"].append(ncr)
                ncr_created = ncr

            save_project_qc(job_code, qc)

            # 3. Transition the WO item
            target_status = STATUS_QC_APPROVED if result == "passed" else STATUS_QC_REJECTED
            wo_result = transition_item_status(
                SHOP_DRAWINGS_DIR, job_code, item_id, target_status, inspector,
                notes=f"QC {result}: {inspection['id']}" + (f" | NCR: {ncr_created['id']}" if ncr_created else ""))

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "inspection": inspection,
                "ncr": ncr_created,
                "wo_transition": wo_result,
            }))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class QCDashboardAPIHandler(BaseHandler):
    """GET /api/qc/dashboard — Aggregated QC metrics across all projects."""
    required_permission = "view_qc"
    def get(self):
        try:
            metrics = {
                "total_inspections": 0,
                "passed": 0,
                "failed": 0,
                "in_progress": 0,
                "open_ncrs": 0,
                "critical_ncrs": 0,
                "items_awaiting_qc": 0,
                "items_approved_today": 0,
                "items_rejected_today": 0,
                "pass_rate": 0,
                "inspections_by_type": {},
                "ncrs_by_severity": {"minor": 0, "major": 0, "critical": 0},
                "ncrs_by_status": {},
                "recent_inspections": [],
                "recent_ncrs": [],
                "inspector_workload": {},
            }

            today = datetime.date.today().isoformat()

            # Scan all QC data files
            if os.path.isdir(QC_DIR):
                for qc_file in os.listdir(QC_DIR):
                    if not qc_file.endswith(".json"):
                        continue
                    job_code = qc_file.replace(".json", "")
                    qc = load_project_qc(job_code)

                    for insp in qc.get("inspections", []):
                        metrics["total_inspections"] += 1
                        s = insp.get("status", "")
                        if s == "passed":
                            metrics["passed"] += 1
                        elif s == "failed":
                            metrics["failed"] += 1
                        elif s == "in_progress":
                            metrics["in_progress"] += 1

                        itype = insp.get("type", "unknown")
                        metrics["inspections_by_type"][itype] = metrics["inspections_by_type"].get(itype, 0) + 1

                        inspector = insp.get("inspector", "unknown")
                        if inspector not in metrics["inspector_workload"]:
                            metrics["inspector_workload"][inspector] = {"total": 0, "passed": 0, "failed": 0}
                        metrics["inspector_workload"][inspector]["total"] += 1
                        if s in ["passed", "failed"]:
                            metrics["inspector_workload"][inspector][s] += 1

                        if insp.get("completed_at", "").startswith(today):
                            if s == "passed":
                                metrics["items_approved_today"] += 1
                            elif s == "failed":
                                metrics["items_rejected_today"] += 1

                        metrics["recent_inspections"].append({
                            "id": insp["id"],
                            "job_code": job_code,
                            "type": itype,
                            "type_label": insp.get("type_label", itype),
                            "status": s,
                            "inspector": inspector,
                            "created_at": insp.get("created_at", ""),
                            "completed_at": insp.get("completed_at", ""),
                        })

                    for ncr in qc.get("ncrs", []):
                        ns = ncr.get("status", "open")
                        sev = ncr.get("severity", "minor")
                        metrics["ncrs_by_severity"][sev] = metrics["ncrs_by_severity"].get(sev, 0) + 1
                        metrics["ncrs_by_status"][ns] = metrics["ncrs_by_status"].get(ns, 0) + 1
                        if ns not in ["closed", "voided"]:
                            metrics["open_ncrs"] += 1
                            if sev == "critical":
                                metrics["critical_ncrs"] += 1

                        metrics["recent_ncrs"].append({
                            "id": ncr["id"],
                            "job_code": job_code,
                            "title": ncr.get("title", ""),
                            "severity": sev,
                            "status": ns,
                            "reported_by": ncr.get("reported_by", ""),
                            "created_at": ncr.get("created_at", ""),
                        })

            # Count items awaiting QC from work orders
            if os.path.isdir(SHOP_DRAWINGS_DIR):
                for project_dir in os.listdir(SHOP_DRAWINGS_DIR):
                    wo_dir = os.path.join(SHOP_DRAWINGS_DIR, project_dir, "work_orders")
                    if not os.path.isdir(wo_dir):
                        continue
                    for wo_file in os.listdir(wo_dir):
                        if not wo_file.endswith(".json"):
                            continue
                        wo = load_work_order(SHOP_DRAWINGS_DIR, project_dir,
                                             wo_file.replace(".json", ""))
                        if wo:
                            metrics["items_awaiting_qc"] += len(wo.items_needing_qc())

            # Calculate pass rate
            completed = metrics["passed"] + metrics["failed"]
            metrics["pass_rate"] = round(metrics["passed"] / completed * 100, 1) if completed > 0 else 0

            # Sort recent items by date descending, limit to 20
            metrics["recent_inspections"].sort(key=lambda x: x.get("created_at", ""), reverse=True)
            metrics["recent_inspections"] = metrics["recent_inspections"][:20]
            metrics["recent_ncrs"].sort(key=lambda x: x.get("created_at", ""), reverse=True)
            metrics["recent_ncrs"] = metrics["recent_ncrs"][:20]

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "metrics": metrics}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class QCItemHistoryHandler(BaseHandler):
    """GET /api/qc/item-history?job_code=X&item_id=Y — Full QC history for a work order item."""
    required_permission = "view_qc"
    def get(self):
        try:
            job_code = self.get_query_argument("job_code", "").strip()
            item_id = self.get_query_argument("item_id", "").strip()
            if not job_code or not item_id:
                self.write(json_encode({"ok": False, "error": "job_code and item_id required"}))
                return

            qc = load_project_qc(job_code)
            history = {
                "inspections": [],
                "ncrs": [],
                "traceability": [],
            }

            # Find all inspections linked to this item
            for insp in qc.get("inspections", []):
                if item_id == insp.get("work_order_item_id", ""):
                    history["inspections"].append(insp)
                elif item_id in [m for m in insp.get("member_marks", [])]:
                    history["inspections"].append(insp)

            # Find NCRs linked to this item
            for ncr in qc.get("ncrs", []):
                if item_id in [m for m in ncr.get("member_marks", [])]:
                    history["ncrs"].append(ncr)

            # Find traceability records
            for trace in qc.get("traceability", []):
                if trace.get("member_mark", "") == item_id:
                    history["traceability"].append(trace)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "item_id": item_id, "history": history}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class QCDashboardPageHandler(BaseHandler):
    """GET /qc-dashboard — Global QC Dashboard with metrics across all projects."""
    required_permission = "view_qc"
    def get(self):
        from templates.qc_dashboard_page import QC_DASHBOARD_PAGE_HTML
        self.render_with_nav(QC_DASHBOARD_PAGE_HTML, active_page="qc")


class NCRDetailHandler(BaseHandler):
    """GET /api/qc/ncr/detail?job_code=X&ncr_id=Y — Get full NCR detail with history."""
    required_permission = "view_qc"
    def get(self):
        job_code = self.get_query_argument("job_code", "")
        ncr_id = self.get_query_argument("ncr_id", "")
        qc = load_project_qc(job_code)
        for ncr in qc.get("ncrs", []):
            if ncr["id"] == ncr_id:
                self.set_header("Content-Type", "application/json")
                self.write(json_encode({"ok": True, "ncr": ncr}))
                return
        self.write(json_encode({"ok": False, "error": "NCR not found"}))


# ─────────────────────────────────────────────
# SHOP DRAWING SYSTEM
# ─────────────────────────────────────────────

SHOP_DRAWINGS_DIR = os.path.join(BASE_DIR, "data", "shop_drawings")

try:
    from shop_drawings.config import ShopDrawingConfig
    from shop_drawings.master import generate_all_shop_drawings
    from shop_drawings.work_orders import (
        WorkOrder, WorkOrderItem, STATUS_QUEUED, STATUS_APPROVED,
        STATUS_STICKERS_PRINTED, STATUS_STAGED, STATUS_IN_PROGRESS,
        STATUS_FABRICATED, STATUS_QC_PENDING, STATUS_QC_APPROVED,
        STATUS_QC_REJECTED, STATUS_READY_TO_SHIP, STATUS_SHIPPED,
        STATUS_DELIVERED, STATUS_INSTALLED,
        STATUS_COMPLETE, STATUS_ON_HOLD,
        STATUS_FLOW, STATUS_LABELS, STATUS_COLORS, VALID_STATUSES,
        MACHINE_TYPES,
        create_work_order, save_work_order, load_work_order,
        list_work_orders, list_all_work_orders, load_all_active_items,
        find_work_order_by_item,
        qr_scan_start, qr_scan_finish,
        assign_item, reassign_item, reprioritize_item, stage_item,
        transition_item_status,
        get_operator_queue, get_machine_queue, get_shop_floor_summary,
    )
    from shop_drawings.wo_stickers import (
        generate_wo_sticker_pdf, generate_wo_sticker_zpl,
        generate_wo_sticker_csv,
    )
    from shop_drawings.shipping import (
        ShippingLoad, LoadItem,
        LOAD_STATUS_BUILDING, LOAD_STATUS_READY, LOAD_STATUS_IN_TRANSIT,
        LOAD_STATUS_DELIVERED, LOAD_STATUS_COMPLETE,
        LOAD_STATUSES, LOAD_STATUS_LABELS, LOAD_STATUS_COLORS, LOAD_FLOW,
        save_load, load_shipping_load, list_loads, next_load_number,
        create_load, add_items_to_load, remove_item_from_load,
        transition_load_status, generate_bol,
        get_shippable_items, get_shipping_summary,
    )
    from shop_drawings.field_ops import (
        PunchListItem, DailyFieldReport, InstallationRecord,
        PUNCH_STATUSES, PUNCH_STATUS_LABELS, PUNCH_STATUS_COLORS, PUNCH_FLOW,
        PUNCH_PRIORITIES, PUNCH_CATEGORIES, PUNCH_CATEGORY_LABELS,
        PUNCH_STATUS_OPEN, PUNCH_STATUS_IN_PROGRESS,
        PUNCH_STATUS_RESOLVED, PUNCH_STATUS_VERIFIED, PUNCH_STATUS_DEFERRED,
        create_punch_item, transition_punch_status,
        load_punch_items, load_punch_item, load_all_punch_items,
        confirm_installation, submit_daily_report,
        load_daily_reports, load_installation_records,
        get_project_completion, get_field_summary,
    )
    from shop_drawings.reporting import (
        REPORT_TYPES, REPORT_LABELS,
        REPORT_PRODUCTION_METRICS, REPORT_EXECUTIVE_SUMMARY,
        REPORT_OPERATOR_PERFORMANCE, REPORT_PROJECT_STATUS,
        REPORT_DELIVERY_ANALYSIS, REPORT_QC_ANALYSIS,
        generate_report, list_available_reports,
        get_production_metrics, get_executive_summary,
        get_operator_performance, get_project_status_report,
        get_delivery_analysis, get_qc_analysis,
    )
    from shop_drawings.activity import (
        EVENT_CATEGORIES, CATEGORY_LABELS, CATEGORY_COLORS,
        SEVERITY_LEVELS, SEVERITY_LABELS,
        EVENT_TYPES, EVENT_LABELS, EVENT_DEFAULT_SEVERITY,
        ActivityEvent, AlertRule, Notification,
        log_event, get_events, get_activity_feed, get_event_stats,
        create_alert_rule, update_alert_rule, delete_alert_rule, list_alert_rules,
        get_notifications, get_unread_count, mark_notification_read,
        mark_all_read, clear_notifications,
    )
    # Phase 8 — Scheduling & Production Planning
    from shop_drawings.scheduling import (
        SCHED_STATUSES, SCHED_STATUS_LABELS, SCHED_STATUS_DRAFT, SCHED_STATUS_ACTIVE,
        PRIORITY_LABELS, PRIORITY_COLORS,
        PRIORITY_URGENT, PRIORITY_HIGH, PRIORITY_NORMAL, PRIORITY_LOW,
        ProductionSchedule, ScheduleEntry,
        create_schedule, get_schedule, list_schedules, update_schedule, delete_schedule,
        add_schedule_entry, get_schedule_entry, update_schedule_entry, delete_schedule_entry,
        get_entries_for_date, get_entries_for_range, get_entries_for_job,
        get_machine_capacity, update_machine_capacity,
        get_daily_capacity_usage, get_capacity_forecast,
        auto_schedule_job,
        get_schedule_summary, get_job_timeline, get_machine_schedule,
        get_bottleneck_forecast, get_overdue_entries,
    )
    # Phase 9 — Document Management & Drawing Revisions
    from shop_drawings.documents import (
        REV_STATUSES, REV_STATUS_LABELS, REV_STATUS_COLORS, REV_STATUS_FLOW,
        DOC_CATEGORIES, DOC_CATEGORY_LABELS,
        RFI_STATUSES, RFI_STATUS_LABELS, RFI_PRIORITIES, RFI_PRIORITY_LABELS,
        XMIT_STATUSES, XMIT_STATUS_LABELS, XMIT_PURPOSES, XMIT_PURPOSE_LABELS,
        BOM_CHANGE_TYPES, BOM_CHANGE_TYPE_LABELS,
        DrawingRevision, RFI, Transmittal, BOMChangeOrder,
        create_revision, get_revision, list_revisions,
        transition_revision, get_latest_revision, get_revision_history,
        create_rfi, get_rfi, list_rfis, respond_to_rfi, close_rfi, void_rfi,
        create_transmittal, get_transmittal, list_transmittals,
        send_transmittal, acknowledge_transmittal,
        log_bom_change, list_bom_changes, get_bom_change_summary,
        get_document_summary,
    )
    # Phase 10 — Job Costing & Financial Tracking
    from shop_drawings.job_costing import (
        COST_CATEGORIES, COST_CATEGORY_LABELS,
        EST_STATUSES, EST_STATUS_LABELS,
        DEFAULT_LABOR_RATES, DEFAULT_LABOR_RATE_LABELS,
        CostEstimate, CostEntry, LaborEntry, ChangeOrderCost,
        create_estimate, get_estimate, list_estimates,
        update_estimate, approve_estimate, delete_estimate,
        add_cost_entry, get_cost_entry, list_cost_entries, delete_cost_entry,
        add_labor_entry, get_labor_entry, list_labor_entries, delete_labor_entry,
        get_labor_rates, update_labor_rates,
        create_change_order, get_change_order, list_change_orders,
        approve_change_order,
        get_job_cost_summary, get_cost_variance_report, get_financial_overview,
    )
    # Phase 11 — Inventory Management
    from shop_drawings.inventory import (
        COIL_STATUSES, COIL_STATUS_LABELS,
        TRANSACTION_TYPES, TRANSACTION_TYPE_LABELS,
        MATERIAL_GRADES, COIL_GAUGES, ALERT_LEVELS,
        InventoryTransaction, StockAlert, Allocation, ReceivingRecord,
        create_coil, get_coil, list_coils, update_coil, delete_coil,
        receive_stock, adjust_stock, consume_stock, list_transactions,
        allocate_stock, release_allocation, list_allocations, get_allocation,
        list_alerts, acknowledge_alert, generate_stock_alerts,
        list_receiving, add_mill_cert, list_mill_certs, delete_mill_cert,
        get_inventory_summary, get_coil_history, get_stock_valuation,
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
    """Try to load BOM data for a project and derive ShopDrawingConfig from it.

    The SA Calculator saves projects via ProjectSaveHandler to:
      /data/projects/{job_code}/current.json   (latest)
      /data/projects/{job_code}/v{n}.json      (versioned)

    The saved payload structure is:
      { job_code, project, buildings, bom_data: { project, buildings: [{geometry, line_items, ...}] } }

    We extract geometry from bom_data.buildings[0].geometry and feed it
    to ShopDrawingConfig.from_bom_data().
    """
    if not HAS_SHOP_DRAWINGS:
        return {}
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
    proj_dir = os.path.join(PROJECTS_DIR, safe)
    if not os.path.isdir(proj_dir):
        return {}

    # Try current.json first (always the latest), then versioned files
    candidates = []
    current_path = os.path.join(proj_dir, "current.json")
    if os.path.isfile(current_path):
        candidates.append(current_path)

    # Also check versioned files (v1.json, v2.json, ...) in descending order
    try:
        version_files = sorted(
            [f for f in os.listdir(proj_dir)
             if f.startswith("v") and f.endswith(".json") and f != "current.json"],
            key=lambda f: int(re.sub(r"[^0-9]", "", f) or "0"),
            reverse=True
        )
        for vf in version_files:
            candidates.append(os.path.join(proj_dir, vf))
    except Exception:
        pass

    # Also check legacy versions/ subdirectory if it exists
    versions_dir = os.path.join(proj_dir, "versions")
    if os.path.isdir(versions_dir):
        try:
            legacy_files = sorted(
                [f for f in os.listdir(versions_dir) if f.endswith(".json")],
                reverse=True
            )
            for vf in legacy_files:
                candidates.append(os.path.join(versions_dir, vf))
        except Exception:
            pass

    for filepath in candidates:
        try:
            with open(filepath) as f:
                data = json.load(f)

            # Extract BOM result — handle multiple payload formats
            bom_result = None

            # Format 1: bom_data.buildings[0].geometry (SA Calculator save format)
            bom_data = data.get("bom_data") or data.get("bom_result") or data.get("results")
            if bom_data and isinstance(bom_data, dict):
                bldgs = bom_data.get("buildings", [])
                if bldgs and isinstance(bldgs, list) and len(bldgs) > 0:
                    first_bldg = bldgs[0]
                    if isinstance(first_bldg, dict) and "geometry" in first_bldg:
                        # Found it — construct the expected format for from_bom_data()
                        bom_result = {"geometry": first_bldg["geometry"]}

            # Format 2: geometry at top level (legacy format)
            if not bom_result and "geometry" in data:
                bom_result = data

            if not bom_result:
                continue

            # Build project_info from saved data
            project_info = {"job_code": job_code}
            proj = data.get("project", {})
            if proj:
                project_info["project_name"] = proj.get("name", "")
                project_info["customer_name"] = proj.get("customer_name", "")
                project_info["location"] = (
                    f"{proj.get('city', '')}, {proj.get('state', '')}"
                    if proj.get("city") else proj.get("state", "")
                )

            # Also check metadata.json as fallback
            if not project_info.get("project_name"):
                meta_path = os.path.join(proj_dir, "metadata.json")
                if os.path.isfile(meta_path):
                    try:
                        with open(meta_path) as mf:
                            meta = json.load(mf)
                        project_info["project_name"] = meta.get("project_name", "")
                        project_info["customer_name"] = meta.get("customer_name", "")
                        project_info["location"] = meta.get("location", "")
                    except Exception:
                        pass

            cfg = ShopDrawingConfig.from_bom_data(bom_result, project_info)
            return cfg.to_dict()
        except Exception:
            continue

    return {}


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


class RafterDrawingHandler(BaseHandler):
    """GET /shop-drawings/{job_code}/rafter — Interactive Rafter Shop Drawing.

    Serves the full SVG-based interactive rafter drawing pre-filled with
    project data from BOM/config.  Supports browser Print→PDF.
    NOTE: Served standalone (no sidebar nav) — the drawing is a full-page
    interactive tool with its own controls and back-link to the dashboard.
    """
    def get(self, job_code):
        # Build config JSON for the drawing from saved config or BOM
        rafter_cfg = {}
        saved = _load_shop_config(job_code)
        if saved:
            rafter_cfg = self._extract_rafter_config(saved, job_code)
        else:
            bom_cfg = _derive_bom_config(job_code)
            if bom_cfg:
                rafter_cfg = self._extract_rafter_config(bom_cfg, job_code)

        # If no config at all, serve with null (standalone defaults)
        cfg_json = json.dumps(rafter_cfg) if rafter_cfg else "null"

        html = RAFTER_DRAWING_HTML
        html = html.replace("{{RAFTER_CONFIG_JSON}}", cfg_json)
        html = html.replace("{{JOB_CODE}}", job_code)
        # Serve standalone — no sidebar nav injection (would break the drawing layout)
        self.set_header("Content-Type", "text/html")
        self.write(html)

    @staticmethod
    def _extract_rafter_config(cfg_dict, job_code):
        """Extract rafter-relevant fields from a ShopDrawingConfig dict
        into the format expected by the HTML drawing's applyServerConfig()."""
        rc = {}
        # Building dimensions
        rc["width_ft"] = cfg_dict.get("raft_width_ft") or cfg_dict.get("building_width_ft") or cfg_dict.get("width_ft", 0)
        rc["purlin_spacing_ft"] = cfg_dict.get("raft_purlin_spacing_ft") or cfg_dict.get("purlin_spacing", 5)
        rc["overhang_ft"] = cfg_dict.get("raft_roofing_overhang_ft") or cfg_dict.get("raft_overhang_ft") or cfg_dict.get("overhang", 1)
        rc["purlin_type"] = cfg_dict.get("raft_purlin_type") or cfg_dict.get("purlin_type", "Z")
        # Angled purlins
        rc["angled_purlins"] = cfg_dict.get("raft_angled_purlins", False)
        rc["purlin_angle_deg"] = cfg_dict.get("raft_purlin_angle_deg", 15)
        # Column settings
        rc["column_mode"] = cfg_dict.get("raft_column_mode", "auto")
        rc["column_spacing_ft"] = cfg_dict.get("raft_column_spacing_ft", 25)
        rc["column_count_manual"] = cfg_dict.get("raft_column_count_manual", 1)
        rc["column_positions_manual"] = cfg_dict.get("raft_column_positions_manual", "")
        rc["front_col_position_ft"] = cfg_dict.get("raft_front_col_position_ft", 0)
        # Rebar
        rc["rebar_size"] = cfg_dict.get("raft_rebar_size", "#9")
        rc["rebar_max_stick_ft"] = cfg_dict.get("raft_rebar_max_stick_ft", 20)
        rc["rebar_end_gap_ft"] = cfg_dict.get("raft_rebar_end_gap_ft", 5)
        # Splice
        rc["splice_location_ft"] = cfg_dict.get("raft_splice_location_ft", 0)
        # Back wall
        rc["back_wall"] = cfg_dict.get("include_back_wall", False)
        # Project info
        rc["job_code"] = job_code
        rc["project_name"] = cfg_dict.get("project_name", "")
        rc["customer"] = cfg_dict.get("customer_name", "")
        rc["rafter_mark"] = cfg_dict.get("rafter_mark", "B1")
        return rc


class ColumnDrawingHandler(BaseHandler):
    """GET /shop-drawings/{job_code}/column — Interactive Column Shop Drawing.

    Serves the full SVG-based interactive column drawing pre-filled with
    project data from BOM/config.  Supports browser Print→PDF.
    NOTE: Served standalone (no sidebar nav) — the drawing is a full-page
    interactive tool with its own controls and back-link to the dashboard.
    """
    def get(self, job_code):
        # Build config JSON for the drawing from saved config or BOM
        col_cfg = {}
        saved = _load_shop_config(job_code)
        if saved:
            col_cfg = self._extract_column_config(saved, job_code)
        else:
            bom_cfg = _derive_bom_config(job_code)
            if bom_cfg:
                col_cfg = self._extract_column_config(bom_cfg, job_code)

        cfg_json = json.dumps(col_cfg) if col_cfg else "null"

        html = COLUMN_DRAWING_HTML
        html = html.replace("{{COLUMN_CONFIG_JSON}}", cfg_json)
        html = html.replace("{{JOB_CODE}}", job_code)
        # Serve standalone — no sidebar nav injection (would break the drawing layout)
        self.set_header("Content-Type", "text/html")
        self.write(html)

    @staticmethod
    def _extract_column_config(cfg_dict, job_code):
        """Extract column-relevant fields from a ShopDrawingConfig dict
        into the format expected by the HTML drawing's applyServerConfig()."""
        rc = {}
        rc["pitch_deg"] = cfg_dict.get("col_pitch_deg") or cfg_dict.get("pitch_deg", 1.2)
        rc["clear_height_ft"] = cfg_dict.get("col_clear_height_ft") or cfg_dict.get("clear_height_ft") or cfg_dict.get("clear_height", 14)
        rc["width_ft"] = cfg_dict.get("col_width_ft") or cfg_dict.get("building_width_ft") or cfg_dict.get("width_ft", 40)
        rc["footing_ft"] = cfg_dict.get("col_footing_ft") or cfg_dict.get("footing_depth_ft") or cfg_dict.get("footing_depth", 10)
        rc["rebar_size"] = cfg_dict.get("col_rebar_size") or cfg_dict.get("rebar_size", "#9")
        rc["above_grade_ft"] = cfg_dict.get("col_above_grade_ft") or cfg_dict.get("above_grade", 8)
        rc["cut_allowance_in"] = cfg_dict.get("col_cut_allowance_in", 6)
        rc["reinforced"] = cfg_dict.get("col_reinforced", True)
        rc["job_code"] = job_code
        # Project info for title block
        rc["project_name"] = cfg_dict.get("project_name", "")
        rc["customer"] = cfg_dict.get("customer_name", "")
        # Frame data for column count calculation
        rc["num_frames"] = cfg_dict.get("n_frames") or cfg_dict.get("num_frames", 0)
        rc["frame_type"] = cfg_dict.get("frame_type", "2-post")
        rc["num_columns"] = cfg_dict.get("n_struct_cols") or cfg_dict.get("num_columns", 0)
        return rc


class SaveInteractivePdfHandler(BaseHandler):
    """POST /api/shop-drawings/save-interactive-pdf

    Receives a PDF file generated client-side from an interactive drawing
    (via jsPDF + svg2pdf.js), saves it to the project's pdfs/ directory,
    and updates the generation log so the dashboard card shows 'View PDF'.
    """
    def post(self):
        try:
            job_code = self.get_argument("job_code", "").strip()
            drawing_type = self.get_argument("drawing_type", "").strip()  # 'column' or 'rafter'
            source = self.get_argument("source", "interactive").strip()

            if not job_code or not drawing_type:
                self.write(json_encode({"ok": False, "error": "Missing job_code or drawing_type"}))
                return

            if drawing_type not in ("column", "rafter"):
                self.write(json_encode({"ok": False, "error": f"Invalid drawing_type: {drawing_type}"}))
                return

            # Get the uploaded PDF file
            file_info = self.request.files.get("pdf_file")
            if not file_info or len(file_info) == 0:
                self.write(json_encode({"ok": False, "error": "No pdf_file uploaded"}))
                return

            pdf_data = file_info[0]["body"]
            original_name = file_info[0].get("filename", f"{job_code}_{drawing_type.upper()}_INTERACTIVE.pdf")

            # Save PDF to project directory
            d = _shop_drawing_project_dir(job_code)
            pdfs_dir = os.path.join(d, "pdfs")
            os.makedirs(pdfs_dir, exist_ok=True)

            safe_jc = re.sub(r"[^a-zA-Z0-9_-]", "_", job_code)
            filename = f"{safe_jc}_{drawing_type.upper()}_INTERACTIVE.pdf"
            filepath = os.path.join(pdfs_dir, filename)

            with open(filepath, "wb") as f:
                f.write(pdf_data)

            # Update generation log so dashboard recognises this drawing
            log_path = os.path.join(pdfs_dir, f"{job_code}_generation_log.json")
            gen_log = {"files": [], "summary": {}}
            if os.path.isfile(log_path):
                with open(log_path) as f:
                    gen_log = json.load(f)

            # Find existing entry for this drawing type or create new one
            files = gen_log.get("files", [])
            found = False
            for entry in files:
                if entry.get("type") == drawing_type:
                    entry["filename"] = filename
                    entry["source"] = "interactive"
                    entry["size_bytes"] = len(pdf_data)
                    entry["description"] = f"{drawing_type.title()} Shop Drawing (Interactive)"
                    entry["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    found = True
                    break

            if not found:
                files.append({
                    "filename": filename,
                    "type": drawing_type,
                    "source": "interactive",
                    "description": f"{drawing_type.title()} Shop Drawing (Interactive)",
                    "size_bytes": len(pdf_data),
                    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
                gen_log["files"] = files

            with open(log_path, "w") as f:
                json.dump(gen_log, f, indent=2)

            self.write(json_encode({
                "ok": True,
                "filename": filename,
                "size_bytes": len(pdf_data),
                "source": "interactive",
            }))

        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({
                "ok": False,
                "error": str(e),
                "trace": traceback.format_exc()
            }))


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

            # Build ShopDrawingConfig
            cfg = ShopDrawingConfig.from_dict(cfg_dict)

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
    required_permission = "view_work_orders"

    def get(self, job_code):
        from templates.work_orders import WORK_ORDERS_HTML
        html = WORK_ORDERS_HTML.replace("{{JOB_CODE}}", job_code)
        self.render_with_nav(html, active_page="workorders", job_code=job_code)


class WorkOrderCreateHandler(BaseHandler):
    """POST /api/work-orders/create — Create a new work order from shop drawings."""
    required_permission = "create_work_orders"

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
    required_permission = "view_work_orders"

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
    required_permission = "view_work_orders"

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
    required_permission = "edit_work_orders"

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
    required_permission = "edit_work_orders"

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
    required_permission = "edit_work_orders"

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
    required_permission = "scan_start_finish"

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
    required_permission = "log_item_notes"

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
    required_permission = "view_work_orders"

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
    required_permission = "view_work_orders"

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
    required_permission = "view_work_orders"

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
    required_permission = "view_work_orders"

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

class ShopFloorPageHandler(BaseHandler):
    """GET /shop-floor — Shop floor fabrication dashboard."""
    required_permission = "view_work_orders"

    def get(self):
        from templates.shop_floor import SHOP_FLOOR_HTML
        self.render_with_nav(SHOP_FLOOR_HTML, active_page="shopfloor")


class ShopFloorDataHandler(BaseHandler):
    """GET /api/shop-floor/data — Aggregated shop floor metrics."""
    required_permission = "view_work_orders"

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
    required_permission = "view_own_work_items"

    def get(self, job_code):
        from templates.work_station import WORK_STATION_HTML
        user = self.get_current_user() or "local"
        html = (WORK_STATION_HTML
                .replace("{{JOB_CODE}}", job_code)
                .replace("{{USER_NAME}}", user))
        self.render_with_nav(html, active_page="workstation", job_code=job_code)


class WorkStationDataHandler(BaseHandler):
    """GET /api/work-station/data — Items + machine info for a job's work station."""
    required_permission = "view_own_work_items"

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
    required_permission = "view_own_work_items"

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
    required_permission = "edit_work_orders"

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


class WorkOrderPacketPDFHandler(BaseHandler):
    """GET /api/work-orders/packet/pdf — Generate printable work order packet PDF."""
    required_permission = "view_work_orders"

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
# PHASE 2: WORK ORDER ASSIGNMENT & QUEUE HANDLERS
# ─────────────────────────────────────────────

class WorkOrderAssignHandler(BaseHandler):
    """POST /api/work-orders/assign — Assign item to operator/welder. Foreman action."""
    required_permission = "assign_operators"

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            item_id = body.get("item_id", "").strip()
            assigned_to = body.get("assigned_to", "").strip()
            priority = int(body.get("priority", 50))

            if not job_code or not item_id or not assigned_to:
                self.write(json_encode({"ok": False, "error": "Missing job_code, item_id, or assigned_to"}))
                return

            assigned_by = self.current_username or "system"
            result = assign_item(SHOP_DRAWINGS_DIR, job_code, item_id,
                                 assigned_to, assigned_by, priority)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class WorkOrderReassignHandler(BaseHandler):
    """POST /api/work-orders/reassign — Reassign item to different operator. Foreman action."""
    required_permission = "assign_operators"

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            item_id = body.get("item_id", "").strip()
            new_operator = body.get("new_operator", "").strip()

            if not job_code or not item_id or not new_operator:
                self.write(json_encode({"ok": False, "error": "Missing required fields"}))
                return

            reassigned_by = self.current_username or "system"
            result = reassign_item(SHOP_DRAWINGS_DIR, job_code, item_id,
                                   new_operator, reassigned_by)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class WorkOrderReprioritizeHandler(BaseHandler):
    """POST /api/work-orders/reprioritize — Change item priority. Foreman action."""
    required_permission = "reprioritize_queue"

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            item_id = body.get("item_id", "").strip()
            new_priority = int(body.get("priority", 50))

            if not job_code or not item_id:
                self.write(json_encode({"ok": False, "error": "Missing job_code or item_id"}))
                return

            changed_by = self.current_username or "system"
            result = reprioritize_item(SHOP_DRAWINGS_DIR, job_code, item_id,
                                       new_priority, changed_by)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class WorkOrderStageHandler(BaseHandler):
    """POST /api/work-orders/stage — Mark item as staged. Laborer action."""
    required_permission = "scan_start_finish"

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            item_id = body.get("item_id", "").strip()

            if not job_code or not item_id:
                self.write(json_encode({"ok": False, "error": "Missing job_code or item_id"}))
                return

            staged_by = self.current_username or "system"
            result = stage_item(SHOP_DRAWINGS_DIR, job_code, item_id, staged_by)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class WorkOrderTransitionHandler(BaseHandler):
    """POST /api/work-orders/transition — Generic status transition.
    Used for QC, shipping, delivery, and install transitions."""
    required_permission = "view_work_orders"

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            item_id = body.get("item_id", "").strip()
            new_status = body.get("new_status", "").strip()
            notes = body.get("notes", "").strip()

            if not job_code or not item_id or not new_status:
                self.write(json_encode({"ok": False, "error": "Missing required fields"}))
                return

            # Permission gate based on target status
            perm = self.perm
            if new_status in [STATUS_QC_APPROVED, STATUS_QC_REJECTED, STATUS_QC_PENDING]:
                if not perm.can("perform_inspections") and not perm.can("sign_off_qc"):
                    self._deny_access()
                    return
            elif new_status in [STATUS_SHIPPED, STATUS_READY_TO_SHIP]:
                if not perm.can("build_loads") and not perm.can("view_shipping"):
                    self._deny_access()
                    return
            elif new_status == STATUS_FABRICATED:
                if not perm.can("scan_start_finish"):
                    self._deny_access()
                    return

            changed_by = self.current_username or "system"
            result = transition_item_status(SHOP_DRAWINGS_DIR, job_code, item_id,
                                            new_status, changed_by, notes)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class OperatorQueueHandler(BaseHandler):
    """GET /api/operator/queue — Get assigned items for current user (My Station / My Work)."""
    required_permission = "view_own_work_items"

    def get(self):
        try:
            username = self.get_query_argument("username", "").strip()
            if not username:
                username = self.current_username or ""

            if not username:
                self.write(json_encode({"ok": False, "error": "No username"}))
                return

            items = get_operator_queue(SHOP_DRAWINGS_DIR, username)

            # Split into active vs upcoming
            active = [i for i in items if i.get("status") == STATUS_IN_PROGRESS]
            upcoming = [i for i in items if i.get("status") in
                        [STATUS_STAGED, STATUS_STICKERS_PRINTED, STATUS_APPROVED,
                         STATUS_QC_REJECTED]]
            completed = [i for i in items if i.get("status") in
                         [STATUS_FABRICATED, STATUS_QC_PENDING, STATUS_QC_APPROVED,
                          STATUS_READY_TO_SHIP, STATUS_SHIPPED]]

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "username": username,
                "active": active,
                "upcoming": upcoming,
                "completed_today": completed,
                "total_assigned": len(items),
            }))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class MachineQueueHandler(BaseHandler):
    """GET /api/machine/queue?machine=WELDING — Get all items for a machine."""
    required_permission = "view_work_orders"

    def get(self):
        try:
            machine = self.get_query_argument("machine", "").strip()
            if not machine:
                self.write(json_encode({"ok": False, "error": "Missing machine parameter"}))
                return

            items = get_machine_queue(SHOP_DRAWINGS_DIR, machine)
            machine_info = MACHINE_TYPES.get(machine, {"label": machine, "operator_type": "unknown"})

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "machine": machine,
                "machine_info": machine_info,
                "items": items,
                "total": len(items),
            }))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ShopFloorSummaryHandler(BaseHandler):
    """GET /api/shop-floor/summary — Enhanced shop floor overview for foreman."""
    required_permission = "view_work_orders"

    def get(self):
        try:
            summary = get_shop_floor_summary(SHOP_DRAWINGS_DIR)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, **summary}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class WorkOrderBulkAssignHandler(BaseHandler):
    """POST /api/work-orders/bulk-assign — Assign multiple items at once. Foreman action."""
    required_permission = "assign_operators"

    def post(self):
        try:
            body = json_decode(self.request.body)
            assignments = body.get("assignments", [])
            # Each: {job_code, item_id, assigned_to, priority?}

            if not assignments:
                self.write(json_encode({"ok": False, "error": "No assignments provided"}))
                return

            assigned_by = self.current_username or "system"
            results = []
            for a in assignments:
                job_code = a.get("job_code", "").strip()
                item_id = a.get("item_id", "").strip()
                assigned_to = a.get("assigned_to", "").strip()
                priority = int(a.get("priority", 50))

                if not job_code or not item_id or not assigned_to:
                    results.append({"ok": False, "item_id": item_id, "error": "Missing fields"})
                    continue

                result = assign_item(SHOP_DRAWINGS_DIR, job_code, item_id,
                                     assigned_to, assigned_by, priority)
                result["item_id"] = item_id
                results.append(result)

            success = sum(1 for r in results if r.get("ok"))
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "total": len(results),
                "success": success,
                "failed": len(results) - success,
                "results": results,
            }))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class MyStationPageHandler(BaseHandler):
    """GET /work-station/mine — Operator's personal queue (My Station). Mobile-first."""
    required_permission = "view_own_work_items"

    def get(self):
        from templates.my_station import MY_STATION_HTML
        username = self.current_username or "local"
        display = self.get_display_name()
        roles_json = json.dumps(self.user_roles)
        html = (MY_STATION_HTML
                .replace("{{USERNAME}}", username)
                .replace("{{DISPLAY_NAME}}", display)
                .replace("{{USER_ROLES}}", roles_json))
        self.render_with_nav(html, active_page="workstation")


class ForemanPanelPageHandler(BaseHandler):
    """GET /shop-floor/assign — Foreman assignment panel."""
    required_permission = "assign_operators"

    def get(self):
        from templates.foreman_panel import FOREMAN_PANEL_HTML
        username = self.current_username or "local"
        display = self.get_display_name()
        html = (FOREMAN_PANEL_HTML
                .replace("{{USERNAME}}", username)
                .replace("{{DISPLAY_NAME}}", display))
        self.render_with_nav(html, active_page="shopfloor")


class StatusConfigHandler(BaseHandler):
    """GET /api/work-orders/status-config — Return status labels, colors, and flow map."""
    required_permission = "view_work_orders"

    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "statuses": VALID_STATUSES,
            "labels": STATUS_LABELS,
            "colors": STATUS_COLORS,
            "flow": {k: v for k, v in STATUS_FLOW.items()},
            "machines": {k: v for k, v in MACHINE_TYPES.items()},
        }))


# ─────────────────────────────────────────────
# SHIPPING & LOAD MANAGEMENT HANDLERS (Phase 4)
# ─────────────────────────────────────────────

class ShippingDashboardPageHandler(BaseHandler):
    """GET /shipping — Shipping dashboard page."""
    required_permission = "view_shipping"
    def get(self):
        from templates.shipping_page import SHIPPING_PAGE_HTML
        self.render_with_nav(SHIPPING_PAGE_HTML, active_page="shipping")


class LoadBuilderPageHandler(BaseHandler):
    """GET /shipping/load-builder — Load builder page."""
    required_permission = "build_loads"
    def get(self):
        from templates.load_builder_page import LOAD_BUILDER_PAGE_HTML
        self.render_with_nav(LOAD_BUILDER_PAGE_HTML, active_page="shipping")


class ShippingListAPIHandler(BaseHandler):
    """GET /api/shipping/loads — List all loads with optional filters."""
    required_permission = "view_shipping"
    def get(self):
        try:
            status = self.get_query_argument("status", "")
            job_code = self.get_query_argument("job_code", "")
            loads = list_loads(BASE_DIR, status=status, job_code=job_code)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "loads": [sl.to_dict() for sl in loads],
                "total": len(loads),
            }))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ShippingLoadDetailHandler(BaseHandler):
    """GET /api/shipping/load?load_id=X — Get full load details."""
    required_permission = "view_shipping"
    def get(self):
        load_id = self.get_query_argument("load_id", "")
        load = load_shipping_load(BASE_DIR, load_id)
        if not load:
            self.write(json_encode({"ok": False, "error": "Load not found"}))
            return
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "load": load.to_dict()}))


class ShippingCreateLoadHandler(BaseHandler):
    """POST /api/shipping/create — Create a new shipping load."""
    required_permission = "build_loads"
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            if not job_code:
                self.write(json_encode({"ok": False, "error": "job_code required"}))
                return
            load = create_load(
                BASE_DIR, job_code,
                created_by=self.current_username or "system",
                destination=body.get("destination", ""),
                carrier=body.get("carrier", ""),
                notes=body.get("notes", ""),
                special_instructions=body.get("special_instructions", ""),
            )
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "load": load.to_dict()}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ShippingAddItemsHandler(BaseHandler):
    """POST /api/shipping/add-items — Add WO items to a load."""
    required_permission = "build_loads"
    def post(self):
        try:
            body = json_decode(self.request.body)
            load_id = body.get("load_id", "").strip()
            items = body.get("items", [])
            if not load_id or not items:
                self.write(json_encode({"ok": False, "error": "load_id and items required"}))
                return
            result = add_items_to_load(
                BASE_DIR, SHOP_DRAWINGS_DIR, load_id, items,
                added_by=self.current_username or "system")
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ShippingRemoveItemHandler(BaseHandler):
    """POST /api/shipping/remove-item — Remove an item from a load."""
    required_permission = "build_loads"
    def post(self):
        try:
            body = json_decode(self.request.body)
            load_id = body.get("load_id", "").strip()
            item_id = body.get("item_id", "").strip()
            result = remove_item_from_load(
                BASE_DIR, SHOP_DRAWINGS_DIR, load_id, item_id,
                removed_by=self.current_username or "system")
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ShippingTransitionHandler(BaseHandler):
    """POST /api/shipping/transition — Transition a load's status (ship, deliver, complete)."""
    required_permission = "mark_shipped"
    def post(self):
        try:
            body = json_decode(self.request.body)
            load_id = body.get("load_id", "").strip()
            new_status = body.get("new_status", "").strip()
            notes = body.get("notes", "")

            if not load_id or not new_status:
                self.write(json_encode({"ok": False, "error": "load_id and new_status required"}))
                return

            result = transition_load_status(
                BASE_DIR, SHOP_DRAWINGS_DIR, load_id, new_status,
                changed_by=self.current_username or "system",
                notes=notes)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ShippingUpdateLoadHandler(BaseHandler):
    """POST /api/shipping/update — Update load metadata (carrier, destination, etc.)."""
    required_permission = "build_loads"
    def post(self):
        try:
            body = json_decode(self.request.body)
            load_id = body.get("load_id", "").strip()
            load = load_shipping_load(BASE_DIR, load_id)
            if not load:
                self.write(json_encode({"ok": False, "error": "Load not found"}))
                return
            for k in ["destination", "site_contact", "site_phone", "carrier",
                       "truck_number", "trailer_type", "driver_name", "driver_phone",
                       "notes", "special_instructions"]:
                if k in body:
                    setattr(load, k, body[k])
            save_load(BASE_DIR, load)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "load": load.to_dict()}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ShippingBOLHandler(BaseHandler):
    """POST /api/shipping/bol — Generate a BOL number for a load."""
    required_permission = "generate_bol"
    def post(self):
        try:
            body = json_decode(self.request.body)
            load_id = body.get("load_id", "").strip()
            result = generate_bol(BASE_DIR, load_id,
                                  generated_by=self.current_username or "system")
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ShippableItemsHandler(BaseHandler):
    """GET /api/shipping/shippable-items — Items ready to be loaded (qc_approved, not on a load)."""
    required_permission = "view_shipping"
    def get(self):
        try:
            job_code = self.get_query_argument("job_code", "")
            items = get_shippable_items(SHOP_DRAWINGS_DIR, job_code=job_code)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "items": items, "total": len(items)}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ShippingSummaryHandler(BaseHandler):
    """GET /api/shipping/summary — Shipping dashboard metrics."""
    required_permission = "view_shipping"
    def get(self):
        try:
            summary = get_shipping_summary(BASE_DIR)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "summary": summary}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ShippingConfigHandler(BaseHandler):
    """GET /api/shipping/config — Return load status labels, colors, flow."""
    required_permission = "view_shipping"
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "statuses": LOAD_STATUSES,
            "labels": LOAD_STATUS_LABELS,
            "colors": LOAD_STATUS_COLORS,
            "flow": LOAD_FLOW,
        }))


# ─────────────────────────────────────────────
# FIELD OPERATIONS & INSTALLATION (Phase 5)
# ─────────────────────────────────────────────

class FieldDashboardPageHandler(BaseHandler):
    """GET /field — Field operations dashboard (mobile-friendly)."""
    required_permission = "view_field_reports"
    def get(self):
        from templates.field_ops_page import FIELD_OPS_PAGE_HTML
        self.render_with_nav(FIELD_OPS_PAGE_HTML, active_page="field")


class InstallTrackerPageHandler(BaseHandler):
    """GET /field/install-tracker — Installation tracking dashboard."""
    required_permission = "view_field_reports"
    def get(self):
        from templates.install_tracker_page import INSTALL_TRACKER_PAGE_HTML
        self.render_with_nav(INSTALL_TRACKER_PAGE_HTML, active_page="field")


class ProjectCompletionPageHandler(BaseHandler):
    """GET /field/completion — Project completion dashboard."""
    required_permission = "view_field_reports"
    def get(self):
        from templates.project_completion_page import PROJECT_COMPLETION_PAGE_HTML
        self.render_with_nav(PROJECT_COMPLETION_PAGE_HTML, active_page="field")


class PunchListAPIHandler(BaseHandler):
    """GET /api/field/punch-list — List punch items, optionally by project."""
    required_permission = "view_field_reports"
    def get(self):
        try:
            job_code = self.get_argument("job_code", "")
            status = self.get_argument("status", "")
            if job_code:
                items = load_punch_items(BASE_DIR, job_code, status=status)
            else:
                items = load_all_punch_items(BASE_DIR)
                if status:
                    items = [i for i in items if i.status == status]
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "items": [i.to_dict() for i in items],
                "count": len(items),
            }))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class PunchCreateHandler(BaseHandler):
    """POST /api/field/punch-list/create — Create a new punch list item."""
    required_permission = "create_punch_list"
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            title = body.get("title", "").strip()
            if not job_code or not title:
                self.write(json_encode({"ok": False, "error": "job_code and title required"}))
                return
            punch = create_punch_item(
                BASE_DIR, job_code,
                created_by=self.current_username or "system",
                title=title,
                description=body.get("description", ""),
                priority=body.get("priority", "medium"),
                category=body.get("category", "other"),
                item_id=body.get("item_id", ""),
                ship_mark=body.get("ship_mark", ""),
                load_id=body.get("load_id", ""),
                location=body.get("location", ""),
                assigned_to=body.get("assigned_to", ""),
                photos=body.get("photos", []),
            )
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "punch": punch.to_dict()}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class PunchTransitionHandler(BaseHandler):
    """POST /api/field/punch-list/transition — Transition punch item status."""
    required_permission = "create_punch_list"
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            punch_id = body.get("punch_id", "").strip()
            new_status = body.get("new_status", "").strip()
            if not all([job_code, punch_id, new_status]):
                self.write(json_encode({"ok": False, "error": "job_code, punch_id, and new_status required"}))
                return
            result = transition_punch_status(
                BASE_DIR, job_code, punch_id, new_status,
                changed_by=self.current_username or "system",
                notes=body.get("notes", ""))
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class PunchDetailHandler(BaseHandler):
    """GET /api/field/punch-list/detail — Get a specific punch item."""
    required_permission = "view_field_reports"
    def get(self):
        job_code = self.get_argument("job_code", "")
        punch_id = self.get_argument("punch_id", "")
        if not job_code or not punch_id:
            self.write(json_encode({"ok": False, "error": "job_code and punch_id required"}))
            return
        punch = load_punch_item(BASE_DIR, job_code, punch_id)
        if not punch:
            self.write(json_encode({"ok": False, "error": "Punch item not found"}))
            return
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "punch": punch.to_dict()}))


class InstallConfirmHandler(BaseHandler):
    """POST /api/field/confirm-install — Confirm item installation."""
    required_permission = "create_punch_list"
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            item_id = body.get("item_id", "").strip()
            if not job_code or not item_id:
                self.write(json_encode({"ok": False, "error": "job_code and item_id required"}))
                return
            result = confirm_installation(
                BASE_DIR, SHOP_DRAWINGS_DIR, job_code, item_id,
                installed_by=self.current_username or "system",
                location=body.get("location", ""),
                notes=body.get("notes", ""),
                photos=body.get("photos", []))
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class DailyReportSubmitHandler(BaseHandler):
    """POST /api/field/daily-report — Submit a daily field report."""
    required_permission = "submit_daily_report"
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            if not job_code:
                self.write(json_encode({"ok": False, "error": "job_code required"}))
                return
            result = submit_daily_report(
                BASE_DIR, SHOP_DRAWINGS_DIR, job_code,
                submitted_by=self.current_username or "system",
                date=body.get("date", ""),
                crew_count=body.get("crew_count", 0),
                crew_names=body.get("crew_names", []),
                hours_worked=body.get("hours_worked", 0.0),
                work_summary=body.get("work_summary", ""),
                items_installed=body.get("items_installed", []),
                equipment_used=body.get("equipment_used", []),
                weather=body.get("weather", ""),
                temperature_f=body.get("temperature_f", 0.0),
                delays=body.get("delays", ""),
                safety_incidents=body.get("safety_incidents", ""),
                photos=body.get("photos", []),
                notes=body.get("notes", ""),
                issues=body.get("issues", ""))
            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class DailyReportListHandler(BaseHandler):
    """GET /api/field/daily-reports — List daily reports for a project."""
    required_permission = "view_field_reports"
    def get(self):
        try:
            job_code = self.get_argument("job_code", "")
            if not job_code:
                self.write(json_encode({"ok": False, "error": "job_code required"}))
                return
            reports = load_daily_reports(BASE_DIR, job_code)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "reports": [r.to_dict() for r in reports],
                "count": len(reports),
            }))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class InstallationRecordsHandler(BaseHandler):
    """GET /api/field/installations — List installation records for a project."""
    required_permission = "view_field_reports"
    def get(self):
        try:
            job_code = self.get_argument("job_code", "")
            if not job_code:
                self.write(json_encode({"ok": False, "error": "job_code required"}))
                return
            records = load_installation_records(BASE_DIR, job_code)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "records": [r.to_dict() for r in records],
                "count": len(records),
            }))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class ProjectCompletionAPIHandler(BaseHandler):
    """GET /api/field/project-completion — Get completion metrics for a project."""
    required_permission = "view_field_reports"
    def get(self):
        try:
            job_code = self.get_argument("job_code", "")
            if not job_code:
                self.write(json_encode({"ok": False, "error": "job_code required"}))
                return
            completion = get_project_completion(SHOP_DRAWINGS_DIR, BASE_DIR, job_code)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "completion": completion}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class FieldSummaryHandler(BaseHandler):
    """GET /api/field/summary — Summary metrics across all projects."""
    required_permission = "view_field_reports"
    def get(self):
        try:
            summary = get_field_summary(SHOP_DRAWINGS_DIR, BASE_DIR)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "summary": summary}))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class FieldConfigHandler(BaseHandler):
    """GET /api/field/config — Return punch list constants."""
    required_permission = "view_field_reports"
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "punch_statuses": PUNCH_STATUSES,
            "punch_status_labels": PUNCH_STATUS_LABELS,
            "punch_priorities": PUNCH_PRIORITIES,
            "punch_categories": PUNCH_CATEGORIES,
            "punch_category_labels": PUNCH_CATEGORY_LABELS,
            "punch_flow": PUNCH_FLOW,
        }))


# ─────────────────────────────────────────────
# PHASE 6: REPORTING & ANALYTICS
# ─────────────────────────────────────────────

class ProductionMetricsPageHandler(BaseHandler):
    """GET /reports/production — Production Metrics dashboard page."""
    required_permission = "view_financials"
    def get(self):
        from templates.production_metrics_page import PRODUCTION_METRICS_PAGE_HTML
        self.write(PRODUCTION_METRICS_PAGE_HTML)


class ExecutiveSummaryPageHandler(BaseHandler):
    """GET /reports/executive — Executive Summary dashboard page."""
    required_permission = "view_financials"
    def get(self):
        from templates.executive_summary_page import EXECUTIVE_SUMMARY_PAGE_HTML
        self.write(EXECUTIVE_SUMMARY_PAGE_HTML)


class ReportListHandler(BaseHandler):
    """GET /api/reports — List available report types."""
    required_permission = "view_financials"
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "reports": list_available_reports(),
        }))


class ReportGenerateHandler(BaseHandler):
    """POST /api/reports/generate — Generate a report by type."""
    required_permission = "view_financials"
    def post(self):
        self.set_header("Content-Type", "application/json")
        data = json_decode(self.request.body)
        report_type = data.get("report_type", "")
        days_back = int(data.get("days_back", 30))

        result = generate_report(
            report_type,
            wo_base_dir=SHOP_DRAWINGS_DIR,
            shipping_base_dir=DATA_DIR,
            field_base_dir=DATA_DIR,
            days_back=days_back,
        )
        self.write(json_encode(result))


class ProductionMetricsAPIHandler(BaseHandler):
    """GET /api/reports/production — Production metrics data."""
    required_permission = "view_financials"
    def get(self):
        self.set_header("Content-Type", "application/json")
        days_back = int(self.get_argument("days_back", "30"))
        try:
            data = get_production_metrics(
                SHOP_DRAWINGS_DIR, DATA_DIR, DATA_DIR,
                days_back=days_back,
            )
            self.write(json_encode({"ok": True, "report": data}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class ExecutiveSummaryAPIHandler(BaseHandler):
    """GET /api/reports/executive — Executive summary data."""
    required_permission = "view_financials"
    def get(self):
        self.set_header("Content-Type", "application/json")
        try:
            data = get_executive_summary(SHOP_DRAWINGS_DIR, DATA_DIR, DATA_DIR)
            self.write(json_encode({"ok": True, "report": data}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class OperatorPerformanceAPIHandler(BaseHandler):
    """GET /api/reports/operators — Operator performance data."""
    required_permission = "view_financials"
    def get(self):
        self.set_header("Content-Type", "application/json")
        days_back = int(self.get_argument("days_back", "30"))
        try:
            data = get_operator_performance(SHOP_DRAWINGS_DIR, days_back=days_back)
            self.write(json_encode({"ok": True, "report": data}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class ProjectStatusReportAPIHandler(BaseHandler):
    """GET /api/reports/project-status — Per-project status breakdown."""
    required_permission = "view_project_pnl"
    def get(self):
        self.set_header("Content-Type", "application/json")
        try:
            data = get_project_status_report(SHOP_DRAWINGS_DIR, DATA_DIR, DATA_DIR)
            self.write(json_encode({"ok": True, "report": data}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class DeliveryAnalysisAPIHandler(BaseHandler):
    """GET /api/reports/delivery — Delivery analysis data."""
    required_permission = "view_financials"
    def get(self):
        self.set_header("Content-Type", "application/json")
        try:
            data = get_delivery_analysis(DATA_DIR, DATA_DIR, SHOP_DRAWINGS_DIR)
            self.write(json_encode({"ok": True, "report": data}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class QCAnalysisAPIHandler(BaseHandler):
    """GET /api/reports/qc — QC analysis data."""
    required_permission = "view_financials"
    def get(self):
        self.set_header("Content-Type", "application/json")
        try:
            data = get_qc_analysis(SHOP_DRAWINGS_DIR)
            self.write(json_encode({"ok": True, "report": data}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class ReportConfigHandler(BaseHandler):
    """GET /api/reports/config — Return report constants."""
    required_permission = "view_financials"
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "report_types": REPORT_TYPES,
            "report_labels": REPORT_LABELS,
        }))


# ─────────────────────────────────────────────
# PHASE 7: ACTIVITY FEED, AUDIT TRAIL & NOTIFICATIONS
# ─────────────────────────────────────────────

class ActivityFeedPageHandler(BaseHandler):
    """GET /activity — Activity Feed & Audit Trail dashboard page."""
    required_permission = "view_audit_log"
    def get(self):
        from templates.activity_feed_page import ACTIVITY_FEED_PAGE_HTML
        self.write(ACTIVITY_FEED_PAGE_HTML)


class ActivityEventsAPIHandler(BaseHandler):
    """GET /api/activity/events — Query activity events with filters."""
    required_permission = "view_audit_log"
    def get(self):
        self.set_header("Content-Type", "application/json")
        category = self.get_argument("category", "")
        event_type = self.get_argument("event_type", "")
        severity = self.get_argument("severity", "")
        job_code = self.get_argument("job_code", "")
        actor = self.get_argument("actor", "")
        since = self.get_argument("since", "")
        limit = int(self.get_argument("limit", "100"))
        offset = int(self.get_argument("offset", "0"))

        result = get_events(
            DATA_DIR, category=category, event_type=event_type,
            severity=severity, job_code=job_code, actor=actor,
            since=since, limit=limit, offset=offset,
        )
        self.write(json_encode({"ok": True, **result}))


class ActivityFeedAPIHandler(BaseHandler):
    """GET /api/activity/feed — Recent activity feed."""
    required_permission = "view_dashboard"
    def get(self):
        self.set_header("Content-Type", "application/json")
        limit = int(self.get_argument("limit", "50"))
        job_code = self.get_argument("job_code", "")
        events = get_activity_feed(DATA_DIR, limit=limit, job_code=job_code)
        self.write(json_encode({"ok": True, "events": events}))


class ActivityStatsAPIHandler(BaseHandler):
    """GET /api/activity/stats — Event statistics."""
    required_permission = "view_audit_log"
    def get(self):
        self.set_header("Content-Type", "application/json")
        days = int(self.get_argument("days", "7"))
        stats = get_event_stats(DATA_DIR, days_back=days)
        self.write(json_encode({"ok": True, "stats": stats}))


class AlertRulesAPIHandler(BaseHandler):
    """GET/POST /api/activity/rules — List or create alert rules."""
    required_permission = "view_audit_log"
    def get(self):
        self.set_header("Content-Type", "application/json")
        rules = list_alert_rules(DATA_DIR)
        self.write(json_encode({"ok": True, "rules": rules}))

    def post(self):
        self.set_header("Content-Type", "application/json")
        data = json_decode(self.request.body)
        user = self.get_current_user()
        username = user.get("username", "unknown") if isinstance(user, dict) else "unknown"

        rule = create_alert_rule(
            DATA_DIR, name=data.get("name", ""),
            created_by=username,
            event_types=data.get("event_types", []),
            categories=data.get("categories", []),
            severities=data.get("severities", []),
            job_codes=data.get("job_codes", []),
            notify_roles=data.get("notify_roles", []),
            notify_users=data.get("notify_users", []),
        )
        self.write(json_encode({"ok": True, "rule": rule.to_dict()}))


class AlertRuleUpdateHandler(BaseHandler):
    """POST /api/activity/rules/update — Update an alert rule."""
    required_permission = "view_audit_log"
    def post(self):
        self.set_header("Content-Type", "application/json")
        data = json_decode(self.request.body)
        rule_id = data.pop("rule_id", "")
        result = update_alert_rule(DATA_DIR, rule_id, **data)
        self.write(json_encode(result))


class AlertRuleDeleteHandler(BaseHandler):
    """POST /api/activity/rules/delete — Delete an alert rule."""
    required_permission = "view_audit_log"
    def post(self):
        self.set_header("Content-Type", "application/json")
        data = json_decode(self.request.body)
        result = delete_alert_rule(DATA_DIR, data.get("rule_id", ""))
        self.write(json_encode(result))


class NotificationsAPIHandler(BaseHandler):
    """GET /api/notifications — Get notifications for current user."""
    required_permission = "view_dashboard"
    def get(self):
        self.set_header("Content-Type", "application/json")
        user = self.get_current_user()
        username = user.get("username", "unknown") if isinstance(user, dict) else "unknown"
        unread = self.get_argument("unread_only", "false").lower() == "true"
        limit = int(self.get_argument("limit", "50"))

        notifs = get_notifications(DATA_DIR, username, unread_only=unread, limit=limit)
        count = get_unread_count(DATA_DIR, username)
        self.write(json_encode({
            "ok": True,
            "notifications": notifs,
            "unread_count": count,
        }))


class NotificationReadHandler(BaseHandler):
    """POST /api/notifications/read — Mark notification as read."""
    required_permission = "view_dashboard"
    def post(self):
        self.set_header("Content-Type", "application/json")
        data = json_decode(self.request.body)
        user = self.get_current_user()
        username = user.get("username", "unknown") if isinstance(user, dict) else "unknown"
        result = mark_notification_read(DATA_DIR, data.get("notification_id", ""), username)
        self.write(json_encode(result))


class NotificationReadAllHandler(BaseHandler):
    """POST /api/notifications/read-all — Mark all notifications as read."""
    required_permission = "view_dashboard"
    def post(self):
        self.set_header("Content-Type", "application/json")
        user = self.get_current_user()
        username = user.get("username", "unknown") if isinstance(user, dict) else "unknown"
        result = mark_all_read(DATA_DIR, username)
        self.write(json_encode(result))


class NotificationClearHandler(BaseHandler):
    """POST /api/notifications/clear — Clear all notifications for user."""
    required_permission = "view_dashboard"
    def post(self):
        self.set_header("Content-Type", "application/json")
        user = self.get_current_user()
        username = user.get("username", "unknown") if isinstance(user, dict) else "unknown"
        result = clear_notifications(DATA_DIR, username)
        self.write(json_encode(result))


class ActivityConfigHandler(BaseHandler):
    """GET /api/activity/config — Return activity/event constants."""
    required_permission = "view_audit_log"
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "event_categories": EVENT_CATEGORIES,
            "category_labels": CATEGORY_LABELS,
            "severity_levels": SEVERITY_LEVELS,
            "severity_labels": SEVERITY_LABELS,
            "event_types": EVENT_TYPES,
            "event_labels": EVENT_LABELS,
        }))


# ─────────────────────────────────────────────
# PHASE 8 — Scheduling & Production Planning
# ─────────────────────────────────────────────

class ProductionSchedulePageHandler(BaseHandler):
    """GET /schedule — Production Schedule dashboard."""
    required_permission = "view_schedule"
    def get(self):
        from templates.production_schedule_page import PRODUCTION_SCHEDULE_PAGE_HTML
        self.set_header("Content-Type", "text/html")
        self.write(PRODUCTION_SCHEDULE_PAGE_HTML)


class ScheduleListAPIHandler(BaseHandler):
    """GET /api/schedule/list — List all production schedules."""
    required_permission = "view_schedule"
    def get(self):
        schedules = list_schedules(DATA_DIR)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "schedules": [s.to_dict() for s in schedules],
        }))


class ScheduleCreateHandler(BaseHandler):
    """POST /api/schedule/create — Create a new production schedule."""
    required_permission = "manage_schedule"
    def post(self):
        data = json.loads(self.request.body)
        name = data.get("name", "").strip()
        start_date = data.get("start_date", "")
        end_date = data.get("end_date", "")
        if not name or not start_date or not end_date:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "name, start_date, end_date required"}))
            return
        ps = create_schedule(
            DATA_DIR, name=name, start_date=start_date, end_date=end_date,
            created_by=self.current_user, description=data.get("description", ""),
            job_codes=data.get("job_codes", []),
        )
        self.write(json_encode({"ok": True, "schedule": ps.to_dict()}))


class ScheduleUpdateHandler(BaseHandler):
    """POST /api/schedule/update — Update a production schedule."""
    required_permission = "manage_schedule"
    def post(self):
        data = json.loads(self.request.body)
        schedule_id = data.get("schedule_id", "")
        if not schedule_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "schedule_id required"}))
            return
        kwargs = {}
        for k in ["name", "description", "status", "start_date", "end_date", "job_codes"]:
            if k in data:
                kwargs[k] = data[k]
        ps = update_schedule(DATA_DIR, schedule_id, **kwargs)
        if not ps:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Schedule not found"}))
            return
        self.write(json_encode({"ok": True, "schedule": ps.to_dict()}))


class ScheduleDeleteHandler(BaseHandler):
    """POST /api/schedule/delete — Delete a production schedule."""
    required_permission = "manage_schedule"
    def post(self):
        data = json.loads(self.request.body)
        schedule_id = data.get("schedule_id", "")
        if not schedule_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "schedule_id required"}))
            return
        ok = delete_schedule(DATA_DIR, schedule_id)
        if not ok:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Schedule not found"}))
            return
        self.write(json_encode({"ok": True}))


class ScheduleEntryAddHandler(BaseHandler):
    """POST /api/schedule/entry/add — Add an entry to the schedule."""
    required_permission = "manage_schedule"
    def post(self):
        data = json.loads(self.request.body)
        required = ["job_code", "work_order_id", "item_id", "machine", "scheduled_date", "estimated_minutes"]
        for f in required:
            if not data.get(f):
                self.set_status(400)
                self.write(json_encode({"ok": False, "error": f"{f} required"}))
                return
        entry = add_schedule_entry(
            DATA_DIR,
            job_code=data["job_code"],
            work_order_id=data["work_order_id"],
            item_id=data["item_id"],
            machine=data["machine"],
            scheduled_date=data["scheduled_date"],
            estimated_minutes=int(data["estimated_minutes"]),
            created_by=self.current_user,
            priority=int(data.get("priority", PRIORITY_NORMAL)),
            assigned_to=data.get("assigned_to", ""),
            ship_mark=data.get("ship_mark", ""),
            component_type=data.get("component_type", ""),
            notes=data.get("notes", ""),
            schedule_id=data.get("schedule_id", ""),
        )
        self.write(json_encode({"ok": True, "entry": entry.to_dict()}))


class ScheduleEntryUpdateHandler(BaseHandler):
    """POST /api/schedule/entry/update — Update a schedule entry."""
    required_permission = "manage_schedule"
    def post(self):
        data = json.loads(self.request.body)
        entry_id = data.get("entry_id", "")
        if not entry_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "entry_id required"}))
            return
        kwargs = {}
        for k in ["machine", "scheduled_date", "estimated_minutes", "priority",
                   "sequence", "assigned_to", "status", "notes"]:
            if k in data:
                kwargs[k] = data[k]
        entry = update_schedule_entry(DATA_DIR, entry_id, **kwargs)
        if not entry:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Entry not found"}))
            return
        self.write(json_encode({"ok": True, "entry": entry.to_dict()}))


class ScheduleEntryDeleteHandler(BaseHandler):
    """POST /api/schedule/entry/delete — Delete a schedule entry."""
    required_permission = "manage_schedule"
    def post(self):
        data = json.loads(self.request.body)
        entry_id = data.get("entry_id", "")
        if not entry_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "entry_id required"}))
            return
        ok = delete_schedule_entry(DATA_DIR, entry_id)
        if not ok:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Entry not found"}))
            return
        self.write(json_encode({"ok": True}))


class ScheduleDateAPIHandler(BaseHandler):
    """GET /api/schedule/date — Get entries for a specific date."""
    required_permission = "view_schedule"
    def get(self):
        date = self.get_argument("date", "")
        machine = self.get_argument("machine", "")
        if not date:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "date required"}))
            return
        entries = get_entries_for_date(DATA_DIR, date, machine=machine)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "date": date,
            "entries": [e.to_dict() for e in entries],
        }))


class ScheduleRangeAPIHandler(BaseHandler):
    """GET /api/schedule/range — Get entries for a date range."""
    required_permission = "view_schedule"
    def get(self):
        start = self.get_argument("start", "")
        end = self.get_argument("end", "")
        machine = self.get_argument("machine", "")
        job_code = self.get_argument("job_code", "")
        if not start or not end:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "start and end required"}))
            return
        entries = get_entries_for_range(DATA_DIR, start, end,
                                        machine=machine, job_code=job_code)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "entries": [e.to_dict() for e in entries],
        }))


class CapacityAPIHandler(BaseHandler):
    """GET /api/schedule/capacity — Get machine capacity configuration."""
    required_permission = "view_schedule"
    def get(self):
        capacity = get_machine_capacity(DATA_DIR)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "capacity": capacity}))


class CapacityUpdateHandler(BaseHandler):
    """POST /api/schedule/capacity/update — Update machine capacity."""
    required_permission = "manage_schedule"
    def post(self):
        data = json.loads(self.request.body)
        machine = data.get("machine", "")
        if not machine:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "machine required"}))
            return
        kwargs = {}
        for k in ["shift_hours", "shifts_per_day", "efficiency_factor", "enabled"]:
            if k in data:
                kwargs[k] = data[k]
        result = update_machine_capacity(DATA_DIR, machine, **kwargs)
        if not result:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Machine not found"}))
            return
        self.write(json_encode({"ok": True, "machine_capacity": result}))


class CapacityUsageAPIHandler(BaseHandler):
    """GET /api/schedule/capacity/usage — Get daily capacity usage."""
    required_permission = "view_schedule"
    def get(self):
        date = self.get_argument("date", "")
        if not date:
            import datetime as dt
            date = dt.date.today().isoformat()
        usage = get_daily_capacity_usage(DATA_DIR, date)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "date": date, "usage": usage}))


class CapacityForecastAPIHandler(BaseHandler):
    """GET /api/schedule/capacity/forecast — Get capacity forecast."""
    required_permission = "view_schedule"
    def get(self):
        days = int(self.get_argument("days", "14"))
        forecast = get_capacity_forecast(DATA_DIR, days_ahead=days)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "forecast": forecast}))


class AutoScheduleHandler(BaseHandler):
    """POST /api/schedule/auto — Auto-schedule unscheduled items for a job."""
    required_permission = "manage_schedule"
    def post(self):
        data = json.loads(self.request.body)
        job_code = data.get("job_code", "")
        start_date = data.get("start_date", "")
        if not job_code or not start_date:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code and start_date required"}))
            return
        wo_base = os.path.join(DATA_DIR, "shop_drawings")
        priority = int(data.get("priority", PRIORITY_NORMAL))
        entries = auto_schedule_job(
            DATA_DIR, wo_base, job_code, start_date,
            created_by=self.current_user, priority=priority,
        )
        self.write(json_encode({
            "ok": True,
            "entries_created": len(entries),
            "entries": [e.to_dict() for e in entries],
        }))


class ScheduleSummaryAPIHandler(BaseHandler):
    """GET /api/schedule/summary — Get overall scheduling summary."""
    required_permission = "view_schedule"
    def get(self):
        summary = get_schedule_summary(DATA_DIR)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "summary": summary}))


class JobTimelineAPIHandler(BaseHandler):
    """GET /api/schedule/job-timeline — Get timeline for a job."""
    required_permission = "view_schedule"
    def get(self):
        job_code = self.get_argument("job_code", "")
        if not job_code:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code required"}))
            return
        timeline = get_job_timeline(DATA_DIR, job_code)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "timeline": timeline}))


class MachineScheduleAPIHandler(BaseHandler):
    """GET /api/schedule/machine — Get detailed schedule for a machine."""
    required_permission = "view_schedule"
    def get(self):
        machine = self.get_argument("machine", "")
        days = int(self.get_argument("days", "7"))
        if not machine:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "machine required"}))
            return
        schedule = get_machine_schedule(DATA_DIR, machine, days_ahead=days)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "schedule": schedule}))


class BottleneckForecastAPIHandler(BaseHandler):
    """GET /api/schedule/bottlenecks — Get bottleneck forecast."""
    required_permission = "view_schedule"
    def get(self):
        days = int(self.get_argument("days", "14"))
        bottlenecks = get_bottleneck_forecast(DATA_DIR, days_ahead=days)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "bottlenecks": bottlenecks}))


class OverdueEntriesAPIHandler(BaseHandler):
    """GET /api/schedule/overdue — Get overdue schedule entries."""
    required_permission = "view_schedule"
    def get(self):
        overdue = get_overdue_entries(DATA_DIR)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "overdue": [e.to_dict() for e in overdue],
            "count": len(overdue),
        }))


class ScheduleConfigHandler(BaseHandler):
    """GET /api/schedule/config — Return scheduling constants."""
    required_permission = "view_schedule"
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "schedule_statuses": SCHED_STATUSES,
            "schedule_status_labels": SCHED_STATUS_LABELS,
            "priority_labels": PRIORITY_LABELS,
            "priority_colors": PRIORITY_COLORS,
            "machine_types": {k: v["label"] for k, v in MACHINE_TYPES.items()},
        }))


# ─────────────────────────────────────────────
# PHASE 9 — Document Management & Drawing Revisions
# ─────────────────────────────────────────────

class DocumentManagementPageHandler(BaseHandler):
    """GET /documents — Document Management dashboard."""
    required_permission = "view_shop_drawings"
    def get(self):
        from templates.document_management_page import DOCUMENT_MANAGEMENT_PAGE_HTML
        self.set_header("Content-Type", "text/html")
        self.write(DOCUMENT_MANAGEMENT_PAGE_HTML)


# ── Drawing Revisions ─────────────────────────────────────────────────

class RevisionListAPIHandler(BaseHandler):
    """GET /api/documents/revisions — List drawing revisions."""
    required_permission = "view_shop_drawings"
    def get(self):
        job_code = self.get_argument("job_code", "")
        category = self.get_argument("category", "")
        status = self.get_argument("status", "")
        drawing_number = self.get_argument("drawing_number", "")
        revs = list_revisions(DATA_DIR, job_code=job_code, category=category,
                              status=status, drawing_number=drawing_number)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "revisions": [r.to_dict() for r in revs],
            "count": len(revs),
        }))


class RevisionDetailAPIHandler(BaseHandler):
    """GET /api/documents/revision?revision_id=X — Get single revision."""
    required_permission = "view_shop_drawings"
    def get(self):
        rev_id = self.get_argument("revision_id", "")
        if not rev_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "revision_id required"}))
            return
        rev = get_revision(DATA_DIR, rev_id)
        if not rev:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Revision not found"}))
            return
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "revision": rev.to_dict()}))


class RevisionCreateHandler(BaseHandler):
    """POST /api/documents/revision/create — Create a new drawing revision."""
    required_permission = "edit_shop_drawings"
    def post(self):
        data = json.loads(self.request.body)
        job_code = data.get("job_code", "").strip()
        drawing_number = data.get("drawing_number", "").strip()
        title = data.get("title", "").strip()
        if not job_code or not drawing_number or not title:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code, drawing_number, title required"}))
            return
        rev = create_revision(
            DATA_DIR, job_code=job_code, drawing_number=drawing_number,
            title=title, revision=data.get("revision", ""),
            created_by=self.current_user,
            category=data.get("category", "shop_drawings"),
            filename=data.get("filename", ""),
            file_size=data.get("file_size", 0),
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
        )
        self.write(json_encode({"ok": True, "revision": rev.to_dict()}))


class RevisionTransitionHandler(BaseHandler):
    """POST /api/documents/revision/transition — Change revision status."""
    required_permission = "approve_drawings"
    def post(self):
        data = json.loads(self.request.body)
        rev_id = data.get("revision_id", "")
        new_status = data.get("status", "")
        if not rev_id or not new_status:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "revision_id and status required"}))
            return
        rev = transition_revision(
            DATA_DIR, rev_id, new_status, actor=self.current_user,
            reason=data.get("rejection_reason", ""),
        )
        if not rev:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "Invalid transition or revision not found"}))
            return
        self.write(json_encode({"ok": True, "revision": rev.to_dict()}))


class RevisionHistoryAPIHandler(BaseHandler):
    """GET /api/documents/revision/history — Revision history for a drawing."""
    required_permission = "view_shop_drawings"
    def get(self):
        job_code = self.get_argument("job_code", "")
        drawing_number = self.get_argument("drawing_number", "")
        if not job_code or not drawing_number:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code and drawing_number required"}))
            return
        history = get_revision_history(DATA_DIR, job_code, drawing_number)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "history": [r.to_dict() for r in history],
            "count": len(history),
        }))


class RevisionLatestAPIHandler(BaseHandler):
    """GET /api/documents/revision/latest — Latest revision for a drawing."""
    required_permission = "view_shop_drawings"
    def get(self):
        job_code = self.get_argument("job_code", "")
        drawing_number = self.get_argument("drawing_number", "")
        if not job_code or not drawing_number:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code and drawing_number required"}))
            return
        rev = get_latest_revision(DATA_DIR, job_code, drawing_number)
        if not rev:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "No revisions found"}))
            return
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "revision": rev.to_dict()}))


# ── RFIs ──────────────────────────────────────────────────────────────

class RFIListAPIHandler(BaseHandler):
    """GET /api/documents/rfis — List RFIs."""
    required_permission = "view_shop_drawings"
    def get(self):
        job_code = self.get_argument("job_code", "")
        status = self.get_argument("status", "")
        rfis = list_rfis(DATA_DIR, job_code=job_code, status=status)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "rfis": [r.to_dict() for r in rfis],
            "count": len(rfis),
        }))


class RFIDetailAPIHandler(BaseHandler):
    """GET /api/documents/rfi?rfi_id=X — Get a single RFI."""
    required_permission = "view_shop_drawings"
    def get(self):
        rfi_id = self.get_argument("rfi_id", "")
        if not rfi_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "rfi_id required"}))
            return
        rfi = get_rfi(DATA_DIR, rfi_id)
        if not rfi:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "RFI not found"}))
            return
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "rfi": rfi.to_dict()}))


class RFICreateHandler(BaseHandler):
    """POST /api/documents/rfi/create — Create a new RFI."""
    required_permission = "edit_shop_drawings"
    def post(self):
        data = json.loads(self.request.body)
        job_code = data.get("job_code", "").strip()
        subject = data.get("subject", "").strip()
        question = data.get("question", "").strip()
        if not job_code or not subject or not question:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code, subject, question required"}))
            return
        rfi = create_rfi(
            DATA_DIR, job_code=job_code, subject=subject, question=question,
            created_by=self.current_user,
            priority=data.get("priority", "normal"),
            drawing_ref=data.get("drawing_ref", ""),
            revision_ref=data.get("revision_ref", ""),
            impact_description=data.get("impact_description", ""),
            due_date=data.get("due_date", ""),
        )
        self.write(json_encode({"ok": True, "rfi": rfi.to_dict()}))


class RFIRespondHandler(BaseHandler):
    """POST /api/documents/rfi/respond — Respond to an RFI."""
    required_permission = "approve_drawings"
    def post(self):
        data = json.loads(self.request.body)
        rfi_id = data.get("rfi_id", "")
        response = data.get("response", "").strip()
        if not rfi_id or not response:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "rfi_id and response required"}))
            return
        rfi = respond_to_rfi(DATA_DIR, rfi_id, response, responded_by=self.current_user)
        if not rfi:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "RFI not found"}))
            return
        self.write(json_encode({"ok": True, "rfi": rfi.to_dict()}))


class RFICloseHandler(BaseHandler):
    """POST /api/documents/rfi/close — Close an RFI."""
    required_permission = "approve_drawings"
    def post(self):
        data = json.loads(self.request.body)
        rfi_id = data.get("rfi_id", "")
        if not rfi_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "rfi_id required"}))
            return
        rfi = close_rfi(DATA_DIR, rfi_id, closed_by=self.current_user)
        if not rfi:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "RFI not found or already closed"}))
            return
        self.write(json_encode({"ok": True, "rfi": rfi.to_dict()}))


class RFIVoidHandler(BaseHandler):
    """POST /api/documents/rfi/void — Void an RFI."""
    required_permission = "approve_drawings"
    def post(self):
        data = json.loads(self.request.body)
        rfi_id = data.get("rfi_id", "")
        if not rfi_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "rfi_id required"}))
            return
        rfi = void_rfi(DATA_DIR, rfi_id)
        if not rfi:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "RFI not found"}))
            return
        self.write(json_encode({"ok": True, "rfi": rfi.to_dict()}))


# ── Transmittals ──────────────────────────────────────────────────────

class TransmittalListAPIHandler(BaseHandler):
    """GET /api/documents/transmittals — List transmittals."""
    required_permission = "view_shop_drawings"
    def get(self):
        job_code = self.get_argument("job_code", "")
        status = self.get_argument("status", "")
        xmits = list_transmittals(DATA_DIR, job_code=job_code, status=status)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "transmittals": [x.to_dict() for x in xmits],
            "count": len(xmits),
        }))


class TransmittalDetailAPIHandler(BaseHandler):
    """GET /api/documents/transmittal?transmittal_id=X — Get a single transmittal."""
    required_permission = "view_shop_drawings"
    def get(self):
        xmit_id = self.get_argument("transmittal_id", "")
        if not xmit_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "transmittal_id required"}))
            return
        xmit = get_transmittal(DATA_DIR, xmit_id)
        if not xmit:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Transmittal not found"}))
            return
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "transmittal": xmit.to_dict()}))


class TransmittalCreateHandler(BaseHandler):
    """POST /api/documents/transmittal/create — Create a new transmittal."""
    required_permission = "edit_shop_drawings"
    def post(self):
        data = json.loads(self.request.body)
        job_code = data.get("job_code", "").strip()
        recipient = data.get("recipient", "").strip()
        purpose = data.get("purpose", "").strip()
        if not job_code or not recipient or not purpose:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code, recipient, purpose required"}))
            return
        xmit = create_transmittal(
            DATA_DIR, job_code=job_code, recipient=recipient, purpose=purpose,
            created_by=self.current_user,
            recipient_email=data.get("recipient_email", ""),
            subject=data.get("subject", ""),
            notes=data.get("notes", ""),
            documents=data.get("documents", []),
        )
        self.write(json_encode({"ok": True, "transmittal": xmit.to_dict()}))


class TransmittalSendHandler(BaseHandler):
    """POST /api/documents/transmittal/send — Mark transmittal as sent."""
    required_permission = "edit_shop_drawings"
    def post(self):
        data = json.loads(self.request.body)
        xmit_id = data.get("transmittal_id", "")
        if not xmit_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "transmittal_id required"}))
            return
        xmit = send_transmittal(DATA_DIR, xmit_id)
        if not xmit:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Transmittal not found or already sent"}))
            return
        self.write(json_encode({"ok": True, "transmittal": xmit.to_dict()}))


class TransmittalAckHandler(BaseHandler):
    """POST /api/documents/transmittal/acknowledge — Acknowledge a transmittal."""
    required_permission = "view_shop_drawings"
    def post(self):
        data = json.loads(self.request.body)
        xmit_id = data.get("transmittal_id", "")
        if not xmit_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "transmittal_id required"}))
            return
        xmit = acknowledge_transmittal(DATA_DIR, xmit_id, acknowledged_by=self.current_user)
        if not xmit:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Transmittal not found or not sent"}))
            return
        self.write(json_encode({"ok": True, "transmittal": xmit.to_dict()}))


# ── BOM Changes ───────────────────────────────────────────────────────

class BOMChangeLogHandler(BaseHandler):
    """POST /api/documents/bom-change/log — Log a BOM change."""
    required_permission = "edit_shop_drawings"
    def post(self):
        data = json.loads(self.request.body)
        job_code = data.get("job_code", "").strip()
        change_type = data.get("change_type", "").strip()
        component = data.get("component", "").strip()
        if not job_code or not change_type or not component:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code, change_type, component required"}))
            return
        bco = log_bom_change(
            DATA_DIR, job_code=job_code,
            from_revision=data.get("from_revision", ""),
            to_revision=data.get("to_revision", ""),
            change_type=change_type,
            component=component, created_by=self.current_user,
            field_changed=data.get("field_changed", ""),
            old_value=data.get("old_value", ""),
            new_value=data.get("new_value", ""),
            reason=data.get("reason", ""),
        )
        self.write(json_encode({"ok": True, "change": bco.to_dict()}))


class BOMChangeListAPIHandler(BaseHandler):
    """GET /api/documents/bom-changes — List BOM changes."""
    required_permission = "view_shop_drawings"
    def get(self):
        job_code = self.get_argument("job_code", "")
        from_rev = self.get_argument("from_revision", "")
        to_rev = self.get_argument("to_revision", "")
        changes = list_bom_changes(DATA_DIR, job_code=job_code,
                                   from_revision=from_rev, to_revision=to_rev)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "changes": [c.to_dict() for c in changes],
            "count": len(changes),
        }))


class BOMChangeSummaryAPIHandler(BaseHandler):
    """GET /api/documents/bom-changes/summary — BOM change summary for a job."""
    required_permission = "view_shop_drawings"
    def get(self):
        job_code = self.get_argument("job_code", "")
        if not job_code:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code required"}))
            return
        summary = get_bom_change_summary(DATA_DIR, job_code)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "summary": summary}))


# ── Document Summary & Config ─────────────────────────────────────────

class DocumentSummaryAPIHandler(BaseHandler):
    """GET /api/documents/summary — Document management summary/analytics."""
    required_permission = "view_shop_drawings"
    def get(self):
        job_code = self.get_argument("job_code", "")
        summary = get_document_summary(DATA_DIR, job_code=job_code)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "summary": summary}))


class DocumentConfigHandler(BaseHandler):
    """GET /api/documents/config — Return document management constants."""
    required_permission = "view_shop_drawings"
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "revision_statuses": REV_STATUSES,
            "revision_status_labels": REV_STATUS_LABELS,
            "revision_status_colors": REV_STATUS_COLORS,
            "revision_status_flow": REV_STATUS_FLOW,
            "document_categories": DOC_CATEGORIES,
            "document_category_labels": DOC_CATEGORY_LABELS,
            "rfi_statuses": RFI_STATUSES,
            "rfi_status_labels": RFI_STATUS_LABELS,
            "rfi_priorities": RFI_PRIORITIES,
            "rfi_priority_labels": RFI_PRIORITY_LABELS,
            "transmittal_statuses": XMIT_STATUSES,
            "transmittal_status_labels": XMIT_STATUS_LABELS,
            "transmittal_purposes": XMIT_PURPOSES,
            "transmittal_purpose_labels": XMIT_PURPOSE_LABELS,
            "bom_change_types": BOM_CHANGE_TYPES,
            "bom_change_type_labels": BOM_CHANGE_TYPE_LABELS,
        }))


# ─────────────────────────────────────────────
# PHASE 10 — Job Costing & Financial Tracking
# ─────────────────────────────────────────────

class JobCostingPageHandler(BaseHandler):
    """GET /job-costing — Job Costing dashboard."""
    required_permission = "view_financials"
    def get(self):
        from templates.job_costing_page import JOB_COSTING_PAGE_HTML
        self.set_header("Content-Type", "text/html")
        self.write(JOB_COSTING_PAGE_HTML)


# ── Cost Estimates ────────────────────────────────────────────────────

class EstimateListAPIHandler(BaseHandler):
    """GET /api/costing/estimates — List cost estimates."""
    required_permission = "view_financials"
    def get(self):
        job_code = self.get_argument("job_code", "")
        status = self.get_argument("status", "")
        estimates = list_estimates(DATA_DIR, job_code=job_code, status=status)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "estimates": [e.to_dict() for e in estimates],
            "count": len(estimates),
        }))


class EstimateDetailAPIHandler(BaseHandler):
    """GET /api/costing/estimate?estimate_id=X — Get single estimate."""
    required_permission = "view_financials"
    def get(self):
        est_id = self.get_argument("estimate_id", "")
        if not est_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "estimate_id required"}))
            return
        est = get_estimate(DATA_DIR, est_id)
        if not est:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Estimate not found"}))
            return
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "estimate": est.to_dict()}))


class EstimateCreateHandler(BaseHandler):
    """POST /api/costing/estimate/create — Create a cost estimate."""
    required_permission = "process_expenses"
    def post(self):
        data = json.loads(self.request.body)
        job_code = data.get("job_code", "").strip()
        name = data.get("name", "").strip()
        if not job_code or not name:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code and name required"}))
            return
        est = create_estimate(
            DATA_DIR, job_code=job_code, name=name,
            created_by=self.current_user,
            contract_value=float(data.get("contract_value", 0)),
            line_items=data.get("line_items", []),
            notes=data.get("notes", ""),
        )
        self.write(json_encode({"ok": True, "estimate": est.to_dict()}))


class EstimateUpdateHandler(BaseHandler):
    """POST /api/costing/estimate/update — Update a cost estimate."""
    required_permission = "process_expenses"
    def post(self):
        data = json.loads(self.request.body)
        est_id = data.get("estimate_id", "")
        if not est_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "estimate_id required"}))
            return
        kwargs = {}
        for k in ["name", "status", "contract_value", "line_items", "notes"]:
            if k in data:
                kwargs[k] = data[k]
        if "contract_value" in kwargs:
            kwargs["contract_value"] = float(kwargs["contract_value"])
        est = update_estimate(DATA_DIR, est_id, **kwargs)
        if not est:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Estimate not found"}))
            return
        self.write(json_encode({"ok": True, "estimate": est.to_dict()}))


class EstimateApproveHandler(BaseHandler):
    """POST /api/costing/estimate/approve — Approve a cost estimate."""
    required_permission = "view_financials"
    def post(self):
        data = json.loads(self.request.body)
        est_id = data.get("estimate_id", "")
        if not est_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "estimate_id required"}))
            return
        est = approve_estimate(DATA_DIR, est_id, approved_by=self.current_user)
        if not est:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Estimate not found"}))
            return
        self.write(json_encode({"ok": True, "estimate": est.to_dict()}))


class EstimateDeleteHandler(BaseHandler):
    """POST /api/costing/estimate/delete — Delete a cost estimate."""
    required_permission = "process_expenses"
    def post(self):
        data = json.loads(self.request.body)
        est_id = data.get("estimate_id", "")
        if not est_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "estimate_id required"}))
            return
        ok = delete_estimate(DATA_DIR, est_id)
        if not ok:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Estimate not found"}))
            return
        self.write(json_encode({"ok": True}))


# ── Cost Entries (Actuals) ────────────────────────────────────────────

class CostEntryListAPIHandler(BaseHandler):
    """GET /api/costing/costs — List actual cost entries."""
    required_permission = "view_financials"
    def get(self):
        job_code = self.get_argument("job_code", "")
        category = self.get_argument("category", "")
        date_from = self.get_argument("date_from", "")
        date_to = self.get_argument("date_to", "")
        entries = list_cost_entries(DATA_DIR, job_code=job_code,
                                    category=category,
                                    date_from=date_from, date_to=date_to)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "entries": [e.to_dict() for e in entries],
            "count": len(entries),
            "total": round(sum(e.total for e in entries), 2),
        }))


class CostEntryCreateHandler(BaseHandler):
    """POST /api/costing/cost/create — Record an actual cost."""
    required_permission = "process_expenses"
    def post(self):
        data = json.loads(self.request.body)
        job_code = data.get("job_code", "").strip()
        category = data.get("category", "").strip()
        description = data.get("description", "").strip()
        if not job_code or not category or not description:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code, category, description required"}))
            return
        entry = add_cost_entry(
            DATA_DIR, job_code=job_code, category=category,
            description=description, created_by=self.current_user,
            quantity=float(data.get("quantity", 1)),
            unit=data.get("unit", ""),
            unit_cost=float(data.get("unit_cost", 0)),
            vendor=data.get("vendor", ""),
            po_number=data.get("po_number", ""),
            invoice_number=data.get("invoice_number", ""),
            work_order_ref=data.get("work_order_ref", ""),
            date=data.get("date", ""),
            notes=data.get("notes", ""),
        )
        self.write(json_encode({"ok": True, "entry": entry.to_dict()}))


class CostEntryDeleteHandler(BaseHandler):
    """POST /api/costing/cost/delete — Delete a cost entry."""
    required_permission = "process_expenses"
    def post(self):
        data = json.loads(self.request.body)
        entry_id = data.get("entry_id", "")
        if not entry_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "entry_id required"}))
            return
        ok = delete_cost_entry(DATA_DIR, entry_id)
        if not ok:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Entry not found"}))
            return
        self.write(json_encode({"ok": True}))


# ── Labor Entries ─────────────────────────────────────────────────────

class LaborEntryListAPIHandler(BaseHandler):
    """GET /api/costing/labor — List labor entries."""
    required_permission = "view_financials"
    def get(self):
        job_code = self.get_argument("job_code", "")
        worker = self.get_argument("worker", "")
        date_from = self.get_argument("date_from", "")
        date_to = self.get_argument("date_to", "")
        entries = list_labor_entries(DATA_DIR, job_code=job_code,
                                     worker=worker,
                                     date_from=date_from, date_to=date_to)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "entries": [e.to_dict() for e in entries],
            "count": len(entries),
            "total_hours": round(sum(e.hours for e in entries), 1),
            "total_cost": round(sum(e.total for e in entries), 2),
        }))


class LaborEntryCreateHandler(BaseHandler):
    """POST /api/costing/labor/create — Record a labor entry."""
    required_permission = "process_expenses"
    def post(self):
        data = json.loads(self.request.body)
        job_code = data.get("job_code", "").strip()
        worker = data.get("worker", "").strip()
        hours = float(data.get("hours", 0))
        if not job_code or not worker or hours <= 0:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code, worker, hours required"}))
            return
        entry = add_labor_entry(
            DATA_DIR, job_code=job_code, worker=worker,
            hours=hours, created_by=self.current_user,
            labor_type=data.get("labor_type", "welder"),
            work_order_ref=data.get("work_order_ref", ""),
            item_ref=data.get("item_ref", ""),
            date=data.get("date", ""),
            rate=float(data.get("rate", 0)),
            overtime=data.get("overtime", False),
            overtime_multiplier=float(data.get("overtime_multiplier", 1.5)),
            description=data.get("description", ""),
        )
        self.write(json_encode({"ok": True, "entry": entry.to_dict()}))


class LaborEntryDeleteHandler(BaseHandler):
    """POST /api/costing/labor/delete — Delete a labor entry."""
    required_permission = "process_expenses"
    def post(self):
        data = json.loads(self.request.body)
        labor_id = data.get("labor_id", "")
        if not labor_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "labor_id required"}))
            return
        ok = delete_labor_entry(DATA_DIR, labor_id)
        if not ok:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Entry not found"}))
            return
        self.write(json_encode({"ok": True}))


# ── Labor Rates ───────────────────────────────────────────────────────

class LaborRatesAPIHandler(BaseHandler):
    """GET /api/costing/labor-rates — Get current labor rates."""
    required_permission = "view_financials"
    def get(self):
        rates = get_labor_rates(DATA_DIR)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "rates": rates,
            "labels": DEFAULT_LABOR_RATE_LABELS,
        }))


class LaborRatesUpdateHandler(BaseHandler):
    """POST /api/costing/labor-rates/update — Update labor rates."""
    required_permission = "process_expenses"
    def post(self):
        data = json.loads(self.request.body)
        rates = data.get("rates", {})
        if not rates:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "rates required"}))
            return
        updated = update_labor_rates(DATA_DIR, rates)
        self.write(json_encode({"ok": True, "rates": updated}))


# ── Change Orders ─────────────────────────────────────────────────────

class ChangeOrderListAPIHandler(BaseHandler):
    """GET /api/costing/change-orders — List change orders."""
    required_permission = "view_financials"
    def get(self):
        job_code = self.get_argument("job_code", "")
        cos = list_change_orders(DATA_DIR, job_code=job_code)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "change_orders": [co.to_dict() for co in cos],
            "count": len(cos),
        }))


class ChangeOrderCreateHandler(BaseHandler):
    """POST /api/costing/change-order/create — Create a change order."""
    required_permission = "process_expenses"
    def post(self):
        data = json.loads(self.request.body)
        job_code = data.get("job_code", "").strip()
        description = data.get("description", "").strip()
        if not job_code or not description:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code and description required"}))
            return
        co = create_change_order(
            DATA_DIR, job_code=job_code, description=description,
            created_by=self.current_user,
            material_impact=float(data.get("material_impact", 0)),
            labor_impact=float(data.get("labor_impact", 0)),
            other_impact=float(data.get("other_impact", 0)),
        )
        self.write(json_encode({"ok": True, "change_order": co.to_dict()}))


class ChangeOrderApproveHandler(BaseHandler):
    """POST /api/costing/change-order/approve — Approve a change order."""
    required_permission = "view_financials"
    def post(self):
        data = json.loads(self.request.body)
        co_id = data.get("co_id", "")
        if not co_id:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "co_id required"}))
            return
        co = approve_change_order(DATA_DIR, co_id, approved_by=self.current_user)
        if not co:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Change order not found"}))
            return
        self.write(json_encode({"ok": True, "change_order": co.to_dict()}))


# ── Job Cost Reports ──────────────────────────────────────────────────

class JobCostSummaryAPIHandler(BaseHandler):
    """GET /api/costing/job-summary?job_code=X — Job P&L summary."""
    required_permission = "view_project_pnl"
    def get(self):
        job_code = self.get_argument("job_code", "")
        if not job_code:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code required"}))
            return
        summary = get_job_cost_summary(DATA_DIR, job_code)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "summary": summary}))


class CostVarianceAPIHandler(BaseHandler):
    """GET /api/costing/variance?job_code=X — Cost variance report."""
    required_permission = "view_project_pnl"
    def get(self):
        job_code = self.get_argument("job_code", "")
        if not job_code:
            self.set_status(400)
            self.write(json_encode({"ok": False, "error": "job_code required"}))
            return
        report = get_cost_variance_report(DATA_DIR, job_code)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "report": report}))


class FinancialOverviewAPIHandler(BaseHandler):
    """GET /api/costing/overview — Cross-job financial overview."""
    required_permission = "view_financials"
    def get(self):
        overview = get_financial_overview(DATA_DIR)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "overview": overview}))


class CostingConfigHandler(BaseHandler):
    """GET /api/costing/config — Return costing constants."""
    required_permission = "view_financials"
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "cost_categories": COST_CATEGORIES,
            "cost_category_labels": COST_CATEGORY_LABELS,
            "estimate_statuses": EST_STATUSES,
            "estimate_status_labels": EST_STATUS_LABELS,
            "labor_rate_labels": DEFAULT_LABOR_RATE_LABELS,
            "default_labor_rates": DEFAULT_LABOR_RATES,
        }))


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 11 — Inventory Management Handlers
# ─────────────────────────────────────────────────────────────────────────────

class InventoryDashboardPageHandler(BaseHandler):
    """GET /inventory — Inventory Management Dashboard."""
    required_permission = "view_inventory"
    def get(self):
        from templates.inventory_dashboard_page import INVENTORY_DASHBOARD_PAGE_HTML
        self.render_with_nav(INVENTORY_DASHBOARD_PAGE_HTML, active_page="inventory")


class CoilListAPIHandler(BaseHandler):
    """GET /api/inventory/coils — List coils with filters."""
    required_permission = "view_inventory"
    def get(self):
        gauge = self.get_query_argument("gauge", "")
        grade = self.get_query_argument("grade", "")
        supplier = self.get_query_argument("supplier", "")
        status = self.get_query_argument("status", "")
        low_stock = self.get_query_argument("low_stock", "") == "true"
        coils = list_coils(DATA_DIR, gauge=gauge, grade=grade,
                           supplier=supplier, status=status,
                           low_stock_only=low_stock)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "coils": coils, "total": len(coils)}))


class CoilDetailAPIHandler(BaseHandler):
    """GET /api/inventory/coil/detail — Get single coil."""
    required_permission = "view_inventory"
    def get(self):
        coil_id = self.get_query_argument("coil_id", "")
        if not coil_id:
            self.write(json_encode({"ok": False, "error": "coil_id required"}))
            return
        coil = get_coil(DATA_DIR, coil_id)
        if not coil:
            self.set_status(404)
            self.write(json_encode({"ok": False, "error": "Coil not found"}))
            return
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "coil": coil}))


class CoilCreateHandler(BaseHandler):
    """POST /api/inventory/coil/create — Create new coil."""
    required_permission = "edit_inventory"
    def post(self):
        data = json_decode(self.request.body)
        try:
            coil = create_coil(
                DATA_DIR,
                coil_id=data.get("coil_id", ""),
                name=data.get("name", ""),
                gauge=data.get("gauge", ""),
                grade=data.get("grade", ""),
                supplier=data.get("supplier", ""),
                weight_lbs=float(data.get("weight_lbs", 0)),
                width_in=float(data.get("width_in", 0)),
                stock_lbs=float(data.get("stock_lbs", 0)),
                price_per_lb=float(data.get("price_per_lb", 0)),
                min_order_lbs=float(data.get("min_order_lbs", 5000)),
                lead_time_weeks=int(data.get("lead_time_weeks", 8)),
                lbs_per_lft=float(data.get("lbs_per_lft", 0)),
                heat_num=data.get("heat_num", ""),
                created_by=self.current_username or "",
            )
            self.write(json_encode({"ok": True, "coil": coil}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class CoilUpdateHandler(BaseHandler):
    """POST /api/inventory/coil/update — Update coil fields."""
    required_permission = "edit_inventory"
    def post(self):
        data = json_decode(self.request.body)
        coil_id = data.pop("coil_id", "")
        if not coil_id:
            self.write(json_encode({"ok": False, "error": "coil_id required"}))
            return
        try:
            coil = update_coil(DATA_DIR, coil_id, **data)
            self.write(json_encode({"ok": True, "coil": coil}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class CoilDeleteAPIHandler(BaseHandler):
    """POST /api/inventory/coil/delete — Delete a coil."""
    required_permission = "edit_inventory"
    def post(self):
        data = json_decode(self.request.body)
        coil_id = data.get("coil_id", "")
        ok = delete_coil(DATA_DIR, coil_id)
        self.write(json_encode({"ok": ok, "error": "" if ok else "Coil not found"}))


class ReceiveStockHandler(BaseHandler):
    """POST /api/inventory/receive — Receive stock into coil."""
    required_permission = "receive_inventory"
    def post(self):
        data = json_decode(self.request.body)
        try:
            result = receive_stock(
                DATA_DIR,
                coil_id=data.get("coil_id", ""),
                quantity_lbs=float(data.get("quantity_lbs", 0)),
                po_number=data.get("po_number", ""),
                bol_number=data.get("bol_number", ""),
                supplier=data.get("supplier", ""),
                heat_number=data.get("heat_number", ""),
                condition_notes=data.get("condition_notes", ""),
                received_by=self.current_username or "",
            )
            self.write(json_encode({"ok": True, **result}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class AdjustStockHandler(BaseHandler):
    """POST /api/inventory/adjust — Adjust stock (correction)."""
    required_permission = "edit_inventory"
    def post(self):
        data = json_decode(self.request.body)
        try:
            result = adjust_stock(
                DATA_DIR,
                coil_id=data.get("coil_id", ""),
                quantity_lbs=float(data.get("quantity_lbs", 0)),
                reason=data.get("reason", ""),
                adjusted_by=self.current_username or "",
            )
            self.write(json_encode({"ok": True, **result}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class ConsumeStockHandler(BaseHandler):
    """POST /api/inventory/consume — Record stock consumption."""
    required_permission = "edit_inventory"
    def post(self):
        data = json_decode(self.request.body)
        try:
            result = consume_stock(
                DATA_DIR,
                coil_id=data.get("coil_id", ""),
                quantity_lbs=float(data.get("quantity_lbs", 0)),
                job_code=data.get("job_code", ""),
                work_order_ref=data.get("work_order_ref", ""),
                consumed_by=self.current_username or "",
            )
            self.write(json_encode({"ok": True, **result}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class TransactionListAPIHandler(BaseHandler):
    """GET /api/inventory/transactions — List stock transactions."""
    required_permission = "view_inventory"
    def get(self):
        coil_id = self.get_query_argument("coil_id", "")
        txn_type = self.get_query_argument("type", "")
        date_from = self.get_query_argument("date_from", "")
        date_to = self.get_query_argument("date_to", "")
        txns = list_transactions(DATA_DIR, coil_id=coil_id,
                                 transaction_type=txn_type,
                                 date_from=date_from, date_to=date_to)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "transactions": txns, "total": len(txns)}))


class AllocateStockHandler(BaseHandler):
    """POST /api/inventory/allocate — Allocate stock to a job."""
    required_permission = "allocate_stock"
    def post(self):
        data = json_decode(self.request.body)
        try:
            alloc = allocate_stock(
                DATA_DIR,
                coil_id=data.get("coil_id", ""),
                job_code=data.get("job_code", ""),
                quantity_lbs=float(data.get("quantity_lbs", 0)),
                work_order_ref=data.get("work_order_ref", ""),
                notes=data.get("notes", ""),
                allocated_by=self.current_username or "",
            )
            self.write(json_encode({"ok": True, "allocation": alloc.to_dict()}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class ReleaseAllocationHandler(BaseHandler):
    """POST /api/inventory/allocate/release — Release an allocation."""
    required_permission = "allocate_stock"
    def post(self):
        data = json_decode(self.request.body)
        try:
            result = release_allocation(
                DATA_DIR,
                allocation_id=data.get("allocation_id", ""),
                released_by=self.current_username or "",
            )
            self.write(json_encode({"ok": True, **result}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class AllocationListAPIHandler(BaseHandler):
    """GET /api/inventory/allocations — List allocations."""
    required_permission = "view_inventory"
    def get(self):
        coil_id = self.get_query_argument("coil_id", "")
        job_code = self.get_query_argument("job_code", "")
        status = self.get_query_argument("status", "")
        allocs = list_allocations(DATA_DIR, coil_id=coil_id,
                                  job_code=job_code, status=status)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "allocations": allocs, "total": len(allocs)}))


class AlertListAPIHandler(BaseHandler):
    """GET /api/inventory/alerts — List stock alerts."""
    required_permission = "view_inventory"
    def get(self):
        ack = self.get_query_argument("acknowledged", "")
        level = self.get_query_argument("level", "")
        coil_id = self.get_query_argument("coil_id", "")
        ack_filter = None
        if ack == "true":
            ack_filter = True
        elif ack == "false":
            ack_filter = False
        alerts_list = list_alerts(DATA_DIR, acknowledged=ack_filter,
                                  alert_level=level, coil_id=coil_id)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "alerts": alerts_list, "total": len(alerts_list)}))


class AlertAcknowledgeHandler(BaseHandler):
    """POST /api/inventory/alerts/acknowledge — Acknowledge an alert."""
    required_permission = "edit_inventory"
    def post(self):
        data = json_decode(self.request.body)
        try:
            alert = acknowledge_alert(DATA_DIR, data.get("alert_id", ""),
                                      acknowledged_by=self.current_username or "")
            self.write(json_encode({"ok": True, "alert": alert}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class GenerateAlertsHandler(BaseHandler):
    """POST /api/inventory/alerts/generate — Scan and generate alerts."""
    required_permission = "edit_inventory"
    def post(self):
        coils_alerted = generate_stock_alerts(DATA_DIR)
        self.write(json_encode({"ok": True, "coils_checked": len(coils_alerted)}))


class ReceivingListAPIHandler(BaseHandler):
    """GET /api/inventory/receiving — List receiving records."""
    required_permission = "view_inventory"
    def get(self):
        coil_id = self.get_query_argument("coil_id", "")
        date_from = self.get_query_argument("date_from", "")
        date_to = self.get_query_argument("date_to", "")
        records = list_receiving(DATA_DIR, coil_id=coil_id,
                                 date_from=date_from, date_to=date_to)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "records": records, "total": len(records)}))


class MillCertListAPIHandler(BaseHandler):
    """GET /api/inventory/mill-certs — List mill certificates."""
    required_permission = "view_inventory"
    def get(self):
        coil_id = self.get_query_argument("coil_id", "")
        certs = list_mill_certs(DATA_DIR, coil_id=coil_id)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, "certs": certs, "total": len(certs)}))


class MillCertAddHandler(BaseHandler):
    """POST /api/inventory/mill-cert/add — Add mill cert record."""
    required_permission = "manage_mill_certs"
    def post(self):
        data = json_decode(self.request.body)
        try:
            cert = add_mill_cert(
                DATA_DIR,
                coil_id=data.get("coil_id", ""),
                heat_number=data.get("heat_number", ""),
                mill_name=data.get("mill_name", ""),
                material_spec=data.get("material_spec", ""),
                filename=data.get("filename", ""),
                created_by=self.current_username or "",
            )
            self.write(json_encode({"ok": True, "cert": cert}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class MillCertDeleteHandler(BaseHandler):
    """POST /api/inventory/mill-cert/delete — Delete mill cert."""
    required_permission = "manage_mill_certs"
    def post(self):
        data = json_decode(self.request.body)
        ok = delete_mill_cert(DATA_DIR, data.get("cert_id", ""))
        self.write(json_encode({"ok": ok}))


class InventorySummaryAPIHandler(BaseHandler):
    """GET /api/inventory/summary — Get inventory summary analytics."""
    required_permission = "view_inventory"
    def get(self):
        summary = get_inventory_summary(DATA_DIR)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, **summary}))


class CoilHistoryAPIHandler(BaseHandler):
    """GET /api/inventory/coil/history — Get full coil history."""
    required_permission = "view_inventory"
    def get(self):
        coil_id = self.get_query_argument("coil_id", "")
        if not coil_id:
            self.write(json_encode({"ok": False, "error": "coil_id required"}))
            return
        try:
            history = get_coil_history(DATA_DIR, coil_id)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, **history}))
        except Exception as e:
            self.write(json_encode({"ok": False, "error": str(e)}))


class StockValuationAPIHandler(BaseHandler):
    """GET /api/inventory/valuation — Get stock valuation."""
    required_permission = "view_inventory_costs"
    def get(self):
        valuation = get_stock_valuation(DATA_DIR)
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({"ok": True, **valuation}))


class InventoryConfigHandler(BaseHandler):
    """GET /api/inventory/config — Return inventory constants."""
    required_permission = "view_inventory"
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json_encode({
            "ok": True,
            "coil_statuses": COIL_STATUSES,
            "coil_status_labels": COIL_STATUS_LABELS,
            "transaction_types": TRANSACTION_TYPES,
            "transaction_type_labels": TRANSACTION_TYPE_LABELS,
            "material_grades": MATERIAL_GRADES,
            "coil_gauges": COIL_GAUGES,
            "alert_levels": ALERT_LEVELS,
        }))


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
        (r"/auth/users/add",         UserAddHandler),
        (r"/auth/users/update-role", UserUpdateRoleHandler),
        (r"/auth/users/delete",      UserDeleteHandler),

        # ── App routes (Dashboard + Calculators) ────────────────
        (r"/",                      DashboardHandler),
        (r"/dashboard",             DashboardHandler),
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
        (r"/api/project/docs/archive",   ProjectArchiveDocHandler),
        (r"/api/project/docs/archived",  ProjectArchivedDocsHandler),
        (r"/project-files/([^/]+)/([^/]+)/([^/]+)", ProjectDocServeHandler),

        # ── API - Project Status (NEW) ────────────────────────
        (r"/api/project/status",         ProjectStatusHandler),

        # ── API - Enhanced Project System ─────────────────────
        (r"/api/project/next-code",      ProjectNextCodeHandler),
        (r"/api/project/create",         ProjectCreateHandler),
        (r"/api/project/metadata",       ProjectMetadataHandler),
        (r"/api/project/checklist",      ProjectChecklistHandler),
        (r"/api/project/next-steps",     ProjectNextStepsHandler),
        (r"/api/project/delete",         ProjectDeleteHandler),
        (r"/api/projects/full",          ProjectListEnhancedHandler),

        # ── Project Page ──────────────────────────────────────
        (r"/project/([^/]+)",            ProjectPageHandler),

        # ── Shop Drawings ─────────────────────────────────────
        (r"/shop-drawings/([^/]+)/rafter",       RafterDrawingHandler),
        (r"/shop-drawings/([^/]+)/column",       ColumnDrawingHandler),
        (r"/shop-drawings/([^/]+)",              ShopDrawingsPageHandler),
        (r"/api/shop-drawings/save-interactive-pdf", SaveInteractivePdfHandler),
        (r"/api/shop-drawings/config",           ShopDrawingsConfigHandler),
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

        # ── Phase 2: Assignment & Queue APIs ─────────────────
        (r"/api/work-orders/assign",             WorkOrderAssignHandler),
        (r"/api/work-orders/reassign",           WorkOrderReassignHandler),
        (r"/api/work-orders/reprioritize",       WorkOrderReprioritizeHandler),
        (r"/api/work-orders/stage",              WorkOrderStageHandler),
        (r"/api/work-orders/transition",         WorkOrderTransitionHandler),
        (r"/api/work-orders/bulk-assign",        WorkOrderBulkAssignHandler),
        (r"/api/work-orders/status-config",      StatusConfigHandler),
        (r"/api/operator/queue",                 OperatorQueueHandler),
        (r"/api/machine/queue",                  MachineQueueHandler),
        (r"/api/shop-floor/summary",             ShopFloorSummaryHandler),

        # ── Shop Floor Dashboard ─────────────────────────────
        (r"/shop-floor",                         ShopFloorPageHandler),
        (r"/shop-floor/assign",                  ForemanPanelPageHandler),
        (r"/api/shop-floor/data",                ShopFloorDataHandler),

        # ── Work Station (tablet/phone) ───────────────────────
        (r"/work-station/mine",                  MyStationPageHandler),
        (r"/work-station/([^/]+)",               WorkStationPageHandler),
        (r"/api/work-station/data",              WorkStationDataHandler),
        (r"/api/work-station/steps",             WorkStationStepsHandler),
        (r"/api/work-station/steps/override",    WorkStationStepOverrideHandler),
        (r"/api/work-orders/packet/pdf",         WorkOrderPacketPDFHandler),

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
        (r"/qc-queue",                       QCInspectionQueuePageHandler),
        (r"/qc-dashboard",                   QCDashboardPageHandler),
        (r"/api/qc/types",                   QCInspectionTypesHandler),
        (r"/api/qc/data",                    QCDataHandler),
        (r"/api/qc/queue",                   QCInspectionQueueAPIHandler),
        (r"/api/qc/sign-off",               QCSignOffHandler),
        (r"/api/qc/dashboard",              QCDashboardAPIHandler),
        (r"/api/qc/item-history",           QCItemHistoryHandler),
        (r"/api/qc/ncr/detail",             NCRDetailHandler),
        (r"/api/qc/inspection/create",       QCInspectionCreateHandler),
        (r"/api/qc/inspection/update",       QCInspectionUpdateHandler),
        (r"/api/qc/ncr/create",              NCRCreateHandler),
        (r"/api/qc/ncr/update",              NCRUpdateHandler),

        # ── Material Traceability ──────────────────────────────
        (r"/api/traceability",               TraceabilityIndexHandler),
        (r"/api/traceability/register",      TraceabilityRegisterHandler),
        (r"/api/traceability/assign",        TraceabilityAssignHandler),
        (r"/api/traceability/report",        TraceabilityReportHandler),

        # ── Shipping & Load Management (Phase 4) ─────────────
        (r"/shipping",                       ShippingDashboardPageHandler),
        (r"/shipping/load-builder",          LoadBuilderPageHandler),
        (r"/api/shipping/loads",             ShippingListAPIHandler),
        (r"/api/shipping/load",              ShippingLoadDetailHandler),
        (r"/api/shipping/create",            ShippingCreateLoadHandler),
        (r"/api/shipping/add-items",         ShippingAddItemsHandler),
        (r"/api/shipping/remove-item",       ShippingRemoveItemHandler),
        (r"/api/shipping/transition",        ShippingTransitionHandler),
        (r"/api/shipping/update",            ShippingUpdateLoadHandler),
        (r"/api/shipping/bol",               ShippingBOLHandler),
        (r"/api/shipping/shippable-items",   ShippableItemsHandler),
        (r"/api/shipping/summary",           ShippingSummaryHandler),
        (r"/api/shipping/config",            ShippingConfigHandler),

        # ── Field Operations & Installation (Phase 5) ────────
        (r"/field",                          FieldDashboardPageHandler),
        (r"/field/install-tracker",          InstallTrackerPageHandler),
        (r"/field/completion",               ProjectCompletionPageHandler),
        (r"/api/field/punch-list",           PunchListAPIHandler),
        (r"/api/field/punch-list/create",    PunchCreateHandler),
        (r"/api/field/punch-list/transition", PunchTransitionHandler),
        (r"/api/field/punch-list/detail",    PunchDetailHandler),
        (r"/api/field/confirm-install",      InstallConfirmHandler),
        (r"/api/field/daily-report",         DailyReportSubmitHandler),
        (r"/api/field/daily-reports",        DailyReportListHandler),
        (r"/api/field/installations",        InstallationRecordsHandler),
        (r"/api/field/project-completion",   ProjectCompletionAPIHandler),
        (r"/api/field/summary",              FieldSummaryHandler),
        (r"/api/field/config",               FieldConfigHandler),

        # ── Reporting & Analytics (Phase 6) ──────────────────
        (r"/reports/production",         ProductionMetricsPageHandler),
        (r"/reports/executive",          ExecutiveSummaryPageHandler),
        (r"/api/reports",                ReportListHandler),
        (r"/api/reports/generate",       ReportGenerateHandler),
        (r"/api/reports/production",     ProductionMetricsAPIHandler),
        (r"/api/reports/executive",      ExecutiveSummaryAPIHandler),
        (r"/api/reports/operators",      OperatorPerformanceAPIHandler),
        (r"/api/reports/project-status", ProjectStatusReportAPIHandler),
        (r"/api/reports/delivery",       DeliveryAnalysisAPIHandler),
        (r"/api/reports/qc",            QCAnalysisAPIHandler),
        (r"/api/reports/config",         ReportConfigHandler),

        # ── Activity Feed, Audit Trail & Notifications (Phase 7) ──
        (r"/activity",                   ActivityFeedPageHandler),
        (r"/api/activity/events",        ActivityEventsAPIHandler),
        (r"/api/activity/feed",          ActivityFeedAPIHandler),
        (r"/api/activity/stats",         ActivityStatsAPIHandler),
        (r"/api/activity/rules",         AlertRulesAPIHandler),
        (r"/api/activity/rules/update",  AlertRuleUpdateHandler),
        (r"/api/activity/rules/delete",  AlertRuleDeleteHandler),
        (r"/api/notifications",          NotificationsAPIHandler),
        (r"/api/notifications/read",     NotificationReadHandler),
        (r"/api/notifications/read-all", NotificationReadAllHandler),
        (r"/api/notifications/clear",    NotificationClearHandler),
        (r"/api/activity/config",        ActivityConfigHandler),

        # ── Phase 8: Scheduling & Production Planning ──────────
        (r"/schedule",                       ProductionSchedulePageHandler),
        (r"/api/schedule/list",              ScheduleListAPIHandler),
        (r"/api/schedule/create",            ScheduleCreateHandler),
        (r"/api/schedule/update",            ScheduleUpdateHandler),
        (r"/api/schedule/delete",            ScheduleDeleteHandler),
        (r"/api/schedule/entry/add",         ScheduleEntryAddHandler),
        (r"/api/schedule/entry/update",      ScheduleEntryUpdateHandler),
        (r"/api/schedule/entry/delete",      ScheduleEntryDeleteHandler),
        (r"/api/schedule/date",              ScheduleDateAPIHandler),
        (r"/api/schedule/range",             ScheduleRangeAPIHandler),
        (r"/api/schedule/capacity",          CapacityAPIHandler),
        (r"/api/schedule/capacity/update",   CapacityUpdateHandler),
        (r"/api/schedule/capacity/usage",    CapacityUsageAPIHandler),
        (r"/api/schedule/capacity/forecast", CapacityForecastAPIHandler),
        (r"/api/schedule/auto",              AutoScheduleHandler),
        (r"/api/schedule/summary",           ScheduleSummaryAPIHandler),
        (r"/api/schedule/job-timeline",      JobTimelineAPIHandler),
        (r"/api/schedule/machine",           MachineScheduleAPIHandler),
        (r"/api/schedule/bottlenecks",       BottleneckForecastAPIHandler),
        (r"/api/schedule/overdue",           OverdueEntriesAPIHandler),
        (r"/api/schedule/config",            ScheduleConfigHandler),

        # ── Phase 9 — Document Management ─────────────────────
        (r"/documents",                                DocumentManagementPageHandler),
        (r"/api/documents/revisions",                  RevisionListAPIHandler),
        (r"/api/documents/revision",                   RevisionDetailAPIHandler),
        (r"/api/documents/revision/create",            RevisionCreateHandler),
        (r"/api/documents/revision/transition",        RevisionTransitionHandler),
        (r"/api/documents/revision/history",           RevisionHistoryAPIHandler),
        (r"/api/documents/revision/latest",            RevisionLatestAPIHandler),
        (r"/api/documents/rfis",                       RFIListAPIHandler),
        (r"/api/documents/rfi",                        RFIDetailAPIHandler),
        (r"/api/documents/rfi/create",                 RFICreateHandler),
        (r"/api/documents/rfi/respond",                RFIRespondHandler),
        (r"/api/documents/rfi/close",                  RFICloseHandler),
        (r"/api/documents/rfi/void",                   RFIVoidHandler),
        (r"/api/documents/transmittals",               TransmittalListAPIHandler),
        (r"/api/documents/transmittal",                TransmittalDetailAPIHandler),
        (r"/api/documents/transmittal/create",         TransmittalCreateHandler),
        (r"/api/documents/transmittal/send",           TransmittalSendHandler),
        (r"/api/documents/transmittal/acknowledge",    TransmittalAckHandler),
        (r"/api/documents/bom-change/log",             BOMChangeLogHandler),
        (r"/api/documents/bom-changes",                BOMChangeListAPIHandler),
        (r"/api/documents/bom-changes/summary",        BOMChangeSummaryAPIHandler),
        (r"/api/documents/summary",                    DocumentSummaryAPIHandler),
        (r"/api/documents/config",                     DocumentConfigHandler),

        # ── Phase 10 — Job Costing ────────────────────────────
        (r"/job-costing",                              JobCostingPageHandler),
        (r"/api/costing/estimates",                    EstimateListAPIHandler),
        (r"/api/costing/estimate",                     EstimateDetailAPIHandler),
        (r"/api/costing/estimate/create",              EstimateCreateHandler),
        (r"/api/costing/estimate/update",              EstimateUpdateHandler),
        (r"/api/costing/estimate/approve",             EstimateApproveHandler),
        (r"/api/costing/estimate/delete",              EstimateDeleteHandler),
        (r"/api/costing/costs",                        CostEntryListAPIHandler),
        (r"/api/costing/cost/create",                  CostEntryCreateHandler),
        (r"/api/costing/cost/delete",                  CostEntryDeleteHandler),
        (r"/api/costing/labor",                        LaborEntryListAPIHandler),
        (r"/api/costing/labor/create",                 LaborEntryCreateHandler),
        (r"/api/costing/labor/delete",                 LaborEntryDeleteHandler),
        (r"/api/costing/labor-rates",                  LaborRatesAPIHandler),
        (r"/api/costing/labor-rates/update",           LaborRatesUpdateHandler),
        (r"/api/costing/change-orders",                ChangeOrderListAPIHandler),
        (r"/api/costing/change-order/create",          ChangeOrderCreateHandler),
        (r"/api/costing/change-order/approve",         ChangeOrderApproveHandler),
        (r"/api/costing/job-summary",                  JobCostSummaryAPIHandler),
        (r"/api/costing/variance",                     CostVarianceAPIHandler),
        (r"/api/costing/overview",                     FinancialOverviewAPIHandler),
        (r"/api/costing/config",                       CostingConfigHandler),

        # ── Phase 11 — Inventory Management ──────────────────
        (r"/inventory",                                InventoryDashboardPageHandler),
        (r"/api/inventory/coils",                      CoilListAPIHandler),
        (r"/api/inventory/coil/detail",                CoilDetailAPIHandler),
        (r"/api/inventory/coil/create",                CoilCreateHandler),
        (r"/api/inventory/coil/update",                CoilUpdateHandler),
        (r"/api/inventory/coil/delete",                CoilDeleteAPIHandler),
        (r"/api/inventory/receive",                    ReceiveStockHandler),
        (r"/api/inventory/adjust",                     AdjustStockHandler),
        (r"/api/inventory/consume",                    ConsumeStockHandler),
        (r"/api/inventory/transactions",               TransactionListAPIHandler),
        (r"/api/inventory/allocate",                   AllocateStockHandler),
        (r"/api/inventory/allocate/release",           ReleaseAllocationHandler),
        (r"/api/inventory/allocations",                AllocationListAPIHandler),
        (r"/api/inventory/alerts",                     AlertListAPIHandler),
        (r"/api/inventory/alerts/acknowledge",         AlertAcknowledgeHandler),
        (r"/api/inventory/alerts/generate",            GenerateAlertsHandler),
        (r"/api/inventory/receiving",                  ReceivingListAPIHandler),
        (r"/api/inventory/mill-certs",                 MillCertListAPIHandler),
        (r"/api/inventory/mill-cert/add",              MillCertAddHandler),
        (r"/api/inventory/mill-cert/delete",           MillCertDeleteHandler),
        (r"/api/inventory/summary",                    InventorySummaryAPIHandler),
        (r"/api/inventory/coil/history",               CoilHistoryAPIHandler),
        (r"/api/inventory/valuation",                  StockValuationAPIHandler),
        (r"/api/inventory/inv-config",                 InventoryConfigHandler),

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
from templates.rafter_drawing import RAFTER_DRAWING_HTML
from templates.column_drawing import COLUMN_DRAWING_HTML
from templates.work_orders import WORK_ORDERS_HTML
from templates.shop_floor import SHOP_FLOOR_HTML
from templates.work_station import WORK_STATION_HTML

# Aliases used by handlers
MAIN_HTML = SA_CALC_HTML
TC_HTML = TC_QUOTE_HTML
