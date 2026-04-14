"""
TitanForge RBAC — User Data Model
JSON-based user storage with multi-role support, audit fields, lockout.

Reference: RULES.md §11 (Technical Architecture), §13 (Auth & Security)

User record schema:
{
  "user_id": "usr_abc123",
  "username": "brad",
  "display_name": "Brad Spence",
  "email": "brad@structuresamerica.com",
  "password_hash": "$2b$12$...",
  "roles": ["shop_foreman", "qc_inspector"],
  "active": true,
  "created_at": "2026-01-15T08:00:00Z",
  "last_login": "2026-04-14T07:30:00Z",
  "force_password_change": false,
  "failed_attempts": 0,
  "locked_until": null
}
"""

from __future__ import annotations
import os
import json
import datetime
import secrets
import hashlib
from typing import List, Dict, Optional

# ── Password hashing ────────────────────────────────────────────────────────
try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

from auth.roles import ROLES, ROLE_ORDER


# ─────────────────────────────────────────────────────────────────────────────
# FILE PATHS
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_PATH = os.path.join(DATA_DIR, "users.json")
AUDIT_PATH = os.path.join(DATA_DIR, "audit_log.json")
PENDING_PATH = os.path.join(DATA_DIR, "pending_users.json")

# Lockout config (RULES.md §13)
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
BCRYPT_COST = 12


# ─────────────────────────────────────────────────────────────────────────────
# PASSWORD UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash password using bcrypt (preferred) or SHA-256 fallback."""
    if HAS_BCRYPT:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(BCRYPT_COST)).decode()
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(stored_hash: str, password: str) -> bool:
    """Verify a password against its stored hash."""
    if HAS_BCRYPT and stored_hash.startswith("$2"):
        return bcrypt.checkpw(password.encode(), stored_hash.encode())
    return stored_hash == hashlib.sha256(password.encode()).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# USER STORAGE (JSON file-based)
# ─────────────────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


def _gen_user_id() -> str:
    return f"usr_{secrets.token_hex(6)}"


def load_users() -> Dict[str, dict]:
    """
    Load all users from JSON.
    Returns dict keyed by username for backward compatibility.
    New format also stores user_id inside each record.
    """
    if not os.path.isfile(USERS_PATH):
        ensure_users_file()
    with open(USERS_PATH, "r") as f:
        return json.load(f)


def save_users(data: Dict[str, dict]):
    """Save users dict to JSON."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(USERS_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_user(username: str) -> Optional[dict]:
    """Get a single user record by username. Returns None if not found."""
    users = load_users()
    return users.get(username)


def create_user(
    username: str,
    password: str,
    display_name: str,
    email: str = "",
    roles: Optional[List[str]] = None,
    force_password_change: bool = True,
    created_by: str = "system",
) -> dict:
    """
    Create a new user. Raises ValueError if username exists or roles invalid.
    """
    users = load_users()

    if username in users:
        raise ValueError(f"Username '{username}' already exists")

    # Validate roles
    if roles is None:
        roles = ["laborer"]  # Default to most restricted role
    for r in roles:
        if r not in ROLES:
            raise ValueError(f"Invalid role: '{r}'. Valid roles: {list(ROLES.keys())}")

    user_id = _gen_user_id()
    now = _now_iso()

    record = {
        "user_id": user_id,
        "username": username,
        "display_name": display_name,
        "email": email,
        "password_hash": hash_password(password),
        "roles": roles,
        "active": True,
        "created_at": now,
        "created_by": created_by,
        "last_login": None,
        "force_password_change": force_password_change,
        "failed_attempts": 0,
        "locked_until": None,
        # Legacy compatibility — first role as primary
        "role": roles[0] if roles else "laborer",
        "password": hash_password(password),  # Legacy field — same as password_hash
    }

    users[username] = record
    save_users(users)

    _audit_log("user_created", created_by, f"Created user '{username}' with roles {roles}")
    return record


def update_user(
    username: str,
    display_name: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    force_password_change: Optional[bool] = None,
    updated_by: str = "system",
) -> dict:
    """Update user profile fields. Returns updated record."""
    users = load_users()
    user = users.get(username)
    if not user:
        raise ValueError(f"User '{username}' not found")

    if display_name is not None:
        user["display_name"] = display_name
    if email is not None:
        user["email"] = email
    if password is not None:
        user["password_hash"] = hash_password(password)
        user["password"] = user["password_hash"]  # Legacy sync
    if force_password_change is not None:
        user["force_password_change"] = force_password_change

    users[username] = user
    save_users(users)
    _audit_log("user_updated", updated_by, f"Updated user '{username}'")
    return user


def deactivate_user(username: str, deactivated_by: str = "system") -> dict:
    """Deactivate (soft-delete) a user. They can't log in but record preserved."""
    users = load_users()
    user = users.get(username)
    if not user:
        raise ValueError(f"User '{username}' not found")

    user["active"] = False
    user["deactivated_at"] = _now_iso()
    user["deactivated_by"] = deactivated_by

    users[username] = user
    save_users(users)
    _audit_log("user_deactivated", deactivated_by, f"Deactivated user '{username}'")
    return user


def assign_roles(username: str, role_ids: List[str], assigned_by: str = "system") -> dict:
    """
    Set user's roles (replaces existing roles).
    Validates all role IDs. At least one role required.
    """
    if not role_ids:
        raise ValueError("At least one role is required")
    for r in role_ids:
        if r not in ROLES:
            raise ValueError(f"Invalid role: '{r}'")

    users = load_users()
    user = users.get(username)
    if not user:
        raise ValueError(f"User '{username}' not found")

    old_roles = user.get("roles", [user.get("role", "laborer")])
    user["roles"] = list(role_ids)
    user["role"] = role_ids[0]  # Legacy compatibility

    users[username] = user
    save_users(users)
    _audit_log("roles_changed", assigned_by,
               f"User '{username}': {old_roles} → {role_ids}")
    return user


def remove_roles(username: str, role_ids: List[str], removed_by: str = "system") -> dict:
    """Remove specific roles from a user. Must keep at least one role."""
    users = load_users()
    user = users.get(username)
    if not user:
        raise ValueError(f"User '{username}' not found")

    current = set(user.get("roles", [user.get("role", "laborer")]))
    remaining = current - set(role_ids)

    if not remaining:
        raise ValueError("Cannot remove all roles. User must have at least one role.")

    user["roles"] = list(remaining)
    user["role"] = list(remaining)[0]

    users[username] = user
    save_users(users)
    _audit_log("roles_removed", removed_by,
               f"User '{username}': removed {role_ids}, remaining {list(remaining)}")
    return user


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN / LOCKOUT
# ─────────────────────────────────────────────────────────────────────────────

def check_lockout(username: str) -> Optional[str]:
    """
    Check if user is locked out.
    Returns None if not locked, or ISO string of when lockout expires.
    """
    user = get_user(username)
    if not user:
        return None

    locked_until = user.get("locked_until")
    if not locked_until:
        return None

    now = datetime.datetime.utcnow()
    lock_time = datetime.datetime.fromisoformat(locked_until.rstrip("Z"))
    if now < lock_time:
        return locked_until
    return None


def record_login(username: str, success: bool, ip_address: str = ""):
    """
    Record a login attempt. On failure, increment counter.
    After MAX_FAILED_ATTEMPTS, lock the account for LOCKOUT_MINUTES.
    On success, reset counters and update last_login.
    """
    users = load_users()
    user = users.get(username)
    if not user:
        return

    if success:
        user["last_login"] = _now_iso()
        user["failed_attempts"] = 0
        user["locked_until"] = None
        _audit_log("login_success", username, f"IP: {ip_address}")
    else:
        attempts = user.get("failed_attempts", 0) + 1
        user["failed_attempts"] = attempts

        if attempts >= MAX_FAILED_ATTEMPTS:
            lock_until = (
                datetime.datetime.utcnow() +
                datetime.timedelta(minutes=LOCKOUT_MINUTES)
            )
            user["locked_until"] = lock_until.isoformat() + "Z"
            _audit_log("account_locked", username,
                       f"Locked after {attempts} failed attempts. IP: {ip_address}")
        else:
            _audit_log("login_failed", username,
                       f"Attempt {attempts}/{MAX_FAILED_ATTEMPTS}. IP: {ip_address}")

    users[username] = user
    save_users(users)


def get_user_roles(username: str) -> List[str]:
    """Get a user's role list. Handles legacy single-role format."""
    user = get_user(username)
    if not user:
        return []
    # Support both new multi-role and legacy single-role formats
    roles = user.get("roles")
    if roles and isinstance(roles, list):
        return roles
    # Legacy: single 'role' field
    legacy = user.get("role", "laborer")
    # Map old role names to new ones
    LEGACY_MAP = {
        "admin": "admin",
        "estimator": "estimator",
        "shop": "shop_foreman",
        "viewer": "laborer",
        "tc_limited": "customer",
    }
    return [LEGACY_MAP.get(legacy, legacy)]


# ─────────────────────────────────────────────────────────────────────────────
# DEFAULT USERS (created on first run)
# ─────────────────────────────────────────────────────────────────────────────

def ensure_users_file():
    """Create users.json with default users if it doesn't exist."""
    if os.path.isfile(USERS_PATH):
        return

    os.makedirs(DATA_DIR, exist_ok=True)
    now = _now_iso()

    users = {
        "zack": {
            "user_id": "usr_god001",
            "username": "zack",
            "display_name": "Zack Bailey",
            "email": "zack@titancarports.com",
            "password_hash": hash_password("titan2026"),
            "password": hash_password("titan2026"),
            "roles": ["god_mode"],
            "role": "god_mode",
            "active": True,
            "created_at": now,
            "created_by": "system",
            "last_login": None,
            "force_password_change": True,
            "failed_attempts": 0,
            "locked_until": None,
        },
        "admin": {
            "user_id": "usr_adm001",
            "username": "admin",
            "display_name": "Admin",
            "email": "admin@structuresamerica.com",
            "password_hash": hash_password("titan2026"),
            "password": hash_password("titan2026"),
            "roles": ["admin"],
            "role": "admin",
            "active": True,
            "created_at": now,
            "created_by": "system",
            "last_login": None,
            "force_password_change": True,
            "failed_attempts": 0,
            "locked_until": None,
        },
        "brad": {
            "user_id": "usr_brd001",
            "username": "brad",
            "display_name": "Brad Spence",
            "email": "brad@structuresamerica.com",
            "password_hash": hash_password("brad2026"),
            "password": hash_password("brad2026"),
            "roles": ["estimator"],
            "role": "estimator",
            "active": True,
            "created_at": now,
            "created_by": "system",
            "last_login": None,
            "force_password_change": True,
            "failed_attempts": 0,
            "locked_until": None,
        },
        "haley": {
            "user_id": "usr_hal001",
            "username": "haley",
            "display_name": "Haley McClendon",
            "email": "haley@structuresamerica.com",
            "password_hash": hash_password("haley2026"),
            "password": hash_password("haley2026"),
            "roles": ["project_manager", "admin"],
            "role": "project_manager",
            "active": True,
            "created_at": now,
            "created_by": "system",
            "last_login": None,
            "force_password_change": True,
            "failed_attempts": 0,
            "locked_until": None,
        },
    }

    with open(USERS_PATH, "w") as f:
        json.dump(users, f, indent=2)

    print("  [AUTH] Created default users file with new RBAC format")
    print("  [AUTH] Default logins:")
    print("  [AUTH]   zack  / titan2026  (God Mode)")
    print("  [AUTH]   admin / titan2026  (Admin)")
    print("  [AUTH]   brad  / brad2026   (Estimator)")
    print("  [AUTH]   haley / haley2026  (PM + Admin)")


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT LOG
# ─────────────────────────────────────────────────────────────────────────────

def _audit_log(action: str, actor: str, details: str = ""):
    """Append an entry to the audit log."""
    os.makedirs(DATA_DIR, exist_ok=True)

    entry = {
        "timestamp": _now_iso(),
        "action": action,
        "actor": actor,
        "details": details,
    }

    # Append to JSON array file
    log = []
    if os.path.isfile(AUDIT_PATH):
        try:
            with open(AUDIT_PATH, "r") as f:
                log = json.load(f)
        except (json.JSONDecodeError, IOError):
            log = []

    log.append(entry)

    # Keep last 10,000 entries
    if len(log) > 10000:
        log = log[-10000:]

    with open(AUDIT_PATH, "w") as f:
        json.dump(log, f, indent=2)


def get_audit_log(limit: int = 100, action_filter: str = None) -> List[dict]:
    """Read audit log entries, most recent first."""
    if not os.path.isfile(AUDIT_PATH):
        return []
    with open(AUDIT_PATH, "r") as f:
        log = json.load(f)

    if action_filter:
        log = [e for e in log if action_filter in e.get("action", "")]

    return list(reversed(log[-limit:]))


# ─────────────────────────────────────────────────────────────────────────────
# USER LISTING (for admin pages)
# ─────────────────────────────────────────────────────────────────────────────

def list_users(include_inactive: bool = False) -> List[dict]:
    """List all users with summary info (no password hashes)."""
    users = load_users()
    result = []
    for username, record in users.items():
        if not include_inactive and not record.get("active", True):
            continue
        result.append({
            "user_id": record.get("user_id", ""),
            "username": username,
            "display_name": record.get("display_name", username),
            "email": record.get("email", ""),
            "roles": record.get("roles", [record.get("role", "laborer")]),
            "active": record.get("active", True),
            "last_login": record.get("last_login"),
            "created_at": record.get("created_at"),
        })
    return result


# ─────────────────────────────────────────────────────────────────────────────
# PENDING USER REGISTRATION (Approval Queue)
# ─────────────────────────────────────────────────────────────────────────────

def _load_pending() -> List[dict]:
    """Load pending user registrations."""
    if not os.path.isfile(PENDING_PATH):
        return []
    try:
        with open(PENDING_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_pending(data: List[dict]):
    """Save pending user registrations."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PENDING_PATH, "w") as f:
        json.dump(data, f, indent=2)


def submit_registration(
    username: str,
    password: str,
    display_name: str,
    email: str = "",
    phone: str = "",
    address: str = "",
    company_role: str = "",
    ip_address: str = "",
) -> dict:
    """
    Submit a new user registration for admin approval.
    Raises ValueError if username already taken or pending.
    Returns the pending record.
    """
    # Check if username already exists as active user
    users = load_users()
    if username in users:
        raise ValueError("Username already taken")

    # Check if already pending
    pending = _load_pending()
    for p in pending:
        if p["username"] == username and p["status"] == "pending":
            raise ValueError("Registration already submitted and awaiting approval")

    record = {
        "request_id": f"REG-{secrets.token_hex(6).upper()}",
        "username": username,
        "password_hash": hash_password(password),
        "display_name": display_name,
        "email": email,
        "phone": phone,
        "address": address,
        "company_role": company_role,
        "status": "pending",  # pending | approved | rejected
        "submitted_at": _now_iso(),
        "submitted_ip": ip_address,
        "reviewed_by": None,
        "reviewed_at": None,
        "review_notes": "",
    }

    pending.append(record)
    _save_pending(pending)
    _audit_log("registration_submitted", username, f"Registration request from IP {ip_address}")
    return record


def list_pending_registrations(status_filter: str = None) -> List[dict]:
    """List pending registrations. Optionally filter by status."""
    pending = _load_pending()
    if status_filter:
        pending = [p for p in pending if p.get("status") == status_filter]
    # Don't expose password hashes
    safe = []
    for p in pending:
        entry = {k: v for k, v in p.items() if k != "password_hash"}
        safe.append(entry)
    return safe


def approve_registration(
    request_id: str,
    roles: List[str],
    approved_by: str = "admin",
    notes: str = "",
) -> dict:
    """
    Approve a pending registration — creates the user account.
    Raises ValueError if request not found or already processed.
    """
    from auth.roles import ROLES

    pending = _load_pending()
    target = None
    for p in pending:
        if p["request_id"] == request_id:
            target = p
            break

    if not target:
        raise ValueError(f"Registration request '{request_id}' not found")
    if target["status"] != "pending":
        raise ValueError(f"Request already {target['status']}")

    # Validate roles
    for r in roles:
        if r not in ROLES:
            raise ValueError(f"Invalid role: '{r}'")

    # Create the user account
    users = load_users()
    if target["username"] in users:
        raise ValueError(f"Username '{target['username']}' already exists")

    now = _now_iso()
    user_id = _gen_user_id()

    users[target["username"]] = {
        "user_id": user_id,
        "username": target["username"],
        "display_name": target["display_name"],
        "email": target.get("email", ""),
        "phone": target.get("phone", ""),
        "address": target.get("address", ""),
        "company_role": target.get("company_role", ""),
        "password_hash": target["password_hash"],
        "password": target["password_hash"],  # Legacy compat
        "roles": roles,
        "role": roles[0],
        "active": True,
        "created_at": now,
        "created_by": approved_by,
        "last_login": None,
        "force_password_change": False,
        "failed_attempts": 0,
        "locked_until": None,
    }
    save_users(users)

    # Update pending record
    target["status"] = "approved"
    target["reviewed_by"] = approved_by
    target["reviewed_at"] = now
    target["review_notes"] = notes
    _save_pending(pending)

    _audit_log("registration_approved", approved_by,
               f"Approved '{target['username']}' with roles {roles}")
    return target


def reject_registration(
    request_id: str,
    rejected_by: str = "admin",
    notes: str = "",
) -> dict:
    """Reject a pending registration."""
    pending = _load_pending()
    target = None
    for p in pending:
        if p["request_id"] == request_id:
            target = p
            break

    if not target:
        raise ValueError(f"Registration request '{request_id}' not found")
    if target["status"] != "pending":
        raise ValueError(f"Request already {target['status']}")

    target["status"] = "rejected"
    target["reviewed_by"] = rejected_by
    target["reviewed_at"] = _now_iso()
    target["review_notes"] = notes
    _save_pending(pending)

    _audit_log("registration_rejected", rejected_by,
               f"Rejected '{target['username']}': {notes}")
    return target


def update_user_profile(
    username: str,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    company_role: Optional[str] = None,
    display_name: Optional[str] = None,
    email: Optional[str] = None,
) -> dict:
    """Update a user's profile fields (phone, address, company role)."""
    users = load_users()
    user = users.get(username)
    if not user:
        raise ValueError(f"User '{username}' not found")

    if phone is not None:
        user["phone"] = phone
    if address is not None:
        user["address"] = address
    if company_role is not None:
        user["company_role"] = company_role
    if display_name is not None:
        user["display_name"] = display_name
    if email is not None:
        user["email"] = email

    users[username] = user
    save_users(users)
    _audit_log("profile_updated", username, f"Updated profile for '{username}'")
    return user
