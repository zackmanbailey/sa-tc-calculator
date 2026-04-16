#!/usr/bin/env python3
"""
TitanForge: Migrate JSON files → SQLite
========================================
One-time migration script. Safe to re-run (uses INSERT OR REPLACE).
Backs up existing JSON files before migration.

Usage:
    python migrate_to_sqlite.py
    python migrate_to_sqlite.py --dry-run   # Preview without writing
"""

import os
import sys
import json
import shutil
import datetime
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

DATA_DIR = os.environ.get("TITANFORGE_DATA_DIR", os.path.join(BASE_DIR, "data"))


def load_json(path, default=None):
    """Safely load a JSON file."""
    if not os.path.isfile(path):
        return default
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"  ⚠ Error reading {path}: {e}")
        return default


def backup_json_files():
    """Create a backup of all JSON data files."""
    backup_dir = os.path.join(DATA_DIR, f"json_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(backup_dir, exist_ok=True)

    for name in os.listdir(DATA_DIR):
        src = os.path.join(DATA_DIR, name)
        if name.endswith(".json") and os.path.isfile(src):
            shutil.copy2(src, os.path.join(backup_dir, name))

    # Backup project dirs
    projects_dir = os.path.join(DATA_DIR, "projects")
    if os.path.isdir(projects_dir):
        shutil.copytree(projects_dir, os.path.join(backup_dir, "projects"),
                        dirs_exist_ok=True)

    # Backup quotes
    quotes_dir = os.path.join(DATA_DIR, "quotes")
    if os.path.isdir(quotes_dir):
        shutil.copytree(quotes_dir, os.path.join(backup_dir, "quotes"),
                        dirs_exist_ok=True)

    # Backup qc
    qc_dir = os.path.join(DATA_DIR, "qc")
    if os.path.isdir(qc_dir):
        shutil.copytree(qc_dir, os.path.join(backup_dir, "qc"),
                        dirs_exist_ok=True)

    print(f"  ✓ JSON files backed up to {backup_dir}")
    return backup_dir


def migrate_users(db, dry_run=False):
    """Migrate data/users.json → users table."""
    path = os.path.join(DATA_DIR, "users.json")
    data = load_json(path, {})
    count = 0
    for username, info in data.items():
        if not isinstance(info, dict):
            continue
        if not dry_run:
            extra = {k: v for k, v in info.items()
                     if k not in ("password", "display_name", "role", "email", "created")}
            db.execute(
                "INSERT OR REPLACE INTO users (username, password, display_name, role, email, created, extra) "
                "VALUES (?,?,?,?,?,?,?)",
                (username, info.get("password", ""), info.get("display_name", username),
                 info.get("role", "viewer"), info.get("email", ""),
                 info.get("created", ""), json.dumps(extra))
            )
        count += 1
    print(f"  {'[DRY RUN] ' if dry_run else ''}Migrated {count} users")
    return count


def migrate_inventory(db, dry_run=False):
    """Migrate data/inventory.json → coils + mill_certs tables."""
    path = os.path.join(DATA_DIR, "inventory.json")
    data = load_json(path, {"coils": {}, "mill_certs": []})

    coil_count = 0
    known_cols = {"name", "gauge", "grade", "supplier", "heat_num", "width_in",
                  "weight_lbs", "stock_lbs", "committed_lbs", "min_stock_lbs",
                  "min_order_lbs", "price_per_lb", "lbs_per_lft", "coil_max_lbs",
                  "lead_time_weeks", "received_date", "status"}

    for coil_id, c in data.get("coils", {}).items():
        if not dry_run:
            extra = {k: v for k, v in c.items() if k not in known_cols}
            db.execute("""
                INSERT OR REPLACE INTO coils (coil_id, name, gauge, grade, supplier, heat_num,
                    width_in, weight_lbs, stock_lbs, committed_lbs, min_stock_lbs,
                    min_order_lbs, price_per_lb, lbs_per_lft, coil_max_lbs,
                    lead_time_weeks, received_date, status, extra)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (coil_id, c.get("name", ""), c.get("gauge", ""), c.get("grade", ""),
                  c.get("supplier", ""), c.get("heat_num", ""),
                  float(c.get("width_in", 0) or 0), float(c.get("weight_lbs", 0) or 0),
                  float(c.get("stock_lbs", 0) or 0), float(c.get("committed_lbs", 0) or 0),
                  float(c.get("min_stock_lbs", 2000) or 2000), float(c.get("min_order_lbs", 0) or 0),
                  float(c.get("price_per_lb", 0) or 0), float(c.get("lbs_per_lft", 0) or 0),
                  float(c.get("coil_max_lbs", 0) or 0), int(c.get("lead_time_weeks", 0) or 0),
                  c.get("received_date", ""), c.get("status", "active"),
                  json.dumps(extra)))
        coil_count += 1

    cert_count = 0
    mill_certs = data.get("mill_certs", [])
    if isinstance(mill_certs, dict):
        mill_certs = list(mill_certs.values())
    for cert in mill_certs:
        if not isinstance(cert, dict):
            continue
        if not dry_run:
            extra = {k: v for k, v in cert.items()
                     if k not in ("coil_id", "heat_num", "filename", "uploaded_at", "date")}
            db.execute(
                "INSERT INTO mill_certs (coil_id, heat_num, filename, uploaded_at, date, extra) "
                "VALUES (?,?,?,?,?,?)",
                (cert.get("coil_id", ""), cert.get("heat_num", ""),
                 cert.get("filename", ""), cert.get("uploaded_at", ""),
                 cert.get("date", ""), json.dumps(extra))
            )
        cert_count += 1

    print(f"  {'[DRY RUN] ' if dry_run else ''}Migrated {coil_count} coils, {cert_count} mill certs")
    return coil_count


def migrate_customers(db, dry_run=False):
    """Migrate data/customers.json → customers table."""
    path = os.path.join(DATA_DIR, "customers.json")
    data = load_json(path, [])
    count = 0
    for c in data:
        if not isinstance(c, dict):
            continue
        if not dry_run:
            # Extract flat fields; customers may have nested contact/address dicts
            contact = c.get("primary_contact", {})
            if isinstance(contact, dict):
                name = contact.get("name", "")
                email = contact.get("email", "")
                phone = contact.get("phone", "")
            else:
                name = c.get("name", "")
                email = c.get("email", "")
                phone = c.get("phone", "")
            addr = c.get("address", {})
            if isinstance(addr, dict):
                city = addr.get("city", "")
                state = addr.get("state", "")
                zipcode = addr.get("zip", "")
                address_str = addr.get("street", "")
            else:
                city = c.get("city", "")
                state = c.get("state", "")
                zipcode = c.get("zip", "")
                address_str = str(addr) if addr else ""

            # Store full original data as extra for lossless migration
            db.execute(
                "INSERT INTO customers (name, email, phone, company, address, city, state, zip, notes, created_at, extra) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (name, email, phone, c.get("company", ""),
                 address_str, city, state, zipcode,
                 c.get("notes", ""), c.get("created_at", ""),
                 json.dumps(c, default=str))
            )
        count += 1
    print(f"  {'[DRY RUN] ' if dry_run else ''}Migrated {count} customers")
    return count


def migrate_allocations(db, dry_run=False):
    """Migrate data/inventory_allocations.json → allocations table."""
    path = os.path.join(DATA_DIR, "inventory_allocations.json")
    data = load_json(path, [])
    count = 0
    for a in data:
        if not isinstance(a, dict):
            continue
        if not dry_run:
            db.execute("""
                INSERT OR REPLACE INTO allocations
                (allocation_id, coil_id, job_code, quantity_lbs, consumed_lbs, status, work_order_ref, notes, date)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (a.get("allocation_id", f"ALLOC-{count}"), a.get("coil_id", ""),
                  a.get("job_code", ""), float(a.get("quantity_lbs", 0)),
                  float(a.get("consumed_lbs", 0)), a.get("status", "active"),
                  a.get("work_order_ref", ""), a.get("notes", ""), a.get("date", "")))
        count += 1
    print(f"  {'[DRY RUN] ' if dry_run else ''}Migrated {count} allocations")
    return count


def migrate_transactions(db, dry_run=False):
    """Migrate data/inventory_transactions.json → transactions table."""
    path = os.path.join(DATA_DIR, "inventory_transactions.json")
    data = load_json(path, [])
    count = 0
    for tx in data:
        if not isinstance(tx, dict):
            continue
        if not dry_run:
            db.execute(
                "INSERT OR REPLACE INTO transactions "
                "(transaction_id, coil_id, type, quantity_lbs, job_code, reference, notes, date) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (tx.get("transaction_id", f"TX-{count}"), tx.get("coil_id", ""),
                 tx.get("type", ""), float(tx.get("quantity_lbs", 0)),
                 tx.get("job_code", ""), tx.get("reference", ""),
                 tx.get("notes", ""), tx.get("date", ""))
            )
        count += 1
    print(f"  {'[DRY RUN] ' if dry_run else ''}Migrated {count} transactions")
    return count


def migrate_receiving(db, dry_run=False):
    """Migrate data/inventory_receiving.json → receiving table."""
    path = os.path.join(DATA_DIR, "inventory_receiving.json")
    data = load_json(path, [])
    count = 0
    for rec in data:
        if not isinstance(rec, dict):
            continue
        if not dry_run:
            db.execute(
                "INSERT OR REPLACE INTO receiving "
                "(receiving_id, coil_id, supplier, quantity_lbs, po_number, bol_number, "
                "heat_number, received_by, notes, date) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (rec.get("receiving_id", f"RCV-{count}"), rec.get("coil_id", ""),
                 rec.get("supplier", ""), float(rec.get("quantity_lbs", 0)),
                 rec.get("po_number", ""), rec.get("bol_number", ""),
                 rec.get("heat_number", ""), rec.get("received_by", ""),
                 rec.get("notes", ""), rec.get("date", ""))
            )
        count += 1
    print(f"  {'[DRY RUN] ' if dry_run else ''}Migrated {count} receiving records")
    return count


def migrate_quotes(db, dry_run=False):
    """Migrate data/quotes/*.json → quotes table."""
    quotes_dir = os.path.join(DATA_DIR, "quotes")
    if not os.path.isdir(quotes_dir):
        print("  No quotes directory found, skipping")
        return 0
    count = 0
    for name in os.listdir(quotes_dir):
        if not name.endswith(".json"):
            continue
        job_code = name[:-5]  # strip .json
        data = load_json(os.path.join(quotes_dir, name))
        if data and not dry_run:
            db.execute(
                "INSERT OR REPLACE INTO quotes (job_code, data, updated_at) VALUES (?,?,?)",
                (job_code, json.dumps(data, default=str),
                 data.get("updated_at", ""))
            )
        count += 1
    print(f"  {'[DRY RUN] ' if dry_run else ''}Migrated {count} quotes")
    return count


def migrate_qc(db, dry_run=False):
    """Migrate data/qc/*.json → qc_data table."""
    qc_dir = os.path.join(DATA_DIR, "qc")
    if not os.path.isdir(qc_dir):
        print("  No QC directory found, skipping")
        return 0
    count = 0
    for name in os.listdir(qc_dir):
        if not name.endswith(".json"):
            continue
        job_code = name[:-5]
        data = load_json(os.path.join(qc_dir, name))
        if data and not dry_run:
            db.execute(
                "INSERT OR REPLACE INTO qc_data (job_code, data, updated_at) VALUES (?,?,?)",
                (job_code, json.dumps(data, default=str), "")
            )
        count += 1
    print(f"  {'[DRY RUN] ' if dry_run else ''}Migrated {count} QC records")
    return count


def migrate_traceability(db, dry_run=False):
    """Migrate data/traceability_index.json → traceability table."""
    path = os.path.join(DATA_DIR, "traceability_index.json")
    data = load_json(path)
    if data and not dry_run:
        db.execute(
            "INSERT OR REPLACE INTO traceability (id, data, updated_at) VALUES (1,?,?)",
            (json.dumps(data, default=str), "")
        )
        print(f"  Migrated traceability index ({len(data.get('heat_numbers', {}))} heat numbers)")
    else:
        print(f"  {'[DRY RUN] ' if dry_run else ''}No traceability data to migrate")
    return 1 if data else 0


def migrate_projects(db, dry_run=False):
    """Migrate data/projects/*/metadata.json, status.json, current.json, v*.json."""
    projects_dir = os.path.join(DATA_DIR, "projects")
    if not os.path.isdir(projects_dir):
        print("  No projects directory found, skipping")
        return 0

    count = 0
    for job_code in sorted(os.listdir(projects_dir)):
        proj_dir = os.path.join(projects_dir, job_code)
        if not os.path.isdir(proj_dir):
            continue

        # Metadata
        meta = load_json(os.path.join(proj_dir, "metadata.json"))
        if meta and not dry_run:
            customer_name = ""
            if isinstance(meta.get("customer"), dict):
                customer_name = meta["customer"].get("name", "")
            elif isinstance(meta.get("customer_name"), str):
                customer_name = meta["customer_name"]

            db.execute("""
                INSERT OR REPLACE INTO projects
                (job_code, project_name, customer_name, stage, data, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?)
            """, (job_code, meta.get("project_name", ""), customer_name,
                  meta.get("stage", "quote"), json.dumps(meta, default=str),
                  meta.get("created_at", ""), meta.get("updated_at", "")))

        # Status
        status = load_json(os.path.join(proj_dir, "status.json"))
        if status and not dry_run:
            db.execute("""
                INSERT OR REPLACE INTO project_status
                (job_code, stage, data, updated_at, updated_by)
                VALUES (?,?,?,?,?)
            """, (job_code, status.get("stage", ""),
                  json.dumps(status, default=str),
                  status.get("updated_at", ""), status.get("updated_by", "")))

        # Current BOM
        current = load_json(os.path.join(proj_dir, "current.json"))
        if current and not dry_run:
            db.execute("""
                INSERT OR REPLACE INTO project_versions
                (job_code, version, data, saved_at, saved_by, is_current)
                VALUES (?,?,?,?,?,1)
            """, (job_code, current.get("version", 1),
                  json.dumps(current, default=str),
                  current.get("saved_at", ""), current.get("saved_by", "")))

        # Version history
        for fname in sorted(os.listdir(proj_dir)):
            if fname.startswith("v") and fname.endswith(".json") and fname != "current.json":
                ver_data = load_json(os.path.join(proj_dir, fname))
                if ver_data and not dry_run:
                    ver_num = ver_data.get("version", 0)
                    if ver_num == 0:
                        try:
                            ver_num = int(fname[1:-5])
                        except ValueError:
                            ver_num = 0
                    if ver_num > 0:
                        db.execute("""
                            INSERT OR IGNORE INTO project_versions
                            (job_code, version, data, saved_at, saved_by, is_current)
                            VALUES (?,?,?,?,?,0)
                        """, (job_code, ver_num, json.dumps(ver_data, default=str),
                              ver_data.get("saved_at", ""), ver_data.get("saved_by", "")))

        count += 1

    print(f"  {'[DRY RUN] ' if dry_run else ''}Migrated {count} projects")
    return count


def main():
    parser = argparse.ArgumentParser(description="Migrate TitanForge JSON data to SQLite")
    parser.add_argument("--dry-run", action="store_true", help="Preview migration without writing")
    args = parser.parse_args()

    print("=" * 60)
    print("TitanForge: JSON → SQLite Migration")
    print("=" * 60)
    print(f"Data directory: {DATA_DIR}")
    print(f"Database path:  {os.path.join(DATA_DIR, 'titanforge.db')}")
    print()

    if not args.dry_run:
        print("Step 0: Backing up JSON files...")
        backup_json_files()
        print()

    print("Step 1: Initializing database schema...")
    import db as tfdb
    if not args.dry_run:
        tfdb.init_db()
    conn = tfdb.get_db() if not args.dry_run else None
    print("  ✓ Schema created")
    print()

    print("Step 2: Migrating data...")
    migrate_users(conn, args.dry_run)
    migrate_inventory(conn, args.dry_run)
    migrate_customers(conn, args.dry_run)
    migrate_allocations(conn, args.dry_run)
    migrate_transactions(conn, args.dry_run)
    migrate_receiving(conn, args.dry_run)
    migrate_quotes(conn, args.dry_run)
    migrate_qc(conn, args.dry_run)
    migrate_traceability(conn, args.dry_run)
    migrate_projects(conn, args.dry_run)

    if not args.dry_run:
        conn.commit()

    print()
    print("=" * 60)
    if args.dry_run:
        print("DRY RUN COMPLETE — no changes written")
    else:
        db_size = os.path.getsize(os.path.join(DATA_DIR, "titanforge.db"))
        print(f"Migration complete! Database size: {db_size:,} bytes")
        print("JSON files preserved as backup. Once verified, they can be removed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
