/**
 * BUG-006 FIX — Payload patch for buildPayload() in tc_quote.py
 * ===============================================================
 *
 * INSTRUCTIONS:
 * In templates/tc_quote.py, find the buildPayload() function (around line 990).
 *
 * REPLACE the concrete line in the costs object:
 *
 *   concrete: { n_piers: numVal('conc_n_piers'), dia_in: numVal('conc_dia_in'),
 *     depth_ft: numVal('conc_depth_ft'), price_cy: numVal('conc_price_cy'), total: concreteCost },
 *
 * WITH:
 *
 *   concrete: buildConcretePayload(),
 *
 * The buildConcretePayload() function is defined in tc_quote_concrete_patch.js
 * and returns an object with:
 *   { buildings: [...], total_cy: N, total: N, global_price_cy: N }
 *
 * This ensures the per-building breakdown is included in saves and exports.
 */
