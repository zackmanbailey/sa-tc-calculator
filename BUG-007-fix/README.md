# BUG-007 Fix: Work Order Status Pipeline

## What This Fixes
- Work orders can now advance through the full status pipeline via UI buttons
- **Rollback support**: Any status can be rolled back to a previous state with optional reason
- **Role-based transitions**: Admin approves, Shop Foreman starts/completes, QC signs off
- **Notification system**: In-app notifications when status changes, with 30-second polling
- **Auto-sticker generation**: "Print Stickers & Mark" button opens ZPL for Zebra ZT411 (4x6 labels, 203 DPI)

## Files Modified

### 1. `shop_drawings/work_orders.py` (FULL REPLACEMENT)
**Replace**: `combined_calc/shop_drawings/work_orders.py`
**With**: `BUG-007-fix/work_orders.py`

Changes:
- Added `STATUS_ROLLBACK` dict for backward transitions
- Added `STATUS_TRANSITION_ROLES` for role-based access control
- Added `STATUS_NOTIFICATIONS` templates
- New functions: `change_work_order_status()`, `get_valid_transitions()`, `can_transition()`, `is_rollback()`
- New notification system: `create_notification()`, `get_notifications()`, `mark_notification_read()`, `get_unread_count()`
- All existing functions preserved unchanged

### 2. `tf_handlers.py` (PATCH — add new handlers)
**File**: `combined_calc/tf_handlers.py`
**Reference**: `BUG-007-fix/tf_handlers_patch.py`

Steps:
1. Add imports near top (around line 30) where other work_order imports are:
```python
from shop_drawings.work_orders import (
    change_work_order_status, get_valid_transitions, can_transition,
    get_notifications, mark_notification_read, get_unread_count,
    STATUS_LABELS, VALID_STATUSES
)
```

2. Copy the 5 handler classes from `tf_handlers_patch.py` and paste them AFTER `WorkOrderHoldHandler` (after line ~4689):
   - `WorkOrderStatusChangeHandler`
   - `WorkOrderTransitionsHandler`
   - `NotificationsHandler`
   - `NotificationReadHandler`
   - `NotificationCountHandler`

3. Add these routes to `get_routes()` function (at the bottom of tf_handlers.py):
```python
(r"/api/work-orders/status-change", WorkOrderStatusChangeHandler),
(r"/api/work-orders/transitions", WorkOrderTransitionsHandler),
(r"/api/notifications", NotificationsHandler),
(r"/api/notifications/read", NotificationReadHandler),
(r"/api/notifications/count", NotificationCountHandler),
```

### 3. `templates/work_orders.py` (PATCH — replace JS block)
**File**: `combined_calc/templates/work_orders.py`
**Reference**: `BUG-007-fix/work_orders_template_patch.js`

Steps:
1. In `templates/work_orders.py`, find the `<script>` tag (line 724)
2. Replace everything from `<script>` (line 724) through `</script>` (line 1139) with:
```
<script>
[contents of work_orders_template_patch.js]
</script>
```

3. Add notification bell to the header section. Find this line (~line 658):
```html
<div class="wo-actions">
```
And add this BEFORE the "New Work Order" button:
```html
<div style="position:relative;margin-right:8px;">
    <button class="btn-wo outline" onclick="showNotifications()" title="Notifications" style="font-size:1.1rem;padding:8px 12px;">
        &#128276;
        <span id="notif-badge" style="display:none;position:absolute;top:-4px;right:-4px;background:#EF4444;color:white;font-size:0.65rem;font-weight:700;width:18px;height:18px;border-radius:50%;align-items:center;justify-content:center;">0</span>
    </button>
</div>
```

## Status Flow After Fix

### Forward (Normal Workflow)
```
Queued → Approved → Stickers Printed → In Progress → Complete
                                                         ↓
                                                     QC Review
```

### Rollback (Any User)
```
Complete → In Progress, Stickers Printed, Approved, or Queued
In Progress → Stickers Printed, Approved, or Queued
Stickers Printed → Approved or Queued
Approved → Queued
```

### Hold/Resume
```
Any status (except Complete) → On Hold → Queued or Approved
```

## Role Permissions

| Transition | Allowed Roles |
|-----------|--------------|
| Queued → Approved | Admin, Estimator |
| Approved → Stickers Printed | Admin, Estimator, Shop |
| Stickers Printed → In Progress | Admin, Shop |
| In Progress → Complete | Admin, Shop, QC |
| Any → On Hold | Admin, Estimator, Shop |
| On Hold → Resume | Admin, Estimator |
| Any rollback | Admin, Estimator, Shop, QC |

## API Endpoints Added

| Method | Endpoint | Purpose |
|--------|---------|---------|
| POST | `/api/work-orders/status-change` | Unified status change (forward + rollback) |
| GET | `/api/work-orders/transitions?status=X` | Get valid next statuses |
| GET | `/api/notifications` | Get notification list |
| POST | `/api/notifications/read` | Mark notification as read |
| GET | `/api/notifications/count` | Get unread count |

## Testing
1. Navigate to Work Orders page for any project with a work order
2. Click on a work order to open detail view
3. Use the Approve button → should transition to "Approved"
4. Use "Print Stickers & Mark" → opens PDF + transitions to "Stickers Printed"
5. Click Start on any item → item goes to "In Progress", WO goes to "In Progress"
6. Click Finish on a started item → item completes with duration
7. Test Rollback dropdown → select a previous status → should prompt for reason
8. Check notification bell → should show status change notifications
