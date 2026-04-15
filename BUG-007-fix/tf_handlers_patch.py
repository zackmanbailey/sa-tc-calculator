"""
BUG-007 FIX — New handler classes to add to tf_handlers.py
==========================================================

INSTRUCTIONS:
1. Add these imports near the top of tf_handlers.py where work_orders imports are:

   from shop_drawings.work_orders import (
       change_work_order_status, get_valid_transitions, can_transition,
       get_notifications, mark_notification_read, get_unread_count,
       STATUS_LABELS, VALID_STATUSES
   )

2. Add these handler classes AFTER the existing WorkOrderHoldHandler class (~line 4689)

3. Add these routes to the get_routes() function at the bottom of tf_handlers.py:

   (r"/api/work-orders/status-change", WorkOrderStatusChangeHandler),
   (r"/api/work-orders/transitions", WorkOrderTransitionsHandler),
   (r"/api/notifications", NotificationsHandler),
   (r"/api/notifications/read", NotificationReadHandler),
   (r"/api/notifications/count", NotificationCountHandler),

"""

# ─────────────────────────────────────────────────────────────────
# PASTE THESE CLASSES INTO tf_handlers.py AFTER WorkOrderHoldHandler
# ─────────────────────────────────────────────────────────────────


class WorkOrderStatusChangeHandler(BaseHandler):
    """POST /api/work-orders/status-change — Unified status change with rollback support.

    BUG-007 FIX: This replaces the need for separate approve/hold endpoints
    by providing a single endpoint that validates transitions, checks roles,
    supports rollback, and fires notifications.

    Body: { job_code, wo_id, new_status, notes? }
    """
    required_roles = ["admin", "estimator", "shop", "qc"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            wo_id = body.get("wo_id", "").strip()
            new_status = body.get("new_status", "").strip()
            notes = body.get("notes", "").strip()

            if not job_code or not wo_id or not new_status:
                self.write(json_encode({
                    "ok": False,
                    "error": "Missing job_code, wo_id, or new_status"
                }))
                return

            changed_by = body.get("changed_by", self.get_current_user() or "system")

            # Determine user role from session/cookie
            user_role = self._get_user_role()

            result = change_work_order_status(
                SHOP_DRAWINGS_DIR, job_code, wo_id,
                new_status=new_status,
                changed_by=changed_by,
                user_role=user_role,
                notes=notes,
            )

            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))

        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({
                "ok": False, "error": str(e),
                "trace": traceback.format_exc()
            }))

    def _get_user_role(self):
        """Extract user role from session. Falls back to 'admin' if auth is disabled."""
        try:
            user = self.get_current_user()
            if user and hasattr(self, 'get_user_role'):
                return self.get_user_role()
            # If no auth system, check cookie or default
            role_cookie = self.get_cookie("tf_role", "admin")
            return role_cookie
        except Exception:
            return "admin"


class WorkOrderTransitionsHandler(BaseHandler):
    """GET /api/work-orders/transitions?status=XXX — Get valid next statuses.

    BUG-007 FIX: Returns both forward and rollback transitions for a given status.
    """
    required_roles = ["admin", "estimator", "shop", "qc"]

    def get(self):
        try:
            current_status = self.get_query_argument("status", "").strip()
            if not current_status:
                self.write(json_encode({
                    "ok": False, "error": "Missing 'status' parameter"
                }))
                return

            transitions = get_valid_transitions(current_status, include_rollback=True)
            forward = get_valid_transitions(current_status, include_rollback=False)
            rollback = [t for t in transitions if t not in forward]

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "current_status": current_status,
                "current_label": STATUS_LABELS.get(current_status, current_status),
                "forward": [{"status": s, "label": STATUS_LABELS.get(s, s)} for s in forward],
                "rollback": [{"status": s, "label": STATUS_LABELS.get(s, s)} for s in rollback],
                "all": [{"status": s, "label": STATUS_LABELS.get(s, s)} for s in transitions],
            }))

        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class NotificationsHandler(BaseHandler):
    """GET /api/notifications — Get notifications for the current user/role.

    BUG-007 FIX: Notification system for status changes.
    Query params: role, limit, unread_only, user
    """
    required_roles = ["admin", "estimator", "shop", "qc"]

    def get(self):
        try:
            role = self.get_query_argument("role", None)
            limit = int(self.get_query_argument("limit", "50"))
            unread_only = self.get_query_argument("unread_only", "false") == "true"
            user = self.get_query_argument("user", self.get_current_user() or "")

            notifications = get_notifications(
                role=role, limit=limit,
                unread_only=unread_only, user=user
            )

            unread = get_unread_count(role=role, user=user)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "notifications": notifications,
                "unread_count": unread,
            }))

        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class NotificationReadHandler(BaseHandler):
    """POST /api/notifications/read — Mark a notification as read.

    Body: { notif_id }
    """
    required_roles = ["admin", "estimator", "shop", "qc"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            notif_id = body.get("notif_id", "").strip()
            user = body.get("user", self.get_current_user() or "system")

            if not notif_id:
                self.write(json_encode({"ok": False, "error": "Missing notif_id"}))
                return

            success = mark_notification_read(notif_id, user)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": success}))

        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class NotificationCountHandler(BaseHandler):
    """GET /api/notifications/count — Get unread notification count.

    Query params: role, user
    """
    required_roles = ["admin", "estimator", "shop", "qc"]

    def get(self):
        try:
            role = self.get_query_argument("role", None)
            user = self.get_query_argument("user", self.get_current_user() or "")
            count = get_unread_count(role=role, user=user)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "unread_count": count}))

        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))
