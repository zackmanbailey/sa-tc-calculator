"""
TitanForge v4 — Project Completion Tracker
=============================================
Monitor field installation progress and sign-offs.
"""

FIELD_COMPLETION_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .completion-container {
        max-width: 1400px;
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
    .completion-card {
        background: var(--tf-card);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 0;
        overflow: hidden;
    }
    .completion-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }
    .completion-table thead th {
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
    .completion-table tbody td {
        padding: 14px 16px;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        color: var(--tf-text);
        vertical-align: middle;
    }
    .completion-table tbody tr { cursor: pointer; transition: background 0.15s; }
    .completion-table tbody tr:hover { background: rgba(255,255,255,0.05); }
    .stage-badge { cursor: pointer; transition: opacity 0.15s; }
    .stage-badge:hover { opacity: 0.8; }
    .progress-wrap {
        display: flex; align-items: center; gap: 10px;
    }
    .progress-bar {
        flex: 1; height: 10px; background: rgba(255,255,255,0.06);
        border-radius: 5px; overflow: hidden; min-width: 120px;
    }
    .progress-fill {
        height: 100%; border-radius: 5px; transition: width 0.4s;
    }
    .progress-pct { font-weight: 700; font-size: 13px; min-width: 42px; text-align: right; }
    .fill-green { background: #22c55e; }
    .fill-gold { background: var(--tf-gold); }
    .fill-blue { background: var(--tf-blue); }
    .fill-red { background: #ef4444; }
    .stage-badge {
        display: inline-block; padding: 4px 10px; border-radius: 6px;
        font-size: 12px; font-weight: 600;
    }
    .stage-fab { background: rgba(59,130,246,0.2); color: #60a5fa; }
    .stage-ship { background: rgba(168,85,247,0.2); color: #c084fc; }
    .stage-install { background: rgba(212,168,67,0.2); color: #d4a843; }
    .stage-complete { background: rgba(34,197,94,0.2); color: #4ade80; }
    .stage-default { background: rgba(148,163,184,0.2); color: #94a3b8; }
    .loading { text-align: center; padding: 60px; color: var(--tf-muted); }
    .empty-state {
        text-align: center; padding: 60px 20px; color: var(--tf-muted);
    }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
</style>

<div class="completion-container">
    <div class="page-header">
        <h1>Project Completion Tracker</h1>
        <p>Monitor field installation progress and sign-offs</p>
    </div>
    <div class="completion-card">
        <div id="completionWrap" class="loading">Loading projects...</div>
    </div>
</div>

<script>
function stageClass(stage) {
    if (!stage) return 'stage-default';
    const s = stage.toLowerCase();
    if (s.includes('fab') || s.includes('production')) return 'stage-fab';
    if (s.includes('ship')) return 'stage-ship';
    if (s.includes('install')) return 'stage-install';
    if (s.includes('complete')) return 'stage-complete';
    return 'stage-default';
}

function estimateProgress(stage) {
    if (!stage) return 0;
    const s = stage.toLowerCase();
    if (s.includes('complete')) return 100;
    if (s.includes('install')) return 75;
    if (s.includes('ship')) return 55;
    if (s.includes('fab') || s.includes('production')) return 35;
    if (s.includes('draft') || s.includes('quote')) return 10;
    return 20;
}

function fillClass(pct) {
    if (pct >= 100) return 'fill-green';
    if (pct >= 60) return 'fill-gold';
    if (pct >= 30) return 'fill-blue';
    return 'fill-red';
}

async function loadCompletion() {
    const wrap = document.getElementById('completionWrap');
    try {
        const resp = await fetch('/api/projects/full');
        const data = await resp.json();
        const projects = Array.isArray(data) ? data : (data.projects || []);
        allCompletionProjects = projects;
        if (!projects.length) {
            wrap.innerHTML = '<div class="empty-state"><h3>No projects found</h3><p>Projects will appear here once created.</p></div>';
            return;
        }
        let html = '<table class="completion-table"><thead><tr>' +
            '<th>Project</th><th>Stage</th><th>Progress</th><th>Last Updated</th>' +
            '</tr></thead><tbody>';
        projects.forEach(p => {
            const stage = p.stage || p.status || '';
            const pct = p.completion_pct != null ? Math.round(p.completion_pct) : estimateProgress(stage);
            const updated = p.updated_at || p.last_updated || p.modified || '—';
            const jobCode = p.job_code || p.id || '';
            html += '<tr onclick="window.location.href=\'/field/ops?project=' + encodeURIComponent(jobCode) + '\'">' +
                '<td style="font-weight:600">' + (p.project_name || p.name || p.job_code || '—') + '</td>' +
                '<td><span class="stage-badge ' + stageClass(stage) + '" onclick="event.stopPropagation(); filterByStage(\'' + stage + '\')">' + (stage || 'Unknown') + '</span></td>' +
                '<td><div class="progress-wrap">' +
                    '<div class="progress-bar"><div class="progress-fill ' + fillClass(pct) + '" style="width:' + pct + '%"></div></div>' +
                    '<span class="progress-pct">' + pct + '%</span>' +
                '</div></td>' +
                '<td style="color:var(--tf-muted);font-size:13px">' + updated + '</td>' +
                '</tr>';
        });
        html += '</tbody></table>';
        wrap.innerHTML = html;
    } catch (err) {
        wrap.innerHTML = '<div class="empty-state"><h3>Unable to load projects</h3><p>' + err.message + '</p></div>';
    }
}

var allCompletionProjects = [];

function filterByStage(stage) {
    if (!allCompletionProjects.length) return;
    const wrap = document.getElementById('completionWrap');
    const filtered = allCompletionProjects.filter(p => {
        const s = (p.stage || p.status || '').toLowerCase();
        return s.toLowerCase() === stage.toLowerCase();
    });
    if (!filtered.length) {
        wrap.innerHTML = '<div class="empty-state"><h3>No projects in stage: ' + stage + '</h3><p><a href="#" onclick="loadCompletion(); return false;" style="color:var(--tf-blue);">Show all projects</a></p></div>';
        return;
    }
    renderCompletionTable(filtered, wrap);
}

function renderCompletionTable(projects, wrap) {
    let html = '<table class="completion-table"><thead><tr>' +
        '<th>Project</th><th>Stage</th><th>Progress</th><th>Last Updated</th>' +
        '</tr></thead><tbody>';
    projects.forEach(p => {
        const stage = p.stage || p.status || '';
        const pct = p.completion_pct != null ? Math.round(p.completion_pct) : estimateProgress(stage);
        const updated = p.updated_at || p.last_updated || p.modified || '—';
        const jobCode = p.job_code || p.id || '';
        html += '<tr onclick="window.location.href=\'/field/ops?project=' + encodeURIComponent(jobCode) + '\'">' +
            '<td style="font-weight:600">' + (p.project_name || p.name || p.job_code || '—') + '</td>' +
            '<td><span class="stage-badge ' + stageClass(stage) + '" onclick="event.stopPropagation(); filterByStage(\'' + stage + '\')">' + (stage || 'Unknown') + '</span></td>' +
            '<td><div class="progress-wrap">' +
                '<div class="progress-bar"><div class="progress-fill ' + fillClass(pct) + '" style="width:' + pct + '%"></div></div>' +
                '<span class="progress-pct">' + pct + '%</span>' +
            '</div></td>' +
            '<td style="color:var(--tf-muted);font-size:13px">' + updated + '</td>' +
            '</tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;
}

loadCompletion();
</script>
"""
