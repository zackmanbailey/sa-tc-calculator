"""
TitanForge RBAC — Middleware & Handler Mixin
Drop-in replacement for the old BaseHandler auth system.

Usage in tf_handlers.py:
    class MyHandler(AuthMixin, tornado.web.RequestHandler):
        def get(self):
            if not self.perm.can("view_shop_drawings"):
                return self.redirect("/dashboard")
            ...

    class AdminOnlyHandler(AuthMixin, tornado.web.RequestHandler):
        @require_permission("manage_users")
        def get(self):
            ...

    class ShopHandler(AuthMixin, tornado.web.RequestHandler):
        @require_any_role("shop_foreman", "god_mode", "admin")
        def post(self):
            ...

Reference: RULES.md §4 (Permission Check Pattern), §13 (Auth & Security)
"""

from __future__ import annotations
import functools
from typing import Optional, List

import tornado.web
from tornado.escape import json_encode

from auth.roles import P, ROLES
from auth.permissions import PermissionSet, merge_permissions, build_template_context
from auth.users import (
    load_users, get_user, get_user_roles,
    verify_password, record_login, check_lockout,
    ensure_users_file,
)


# Module-level flag — set by app.py at startup
AUTH_ENABLED = False


class AuthMixin:
    """
    Mixin for Tornado RequestHandlers that provides the new RBAC system.

    Replaces the old BaseHandler. Add this as a mixin to any handler class.

    Provides:
        self.current_username  — str or "local"
        self.current_user_data — full user dict or None
        self.user_roles        — list of role IDs
        self.perm              — PermissionSet (merged from all roles)
        self.template_ctx      — dict ready for template rendering
    """

    # Override in subclass to auto-check permission in prepare()
    required_permission: Optional[str] = None
    required_roles: Optional[List[str]] = None

    # ── Cached properties (computed once per request) ────────────────────

    _cached_user_data = None
    _cached_perm = None

    @property
    def current_username(self) -> str:
        """Get current authenticated username."""
        if not AUTH_ENABLED:
            return "local"
        cookie = self.get_secure_cookie("sa_user")
        if cookie:
            return cookie.decode("utf-8")
        return ""

    @property
    def current_user_data(self) -> Optional[dict]:
        """Get full user record for the current user."""
        if self._cached_user_data is not None:
            return self._cached_user_data

        username = self.current_username
        if not username or username == "local":
            # Dev mode: return synthetic God Mode user
            self._cached_user_data = {
                "username": "local",
                "display_name": "Admin (Dev)",
                "roles": ["god_mode"],
                "active": True,
            }
            return self._cached_user_data

        self._cached_user_data = get_user(username)
        return self._cached_user_data

    @property
    def user_roles(self) -> List[str]:
        """Get current user's role list."""
        if not AUTH_ENABLED:
            return ["god_mode"]
        username = self.current_username
        if not username:
            return []
        return get_user_roles(username)

    @property
    def perm(self) -> PermissionSet:
        """Get merged PermissionSet for current user."""
        if self._cached_perm is not None:
            return self._cached_perm
        self._cached_perm = merge_permissions(self.user_roles)
        return self._cached_perm

    @property
    def template_ctx(self) -> dict:
        """Build template context with all permission flags."""
        return build_template_context(self.user_roles)

    # ── Tornado overrides ────────────────────────────────────────────────

    def get_current_user(self):
        """Tornado's built-in current_user property. Returns username string."""
        return self.current_username or None

    def prepare(self):
        """
        Runs before every request. Checks:
        1. Auth enabled? → Must be logged in
        2. User active? → Deactivated users can't access
        3. required_permission set? → Check it
        4. required_roles set? → Check role membership
        """
        if not AUTH_ENABLED:
            return

        path = self.request.path

        # Public paths that don't require auth
        if path.startswith("/auth/") or path.startswith("/static/"):
            return

        username = self.current_username
        if not username:
            if self.request.method == "GET":
                self.redirect("/auth/login")
            else:
                self.set_status(401)
                self.write(json_encode({"error": "Not authenticated"}))
            raise tornado.web.Finish()

        # Check user is active
        user = self.current_user_data
        if user and not user.get("active", True):
            self.clear_cookie("sa_user")
            self.redirect("/auth/login")
            raise tornado.web.Finish()

        # Auto-check required_permission if set on handler class
        if self.required_permission is not None:
            if not self.perm.can(self.required_permission):
                self._deny_access()

        # Auto-check required_roles if set on handler class
        if self.required_roles is not None:
            if not self.perm.has_any_role(*self.required_roles):
                self._deny_access()

    def _deny_access(self):
        """
        Deny access: redirect GET to dashboard, return 403 JSON for API calls.
        Per RULES.md: unauthorized URLs redirect to dashboard, not a 403 page.
        """
        if self.request.method == "GET" and not self.request.path.startswith("/api/"):
            self.redirect("/dashboard")
        else:
            self.set_status(403)
            self.write(json_encode({"error": "Insufficient permissions"}))
        raise tornado.web.Finish()

    # ── Helper methods for handlers ──────────────────────────────────────

    def get_display_name(self) -> str:
        """Get current user's display name."""
        user = self.current_user_data
        if user:
            return user.get("display_name", self.current_username)
        return self.current_username or "Guest"

    def get_user_role(self) -> str:
        """
        LEGACY: Returns primary role as string.
        New code should use self.user_roles or self.perm instead.
        """
        roles = self.user_roles
        return roles[0] if roles else "laborer"

    def check_permission(self, permission: str) -> bool:
        """
        LEGACY: Check a single permission.
        New code should use self.perm.can(permission) instead.
        """
        return self.perm.can(permission)

    def render_with_nav(self, html: str, active_page: str = "",
                        job_code: str = ""):
        """Render HTML with the unified sidebar navigation injected."""
        from templates.shared_nav import inject_nav

        display = self.get_display_name()
        role = self.get_user_role()

        result = inject_nav(html, active_page=active_page, job_code=job_code,
                            user_name=display, user_role=role,
                            user_roles=self.user_roles)
        self.set_header("Content-Type", "text/html")
        self.write(result)


# ─────────────────────────────────────────────────────────────────────────────
# DECORATORS
# ─────────────────────────────────────────────────────────────────────────────

def require_permission(permission: str):
    """
    Decorator for handler methods. Checks permission before execution.

    Usage:
        @require_permission("manage_work_orders")
        def post(self):
            ...
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if AUTH_ENABLED and not self.perm.can(permission):
                self._deny_access()
                return
            return method(self, *args, **kwargs)
        return wrapper
    return decorator


def require_any_role(*role_ids: str):
    """
    Decorator for handler methods. Checks that user has at least one of the roles.

    Usage:
        @require_any_role("god_mode", "admin", "shop_foreman")
        def post(self):
            ...
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if AUTH_ENABLED and not self.perm.has_any_role(*role_ids):
                self._deny_access()
                return
            return method(self, *args, **kwargs)
        return wrapper
    return decorator


def require_financial_access(method):
    """
    Decorator that requires any level of financial access.

    Usage:
        @require_financial_access
        def get(self):
            ...
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if AUTH_ENABLED and not self.perm.has_financial_access():
            self._deny_access()
            return
        return method(self, *args, **kwargs)
    return wrapper


def require_delete_capability(method):
    """
    Decorator that requires delete permission (God Mode only).

    Usage:
        @require_delete_capability
        def delete(self):
            ...
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if AUTH_ENABLED and not self.perm.can_delete:
            self._deny_access()
            return
        return method(self, *args, **kwargs)
    return wrapper
