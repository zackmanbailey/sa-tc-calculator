"""
BUG-018 FIX — Global Search Backend
=====================================

The frontend search UI already exists in shared_nav.py (search overlay, Ctrl+K shortcut,
typeahead). The missing piece is the /api/search backend endpoint.

INSTRUCTIONS:

1. Add this handler to tf_handlers.py

2. Add route to get_routes():
   (r"/api/search", GlobalSearchHandler),

3. The existing shared_nav.py search UI will automatically connect.
"""

import os
import json
import re


class GlobalSearchHandler(BaseHandler):
    """GET /api/search?q=query — Global search across projects, customers, coils, work orders.

    BUG-018 FIX: Backend for the global search that already has a frontend.
    Returns up to 10 results across all searchable entities.
    """

    def get(self):
        try:
            query = self.get_query_argument("q", "").strip().lower()
            if len(query) < 2:
                self.write(json_encode({"ok": True, "results": [], "query": query}))
                return

            results = []

            # Search projects
            results.extend(self._search_projects(query))

            # Search customers
            results.extend(self._search_customers(query))

            # Search inventory coils
            results.extend(self._search_coils(query))

            # Search work orders
            results.extend(self._search_work_orders(query))

            # Sort by relevance (exact match first, then contains)
            results.sort(key=lambda r: (
                0 if query in (r.get("title", "") or "").lower()[:len(query)] else 1,
                r.get("title", "").lower()
            ))

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "results": results[:10],
                "query": query,
                "total": len(results),
            }))

        except Exception as e:
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "results": [], "error": str(e)}))

    def _search_projects(self, query):
        """Search saved projects."""
        results = []
        projects_dir = os.path.join(BASE_DIR, "data", "projects")
        if not os.path.isdir(projects_dir):
            return results

        for job_dir in os.listdir(projects_dir):
            job_path = os.path.join(projects_dir, job_dir)
            if not os.path.isdir(job_path):
                continue

            # Check if job code matches
            if query in job_dir.lower():
                results.append({
                    "type": "project",
                    "title": job_dir,
                    "subtitle": "Project",
                    "url": "/project/" + job_dir,
                })
                continue

            # Check project metadata
            meta_path = os.path.join(job_path, "project.json")
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r") as f:
                        meta = json.load(f)
                    name = (meta.get("name", "") or meta.get("project_name", "")).lower()
                    customer = (meta.get("customer_name", "") or "").lower()
                    if query in name or query in customer or query in job_dir.lower():
                        results.append({
                            "type": "project",
                            "title": meta.get("name", job_dir),
                            "subtitle": f"Project: {job_dir}" + (f" — {meta.get('customer_name', '')}" if meta.get('customer_name') else ""),
                            "url": "/project/" + job_dir,
                        })
                except (json.JSONDecodeError, IOError):
                    pass

        return results[:5]

    def _search_customers(self, query):
        """Search customers database."""
        results = []
        customers_path = os.path.join(BASE_DIR, "data", "customers.json")
        if not os.path.exists(customers_path):
            return results

        try:
            with open(customers_path, "r") as f:
                customers = json.load(f)

            for c in (customers if isinstance(customers, list) else customers.get("customers", [])):
                name = (c.get("name", "") or "").lower()
                company = (c.get("company", "") or "").lower()
                email = (c.get("email", "") or "").lower()
                if query in name or query in company or query in email:
                    results.append({
                        "type": "customer",
                        "title": c.get("name", "Unknown"),
                        "subtitle": f"Customer" + (f" — {c.get('company', '')}" if c.get('company') else ""),
                        "url": "/customers?search=" + c.get("name", ""),
                    })
        except (json.JSONDecodeError, IOError):
            pass

        return results[:5]

    def _search_coils(self, query):
        """Search inventory coils."""
        results = []
        inv_path = os.path.join(BASE_DIR, "data", "inventory.json")
        if not os.path.exists(inv_path):
            return results

        try:
            with open(inv_path, "r") as f:
                inv = json.load(f)

            coils = inv.get("coils", []) if isinstance(inv, dict) else []
            for coil in coils:
                name = (coil.get("name", "") or "").lower()
                gauge = str(coil.get("gauge", "")).lower()
                heat = (coil.get("heat_num", "") or "").lower()
                if query in name or query in gauge or query in heat:
                    results.append({
                        "type": "coil",
                        "title": coil.get("name", "Unknown Coil"),
                        "subtitle": f"Coil — {coil.get('stock_lbs', 0):,.0f} lbs" + (f" | Heat# {coil.get('heat_num', '')}" if coil.get('heat_num') else ""),
                        "url": "/inventory",
                    })
        except (json.JSONDecodeError, IOError):
            pass

        return results[:5]

    def _search_work_orders(self, query):
        """Search work orders."""
        results = []
        wo_base = os.path.join(BASE_DIR, "data", "shop_drawings")
        if not os.path.isdir(wo_base):
            return results

        for job_dir in os.listdir(wo_base):
            wo_dir = os.path.join(wo_base, job_dir, "work_orders")
            if not os.path.isdir(wo_dir):
                continue

            for wo_file in os.listdir(wo_dir):
                if not wo_file.endswith(".json"):
                    continue

                try:
                    with open(os.path.join(wo_dir, wo_file), "r") as f:
                        wo = json.load(f)

                    wo_id = (wo.get("work_order_id", "") or "").lower()
                    if query in wo_id or query in job_dir.lower():
                        results.append({
                            "type": "work_order",
                            "title": wo.get("work_order_id", wo_file),
                            "subtitle": f"Work Order — {job_dir} | {wo.get('status', 'unknown')}",
                            "url": f"/work-orders/{job_dir}",
                        })
                except (json.JSONDecodeError, IOError):
                    continue

        return results[:5]
