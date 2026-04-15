from templates.shared_styles import DESIGN_SYSTEM_CSS

DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge — Mission Control</title>
    <style>
""" + DESIGN_SYSTEM_CSS + r"""

        /* ── Mission Control Styles ──────────────────── */
        .mc {
            max-width: 1400px;
            margin: 0 auto;
            padding: var(--tf-sp-6) var(--tf-sp-8);
        }

        /* Hero Welcome */
        .mc-hero {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: var(--tf-sp-6);
            flex-wrap: wrap;
            gap: var(--tf-sp-4);
        }

        .mc-hero-left h1 {
            font-size: var(--tf-text-2xl);
            font-weight: 700;
            color: var(--tf-gray-900);
            letter-spacing: -0.02em;
        }

        .mc-hero-left h1 span {
            background: linear-gradient(135deg, var(--tf-blue) 0%, #7C3AED 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .mc-hero-sub {
            color: var(--tf-gray-500);
            font-size: var(--tf-text-base);
            margin-top: 4px;
        }

        .mc-hero-right {
            display: flex;
            gap: var(--tf-sp-3);
        }

        /* Pulse Stats Row */
        .mc-pulse {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: var(--tf-sp-4);
            margin-bottom: var(--tf-sp-6);
        }

        .pulse-card {
            background: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg);
            padding: var(--tf-sp-5);
            display: flex;
            align-items: center;
            gap: var(--tf-sp-4);
            transition: all 200ms var(--tf-ease);
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }

        .pulse-card:hover {
            box-shadow: var(--tf-shadow-md);
            transform: translateY(-2px);
        }

        .pulse-card::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 3px;
        }

        .pulse-card.pc-blue::after   { background: var(--tf-blue); }
        .pulse-card.pc-amber::after  { background: var(--tf-amber); }
        .pulse-card.pc-green::after  { background: var(--tf-success); }
        .pulse-card.pc-purple::after { background: #7C3AED; }

        .pulse-icon {
            width: 48px;
            height: 48px;
            border-radius: var(--tf-radius-lg);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            flex-shrink: 0;
        }

        .pulse-icon.blue   { background: var(--tf-blue-light); }
        .pulse-icon.amber  { background: var(--tf-amber-light); }
        .pulse-icon.green  { background: var(--tf-success-bg); }
        .pulse-icon.purple { background: #EDE9FE; }

        .pulse-value {
            font-size: var(--tf-text-2xl);
            font-weight: 700;
            color: var(--tf-gray-900);
            line-height: 1.1;
        }

        .pulse-label {
            font-size: var(--tf-text-xs);
            font-weight: 600;
            color: var(--tf-gray-500);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-top: 2px;
        }

        /* Launchpad (Quick Actions) */
        .mc-launchpad {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--tf-sp-4);
            margin-bottom: var(--tf-sp-8);
        }

        .launch-card {
            background: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg);
            padding: var(--tf-sp-5) var(--tf-sp-4);
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: var(--tf-sp-3);
            cursor: pointer;
            transition: all 200ms var(--tf-ease);
            text-decoration: none;
            text-align: center;
        }

        .launch-card:hover {
            box-shadow: var(--tf-shadow-md);
            transform: translateY(-3px);
            border-color: var(--tf-blue);
        }

        .launch-icon {
            width: 52px;
            height: 52px;
            border-radius: var(--tf-radius-lg);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }

        .launch-icon.li-blue   { background: linear-gradient(135deg, #DBEAFE, #BFDBFE); }
        .launch-icon.li-amber  { background: linear-gradient(135deg, #FEF3C7, #FDE68A); }
        .launch-icon.li-green  { background: linear-gradient(135deg, #ECFDF5, #A7F3D0); }
        .launch-icon.li-purple { background: linear-gradient(135deg, #EDE9FE, #C4B5FD); }
        .launch-icon.li-navy   { background: linear-gradient(135deg, #1E293B, #334155); color: #fff; }

        .launch-title {
            font-size: var(--tf-text-sm);
            font-weight: 700;
            color: var(--tf-gray-900);
        }

        .launch-desc {
            font-size: var(--tf-text-xs);
            color: var(--tf-gray-500);
            line-height: 1.4;
        }

        /* Section Toggle */
        .mc-section-tabs {
            display: flex;
            gap: var(--tf-sp-1);
            border-bottom: 2px solid var(--tf-border);
            margin-bottom: var(--tf-sp-5);
        }

        .mc-tab {
            background: none;
            border: none;
            padding: var(--tf-sp-3) var(--tf-sp-5);
            font-size: var(--tf-text-sm);
            font-weight: 600;
            color: var(--tf-gray-500);
            cursor: pointer;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            transition: all var(--tf-duration) var(--tf-ease);
            display: flex;
            align-items: center;
            gap: var(--tf-sp-2);
        }

        .mc-tab:hover { color: var(--tf-gray-700); }
        .mc-tab.active { color: var(--tf-blue); border-bottom-color: var(--tf-blue); }

        .mc-tab-badge {
            background: var(--tf-danger);
            color: #fff;
            border-radius: 50%;
            font-size: 10px;
            font-weight: 700;
            width: 20px;
            height: 20px;
            display: none;
            align-items: center;
            justify-content: center;
        }

        .mc-tab-badge.show { display: inline-flex; }

        /* Pipeline Header */
        .mc-pipeline-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--tf-sp-4);
            flex-wrap: wrap;
            gap: var(--tf-sp-3);
        }

        .mc-pipeline-header h2 {
            font-size: var(--tf-text-lg);
            font-weight: 700;
            color: var(--tf-gray-900);
        }

        .mc-pipeline-controls {
            display: flex;
            align-items: center;
            gap: var(--tf-sp-3);
        }

        .view-pill {
            display: flex;
            background: var(--tf-gray-100);
            padding: 3px;
            border-radius: var(--tf-radius);
        }

        .pill-btn {
            background: transparent;
            border: none;
            padding: 7px 14px;
            border-radius: var(--tf-radius-sm);
            cursor: pointer;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            color: var(--tf-gray-500);
            transition: all var(--tf-duration) var(--tf-ease);
        }

        .pill-btn.active {
            background: var(--tf-surface);
            color: var(--tf-gray-900);
            box-shadow: var(--tf-shadow-sm);
        }

        .filter-toggle {
            display: flex;
            align-items: center;
            gap: var(--tf-sp-2);
            font-size: var(--tf-text-xs);
            color: var(--tf-gray-500);
            cursor: pointer;
            font-weight: 500;
        }

        .filter-toggle input[type="checkbox"] {
            width: 16px;
            height: 16px;
            accent-color: var(--tf-blue);
        }

        /* ── Pipeline Cards View ───────────────────── */
        .pipeline-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: var(--tf-sp-4);
            margin-bottom: var(--tf-sp-8);
        }

        .pipe-card {
            background: var(--tf-surface);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius-lg);
            padding: var(--tf-sp-5);
            cursor: pointer;
            transition: all 200ms var(--tf-ease);
            position: relative;
        }

        .pipe-card:hover {
            box-shadow: var(--tf-shadow-lg);
            transform: translateY(-2px);
            border-color: var(--tf-blue);
        }

        .pipe-card-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: var(--tf-sp-3);
        }

        .pipe-job {
            font-size: var(--tf-text-xs);
            font-weight: 700;
            color: var(--tf-blue);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .pipe-stage-badge {
            display: inline-flex;
            align-items: center;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .psb-quote, .psb-contract          { background: var(--tf-blue-light); color: var(--tf-blue); }
        .psb-engineering, .psb-shop-drawings { background: #EDE9FE; color: #6D28D9; }
        .psb-fabrication                     { background: var(--tf-amber-light); color: #92400E; }
        .psb-shipping, .psb-install          { background: var(--tf-success-bg); color: var(--tf-success); }
        .psb-complete                        { background: var(--tf-gray-100); color: var(--tf-gray-600); }

        .pipe-name {
            font-size: var(--tf-text-md);
            font-weight: 700;
            color: var(--tf-gray-900);
            margin-bottom: 2px;
            line-height: 1.3;
        }

        .pipe-customer {
            font-size: var(--tf-text-xs);
            color: var(--tf-gray-500);
            margin-bottom: var(--tf-sp-4);
        }

        /* Progress Pipeline (the fun part!) */
        .pipe-progress {
            display: flex;
            align-items: center;
            gap: 0;
            margin-bottom: var(--tf-sp-3);
            position: relative;
        }

        .pipe-step {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            z-index: 1;
        }

        .pipe-dot {
            width: 22px;
            height: 22px;
            border-radius: 50%;
            border: 2px solid var(--tf-gray-300);
            background: var(--tf-surface);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            transition: all 300ms var(--tf-ease);
            position: relative;
            z-index: 2;
        }

        .pipe-dot.done {
            background: var(--tf-success);
            border-color: var(--tf-success);
            color: #fff;
        }

        .pipe-dot.active {
            background: var(--tf-blue);
            border-color: var(--tf-blue);
            color: #fff;
            box-shadow: 0 0 0 4px rgba(30, 64, 175, 0.15);
            animation: dotPulse 2s ease-in-out infinite;
        }

        @keyframes dotPulse {
            0%, 100% { box-shadow: 0 0 0 4px rgba(30, 64, 175, 0.15); }
            50% { box-shadow: 0 0 0 8px rgba(30, 64, 175, 0.08); }
        }

        .pipe-dot.pending {
            background: var(--tf-surface);
            border-color: var(--tf-gray-300);
        }

        .pipe-step-label {
            font-size: 8px;
            font-weight: 600;
            color: var(--tf-gray-400);
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            text-align: center;
            white-space: nowrap;
        }

        .pipe-step-label.active-label { color: var(--tf-blue); font-weight: 700; }
        .pipe-step-label.done-label   { color: var(--tf-success); }

        /* Connector line between dots */
        .pipe-connector {
            height: 3px;
            flex: 1;
            background: var(--tf-gray-200);
            position: relative;
            top: -11px;
            z-index: 0;
            margin: 0 -4px;
        }

        .pipe-connector.done { background: var(--tf-success); }
        .pipe-connector.active { background: linear-gradient(90deg, var(--tf-success), var(--tf-blue)); }

        /* Progress bar (simplified visual) */
        .pipe-bar-track {
            width: 100%;
            height: 6px;
            background: var(--tf-gray-100);
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: var(--tf-sp-2);
        }

        .pipe-bar-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 600ms var(--tf-ease);
        }

        .pipe-bar-fill.early   { background: linear-gradient(90deg, var(--tf-blue), #60A5FA); }
        .pipe-bar-fill.mid     { background: linear-gradient(90deg, #7C3AED, #A78BFA); }
        .pipe-bar-fill.late    { background: linear-gradient(90deg, var(--tf-amber), #FBBF24); }
        .pipe-bar-fill.almost  { background: linear-gradient(90deg, var(--tf-success), #34D399); }
        .pipe-bar-fill.done    { background: var(--tf-gray-400); }

        .pipe-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: var(--tf-text-xs);
            color: var(--tf-gray-400);
        }

        .pipe-meta-docs {
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .pipe-pct {
            font-weight: 700;
            color: var(--tf-gray-600);
        }

        /* Completed overlay */
        .pipe-card.completed {
            opacity: 0.7;
        }

        .pipe-card.completed .pipe-name { text-decoration: line-through; }

        /* ── Kanban Board ──────────────────────────── */
        .kanban-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: var(--tf-sp-4);
            margin-bottom: var(--tf-sp-8);
        }

        .kanban-column {
            background: var(--tf-gray-50);
            border-radius: var(--tf-radius-lg);
            padding: var(--tf-sp-4);
            border: 1px solid var(--tf-border);
            min-height: 180px;
        }

        .column-header {
            font-size: var(--tf-text-xs);
            font-weight: 700;
            color: var(--tf-gray-600);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: var(--tf-sp-3);
            padding-bottom: var(--tf-sp-2);
            border-bottom: 2px solid var(--tf-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .col-count {
            background: var(--tf-gray-200);
            color: var(--tf-gray-600);
            padding: 2px 8px;
            border-radius: 999px;
            font-size: 10px;
        }

        .mini-card {
            background: var(--tf-surface);
            border-radius: var(--tf-radius);
            padding: var(--tf-sp-3);
            margin-bottom: var(--tf-sp-2);
            cursor: pointer;
            transition: all var(--tf-duration) var(--tf-ease);
            box-shadow: var(--tf-shadow-sm);
            border-left: 3px solid transparent;
        }

        .mini-card:hover {
            box-shadow: var(--tf-shadow-md);
            transform: translateX(2px);
        }

        .mini-card.mc-quote, .mini-card.mc-contract          { border-left-color: var(--tf-blue); }
        .mini-card.mc-engineering, .mini-card.mc-shop-drawings { border-left-color: #7C3AED; }
        .mini-card.mc-fabrication                              { border-left-color: var(--tf-amber); }
        .mini-card.mc-shipping, .mini-card.mc-install          { border-left-color: var(--tf-success); }
        .mini-card.mc-complete                                 { border-left-color: var(--tf-gray-400); }

        .mini-card-job {
            font-size: 10px;
            font-weight: 700;
            color: var(--tf-blue);
            text-transform: uppercase;
        }

        .mini-card-name {
            font-size: var(--tf-text-sm);
            font-weight: 600;
            color: var(--tf-gray-800);
            margin-top: 2px;
            line-height: 1.3;
        }

        .mini-card-customer {
            font-size: 10px;
            color: var(--tf-gray-400);
            margin-top: 2px;
        }

        /* ── Table View ────────────────────────────── */
        .table-container {
            background: var(--tf-surface);
            border-radius: var(--tf-radius-lg);
            border: 1px solid var(--tf-border);
            overflow: hidden;
        }

        .table {
            width: 100%;
            border-collapse: collapse;
        }

        .table thead th {
            background: var(--tf-navy);
            color: #fff;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding: var(--tf-sp-3) var(--tf-sp-4);
            text-align: left;
            cursor: pointer;
            user-select: none;
            white-space: nowrap;
            transition: background var(--tf-duration) var(--tf-ease);
        }

        .table thead th:hover { background: var(--tf-navy-light); }
        .table td {
            padding: var(--tf-sp-3) var(--tf-sp-4);
            border-bottom: 1px solid var(--tf-gray-100);
            font-size: var(--tf-text-sm);
        }
        .table tbody tr { cursor: pointer; transition: background var(--tf-duration) var(--tf-ease); }
        .table tbody tr:hover td { background: var(--tf-blue-light); }

        .stage-badge {
            display: inline-flex;
            align-items: center;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            white-space: nowrap;
        }

        .stage-quote, .stage-contract          { background: var(--tf-blue-light); color: var(--tf-blue); }
        .stage-engineering, .stage-shop-drawings { background: #EDE9FE; color: #6D28D9; }
        .stage-fabrication                       { background: var(--tf-amber-light); color: #92400E; }
        .stage-shipping, .stage-install          { background: var(--tf-success-bg); color: var(--tf-success); }
        .stage-complete                          { background: var(--tf-gray-100); color: var(--tf-gray-600); }

        .price.hidden { display: none; }

        /* ── Inventory Section ──────────────────────── */
        .inv-stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: var(--tf-sp-4);
            margin-bottom: var(--tf-sp-5);
        }

        /* ── Quick Peek Modal ──────────────────────── */
        .modal {
            display: none;
            position: fixed;
            inset: 0;
            z-index: 2000;
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(4px);
            animation: fadeIn 200ms var(--tf-ease);
        }

        .modal.show {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

        .modal-content {
            background: var(--tf-surface);
            border-radius: var(--tf-radius-xl);
            width: 92%;
            max-width: 860px;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: var(--tf-shadow-lg);
            animation: slideUp 250ms var(--tf-ease);
        }

        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to   { transform: translateY(0); opacity: 1; }
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: var(--tf-sp-6);
            border-bottom: 1px solid var(--tf-border);
        }

        .modal-title {
            font-size: var(--tf-text-lg);
            font-weight: 700;
            color: var(--tf-gray-900);
        }

        .modal-badge-group { display: flex; gap: var(--tf-sp-2); margin-top: var(--tf-sp-2); }

        .modal-badge {
            display: inline-flex;
            align-items: center;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            color: #fff;
        }

        .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--tf-gray-400);
            padding: var(--tf-sp-2);
            border-radius: var(--tf-radius-sm);
            transition: all var(--tf-duration) var(--tf-ease);
            line-height: 1;
        }
        .close-btn:hover { background: var(--tf-gray-100); color: var(--tf-gray-800); }

        .modal-body { padding: var(--tf-sp-6); }

        /* Info Grid (Overview) */
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: var(--tf-sp-4);
        }

        .info-item {
            background: var(--tf-gray-50);
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius);
            padding: var(--tf-sp-4);
        }

        .info-label {
            font-size: var(--tf-text-xs);
            font-weight: 600;
            color: var(--tf-gray-500);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: var(--tf-sp-1);
        }

        .info-value {
            font-size: var(--tf-text-md);
            font-weight: 600;
            color: var(--tf-gray-900);
        }

        /* Forms */
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--tf-sp-4);
        }

        .form-group { margin-bottom: var(--tf-sp-4); }

        .form-group label {
            display: block;
            font-size: var(--tf-text-xs);
            font-weight: 600;
            color: var(--tf-gray-600);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: var(--tf-sp-1);
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 10px 12px;
            font-family: var(--tf-font);
            font-size: var(--tf-text-base);
            color: var(--tf-gray-800);
            background: #fff;
            border: 1px solid var(--tf-border);
            border-radius: var(--tf-radius);
            outline: none;
            transition: all var(--tf-duration) var(--tf-ease);
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            border-color: var(--tf-blue-mid);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
        }

        .form-section-title {
            font-size: var(--tf-text-sm);
            font-weight: 700;
            color: var(--tf-gray-700);
            margin-top: var(--tf-sp-4);
            margin-bottom: var(--tf-sp-3);
            padding-bottom: var(--tf-sp-2);
            border-bottom: 1px solid var(--tf-border);
        }

        .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: var(--tf-sp-3);
            margin-top: var(--tf-sp-6);
            padding-top: var(--tf-sp-4);
            border-top: 1px solid var(--tf-border);
        }

        /* Empty state */
        .empty-state {
            text-align: center;
            padding: var(--tf-sp-12) var(--tf-sp-4);
            color: var(--tf-gray-500);
        }
        .empty-state-icon { font-size: 2.5rem; margin-bottom: var(--tf-sp-3); opacity: 0.5; }
        .empty-state-title { font-size: var(--tf-text-md); font-weight: 700; color: var(--tf-gray-700); margin-bottom: var(--tf-sp-2); }

        /* Celebration confetti */
        @keyframes confettiDrop {
            0%   { transform: translateY(-20px) rotate(0deg); opacity: 1; }
            100% { transform: translateY(40px) rotate(360deg); opacity: 0; }
        }

        .confetti-burst {
            position: absolute;
            top: 0;
            left: 50%;
            pointer-events: none;
            z-index: 10;
        }

        .confetti-bit {
            position: absolute;
            width: 6px;
            height: 6px;
            border-radius: 2px;
            animation: confettiDrop 1.2s ease-out forwards;
        }

        /* ── Responsive ────────────────────────────── */
        @media (max-width: 1280px) {
            .mc-pulse { grid-template-columns: repeat(2, 1fr); }
        }

        @media (max-width: 1024px) {
            .mc { padding: var(--tf-sp-4); }
            .pipeline-grid { grid-template-columns: 1fr; }
            .kanban-container { grid-template-columns: repeat(2, 1fr); }
            .modal-content { width: 95%; max-height: 90vh; }
            .inv-stats { grid-template-columns: repeat(2, 1fr); }
        }

        @media (max-width: 768px) {
            .mc-pulse { grid-template-columns: 1fr; }
            .mc-launchpad { grid-template-columns: repeat(2, 1fr); }
            .kanban-container { grid-template-columns: 1fr; }
            .mc-hero { flex-direction: column; align-items: flex-start; }
            .form-row { grid-template-columns: 1fr; }
            .inv-stats { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <script>
        var USER_ROLE = '{{USER_ROLE}}';
        var USER_NAME = '{{USER_NAME}}';
    </script>

    <!-- OLD TOPBAR (hidden by inject_nav CSS but kept for fallback) -->
    <div class="tf-topbar">
        <a href="/" class="tf-logo">
            <div class="tf-logo-icon">&#9878;</div>
            TITANFORGE
        </a>
        <nav>
            <a href="/" class="active">Dashboard</a>
            <a href="/sa">SA Estimator</a>
            <a href="/tc">TC Estimator</a>
            <a href="/customers">Customers</a>
            <a href="/shop-floor">Shop Floor</a>
        </nav>
        <div class="tf-user">
            <span id="userNameOld">User</span>
            <button class="logout-btn" onclick="handleLogout()">Logout</button>
        </div>
    </div>

    <!-- ═══════════════════════════════════════════════ -->
    <!-- MAIN CONTENT                                    -->
    <!-- ═══════════════════════════════════════════════ -->
    <div class="mc">

        <!-- HERO -->
        <div class="mc-hero">
            <div class="mc-hero-left">
                <h1>Welcome back, <span id="heroName">there</span></h1>
                <p class="mc-hero-sub" id="heroDate">Steel Fabrication Mission Control</p>
            </div>
            <div class="mc-hero-right">
                <button class="tf-btn tf-btn-primary" onclick="openNewProjectForm()" id="newProjectBtn">+ New Project</button>
            </div>
        </div>

        <!-- PULSE STATS -->
        <div class="mc-pulse">
            <div class="pulse-card pc-blue" onclick="scrollToProjects('all')">
                <div class="pulse-icon blue">&#128202;</div>
                <div>
                    <div class="pulse-value" id="activeProjects">&mdash;</div>
                    <div class="pulse-label">Active Projects</div>
                </div>
            </div>
            <div class="pulse-card pc-purple" onclick="scrollToProjects('engineering')">
                <div class="pulse-icon purple">&#128208;</div>
                <div>
                    <div class="pulse-value" id="inEngineering">&mdash;</div>
                    <div class="pulse-label">In Engineering</div>
                </div>
            </div>
            <div class="pulse-card pc-amber" onclick="scrollToProjects('fabrication')">
                <div class="pulse-icon amber">&#128295;</div>
                <div>
                    <div class="pulse-value" id="inFabrication">&mdash;</div>
                    <div class="pulse-label">In Fabrication</div>
                </div>
            </div>
            <div class="pulse-card pc-green" onclick="scrollToProjects('shipping')">
                <div class="pulse-icon green">&#128230;</div>
                <div>
                    <div class="pulse-value" id="readyToShip">&mdash;</div>
                    <div class="pulse-label">Ready to Ship</div>
                </div>
            </div>
        </div>

        <!-- LAUNCHPAD -->
        <div class="mc-launchpad">
            <a class="launch-card" href="/sa">
                <div class="launch-icon li-blue">&#128208;</div>
                <div class="launch-title">SA Estimator</div>
                <div class="launch-desc">Structures America pricing</div>
            </a>
            <a class="launch-card" href="/tc">
                <div class="launch-icon li-amber">&#128221;</div>
                <div class="launch-title">TC Estimator</div>
                <div class="launch-desc">Titan Carports pricing</div>
            </a>
            <a class="launch-card" href="/shop-floor">
                <div class="launch-icon li-navy">&#127981;</div>
                <div class="launch-title">Shop Floor</div>
                <div class="launch-desc">Production dashboard</div>
            </a>
            <a class="launch-card" href="/customers">
                <div class="launch-icon li-green">&#128100;</div>
                <div class="launch-title">Customers</div>
                <div class="launch-desc">CRM & contacts</div>
            </a>
        </div>

        <!-- SECTION TABS -->
        <div class="mc-section-tabs">
            <button class="mc-tab active" id="tabProjects" onclick="switchSection('projects')">
                &#128204; Projects
            </button>
            <button class="mc-tab" id="tabInventory" onclick="switchSection('inventory')">
                &#128230; Inventory
                <span class="mc-tab-badge" id="invAlertDot">0</span>
            </button>
        </div>

        <!-- ═══════════════════════════════════════════════ -->
        <!-- PROJECTS SECTION                                -->
        <!-- ═══════════════════════════════════════════════ -->
        <div id="sectionProjects">
            <div class="mc-pipeline-header">
                <h2>Project Pipeline</h2>
                <div class="mc-pipeline-controls">
                    <label class="filter-toggle">
                        <input type="checkbox" id="showCompletedToggle" onchange="toggleCompleted()">
                        Show completed
                    </label>
                    <div class="view-pill">
                        <button class="pill-btn active" id="pipelineToggle" onclick="switchView('pipeline')">Pipeline</button>
                        <button class="pill-btn" id="kanbanToggle" onclick="switchView('kanban')">Board</button>
                        <button class="pill-btn" id="tableToggle" onclick="switchView('table')">Table</button>
                    </div>
                </div>
            </div>

            <!-- PIPELINE CARDS VIEW (new default) -->
            <div id="pipelineView" class="pipeline-grid"></div>

            <!-- KANBAN VIEW -->
            <div id="kanbanView" class="kanban-container" style="display:none;"></div>

            <!-- TABLE VIEW -->
            <div id="tableView" class="table-container" style="display:none;">
                <table class="table">
                    <thead>
                        <tr>
                            <th onclick="sortTable('jobCode')">Job Code</th>
                            <th onclick="sortTable('name')">Project</th>
                            <th onclick="sortTable('customer')">Customer</th>
                            <th onclick="sortTable('stage')">Stage</th>
                            <th class="price" onclick="sortTable('docs')">Docs</th>
                            <th onclick="sortTable('updated')">Updated</th>
                            <th>Progress</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>
        </div>

        <!-- ═══════════════════════════════════════════════ -->
        <!-- INVENTORY SECTION                               -->
        <!-- ═══════════════════════════════════════════════ -->
        <div id="sectionInventory" style="display:none;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--tf-sp-5);flex-wrap:wrap;gap:var(--tf-sp-3);">
                <h2 style="font-size:var(--tf-text-lg);font-weight:700;color:var(--tf-gray-900);">Steel Coil Inventory</h2>
                <div style="display:flex;gap:var(--tf-sp-2);">
                    <button class="tf-btn tf-btn-primary tf-btn-sm" onclick="openAddCoilModal()">+ Add Coil</button>
                    <button class="tf-btn tf-btn-outline tf-btn-sm" onclick="openAddCertModal()">Upload Mill Cert</button>
                </div>
            </div>

            <div class="inv-stats">
                <div class="pulse-card pc-blue">
                    <div class="pulse-icon blue">&#128230;</div>
                    <div>
                        <div class="pulse-value" id="invTotalCoils">&mdash;</div>
                        <div class="pulse-label">Total Coils</div>
                    </div>
                </div>
                <div class="pulse-card pc-green">
                    <div class="pulse-icon green">&#9989;</div>
                    <div>
                        <div class="pulse-value" id="invInStock">&mdash;</div>
                        <div class="pulse-label">In Stock</div>
                    </div>
                </div>
                <div class="pulse-card pc-amber">
                    <div class="pulse-icon amber">&#9888;</div>
                    <div>
                        <div class="pulse-value" id="invLowStock">&mdash;</div>
                        <div class="pulse-label">Low Stock</div>
                    </div>
                </div>
                <div class="pulse-card" style="border-color:var(--tf-danger-bg);">
                    <div class="pulse-icon" style="background:var(--tf-danger-bg);">&#10060;</div>
                    <div>
                        <div class="pulse-value" id="invOutStock">&mdash;</div>
                        <div class="pulse-label">Out of Stock</div>
                    </div>
                </div>
            </div>

            <div class="table-container">
                <table class="table" id="invTable">
                    <thead>
                        <tr>
                            <th>Coil ID</th>
                            <th>Description</th>
                            <th>Gauge</th>
                            <th>Width</th>
                            <th>Color</th>
                            <th>Stock (lbs)</th>
                            <th>Min Stock</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="invTableBody"></tbody>
                </table>
            </div>
        </div>

    </div> <!-- end .mc -->

    <!-- ADD COIL MODAL -->
    <div class="modal" id="addCoilModal">
        <div class="modal-content" style="max-width:600px;">
            <div class="modal-header">
                <h2 class="modal-title">Add New Coil</h2>
                <button class="close-btn" onclick="closeAddCoilModal()">&times;</button>
            </div>
            <div class="modal-body">
                <form onsubmit="return submitNewCoil(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Coil ID *</label>
                            <input type="text" id="newCoilId" placeholder="e.g. c_section_29" required>
                        </div>
                        <div class="form-group">
                            <label>Description *</label>
                            <input type="text" id="newCoilDesc" placeholder="e.g. 29ga White" required>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Gauge</label>
                            <input type="text" id="newCoilGauge" placeholder="e.g. 29">
                        </div>
                        <div class="form-group">
                            <label>Width</label>
                            <input type="text" id="newCoilWidth" placeholder="e.g. 36 in">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Color</label>
                            <input type="text" id="newCoilColor" placeholder="e.g. White">
                        </div>
                        <div class="form-group">
                            <label>Stock (lbs) *</label>
                            <input type="number" id="newCoilStock" placeholder="0" required min="0">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Min Stock (lbs)</label>
                            <input type="number" id="newCoilMinStock" placeholder="2000" min="0">
                        </div>
                        <div class="form-group">
                            <label>Cost per lb ($)</label>
                            <input type="number" id="newCoilCostLb" placeholder="0.50" step="0.01" min="0">
                        </div>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="tf-btn tf-btn-outline" onclick="closeAddCoilModal()">Cancel</button>
                        <button type="submit" class="tf-btn tf-btn-primary">Add Coil</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- ADD CERT MODAL -->
    <div class="modal" id="addCertModal">
        <div class="modal-content" style="max-width:500px;">
            <div class="modal-header">
                <h2 class="modal-title">Upload Mill Certificate</h2>
                <button class="close-btn" onclick="closeAddCertModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label>Select Coil</label>
                    <select id="certCoilSelect" class="tf-select"></select>
                </div>
                <div class="form-group">
                    <label>Heat Number</label>
                    <input type="text" id="certHeatNum" placeholder="e.g. H-2026-001" class="tf-input">
                </div>
                <div class="form-group">
                    <label>Certificate File (PDF/Image)</label>
                    <input type="file" id="certFile" accept=".pdf,.jpg,.png,.gif" style="width:100%;padding:10px;font-size:var(--tf-text-sm);">
                </div>
                <div class="form-actions">
                    <button type="button" class="tf-btn tf-btn-outline" onclick="closeAddCertModal()">Cancel</button>
                    <button type="button" class="tf-btn tf-btn-primary" onclick="submitCert()">Upload Certificate</button>
                </div>
            </div>
        </div>
    </div>

    <!-- EDIT STOCK MODAL -->
    <div class="modal" id="editStockModal">
        <div class="modal-content" style="max-width:400px;">
            <div class="modal-header">
                <h2 class="modal-title">Update Stock</h2>
                <button class="close-btn" onclick="closeEditStockModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label>Coil</label>
                    <input type="text" id="editStockCoilName" readonly style="background:var(--tf-gray-50);font-weight:600;" class="tf-input">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Current Stock (lbs)</label>
                        <input type="number" id="editStockCurrent" readonly style="background:var(--tf-gray-50);" class="tf-input">
                    </div>
                    <div class="form-group">
                        <label>New Stock (lbs)</label>
                        <input type="number" id="editStockNew" min="0" required class="tf-input">
                    </div>
                </div>
                <div class="form-group">
                    <label>Min Stock (lbs)</label>
                    <input type="number" id="editStockMin" min="0" class="tf-input">
                </div>
                <input type="hidden" id="editStockCoilId">
                <div class="form-actions">
                    <button type="button" class="tf-btn tf-btn-outline" onclick="closeEditStockModal()">Cancel</button>
                    <button type="button" class="tf-btn tf-btn-primary" onclick="submitStockUpdate()">Update</button>
                </div>
            </div>
        </div>
    </div>

    <!-- NEW PROJECT MODAL -->
    <div class="modal" id="newProjectModal">
        <div class="modal-content">
            <div class="modal-header">
                <div>
                    <h2 class="modal-title">New Project</h2>
                    <div class="modal-badge-group">
                        <span class="modal-badge" style="background: var(--tf-blue);" id="newJobCodeBadge">Loading...</span>
                    </div>
                </div>
                <button class="close-btn" onclick="closeNewProjectModal()">&times;</button>
            </div>
            <div class="modal-body">
                <form id="newProjectForm" onsubmit="return submitNewProject(event)">
                    <div class="form-group">
                        <label>Job Code (auto-generated)</label>
                        <input type="text" id="npJobCode" readonly style="background: var(--tf-gray-50); font-weight: 700; color: var(--tf-blue);">
                    </div>
                    <div class="form-group">
                        <label>Project Name *</label>
                        <input type="text" id="npProjectName" placeholder="e.g. Smith Residence Carport" required>
                    </div>

                    <div class="form-section-title">Customer Information</div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Customer Name</label>
                            <input type="text" id="npCustomerName" placeholder="Full name">
                        </div>
                        <div class="form-group">
                            <label>Phone</label>
                            <input type="tel" id="npCustomerPhone" placeholder="(555) 555-5555">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="npCustomerEmail" placeholder="customer@email.com">
                    </div>

                    <div class="form-section-title">Project Location</div>
                    <div class="form-group">
                        <label>Street Address</label>
                        <input type="text" id="npStreet" placeholder="123 Main St">
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>City</label>
                            <input type="text" id="npCity" placeholder="City">
                        </div>
                        <div class="form-group" style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--tf-sp-2);">
                            <div>
                                <label>State</label>
                                <input type="text" id="npState" placeholder="TX" maxlength="2" style="text-transform: uppercase;">
                            </div>
                            <div>
                                <label>Zip</label>
                                <input type="text" id="npZip" placeholder="75001" maxlength="10">
                            </div>
                        </div>
                    </div>

                    <div class="form-section-title">Project Details</div>
                    <div class="form-group">
                        <label>Starting Stage</label>
                        <select id="npStage">
                            <option value="quote" selected>Quote</option>
                            <option value="contract">Contract</option>
                            <option value="engineering">Engineering</option>
                            <option value="shop_drawings">Shop Drawings</option>
                            <option value="fabrication">Fabrication</option>
                            <option value="shipping">Shipping</option>
                            <option value="install">Install</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Notes</label>
                        <textarea id="npNotes" rows="3" placeholder="Any initial notes about this project..."></textarea>
                    </div>

                    <div class="form-actions">
                        <button type="button" class="tf-btn tf-btn-outline" onclick="closeNewProjectModal()">Cancel</button>
                        <button type="submit" class="tf-btn tf-btn-primary" id="npSubmitBtn">Create Project</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- QUICK PEEK MODAL -->
    <div class="modal" id="projectModal">
        <div class="modal-content">
            <div class="modal-header">
                <div>
                    <h2 class="modal-title" id="modalTitle">Project Details</h2>
                    <div class="modal-badge-group" id="modalBadgeGroup"></div>
                </div>
                <button class="close-btn" onclick="closeProjectModal()">&times;</button>
            </div>
            <div class="modal-body">
                <!-- Pipeline progress in modal -->
                <div id="modalPipeline" style="margin-bottom:var(--tf-sp-5);"></div>
                <div class="info-grid" id="overviewInfo"></div>
                <div style="margin-top: var(--tf-sp-5); display: flex; gap: var(--tf-sp-2); flex-wrap: wrap;">
                    <button class="tf-btn tf-btn-primary" id="openFullPageBtn" onclick="">Open Project</button>
                    <button class="tf-btn tf-btn-outline" id="openShopDrawingsBtn" style="border-color:#1E40AF;color:#1E40AF;">Shop Drawings</button>
                    <button class="tf-btn tf-btn-outline" id="openWorkOrdersBtn" style="border-color:#0F766E;color:#0F766E;">Work Orders</button>
                    <button class="tf-btn tf-btn-outline" onclick="closeProjectModal()">Close</button>
                </div>
            </div>
        </div>
    </div>

    <script>
    // ══════════════════════════════════════════════
    // GLOBAL STATE
    // ══════════════════════════════════════════════
    var allProjects = [];
    var filteredProjects = [];
    var currentView = 'pipeline';
    var currentProject = null;
    var currentSortColumn = null;
    var currentSortDirection = 'asc';
    var inventoryAlerts = [];
    var showCompleted = false;

    var STAGES = ['quote', 'contract', 'engineering', 'shop-drawings', 'fabrication', 'shipping', 'install'];
    var STAGE_LABELS = { 'quote': 'Quote', 'contract': 'Contract', 'engineering': 'Eng', 'shop-drawings': 'Shop Drw', 'fabrication': 'Fab', 'shipping': 'Ship', 'install': 'Install', 'complete': 'Done' };

    document.addEventListener('DOMContentLoaded', function() { initializePage(); });

    function initializePage() {
        // Set hero name
        var displayName = (USER_NAME && USER_NAME !== '{{USER_NAME}}') ? USER_NAME : 'there';
        document.getElementById('heroName').textContent = displayName;

        // Date subtitle
        var now = new Date();
        var opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        document.getElementById('heroDate').textContent = now.toLocaleDateString('en-US', opts);

        // Role-based visibility
        if (USER_ROLE !== 'admin' && USER_ROLE !== 'estimator') {
            document.getElementById('newProjectBtn').style.display = 'none';
        }

        loadProjects();
        loadInventoryAlerts();
        setupEventListeners();

        if (USER_ROLE === 'shop') {
            document.querySelectorAll('.price').forEach(function(el) { el.classList.add('hidden'); });
        }
    }

    function setupEventListeners() {
        // Close modals on backdrop click
        ['projectModal', 'newProjectModal', 'addCoilModal', 'addCertModal', 'editStockModal'].forEach(function(id) {
            document.getElementById(id).addEventListener('click', function(e) {
                if (e.target === this) this.classList.remove('show');
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal.show').forEach(function(m) { m.classList.remove('show'); });
            }
        });
    }

    // ── Load Projects ─────────────────────────────
    function loadProjects() {
        fetch('/api/projects/full')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                allProjects = (data.projects || []).map(normalizeProject);
                applyFilters();
            })
            .catch(function(err) {
                fetch('/api/projects')
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        allProjects = (data.projects || []).map(normalizeProject);
                        applyFilters();
                    })
                    .catch(function() { allProjects = []; applyFilters(); });
            });
    }

    function normalizeProject(p) {
        return {
            job_code: p.job_code || p.jobCode || '',
            project_name: p.project_name || p.name || '',
            customer_name: (p.customer && p.customer.name) ? p.customer.name : (p.customer || ''),
            customer: p.customer || {},
            location: p.location || {},
            stage: (p.stage || 'quote').replace(/_/g, '-'),
            created_at: p.created_at || p.saved_at || '',
            updated_at: p.updated_at || p.saved_at || '',
            archived: p.archived || false,
            n_versions: p.n_versions || 0,
            doc_count: p.doc_count || 0,
            notes: p.notes || '',
        };
    }

    function applyFilters() {
        filteredProjects = allProjects.filter(function(p) {
            if (!showCompleted && p.stage === 'complete') return false;
            if (p.archived) return false;
            return true;
        });
        updateStats();
        renderProjects();
    }

    function toggleCompleted() {
        showCompleted = document.getElementById('showCompletedToggle').checked;
        applyFilters();
    }

    // ── Stats ─────────────────────────────────────
    function updateStats() {
        var active = allProjects.filter(function(p) { return p.stage !== 'complete' && !p.archived; });
        document.getElementById('activeProjects').textContent = active.length;
        document.getElementById('inEngineering').textContent = active.filter(function(p) { return p.stage === 'engineering' || p.stage === 'shop-drawings'; }).length;
        document.getElementById('inFabrication').textContent = active.filter(function(p) { return p.stage === 'fabrication'; }).length;
        document.getElementById('readyToShip').textContent = active.filter(function(p) { return p.stage === 'shipping' || p.stage === 'install'; }).length;
    }

    // ── Stage Progress Helpers ────────────────────
    function getStageIndex(stage) {
        var idx = STAGES.indexOf(stage);
        if (stage === 'complete') return STAGES.length;
        return idx >= 0 ? idx : 0;
    }

    function getStagePercent(stage) {
        if (stage === 'complete') return 100;
        var idx = getStageIndex(stage);
        return Math.round((idx / STAGES.length) * 100);
    }

    function getBarClass(pct) {
        if (pct >= 100) return 'done';
        if (pct >= 70) return 'almost';
        if (pct >= 40) return 'mid';
        if (pct >= 20) return 'late';
        return 'early';
    }

    function buildPipelineDots(stage, compact) {
        var currentIdx = getStageIndex(stage);
        var isComplete = stage === 'complete';
        var html = '<div style="display:flex;align-items:center;gap:0;">';

        STAGES.forEach(function(s, i) {
            var dotClass = 'pipe-dot ';
            var labelClass = 'pipe-step-label ';

            if (isComplete || i < currentIdx) {
                dotClass += 'done';
                labelClass += 'done-label';
            } else if (i === currentIdx) {
                dotClass += 'active';
                labelClass += 'active-label';
            } else {
                dotClass += 'pending';
            }

            html += '<div class="pipe-step">';
            html += '<div class="' + dotClass + '">';
            if (isComplete || i < currentIdx) {
                html += '&#10003;';
            } else if (i === currentIdx) {
                html += '&#9679;';
            }
            html += '</div>';
            if (!compact) {
                html += '<div class="' + labelClass + '">' + STAGE_LABELS[s] + '</div>';
            }
            html += '</div>';

            // Connector between dots
            if (i < STAGES.length - 1) {
                var connClass = 'pipe-connector ';
                if (isComplete || i < currentIdx - 1) connClass += 'done';
                else if (i === currentIdx - 1) connClass += 'active';
                html += '<div class="' + connClass + '"></div>';
            }
        });

        html += '</div>';
        return html;
    }

    // ── Render Dispatch ───────────────────────────
    function renderProjects() {
        if (currentView === 'pipeline') renderPipeline();
        else if (currentView === 'kanban') renderKanban();
        else renderTable();
    }

    // ── Pipeline Cards View ───────────────────────
    function renderPipeline() {
        var container = document.getElementById('pipelineView');
        container.innerHTML = '';

        if (filteredProjects.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">&#128640;</div><div class="empty-state-title">No projects yet</div><p>Create your first project to get started!</p></div>';
            return;
        }

        // Sort: active first (by stage progress descending), then completed
        var sorted = filteredProjects.slice().sort(function(a, b) {
            var aComp = a.stage === 'complete' ? 1 : 0;
            var bComp = b.stage === 'complete' ? 1 : 0;
            if (aComp !== bComp) return aComp - bComp;
            return getStageIndex(b.stage) - getStageIndex(a.stage);
        });

        sorted.forEach(function(project) {
            var pct = getStagePercent(project.stage);
            var isComplete = project.stage === 'complete';
            var stageLabel = (STAGE_LABELS[project.stage] || project.stage).toUpperCase();

            var card = document.createElement('div');
            card.className = 'pipe-card' + (isComplete ? ' completed' : '');
            card.onclick = function() { openProjectModal(project); };

            card.innerHTML = ''
                + '<div class="pipe-card-top">'
                +   '<div class="pipe-job">' + esc(project.job_code) + '</div>'
                +   '<span class="pipe-stage-badge psb-' + project.stage + '">' + stageLabel + '</span>'
                + '</div>'
                + '<div class="pipe-name">' + esc(project.project_name || 'Untitled') + '</div>'
                + '<div class="pipe-customer">' + esc(project.customer_name || 'No customer') + '</div>'
                + buildPipelineDots(project.stage, false)
                + '<div class="pipe-bar-track"><div class="pipe-bar-fill ' + getBarClass(pct) + '" style="width:' + pct + '%;"></div></div>'
                + '<div class="pipe-meta">'
                +   '<div class="pipe-meta-docs">&#128196; ' + (project.doc_count || 0) + ' docs &middot; v' + (project.n_versions || 1) + '</div>'
                +   '<div class="pipe-pct">' + pct + '%</div>'
                + '</div>';

            container.appendChild(card);
        });
    }

    // ── Kanban View ───────────────────────────────
    function renderKanban() {
        var stages = STAGES.slice();
        if (showCompleted) stages.push('complete');

        var kanbanContainer = document.getElementById('kanbanView');
        kanbanContainer.innerHTML = '';

        stages.forEach(function(stage) {
            var projects = filteredProjects.filter(function(p) { return p.stage === stage; });
            var label = STAGE_LABELS[stage] || stage;

            var column = document.createElement('div');
            column.className = 'kanban-column';
            column.innerHTML = '<div class="column-header"><span>' + label + '</span><span class="col-count">' + projects.length + '</span></div>';

            projects.forEach(function(project) {
                var card = document.createElement('div');
                card.className = 'mini-card mc-' + project.stage;
                card.onclick = function() { openProjectModal(project); };
                card.innerHTML = '<div class="mini-card-job">' + esc(project.job_code) + '</div>'
                    + '<div class="mini-card-name">' + esc(project.project_name || 'Untitled') + '</div>'
                    + '<div class="mini-card-customer">' + esc(project.customer_name || '') + '</div>';
                column.appendChild(card);
            });

            kanbanContainer.appendChild(column);
        });
    }

    // ── Table View ────────────────────────────────
    function renderTable() {
        var tableBody = document.getElementById('tableBody');
        tableBody.innerHTML = '';

        filteredProjects.forEach(function(project) {
            var row = document.createElement('tr');
            row.onclick = function() { openProjectModal(project); };

            var stageLabel = STAGE_LABELS[project.stage] || project.stage;
            var pct = getStagePercent(project.stage);
            var updated = project.updated_at ? new Date(project.updated_at).toLocaleDateString() : '';

            row.innerHTML = '<td><strong>' + esc(project.job_code) + '</strong></td>'
                + '<td>' + esc(project.project_name) + '</td>'
                + '<td>' + esc(project.customer_name) + '</td>'
                + '<td><span class="stage-badge stage-' + project.stage + '">' + stageLabel + '</span></td>'
                + '<td class="price">' + (project.doc_count || 0) + ' docs</td>'
                + '<td>' + updated + '</td>'
                + '<td><div style="display:flex;align-items:center;gap:8px;"><div style="flex:1;height:6px;background:var(--tf-gray-100);border-radius:3px;overflow:hidden;"><div style="height:100%;width:' + pct + '%;background:var(--tf-blue);border-radius:3px;"></div></div><span style="font-size:11px;font-weight:700;color:var(--tf-gray-600);">' + pct + '%</span></div></td>';

            tableBody.appendChild(row);
        });
    }

    // ── View Switching ────────────────────────────
    function switchView(view) {
        currentView = view;
        document.getElementById('pipelineToggle').classList.toggle('active', view === 'pipeline');
        document.getElementById('kanbanToggle').classList.toggle('active', view === 'kanban');
        document.getElementById('tableToggle').classList.toggle('active', view === 'table');
        document.getElementById('pipelineView').style.display = view === 'pipeline' ? 'grid' : 'none';
        document.getElementById('kanbanView').style.display = view === 'kanban' ? 'grid' : 'none';
        document.getElementById('tableView').style.display = view === 'table' ? 'block' : 'none';
        renderProjects();
    }

    function sortTable(column) {
        if (currentSortColumn === column) {
            currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            currentSortDirection = 'asc';
            currentSortColumn = column;
        }
        filteredProjects.sort(function(a, b) {
            var aVal, bVal;
            if (column === 'jobCode') { aVal = a.job_code; bVal = b.job_code; }
            else if (column === 'name') { aVal = a.project_name; bVal = b.project_name; }
            else if (column === 'customer') { aVal = a.customer_name; bVal = b.customer_name; }
            else if (column === 'stage') { aVal = getStageIndex(a.stage); bVal = getStageIndex(b.stage); }
            else if (column === 'updated') { aVal = a.updated_at; bVal = b.updated_at; }
            else { aVal = a[column]; bVal = b[column]; }
            if (typeof aVal === 'string') { aVal = (aVal || '').toLowerCase(); bVal = (bVal || '').toLowerCase(); }
            var cmp = aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
            return currentSortDirection === 'asc' ? cmp : -cmp;
        });
        renderTable();
    }

    function scrollToProjects(filter) {
        document.getElementById('sectionProjects').scrollIntoView({ behavior: 'smooth' });
    }

    // ── Section Switching ─────────────────────────
    var currentSection = 'projects';

    function switchSection(section) {
        currentSection = section;
        document.getElementById('sectionProjects').style.display = section === 'projects' ? '' : 'none';
        document.getElementById('sectionInventory').style.display = section === 'inventory' ? '' : 'none';
        document.getElementById('tabProjects').classList.toggle('active', section === 'projects');
        document.getElementById('tabInventory').classList.toggle('active', section === 'inventory');
        if (section === 'inventory') loadFullInventory();
    }

    // ── Quick Peek Modal ──────────────────────────
    function openProjectModal(project) {
        currentProject = project;
        document.getElementById('modalTitle').textContent = project.job_code + ' — ' + (project.project_name || 'Untitled');

        var badgeGroup = document.getElementById('modalBadgeGroup');
        badgeGroup.innerHTML = '';
        var stageBadge = document.createElement('span');
        stageBadge.className = 'modal-badge';
        stageBadge.style.backgroundColor = '#1E40AF';
        stageBadge.textContent = (STAGE_LABELS[project.stage] || project.stage).toUpperCase();
        badgeGroup.appendChild(stageBadge);

        if (project.n_versions > 0) {
            var vBadge = document.createElement('span');
            vBadge.className = 'modal-badge';
            vBadge.style.backgroundColor = '#F59E0B';
            vBadge.textContent = 'v' + project.n_versions;
            badgeGroup.appendChild(vBadge);
        }

        // Pipeline dots in modal
        document.getElementById('modalPipeline').innerHTML = buildPipelineDots(project.stage, false);

        // Overview info
        var info = document.getElementById('overviewInfo');
        info.innerHTML = '';
        var items = [
            { label: 'Job Code', value: project.job_code },
            { label: 'Project Name', value: project.project_name },
            { label: 'Customer', value: project.customer_name },
            { label: 'Stage', value: (STAGE_LABELS[project.stage] || project.stage) },
            { label: 'Documents', value: (project.doc_count || 0) + ' files' },
            { label: 'Updated', value: project.updated_at ? new Date(project.updated_at).toLocaleDateString() : '-' },
        ];
        items.forEach(function(item) {
            var div = document.createElement('div');
            div.className = 'info-item';
            div.innerHTML = '<div class="info-label">' + item.label + '</div><div class="info-value">' + esc(item.value || '-') + '</div>';
            info.appendChild(div);
        });

        // Navigation buttons
        var jc = encodeURIComponent(project.job_code);
        document.getElementById('openFullPageBtn').onclick = function() { window.location.href = '/project/' + jc; };
        document.getElementById('openShopDrawingsBtn').onclick = function() { window.location.href = '/shop-drawings/' + jc; };
        document.getElementById('openWorkOrdersBtn').onclick = function() { window.location.href = '/work-orders/' + jc; };

        document.getElementById('projectModal').classList.add('show');
    }

    function closeProjectModal() {
        document.getElementById('projectModal').classList.remove('show');
        currentProject = null;
    }

    // ── New Project Modal ─────────────────────────
    function openNewProjectForm() {
        fetch('/api/project/next-code')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var code = data.job_code || '';
                document.getElementById('npJobCode').value = code;
                document.getElementById('newJobCodeBadge').textContent = code;
            })
            .catch(function() {
                document.getElementById('npJobCode').value = 'ERROR';
                document.getElementById('newJobCodeBadge').textContent = 'ERROR';
            });

        document.getElementById('npProjectName').value = '';
        document.getElementById('npCustomerName').value = '';
        document.getElementById('npCustomerPhone').value = '';
        document.getElementById('npCustomerEmail').value = '';
        document.getElementById('npStreet').value = '';
        document.getElementById('npCity').value = '';
        document.getElementById('npState').value = '';
        document.getElementById('npZip').value = '';
        document.getElementById('npStage').value = 'quote';
        document.getElementById('npNotes').value = '';
        document.getElementById('npSubmitBtn').disabled = false;
        document.getElementById('npSubmitBtn').textContent = 'Create Project';

        document.getElementById('newProjectModal').classList.add('show');
        setTimeout(function() { document.getElementById('npProjectName').focus(); }, 200);
    }

    function closeNewProjectModal() { document.getElementById('newProjectModal').classList.remove('show'); }

    function submitNewProject(e) {
        e.preventDefault();
        var jobCode = document.getElementById('npJobCode').value.trim();
        var projectName = document.getElementById('npProjectName').value.trim();
        if (!projectName) { alert('Please enter a project name.'); return false; }

        var submitBtn = document.getElementById('npSubmitBtn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating...';

        var payload = {
            job_code: jobCode,
            project_name: projectName,
            customer_name: document.getElementById('npCustomerName').value.trim(),
            customer_phone: document.getElementById('npCustomerPhone').value.trim(),
            customer_email: document.getElementById('npCustomerEmail').value.trim(),
            location_street: document.getElementById('npStreet').value.trim(),
            location_city: document.getElementById('npCity').value.trim(),
            location_state: document.getElementById('npState').value.trim().toUpperCase(),
            location_zip: document.getElementById('npZip').value.trim(),
            stage: document.getElementById('npStage').value,
            notes: document.getElementById('npNotes').value.trim(),
        };

        fetch('/api/project/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.ok) {
                closeNewProjectModal();
                window.location.href = '/project/' + encodeURIComponent(data.job_code);
            } else {
                alert('Error creating project: ' + (data.error || 'Unknown error'));
                submitBtn.disabled = false;
                submitBtn.textContent = 'Create Project';
            }
        })
        .catch(function(err) {
            alert('Error: ' + err.message);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Create Project';
        });

        return false;
    }

    // ── Helpers ───────────────────────────────────
    function esc(s) {
        var d = document.createElement('div');
        d.textContent = s || '';
        return d.innerHTML;
    }

    function handleLogout() {
        if (confirm('Are you sure you want to logout?')) window.location.href = '/auth/logout';
    }

    // ══════════════════════════════════════════════
    // INVENTORY MANAGEMENT
    // ══════════════════════════════════════════════
    var inventoryData = {};

    function loadInventoryAlerts() {
        fetch('/api/inventory')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var coils = data.coils || {};
                var alertCount = 0;
                Object.values(coils).forEach(function(c) {
                    var avail = (c.stock_lbs || 0) - (c.committed_lbs || 0);
                    var minStock = c.min_stock_lbs || 2000;
                    if (avail <= 0 || avail < minStock) alertCount++;
                });
                var dot = document.getElementById('invAlertDot');
                if (alertCount > 0) {
                    dot.textContent = alertCount;
                    dot.classList.add('show');
                }
            })
            .catch(function() {});
    }

    function loadFullInventory() {
        fetch('/api/inventory')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                inventoryData = data.coils || {};
                renderInventoryTable();
                updateInventoryStats();
            })
            .catch(function(e) { console.error('Inventory error:', e); });
    }

    function updateInventoryStats() {
        var coils = Object.values(inventoryData);
        var total = coils.length;
        var outCount = 0, lowCount = 0, okCount = 0;

        coils.forEach(function(c) {
            var avail = (c.stock_lbs || 0) - (c.committed_lbs || 0);
            var minStock = c.min_stock_lbs || 2000;
            if (avail <= 0) outCount++;
            else if (avail < minStock) lowCount++;
            else okCount++;
        });

        document.getElementById('invTotalCoils').textContent = total;
        document.getElementById('invInStock').textContent = okCount;
        document.getElementById('invLowStock').textContent = lowCount;
        document.getElementById('invOutStock').textContent = outCount;

        var dot = document.getElementById('invAlertDot');
        var alertTotal = outCount + lowCount;
        if (alertTotal > 0) {
            dot.textContent = alertTotal;
            dot.classList.add('show');
        } else {
            dot.classList.remove('show');
        }
    }

    function renderInventoryTable() {
        var tbody = document.getElementById('invTableBody');
        tbody.innerHTML = '';
        var ids = Object.keys(inventoryData).sort();

        if (ids.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;padding:2rem;color:var(--tf-gray-400);">No coils in inventory. Click "+ Add Coil" to get started.</td></tr>';
            return;
        }

        ids.forEach(function(id) {
            var c = inventoryData[id];
            var avail = (c.stock_lbs || 0) - (c.committed_lbs || 0);
            var minStock = c.min_stock_lbs || 2000;
            var statusClass, statusText;

            if (avail <= 0) { statusClass = 'tf-badge-danger'; statusText = 'OUT'; }
            else if (avail < minStock) { statusClass = 'tf-badge-amber'; statusText = 'LOW'; }
            else { statusClass = 'tf-badge-success'; statusText = 'OK'; }

            var row = document.createElement('tr');
            row.style.cursor = 'pointer';
            row.onclick = function(e) {
                if (e.target.tagName === 'BUTTON') return;
                window.location.href = '/coil/' + encodeURIComponent(id);
            };

            row.innerHTML = '<td><strong>' + esc(id) + '</strong></td>'
                + '<td>' + esc(c.description || c.name || '') + '</td>'
                + '<td>' + esc(c.gauge || '') + '</td>'
                + '<td>' + esc(c.width || '') + '</td>'
                + '<td>' + esc(c.color || '') + '</td>'
                + '<td style="font-weight:700;">' + Number(c.stock_lbs || 0).toLocaleString() + '</td>'
                + '<td>' + Number(minStock).toLocaleString() + '</td>'
                + '<td><span class="tf-badge ' + statusClass + '">' + statusText + '</span></td>'
                + '<td>'
                + '<button class="tf-btn tf-btn-ghost tf-btn-sm" onclick="event.stopPropagation();openEditStock(\'' + esc(id) + '\')">Edit</button>'
                + '<button class="tf-btn tf-btn-ghost tf-btn-sm" style="color:var(--tf-danger);" onclick="event.stopPropagation();deleteCoil(\'' + esc(id) + '\')">Delete</button>'
                + '</td>';

            tbody.appendChild(row);
        });
    }

    // ── Coil Modals ───────────────────────────────
    function openAddCoilModal() {
        ['newCoilId','newCoilDesc','newCoilGauge','newCoilWidth','newCoilColor','newCoilStock','newCoilCostLb'].forEach(function(id) { document.getElementById(id).value = ''; });
        document.getElementById('newCoilMinStock').value = '2000';
        document.getElementById('addCoilModal').classList.add('show');
    }
    function closeAddCoilModal() { document.getElementById('addCoilModal').classList.remove('show'); }

    function submitNewCoil(e) {
        e.preventDefault();
        var coilId = document.getElementById('newCoilId').value.trim();
        var desc = document.getElementById('newCoilDesc').value.trim();
        if (!coilId || !desc) return false;

        var payload = {};
        payload[coilId] = {
            name: desc, description: desc,
            gauge: document.getElementById('newCoilGauge').value.trim(),
            width: document.getElementById('newCoilWidth').value.trim(),
            color: document.getElementById('newCoilColor').value.trim(),
            stock_lbs: parseFloat(document.getElementById('newCoilStock').value) || 0,
            committed_lbs: 0,
            min_stock_lbs: parseFloat(document.getElementById('newCoilMinStock').value) || 2000,
            cost_per_lb: parseFloat(document.getElementById('newCoilCostLb').value) || 0,
            mill_certs: [],
        };

        fetch('/api/inventory/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ coils: payload, merge: true })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.ok || data.saved) { closeAddCoilModal(); loadFullInventory(); }
            else { alert('Error: ' + (data.error || 'Unknown')); }
        })
        .catch(function(e) { alert('Error: ' + e.message); });
        return false;
    }

    function openEditStock(coilId) {
        var c = inventoryData[coilId];
        if (!c) return;
        document.getElementById('editStockCoilId').value = coilId;
        document.getElementById('editStockCoilName').value = coilId + ' — ' + (c.description || c.name || '');
        document.getElementById('editStockCurrent').value = c.stock_lbs || 0;
        document.getElementById('editStockNew').value = c.stock_lbs || 0;
        document.getElementById('editStockMin').value = c.min_stock_lbs || 2000;
        document.getElementById('editStockModal').classList.add('show');
    }
    function closeEditStockModal() { document.getElementById('editStockModal').classList.remove('show'); }

    function submitStockUpdate() {
        var coilId = document.getElementById('editStockCoilId').value;
        var newStock = parseFloat(document.getElementById('editStockNew').value) || 0;
        var minStock = parseFloat(document.getElementById('editStockMin').value) || 0;

        fetch('/api/inventory/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ coil_id: coilId, stock_lbs: newStock, min_stock_lbs: minStock })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) { closeEditStockModal(); loadFullInventory(); })
        .catch(function(e) { alert('Error: ' + e.message); });
    }

    function deleteCoil(coilId) {
        if (!confirm('Delete coil "' + coilId + '"? This cannot be undone.')) return;
        fetch('/api/inventory/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ coil_id: coilId })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) { if (data.ok) loadFullInventory(); else alert('Error: ' + (data.error || 'Unknown')); })
        .catch(function(e) { alert('Error: ' + e.message); });
    }

    function openAddCertModal() {
        var sel = document.getElementById('certCoilSelect');
        sel.innerHTML = '';
        Object.keys(inventoryData).sort().forEach(function(id) {
            var opt = document.createElement('option');
            opt.value = id;
            opt.textContent = id + ' — ' + (inventoryData[id].description || inventoryData[id].name || '');
            sel.appendChild(opt);
        });
        document.getElementById('certHeatNum').value = '';
        document.getElementById('certFile').value = '';
        document.getElementById('addCertModal').classList.add('show');
    }
    function closeAddCertModal() { document.getElementById('addCertModal').classList.remove('show'); }

    function submitCert() {
        var coilId = document.getElementById('certCoilSelect').value;
        var heatNum = document.getElementById('certHeatNum').value.trim();
        var fileInput = document.getElementById('certFile');

        if (!coilId) { alert('Select a coil.'); return; }
        if (!fileInput.files.length) { alert('Select a certificate file.'); return; }

        var formData = new FormData();
        formData.append('coil_id', coilId);
        formData.append('heat_num', heatNum);
        formData.append('file', fileInput.files[0]);

        fetch('/api/inventory/cert/upload', { method: 'POST', body: formData })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.ok) { closeAddCertModal(); loadFullInventory(); alert('Certificate uploaded for ' + coilId); }
            else { alert('Error: ' + (data.error || 'Unknown')); }
        })
        .catch(function(e) { alert('Upload error: ' + e.message); });
    }
    </script>
</body>
</html>
"""
