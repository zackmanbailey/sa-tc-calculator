"""
TitanForge v4 — Task Manager
==============================
Kanban board with todo/in-progress/done columns, assignments, due dates, priorities.
"""

TASKS_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .tasks-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', system-ui, -apple-system, sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
    .toolbar input[type="text"] { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px; width: 260px; }
    .toolbar input::placeholder { color: var(--tf-muted); }
    .toolbar select { background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; }
    .btn-gold { background: var(--tf-gold); color: #0f172a; border: none; border-radius: 8px; padding: 10px 20px; font-weight: 700; font-size: 14px; cursor: pointer; }
    .btn-gold:hover { opacity: 0.9; }
    .btn-outline { background: transparent; color: var(--tf-muted); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 14px; cursor: pointer; }
    .btn-outline:hover { border-color: var(--tf-gold); color: var(--tf-gold); }
    .kanban { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; min-height: 500px; }
    @media (max-width: 900px) { .kanban { grid-template-columns: 1fr; } }
    .kanban-col {
        background: rgba(255,255,255,0.02); border-radius: 12px; padding: 16px;
        border: 1px solid rgba(255,255,255,0.04); min-height: 400px;
    }
    .kanban-col-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    .kanban-col-header h3 { font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin: 0; }
    .kanban-count { background: rgba(255,255,255,0.1); border-radius: 12px; padding: 2px 10px; font-size: 12px; font-weight: 700; }
    .col-todo .kanban-col-header h3 { color: var(--tf-muted); }
    .col-progress .kanban-col-header h3 { color: var(--tf-blue); }
    .col-done .kanban-col-header h3 { color: #4ade80; }
    .task-card {
        background: var(--tf-card); border-radius: 10px; padding: 14px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.06); cursor: pointer; transition: border-color 0.2s;
    }
    .task-card:hover { border-color: var(--tf-blue); }
    .task-card .task-title { font-size: 14px; font-weight: 600; margin-bottom: 8px; }
    .task-card .task-meta { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--tf-muted); }
    .task-card .task-project { font-size: 12px; color: var(--tf-blue); margin-bottom: 6px; }
    .priority-high { border-left: 3px solid #ef4444; }
    .priority-medium { border-left: 3px solid var(--tf-gold); }
    .priority-low { border-left: 3px solid var(--tf-blue); }
    .avatar-sm { width: 22px; height: 22px; border-radius: 50%; background: var(--tf-blue); display: inline-flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700; color: #fff; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 520px; max-width: 90vw; border: 1px solid rgba(255,255,255,0.1); }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; font-family: inherit; box-sizing: border-box;
    }
    .form-group textarea { min-height: 70px; resize: vertical; }
    .due-overdue { color: #f87171; }
    .due-soon { color: var(--tf-gold); }
</style>

<div class="tasks-container">
    <div class="page-header">
        <h1>Task Manager</h1>
        <p>Manage and track tasks across projects with kanban workflow</p>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;">
            <input type="text" id="taskSearch" placeholder="Search tasks..." oninput="filterTasks()">
            <select id="filterPriority" onchange="filterTasks()">
                <option value="">All Priorities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
            </select>
            <select id="filterAssignee" onchange="filterTasks()">
                <option value="">All Assignees</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openModal('taskModal')">+ New Task</button>
    </div>
    <div class="kanban">
        <div class="kanban-col col-todo" id="colTodo">
            <div class="kanban-col-header"><h3>To Do</h3><span class="kanban-count" id="countTodo">0</span></div>
            <div id="todoCards"></div>
        </div>
        <div class="kanban-col col-progress" id="colProgress">
            <div class="kanban-col-header"><h3>In Progress</h3><span class="kanban-count" id="countProgress">0</span></div>
            <div id="progressCards"></div>
        </div>
        <div class="kanban-col col-done" id="colDone">
            <div class="kanban-col-header"><h3>Done</h3><span class="kanban-count" id="countDone">0</span></div>
            <div id="doneCards"></div>
        </div>
    </div>
</div>

<div class="modal-overlay" id="taskModal">
    <div class="modal">
        <h2 id="taskModalTitle">New Task</h2>
        <input type="hidden" id="taskId">
        <div class="form-group"><label>Title</label><input type="text" id="taskTitle" placeholder="Task title"></div>
        <div class="form-group"><label>Description</label><textarea id="taskDesc" placeholder="Details..."></textarea></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>Priority</label><select id="taskPriority"><option value="low">Low</option><option value="medium" selected>Medium</option><option value="high">High</option></select></div>
            <div class="form-group"><label>Status</label><select id="taskStatus"><option value="todo">To Do</option><option value="in_progress">In Progress</option><option value="done">Done</option></select></div>
            <div class="form-group"><label>Assignee</label><input type="text" id="taskAssignee" placeholder="Name"></div>
            <div class="form-group"><label>Due Date</label><input type="date" id="taskDue"></div>
        </div>
        <div class="form-group"><label>Project</label><input type="text" id="taskProject" placeholder="Link to project"></div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('taskModal')">Cancel</button>
            <button class="btn-gold" onclick="saveTask()">Save Task</button>
        </div>
    </div>
</div>

<script>
let allTasks = [];

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); clearTaskForm(); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

function clearTaskForm() {
    ['taskId','taskTitle','taskDesc','taskAssignee','taskDue','taskProject'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('taskPriority').value = 'medium';
    document.getElementById('taskStatus').value = 'todo';
    document.getElementById('taskModalTitle').textContent = 'New Task';
}

function editTask(task) {
    document.getElementById('taskModalTitle').textContent = 'Edit Task';
    document.getElementById('taskId').value = task.id || '';
    document.getElementById('taskTitle').value = task.title || '';
    document.getElementById('taskDesc').value = task.description || '';
    document.getElementById('taskPriority').value = task.priority || 'medium';
    document.getElementById('taskStatus').value = task.status || 'todo';
    document.getElementById('taskAssignee').value = task.assignee || '';
    document.getElementById('taskDue').value = task.due_date || '';
    document.getElementById('taskProject').value = task.project || '';
    openModal('taskModal');
}

function getDueClass(d) {
    if (!d) return '';
    const diff = (new Date(d) - new Date()) / 86400000;
    if (diff < 0) return 'due-overdue';
    if (diff < 3) return 'due-soon';
    return '';
}

function renderCard(t) {
    const prClass = 'priority-' + (t.priority || 'low');
    const initials = (t.assignee || '?').split(' ').map(w => w[0]).join('').substring(0,2).toUpperCase();
    const dueClass = getDueClass(t.due_date);
    return '<div class="task-card ' + prClass + '" onclick=\'editTask(' + JSON.stringify(t).replace(/'/g,"&#39;") + ')\'>' +
        (t.project ? '<div class="task-project">' + t.project + '</div>' : '') +
        '<div class="task-title">' + (t.title || 'Untitled') + '</div>' +
        '<div class="task-meta"><span class="' + dueClass + '">' + (t.due_date || 'No due date') + '</span>' +
        '<span class="avatar-sm" title="' + (t.assignee || '') + '">' + initials + '</span></div></div>';
}

function renderKanban(tasks) {
    const todo = tasks.filter(t => t.status === 'todo' || !t.status);
    const progress = tasks.filter(t => t.status === 'in_progress');
    const done = tasks.filter(t => t.status === 'done');
    document.getElementById('todoCards').innerHTML = todo.length ? todo.map(renderCard).join('') : '<div style="text-align:center;color:var(--tf-muted);padding:20px;font-size:13px;">No tasks</div>';
    document.getElementById('progressCards').innerHTML = progress.length ? progress.map(renderCard).join('') : '<div style="text-align:center;color:var(--tf-muted);padding:20px;font-size:13px;">No tasks</div>';
    document.getElementById('doneCards').innerHTML = done.length ? done.map(renderCard).join('') : '<div style="text-align:center;color:var(--tf-muted);padding:20px;font-size:13px;">No tasks</div>';
    document.getElementById('countTodo').textContent = todo.length;
    document.getElementById('countProgress').textContent = progress.length;
    document.getElementById('countDone').textContent = done.length;
}

function filterTasks() {
    const search = document.getElementById('taskSearch').value.toLowerCase();
    const priority = document.getElementById('filterPriority').value;
    const assignee = document.getElementById('filterAssignee').value;
    let filtered = allTasks.filter(t => {
        if (search && !(t.title||'').toLowerCase().includes(search) && !(t.project||'').toLowerCase().includes(search)) return false;
        if (priority && t.priority !== priority) return false;
        if (assignee && t.assignee !== assignee) return false;
        return true;
    });
    renderKanban(filtered);
}

async function loadTasks() {
    try {
        const resp = await fetch('/api/tasks');
        const data = await resp.json();
        allTasks = Array.isArray(data) ? data : (data.tasks || []);
        const assignees = [...new Set(allTasks.map(t => t.assignee).filter(Boolean))];
        const sel = document.getElementById('filterAssignee');
        assignees.forEach(a => { const o = document.createElement('option'); o.value = a; o.textContent = a; sel.appendChild(o); });
        renderKanban(allTasks);
    } catch(e) { renderKanban([]); }
}

async function saveTask() {
    const payload = {
        id: document.getElementById('taskId').value || undefined,
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDesc').value,
        priority: document.getElementById('taskPriority').value,
        status: document.getElementById('taskStatus').value,
        assignee: document.getElementById('taskAssignee').value,
        due_date: document.getElementById('taskDue').value,
        project: document.getElementById('taskProject').value
    };
    if (!payload.title) { alert('Title is required'); return; }
    try {
        await fetch('/api/tasks', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal('taskModal');
        loadTasks();
    } catch(e) { alert('Error: ' + e.message); }
}

loadTasks();
</script>
"""
