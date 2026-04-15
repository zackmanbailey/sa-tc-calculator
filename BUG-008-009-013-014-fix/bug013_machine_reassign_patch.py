"""
BUG-013 FIX — Machine Assignment Reassignment
===============================================

INSTRUCTIONS:

1. Add this function to shop_drawings/work_orders.py:
"""

# ── ADD to shop_drawings/work_orders.py after qr_scan_finish() ──

VALID_MACHINES = ["WELDING", "Z1", "C1", "P1", "ANGLE", "SPARTAN", "C2", "REBAR", "CLEANING"]

def reassign_machine(base_dir, job_code, wo_id, item_id, new_machine, changed_by="system"):
    """Reassign a work order item to a different machine.

    BUG-013 FIX: Allows any shop-floor role to change machine assignments
    after work orders are created.

    Returns: {"ok": True/False, "item": {...}, "error": "..."}
    """
    if new_machine not in VALID_MACHINES:
        return {"ok": False, "error": f"Invalid machine: {new_machine}. Valid: {', '.join(VALID_MACHINES)}"}

    wo = load_work_order(base_dir, job_code, wo_id)
    if not wo:
        return {"ok": False, "error": f"Work order {wo_id} not found"}

    target_item = None
    for item in wo.items:
        if item.item_id == item_id:
            target_item = item
            break

    if not target_item:
        return {"ok": False, "error": f"Item {item_id} not found in {wo_id}"}

    # Cannot reassign items that are already in progress or complete
    if target_item.status in [STATUS_IN_PROGRESS, STATUS_COMPLETE]:
        return {
            "ok": False,
            "error": f"Cannot reassign machine for item in status '{target_item.status}'. "
                     f"Item must be in 'queued' or 'stickers_printed' status."
        }

    old_machine = target_item.machine
    target_item.machine = new_machine

    # Log the change in the item's notes
    import datetime
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    change_note = f"[{timestamp}] Machine reassigned: {old_machine} -> {new_machine} by {changed_by}"
    if target_item.notes:
        target_item.notes += " | " + change_note
    else:
        target_item.notes = change_note

    save_work_order(base_dir, job_code, wo)
    return {
        "ok": True,
        "item": {
            "item_id": target_item.item_id,
            "machine": new_machine,
            "old_machine": old_machine,
            "changed_by": changed_by,
        }
    }


"""
2. Add this handler class to tf_handlers.py:
"""

class WorkOrderMachineReassignHandler(BaseHandler):
    """POST /api/work-orders/reassign-machine — Reassign item to different machine.

    BUG-013 FIX: Any shop role can reassign machines.
    Body: { job_code, wo_id, item_id, new_machine }
    """
    required_roles = ["admin", "estimator", "shop", "qc"]

    def post(self):
        try:
            body = json_decode(self.request.body)
            job_code = body.get("job_code", "").strip()
            wo_id = body.get("wo_id", "").strip()
            item_id = body.get("item_id", "").strip()
            new_machine = body.get("new_machine", "").strip().upper()

            if not all([job_code, wo_id, item_id, new_machine]):
                self.write(json_encode({
                    "ok": False, "error": "Missing required fields"
                }))
                return

            from shop_drawings.work_orders import reassign_machine
            changed_by = body.get("changed_by", self.get_current_user() or "system")
            result = reassign_machine(
                SHOP_DRAWINGS_DIR, job_code, wo_id, item_id,
                new_machine, changed_by=changed_by
            )

            self.set_header("Content-Type", "application/json")
            self.write(json_encode(result))
        except Exception as e:
            self.set_status(500)
            self.write(json_encode({"ok": False, "error": str(e)}))


"""
3. Add this route to get_routes():
   (r"/api/work-orders/reassign-machine", WorkOrderMachineReassignHandler),

4. In templates/work_orders.py, update the items table rendering.
   Find the machine badge display (around line 1018):

     <td><span class="machine-badge">${item.machine}</span></td>

   REPLACE with:

     <td>
       <select class="machine-select" onchange="reassignMachine('${wo.job_code}','${wo.work_order_id}','${item.item_id}',this.value)"
         ${item.status === 'in_progress' || item.status === 'complete' ? 'disabled' : ''}
         style="padding:3px 8px;border-radius:4px;font-size:0.8rem;font-weight:600;border:1.5px solid #D0D7E2;background:${item.status === 'in_progress' || item.status === 'complete' ? '#F1F5F9' : 'white'}">
         ${['WELDING','Z1','C1','P1','ANGLE','SPARTAN','C2','REBAR','CLEANING'].map(m =>
           '<option value="'+m+'"'+(m===item.machine?' selected':'')+'>'+m+'</option>'
         ).join('')}
       </select>
     </td>

5. Add this JS function to the work orders template script:

   async function reassignMachine(jobCode, woId, itemId, newMachine) {
     const result = await apiCall('/api/work-orders/reassign-machine', 'POST', {
       job_code: jobCode, wo_id: woId, item_id: itemId, new_machine: newMachine
     });
     if (result.ok) {
       showToast('Machine reassigned to ' + newMachine, 'success');
     } else {
       showToast('Error: ' + (result.error || 'Unknown'), 'error');
       loadWODetail(woId);  // Reload to revert the select
     }
   }
"""
