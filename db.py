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
        result.append({
            "id": r["id"], "name": r["name"], "email": r["email"],
            "phone": r["phone"], "company": r["company"],
            "address": r["address"], "city": r["city"],
            "state": r["state"], "zip": r["zip"],
            "notes": r["notes"], "created_at": r["created_at"],
            **extra,
        })
    return result


def save_customers(data):
    """Save full customers list (replaces all)."""
    invalidate("customers")
    conn = get_db()
    conn.execute("DELETE FROM customers")
    for c in data:
        if not isinstance(c, dict):
            continue
        extra = {k: v for k, v in c.items()
                 if k not in ("id", "name", "email", "phone", "company",
                              "address", "city", "state", "zip", "notes", "created_at")}
        conn.execute(
            "INSERT INTO customers (name, email, phone, company, address, city, state, zip, notes, created_at, extra) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (c.get("name", ""), c.get("email", ""), c.get("phone", ""),
             c.get("company", ""), c.get("address", ""), c.get("city", ""),
             c.get("state", ""), c.get("zip", ""), c.get("notes", ""),
             c.get("created_at", ""), json.dumps(extra))
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
