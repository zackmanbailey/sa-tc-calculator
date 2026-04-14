#!/usr/bin/env python3
"""
TitanForge RBAC Verification Tests
Tests the role definitions, permission merging, financial isolation,
multi-role behavior, and user management.
"""

import sys, os, json, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auth.users

passed = 0
failed = 0

def test(name, condition):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}")
        failed += 1


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 1: Role Definitions ══")
# ─────────────────────────────────────────────────────────────────────────────
from auth.roles import ROLES, ROLE_IDS, P, get_role, get_role_permissions, get_role_cards, get_role_sidebar, list_all_roles

test("18 roles defined", len(ROLES) == 18)
test("God Mode is rank 0", ROLES["god_mode"].rank == 0)
test("Customer is rank 17", ROLES["customer"].rank == 17)
test("God Mode can delete", ROLES["god_mode"].can_delete is True)
test("Admin cannot delete", ROLES["admin"].can_delete is False)
test("God Mode can manage users", ROLES["god_mode"].can_manage_users is True)
test("Shop Foreman cannot manage users", ROLES["shop_foreman"].can_manage_users is False)
test("Laborer is mobile-first", ROLES["laborer"].mobile_first is True)
test("Admin is NOT mobile-first", ROLES["admin"].mobile_first is False)

# Check all expected role IDs exist
expected_ids = [
    "god_mode", "admin", "project_manager", "estimator", "sales",
    "purchasing", "inventory_manager", "accounting", "shop_foreman",
    "qc_inspector", "engineer", "roll_forming_operator", "welder",
    "shipping_coordinator", "laborer", "field_crew", "safety_officer", "customer"
]
test("All 18 role IDs present", all(rid in ROLES for rid in expected_ids))

# God Mode has every permission
god_perms = get_role_permissions("god_mode")
test("God Mode has manage_users", P.MANAGE_USERS in god_perms)
test("God Mode has delete_anything", P.DELETE_ANYTHING in god_perms)
test("God Mode has run_calculator", P.RUN_CALCULATOR in god_perms)
test("God Mode has sign_off_qc", P.SIGN_OFF_QC in god_perms)

# Shop Foreman specifics
foreman_perms = get_role_permissions("shop_foreman")
test("Foreman can submit receipts", P.SUBMIT_RECEIPTS in foreman_perms)
test("Foreman can view own receipts", P.VIEW_OWN_RECEIPTS in foreman_perms)
test("Foreman CANNOT view financials", P.VIEW_FINANCIALS not in foreman_perms)
test("Foreman CANNOT view BOM pricing", P.VIEW_BOM_PRICING not in foreman_perms)
test("Foreman CANNOT sign off QC", P.SIGN_OFF_QC not in foreman_perms)

# Estimator specifics
est_perms = get_role_permissions("estimator")
test("Estimator can run calculator", P.RUN_CALCULATOR in est_perms)
test("Estimator can view BOM pricing", P.VIEW_BOM_PRICING in est_perms)
test("Estimator CANNOT view work orders", P.VIEW_WORK_ORDERS not in est_perms)
test("Estimator CANNOT view shop drawings", P.VIEW_SHOP_DRAWINGS not in est_perms)

# list_all_roles helper
all_roles = list_all_roles()
test("list_all_roles returns 18", len(all_roles) == 18)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 2: Permission Merging (Multi-Role) ══")
# ─────────────────────────────────────────────────────────────────────────────
from auth.permissions import merge_permissions, PermissionSet, FINANCIAL_LEVELS

# Single role
ps_single = merge_permissions(["estimator"])
test("Single role: estimator has run_calculator", ps_single.can(P.RUN_CALCULATOR))
test("Single role: estimator cannot delete", ps_single.can_delete is False)
test("Single role: financial = quoting", ps_single.financial_level == "quoting")

# Multi-role: shop_foreman + qc_inspector (like Brad example in RULES.md)
ps_multi = merge_permissions(["shop_foreman", "qc_inspector"])
test("Multi: has create_work_orders (from foreman)", ps_multi.can(P.CREATE_WORK_ORDERS))
test("Multi: has sign_off_qc (from QC)", ps_multi.can(P.SIGN_OFF_QC))
test("Multi: has submit_receipts (from foreman)", ps_multi.can(P.SUBMIT_RECEIPTS))
test("Multi: has perform_inspections (from QC)", ps_multi.can(P.PERFORM_INSPECTIONS))
test("Multi: CANNOT view financials", ps_multi.can(P.VIEW_FINANCIALS) is False)
test("Multi: CANNOT delete", ps_multi.can_delete is False)

# Financial escalation: estimator + accounting = full
ps_fin = merge_permissions(["estimator", "accounting"])
test("Est+Acct: financial = full (highest wins)", ps_fin.financial_level == "full")
test("Est+Acct: can see BOM pricing", ps_fin.can_see_bom_pricing())
test("Est+Acct: can see margins", ps_fin.can_see_margins())
test("Est+Acct: can see vendor costs", ps_fin.can_see_vendor_costs())

# Delete only from God Mode
ps_no_del = merge_permissions(["admin", "project_manager"])
test("Admin+PM: cannot delete", ps_no_del.can_delete is False)

ps_del = merge_permissions(["god_mode"])
test("God Mode: can delete", ps_del.can_delete is True)

# Empty roles
ps_empty = merge_permissions([])
test("Empty roles: no permissions", len(ps_empty.permissions) == 0)
test("Empty roles: no financial access", ps_empty.has_financial_access() is False)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 3: Financial Data Isolation ══")
# ─────────────────────────────────────────────────────────────────────────────

# Full financial access
ps_god = merge_permissions(["god_mode"])
test("God: has_financial_access", ps_god.has_financial_access())
test("God: has_full_financial_access", ps_god.has_full_financial_access())
test("God: can_see_bom_pricing", ps_god.can_see_bom_pricing())
test("God: can_see_margins", ps_god.can_see_margins())

# No financial access
ps_laborer = merge_permissions(["laborer"])
test("Laborer: NO financial access", ps_laborer.has_financial_access() is False)
test("Laborer: NO full financial access", ps_laborer.has_full_financial_access() is False)
test("Laborer: CANNOT see BOM pricing", ps_laborer.can_see_bom_pricing() is False)

# Foreman: own_receipts only
ps_foreman = merge_permissions(["shop_foreman"])
test("Foreman: HAS financial access (receipts)", ps_foreman.has_financial_access())
test("Foreman: NOT full financial", ps_foreman.has_full_financial_access() is False)
test("Foreman: CANNOT see BOM pricing", ps_foreman.can_see_bom_pricing() is False)
test("Foreman: CANNOT see margins", ps_foreman.can_see_margins() is False)

# Sales: totals only
ps_sales = merge_permissions(["sales"])
test("Sales: can see quote totals", ps_sales.can_see_quote_totals())
test("Sales: CANNOT see BOM pricing", ps_sales.can_see_bom_pricing() is False)
test("Sales: CANNOT see margins", ps_sales.can_see_margins() is False)

# Purchasing: vendor costs
ps_purch = merge_permissions(["purchasing"])
test("Purchasing: can see vendor costs", ps_purch.can_see_vendor_costs())
test("Purchasing: CANNOT see margins", ps_purch.can_see_margins() is False)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 4: Dashboard Cards & Sidebar ══")
# ─────────────────────────────────────────────────────────────────────────────

# God Mode: gets all cards including financial ones
god_cards = ps_god.get_dashboard_cards()
god_card_ids = [c.id for c in god_cards]
test("God: has business_summary card", "business_summary" in god_card_ids)
test("God: has user_management card", "user_management" in god_card_ids)

# Laborer: minimal cards, no financial
laborer_cards = ps_laborer.get_dashboard_cards()
laborer_card_ids = [c.id for c in laborer_cards]
test("Laborer: has today_tasks card", "today_tasks" in laborer_card_ids)
test("Laborer: has quick_scan card", "quick_scan" in laborer_card_ids)
test("Laborer: NO business_summary", "business_summary" not in laborer_card_ids)

# Multi-role cards merge
ps_multi_cards = merge_permissions(["estimator", "shop_foreman"])
multi_cards = ps_multi_cards.get_dashboard_cards()
multi_card_ids = [c.id for c in multi_cards]
test("Est+Foreman: has active_quotes (from Est)", "active_quotes" in multi_card_ids)
test("Est+Foreman: has shop_overview (from Foreman)", "shop_overview" in multi_card_ids)

# Card groups
groups = ps_multi_cards.get_dashboard_card_groups()
test("Est+Foreman: has Estimating group", "Estimating" in groups)
test("Est+Foreman: has Shop Floor group", "Shop Floor" in groups)

# Sidebar
god_sidebar = ps_god.get_sidebar()
god_sb_ids = [s["id"] for s in god_sidebar]
test("God sidebar: has admin section", "admin" in god_sb_ids)
test("God sidebar: has dashboard", "dashboard" in god_sb_ids)

laborer_sb = ps_laborer.get_sidebar()
laborer_sb_ids = [s["id"] for s in laborer_sb]
test("Laborer sidebar: has my_tasks", "my_tasks" in laborer_sb_ids)
test("Laborer sidebar: NO admin", "admin" not in laborer_sb_ids)
test("Laborer sidebar: NO financial", "financial" not in laborer_sb_ids)

# Financial sidebar hidden for non-financial roles
foreman_sb = ps_foreman.get_sidebar()
foreman_sb_ids = [s["id"] for s in foreman_sb]
test("Foreman sidebar: NO financial section", "financial" not in foreman_sb_ids)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 5: User CRUD & Multi-Role Assignment ══")
# ─────────────────────────────────────────────────────────────────────────────

# Use a temp directory for test data
_orig_data_dir = auth.users.DATA_DIR
_orig_users_path = auth.users.USERS_PATH
_orig_audit_path = auth.users.AUDIT_PATH

import auth.users
_tmpdir = tempfile.mkdtemp()
auth.users.DATA_DIR = _tmpdir
auth.users.USERS_PATH = os.path.join(_tmpdir, "users.json")
auth.users.AUDIT_PATH = os.path.join(_tmpdir, "audit_log.json")

try:
    # Create user
    u = auth.users.create_user("testguy", "pass123", "Test Guy", "test@test.com",
                                roles=["welder", "laborer"])
    test("Create user: returns record", u["username"] == "testguy")
    test("Create user: multi-role", u["roles"] == ["welder", "laborer"])
    test("Create user: force password change", u["force_password_change"] is True)

    # Get user
    u2 = auth.users.get_user("testguy")
    test("Get user: found", u2 is not None)
    test("Get user: display_name", u2["display_name"] == "Test Guy")

    # get_user_roles
    roles = auth.users.get_user_roles("testguy")
    test("get_user_roles: returns list", roles == ["welder", "laborer"])

    # Assign roles
    auth.users.assign_roles("testguy", ["shop_foreman", "qc_inspector"], "admin")
    roles2 = auth.users.get_user_roles("testguy")
    test("Assign roles: updated", set(roles2) == {"shop_foreman", "qc_inspector"})

    # Remove role
    auth.users.remove_roles("testguy", ["qc_inspector"], "admin")
    roles3 = auth.users.get_user_roles("testguy")
    test("Remove role: one remaining", roles3 == ["shop_foreman"])

    # Cannot remove all roles
    try:
        auth.users.remove_roles("testguy", ["shop_foreman"], "admin")
        test("Remove all roles: should fail", False)
    except ValueError:
        test("Remove all roles: raises ValueError", True)

    # Duplicate username
    try:
        auth.users.create_user("testguy", "x", "Dup")
        test("Duplicate username: should fail", False)
    except ValueError:
        test("Duplicate username: raises ValueError", True)

    # Invalid role
    try:
        auth.users.create_user("bad", "x", "Bad", roles=["not_a_role"])
        test("Invalid role: should fail", False)
    except ValueError:
        test("Invalid role: raises ValueError", True)

    # Password verify
    test("Password verify: correct", auth.users.verify_password(u["password_hash"], "pass123"))
    test("Password verify: wrong", auth.users.verify_password(u["password_hash"], "wrong") is False)

    # Update user
    auth.users.update_user("testguy", display_name="Updated Guy", email="new@test.com")
    u3 = auth.users.get_user("testguy")
    test("Update user: display_name", u3["display_name"] == "Updated Guy")
    test("Update user: email", u3["email"] == "new@test.com")

    # Deactivate
    auth.users.deactivate_user("testguy", "admin")
    u4 = auth.users.get_user("testguy")
    test("Deactivate: active=False", u4["active"] is False)

    # List users
    auth.users.create_user("active_guy", "pass", "Active", roles=["laborer"])
    users_list = auth.users.list_users(include_inactive=False)
    usernames = [u["username"] for u in users_list]
    test("List users: excludes inactive", "testguy" not in usernames)
    test("List users: includes active", "active_guy" in usernames)

    # Login lockout
    auth.users.record_login("active_guy", False, "1.2.3.4")
    auth.users.record_login("active_guy", False, "1.2.3.4")
    auth.users.record_login("active_guy", False, "1.2.3.4")
    auth.users.record_login("active_guy", False, "1.2.3.4")
    auth.users.record_login("active_guy", False, "1.2.3.4")  # 5th = lockout
    lockout = auth.users.check_lockout("active_guy")
    test("Lockout: triggered after 5 failures", lockout is not None)

    # Successful login resets
    auth.users.record_login("active_guy", True, "1.2.3.4")
    lockout2 = auth.users.check_lockout("active_guy")
    test("Lockout: cleared after success", lockout2 is None)

    # Audit log
    audit = auth.users.get_audit_log(limit=50)
    test("Audit log: has entries", len(audit) > 0)
    test("Audit log: has action field", "action" in audit[0])

finally:
    # Restore original paths
    auth.users.DATA_DIR = _orig_data_dir
    auth.users.USERS_PATH = _orig_users_path
    auth.users.AUDIT_PATH = _orig_audit_path
    shutil.rmtree(_tmpdir)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 6: Legacy Compatibility ══")
# ─────────────────────────────────────────────────────────────────────────────

# Old ROLE_PERMISSIONS still accessible
from tf_handlers import ROLE_PERMISSIONS as OLD_PERMS
test("Legacy: admin role exists", "admin" in OLD_PERMS)
test("Legacy: god_mode mapped", "god_mode" in OLD_PERMS)
test("Legacy: shop_foreman mapped", "shop_foreman" in OLD_PERMS)
test("Legacy: estimator exists", "estimator" in OLD_PERMS)

# Old check_role function
from tf_handlers import check_role
test("Legacy check_role: admin in [admin]", check_role("admin", ["admin"]))
test("Legacy check_role: god_mode in [god_mode]", check_role("god_mode", ["god_mode"]))

# Old get_user_permissions
from tf_handlers import get_user_permissions
old_admin_perms = get_user_permissions("admin")
test("Legacy get_user_permissions: admin has quotes", "quotes" in old_admin_perms)

# PermissionSet serialization
ps = merge_permissions(["estimator", "shop_foreman"])
d = ps.to_dict()
test("Serialization: has roles", d["roles"] == ["estimator", "shop_foreman"])
test("Serialization: has permissions", len(d["permissions"]) > 0)
test("Serialization: has financial_level", "financial_level" in d)

# build_template_context
from auth.permissions import build_template_context
ctx = build_template_context(["shop_foreman"])
test("Template context: has perm", "perm" in ctx)
test("Template context: has sidebar", "sidebar" in ctx)
test("Template context: show_financial=True (receipts)", ctx["show_financial"] is True)
test("Template context: show_bom_pricing=False", ctx["show_bom_pricing"] is False)
test("Template context: can_delete=False", ctx["can_delete"] is False)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 7: Edge Cases ══")
# ─────────────────────────────────────────────────────────────────────────────

# Unknown role returns empty
ps_bad = merge_permissions(["nonexistent_role"])
test("Unknown role: no permissions", len(ps_bad.permissions) == 0)
test("Unknown role: no financial", ps_bad.has_financial_access() is False)

# Single-user multi-role — all mobile-first roles
ps_allm = merge_permissions(["laborer", "roll_forming_operator"])
test("All mobile roles: mobile_first=True", ps_allm.mobile_first is True)

# Mixed mobile + desktop
ps_mix = merge_permissions(["laborer", "admin"])
test("Mixed mobile+desktop: mobile_first=False", ps_mix.mobile_first is False)

# Permission methods
ps_pm = merge_permissions(["project_manager"])
test("PM: has_any works", ps_pm.has_any(P.VIEW_PROJECTS, P.DELETE_ANYTHING))
test("PM: has_all works (both granted)", ps_pm.has_all(P.VIEW_PROJECTS, P.VIEW_BOM))
test("PM: has_all fails (missing)", ps_pm.has_all(P.VIEW_PROJECTS, P.DELETE_ANYTHING) is False)
test("PM: has_role works", ps_pm.has_role("project_manager"))
test("PM: has_any_role works", ps_pm.has_any_role("project_manager", "admin"))
test("PM: has_any_role fails", ps_pm.has_any_role("laborer", "welder") is False)


# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{'═'*60}")
print(f"  RESULTS: {passed} passed, {failed} failed, {passed+failed} total")
print(f"{'═'*60}")
sys.exit(0 if failed == 0 else 1)
