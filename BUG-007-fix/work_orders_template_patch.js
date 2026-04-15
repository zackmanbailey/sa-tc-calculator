/**
 * Work Orders Template JavaScript Patch - BUG-007 Fix
 *
 * This file REPLACES the existing <script> block in templates/work_orders.py (lines 724-1139)
 *
 * INCLUDES:
 * - All existing functionality (apiCall, loadWorkOrders, createWorkOrder, etc.)
 * - NEW: Unified status change function (changeStatus)
 * - NEW: Rollback confirmation (rollbackStatus)
 * - NEW: Notification polling and bell system
 * - NEW: Enhanced renderDetail() with rollback dropdown
 */

const JOB_CODE = '{{JOB_CODE}}';
let workOrders = [];
let currentWO = null;
let scanHistory = [];
let unreadCount = 0;

/**
 * NOTIFICATION SYSTEM - BUG-007 Addition
 */

async function pollNotifications() {
    try {
        const data = await apiCall('/api/notifications/count?role=admin', 'GET');
        if (data.ok) {
            unreadCount = data.unread_count;
            updateNotifBadge();
        }
    } catch(e) {
        // Silent fail for polling
    }
}

function updateNotifBadge() {
    const badge = document.getElementById('notif-badge');
    if (badge) {
        badge.textContent = unreadCount;
        badge.style.display = unreadCount > 0 ? 'inline-flex' : 'none';
    }
}

async function showNotifications() {
    const data = await apiCall('/api/notifications?limit=20', 'GET');
    if (!data.ok) return;

    let html = '<div style="max-height:400px;overflow-y:auto;">';
    if (data.notifications.length === 0) {
        html += '<p style="color:var(--tf-slate);padding:16px;">No notifications</p>';
    }
    data.notifications.forEach(n => {
        const time = new Date(n.timestamp).toLocaleString();
        const statusBadge = `<span class="status-badge ${n.to_status}">${n.to_status}</span>`;
        html += `<div style="padding:12px 16px;border-bottom:1px solid var(--tf-border);font-size:0.85rem;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <strong>${n.wo_id}</strong> ${statusBadge}
            </div>
            <div style="color:var(--tf-slate);">${n.message}</div>
            <div style="color:var(--tf-slate);font-size:0.75rem;margin-top:4px;">${time} by ${n.changed_by}</div>
        </div>`;
    });
    html += '</div>';

    const modal = document.createElement('div');
    modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.4);z-index:10000;display:flex;align-items:center;justify-content:center;';
    modal.onclick = (e) => { if(e.target === modal) modal.remove(); };
    modal.innerHTML = `<div style="background:white;border-radius:12px;width:500px;max-width:90vw;overflow:hidden;">
        <div style="padding:16px 20px;border-bottom:1px solid var(--tf-border);display:flex;justify-content:space-between;align-items:center;">
            <h3 style="margin:0;font-size:1.1rem;">Notifications</h3>
            <button onclick="this.closest('div[style*=fixed]').remove()" style="background:none;border:none;font-size:1.2rem;cursor:pointer;">&times;</button>
        </div>
        ${html}
    </div>`;
    document.body.appendChild(modal);
}

/**
 * STATUS CHANGE FUNCTIONS - BUG-007 Addition
 */

async function changeStatus(woId, newStatus, notes='') {
    const data = await apiCall('/api/work-orders/status-change', 'POST', {
        job_code: JOB_CODE,
        wo_id: woId,
        new_status: newStatus,
        notes: notes
    });

    if (data.ok) {
        showToast(data.message || 'Status updated', data.rollback ? 'info' : 'success');
        currentWO = data.work_order;
        await refreshAll();
        renderDetail();
    } else {
        showToast(data.error || 'Status change failed', 'error');
    }
}

async function rollbackStatus(woId, newStatus, label) {
    const reason = prompt(`Rolling back to "${label}". Enter reason (optional):`);
    if (reason === null) return; // cancelled
    await changeStatus(woId, newStatus, reason);
}

/**
 * CORE API AND DATA FUNCTIONS
 */

async function refreshAll() {
    await loadWorkOrders();
    await pollNotifications();
}

async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (data) options.body = JSON.stringify(data);

    try {
        const response = await fetch(endpoint, options);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { ok: false, error: error.message };
    }
}

async function loadWorkOrders() {
    const data = await apiCall('/api/work-orders?job_code=' + JOB_CODE);
    if (data.ok) {
        workOrders = data.work_orders || [];
        renderOverview();
    }
}

async function loadWODetail(woId) {
    const data = await apiCall('/api/work-orders/' + woId);
    if (data.ok) {
        currentWO = data.work_order;
        scanHistory = data.scan_history || [];
        renderDetail();
    }
}

async function createWorkOrder(formData) {
    const data = await apiCall('/api/work-orders', 'POST', {
        job_code: JOB_CODE,
        ...formData
    });

    if (data.ok) {
        showToast('Work Order created', 'success');
        document.getElementById('createWOForm').reset();
        await refreshAll();
    } else {
        showToast(data.error || 'Failed to create', 'error');
    }
}

/**
 * STATUS CHANGE ACTIONS - EXISTING FUNCTIONALITY (Legacy wrapper functions)
 */

async function approveWO(woId) {
    await changeStatus(woId, 'approved');
}

async function markStickersPrinted(woId) {
    await changeStatus(woId, 'stickers_printed');
}

async function holdWO(woId) {
    await changeStatus(woId, 'on_hold');
}

/**
 * SCANNING FUNCTIONS
 */

async function scanItem(woId, itemId) {
    const data = await apiCall('/api/work-orders/scan-item', 'POST', {
        wo_id: woId,
        item_id: itemId
    });

    if (data.ok) {
        scanHistory = data.scan_history || [];
        renderScanHistory();
        showToast('Item scanned', 'success');
    } else {
        showToast(data.error || 'Scan failed', 'error');
    }
}

async function processQRScan(qrData) {
    if (!currentWO) {
        showToast('No work order selected', 'error');
        return;
    }

    // Parse QR data (format: WO|ITEM or similar)
    const parts = qrData.split('|');
    if (parts.length >= 2) {
        const itemId = parts[1];
        await scanItem(currentWO.work_order_id, itemId);
    } else {
        showToast('Invalid QR code format', 'error');
    }
}

/**
 * UI NAVIGATION
 */

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

    const tabEl = document.getElementById(tabName);
    if (tabEl) tabEl.style.display = 'block';

    const btnEl = document.querySelector(`[onclick="switchTab('${tabName}')"]`);
    if (btnEl) btnEl.classList.add('active');
}

/**
 * RENDERING FUNCTIONS
 */

function renderOverview() {
    const container = document.getElementById('overview-content');
    if (!container) return;

    let html = '<table class="wo-table"><thead><tr><th>WO ID</th><th>Status</th><th>Created</th><th>Action</th></tr></thead><tbody>';

    workOrders.forEach(wo => {
        const statusClass = `status-${wo.status}`;
        const created = new Date(wo.created_at).toLocaleDateString();
        html += `<tr>
            <td><strong>${wo.work_order_id}</strong></td>
            <td><span class="status-badge ${wo.status}">${wo.status}</span></td>
            <td>${created}</td>
            <td><button class="btn-wo primary" onclick="loadWODetail('${wo.work_order_id}'); switchTab('detail')">View</button></td>
        </tr>`;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

function renderDetail() {
    const container = document.getElementById('detail-content');
    if (!container || !currentWO) return;

    const wo = currentWO;
    const woId = wo.work_order_id;

    // Status badge
    let html = `<div class="wo-detail">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
            <h2>${wo.work_order_id}</h2>
            <span class="status-badge ${wo.status}">${wo.status}</span>
        </div>

        <div class="wo-info-grid">
            <div><strong>Created:</strong> ${new Date(wo.created_at).toLocaleString()}</div>
            <div><strong>Updated:</strong> ${new Date(wo.updated_at).toLocaleString()}</div>
            <div><strong>Items:</strong> ${wo.items ? wo.items.length : 0}</div>
        </div>
    `;

    // Items table
    if (wo.items && wo.items.length > 0) {
        html += '<h3 style="margin-top:20px;">Items</h3><table class="wo-table"><thead><tr><th>Item ID</th><th>Description</th><th>Qty</th><th>Status</th></tr></thead><tbody>';
        wo.items.forEach(item => {
            html += `<tr>
                <td>${item.item_id}</td>
                <td>${item.description || '-'}</td>
                <td>${item.quantity}</td>
                <td><span class="status-badge ${item.status}">${item.status}</span></td>
            </tr>`;
        });
        html += '</tbody></table>';
    }

    // Action buttons - BUG-007 Enhanced with rollback
    let actionsHtml = '';

    // Sticker download buttons (always available)
    const stickerBtns = `<button class="btn-wo outline" onclick="printStickers('${woId}')">&#128438; Print Stickers</button>
                         <button class="btn-wo outline" onclick="downloadPacketPDF('${woId}')">&#128196; Download PDF</button>`;

    // Forward actions based on status
    if (wo.status === 'queued') {
        actionsHtml = `<button class="btn-wo success" onclick="changeStatus('${woId}','approved')">&#10003; Approve</button>
                       <button class="btn-wo warning" onclick="changeStatus('${woId}','on_hold')">&#9888; Hold</button>`;
    } else if (wo.status === 'approved') {
        actionsHtml = `${stickerBtns}
                       <button class="btn-wo primary" onclick="printAndMark('${woId}')">&#9113; Print Stickers & Mark</button>
                       <button class="btn-wo warning" onclick="changeStatus('${woId}','on_hold')">&#9888; Hold</button>`;
    } else if (wo.status === 'on_hold') {
        actionsHtml = `<button class="btn-wo success" onclick="changeStatus('${woId}','approved')">&#9654; Resume (Approved)</button>
                       <button class="btn-wo outline" onclick="changeStatus('${woId}','queued')">&#8634; Back to Queued</button>`;
    } else if (wo.status === 'stickers_printed') {
        actionsHtml = `${stickerBtns}
                       <button class="btn-wo warning" onclick="changeStatus('${woId}','on_hold')">&#9888; Hold</button>`;
    } else if (wo.status === 'in_progress') {
        actionsHtml = `${stickerBtns}
                       <button class="btn-wo warning" onclick="changeStatus('${woId}','on_hold')">&#9888; Hold</button>`;
    } else if (wo.status === 'complete') {
        actionsHtml = stickerBtns;
    }

    // Rollback dropdown (for any non-queued, non-hold status)
    if (wo.status !== 'queued' && wo.status !== 'on_hold') {
        let rollbackOptions = '';
        const rollbackMap = {
            'approved': [{ s: 'queued', l: 'Queued' }],
            'stickers_printed': [{ s: 'queued', l: 'Queued' }, { s: 'approved', l: 'Approved' }],
            'in_progress': [{ s: 'queued', l: 'Queued' }, { s: 'approved', l: 'Approved' }, { s: 'stickers_printed', l: 'Stickers Printed' }],
            'complete': [{ s: 'queued', l: 'Queued' }, { s: 'approved', l: 'Approved' }, { s: 'stickers_printed', l: 'Stickers Printed' }, { s: 'in_progress', l: 'In Progress' }],
        };
        const options = rollbackMap[wo.status] || [];
        if (options.length > 0) {
            options.forEach(opt => {
                rollbackOptions += `<div class="rollback-option" onclick="rollbackStatus('${woId}','${opt.s}','${opt.l}')" style="padding:8px 16px;cursor:pointer;font-size:0.85rem;white-space:nowrap;"
                    onmouseover="this.style.background='var(--tf-bg)'" onmouseout="this.style.background='white'">
                    &#8634; ${opt.l}</div>`;
            });
            actionsHtml += `<div style="position:relative;display:inline-block;">
                <button class="btn-wo outline" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block'">&#8634; Rollback &#9662;</button>
                <div style="display:none;position:absolute;top:100%;right:0;background:white;border:1px solid var(--tf-border);border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.1);z-index:100;margin-top:4px;">
                    ${rollbackOptions}
                </div>
            </div>`;
        }
    }

    html += `<div style="margin-top:20px;display:flex;gap:10px;flex-wrap:wrap;">
        ${actionsHtml}
    </div>`;

    html += '</div>';
    container.innerHTML = html;
}

function renderScanHistory() {
    const container = document.getElementById('scan-history-content');
    if (!container) return;

    let html = '<h3>Scan History</h3>';

    if (scanHistory.length === 0) {
        html += '<p style="color:var(--tf-slate);">No scans recorded</p>';
    } else {
        html += '<table class="wo-table"><thead><tr><th>Item ID</th><th>Scanned At</th><th>Status</th></tr></thead><tbody>';
        scanHistory.forEach(scan => {
            const scannedAt = new Date(scan.scanned_at).toLocaleString();
            html += `<tr>
                <td>${scan.item_id}</td>
                <td>${scannedAt}</td>
                <td><span class="status-badge scanned">Scanned</span></td>
            </tr>`;
        });
        html += '</tbody></table>';
    }

    container.innerHTML = html;
}

/**
 * PRINTING FUNCTIONS
 */

async function printStickers(woId) {
    const data = await apiCall('/api/work-orders/' + woId + '/print-stickers', 'POST');

    if (data.ok) {
        showToast('Stickers queued for printing', 'success');
    } else {
        showToast(data.error || 'Print failed', 'error');
    }
}

async function printSingleSticker(woId, itemId) {
    const data = await apiCall('/api/work-orders/' + woId + '/print-sticker', 'POST', {
        item_id: itemId
    });

    if (data.ok) {
        showToast('Sticker queued for printing', 'success');
    } else {
        showToast(data.error || 'Print failed', 'error');
    }
}

async function printAndMark(woId) {
    const data = await apiCall('/api/work-orders/' + woId + '/print-and-mark', 'POST');

    if (data.ok) {
        showToast('Stickers printed and marked', 'success');
        currentWO = data.work_order;
        await refreshAll();
        renderDetail();
    } else {
        showToast(data.error || 'Operation failed', 'error');
    }
}

async function downloadPacketPDF(woId) {
    window.location.href = '/api/work-orders/' + woId + '/packet-pdf?job_code=' + JOB_CODE;
}

/**
 * TOAST NOTIFICATION
 */

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        z-index: 9999;
        font-size: 0.95rem;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * INITIALIZATION
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tabs
    switchTab('overview');

    // Load initial data
    loadWorkOrders();

    // Start notification polling
    pollNotifications();

    // Poll notifications every 30 seconds
    setInterval(pollNotifications, 30000);

    // QR scan listener (if scanner input exists)
    const scanInput = document.getElementById('qr-scan-input');
    if (scanInput) {
        scanInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                processQRScan(this.value);
                this.value = '';
            }
        });
    }
});
