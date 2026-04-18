"""
TitanForge RBAC — Role Definitions
18 roles with granular permissions, dashboard cards, sidebar sections.

Reference: RULES.md §2 (Roles & Permissions), §3 (Page Access Matrix)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set


# ─────────────────────────────────────────────────────────────────────────────
# PERMISSION STRINGS
# Every action in the system maps to one of these. Handlers check these,
# never role names directly (except for God Mode overrides).
# ─────────────────────────────────────────────────────────────────────────────

class P:
    """Permission constants. Use P.VIEW_DASHBOARD instead of magic strings."""

    # ── System Administration ────────────────────────────────────────────────
    MANAGE_USERS         = "manage_users"           # Create/deactivate users, assign roles
    MANAGE_SETTINGS      = "manage_settings"         # System config, defaults, pricing, company info
    VIEW_AUDIT_LOG       = "view_audit_log"
    DELETE_ANYTHING       = "delete_anything"         # Projects, files, data (God Mode only)

    # ── Dashboard ────────────────────────────────────────────────────────────
    VIEW_DASHBOARD       = "view_dashboard"          # Everyone has this

    # ── Calculator / Estimating ──────────────────────────────────────────────
    RUN_CALCULATOR       = "run_calculator"           # SA Calculator full access
    VIEW_CALCULATOR      = "view_calculator"          # Read-only calculator output
    CREATE_QUOTES        = "create_quotes"
    VIEW_QUOTES          = "view_quotes"
    VIEW_QUOTE_TOTALS    = "view_quote_totals"        # Total only (Sales)

    # ── BOM & Pricing ────────────────────────────────────────────────────────
    VIEW_BOM             = "view_bom"
    VIEW_BOM_PRICING     = "view_bom_pricing"         # See dollar amounts on BOM
    VIEW_SELL_PRICES     = "view_sell_prices"          # Customer-facing prices
    VIEW_VENDOR_COSTS    = "view_vendor_costs"         # Cost from vendors (Purchasing)
    VIEW_MARGINS         = "view_margins"              # Margin / markup data
    EDIT_PRICING         = "edit_pricing"              # Override prices

    # ── Projects ─────────────────────────────────────────────────────────────
    CREATE_PROJECTS      = "create_projects"
    EDIT_PROJECTS        = "edit_projects"
    VIEW_PROJECTS        = "view_projects"
    VIEW_PROJECT_FINANCIALS = "view_project_financials"
    CONVERT_QUOTE_TO_PROJECT = "convert_quote_to_project"
    SET_MILESTONES       = "set_milestones"
    DELETE_PROJECTS      = "delete_projects"          # Requires God Mode

    # ── Shop Drawings ────────────────────────────────────────────────────────
    VIEW_SHOP_DRAWINGS   = "view_shop_drawings"
    EDIT_SHOP_DRAWINGS   = "edit_shop_drawings"       # Engineer / God / Admin
    APPROVE_DRAWINGS     = "approve_drawings"          # Stamp drawings

    # ── Work Orders ──────────────────────────────────────────────────────────
    CREATE_WORK_ORDERS   = "create_work_orders"
    EDIT_WORK_ORDERS     = "edit_work_orders"
    VIEW_WORK_ORDERS     = "view_work_orders"
    VIEW_OWN_WORK_ITEMS  = "view_own_work_items"       # Filtered to assigned items
    APPROVE_WORK_ORDERS  = "approve_work_orders"
    ASSIGN_OPERATORS     = "assign_operators"
    REPRIORITIZE_QUEUE   = "reprioritize_queue"

    # ── Work Station (fabrication floor) ──────────────────────────────────────
    SCAN_START_FINISH    = "scan_start_finish"         # QR scan to start/finish items
    LOG_COIL_CHANGEOVER  = "log_coil_changeover"
    LOG_ITEM_NOTES       = "log_item_notes"            # Operator notes on items

    # ── QC / Inspection ──────────────────────────────────────────────────────
    VIEW_QC              = "view_qc"
    PERFORM_INSPECTIONS  = "perform_inspections"
    SIGN_OFF_QC          = "sign_off_qc"               # Digital signature = passes
    REJECT_QC_ITEMS      = "reject_qc_items"
    CREATE_NCR           = "create_ncr"
    MANAGE_AISC_LIBRARY  = "manage_aisc_library"
    VIEW_AISC_LIBRARY    = "view_aisc_library"

    # ── Inventory ────────────────────────────────────────────────────────────
    VIEW_INVENTORY       = "view_inventory"            # Quantities only
    VIEW_INVENTORY_COSTS = "view_inventory_costs"      # Dollar amounts on inventory
    EDIT_INVENTORY       = "edit_inventory"             # Receive, allocate, modify
    RECEIVE_INVENTORY    = "receive_inventory"
    ALLOCATE_STOCK       = "allocate_stock"
    MANAGE_MILL_CERTS    = "manage_mill_certs"

    # ── Purchasing ───────────────────────────────────────────────────────────
    CREATE_PO            = "create_po"
    VIEW_PO              = "view_po"
    VIEW_PO_PRICING      = "view_po_pricing"
    MANAGE_VENDORS       = "manage_vendors"

    # ── Shipping ─────────────────────────────────────────────────────────────
    BUILD_LOADS          = "build_loads"
    GENERATE_BOL         = "generate_bol"
    MARK_SHIPPED         = "mark_shipped"
    VIEW_SHIPPING        = "view_shipping"

    # ── Financial Reports ────────────────────────────────────────────────────
    VIEW_FINANCIALS      = "view_financials"           # Full financial reports
    VIEW_PROJECT_PNL     = "view_project_pnl"
    PROCESS_EXPENSES     = "process_expenses"

    # ── Sales Pipeline ───────────────────────────────────────────────────────
    MANAGE_LEADS         = "manage_leads"
    VIEW_PIPELINE        = "view_pipeline"
    VIEW_CUSTOMER_INFO   = "view_customer_info"

    # ── Consumable Receipts ──────────────────────────────────────────────────
    SUBMIT_RECEIPTS      = "submit_receipts"           # Shop Foreman, Field Crew
    VIEW_ALL_RECEIPTS    = "view_all_receipts"         # Accounting
    VIEW_OWN_RECEIPTS    = "view_own_receipts"         # Own submissions only

    # ── Field Operations ─────────────────────────────────────────────────────
    SUBMIT_DAILY_REPORT  = "submit_daily_report"
    SUBMIT_JHA           = "submit_jha"
    UPLOAD_FIELD_PHOTOS  = "upload_field_photos"
    TRACK_EQUIPMENT      = "track_equipment"
    SUBMIT_EXPENSES      = "submit_expenses"
    CREATE_PUNCH_LIST    = "create_punch_list"
    VIEW_FIELD_REPORTS   = "view_field_reports"
    VIEW_FIELD_DRAWINGS  = "view_field_drawings"       # Offline-capable

    # ── Safety ───────────────────────────────────────────────────────────────
    REVIEW_JHA           = "review_jha"
    FILE_INCIDENT        = "file_incident"
    VIEW_SAFETY_METRICS  = "view_safety_metrics"
    STOP_WORK            = "stop_work"                 # Alerts PM + God Mode

    # ── Scheduling & Production Planning ────────────────────────────────────
    MANAGE_SCHEDULE      = "manage_schedule"            # Create/edit schedules, set priorities
    VIEW_SCHEDULE        = "view_schedule"              # Read-only schedule/calendar access

    # ── Customer Portal (future) ─────────────────────────────────────────────
    VIEW_OWN_PROJECT     = "view_own_project"          # Customer sees their project only
    VIEW_SHARED_PHOTOS   = "view_shared_photos"
    DOWNLOAD_DOCUMENTS   = "download_documents"


# Shorthand for readability in role definitions below
PERMISSIONS = {k: v for k, v in vars(P).items() if not k.startswith("_")}


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD CARD DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DashboardCard:
    """A modular card rendered on the role-merged dashboard."""
    id: str                          # Unique card ID (e.g. "business_summary")
    title: str                       # Display title
    group: str                       # Grouping header (Shop Floor, Quality, etc.)
    icon: str = ""                   # Icon class or emoji
    link: str = ""                   # "See all" target URL
    requires_financial: bool = False # Card contains dollar amounts
    priority: int = 50               # Sort order within group (lower = higher)


# Card registry — referenced by role definitions
CARDS = {
    # ── Admin / Overview ─────────────────────
    "business_summary":     DashboardCard("business_summary", "Business Summary", "Overview", link="/reports", requires_financial=True, priority=10),
    "all_projects":         DashboardCard("all_projects", "All Projects", "Overview", link="/projects", priority=20),
    "all_projects_fin":     DashboardCard("all_projects_fin", "All Projects", "Overview", link="/projects", requires_financial=True, priority=20),
    "user_management":      DashboardCard("user_management", "User Management", "Administration", link="/admin", priority=10),
    "system_health":        DashboardCard("system_health", "System Health", "Administration", priority=20),
    "audit_log":            DashboardCard("audit_log", "Audit Log", "Administration", link="/audit", priority=30),
    "recent_activity":      DashboardCard("recent_activity", "Recent Activity", "Overview", priority=30),

    # ── Project Management ───────────────────
    "active_projects":      DashboardCard("active_projects", "Active Projects", "Projects", link="/projects", requires_financial=True, priority=10),
    "milestones":           DashboardCard("milestones", "Milestones", "Projects", priority=20),
    "shop_progress":        DashboardCard("shop_progress", "Shop Progress", "Projects", priority=30),
    "field_status":         DashboardCard("field_status", "Field Status", "Projects", priority=40),
    "customer_comms":       DashboardCard("customer_comms", "Customer Communications", "Projects", priority=50),

    # ── Estimating ───────────────────────────
    "active_quotes":        DashboardCard("active_quotes", "Active Quotes", "Estimating", link="/sa", priority=10),
    "quick_calc":           DashboardCard("quick_calc", "Quick Calculator", "Estimating", link="/sa", priority=20),
    "inventory_summary":    DashboardCard("inventory_summary", "Inventory Summary", "Estimating", priority=30),

    # ── Sales ────────────────────────────────
    "sales_pipeline":       DashboardCard("sales_pipeline", "Sales Pipeline", "Sales", priority=10),
    "active_leads":         DashboardCard("active_leads", "Active Leads", "Sales", priority=20),
    "quote_activity":       DashboardCard("quote_activity", "Recent Quote Activity", "Sales", priority=30),
    "win_loss":             DashboardCard("win_loss", "Win / Loss", "Sales", priority=40),

    # ── Purchasing ───────────────────────────
    "open_pos":             DashboardCard("open_pos", "Open POs", "Purchasing", requires_financial=True, priority=10),
    "pending_deliveries":   DashboardCard("pending_deliveries", "Pending Deliveries", "Purchasing", priority=20),
    "price_alerts":         DashboardCard("price_alerts", "Price Alerts", "Purchasing", requires_financial=True, priority=30),
    "vendor_summary":       DashboardCard("vendor_summary", "Vendor Summary", "Purchasing", priority=40),

    # ── Inventory ────────────────────────────
    "inventory_alerts":     DashboardCard("inventory_alerts", "Inventory Alerts", "Inventory", priority=10),
    "incoming_deliveries":  DashboardCard("incoming_deliveries", "Incoming Deliveries", "Inventory", priority=20),
    "allocation_summary":   DashboardCard("allocation_summary", "Allocation Summary", "Inventory", priority=30),
    "recent_receiving":     DashboardCard("recent_receiving", "Recent Receiving", "Inventory", priority=40),

    # ── Accounting ───────────────────────────
    "revenue_summary":      DashboardCard("revenue_summary", "Revenue Summary", "Financial", requires_financial=True, priority=10),
    "pending_expenses":     DashboardCard("pending_expenses", "Pending Expense Reports", "Financial", requires_financial=True, priority=20),
    "project_pnl":          DashboardCard("project_pnl", "Project P&L", "Financial", requires_financial=True, priority=30),
    "vendor_bills":         DashboardCard("vendor_bills", "Vendor Bills Due", "Financial", requires_financial=True, priority=40),

    # ── Shop Floor ───────────────────────────
    "shop_overview":        DashboardCard("shop_overview", "Shop Floor Overview", "Shop Floor", link="/shop-floor", priority=10),
    "active_projects_nf":   DashboardCard("active_projects_nf", "Active Projects", "Shop Floor", link="/projects", priority=20),
    "today_priorities":     DashboardCard("today_priorities", "Today's Priorities", "Shop Floor", priority=30),
    "crew_status":          DashboardCard("crew_status", "Crew Status", "Shop Floor", priority=40),
    "receipt_log":          DashboardCard("receipt_log", "Consumable Receipts", "Shop Floor", link="/receipts", priority=50),

    # ── QC ───────────────────────────────────
    "inspection_queue":     DashboardCard("inspection_queue", "Inspection Queue", "Quality", priority=10),
    "open_ncrs":            DashboardCard("open_ncrs", "Open NCRs", "Quality", priority=20),
    "recent_signoffs":      DashboardCard("recent_signoffs", "Recent Sign-offs", "Quality", priority=30),
    "aisc_shortcut":        DashboardCard("aisc_shortcut", "AISC Library", "Quality", priority=40),

    # ── Engineer ─────────────────────────────
    "drawings_pending":     DashboardCard("drawings_pending", "Drawings Pending Review", "Engineering", priority=10),
    "recent_uploads":       DashboardCard("recent_uploads", "Recent Uploads", "Engineering", priority=20),
    "project_drawing_sets": DashboardCard("project_drawing_sets", "Project Drawing Sets", "Engineering", priority=30),

    # ── Operator ─────────────────────────────
    "machine_status":       DashboardCard("machine_status", "Machine Status", "My Station", priority=10),
    "run_queue":            DashboardCard("run_queue", "Run Queue", "My Station", priority=20),
    "production_log":       DashboardCard("production_log", "Production Log", "My Station", priority=30),

    # ── Welder ───────────────────────────────
    "my_queue":             DashboardCard("my_queue", "My Queue", "My Work", priority=10),
    "active_item":          DashboardCard("active_item", "Active Item", "My Work", priority=20),
    "recently_completed":   DashboardCard("recently_completed", "Recently Completed", "My Work", priority=30),

    # ── Shipping ─────────────────────────────
    "ready_to_ship":        DashboardCard("ready_to_ship", "Ready to Ship", "Shipping", priority=10),
    "active_loads":         DashboardCard("active_loads", "Active Loads", "Shipping", priority=20),
    "fab_progress":         DashboardCard("fab_progress", "Fabrication Progress", "Shipping", priority=30),

    # ── Laborer ──────────────────────────────
    "today_tasks":          DashboardCard("today_tasks", "Today's Tasks", "My Tasks", priority=10),
    "quick_scan":           DashboardCard("quick_scan", "Quick Scan", "My Tasks", priority=20),
    "recent_scans":         DashboardCard("recent_scans", "Recent Activity", "My Tasks", priority=30),

    # ── Field Crew ───────────────────────────
    "field_project_select": DashboardCard("field_project_select", "Active Project", "Field", priority=10),
    "field_documents":      DashboardCard("field_documents", "Project Documents", "Field", priority=20),
    "field_daily_actions":  DashboardCard("field_daily_actions", "Daily Actions", "Field", priority=30),
    "field_equipment":      DashboardCard("field_equipment", "Equipment & Expenses", "Field", priority=40),
    "field_deliveries":     DashboardCard("field_deliveries", "Deliveries", "Field", priority=50),

    # ── Safety ───────────────────────────────
    "open_jhas":            DashboardCard("open_jhas", "Open JHAs", "Safety", priority=10),
    "incident_log":         DashboardCard("incident_log", "Incident Log", "Safety", priority=20),
    "safety_metrics":       DashboardCard("safety_metrics", "Safety Metrics", "Safety", priority=30),
    "stop_work_alerts":     DashboardCard("stop_work_alerts", "Stop-Work Alerts", "Safety", priority=40),

    # ── Customer ─────────────────────────────
    "my_project_status":    DashboardCard("my_project_status", "My Project Status", "My Project", priority=10),
    "upcoming_dates":       DashboardCard("upcoming_dates", "Upcoming Dates", "My Project", priority=20),
    "customer_photos":      DashboardCard("customer_photos", "Recent Photos", "My Project", priority=30),
    "customer_documents":   DashboardCard("customer_documents", "Documents", "My Project", priority=40),
}


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR SECTION DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

# Sidebar sections in display order. Each role references these by ID.
SIDEBAR_SECTIONS = [
    {"id": "dashboard",      "label": "Dashboard",       "icon": "home",      "url": "/dashboard"},
    {"id": "estimating",     "label": "Estimating",      "icon": "calculator", "children": [
        {"id": "calculator",   "label": "Calculator",    "url": "/sa"},
        {"id": "my_projects",  "label": "My Projects",   "url": "/projects?mine=1"},
        {"id": "quotes",       "label": "Quotes",        "url": "/quotes"},
        {"id": "inv_levels",   "label": "Inventory Levels", "url": "/inventory?readonly=1"},
    ]},
    {"id": "projects",       "label": "Projects",        "icon": "folder",    "children": [
        {"id": "project_list", "label": "All Projects",  "url": "/projects"},
        {"id": "timeline",     "label": "Timeline",      "url": "/timeline"},
        {"id": "budget",       "label": "Budget",        "url": "/budget"},
    ]},
    {"id": "shop_floor",     "label": "Shop Floor",      "icon": "factory",   "children": [
        {"id": "shop_dash",      "label": "Dashboard",      "url": "/shop-floor"},
        {"id": "work_orders",    "label": "Work Orders",    "url": "/work-orders"},
        {"id": "workflows",      "label": "Workflows",      "url": "/workflows"},
        {"id": "machine_queues", "label": "Machine Queues", "url": "/machines"},
        {"id": "crew",           "label": "Crew",           "url": "/crew"},
        {"id": "receipts",       "label": "Consumable Receipts", "url": "/receipts"},
        {"id": "shop_drawings_nav", "label": "Shop Drawings", "url": "/shop-drawings"},
    ]},
    {"id": "quality",        "label": "Quality",         "icon": "shield-check", "children": [
        {"id": "inspections",    "label": "Inspection Queue",  "url": "/qc"},
        {"id": "ncr_log",       "label": "NCR Log",           "url": "/qc/ncr"},
        {"id": "aisc_library",  "label": "AISC Library",      "url": "/aisc"},
        {"id": "traceability",  "label": "Traceability",      "url": "/traceability"},
        {"id": "qc_audit",      "label": "Audit Log",         "url": "/audit?filter=qc"},
    ]},
    {"id": "inventory",      "label": "Inventory",       "icon": "package",   "children": [
        {"id": "coil_inv",       "label": "Coil Inventory",   "url": "/inventory?type=coils"},
        {"id": "purchased",      "label": "Purchased Items",  "url": "/inventory?type=purchased"},
        {"id": "rebar_stock",    "label": "Rebar Stock",      "url": "/inventory?type=rebar"},
        {"id": "fasteners",      "label": "Fasteners",        "url": "/inventory?type=fasteners"},
        {"id": "receiving",      "label": "Receiving",         "url": "/receiving"},
        {"id": "allocations",    "label": "Allocations",      "url": "/allocations"},
        {"id": "mill_certs",     "label": "Mill Certs",       "url": "/certs"},
    ]},
    {"id": "purchasing",     "label": "Purchasing",      "icon": "shopping-cart", "children": [
        {"id": "pos",           "label": "Purchase Orders",   "url": "/pos"},
        {"id": "vendors",       "label": "Vendors",           "url": "/vendors"},
        {"id": "price_history", "label": "Price History",     "url": "/prices"},
        {"id": "mat_reqs",      "label": "Material Reqs",     "url": "/material-reqs"},
    ]},
    {"id": "shipping",       "label": "Shipping",        "icon": "truck",     "children": [
        {"id": "ship_dash",     "label": "Dashboard",         "url": "/shipping"},
        {"id": "build_load",    "label": "Build Load",        "url": "/shipping/build"},
        {"id": "active_ships",  "label": "Active Shipments",  "url": "/shipping/active"},
        {"id": "bol_history",   "label": "BOL History",       "url": "/shipping/bol"},
    ]},
    {"id": "field",          "label": "Field",           "icon": "hard-hat",  "children": [
        {"id": "field_projects", "label": "My Projects",      "url": "/field/projects"},
        {"id": "field_docs",     "label": "Documents",        "url": "/field/docs"},
        {"id": "daily_reports",  "label": "Daily Reports",    "url": "/field/daily"},
        {"id": "jha",           "label": "Hazard Analysis",   "url": "/field/jha"},
        {"id": "field_photos",  "label": "Photos",            "url": "/field/photos"},
        {"id": "equipment",     "label": "Equipment",         "url": "/field/equipment"},
        {"id": "expenses",      "label": "Expenses",          "url": "/field/expenses"},
        {"id": "punch_list",    "label": "Punch List",        "url": "/field/punch"},
    ]},
    {"id": "safety",         "label": "Safety",          "icon": "alert-triangle", "children": [
        {"id": "jha_review",    "label": "JHA Review",        "url": "/safety/jha"},
        {"id": "incidents",     "label": "Incidents",         "url": "/safety/incidents"},
        {"id": "safety_stats",  "label": "Safety Metrics",    "url": "/safety/metrics"},
        {"id": "training",      "label": "Training Records",  "url": "/safety/training"},
        {"id": "equip_inspect", "label": "Equipment Inspections", "url": "/safety/equipment"},
    ]},
    {"id": "financial",      "label": "Financial",       "icon": "dollar-sign", "children": [
        {"id": "fin_dash",      "label": "Dashboard",         "url": "/financial"},
        {"id": "project_costs", "label": "Project Costs",     "url": "/financial/projects"},
        {"id": "expense_rpts",  "label": "Expense Reports",   "url": "/financial/expenses"},
        {"id": "equip_costs",   "label": "Equipment Costs",   "url": "/financial/equipment"},
        {"id": "vendor_bills_nav", "label": "Vendor Bills",   "url": "/financial/vendor-bills"},
        {"id": "invoices",      "label": "Invoices",          "url": "/financial/invoices"},
        {"id": "reports",       "label": "Reports",           "url": "/financial/reports"},
    ]},
    {"id": "sales",          "label": "Sales",           "icon": "trending-up", "children": [
        {"id": "pipeline_nav",  "label": "Pipeline",          "url": "/sales/pipeline"},
        {"id": "leads",         "label": "Leads",             "url": "/sales/leads"},
        {"id": "customers_nav", "label": "Customers",         "url": "/customers"},
        {"id": "quote_status",  "label": "Quote Status",      "url": "/sales/quotes"},
    ]},
    {"id": "admin",          "label": "Administration",  "icon": "settings",  "children": [
        {"id": "user_mgmt",     "label": "Users",             "url": "/admin/users"},
        {"id": "settings",      "label": "Settings",          "url": "/admin/settings"},
        {"id": "audit_log_nav", "label": "Audit Log",         "url": "/audit"},
    ]},
    # ── Standalone sections for role-specific access ───
    {"id": "schedule",       "label": "Planning",        "icon": "calendar",  "children": [
        {"id": "sched_board",    "label": "Schedule",        "url": "/schedule"},
    ]},
    {"id": "reports",        "label": "Reports",         "icon": "bar-chart", "children": [
        {"id": "prod_reports",   "label": "Production Reports", "url": "/reports/production"},
        {"id": "exec_reports",   "label": "Executive Summary",  "url": "/reports/executive"},
    ]},
    {"id": "documents",      "label": "Documents",       "icon": "file-text", "children": [
        {"id": "doc_mgmt",      "label": "Doc Management",     "url": "/documents"},
    ]},
    {"id": "customers",      "label": "Customers",       "icon": "users",     "children": [
        {"id": "cust_list",      "label": "All Customers",      "url": "/customers"},
    ]},
    # ── Minimal sidebars for restricted roles ───
    {"id": "my_station",     "label": "My Station",      "icon": "cpu",       "children": [
        {"id": "my_machine",    "label": "My Machine",        "url": "/work-station/mine"},
        {"id": "my_run_queue",  "label": "Run Queue",         "url": "/work-station/queue"},
        {"id": "my_prod_log",   "label": "Production Log",    "url": "/work-station/log"},
        {"id": "my_coil_status","label": "Coil Status",       "url": "/work-station/coil"},
    ]},
    {"id": "my_work",        "label": "My Work",         "icon": "flame",     "children": [
        {"id": "my_weld_queue", "label": "My Queue",          "url": "/work-station/mine"},
        {"id": "my_drawings",   "label": "Shop Drawings",     "url": "/shop-drawings"},
        {"id": "my_cut_list",   "label": "Cut List",          "url": "/work-station/cuts"},
        {"id": "my_completed",  "label": "Completed Items",   "url": "/work-station/completed"},
    ]},
    {"id": "my_tasks",       "label": "My Tasks",        "icon": "clipboard", "children": [
        {"id": "laborer_tasks", "label": "Tasks",             "url": "/tasks"},
        {"id": "laborer_scan",  "label": "Scan",              "url": "/scan"},
    ]},
    {"id": "my_project",     "label": "My Project",      "icon": "eye",       "children": [
        {"id": "cust_status",   "label": "Project Status",    "url": "/portal/status"},
        {"id": "cust_photos",   "label": "Photos",            "url": "/portal/photos"},
        {"id": "cust_docs",     "label": "Documents",         "url": "/portal/docs"},
    ]},
]

# Build lookup by section id
_SIDEBAR_MAP = {s["id"]: s for s in SIDEBAR_SECTIONS}


# ─────────────────────────────────────────────────────────────────────────────
# ROLE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RoleDef:
    """Complete definition of a single role."""
    id: str
    name: str
    rank: int                                  # 0 = God Mode (highest privilege)
    description: str = ""
    financial_access: str = "none"             # "full", "quoting", "totals_only", "vendor", "own_receipts", "own_expenses", "none"
    can_delete: bool = False
    can_manage_users: bool = False
    mobile_first: bool = False
    permissions: List[str] = field(default_factory=list)
    dashboard_cards: List[str] = field(default_factory=list)
    sidebar_sections: List[str] = field(default_factory=list)


# ── All 18 roles ────────────────────────────────────────────────────────────

_ROLE_DEFS = [

    RoleDef(
        id="god_mode", name="God Mode", rank=0,
        description="Full system access including user management and delete capabilities.",
        financial_access="full", can_delete=True, can_manage_users=True,
        permissions=[
            P.VIEW_DASHBOARD, P.MANAGE_USERS, P.MANAGE_SETTINGS, P.VIEW_AUDIT_LOG, P.DELETE_ANYTHING,
            P.RUN_CALCULATOR, P.VIEW_CALCULATOR, P.CREATE_QUOTES, P.VIEW_QUOTES, P.VIEW_QUOTE_TOTALS,
            P.VIEW_BOM, P.VIEW_BOM_PRICING, P.VIEW_SELL_PRICES, P.VIEW_VENDOR_COSTS, P.VIEW_MARGINS, P.EDIT_PRICING,
            P.CREATE_PROJECTS, P.EDIT_PROJECTS, P.VIEW_PROJECTS, P.VIEW_PROJECT_FINANCIALS, P.CONVERT_QUOTE_TO_PROJECT, P.SET_MILESTONES, P.DELETE_PROJECTS,
            P.VIEW_SHOP_DRAWINGS, P.EDIT_SHOP_DRAWINGS, P.APPROVE_DRAWINGS,
            P.CREATE_WORK_ORDERS, P.EDIT_WORK_ORDERS, P.VIEW_WORK_ORDERS, P.APPROVE_WORK_ORDERS, P.ASSIGN_OPERATORS, P.REPRIORITIZE_QUEUE,
            P.SCAN_START_FINISH, P.LOG_COIL_CHANGEOVER, P.LOG_ITEM_NOTES,
            P.VIEW_QC, P.PERFORM_INSPECTIONS, P.SIGN_OFF_QC, P.REJECT_QC_ITEMS, P.CREATE_NCR, P.MANAGE_AISC_LIBRARY, P.VIEW_AISC_LIBRARY,
            P.VIEW_INVENTORY, P.VIEW_INVENTORY_COSTS, P.EDIT_INVENTORY, P.RECEIVE_INVENTORY, P.ALLOCATE_STOCK, P.MANAGE_MILL_CERTS,
            P.CREATE_PO, P.VIEW_PO, P.VIEW_PO_PRICING, P.MANAGE_VENDORS,
            P.BUILD_LOADS, P.GENERATE_BOL, P.MARK_SHIPPED, P.VIEW_SHIPPING,
            P.VIEW_FINANCIALS, P.VIEW_PROJECT_PNL, P.PROCESS_EXPENSES,
            P.MANAGE_LEADS, P.VIEW_PIPELINE, P.VIEW_CUSTOMER_INFO,
            P.SUBMIT_RECEIPTS, P.VIEW_ALL_RECEIPTS, P.VIEW_OWN_RECEIPTS,
            P.SUBMIT_DAILY_REPORT, P.SUBMIT_JHA, P.UPLOAD_FIELD_PHOTOS, P.TRACK_EQUIPMENT, P.SUBMIT_EXPENSES, P.CREATE_PUNCH_LIST, P.VIEW_FIELD_REPORTS, P.VIEW_FIELD_DRAWINGS,
            P.REVIEW_JHA, P.FILE_INCIDENT, P.VIEW_SAFETY_METRICS, P.STOP_WORK,
            P.VIEW_OWN_PROJECT, P.VIEW_SHARED_PHOTOS, P.DOWNLOAD_DOCUMENTS,
            P.MANAGE_SCHEDULE, P.VIEW_SCHEDULE,
        ],
        dashboard_cards=["business_summary", "all_projects_fin", "user_management", "system_health", "audit_log"],
        sidebar_sections=["dashboard", "estimating", "projects", "shop_floor", "quality", "inventory", "purchasing", "shipping", "field", "safety", "financial", "sales", "admin"],
    ),

    RoleDef(
        id="admin", name="Admin", rank=1,
        description="Full system access including user management and project deletion.",
        financial_access="full", can_manage_users=True, can_delete=True,
        permissions=[
            P.VIEW_DASHBOARD, P.MANAGE_USERS, P.MANAGE_SETTINGS, P.VIEW_AUDIT_LOG, P.DELETE_ANYTHING,
            P.RUN_CALCULATOR, P.VIEW_CALCULATOR, P.CREATE_QUOTES, P.VIEW_QUOTES, P.VIEW_QUOTE_TOTALS,
            P.VIEW_BOM, P.VIEW_BOM_PRICING, P.VIEW_SELL_PRICES, P.VIEW_VENDOR_COSTS, P.VIEW_MARGINS, P.EDIT_PRICING,
            P.CREATE_PROJECTS, P.EDIT_PROJECTS, P.VIEW_PROJECTS, P.VIEW_PROJECT_FINANCIALS, P.CONVERT_QUOTE_TO_PROJECT, P.SET_MILESTONES, P.DELETE_PROJECTS,
            P.VIEW_SHOP_DRAWINGS, P.EDIT_SHOP_DRAWINGS, P.APPROVE_DRAWINGS,
            P.CREATE_WORK_ORDERS, P.EDIT_WORK_ORDERS, P.VIEW_WORK_ORDERS, P.APPROVE_WORK_ORDERS, P.ASSIGN_OPERATORS, P.REPRIORITIZE_QUEUE,
            P.SCAN_START_FINISH, P.LOG_COIL_CHANGEOVER, P.LOG_ITEM_NOTES,
            P.VIEW_QC, P.PERFORM_INSPECTIONS, P.SIGN_OFF_QC, P.REJECT_QC_ITEMS, P.CREATE_NCR, P.MANAGE_AISC_LIBRARY, P.VIEW_AISC_LIBRARY,
            P.VIEW_INVENTORY, P.VIEW_INVENTORY_COSTS, P.EDIT_INVENTORY, P.RECEIVE_INVENTORY, P.ALLOCATE_STOCK, P.MANAGE_MILL_CERTS,
            P.CREATE_PO, P.VIEW_PO, P.VIEW_PO_PRICING, P.MANAGE_VENDORS,
            P.BUILD_LOADS, P.GENERATE_BOL, P.MARK_SHIPPED, P.VIEW_SHIPPING,
            P.VIEW_FINANCIALS, P.VIEW_PROJECT_PNL, P.PROCESS_EXPENSES,
            P.MANAGE_LEADS, P.VIEW_PIPELINE, P.VIEW_CUSTOMER_INFO,
            P.SUBMIT_RECEIPTS, P.VIEW_ALL_RECEIPTS, P.VIEW_OWN_RECEIPTS,
            P.SUBMIT_DAILY_REPORT, P.SUBMIT_JHA, P.UPLOAD_FIELD_PHOTOS, P.TRACK_EQUIPMENT, P.SUBMIT_EXPENSES, P.CREATE_PUNCH_LIST, P.VIEW_FIELD_REPORTS, P.VIEW_FIELD_DRAWINGS,
            P.REVIEW_JHA, P.FILE_INCIDENT, P.VIEW_SAFETY_METRICS, P.STOP_WORK,
            P.MANAGE_SCHEDULE, P.VIEW_SCHEDULE,
        ],
        dashboard_cards=["business_summary", "all_projects_fin", "recent_activity"],
        sidebar_sections=["dashboard", "estimating", "projects", "shop_floor", "quality", "inventory", "purchasing", "shipping", "field", "safety", "financial", "sales", "admin"],
    ),

    RoleDef(
        id="project_manager", name="Project Manager", rank=2,
        description="Full project visibility including financials. Coordinates shop and field.",
        financial_access="full",
        permissions=[
            P.VIEW_DASHBOARD,
            P.RUN_CALCULATOR, P.VIEW_CALCULATOR, P.CREATE_QUOTES, P.VIEW_QUOTES, P.VIEW_QUOTE_TOTALS,
            P.VIEW_BOM, P.VIEW_BOM_PRICING, P.VIEW_SELL_PRICES, P.VIEW_MARGINS,
            P.CREATE_PROJECTS, P.EDIT_PROJECTS, P.VIEW_PROJECTS, P.VIEW_PROJECT_FINANCIALS, P.CONVERT_QUOTE_TO_PROJECT, P.SET_MILESTONES,
            P.VIEW_SHOP_DRAWINGS,
            P.CREATE_WORK_ORDERS, P.EDIT_WORK_ORDERS, P.VIEW_WORK_ORDERS, P.APPROVE_WORK_ORDERS,
            P.VIEW_QC,
            P.VIEW_INVENTORY, P.VIEW_INVENTORY_COSTS, P.VIEW_PO, P.VIEW_PO_PRICING,
            P.VIEW_SHIPPING, P.BUILD_LOADS, P.GENERATE_BOL, P.MARK_SHIPPED,
            P.VIEW_FINANCIALS, P.VIEW_PROJECT_PNL,
            P.VIEW_PIPELINE, P.VIEW_CUSTOMER_INFO,
            P.VIEW_ALL_RECEIPTS, P.VIEW_OWN_RECEIPTS,
            P.VIEW_FIELD_REPORTS, P.VIEW_FIELD_DRAWINGS,
            P.MANAGE_SCHEDULE, P.VIEW_SCHEDULE,
        ],
        dashboard_cards=["active_projects", "milestones", "shop_progress", "field_status", "customer_comms"],
        sidebar_sections=["dashboard", "projects", "customers", "schedule", "reports", "documents", "estimating", "shop_floor", "quality", "inventory", "purchasing", "shipping", "field", "financial", "sales"],
    ),

    RoleDef(
        id="estimator", name="Estimator", rank=3,
        description="Calculator, BOM, quoting. Sees pricing but not shop/field operations.",
        financial_access="quoting",
        permissions=[
            P.VIEW_DASHBOARD,
            P.RUN_CALCULATOR, P.VIEW_CALCULATOR, P.CREATE_QUOTES, P.VIEW_QUOTES,
            P.VIEW_BOM, P.VIEW_BOM_PRICING, P.VIEW_SELL_PRICES, P.EDIT_PRICING,
            P.CREATE_PROJECTS, P.EDIT_PROJECTS, P.VIEW_PROJECTS,
            P.VIEW_INVENTORY, P.VIEW_CUSTOMER_INFO, P.VIEW_SHOP_DRAWINGS,
        ],
        dashboard_cards=["active_quotes", "quick_calc", "inventory_summary"],
        sidebar_sections=["dashboard", "estimating", "projects", "customers", "documents"],
    ),

    RoleDef(
        id="sales", name="Sales / Business Dev", rank=4,
        description="Customer relationships, pipeline, quote totals. No BOM details.",
        financial_access="totals_only",
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_QUOTE_TOTALS,
            P.VIEW_PROJECTS,
            P.MANAGE_LEADS, P.VIEW_PIPELINE, P.VIEW_CUSTOMER_INFO,
        ],
        dashboard_cards=["sales_pipeline", "active_leads", "quote_activity", "win_loss"],
        sidebar_sections=["dashboard", "sales"],
    ),

    RoleDef(
        id="purchasing", name="Purchasing / Procurement", rank=5,
        description="Vendor costs, POs, material requirements. No customer pricing.",
        financial_access="vendor",
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_BOM,
            P.VIEW_PROJECTS,
            P.VIEW_VENDOR_COSTS,
            P.VIEW_INVENTORY, P.VIEW_INVENTORY_COSTS,
            P.CREATE_PO, P.VIEW_PO, P.VIEW_PO_PRICING, P.MANAGE_VENDORS,
        ],
        dashboard_cards=["open_pos", "pending_deliveries", "price_alerts", "vendor_summary"],
        sidebar_sections=["dashboard", "inventory", "shipping", "purchasing"],
    ),

    RoleDef(
        id="inventory_manager", name="Inventory Manager", rank=6,
        description="Full inventory control. Quantities only, no pricing.",
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_INVENTORY, P.EDIT_INVENTORY, P.RECEIVE_INVENTORY, P.ALLOCATE_STOCK, P.MANAGE_MILL_CERTS,
        ],
        dashboard_cards=["inventory_alerts", "incoming_deliveries", "allocation_summary", "recent_receiving"],
        sidebar_sections=["dashboard", "inventory"],
    ),

    RoleDef(
        id="accounting", name="Accounting / Bookkeeper", rank=7,
        description="All financial data. View/export only — cannot modify projects or operations.",
        financial_access="full",
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_BOM, P.VIEW_BOM_PRICING, P.VIEW_SELL_PRICES, P.VIEW_VENDOR_COSTS, P.VIEW_MARGINS,
            P.VIEW_PROJECTS, P.VIEW_PROJECT_FINANCIALS,
            P.VIEW_INVENTORY, P.VIEW_INVENTORY_COSTS,
            P.VIEW_PO, P.VIEW_PO_PRICING,
            P.VIEW_FINANCIALS, P.VIEW_PROJECT_PNL, P.PROCESS_EXPENSES,
            P.VIEW_ALL_RECEIPTS,
        ],
        dashboard_cards=["revenue_summary", "pending_expenses", "project_pnl", "vendor_bills"],
        sidebar_sections=["dashboard", "financial"],
    ),

    RoleDef(
        id="shop_foreman", name="Shop Foreman", rank=8,
        description="Manages shop floor. No costs. Can submit consumable receipts.",
        financial_access="own_receipts",
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_PROJECTS,
            P.VIEW_SHOP_DRAWINGS,
            P.CREATE_WORK_ORDERS, P.EDIT_WORK_ORDERS, P.VIEW_WORK_ORDERS, P.ASSIGN_OPERATORS, P.REPRIORITIZE_QUEUE,
            P.SCAN_START_FINISH, P.LOG_COIL_CHANGEOVER, P.LOG_ITEM_NOTES,
            P.VIEW_QC,
            P.SUBMIT_RECEIPTS, P.VIEW_OWN_RECEIPTS,
            P.MANAGE_SCHEDULE, P.VIEW_SCHEDULE,
        ],
        dashboard_cards=["shop_overview", "active_projects_nf", "today_priorities", "crew_status", "receipt_log"],
        sidebar_sections=["dashboard", "shop_floor"],
    ),

    RoleDef(
        id="qc_inspector", name="QA/QC Inspector", rank=9,
        description="Inspections, NCRs, traceability. Full QC authority.",
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_SHOP_DRAWINGS,
            P.VIEW_WORK_ORDERS,
            P.VIEW_QC, P.PERFORM_INSPECTIONS, P.SIGN_OFF_QC, P.REJECT_QC_ITEMS, P.CREATE_NCR,
            P.VIEW_AISC_LIBRARY,
            P.MANAGE_MILL_CERTS,
        ],
        mobile_first=True,
        dashboard_cards=["inspection_queue", "open_ncrs", "recent_signoffs", "aisc_shortcut"],
        sidebar_sections=["dashboard", "quality"],
    ),

    RoleDef(
        id="engineer", name="Engineer / Detailer", rank=10,
        description="Shop drawing edit access. Reviews calculator output. Stamps drawings.",
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_CALCULATOR,
            P.VIEW_PROJECTS,
            P.VIEW_SHOP_DRAWINGS, P.EDIT_SHOP_DRAWINGS, P.APPROVE_DRAWINGS,
            P.VIEW_AISC_LIBRARY,
        ],
        dashboard_cards=["drawings_pending", "recent_uploads", "project_drawing_sets"],
        sidebar_sections=["dashboard", "shop_floor", "projects", "documents"],
    ),

    RoleDef(
        id="roll_forming_operator", name="Roll Forming Operator", rank=11,
        description="Machine queue, coil info, scan start/finish. Own items only.",
        mobile_first=True,
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_OWN_WORK_ITEMS,
            P.SCAN_START_FINISH, P.LOG_COIL_CHANGEOVER, P.LOG_ITEM_NOTES,
            P.VIEW_SCHEDULE,
        ],
        dashboard_cards=["machine_status", "run_queue", "production_log"],
        sidebar_sections=["dashboard", "my_station"],
    ),

    RoleDef(
        id="welder", name="Welder", rank=12,
        description="Assigned items, shop drawings (read), scan start/finish.",
        mobile_first=True,
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_SHOP_DRAWINGS,
            P.VIEW_OWN_WORK_ITEMS,
            P.SCAN_START_FINISH, P.LOG_ITEM_NOTES,
            P.VIEW_SCHEDULE,
        ],
        dashboard_cards=["my_queue", "active_item", "recently_completed"],
        sidebar_sections=["dashboard", "my_work"],
    ),

    RoleDef(
        id="shipping_coordinator", name="Shipping Coordinator", rank=13,
        description="Build loads, BOL, track shipments. Weights/counts only, no pricing.",
        mobile_first=True,
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_PROJECTS,
            P.VIEW_WORK_ORDERS,
            P.BUILD_LOADS, P.GENERATE_BOL, P.MARK_SHIPPED, P.VIEW_SHIPPING,
            P.VIEW_SCHEDULE,
        ],
        dashboard_cards=["ready_to_ship", "active_loads", "fab_progress"],
        sidebar_sections=["dashboard", "shipping"],
    ),

    RoleDef(
        id="laborer", name="Laborer", rank=14,
        description="Staging/moving tasks. Scan to confirm. Minimal UI.",
        mobile_first=True,
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_OWN_WORK_ITEMS,
            P.SCAN_START_FINISH,
        ],
        dashboard_cards=["today_tasks", "quick_scan", "recent_scans"],
        sidebar_sections=["dashboard", "my_tasks"],
    ),

    RoleDef(
        id="field_crew", name="Field Crew", rank=15,
        description="Field ops — drawings, daily reports, JHA, photos, expenses. Mobile-first.",
        financial_access="own_expenses",
        mobile_first=True,
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_PROJECTS,
            P.VIEW_FIELD_DRAWINGS,
            P.SUBMIT_DAILY_REPORT, P.SUBMIT_JHA, P.UPLOAD_FIELD_PHOTOS,
            P.TRACK_EQUIPMENT, P.SUBMIT_EXPENSES, P.CREATE_PUNCH_LIST,
            P.VIEW_FIELD_REPORTS,
        ],
        dashboard_cards=["field_project_select", "field_documents", "field_daily_actions", "field_equipment", "field_deliveries"],
        sidebar_sections=["dashboard", "field"],
    ),

    RoleDef(
        id="safety_officer", name="Safety Officer", rank=16,
        description="JHA review, incident reports, safety metrics, stop-work authority.",
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_FIELD_REPORTS,
            P.REVIEW_JHA, P.FILE_INCIDENT, P.VIEW_SAFETY_METRICS, P.STOP_WORK,
        ],
        dashboard_cards=["open_jhas", "incident_log", "safety_metrics", "stop_work_alerts"],
        sidebar_sections=["dashboard", "safety"],
    ),

    RoleDef(
        id="customer", name="Customer", rank=17,
        description="External portal. Own project only — status, photos, documents.",
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_OWN_PROJECT, P.VIEW_SHARED_PHOTOS, P.DOWNLOAD_DOCUMENTS,
        ],
        dashboard_cards=["my_project_status", "upcoming_dates", "customer_photos", "customer_documents"],
        sidebar_sections=["dashboard", "my_project"],
    ),

    # ── Additional roles from 18-role RBAC spec ─────────────────────────────

    RoleDef(
        id="shop_manager", name="Shop Manager", rank=8,
        description="Full shop floor management including scheduling, drawings, reports, and inventory.",
        financial_access="own_receipts",
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_PROJECTS,
            P.VIEW_SHOP_DRAWINGS,
            P.CREATE_WORK_ORDERS, P.EDIT_WORK_ORDERS, P.VIEW_WORK_ORDERS, P.APPROVE_WORK_ORDERS,
            P.ASSIGN_OPERATORS, P.REPRIORITIZE_QUEUE,
            P.SCAN_START_FINISH, P.LOG_COIL_CHANGEOVER, P.LOG_ITEM_NOTES,
            P.VIEW_QC,
            P.VIEW_INVENTORY, P.EDIT_INVENTORY, P.RECEIVE_INVENTORY, P.ALLOCATE_STOCK,
            P.SUBMIT_RECEIPTS, P.VIEW_OWN_RECEIPTS,
            P.MANAGE_SCHEDULE, P.VIEW_SCHEDULE,
        ],
        dashboard_cards=["shop_overview", "active_projects_nf", "today_priorities", "crew_status", "receipt_log"],
        sidebar_sections=["dashboard", "shop_floor", "quality", "schedule", "reports", "inventory"],
    ),

    RoleDef(
        id="fabricator", name="Fabricator", rank=12,
        description="Shop floor fabrication. Work orders, queue, and shop drawings.",
        mobile_first=True,
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_SHOP_DRAWINGS,
            P.VIEW_WORK_ORDERS, P.VIEW_OWN_WORK_ITEMS,
            P.SCAN_START_FINISH, P.LOG_ITEM_NOTES,
            P.VIEW_SCHEDULE,
        ],
        dashboard_cards=["my_queue", "active_item", "recently_completed"],
        sidebar_sections=["dashboard", "shop_floor", "my_work"],
    ),

    RoleDef(
        id="qa_manager", name="QA Manager", rank=9,
        description="Full QC authority plus reporting. Manages inspection teams.",
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_SHOP_DRAWINGS,
            P.VIEW_WORK_ORDERS,
            P.VIEW_QC, P.PERFORM_INSPECTIONS, P.SIGN_OFF_QC, P.REJECT_QC_ITEMS, P.CREATE_NCR,
            P.VIEW_AISC_LIBRARY, P.MANAGE_AISC_LIBRARY,
            P.MANAGE_MILL_CERTS,
        ],
        dashboard_cards=["inspection_queue", "open_ncrs", "recent_signoffs", "aisc_shortcut"],
        sidebar_sections=["dashboard", "quality", "reports"],
    ),

    RoleDef(
        id="shipping_clerk", name="Shipping Clerk", rank=13,
        description="Shipping operations, load building, and inventory visibility.",
        mobile_first=True,
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_PROJECTS,
            P.VIEW_WORK_ORDERS,
            P.BUILD_LOADS, P.GENERATE_BOL, P.MARK_SHIPPED, P.VIEW_SHIPPING,
            P.VIEW_INVENTORY,
            P.VIEW_SCHEDULE,
        ],
        dashboard_cards=["ready_to_ship", "active_loads", "fab_progress"],
        sidebar_sections=["dashboard", "shipping", "inventory"],
    ),

    RoleDef(
        id="field_ops", name="Field Operations", rank=15,
        description="Field operations and job costing visibility.",
        financial_access="own_expenses",
        mobile_first=True,
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_PROJECTS, P.VIEW_PROJECT_FINANCIALS,
            P.VIEW_FIELD_DRAWINGS,
            P.SUBMIT_DAILY_REPORT, P.SUBMIT_JHA, P.UPLOAD_FIELD_PHOTOS,
            P.TRACK_EQUIPMENT, P.SUBMIT_EXPENSES, P.CREATE_PUNCH_LIST,
            P.VIEW_FIELD_REPORTS,
        ],
        dashboard_cards=["field_project_select", "field_documents", "field_daily_actions", "field_equipment"],
        sidebar_sections=["dashboard", "field", "financial"],
    ),

    RoleDef(
        id="foreman", name="Foreman", rank=8,
        description="Shop floor supervision with scheduling and queue management.",
        financial_access="own_receipts",
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_PROJECTS,
            P.VIEW_SHOP_DRAWINGS,
            P.CREATE_WORK_ORDERS, P.EDIT_WORK_ORDERS, P.VIEW_WORK_ORDERS,
            P.ASSIGN_OPERATORS, P.REPRIORITIZE_QUEUE,
            P.VIEW_OWN_WORK_ITEMS,
            P.SCAN_START_FINISH, P.LOG_ITEM_NOTES,
            P.SUBMIT_RECEIPTS, P.VIEW_OWN_RECEIPTS,
            P.MANAGE_SCHEDULE, P.VIEW_SCHEDULE,
        ],
        dashboard_cards=["shop_overview", "today_priorities", "crew_status", "my_queue"],
        sidebar_sections=["dashboard", "shop_floor", "schedule", "my_work"],
    ),

    RoleDef(
        id="accountant", name="Accountant", rank=7,
        description="Financial visibility and customer access. View/export only.",
        financial_access="full",
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_BOM, P.VIEW_BOM_PRICING, P.VIEW_SELL_PRICES, P.VIEW_VENDOR_COSTS, P.VIEW_MARGINS,
            P.VIEW_PROJECTS, P.VIEW_PROJECT_FINANCIALS,
            P.VIEW_INVENTORY, P.VIEW_INVENTORY_COSTS,
            P.VIEW_PO, P.VIEW_PO_PRICING,
            P.VIEW_FINANCIALS, P.VIEW_PROJECT_PNL, P.PROCESS_EXPENSES,
            P.VIEW_ALL_RECEIPTS,
            P.VIEW_CUSTOMER_INFO,
        ],
        dashboard_cards=["revenue_summary", "pending_expenses", "project_pnl", "vendor_bills"],
        sidebar_sections=["dashboard", "financial", "customers", "reports"],
    ),

    RoleDef(
        id="viewer", name="Viewer", rank=18,
        description="Dashboard read-only access. No operational capabilities.",
        permissions=[
            P.VIEW_DASHBOARD,
        ],
        dashboard_cards=["recent_activity"],
        sidebar_sections=["dashboard"],
    ),

    RoleDef(
        id="installer", name="Installer", rank=15,
        description="Field installation crew. Mobile-first field operations.",
        mobile_first=True,
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_PROJECTS,
            P.VIEW_FIELD_DRAWINGS,
            P.SUBMIT_DAILY_REPORT, P.UPLOAD_FIELD_PHOTOS,
            P.CREATE_PUNCH_LIST,
            P.VIEW_FIELD_REPORTS,
        ],
        dashboard_cards=["field_project_select", "field_documents", "field_daily_actions"],
        sidebar_sections=["dashboard", "field"],
    ),

    RoleDef(
        id="driver", name="Driver", rank=14,
        description="Shipping driver. View shipments and confirm delivery.",
        mobile_first=True,
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_SHIPPING, P.MARK_SHIPPED,
        ],
        dashboard_cards=["active_loads"],
        sidebar_sections=["dashboard", "shipping"],
    ),

    RoleDef(
        id="executive", name="Executive", rank=2,
        description="High-level dashboard and reports access. Strategic oversight.",
        financial_access="full",
        permissions=[
            P.VIEW_DASHBOARD,
            P.VIEW_PROJECTS, P.VIEW_PROJECT_FINANCIALS,
            P.VIEW_FINANCIALS, P.VIEW_PROJECT_PNL,
            P.VIEW_SCHEDULE,
        ],
        dashboard_cards=["business_summary", "all_projects_fin", "recent_activity"],
        sidebar_sections=["dashboard", "reports"],
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# LOOKUP TABLES
# ─────────────────────────────────────────────────────────────────────────────

# Role ID → RoleDef
ROLES: Dict[str, RoleDef] = {r.id: r for r in _ROLE_DEFS}

# Role ID → rank integer
ROLE_IDS: Dict[str, int] = {r.id: r.rank for r in _ROLE_DEFS}

# Ordered list of role IDs (by rank)
ROLE_ORDER: List[str] = [r.id for r in _ROLE_DEFS]


def get_role(role_id: str) -> Optional[RoleDef]:
    """Get role definition by ID. Returns None if not found."""
    return ROLES.get(role_id)


def get_role_permissions(role_id: str) -> Set[str]:
    """Get set of permission strings for a role."""
    role = ROLES.get(role_id)
    if not role:
        return set()
    return set(role.permissions)


def get_role_cards(role_id: str) -> List[DashboardCard]:
    """Get dashboard card objects for a role."""
    role = ROLES.get(role_id)
    if not role:
        return []
    return [CARDS[cid] for cid in role.dashboard_cards if cid in CARDS]


def get_role_sidebar(role_id: str) -> List[dict]:
    """Get sidebar section definitions for a role."""
    role = ROLES.get(role_id)
    if not role:
        return []
    return [_SIDEBAR_MAP[sid] for sid in role.sidebar_sections if sid in _SIDEBAR_MAP]


def list_all_roles() -> List[dict]:
    """Return summary list of all roles (for admin UI)."""
    return [
        {
            "id": r.id,
            "name": r.name,
            "rank": r.rank,
            "description": r.description,
            "financial_access": r.financial_access,
            "can_delete": r.can_delete,
            "can_manage_users": r.can_manage_users,
            "mobile_first": r.mobile_first,
            "permission_count": len(r.permissions),
        }
        for r in _ROLE_DEFS
    ]
