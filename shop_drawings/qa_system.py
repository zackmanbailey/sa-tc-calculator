"""
TitanForge — QA/QC Document Management System
================================================
Backend for all AISC quality documentation:
  - WPS Library (Welding Procedure Specifications)
  - Welder Certifications (qualification records, continuity)
  - Calibration Log (tool/equipment calibration tracking)
  - Procedures (SOPs, quality manual, work instructions)
  - NCR statistics and QA dashboard data

Data stored in data/qa/ as JSON files.
"""

import os
import json
import datetime
import uuid
from typing import List, Dict, Optional


# ─────────────────────────────────────────────
# FILE PATHS
# ─────────────────────────────────────────────

def _qa_dir(base_dir: str) -> str:
    d = os.path.join(base_dir, "..", "data", "qa")
    d = os.path.normpath(d)
    os.makedirs(d, exist_ok=True)
    return d

def _load(path: str) -> dict:
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return {}

def _save(path: str, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ═══════════════════════════════════════════════
# WPS LIBRARY
# ═══════════════════════════════════════════════

DEFAULT_WPS = {
    "WPS-B": {
        "wps_id": "WPS-B",
        "title": "Stitch Welds — CEE-to-CEE Body",
        "standard": "AWS D1.1",
        "joint_type": "Fillet (Lap Joint)",
        "process": "GMAW (MIG)",
        "filler_metal": "ER70S-6, 0.035\" dia",
        "shielding_gas": "75% Ar / 25% CO2, 35 CFH",
        "base_metal": "A572 Gr 50 / A36",
        "thickness_range": "10GA (0.135\") to 7GA (0.179\")",
        "position": "1F, 2F (Flat, Horizontal)",
        "preheat": "None required (ambient >50°F)",
        "interpass_temp": "450°F max",
        "voltage": "19-22V",
        "amperage": "150-200A",
        "wire_speed": "280-350 IPM",
        "travel_speed": "12-18 IPM",
        "weld_size": "3/16\" fillet",
        "stitch_pattern": "2\" weld @ 12\" O.C. (both sides)",
        "acceptance_criteria": "AWS D1.1 Table 6.1 — Visual: no cracks, no incomplete fusion, undercut ≤1/32\", no porosity >3/32\"",
        "pqr_ref": "PQR-001",
        "approved_by": "QC Manager",
        "approved_date": "2024-01-15",
        "status": "active",
        "notes": "Primary production weld for column and rafter box beam assembly.",
    },
    "WPS-C": {
        "wps_id": "WPS-C",
        "title": "Clip-to-Rafter Attachment Welds",
        "standard": "AWS D1.1",
        "joint_type": "Fillet (Tee Joint)",
        "process": "GMAW (MIG)",
        "filler_metal": "ER70S-6, 0.035\" dia",
        "shielding_gas": "75% Ar / 25% CO2, 35 CFH",
        "base_metal": "A572 Gr 50 clip to A572 Gr 50 rafter",
        "thickness_range": "12GA (0.105\") clip to 10GA (0.135\") rafter",
        "position": "1F, 2F, 3F (Flat, Horizontal, Vertical up)",
        "preheat": "None required (ambient >50°F)",
        "interpass_temp": "450°F max",
        "voltage": "18-21V",
        "amperage": "140-180A",
        "wire_speed": "260-320 IPM",
        "travel_speed": "10-16 IPM",
        "weld_size": "1/8\" fillet minimum",
        "stitch_pattern": "Continuous both sides of clip",
        "acceptance_criteria": "AWS D1.1 Table 6.1 — Visual: full wrap, no cracks, undercut ≤1/32\"",
        "pqr_ref": "PQR-002",
        "approved_by": "QC Manager",
        "approved_date": "2024-01-15",
        "status": "active",
        "notes": "Purlin clips welded to rafter flanges. Must be located per shop drawing dimensions.",
    },
    "WPS-D": {
        "wps_id": "WPS-D",
        "title": "Rebar Attachment Welds",
        "standard": "AWS D1.4 (Reinforcing Steel)",
        "joint_type": "Fillet (Lap Joint)",
        "process": "GMAW (MIG)",
        "filler_metal": "ER70S-6, 0.035\" dia",
        "shielding_gas": "75% Ar / 25% CO2, 35 CFH",
        "base_metal": "A615 Gr 60 rebar to A572 Gr 50 CEE",
        "thickness_range": "#4 rebar (0.500\") to 10GA (0.135\") CEE",
        "position": "1F, 2F (Flat, Horizontal)",
        "preheat": "100°F minimum for #5 and larger rebar",
        "interpass_temp": "500°F max",
        "voltage": "19-23V",
        "amperage": "160-210A",
        "wire_speed": "290-360 IPM",
        "travel_speed": "8-14 IPM",
        "weld_size": "3/16\" fillet both sides",
        "stitch_pattern": "3\" welds at each end + 2\" midpoint",
        "acceptance_criteria": "AWS D1.4 — no cracks, full fusion at root, profile per figure",
        "pqr_ref": "PQR-003",
        "approved_by": "QC Manager",
        "approved_date": "2024-02-01",
        "status": "active",
        "notes": "Reinforced columns only. Rebar must be centered in box beam cavity.",
    },
    "WPS-F": {
        "wps_id": "WPS-F",
        "title": "Column/Rafter End Plate Welds",
        "standard": "AWS D1.1",
        "joint_type": "Fillet (Corner / Tee Joint)",
        "process": "GMAW (MIG)",
        "filler_metal": "ER70S-6, 0.035\" dia",
        "shielding_gas": "75% Ar / 25% CO2, 35 CFH",
        "base_metal": "A36 plate to A572 Gr 50 CEE",
        "thickness_range": "3/8\" plate to 10GA (0.135\") CEE",
        "position": "1F, 2F, 4F (Flat, Horizontal, Overhead)",
        "preheat": "None required (ambient >50°F)",
        "interpass_temp": "450°F max",
        "voltage": "20-24V",
        "amperage": "170-220A",
        "wire_speed": "300-380 IPM",
        "travel_speed": "10-15 IPM",
        "weld_size": "1/4\" fillet continuous all around",
        "stitch_pattern": "Continuous 360° — no starts/stops on corners",
        "acceptance_criteria": "AWS D1.1 Table 6.1 — continuous profile, no cracks, no porosity, undercut ≤1/32\"",
        "pqr_ref": "PQR-004",
        "approved_by": "QC Manager",
        "approved_date": "2024-01-15",
        "status": "active",
        "notes": "Critical connection weld. End plates must be square to box beam axis within 1/16\". Cap plates cut to roof pitch angle.",
    },
}


def get_wps_library(base_dir: str) -> Dict:
    """Get all WPS documents."""
    path = os.path.join(_qa_dir(base_dir), "wps_library.json")
    data = _load(path)
    if not data:
        data = dict(DEFAULT_WPS)
        _save(path, data)
    return data


def save_wps(base_dir: str, wps_id: str, wps_data: dict):
    """Save or update a single WPS."""
    path = os.path.join(_qa_dir(base_dir), "wps_library.json")
    lib = _load(path) or dict(DEFAULT_WPS)
    lib[wps_id] = wps_data
    _save(path, lib)


# ═══════════════════════════════════════════════
# WELDER CERTIFICATIONS
# ═══════════════════════════════════════════════

def _welders_path(base_dir: str) -> str:
    return os.path.join(_qa_dir(base_dir), "welder_certs.json")


def get_welder_certs(base_dir: str) -> List[dict]:
    """Get all welder certification records."""
    data = _load(_welders_path(base_dir))
    return data.get("welders", [])


def save_welder_cert(base_dir: str, cert: dict) -> dict:
    """Add or update a welder certification."""
    path = _welders_path(base_dir)
    data = _load(path) or {"welders": []}

    # Generate ID if new
    if not cert.get("cert_id"):
        cert["cert_id"] = f"WC-{uuid.uuid4().hex[:8].upper()}"
        cert["created_at"] = datetime.datetime.now().isoformat()

    # Update existing or append
    existing = next((i for i, w in enumerate(data["welders"])
                     if w.get("cert_id") == cert["cert_id"]), None)
    if existing is not None:
        data["welders"][existing] = cert
    else:
        data["welders"].append(cert)

    cert["updated_at"] = datetime.datetime.now().isoformat()
    _save(path, data)
    return cert


def check_welder_expirations(base_dir: str) -> List[dict]:
    """Check for expiring welder certifications (within 30 days)."""
    welders = get_welder_certs(base_dir)
    alerts = []
    today = datetime.date.today()
    for w in welders:
        exp = w.get("expiration_date", "")
        if not exp:
            continue
        try:
            exp_date = datetime.date.fromisoformat(exp)
            days_left = (exp_date - today).days
            if days_left <= 0:
                alerts.append({**w, "alert": "EXPIRED", "days_left": days_left})
            elif days_left <= 30:
                alerts.append({**w, "alert": "EXPIRING_SOON", "days_left": days_left})
        except (ValueError, TypeError):
            pass
    return alerts


# ═══════════════════════════════════════════════
# CALIBRATION LOG
# ═══════════════════════════════════════════════

def _calibration_path(base_dir: str) -> str:
    return os.path.join(_qa_dir(base_dir), "calibration_log.json")


def get_calibration_log(base_dir: str) -> List[dict]:
    """Get all calibration records."""
    data = _load(_calibration_path(base_dir))
    return data.get("tools", [])


def save_calibration_record(base_dir: str, record: dict) -> dict:
    """Add or update a calibration record."""
    path = _calibration_path(base_dir)
    data = _load(path) or {"tools": []}

    if not record.get("tool_id"):
        record["tool_id"] = f"CAL-{uuid.uuid4().hex[:8].upper()}"
        record["created_at"] = datetime.datetime.now().isoformat()

    existing = next((i for i, t in enumerate(data["tools"])
                     if t.get("tool_id") == record["tool_id"]), None)
    if existing is not None:
        data["tools"][existing] = record
    else:
        data["tools"].append(record)

    record["updated_at"] = datetime.datetime.now().isoformat()
    _save(path, data)
    return record


def check_calibration_due(base_dir: str) -> List[dict]:
    """Check for tools with calibration due within 14 days."""
    tools = get_calibration_log(base_dir)
    alerts = []
    today = datetime.date.today()
    for t in tools:
        due = t.get("next_cal_date", "")
        if not due:
            continue
        try:
            due_date = datetime.date.fromisoformat(due)
            days_left = (due_date - today).days
            if days_left <= 0:
                alerts.append({**t, "alert": "OVERDUE", "days_left": days_left})
            elif days_left <= 14:
                alerts.append({**t, "alert": "DUE_SOON", "days_left": days_left})
        except (ValueError, TypeError):
            pass
    return alerts


# ═══════════════════════════════════════════════
# PROCEDURES LIBRARY
# ═══════════════════════════════════════════════

DEFAULT_PROCEDURES = [
    {
        "proc_id": "QM-001",
        "title": "Quality Manual",
        "category": "quality_manual",
        "standard_ref": "AISC 360 Chapter M",
        "revision": "A",
        "status": "active",
        "description": "Master quality management system document. Covers organizational structure, responsibilities, quality policy, and references to all supporting procedures.",
        "approved_by": "Quality Manager",
        "approved_date": "2024-01-01",
    },
    {
        "proc_id": "SOP-001",
        "title": "Receiving Inspection Procedure",
        "category": "inspection",
        "standard_ref": "AISC QM §5.3 / ASTM A6",
        "revision": "A",
        "status": "active",
        "description": "Inspection of incoming steel materials: verify MTRs, check heat numbers, confirm grade and dimensions, assess surface condition, log in traceability system.",
    },
    {
        "proc_id": "SOP-002",
        "title": "Welding Procedure — Production",
        "category": "welding",
        "standard_ref": "AWS D1.1 §5",
        "revision": "A",
        "status": "active",
        "description": "General production welding procedure covering fit-up, preheat, technique, interpass temp, and visual inspection. References specific WPS documents for each joint type.",
    },
    {
        "proc_id": "SOP-003",
        "title": "Non-Destructive Testing (NDT) Procedure",
        "category": "inspection",
        "standard_ref": "AWS D1.1 §6.12 / ASTM E494",
        "revision": "A",
        "status": "active",
        "description": "Ultrasonic testing (UT) procedure for CJP and partial pen welds. Covers equipment calibration, scanning technique, acceptance criteria per AWS D1.1 Table 6.2, and reporting requirements.",
    },
    {
        "proc_id": "SOP-004",
        "title": "NCR and Corrective Action Procedure",
        "category": "quality_manual",
        "standard_ref": "AISC QM §8.3 / §8.5",
        "revision": "A",
        "status": "active",
        "description": "Process for documenting non-conformances, conducting root cause analysis, implementing corrective actions, verifying effectiveness, and preventing recurrence.",
    },
    {
        "proc_id": "SOP-005",
        "title": "Fabrication and Assembly Procedure",
        "category": "fabrication",
        "standard_ref": "AISC 360 §M2",
        "revision": "A",
        "status": "active",
        "description": "Step-by-step fabrication process for columns, rafters, and purlins. Covers material handling, layout, cutting, forming, assembly, welding, cleaning, and inspection.",
    },
    {
        "proc_id": "SOP-006",
        "title": "Final Inspection and Shipping Procedure",
        "category": "inspection",
        "standard_ref": "AISC 360 §M4",
        "revision": "A",
        "status": "active",
        "description": "Final inspection checklist before shipping: dimensional verification, weld visual, surface prep, coating verification, marking, packaging, and load-out documentation.",
    },
    {
        "proc_id": "SOP-007",
        "title": "Equipment Calibration Procedure",
        "category": "calibration",
        "standard_ref": "AISC QM §7.6",
        "revision": "A",
        "status": "active",
        "description": "Calibration program for all measuring and testing equipment. Covers calibration intervals, methods, traceability to NIST standards, and out-of-tolerance handling.",
    },
    {
        "proc_id": "SOP-008",
        "title": "Document Control Procedure",
        "category": "quality_manual",
        "standard_ref": "AISC QM §4.2",
        "revision": "A",
        "status": "active",
        "description": "Controls for creation, review, approval, distribution, and revision of all quality documents. Ensures shop floor always uses current revision documents.",
    },
    {
        "proc_id": "SOP-009",
        "title": "Surface Preparation and Coating Procedure",
        "category": "fabrication",
        "standard_ref": "SSPC-SP2 / AISC CoP 2.0",
        "revision": "A",
        "status": "active",
        "description": "Surface cleaning, weld grinding, and cold galvanizing application. Covers DFT requirements, application conditions, and inspection criteria.",
    },
    {
        "proc_id": "SOP-010",
        "title": "Welder Qualification and Continuity Procedure",
        "category": "welding",
        "standard_ref": "AWS D1.1 §4.19",
        "revision": "A",
        "status": "active",
        "description": "Process for qualifying new welders, maintaining continuity records, and requalification when continuity lapses. Covers test positions, acceptance criteria, and record keeping.",
    },
]


def get_procedures(base_dir: str) -> List[dict]:
    """Get all procedures."""
    path = os.path.join(_qa_dir(base_dir), "procedures.json")
    data = _load(path)
    if not data:
        data = {"procedures": list(DEFAULT_PROCEDURES)}
        _save(path, data)
    return data.get("procedures", [])


def save_procedure(base_dir: str, proc: dict) -> dict:
    """Add or update a procedure."""
    path = os.path.join(_qa_dir(base_dir), "procedures.json")
    data = _load(path) or {"procedures": list(DEFAULT_PROCEDURES)}

    if not proc.get("proc_id"):
        num = len(data["procedures"]) + 1
        proc["proc_id"] = f"SOP-{num:03d}"
        proc["created_at"] = datetime.datetime.now().isoformat()

    existing = next((i for i, p in enumerate(data["procedures"])
                     if p.get("proc_id") == proc["proc_id"]), None)
    if existing is not None:
        data["procedures"][existing] = proc
    else:
        data["procedures"].append(proc)

    proc["updated_at"] = datetime.datetime.now().isoformat()
    _save(path, data)
    return proc


# ═══════════════════════════════════════════════
# INSPECTOR QUALIFICATIONS REGISTRY
# ═══════════════════════════════════════════════

# Certification types and their inspection scopes
INSPECTOR_CERT_TYPES = {
    "CWI": {
        "name": "Certified Welding Inspector",
        "standard": "AWS QC1",
        "scopes": ["visual_weld", "wps_compliance", "welder_qualification", "final_inspection"],
    },
    "SCWI": {
        "name": "Senior Certified Welding Inspector",
        "standard": "AWS QC1",
        "scopes": ["visual_weld", "wps_compliance", "welder_qualification", "final_inspection", "ndt_oversight"],
    },
    "ASNT_II_UT": {
        "name": "ASNT Level II — Ultrasonic Testing",
        "standard": "ASNT SNT-TC-1A",
        "scopes": ["ndt_ut"],
    },
    "ASNT_II_MT": {
        "name": "ASNT Level II — Magnetic Particle Testing",
        "standard": "ASNT SNT-TC-1A",
        "scopes": ["ndt_mt"],
    },
    "ASNT_II_PT": {
        "name": "ASNT Level II — Liquid Penetrant Testing",
        "standard": "ASNT SNT-TC-1A",
        "scopes": ["ndt_pt"],
    },
    "ASNT_III": {
        "name": "ASNT Level III — NDE",
        "standard": "ASNT SNT-TC-1A",
        "scopes": ["ndt_ut", "ndt_mt", "ndt_pt", "ndt_oversight"],
    },
    "QC_TECH": {
        "name": "QC Technician (In-House)",
        "standard": "Company QM-001",
        "scopes": ["dimensional", "visual_general", "coating"],
    },
}

# Map inspection types to required cert scopes
INSPECTION_SCOPE_REQUIREMENTS = {
    "visual_weld":          ["CWI", "SCWI"],
    "wps_compliance":       ["CWI", "SCWI"],
    "welder_qualification": ["CWI", "SCWI"],
    "final_inspection":     ["CWI", "SCWI"],
    "ndt_ut":               ["ASNT_II_UT", "ASNT_III"],
    "ndt_mt":               ["ASNT_II_MT", "ASNT_III"],
    "ndt_pt":               ["ASNT_II_PT", "ASNT_III"],
    "ndt_oversight":        ["SCWI", "ASNT_III"],
    "dimensional":          ["QC_TECH", "CWI", "SCWI"],
    "visual_general":       ["QC_TECH", "CWI", "SCWI"],
    "coating":              ["QC_TECH", "CWI", "SCWI"],
    "qc_hold_release":      ["CWI", "SCWI"],
}


def _inspectors_path(base_dir: str) -> str:
    return os.path.join(_qa_dir(base_dir), "inspector_quals.json")


def get_inspector_quals(base_dir: str) -> List[dict]:
    """Get all inspector qualification records."""
    data = _load(_inspectors_path(base_dir))
    return data.get("inspectors", [])


def save_inspector_qual(base_dir: str, qual: dict) -> dict:
    """Add or update an inspector qualification record."""
    path = _inspectors_path(base_dir)
    data = _load(path) or {"inspectors": []}

    if not qual.get("qual_id"):
        qual["qual_id"] = f"IQ-{uuid.uuid4().hex[:8].upper()}"
        qual["created_at"] = datetime.datetime.now().isoformat()

    existing = next((i for i, q in enumerate(data["inspectors"])
                     if q.get("qual_id") == qual["qual_id"]), None)
    if existing is not None:
        data["inspectors"][existing] = qual
    else:
        data["inspectors"].append(qual)

    qual["updated_at"] = datetime.datetime.now().isoformat()
    _save(path, data)
    return qual


def delete_inspector_qual(base_dir: str, qual_id: str) -> bool:
    """Remove an inspector qualification record."""
    path = _inspectors_path(base_dir)
    data = _load(path) or {"inspectors": []}
    before = len(data["inspectors"])
    data["inspectors"] = [q for q in data["inspectors"] if q.get("qual_id") != qual_id]
    if len(data["inspectors"]) < before:
        _save(path, data)
        return True
    return False


def check_inspector_expirations(base_dir: str) -> List[dict]:
    """Check for expiring inspector certifications (within 60 days)."""
    inspectors = get_inspector_quals(base_dir)
    alerts = []
    today = datetime.date.today()
    for q in inspectors:
        exp = q.get("expiration_date", "")
        if not exp:
            continue
        try:
            exp_date = datetime.date.fromisoformat(exp)
            days_left = (exp_date - today).days
            if days_left <= 0:
                alerts.append({**q, "alert": "EXPIRED", "days_left": days_left})
            elif days_left <= 60:
                alerts.append({**q, "alert": "EXPIRING_SOON", "days_left": days_left})
        except (ValueError, TypeError):
            pass
    return alerts


def validate_inspector_for_scope(base_dir: str, inspector_name: str,
                                  inspection_type: str) -> dict:
    """
    Check if a named inspector has valid, non-expired credentials
    for the given inspection type.

    Returns: {"ok": True/False, "inspector": {...}, "cert_type": "CWI", ...}
    """
    inspection_type = inspection_type.lower().strip()
    required_certs = INSPECTION_SCOPE_REQUIREMENTS.get(inspection_type)

    # If not a controlled scope, allow anyone
    if required_certs is None:
        return {"ok": True, "reason": "uncontrolled_scope"}

    inspectors = get_inspector_quals(base_dir)
    today = datetime.date.today()

    # Find matching inspector by name (case-insensitive)
    name_lower = inspector_name.lower().strip()
    matches = [q for q in inspectors
                if q.get("inspector_name", "").lower().strip() == name_lower]

    if not matches:
        return {
            "ok": False,
            "error": f"Inspector '{inspector_name}' not found in qualification registry",
            "hint": "Add this inspector via QA > Inspector Registry before they can perform controlled inspections",
        }

    # Check if any of their certs cover this scope and are current
    for q in matches:
        cert_type = q.get("cert_type", "")
        if cert_type not in required_certs:
            continue
        if q.get("status") not in ("active", None, ""):
            continue
        exp = q.get("expiration_date", "")
        if exp:
            try:
                if datetime.date.fromisoformat(exp) < today:
                    continue  # expired
            except (ValueError, TypeError):
                pass
        # Valid cert found
        return {
            "ok": True,
            "inspector": q,
            "cert_type": cert_type,
            "cert_name": INSPECTOR_CERT_TYPES.get(cert_type, {}).get("name", cert_type),
        }

    # Has a record but no valid cert for this scope
    held_certs = [q.get("cert_type", "?") for q in matches]
    return {
        "ok": False,
        "error": f"Inspector '{inspector_name}' does not hold a valid certification for '{inspection_type}' inspections",
        "held_certs": held_certs,
        "required_certs": required_certs,
    }


def get_inspector_registry_summary(base_dir: str) -> dict:
    """Summary data for the inspector registry dashboard."""
    inspectors = get_inspector_quals(base_dir)
    today = datetime.date.today()
    active = 0
    expired = 0
    expiring_soon = 0
    by_type = {}

    for q in inspectors:
        ct = q.get("cert_type", "OTHER")
        by_type[ct] = by_type.get(ct, 0) + 1

        exp = q.get("expiration_date", "")
        if not exp:
            active += 1
            continue
        try:
            exp_date = datetime.date.fromisoformat(exp)
            days_left = (exp_date - today).days
            if days_left <= 0:
                expired += 1
            elif days_left <= 60:
                expiring_soon += 1
                active += 1
            else:
                active += 1
        except (ValueError, TypeError):
            active += 1

    return {
        "total": len(inspectors),
        "active": active,
        "expired": expired,
        "expiring_soon": expiring_soon,
        "by_type": by_type,
    }


# ═══════════════════════════════════════════════
# PROCEDURE QUALIFICATION RECORDS (PQR)
# ═══════════════════════════════════════════════

def _pqr_path(base_dir: str) -> str:
    return os.path.join(_qa_dir(base_dir), "pqr_library.json")


def get_pqr_library(base_dir: str) -> List[dict]:
    """Get all PQR records."""
    data = _load(_pqr_path(base_dir))
    return data.get("pqrs", [])


def save_pqr(base_dir: str, record: dict) -> dict:
    """Add or update a PQR record."""
    path = _pqr_path(base_dir)
    data = _load(path)
    if "pqrs" not in data:
        data["pqrs"] = []

    pqr_id = record.get("pqr_id", "")
    existing = [i for i, p in enumerate(data["pqrs"]) if p.get("pqr_id") == pqr_id]
    if existing:
        record["updated_at"] = datetime.datetime.now().isoformat()
        data["pqrs"][existing[0]] = record
    else:
        record["pqr_id"] = "PQR-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        record["created_at"] = datetime.datetime.now().isoformat()
        record["updated_at"] = record["created_at"]
        data["pqrs"].append(record)

    _save(path, data)
    return record


def delete_pqr(base_dir: str, pqr_id: str) -> bool:
    """Remove a PQR record."""
    path = _pqr_path(base_dir)
    data = _load(path)
    before = len(data.get("pqrs", []))
    data["pqrs"] = [p for p in data.get("pqrs", []) if p.get("pqr_id") != pqr_id]
    if len(data["pqrs"]) < before:
        _save(path, data)
        return True
    return False


# ═══════════════════════════════════════════════
# QA DASHBOARD STATS
# ═══════════════════════════════════════════════

def get_qa_stats(base_dir: str) -> dict:
    """Aggregate QA stats for the hub dashboard."""
    wps_lib = get_wps_library(base_dir)
    active_wps = sum(1 for w in wps_lib.values() if w.get("status") == "active")

    welders = get_welder_certs(base_dir)
    active_welders = sum(1 for w in welders
                         if w.get("status", "active") == "active")

    tools = get_calibration_log(base_dir)
    in_cal = sum(1 for t in tools if t.get("status", "active") == "active")

    welder_alerts = check_welder_expirations(base_dir)
    cal_alerts = check_calibration_due(base_dir)
    inspector_alerts = check_inspector_expirations(base_dir)
    inspector_summary = get_inspector_registry_summary(base_dir)

    # Count NCRs from QC data (scan all project QC files)
    qc_dir = os.path.join(os.path.dirname(_qa_dir(base_dir)), "qc")
    open_ncrs = 0
    inspections_30d = 0
    cutoff = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()

    if os.path.isdir(qc_dir):
        for fname in os.listdir(qc_dir):
            if not fname.endswith(".json"):
                continue
            try:
                with open(os.path.join(qc_dir, fname)) as f:
                    qc_data = json.load(f)
                for ncr in qc_data.get("ncrs", []):
                    if ncr.get("status") in ("open", "under_review", "corrective_action"):
                        open_ncrs += 1
                for ins in qc_data.get("inspections", []):
                    created = ins.get("created_at", "")
                    if created >= cutoff:
                        inspections_30d += 1
            except (json.JSONDecodeError, IOError):
                pass

    return {
        "ok": True,
        "active_wps": active_wps,
        "certified_welders": active_welders,
        "inspections_30d": inspections_30d,
        "open_ncrs": open_ncrs,
        "calibrated_tools": in_cal,
        "welder_alerts": [{"name": a.get("welder_name",""), "alert": a.get("alert",""), "days_left": a.get("days_left",0)} for a in welder_alerts],
        "calibration_alerts": [{"tool": a.get("tool_name",""), "alert": a.get("alert",""), "days_left": a.get("days_left",0)} for a in cal_alerts],
        "inspector_alerts": [{"name": a.get("inspector_name",""), "cert_type": a.get("cert_type",""), "alert": a.get("alert",""), "days_left": a.get("days_left",0)} for a in inspector_alerts],
        "qualified_inspectors": inspector_summary.get("active", 0),
    }
