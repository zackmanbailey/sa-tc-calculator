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

        /* ── Dashboard Modern Design System ─────────── */
        :root {
            --dash-bg: #0B1120;
            --dash-surface: #141D2F;
            --dash-surface-2: #1A2540;
            --dash-border: rgba(59, 130, 246, 0.12);
            --dash-border-subtle: rgba(255,255,255,0.06);
            --dash-text: #E2E8F0;
            --dash-text-dim: #94A3B8;
            --dash-text-muted: #64748B;
            --dash-accent: #3B82F6;
            --dash-accent-glow: rgba(59, 130, 246, 0.15);
            --dash-green: #10B981;
            --dash-amber: #F59E0B;
            --dash-red: #EF4444;
            --dash-purple: #8B5CF6;
            --dash-radius: 14px;
            --dash-radius-sm: 10px;
            --dash-radius-xs: 6px;
        }

        body {
            background: var(--dash-bg) !important;
            color: var(--dash-text);
        }

        /* ── Main Container ─────────────────────────── */
        .mc {
            max-width: 1440px;
            margin: 0 auto;
            padding: 28px 32px 48px;
        }

        /* ── Welcome Header ─────────────────────────── */
        .dash-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 32px;
            flex-wrap: wrap;
            gap: 16px;
        }

        .dash-header-left h1 {
            font-size: 1.75rem;
            font-weight: 700;
            color: #F8FAFC;
            letter-spacing: -0.03em;
            margin: 0;
            line-height: 1.3;
        }

        .dash-header-left h1 .name-gradient {
            background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 50%, #F472B6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .dash-header-meta {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 8px;
            flex-wrap: wrap;
        }

        .dash-date {
            font-size: 0.85rem;
            color: var(--dash-text-dim);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .role-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            background: rgba(59, 130, 246, 0.15);
            color: #60A5FA;
            border: 1px solid rgba(59, 130, 246, 0.25);
        }

        .role-badge.role-admin { background: rgba(139, 92, 246, 0.15); color: #A78BFA; border-color: rgba(139, 92, 246, 0.25); }
        .role-badge.role-shop  { background: rgba(245, 158, 11, 0.15); color: #FBBF24; border-color: rgba(245, 158, 11, 0.25); }
        .role-badge.role-qc    { background: rgba(16, 185, 129, 0.15); color: #34D399; border-color: rgba(16, 185, 129, 0.25); }

        .dash-header-actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .dash-action-btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            font-size: 0.8rem;
            font-weight: 600;
            border: 1px solid var(--dash-border);
            border-radius: var(--dash-radius-sm);
            background: var(--dash-surface);
            color: var(--dash-text);
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            font-family: inherit;
        }

        .dash-action-btn:hover {
            background: var(--dash-surface-2);
            border-color: var(--dash-accent);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        .dash-action-btn.primary {
            background: linear-gradient(135deg, #2563EB, #3B82F6);
            border-color: rgba(59, 130, 246, 0.4);
            color: #fff;
        }

        .dash-action-btn.primary:hover {
            background: linear-gradient(135deg, #1D4ED8, #2563EB);
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
        }

        /* ── Metrics Row (Glassmorphism) ────────────── */
        .metrics-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 32px;
        }

        .metric-card {
            position: relative;
            padding: 22px 20px;
            border-radius: var(--dash-radius);
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.6));
            border: 1px solid var(--dash-border-subtle);
            backdrop-filter: blur(16px);
            overflow: hidden;
            cursor: pointer;
            transition: all 0.25s ease;
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            opacity: 0.8;
        }

        .metric-card.mc-blue::before   { background: linear-gradient(90deg, #3B82F6, #60A5FA); }
        .metric-card.mc-amber::before  { background: linear-gradient(90deg, #F59E0B, #FBBF24); }
        .metric-card.mc-green::before  { background: linear-gradient(90deg, #10B981, #34D399); }
        .metric-card.mc-red::before    { background: linear-gradient(90deg, #EF4444, #F87171); }
        .metric-card.mc-purple::before { background: linear-gradient(90deg, #8B5CF6, #A78BFA); }

        .metric-card:hover {
            transform: translateY(-2px);
            border-color: rgba(59, 130, 246, 0.2);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3), 0 0 0 1px rgba(59, 130, 246, 0.1);
        }

        .metric-card-inner {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .metric-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            flex-shrink: 0;
        }

        .metric-icon.mi-blue   { background: rgba(59, 130, 246, 0.15); }
        .metric-icon.mi-amber  { background: rgba(245, 158, 11, 0.15); }
        .metric-icon.mi-green  { background: rgba(16, 185, 129, 0.15); }
        .metric-icon.mi-red    { background: rgba(239, 68, 68, 0.15); }
        .metric-icon.mi-purple { background: rgba(139, 92, 246, 0.15); }

        .metric-data { flex: 1; }

        .metric-value {
            font-size: 1.8rem;
            font-weight: 800;
            color: #F8FAFC;
            line-height: 1;
            letter-spacing: -0.02em;
        }

        .metric-label {
            font-size: 0.7rem;
            font-weight: 600;
            color: var(--dash-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 4px;
        }

        .metric-trend {
            font-size: 0.7rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 2px;
            margin-top: 4px;
            padding: 2px 6px;
            border-radius: 4px;
        }

        .metric-trend.up   { color: #34D399; background: rgba(16, 185, 129, 0.1); }
        .metric-trend.down { color: #F87171; background: rgba(239, 68, 68, 0.1); }
        .metric-trend.flat { color: var(--dash-text-muted); background: rgba(100,116,139,0.1); }

        /* ── Role-Dynamic Content Sections ──────────── */
        .dash-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 32px;
        }

        .dash-grid-full {
            grid-column: 1 / -1;
        }

        .dash-card {
            background: var(--dash-surface);
            border: 1px solid var(--dash-border-subtle);
            border-radius: var(--dash-radius);
            overflow: hidden;
        }

        .dash-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 20px;
            border-bottom: 1px solid var(--dash-border-subtle);
        }

        .dash-card-title {
            font-size: 0.9rem;
            font-weight: 700;
            color: #F1F5F9;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .dash-card-title .card-icon {
            font-size: 1rem;
        }

        .dash-card-badge {
            font-size: 0.65rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.15);
            color: #60A5FA;
        }

        .dash-card-body {
            padding: 16px 20px;
            max-height: 380px;
            overflow-y: auto;
        }

        .dash-card-body::-webkit-scrollbar { width: 4px; }
        .dash-card-body::-webkit-scrollbar-track { background: transparent; }
        .dash-card-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

        /* ── Activity Feed ──────────────────────────── */
        .activity-item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 10px 0;
            border-bottom: 1px solid var(--dash-border-subtle);
        }

        .activity-item:last-child { border-bottom: none; }

        .activity-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
            margin-top: 6px;
        }

        .activity-dot.green  { background: var(--dash-green); box-shadow: 0 0 6px rgba(16,185,129,0.4); }
        .activity-dot.blue   { background: var(--dash-accent); box-shadow: 0 0 6px rgba(59,130,246,0.4); }
        .activity-dot.amber  { background: var(--dash-amber); box-shadow: 0 0 6px rgba(245,158,11,0.4); }
        .activity-dot.red    { background: var(--dash-red); box-shadow: 0 0 6px rgba(239,68,68,0.4); }
        .activity-dot.purple { background: var(--dash-purple); box-shadow: 0 0 6px rgba(139,92,246,0.4); }

        .activity-text {
            font-size: 0.8rem;
            color: var(--dash-text);
            line-height: 1.4;
        }

        .activity-text strong { color: #F1F5F9; }

        .activity-time {
            font-size: 0.68rem;
            color: var(--dash-text-muted);
            margin-top: 2px;
        }

        /* ── System Health / Overview Cards ─────────── */
        .health-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }

        .health-item {
            text-align: center;
            padding: 14px 10px;
            background: rgba(255,255,255,0.02);
            border-radius: var(--dash-radius-sm);
            border: 1px solid var(--dash-border-subtle);
        }

        .health-value {
            font-size: 1.3rem;
            font-weight: 800;
            color: #F8FAFC;
        }

        .health-label {
            font-size: 0.68rem;
            color: var(--dash-text-muted);
            margin-top: 2px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .status-dot {
            display: inline-block;
            width: 7px;
            height: 7px;
            border-radius: 50%;
            margin-right: 4px;
            vertical-align: middle;
        }

        .status-dot.green  { background: var(--dash-green); box-shadow: 0 0 4px rgba(16,185,129,0.5); }
        .status-dot.amber  { background: var(--dash-amber); box-shadow: 0 0 4px rgba(245,158,11,0.5); }
        .status-dot.red    { background: var(--dash-red); box-shadow: 0 0 4px rgba(239,68,68,0.5); }

        /* ── Shop Floor Queue ───────────────────────── */
        .queue-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 12px;
            margin-bottom: 6px;
            background: rgba(255,255,255,0.02);
            border-radius: var(--dash-radius-xs);
            border: 1px solid var(--dash-border-subtle);
            transition: all 0.15s ease;
            cursor: pointer;
        }

        .queue-item:hover {
            background: rgba(59, 130, 246, 0.05);
            border-color: rgba(59, 130, 246, 0.2);
        }

        .queue-priority {
            width: 4px;
            height: 32px;
            border-radius: 2px;
            flex-shrink: 0;
        }

        .queue-priority.high   { background: var(--dash-red); }
        .queue-priority.medium { background: var(--dash-amber); }
        .queue-priority.normal { background: var(--dash-green); }

        .queue-info { flex: 1; min-width: 0; }

        .queue-title {
            font-size: 0.8rem;
            font-weight: 600;
            color: #F1F5F9;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .queue-subtitle {
            font-size: 0.7rem;
            color: var(--dash-text-muted);
            margin-top: 1px;
        }

        .queue-status {
            font-size: 0.65rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 999px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            flex-shrink: 0;
        }

        .queue-status.pending  { background: rgba(245,158,11,0.15); color: #FBBF24; }
        .queue-status.active   { background: rgba(59,130,246,0.15); color: #60A5FA; }
        .queue-status.done     { background: rgba(16,185,129,0.15); color: #34D399; }

        /* ── Progress Bars ──────────────────────────── */
        .progress-item {
            margin-bottom: 14px;
        }

        .progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }

        .progress-label {
            font-size: 0.78rem;
            font-weight: 600;
            color: var(--dash-text);
        }

        .progress-pct {
            font-size: 0.72rem;
            font-weight: 700;
            color: var(--dash-text-dim);
        }

        .progress-track {
            height: 6px;
            background: rgba(255,255,255,0.06);
            border-radius: 3px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.8s ease;
        }

        .progress-fill.blue   { background: linear-gradient(90deg, #2563EB, #60A5FA); }
        .progress-fill.green  { background: linear-gradient(90deg, #059669, #34D399); }
        .progress-fill.amber  { background: linear-gradient(90deg, #D97706, #FBBF24); }
        .progress-fill.purple { background: linear-gradient(90deg, #7C3AED, #A78BFA); }

        /* ── QC Inspection Items ────────────────────── */
        .qc-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 12px;
            margin-bottom: 6px;
            background: rgba(255,255,255,0.02);
            border-radius: var(--dash-radius-xs);
            border: 1px solid var(--dash-border-subtle);
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .qc-item:hover {
            background: rgba(16, 185, 129, 0.05);
            border-color: rgba(16, 185, 129, 0.2);
        }

        .qc-type-badge {
            font-size: 0.65rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 999px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .qc-type-badge.inspection { background: rgba(59,130,246,0.15); color: #60A5FA; }
        .qc-type-badge.ncr        { background: rgba(239,68,68,0.15); color: #F87171; }
        .qc-type-badge.signoff    { background: rgba(16,185,129,0.15); color: #34D399; }

        /* ── Gamification Stats Grid ────────────────── */
        .gamification-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }

        .gam-stat {
            text-align: center;
            padding: 16px 10px;
            background: rgba(255,255,255,0.02);
            border-radius: var(--dash-radius-sm);
            border: 1px solid var(--dash-border-subtle);
        }

        .gam-value {
            font-size: 1.6rem;
            font-weight: 800;
            color: #F8FAFC;
            line-height: 1;
        }

        .gam-label {
            font-size: 0.68rem;
            color: var(--dash-text-muted);
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        /* ── Quick Links ────────────────────────────── */
        .quick-links-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            margin-bottom: 32px;
        }

        .quick-link {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
            padding: 20px 14px;
            background: var(--dash-surface);
            border: 1px solid var(--dash-border-subtle);
            border-radius: var(--dash-radius);
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            text-align: center;
        }

        .quick-link:hover {
            transform: translateY(-3px);
            border-color: rgba(59, 130, 246, 0.3);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }

        .quick-link-icon {
            width: 46px;
            height: 46px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
        }

        .qli-blue   { background: linear-gradient(135deg, rgba(37,99,235,0.2), rgba(96,165,250,0.1)); }
        .qli-amber  { background: linear-gradient(135deg, rgba(217,119,6,0.2), rgba(251,191,36,0.1)); }
        .qli-green  { background: linear-gradient(135deg, rgba(5,150,105,0.2), rgba(52,211,153,0.1)); }
        .qli-purple { background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(167,139,250,0.1)); }
        .qli-navy   { background: linear-gradient(135deg, rgba(30,41,59,0.8), rgba(51,65,85,0.6)); }

        .quick-link-title {
            font-size: 0.8rem;
            font-weight: 700;
            color: #F1F5F9;
        }

        .quick-link-desc {
            font-size: 0.68rem;
            color: var(--dash-text-muted);
            line-height: 1.4;
        }

        /* ── Section Divider ────────────────────────── */
        .section-divider {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 28px 0 18px;
        }

        .section-divider h2 {
            font-size: 1rem;
            font-weight: 700;
            color: #F1F5F9;
            white-space: nowrap;
        }

        .section-divider::after {
            content: '';
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, var(--dash-border-subtle), transparent);
        }

        /* ── Section Tabs ──────────────────────────── */
        .mc-section-tabs {
            display: flex;
            gap: 2px;
            border-bottom: 1px solid var(--dash-border-subtle);
            margin-bottom: 20px;
        }

        .mc-tab {
            background: none;
            border: none;
            padding: 10px 18px;
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--dash-text-muted);
            cursor: pointer;
            border-bottom: 2px solid transparent;
            margin-bottom: -1px;
            transition: all 0.15s ease;
            display: flex;
            align-items: center;
            gap: 6px;
            font-family: inherit;
        }

        .mc-tab:hover { color: var(--dash-text); }
        .mc-tab.active { color: #60A5FA; border-bottom-color: #3B82F6; }

        .mc-tab-badge {
            background: var(--dash-red);
            color: #fff;
            border-radius: 50%;
            font-size: 9px;
            font-weight: 700;
            width: 18px;
            height: 18px;
            display: none;
            align-items: center;
            justify-content: center;
        }

        .mc-tab-badge.show { display: inline-flex; }

        /* ── Pipeline Header ────────────────────────── */
        .mc-pipeline-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            flex-wrap: wrap;
            gap: 12px;
        }

        .mc-pipeline-header h2 {
            font-size: 1rem;
            font-weight: 700;
            color: #F1F5F9;
        }

        .mc-pipeline-controls {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .view-pill {
            display: flex;
            background: rgba(255,255,255,0.04);
            padding: 3px;
            border-radius: var(--dash-radius-xs);
            border: 1px solid var(--dash-border-subtle);
        }

        .pill-btn {
            background: transparent;
            border: none;
            padding: 6px 14px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--dash-text-muted);
            transition: all 0.15s ease;
            font-family: inherit;
        }

        .pill-btn.active {
            background: rgba(59, 130, 246, 0.15);
            color: #60A5FA;
        }

        .pill-btn:hover:not(.active) { color: var(--dash-text); }

        .filter-toggle {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.72rem;
            color: var(--dash-text-muted);
            cursor: pointer;
            font-weight: 500;
        }

        .filter-toggle input[type="checkbox"] {
            width: 14px;
            height: 14px;
            accent-color: var(--dash-accent);
        }

        /* ── Pipeline Cards ─────────────────────────── */
        .pipeline-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 14px;
            margin-bottom: 32px;
        }

        .pipe-card {
            background: var(--dash-surface);
            border: 1px solid var(--dash-border-subtle);
            border-radius: var(--dash-radius);
            padding: 20px;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
        }

        .pipe-card:hover {
            border-color: rgba(59, 130, 246, 0.25);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            transform: translateY(-2px);
        }

        .pipe-card-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }

        .pipe-job {
            font-size: 0.7rem;
            font-weight: 700;
            color: #60A5FA;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .pipe-stage-badge {
            display: inline-flex;
            align-items: center;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.6rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .psb-quote, .psb-contract          { background: rgba(59,130,246,0.15); color: #60A5FA; }
        .psb-engineering, .psb-shop-drawings { background: rgba(139,92,246,0.15); color: #A78BFA; }
        .psb-fabrication                     { background: rgba(245,158,11,0.15); color: #FBBF24; }
        .psb-shipping, .psb-install          { background: rgba(16,185,129,0.15); color: #34D399; }
        .psb-complete                        { background: rgba(100,116,139,0.15); color: #94A3B8; }

        .pipe-name {
            font-size: 0.95rem;
            font-weight: 700;
            color: #F1F5F9;
            margin-bottom: 2px;
            line-height: 1.3;
        }

        .pipe-customer {
            font-size: 0.72rem;
            color: var(--dash-text-muted);
            margin-bottom: 14px;
        }

        /* Pipeline Dots */
        .pipe-progress {
            display: flex;
            align-items: center;
            gap: 0;
            margin-bottom: 12px;
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
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid rgba(255,255,255,0.1);
            background: var(--dash-surface);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 9px;
            transition: all 0.3s ease;
            position: relative;
            z-index: 2;
        }

        .pipe-dot.done {
            background: var(--dash-green);
            border-color: var(--dash-green);
            color: #fff;
        }

        .pipe-dot.active {
            background: var(--dash-accent);
            border-color: var(--dash-accent);
            color: #fff;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
            animation: dotPulse 2s ease-in-out infinite;
        }

        @keyframes dotPulse {
            0%, 100% { box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2); }
            50% { box-shadow: 0 0 0 8px rgba(59, 130, 246, 0.08); }
        }

        .pipe-dot.pending {
            background: var(--dash-surface);
            border-color: rgba(255,255,255,0.1);
        }

        .pipe-step-label {
            font-size: 7px;
            font-weight: 600;
            color: var(--dash-text-muted);
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            text-align: center;
            white-space: nowrap;
        }

        .pipe-step-label.active-label { color: #60A5FA; font-weight: 700; }
        .pipe-step-label.done-label   { color: #34D399; }

        .pipe-connector {
            height: 2px;
            flex: 1;
            background: rgba(255,255,255,0.06);
            position: relative;
            top: -10px;
            z-index: 0;
            margin: 0 -3px;
        }

        .pipe-connector.done   { background: var(--dash-green); }
        .pipe-connector.active { background: linear-gradient(90deg, var(--dash-green), var(--dash-accent)); }

        .pipe-bar-track {
            width: 100%;
            height: 4px;
            background: rgba(255,255,255,0.05);
            border-radius: 2px;
            overflow: hidden;
            margin-bottom: 8px;
        }

        .pipe-bar-fill {
            height: 100%;
            border-radius: 2px;
            transition: width 0.6s ease;
        }

        .pipe-bar-fill.early  { background: linear-gradient(90deg, #2563EB, #60A5FA); }
        .pipe-bar-fill.mid    { background: linear-gradient(90deg, #7C3AED, #A78BFA); }
        .pipe-bar-fill.late   { background: linear-gradient(90deg, #D97706, #FBBF24); }
        .pipe-bar-fill.almost { background: linear-gradient(90deg, #059669, #34D399); }
        .pipe-bar-fill.done   { background: rgba(100,116,139,0.5); }

        .pipe-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.7rem;
            color: var(--dash-text-muted);
        }

        .pipe-meta-docs {
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .pipe-pct {
            font-weight: 700;
            color: var(--dash-text-dim);
        }

        .pipe-card.completed { opacity: 0.5; }
        .pipe-card.completed .pipe-name { text-decoration: line-through; }

        /* ── Kanban Board ──────────────────────────── */
        .kanban-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
            margin-bottom: 32px;
        }

        .kanban-column {
            background: rgba(255,255,255,0.02);
            border-radius: var(--dash-radius);
            padding: 14px;
            border: 1px solid var(--dash-border-subtle);
            min-height: 160px;
        }

        .column-header {
            font-size: 0.7rem;
            font-weight: 700;
            color: var(--dash-text-dim);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--dash-border-subtle);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .col-count {
            background: rgba(255,255,255,0.08);
            color: var(--dash-text-dim);
            padding: 2px 8px;
            border-radius: 999px;
            font-size: 0.62rem;
        }

        .mini-card {
            background: var(--dash-surface);
            border-radius: var(--dash-radius-xs);
            padding: 10px 12px;
            margin-bottom: 6px;
            cursor: pointer;
            transition: all 0.15s ease;
            border-left: 3px solid transparent;
            border-top: none;
            border-right: none;
            border-bottom: none;
        }

        .mini-card:hover {
            transform: translateX(2px);
            background: var(--dash-surface-2);
        }

        .mini-card.mc-quote, .mini-card.mc-contract          { border-left-color: #3B82F6; }
        .mini-card.mc-engineering, .mini-card.mc-shop-drawings { border-left-color: #8B5CF6; }
        .mini-card.mc-fabrication                              { border-left-color: #F59E0B; }
        .mini-card.mc-shipping, .mini-card.mc-install          { border-left-color: #10B981; }
        .mini-card.mc-complete                                 { border-left-color: #64748B; }

        .mini-card-job {
            font-size: 0.62rem;
            font-weight: 700;
            color: #60A5FA;
            text-transform: uppercase;
        }

        .mini-card-name {
            font-size: 0.8rem;
            font-weight: 600;
            color: #E2E8F0;
            margin-top: 2px;
            line-height: 1.3;
        }

        .mini-card-customer {
            font-size: 0.62rem;
            color: var(--dash-text-muted);
            margin-top: 2px;
        }

        /* ── Table View ────────────────────────────── */
        .table-container {
            background: var(--dash-surface);
            border-radius: var(--dash-radius);
            border: 1px solid var(--dash-border-subtle);
            overflow: hidden;
        }

        .table {
            width: 100%;
            border-collapse: collapse;
        }

        .table thead th {
            background: rgba(15, 23, 42, 0.8);
            color: var(--dash-text-dim);
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding: 10px 16px;
            text-align: left;
            cursor: pointer;
            user-select: none;
            white-space: nowrap;
            transition: background 0.15s ease;
            border-bottom: 1px solid var(--dash-border-subtle);
        }

        .table thead th:hover { background: rgba(30, 41, 59, 0.8); }

        .table td {
            padding: 10px 16px;
            border-bottom: 1px solid var(--dash-border-subtle);
            font-size: 0.82rem;
            color: var(--dash-text);
        }

        .table tbody tr { cursor: pointer; transition: background 0.15s ease; }
        .table tbody tr:hover td { background: rgba(59, 130, 246, 0.05); }

        .stage-badge {
            display: inline-flex;
            align-items: center;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 600;
            white-space: nowrap;
        }

        .stage-quote, .stage-contract          { background: rgba(59,130,246,0.15); color: #60A5FA; }
        .stage-engineering, .stage-shop-drawings { background: rgba(139,92,246,0.15); color: #A78BFA; }
        .stage-fabrication                       { background: rgba(245,158,11,0.15); color: #FBBF24; }
        .stage-shipping, .stage-install          { background: rgba(16,185,129,0.15); color: #34D399; }
        .stage-complete                          { background: rgba(100,116,139,0.15); color: #94A3B8; }

        .price.hidden { display: none; }

        /* ── Inventory Section ──────────────────────── */
        .inv-stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-bottom: 20px;
        }

        /* ── Quick Peek Modal ──────────────────────── */
        .modal {
            display: none;
            position: fixed;
            inset: 0;
            z-index: 2000;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(8px);
            animation: fadeIn 200ms ease;
        }

        .modal.show {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

        .modal-content {
            background: var(--dash-surface);
            border: 1px solid var(--dash-border-subtle);
            border-radius: 16px;
            width: 92%;
            max-width: 860px;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: 0 24px 48px rgba(0,0,0,0.5);
            animation: slideUp 250ms ease;
        }

        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to   { transform: translateY(0); opacity: 1; }
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 24px;
            border-bottom: 1px solid var(--dash-border-subtle);
        }

        .modal-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #F1F5F9;
        }

        .modal-badge-group { display: flex; gap: 8px; margin-top: 8px; }

        .modal-badge {
            display: inline-flex;
            align-items: center;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 600;
            color: #fff;
        }

        .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--dash-text-muted);
            padding: 8px;
            border-radius: 8px;
            transition: all 0.15s ease;
            line-height: 1;
        }
        .close-btn:hover { background: rgba(255,255,255,0.05); color: #F1F5F9; }

        .modal-body { padding: 24px; }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
        }

        .info-item {
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--dash-border-subtle);
            border-radius: var(--dash-radius-sm);
            padding: 14px;
        }

        .info-label {
            font-size: 0.68rem;
            font-weight: 600;
            color: var(--dash-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 4px;
        }

        .info-value {
            font-size: 0.9rem;
            font-weight: 600;
            color: #F1F5F9;
        }

        /* Forms */
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
        }

        .form-group { margin-bottom: 14px; }

        .form-group label {
            display: block;
            font-size: 0.68rem;
            font-weight: 600;
            color: var(--dash-text-dim);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 4px;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 10px 12px;
            font-family: inherit;
            font-size: 0.85rem;
            color: #F1F5F9;
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--dash-border-subtle);
            border-radius: var(--dash-radius-xs);
            outline: none;
            transition: all 0.15s ease;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            border-color: rgba(59, 130, 246, 0.5);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .form-group input::placeholder,
        .form-group textarea::placeholder { color: var(--dash-text-muted); }

        .form-group select { cursor: pointer; }
        .form-group select option { background: var(--dash-surface); color: var(--dash-text); }

        .form-section-title {
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--dash-text);
            margin-top: 16px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--dash-border-subtle);
        }

        .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 20px;
            padding-top: 16px;
            border-top: 1px solid var(--dash-border-subtle);
        }

        /* Empty state */
        .empty-state {
            text-align: center;
            padding: 48px 16px;
            color: var(--dash-text-muted);
        }
        .empty-state-icon { font-size: 2.5rem; margin-bottom: 12px; opacity: 0.4; }
        .empty-state-title { font-size: 0.95rem; font-weight: 700; color: var(--dash-text); margin-bottom: 8px; }

        /* Animation for counter */
        @keyframes countUp {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .metric-value.loaded { animation: countUp 0.4s ease forwards; }

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

        /* ── No-Data Placeholder ────────────────────── */
        .no-data {
            text-align: center;
            padding: 24px;
            color: var(--dash-text-muted);
            font-size: 0.82rem;
        }

        /* ── Responsive ────────────────────────────── */
        @media (max-width: 1280px) {
            .metrics-row { grid-template-columns: repeat(2, 1fr); }
            .dash-grid { grid-template-columns: 1fr; }
        }

        @media (max-width: 1024px) {
            .mc { padding: 20px 16px; }
            .pipeline-grid { grid-template-columns: 1fr; }
            .kanban-container { grid-template-columns: repeat(2, 1fr); }
            .modal-content { width: 95%; max-height: 90vh; }
            .inv-stats { grid-template-columns: repeat(2, 1fr); }
            .health-grid { grid-template-columns: repeat(2, 1fr); }
        }

        @media (max-width: 768px) {
            .metrics-row { grid-template-columns: 1fr; }
            .quick-links-grid { grid-template-columns: repeat(2, 1fr); }
            .kanban-container { grid-template-columns: 1fr; }
            .dash-header { flex-direction: column; align-items: flex-start; }
            .form-row { grid-template-columns: 1fr; }
            .inv-stats { grid-template-columns: 1fr; }
            .health-grid { grid-template-columns: 1fr; }
            .gamification-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <script>
        var USER_ROLE = '{{USER_ROLE}}';
        var USER_NAME = '{{USER_NAME}}';
        window.USER_ROLES = ['{{USER_ROLE}}'];
    </script>

    <div class="mc" data-user-role="{{USER_ROLE}}">

        <!-- ═══════════════════════════════════════════ -->
        <!-- WELCOME HEADER                              -->
        <!-- ═══════════════════════════════════════════ -->
        <div class="dash-header">
            <div class="dash-header-left">
                <h1 id="heroGreeting">Good morning, <span class="name-gradient" id="heroName">there</span></h1>
                <div class="dash-header-meta">
                    <span class="dash-date" id="heroDate">&#128197; Loading...</span>
                    <span class="role-badge" id="roleBadge">{{USER_ROLE}}</span>
                </div>
            </div>
            <div class="dash-header-actions" id="headerActions">
                <button class="dash-action-btn primary" onclick="openNewProjectForm()" id="newProjectBtn">+ New Project</button>
                <a class="dash-action-btn" href="/customers">+ New Customer</a>
                <a class="dash-action-btn" href="/sa">+ New Quote</a>
            </div>
        </div>

        <!-- ═══════════════════════════════════════════ -->
        <!-- KEY METRICS ROW                             -->
        <!-- ═══════════════════════════════════════════ -->
        <div class="metrics-row">
            <div class="metric-card mc-blue" onclick="scrollToProjects('all')">
                <div class="metric-card-inner">
                    <div class="metric-icon mi-blue">&#128202;</div>
                    <div class="metric-data">
                        <div class="metric-value" id="activeProjects">&mdash;</div>
                        <div class="metric-label">Active Projects</div>
                        <div class="metric-trend flat" id="projectsTrend">&#8212; steady</div>
                    </div>
                </div>
            </div>
            <div class="metric-card mc-amber" onclick="scrollToProjects('fabrication')">
                <div class="metric-card-inner">
                    <div class="metric-icon mi-amber">&#128295;</div>
                    <div class="metric-data">
                        <div class="metric-value" id="openWorkOrders">&mdash;</div>
                        <div class="metric-label">Open Work Orders</div>
                    </div>
                </div>
            </div>
            <div class="metric-card mc-green" onclick="switchSection('projects')">
                <div class="metric-card-inner">
                    <div class="metric-icon mi-green">&#128270;</div>
                    <div class="metric-data">
                        <div class="metric-value" id="pendingQC">&mdash;</div>
                        <div class="metric-label">Pending QC Items</div>
                    </div>
                </div>
            </div>
            <div class="metric-card mc-red" onclick="switchSection('inventory')">
                <div class="metric-card-inner">
                    <div class="metric-icon mi-red">&#9888;&#65039;</div>
                    <div class="metric-data">
                        <div class="metric-value" id="inventoryAlerts">&mdash;</div>
                        <div class="metric-label">Inventory Alerts</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ═══════════════════════════════════════════ -->
        <!-- ROLE-DYNAMIC CONTENT                        -->
        <!-- ═══════════════════════════════════════════ -->

        <!-- ADMIN / GOD MODE SECTION -->
        <div id="adminSection" class="dash-grid" style="display:none;">
            <!-- Business Overview -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128200;</span> Business Overview</div>
                </div>
                <div class="dash-card-body">
                    <div class="health-grid" id="businessOverview">
                        <div class="health-item">
                            <div class="health-value" id="bizActiveProjects">--</div>
                            <div class="health-label">Active Projects</div>
                        </div>
                        <div class="health-item">
                            <div class="health-value" id="bizTotalWOs">--</div>
                            <div class="health-label">Total Work Orders</div>
                        </div>
                        <div class="health-item">
                            <div class="health-value" id="bizTeamUtil">--</div>
                            <div class="health-label">Team Utilization</div>
                        </div>
                        <div class="health-item">
                            <div class="health-value" id="bizInEngineering">--</div>
                            <div class="health-label">In Engineering</div>
                        </div>
                        <div class="health-item">
                            <div class="health-value" id="bizInFabrication">--</div>
                            <div class="health-label">In Fabrication</div>
                        </div>
                        <div class="health-item">
                            <div class="health-value" id="bizReadyToShip">--</div>
                            <div class="health-label">Ready to Ship</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Activity Feed -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128337;</span> Recent Activity</div>
                    <span class="dash-card-badge" id="activityCount">0</span>
                </div>
                <div class="dash-card-body" id="activityFeed">
                    <div class="no-data">Loading activity...</div>
                </div>
            </div>

            <!-- System Health -->
            <div class="dash-card dash-grid-full">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128994;</span> System Health</div>
                </div>
                <div class="dash-card-body">
                    <div class="health-grid" id="systemHealth">
                        <div class="health-item">
                            <div class="health-value"><span class="status-dot green"></span> <span id="sysUsersOnline">--</span></div>
                            <div class="health-label">Active Users</div>
                        </div>
                        <div class="health-item">
                            <div class="health-value" id="sysPendingActions">--</div>
                            <div class="health-label">Pending Actions</div>
                        </div>
                        <div class="health-item">
                            <div class="health-value"><span class="status-dot green"></span> <span id="sysStatus">Online</span></div>
                            <div class="health-label">System Status</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- SHOP FLOOR SECTION -->
        <div id="shopSection" class="dash-grid" style="display:none;">
            <!-- My Queue / Today's Tasks -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128203;</span> My Queue</div>
                    <span class="dash-card-badge" id="queueCount">0</span>
                </div>
                <div class="dash-card-body" id="shopQueue">
                    <div class="no-data">Loading your queue...</div>
                </div>
            </div>

            <!-- Active Work Orders on Floor -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#127981;</span> Active on Floor</div>
                </div>
                <div class="dash-card-body" id="floorActive">
                    <div class="no-data">Loading floor status...</div>
                </div>
            </div>

            <!-- Production Progress -->
            <div class="dash-card dash-grid-full">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128200;</span> Production Progress</div>
                </div>
                <div class="dash-card-body" id="productionProgress">
                    <div class="no-data">Loading production data...</div>
                </div>
            </div>
        </div>

        <!-- QC INSPECTOR SECTION -->
        <div id="qcSection" class="dash-grid" style="display:none;">
            <!-- Inspection Queue -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128270;</span> Inspection Queue</div>
                    <span class="dash-card-badge" id="inspectionCount">0</span>
                </div>
                <div class="dash-card-body" id="inspectionQueue">
                    <div class="no-data">Loading inspections...</div>
                </div>
            </div>

            <!-- Open NCRs -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#9888;&#65039;</span> Open NCRs</div>
                    <span class="dash-card-badge" id="ncrCount">0</span>
                </div>
                <div class="dash-card-body" id="openNCRs">
                    <div class="no-data">Loading NCRs...</div>
                </div>
            </div>

            <!-- Inspection Stats & Calibration -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128202;</span> Inspection Stats</div>
                </div>
                <div class="dash-card-body">
                    <div class="health-grid" id="qcInspectionStats">
                        <div class="health-item">
                            <div class="health-value" id="qcTotalInspected">--</div>
                            <div class="health-label">Total Inspected</div>
                        </div>
                        <div class="health-item">
                            <div class="health-value" id="qcPassRate">--</div>
                            <div class="health-label">Pass Rate</div>
                        </div>
                        <div class="health-item">
                            <div class="health-value" id="qcCalibDue">--</div>
                            <div class="health-label">Calibration Due</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Sign-offs -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#9989;</span> Recent Sign-offs</div>
                </div>
                <div class="dash-card-body" id="recentSignoffs">
                    <div class="no-data">Loading sign-offs...</div>
                </div>
            </div>
        </div>

        <!-- ESTIMATOR SECTION -->
        <div id="estimatorSection" class="dash-grid" style="display:none;">
            <!-- Active Projects -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128202;</span> Active Projects</div>
                    <span class="dash-card-badge" id="estProjectCount">0</span>
                </div>
                <div class="dash-card-body" id="estActiveProjects">
                    <div class="no-data">Loading projects...</div>
                </div>
            </div>

            <!-- Quotes Pending -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128221;</span> Quotes Pending</div>
                    <span class="dash-card-badge" id="estQuoteCount">0</span>
                </div>
                <div class="dash-card-body" id="estQuotesPending">
                    <div class="no-data">Loading quotes...</div>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="dash-card dash-grid-full">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128337;</span> Recent Activity</div>
                    <span class="dash-card-badge" id="estActivityCount">0</span>
                </div>
                <div class="dash-card-body" id="estActivityFeed">
                    <div class="no-data">Loading activity...</div>
                </div>
            </div>
        </div>

        <!-- FABRICATOR / WELDER SECTION (My Work) -->
        <div id="fabSection" class="dash-grid" style="display:none;">
            <!-- My Queue -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128203;</span> My Queue</div>
                    <span class="dash-card-badge" id="fabQueueCount">0</span>
                </div>
                <div class="dash-card-body" id="fabQueue">
                    <div class="no-data">Loading your queue...</div>
                </div>
            </div>

            <!-- Recent Completions -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#9989;</span> Recent Completions</div>
                </div>
                <div class="dash-card-body" id="fabCompletions">
                    <div class="no-data">Loading completions...</div>
                </div>
            </div>

            <!-- Gamification Stats -->
            <div class="dash-card dash-grid-full">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#127942;</span> My Stats</div>
                </div>
                <div class="dash-card-body">
                    <div class="gamification-grid" id="fabGamification">
                        <div class="gam-stat">
                            <div class="gam-value" id="fabXP">0</div>
                            <div class="gam-label">XP Earned</div>
                        </div>
                        <div class="gam-stat">
                            <div class="gam-value" id="fabStreak">0</div>
                            <div class="gam-label">Day Streak</div>
                        </div>
                        <div class="gam-stat">
                            <div class="gam-value" id="fabAchievements">0</div>
                            <div class="gam-label">Achievements</div>
                        </div>
                        <div class="gam-stat">
                            <div class="gam-value" id="fabLevel">1</div>
                            <div class="gam-label">Level</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- SHIPPING SECTION -->
        <div id="shippingSection" class="dash-grid" style="display:none;">
            <!-- Ready to Ship -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128230;</span> Ready to Ship</div>
                    <span class="dash-card-badge" id="shipReadyCount">0</span>
                </div>
                <div class="dash-card-body" id="shipReady">
                    <div class="no-data">Loading ready items...</div>
                </div>
            </div>

            <!-- Today's Loads -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128666;</span> Today&#39;s Loads</div>
                    <span class="dash-card-badge" id="shipTodayCount">0</span>
                </div>
                <div class="dash-card-body" id="shipToday">
                    <div class="no-data">No loads scheduled today.</div>
                </div>
            </div>

            <!-- Recent Shipments -->
            <div class="dash-card dash-grid-full">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128203;</span> Recent Shipments</div>
                </div>
                <div class="dash-card-body" id="shipRecent">
                    <div class="no-data">Loading recent shipments...</div>
                </div>
            </div>
        </div>

        <!-- PROJECT MANAGER SECTION -->
        <div id="pmSection" class="dash-grid" style="display:none;">
            <!-- Active Projects with Progress -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128202;</span> Active Projects</div>
                    <span class="dash-card-badge" id="pmProjectCount">0</span>
                </div>
                <div class="dash-card-body" id="pmActiveProjects">
                    <div class="no-data">Loading projects...</div>
                </div>
            </div>

            <!-- Upcoming Milestones -->
            <div class="dash-card">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#127919;</span> Upcoming Milestones</div>
                </div>
                <div class="dash-card-body" id="pmMilestones">
                    <div class="no-data">Loading milestones...</div>
                </div>
            </div>

            <!-- Customer Activity -->
            <div class="dash-card dash-grid-full">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128100;</span> Customer Activity</div>
                </div>
                <div class="dash-card-body" id="pmCustomerActivity">
                    <div class="no-data">Loading customer activity...</div>
                </div>
            </div>
        </div>

        <!-- VIEWER SECTION (Read-only summary) -->
        <div id="viewerSection" class="dash-grid" style="display:none;">
            <div class="dash-card dash-grid-full">
                <div class="dash-card-header">
                    <div class="dash-card-title"><span class="card-icon">&#128200;</span> Business Summary</div>
                </div>
                <div class="dash-card-body">
                    <div class="health-grid" id="viewerOverview">
                        <div class="health-item">
                            <div class="health-value" id="viewerActiveProjects">--</div>
                            <div class="health-label">Active Projects</div>
                        </div>
                        <div class="health-item">
                            <div class="health-value" id="viewerTotalWOs">--</div>
                            <div class="health-label">Open Work Orders</div>
                        </div>
                        <div class="health-item">
                            <div class="health-value" id="viewerInFab">--</div>
                            <div class="health-label">In Fabrication</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ═══════════════════════════════════════════ -->
        <!-- QUICK LINKS (all roles)                     -->
        <!-- ═══════════════════════════════════════════ -->
        <div class="section-divider"><h2>Quick Links</h2></div>
        <div class="quick-links-grid" id="quickLinksGrid">
            <a class="quick-link" href="/sa">
                <div class="quick-link-icon qli-blue">&#128208;</div>
                <div class="quick-link-title">SA Estimator</div>
                <div class="quick-link-desc">Structures America pricing</div>
            </a>
            <a class="quick-link" href="/tc">
                <div class="quick-link-icon qli-amber">&#128221;</div>
                <div class="quick-link-title">TC Estimator</div>
                <div class="quick-link-desc">Titan Carports pricing</div>
            </a>
            <a class="quick-link" href="/shop-floor">
                <div class="quick-link-icon qli-navy">&#127981;</div>
                <div class="quick-link-title">Shop Floor</div>
                <div class="quick-link-desc">Production dashboard</div>
            </a>
            <a class="quick-link" href="/customers">
                <div class="quick-link-icon qli-green">&#128100;</div>
                <div class="quick-link-title">Customers</div>
                <div class="quick-link-desc">CRM & contacts</div>
            </a>
            <a class="quick-link" href="/work-orders">
                <div class="quick-link-icon qli-purple">&#128203;</div>
                <div class="quick-link-title">Work Orders</div>
                <div class="quick-link-desc">All work orders</div>
            </a>
        </div>

        <!-- ═══════════════════════════════════════════ -->
        <!-- SECTION TABS                                -->
        <!-- ═══════════════════════════════════════════ -->
        <div class="mc-section-tabs">
            <button class="mc-tab active" id="tabProjects" onclick="switchSection('projects')">
                &#128204; Projects
            </button>
            <button class="mc-tab" id="tabInventory" onclick="switchSection('inventory')">
                &#128230; Inventory
                <span class="mc-tab-badge" id="invAlertDot">0</span>
            </button>
        </div>

        <!-- ═══════════════════════════════════════════ -->
        <!-- PROJECTS SECTION                            -->
        <!-- ═══════════════════════════════════════════ -->
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

            <div id="pipelineView" class="pipeline-grid"></div>
            <div id="kanbanView" class="kanban-container" style="display:none;"></div>
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

        <!-- ═══════════════════════════════════════════ -->
        <!-- INVENTORY SECTION                           -->
        <!-- ═══════════════════════════════════════════ -->
        <div id="sectionInventory" style="display:none;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:12px;">
                <h2 style="font-size:1rem;font-weight:700;color:#F1F5F9;">Steel Coil Inventory</h2>
                <div style="display:flex;gap:8px;">
                    <button class="dash-action-btn primary" onclick="openAddCoilModal()">+ Add Coil</button>
                    <button class="dash-action-btn" onclick="openAddCertModal()">Upload Mill Cert</button>
                </div>
            </div>

            <div class="inv-stats">
                <div class="metric-card mc-blue">
                    <div class="metric-card-inner">
                        <div class="metric-icon mi-blue">&#128230;</div>
                        <div class="metric-data">
                            <div class="metric-value" id="invTotalCoils">&mdash;</div>
                            <div class="metric-label">Total Coils</div>
                        </div>
                    </div>
                </div>
                <div class="metric-card mc-green">
                    <div class="metric-card-inner">
                        <div class="metric-icon mi-green">&#9989;</div>
                        <div class="metric-data">
                            <div class="metric-value" id="invInStock">&mdash;</div>
                            <div class="metric-label">In Stock</div>
                        </div>
                    </div>
                </div>
                <div class="metric-card mc-amber">
                    <div class="metric-card-inner">
                        <div class="metric-icon mi-amber">&#9888;</div>
                        <div class="metric-data">
                            <div class="metric-value" id="invLowStock">&mdash;</div>
                            <div class="metric-label">Low Stock</div>
                        </div>
                    </div>
                </div>
                <div class="metric-card mc-red">
                    <div class="metric-card-inner">
                        <div class="metric-icon mi-red">&#10060;</div>
                        <div class="metric-data">
                            <div class="metric-value" id="invOutStock">&mdash;</div>
                            <div class="metric-label">Out of Stock</div>
                        </div>
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
                        <button type="button" class="dash-action-btn" onclick="closeAddCoilModal()">Cancel</button>
                        <button type="submit" class="dash-action-btn primary">Add Coil</button>
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
                    <select id="certCoilSelect"></select>
                </div>
                <div class="form-group">
                    <label>Heat Number</label>
                    <input type="text" id="certHeatNum" placeholder="e.g. H-2026-001">
                </div>
                <div class="form-group">
                    <label>Certificate File (PDF/Image)</label>
                    <input type="file" id="certFile" accept=".pdf,.jpg,.png,.gif" style="width:100%;padding:10px;font-size:0.82rem;color:var(--dash-text);background:rgba(255,255,255,0.04);border:1px solid var(--dash-border-subtle);border-radius:var(--dash-radius-xs);">
                </div>
                <div class="form-actions">
                    <button type="button" class="dash-action-btn" onclick="closeAddCertModal()">Cancel</button>
                    <button type="button" class="dash-action-btn primary" onclick="submitCert()">Upload Certificate</button>
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
                    <input type="text" id="editStockCoilName" readonly style="opacity:0.6;">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Current Stock (lbs)</label>
                        <input type="number" id="editStockCurrent" readonly style="opacity:0.6;">
                    </div>
                    <div class="form-group">
                        <label>New Stock (lbs)</label>
                        <input type="number" id="editStockNew" min="0" required>
                    </div>
                </div>
                <div class="form-group">
                    <label>Min Stock (lbs)</label>
                    <input type="number" id="editStockMin" min="0">
                </div>
                <input type="hidden" id="editStockCoilId">
                <div class="form-actions">
                    <button type="button" class="dash-action-btn" onclick="closeEditStockModal()">Cancel</button>
                    <button type="button" class="dash-action-btn primary" onclick="submitStockUpdate()">Update</button>
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
                        <span class="modal-badge" style="background: #2563EB;" id="newJobCodeBadge">Loading...</span>
                    </div>
                </div>
                <button class="close-btn" onclick="closeNewProjectModal()">&times;</button>
            </div>
            <div class="modal-body">
                <form id="newProjectForm" onsubmit="return submitNewProject(event)">
                    <div class="form-group">
                        <label>Job Code (auto-generated)</label>
                        <input type="text" id="npJobCode" readonly style="opacity:0.6; font-weight:700; color:#60A5FA;">
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
                        <div class="form-group" style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
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
                        <button type="button" class="dash-action-btn" onclick="closeNewProjectModal()">Cancel</button>
                        <button type="submit" class="dash-action-btn primary" id="npSubmitBtn">Create Project</button>
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
                <div id="modalPipeline" style="margin-bottom:20px;"></div>
                <div class="info-grid" id="overviewInfo"></div>
                <div style="margin-top: 20px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <button class="dash-action-btn primary" id="openFullPageBtn" onclick="">Open Project</button>
                    <button class="dash-action-btn" id="openShopDrawingsBtn">Shop Drawings</button>
                    <button class="dash-action-btn" id="openWorkOrdersBtn">Work Orders</button>
                    <button class="dash-action-btn" onclick="closeProjectModal()">Close</button>
                    <button class="dash-action-btn" id="deleteProjectBtn" style="color:var(--dash-red);margin-left:auto;" onclick="deleteProject()">&#128465; Delete</button>
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

    // Role groups for section visibility
    var ADMIN_ROLES = ['admin', 'god_mode', 'owner', 'general_manager', 'executive'];
    var SHOP_ROLES  = ['shop_manager', 'foreman', 'shop_foreman', 'shop', 'production_manager'];
    var FAB_ROLES   = ['fabricator', 'welder', 'operator', 'laborer'];
    var QC_ROLES    = ['qa_inspector', 'qa_manager', 'qc_inspector', 'qc_manager', 'qc'];
    var ESTIMATOR_ROLES = ['estimator'];
    var SHIPPING_ROLES  = ['shipping_clerk', 'driver'];
    var PM_ROLES        = ['project_manager'];
    var VIEWER_ROLES    = ['viewer'];

    document.addEventListener('DOMContentLoaded', function() { initializePage(); });

    function initializePage() {
        // Greeting based on time of day
        var hour = new Date().getHours();
        var greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
        var displayName = (USER_NAME && USER_NAME.length > 0 && USER_NAME !== 'local') ? USER_NAME : 'there';
        document.getElementById('heroGreeting').innerHTML = greeting + ', <span class="name-gradient">' + esc(displayName) + '</span>';

        // Date
        var now = new Date();
        var opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        var timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        document.getElementById('heroDate').innerHTML = '&#128197; ' + now.toLocaleDateString('en-US', opts) + ' &middot; ' + timeStr;

        // Role badge styling
        var badge = document.getElementById('roleBadge');
        var roleDisplay = USER_ROLE.replace(/_/g, ' ');
        badge.textContent = roleDisplay;
        if (ADMIN_ROLES.indexOf(USER_ROLE) >= 0) badge.classList.add('role-admin');
        else if (SHOP_ROLES.indexOf(USER_ROLE) >= 0 || FAB_ROLES.indexOf(USER_ROLE) >= 0) badge.classList.add('role-shop');
        else if (QC_ROLES.indexOf(USER_ROLE) >= 0) badge.classList.add('role-qc');
        else if (ESTIMATOR_ROLES.indexOf(USER_ROLE) >= 0) badge.classList.add('role-admin');
        else if (SHIPPING_ROLES.indexOf(USER_ROLE) >= 0) badge.classList.add('role-shop');
        else if (PM_ROLES.indexOf(USER_ROLE) >= 0) badge.classList.add('role-admin');

        // Role-based section visibility
        showRoleSections();

        // Role-based action buttons — hide for shop floor, fab, shipping, viewer
        if (SHOP_ROLES.indexOf(USER_ROLE) >= 0 || FAB_ROLES.indexOf(USER_ROLE) >= 0 ||
            SHIPPING_ROLES.indexOf(USER_ROLE) >= 0 || VIEWER_ROLES.indexOf(USER_ROLE) >= 0) {
            document.getElementById('headerActions').style.display = 'none';
        }

        // Hide prices for shop/fab roles
        if (USER_ROLE === 'shop' || SHOP_ROLES.indexOf(USER_ROLE) >= 0 || FAB_ROLES.indexOf(USER_ROLE) >= 0) {
            document.querySelectorAll('.price').forEach(function(el) { el.classList.add('hidden'); });
        }

        // Hide project/inventory tabs for viewer role
        if (VIEWER_ROLES.indexOf(USER_ROLE) >= 0) {
            var tabSection = document.querySelector('.mc-section-tabs');
            if (tabSection) tabSection.style.display = 'none';
            var projSection = document.getElementById('sectionProjects');
            if (projSection) projSection.style.display = 'none';
            var invSection = document.getElementById('sectionInventory');
            if (invSection) invSection.style.display = 'none';
        }

        loadProjects();
        loadInventoryAlerts();
        loadDashboardStats();
        setupEventListeners();
    }

    function showRoleSections() {
        var role = USER_ROLE;
        // Admin/executive: full dashboard
        if (ADMIN_ROLES.indexOf(role) >= 0) {
            document.getElementById('adminSection').style.display = 'grid';
        }
        // Estimator: project pipeline focus
        if (ESTIMATOR_ROLES.indexOf(role) >= 0) {
            document.getElementById('estimatorSection').style.display = 'grid';
        }
        // Shop manager/foreman: shop floor focus
        if (SHOP_ROLES.indexOf(role) >= 0) {
            document.getElementById('shopSection').style.display = 'grid';
        }
        // Fabricator/welder: my work focus
        if (FAB_ROLES.indexOf(role) >= 0) {
            document.getElementById('fabSection').style.display = 'grid';
        }
        // QA/QC inspector/manager: quality focus
        if (QC_ROLES.indexOf(role) >= 0) {
            document.getElementById('qcSection').style.display = 'grid';
        }
        // Shipping clerk/driver: shipping focus
        if (SHIPPING_ROLES.indexOf(role) >= 0) {
            document.getElementById('shippingSection').style.display = 'grid';
        }
        // Project manager: project overview
        if (PM_ROLES.indexOf(role) >= 0) {
            document.getElementById('pmSection').style.display = 'grid';
        }
        // Viewer: read-only summary
        if (VIEWER_ROLES.indexOf(role) >= 0) {
            document.getElementById('viewerSection').style.display = 'grid';
        }

        // Hide metrics cards that are not relevant per role
        applyMetricsVisibility();
        // Show role-appropriate quick links
        applyQuickLinksVisibility();
    }

    function applyMetricsVisibility() {
        var metricsRow = document.querySelector('.metrics-row');
        if (!metricsRow) return;
        var cards = metricsRow.querySelectorAll('.metric-card');
        // cards[0] = Active Projects, cards[1] = Open Work Orders, cards[2] = Pending QC, cards[3] = Inventory Alerts

        if (VIEWER_ROLES.indexOf(USER_ROLE) >= 0) {
            // Viewer: show only Active Projects
            if (cards[1]) cards[1].style.display = 'none';
            if (cards[2]) cards[2].style.display = 'none';
            if (cards[3]) cards[3].style.display = 'none';
            metricsRow.style.gridTemplateColumns = '1fr';
        } else if (SHIPPING_ROLES.indexOf(USER_ROLE) >= 0) {
            // Shipping: hide QC, show work orders as "Ready to Ship" context
            if (cards[2]) cards[2].style.display = 'none';
            metricsRow.style.gridTemplateColumns = 'repeat(3, 1fr)';
        } else if (FAB_ROLES.indexOf(USER_ROLE) >= 0) {
            // Fabricator: hide inventory alerts
            if (cards[3]) cards[3].style.display = 'none';
            metricsRow.style.gridTemplateColumns = 'repeat(3, 1fr)';
        }
    }

    function applyQuickLinksVisibility() {
        var qlSection = document.querySelector('.quick-links-grid');
        var qlDivider = qlSection ? qlSection.previousElementSibling : null;
        if (!qlSection) return;

        if (FAB_ROLES.indexOf(USER_ROLE) >= 0) {
            // Fabricators: hide quick links — they use My Queue
            qlSection.style.display = 'none';
            if (qlDivider) qlDivider.style.display = 'none';
        } else if (VIEWER_ROLES.indexOf(USER_ROLE) >= 0) {
            // Viewer: hide quick links
            qlSection.style.display = 'none';
            if (qlDivider) qlDivider.style.display = 'none';
        } else if (ESTIMATOR_ROLES.indexOf(USER_ROLE) >= 0) {
            // Estimator: show only SA Estimator, TC Estimator, Customers
            var links = qlSection.querySelectorAll('.quick-link');
            links.forEach(function(link) {
                var href = link.getAttribute('href') || '';
                if (href === '/sa' || href === '/tc' || href === '/customers') {
                    link.style.display = '';
                } else {
                    link.style.display = 'none';
                }
            });
        } else if (SHIPPING_ROLES.indexOf(USER_ROLE) >= 0) {
            // Shipping: show only Work Orders, Shop Floor
            var links = qlSection.querySelectorAll('.quick-link');
            links.forEach(function(link) {
                var href = link.getAttribute('href') || '';
                if (href === '/work-orders' || href === '/shop-floor') {
                    link.style.display = '';
                } else {
                    link.style.display = 'none';
                }
            });
        } else if (SHOP_ROLES.indexOf(USER_ROLE) >= 0) {
            // Shop manager: show Shop Floor, Work Orders
            var links = qlSection.querySelectorAll('.quick-link');
            links.forEach(function(link) {
                var href = link.getAttribute('href') || '';
                if (href === '/shop-floor' || href === '/work-orders') {
                    link.style.display = '';
                } else {
                    link.style.display = 'none';
                }
            });
        }
    }

    function setupEventListeners() {
        ['projectModal', 'newProjectModal', 'addCoilModal', 'addCertModal', 'editStockModal'].forEach(function(id) {
            document.getElementById(id).addEventListener('click', function(e) {
                if (e.target === this) this.classList.remove('show');
            });
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal.show').forEach(function(m) { m.classList.remove('show'); });
            }
        });
    }

    // ── Dashboard Stats API ───────────────────────
    function loadDashboardStats() {
        fetch('/api/dashboard/stats')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (!data.ok) return;

                // Animate metric counters
                animateCounter('activeProjects', data.active_projects || 0);
                animateCounter('openWorkOrders', data.open_work_orders || 0);
                animateCounter('pendingQC', data.pending_qc || 0);
                animateCounter('inventoryAlerts', data.inventory_alerts || 0);

                // Admin sections
                if (ADMIN_ROLES.indexOf(USER_ROLE) >= 0) {
                    renderAdminSections(data);
                }
                // Estimator sections
                if (ESTIMATOR_ROLES.indexOf(USER_ROLE) >= 0) {
                    renderEstimatorSections(data);
                }
                // Shop manager/foreman sections
                if (SHOP_ROLES.indexOf(USER_ROLE) >= 0) {
                    renderShopSections(data);
                }
                // Fabricator/welder sections
                if (FAB_ROLES.indexOf(USER_ROLE) >= 0) {
                    renderFabSections(data);
                }
                // QC sections
                if (QC_ROLES.indexOf(USER_ROLE) >= 0) {
                    renderQCSections(data);
                }
                // Shipping sections
                if (SHIPPING_ROLES.indexOf(USER_ROLE) >= 0) {
                    renderShippingSections(data);
                }
                // Project manager sections
                if (PM_ROLES.indexOf(USER_ROLE) >= 0) {
                    renderPMSections(data);
                }
                // Viewer sections
                if (VIEWER_ROLES.indexOf(USER_ROLE) >= 0) {
                    renderViewerSections(data);
                }
            })
            .catch(function(err) {
                console.error('Dashboard stats error:', err);
                // Fallback: show zeros
                ['activeProjects', 'openWorkOrders', 'pendingQC', 'inventoryAlerts'].forEach(function(id) {
                    document.getElementById(id).textContent = '0';
                });
            });
    }

    function animateCounter(elementId, target) {
        var el = document.getElementById(elementId);
        if (!el) return;
        var current = 0;
        var duration = 600;
        var start = performance.now();

        function step(timestamp) {
            var progress = Math.min((timestamp - start) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
            current = Math.round(eased * target);
            el.textContent = current;
            if (progress < 1) requestAnimationFrame(step);
            else { el.textContent = target; el.classList.add('loaded'); }
        }
        requestAnimationFrame(step);
    }

    // ── Render Admin Sections ─────────────────────
    function renderAdminSections(data) {
        // Business overview
        var el;
        el = document.getElementById('bizActiveProjects');
        if (el) el.textContent = data.active_projects || 0;
        el = document.getElementById('bizTotalWOs');
        if (el) el.textContent = data.open_work_orders || 0;
        el = document.getElementById('bizTeamUtil');
        if (el) el.textContent = (data.active_projects > 0 ? Math.min(95, 60 + data.active_projects * 5) : 0) + '%';
        el = document.getElementById('bizInEngineering');
        if (el) el.textContent = data.in_engineering || 0;
        el = document.getElementById('bizInFabrication');
        if (el) el.textContent = data.in_fabrication || 0;
        el = document.getElementById('bizReadyToShip');
        if (el) el.textContent = data.ready_to_ship || 0;

        // Activity feed
        var feed = document.getElementById('activityFeed');
        var activities = data.recent_activity || [];
        document.getElementById('activityCount').textContent = activities.length;

        if (activities.length === 0) {
            feed.innerHTML = '<div class="no-data">No recent activity</div>';
        } else {
            var html = '';
            activities.forEach(function(a) {
                var dotColor = 'blue';
                var action = a.action || '';
                if (action.indexOf('create') >= 0 || action.indexOf('add') >= 0) dotColor = 'green';
                else if (action.indexOf('delete') >= 0 || action.indexOf('reject') >= 0) dotColor = 'red';
                else if (action.indexOf('update') >= 0 || action.indexOf('edit') >= 0) dotColor = 'amber';
                else if (action.indexOf('approve') >= 0 || action.indexOf('sign') >= 0) dotColor = 'purple';

                var desc = (a.action || 'action').replace(/_/g, ' ');
                var entity = a.entity_id || '';
                var timeAgo = formatTimeAgo(a.timestamp || a.created_at || '');

                html += '<div class="activity-item">';
                html += '<div class="activity-dot ' + dotColor + '"></div>';
                html += '<div><div class="activity-text"><strong>' + esc(a.user || 'system') + '</strong> ' + esc(desc);
                if (entity) html += ' <strong>' + esc(entity) + '</strong>';
                html += '</div>';
                html += '<div class="activity-time">' + timeAgo + '</div>';
                html += '</div></div>';
            });
            feed.innerHTML = html;
        }

        // System health
        var usersOnline = document.getElementById('sysUsersOnline');
        if (usersOnline) usersOnline.textContent = data.users_online || 1;
        var pending = document.getElementById('sysPendingActions');
        if (pending) pending.textContent = (data.pending_qc || 0) + (data.inventory_alerts || 0);
    }

    // ── Render Shop Sections ──────────────────────
    function renderShopSections(data) {
        var queue = document.getElementById('shopQueue');
        var woItems = data.work_order_items || [];
        document.getElementById('queueCount').textContent = woItems.length;

        if (woItems.length === 0) {
            queue.innerHTML = '<div class="no-data">No items in your queue. Check work orders for assignments.</div>';
        } else {
            var html = '';
            woItems.slice(0, 8).forEach(function(item) {
                var priority = item.priority || 'normal';
                var status = item.status || 'pending';
                html += '<div class="queue-item" onclick="window.location.href=\'/work-orders\'">';
                html += '<div class="queue-priority ' + priority + '"></div>';
                html += '<div class="queue-info">';
                html += '<div class="queue-title">' + esc(item.description || item.name || 'Work Item') + '</div>';
                html += '<div class="queue-subtitle">' + esc(item.job_code || '') + ' &middot; Qty: ' + (item.qty || 1) + '</div>';
                html += '</div>';
                html += '<span class="queue-status ' + status + '">' + status + '</span>';
                html += '</div>';
            });
            queue.innerHTML = html;
        }

        // Floor active
        var floor = document.getElementById('floorActive');
        var activeWOs = data.active_work_orders || [];
        if (activeWOs.length === 0) {
            floor.innerHTML = '<div class="no-data">No active work orders on the floor.</div>';
        } else {
            var html2 = '';
            activeWOs.slice(0, 6).forEach(function(wo) {
                html2 += '<div class="queue-item" onclick="window.location.href=\'/work-orders\'">';
                html2 += '<div class="queue-priority medium"></div>';
                html2 += '<div class="queue-info">';
                html2 += '<div class="queue-title">' + esc(wo.wo_id || wo.id || 'Work Order') + '</div>';
                html2 += '<div class="queue-subtitle">' + esc(wo.job_code || '') + ' &middot; ' + (wo.item_count || 0) + ' items</div>';
                html2 += '</div>';
                html2 += '<span class="queue-status ' + (wo.status || 'active') + '">' + (wo.status || 'active') + '</span>';
                html2 += '</div>';
            });
            floor.innerHTML = html2;
        }

        // Production progress
        var prog = document.getElementById('productionProgress');
        var stages = data.stage_counts || {};
        var total = data.active_projects || 1;
        if (total === 0) total = 1;
        var progHtml = '';

        var stageMap = [
            { key: 'engineering', label: 'Engineering', color: 'purple' },
            { key: 'fabrication', label: 'Fabrication', color: 'amber' },
            { key: 'shipping', label: 'Shipping', color: 'blue' },
            { key: 'install', label: 'Installation', color: 'green' }
        ];

        stageMap.forEach(function(s) {
            var count = stages[s.key] || 0;
            var pct = Math.round((count / total) * 100);
            progHtml += '<div class="progress-item">';
            progHtml += '<div class="progress-header"><span class="progress-label">' + s.label + '</span><span class="progress-pct">' + count + ' projects (' + pct + '%)</span></div>';
            progHtml += '<div class="progress-track"><div class="progress-fill ' + s.color + '" style="width:' + pct + '%;"></div></div>';
            progHtml += '</div>';
        });
        prog.innerHTML = progHtml;
    }

    // ── Render QC Sections ────────────────────────
    function renderQCSections(data) {
        var inspQueue = document.getElementById('inspectionQueue');
        var qcItems = data.qc_items || [];
        var pendingInsp = qcItems.filter(function(i) { return i.status === 'pending' || i.status === 'in_progress'; });
        document.getElementById('inspectionCount').textContent = pendingInsp.length;

        if (pendingInsp.length === 0) {
            inspQueue.innerHTML = '<div class="no-data">No pending inspections. All clear!</div>';
        } else {
            var html = '';
            pendingInsp.slice(0, 8).forEach(function(item) {
                html += '<div class="qc-item" onclick="window.location.href=\'/qc\'">';
                html += '<span class="qc-type-badge inspection">Inspect</span>';
                html += '<div class="queue-info">';
                html += '<div class="queue-title">' + esc(item.component || item.description || 'Inspection') + '</div>';
                html += '<div class="queue-subtitle">' + esc(item.job_code || '') + '</div>';
                html += '</div>';
                html += '</div>';
            });
            inspQueue.innerHTML = html;
        }

        // Open NCRs
        var ncrEl = document.getElementById('openNCRs');
        var ncrs = data.open_ncrs || [];
        document.getElementById('ncrCount').textContent = ncrs.length;

        if (ncrs.length === 0) {
            ncrEl.innerHTML = '<div class="no-data">No open NCRs. Great work!</div>';
        } else {
            var ncrHtml = '';
            ncrs.slice(0, 6).forEach(function(ncr) {
                ncrHtml += '<div class="qc-item">';
                ncrHtml += '<span class="qc-type-badge ncr">NCR</span>';
                ncrHtml += '<div class="queue-info">';
                ncrHtml += '<div class="queue-title">' + esc(ncr.ncr_number || ncr.id || 'NCR') + '</div>';
                ncrHtml += '<div class="queue-subtitle">' + esc(ncr.description || ncr.defect_description || '') + '</div>';
                ncrHtml += '</div>';
                ncrHtml += '</div>';
            });
            ncrEl.innerHTML = ncrHtml;
        }

        // Recent sign-offs
        var signoffsEl = document.getElementById('recentSignoffs');
        var signoffs = data.recent_signoffs || [];
        if (signoffs.length === 0) {
            signoffsEl.innerHTML = '<div class="no-data">No recent sign-offs.</div>';
        } else {
            var soHtml = '';
            signoffs.slice(0, 6).forEach(function(so) {
                soHtml += '<div class="qc-item">';
                soHtml += '<span class="qc-type-badge signoff">Signed</span>';
                soHtml += '<div class="queue-info">';
                soHtml += '<div class="queue-title">' + esc(so.component || so.description || 'Sign-off') + '</div>';
                soHtml += '<div class="queue-subtitle">' + esc(so.inspector || so.signed_by || '') + ' &middot; ' + esc(so.date || '') + '</div>';
                soHtml += '</div>';
                soHtml += '</div>';
            });
            signoffsEl.innerHTML = soHtml;
        }

        // Inspection stats
        var totalInspected = signoffs.length + pendingInsp.length;
        var passRate = totalInspected > 0 ? Math.round((signoffs.length / totalInspected) * 100) : 0;
        var tiEl = document.getElementById('qcTotalInspected');
        if (tiEl) tiEl.textContent = totalInspected;
        var prEl = document.getElementById('qcPassRate');
        if (prEl) prEl.textContent = passRate + '%';
        // Calibration due — fetch from calibration API
        var calEl = document.getElementById('qcCalibDue');
        if (calEl) {
            fetch('/api/qc/calibration')
                .then(function(r) { return r.json(); })
                .then(function(cData) {
                    var records = cData.records || cData.calibration_records || [];
                    var dueCount = 0;
                    var now = new Date();
                    var thirtyDays = 30 * 24 * 60 * 60 * 1000;
                    records.forEach(function(rec) {
                        var nextCal = rec.next_calibration || rec.next_due || '';
                        if (nextCal) {
                            var d = new Date(nextCal);
                            if (d - now < thirtyDays) dueCount++;
                        }
                    });
                    calEl.textContent = dueCount;
                })
                .catch(function() { calEl.textContent = '0'; });
        }
    }

    // ── Render Estimator Sections ─────────────────
    function renderEstimatorSections(data) {
        // Active projects
        var el = document.getElementById('estActiveProjects');
        var stages = data.stage_counts || {};
        var activeCount = data.active_projects || 0;
        document.getElementById('estProjectCount').textContent = activeCount;

        if (activeCount === 0) {
            el.innerHTML = '<div class="no-data">No active projects. Start a new quote!</div>';
        } else {
            var html = '';
            var stageList = [
                { key: 'quote', label: 'Quote', color: 'blue' },
                { key: 'contract', label: 'Contract', color: 'blue' },
                { key: 'engineering', label: 'Engineering', color: 'purple' },
                { key: 'fabrication', label: 'Fabrication', color: 'amber' },
                { key: 'shipping', label: 'Shipping', color: 'green' }
            ];
            stageList.forEach(function(s) {
                var count = stages[s.key] || 0;
                if (count > 0) {
                    var pct = Math.round((count / activeCount) * 100);
                    html += '<div class="progress-item">';
                    html += '<div class="progress-header"><span class="progress-label">' + s.label + '</span><span class="progress-pct">' + count + ' (' + pct + '%)</span></div>';
                    html += '<div class="progress-track"><div class="progress-fill ' + s.color + '" style="width:' + pct + '%;"></div></div>';
                    html += '</div>';
                }
            });
            if (!html) html = '<div class="no-data">' + activeCount + ' active projects across stages</div>';
            el.innerHTML = html;
        }

        // Quotes pending
        var quotesEl = document.getElementById('estQuotesPending');
        var quoteCount = (stages['quote'] || 0) + (stages['contract'] || 0);
        document.getElementById('estQuoteCount').textContent = quoteCount;
        if (quoteCount === 0) {
            quotesEl.innerHTML = '<div class="no-data">No quotes pending. Pipeline is clear.</div>';
        } else {
            quotesEl.innerHTML = '<div class="health-grid">' +
                '<div class="health-item"><div class="health-value">' + (stages['quote'] || 0) + '</div><div class="health-label">In Quoting</div></div>' +
                '<div class="health-item"><div class="health-value">' + (stages['contract'] || 0) + '</div><div class="health-label">Awaiting Contract</div></div>' +
                '<div class="health-item"><div class="health-value">' + activeCount + '</div><div class="health-label">Total Active</div></div>' +
                '</div>';
        }

        // Activity feed (reuse admin's logic)
        var feed = document.getElementById('estActivityFeed');
        var activities = data.recent_activity || [];
        document.getElementById('estActivityCount').textContent = activities.length;
        if (activities.length === 0) {
            feed.innerHTML = '<div class="no-data">No recent activity</div>';
        } else {
            var ahtml = '';
            activities.slice(0, 10).forEach(function(a) {
                var dotColor = 'blue';
                var action = a.action || '';
                if (action.indexOf('create') >= 0 || action.indexOf('add') >= 0) dotColor = 'green';
                else if (action.indexOf('delete') >= 0) dotColor = 'red';
                else if (action.indexOf('update') >= 0) dotColor = 'amber';
                var desc = (a.action || 'action').replace(/_/g, ' ');
                var entity = a.entity_id || '';
                var timeAgo = formatTimeAgo(a.timestamp || a.created_at || '');
                ahtml += '<div class="activity-item">';
                ahtml += '<div class="activity-dot ' + dotColor + '"></div>';
                ahtml += '<div><div class="activity-text"><strong>' + esc(a.user || 'system') + '</strong> ' + esc(desc);
                if (entity) ahtml += ' <strong>' + esc(entity) + '</strong>';
                ahtml += '</div><div class="activity-time">' + timeAgo + '</div></div></div>';
            });
            feed.innerHTML = ahtml;
        }
    }

    // ── Render Fabricator/Welder Sections ─────────
    function renderFabSections(data) {
        // My Queue
        var queue = document.getElementById('fabQueue');
        var woItems = data.work_order_items || [];
        document.getElementById('fabQueueCount').textContent = woItems.length;

        if (woItems.length === 0) {
            queue.innerHTML = '<div class="no-data">No items in your queue. Check with your foreman.</div>';
        } else {
            var html = '';
            woItems.slice(0, 10).forEach(function(item) {
                var priority = item.priority || 'normal';
                var status = item.status || 'pending';
                html += '<div class="queue-item" onclick="window.location.href=\'/my-queue\'">';
                html += '<div class="queue-priority ' + priority + '"></div>';
                html += '<div class="queue-info">';
                html += '<div class="queue-title">' + esc(item.description || item.name || 'Work Item') + '</div>';
                html += '<div class="queue-subtitle">' + esc(item.job_code || '') + ' &middot; Qty: ' + (item.qty || 1) + '</div>';
                html += '</div>';
                html += '<span class="queue-status ' + status + '">' + status + '</span>';
                html += '</div>';
            });
            queue.innerHTML = html;
        }

        // Recent completions
        var compEl = document.getElementById('fabCompletions');
        var signoffs = data.recent_signoffs || [];
        if (signoffs.length === 0) {
            compEl.innerHTML = '<div class="no-data">No recent completions yet. Keep going!</div>';
        } else {
            var chtml = '';
            signoffs.slice(0, 6).forEach(function(so) {
                chtml += '<div class="qc-item">';
                chtml += '<span class="qc-type-badge signoff">Done</span>';
                chtml += '<div class="queue-info">';
                chtml += '<div class="queue-title">' + esc(so.component || so.description || 'Completed') + '</div>';
                chtml += '<div class="queue-subtitle">' + esc(so.date || '') + '</div>';
                chtml += '</div></div>';
            });
            compEl.innerHTML = chtml;
        }

        // Gamification stats — fetch from dedicated API
        fetch('/api/gamification/profile')
            .then(function(r) { return r.json(); })
            .then(function(gRes) {
                var gamData = gRes.profile || gRes || {};
                var xpEl = document.getElementById('fabXP');
                if (xpEl) xpEl.textContent = gamData.xp || 0;
                var streakEl = document.getElementById('fabStreak');
                if (streakEl) streakEl.textContent = gamData.streak || 0;
                var achEl = document.getElementById('fabAchievements');
                if (achEl) achEl.textContent = (gamData.achievements || []).length || 0;
                var lvlEl = document.getElementById('fabLevel');
                if (lvlEl) lvlEl.textContent = gamData.level || Math.max(1, Math.floor((gamData.xp || 0) / 500) + 1);
            })
            .catch(function() {
                // Fallback: zeros already shown
            });
    }

    // ── Render Shipping Sections ──────────────────
    function renderShippingSections(data) {
        var readyEl = document.getElementById('shipReady');
        var readyCount = data.ready_to_ship || 0;
        document.getElementById('shipReadyCount').textContent = readyCount;

        if (readyCount === 0) {
            readyEl.innerHTML = '<div class="no-data">No items ready to ship.</div>';
        } else {
            readyEl.innerHTML = '<div class="health-grid">' +
                '<div class="health-item"><div class="health-value">' + readyCount + '</div><div class="health-label">Ready to Ship</div></div>' +
                '<div class="health-item"><div class="health-value">' + (data.in_fabrication || 0) + '</div><div class="health-label">In Fabrication</div></div>' +
                '<div class="health-item"><div class="health-value">' + (data.active_projects || 0) + '</div><div class="health-label">Active Projects</div></div>' +
                '</div>';
        }

        // Today's loads — from active work orders that are in shipping stage
        var todayEl = document.getElementById('shipToday');
        var activeWOs = data.active_work_orders || [];
        var shippingWOs = activeWOs.filter(function(wo) {
            return (wo.status || '').indexOf('ship') >= 0 || (wo.stage || '').indexOf('ship') >= 0;
        });
        document.getElementById('shipTodayCount').textContent = shippingWOs.length;

        if (shippingWOs.length === 0) {
            todayEl.innerHTML = '<div class="no-data">No loads scheduled. Check shipping hub for updates.</div>';
        } else {
            var shtml = '';
            shippingWOs.slice(0, 6).forEach(function(wo) {
                shtml += '<div class="queue-item" onclick="window.location.href=\'/shipping\'">';
                shtml += '<div class="queue-priority medium"></div>';
                shtml += '<div class="queue-info">';
                shtml += '<div class="queue-title">' + esc(wo.wo_id || wo.id || 'Load') + '</div>';
                shtml += '<div class="queue-subtitle">' + esc(wo.job_code || '') + '</div>';
                shtml += '</div>';
                shtml += '<span class="queue-status active">loading</span>';
                shtml += '</div>';
            });
            todayEl.innerHTML = shtml;
        }

        // Recent shipments
        var recentEl = document.getElementById('shipRecent');
        var signoffs = data.recent_signoffs || [];
        if (signoffs.length === 0) {
            recentEl.innerHTML = '<div class="no-data">No recent shipments recorded.</div>';
        } else {
            var rhtml = '';
            signoffs.slice(0, 6).forEach(function(so) {
                rhtml += '<div class="queue-item">';
                rhtml += '<div class="queue-priority normal"></div>';
                rhtml += '<div class="queue-info">';
                rhtml += '<div class="queue-title">' + esc(so.component || so.description || 'Shipment') + '</div>';
                rhtml += '<div class="queue-subtitle">' + esc(so.date || '') + '</div>';
                rhtml += '</div>';
                rhtml += '<span class="queue-status done">shipped</span>';
                rhtml += '</div>';
            });
            recentEl.innerHTML = rhtml;
        }
    }

    // ── Render Project Manager Sections ───────────
    function renderPMSections(data) {
        var projEl = document.getElementById('pmActiveProjects');
        var activeCount = data.active_projects || 0;
        var stages = data.stage_counts || {};
        document.getElementById('pmProjectCount').textContent = activeCount;

        if (activeCount === 0) {
            projEl.innerHTML = '<div class="no-data">No active projects.</div>';
        } else {
            var html = '';
            var stageList = [
                { key: 'quote', label: 'Quote', color: 'blue' },
                { key: 'contract', label: 'Contract', color: 'blue' },
                { key: 'engineering', label: 'Engineering', color: 'purple' },
                { key: 'shop-drawings', label: 'Shop Drawings', color: 'purple' },
                { key: 'fabrication', label: 'Fabrication', color: 'amber' },
                { key: 'shipping', label: 'Shipping', color: 'green' },
                { key: 'install', label: 'Installation', color: 'green' }
            ];
            stageList.forEach(function(s) {
                var count = stages[s.key] || 0;
                var pct = Math.round((count / Math.max(activeCount, 1)) * 100);
                html += '<div class="progress-item">';
                html += '<div class="progress-header"><span class="progress-label">' + s.label + '</span><span class="progress-pct">' + count + ' projects</span></div>';
                html += '<div class="progress-track"><div class="progress-fill ' + s.color + '" style="width:' + pct + '%;"></div></div>';
                html += '</div>';
            });
            projEl.innerHTML = html;
        }

        // Upcoming milestones
        var mileEl = document.getElementById('pmMilestones');
        var milestones = [];
        // Build milestones from stage transitions
        if (stages['fabrication'] > 0) milestones.push({ text: stages['fabrication'] + ' project(s) in fabrication', icon: 'amber' });
        if (stages['shipping'] > 0) milestones.push({ text: stages['shipping'] + ' project(s) ready to ship', icon: 'green' });
        if (stages['engineering'] > 0) milestones.push({ text: stages['engineering'] + ' project(s) in engineering', icon: 'purple' });
        if ((data.pending_qc || 0) > 0) milestones.push({ text: data.pending_qc + ' QC items pending', icon: 'blue' });

        if (milestones.length === 0) {
            mileEl.innerHTML = '<div class="no-data">No upcoming milestones.</div>';
        } else {
            var mhtml = '';
            milestones.forEach(function(m) {
                mhtml += '<div class="activity-item">';
                mhtml += '<div class="activity-dot ' + m.icon + '"></div>';
                mhtml += '<div><div class="activity-text">' + esc(m.text) + '</div></div>';
                mhtml += '</div>';
            });
            mileEl.innerHTML = mhtml;
        }

        // Customer activity (reuse recent activity)
        var custEl = document.getElementById('pmCustomerActivity');
        var activities = data.recent_activity || [];
        if (activities.length === 0) {
            custEl.innerHTML = '<div class="no-data">No recent customer activity.</div>';
        } else {
            var cahtml = '';
            activities.slice(0, 8).forEach(function(a) {
                var dotColor = 'blue';
                var action = a.action || '';
                if (action.indexOf('create') >= 0) dotColor = 'green';
                else if (action.indexOf('update') >= 0) dotColor = 'amber';
                var desc = (a.action || 'action').replace(/_/g, ' ');
                cahtml += '<div class="activity-item">';
                cahtml += '<div class="activity-dot ' + dotColor + '"></div>';
                cahtml += '<div><div class="activity-text"><strong>' + esc(a.user || 'system') + '</strong> ' + esc(desc);
                if (a.entity_id) cahtml += ' <strong>' + esc(a.entity_id) + '</strong>';
                cahtml += '</div><div class="activity-time">' + formatTimeAgo(a.timestamp || a.created_at || '') + '</div></div></div>';
            });
            custEl.innerHTML = cahtml;
        }
    }

    // ── Render Viewer Sections ────────────────────
    function renderViewerSections(data) {
        var el;
        el = document.getElementById('viewerActiveProjects');
        if (el) el.textContent = data.active_projects || 0;
        el = document.getElementById('viewerTotalWOs');
        if (el) el.textContent = data.open_work_orders || 0;
        el = document.getElementById('viewerInFab');
        if (el) el.textContent = data.in_fabrication || 0;
    }

    // ── Time Formatting ───────────────────────────
    function formatTimeAgo(dateStr) {
        if (!dateStr) return '';
        try {
            var d = new Date(dateStr);
            var now = new Date();
            var diff = Math.floor((now - d) / 1000);
            if (diff < 60) return 'just now';
            if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
            if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
            if (diff < 604800) return Math.floor(diff / 86400) + 'd ago';
            return d.toLocaleDateString();
        } catch(e) { return dateStr; }
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
        // These are fallback local stats; the API stats are primary
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
            container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">&#128640;</div><div class="empty-state-title">No projects yet</div><p style="color:var(--dash-text-muted);">Create your first project to get started!</p></div>';
            return;
        }

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

            row.innerHTML = '<td><strong style="color:#60A5FA;">' + esc(project.job_code) + '</strong></td>'
                + '<td>' + esc(project.project_name) + '</td>'
                + '<td>' + esc(project.customer_name) + '</td>'
                + '<td><span class="stage-badge stage-' + project.stage + '">' + stageLabel + '</span></td>'
                + '<td class="price">' + (project.doc_count || 0) + ' docs</td>'
                + '<td>' + updated + '</td>'
                + '<td><div style="display:flex;align-items:center;gap:8px;"><div style="flex:1;height:4px;background:rgba(255,255,255,0.05);border-radius:2px;overflow:hidden;"><div style="height:100%;width:' + pct + '%;background:#3B82F6;border-radius:2px;"></div></div><span style="font-size:0.7rem;font-weight:700;color:var(--dash-text-dim);">' + pct + '%</span></div></td>';

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
        stageBadge.style.backgroundColor = '#2563EB';
        stageBadge.textContent = (STAGE_LABELS[project.stage] || project.stage).toUpperCase();
        badgeGroup.appendChild(stageBadge);

        if (project.n_versions > 0) {
            var vBadge = document.createElement('span');
            vBadge.className = 'modal-badge';
            vBadge.style.backgroundColor = '#F59E0B';
            vBadge.textContent = 'v' + project.n_versions;
            badgeGroup.appendChild(vBadge);
        }

        document.getElementById('modalPipeline').innerHTML = buildPipelineDots(project.stage, false);

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

    function deleteProject() {
        if (!currentProject) return;
        var jc = currentProject.job_code;
        var name = currentProject.project_name || 'Untitled';
        if (!confirm('DELETE PROJECT\n\n"' + jc + ' — ' + name + '"\n\nThis will permanently delete ALL project data including:\n- Estimates & revisions\n- Shop drawings\n- Work orders\n- Documents\n\nThis cannot be undone. Are you sure?')) return;
        if (!confirm('FINAL WARNING: Click OK to proceed with deleting ' + jc)) return;

        fetch('/api/project/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_code: jc, confirm: true }),
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.ok) {
                closeProjectModal();
                allProjects = allProjects.filter(function(p) { return p.job_code !== jc; });
                filteredProjects = filteredProjects.filter(function(p) { return p.job_code !== jc; });
                updateStats();
                renderProjects();
                alert('Project ' + jc + ' deleted successfully.');
            } else {
                alert('Delete failed: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(function(err) {
            alert('Delete failed: ' + err.message);
        });
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
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;padding:2rem;color:var(--dash-text-muted);">No coils in inventory. Click "+ Add Coil" to get started.</td></tr>';
            return;
        }

        ids.forEach(function(id) {
            var c = inventoryData[id];
            var avail = (c.stock_lbs || 0) - (c.committed_lbs || 0);
            var minStock = c.min_stock_lbs || 2000;
            var statusClass, statusText, statusColor;

            if (avail <= 0) { statusText = 'OUT'; statusColor = 'background:rgba(239,68,68,0.15);color:#F87171;'; }
            else if (avail < minStock) { statusText = 'LOW'; statusColor = 'background:rgba(245,158,11,0.15);color:#FBBF24;'; }
            else { statusText = 'OK'; statusColor = 'background:rgba(16,185,129,0.15);color:#34D399;'; }

            var row = document.createElement('tr');
            row.style.cursor = 'pointer';
            row.onclick = function(e) {
                if (e.target.tagName === 'BUTTON') return;
                window.location.href = '/coil/' + encodeURIComponent(id);
            };

            row.innerHTML = '<td><strong style="color:#60A5FA;">' + esc(id) + '</strong></td>'
                + '<td>' + esc(c.description || c.name || '') + '</td>'
                + '<td>' + esc(c.gauge || '') + '</td>'
                + '<td>' + esc(c.width || '') + '</td>'
                + '<td>' + esc(c.color || '') + '</td>'
                + '<td style="font-weight:700;">' + Number(c.stock_lbs || 0).toLocaleString() + '</td>'
                + '<td>' + Number(minStock).toLocaleString() + '</td>'
                + '<td><span style="display:inline-flex;align-items:center;padding:3px 10px;border-radius:999px;font-size:0.7rem;font-weight:600;' + statusColor + '">' + statusText + '</span></td>'
                + '<td>'
                + '<button class="dash-action-btn" style="padding:4px 10px;font-size:0.7rem;" onclick="event.stopPropagation();openEditStock(\'' + esc(id) + '\')">Edit</button> '
                + '<button class="dash-action-btn" style="padding:4px 10px;font-size:0.7rem;color:var(--dash-red);" onclick="event.stopPropagation();deleteCoil(\'' + esc(id) + '\')">Delete</button>'
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
