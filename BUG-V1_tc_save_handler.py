"""
BUG-V1 FIX: Add TC Quote Save/Load Handler
=============================================
File: combined_calc/tf_handlers.py + combined_calc/templates/tc_quote.py
Severity: MEDIUM (functional, bad UX — users can export PDF/Excel but can't save drafts)
Discovered: Post-patch verification, April 15, 2026

PROBLEM:
  The TC Estimator page (/tc) has no save functionality. Users can fill out the
  entire TC quote form but lose all data when navigating away. The only way to
  preserve data is to export as PDF or Excel, which can't be re-imported.

  Patch 09 from the original package documented this issue but the handler was
  never actually added to tf_handlers.py.

ROOT CAUSE:
  - No TCQuoteSaveHandler class exists in tf_handlers.py
  - No /api/tc/save or /api/tc/load route is registered in get_routes()
  - The tc_quote.py template has no save button or save function

FIX — 3 CHANGES REQUIRED:

═══════════════════════════════════════════
CHANGE 1: Add handler class to tf_handlers.py
═══════════════════════════════════════════
Insert AFTER TCExportExcelHandler class (around line 1908), BEFORE the
"PROJECT CREATE" section:

------- START PASTE (tf_handlers.py, after line ~1908) -------
"""

TC_SAVE_HANDLER_CODE = '''
class TCQuoteSaveHandler(BaseHandler):
    """POST /api/tc/save — Save TC Quote data as JSON."""
    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            if not job_code:
                self.set_header("Content-Type", "application/json")
                self.write(json_encode({"ok": False, "error": "job_code is required"}))
                return

            project_dir = os.path.join(BASE_DIR, "data", "projects", job_code)
            os.makedirs(project_dir, exist_ok=True)

            tc_path = os.path.join(project_dir, "tc_quote.json")
            with open(tc_path, "w") as f:
                json.dump(body.get("data", {}), f, indent=2)

            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True}))
        except Exception as e:
            import traceback
            self.set_header("Content-Type", "application/json")
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


class TCQuoteLoadHandler(BaseHandler):
    """GET /api/tc/load?job_code=XXX — Load saved TC Quote data."""
    def get(self):
        job_code = self.get_argument("job_code", "").strip()
        if not job_code:
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": False, "error": "job_code required"}))
            return

        tc_path = os.path.join(BASE_DIR, "data", "projects", job_code, "tc_quote.json")
        if os.path.exists(tc_path):
            with open(tc_path, "r") as f:
                data = json.load(f)
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": True, "data": data}))
        else:
            self.set_header("Content-Type", "application/json")
            self.write(json_encode({"ok": False, "error": "No saved TC quote found"}))
'''

"""
------- END PASTE -------


═══════════════════════════════════════════
CHANGE 2: Add routes to get_routes() in tf_handlers.py
═══════════════════════════════════════════
Find the TC export routes section (around line 5742-5744) and add:

    (r"/api/tc/save",               TCQuoteSaveHandler),
    (r"/api/tc/load",               TCQuoteLoadHandler),

Place them after the existing TC route:
    (r"/tc",                    TCQuoteHandler),
    (r"/api/tc/save",           TCQuoteSaveHandler),    # <-- ADD
    (r"/api/tc/load",           TCQuoteLoadHandler),    # <-- ADD


═══════════════════════════════════════════
CHANGE 3: Add Save button + functions to tc_quote.py template
═══════════════════════════════════════════
In combined_calc/templates/tc_quote.py, find the export buttons section:

    <button class="btn btn-outline btn-sm" onclick="tcExportPDF()">⬇ PDF</button>
    <button class="btn btn-outline btn-sm" onclick="tcExportExcel()">⬇ Excel</button>

Add a Save Draft button BEFORE the PDF button:

    <button class="btn btn-green btn-sm" onclick="tcSaveDraft()">💾 Save Draft</button>
    <button class="btn btn-outline btn-sm" onclick="tcExportPDF()">⬇ PDF</button>
    <button class="btn btn-outline btn-sm" onclick="tcExportExcel()">⬇ Excel</button>

Then add the save/load JavaScript functions before the closing </script> tag:

------- START PASTE (tc_quote.py, before </script>) -------
"""

TC_SAVE_JS_CODE = '''
// ── TC Save/Load ──
async function tcSaveDraft() {
  const jobCode = strVal('proj_code');
  if (!jobCode) { alert('Please enter a Project Code first.'); return; }
  try {
    const payload = buildPayload();
    const resp = await fetch('/api/tc/save', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ job_code: jobCode, data: payload })
    });
    const d = await resp.json();
    if (d.ok) {
      const btn = event.target;
      const orig = btn.textContent;
      btn.textContent = '✓ Saved!';
      btn.style.background = '#22c55e';
      setTimeout(() => { btn.textContent = orig; btn.style.background = ''; }, 2000);
    } else {
      alert('Save failed: ' + (d.error || 'unknown error'));
    }
  } catch(e) { alert('Save failed: ' + e.message); }
}

async function tcLoadDraft() {
  const jobCode = strVal('proj_code');
  if (!jobCode) return;
  try {
    const resp = await fetch('/api/tc/load?job_code=' + encodeURIComponent(jobCode));
    const d = await resp.json();
    if (d.ok && d.data) {
      // Restore form fields from saved data
      const p = d.data.project || {};
      if (p.name) document.getElementById('proj_name').value = p.name;
      if (p.location) document.getElementById('proj_location').value = p.location;
      // Additional field restoration can be added here
      console.log('[TC] Loaded saved draft for', jobCode);
    }
  } catch(e) { console.warn('[TC] No saved draft:', e); }
}
'''

"""
------- END PASTE -------

Also add auto-load on DOMContentLoaded. Find:
    window.addEventListener('DOMContentLoaded', () => {

And add after the existing init code:
    // Auto-load saved TC draft if project code exists
    tcLoadDraft();

═══════════════════════════════════════════
VERIFICATION:
═══════════════════════════════════════════
After applying:
1. Navigate to /tc?project=SIM-001
2. Fill in some TC fields
3. Click "Save Draft" — should show green "✓ Saved!" flash
4. Navigate away and return to /tc?project=SIM-001
5. Previously saved data should auto-load
6. Check data/projects/SIM-001/tc_quote.json exists
"""
