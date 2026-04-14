#!/usr/bin/env python3
"""
TitanForge Phase 9 Tests — Document Management & Drawing Revisions
====================================================================
Tests drawing revisions, RFIs, transmittals, BOM changes,
handlers, RBAC, routes, template, and full E2E workflows.
"""

import os, sys, json, shutil, tempfile, datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

passed = 0
failed = 0
def test(label, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  \u2705 {label}")
    else:
        failed += 1
        print(f"  \u274c {label}")

tmp = tempfile.mkdtemp()

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 1: Revision Status Constants ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.documents import (
    REV_STATUSES, REV_STATUS_LABELS, REV_STATUS_COLORS, REV_STATUS_FLOW,
    REV_STATUS_DRAFT, REV_STATUS_SUBMITTED, REV_STATUS_IN_REVIEW,
    REV_STATUS_APPROVED, REV_STATUS_REJECTED, REV_STATUS_SUPERSEDED,
)

test("6 revision statuses", len(REV_STATUSES) == 6)
test("Draft status value", REV_STATUS_DRAFT == "draft")
test("Submitted status value", REV_STATUS_SUBMITTED == "submitted")
test("In-review status value", REV_STATUS_IN_REVIEW == "in_review")
test("Approved status value", REV_STATUS_APPROVED == "approved")
test("Rejected status value", REV_STATUS_REJECTED == "rejected")
test("Superseded status value", REV_STATUS_SUPERSEDED == "superseded")
test("All statuses have labels", all(s in REV_STATUS_LABELS for s in REV_STATUSES))
test("All statuses have colors", all(s in REV_STATUS_COLORS for s in REV_STATUSES))
test("Draft can transition to submitted", REV_STATUS_SUBMITTED in REV_STATUS_FLOW[REV_STATUS_DRAFT])
test("Submitted can transition to in_review", REV_STATUS_IN_REVIEW in REV_STATUS_FLOW[REV_STATUS_SUBMITTED])
test("In-review can transition to approved", REV_STATUS_APPROVED in REV_STATUS_FLOW[REV_STATUS_IN_REVIEW])
test("In-review can transition to rejected", REV_STATUS_REJECTED in REV_STATUS_FLOW[REV_STATUS_IN_REVIEW])
test("Approved can transition to superseded", REV_STATUS_SUPERSEDED in REV_STATUS_FLOW[REV_STATUS_APPROVED])
test("Rejected can transition to draft", REV_STATUS_DRAFT in REV_STATUS_FLOW[REV_STATUS_REJECTED])

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 2: Document Category Constants ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.documents import (
    DOC_CATEGORIES, DOC_CATEGORY_LABELS,
)

test("6 document categories", len(DOC_CATEGORIES) == 6)
test("All categories have labels", all(c in DOC_CATEGORY_LABELS for c in DOC_CATEGORIES))
test("shop_drawings in categories", "shop_drawings" in DOC_CATEGORIES)
test("engineering in categories", "engineering" in DOC_CATEGORIES)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 3: RFI Constants ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.documents import (
    RFI_STATUSES, RFI_STATUS_LABELS,
    RFI_STATUS_OPEN, RFI_STATUS_PENDING, RFI_STATUS_ANSWERED,
    RFI_STATUS_CLOSED, RFI_STATUS_VOID,
    RFI_PRIORITIES, RFI_PRIORITY_LABELS,
    RFI_PRIORITY_CRITICAL, RFI_PRIORITY_HIGH,
    RFI_PRIORITY_NORMAL, RFI_PRIORITY_LOW,
)

test("5 RFI statuses", len(RFI_STATUSES) == 5)
test("Open status", RFI_STATUS_OPEN == "open")
test("Pending status", RFI_STATUS_PENDING == "pending")
test("Answered status", RFI_STATUS_ANSWERED == "answered")
test("Closed status", RFI_STATUS_CLOSED == "closed")
test("Void status", RFI_STATUS_VOID == "void")
test("All RFI statuses have labels", all(s in RFI_STATUS_LABELS for s in RFI_STATUSES))
test("4 RFI priorities", len(RFI_PRIORITIES) == 4)
test("Critical priority", RFI_PRIORITY_CRITICAL == "critical")
test("All priorities have labels", all(p in RFI_PRIORITY_LABELS for p in RFI_PRIORITIES))

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 4: Transmittal & BOM Change Constants ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.documents import (
    XMIT_STATUSES, XMIT_STATUS_LABELS, XMIT_PURPOSES, XMIT_PURPOSE_LABELS,
    XMIT_STATUS_DRAFT, XMIT_STATUS_SENT, XMIT_STATUS_ACKNOWLEDGED,
    BOM_CHANGE_TYPES, BOM_CHANGE_TYPE_LABELS,
    BOM_CHANGE_ADDED, BOM_CHANGE_REMOVED, BOM_CHANGE_MODIFIED, BOM_CHANGE_QUANTITY,
)

test("3 transmittal statuses", len(XMIT_STATUSES) == 3)
test("Draft transmittal", XMIT_STATUS_DRAFT == "draft")
test("Sent transmittal", XMIT_STATUS_SENT == "sent")
test("Acknowledged transmittal", XMIT_STATUS_ACKNOWLEDGED == "acknowledged")
test("All xmit statuses have labels", all(s in XMIT_STATUS_LABELS for s in XMIT_STATUSES))
test("4 transmittal purposes", len(XMIT_PURPOSES) == 4)
test("All purposes have labels", all(p in XMIT_PURPOSE_LABELS for p in XMIT_PURPOSES))
test("4 BOM change types", len(BOM_CHANGE_TYPES) == 4)
test("Added change type", BOM_CHANGE_ADDED == "added")
test("Removed change type", BOM_CHANGE_REMOVED == "removed")
test("Modified change type", BOM_CHANGE_MODIFIED == "modified")
test("Quantity change type", BOM_CHANGE_QUANTITY == "quantity_change")
test("All change types have labels", all(t in BOM_CHANGE_TYPE_LABELS for t in BOM_CHANGE_TYPES))

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 5: DrawingRevision Data Model ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.documents import DrawingRevision

rev = DrawingRevision(
    job_code="JOB-100", drawing_number="SD-001", title="Floor Plan",
    category="shop_drawings", revision="A", created_by="engineer1",
)

test("Revision ID auto-generated", rev.revision_id.startswith("REV-"))
test("Created_at auto-set", len(rev.created_at) > 0)
test("Job code stored", rev.job_code == "JOB-100")
test("Drawing number stored", rev.drawing_number == "SD-001")
test("Title stored", rev.title == "Floor Plan")
test("Category stored", rev.category == "shop_drawings")
test("Default status is draft", rev.status == REV_STATUS_DRAFT)
test("status_label property", rev.status_label == "Draft")
test("status_color property", len(rev.status_color) > 0)
test("category_label property", rev.category_label == "Shop Drawings")
test("can_transition_to submitted", rev.can_transition_to(REV_STATUS_SUBMITTED))
test("cannot transition to approved directly", not rev.can_transition_to(REV_STATUS_APPROVED))

# to_dict / from_dict
d = rev.to_dict()
test("to_dict returns dict", isinstance(d, dict))
test("to_dict has revision_id", "revision_id" in d)
rev2 = DrawingRevision.from_dict(d)
test("from_dict preserves revision_id", rev2.revision_id == rev.revision_id)
test("from_dict preserves job_code", rev2.job_code == "JOB-100")
test("from_dict preserves title", rev2.title == "Floor Plan")

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 6: RFI Data Model ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.documents import RFI

rfi = RFI(
    rfi_number=1, job_code="JOB-100", subject="Column size",
    question="What is the column size for grid A1?",
    priority="high", created_by="pm1",
)

test("RFI ID auto-generated", rfi.rfi_id.startswith("RFI-"))
test("Created_at auto-set", len(rfi.created_at) > 0)
test("RFI number stored", rfi.rfi_number == 1)
test("Subject stored", rfi.subject == "Column size")
test("Default status is open", rfi.status == RFI_STATUS_OPEN)
test("status_label property", rfi.status_label == "Open")
test("priority_label property", rfi.priority_label == "High")
test("is_overdue false (no due date)", not rfi.is_overdue)

# Overdue check
rfi_overdue = RFI(due_date="2020-01-01", status=RFI_STATUS_OPEN)
test("is_overdue true for past date", rfi_overdue.is_overdue)

rfi_closed = RFI(due_date="2020-01-01", status=RFI_STATUS_CLOSED)
test("is_overdue false when closed", not rfi_closed.is_overdue)

# to_dict / from_dict
d = rfi.to_dict()
test("RFI to_dict returns dict", isinstance(d, dict))
rfi2 = RFI.from_dict(d)
test("RFI from_dict preserves id", rfi2.rfi_id == rfi.rfi_id)
test("RFI from_dict preserves subject", rfi2.subject == "Column size")

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 7: Transmittal Data Model ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.documents import Transmittal

xmit = Transmittal(
    transmittal_number=1, job_code="JOB-100", recipient="Acme Corp",
    recipient_email="acme@example.com", purpose="for_approval",
    subject="Shop drawings for review", created_by="pm1",
    documents=[{"drawing_number": "SD-001", "revision": "A"}],
)

test("Transmittal ID auto-generated", xmit.transmittal_id.startswith("XMIT-"))
test("Created_at auto-set", len(xmit.created_at) > 0)
test("Transmittal number stored", xmit.transmittal_number == 1)
test("Recipient stored", xmit.recipient == "Acme Corp")
test("Default status is draft", xmit.status == XMIT_STATUS_DRAFT)
test("status_label property", xmit.status_label == "Draft")
test("purpose_label property", xmit.purpose_label == "For Approval")
test("Documents list stored", len(xmit.documents) == 1)

d = xmit.to_dict()
test("Transmittal to_dict", isinstance(d, dict))
xmit2 = Transmittal.from_dict(d)
test("Transmittal from_dict preserves id", xmit2.transmittal_id == xmit.transmittal_id)
test("Transmittal from_dict preserves docs", len(xmit2.documents) == 1)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 8: BOMChangeOrder Data Model ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.documents import BOMChangeOrder

bco = BOMChangeOrder(
    job_code="JOB-100", from_revision="A", to_revision="B",
    change_type="modified", component="Rafter R1",
    field_changed="length", old_value="30ft", new_value="32ft",
    reason="Design change", created_by="engineer1",
)

test("BCO ID auto-generated", bco.change_id.startswith("BCO-"))
test("Created_at auto-set", len(bco.created_at) > 0)
test("Job code stored", bco.job_code == "JOB-100")
test("Change type stored", bco.change_type == "modified")
test("Component stored", bco.component == "Rafter R1")
test("Old value stored", bco.old_value == "30ft")
test("New value stored", bco.new_value == "32ft")

d = bco.to_dict()
test("BCO to_dict", isinstance(d, dict))
bco2 = BOMChangeOrder.from_dict(d)
test("BCO from_dict preserves id", bco2.change_id == bco.change_id)
test("BCO from_dict preserves component", bco2.component == "Rafter R1")

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 9: Drawing Revision CRUD ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.documents import (
    create_revision, get_revision, list_revisions,
    transition_revision, get_latest_revision, get_revision_history,
)

t9 = tempfile.mkdtemp()

r1 = create_revision(t9, "JOB-A", "SD-001", "Floor Plan", "A", "eng1",
                      category="shop_drawings", filename="floor.pdf", file_size=1024)
test("Created revision", r1.revision_id.startswith("REV-"))
test("Rev status is draft", r1.status == REV_STATUS_DRAFT)
test("Rev filename", r1.filename == "floor.pdf")

# Get by ID
got = get_revision(t9, r1.revision_id)
test("Get revision by ID", got is not None)
test("Get revision matches", got.title == "Floor Plan")

# Get non-existent
test("Get missing revision returns None", get_revision(t9, "REV-FAKE") is None)

# List revisions
r2 = create_revision(t9, "JOB-A", "SD-002", "Rafter Detail", "A", "eng1",
                      category="engineering")
r3 = create_revision(t9, "JOB-B", "SD-001", "Column Detail", "A", "eng2",
                      category="shop_drawings")

all_revs = list_revisions(t9)
test("List all revisions returns 3", len(all_revs) == 3)

job_a_revs = list_revisions(t9, job_code="JOB-A")
test("Filter by job_code", len(job_a_revs) == 2)

eng_revs = list_revisions(t9, category="engineering")
test("Filter by category", len(eng_revs) == 1)

# Latest revision
latest = get_latest_revision(t9, "JOB-A", "SD-001")
test("Latest revision found", latest is not None)
test("Latest revision matches", latest.revision_id == r1.revision_id)

# Revision history
history = get_revision_history(t9, "JOB-A", "SD-001")
test("History returns 1", len(history) == 1)

shutil.rmtree(t9)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 10: Revision Status Transitions ══")
# ═══════════════════════════════════════════════════════════════════

t10 = tempfile.mkdtemp()

r = create_revision(t10, "JOB-X", "SD-100", "Test Drawing", "A", "eng1")

# Draft → Submitted
r = transition_revision(t10, r.revision_id, REV_STATUS_SUBMITTED, actor="eng1")
test("Transition to submitted", r is not None)
test("Status is submitted", r.status == REV_STATUS_SUBMITTED)
test("Submitted by recorded", r.submitted_by == "eng1")

# Submitted → In Review
r = transition_revision(t10, r.revision_id, REV_STATUS_IN_REVIEW, actor="reviewer1")
test("Transition to in_review", r is not None)
test("Status is in_review", r.status == REV_STATUS_IN_REVIEW)

# In Review → Approved
r = transition_revision(t10, r.revision_id, REV_STATUS_APPROVED, actor="pm1")
test("Transition to approved", r is not None)
test("Status is approved", r.status == REV_STATUS_APPROVED)
test("Approved by recorded", r.approved_by == "pm1")

# Invalid transition: approved → submitted
bad = transition_revision(t10, r.revision_id, REV_STATUS_SUBMITTED, actor="pm1")
test("Invalid transition returns None", bad is None)

# Create Rev B and approve — auto-supersedes Rev A
r_b = create_revision(t10, "JOB-X", "SD-100", "Test Drawing", "B", "eng1")
transition_revision(t10, r_b.revision_id, REV_STATUS_SUBMITTED, actor="eng1")
transition_revision(t10, r_b.revision_id, REV_STATUS_IN_REVIEW, actor="reviewer1")
r_b = transition_revision(t10, r_b.revision_id, REV_STATUS_APPROVED, actor="pm1")
test("Rev B approved", r_b.status == REV_STATUS_APPROVED)

# Check Rev A is now superseded
r_a_check = get_revision(t10, r.revision_id)
test("Rev A auto-superseded", r_a_check.status == REV_STATUS_SUPERSEDED)
test("Rev A superseded_by set", r_a_check.superseded_by == r_b.revision_id)

# Rejection flow
r_c = create_revision(t10, "JOB-X", "SD-200", "Another Drawing", "A", "eng1")
transition_revision(t10, r_c.revision_id, REV_STATUS_SUBMITTED, actor="eng1")
transition_revision(t10, r_c.revision_id, REV_STATUS_IN_REVIEW, actor="rev1")
r_c = transition_revision(t10, r_c.revision_id, REV_STATUS_REJECTED, actor="pm1",
                           reason="Missing dimensions")
test("Rejection recorded", r_c.status == REV_STATUS_REJECTED)
test("Rejection reason stored", r_c.rejection_reason == "Missing dimensions")

# Rejected → Draft (rework)
r_c = transition_revision(t10, r_c.revision_id, REV_STATUS_DRAFT, actor="eng1")
test("Rejected back to draft", r_c.status == REV_STATUS_DRAFT)

shutil.rmtree(t10)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 11: RFI CRUD ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.documents import (
    create_rfi, get_rfi, list_rfis, respond_to_rfi, close_rfi, void_rfi,
)

t11 = tempfile.mkdtemp()

rfi1 = create_rfi(t11, "JOB-A", "Column Size", "What size column for A1?",
                  "pm1", priority="high", drawing_ref="SD-001", due_date="2099-12-31")
test("RFI created", rfi1.rfi_id.startswith("RFI-"))
test("RFI number is 1", rfi1.rfi_number == 1)
test("RFI status is open", rfi1.status == RFI_STATUS_OPEN)

rfi2 = create_rfi(t11, "JOB-A", "Beam Connection", "Detail for beam B2?", "pm1")
test("Second RFI number is 2", rfi2.rfi_number == 2)

rfi3 = create_rfi(t11, "JOB-B", "Footing Depth", "What depth for footing F1?", "pm2")
test("Different job RFI number is 1", rfi3.rfi_number == 1)

# Get by ID
got = get_rfi(t11, rfi1.rfi_id)
test("Get RFI by ID", got is not None)
test("Get RFI matches subject", got.subject == "Column Size")

test("Get missing RFI returns None", get_rfi(t11, "RFI-FAKE") is None)

# List RFIs
all_rfis = list_rfis(t11)
test("List all RFIs returns 3", len(all_rfis) == 3)

job_a_rfis = list_rfis(t11, job_code="JOB-A")
test("Filter by job_code", len(job_a_rfis) == 2)

# Respond
responded = respond_to_rfi(t11, rfi1.rfi_id, "Use W14x90", "engineer1")
test("Respond to RFI", responded is not None)
test("RFI status is answered", responded.status == RFI_STATUS_ANSWERED)
test("Response text stored", responded.response == "Use W14x90")
test("Responded by recorded", responded.responded_by == "engineer1")

# Close
closed = close_rfi(t11, rfi1.rfi_id, "pm1")
test("Close RFI", closed is not None)
test("RFI status is closed", closed.status == RFI_STATUS_CLOSED)
test("Closed by recorded", closed.closed_by == "pm1")

# Void
voided = void_rfi(t11, rfi2.rfi_id)
test("Void RFI", voided is not None)
test("RFI status is void", voided.status == RFI_STATUS_VOID)

# Filter by status
open_rfis = list_rfis(t11, status="open")
test("Filter by open status", len(open_rfis) == 1)  # only rfi3

shutil.rmtree(t11)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 12: Transmittal CRUD ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.documents import (
    create_transmittal, get_transmittal, list_transmittals,
    send_transmittal, acknowledge_transmittal,
)

t12 = tempfile.mkdtemp()

x1 = create_transmittal(t12, "JOB-A", "Acme Corp", "for_approval", "pm1",
                         subject="Shop drawings batch 1",
                         recipient_email="acme@example.com",
                         documents=[{"drawing_number": "SD-001", "revision": "A"}])
test("Transmittal created", x1.transmittal_id.startswith("XMIT-"))
test("Transmittal number is 1", x1.transmittal_number == 1)
test("Status is draft", x1.status == XMIT_STATUS_DRAFT)
test("Docs attached", len(x1.documents) == 1)

x2 = create_transmittal(t12, "JOB-A", "Builder Inc", "for_construction", "pm1")
test("Second transmittal number is 2", x2.transmittal_number == 2)

# Get by ID
got = get_transmittal(t12, x1.transmittal_id)
test("Get transmittal by ID", got is not None)
test("Get transmittal matches", got.recipient == "Acme Corp")

test("Get missing transmittal returns None", get_transmittal(t12, "XMIT-FAKE") is None)

# List
all_xmits = list_transmittals(t12)
test("List all transmittals returns 2", len(all_xmits) == 2)

# Send
sent = send_transmittal(t12, x1.transmittal_id)
test("Send transmittal", sent is not None)
test("Status is sent", sent.status == XMIT_STATUS_SENT)
test("Sent_at set", len(sent.sent_at) > 0)

# Acknowledge
acked = acknowledge_transmittal(t12, x1.transmittal_id, "field_rep1")
test("Acknowledge transmittal", acked is not None)
test("Status is acknowledged", acked.status == XMIT_STATUS_ACKNOWLEDGED)
test("Acknowledged by recorded", acked.acknowledged_by == "field_rep1")

# Filter by status
drafts = list_transmittals(t12, status="draft")
test("Filter by draft status", len(drafts) == 1)

shutil.rmtree(t12)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 13: BOM Change Orders ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.documents import (
    log_bom_change, list_bom_changes, get_bom_change_summary,
)

t13 = tempfile.mkdtemp()

bc1 = log_bom_change(t13, "JOB-A", "A", "B", "modified", "Rafter R1", "eng1",
                      field_changed="length", old_value="30ft", new_value="32ft",
                      reason="Design revision")
test("BOM change created", bc1.change_id.startswith("BCO-"))
test("Change type stored", bc1.change_type == "modified")

bc2 = log_bom_change(t13, "JOB-A", "A", "B", "added", "Gusset G5", "eng1",
                      reason="Added stiffener")
bc3 = log_bom_change(t13, "JOB-A", "B", "C", "removed", "Brace B3", "eng1")
bc4 = log_bom_change(t13, "JOB-B", "A", "B", "quantity_change", "Bolt Pack", "eng2",
                      field_changed="quantity", old_value="100", new_value="120")

# List
all_changes = list_bom_changes(t13)
test("List all BOM changes returns 4", len(all_changes) == 4)

job_a_changes = list_bom_changes(t13, job_code="JOB-A")
test("Filter by job_code", len(job_a_changes) == 3)

rev_ab_changes = list_bom_changes(t13, from_revision="A", to_revision="B")
test("Filter by revision pair", len(rev_ab_changes) == 3)  # bc1, bc2, bc4

# Summary
summary = get_bom_change_summary(t13, "JOB-A")
test("Summary total", summary["total_changes"] == 3)
test("Summary by_type has modified", summary["by_type"].get("modified") == 1)
test("Summary by_type has added", summary["by_type"].get("added") == 1)
test("Summary has by_revision_pair", len(summary["by_revision_pair"]) > 0)

shutil.rmtree(t13)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 14: Document Summary / Analytics ══")
# ═══════════════════════════════════════════════════════════════════

from shop_drawings.documents import get_document_summary

t14 = tempfile.mkdtemp()

# Create some test data
create_revision(t14, "JOB-A", "SD-001", "Floor Plan", "A", "eng1", category="shop_drawings")
create_revision(t14, "JOB-A", "SD-002", "Rafter Detail", "A", "eng1", category="engineering")
r_for_approve = create_revision(t14, "JOB-A", "SD-003", "Column Detail", "A", "eng1")
transition_revision(t14, r_for_approve.revision_id, REV_STATUS_SUBMITTED, actor="eng1")
transition_revision(t14, r_for_approve.revision_id, REV_STATUS_IN_REVIEW, actor="rev1")
transition_revision(t14, r_for_approve.revision_id, REV_STATUS_APPROVED, actor="pm1")

create_rfi(t14, "JOB-A", "Test RFI", "Question?", "pm1", due_date="2020-01-01")  # overdue
create_rfi(t14, "JOB-A", "Test RFI 2", "Question 2?", "pm1")

create_transmittal(t14, "JOB-A", "Acme", "for_review", "pm1")

summary = get_document_summary(t14)
test("Summary has total_revisions", summary["total_revisions"] == 3)
test("Summary revisions_by_status has draft", summary["revisions_by_status"].get("draft", 0) == 2)
test("Summary revisions_by_status has approved", summary["revisions_by_status"].get("approved", 0) == 1)
test("Summary revisions_by_category", len(summary["revisions_by_category"]) == 2)
test("Summary unique_drawings", summary["unique_drawings"] == 3)
test("Summary total_rfis", summary["total_rfis"] == 2)
test("Summary overdue_rfis", summary["overdue_rfis"] == 1)
test("Summary open_rfis", summary["open_rfis"] == 2)
test("Summary total_transmittals", summary["total_transmittals"] == 1)

# Filter by job
summary_b = get_document_summary(t14, job_code="JOB-B")
test("Summary for non-existent job is empty", summary_b["total_revisions"] == 0)

shutil.rmtree(t14)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 15: RBAC Permissions for Documents ══")
# ═══════════════════════════════════════════════════════════════════

from auth.roles import P, ROLES, get_role

test("VIEW_SHOP_DRAWINGS permission exists", hasattr(P, "VIEW_SHOP_DRAWINGS"))
test("EDIT_SHOP_DRAWINGS permission exists", hasattr(P, "EDIT_SHOP_DRAWINGS"))
test("APPROVE_DRAWINGS permission exists", hasattr(P, "APPROVE_DRAWINGS"))

# Check that key roles have the permissions
god = get_role("god_mode")
test("god_mode has VIEW_SHOP_DRAWINGS", P.VIEW_SHOP_DRAWINGS in god.permissions)
test("god_mode has EDIT_SHOP_DRAWINGS", P.EDIT_SHOP_DRAWINGS in god.permissions)
test("god_mode has APPROVE_DRAWINGS", P.APPROVE_DRAWINGS in god.permissions)

admin = get_role("admin")
test("admin has VIEW_SHOP_DRAWINGS", P.VIEW_SHOP_DRAWINGS in admin.permissions)

pm = get_role("project_manager")
test("project_manager has VIEW_SHOP_DRAWINGS", P.VIEW_SHOP_DRAWINGS in pm.permissions)

engineer = get_role("engineer")
test("engineer has VIEW_SHOP_DRAWINGS", P.VIEW_SHOP_DRAWINGS in engineer.permissions)
test("engineer has EDIT_SHOP_DRAWINGS", P.EDIT_SHOP_DRAWINGS in engineer.permissions)

# Shop floor ops should have view access
foreman = get_role("shop_foreman")
test("shop_foreman has VIEW_SHOP_DRAWINGS", P.VIEW_SHOP_DRAWINGS in foreman.permissions)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 16: Handler Classes Exist ══")
# ═══════════════════════════════════════════════════════════════════

import tf_handlers as tfh

handler_names = [
    "DocumentManagementPageHandler",
    "RevisionListAPIHandler",
    "RevisionDetailAPIHandler",
    "RevisionCreateHandler",
    "RevisionTransitionHandler",
    "RevisionHistoryAPIHandler",
    "RevisionLatestAPIHandler",
    "RFIListAPIHandler",
    "RFIDetailAPIHandler",
    "RFICreateHandler",
    "RFIRespondHandler",
    "RFICloseHandler",
    "RFIVoidHandler",
    "TransmittalListAPIHandler",
    "TransmittalDetailAPIHandler",
    "TransmittalCreateHandler",
    "TransmittalSendHandler",
    "TransmittalAckHandler",
    "BOMChangeLogHandler",
    "BOMChangeListAPIHandler",
    "BOMChangeSummaryAPIHandler",
    "DocumentSummaryAPIHandler",
    "DocumentConfigHandler",
]

for name in handler_names:
    test(f"Handler {name} exists", hasattr(tfh, name))

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 17: Handler RBAC Permissions ══")
# ═══════════════════════════════════════════════════════════════════

# View handlers (view_shop_drawings)
view_handlers = [
    "DocumentManagementPageHandler",
    "RevisionListAPIHandler", "RevisionDetailAPIHandler",
    "RevisionHistoryAPIHandler", "RevisionLatestAPIHandler",
    "RFIListAPIHandler", "RFIDetailAPIHandler",
    "TransmittalListAPIHandler", "TransmittalDetailAPIHandler",
    "BOMChangeListAPIHandler", "BOMChangeSummaryAPIHandler",
    "DocumentSummaryAPIHandler", "DocumentConfigHandler",
    "TransmittalAckHandler",
]
for name in view_handlers:
    cls = getattr(tfh, name)
    test(f"{name} requires view_shop_drawings",
         getattr(cls, "required_permission", "") == "view_shop_drawings")

# Edit handlers (edit_shop_drawings)
edit_handlers = [
    "RevisionCreateHandler",
    "RFICreateHandler",
    "TransmittalCreateHandler", "TransmittalSendHandler",
    "BOMChangeLogHandler",
]
for name in edit_handlers:
    cls = getattr(tfh, name)
    test(f"{name} requires edit_shop_drawings",
         getattr(cls, "required_permission", "") == "edit_shop_drawings")

# Approve handlers (approve_drawings)
approve_handlers = [
    "RevisionTransitionHandler",
    "RFIRespondHandler", "RFICloseHandler", "RFIVoidHandler",
]
for name in approve_handlers:
    cls = getattr(tfh, name)
    test(f"{name} requires approve_drawings",
         getattr(cls, "required_permission", "") == "approve_drawings")

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 18: Route Table ══")
# ═══════════════════════════════════════════════════════════════════

routes = tfh.get_routes()
route_map = {}
for r in routes:
    pattern = r[0]
    handler = r[1] if len(r) >= 2 else None
    route_map[pattern] = handler

expected_routes = {
    r"/documents": "DocumentManagementPageHandler",
    r"/api/documents/revisions": "RevisionListAPIHandler",
    r"/api/documents/revision": "RevisionDetailAPIHandler",
    r"/api/documents/revision/create": "RevisionCreateHandler",
    r"/api/documents/revision/transition": "RevisionTransitionHandler",
    r"/api/documents/revision/history": "RevisionHistoryAPIHandler",
    r"/api/documents/revision/latest": "RevisionLatestAPIHandler",
    r"/api/documents/rfis": "RFIListAPIHandler",
    r"/api/documents/rfi": "RFIDetailAPIHandler",
    r"/api/documents/rfi/create": "RFICreateHandler",
    r"/api/documents/rfi/respond": "RFIRespondHandler",
    r"/api/documents/rfi/close": "RFICloseHandler",
    r"/api/documents/rfi/void": "RFIVoidHandler",
    r"/api/documents/transmittals": "TransmittalListAPIHandler",
    r"/api/documents/transmittal": "TransmittalDetailAPIHandler",
    r"/api/documents/transmittal/create": "TransmittalCreateHandler",
    r"/api/documents/transmittal/send": "TransmittalSendHandler",
    r"/api/documents/transmittal/acknowledge": "TransmittalAckHandler",
    r"/api/documents/bom-change/log": "BOMChangeLogHandler",
    r"/api/documents/bom-changes": "BOMChangeListAPIHandler",
    r"/api/documents/bom-changes/summary": "BOMChangeSummaryAPIHandler",
    r"/api/documents/summary": "DocumentSummaryAPIHandler",
    r"/api/documents/config": "DocumentConfigHandler",
}

for pattern, handler_name in expected_routes.items():
    handler = route_map.get(pattern)
    test(f"Route {pattern} → {handler_name}",
         handler is not None and handler.__name__ == handler_name)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 19: Template File ══")
# ═══════════════════════════════════════════════════════════════════

from templates.document_management_page import DOCUMENT_MANAGEMENT_PAGE_HTML

test("Template var exists", DOCUMENT_MANAGEMENT_PAGE_HTML is not None)
test("Template is HTML", "<!DOCTYPE html>" in DOCUMENT_MANAGEMENT_PAGE_HTML)
test("Template has title", "Document Management" in DOCUMENT_MANAGEMENT_PAGE_HTML)
test("Template has revisions tab", "Drawing Revisions" in DOCUMENT_MANAGEMENT_PAGE_HTML)
test("Template has RFIs tab", "RFIs" in DOCUMENT_MANAGEMENT_PAGE_HTML)
test("Template has transmittals tab", "Transmittals" in DOCUMENT_MANAGEMENT_PAGE_HTML)
test("Template has BOM tab", "BOM Changes" in DOCUMENT_MANAGEMENT_PAGE_HTML)
test("Template has revisions API call", "/api/documents/revisions" in DOCUMENT_MANAGEMENT_PAGE_HTML)
test("Template has config API call", "/api/documents/config" in DOCUMENT_MANAGEMENT_PAGE_HTML)
test("Template has summary API call", "/api/documents/summary" in DOCUMENT_MANAGEMENT_PAGE_HTML)
test("Template has new revision form", "revisionModal" in DOCUMENT_MANAGEMENT_PAGE_HTML)
test("Template has new RFI form", "rfiModal" in DOCUMENT_MANAGEMENT_PAGE_HTML)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 20: Full E2E — Drawing Revision Lifecycle ══")
# ═══════════════════════════════════════════════════════════════════

t20 = tempfile.mkdtemp()

# Engineer creates drawing revision
rev_a = create_revision(t20, "JOB-E2E", "SD-E2E-001", "Truss Layout", "A", "engineer1",
                         category="shop_drawings", filename="truss_layout_A.pdf", file_size=2048)
test("E2E: Rev A created", rev_a.status == REV_STATUS_DRAFT)

# Engineer submits for review
rev_a = transition_revision(t20, rev_a.revision_id, REV_STATUS_SUBMITTED, actor="engineer1")
test("E2E: Rev A submitted", rev_a.status == REV_STATUS_SUBMITTED)

# Reviewer marks in review
rev_a = transition_revision(t20, rev_a.revision_id, REV_STATUS_IN_REVIEW, actor="reviewer1")
test("E2E: Rev A in review", rev_a.status == REV_STATUS_IN_REVIEW)

# Reviewer rejects
rev_a = transition_revision(t20, rev_a.revision_id, REV_STATUS_REJECTED, actor="reviewer1",
                             reason="Missing connection details")
test("E2E: Rev A rejected", rev_a.status == REV_STATUS_REJECTED)

# Engineer reworks, creates Rev B
rev_a = transition_revision(t20, rev_a.revision_id, REV_STATUS_DRAFT, actor="engineer1")
rev_b = create_revision(t20, "JOB-E2E", "SD-E2E-001", "Truss Layout", "B", "engineer1",
                         category="shop_drawings", filename="truss_layout_B.pdf", file_size=2560)

# Rev B goes through approval
transition_revision(t20, rev_b.revision_id, REV_STATUS_SUBMITTED, actor="engineer1")
transition_revision(t20, rev_b.revision_id, REV_STATUS_IN_REVIEW, actor="reviewer1")
rev_b = transition_revision(t20, rev_b.revision_id, REV_STATUS_APPROVED, actor="pm1")
test("E2E: Rev B approved", rev_b.status == REV_STATUS_APPROVED)

# Check latest
latest = get_latest_revision(t20, "JOB-E2E", "SD-E2E-001")
test("E2E: Latest is Rev B", latest.revision == "B")

# Check history shows both
history = get_revision_history(t20, "JOB-E2E", "SD-E2E-001")
test("E2E: History shows 2 revisions", len(history) == 2)

shutil.rmtree(t20)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 21: Full E2E — RFI Lifecycle ══")
# ═══════════════════════════════════════════════════════════════════

t21 = tempfile.mkdtemp()

# PM creates RFI
rfi = create_rfi(t21, "JOB-E2E", "Anchor Bolt Embedment",
                 "What is the required embedment depth for anchor bolts at grid C3?",
                 "pm1", priority="critical", drawing_ref="SD-E2E-001",
                 due_date="2099-12-31")
test("E2E RFI: Created", rfi.status == RFI_STATUS_OPEN)
test("E2E RFI: Critical priority", rfi.priority == RFI_PRIORITY_CRITICAL)

# Engineer responds
rfi = respond_to_rfi(t21, rfi.rfi_id, "12 inches minimum per spec IBC 2018", "engineer1")
test("E2E RFI: Responded", rfi.status == RFI_STATUS_ANSWERED)

# PM closes
rfi = close_rfi(t21, rfi.rfi_id, "pm1")
test("E2E RFI: Closed", rfi.status == RFI_STATUS_CLOSED)
test("E2E RFI: Not overdue when closed", not rfi.is_overdue)

# Create and void another RFI
rfi2 = create_rfi(t21, "JOB-E2E", "Void Test", "Will be cancelled", "pm1")
rfi2 = void_rfi(t21, rfi2.rfi_id)
test("E2E RFI: Voided", rfi2.status == RFI_STATUS_VOID)

shutil.rmtree(t21)

# ═══════════════════════════════════════════════════════════════════
print("\n══ TEST 22: Full E2E — Transmittal + BOM Change ══")
# ═══════════════════════════════════════════════════════════════════

t22 = tempfile.mkdtemp()

# Create transmittal with documents
xmit = create_transmittal(t22, "JOB-E2E", "GC Construction LLC", "for_approval", "pm1",
                           subject="Shop Drawing Package - Phase 1",
                           recipient_email="gc@construction.com",
                           documents=[
                               {"drawing_number": "SD-001", "revision": "B", "title": "Floor Plan"},
                               {"drawing_number": "SD-002", "revision": "A", "title": "Rafter Detail"},
                           ])
test("E2E XMIT: Created with 2 docs", len(xmit.documents) == 2)
test("E2E XMIT: Draft status", xmit.status == XMIT_STATUS_DRAFT)

# Send
xmit = send_transmittal(t22, xmit.transmittal_id)
test("E2E XMIT: Sent", xmit.status == XMIT_STATUS_SENT)

# Acknowledge
xmit = acknowledge_transmittal(t22, xmit.transmittal_id, "gc_rep")
test("E2E XMIT: Acknowledged", xmit.status == XMIT_STATUS_ACKNOWLEDGED)

# Log BOM changes between revisions
log_bom_change(t22, "JOB-E2E", "A", "B", "modified", "Rafter R1", "eng1",
               field_changed="length", old_value="24ft", new_value="26ft",
               reason="Span increase")
log_bom_change(t22, "JOB-E2E", "A", "B", "added", "Gusset G3", "eng1",
               reason="Added for wind load")
log_bom_change(t22, "JOB-E2E", "A", "B", "quantity_change", "Purlins", "eng1",
               field_changed="count", old_value="12", new_value="14",
               reason="Reduced spacing")

summary = get_bom_change_summary(t22, "JOB-E2E")
test("E2E BOM: 3 changes logged", summary["total_changes"] == 3)
test("E2E BOM: by_type correct", len(summary["by_type"]) == 3)

# Overall document summary
doc_summary = get_document_summary(t22)
test("E2E Summary: transmittals counted", doc_summary["total_transmittals"] == 1)

shutil.rmtree(t22)

# ═══════════════════════════════════════════════════════════════════
# CLEANUP & FINAL REPORT
# ═══════════════════════════════════════════════════════════════════

shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{'='*60}")
print(f"Phase 9 Results: {passed} passed, {failed} failed, {passed+failed} total")
print(f"{'='*60}")
if failed:
    sys.exit(1)
