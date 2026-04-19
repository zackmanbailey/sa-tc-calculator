"""
TitanForge v4 — Customer Portal Photos
=========================================
Progress photos by project, before/after, tagged by phase, filterable gallery.
"""

PORTAL_PHOTOS_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a;
        --tf-card: #1e293b;
        --tf-text: #e2e8f0;
        --tf-muted: #94a3b8;
        --tf-gold: #d4a843;
        --tf-blue: #3b82f6;
    }
    .photos-container {
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
    .photo-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
    .photo-card {
        background: var(--tf-card); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);
        overflow: hidden; cursor: pointer; transition: border-color 0.2s, transform 0.2s;
    }
    .photo-card:hover { border-color: var(--tf-blue); transform: translateY(-2px); }
    .photo-thumb {
        width: 100%; height: 200px; background: var(--tf-bg); display: flex;
        align-items: center; justify-content: center; color: var(--tf-muted); font-size: 40px;
        overflow: hidden; position: relative;
    }
    .photo-thumb img { width: 100%; height: 100%; object-fit: cover; }
    .photo-info { padding: 14px; }
    .photo-info h4 { font-size: 14px; font-weight: 600; margin: 0 0 6px 0; }
    .photo-info .photo-meta { font-size: 12px; color: var(--tf-muted); display: flex; justify-content: space-between; }
    .photo-tags { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }
    .tag { background: rgba(59,130,246,0.15); color: #60a5fa; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .share-badge { position: absolute; top: 8px; right: 8px; background: rgba(34,197,94,0.9); color: #fff; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); grid-column: 1 / -1; }
    .empty-state h3 { font-size: 18px; margin-bottom: 8px; color: var(--tf-text); }
    .loading { text-align: center; padding: 40px; color: var(--tf-muted); grid-column: 1 / -1; }
    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 1000; justify-content: center; align-items: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 12px; padding: 28px; width: 560px; max-width: 90vw; border: 1px solid rgba(255,255,255,0.1); max-height: 85vh; overflow-y: auto; }
    .modal h2 { font-size: 20px; margin: 0 0 20px 0; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px; font-family: inherit; box-sizing: border-box;
    }
    .lightbox { max-width: 90vw; max-height: 80vh; background: #000; border-radius: 12px; padding: 0; overflow: hidden; text-align: center; }
    .lightbox img { max-width: 100%; max-height: 75vh; object-fit: contain; }
    .lightbox-info { padding: 16px; text-align: left; background: var(--tf-card); }

/* ── Responsive ── */
@media (max-width: 768px) {
    .page-header h1 { font-size: 22px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .modal-overlay .modal, .modal { width: 95%; max-width: 95vw; margin: 20px auto; padding: 20px; }
    .photo-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
    .toolbar { gap: 8px; }
    .photo-grid { grid-template-columns: 1fr 1fr; }
}
</style>

<div class="photos-container">
    <div class="page-header">
        <h1>Portal Photos</h1>
        <p>Progress photos by project, tagged by phase, with customer sharing controls</p>
    </div>
    <div class="toolbar">
        <div style="display:flex;gap:10px;align-items:center;">
            <input type="text" id="photoSearch" placeholder="Search photos..." oninput="filterPhotos()">
            <select id="filterProject" onchange="filterPhotos()"><option value="">All Projects</option></select>
            <select id="filterPhase" onchange="filterPhotos()">
                <option value="">All Phases</option>
                <option value="fabrication">Fabrication</option>
                <option value="coating">Coating</option>
                <option value="shipping">Shipping</option>
                <option value="install">Installation</option>
                <option value="complete">Complete</option>
            </select>
        </div>
        <button class="btn-gold" onclick="openModal('uploadModal')">+ Upload Photos</button>
    </div>
    <div class="photo-grid" id="photoGrid">
        <div class="loading">Loading photos...</div>
    </div>
</div>

<div class="modal-overlay" id="uploadModal">
    <div class="modal">
        <h2>Upload Photos</h2>
        <div class="form-group"><label>Project</label><input type="text" id="uploadProject" placeholder="Job code"></div>
        <div class="form-group"><label>Phase</label><select id="uploadPhase"><option value="fabrication">Fabrication</option><option value="coating">Coating</option><option value="shipping">Shipping</option><option value="install">Installation</option><option value="complete">Complete</option></select></div>
        <div class="form-group"><label>Photos</label><input type="file" id="uploadFiles" multiple accept="image/*" style="padding:8px;"></div>
        <div class="form-group"><label>Caption</label><input type="text" id="uploadCaption" placeholder="Photo description"></div>
        <div class="form-group">
            <label><input type="checkbox" id="uploadShare" checked style="width:auto;margin-right:8px;">Share with customer</label>
        </div>
        <div class="modal-actions">
            <button class="btn-outline" onclick="closeModal('uploadModal')">Cancel</button>
            <button class="btn-gold" onclick="uploadPhotos()">Upload</button>
        </div>
    </div>
</div>

<div class="modal-overlay" id="lightboxModal">
    <div class="lightbox" id="lightboxContent"></div>
</div>

<script>
let allPhotos = [];

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); }));

function renderPhotos(photos) {
    const grid = document.getElementById('photoGrid');
    if (!photos.length) {
        grid.innerHTML = '<div class="empty-state"><h3>No photos found</h3><p>Upload progress photos to share with customers.</p></div>';
        return;
    }
    grid.innerHTML = photos.map((p, i) => {
        const tags = (p.tags || [p.phase]).filter(Boolean);
        return '<div class="photo-card" onclick="openLightbox(' + i + ')">' +
            '<div class="photo-thumb">' +
            (p.url ? '<img src="' + p.url + '" alt="' + (p.caption||'') + '">' : '\ud83d\udcf7') +
            (p.shared ? '<span class="share-badge">Shared</span>' : '') +
            '</div><div class="photo-info"><h4>' + (p.caption || 'Photo ' + (i+1)) + '</h4>' +
            '<div class="photo-meta"><span>' + (p.project || '') + '</span><span>' + (p.date || '') + '</span></div>' +
            '<div class="photo-tags">' + tags.map(t => '<span class="tag">' + t + '</span>').join('') + '</div>' +
            '</div></div>';
    }).join('');
}

function filterPhotos() {
    const search = document.getElementById('photoSearch').value.toLowerCase();
    const project = document.getElementById('filterProject').value;
    const phase = document.getElementById('filterPhase').value;
    const filtered = allPhotos.filter(p => {
        if (search && !(p.caption||'').toLowerCase().includes(search) && !(p.project||'').toLowerCase().includes(search)) return false;
        if (project && p.project !== project) return false;
        if (phase && p.phase !== phase) return false;
        return true;
    });
    renderPhotos(filtered);
}

function openLightbox(idx) {
    const p = allPhotos[idx];
    if (!p) return;
    document.getElementById('lightboxContent').innerHTML =
        (p.url ? '<img src="' + p.url + '" alt="' + (p.caption||'') + '">' : '<div style="padding:60px;color:var(--tf-muted);font-size:60px;">\ud83d\udcf7</div>') +
        '<div class="lightbox-info"><h4 style="margin:0 0 6px;">' + (p.caption || 'Untitled') + '</h4>' +
        '<div style="font-size:13px;color:var(--tf-muted);">' + (p.project||'') + ' &bull; ' + (p.phase||'') + ' &bull; ' + (p.date||'') + '</div></div>';
    openModal('lightboxModal');
}

async function uploadPhotos() {
    const payload = {
        project: document.getElementById('uploadProject').value,
        phase: document.getElementById('uploadPhase').value,
        caption: document.getElementById('uploadCaption').value,
        shared: document.getElementById('uploadShare').checked,
        date: new Date().toISOString().slice(0,10)
    };
    if (!payload.project) { alert('Project is required'); return; }
    try {
        await fetch('/api/portal/photos', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        closeModal('uploadModal');
        loadPhotos();
    } catch(e) { alert('Error: ' + e.message); }
}

async function loadPhotos() {
    try {
        const resp = await fetch('/api/portal/photos');
        const data = await resp.json();
        allPhotos = Array.isArray(data) ? data : (data.photos || []);
        const projects = [...new Set(allPhotos.map(p => p.project).filter(Boolean))];
        const sel = document.getElementById('filterProject');
        if (sel.options.length <= 1) projects.forEach(p => { const o = document.createElement('option'); o.value = p; o.textContent = p; sel.appendChild(o); });
        renderPhotos(allPhotos);
    } catch(e) { renderPhotos([]); }
}

loadPhotos();
</script>
"""
