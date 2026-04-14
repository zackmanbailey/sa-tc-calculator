"""
TitanForge v4 — Document Management & Drawing Revisions
=========================================================
Formal document revision control, RFI tracking, transmittal logs,
and BOM change tracking for engineering and shop drawings.

Covers:
  - Drawing revisions with version history, markup notes, approval status
  - RFIs (Requests for Information) with response tracking
  - Transmittals for sending drawing packages to customers/field
  - BOM change orders tracking what changed between revisions

Integrates with existing:
  - Project docs system (tf_handlers.py ProjectDocUploadHandler, etc.)
  - Shop drawing revision tracking (_load_revisions, _save_revision)
  - ShopDrawingConfig for BOM data

Permissions (reuses existing):
  - VIEW_SHOP_DRAWINGS: read-only access to documents, revisions, RFIs
  - EDIT_SHOP_DRAWINGS: create/edit revisions, create RFIs, create transmittals
  - APPROVE_DRAWINGS: approve/reject revisions, close RFIs

Reference: RULES.md §3 (Role Definitions)
"""

import os
import json
import uuid
import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from collections import defaultdict


# ─────────────────────────────────────────────
# DRAWING REVISION STATUS CONSTANTS
# ─────────────────────────────────────────────

REV_STATUS_DRAFT = "draft"               # Uploaded, not yet submitted
REV_STATUS_SUBMITTED = "submitted"       # Submitted for review
REV_STATUS_IN_REVIEW = "in_review"       # Being reviewed
REV_STATUS_APPROVED = "approved"         # Approved for fabrication
REV_STATUS_REJECTED = "rejected"         # Rejected — needs rework
REV_STATUS_SUPERSEDED = "superseded"     # Replaced by newer revision

REV_STATUSES = [
    REV_STATUS_DRAFT, REV_STATUS_SUBMITTED, REV_STATUS_IN_REVIEW,
    REV_STATUS_APPROVED, REV_STATUS_REJECTED, REV_STATUS_SUPERSEDED,
]

REV_STATUS_LABELS = {
    REV_STATUS_DRAFT: "Draft",
    REV_STATUS_SUBMITTED: "Submitted",
    REV_STATUS_IN_REVIEW: "In Review",
    REV_STATUS_APPROVED: "Approved",
    REV_STATUS_REJECTED: "Rejected",
    REV_STATUS_SUPERSEDED: "Superseded",
}

REV_STATUS_COLORS = {
    REV_STATUS_DRAFT: "gray",
    REV_STATUS_SUBMITTED: "blue",
    REV_STATUS_IN_REVIEW: "orange",
    REV_STATUS_APPROVED: "green",
    REV_STATUS_REJECTED: "red",
    REV_STATUS_SUPERSEDED: "purple",
}

# Valid transitions
REV_STATUS_FLOW = {
    REV_STATUS_DRAFT: [REV_STATUS_SUBMITTED],
    REV_STATUS_SUBMITTED: [REV_STATUS_IN_REVIEW, REV_STATUS_REJECTED],
    REV_STATUS_IN_REVIEW: [REV_STATUS_APPROVED, REV_STATUS_REJECTED],
    REV_STATUS_APPROVED: [REV_STATUS_SUPERSEDED],
    REV_STATUS_REJECTED: [REV_STATUS_DRAFT],   # Back to draft for rework
    REV_STATUS_SUPERSEDED: [],                   # Terminal
}


# ─────────────────────────────────────────────
# DOCUMENT CATEGORIES
# ─────────────────────────────────────────────

DOC_CAT_ENGINEERING = "engineering"
DOC_CAT_SHOP_DRAWINGS = "shop_drawings"
DOC_CAT_SUBMITTALS = "submittals"
DOC_CAT_FIELD = "field"
DOC_CAT_AS_BUILT = "as_built"
DOC_CAT_SPECIFICATIONS = "specifications"

DOC_CATEGORIES = [
    DOC_CAT_ENGINEERING, DOC_CAT_SHOP_DRAWINGS, DOC_CAT_SUBMITTALS,
    DOC_CAT_FIELD, DOC_CAT_AS_BUILT, DOC_CAT_SPECIFICATIONS,
]

DOC_CATEGORY_LABELS = {
    DOC_CAT_ENGINEERING: "Engineering Drawings",
    DOC_CAT_SHOP_DRAWINGS: "Shop Drawings",
    DOC_CAT_SUBMITTALS: "Submittals",
    DOC_CAT_FIELD: "Field Documents",
    DOC_CAT_AS_BUILT: "As-Built Drawings",
    DOC_CAT_SPECIFICATIONS: "Specifications",
}


# ─────────────────────────────────────────────
# RFI STATUS CONSTANTS
# ─────────────────────────────────────────────

RFI_STATUS_OPEN = "open"
RFI_STATUS_PENDING = "pending"           # Awaiting response
RFI_STATUS_ANSWERED = "answered"         # Response received
RFI_STATUS_CLOSED = "closed"             # Resolved and closed
RFI_STATUS_VOID = "void"                 # Cancelled

RFI_STATUSES = [
    RFI_STATUS_OPEN, RFI_STATUS_PENDING, RFI_STATUS_ANSWERED,
    RFI_STATUS_CLOSED, RFI_STATUS_VOID,
]

RFI_STATUS_LABELS = {
    RFI_STATUS_OPEN: "Open",
    RFI_STATUS_PENDING: "Pending Response",
    RFI_STATUS_ANSWERED: "Answered",
    RFI_STATUS_CLOSED: "Closed",
    RFI_STATUS_VOID: "Void",
}

RFI_PRIORITY_CRITICAL = "critical"
RFI_PRIORITY_HIGH = "high"
RFI_PRIORITY_NORMAL = "normal"
RFI_PRIORITY_LOW = "low"

RFI_PRIORITIES = [RFI_PRIORITY_CRITICAL, RFI_PRIORITY_HIGH,
                  RFI_PRIORITY_NORMAL, RFI_PRIORITY_LOW]

RFI_PRIORITY_LABELS = {
    RFI_PRIORITY_CRITICAL: "Critical",
    RFI_PRIORITY_HIGH: "High",
    RFI_PRIORITY_NORMAL: "Normal",
    RFI_PRIORITY_LOW: "Low",
}


# ─────────────────────────────────────────────
# TRANSMITTAL STATUS
# ─────────────────────────────────────────────

XMIT_STATUS_DRAFT = "draft"
XMIT_STATUS_SENT = "sent"
XMIT_STATUS_ACKNOWLEDGED = "acknowledged"

XMIT_STATUSES = [XMIT_STATUS_DRAFT, XMIT_STATUS_SENT, XMIT_STATUS_ACKNOWLEDGED]

XMIT_STATUS_LABELS = {
    XMIT_STATUS_DRAFT: "Draft",
    XMIT_STATUS_SENT: "Sent",
    XMIT_STATUS_ACKNOWLEDGED: "Acknowledged",
}

# Transmittal purposes
XMIT_FOR_APPROVAL = "for_approval"
XMIT_FOR_CONSTRUCTION = "for_construction"
XMIT_FOR_RECORD = "for_record"
XMIT_FOR_REVIEW = "for_review"

XMIT_PURPOSES = [XMIT_FOR_APPROVAL, XMIT_FOR_CONSTRUCTION,
                  XMIT_FOR_RECORD, XMIT_FOR_REVIEW]

XMIT_PURPOSE_LABELS = {
    XMIT_FOR_APPROVAL: "For Approval",
    XMIT_FOR_CONSTRUCTION: "For Construction",
    XMIT_FOR_RECORD: "For Record",
    XMIT_FOR_REVIEW: "For Review",
}


# ─────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────

@dataclass
class DrawingRevision:
    """A specific revision of a drawing document."""
    revision_id: str = ""
    job_code: str = ""
    drawing_number: str = ""           # e.g., "SD-001", "ENG-A100"
    title: str = ""
    category: str = DOC_CAT_SHOP_DRAWINGS
    revision: str = ""                  # "A", "B", "C", etc.
    status: str = REV_STATUS_DRAFT
    filename: str = ""                  # Stored filename
    file_size: int = 0
    description: str = ""
    markup_notes: str = ""              # Review markup comments
    created_by: str = ""
    created_at: str = ""
    submitted_by: str = ""
    submitted_at: str = ""
    reviewed_by: str = ""
    reviewed_at: str = ""
    approved_by: str = ""
    approved_at: str = ""
    rejection_reason: str = ""
    superseded_by: str = ""            # revision_id of newer revision
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.revision_id:
            self.revision_id = f"REV-{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "DrawingRevision":
        obj = cls()
        for k, v in d.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        return obj

    @property
    def status_label(self) -> str:
        return REV_STATUS_LABELS.get(self.status, self.status)

    @property
    def status_color(self) -> str:
        return REV_STATUS_COLORS.get(self.status, "gray")

    @property
    def category_label(self) -> str:
        return DOC_CATEGORY_LABELS.get(self.category, self.category)

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in REV_STATUS_FLOW.get(self.status, [])


@dataclass
class RFI:
    """Request for Information — questions about drawings/specs."""
    rfi_id: str = ""
    rfi_number: int = 0                 # Sequential number (auto-assigned)
    job_code: str = ""
    subject: str = ""
    question: str = ""
    priority: str = RFI_PRIORITY_NORMAL
    status: str = RFI_STATUS_OPEN
    drawing_ref: str = ""               # Related drawing number
    revision_ref: str = ""              # Related revision_id
    response: str = ""
    responded_by: str = ""
    responded_at: str = ""
    impact_description: str = ""        # Schedule/cost impact
    created_by: str = ""
    created_at: str = ""
    closed_by: str = ""
    closed_at: str = ""
    due_date: str = ""                  # Expected response date

    def __post_init__(self):
        if not self.rfi_id:
            self.rfi_id = f"RFI-{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "RFI":
        obj = cls()
        for k, v in d.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        return obj

    @property
    def status_label(self) -> str:
        return RFI_STATUS_LABELS.get(self.status, self.status)

    @property
    def priority_label(self) -> str:
        return RFI_PRIORITY_LABELS.get(self.priority, self.priority)

    @property
    def is_overdue(self) -> bool:
        if not self.due_date or self.status in [RFI_STATUS_CLOSED, RFI_STATUS_VOID]:
            return False
        return self.due_date < datetime.date.today().isoformat()


@dataclass
class Transmittal:
    """A transmittal package — set of documents sent to a recipient."""
    transmittal_id: str = ""
    transmittal_number: int = 0         # Sequential number
    job_code: str = ""
    recipient: str = ""                 # Company/person name
    recipient_email: str = ""
    purpose: str = XMIT_FOR_REVIEW
    status: str = XMIT_STATUS_DRAFT
    subject: str = ""
    notes: str = ""
    documents: List[Dict[str, str]] = field(default_factory=list)  # [{drawing_number, revision, title}]
    created_by: str = ""
    created_at: str = ""
    sent_at: str = ""
    acknowledged_at: str = ""
    acknowledged_by: str = ""

    def __post_init__(self):
        if not self.transmittal_id:
            self.transmittal_id = f"XMIT-{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Transmittal":
        obj = cls()
        for k, v in d.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        return obj

    @property
    def status_label(self) -> str:
        return XMIT_STATUS_LABELS.get(self.status, self.status)

    @property
    def purpose_label(self) -> str:
        return XMIT_PURPOSE_LABELS.get(self.purpose, self.purpose)


@dataclass
class BOMChangeOrder:
    """Tracks changes between BOM revisions."""
    change_id: str = ""
    job_code: str = ""
    from_revision: str = ""             # Previous revision letter
    to_revision: str = ""               # New revision letter
    change_type: str = ""               # "added", "removed", "modified", "quantity_change"
    component: str = ""                 # Component description
    field_changed: str = ""             # Which field changed
    old_value: str = ""
    new_value: str = ""
    reason: str = ""
    created_by: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.change_id:
            self.change_id = f"BCO-{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "BOMChangeOrder":
        obj = cls()
        for k, v in d.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        return obj


# ─────────────────────────────────────────────
# FILE STORAGE
# ─────────────────────────────────────────────

def _docs_dir(base_dir: str) -> str:
    d = os.path.join(base_dir, "_documents")
    os.makedirs(d, exist_ok=True)
    return d

def _load_json(base_dir: str, filename: str) -> list:
    path = os.path.join(_docs_dir(base_dir), filename)
    if not os.path.isfile(path):
        return []
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []

def _save_json(base_dir: str, filename: str, data: list):
    path = os.path.join(_docs_dir(base_dir), filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def _load_revisions_file(base_dir: str) -> list:
    return _load_json(base_dir, "revisions.json")

def _save_revisions_file(base_dir: str, data: list):
    _save_json(base_dir, "revisions.json", data)

def _load_rfis_file(base_dir: str) -> list:
    return _load_json(base_dir, "rfis.json")

def _save_rfis_file(base_dir: str, data: list):
    _save_json(base_dir, "rfis.json", data)

def _load_transmittals_file(base_dir: str) -> list:
    return _load_json(base_dir, "transmittals.json")

def _save_transmittals_file(base_dir: str, data: list):
    _save_json(base_dir, "transmittals.json", data)

def _load_bom_changes_file(base_dir: str) -> list:
    return _load_json(base_dir, "bom_changes.json")

def _save_bom_changes_file(base_dir: str, data: list):
    _save_json(base_dir, "bom_changes.json", data)


# ─────────────────────────────────────────────
# DRAWING REVISION CRUD
# ─────────────────────────────────────────────

def create_revision(base_dir: str, job_code: str, drawing_number: str,
                    title: str, revision: str, created_by: str,
                    category: str = DOC_CAT_SHOP_DRAWINGS,
                    filename: str = "", file_size: int = 0,
                    description: str = "",
                    metadata: Optional[dict] = None) -> DrawingRevision:
    """Create a new drawing revision."""
    rev = DrawingRevision(
        job_code=job_code,
        drawing_number=drawing_number,
        title=title,
        revision=revision,
        category=category,
        filename=filename,
        file_size=file_size,
        description=description,
        created_by=created_by,
        metadata=metadata or {},
    )

    data = _load_revisions_file(base_dir)
    data.append(rev.to_dict())
    _save_revisions_file(base_dir, data)
    return rev


def get_revision(base_dir: str, revision_id: str) -> Optional[DrawingRevision]:
    """Get a single revision by ID."""
    data = _load_revisions_file(base_dir)
    for d in data:
        if d.get("revision_id") == revision_id:
            return DrawingRevision.from_dict(d)
    return None


def list_revisions(base_dir: str, job_code: str = "",
                   category: str = "", drawing_number: str = "",
                   status: str = "") -> List[DrawingRevision]:
    """List revisions with optional filters."""
    data = _load_revisions_file(base_dir)
    result = []
    for d in data:
        if job_code and d.get("job_code") != job_code:
            continue
        if category and d.get("category") != category:
            continue
        if drawing_number and d.get("drawing_number") != drawing_number:
            continue
        if status and d.get("status") != status:
            continue
        result.append(DrawingRevision.from_dict(d))
    # Sort newest first
    result.sort(key=lambda r: r.created_at, reverse=True)
    return result


def transition_revision(base_dir: str, revision_id: str, new_status: str,
                        actor: str, **kwargs) -> Optional[DrawingRevision]:
    """Transition a revision to a new status."""
    data = _load_revisions_file(base_dir)
    for i, d in enumerate(data):
        if d.get("revision_id") != revision_id:
            continue
        rev = DrawingRevision.from_dict(d)
        if not rev.can_transition_to(new_status):
            return None

        rev.status = new_status
        now = datetime.datetime.now().isoformat()

        if new_status == REV_STATUS_SUBMITTED:
            rev.submitted_by = actor
            rev.submitted_at = now
        elif new_status == REV_STATUS_IN_REVIEW:
            rev.reviewed_by = actor
            rev.reviewed_at = now
        elif new_status == REV_STATUS_APPROVED:
            rev.approved_by = actor
            rev.approved_at = now
            # Auto-supersede previous approved revision for same drawing
            for j, other in enumerate(data):
                if (other.get("drawing_number") == rev.drawing_number
                        and other.get("job_code") == rev.job_code
                        and other.get("revision_id") != rev.revision_id
                        and other.get("status") == REV_STATUS_APPROVED):
                    data[j]["status"] = REV_STATUS_SUPERSEDED
                    data[j]["superseded_by"] = rev.revision_id
        elif new_status == REV_STATUS_REJECTED:
            rev.rejection_reason = kwargs.get("reason", "")

        for k, v in kwargs.items():
            if hasattr(rev, k) and k not in ("revision_id", "status"):
                setattr(rev, k, v)

        data[i] = rev.to_dict()
        _save_revisions_file(base_dir, data)
        return rev
    return None


def get_latest_revision(base_dir: str, job_code: str,
                        drawing_number: str) -> Optional[DrawingRevision]:
    """Get the latest (most recent) revision for a drawing."""
    revs = list_revisions(base_dir, job_code=job_code,
                          drawing_number=drawing_number)
    return revs[0] if revs else None


def get_revision_history(base_dir: str, job_code: str,
                         drawing_number: str) -> List[DrawingRevision]:
    """Get full revision history for a drawing, newest first."""
    return list_revisions(base_dir, job_code=job_code,
                          drawing_number=drawing_number)


# ─────────────────────────────────────────────
# RFI CRUD
# ─────────────────────────────────────────────

def create_rfi(base_dir: str, job_code: str, subject: str,
               question: str, created_by: str,
               priority: str = RFI_PRIORITY_NORMAL,
               drawing_ref: str = "", revision_ref: str = "",
               due_date: str = "",
               impact_description: str = "") -> RFI:
    """Create a new RFI."""
    data = _load_rfis_file(base_dir)

    # Auto-assign RFI number (sequential per project)
    project_rfis = [d for d in data if d.get("job_code") == job_code]
    next_num = max((d.get("rfi_number", 0) for d in project_rfis), default=0) + 1

    rfi = RFI(
        rfi_number=next_num,
        job_code=job_code,
        subject=subject,
        question=question,
        priority=priority,
        drawing_ref=drawing_ref,
        revision_ref=revision_ref,
        due_date=due_date,
        impact_description=impact_description,
        created_by=created_by,
    )

    data.append(rfi.to_dict())
    _save_rfis_file(base_dir, data)
    return rfi


def get_rfi(base_dir: str, rfi_id: str) -> Optional[RFI]:
    """Get a single RFI by ID."""
    data = _load_rfis_file(base_dir)
    for d in data:
        if d.get("rfi_id") == rfi_id:
            return RFI.from_dict(d)
    return None


def list_rfis(base_dir: str, job_code: str = "",
              status: str = "", priority: str = "") -> List[RFI]:
    """List RFIs with optional filters."""
    data = _load_rfis_file(base_dir)
    result = []
    for d in data:
        if job_code and d.get("job_code") != job_code:
            continue
        if status and d.get("status") != status:
            continue
        if priority and d.get("priority") != priority:
            continue
        result.append(RFI.from_dict(d))
    result.sort(key=lambda r: r.created_at, reverse=True)
    return result


def respond_to_rfi(base_dir: str, rfi_id: str, response: str,
                   responded_by: str) -> Optional[RFI]:
    """Add a response to an RFI."""
    data = _load_rfis_file(base_dir)
    for i, d in enumerate(data):
        if d.get("rfi_id") == rfi_id:
            d["response"] = response
            d["responded_by"] = responded_by
            d["responded_at"] = datetime.datetime.now().isoformat()
            d["status"] = RFI_STATUS_ANSWERED
            data[i] = d
            _save_rfis_file(base_dir, data)
            return RFI.from_dict(d)
    return None


def close_rfi(base_dir: str, rfi_id: str, closed_by: str) -> Optional[RFI]:
    """Close an RFI."""
    data = _load_rfis_file(base_dir)
    for i, d in enumerate(data):
        if d.get("rfi_id") == rfi_id:
            d["status"] = RFI_STATUS_CLOSED
            d["closed_by"] = closed_by
            d["closed_at"] = datetime.datetime.now().isoformat()
            data[i] = d
            _save_rfis_file(base_dir, data)
            return RFI.from_dict(d)
    return None


def void_rfi(base_dir: str, rfi_id: str) -> Optional[RFI]:
    """Void/cancel an RFI."""
    data = _load_rfis_file(base_dir)
    for i, d in enumerate(data):
        if d.get("rfi_id") == rfi_id:
            d["status"] = RFI_STATUS_VOID
            data[i] = d
            _save_rfis_file(base_dir, data)
            return RFI.from_dict(d)
    return None


# ─────────────────────────────────────────────
# TRANSMITTAL CRUD
# ─────────────────────────────────────────────

def create_transmittal(base_dir: str, job_code: str, recipient: str,
                       purpose: str, created_by: str,
                       subject: str = "", notes: str = "",
                       recipient_email: str = "",
                       documents: Optional[List[dict]] = None) -> Transmittal:
    """Create a new transmittal."""
    data = _load_transmittals_file(base_dir)

    # Auto-assign transmittal number
    project_xmits = [d for d in data if d.get("job_code") == job_code]
    next_num = max((d.get("transmittal_number", 0) for d in project_xmits), default=0) + 1

    xmit = Transmittal(
        transmittal_number=next_num,
        job_code=job_code,
        recipient=recipient,
        recipient_email=recipient_email,
        purpose=purpose,
        subject=subject,
        notes=notes,
        documents=documents or [],
        created_by=created_by,
    )

    data.append(xmit.to_dict())
    _save_transmittals_file(base_dir, data)
    return xmit


def get_transmittal(base_dir: str, transmittal_id: str) -> Optional[Transmittal]:
    """Get a single transmittal by ID."""
    data = _load_transmittals_file(base_dir)
    for d in data:
        if d.get("transmittal_id") == transmittal_id:
            return Transmittal.from_dict(d)
    return None


def list_transmittals(base_dir: str, job_code: str = "",
                      status: str = "") -> List[Transmittal]:
    """List transmittals with optional filters."""
    data = _load_transmittals_file(base_dir)
    result = []
    for d in data:
        if job_code and d.get("job_code") != job_code:
            continue
        if status and d.get("status") != status:
            continue
        result.append(Transmittal.from_dict(d))
    result.sort(key=lambda r: r.created_at, reverse=True)
    return result


def send_transmittal(base_dir: str, transmittal_id: str) -> Optional[Transmittal]:
    """Mark a transmittal as sent."""
    data = _load_transmittals_file(base_dir)
    for i, d in enumerate(data):
        if d.get("transmittal_id") == transmittal_id:
            d["status"] = XMIT_STATUS_SENT
            d["sent_at"] = datetime.datetime.now().isoformat()
            data[i] = d
            _save_transmittals_file(base_dir, data)
            return Transmittal.from_dict(d)
    return None


def acknowledge_transmittal(base_dir: str, transmittal_id: str,
                            acknowledged_by: str) -> Optional[Transmittal]:
    """Mark a transmittal as acknowledged by recipient."""
    data = _load_transmittals_file(base_dir)
    for i, d in enumerate(data):
        if d.get("transmittal_id") == transmittal_id:
            d["status"] = XMIT_STATUS_ACKNOWLEDGED
            d["acknowledged_at"] = datetime.datetime.now().isoformat()
            d["acknowledged_by"] = acknowledged_by
            data[i] = d
            _save_transmittals_file(base_dir, data)
            return Transmittal.from_dict(d)
    return None


# ─────────────────────────────────────────────
# BOM CHANGE ORDER CRUD
# ─────────────────────────────────────────────

BOM_CHANGE_ADDED = "added"
BOM_CHANGE_REMOVED = "removed"
BOM_CHANGE_MODIFIED = "modified"
BOM_CHANGE_QUANTITY = "quantity_change"

BOM_CHANGE_TYPES = [BOM_CHANGE_ADDED, BOM_CHANGE_REMOVED,
                    BOM_CHANGE_MODIFIED, BOM_CHANGE_QUANTITY]

BOM_CHANGE_TYPE_LABELS = {
    BOM_CHANGE_ADDED: "Added",
    BOM_CHANGE_REMOVED: "Removed",
    BOM_CHANGE_MODIFIED: "Modified",
    BOM_CHANGE_QUANTITY: "Quantity Change",
}


def log_bom_change(base_dir: str, job_code: str,
                   from_revision: str, to_revision: str,
                   change_type: str, component: str,
                   created_by: str,
                   field_changed: str = "",
                   old_value: str = "", new_value: str = "",
                   reason: str = "") -> BOMChangeOrder:
    """Log a BOM change between revisions."""
    bco = BOMChangeOrder(
        job_code=job_code,
        from_revision=from_revision,
        to_revision=to_revision,
        change_type=change_type,
        component=component,
        field_changed=field_changed,
        old_value=old_value,
        new_value=new_value,
        reason=reason,
        created_by=created_by,
    )

    data = _load_bom_changes_file(base_dir)
    data.append(bco.to_dict())
    _save_bom_changes_file(base_dir, data)
    return bco


def list_bom_changes(base_dir: str, job_code: str = "",
                     from_revision: str = "",
                     to_revision: str = "") -> List[BOMChangeOrder]:
    """List BOM changes with optional filters."""
    data = _load_bom_changes_file(base_dir)
    result = []
    for d in data:
        if job_code and d.get("job_code") != job_code:
            continue
        if from_revision and d.get("from_revision") != from_revision:
            continue
        if to_revision and d.get("to_revision") != to_revision:
            continue
        result.append(BOMChangeOrder.from_dict(d))
    result.sort(key=lambda r: r.created_at, reverse=True)
    return result


def get_bom_change_summary(base_dir: str, job_code: str) -> dict:
    """Get a summary of all BOM changes for a project."""
    changes = list_bom_changes(base_dir, job_code=job_code)
    by_type = defaultdict(int)
    by_revision = defaultdict(int)
    for c in changes:
        by_type[c.change_type] += 1
        key = f"{c.from_revision} → {c.to_revision}"
        by_revision[key] += 1

    return {
        "job_code": job_code,
        "total_changes": len(changes),
        "by_type": dict(by_type),
        "by_revision_pair": dict(by_revision),
    }


# ─────────────────────────────────────────────
# DOCUMENT MANAGEMENT ANALYTICS
# ─────────────────────────────────────────────

def get_document_summary(base_dir: str, job_code: str = "") -> dict:
    """Overall document management summary."""
    revisions = list_revisions(base_dir, job_code=job_code)
    rfis = list_rfis(base_dir, job_code=job_code)
    transmittals = list_transmittals(base_dir, job_code=job_code)

    # Revision stats
    rev_by_status = defaultdict(int)
    rev_by_category = defaultdict(int)
    for r in revisions:
        rev_by_status[r.status] += 1
        rev_by_category[r.category] += 1

    # RFI stats
    rfi_by_status = defaultdict(int)
    rfi_by_priority = defaultdict(int)
    overdue_rfis = 0
    for r in rfis:
        rfi_by_status[r.status] += 1
        rfi_by_priority[r.priority] += 1
        if r.is_overdue:
            overdue_rfis += 1

    # Transmittal stats
    xmit_by_status = defaultdict(int)
    for x in transmittals:
        xmit_by_status[x.status] += 1

    # Unique drawings
    unique_drawings = set()
    for r in revisions:
        unique_drawings.add(f"{r.job_code}:{r.drawing_number}")

    return {
        "total_revisions": len(revisions),
        "revisions_by_status": dict(rev_by_status),
        "revisions_by_category": dict(rev_by_category),
        "unique_drawings": len(unique_drawings),
        "total_rfis": len(rfis),
        "rfis_by_status": dict(rfi_by_status),
        "rfis_by_priority": dict(rfi_by_priority),
        "overdue_rfis": overdue_rfis,
        "open_rfis": rfi_by_status.get(RFI_STATUS_OPEN, 0) + rfi_by_status.get(RFI_STATUS_PENDING, 0),
        "total_transmittals": len(transmittals),
        "transmittals_by_status": dict(xmit_by_status),
    }
