"""
TitanForge v4 — Project Timeline
==================================
Multi-project Gantt-style view with milestones, dependencies, critical path.
"""

TIMELINE_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .timeline-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .toolbar input[type="text"], .toolbar input[type="date"] { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; }
    .toolbar input::placeholder { color: var(--tf-muted); }
    .toolbar select { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; }
    .btn-gold { background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-gold:hover { opacity: 0.9; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .gantt-wrapper {
        background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);
        overflow-x: auto; position: relative;
    }
    .gantt-header { display: flex; border-bottom: 1px solid rgba(255,255,255,0.06); }
    .gantt-label-col { min-width: 220px; width: 220px; padding: 12px 16px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--tf-muted); background: #1a2744; flex-shrink: 0; }
    .gantt-dates { display: flex; flex: 1; }
    .gantt-date-cell { min-width: 40px; padding: 12px 4px; text-align: center; font-size: 11px; color: var(--tf-muted); background: #1a2744; border-left: 1px solid rgba(255,255,255,0.03); }
    .gantt-date-cell.today { background: rgba(59,130,246,0.15); color: var(--tf-blue); font-weight: 700; }
    .gantt-row { display: flex; border-bottom: 1px solid rgba(255,255,255,0.04); min-height: 44px; align-items: center; }
    .gantt-row:hover { background: rgba(255,255,255,0.02); }
    .gantt-row-label { min-width: 220px; width: 220px; padding: 8px 16px; font-size: 13px; font-weight: 600; flex-shrink: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer; }
    .gantt-row-label:hover { color: var(--tf-blue); }
    .gantt-row-bars { display: flex; flex: 1; position: relative; height: 44px; }
    .gantt-bar {
        position: absolute; height: 24px; top: 10px; border-radius: 6px; min-width: 20px;
        font-size: 11px; color: #fff; display: flex; align-items: center; padding: 0 8px;
        cursor: pointer; transition: opacity 0.2s;
    }
    .gantt-bar:hover { opacity: 0.8; }
    .gantt-bar.bar-blue { background: var(--tf-blue); }
    .gantt-bar.bar-gold { background: var(--tf-gold); color: #0f172a; }
    .gantt-bar.bar-green { background: #22c55e; }
    .gantt-bar.bar-red { background: #ef4444; }
    .gantt-bar.bar-critical { background: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.4); }
    .milestone-marker { position: absolute; top: 12px; width: 18px; height: 18px; background: var(--tf-gold); transform: rotate(45deg); border-radius: 3px; cursor: pointer; }
    .legend { display: flex; gap: 20px; margin-top: 16px; flex-wrap: wrap; }
    .legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--tf-muted); }
    .legend-dot { width: 12px; height: 12px; border-radius: 3px; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); }
</style>

<div class="timeline-container">
    <div class="page-header">
        <h1>Project Timeline</h1>
        <p>Multi-project Gantt view with milestones and dependencies</p>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;">
            <input type="text" id="tlSearch" placeholder="Search projects..." oninput="filterTimeline()">
            <input type="date" id="tlDateFrom" onchange="rerender()">
            <input type="date" id="tlDateTo" onchange="rerender()">
            <select id="tlZoom" onchange="rerender()">
                <option value="day">Day</option>
                <option value="week" selected>Week</option>
                <option value="month">Month</option>
            </select>
        </div>
        <div style="display:flex;gap:10px;">
            <button class="btn-outline" onclick="toggleCriticalPath()">Show Critical Path</button>
            <button class="btn-gold" onclick="exportTimeline()">Export</button>
        </div>
    </div>
    <div class="gantt-wrapper" id="ganttWrapper">
        <div class="loading">Loading timeline...</div>
    </div>
    <div class="legend">
        <div class="legend-item"><div class="legend-dot" style="background:var(--tf-blue);"></div>Fabrication</div>
        <div class="legend-item"><div class="legend-dot" style="background:#22c55e;"></div>Complete</div>
        <div class="legend-item"><div class="legend-dot" style="background:var(--tf-gold);"></div>Install</div>
        <div class="legend-item"><div class="legend-dot" style="background:#ef4444;"></div>Critical / Delayed</div>
        <div class="legend-item"><div class="legend-dot" style="background:var(--tf-gold);transform:rotate(45deg);width:10px;height:10px;"></div>Milestone</div>
    </div>
</div>

<script>
let allProjects = [];
let showCritical = false;

function daysBetween(a, b) { return Math.round((new Date(b) - new Date(a)) / 86400000); }

function generateDates(start, end) {
    const dates = [];
    let d = new Date(start);
    const e = new Date(end);
    while (d <= e) { dates.push(new Date(d)); d.setDate(d.getDate() + 1); }
    return dates;
}

function formatShortDate(d) {
    return (d.getMonth()+1) + '/' + d.getDate();
}

function renderGantt(projects) {
    const wrapper = document.getElementById('ganttWrapper');
    if (!projects.length) {
        wrapper.innerHTML = '<div class="empty-state"><h3>No projects found</h3><p>Projects with start and end dates will appear here.</p></div>';
        return;
    }
    const allDates = [];
    projects.forEach(p => {
        if (p.start_date) allDates.push(new Date(p.start_date));
        if (p.end_date) allDates.push(new Date(p.end_date));
    });
    if (!allDates.length) { wrapper.innerHTML = '<div class="empty-state"><h3>No date ranges found</h3><p>Add start/end dates to projects.</p></div>'; return; }
    const fromInput = document.getElementById('tlDateFrom').value;
    const toInput = document.getElementById('tlDateTo').value;
    let minDate = fromInput ? new Date(fromInput) : new Date(Math.min(...allDates));
    let maxDate = toInput ? new Date(toInput) : new Date(Math.max(...allDates));
    minDate.setDate(minDate.getDate() - 3);
    maxDate.setDate(maxDate.getDate() + 7);
    const dates = generateDates(minDate, maxDate);
    const todayStr = new Date().toISOString().slice(0,10);
    const cellWidth = 40;
    let html = '<div class="gantt-header"><div class="gantt-label-col">Project</div><div class="gantt-dates">';
    dates.forEach(d => {
        const isToday = d.toISOString().slice(0,10) === todayStr;
        html += '<div class="gantt-date-cell' + (isToday ? ' today' : '') + '" style="min-width:' + cellWidth + 'px;">' + formatShortDate(d) + '</div>';
    });
    html += '</div></div>';

    projects.forEach(p => {
        const start = p.start_date ? new Date(p.start_date) : null;
        const end = p.end_date ? new Date(p.end_date) : null;
        html += '<div class="gantt-row"><div class="gantt-row-label" title="' + (p.project_name || p.name || '') + '" onclick="window.location.href=\'/project/' + (p.id || '') + '\'">' + (p.project_name || p.name || 'Unnamed') + '</div>';
        html += '<div class="gantt-row-bars" style="width:' + (dates.length * cellWidth) + 'px;">';
        if (start && end) {
            const offsetDays = daysBetween(minDate, start);
            const durDays = Math.max(daysBetween(start, end), 1);
            const left = offsetDays * cellWidth;
            const width = durDays * cellWidth;
            const pct = p.progress || 0;
            let barClass = 'bar-blue';
            if (pct >= 100) barClass = 'bar-green';
            else if (showCritical && p.is_critical) barClass = 'bar-critical';
            html += '<div class="gantt-bar ' + barClass + '" style="left:' + left + 'px;width:' + width + 'px;" title="' + (p.project_name||'') + ' (' + pct + '%)">' + (width > 60 ? (p.job_code || '') : '') + '</div>';
        }
        if (p.milestones) {
            p.milestones.forEach(m => {
                const mDate = new Date(m.date);
                const mOffset = daysBetween(minDate, mDate) * cellWidth;
                html += '<div class="milestone-marker" style="left:' + mOffset + 'px;" title="' + (m.name || 'Milestone') + '"></div>';
            });
        }
        html += '</div></div>';
    });
    wrapper.innerHTML = html;
}

function filterTimeline() {
    const search = document.getElementById('tlSearch').value.toLowerCase();
    const filtered = allProjects.filter(p => !search || (p.project_name||p.name||'').toLowerCase().includes(search) || (p.job_code||'').toLowerCase().includes(search));
    renderGantt(filtered);
}

function rerender() { filterTimeline(); }
function toggleCriticalPath() { showCritical = !showCritical; filterTimeline(); }

function exportTimeline() {
    const rows = [['Project','Job Code','Start','End','Progress']];
    allProjects.forEach(p => rows.push([p.project_name||p.name||'',p.job_code||'',p.start_date||'',p.end_date||'',(p.progress||0)+'%']));
    const csv = rows.map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], {type:'text/csv'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'timeline.csv'; a.click();
}

async function loadTimeline() {
    try {
        const resp = await fetch('/api/timeline');
        const data = await resp.json();
        allProjects = Array.isArray(data) ? data : (data.projects || []);
        renderGantt(allProjects);
    } catch(e) {
        try {
            const resp2 = await fetch('/api/projects/full');
            const data2 = await resp2.json();
            allProjects = Array.isArray(data2) ? data2 : (data2.projects || []);
            renderGantt(allProjects);
        } catch(e2) {
            document.getElementById('ganttWrapper').innerHTML = '<div class="empty-state"><h3>Unable to load timeline</h3><p>' + e2.message + '</p></div>';
        }
    }
}

loadTimeline();
</script>
"""
