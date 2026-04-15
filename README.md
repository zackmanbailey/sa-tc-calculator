# Post-Patch Verification — New Bug Fixes

**Date:** April 15, 2026
**Context:** Found during post-patch verification of TitanForge v4.2

These 4 bugs were discovered during two full end-to-end simulations
(8 buildings total, both simulations taken through the complete pipeline).

## Bugs Found

| Bug | Description | Severity | File(s) |
|-----|-------------|----------|---------|
| V1 | TC Quote has no save functionality | MEDIUM | tf_handlers.py, tc_quote.py |
| V2 | Space width float remainder triggers false warning | LOW | bom.py |
| V3 | Sidebar display doesn't sync after programmatic update | LOW | sa_calc.py |
| V4 | /api/projects/list returns 404 (API inconsistency) | MEDIUM | tf_handlers.py |

## Priority Order

1. **BUG-V1** — TC Save Handler (MEDIUM, most user-facing impact)
2. **BUG-V4** — Projects List Alias (MEDIUM, quick 1-line fix)
3. **BUG-V2** — Space Width Warning (LOW, 1-line fix)
4. **BUG-V3** — Sidebar Display Sync (LOW, cosmetic only)

## Application Instructions

Each `.py` file contains detailed before/after code and exact file locations.
BUG-V1 requires 3 changes (handler class + route + template button).
BUG-V2, V3, V4 are each single-line or small changes.
