"""
TitanForge Database Abstraction Layer
======================================
Drop-in replacement for JSON file storage, backed by SQLite.

All existing function signatures are preserved:
    load_inventory() / save_inventory()
    load_users() / save_users()
    load_customers() / save_customers()
    load_quote_data(job_code) / save_quote_data(job_code, data)
    load_project_qc(job_code) / save_project_qc(job_code, data)
    load_traceability_index() / save_traceability_index(data)

Plus new abstracted helpers for previously-inline operations:
    load_allocations() / save_allocation() / release_allocation()
    load_transactions() / log_transaction()
    load_receiving() / save_receiving_record()
    load_project_metadata(job_code) / save_project_metadata(job_code, data)
    load_project_status(job_code) / save_project_status(job_code, data)
    load_project_current(job_code) / save_project_current(job_code, data)

Thread-safe via connection-per-call with WAL mode.
"""

import os
import json
import sqlite3
import threading
import datetime
import logging

logger = logging.getLogger("titanforge.db")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("TITANFORGE_DATA_DIR", os.path.join(BASE_DIR, "data"))
DB_PATH = os.path.join(DATA_DIR, "titanforge.db")

_local = threading.local()


# ─────────────────────────────────────────────
# CONNECTION MANAGEMENT
# ─────────────────────────────────────────────

def get_db():
    """Get a thread-local database connection."""
    if not hasattr(_local, "conn") or _local.conn is None:
        os.makedirs(DATA_DIR, exist_ok=True)
        _local.conn = sqlite3.connect(DB_PATH, timeout=10)
        try:
            _local.conn.execute("PRAGMA journal_mode=WAL")
        except Exception:
            # WAL not supported on some filesystems; fall back to DELETE
            _local.conn.execute("PRAGMA journal_mode=DELETE")
        _local.conn.execute("PRAGMA foreign_keys=ON")
        _local.conn.execute("PRAGMA busy_timeout=5000")
        _local.conn.row_factory = sqlite3.Row
    return _local.conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_db()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    logger.info("Database initialized at %s", DB_PATH)


# ─────────────────────────────────────────────
# SCHEMA
# ─────────────────────────────────────────────

SCHEMA_SQL = """
-- Users
CREATE TABLE IF NOT EXISTS users (
    username    TEXT PRIMARY KEY,
    password    TEXT NOT NULL DEFAULT '',
    display_name TEXT NOT NULL DEFAULT '',
    role        TEXT NOT NULL DEFAULT 'viewer',
    email       TEXT DEFAULT '',
    created     TEXT DEFAULT '',
    extra       TEXT DEFAULT '{}'
);

-- Customers
CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL DEFAULT '',
    email       TEXT DEFAULT '',
    phone       TEXT DEFAULT '',
    company     TEXT DEFAULT '',
    address     TEXT DEFAULT '',
    city        TEXT DEFAULT '',
    state       TEXT DEFAULT '',
    zip         TEXT DEFAULT '',
    notes       TEXT DEFAULT '',
    created_at  TEXT DEFAULT '',
    extra       TEXT DEFAULT '{}'
);

-- Inventory Coils
CREATE TABLE IF NOT EXISTS coils (
    coil_id         TEXT PRIMARY KEY,
    name            TEXT NOT NULL DEFAULT '',
    gauge           TEXT DEFAULT '',
    grade           TEXT DEFAULT '',
    supplier        TEXT DEFAULT '',
    heat_num        TEXT DEFAULT '',
    width_in        REAL DEFAULT 0,
    weight_lbs      REAL DEFAULT 0,
    stock_lbs       REAL DEFAULT 0,
    committed_lbs   REAL DEFAULT 0,
    min_stock_lbs   REAL DEFAULT 2000,
    min_order_lbs   REAL DEFAULT 0,
    price_per_lb    REAL DEFAULT 0,
    lbs_per_lft     REAL DEFAULT 0,
    coil_max_lbs    REAL DEFAULT 0,
    lead_time_weeks INTEGER DEFAULT 0,
    received_date   TEXT DEFAULT '',
    status          TEXT DEFAULT 'active',
    extra           TEXT DEFAULT '{}'
);

-- Mill Certificates
CREATE TABLE IF NOT EXISTS mill_certs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    coil_id     TEXT DEFAULT '',
    heat_num    TEXT DEFAULT '',
    filename    TEXT DEFAULT '',
    uploaded_at TEXT DEFAULT '',
    date        TEXT DEFAULT '',
    extra       TEXT DEFAULT '{}'
);

-- Inventory Allocations
CREATE TABLE IF NOT EXISTS allocations (
    allocation_id   TEXT PRIMARY KEY,
    coil_id         TEXT NOT NULL,
    job_code        TEXT NOT NULL,
    quantity_lbs    REAL NOT NULL DEFAULT 0,
    consumed_lbs    REAL DEFAULT 0,
    status          TEXT DEFAULT 'active',
    work_order_ref  TEXT DEFAULT '',
    notes           TEXT DEFAULT '',
    date            TEXT DEFAULT ''
);

-- Inventory Transactions
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id  TEXT PRIMARY KEY,
    coil_id         TEXT NOT NULL,
    type            TEXT NOT NULL,
    quantity_lbs    REAL NOT NULL DEFAULT 0,
    job_code        TEXT DEFAULT '',
    reference       TEXT DEFAULT '',
    notes           TEXT DEFAULT '',
    date            TEXT DEFAULT ''
);

-- Inventory Receiving
CREATE TABLE IF NOT EXISTS receiving (
    receiving_id    TEXT PRIMARY KEY,
    coil_id         TEXT NOT NULL,
    supplier        TEXT DEFAULT '',
    quantity_lbs    REAL DEFAULT 0,
    po_number       TEXT DEFAULT '',
    bol_number      TEXT DEFAULT '',
    heat_number     TEXT DEFAULT '',
    received_by     TEXT DEFAULT '',
    notes           TEXT DEFAULT '',
    date            TEXT DEFAULT ''
);

-- Quotes
CREATE TABLE IF NOT EXISTS quotes (
    job_code    TEXT PRIMARY KEY,
    data        TEXT NOT NULL DEFAULT '{}',
    updated_at  TEXT DEFAULT ''
);

-- QC Data
CREATE TABLE IF NOT EXISTS qc_data (
    job_code    TEXT PRIMARY KEY,
    data        TEXT NOT NULL DEFAULT '{}',
    updated_at  TEXT DEFAULT ''
);

-- Traceability Index
CREATE TABLE IF NOT EXISTS traceability (
    id      INTEGER PRIMARY KEY CHECK (id = 1),
    data    TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT DEFAULT ''
);

-- Project Metadata
CREATE TABLE IF NOT EXISTS projects (
    job_code        TEXT PRIMARY KEY,
    project_name    TEXT DEFAULT '',
    customer_name   TEXT DEFAULT '',
    stage           TEXT DEFAULT 'quote',
    data            TEXT NOT NULL DEFAULT '{}',
    created_at      TEXT DEFAULT '',
    updated_at      TEXT DEFAULT ''
);

-- Project Current BOM (versioned)
CREATE TABLE IF NOT EXISTS project_versions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    job_code    TEXT NOT NULL,
    version     INTEGER NOT NULL DEFAULT 1,
    data        TEXT NOT NULL DEFAULT '{}',
    saved_at    TEXT DEFAULT '',
    saved_by    TEXT DEFAULT '',
    is_current  INTEGER DEFAULT 0,
    UNIQUE(job_code, version)
);

-- Project Status
CREATE TABLE IF NOT EXISTS project_status (
    job_code    TEXT PRIMARY KEY,
    stage       TEXT DEFAULT '',
    data        TEXT NOT NULL DEFAULT '{}',
    updated_at  TEXT DEFAULT '',
    updated_by  TEXT DEFAULT ''
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_allocations_coil ON allocations(coil_id);
CREATE INDEX IF NOT EXISTS idx_allocations_job ON allocations(job_code);
CREATE INDEX IF NOT EXISTS idx_allocations_status ON allocations(status);
CREATE INDEX IF NOT EXISTS idx_transactions_coil ON transactions(coil_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_receiving_coil ON receiving(coil_id);
CREATE INDEX IF NOT EXISTS idx_project_versions_job ON project_versions(job_code);
CREATE INDEX IF NOT EXISTS idx_projects_stage ON projects(stage);

-- Activity Log
CREATE TABLE IF NOT EXISTS activity_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT NOT NULL,
    user        TEXT NOT NULL DEFAULT 'system',
    action      TEXT NOT NULL,
    entity_type TEXT DEFAULT '',
    entity_id   TEXT DEFAULT '',
    details     TEXT DEFAULT '{}',
    ip_address  TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_log(user);
CREATE INDEX IF NOT EXISTS idx_activity_entity ON activity_log(entity_type, entity_id);

-- Gamification: XP & Levels
CREATE TABLE IF NOT EXISTS user_xp (
    username    TEXT PRIMARY KEY,
    total_xp    INTEGER NOT NULL DEFAULT 0,
    level       INTEGER NOT NULL DEFAULT 1,
    streak_days INTEGER NOT NULL DEFAULT 0,
    last_active TEXT DEFAULT '',
    updated_at  TEXT DEFAULT ''
);

-- Gamification: Achievements
CREATE TABLE IF NOT EXISTS achievements (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT NOT NULL,
    badge_id    TEXT NOT NULL,
    badge_name  TEXT NOT NULL,
    description TEXT DEFAULT '',
    icon        TEXT DEFAULT '',
    earned_at   TEXT NOT NULL,
    UNIQUE(username, badge_id)
);
CREATE INDEX IF NOT EXISTS idx_achievements_user ON achievements(username);

-- Gamification: XP Transactions (audit trail)
CREATE TABLE IF NOT EXISTS xp_transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT NOT NULL,
    xp_amount   INTEGER NOT NULL,
    reason      TEXT NOT NULL,
    entity_type TEXT DEFAULT '',
    entity_id   TEXT DEFAULT '',
    created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_xp_tx_user ON xp_transactions(username);
CREATE INDEX IF NOT EXISTS idx_xp_tx_date ON xp_transactions(created_at);
"""


# ─────────────────────────────────────────────
# USERS
# ─────────────────────────────────────────────

def load_users():
    """Load all users as {username: {password, display_name, role, ...}}."""
    return cached("users", _load_users_uncached, ttl=60)

def _load_users_uncached():
    conn = get_db()
    rows = conn.execute("SELECT * FROM users").fetchall()
    result = {}
    for r in rows:
        extra = json.loads(r["extra"] or "{}")
        result[r["username"]] = {
            "password": r["password"],
            "display_name": r["display_name"],
            "role": r["role"],
            "email": r["email"],
            "created": r["created"],
            **extra,
        }
    if not result:
        # Bootstrap default admin
        _ensure_default_users()
        return load_users()
    return result


def save_users(data):
    """Save full users dict {username: {password, display_name, role, ...}}."""
    invalidate("users")
    conn = get_db()
    conn.execute("DELETE FROM users")
    for username, info in data.items():
        extra = {k: v for k, v in info.items()
                 if k not in ("password", "display_name", "role", "email", "created")}
        conn.execute(
            "INSERT INTO users (username, password, display_name, role, email, created, extra) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (username, info.get("password", ""), info.get("display_name", username),
             info.get("role", "viewer"), info.get("email", ""),
             info.get("created", ""), json.dumps(extra))
        )
    conn.commit()


def _ensure_default_users():
    """Create default admin user if no users exist."""
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count == 0:
        now = datetime.datetime.now().isoformat()
        conn.execute(
            "INSERT INTO users (username, password, display_name, role, created) "
            "VALUES (?, ?, ?, ?, ?)",
            ("admin", "", "Admin", "admin", now)
        )
        conn.commit()


# ─────────────────────────────────────────────
# INVENTORY (Coils)
# ─────────────────────────────────────────────

def load_inventory():
    """Load inventory in legacy format: {coils: {id: {...}}, mill_certs: [...]}."""
    return cached("inventory", _load_inventory_uncached, ttl=15)

def _load_inventory_uncached():
    conn = get_db()
    coils = {}
    for r in conn.execute("SELECT * FROM coils").fetchall():
        extra = json.loads(r["extra"] or "{}")
        coils[r["coil_id"]] = {
            "name": r["name"], "gauge": r["gauge"], "grade": r["grade"],
            "supplier": r["supplier"], "heat_num": r["heat_num"],
            "width_in": r["width_in"], "weight_lbs": r["weight_lbs"],
            "stock_lbs": r["stock_lbs"], "committed_lbs": r["committed_lbs"],
            "min_stock_lbs": r["min_stock_lbs"], "min_order_lbs": r["min_order_lbs"],
            "price_per_lb": r["price_per_lb"], "lbs_per_lft": r["lbs_per_lft"],
            "coil_max_lbs": r["coil_max_lbs"], "lead_time_weeks": r["lead_time_weeks"],
            "received_date": r["received_date"], "status": r["status"],
            **extra,
        }

    certs = []
    for r in conn.execute("SELECT * FROM mill_certs").fetchall():
        extra = json.loads(r["extra"] or "{}")
        certs.append({
            "coil_id": r["coil_id"], "heat_num": r["heat_num"],
            "filename": r["filename"], "uploaded_at": r["uploaded_at"],
            "date": r["date"], **extra,
        })

    return {"coils": coils, "mill_certs": certs}


def save_inventory(data):
    """Save inventory from legacy format: {coils: {id: {...}}, mill_certs: [...]}."""
    invalidate("inventory")
    conn = get_db()

    # Upsert coils
    known_cols = {"name", "gauge", "grade", "supplier", "heat_num", "width_in",
                  "weight_lbs", "stock_lbs", "committed_lbs", "min_stock_lbs",
                  "min_order_lbs", "price_per_lb", "lbs_per_lft", "coil_max_lbs",
                  "lead_time_weeks", "received_date", "status"}

    for coil_id, c in data.get("coils", {}).items():
        extra = {k: v for k, v in c.items() if k not in known_cols}
        conn.execute("""
            INSERT INTO coils (coil_id, name, gauge, grade, supplier, heat_num,
                width_in, weight_lbs, stock_lbs, committed_lbs, min_stock_lbs,
                min_order_lbs, price_per_lb, lbs_per_lft, coil_max_lbs,
                lead_time_weeks, received_date, status, extra)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(coil_id) DO UPDATE SET
                name=excluded.name, gauge=excluded.gauge, grade=excluded.grade,
                supplier=excluded.supplier, heat_num=excluded.heat_num,
                width_in=excluded.width_in, weight_lbs=excluded.weight_lbs,
                stock_lbs=excluded.stock_lbs, committed_lbs=excluded.committed_lbs,
                min_stock_lbs=excluded.min_stock_lbs, min_order_lbs=excluded.min_order_lbs,
                price_per_lb=excluded.price_per_lb, lbs_per_lft=excluded.lbs_per_lft,
                coil_max_lbs=excluded.coil_max_lbs, lead_time_weeks=excluded.lead_time_weeks,
                received_date=excluded.received_date, status=excluded.status,
                extra=excluded.extra
        """, (coil_id, c.get("name", ""), c.get("gauge", ""), c.get("grade", ""),
              c.get("supplier", ""), c.get("heat_num", ""),
              float(c.get("width_in", 0) or 0), float(c.get("weight_lbs", 0) or 0),
              float(c.get("stock_lbs", 0) or 0), float(c.get("committed_lbs", 0) or 0),
              float(c.get("min_stock_lbs", 2000) or 2000), float(c.get("min_order_lbs", 0) or 0),
              float(c.get("price_per_lb", 0) or 0), float(c.get("lbs_per_lft", 0) or 0),
              float(c.get("coil_max_lbs", 0) or 0), int(c.get("lead_time_weeks", 0) or 0),
              c.get("received_date", ""), c.get("status", "active"),
              json.dumps(extra)))

    # Replace mill certs
    conn.execute("DELETE FROM mill_certs")
    for cert in data.get("mill_certs", []):
        if isinstance(cert, dict):
            extra = {k: v for k, v in cert.items()
                     if k not in ("coil_id", "heat_num", "filename", "uploaded_at", "date")}
            conn.execute(
                "INSERT INTO mill_certs (coil_id, heat_num, filename, uploaded_at, date, extra) "
                "VALUES (?,?,?,?,?,?)",
                (cert.get("coil_id", ""), cert.get("heat_num", ""),
                 cert.get("filename", ""), cert.get("uploaded_at", ""),
                 cert.get("date", ""), json.dumps(extra))
            )
    conn.commit()


# ─────────────────────────────────────────────
# CUSTOMERS
# ─────────────────────────────────────────────

def load_customers():
    """Load all customers as a list of dicts."""
    return cached("customers", _load_customers_uncached, ttl=30)

def _load_customers_uncached():
    conn = get_db()
    rows = conn.execute("SELECT * FROM customers ORDER BY name").fetchall()
    result = []
    for r in rows:
        extra = json.loads(r["extra"] or "{}")
        cust = {
            "id": r["id"],
            "company": r["company"],
            "name": r["name"],
            "email": r["email"],
            "phone": r["phone"],
            # Reconstruct nested primary_contact (handler / frontend expects this)
            "primary_contact": extra.pop("primary_contact", None) or {
                "name": r["name"],
                "email": r["email"],
                "phone": r["phone"],
                "title": extra.pop("contact_title", ""),
            },
            # Reconstruct nested address
            "address": extra.pop("address", None) if isinstance(extra.get("address"), dict) else {
                "street": r["address"],
                "city": r["city"],
                "state": r["state"],
                "zip": r["zip"],
            },
            "city": r["city"],
            "state": r["state"],
            "zip": r["zip"],
            "notes": r["notes"],
            "created_at": r["created_at"],
            **extra,
        }
        result.append(cust)
    return result


def save_customers(data):
    """Save full customers list (replaces all).

    Handles both flat format (name, email, phone, address as strings)
    and nested format from the handler (primary_contact: {name, phone, email, title},
    address: {street, city, state, zip}).
    """
    invalidate("customers")
    conn = get_db()
    conn.execute("DELETE FROM customers")
    KNOWN_COLS = {"id", "name", "email", "phone", "company",
                  "address", "city", "state", "zip", "notes", "created_at"}
    for c in data:
        if not isinstance(c, dict):
            continue

        # --- Flatten nested primary_contact ---------------------------------
        name = c.get("name", "")
        email = c.get("email", "")
        phone = c.get("phone", "")
        pc = c.get("primary_contact")
        if isinstance(pc, dict):
            name = name or pc.get("name", "")
            email = email or pc.get("email", "")
            phone = phone or pc.get("phone", "")

        # --- Flatten nested address -----------------------------------------
        addr_raw = c.get("address", "")
        city = c.get("city", "")
        state = c.get("state", "")
        zip_code = c.get("zip", "")
        if isinstance(addr_raw, dict):
            city = city or addr_raw.get("city", "")
            state = state or addr_raw.get("state", "")
            zip_code = zip_code or addr_raw.get("zip", "")
            addr_raw = addr_raw.get("street", "")
        # Ensure address is a plain string
        address_str = str(addr_raw) if addr_raw else ""

        # --- Build extra JSON for all non-core fields -----------------------
        extra = {}
        for k, v in c.items():
            if k not in KNOWN_COLS:
                # Ensure all values are JSON-serializable
                if isinstance(v, (dict, list)):
                    extra[k] = v
                else:
                    extra[k] = v

        conn.execute(
            "INSERT INTO customers (name, email, phone, company, address, city, state, zip, notes, created_at, extra) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (str(name), str(email), str(phone),
             str(c.get("company", "")), address_str, str(city),
             str(state), str(zip_code), str(c.get("notes", "")),
             str(c.get("created_at", "")), json.dumps(extra))
        )
    conn.commit()


# ─────────────────────────────────────────────
# QUOTES
# ─────────────────────────────────────────────

def load_quote_data(job_code):
    """Load quote for a job code, or return None."""
    conn = get_db()
    row = conn.execute("SELECT data FROM quotes WHERE job_code=?", (job_code,)).fetchone()
    if row:
        return json.loads(row["data"])
    return None


def save_quote_data(job_code, data):
    """Save quote data for a job code."""
    now = datetime.datetime.now().isoformat()
    data["updated_at"] = now
    conn = get_db()
    conn.execute(
        "INSERT INTO quotes (job_code, data, updated_at) VALUES (?,?,?) "
        "ON CONFLICT(job_code) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at",
        (job_code, json.dumps(data, default=str), now)
    )
    conn.commit()


# ─────────────────────────────────────────────
# QC DATA
# ─────────────────────────────────────────────

def load_project_qc(job_code):
    """Load QC data for a project."""
    conn = get_db()
    row = conn.execute("SELECT data FROM qc_data WHERE job_code=?", (job_code,)).fetchone()
    if row:
        return json.loads(row["data"])
    return {"inspections": [], "ncrs": [], "traceability": []}


def save_project_qc(job_code, data):
    """Save QC data for a project."""
    now = datetime.datetime.now().isoformat()
    conn = get_db()
    conn.execute(
        "INSERT INTO qc_data (job_code, data, updated_at) VALUES (?,?,?) "
        "ON CONFLICT(job_code) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at",
        (job_code, json.dumps(data, default=str), now)
    )
    conn.commit()


# ─────────────────────────────────────────────
# TRACEABILITY INDEX
# ─────────────────────────────────────────────

def load_traceability_index():
    """Load traceability index (singleton)."""
    conn = get_db()
    row = conn.execute("SELECT data FROM traceability WHERE id=1").fetchone()
    if row:
        return json.loads(row["data"])
    return {"heat_numbers": {}}


def save_traceability_index(data):
    """Save traceability index."""
    now = datetime.datetime.now().isoformat()
    conn = get_db()
    conn.execute(
        "INSERT INTO traceability (id, data, updated_at) VALUES (1,?,?) "
        "ON CONFLICT(id) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at",
        (json.dumps(data, default=str), now)
    )
    conn.commit()


# ─────────────────────────────────────────────
# ALLOCATIONS
# ─────────────────────────────────────────────

def load_allocations(status_filter=None):
    """Load inventory allocations, optionally filtered by status."""
    conn = get_db()
    if status_filter:
        rows = conn.execute("SELECT * FROM allocations WHERE status=? ORDER BY date DESC",
                            (status_filter,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM allocations ORDER BY date DESC").fetchall()
    return [dict(r) for r in rows]


def save_allocation(alloc):
    """Insert or update an allocation record."""
    conn = get_db()
    conn.execute("""
        INSERT INTO allocations (allocation_id, coil_id, job_code, quantity_lbs,
            consumed_lbs, status, work_order_ref, notes, date)
        VALUES (?,?,?,?,?,?,?,?,?)
        ON CONFLICT(allocation_id) DO UPDATE SET
            quantity_lbs=excluded.quantity_lbs, consumed_lbs=excluded.consumed_lbs,
            status=excluded.status, notes=excluded.notes
    """, (alloc["allocation_id"], alloc["coil_id"], alloc["job_code"],
          float(alloc.get("quantity_lbs", 0)), float(alloc.get("consumed_lbs", 0)),
          alloc.get("status", "active"), alloc.get("work_order_ref", ""),
          alloc.get("notes", ""), alloc.get("date", "")))
    conn.commit()


def release_allocation(allocation_id):
    """Mark an allocation as released."""
    conn = get_db()
    conn.execute("UPDATE allocations SET status='released' WHERE allocation_id=?",
                 (allocation_id,))
    conn.commit()


def count_allocations():
    """Get count of active allocations."""
    conn = get_db()
    return conn.execute("SELECT COUNT(*) FROM allocations WHERE status='active'").fetchone()[0]


# ─────────────────────────────────────────────
# TRANSACTIONS
# ─────────────────────────────────────────────

def load_transactions():
    """Load all inventory transactions."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM transactions ORDER BY date DESC").fetchall()
    return [dict(r) for r in rows]


def log_transaction(tx):
    """Insert a new transaction record."""
    conn = get_db()
    conn.execute(
        "INSERT INTO transactions (transaction_id, coil_id, type, quantity_lbs, "
        "job_code, reference, notes, date) VALUES (?,?,?,?,?,?,?,?)",
        (tx["transaction_id"], tx["coil_id"], tx["type"],
         float(tx.get("quantity_lbs", 0)), tx.get("job_code", ""),
         tx.get("reference", ""), tx.get("notes", ""), tx.get("date", ""))
    )
    conn.commit()


# ─────────────────────────────────────────────
# RECEIVING
# ─────────────────────────────────────────────

def load_receiving():
    """Load all receiving records."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM receiving ORDER BY date DESC").fetchall()
    return [dict(r) for r in rows]


def save_receiving_record(rec):
    """Insert a new receiving record."""
    conn = get_db()
    conn.execute(
        "INSERT INTO receiving (receiving_id, coil_id, supplier, quantity_lbs, "
        "po_number, bol_number, heat_number, received_by, notes, date) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (rec["receiving_id"], rec["coil_id"], rec.get("supplier", ""),
         float(rec.get("quantity_lbs", 0)), rec.get("po_number", ""),
         rec.get("bol_number", ""), rec.get("heat_number", ""),
         rec.get("received_by", ""), rec.get("notes", ""), rec.get("date", ""))
    )
    conn.commit()


# ─────────────────────────────────────────────
# PROJECTS
# ─────────────────────────────────────────────

def load_project_metadata(job_code):
    """Load project metadata, or None if not found."""
    conn = get_db()
    row = conn.execute("SELECT data FROM projects WHERE job_code=?", (job_code,)).fetchone()
    if row:
        return json.loads(row["data"])
    return None


def save_project_metadata(job_code, data):
    """Save project metadata."""
    now = datetime.datetime.now().isoformat()
    data.setdefault("job_code", job_code)
    conn = get_db()
    conn.execute("""
        INSERT INTO projects (job_code, project_name, customer_name, stage, data, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?)
        ON CONFLICT(job_code) DO UPDATE SET
            project_name=excluded.project_name, customer_name=excluded.customer_name,
            stage=excluded.stage, data=excluded.data, updated_at=excluded.updated_at
    """, (job_code,
          data.get("project_name", ""),
          data.get("customer", {}).get("name", "") if isinstance(data.get("customer"), dict) else data.get("customer_name", ""),
          data.get("stage", "quote"),
          json.dumps(data, default=str),
          data.get("created_at", now), now))
    conn.commit()


def list_projects(stage=None):
    """List all projects, optionally filtered by stage."""
    conn = get_db()
    if stage:
        rows = conn.execute("SELECT data FROM projects WHERE stage=? ORDER BY job_code", (stage,)).fetchall()
    else:
        rows = conn.execute("SELECT data FROM projects ORDER BY job_code").fetchall()
    return [json.loads(r["data"]) for r in rows]


def load_project_status(job_code):
    """Load project status."""
    conn = get_db()
    row = conn.execute("SELECT data FROM project_status WHERE job_code=?", (job_code,)).fetchone()
    if row:
        return json.loads(row["data"])
    return None


def save_project_status(job_code, data):
    """Save project status."""
    now = datetime.datetime.now().isoformat()
    conn = get_db()
    conn.execute("""
        INSERT INTO project_status (job_code, stage, data, updated_at, updated_by)
        VALUES (?,?,?,?,?)
        ON CONFLICT(job_code) DO UPDATE SET
            stage=excluded.stage, data=excluded.data,
            updated_at=excluded.updated_at, updated_by=excluded.updated_by
    """, (job_code, data.get("stage", ""), json.dumps(data, default=str),
          now, data.get("updated_by", "")))
    conn.commit()


def load_project_current(job_code):
    """Load the current BOM version for a project."""
    conn = get_db()
    row = conn.execute(
        "SELECT data FROM project_versions WHERE job_code=? AND is_current=1",
        (job_code,)
    ).fetchone()
    if row:
        return json.loads(row["data"])
    return None


def save_project_current(job_code, data, version=None, saved_by=""):
    """Save a new BOM version as current."""
    now = datetime.datetime.now().isoformat()
    conn = get_db()

    if version is None:
        row = conn.execute(
            "SELECT MAX(version) as v FROM project_versions WHERE job_code=?",
            (job_code,)
        ).fetchone()
        version = (row["v"] or 0) + 1

    # Unmark previous current
    conn.execute("UPDATE project_versions SET is_current=0 WHERE job_code=?", (job_code,))

    # Insert new version
    data["version"] = version
    data["saved_at"] = now
    conn.execute(
        "INSERT INTO project_versions (job_code, version, data, saved_at, saved_by, is_current) "
        "VALUES (?,?,?,?,?,1)",
        (job_code, version, json.dumps(data, default=str), now, saved_by)
    )
    conn.commit()
    return version


# ─────────────────────────────────────────────
# CACHE LAYER (in-memory, per-process)
# ─────────────────────────────────────────────

_cache = {}
_cache_ttl = {}
DEFAULT_TTL = 30  # seconds


def cached(key, loader, ttl=DEFAULT_TTL):
    """Simple in-memory cache with TTL."""
    import time
    now = time.time()
    if key in _cache and _cache_ttl.get(key, 0) > now:
        return _cache[key]
    result = loader()
    _cache[key] = result
    _cache_ttl[key] = now + ttl
    return result


def invalidate(key=None):
    """Clear cache for a specific key, or all keys if None."""
    if key is None:
        _cache.clear()
        _cache_ttl.clear()
    else:
        _cache.pop(key, None)
        _cache_ttl.pop(key, None)


# ─────────────────────────────────────────────
# ACTIVITY LOG
# ─────────────────────────────────────────────

def log_activity(user, action, entity_type="", entity_id="", details=None, ip_address=""):
    """Record an activity to the audit log.

    Args:
        user: username performing the action
        action: short verb phrase, e.g. "created_project", "updated_coil"
        entity_type: "project", "coil", "customer", "user", "quote", etc.
        entity_id: the specific ID (job_code, coil_id, customer id, etc.)
        details: optional dict of extra context (serialized to JSON)
        ip_address: requesting client IP
    """
    conn = get_db()
    # Ensure details is a JSON string, not a raw dict
    if isinstance(details, str):
        details_str = details
    elif details is not None:
        details_str = json.dumps(details)
    else:
        details_str = "{}"
    conn.execute(
        """INSERT INTO activity_log (timestamp, user, action, entity_type, entity_id, details, ip_address)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.datetime.utcnow().isoformat() + "Z",
            user or "system",
            str(action),
            str(entity_type),
            str(entity_id),
            details_str,
            str(ip_address),
        ),
    )
    conn.commit()


def get_activity_log(limit=50, offset=0, user=None, entity_type=None, entity_id=None):
    """Retrieve activity log entries with optional filters.

    Returns list of dicts sorted by most recent first.
    """
    conn = get_db()
    sql = "SELECT * FROM activity_log WHERE 1=1"
    params = []
    if user:
        sql += " AND user = ?"
        params.append(user)
    if entity_type:
        sql += " AND entity_type = ?"
        params.append(entity_type)
    if entity_id:
        sql += " AND entity_id = ?"
        params.append(str(entity_id))
    sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = conn.execute(sql, params).fetchall()
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "user": r["user"],
            "action": r["action"],
            "entity_type": r["entity_type"],
            "entity_id": r["entity_id"],
            "details": json.loads(r["details"] or "{}"),
            "ip_address": r["ip_address"],
        })
    return result


def get_activity_count(user=None, entity_type=None, entity_id=None):
    """Get total count of activity entries (for pagination)."""
    conn = get_db()
    sql = "SELECT COUNT(*) FROM activity_log WHERE 1=1"
    params = []
    if user:
        sql += " AND user = ?"
        params.append(user)
    if entity_type:
        sql += " AND entity_type = ?"
        params.append(entity_type)
    if entity_id:
        sql += " AND entity_id = ?"
        params.append(str(entity_id))
    return conn.execute(sql, params).fetchone()[0]


# ─────────────────────────────────────────────
# GAMIFICATION
# ─────────────────────────────────────────────

# XP values for actions
XP_VALUES = {
    "login": 5,
    "created_project": 50,
    "saved_quote": 30,
    "created_customer": 25,
    "updated_customer": 10,
    "created_coil": 15,
    "updated_coil": 10,
    "created_work_order": 40,
    "completed_item": 20,
    "passed_inspection": 15,
    "failed_inspection": 5,
    "uploaded_doc": 10,
    "generated_shop_drawings": 35,
    "approved_work_order": 25,
    "default": 5,
}

# Level thresholds
LEVEL_THRESHOLDS = [
    (0, "Apprentice"),
    (100, "Welder I"),
    (300, "Welder II"),
    (600, "Fabricator"),
    (1000, "Senior Fabricator"),
    (1500, "Foreman"),
    (2500, "Master Builder"),
    (4000, "Shop Legend"),
    (6000, "TitanForge Elite"),
    (10000, "Titan"),
]

# Achievement definitions
ACHIEVEMENT_DEFS = {
    "first_project": {"name": "First Blueprint", "desc": "Created your first project", "icon": "📋", "check": lambda stats: stats.get("projects_created", 0) >= 1},
    "five_projects": {"name": "Project Manager", "desc": "Created 5 projects", "icon": "📊", "check": lambda stats: stats.get("projects_created", 0) >= 5},
    "first_wo": {"name": "Shop Starter", "desc": "Created your first work order", "icon": "🔧", "check": lambda stats: stats.get("work_orders_created", 0) >= 1},
    "ten_inspections": {"name": "Quality Eye", "desc": "Passed 10 inspections", "icon": "🔍", "check": lambda stats: stats.get("inspections_passed", 0) >= 10},
    "fifty_inspections": {"name": "QC Master", "desc": "Passed 50 inspections", "icon": "🏅", "check": lambda stats: stats.get("inspections_passed", 0) >= 50},
    "hundred_items": {"name": "Production Machine", "desc": "Completed 100 fabrication items", "icon": "⚡", "check": lambda stats: stats.get("items_completed", 0) >= 100},
    "streak_3": {"name": "Hat Trick", "desc": "3-day login streak", "icon": "🔥", "check": lambda stats: stats.get("streak_days", 0) >= 3},
    "streak_7": {"name": "On Fire", "desc": "7-day login streak", "icon": "🔥🔥", "check": lambda stats: stats.get("streak_days", 0) >= 7},
    "streak_30": {"name": "Iron Will", "desc": "30-day login streak", "icon": "💎", "check": lambda stats: stats.get("streak_days", 0) >= 30},
    "level_5": {"name": "Rising Star", "desc": "Reached level 5 (Foreman)", "icon": "⭐", "check": lambda stats: stats.get("level", 1) >= 5},
    "xp_1000": {"name": "XP Hunter", "desc": "Earned 1,000 XP", "icon": "🏆", "check": lambda stats: stats.get("total_xp", 0) >= 1000},
    "first_customer": {"name": "Client Whisperer", "desc": "Added your first customer", "icon": "🤝", "check": lambda stats: stats.get("customers_created", 0) >= 1},
    "speed_demon": {"name": "Speed Demon", "desc": "Completed 10 items in one day", "icon": "💨", "check": lambda stats: stats.get("items_today", 0) >= 10},
}


def get_level_info(total_xp):
    """Given total XP, return (level_number, level_name, xp_for_next, xp_progress)."""
    level = 1
    name = "Apprentice"
    for i, (threshold, lname) in enumerate(LEVEL_THRESHOLDS):
        if total_xp >= threshold:
            level = i + 1
            name = lname
    next_threshold = LEVEL_THRESHOLDS[min(level, len(LEVEL_THRESHOLDS) - 1)][0]
    prev_threshold = LEVEL_THRESHOLDS[level - 1][0] if level > 0 else 0
    xp_in_level = total_xp - prev_threshold
    xp_needed = max(next_threshold - prev_threshold, 1)
    progress_pct = min(round(xp_in_level / xp_needed * 100), 100) if level < len(LEVEL_THRESHOLDS) else 100
    return {
        "level": level,
        "name": name,
        "total_xp": total_xp,
        "xp_in_level": xp_in_level,
        "xp_needed": xp_needed,
        "progress_pct": progress_pct,
        "next_level": LEVEL_THRESHOLDS[min(level, len(LEVEL_THRESHOLDS) - 1)][1] if level < len(LEVEL_THRESHOLDS) else name,
    }


def award_xp(username, action, entity_type="", entity_id="", extra_xp=0):
    """Award XP to a user for an action. Returns (xp_awarded, new_total, leveled_up, new_achievements)."""
    conn = get_db()
    now = datetime.datetime.now().isoformat()
    xp = XP_VALUES.get(action, XP_VALUES["default"]) + extra_xp

    # Get or create user_xp row
    row = conn.execute("SELECT * FROM user_xp WHERE username = ?", (username,)).fetchone()
    if row is None:
        conn.execute("INSERT INTO user_xp (username, total_xp, level, streak_days, last_active, updated_at) VALUES (?, 0, 1, 0, '', ?)", (username, now))
        conn.commit()
        row = conn.execute("SELECT * FROM user_xp WHERE username = ?", (username,)).fetchone()

    old_level = row["level"]
    old_xp = row["total_xp"]
    new_xp = old_xp + xp

    # Calculate new level
    new_level_info = get_level_info(new_xp)
    new_level = new_level_info["level"]

    # Update streak
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    last_active = row["last_active"] or ""
    streak = row["streak_days"] or 0
    if last_active != today_str:
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        if last_active == yesterday:
            streak += 1
        elif last_active != today_str:
            streak = 1  # reset streak

    conn.execute(
        "UPDATE user_xp SET total_xp = ?, level = ?, streak_days = ?, last_active = ?, updated_at = ? WHERE username = ?",
        (new_xp, new_level, streak, today_str, now, username)
    )

    # Record XP transaction
    conn.execute(
        "INSERT INTO xp_transactions (username, xp_amount, reason, entity_type, entity_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (username, xp, action, entity_type, entity_id, now)
    )
    conn.commit()

    leveled_up = new_level > old_level

    # Check for new achievements
    new_achievements = check_achievements(username)

    return {
        "xp_awarded": xp,
        "new_total": new_xp,
        "level": new_level,
        "level_name": new_level_info["name"],
        "leveled_up": leveled_up,
        "streak": streak,
        "new_achievements": new_achievements,
    }


def check_achievements(username):
    """Check and award any new achievements for a user. Returns list of newly earned badges."""
    conn = get_db()

    # Get user stats
    row = conn.execute("SELECT * FROM user_xp WHERE username = ?", (username,)).fetchone()
    if not row:
        return []

    stats = {
        "total_xp": row["total_xp"],
        "level": row["level"],
        "streak_days": row["streak_days"],
    }

    # Count actions from xp_transactions
    action_counts = conn.execute(
        "SELECT reason, COUNT(*) as cnt FROM xp_transactions WHERE username = ? GROUP BY reason",
        (username,)
    ).fetchall()
    for ac in action_counts:
        reason = ac["reason"]
        cnt = ac["cnt"]
        if reason == "created_project":
            stats["projects_created"] = cnt
        elif reason == "created_work_order":
            stats["work_orders_created"] = cnt
        elif reason == "passed_inspection":
            stats["inspections_passed"] = cnt
        elif reason == "completed_item":
            stats["items_completed"] = cnt
        elif reason == "created_customer":
            stats["customers_created"] = cnt

    # Count items completed today
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today_count = conn.execute(
        "SELECT COUNT(*) FROM xp_transactions WHERE username = ? AND reason = 'completed_item' AND created_at LIKE ?",
        (username, today + "%")
    ).fetchone()[0]
    stats["items_today"] = today_count

    # Get already-earned achievements
    earned = set()
    for r in conn.execute("SELECT badge_id FROM achievements WHERE username = ?", (username,)).fetchall():
        earned.add(r["badge_id"])

    # Check for new ones
    now = datetime.datetime.now().isoformat()
    new_badges = []
    for badge_id, bdef in ACHIEVEMENT_DEFS.items():
        if badge_id not in earned and bdef["check"](stats):
            try:
                conn.execute(
                    "INSERT INTO achievements (username, badge_id, badge_name, description, icon, earned_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (username, badge_id, bdef["name"], bdef["desc"], bdef["icon"], now)
                )
                new_badges.append({"id": badge_id, "name": bdef["name"], "desc": bdef["desc"], "icon": bdef["icon"]})
            except Exception:
                pass  # duplicate
    if new_badges:
        conn.commit()

    return new_badges


def get_user_gamification(username):
    """Get full gamification profile for a user."""
    conn = get_db()
    row = conn.execute("SELECT * FROM user_xp WHERE username = ?", (username,)).fetchone()
    if not row:
        return {
            "total_xp": 0, "level": 1, "level_name": "Apprentice",
            "streak_days": 0, "achievements": [], "progress_pct": 0,
            "xp_in_level": 0, "xp_needed": 100, "next_level": "Welder I",
        }

    level_info = get_level_info(row["total_xp"])
    achievements = []
    for r in conn.execute("SELECT * FROM achievements WHERE username = ? ORDER BY earned_at DESC", (username,)).fetchall():
        achievements.append({
            "badge_id": r["badge_id"],
            "badge_name": r["badge_name"],
            "description": r["description"],
            "icon": r["icon"],
            "earned_at": r["earned_at"],
        })

    return {
        **level_info,
        "streak_days": row["streak_days"],
        "last_active": row["last_active"],
        "achievements": achievements,
    }


def get_leaderboard(limit=10):
    """Get top users by XP."""
    conn = get_db()
    rows = conn.execute(
        "SELECT username, total_xp, level, streak_days FROM user_xp ORDER BY total_xp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    result = []
    for i, r in enumerate(rows):
        info = get_level_info(r["total_xp"])
        result.append({
            "rank": i + 1,
            "username": r["username"],
            "total_xp": r["total_xp"],
            "level": r["level"],
            "level_name": info["name"],
            "streak_days": r["streak_days"],
        })
    return result
