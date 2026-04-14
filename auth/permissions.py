"""
TitanForge RBAC — Permission Engine
Multi-role merging, financial data isolation, permission checking.

Reference: RULES.md §2.2 (Multi-Role Rules)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional

from auth.roles import (
    ROLES, CARDS, RoleDef, DashboardCard,
    get_role, get_role_permissions, get_role_cards, get_role_sidebar,
    _SIDEBAR_MAP,
)


# ─────────────────────────────────────────────────────────────────────────────
# FINANCIAL ACCESS LEVELS (ordered by visibility)
# ─────────────────────────────────────────────────────────────────────────────

FINANCIAL_LEVELS = {
    "full":          5,   # God, Admin, PM, Accounting
    "quoting":       4,   # Estimator — BOM pricing, sell prices
    "vendor":        3,   # Purchasing — vendor costs only
    "totals_only":   2,   # Sales — quote totals, no line items
    "own_receipts":  1,   # Shop Foreman — own consumable submissions
    "own_expenses":  1,   # Field Crew — own expense submissions
    "none":          0,   # No financial visibility
}


# ─────────────────────────────────────────────────────────────────────────────
# PERMISSION SET — the merged result for a multi-role user
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PermissionSet:
    """
    Merged permission set for a user with one or more roles.

    Access is ADDITIVE (union of all role permissions).
    Financial visibility = highest level across all roles.
    Delete capability = only if explicitly granted by at least one role.
    User management = only if explicitly granted by at least one role.
    """
    roles: List[str] = field(default_factory=list)
    permissions: Set[str] = field(default_factory=set)
    financial_level: str = "none"
    can_delete: bool = False
    can_manage_users: bool = False
    mobile_first: bool = False
    dashboard_card_ids: List[str] = field(default_factory=list)
    sidebar_section_ids: List[str] = field(default_factory=list)

    # ── Permission Checks ────────────────────────────────────────────────

    def can(self, permission: str) -> bool:
        """Check if the user has a specific permission."""
        return permission in self.permissions

    def has_any(self, *permissions: str) -> bool:
        """Check if the user has ANY of the given permissions."""
        return bool(self.permissions & set(permissions))

    def has_all(self, *permissions: str) -> bool:
        """Check if the user has ALL of the given permissions."""
        return set(permissions).issubset(self.permissions)

    def has_role(self, role_id: str) -> bool:
        """Check if user has a specific role."""
        return role_id in self.roles

    def has_any_role(self, *role_ids: str) -> bool:
        """Check if user has any of the given roles."""
        return bool(set(self.roles) & set(role_ids))

    # ── Financial Access ─────────────────────────────────────────────────

    def has_financial_access(self) -> bool:
        """True if user can see ANY financial data (level > 0)."""
        return FINANCIAL_LEVELS.get(self.financial_level, 0) > 0

    def has_full_financial_access(self) -> bool:
        """True if user has full financial visibility."""
        return self.financial_level == "full"

    def can_see_bom_pricing(self) -> bool:
        """True if user can see dollar amounts on BOM line items."""
        return FINANCIAL_LEVELS.get(self.financial_level, 0) >= FINANCIAL_LEVELS["quoting"]

    def can_see_vendor_costs(self) -> bool:
        """True if user can see vendor/purchase costs."""
        return FINANCIAL_LEVELS.get(self.financial_level, 0) >= FINANCIAL_LEVELS["vendor"]

    def can_see_margins(self) -> bool:
        """True if user can see margin/markup data."""
        return self.financial_level == "full" or self.financial_level == "quoting"

    def can_see_quote_totals(self) -> bool:
        """True if user can see at least quote total amounts."""
        return FINANCIAL_LEVELS.get(self.financial_level, 0) >= FINANCIAL_LEVELS["totals_only"]

    # ── Dashboard ────────────────────────────────────────────────────────

    def get_dashboard_cards(self) -> List[DashboardCard]:
        """
        Get the merged, deduplicated, ordered list of dashboard cards.
        Cards requiring financial access are excluded if user lacks it.
        """
        seen = set()
        cards = []
        for card_id in self.dashboard_card_ids:
            if card_id in seen:
                continue
            card = CARDS.get(card_id)
            if not card:
                continue
            # Skip financial cards if user has no financial access
            if card.requires_financial and not self.has_financial_access():
                continue
            seen.add(card_id)
            cards.append(card)

        # Sort by group then priority
        cards.sort(key=lambda c: (c.group, c.priority))
        return cards

    def get_dashboard_card_groups(self) -> Dict[str, List[DashboardCard]]:
        """Get cards grouped by their group header."""
        groups: Dict[str, List[DashboardCard]] = {}
        for card in self.get_dashboard_cards():
            groups.setdefault(card.group, []).append(card)
        return groups

    # ── Sidebar ──────────────────────────────────────────────────────────

    def get_sidebar(self) -> List[dict]:
        """Get the merged, ordered sidebar sections."""
        seen = set()
        sections = []
        for sid in self.sidebar_section_ids:
            if sid in seen:
                continue
            section = _SIDEBAR_MAP.get(sid)
            if not section:
                continue
            # Skip financial sidebar if no financial access
            if sid == "financial" and not self.has_financial_access():
                continue
            # Skip admin sidebar unless user can manage users
            if sid == "admin" and not self.can_manage_users:
                continue
            seen.add(sid)
            sections.append(section)
        return sections

    # ── Serialization ────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Serialize for API responses or template context."""
        return {
            "roles": self.roles,
            "permissions": sorted(self.permissions),
            "financial_level": self.financial_level,
            "can_delete": self.can_delete,
            "can_manage_users": self.can_manage_users,
            "mobile_first": self.mobile_first,
        }


# ─────────────────────────────────────────────────────────────────────────────
# MERGE FUNCTION — the core of multi-role support
# ─────────────────────────────────────────────────────────────────────────────

def merge_permissions(role_ids: List[str]) -> PermissionSet:
    """
    Merge permissions from multiple roles into a single PermissionSet.

    Rules (from RULES.md §2.2):
    - Permissions are ADDITIVE (union of all roles)
    - Financial visibility = highest level across roles
    - Delete capability requires explicit role grant (not inherited)
    - User management requires explicit role grant (not inherited)
    - Dashboard cards = union of all role cards (deduplicated)
    - Sidebar sections = union of all role sidebars (deduplicated)
    - Mobile-first = True only if ALL roles are mobile-first (conservative)
    """
    ps = PermissionSet()
    ps.roles = list(role_ids)

    if not role_ids:
        return ps

    all_perms: Set[str] = set()
    max_fin_level = 0
    all_card_ids: List[str] = []
    all_sidebar_ids: List[str] = []
    all_mobile = True

    for rid in role_ids:
        role = get_role(rid)
        if not role:
            continue

        # Union of permissions
        all_perms.update(role.permissions)

        # Highest financial access
        fin = FINANCIAL_LEVELS.get(role.financial_access, 0)
        if fin > max_fin_level:
            max_fin_level = fin
            ps.financial_level = role.financial_access

        # Destructive: explicit grant only
        if role.can_delete:
            ps.can_delete = True
        if role.can_manage_users:
            ps.can_manage_users = True

        # Collect cards and sidebar (order preserved, dupes removed later)
        all_card_ids.extend(role.dashboard_cards)
        all_sidebar_ids.extend(role.sidebar_sections)

        if not role.mobile_first:
            all_mobile = False

    ps.permissions = all_perms
    ps.mobile_first = all_mobile

    # Deduplicate cards while preserving first-seen order
    seen_cards: Set[str] = set()
    deduped_cards: List[str] = []
    for cid in all_card_ids:
        if cid not in seen_cards:
            seen_cards.add(cid)
            deduped_cards.append(cid)
    ps.dashboard_card_ids = deduped_cards

    # Deduplicate sidebar while preserving order
    seen_sb: Set[str] = set()
    deduped_sb: List[str] = []
    for sid in all_sidebar_ids:
        if sid not in seen_sb:
            seen_sb.add(sid)
            deduped_sb.append(sid)
    ps.sidebar_section_ids = deduped_sb

    return ps


# ─────────────────────────────────────────────────────────────────────────────
# CONVENIENCE FUNCTIONS (used by handlers)
# ─────────────────────────────────────────────────────────────────────────────

def can(role_ids: List[str], permission: str) -> bool:
    """Quick check: do these roles grant this permission?"""
    for rid in role_ids:
        if permission in get_role_permissions(rid):
            return True
    return False


def has_financial_access(role_ids: List[str]) -> bool:
    """Quick check: do any of these roles grant financial access?"""
    for rid in role_ids:
        role = get_role(rid)
        if role and FINANCIAL_LEVELS.get(role.financial_access, 0) > 0:
            return True
    return False


def build_template_context(role_ids: List[str]) -> dict:
    """
    Build the complete template context for rendering pages.
    Returns a dict with all permission flags a template might need.
    """
    ps = merge_permissions(role_ids)
    return {
        "perm": ps,
        "roles": ps.roles,
        "can": ps.can,           # Template can call: ctx['can']('view_shop_drawings')
        "has_role": ps.has_role,
        "show_financial": ps.has_financial_access(),
        "show_bom_pricing": ps.can_see_bom_pricing(),
        "show_vendor_costs": ps.can_see_vendor_costs(),
        "show_margins": ps.can_see_margins(),
        "can_delete": ps.can_delete,
        "can_manage_users": ps.can_manage_users,
        "mobile_first": ps.mobile_first,
        "dashboard_cards": ps.get_dashboard_cards(),
        "dashboard_groups": ps.get_dashboard_card_groups(),
        "sidebar": ps.get_sidebar(),
    }
