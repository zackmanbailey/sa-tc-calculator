"""
TitanForge RBAC — Role-Based Access Control System
18 roles, multi-role merging, financial data isolation, permission middleware.
"""

from auth.roles import ROLES, ROLE_IDS, PERMISSIONS, get_role, get_role_permissions
from auth.permissions import PermissionSet, merge_permissions, can, has_financial_access
from auth.users import (
    load_users, save_users, get_user, create_user, update_user,
    deactivate_user, assign_roles, remove_roles, verify_password, hash_password,
    ensure_users_file, record_login, check_lockout,
)
from auth.middleware import AuthMixin, require_permission, require_any_role

__all__ = [
    # Roles
    "ROLES", "ROLE_IDS", "PERMISSIONS", "get_role", "get_role_permissions",
    # Permissions
    "PermissionSet", "merge_permissions", "can", "has_financial_access",
    # Users
    "load_users", "save_users", "get_user", "create_user", "update_user",
    "deactivate_user", "assign_roles", "remove_roles", "verify_password",
    "hash_password", "ensure_users_file", "record_login", "check_lockout",
    # Middleware
    "AuthMixin", "require_permission", "require_any_role",
]
