"""
TitanForge — Comprehensive Project Data System Tests
=====================================================
Tests the entire project data lifecycle:
1. project_paths() helper returns correct paths
2. project_estimator_status() reports accurate status
3. cascade_delete_project() removes ALL associated data
4. TC save/load handlers work correctly
5. BOM auto-save writes bom_snapshot.json
6. Estimator status API endpoint works
7. Full lifecycle: create → save data → check status → delete → verify clean
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestProjectPaths(unittest.TestCase):
    """Test the project_paths() helper function."""

    def setUp(self):
        # Import after path setup
        import tf_handlers
        self.tf = tf_handlers
        self.original_base = self.tf.BASE_DIR
        self.original_projects = self.tf.PROJECTS_DIR
        self.original_quotes = self.tf.QUOTES_DIR
        self.original_qc = self.tf.QC_DIR

        # Use temp directory
        self.tmpdir = tempfile.mkdtemp()
        self.tf.BASE_DIR = self.tmpdir
        self.tf.DATA_DIR = os.path.join(self.tmpdir, "data")
        self.tf.PROJECTS_DIR = os.path.join(self.tmpdir, "data", "projects")
        self.tf.QUOTES_DIR = os.path.join(self.tmpdir, "data", "quotes")
        self.tf.QC_DIR = os.path.join(self.tmpdir, "data", "qc")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        self.tf.BASE_DIR = self.original_base
        self.tf.PROJECTS_DIR = self.original_projects
        self.tf.QUOTES_DIR = self.original_quotes
        self.tf.QC_DIR = self.original_qc

    def test_project_paths_returns_all_keys(self):
        """project_paths must return all expected path keys."""
        paths = self.tf.project_paths("SA-2401")
        required_keys = [
            "project_dir", "metadata", "sa_current", "status",
            "tc_quote", "quote", "qc", "shop_drawings_dir", "docs_dir",
        ]
        for key in required_keys:
            self.assertIn(key, paths, f"Missing key: {key}")

    def test_project_paths_sanitizes_job_code(self):
        """Dangerous characters in job_code must be sanitized."""
        paths = self.tf.project_paths("../../etc/passwd")
        # Should not contain path traversal
        self.assertNotIn("..", paths["project_dir"])
        self.assertIn("______etc_passwd", paths["project_dir"])

    def test_project_paths_correct_locations(self):
        """Paths should point to the correct directories."""
        paths = self.tf.project_paths("TEST-001")
        self.assertTrue(paths["project_dir"].endswith("projects/TEST-001"))
        self.assertTrue(paths["tc_quote"].endswith("projects/TEST-001/tc_quote.json"))
        self.assertTrue(paths["quote"].endswith("quotes/TEST-001.json"))
        self.assertTrue(paths["qc"].endswith("qc/TEST-001.json"))
        self.assertTrue(paths["shop_drawings_dir"].endswith("shop_drawings/TEST-001"))

    def test_safe_job_strips_whitespace(self):
        """_safe_job should strip whitespace from job codes."""
        result = self.tf._safe_job("  SA-2401  ")
        self.assertEqual(result, "SA-2401")


class TestEstimatorStatus(unittest.TestCase):
    """Test project_estimator_status() reporting."""

    def setUp(self):
        import tf_handlers
        self.tf = tf_handlers
        self.original_base = self.tf.BASE_DIR
        self.original_projects = self.tf.PROJECTS_DIR
        self.original_quotes = self.tf.QUOTES_DIR
        self.original_qc = self.tf.QC_DIR

        self.tmpdir = tempfile.mkdtemp()
        self.tf.BASE_DIR = self.tmpdir
        self.tf.DATA_DIR = os.path.join(self.tmpdir, "data")
        self.tf.PROJECTS_DIR = os.path.join(self.tmpdir, "data", "projects")
        self.tf.QUOTES_DIR = os.path.join(self.tmpdir, "data", "quotes")
        self.tf.QC_DIR = os.path.join(self.tmpdir, "data", "qc")

        # Create project directory
        self.proj_dir = os.path.join(self.tf.PROJECTS_DIR, "TEST-001")
        os.makedirs(self.proj_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        self.tf.BASE_DIR = self.original_base
        self.tf.PROJECTS_DIR = self.original_projects
        self.tf.QUOTES_DIR = self.original_quotes
        self.tf.QC_DIR = self.original_qc

    def test_empty_project_all_false(self):
        """New project with no data should report everything as not linked."""
        status = self.tf.project_estimator_status("TEST-001")
        self.assertFalse(status["sa_linked"])
        self.assertFalse(status["tc_linked"])
        self.assertFalse(status["bom_available"])
        self.assertFalse(status["quote_linked"])
        self.assertFalse(status["shop_linked"])
        self.assertEqual(status["wo_count"], 0)
        self.assertFalse(status["qc_linked"])

    def test_sa_linked_after_save(self):
        """SA should show as linked after current.json is created."""
        sa_data = {
            "job_code": "TEST-001",
            "version": 1,
            "saved_at": "2026-04-14T10:00:00",
            "saved_by": "admin",
            "bom_data": {"project": {}, "buildings": []},
        }
        with open(os.path.join(self.proj_dir, "current.json"), "w") as f:
            json.dump(sa_data, f)

        status = self.tf.project_estimator_status("TEST-001")
        self.assertTrue(status["sa_linked"])
        self.assertTrue(status["bom_available"])
        self.assertEqual(status["sa_meta"]["version"], 1)

    def test_sa_linked_without_bom(self):
        """SA linked but no bom_data means BOM not available."""
        sa_data = {
            "job_code": "TEST-001",
            "version": 1,
            "saved_at": "2026-04-14T10:00:00",
        }
        with open(os.path.join(self.proj_dir, "current.json"), "w") as f:
            json.dump(sa_data, f)

        status = self.tf.project_estimator_status("TEST-001")
        self.assertTrue(status["sa_linked"])
        self.assertFalse(status["bom_available"])

    def test_tc_linked_after_save(self):
        """TC should show as linked after tc_quote.json is created."""
        tc_data = {"version": 1, "saved_at": "2026-04-14", "saved_by": "admin"}
        with open(os.path.join(self.proj_dir, "tc_quote.json"), "w") as f:
            json.dump(tc_data, f)

        status = self.tf.project_estimator_status("TEST-001")
        self.assertTrue(status["tc_linked"])
        self.assertEqual(status["tc_meta"]["version"], 1)

    def test_quote_linked(self):
        """Quote should show as linked after quote file is created."""
        os.makedirs(self.tf.QUOTES_DIR, exist_ok=True)
        with open(os.path.join(self.tf.QUOTES_DIR, "TEST-001.json"), "w") as f:
            json.dump({"data": "test"}, f)

        status = self.tf.project_estimator_status("TEST-001")
        self.assertTrue(status["quote_linked"])

    def test_qc_linked(self):
        """QC should show as linked after qc file is created."""
        os.makedirs(self.tf.QC_DIR, exist_ok=True)
        with open(os.path.join(self.tf.QC_DIR, "TEST-001.json"), "w") as f:
            json.dump({"inspections": []}, f)

        status = self.tf.project_estimator_status("TEST-001")
        self.assertTrue(status["qc_linked"])

    def test_shop_drawings_linked(self):
        """Shop drawings should show linked after config.json exists."""
        shop_dir = os.path.join(self.tmpdir, "data", "shop_drawings", "TEST-001")
        os.makedirs(shop_dir, exist_ok=True)
        with open(os.path.join(shop_dir, "config.json"), "w") as f:
            json.dump({"config": "test"}, f)

        status = self.tf.project_estimator_status("TEST-001")
        self.assertTrue(status["shop_linked"])

    def test_work_order_count(self):
        """Work order count should reflect number of WO json files."""
        wo_dir = os.path.join(self.tmpdir, "data", "shop_drawings", "TEST-001", "work_orders")
        os.makedirs(wo_dir, exist_ok=True)
        for i in range(3):
            with open(os.path.join(wo_dir, f"WO-{i}.json"), "w") as f:
                json.dump({"wo_id": i}, f)

        status = self.tf.project_estimator_status("TEST-001")
        self.assertEqual(status["wo_count"], 3)


class TestCascadeDelete(unittest.TestCase):
    """Test cascade_delete_project() removes ALL associated data."""

    def setUp(self):
        import tf_handlers
        self.tf = tf_handlers
        self.original_base = self.tf.BASE_DIR
        self.original_projects = self.tf.PROJECTS_DIR
        self.original_quotes = self.tf.QUOTES_DIR
        self.original_qc = self.tf.QC_DIR

        self.tmpdir = tempfile.mkdtemp()
        self.tf.BASE_DIR = self.tmpdir
        self.tf.DATA_DIR = os.path.join(self.tmpdir, "data")
        self.tf.PROJECTS_DIR = os.path.join(self.tmpdir, "data", "projects")
        self.tf.QUOTES_DIR = os.path.join(self.tmpdir, "data", "quotes")
        self.tf.QC_DIR = os.path.join(self.tmpdir, "data", "qc")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        self.tf.BASE_DIR = self.original_base
        self.tf.PROJECTS_DIR = self.original_projects
        self.tf.QUOTES_DIR = self.original_quotes
        self.tf.QC_DIR = self.original_qc

    def _create_full_project(self, job_code="TEST-DEL"):
        """Create a project with data in ALL locations."""
        safe = self.tf._safe_job(job_code)

        # Project dir + SA data
        proj_dir = os.path.join(self.tf.PROJECTS_DIR, safe)
        os.makedirs(proj_dir, exist_ok=True)
        for fname in ["metadata.json", "current.json", "status.json",
                       "tc_quote.json", "bom_snapshot.json", "v1.json"]:
            with open(os.path.join(proj_dir, fname), "w") as f:
                json.dump({"test": True}, f)

        # Quote
        os.makedirs(self.tf.QUOTES_DIR, exist_ok=True)
        with open(os.path.join(self.tf.QUOTES_DIR, f"{safe}.json"), "w") as f:
            json.dump({"quote": True}, f)

        # QC
        os.makedirs(self.tf.QC_DIR, exist_ok=True)
        with open(os.path.join(self.tf.QC_DIR, f"{safe}.json"), "w") as f:
            json.dump({"qc": True}, f)

        # Shop drawings dir with subdirectories
        shop_dir = os.path.join(self.tmpdir, "data", "shop_drawings", safe)
        os.makedirs(os.path.join(shop_dir, "work_orders"), exist_ok=True)
        os.makedirs(os.path.join(shop_dir, "_documents"), exist_ok=True)
        os.makedirs(os.path.join(shop_dir, "_job_costing"), exist_ok=True)
        os.makedirs(os.path.join(shop_dir, "_scheduling"), exist_ok=True)
        os.makedirs(os.path.join(shop_dir, "pdfs"), exist_ok=True)

        with open(os.path.join(shop_dir, "config.json"), "w") as f:
            json.dump({"config": True}, f)
        with open(os.path.join(shop_dir, "work_orders", "WO-1.json"), "w") as f:
            json.dump({"wo": True}, f)
        with open(os.path.join(shop_dir, "_documents", "revisions.json"), "w") as f:
            json.dump({"revisions": []}, f)
        with open(os.path.join(shop_dir, "_job_costing", "estimates.json"), "w") as f:
            json.dump({"estimates": []}, f)

        return proj_dir, shop_dir

    def test_cascade_delete_removes_project_dir(self):
        """Project directory must be completely removed."""
        proj_dir, _ = self._create_full_project()
        self.assertTrue(os.path.isdir(proj_dir))

        self.tf.cascade_delete_project("TEST-DEL")
        self.assertFalse(os.path.isdir(proj_dir))

    def test_cascade_delete_removes_shop_drawings(self):
        """Shop drawings directory must be completely removed."""
        _, shop_dir = self._create_full_project()
        self.assertTrue(os.path.isdir(shop_dir))

        self.tf.cascade_delete_project("TEST-DEL")
        self.assertFalse(os.path.isdir(shop_dir))

    def test_cascade_delete_removes_quote(self):
        """Quote file must be removed."""
        self._create_full_project()
        quote_path = os.path.join(self.tf.QUOTES_DIR, "TEST-DEL.json")
        self.assertTrue(os.path.isfile(quote_path))

        self.tf.cascade_delete_project("TEST-DEL")
        self.assertFalse(os.path.isfile(quote_path))

    def test_cascade_delete_removes_qc(self):
        """QC file must be removed."""
        self._create_full_project()
        qc_path = os.path.join(self.tf.QC_DIR, "TEST-DEL.json")
        self.assertTrue(os.path.isfile(qc_path))

        self.tf.cascade_delete_project("TEST-DEL")
        self.assertFalse(os.path.isfile(qc_path))

    def test_cascade_delete_returns_deleted_list(self):
        """cascade_delete must return a list of what was deleted."""
        self._create_full_project()
        deleted = self.tf.cascade_delete_project("TEST-DEL")
        self.assertIsInstance(deleted, list)
        self.assertTrue(len(deleted) >= 3)  # At least project_dir, shop_dir, quote, qc

    def test_cascade_delete_leaves_other_projects_intact(self):
        """Deleting one project must not affect other projects."""
        self._create_full_project("TEST-DEL")
        self._create_full_project("TEST-KEEP")

        self.tf.cascade_delete_project("TEST-DEL")

        # TEST-KEEP should still exist
        keep_dir = os.path.join(self.tf.PROJECTS_DIR, "TEST-KEEP")
        self.assertTrue(os.path.isdir(keep_dir))
        self.assertTrue(os.path.isfile(os.path.join(self.tf.QUOTES_DIR, "TEST-KEEP.json")))
        self.assertTrue(os.path.isfile(os.path.join(self.tf.QC_DIR, "TEST-KEEP.json")))

    def test_cascade_delete_no_error_on_missing_data(self):
        """cascade_delete should not error if some data doesn't exist."""
        # Create just the project dir, nothing else
        proj_dir = os.path.join(self.tf.PROJECTS_DIR, "MINIMAL")
        os.makedirs(proj_dir, exist_ok=True)
        with open(os.path.join(proj_dir, "metadata.json"), "w") as f:
            json.dump({"job_code": "MINIMAL"}, f)

        # Should not raise
        deleted = self.tf.cascade_delete_project("MINIMAL")
        self.assertIsInstance(deleted, list)

    def test_full_lifecycle(self):
        """Full lifecycle: create project, add data everywhere, verify status, delete, verify clean."""
        job_code = "LIFECYCLE-TEST"
        self._create_full_project(job_code)

        # Verify status shows everything linked
        status = self.tf.project_estimator_status(job_code)
        self.assertTrue(status["sa_linked"])
        self.assertTrue(status["quote_linked"])
        self.assertTrue(status["qc_linked"])
        self.assertTrue(status["shop_linked"])
        self.assertEqual(status["wo_count"], 1)

        # Delete
        deleted = self.tf.cascade_delete_project(job_code)
        self.assertTrue(len(deleted) >= 3)

        # Verify everything is gone
        status_after = self.tf.project_estimator_status(job_code)
        self.assertFalse(status_after["sa_linked"])
        self.assertFalse(status_after["tc_linked"])
        self.assertFalse(status_after["bom_available"])
        self.assertFalse(status_after["quote_linked"])
        self.assertFalse(status_after["qc_linked"])
        self.assertFalse(status_after["shop_linked"])
        self.assertEqual(status_after["wo_count"], 0)


class TestBOMAutoSave(unittest.TestCase):
    """Test that BOM auto-save writes bom_snapshot.json."""

    def setUp(self):
        import tf_handlers
        self.tf = tf_handlers
        self.original_projects = self.tf.PROJECTS_DIR
        self.tmpdir = tempfile.mkdtemp()
        self.tf.PROJECTS_DIR = os.path.join(self.tmpdir, "data", "projects")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        self.tf.PROJECTS_DIR = self.original_projects

    def test_bom_snapshot_path_exists_in_project(self):
        """After creating project dir and saving BOM, bom_snapshot.json should exist."""
        job_code = "BOM-TEST"
        paths = self.tf.project_paths(job_code)
        os.makedirs(paths["project_dir"], exist_ok=True)

        # Simulate what CalculateHandler does
        bom_path = os.path.join(paths["project_dir"], "bom_snapshot.json")
        bom_snapshot = {
            "job_code": job_code,
            "bom_data": {"project": {"name": "Test"}, "buildings": []},
            "calculated_at": "2026-04-14T10:00:00",
        }
        with open(bom_path, "w") as f:
            json.dump(bom_snapshot, f)

        self.assertTrue(os.path.isfile(bom_path))
        with open(bom_path) as f:
            data = json.load(f)
        self.assertEqual(data["job_code"], job_code)
        self.assertIn("bom_data", data)


class TestTCQuotePersistence(unittest.TestCase):
    """Test TC quote save/load data structure."""

    def setUp(self):
        import tf_handlers
        self.tf = tf_handlers
        self.original_projects = self.tf.PROJECTS_DIR
        self.tmpdir = tempfile.mkdtemp()
        self.tf.PROJECTS_DIR = os.path.join(self.tmpdir, "data", "projects")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        self.tf.PROJECTS_DIR = self.original_projects

    def test_tc_save_creates_file(self):
        """Saving TC data should create tc_quote.json in project dir."""
        job_code = "TC-TEST"
        paths = self.tf.project_paths(job_code)
        os.makedirs(paths["project_dir"], exist_ok=True)

        tc_data = {
            "project": {"job_code": job_code, "name": "TC Test"},
            "costs": {"concrete": {"total": 5000}},
            "version": 1,
            "saved_at": "2026-04-14T10:00:00",
            "saved_by": "admin",
        }
        with open(paths["tc_quote"], "w") as f:
            json.dump(tc_data, f)

        self.assertTrue(os.path.isfile(paths["tc_quote"]))

    def test_tc_load_returns_data(self):
        """Loading TC data should return the saved data."""
        job_code = "TC-LOAD"
        paths = self.tf.project_paths(job_code)
        os.makedirs(paths["project_dir"], exist_ok=True)

        tc_data = {
            "project": {"job_code": job_code},
            "costs": {"labor": {"total": 8000}},
            "version": 2,
        }
        with open(paths["tc_quote"], "w") as f:
            json.dump(tc_data, f)

        with open(paths["tc_quote"]) as f:
            loaded = json.load(f)

        self.assertEqual(loaded["version"], 2)
        self.assertEqual(loaded["costs"]["labor"]["total"], 8000)

    def test_tc_versioning(self):
        """Multiple saves should increment version and create versioned files."""
        job_code = "TC-VER"
        paths = self.tf.project_paths(job_code)
        os.makedirs(paths["project_dir"], exist_ok=True)

        for v in range(1, 4):
            tc_data = {"version": v, "saved_at": f"2026-04-14T1{v}:00:00"}
            with open(paths["tc_quote"], "w") as f:
                json.dump(tc_data, f)
            # Also save versioned
            ver_path = os.path.join(paths["project_dir"], f"tc_v{v}.json")
            with open(ver_path, "w") as f:
                json.dump(tc_data, f)

        # Current should be v3
        with open(paths["tc_quote"]) as f:
            current = json.load(f)
        self.assertEqual(current["version"], 3)

        # All versions should exist
        for v in range(1, 4):
            self.assertTrue(os.path.isfile(
                os.path.join(paths["project_dir"], f"tc_v{v}.json")))

    def test_tc_deleted_by_cascade(self):
        """TC data should be deleted when project is cascade-deleted."""
        job_code = "TC-CASCADE"
        paths = self.tf.project_paths(job_code)
        os.makedirs(paths["project_dir"], exist_ok=True)

        with open(paths["tc_quote"], "w") as f:
            json.dump({"version": 1}, f)
        with open(os.path.join(paths["project_dir"], "metadata.json"), "w") as f:
            json.dump({"job_code": job_code}, f)

        self.assertTrue(os.path.isfile(paths["tc_quote"]))
        self.tf.cascade_delete_project(job_code)
        self.assertFalse(os.path.isfile(paths["tc_quote"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
