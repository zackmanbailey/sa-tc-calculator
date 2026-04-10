"""
TitanForge — Shipping Hub Template
===================================
Full HTML page for managing shipping documents: packing lists, bills of lading,
shipping manifests, purchase orders, and inventory reorder alerts.

Provides tabbed interface for document generation, viewing, and printing.
Dark theme with print-friendly CSS for physical document output.
"""

SHIPPING_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shipping Hub — {{JOB_CODE}} | TitanForge</title>
    <style>
        /* ============================================================
           TitanForge Design System — Shipping Hub
           ============================================================ */

        :root {
            /* Brand Colors */
            --tf-navy:       #0F172A;
            --tf-navy-light: #1E293B;
            --tf-blue:       #1E40AF;
            --tf-blue-mid:   #2563EB;
            --tf-blue-light: #DBEAFE;
            --tf-amber:      #F59E0B;
            --tf-gold:       #F6AE2D;
            --tf-amber-light:#FEF3C7;

            /* Semantic Colors */
            --tf-success:    #059669;
            --tf-success-bg: #ECFDF5;
            --tf-warning:    #D97706;
            --tf-warning-bg: #FFFBEB;
            --tf-danger:     #DC2626;
            --tf-danger-bg:  #FEF2F2;
            --tf-info:       #0284C7;
            --tf-info-bg:    #F0F9FF;

            /* Neutrals */
            --tf-gray-50:    #F8FAFC;
            --tf-gray-100:   #F1F5F9;
            --tf-gray-200:   #E2E8F0;
            --tf-gray-300:   #CBD5E1;
            --tf-gray-400:   #94A3B8;
            --tf-gray-500:   #64748B;
            --tf-gray-600:   #475569;
            --tf-gray-700:   #334155;
            --tf-gray-800:   #1E293B;
            --tf-gray-900:   #0F172A;

            /* Surfaces — Dark Theme */
            --tf-bg:         #0F172A;
            --tf-surface:    #1E293B;
            --tf-border:     #334155;
            --tf-text:       #F1F5F9;
            --tf-text-muted: #94A3B8;

            /* Typography */
            --tf-font:       'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
            --tf-font-mono:  'JetBrains Mono', 'Fira Code', 'Consolas', monospace;

            /* Type Scale */
            --tf-text-xs:    0.75rem;
            --tf-text-sm:    0.8125rem;
            --tf-text-base:  0.875rem;
            --tf-text-md:    1rem;
            --tf-text-lg:    1.125rem;
            --tf-text-xl:    1.25rem;
            --tf-text-2xl:   1.5rem;

            /* Spacing */
            --tf-sp-2:  0.5rem;
            --tf-sp-3:  0.75rem;
            --tf-sp-4:  1rem;
            --tf-sp-6:  1.5rem;
            --tf-sp-8:  2rem;

            /* Radii & Shadows */
            --tf-radius:    8px;
            --tf-shadow:    0 1px 3px rgba(0,0,0,0.3);
            --tf-shadow-lg: 0 10px 15px rgba(0,0,0,0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: var(--tf-font);
            background-color: var(--tf-bg);
            color: var(--tf-text);
            line-height: 1.6;
        }

        /* ── Containers ────────────────────────────────────────────── */

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: var(--tf-sp-6);
        }

        .page-header {
            margin-bottom: var(--tf-sp-8);
        }

        .page-title {
            font-size: var(--tf-text-2xl);
            font-weight: 700;
            color: var(--tf-gold);
            margin-bottom: var(--tf-sp-4);
        }

        .page-subtitle {
            font-size: var(--tf-text-base);
            color: var(--tf-text-muted);
        }

        /* ── Tabs ──────────────────────────────────────────────────── */

        .tabs {
            display: flex;
            gap: var(--tf-sp-2);
            margin-bottom: var(--tf-sp-6);
            border-bottom: 2px solid var(--tf-border);
            overflow-x: auto;
        }

        .tab-button {
            padding: var(--tf-sp-3) var(--tf-sp-6);
            background: none;
            border: none;
            color: var(--tf-text-muted);
            font-size: var(--tf-text-base);
            font-weight: 600;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 150ms ease;
            white-space: nowrap;
        }

        .tab-button:hover {
            color: var(--tf-gold);
        }

        .tab-button.active {
            color: var(--tf-gold);
            border-bottom-color: var(--tf-gold);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        /* ── Cards ────────────────────────────────────────────────── */

        .card {
            background-color: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius);
            padding: var(--tf-sp-6);
            margin-bottom: var(--tf-sp-6);
            box-shadow: var(--tf-shadow);
        }

        .card-header {
            font-size: var(--tf-text-lg);
            font-weight: 600;
            color: var(--tf-text);
            margin-bottom: var(--tf-sp-4);
            border-bottom: 1px solid var(--tf-border);
            padding-bottom: var(--tf-sp-4);
        }

        /* ── Forms ────────────────────────────────────────────────── */

        .form-group {
            margin-bottom: var(--tf-sp-6);
        }

        .form-label {
            display: block;
            font-weight: 600;
            color: var(--tf-text);
            margin-bottom: var(--tf-sp-2);
            font-size: var(--tf-text-sm);
        }

        .form-input,
        .form-textarea,
        .form-select {
            width: 100%;
            padding: var(--tf-sp-3);
            background-color: var(--tf-navy);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius);
            color: var(--tf-text);
            font-family: var(--tf-font);
            font-size: var(--tf-text-base);
        }

        .form-input:focus,
        .form-textarea:focus,
        .form-select:focus {
            outline: none;
            border-color: var(--tf-gold);
            box-shadow: 0 0 0 3px rgba(246, 174, 45, 0.1);
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--tf-sp-6);
        }

        .form-row.thirds {
            grid-template-columns: 1fr 1fr 1fr;
        }

        /* ── Line Items Table ──────────────────────────────────────── */

        .line-items-table {
            width: 100%;
            border-collapse: collapse;
            margin: var(--tf-sp-6) 0;
        }

        .line-items-table th {
            background-color: var(--tf-navy);
            color: var(--tf-text);
            font-weight: 600;
            padding: var(--tf-sp-3);
            text-align: left;
            border: 1px solid var(--tf-border);
            font-size: var(--tf-text-sm);
        }

        .line-items-table td {
            padding: var(--tf-sp-3);
            border: 1px solid var(--tf-border);
            font-size: var(--tf-text-sm);
        }

        .line-items-table tr:nth-child(even) {
            background-color: var(--tf-navy);
        }

        .line-items-table .numeric {
            text-align: right;
            font-family: var(--tf-font-mono);
        }

        .line-item-row {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr auto;
            gap: var(--tf-sp-4);
            align-items: center;
            margin-bottom: var(--tf-sp-4);
            padding: var(--tf-sp-4);
            background-color: var(--tf-navy);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius);
        }

        .line-item-row input {
            width: 100%;
            padding: var(--tf-sp-2);
            background-color: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: 4px;
            color: var(--tf-text);
        }

        /* ── Buttons ───────────────────────────────────────────────── */

        .btn {
            display: inline-block;
            padding: var(--tf-sp-3) var(--tf-sp-6);
            background-color: var(--tf-blue-mid);
            color: white;
            border: none;
            border-radius: var(--tf-radius);
            font-weight: 600;
            cursor: pointer;
            font-size: var(--tf-text-base);
            transition: all 150ms ease;
        }

        .btn:hover {
            background-color: var(--tf-blue);
        }

        .btn-gold {
            background-color: var(--tf-gold);
            color: var(--tf-navy);
        }

        .btn-gold:hover {
            background-color: #FFB84D;
        }

        .btn-success {
            background-color: var(--tf-success);
        }

        .btn-success:hover {
            background-color: #047857;
        }

        .btn-danger {
            background-color: var(--tf-danger);
        }

        .btn-danger:hover {
            background-color: #B91C1C;
        }

        .btn-small {
            padding: var(--tf-sp-2) var(--tf-sp-4);
            font-size: var(--tf-text-sm);
        }

        .btn-group {
            display: flex;
            gap: var(--tf-sp-4);
            margin-top: var(--tf-sp-6);
        }

        /* ── Checkboxes ────────────────────────────────────────────– */

        .checkbox-list {
            display: flex;
            flex-direction: column;
            gap: var(--tf-sp-4);
        }

        .checkbox-item {
            display: flex;
            align-items: center;
            gap: var(--tf-sp-3);
        }

        .checkbox-item input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
            accent-color: var(--tf-gold);
        }

        .checkbox-item label {
            cursor: pointer;
            flex: 1;
        }

        /* ── Data Display ──────────────────────────────────────────– */

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--tf-sp-6);
            margin-bottom: var(--tf-sp-6);
        }

        .info-item {
            background-color: var(--tf-navy);
            padding: var(--tf-sp-4);
            border-radius: var(--tf-radius);
            border: 1px solid var(--tf-border);
        }

        .info-label {
            font-size: var(--tf-text-xs);
            color: var(--tf-text-muted);
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: var(--tf-sp-2);
        }

        .info-value {
            font-size: var(--tf-text-lg);
            color: var(--tf-text);
            font-weight: 600;
        }

        /* ── Table Styles ──────────────────────────────────────────– */

        .data-table {
            width: 100%;
            border-collapse: collapse;
        }

        .data-table th {
            background-color: var(--tf-navy);
            color: var(--tf-text);
            padding: var(--tf-sp-4);
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid var(--tf-border);
        }

        .data-table td {
            padding: var(--tf-sp-4);
            border-bottom: 1px solid var(--tf-border);
        }

        .data-table tr:hover {
            background-color: var(--tf-navy);
        }

        .data-table .numeric {
            text-align: right;
            font-family: var(--tf-font-mono);
        }

        /* ── Alerts ────────────────────────────────────────────────– */

        .alert {
            padding: var(--tf-sp-4);
            border-radius: var(--tf-radius);
            margin-bottom: var(--tf-sp-6);
            font-size: var(--tf-text-sm);
        }

        .alert-info {
            background-color: var(--tf-info-bg);
            border: 1px solid var(--tf-info);
            color: var(--tf-info);
        }

        .alert-warning {
            background-color: var(--tf-warning-bg);
            border: 1px solid var(--tf-warning);
            color: var(--tf-warning);
        }

        .alert-danger {
            background-color: var(--tf-danger-bg);
            border: 1px solid var(--tf-danger);
            color: var(--tf-danger);
        }

        .alert-success {
            background-color: var(--tf-success-bg);
            border: 1px solid var(--tf-success);
            color: var(--tf-success);
        }

        /* ── Status Badge ──────────────────────────────────────────– */

        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: var(--tf-text-xs);
            font-weight: 600;
        }

        .badge-success {
            background-color: var(--tf-success-bg);
            color: var(--tf-success);
        }

        .badge-warning {
            background-color: var(--tf-warning-bg);
            color: var(--tf-warning);
        }

        .badge-danger {
            background-color: var(--tf-danger-bg);
            color: var(--tf-danger);
        }

        /* ── Print Styles ──────────────────────────────────────────– */

        @media print {
            body {
                background-color: white;
                color: #000;
            }

            .container {
                max-width: 100%;
                padding: 0;
            }

            {{NAV_HTML}} {
                display: none !important;
            }

            .tabs, .tab-button, .btn-group, .btn {
                display: none !important;
            }

            .page-header {
                margin-bottom: 20px;
            }

            .card {
                background-color: white;
                border: 1px solid #000;
                box-shadow: none;
                page-break-inside: avoid;
            }

            .card-header {
                border-bottom: 2px solid #000;
                font-weight: bold;
            }

            .line-items-table {
                width: 100%;
                border-collapse: collapse;
            }

            .line-items-table th,
            .line-items-table td {
                border: 1px solid #000;
                padding: 8px;
                text-align: left;
            }

            .data-table th {
                background-color: #f0f0f0;
                color: #000;
            }

            .data-table td {
                border-bottom: 1px solid #000;
            }

            .form-input, .form-select, .form-textarea {
                border: 1px solid #000;
                background-color: white;
                color: #000;
            }

            .info-item {
                background-color: white;
                border: 1px solid #000;
            }

            .alert {
                border: 1px solid #000;
            }
        }

        /* ── Loading State ─────────────────────────────────────────– */

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid var(--tf-border);
            border-top: 3px solid var(--tf-gold);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    {{NAV_HTML}}

    <div class="container">
        <!-- Page Header -->
        <div class="page-header">
            <h1 class="page-title">Shipping Hub</h1>
            <p class="page-subtitle">Job Code: <strong>{{JOB_CODE}}</strong></p>
        </div>

        <!-- Tabs -->
        <div class="tabs">
            <button class="tab-button active" data-tab="packing-lists">
                📦 Packing Lists
            </button>
            <button class="tab-button" data-tab="bills-of-lading">
                📄 Bills of Lading
            </button>
            <button class="tab-button" data-tab="manifests">
                🚚 Shipping Manifest
            </button>
            <button class="tab-button" data-tab="purchase-orders">
                💳 Purchase Orders
            </button>
            <button class="tab-button" data-tab="reorder-alerts">
                ⚠️ Reorder Alerts
            </button>
        </div>

        <!-- ================================================================
             TAB 1: PACKING LISTS
             ================================================================ -->
        <div id="packing-lists" class="tab-content active">
            <div class="card">
                <div class="card-header">Create Packing List</div>

                <div class="form-group">
                    <label class="form-label">Select Items to Pack</label>
                    <div class="checkbox-list" id="packing-items-list">
                        <!-- Populated by JavaScript from work order -->
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Ship Date</label>
                        <input type="date" class="form-input" id="pack-ship-date">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Truck Number</label>
                        <input type="text" class="form-input" id="pack-truck-number" placeholder="e.g., T001">
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Trailer Number</label>
                        <input type="text" class="form-input" id="pack-trailer-number" placeholder="e.g., TR001">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Driver Name</label>
                        <input type="text" class="form-input" id="pack-driver-name">
                    </div>
                </div>

                <div class="btn-group">
                    <button class="btn btn-gold" onclick="generatePackingList()">
                        Generate Packing List
                    </button>
                    <button class="btn" onclick="printPackingList()">
                        🖨️ Print
                    </button>
                </div>
            </div>

            <div class="card">
                <div class="card-header">Previous Packing Lists</div>
                <div id="packing-lists-history">
                    <p style="color: var(--tf-text-muted);">No packing lists yet.</p>
                </div>
            </div>
        </div>

        <!-- ================================================================
             TAB 2: BILLS OF LADING
             ================================================================ -->
        <div id="bills-of-lading" class="tab-content">
            <div class="card">
                <div class="card-header">Create Bill of Lading</div>

                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Carrier Name</label>
                        <input type="text" class="form-input" id="bol-carrier-name" placeholder="e.g., XYZ Trucking">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Driver Name</label>
                        <input type="text" class="form-input" id="bol-driver-name">
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Truck Number</label>
                        <input type="text" class="form-input" id="bol-truck-number">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Trailer Number</label>
                        <input type="text" class="form-input" id="bol-trailer-number">
                    </div>
                </div>

                <fieldset>
                    <legend style="color: var(--tf-text); margin-bottom: var(--tf-sp-4); font-weight: 600;">
                        Consignee (Destination)
                    </legend>

                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Company Name</label>
                            <input type="text" class="form-input" id="bol-consignee-company">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Contact Person</label>
                            <input type="text" class="form-input" id="bol-consignee-contact">
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Address</label>
                        <input type="text" class="form-input" id="bol-consignee-address">
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">City</label>
                            <input type="text" class="form-input" id="bol-consignee-city">
                        </div>
                        <div class="form-group">
                            <label class="form-label">State</label>
                            <input type="text" class="form-input" id="bol-consignee-state" style="max-width: 80px;">
                        </div>
                        <div class="form-group">
                            <label class="form-label">ZIP</label>
                            <input type="text" class="form-input" id="bol-consignee-zip" style="max-width: 120px;">
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Phone</label>
                        <input type="text" class="form-input" id="bol-consignee-phone">
                    </div>
                </fieldset>

                <div class="btn-group">
                    <button class="btn btn-gold" onclick="generateBOL()">
                        Generate Bill of Lading
                    </button>
                    <button class="btn" onclick="printBOL()">
                        🖨️ Print
                    </button>
                </div>
            </div>

            <div class="card">
                <div class="card-header">Previous Bills of Lading</div>
                <div id="bol-history">
                    <p style="color: var(--tf-text-muted);">No BOLs yet.</p>
                </div>
            </div>
        </div>

        <!-- ================================================================
             TAB 3: SHIPPING MANIFEST
             ================================================================ -->
        <div id="manifests" class="tab-content">
            <div class="card">
                <div class="card-header">Shipping Manifest</div>
                <p style="margin-bottom: var(--tf-sp-4); color: var(--tf-text-muted);">
                    Consolidated view of all truck loads for this job. Items are sorted by weight (heaviest first).
                </p>

                <div id="manifest-display">
                    <p style="color: var(--tf-text-muted);">Load data will appear here.</p>
                </div>

                <div class="btn-group">
                    <button class="btn btn-gold" onclick="generateManifest()">
                        Generate Manifest
                    </button>
                    <button class="btn" onclick="printManifest()">
                        🖨️ Print
                    </button>
                </div>
            </div>
        </div>

        <!-- ================================================================
             TAB 4: PURCHASE ORDERS
             ================================================================ -->
        <div id="purchase-orders" class="tab-content">
            <div class="card">
                <div class="card-header">Create Purchase Order</div>

                <div class="form-group">
                    <label class="form-label">PO Number (auto-generated if blank)</label>
                    <input type="text" class="form-input" id="po-number" placeholder="Leave blank for auto">
                </div>

                <fieldset>
                    <legend style="color: var(--tf-text); margin-bottom: var(--tf-sp-4); font-weight: 600;">
                        Vendor Information
                    </legend>

                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Vendor Name</label>
                            <input type="text" class="form-input" id="po-vendor-name">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Contact</label>
                            <input type="text" class="form-input" id="po-vendor-contact">
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Address</label>
                        <input type="text" class="form-input" id="po-vendor-address">
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">City</label>
                            <input type="text" class="form-input" id="po-vendor-city">
                        </div>
                        <div class="form-group">
                            <label class="form-label">State</label>
                            <input type="text" class="form-input" id="po-vendor-state" style="max-width: 80px;">
                        </div>
                        <div class="form-group">
                            <label class="form-label">ZIP</label>
                            <input type="text" class="form-input" id="po-vendor-zip" style="max-width: 120px;">
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Phone</label>
                        <input type="text" class="form-input" id="po-vendor-phone">
                    </div>
                </fieldset>

                <div class="form-group">
                    <label class="form-label">Requested Delivery Date</label>
                    <input type="date" class="form-input" id="po-delivery-date">
                </div>

                <div class="form-group">
                    <label class="form-label">Notes / Special Instructions</label>
                    <textarea class="form-textarea" id="po-notes" rows="3"></textarea>
                </div>

                <div class="card" style="margin-top: var(--tf-sp-6); background-color: var(--tf-navy);">
                    <div class="card-header">Line Items</div>

                    <div id="po-line-items-editor">
                        <!-- Dynamically populated -->
                    </div>

                    <button class="btn btn-small" onclick="addPOLineItem()" style="margin-top: var(--tf-sp-4);">
                        + Add Line Item
                    </button>
                </div>

                <div class="info-grid" style="margin-top: var(--tf-sp-6);">
                    <div class="info-item">
                        <div class="info-label">Subtotal</div>
                        <div class="info-value" id="po-subtotal">$0.00</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Tax (8.25%)</div>
                        <div class="info-value" id="po-tax">$0.00</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Total</div>
                        <div class="info-value" id="po-total">$0.00</div>
                    </div>
                </div>

                <div class="btn-group">
                    <button class="btn btn-gold" onclick="generatePO()">
                        Generate Purchase Order
                    </button>
                    <button class="btn" onclick="printPO()">
                        🖨️ Print
                    </button>
                </div>
            </div>

            <div class="card">
                <div class="card-header">Previous Purchase Orders</div>
                <div id="po-history">
                    <p style="color: var(--tf-text-muted);">No POs yet.</p>
                </div>
            </div>
        </div>

        <!-- ================================================================
             TAB 5: REORDER ALERTS
             ================================================================ -->
        <div id="reorder-alerts" class="tab-content">
            <div class="card">
                <div class="card-header">Inventory Below Reorder Point</div>

                <div id="reorder-alerts-display">
                    <p style="color: var(--tf-text-muted);">Loading inventory data...</p>
                </div>

                <div class="btn-group">
                    <button class="btn btn-gold" onclick="refreshReorderAlerts()">
                        🔄 Refresh
                    </button>
                    <button class="btn btn-success" onclick="createPOFromAlerts()">
                        ✓ Create PO from Selected
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ================================================================
        // TAB MANAGEMENT
        // ================================================================

        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', function() {
                const tabName = this.getAttribute('data-tab');

                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });

                // Deactivate all buttons
                document.querySelectorAll('.tab-button').forEach(btn => {
                    btn.classList.remove('active');
                });

                // Show selected tab
                document.getElementById(tabName).classList.add('active');
                this.classList.add('active');
            });
        });

        // ================================================================
        // JOB CODE & API HELPERS
        // ================================================================

        const JOB_CODE = '{{JOB_CODE}}';

        function apiCall(endpoint, method = 'GET', data = null) {
            const opts = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            if (data) {
                opts.body = JSON.stringify(data);
            }

            return fetch(endpoint, opts)
                .then(r => {
                    if (!r.ok) throw new Error(`HTTP ${r.status}`);
                    return r.json();
                })
                .catch(err => {
                    console.error('API error:', err);
                    alert('Error: ' + err.message);
                    throw err;
                });
        }

        // ================================================================
        // PACKING LIST TAB
        // ================================================================

        function loadPackingItemsList() {
            apiCall(`/api/shipping/work-order/${JOB_CODE}`)
                .then(data => {
                    const items = data.items || [];
                    const completedItems = items.filter(i => i.status === 'complete');

                    const html = completedItems.map(item => `
                        <div class="checkbox-item">
                            <input type="checkbox" id="item-${item.item_id}" value="${item.item_id}">
                            <label for="item-${item.item_id}">
                                <strong>${item.ship_mark}</strong> — ${item.description}
                                <span style="color: var(--tf-text-muted); font-size: var(--tf-text-sm);">
                                    (Qty: ${item.quantity})
                                </span>
                            </label>
                        </div>
                    `).join('');

                    document.getElementById('packing-items-list').innerHTML = html ||
                        '<p style="color: var(--tf-text-muted);">No completed items.</p>';
                });
        }

        function generatePackingList() {
            const selectedItems = Array.from(document.querySelectorAll('#packing-items-list input:checked'))
                .map(cb => cb.value);

            if (selectedItems.length === 0) {
                alert('Please select at least one item.');
                return;
            }

            const shipDate = document.getElementById('pack-ship-date').value;
            const truckNumber = document.getElementById('pack-truck-number').value;
            const trailerNumber = document.getElementById('pack-trailer-number').value;
            const driverName = document.getElementById('pack-driver-name').value;

            const payload = {
                items_filter: selectedItems,
                ship_date: shipDate,
                truck_info: {
                    truck_number: truckNumber,
                    trailer_number: trailerNumber,
                    driver_name: driverName,
                },
            };

            apiCall(`/api/shipping/packing-list/${JOB_CODE}`, 'POST', payload)
                .then(packing_list => {
                    alert('Packing list generated: ' + packing_list.packing_list_id);
                    loadPackingListHistory();
                });
        }

        function loadPackingListHistory() {
            apiCall(`/api/shipping/packing-list/${JOB_CODE}`)
                .then(data => {
                    const docs = data.docs || [];
                    if (docs.length === 0) {
                        document.getElementById('packing-lists-history').innerHTML =
                            '<p style="color: var(--tf-text-muted);">No packing lists yet.</p>';
                        return;
                    }

                    const html = docs.map(doc => `
                        <div style="margin-bottom: var(--tf-sp-4); padding: var(--tf-sp-4); background-color: var(--tf-navy); border: 1px solid var(--tf-border); border-radius: var(--tf-radius);">
                            <p><strong>${doc.packing_list_id}</strong> — ${doc.ship_date}</p>
                            <p style="font-size: var(--tf-text-sm); color: var(--tf-text-muted);">
                                ${doc.totals.total_pieces} pieces, ${doc.totals.total_weight_lbs} lbs
                            </p>
                            <button class="btn btn-small" onclick="printDocumentPreview('${doc.packing_list_id}', 'packing_list')">
                                View & Print
                            </button>
                        </div>
                    `).join('');

                    document.getElementById('packing-lists-history').innerHTML = html;
                });
        }

        function printPackingList() {
            alert('Print functionality: packing list preview will open in print dialog.');
            window.print();
        }

        // ================================================================
        // BILL OF LADING TAB
        // ================================================================

        function generateBOL() {
            const carrierName = document.getElementById('bol-carrier-name').value;
            const driverName = document.getElementById('bol-driver-name').value;
            const truckNumber = document.getElementById('bol-truck-number').value;
            const trailerNumber = document.getElementById('bol-trailer-number').value;

            const consignee = {
                company: document.getElementById('bol-consignee-company').value,
                contact: document.getElementById('bol-consignee-contact').value,
                address: document.getElementById('bol-consignee-address').value,
                city: document.getElementById('bol-consignee-city').value,
                state: document.getElementById('bol-consignee-state').value,
                zip: document.getElementById('bol-consignee-zip').value,
                phone: document.getElementById('bol-consignee-phone').value,
            };

            const payload = {
                carrier_info: {
                    carrier_name: carrierName,
                    driver: driverName,
                    truck_number: truckNumber,
                    trailer_number: trailerNumber,
                },
                consignee: consignee,
            };

            apiCall(`/api/shipping/bill-of-lading/${JOB_CODE}`, 'POST', payload)
                .then(bol => {
                    alert('Bill of Lading generated: ' + bol.bol_number);
                    loadBOLHistory();
                });
        }

        function loadBOLHistory() {
            apiCall(`/api/shipping/bill-of-lading/${JOB_CODE}`)
                .then(data => {
                    const docs = data.docs || [];
                    if (docs.length === 0) {
                        document.getElementById('bol-history').innerHTML =
                            '<p style="color: var(--tf-text-muted);">No BOLs yet.</p>';
                        return;
                    }

                    const html = docs.map(doc => `
                        <div style="margin-bottom: var(--tf-sp-4); padding: var(--tf-sp-4); background-color: var(--tf-navy); border: 1px solid var(--tf-border); border-radius: var(--tf-radius);">
                            <p><strong>${doc.bol_number}</strong> — ${doc.bol_date}</p>
                            <p style="font-size: var(--tf-text-sm); color: var(--tf-text-muted);">
                                Carrier: ${doc.carrier.name} | Weight: ${doc.totals.total_weight_lbs} lbs
                            </p>
                            <button class="btn btn-small" onclick="printDocumentPreview('${doc.bol_number}', 'bill_of_lading')">
                                View & Print
                            </button>
                        </div>
                    `).join('');

                    document.getElementById('bol-history').innerHTML = html;
                });
        }

        function printBOL() {
            window.print();
        }

        // ================================================================
        // MANIFEST TAB
        // ================================================================

        function generateManifest() {
            apiCall(`/api/shipping/manifest/${JOB_CODE}`, 'POST', {})
                .then(manifest => {
                    displayManifest(manifest);
                });
        }

        function displayManifest(manifest) {
            const loads = manifest.loads || [];
            if (loads.length === 0) {
                document.getElementById('manifest-display').innerHTML =
                    '<p style="color: var(--tf-text-muted);">No loads yet.</p>';
                return;
            }

            const html = `
                <p style="margin-bottom: var(--tf-sp-6);">
                    <strong>Manifest ID:</strong> ${manifest.manifest_id}<br>
                    <strong>Date:</strong> ${manifest.manifest_date}<br>
                    <strong>Total Loads:</strong> ${manifest.totals.total_loads}
                    | <strong>Total Weight:</strong> ${manifest.totals.total_weight_lbs} lbs
                    | <strong>Total Pieces:</strong> ${manifest.totals.total_pieces}
                </p>

                ${loads.map((load, idx) => `
                    <div style="margin-bottom: var(--tf-sp-6); padding: var(--tf-sp-4); background-color: var(--tf-navy); border: 1px solid var(--tf-border); border-radius: var(--tf-radius);">
                        <h4 style="color: var(--tf-gold); margin-bottom: var(--tf-sp-3);">Load #${load.load_number}</h4>
                        <div class="info-grid">
                            <div class="info-item">
                                <div class="info-label">Truck</div>
                                <div class="info-value">${load.truck_number}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Trailer</div>
                                <div class="info-value">${load.trailer_number}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Weight</div>
                                <div class="info-value">${load.weight_lbs} lbs</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Pieces</div>
                                <div class="info-value">${load.piece_count}</div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            `;

            document.getElementById('manifest-display').innerHTML = html;
        }

        function printManifest() {
            window.print();
        }

        // ================================================================
        // PURCHASE ORDER TAB
        // ================================================================

        function addPOLineItem() {
            const container = document.getElementById('po-line-items-editor');
            const rowCount = container.querySelectorAll('.line-item-row').length;

            const row = document.createElement('div');
            row.className = 'line-item-row';
            row.innerHTML = `
                <input type="text" placeholder="Description" class="po-item-description">
                <input type="text" placeholder="Gauge" class="po-item-gauge" style="width: 80px;">
                <input type="text" placeholder="Width" class="po-item-width" style="width: 80px;">
                <input type="number" placeholder="Weight (lbs)" class="po-item-weight" step="0.01">
                <input type="number" placeholder="Unit Price" class="po-item-price" step="0.0001" class="po-item-price">
                <button class="btn btn-danger btn-small" onclick="this.parentElement.remove(); recalculatePO();">
                    Remove
                </button>
            `;

            container.appendChild(row);
        }

        function recalculatePO() {
            const rows = document.querySelectorAll('.line-item-row');
            let subtotal = 0;

            rows.forEach(row => {
                const weight = parseFloat(row.querySelector('.po-item-weight').value) || 0;
                const price = parseFloat(row.querySelector('.po-item-price').value) || 0;
                subtotal += weight * price;
            });

            const tax = subtotal * 0.0825;
            const total = subtotal + tax;

            document.getElementById('po-subtotal').textContent = '$' + subtotal.toFixed(2);
            document.getElementById('po-tax').textContent = '$' + tax.toFixed(2);
            document.getElementById('po-total').textContent = '$' + total.toFixed(2);
        }

        function generatePO() {
            const poNumber = document.getElementById('po-number').value || null;
            const vendor = {
                name: document.getElementById('po-vendor-name').value,
                contact: document.getElementById('po-vendor-contact').value,
                address: document.getElementById('po-vendor-address').value,
                city: document.getElementById('po-vendor-city').value,
                state: document.getElementById('po-vendor-state').value,
                zip: document.getElementById('po-vendor-zip').value,
                phone: document.getElementById('po-vendor-phone').value,
            };

            const deliveryDate = document.getElementById('po-delivery-date').value;
            const notes = document.getElementById('po-notes').value;

            const lineItems = Array.from(document.querySelectorAll('.line-item-row')).map(row => ({
                description: row.querySelector('.po-item-description').value,
                gauge: row.querySelector('.po-item-gauge').value,
                width: row.querySelector('.po-item-width').value,
                weight_lbs: parseFloat(row.querySelector('.po-item-weight').value) || 0,
                unit_price: parseFloat(row.querySelector('.po-item-price').value) || 0,
            }));

            if (lineItems.length === 0) {
                alert('Please add at least one line item.');
                return;
            }

            const payload = {
                po_number: poNumber,
                vendor: vendor,
                line_items: lineItems,
                delivery_date: deliveryDate,
                notes: notes,
            };

            apiCall(`/api/shipping/purchase-order/${JOB_CODE}`, 'POST', payload)
                .then(po => {
                    alert('Purchase Order generated: ' + po.po_number);
                    loadPOHistory();
                });
        }

        function loadPOHistory() {
            apiCall(`/api/shipping/purchase-order/${JOB_CODE}`)
                .then(data => {
                    const docs = data.docs || [];
                    if (docs.length === 0) {
                        document.getElementById('po-history').innerHTML =
                            '<p style="color: var(--tf-text-muted);">No POs yet.</p>';
                        return;
                    }

                    const html = docs.map(doc => `
                        <div style="margin-bottom: var(--tf-sp-4); padding: var(--tf-sp-4); background-color: var(--tf-navy); border: 1px solid var(--tf-border); border-radius: var(--tf-radius);">
                            <p><strong>${doc.po_number}</strong> — ${doc.po_date}</p>
                            <p style="font-size: var(--tf-text-sm); color: var(--tf-text-muted);">
                                Vendor: ${doc.vendor.name} | Total: $${doc.financial.total.toFixed(2)}
                            </p>
                            <button class="btn btn-small" onclick="printDocumentPreview('${doc.po_number}', 'purchase_order')">
                                View & Print
                            </button>
                        </div>
                    `).join('');

                    document.getElementById('po-history').innerHTML = html;
                });
        }

        function printPO() {
            window.print();
        }

        // ================================================================
        // REORDER ALERTS TAB
        // ================================================================

        function refreshReorderAlerts() {
            apiCall(`/api/shipping/reorder-alerts/${JOB_CODE}`)
                .then(data => {
                    displayReorderAlerts(data.alerts || []);
                });
        }

        function displayReorderAlerts(alerts) {
            const container = document.getElementById('reorder-alerts-display');

            if (alerts.length === 0) {
                container.innerHTML =
                    '<div class="alert alert-success">✓ All inventory levels are healthy!</div>';
                return;
            }

            const html = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th></th>
                            <th>Coil ID</th>
                            <th>Description</th>
                            <th class="numeric">Stock (lbs)</th>
                            <th class="numeric">Available (lbs)</th>
                            <th class="numeric">Reorder Point</th>
                            <th class="numeric">Suggested Order</th>
                            <th class="numeric">Est. Cost</th>
                            <th>Lead Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${alerts.map((alert, idx) => `
                            <tr>
                                <td>
                                    <input type="checkbox" class="reorder-item-checkbox" value="${alert.coil_id}">
                                </td>
                                <td><strong>${alert.coil_id}</strong></td>
                                <td>${alert.name}</td>
                                <td class="numeric">${alert.current_stock_lbs}</td>
                                <td class="numeric">${alert.available_lbs}</td>
                                <td class="numeric">${alert.reorder_point_lbs}</td>
                                <td class="numeric">${alert.suggested_order_qty}</td>
                                <td class="numeric">$${alert.estimated_cost.toFixed(2)}</td>
                                <td>${alert.lead_time_weeks}w</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;

            container.innerHTML = html;
        }

        function createPOFromAlerts() {
            const selectedCoils = Array.from(document.querySelectorAll('.reorder-item-checkbox:checked'))
                .map(cb => cb.value);

            if (selectedCoils.length === 0) {
                alert('Please select at least one coil.');
                return;
            }

            apiCall(`/api/shipping/po-from-reorder/${JOB_CODE}`, 'POST', {
                coil_ids: selectedCoils,
            })
                .then(po => {
                    alert('Purchase Order generated from reorder alerts: ' + po.po_number);
                    loadPOHistory();
                });
        }

        // ================================================================
        // INITIALIZATION
        // ================================================================

        document.addEventListener('DOMContentLoaded', function() {
            // Set today's date as default
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('pack-ship-date').value = today;
            document.getElementById('po-delivery-date').value = today;

            // Load initial data
            loadPackingItemsList();
            loadPackingListHistory();
            loadBOLHistory();
            loadPOHistory();
            refreshReorderAlerts();

            // Add change listeners to PO line items for auto-calculation
            document.addEventListener('change', function(e) {
                if (e.target.matches('.po-item-weight, .po-item-price')) {
                    recalculatePO();
                }
            });

            // Add initial line item row
            addPOLineItem();
        });

        // Helper: Print document preview
        function printDocumentPreview(docId, docType) {
            // In a real implementation, this would fetch the document and display it
            alert(`Print preview for ${docId} (${docType}) — opening print dialog...`);
            window.print();
        }
    </script>
</body>
</html>
"""
