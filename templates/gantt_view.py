"""
TitanForge v3.0 — Multi-Job Gantt View / Scheduling Page
==========================================================
Production schedule visualization showing all active jobs,
fabrication timeline, machine utilization, and capacity warnings.

Renders a horizontal Gantt chart with job bars, due dates, and today marker.
Includes machine utilization heat map and capacity indicators.
"""

from templates.shared_styles import DESIGN_SYSTEM_CSS

GANTT_VIEW_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TitanForge — Production Schedule</title>
<style>
""" + DESIGN_SYSTEM_CSS + """

/* ── Gantt View Container ─────────────────────────────── */
body {
    background: var(--tf-navy);
    color: var(--tf-gray-100);
}

.gantt-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    margin-left: 240px;
    transition: margin-left 0.25s cubic-bezier(0.4,0,0.2,1);
}

.tf-sidebar.collapsed ~ .gantt-container {
    margin-left: 60px;
}

.gantt-header {
    padding: 20px;
    background: var(--tf-navy-light);
    border-bottom: 1px solid var(--tf-gray-700);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 15px;
}

.gantt-header h1 {
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--tf-gray-100);
    margin: 0;
}

.gantt-header-controls {
    display: flex;
    align-items: center;
    gap: 12px;
}

.date-range-input, .view-toggle {
    background: var(--tf-navy);
    border: 1px solid var(--tf-gray-700);
    color: var(--tf-gray-100);
    padding: 8px 12px;
    border-radius: var(--tf-radius);
    font-size: var(--tf-text-base);
    cursor: pointer;
    transition: all 0.15s;
}

.date-range-input:hover, .view-toggle:hover {
    border-color: #F6AE2D;
    background: rgba(246, 174, 45, 0.05);
}

.view-toggle.active {
    background: #F6AE2D;
    color: var(--tf-navy);
    font-weight: 600;
}

/* ── Main Content Area ────────────────────────────────── */
.gantt-main {
    display: flex;
    flex: 1;
    overflow: hidden;
}

/* ── Sidebar: Job List ────────────────────────────────── */
.gantt-sidebar {
    width: 280px;
    background: var(--tf-navy);
    border-right: 1px solid var(--tf-gray-700);
    overflow-y: auto;
    padding: 12px;
}

.gantt-sidebar h3 {
    font-size: var(--tf-text-sm);
    font-weight: 700;
    color: #F6AE2D;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0 0 10px 0;
    padding: 0 8px;
}

.job-item {
    background: var(--tf-navy-light);
    border: 1px solid var(--tf-gray-700);
    border-radius: var(--tf-radius);
    padding: 12px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.15s;
}

.job-item:hover {
    border-color: #F6AE2D;
    background: rgba(246, 174, 45, 0.05);
}

.job-item.selected {
    border-color: #F6AE2D;
    background: rgba(246, 174, 45, 0.1);
    box-shadow: 0 0 12px rgba(246, 174, 45, 0.15);
}

.job-code {
    font-weight: 700;
    color: var(--tf-gray-100);
    font-size: var(--tf-text-base);
    margin-bottom: 2px;
}

.job-customer {
    font-size: var(--tf-text-xs);
    color: var(--tf-gray-400);
    margin-bottom: 4px;
}

.job-due {
    font-size: var(--tf-text-xs);
    color: #F6AE2D;
}

/* ── Timeline Area ────────────────────────────────────── */
.gantt-timeline {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.gantt-time-header {
    height: 60px;
    background: var(--tf-navy-light);
    border-bottom: 1px solid var(--tf-gray-700);
    display: flex;
    align-items: flex-end;
    overflow-x: auto;
    overflow-y: hidden;
    position: relative;
}

.gantt-time-header::after {
    content: '';
    position: absolute;
    height: 100%;
    width: 3px;
    background: #F6AE2D;
    left: var(--today-offset, 0);
    top: 0;
    opacity: 0.6;
    z-index: 50;
    border-left: 2px dashed #F6AE2D;
}

.time-label {
    flex-shrink: 0;
    width: 80px;
    padding: 8px 4px;
    text-align: center;
    font-size: var(--tf-text-xs);
    color: var(--tf-gray-400);
    border-right: 1px solid rgba(51, 65, 85, 0.5);
}

.gantt-rows {
    flex: 1;
    overflow-y: auto;
    overflow-x: auto;
    position: relative;
}

/* ── Today Marker ─────────────────────────────────────── */
.gantt-today-line {
    position: absolute;
    width: 2px;
    height: 100%;
    background: #F6AE2D;
    left: var(--today-offset, 0);
    top: 0;
    z-index: 40;
    opacity: 0.4;
    pointer-events: none;
}

.gantt-today-label {
    position: absolute;
    top: 5px;
    left: calc(var(--today-offset, 0) + 4px);
    background: #F6AE2D;
    color: var(--tf-navy);
    padding: 2px 6px;
    border-radius: 3px;
    font-size: var(--tf-text-xs);
    font-weight: 600;
    z-index: 45;
    white-space: nowrap;
}

/* ── Job Row ──────────────────────────────────────────── */
.gantt-row {
    display: flex;
    align-items: center;
    height: 60px;
    border-bottom: 1px solid var(--tf-gray-700);
    background: var(--tf-navy);
}

.gantt-row:hover {
    background: rgba(51, 65, 85, 0.3);
}

.gantt-row-label {
    flex-shrink: 0;
    width: 280px;
    padding: 0 12px;
    display: flex;
    align-items: center;
    border-right: 1px solid var(--tf-gray-700);
    background: var(--tf-navy);
    position: sticky;
    left: 0;
    z-index: 20;
}

.row-label-text {
    font-size: var(--tf-text-sm);
    font-weight: 600;
    color: var(--tf-gray-100);
}

.gantt-bars-container {
    flex: 1;
    position: relative;
    height: 100%;
}

/* ── Gantt Bar ────────────────────────────────────────── */
.gantt-bar {
    position: absolute;
    height: 36px;
    top: 50%;
    transform: translateY(-50%);
    border-radius: var(--tf-radius);
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: var(--tf-text-xs);
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    min-width: 30px;
}

.gantt-bar:hover {
    transform: translateY(-50%) scale(1.05);
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.gantt-bar.queued {
    background: #64748B;
    opacity: 0.6;
}

.gantt-bar.queued:hover {
    opacity: 0.8;
}

.gantt-bar.in-progress {
    background: #3B82F6;
    animation: pulse-bar 2s ease-in-out infinite;
}

.gantt-bar.complete {
    background: #22C55E;
}

@keyframes pulse-bar {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

/* ── Due Date Marker ──────────────────────────────────── */
.gantt-due-marker {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 12px;
    height: 12px;
    background: #EF4444;
    border: 2px solid white;
    border-radius: 50%;
    z-index: 30;
}

.gantt-due-marker::after {
    content: attr(data-due);
    position: absolute;
    top: -20px;
    left: -30px;
    background: #EF4444;
    color: white;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: var(--tf-text-xs);
    font-weight: 600;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.15s;
}

.gantt-due-marker:hover::after {
    opacity: 1;
}

/* ── Hover Tooltip ────────────────────────────────────── */
.gantt-tooltip {
    position: absolute;
    background: var(--tf-navy-light);
    border: 1px solid #F6AE2D;
    border-radius: var(--tf-radius);
    padding: 12px;
    z-index: 100;
    pointer-events: none;
    min-width: 180px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    display: none;
}

.gantt-tooltip.visible {
    display: block;
}

.gantt-tooltip-title {
    font-weight: 700;
    color: #F6AE2D;
    margin-bottom: 6px;
    font-size: var(--tf-text-sm);
}

.gantt-tooltip-item {
    font-size: var(--tf-text-xs);
    color: var(--tf-gray-300);
    margin: 4px 0;
}

.gantt-tooltip-progress {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid var(--tf-gray-700);
}

.progress-bar {
    width: 100%;
    height: 4px;
    background: var(--tf-navy);
    border-radius: 2px;
    overflow: hidden;
    margin-top: 4px;
}

.progress-fill {
    height: 100%;
    background: #22C55E;
    transition: width 0.3s;
}

/* ── Machine Utilization Section ──────────────────────── */
.gantt-footer {
    max-height: 280px;
    background: var(--tf-navy-light);
    border-top: 1px solid var(--tf-gray-700);
    overflow-y: auto;
    padding: 16px;
}

.machine-section-title {
    font-size: var(--tf-text-sm);
    font-weight: 700;
    color: #F6AE2D;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
}

.machine-rows {
    display: grid;
    gap: 12px;
}

.machine-row {
    display: flex;
    align-items: center;
    gap: 12px;
}

.machine-name {
    flex-shrink: 0;
    width: 140px;
    font-weight: 600;
    font-size: var(--tf-text-sm);
    color: var(--tf-gray-100);
}

.machine-heatmap {
    flex: 1;
    display: flex;
    gap: 3px;
}

.heatmap-day {
    flex: 0 0 20px;
    height: 20px;
    border-radius: 3px;
    cursor: pointer;
    transition: all 0.15s;
    position: relative;
}

.heatmap-day:hover {
    transform: scale(1.2);
    z-index: 10;
}

.heatmap-day.empty {
    background: var(--tf-gray-700);
    opacity: 0.3;
}

.heatmap-day.light {
    background: #3B82F6;
    opacity: 0.4;
}

.heatmap-day.medium {
    background: #F59E0B;
    opacity: 0.7;
}

.heatmap-day.heavy {
    background: #EF4444;
    opacity: 1;
}

.heatmap-day::after {
    content: attr(data-items);
    position: absolute;
    background: var(--tf-navy);
    border: 1px solid #F6AE2D;
    padding: 4px 6px;
    border-radius: 3px;
    font-size: var(--tf-text-xs);
    color: var(--tf-gray-100);
    white-space: nowrap;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(-4px);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.15s;
    z-index: 20;
}

.heatmap-day:hover::after {
    opacity: 1;
}

/* ── Capacity Warnings ────────────────────────────────── */
.capacity-warning {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid #EF4444;
    border-radius: var(--tf-radius);
    padding: 10px;
    margin-top: 10px;
    font-size: var(--tf-text-xs);
    color: #FECACA;
}

.capacity-warning::before {
    content: '⚠';
    font-weight: 700;
    color: #EF4444;
}

/* ── Scrollbar Styling ────────────────────────────────── */
.gantt-rows::-webkit-scrollbar,
.gantt-sidebar::-webkit-scrollbar,
.gantt-footer::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

.gantt-rows::-webkit-scrollbar-track,
.gantt-sidebar::-webkit-scrollbar-track,
.gantt-footer::-webkit-scrollbar-track {
    background: var(--tf-navy);
}

.gantt-rows::-webkit-scrollbar-thumb,
.gantt-sidebar::-webkit-scrollbar-thumb,
.gantt-footer::-webkit-scrollbar-thumb {
    background: var(--tf-gray-600);
    border-radius: 4px;
}

.gantt-rows::-webkit-scrollbar-thumb:hover,
.gantt-sidebar::-webkit-scrollbar-thumb:hover,
.gantt-footer::-webkit-scrollbar-thumb:hover {
    background: #F6AE2D;
}

/* ── Responsive ───────────────────────────────────────── */
@media (max-width: 1200px) {
    .gantt-sidebar {
        width: 220px;
    }

    .gantt-row-label {
        width: 220px;
    }
}

@media (max-width: 768px) {
    .gantt-container {
        margin-left: 60px;
    }

    .gantt-header {
        padding: 12px;
        flex-direction: column;
        align-items: flex-start;
    }

    .gantt-header h1 {
        font-size: 1.25rem;
    }

    .gantt-sidebar {
        width: 180px;
        display: none;
    }

    .gantt-main {
        flex-direction: column;
    }
}
</style>
</head>
<body>


<div class="gantt-container">
    <!-- Header with Controls -->
    <div class="gantt-header">
        <h1>Production Schedule</h1>
        <div class="gantt-header-controls">
            <input type="text" class="date-range-input" id="dateRangeInput"
                   placeholder="Date range" readonly>
            <button class="view-toggle active" data-view="week">Week</button>
            <button class="view-toggle" data-view="2week">2 Weeks</button>
            <button class="view-toggle" data-view="month">Month</button>
        </div>
    </div>

    <!-- Main Gantt Area -->
    <div class="gantt-main">
        <!-- Left Sidebar: Job List -->
        <div class="gantt-sidebar" id="jobList"></div>

        <!-- Timeline -->
        <div class="gantt-timeline">
            <!-- Time Header -->
            <div class="gantt-time-header" id="timeHeader"></div>

            <!-- Gantt Rows -->
            <div class="gantt-rows" id="ganttRows">
                <div class="gantt-today-line"></div>
                <div class="gantt-today-label">Today</div>
            </div>
        </div>
    </div>

    <!-- Machine Utilization Footer -->
    <div class="gantt-footer" id="machineUtilization"></div>
</div>

<!-- Tooltip -->
<div class="gantt-tooltip" id="tooltip"></div>

<script>

// ─────────────────────────────────────────────
// GANTT VIEW INITIALIZATION
// ─────────────────────────────────────────────

let ganttData = null;
let currentView = 'week';
const MS_PER_DAY = 86400000;
const PIXELS_PER_DAY = 140;

// View durations in days
const VIEW_DURATIONS = {
    week: 7,
    '2week': 14,
    month: 30
};

// Fabrication time estimates (minutes)
const FAB_TIMES = {
    column: 90,
    rafter: 110,
    purlin: 20,
    sag_rod: 10,
    clip: 8,
    panel: 45,
    trim: 15,
    base_plate: 12,
    gusset: 18,
    plate: 15,
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    fetchGanttData();
    setupViewToggle();
});

// ─────────────────────────────────────────────
// FETCH DATA FROM API
// ─────────────────────────────────────────────

async function fetchGanttData() {
    try {
        const response = await fetch('/api/gantt/data');
        if (!response.ok) throw new Error('Failed to fetch gantt data');
        const result = await response.json();
        // API wraps data in {ok, data} envelope — unwrap it
        ganttData = result.data || result;
        if (result.warning) console.warn('[Schedule]', result.warning);
        renderGantt();
    } catch (error) {
        console.error('Error fetching gantt data:', error);
        document.getElementById('ganttRows').innerHTML =
            '<div style="padding: 20px; color: #ef4444;">Error loading schedule data</div>';
    }
}

// ─────────────────────────────────────────────
// RENDER GANTT CHART
// ─────────────────────────────────────────────

function renderGantt() {
    if (!ganttData) return;

    const today = new Date(ganttData.today);
    const viewDays = VIEW_DURATIONS[currentView];
    const startDate = new Date(today);
    startDate.setDate(startDate.getDate() - 1);
    const endDate = new Date(startDate);
    endDate.setDate(endDate.getDate() + viewDays);

    // Update date range
    document.getElementById('dateRangeInput').value =
        `${startDate.toLocaleDateString()} - ${endDate.toLocaleDateString()}`;

    // Render time header
    renderTimeHeader(startDate, endDate);

    // Render job list sidebar
    renderJobList();

    // Render gantt rows
    renderGanttRows(startDate, endDate, today);

    // Render machine utilization
    renderMachineUtilization(startDate, endDate);

    // Update today line position
    updateTodayLine(startDate, today);
}

function renderTimeHeader(startDate, endDate) {
    const header = document.getElementById('timeHeader');
    header.innerHTML = '';

    let currentDate = new Date(startDate);
    while (currentDate <= endDate) {
        const label = document.createElement('div');
        label.className = 'time-label';
        label.textContent = currentDate.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric'
        });
        label.style.width = PIXELS_PER_DAY + 'px';
        header.appendChild(label);
        currentDate.setDate(currentDate.getDate() + 1);
    }
}

function renderJobList() {
    const list = document.getElementById('jobList');
    list.innerHTML = '<h3>Active Jobs</h3>';

    ganttData.jobs.forEach(job => {
        const div = document.createElement('div');
        div.className = 'job-item';
        div.innerHTML = `
            <div class="job-code">${job.job_code}</div>
            <div class="job-customer">${typeof job.customer === 'object' ? (job.customer.name || '') : (job.customer || '')}</div>
            <div class="job-due">Due: ${job.due_date}</div>
        `;
        div.addEventListener('click', () => {
            document.querySelectorAll('.job-item').forEach(j => j.classList.remove('selected'));
            div.classList.add('selected');
            window.location.href = '/project/' + encodeURIComponent(job.job_code);
        });
        list.appendChild(div);
    });
}

function renderGanttRows(startDate, endDate, today) {
    const container = document.getElementById('ganttRows');
    const existingToday = container.querySelector('.gantt-today-line');
    const existingLabel = container.querySelector('.gantt-today-label');
    container.innerHTML = '';
    if (existingToday) container.appendChild(existingToday);
    if (existingLabel) container.appendChild(existingLabel);

    ganttData.jobs.forEach(job => {
        const row = document.createElement('div');
        row.className = 'gantt-row';

        const label = document.createElement('div');
        label.className = 'gantt-row-label';
        label.innerHTML = `<div class="row-label-text">${job.job_code}</div>`;

        const barsContainer = document.createElement('div');
        barsContainer.className = 'gantt-bars-container';

        // Render bars for each work order
        if (job.work_orders && job.work_orders.length > 0) {
            job.work_orders.forEach(wo => {
                const bar = createGanttBar(wo, job, startDate, endDate, today);
                if (bar) barsContainer.appendChild(bar);
            });
        }

        // Render due date marker if within range
        if (job.due_date) {
            const dueDate = new Date(job.due_date);
            if (dueDate >= startDate && dueDate <= endDate) {
                const offset = calculateDayOffset(startDate, dueDate);
                const marker = document.createElement('div');
                marker.className = 'gantt-due-marker';
                marker.setAttribute('data-due', job.due_date);
                marker.style.left = (offset * PIXELS_PER_DAY) + 'px';
                barsContainer.appendChild(marker);
            }
        }

        row.appendChild(label);
        row.appendChild(barsContainer);
        container.appendChild(row);
    });
}

function createGanttBar(wo, job, startDate, endDate, today) {
    if (!wo.items || wo.items.length === 0) return null;

    const createdAt = new Date(wo.created_at);
    if (createdAt > endDate) return null;

    // Estimate duration
    const estimatedDays = estimateDuration(wo.items);
    const completionDate = new Date(createdAt);
    completionDate.setDate(completionDate.getDate() + estimatedDays);

    // Calculate visible portion within date range
    const barStart = new Date(Math.max(createdAt.getTime(), startDate.getTime()));
    const barEnd = new Date(Math.min(completionDate.getTime(), endDate.getTime()));

    const startOffset = calculateDayOffset(startDate, barStart);
    const durationDays = (barEnd.getTime() - barStart.getTime()) / MS_PER_DAY;

    const bar = document.createElement('div');
    const statusClass = wo.status.replace('_', '-');
    bar.className = `gantt-bar ${statusClass}`;
    bar.style.left = (startOffset * PIXELS_PER_DAY) + 'px';
    bar.style.width = Math.max(30, durationDays * PIXELS_PER_DAY) + 'px';

    // Count completion
    const total = wo.items.length;
    const complete = wo.items.filter(i => i.status === 'complete').length;
    const inProgress = wo.items.filter(i => i.status === 'in_progress').length;
    const pctComplete = total > 0 ? Math.round((complete / total) * 100) : 0;

    bar.innerHTML = `${pctComplete}%`;

    bar.addEventListener('mouseenter', (e) => {
        showTooltip(e, {
            job: job.job_code,
            items: total,
            complete: complete,
            inProgress: inProgress,
            pctComplete: pctComplete,
            estimatedCompletion: wo.created_at.substring(0, 10)
        });
    });

    bar.addEventListener('mouseleave', () => hideTooltip());

    bar.addEventListener('click', () => {
        window.location.href = '/project/' + encodeURIComponent(job.job_code);
    });

    return bar;
}

function estimateDuration(items) {
    if (!items || items.length === 0) return 0.5;

    let totalMinutes = 0;
    items.forEach(item => {
        const type = item.component_type || 'unknown';
        const qty = item.quantity || 1;
        const time = FAB_TIMES[type] || 30;
        totalMinutes += time * qty;
    });

    // Assume 8-hour day and 2 machines parallel
    const workdayMinutes = 480;
    const days = totalMinutes / workdayMinutes;
    return Math.max(0.5, Math.ceil(days * 2) / 2);
}

function calculateDayOffset(startDate, targetDate) {
    return Math.floor((targetDate.getTime() - startDate.getTime()) / MS_PER_DAY);
}

function updateTodayLine(startDate, today) {
    const offset = calculateDayOffset(startDate, today);
    const pixelOffset = (offset * PIXELS_PER_DAY) + 'px';
    document.getElementById('ganttRows').style.setProperty('--today-offset', pixelOffset);
    document.getElementById('timeHeader').style.setProperty('--today-offset', pixelOffset);
}

function renderMachineUtilization(startDate, endDate) {
    const container = document.getElementById('machineUtilization');
    container.innerHTML = '<div class="machine-section-title">Machine Utilization</div>';

    const machineRows = document.createElement('div');
    machineRows.className = 'machine-rows';

    // Get all unique machines
    const machines = new Set();
    ganttData.jobs.forEach(job => {
        job.machines_used.forEach(m => machines.add(m));
    });

    if (ganttData.machine_schedule) {
        Array.from(machines).sort().forEach(machine => {
            const row = document.createElement('div');
            row.className = 'machine-row';

            const name = document.createElement('div');
            name.className = 'machine-name';
            name.textContent = machine;

            const heatmap = document.createElement('div');
            heatmap.className = 'machine-heatmap';

            let currentDate = new Date(startDate);
            let hasOverload = false;

            while (currentDate <= endDate) {
                const dateStr = currentDate.toISOString().split('T')[0];
                const dayData = ganttData.machine_schedule[machine]?.find(d => d.date === dateStr);
                const itemCount = dayData?.item_count || 0;
                const isOverloaded = dayData?.is_overloaded || false;

                const day = document.createElement('div');
                day.className = 'heatmap-day';

                if (itemCount === 0) {
                    day.classList.add('empty');
                } else if (itemCount <= 5) {
                    day.classList.add('light');
                } else if (itemCount <= 15) {
                    day.classList.add('medium');
                } else {
                    day.classList.add('heavy');
                    hasOverload = true;
                }

                day.setAttribute('data-items', itemCount);
                day.style.width = (PIXELS_PER_DAY / 7) + 'px';

                heatmap.appendChild(day);
                currentDate.setDate(currentDate.getDate() + 1);
            }

            row.appendChild(name);
            row.appendChild(heatmap);
            machineRows.appendChild(row);

            if (hasOverload) {
                const warning = document.createElement('div');
                warning.className = 'capacity-warning';
                warning.textContent = `${machine} exceeds 15 items on some days`;
                machineRows.appendChild(warning);
            }
        });
    }

    container.appendChild(machineRows);
}

// ─────────────────────────────────────────────
// TOOLTIP HANDLING
// ─────────────────────────────────────────────

function showTooltip(event, data) {
    const tooltip = document.getElementById('tooltip');
    tooltip.innerHTML = `
        <div class="gantt-tooltip-title">${data.job}</div>
        <div class="gantt-tooltip-item"><strong>${data.items}</strong> items</div>
        <div class="gantt-tooltip-item"><strong>${data.complete}</strong> complete</div>
        <div class="gantt-tooltip-item"><strong>${data.inProgress}</strong> in progress</div>
        <div class="gantt-tooltip-progress">
            <div>Progress: <strong>${data.pctComplete}%</strong></div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${data.pctComplete}%"></div>
            </div>
        </div>
    `;
    tooltip.classList.add('visible');

    const rect = event.target.getBoundingClientRect();
    tooltip.style.left = (rect.left + rect.width / 2 - 90) + 'px';
    tooltip.style.top = (rect.top - 120) + 'px';
}

function hideTooltip() {
    document.getElementById('tooltip').classList.remove('visible');
}

// ─────────────────────────────────────────────
// VIEW TOGGLE
// ─────────────────────────────────────────────

function setupViewToggle() {
    document.querySelectorAll('.view-toggle').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.view-toggle').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentView = e.target.getAttribute('data-view');
            renderGantt();
        });
    });
}

// Auto-refresh every 2 minutes
setInterval(() => {
    fetchGanttData();
}, 120000);

</script>
</body>
</html>
"""
