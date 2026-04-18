"""
TitanForge v4 — Install Tracker
==================================
Track installation crew assignments and schedules.
"""

FIELD_INSTALL_TRACKER_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .tracker-container {
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
    .summary-bar {
        display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap;
    }
    .summary-pill {
        background: var(--tf-card);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 14px 22px;
        text-align: center;
        min-width: 140px;
        cursor: pointer; transition: border-color 0.15s, background 0.15s;
    }
    .summary-pill:hover { border-color: rgba(212,168,67,0.4); background: rgba(212,168,67,0.06); }
    .summary-pill.active { border-color: var(--tf-gold); background: rgba(212,168,67,0.1); }
    .summary-pill .num {
        font-size: 24px; font-weight: 800; color: var(--tf-gold);
    }
    .summary-pill .lbl {
        font-size: 12px; color: var(--tf-muted); margin-top: 4px;
    }
    .project-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
        gap: 20px;
    }
    .install-card {
        background: var(--tf-card);
        border-radius: 12px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.06);
        cursor: pointer; transition: border-color 0.15s, transform 0.15s;
    }
    .install-card:hover { border-color: rgba(212,168,67,0.3); transform: translateY(-2px); }
    .card-title {
        font-size: 16px; font-weight: 700; margin: 0 0 4px 0; color: var(--tf-text);
    }
    .card-code {
        font-size: 12px; color: var(--tf-muted); margin-bottom: 16px;
    }
    .card-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 6px 0; font-size: 14px;
    }
    .card-row .label { color: var(--tf-muted); }
    .card-row .value { font-weight: 600; }
    .stage-badge {
        display: inline-block; padding: 4px 10px; border-radius: 6px;
        font-size: 12px; font-weight: 600;
    }
    .stage-shipping { background: rgba(168,85,247,0.2); color: #c084fc; }
    .stage-install { background: rgba(212,168,67,0.2); color: #d4a843; }
    .stage-complete { background: rgba(34,197,94,0.2); color: #4ade80; }
    .progress-bar {
        width: 100%; height: 8px; background: rgba(255,255,255,0.06);
        border-radius: 4px; margin-top: 14px; overflow: hidden;
    }
    .progress-fill {
        height: 100%; border-radius: 4px; background: var(--tf-gold);
    }
    .loading { text-align: center; padding: 60px; color: var(--tf-muted); }
    .empty-state {
        text-align: center; padding: 60px 20px; color: var(--tf-muted);
    }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
</style>

<div class="tracker-container">
    <div class="page-header">
        <h1>Install Tracker</h1>
        <p>Track installation crew assignments and schedules</p>
    </div>
    <div id="summaryBar" class="summary-bar" style="display:none"></div>
    <div id="projectGrid" class="loading">Loading install projects...</div>
</div>

<script>
function stageLabel(stage) {
    if (!stage) return 'Unknown';
    const s = stage.toLowerCase();
    if (s.includes('ship')) return 'SHIPPING';
    if (s.includes('install')) return 'INSTALL';
    if (s.includes('complete')) return 'COMPLETE';
    return stage;
}

function stageClass(stage) {
    const s = (stage || '').toLowerCase();
    if (s.includes('ship')) return 'stage-shipping';
    if (s.includes('install')) return 'stage-install';
    if (s.includes('complete')) return 'stage-complete';
    return '';
}

function estimateProgress(stage) {
    const s = (stage || '').toLowerCase();
    if (s.includes('complete')) return 100;
    if (s.includes('install')) return 65;
    if (s.includes('ship')) return 35;
    return 0;
}

async function loadInstallProjects() {
    const wrap = document.getElementById('projectGrid');
    const bar = document.getElementById('summaryBar');
    try {
        const resp = await fetch('/api/projects/full');
        const data = await resp.json();
        const all = Array.isArray(data) ? data : (data.projects || []);
        const installStages = ['shipping', 'ship', 'install', 'complete'];
        const projects = all.filter(p => {
            const s = (p.stage || p.status || '').toLowerCase();
            return installStages.some(st => s.includes(st));
        });
        if (!projects.length) {
            wrap.className = '';
            wrap.innerHTML = '<div class="empty-state"><h3>No active install projects</h3><p>Projects in SHIPPING, INSTALL, or COMPLETE stages will appear here.</p></div>';
            return;
        }
        // Summary
        const shipping = projects.filter(p => (p.stage||'').toLowerCase().includes('ship')).length;
        const installing = projects.filter(p => (p.stage||'').toLowerCase().includes('install')).length;
        const completed = projects.filter(p => (p.stage||'').toLowerCase().includes('complete')).length;
        bar.style.display = 'flex';
        bar.innerHTML =
            '<div class="summary-pill" onclick="filterInstallCards(\'all\')" data-filter="all"><div class="num">' + projects.length + '</div><div class="lbl">Total</div></div>' +
            '<div class="summary-pill" onclick="filterInstallCards(\'ship\')" data-filter="ship"><div class="num">' + shipping + '</div><div class="lbl">Shipping</div></div>' +
            '<div class="summary-pill" onclick="filterInstallCards(\'install\')" data-filter="install"><div class="num">' + installing + '</div><div class="lbl">Installing</div></div>' +
            '<div class="summary-pill" onclick="filterInstallCards(\'complete\')" data-filter="complete"><div class="num">' + completed + '</div><div class="lbl">Completed</div></div>';

        allInstallProjects = projects;
        wrap.className = 'project-grid';
        wrap.innerHTML = projects.map(p => {
            const stage = p.stage || p.status || '';
            const pct = p.completion_pct != null ? Math.round(p.completion_pct) : estimateProgress(stage);
            const jobCode = p.job_code || p.id || '';
            return '<div class="install-card" data-stage="' + stage.toLowerCase() + '" onclick="window.location.href=\'/projects/' + encodeURIComponent(jobCode) + '\'">' +
                '<h3 class="card-title">' + (p.project_name || p.name || 'Unnamed') + '</h3>' +
                '<div class="card-code">' + (p.job_code || p.id || '') + '</div>' +
                '<div class="card-row"><span class="label">Customer</span><span class="value">' + (p.customer || p.customer_name || '—') + '</span></div>' +
                '<div class="card-row"><span class="label">Stage</span><span class="stage-badge ' + stageClass(stage) + '">' + stageLabel(stage) + '</span></div>' +
                '<div class="card-row"><span class="label">Crew</span><span class="value">' + (p.crew || p.install_crew || '—') + '</span></div>' +
                '<div class="card-row"><span class="label">Install Date</span><span class="value">' + (p.install_date || p.scheduled_install || '—') + '</span></div>' +
                '<div class="card-row"><span class="label">Progress</span><span class="value">' + pct + '%</span></div>' +
                '<div class="progress-bar"><div class="progress-fill" style="width:' + pct + '%"></div></div>' +
                '</div>';
        }).join('');
    } catch (err) {
        wrap.className = '';
        wrap.innerHTML = '<div class="empty-state"><h3>Unable to load projects</h3><p>' + err.message + '</p></div>';
    }
}

var allInstallProjects = [];

function filterInstallCards(filter) {
    // Highlight active pill
    document.querySelectorAll('.summary-pill').forEach(p => p.classList.remove('active'));
    const activePill = document.querySelector('.summary-pill[data-filter="' + filter + '"]');
    if (activePill) activePill.classList.add('active');

    const cards = document.querySelectorAll('.install-card');
    cards.forEach(card => {
        const stage = card.getAttribute('data-stage') || '';
        if (filter === 'all') {
            card.style.display = '';
        } else {
            card.style.display = stage.includes(filter) ? '' : 'none';
        }
    });
}

loadInstallProjects();
</script>
"""
