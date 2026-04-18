"""
TitanForge v4 -- Field Photo Gallery
=======================================
Grid view, upload photos, tag by project/date/area, annotations, progress tracking.
"""

FIELD_PHOTOS_PAGE_HTML = r"""
<style>
    :root {
        --tf-bg: #0f172a; --tf-card: #1e293b; --tf-text: #e2e8f0;
        --tf-muted: #94a3b8; --tf-gold: #d4a843; --tf-blue: #3b82f6;
        --tf-green: #10b981; --tf-red: #ef4444; --tf-orange: #f59e0b;
    }
    .photos-container {
        max-width: 1400px; margin: 0 auto; padding: 24px 32px;
        font-family: 'Inter', 'Segoe UI', sans-serif; color: var(--tf-text);
    }
    .page-header { margin-bottom: 28px; }
    .page-header h1 { font-size: 28px; font-weight: 800; margin: 0 0 6px 0; }
    .page-header p { font-size: 14px; color: var(--tf-muted); margin: 0; }

    .stat-row {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px; margin-bottom: 24px;
    }
    .stat-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 20px 24px; cursor: pointer; transition: border-color 0.2s, transform 0.15s;
    }
    .stat-card:hover { border-color: var(--tf-gold); transform: translateY(-2px); }
    .stat-card .label { font-size: 12px; color: var(--tf-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .stat-card .value { font-size: 28px; font-weight: 800; }
    .stat-gold .value { color: var(--tf-gold); }
    .stat-blue .value { color: var(--tf-blue); }
    .stat-green .value { color: var(--tf-green); }

    .toolbar {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
    }
    .toolbar-left { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .toolbar input[type="text"], .toolbar input[type="date"], .toolbar select {
        background: var(--tf-card); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px; padding: 10px 16px; color: var(--tf-text); font-size: 14px;
    }
    .toolbar input:focus, .toolbar select:focus { outline: none; border-color: var(--tf-blue); }
    .btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
    .btn-primary { background: var(--tf-gold); color: #0f172a; }
    .btn-primary:hover { background: #e0b44e; }
    .btn-secondary { background: var(--tf-card); color: var(--tf-text); border: 1px solid rgba(255,255,255,0.06); }
    .btn-sm { padding: 6px 14px; font-size: 12px; }

    .photo-grid {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 16px; margin-bottom: 20px;
    }
    .photo-card {
        background: var(--tf-card); border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        overflow: hidden; transition: border-color 0.2s, transform 0.15s; cursor: pointer;
    }
    .photo-card:hover { border-color: var(--tf-blue); transform: translateY(-2px); }
    .photo-thumbnail {
        width: 100%; height: 200px; background: var(--tf-bg);
        display: flex; align-items: center; justify-content: center;
        color: var(--tf-muted); font-size: 48px; overflow: hidden;
    }
    .photo-thumbnail img { width: 100%; height: 100%; object-fit: cover; }
    .photo-info { padding: 16px; }
    .photo-info h4 { font-size: 14px; font-weight: 700; margin: 0 0 6px 0; }
    .photo-info .meta { font-size: 12px; color: var(--tf-muted); margin-bottom: 8px; }
    .photo-tags { display: flex; gap: 6px; flex-wrap: wrap; }
    .photo-tag {
        display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px;
        font-weight: 600; background: rgba(59,130,246,0.1); color: var(--tf-blue);
    }
    .photo-tag.area { background: rgba(212,168,67,0.1); color: var(--tf-gold); }
    .photo-tag.progress { background: rgba(16,185,129,0.1); color: var(--tf-green); }

    .upload-zone {
        border: 2px dashed rgba(255,255,255,0.1); border-radius: 16px;
        padding: 40px; text-align: center; cursor: pointer;
        transition: border-color 0.2s, background 0.2s; margin-bottom: 20px;
    }
    .upload-zone:hover, .upload-zone.dragover {
        border-color: var(--tf-blue); background: rgba(59,130,246,0.04);
    }
    .upload-zone .icon { font-size: 48px; margin-bottom: 12px; opacity: 0.5; }
    .upload-zone h3 { font-size: 16px; margin-bottom: 6px; }
    .upload-zone p { font-size: 13px; color: var(--tf-muted); }

    .empty-state { text-align: center; padding: 60px 20px; color: var(--tf-muted); }
    .empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
    .empty-state h3 { font-size: 18px; color: var(--tf-text); margin-bottom: 8px; }
    .empty-state p { font-size: 14px; max-width: 400px; margin: 0 auto 20px; }

    .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; align-items: center; justify-content: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: var(--tf-card); border-radius: 16px; padding: 32px; width: 90%; max-width: 600px; max-height: 90vh; overflow-y: auto; border: 1px solid rgba(255,255,255,0.08); }
    .modal h2 { font-size: 22px; font-weight: 800; margin: 0 0 24px 0; }
    .modal-close { float: right; background: none; border: none; color: var(--tf-muted); font-size: 24px; cursor: pointer; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--tf-muted); margin-bottom: 6px; }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; background: var(--tf-bg); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 10px 14px; color: var(--tf-text); font-size: 14px;
    }
    .form-group textarea { min-height: 60px; resize: vertical; }
    .form-group input:focus, .form-group select:focus { outline: none; border-color: var(--tf-blue); }
    .modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 24px; }

    /* Lightbox */
    .lightbox { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.9); z-index: 2000; align-items: center; justify-content: center; }
    .lightbox.active { display: flex; }
    .lightbox img { max-width: 90%; max-height: 90vh; border-radius: 8px; }
    .lightbox-close { position: absolute; top: 20px; right: 20px; background: none; border: none; color: #fff; font-size: 32px; cursor: pointer; }
    .lightbox-info { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--tf-card); padding: 16px 24px; border-radius: 12px; text-align: center; }
</style>

<div class="photos-container">
    <div class="page-header">
        <h1>Field Photos</h1>
        <p>Capture and organize field progress photos with tags, annotations, and project tracking</p>
    </div>

    <div class="stat-row">
        <div class="stat-card stat-gold"><div class="label">Total Photos</div><div class="value" id="stat-total">0</div></div>
        <div class="stat-card stat-blue"><div class="label">This Week</div><div class="value" id="stat-week">0</div></div>
        <div class="stat-card stat-green"><div class="label">Projects Covered</div><div class="value" id="stat-projects">0</div></div>
    </div>

    <div class="upload-zone" id="uploadZone" onclick="document.getElementById('fileInput').click()">
        <div class="icon">&#128247;</div>
        <h3>Drop photos here or click to upload</h3>
        <p>Supports JPG, PNG, HEIC - Max 25MB per file</p>
        <input type="file" id="fileInput" multiple accept="image/*" style="display:none" onchange="handleUpload(this.files)">
    </div>

    <div class="toolbar">
        <div class="toolbar-left">
            <input type="text" id="searchInput" placeholder="Search photos..." oninput="renderPhotos()">
            <select id="filterProject" onchange="renderPhotos()"><option value="">All Projects</option></select>
            <input type="date" id="filterDate" onchange="renderPhotos()">
            <select id="filterArea" onchange="renderPhotos()">
                <option value="">All Areas</option>
                <option value="foundation">Foundation</option>
                <option value="framing">Framing</option>
                <option value="roofing">Roofing</option>
                <option value="siding">Siding</option>
                <option value="trim">Trim</option>
                <option value="interior">Interior</option>
                <option value="site">Site Work</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="document.getElementById('fileInput').click()">+ Upload Photos</button>
    </div>

    <div class="photo-grid" id="photoGrid"></div>

    <div class="empty-state" id="emptyState">
        <div class="icon">&#128247;</div>
        <h3>No Photos Yet</h3>
        <p>Upload field photos to document progress and share with your team.</p>
        <button class="btn btn-primary" onclick="document.getElementById('fileInput').click()">+ Upload First Photos</button>
    </div>
</div>

<!-- Photo Detail Modal -->
<div class="modal-overlay" id="photoModal">
    <div class="modal">
        <button class="modal-close" onclick="closeModal('photoModal')">&times;</button>
        <h2>Photo Details</h2>
        <form id="photoForm" onsubmit="savePhotoDetails(event)">
            <div class="form-group"><label>Caption</label><input type="text" id="photoCaption" placeholder="Describe this photo"></div>
            <div class="form-group"><label>Project</label><select id="photoProject"><option value="">Select Project</option></select></div>
            <div class="form-group"><label>Area</label>
                <select id="photoArea">
                    <option value="">Select Area</option>
                    <option value="foundation">Foundation</option>
                    <option value="framing">Framing</option>
                    <option value="roofing">Roofing</option>
                    <option value="siding">Siding</option>
                    <option value="trim">Trim</option>
                    <option value="interior">Interior</option>
                    <option value="site">Site Work</option>
                </select>
            </div>
            <div class="form-group"><label>Tags (comma-separated)</label><input type="text" id="photoTags" placeholder="e.g. progress, before, issue"></div>
            <div class="form-group"><label>Notes / Annotations</label><textarea id="photoNotes" placeholder="Additional notes..."></textarea></div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('photoModal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Details</button>
            </div>
        </form>
    </div>
</div>

<!-- Lightbox -->
<div class="lightbox" id="lightbox" onclick="closeLightbox()">
    <button class="lightbox-close">&times;</button>
    <img id="lightboxImg" src="" alt="">
    <div class="lightbox-info">
        <div id="lightboxCaption" style="font-weight:700;margin-bottom:4px;"></div>
        <div id="lightboxMeta" style="font-size:13px;color:var(--tf-muted);"></div>
    </div>
</div>

<script>
    let photos = [];
    let editingId = null;

    async function loadPhotos() {
        try {
            const resp = await fetch('/api/field/photos');
            const data = await resp.json();
            photos = data.photos || [];
            renderPhotos();
            updateStats();
        } catch(e) { console.error('Failed to load photos:', e); renderPhotos(); }
    }

    function renderPhotos() {
        const grid = document.getElementById('photoGrid');
        const empty = document.getElementById('emptyState');
        const search = document.getElementById('searchInput').value.toLowerCase();
        const projectFilter = document.getElementById('filterProject').value;
        const dateFilter = document.getElementById('filterDate').value;
        const areaFilter = document.getElementById('filterArea').value;

        let filtered = photos.filter(p => {
            if (search && !JSON.stringify(p).toLowerCase().includes(search)) return false;
            if (projectFilter && p.project_id !== projectFilter) return false;
            if (dateFilter && p.date !== dateFilter) return false;
            if (areaFilter && p.area !== areaFilter) return false;
            return true;
        });

        if (filtered.length === 0) { grid.innerHTML = ''; empty.style.display = 'block'; return; }
        empty.style.display = 'none';

        grid.innerHTML = filtered.map(p => `
            <div class="photo-card" onclick="openLightbox('${p.id}')">
                <div class="photo-thumbnail">
                    ${p.thumbnail_url ? `<img src="${p.thumbnail_url}" alt="${p.caption || ''}">` : '&#128247;'}
                </div>
                <div class="photo-info">
                    <h4>${p.caption || 'Untitled Photo'}</h4>
                    <div class="meta">${p.date || ''} - ${p.uploaded_by || ''}</div>
                    <div class="photo-tags">
                        ${p.project_name ? `<span class="photo-tag">${p.project_name}</span>` : ''}
                        ${p.area ? `<span class="photo-tag area">${p.area}</span>` : ''}
                        ${(p.tags || []).map(t => `<span class="photo-tag progress">${t}</span>`).join('')}
                    </div>
                </div>
            </div>
        `).join('');
    }

    function updateStats() {
        document.getElementById('stat-total').textContent = photos.length;
        const weekAgo = new Date(Date.now() - 7*24*60*60*1000);
        document.getElementById('stat-week').textContent = photos.filter(p => new Date(p.date) >= weekAgo).length;
        const projects = new Set(photos.map(p => p.project_id).filter(Boolean));
        document.getElementById('stat-projects').textContent = projects.size;
    }

    function handleUpload(files) {
        if (!files || files.length === 0) return;
        for (const file of files) {
            const formData = new FormData();
            formData.append('photo', file);
            fetch('/api/field/photos/upload', { method: 'POST', body: formData })
                .then(() => loadPhotos())
                .catch(e => console.error('Upload error:', e));
        }
    }

    // Drag & drop
    const zone = document.getElementById('uploadZone');
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
    zone.addEventListener('drop', e => { e.preventDefault(); zone.classList.remove('dragover'); handleUpload(e.dataTransfer.files); });

    function openLightbox(id) {
        const p = photos.find(x => x.id === id);
        if (!p) return;
        document.getElementById('lightboxImg').src = p.url || p.thumbnail_url || '';
        document.getElementById('lightboxCaption').textContent = p.caption || '';
        document.getElementById('lightboxMeta').textContent = `${p.date || ''} - ${p.project_name || ''} - ${p.area || ''}`;
        document.getElementById('lightbox').classList.add('active');
        editingId = id;
    }

    function closeLightbox() { document.getElementById('lightbox').classList.remove('active'); }

    function openPhotoDetail(id) {
        const p = photos.find(x => x.id === id);
        if (!p) return;
        editingId = id;
        document.getElementById('photoCaption').value = p.caption || '';
        document.getElementById('photoProject').value = p.project_id || '';
        document.getElementById('photoArea').value = p.area || '';
        document.getElementById('photoTags').value = (p.tags || []).join(', ');
        document.getElementById('photoNotes').value = p.notes || '';
        document.getElementById('photoModal').classList.add('active');
    }

    async function savePhotoDetails(e) {
        e.preventDefault();
        const payload = {
            id: editingId,
            caption: document.getElementById('photoCaption').value,
            project_id: document.getElementById('photoProject').value,
            area: document.getElementById('photoArea').value,
            tags: document.getElementById('photoTags').value.split(',').map(t => t.trim()).filter(Boolean),
            notes: document.getElementById('photoNotes').value
        };
        try {
            await fetch('/api/field/photos', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            closeModal('photoModal');
            loadPhotos();
        } catch(e) { alert('Error saving photo details'); }
    }

    function closeModal(id) { document.getElementById(id).classList.remove('active'); }
    window.addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('active'); });

    document.addEventListener('DOMContentLoaded', loadPhotos);
</script>
"""
