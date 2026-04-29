"""
TitanForge Email Notification System
Lightweight email notifications using smtplib, designed for Railway deployment.
Uses Tornado IOLoop for non-blocking sends.
"""

import os
import json
import smtplib
import logging
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import deque

import tornado.ioloop

logger = logging.getLogger("titanforge.email")

# ── SMTP Configuration (from environment variables) ─────────────────────────

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
SMTP_FROM = os.environ.get("SMTP_FROM", "") or SMTP_USER
NOTIFICATION_ENABLED = os.environ.get("NOTIFICATION_ENABLED", "false").lower() in ("1", "true", "yes")

# ── Data directory (matches tf_handlers.py) ──────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("TITANFORGE_DATA_DIR", os.path.join(BASE_DIR, "data"))
NOTIFICATION_SETTINGS_PATH = os.path.join(DATA_DIR, "notifications", "email_settings.json")


# ── Notification Types ───────────────────────────────────────────────────────

NOTIFICATION_TYPES = {
    "qc_hold": {
        "label": "QC Hold",
        "description": "QC hold placed on a work order",
        "default_roles": ["admin", "qc_manager", "estimator"],
        "icon": "&#9888;",  # warning sign
        "color": "#E74C3C",
    },
    "ncr_created": {
        "label": "NCR Created",
        "description": "New Non-Conformance Report created",
        "default_roles": ["admin", "qc_manager", "estimator"],
        "icon": "&#10060;",  # cross mark
        "color": "#C0392B",
    },
    "inventory_alert": {
        "label": "Inventory Alert",
        "description": "Inventory below minimum threshold",
        "default_roles": ["admin", "estimator", "purchasing"],
        "icon": "&#128230;",  # package
        "color": "#F39C12",
    },
    "project_stage_change": {
        "label": "Project Stage Change",
        "description": "Project moves to a new stage",
        "default_roles": ["admin", "estimator"],
        "icon": "&#128204;",  # pushpin
        "color": "#3498DB",
    },
    "work_order_complete": {
        "label": "Work Order Complete",
        "description": "All items in a work order completed",
        "default_roles": ["admin", "estimator", "shop"],
        "icon": "&#9989;",  # check mark
        "color": "#27AE60",
    },
    "shipping_ready": {
        "label": "Shipping Ready",
        "description": "Job ready to ship",
        "default_roles": ["admin", "estimator", "shipping"],
        "icon": "&#128666;",  # delivery truck
        "color": "#2980B9",
    },
    "wo_status_change": {
        "label": "WO Status Change",
        "description": "Work order status changed",
        "default_roles": ["admin", "estimator", "shop"],
        "icon": "&#128260;",  # arrows
        "color": "#8E44AD",
    },
    "qc_critical_fail": {
        "label": "QC Critical Failure",
        "description": "Critical item failed QC inspection",
        "default_roles": ["admin", "qc_manager", "estimator"],
        "icon": "&#128680;",  # rotating light
        "color": "#E74C3C",
    },
    "wo_revision": {
        "label": "WO Revision",
        "description": "Work order revised — change order applied",
        "default_roles": ["admin", "estimator", "shop"],
        "icon": "&#128221;",  # memo
        "color": "#F39C12",
    },
}


# ── Email Queue ──────────────────────────────────────────────────────────────

_email_queue = deque(maxlen=500)
_processing = False


# ── Settings Management ──────────────────────────────────────────────────────

def _default_settings():
    """Return default notification settings."""
    settings = {
        "enabled": NOTIFICATION_ENABLED,
        "recipients": {},
        "type_settings": {},
    }
    for ntype, info in NOTIFICATION_TYPES.items():
        settings["type_settings"][ntype] = {
            "enabled": True,
            "roles": info["default_roles"][:],
        }
    return settings


def load_notification_settings():
    """Load notification settings from disk."""
    if os.path.isfile(NOTIFICATION_SETTINGS_PATH):
        try:
            with open(NOTIFICATION_SETTINGS_PATH) as f:
                data = json.load(f)
            # Merge with defaults for any new notification types
            defaults = _default_settings()
            for ntype in defaults["type_settings"]:
                if ntype not in data.get("type_settings", {}):
                    data.setdefault("type_settings", {})[ntype] = defaults["type_settings"][ntype]
            return data
        except Exception:
            logger.warning("Failed to load notification settings, using defaults")
    return _default_settings()


def save_notification_settings(settings):
    """Save notification settings to disk."""
    os.makedirs(os.path.dirname(NOTIFICATION_SETTINGS_PATH), exist_ok=True)
    with open(NOTIFICATION_SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)


# ── Recipient Lookup ─────────────────────────────────────────────────────────

def get_notification_recipients(notification_type, project_code=None):
    """Look up who should receive a notification based on type and role.

    Returns a list of email addresses.
    """
    settings = load_notification_settings()

    # Check if this notification type is enabled
    type_cfg = settings.get("type_settings", {}).get(notification_type, {})
    if not type_cfg.get("enabled", True):
        return []

    # Get explicit recipients for this notification type
    explicit = settings.get("recipients", {}).get(notification_type, [])
    if explicit:
        return explicit

    # Fall back to global recipients list
    global_recipients = settings.get("recipients", {}).get("_global", [])
    if global_recipients:
        return global_recipients

    # Look up users by role from users.json
    recipients = []
    allowed_roles = type_cfg.get("roles", [])
    users_path = os.path.join(DATA_DIR, "users.json")
    if os.path.isfile(users_path):
        try:
            with open(users_path) as f:
                users = json.load(f)
            for username, udata in users.items():
                user_role = udata.get("role", "")
                user_roles = udata.get("roles", [user_role])
                user_email = udata.get("email", "")
                if user_email and any(r in allowed_roles for r in user_roles):
                    recipients.append(user_email)
        except Exception:
            logger.warning("Failed to load users for notification recipients")

    return recipients


# ── HTML Email Templates ─────────────────────────────────────────────────────

def _base_email_html(title, icon, color, body_html):
    """Wrap notification content in a branded HTML email template."""
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#1a1a2e;font-family:Arial,Helvetica,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#1a1a2e;padding:20px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#16213e;border-radius:8px;overflow:hidden;border:1px solid #0f3460;">

<!-- Header -->
<tr><td style="background:linear-gradient(135deg,#0f3460,#533483);padding:24px 32px;">
  <table width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td style="font-size:28px;font-weight:700;color:#e94560;font-family:Arial,sans-serif;">
      TitanForge
    </td>
    <td align="right" style="font-size:12px;color:#8899aa;font-family:Arial,sans-serif;">
      {datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")}
    </td>
  </tr>
  </table>
</td></tr>

<!-- Alert Banner -->
<tr><td style="background:{color};padding:16px 32px;">
  <span style="font-size:18px;color:#fff;font-weight:700;font-family:Arial,sans-serif;">
    {icon} {title}
  </span>
</td></tr>

<!-- Body -->
<tr><td style="padding:24px 32px;color:#c8d6e5;font-size:14px;line-height:1.6;font-family:Arial,sans-serif;">
  {body_html}
</td></tr>

<!-- Footer -->
<tr><td style="padding:16px 32px;border-top:1px solid #0f3460;font-size:11px;color:#576574;font-family:Arial,sans-serif;">
  This is an automated notification from TitanForge. Do not reply to this email.
  <br>Titan Carports &mdash; Steel Fabrication Management System
</td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""


def _template_qc_hold(data):
    """Generate QC hold email content."""
    job_code = data.get("job_code", "Unknown")
    wo_id = data.get("wo_id", "Unknown")
    reason = data.get("reason", "No reason provided")
    held_by = data.get("held_by", "Unknown")
    body = f"""
    <p>A <strong>QC Hold</strong> has been placed on a work order.</p>
    <table style="width:100%;border-collapse:collapse;margin:12px 0;">
      <tr><td style="padding:8px 12px;color:#8899aa;width:140px;">Job Code</td>
          <td style="padding:8px 12px;color:#fff;font-weight:600;">{job_code}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Work Order</td>
          <td style="padding:8px 12px;color:#fff;font-weight:600;">{wo_id}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Held By</td>
          <td style="padding:8px 12px;color:#fff;">{held_by}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Reason</td>
          <td style="padding:8px 12px;color:#fff;">{reason}</td></tr>
    </table>
    <p style="color:#e94560;font-weight:600;">Action required: Review the hold and determine next steps.</p>
    """
    return _base_email_html("QC Hold Placed", "&#9888;", "#E74C3C", body)


def _template_ncr_created(data):
    """Generate NCR created email content."""
    job_code = data.get("job_code", "Unknown")
    ncr_id = data.get("ncr_id", "Unknown")
    severity = data.get("severity", "minor").upper()
    title = data.get("title", "No title")
    description = data.get("description", "")
    reported_by = data.get("reported_by", "Unknown")

    sev_color = {"MINOR": "#F39C12", "MAJOR": "#E74C3C", "CRITICAL": "#C0392B"}.get(severity, "#F39C12")
    body = f"""
    <p>A new <strong>Non-Conformance Report</strong> has been created.</p>
    <table style="width:100%;border-collapse:collapse;margin:12px 0;">
      <tr><td style="padding:8px 12px;color:#8899aa;width:140px;">NCR ID</td>
          <td style="padding:8px 12px;color:#fff;font-weight:600;">{ncr_id}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Job Code</td>
          <td style="padding:8px 12px;color:#fff;font-weight:600;">{job_code}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Severity</td>
          <td style="padding:8px 12px;color:{sev_color};font-weight:700;">{severity}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Title</td>
          <td style="padding:8px 12px;color:#fff;">{title}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Description</td>
          <td style="padding:8px 12px;color:#fff;">{description or 'N/A'}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Reported By</td>
          <td style="padding:8px 12px;color:#fff;">{reported_by}</td></tr>
    </table>
    """
    return _base_email_html("NCR Created", "&#10060;", "#C0392B", body)


def _template_inventory_alert(data):
    """Generate inventory alert email content."""
    coil_name = data.get("coil_name", "Unknown")
    coil_id = data.get("coil_id", "")
    available_lbs = data.get("available_lbs", 0)
    min_stock_lbs = data.get("min_stock_lbs", 0)
    alert_level = data.get("level", "warning").upper()

    level_color = "#E74C3C" if alert_level == "CRITICAL" else "#F39C12"
    body = f"""
    <p>An inventory threshold alert has been triggered.</p>
    <table style="width:100%;border-collapse:collapse;margin:12px 0;">
      <tr><td style="padding:8px 12px;color:#8899aa;width:140px;">Material</td>
          <td style="padding:8px 12px;color:#fff;font-weight:600;">{coil_name}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Coil ID</td>
          <td style="padding:8px 12px;color:#fff;">{coil_id}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Alert Level</td>
          <td style="padding:8px 12px;color:{level_color};font-weight:700;">{alert_level}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Available</td>
          <td style="padding:8px 12px;color:#fff;">{available_lbs:,.0f} lbs</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Minimum Stock</td>
          <td style="padding:8px 12px;color:#fff;">{min_stock_lbs:,.0f} lbs</td></tr>
    </table>
    <p style="color:{level_color};font-weight:600;">
      {'OUT OF STOCK - Immediate reorder required!' if available_lbs <= 0 else 'Stock is below minimum threshold. Consider reordering.'}
    </p>
    """
    return _base_email_html("Inventory Alert", "&#128230;", level_color, body)


def _template_project_stage_change(data):
    """Generate project stage change email content."""
    job_code = data.get("job_code", "Unknown")
    project_name = data.get("project_name", "")
    old_stage = data.get("old_stage", "N/A").replace("_", " ").title()
    new_stage = data.get("new_stage", "Unknown").replace("_", " ").title()
    changed_by = data.get("changed_by", "Unknown")
    body = f"""
    <p>A project has moved to a new stage.</p>
    <table style="width:100%;border-collapse:collapse;margin:12px 0;">
      <tr><td style="padding:8px 12px;color:#8899aa;width:140px;">Job Code</td>
          <td style="padding:8px 12px;color:#fff;font-weight:600;">{job_code}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Project</td>
          <td style="padding:8px 12px;color:#fff;">{project_name or job_code}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Previous Stage</td>
          <td style="padding:8px 12px;color:#8899aa;">{old_stage}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">New Stage</td>
          <td style="padding:8px 12px;color:#27AE60;font-weight:700;">{new_stage}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Changed By</td>
          <td style="padding:8px 12px;color:#fff;">{changed_by}</td></tr>
    </table>
    """
    return _base_email_html("Project Stage Change", "&#128204;", "#3498DB", body)


def _template_work_order_complete(data):
    """Generate work order complete email content."""
    job_code = data.get("job_code", "Unknown")
    wo_id = data.get("wo_id", "Unknown")
    total_items = data.get("total_items", 0)
    completed_by = data.get("completed_by", "Unknown")
    body = f"""
    <p>A work order has been <strong>completed</strong> &mdash; all items finished.</p>
    <table style="width:100%;border-collapse:collapse;margin:12px 0;">
      <tr><td style="padding:8px 12px;color:#8899aa;width:140px;">Job Code</td>
          <td style="padding:8px 12px;color:#fff;font-weight:600;">{job_code}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Work Order</td>
          <td style="padding:8px 12px;color:#fff;font-weight:600;">{wo_id}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Total Items</td>
          <td style="padding:8px 12px;color:#fff;">{total_items}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Completed By</td>
          <td style="padding:8px 12px;color:#fff;">{completed_by}</td></tr>
    </table>
    <p style="color:#27AE60;font-weight:600;">This work order is ready for the next step in the workflow.</p>
    """
    return _base_email_html("Work Order Complete", "&#9989;", "#27AE60", body)


def _template_shipping_ready(data):
    """Generate shipping ready email content."""
    job_code = data.get("job_code", "Unknown")
    load_id = data.get("load_id", "Unknown")
    item_count = data.get("item_count", 0)
    finalized_by = data.get("finalized_by", "Unknown")
    body = f"""
    <p>A load has been <strong>finalized</strong> and is ready to ship.</p>
    <table style="width:100%;border-collapse:collapse;margin:12px 0;">
      <tr><td style="padding:8px 12px;color:#8899aa;width:140px;">Job Code</td>
          <td style="padding:8px 12px;color:#fff;font-weight:600;">{job_code}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Load ID</td>
          <td style="padding:8px 12px;color:#fff;font-weight:600;">{load_id}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Items</td>
          <td style="padding:8px 12px;color:#fff;">{item_count}</td></tr>
      <tr><td style="padding:8px 12px;color:#8899aa;">Finalized By</td>
          <td style="padding:8px 12px;color:#fff;">{finalized_by}</td></tr>
    </table>
    <p style="color:#2980B9;font-weight:600;">Coordinate pickup/delivery scheduling.</p>
    """
    return _base_email_html("Shipping Ready", "&#128666;", "#2980B9", body)


# Template dispatcher
_TEMPLATES = {
    "qc_hold": _template_qc_hold,
    "ncr_created": _template_ncr_created,
    "inventory_alert": _template_inventory_alert,
    "project_stage_change": _template_project_stage_change,
    "work_order_complete": _template_work_order_complete,
    "shipping_ready": _template_shipping_ready,
}


# ── Core Send Functions ──────────────────────────────────────────────────────

def _send_email_sync(to_addrs, subject, html_body):
    """Send an email synchronously via SMTP. Called from the IOLoop callback."""
    if not SMTP_USER or not SMTP_PASS:
        logger.warning("SMTP credentials not configured, skipping email send")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM or SMTP_USER
        msg["To"] = ", ".join(to_addrs) if isinstance(to_addrs, list) else to_addrs

        # Plain text fallback
        plain = f"TitanForge Notification: {subject}\n\nPlease view this email in an HTML-capable client."
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM or SMTP_USER, to_addrs, msg.as_string())

        logger.info(f"Email sent: '{subject}' to {to_addrs}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email '{subject}': {e}")
        return False


def _process_queue():
    """Process the next item in the email queue."""
    global _processing
    if not _email_queue:
        _processing = False
        return

    _processing = True
    item = _email_queue.popleft()

    try:
        _send_email_sync(item["to"], item["subject"], item["html"])
    except Exception as e:
        logger.error(f"Queue processing error: {e}")

    # Schedule next item with a small delay to avoid hammering SMTP
    if _email_queue:
        try:
            ioloop = tornado.ioloop.IOLoop.current()
            ioloop.call_later(1.0, _process_queue)
        except Exception:
            _processing = False
    else:
        _processing = False


def _enqueue_email(to_addrs, subject, html_body):
    """Add an email to the async queue for non-blocking delivery."""
    _email_queue.append({
        "to": to_addrs if isinstance(to_addrs, list) else [to_addrs],
        "subject": subject,
        "html": html_body,
        "queued_at": datetime.datetime.now().isoformat(),
    })

    global _processing
    if not _processing:
        try:
            ioloop = tornado.ioloop.IOLoop.current()
            ioloop.call_later(0.1, _process_queue)
        except Exception:
            # IOLoop not running yet (startup), process synchronously
            _process_queue()


# ── Public API ───────────────────────────────────────────────────────────────

def send_notification(notification_type, recipients=None, context_data=None):
    """Format and send an email notification.

    Args:
        notification_type: One of the NOTIFICATION_TYPES keys.
        recipients: List of email addresses. If None, auto-lookup by role.
        context_data: Dict of data to populate the email template.
    """
    if not NOTIFICATION_ENABLED:
        logger.debug(f"Email notifications disabled, skipping {notification_type}")
        return

    if notification_type not in NOTIFICATION_TYPES:
        logger.warning(f"Unknown notification type: {notification_type}")
        return

    settings = load_notification_settings()
    type_cfg = settings.get("type_settings", {}).get(notification_type, {})
    if not type_cfg.get("enabled", True):
        logger.debug(f"Notification type '{notification_type}' is disabled in settings")
        return

    # Determine recipients
    if not recipients:
        recipients = get_notification_recipients(notification_type,
                                                  project_code=context_data.get("job_code") if context_data else None)
    if not recipients:
        logger.debug(f"No recipients for {notification_type}, skipping")
        return

    # Generate email content
    data = context_data or {}
    template_fn = _TEMPLATES.get(notification_type)
    if not template_fn:
        logger.warning(f"No email template for {notification_type}")
        return

    html_body = template_fn(data)
    type_info = NOTIFICATION_TYPES[notification_type]
    subject = f"[TitanForge] {type_info['label']}"

    # Add context to subject line
    job_code = data.get("job_code", "")
    if job_code:
        subject += f" - {job_code}"

    _enqueue_email(recipients, subject, html_body)
    logger.info(f"Queued {notification_type} notification to {len(recipients)} recipient(s)")


def send_test_email(to_addr):
    """Send a test email to verify SMTP configuration.

    Returns (success: bool, message: str).
    """
    if not SMTP_USER or not SMTP_PASS:
        return False, "SMTP credentials not configured. Set SMTP_USER and SMTP_PASS environment variables."

    body = _base_email_html(
        "Test Notification",
        "&#128276;",
        "#3498DB",
        """
        <p>This is a <strong>test notification</strong> from TitanForge.</p>
        <p>If you received this email, your SMTP configuration is working correctly.</p>
        <table style="width:100%;border-collapse:collapse;margin:12px 0;">
          <tr><td style="padding:8px 12px;color:#8899aa;width:140px;">SMTP Host</td>
              <td style="padding:8px 12px;color:#fff;">{host}</td></tr>
          <tr><td style="padding:8px 12px;color:#8899aa;">SMTP Port</td>
              <td style="padding:8px 12px;color:#fff;">{port}</td></tr>
          <tr><td style="padding:8px 12px;color:#8899aa;">From</td>
              <td style="padding:8px 12px;color:#fff;">{from_addr}</td></tr>
          <tr><td style="padding:8px 12px;color:#8899aa;">Timestamp</td>
              <td style="padding:8px 12px;color:#fff;">{ts}</td></tr>
        </table>
        """.format(
            host=SMTP_HOST,
            port=SMTP_PORT,
            from_addr=SMTP_FROM or SMTP_USER,
            ts=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
    )

    success = _send_email_sync([to_addr], "[TitanForge] Test Notification", body)
    if success:
        return True, f"Test email sent to {to_addr}"
    else:
        return False, "Failed to send test email. Check SMTP credentials and server logs."


def get_queue_status():
    """Return current queue status for monitoring."""
    return {
        "enabled": NOTIFICATION_ENABLED,
        "smtp_configured": bool(SMTP_USER and SMTP_PASS),
        "smtp_host": SMTP_HOST,
        "smtp_port": SMTP_PORT,
        "queue_size": len(_email_queue),
        "processing": _processing,
    }
