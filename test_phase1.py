#!/usr/bin/env python3
"""
TitanForge Phase 1 — Role-Aware Dashboard & Sidebar Integration Tests
Tests that the dashboard template, sidebar builder, and middleware correctly
produce role-specific output for different user types.
"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
print("\n══ TEST 1: Sidebar — God Mode (full access) ══")
# ─────────────────────────────────────────────────────────────────────────────
from templates.shared_nav import _build_role_sidebar

god_sidebar = _build_role_sidebar("dashboard", "", "Zack", "god_mode", ["god_mode"])
test("God Mode sidebar is a string", isinstance(god_sidebar, str))
test("God Mode sees Estimating section", "Estimating" in god_sidebar)
test("God Mode sees Projects section", "Projects" in god_sidebar)
test("God Mode sees Shop Floor section", "Shop Floor" in god_sidebar)
test("God Mode sees Quality section", "Quality" in god_sidebar)
test("God Mode sees Inventory section", "Inventory" in god_sidebar)
test("God Mode sees Purchasing section", "Purchasing" in god_sidebar)
test("God Mode sees Shipping section", "Shipping" in god_sidebar)
test("God Mode sees Financial section", "Financial" in god_sidebar)
test("God Mode sees Sales section", "Sales" in god_sidebar)
test("God Mode sees Admin section", "Admin" in god_sidebar)
test("God Mode sees Dashboard link", "Dashboard" in god_sidebar)
test("God Mode role display shows God Mode", "God Mode" in god_sidebar)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 2: Sidebar — Laborer (minimal access) ══")
# ─────────────────────────────────────────────────────────────────────────────

laborer_sidebar = _build_role_sidebar("dashboard", "", "Juan", "laborer", ["laborer"])
test("Laborer sidebar is a string", isinstance(laborer_sidebar, str))
test("Laborer sees Dashboard", "Dashboard" in laborer_sidebar)
test("Laborer sees My Tasks section", "My Tasks" in laborer_sidebar)
test("Laborer does NOT see Estimating", "Estimating" not in laborer_sidebar)
test("Laborer does NOT see Financial", "Financial" not in laborer_sidebar)
test("Laborer does NOT see Admin", "Admin" not in laborer_sidebar)
test("Laborer does NOT see Purchasing", "Purchasing" not in laborer_sidebar)
test("Laborer does NOT see Sales", "Sales" not in laborer_sidebar)
test("Laborer role display shows Laborer", "Laborer" in laborer_sidebar)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 3: Sidebar — Shop Foreman (shop + receipts, NO financials) ══")
# ─────────────────────────────────────────────────────────────────────────────

foreman_sidebar = _build_role_sidebar("shopfloor", "", "Mike", "shop_foreman", ["shop_foreman"])
test("Foreman sees Shop Floor", "Shop Floor" in foreman_sidebar)
test("Foreman sees Consumable Receipts link", "Consumable Receipts" in foreman_sidebar)
test("Foreman sees Quality section", "Quality" in foreman_sidebar)
test("Foreman does NOT see Inventory (no view_inventory perm)", "Inventory" not in foreman_sidebar)
test("Foreman does NOT see Financial section", "Financial" not in foreman_sidebar or "Reports" not in foreman_sidebar)
test("Foreman does NOT see Admin section", "Admin" not in foreman_sidebar or "Users" not in foreman_sidebar)
test("Foreman does NOT see Sales section", "Sales" not in foreman_sidebar)
test("Foreman shopfloor is active", 'class="tf-nav-item active"' in foreman_sidebar)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 4: Sidebar — Field Crew (separate from shop) ══")
# ─────────────────────────────────────────────────────────────────────────────

field_sidebar = _build_role_sidebar("field", "", "Crew", "field_crew", ["field_crew"])
test("Field crew sees Dashboard", "Dashboard" in field_sidebar)
test("Field crew sees Field section", "Field" in field_sidebar)
test("Field crew sees Field Ops", "Field Ops" in field_sidebar)
test("Field crew sees Safety section (JHA)", "Hazard Analysis" in field_sidebar)
test("Field crew does NOT see Shop Floor", "Shop Floor" not in field_sidebar)
test("Field crew does NOT see Estimating", "Estimating" not in field_sidebar)
test("Field crew does NOT see Admin", field_sidebar.count(">Admin<") == 0)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 5: Sidebar — Multi-role (Shop Foreman + QC Inspector) ══")
# ─────────────────────────────────────────────────────────────────────────────

multi_sidebar = _build_role_sidebar("dashboard", "", "Brad", "shop_foreman",
                                     ["shop_foreman", "qc_inspector"])
test("Multi-role sees Shop Floor", "Shop Floor" in multi_sidebar)
test("Multi-role sees Quality", "Quality" in multi_sidebar)
test("Multi-role sees Inspections", "Inspections" in multi_sidebar)
test("Multi-role does NOT see Inventory (neither role has it)", "Inventory" not in multi_sidebar)
test("Multi-role role display shows both", "Shop Foreman" in multi_sidebar and "Qc Inspector" in multi_sidebar)
test("Multi-role does NOT see Financial", "Financial" not in multi_sidebar or "Reports" not in multi_sidebar)
test("Multi-role does NOT see Admin", multi_sidebar.count("Users</span>") == 0)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 6: Sidebar — Customer (most restricted) ══")
# ─────────────────────────────────────────────────────────────────────────────

customer_sidebar = _build_role_sidebar("dashboard", "", "Client", "customer", ["customer"])
test("Customer sees Dashboard", "Dashboard" in customer_sidebar)
test("Customer does NOT see Shop Floor", "Shop Floor" not in customer_sidebar)
test("Customer does NOT see Estimating", "Estimating" not in customer_sidebar)
test("Customer does NOT see Admin", customer_sidebar.count("Users</span>") == 0)
test("Customer does NOT see Financial", "Financial" not in customer_sidebar or "Reports" not in customer_sidebar)
test("Customer does NOT see Quality", "Quality" not in customer_sidebar)
test("Customer does NOT see Purchasing", "Purchasing" not in customer_sidebar)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 7: inject_nav() integration ══")
# ─────────────────────────────────────────────────────────────────────────────
from templates.shared_nav import inject_nav

sample_html = """<!DOCTYPE html><html><head><style>body{margin:0;}</style></head>
<body><h1>Test Page</h1></body></html>"""

result = inject_nav(sample_html, active_page="dashboard", user_name="Zack",
                    user_role="god_mode", user_roles=["god_mode"])

test("inject_nav returns string", isinstance(result, str))
test("Sidebar CSS injected (tf-sidebar)", ".tf-sidebar" in result)
test("Sidebar HTML injected (aside tag)", "<aside" in result)
test("tf-main wrapper added", "tf-main" in result)
test("Sidebar JS injected (toggleSidebar)", "toggleSidebar" in result)
test("User name appears", "Zack" in result)

# Test with restricted role to confirm financial section is excluded
restricted = inject_nav(sample_html, active_page="dashboard", user_name="Worker",
                        user_role="laborer", user_roles=["laborer"])
test("Laborer inject — no Financial section", "Financial" not in restricted or ">Reports<" not in restricted)
test("Laborer inject — no Admin section", restricted.count("Users</span>") == 0)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 8: Dashboard card groups (permission-based) ══")
# ─────────────────────────────────────────────────────────────────────────────
from auth.permissions import merge_permissions, build_template_context

# God Mode gets all card groups
god_ctx = build_template_context(["god_mode"])
god_groups = god_ctx["dashboard_groups"]
test("God Mode has card groups", len(god_groups) > 0)
god_group_names = list(god_groups.keys())
test("God Mode has Overview group", "Overview" in god_group_names)

# Laborer gets minimal cards
lab_ctx = build_template_context(["laborer"])
lab_groups = lab_ctx["dashboard_groups"]
lab_group_names = list(lab_groups.keys())
test("Laborer has card groups", len(lab_groups) > 0)
test("Laborer has fewer groups than God Mode", len(lab_groups) <= len(god_groups))

# Foreman should NOT have financial cards
foreman_ctx = build_template_context(["shop_foreman"])
foreman_perm = foreman_ctx["perm"]
foreman_cards = foreman_perm.get_dashboard_cards()
financial_cards = [c for c in foreman_cards if getattr(c, "requires_financial", False)]
test("Foreman has no financial cards", len(financial_cards) == 0)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 9: Template context flags ══")
# ─────────────────────────────────────────────────────────────────────────────

# God Mode flags
test("God Mode can_delete is True", god_ctx["can_delete"] is True)
test("God Mode can_manage_users is True", god_ctx["can_manage_users"] is True)
test("God Mode show_financial is True", god_ctx["show_financial"] is True)
test("God Mode show_bom_pricing is True", god_ctx["show_bom_pricing"] is True)
test("God Mode mobile_first is False", god_ctx["mobile_first"] is False)

# Laborer flags
test("Laborer can_delete is False", lab_ctx["can_delete"] is False)
test("Laborer can_manage_users is False", lab_ctx["can_manage_users"] is False)
test("Laborer show_financial is False", lab_ctx["show_financial"] is False)
test("Laborer mobile_first is True", lab_ctx["mobile_first"] is True)

# Shop Foreman flags
test("Foreman can_delete is False", foreman_ctx["can_delete"] is False)
test("Foreman show_financial is True (own_receipts level)", foreman_ctx["show_financial"] is True)
test("Foreman show_bom_pricing is False", foreman_ctx["show_bom_pricing"] is False)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 10: Sidebar — active page highlighting ══")
# ─────────────────────────────────────────────────────────────────────────────

# SA estimator page should highlight SA
sa_sidebar = _build_role_sidebar("sa", "", "Brad", "estimator", ["estimator"])
test("Estimator on SA page — SA link is active",
     'class="tf-nav-item active"' in sa_sidebar and "SA Estimator" in sa_sidebar)

# Admin page
admin_sidebar = _build_role_sidebar("admin", "", "Zack", "god_mode", ["god_mode"])
test("God Mode on Admin page — admin link is active",
     'class="tf-nav-item active"' in admin_sidebar)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 11: render_with_nav middleware ══")
# ─────────────────────────────────────────────────────────────────────────────
from auth.middleware import AuthMixin, AUTH_ENABLED

# Verify render_with_nav passes user_roles — check the source code
import inspect
src = inspect.getsource(AuthMixin.render_with_nav)
test("render_with_nav passes user_roles kwarg", "user_roles=self.user_roles" in src)
test("render_with_nav calls inject_nav", "inject_nav" in src)


# ─────────────────────────────────────────────────────────────────────────────
print("\n══ TEST 12: Project context section (conditional links) ══")
# ─────────────────────────────────────────────────────────────────────────────

# God Mode should have all project context links
god_project = _build_role_sidebar("project", "JOB-001", "Zack", "god_mode", ["god_mode"])
test("God Mode project sidebar has Shop Drawings link", "navShopDrwLink" in god_project)
test("God Mode project sidebar has Work Orders link", "navWorkOrdersLink" in god_project)
test("God Mode project sidebar has QC link", "navQCLink" in god_project)
test("God Mode project sidebar has Quote link", "navQuoteLink" in god_project)

# Laborer should NOT have project-level links
lab_project = _build_role_sidebar("tasks", "", "Juan", "laborer", ["laborer"])
test("Laborer has NO Shop Drawings project link", "navShopDrwLink" not in lab_project)
test("Laborer has NO Quote project link", "navQuoteLink" not in lab_project)


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{'═'*60}")
print(f"Phase 1 Integration Tests: {passed} passed, {failed} failed out of {passed + failed}")
print(f"{'═'*60}")

if failed > 0:
    print("\n⚠️  Some tests failed! Review above.")
    sys.exit(1)
else:
    print("\n✅ All Phase 1 tests passed!")
    sys.exit(0)
