"""
TitanForge v4 — Punch List
=============================
Track field installation punch list items.
"""

FIELD_PUNCH_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .punch-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 {
        font-size: 28px; font-weight: 800; margin: 0 0 6px 0; color: var(--tf-text);
    }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
    }
    .project-select {
        background: var(--tf-card);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 10px 16px;
        color: var(--tf-text);
        font-size: 14px;
        min-width: 260px;
    }
    .project-select option { background: var(--tf-card); color: var(--tf-text); }
    .btn-gold {
        background: var(--tf-gold);
        color: #0f172a;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 700;
        font-size: 14px;
        cursor: pointer;
    }
    .btn-gold:hover { opacity: 0.9; }
    .punch-card {
        background: var(--tf-card);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 24px;
    }
    .punch-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }
    .punch-table thead th {
        background: #1a2744;
        padding: 14px 16px;
        text-align: left;
        font-weight: 700;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--tf-muted);
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .punch-table tbody td {
        padding: 12px 16px;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        color: var(--tf-text);
    }
    .empty-state {
        text-align: center; padding: 60px 20px; color: var(--tf-muted);
    }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .empty-state p { margin-bottom: 20px; }
    .priority-high { color: #f87171; font-weight: 600; }
    .priority-medium { color: var(--tf-gold); font-weight: 600; }
    .priority-low { color: #4ade80; font-weight: 600; }
</style>

<div class="punch-container">
    <div class="page-header">
        <h1>Punch List</h1>
        <p>Track field installation punch list items</p>
    </div>
    <div class="toolbar">
        <select id="projectSelector" class="project-select" onchange="filterByProject()">
            <option value="">All Projects</option>
        </select>
        <button class="btn-gold" onclick="addItem()">+ Add Item</button>
    </div>
    <div class="punch-card">
        <div id="punchContent">
            <div class="empty-state">
                <h3>No punch list items yet</h3>
                <p>Punch list items will appear here as they are created during field installation.</p>
                <button class="btn-gold" onclick="addItem()">+ Add Item</button>
            </div>
        </div>
    </div>
</div>

<script>
async function loadProjects() {
    try {
        const resp = await fetch('/api/projects');
        const data = await resp.json();
        const projects = Array.isArray(data) ? data : (data.projects || []);
        const sel = document.getElementById('projectSelector');
        projects.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id || p.job_code || '';
            opt.textContent = (p.job_code ? p.job_code + ' — ' : '') + (p.project_name || p.name || 'Unnamed');
            sel.appendChild(opt);
        });
    } catch (err) {
        console.error('Failed to load projects:', err);
    }
}

function filterByProject() {
    // Placeholder — will filter punch items when backend is ready
}

function addItem() {
    alert('Coming soon — punch list item creation will be available in a future update.');
}

loadProjects();
</script>
"""
