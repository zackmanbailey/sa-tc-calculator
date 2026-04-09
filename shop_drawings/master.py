"""
Master Shop Drawing Orchestrator
Generates ALL shop drawings for a project in one call.
Returns a manifest of all generated files.
"""

import os
import json
import datetime
from typing import Dict, List, Optional

from shop_drawings.config import ShopDrawingConfig
from shop_drawings.column_gen import generate_column_drawing, generate_all_column_drawings
from shop_drawings.rafter_gen import generate_rafter_drawing, generate_all_rafter_drawings
from shop_drawings.purlin_gen import generate_purlin_drawing
from shop_drawings.cutlist_gen import generate_cutlist_drawing
from shop_drawings.sticker_gen import generate_sticker_pdf
from shop_drawings.shipping_gen import generate_shipping_manifest


def generate_all_shop_drawings(
    cfg: ShopDrawingConfig,
    output_dir: str,
    revision: str = "-",
    include_stickers: bool = True,
    include_manifest: bool = True,
) -> Dict:
    """
    Generate ALL shop drawings for a project.

    Args:
        cfg: Complete ShopDrawingConfig
        output_dir: Directory to write PDFs
        revision: Revision letter (default "-" for initial)
        include_stickers: Generate sticker PDFs
        include_manifest: Generate shipping manifest

    Returns:
        Dict with:
          - files: list of {path, type, description}
          - summary: {total_files, total_bytes, timestamp}
          - errors: list of error messages
    """
    os.makedirs(output_dir, exist_ok=True)

    # Ensure all numeric fields are proper types (safety net for JSON data)
    cfg.ensure_numeric()

    files = []
    errors = []
    total_bytes = 0

    job = cfg.job_code or "DRAFT"

    # ── 1. Column Drawings ──
    try:
        col_paths = generate_all_column_drawings(cfg, output_dir, revision)
        for p in col_paths:
            size = os.path.getsize(p)
            total_bytes += size
            files.append({
                "path": p,
                "filename": os.path.basename(p),
                "type": "column",
                "description": f"Column Shop Drawing",
                "size_bytes": size,
            })
    except Exception as e:
        errors.append(f"Column drawing error: {str(e)}")

    # ── 2. Rafter Drawings ──
    try:
        raft_paths = generate_all_rafter_drawings(cfg, output_dir, revision)
        for p in raft_paths:
            size = os.path.getsize(p)
            total_bytes += size
            files.append({
                "path": p,
                "filename": os.path.basename(p),
                "type": "rafter",
                "description": f"Rafter Shop Drawing",
                "size_bytes": size,
            })
    except Exception as e:
        errors.append(f"Rafter drawing error: {str(e)}")

    # ── 3. Purlin Group Drawings ──
    try:
        path = os.path.join(output_dir, f"{job}_PURLINS.pdf")
        generate_purlin_drawing(cfg, output_path=path, revision=revision)
        size = os.path.getsize(path)
        total_bytes += size
        files.append({
            "path": path,
            "filename": os.path.basename(path),
            "type": "purlin",
            "description": "Purlin Groups Shop Drawing",
            "size_bytes": size,
        })
    except Exception as e:
        errors.append(f"Purlin drawing error: {str(e)}")

    # ── 4. Cut Lists ──
    try:
        path = os.path.join(output_dir, f"{job}_CUTLISTS.pdf")
        generate_cutlist_drawing(cfg, output_path=path, revision=revision)
        size = os.path.getsize(path)
        total_bytes += size
        files.append({
            "path": path,
            "filename": os.path.basename(path),
            "type": "cutlist",
            "description": "Cut Lists (Endcaps, Roofing, Components)",
            "size_bytes": size,
        })
    except Exception as e:
        errors.append(f"Cut list error: {str(e)}")

    # ── 5. Stickers ──
    if include_stickers:
        try:
            path = os.path.join(output_dir, f"{job}_STICKERS.pdf")
            generate_sticker_pdf(cfg, output_path=path)
            size = os.path.getsize(path)
            total_bytes += size
            files.append({
                "path": path,
                "filename": os.path.basename(path),
                "type": "stickers",
                "description": "Fabrication Stickers (4\"x6\")",
                "size_bytes": size,
            })
        except Exception as e:
            errors.append(f"Sticker error: {str(e)}")

    # ── 6. Shipping Manifest ──
    if include_manifest:
        try:
            path = os.path.join(output_dir, f"{job}_MANIFEST.pdf")
            generate_shipping_manifest(cfg, output_path=path, revision=revision)
            size = os.path.getsize(path)
            total_bytes += size
            files.append({
                "path": path,
                "filename": os.path.basename(path),
                "type": "manifest",
                "description": "Shipping Manifest & Loading Order",
                "size_bytes": size,
            })
        except Exception as e:
            errors.append(f"Manifest error: {str(e)}")

    # ── Save generation log ──
    log = {
        "job_code": job,
        "project_name": cfg.project_name,
        "generated_at": datetime.datetime.now().isoformat(),
        "revision": revision,
        "total_files": len(files),
        "total_bytes": total_bytes,
        "files": [{
            "filename": f["filename"],
            "type": f["type"],
            "description": f["description"],
            "size_bytes": f["size_bytes"],
        } for f in files],
        "errors": errors,
        "config": cfg.to_dict(),
    }
    log_path = os.path.join(output_dir, f"{job}_generation_log.json")
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2, default=str)

    return {
        "files": files,
        "log_path": log_path,
        "summary": {
            "total_files": len(files),
            "total_bytes": total_bytes,
            "total_kb": round(total_bytes / 1024, 1),
            "timestamp": log["generated_at"],
            "errors": len(errors),
        },
        "errors": errors,
    }
