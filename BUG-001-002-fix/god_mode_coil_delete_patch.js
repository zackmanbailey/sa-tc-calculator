/**
 * GOD MODE COIL DELETE — Patch for inventory_dashboard_page.py
 * =============================================================
 *
 * INSTRUCTIONS:
 * In inventory_dashboard_page.py, add this delete function to the script section.
 * Also add a delete button to each coil row in the coils table (admin only).
 *
 * 1. Add this JS function:
 */

/**
 * Delete a coil (ADMIN ONLY — "God Mode").
 * Shows confirmation dialog with coil details before deleting.
 */
async function deleteCoil(coilId, coilName) {
  // Check if user is admin
  const userRole = (document.cookie.match(/tf_role=([^;]+)/) || [])[1] || 'admin';
  if (userRole !== 'admin') {
    showToast('Only administrators can delete coils', 'error');
    return;
  }

  // Double confirmation for destructive action
  const confirmed = confirm(
    `⚠️ DELETE COIL: ${coilName} (${coilId})\n\n` +
    `This action is PERMANENT and cannot be undone.\n` +
    `All transaction history for this coil will be preserved in the audit log.\n\n` +
    `Are you sure you want to delete this coil?`
  );

  if (!confirmed) return;

  // Second confirmation with typed input
  const typed = prompt(
    `Type the coil ID "${coilId}" to confirm deletion:`
  );

  if (typed !== coilId) {
    showToast('Deletion cancelled — coil ID did not match', 'info');
    return;
  }

  try {
    const resp = await fetch('/api/inventory/coil/delete', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ coil_id: coilId })
    });
    const result = await resp.json();

    if (result.ok) {
      showToast(`Coil "${coilName}" deleted permanently`, 'success');
      loadCoils(); // Refresh the coils table
    } else {
      showToast('Error: ' + (result.error || 'Unknown'), 'error');
    }
  } catch(e) {
    showToast('Error: ' + e.message, 'error');
  }
}

/*
 * 2. In the coils table rendering, add a delete button column.
 *    Find where coil rows are rendered and add this cell for admin users:
 *
 *    <td class="admin-only" style="display:${userRole === 'admin' ? '' : 'none'}">
 *      <button onclick="deleteCoil('${coil.coil_id}', '${coil.name}')"
 *        class="btn-sm danger" title="Delete coil (Admin only)"
 *        style="background:#EF4444;color:white;border:none;padding:3px 8px;border-radius:4px;cursor:pointer;font-size:0.75rem">
 *        &#128465; Delete
 *      </button>
 *    </td>
 *
 * 3. Add admin-only styling:
 *
 *    .admin-only { /* Shown only for admin role via JS */ }
 */
