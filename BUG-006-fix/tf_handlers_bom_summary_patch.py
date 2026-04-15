"""
BUG-006 FIX — New handler for /api/project/bom-summary
========================================================

INSTRUCTIONS:
1. Add this handler class to tf_handlers.py AFTER the existing CalculateHandler (~line 823)

2. Add this route to get_routes():
   (r"/api/project/bom-summary", ProjectBOMSummaryHandler),

This endpoint returns per-building concrete and geometry data from a saved
BOM calculation, so the TC Estimator can auto-populate its per-building
concrete breakdown table.
"""

import os
import json


class ProjectBOMSummaryHandler(BaseHandler):
    """GET /api/project/bom-summary?job_code=XXX — Per-building BOM summary for TC import.

    BUG-006 FIX: Returns per-building concrete data (n_piers, depth, cubic yards)
    so the TC Estimator can show a per-building concrete breakdown.

    Response:
    {
      "ok": true,
      "buildings": [
        {
          "building_id": "bldg_1",
          "building_name": "Building 1",
          "type": "tee",
          "width_ft": 40,
          "length_ft": 60,
          "n_struct_cols": 8,
          "concrete_n_piers": 8,
          "concrete_cy": 5.12,
          "footing_depth_ft": 10.0
        },
        ...
      ]
    }
    """
    required_roles = ["admin", "estimator", "shop", "qc"]

    def get(self):
        try:
            job_code = self.get_query_argument("job_code", "").strip()
            if not job_code:
                self.write(json_encode({"ok": False, "error": "Missing job_code parameter"}))
                return

            # Look for saved BOM data in the project directory
            # Projects save BOM results as JSON files
            bom_data = self._find_bom_data(job_code)

            if not bom_data:
                self.write(json_encode({
                    "ok": False,
                    "error": "No saved BOM found for job " + job_code
                }))
                return

            buildings = []
            for b in bom_data.get("buildings", []):
                geom = b.get("geometry", {})
                buildings.append({
                    "building_id": b.get("building_id", ""),
                    "building_name": b.get("building_name", ""),
                    "type": b.get("type", "tee"),
                    "width_ft": b.get("width_ft", 0),
                    "length_ft": b.get("length_ft", 0),
                    "clear_height_ft": b.get("clear_height_ft", 0),
                    "n_struct_cols": geom.get("n_struct_cols", 0),
                    "concrete_n_piers": geom.get("concrete_n_piers", 0),
                    "concrete_cy": geom.get("concrete_cy", 0),
                    "footing_depth_ft": geom.get("footing_depth_ft", 10),
                })

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({
                "ok": True,
                "job_code": job_code,
                "buildings": buildings,
                "footing_depth_ft": bom_data.get("project", {}).get("footing_depth_ft", 10),
            }))

        except Exception as e:
            import traceback
            self.set_status(500)
            self.write(json_encode({
                "ok": False, "error": str(e),
                "trace": traceback.format_exc()
            }))

    def _find_bom_data(self, job_code):
        """Search for saved BOM data for a given job code.

        Checks multiple possible storage locations:
        1. data/projects/{job_code}/bom.json (canonical location)
        2. data/projects/{job_code}/sa_result.json (saved SA calc result)
        3. data/bom_results/{job_code}.json (legacy flat storage)
        """
        search_paths = [
            os.path.join(BASE_DIR, "data", "projects", job_code, "bom.json"),
            os.path.join(BASE_DIR, "data", "projects", job_code, "sa_result.json"),
            os.path.join(BASE_DIR, "data", "bom_results", job_code + ".json"),
        ]

        for path in search_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        data = json.load(f)
                    # Validate it has buildings data
                    if "buildings" in data and len(data["buildings"]) > 0:
                        return data
                except (json.JSONDecodeError, IOError):
                    continue

        return None
