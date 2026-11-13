"""
Script to apply Modern Clean SaaS Light Theme (Untitled UI style) to AQMS Dashboard:
- Matches user reference image:
  * White sidebar (#FFFFFF) with clean border (#E2E8F0)
  * Active menu tab: Solid Royal Indigo/Purple (#5E5CE6 / #6366F1), white text, rounded 12px, soft purple shadow
  * Body background: Soft neutral canvas (#F8F9FC)
  * Navbar: Crisp white (#FFFFFF) with subtle border (#E2E8F0)
  * Hero Banner: Vibrant violet-indigo mesh gradient bar behind KPI cards
  * KPI Cards: Clean floating white cards (#FFFFFF) with subtle drop shadow (0 4px 20px rgba(0,0,0,0.06)), rounded 16px, dark typography (#0F172A), pastel icon badges, clean colored border-top/accent
  * Chart Cards: Crisp white surfaces (#FFFFFF), 1px solid #E2E8F0, soft modern elevation
  * Leaflet Map: Modern CartoDB Positron / Light Gray clean vector aesthetic
  * Tables & Heatmaps: Clean light backgrounds, refined borders, legible high-contrast text
  * Tooltips: Dark sleek popovers with white text
  * Chart.js: Light-mode gridlines (rgba(0,0,0,0.05)), dark slate labels (#64748B)
"""

import re

BASE = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main"
CSS_PATH = BASE + r"\assets\css\style.css"
JS_PATH  = BASE + r"\assets\js\dashboard.js"
HTML_PATH = BASE + r"\index.html"

# ==============================================================================
# 1. GENERATE MODERN CLEAN SAAS LIGHT STYLE.CSS
# ==============================================================================

LIGHT_CSS = """/* ============================================================
   AQMS DASHBOARD - Clean Modern SaaS Theme (Untitled UI Aesthetic)
   Indonesia Air Quality Monitoring System Dashboard
   ============================================================ */

/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── CSS Custom Properties ── */
:root {
  /* Background & Surface */
  --bg-primary: #f8f9fc;
  --bg-secondary: #ffffff;
  --bg-card: #ffffff;
  --bg-card-hover: #ffffff;
  --bg-surface: #f1f5f9;
  --border-subtle: #e2e8f0;
  --border-medium: #cbd5e1;

  /* Text Colors */
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #64748b;
  --text-accent: #5e5ce6;

  /* Brand Accents */
  --accent-primary: #5e5ce6;
  --accent-primary-hover: #4f46e5;
  --accent-primary-glow: rgba(94, 92, 230, 0.25);
  --accent-secondary: #8b5cf6;
  --accent-success: #10b981;
  --accent-warning: #f59e0b;
  --accent-danger: #ef4444;

  /* Air Quality Colors */
  --aqi-good: #10b981;
  --aqi-moderate: #eab308;
  --aqi-unhealthy-sensitive: #f97316;
  --aqi-unhealthy: #ef4444;
  --aqi-very-unhealthy: #a855f7;
  --aqi-hazardous: #7e0023;

  /* Status Colors */
  --status-ok: #10b981;
  --status-caution: #f59e0b;
  --status-excluded: #ef4444;

  /* Surface Cards */
  --glass-bg: #ffffff;
  --glass-border: #e2e8f0;
  --glass-blur: 0px;

  /* Spacing */
  --gap-sm: 8px;
  --gap-md: 16px;
  --gap-lg: 24px;
  --gap-xl: 32px;

  /* Border Radius */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;

  /* Transitions */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 220ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
  --shadow-card: 0 4px 16px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.03);
  --shadow-card-hover: 0 12px 28px -4px rgba(15, 23, 42, 0.08), 0 4px 12px -2px rgba(15, 23, 42, 0.04);
  --shadow-glow: 0 0 24px rgba(94, 92, 230, 0.18);
}

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html {
  font-size: 14px;
  scroll-behavior: smooth;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
  overflow-x: clip;
  line-height: 1.6;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* ================================================================
   NAVBAR (Clean Header)
   ================================================================ */
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--gap-lg);
  height: 64px;
  background: #ffffff;
  border-bottom: 1px solid var(--border-subtle);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.navbar-logo {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, #5e5ce6, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 16px;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(94, 92, 230, 0.25);
  cursor: pointer;
  user-select: none;
  transition: all var(--transition-base);
}

.navbar-logo:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(94, 92, 230, 0.35);
}

.navbar-logo.collapsed {
  opacity: 0.8;
  filter: grayscale(0.2);
}

.navbar-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.3px;
}

.navbar-subtitle {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-weight: 500;
  letter-spacing: 0.4px;
  text-transform: uppercase;
}

.navbar-controls {
  display: flex;
  align-items: center;
  gap: var(--gap-md);
}

/* Filter Controls */
.filter-group {
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
}

.filter-label {
  font-size: 0.74rem;
  color: var(--text-secondary);
  font-weight: 600;
  letter-spacing: 0.2px;
}

.filter-select {
  background: #f8f9fc;
  border: 1px solid var(--border-subtle);
  color: #1e293b;
  padding: 7px 12px;
  border-radius: var(--radius-sm);
  font-family: inherit;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  outline: none;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2'%3E%3Cpolyline points='6,9 12,15 18,9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 30px;
}

.filter-select:hover {
  border-color: var(--border-medium);
  background-color: #ffffff;
}

.filter-select:focus {
  border-color: var(--accent-primary);
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(94, 92, 230, 0.12);
}

/* ================================================================
   SIDEBAR & TAB NAVIGATION (Vertical Clean Layout)
   ================================================================ */
.dashboard-body {
  display: flex;
  min-height: calc(100vh - 64px);
  width: 100%;
  position: relative;
  overflow-x: clip;
}

.sidebar-nav {
  width: 320px;
  min-width: 320px;
  flex-shrink: 0;
  background: #ffffff;
  border-right: 1px solid var(--border-subtle);
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: -webkit-sticky;
  position: sticky;
  top: 64px;
  height: calc(100vh - 64px);
  overflow-y: auto;
  align-self: flex-start;
  z-index: 40;
  transition: margin-left 0.35s cubic-bezier(0.4, 0, 0.2, 1), transform 0.35s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.25s ease;
  will-change: margin-left, transform;
}

.dashboard-body.sidebar-collapsed .sidebar-nav {
  margin-left: -320px;
  transform: translateX(-100%);
  opacity: 0;
  pointer-events: none;
}

.sidebar-section-title {
  font-size: 0.68rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding: 0 8px;
}

.tab-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0;
  background: transparent;
  border: none;
  width: 100%;
}

.tab-btn {
  position: relative;
  padding: 12px 14px;
  font-family: inherit;
  border: 1px solid transparent;
  background: transparent;
  border-radius: var(--radius-md);
  color: #475569;
  cursor: pointer;
  transition: all var(--transition-base);
  white-space: normal;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  text-align: left;
  width: 100%;
}

.tab-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

/* Active Menu Tab (Solid Indigo / Purple Modern SaaS Accent) */
.tab-btn.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 6px 18px rgba(94, 92, 230, 0.25);
}

.tab-btn.active::after {
  display: none;
}

.tab-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 7px;
  background: #f1f5f9;
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  flex-shrink: 0;
  margin-top: 1px;
  transition: all var(--transition-base);
}

.tab-btn.active .tab-number {
  background: rgba(255, 255, 255, 0.22);
  color: #ffffff;
}

.tab-btn-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.tab-title {
  font-size: 0.82rem;
  font-weight: 600;
  line-height: 1.35;
  color: inherit;
}

.tab-desc {
  font-size: 0.68rem;
  color: #64748b;
  line-height: 1.25;
}

.tab-btn.active .tab-desc {
  color: rgba(255, 255, 255, 0.85);
}

/* Sidebar Footer / Subscription Box Style */
.sidebar-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--border-subtle);
}

.sidebar-status-box {
  background: #f8f9fc;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 12px 14px;
}

.sidebar-status-title {
  font-size: 0.65rem;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.sidebar-status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #0f172a;
}

.status-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
  flex-shrink: 0;
}

.sidebar-status-desc {
  font-size: 0.68rem;
  color: #d97706;
  font-weight: 500;
  margin-top: 4px;
}

.sidebar-brand-credit {
  font-size: 0.72rem;
  color: #94a3b8;
  line-height: 1.35;
  padding: 0 4px;
}

/* ================================================================
   MAIN CONTENT & HERO BANNER
   ================================================================ */
.main-content {
  flex: 1;
  min-width: 0;
  padding: var(--gap-lg);
  position: relative;
  z-index: 1;
  overflow-x: hidden;
  background: var(--bg-primary);
}

.tab-panel {
  display: none;
  animation: fadeIn 0.35s ease;
}

.tab-panel.active { display: block; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ================================================================
   KPI HERO SECTION (Top Accent Gradient Banner & Floating Cards)
   ================================================================ */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr) !important;
  gap: 16px;
  margin-bottom: var(--gap-lg);
  position: relative;
  padding: 24px;
  border-radius: var(--radius-xl);
  background: linear-gradient(135deg, #38bdf8 0%, #6366f1 50%, #8b5cf6 100%);
  box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.25);
}

.kpi-card {
  background: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.8) !important;
  border-radius: var(--radius-lg);
  padding: 16px 18px;
  position: relative;
  overflow: hidden;
  transition: all var(--transition-base);
  min-width: 0;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08) !important;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.12) !important;
}

.kpi-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.kpi-header-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 999px;
  letter-spacing: 0.2px;
}

.kpi-value {
  font-size: 1.55rem;
  font-weight: 800;
  line-height: 1.15;
  margin-bottom: 4px;
  font-variant-numeric: tabular-nums;
  font-family: 'JetBrains Mono', monospace;
  color: #0f172a !important;
}

.kpi-value .unit {
  font-size: 0.75rem;
  font-weight: 500;
  color: #64748b;
  margin-left: 2px;
}

.kpi-label {
  font-size: 0.72rem;
  font-weight: 500;
  line-height: 1.3;
  color: #64748b;
}

/* KPI Status Badges & Borders (Pastel Clean Light Mode Badges) */
.kpi-card.index-green {
  border-top: 4px solid #10b981 !important;
}
.kpi-card.index-green .kpi-trend {
  background: #ecfdf5 !important;
  color: #059669 !important;
}

.kpi-card.index-yellow {
  border-top: 4px solid #eab308 !important;
}
.kpi-card.index-yellow .kpi-trend {
  background: #fefce8 !important;
  color: #ca8a04 !important;
}

.kpi-card.index-orange {
  border-top: 4px solid #f97316 !important;
}
.kpi-card.index-orange .kpi-trend {
  background: #fff7ed !important;
  color: #ea580c !important;
}

.kpi-card.index-red {
  border-top: 4px solid #ef4444 !important;
}
.kpi-card.index-red .kpi-trend {
  background: #fef2f2 !important;
  color: #dc2626 !important;
}

/* ================================================================
   CHART CARDS (Crisp White SaaS Elevation)
   ================================================================ */
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--gap-md);
}

.chart-grid.three-col { grid-template-columns: repeat(3, 1fr); }
.chart-grid.single { grid-template-columns: 1fr; }

.chart-card {
  background: #ffffff;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--gap-lg);
  position: relative;
  transition: all var(--transition-base);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.chart-card:hover {
  border-color: #cbd5e1;
  box-shadow: var(--shadow-card-hover);
}

.chart-card.full-width { grid-column: 1 / -1; }
.chart-card.span-2 { grid-column: span 2; }

.chart-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--gap-md);
}

.chart-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.2px;
}

.chart-subtitle {
  font-size: 0.74rem;
  color: #64748b;
  margin-top: 2px;
}

/* Info Box */
.info-box {
  display: flex;
  gap: 12px;
  padding: 14px 18px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: var(--radius-md);
  font-size: 0.8rem;
  color: #1e3a8a;
  line-height: 1.55;
  margin-bottom: var(--gap-lg);
}

.info-icon {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #3b82f6;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.75rem;
  flex-shrink: 0;
}

/* ================================================================
   LEADERBOARD / RANKING & MAP GRID
   ================================================================ */
.map-leaderboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--gap-md);
  align-items: stretch;
}

.map-leaderboard-card {
  display: flex;
  flex-direction: column;
}

.map-leaderboard-card .chart-card-header {
  flex-shrink: 0;
  margin-bottom: 12px;
}

#rankingLeaderboard {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.ranking-scroll-container {
  flex: 1;
  max-height: 520px;
  overflow-y: auto;
  padding-right: 6px;
}

.ranking-scroll-container::-webkit-scrollbar { width: 5px; }
.ranking-scroll-container::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
.ranking-scroll-container::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

.rank-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  margin-bottom: 8px;
  background: #f8f9fc;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.rank-item:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

/* ================================================================
   MAP STYLING
   ================================================================ */
.map-container {
  width: 100%;
  height: 480px;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border-subtle);
  position: relative;
  background: #f1f5f9;
}

.map-container .leaflet-container {
  background: #f1f5f9;
}

.map-header-tools {
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
  flex-wrap: wrap;
}

.legend-strip {
  display: flex;
  gap: 10px;
  background: #f8f9fc;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 4px 10px;
  font-size: 0.72rem;
  color: #475569;
}

.legend-item { display: flex; align-items: center; gap: 4px; }
.legend-color { width: 10px; height: 10px; border-radius: 3px; }

.map-note {
  font-size: 0.72rem;
  color: var(--text-muted);
  margin-top: 8px;
}

/* Toggle Group for Buffer */
.toggle-group {
  display: flex;
  background: #f1f5f9;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
  overflow: hidden;
}

.toggle-btn {
  padding: 5px 12px;
  font-size: 0.74rem;
  font-family: inherit;
  font-weight: 600;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.toggle-btn:hover { color: #0f172a; }
.toggle-btn.active {
  background: var(--accent-primary);
  color: #ffffff;
}

/* Leaflet Popup & Tooltip */
.leaflet-popup-content-wrapper {
  background: #ffffff !important;
  color: #0f172a !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15) !important;
  border: 1px solid var(--border-subtle) !important;
}

.leaflet-popup-tip { background: #ffffff !important; }

.leaflet-tooltip.station-map-tooltip {
  padding: 6px 10px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  background: #ffffff;
  color: #0f172a;
  font-size: 0.74rem;
  box-shadow: var(--shadow-sm);
}

.popup-title {
  font-weight: 700;
  font-size: 0.9rem;
  color: #0f172a;
  margin-bottom: 6px;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 4px;
}

.popup-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 3px;
  font-size: 0.76rem;
}

.popup-label { color: #64748b; }
.popup-value { font-weight: 600; color: #0f172a; }

/* ================================================================
   DATA TABLES
   ================================================================ */
.data-table-wrapper {
  overflow-x: auto;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  background: #ffffff;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}

.data-table thead th {
  padding: 10px 14px;
  background: #f8f9fc;
  color: #475569;
  font-weight: 700;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  border-bottom: 1px solid var(--border-subtle);
  text-align: left;
}

.data-table tbody td {
  padding: 10px 14px;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
}

.data-table tbody tr:hover td {
  background: #f8f9fc;
}

/* Badges */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 600;
}

.badge-logger {
  background: #fffbeb;
  color: #d97706;
  border: 1px solid #fde68a;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.68rem;
  font-weight: 600;
}

.status-badge-sm {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
}

.status-badge-sm.ok { background: #ecfdf5; color: #059669; }
.status-badge-sm.caution { background: #fffbeb; color: #d97706; }
.status-badge-sm.excluded { background: #fef2f2; color: #dc2626; }

.priority-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
}

.priority-1 { background: #fee2e2; color: #b91c1c; }
.priority-2 { background: #ffedd5; color: #c2410c; }
.priority-3 { background: #fef9c3; color: #a16207; }

/* ================================================================
   WIND ROSE & TRAFFIC SECTION
   ================================================================ */
.wind-rose-body-split {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 14px;
  align-items: center;
  margin-top: 10px;
}

.wind-rose-chart-pane { min-width: 0; width: 100%; }
.wind-rose-side-pane { min-width: 0; display: flex; flex-direction: column; }

.wind-rose-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
  margin-bottom: 8px;
}

.rose-metric-item {
  background: #f8f9fc;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 8px 6px;
  text-align: center;
}

.rose-metric-label {
  font-size: 0.65rem;
  color: #64748b;
  text-transform: uppercase;
  font-weight: 600;
}

.rose-metric-val {
  font-size: 0.85rem;
  font-weight: 700;
  color: #0f172a;
}

.wind-rose-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
  margin-top: 2px;
}

.rose-grid-cell {
  background: #ffffff;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 6px 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rose-grid-dir { font-weight: 700; font-size: 0.72rem; color: #334155; }
.rose-grid-val { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 600; }

.wind-rose-insight {
  margin-top: 10px;
  font-size: 0.74rem;
  color: #475569;
  text-align: center;
  background: #f8f9fc;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.wind-rose-insight strong { color: #0f172a; }

/* Pearson Matrix */
.correlation-matrix-wrapper {
  width: 100%;
  overflow: visible;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  background: #ffffff;
}

.correlation-matrix-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  font-size: 0.78rem;
}

.correlation-matrix-table thead th {
  padding: 10px 4px;
  text-align: center;
  font-weight: 700;
  font-size: 0.72rem;
  color: #475569;
  background: #f8f9fc;
  border-bottom: 1px solid var(--border-subtle);
}

.correlation-matrix-table tbody td {
  padding: 9px 3px;
  text-align: center;
  border-bottom: 1px solid #f1f5f9;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  font-weight: 600;
}

.correlation-matrix-table tbody td:first-child {
  font-family: inherit;
  font-weight: 700;
  color: #1e293b;
  text-align: left;
  padding-left: 14px;
}

/* ================================================================
   SENSOR RELIABILITY HEATMAP & AUDIT CALLOUT
   ================================================================ */
.reliability-summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--gap-md);
  margin-top: 12px;
  margin-bottom: 14px;
}

.reliability-stat-card {
  background: #f8f9fc;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
}

.reliability-stat-card .stat-label {
  font-size: 0.68rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}

.reliability-stat-card .stat-val {
  font-size: 1.3rem;
  font-weight: 800;
  color: #0f172a;
  font-family: 'JetBrains Mono', monospace;
  margin-top: 2px;
}

.reliability-stat-card .stat-sub {
  font-size: 0.7rem;
  color: #64748b;
  margin-top: 2px;
}

.reliability-table-container {
  width: 100%;
  overflow-x: auto;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  background: #ffffff;
  margin-bottom: 14px;
}

.reliability-heatmap-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.72rem;
  min-width: 1100px;
}

.reliability-heatmap-table thead th {
  padding: 8px 4px;
  text-align: center;
  font-weight: 600;
  font-size: 0.68rem;
  color: #64748b;
  background: #f8f9fc;
  border-bottom: 1px solid var(--border-subtle);
  border-right: 1px solid #f1f5f9;
}

.reliability-heatmap-table thead tr.year-row th {
  padding: 8px 10px;
  font-size: 0.74rem;
  font-weight: 700;
  color: #1e293b;
  background: #edf2f7;
}

.reliability-heatmap-table thead th.sticky-col,
.reliability-heatmap-table tbody td.sticky-col {
  position: sticky;
  left: 0;
  z-index: 2;
  background: #ffffff;
  border-right: 2px solid var(--border-subtle);
  text-align: left;
  padding-left: 12px;
  padding-right: 8px;
  min-width: 190px;
  max-width: 210px;
}

.reliability-heatmap-table thead th.sticky-status,
.reliability-heatmap-table tbody td.sticky-status {
  position: sticky;
  left: 190px;
  z-index: 2;
  background: #ffffff;
  border-right: 2px solid var(--border-subtle);
  text-align: center;
  width: 75px;
}

.reliability-heatmap-table thead th.sticky-col,
.reliability-heatmap-table thead th.sticky-status {
  z-index: 4;
  background: #f8f9fc;
}

.reliability-heatmap-table tbody td {
  padding: 3px 2px;
  text-align: center;
  border-bottom: 1px solid #f1f5f9;
  border-right: 1px solid #f8f9fc;
}

.heat-cell {
  display: block;
  width: 100%;
  height: 24px;
  line-height: 24px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  transition: transform 0.12s ease;
}

.heat-cell:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  z-index: 5;
  position: relative;
}

.heat-cell.empty {
  background: #e2e8f0 !important;
  color: #94a3b8 !important;
}

.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding: 10px 14px;
  background: #f8f9fc;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  font-size: 0.74rem;
  color: #475569;
}

.legend-chip { display: flex; align-items: center; gap: 6px; }
.legend-swatch { width: 14px; height: 14px; border-radius: 4px; display: inline-block; }

.reliability-tooltip {
  position: fixed;
  z-index: 9999;
  pointer-events: none;
  background: #0f172a;
  color: #f8fafc;
  border: 1px solid #334155;
  border-radius: var(--radius-md);
  padding: 10px 14px;
  font-size: 0.74rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
  display: none;
}

/* Audit Methodology Callout Box */
.audit-methodology-callout {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-left: 4px solid #10b981;
  border-radius: 10px;
  padding: 18px 20px;
  margin: 0 0 20px 0;
  color: #166534;
  font-size: 0.85rem;
  line-height: 1.6;
}

.audit-methodology-callout .callout-icon-wrap {
  flex-shrink: 0;
  color: #16a34a;
  margin-top: 2px;
}

.audit-methodology-callout .callout-body strong {
  display: block;
  color: #14532d;
  font-size: 0.9rem;
  margin-bottom: 6px;
  font-weight: 700;
}

.audit-methodology-callout .callout-body p {
  margin: 0;
  color: #166534;
}

/* Diurnal CSS Grid Heatmap */
.heatmap-grid {
  display: grid;
  gap: 3px;
  padding: 8px 0;
}

.heatmap-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.heatmap-cell {
  height: 28px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.62rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  transition: transform 0.12s ease;
  cursor: pointer;
}

.heatmap-cell:hover {
  transform: scale(1.15);
  z-index: 2;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  inset: 0;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  transition: opacity var(--transition-slow);
}

.loading-overlay.hidden {
  opacity: 0;
  pointer-events: none;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-text {
  margin-top: 16px;
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 600;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Utility */
.mb-lg { margin-bottom: var(--gap-lg); }
.text-muted { color: var(--text-muted); }

/* Responsive adjustments */
@media (max-width: 1200px) {
  .dashboard-body { flex-direction: column; }
  .sidebar-nav {
    width: 100%;
    min-width: 100%;
    height: auto;
    position: static;
    border-right: none;
    border-bottom: 1px solid var(--border-subtle);
    padding: 14px var(--gap-md);
  }
  .tab-nav { flex-direction: row; overflow-x: auto; }
  .tab-btn { min-width: 240px; }
  .chart-grid { grid-template-columns: 1fr; }
  .map-leaderboard-grid { grid-template-columns: 1fr; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr) !important; }
}

@media (max-width: 768px) {
  .kpi-grid { grid-template-columns: 1fr !important; padding: 16px; }
  .reliability-summary-grid { grid-template-columns: repeat(2, 1fr); }
  .wind-rose-body-split { grid-template-columns: 1fr; }
}
"""

with open(CSS_PATH, "w", encoding="utf-8") as f:
    f.write(LIGHT_CSS)
print("[OK] style.css rewritten with clean modern light SaaS theme")


# ==============================================================================
# 2. UPDATE DASHBOARD.JS FOR LIGHT MODE TILES & CHART.JS PALETTE
# ==============================================================================

with open(JS_PATH, encoding="utf-8") as f:
    js = f.read()

# A) Set global Chart.js defaults to clean light mode right at document start
chart_defaults_code = """// Chart.js Light Mode Defaults (Untitled UI Style)
if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#64748b';
  Chart.defaults.font.family = "'Plus Jakarta Sans', 'Inter', sans-serif";
  Chart.defaults.plugins.tooltip.backgroundColor = '#0f172a';
  Chart.defaults.plugins.tooltip.titleColor = '#ffffff';
  Chart.defaults.plugins.tooltip.bodyColor = '#e2e8f0';
  Chart.defaults.plugins.tooltip.borderColor = '#334155';
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.plugins.tooltip.padding = 10;
}
"""

if "Chart.defaults.color" not in js:
    # insert before document.addEventListener('DOMContentLoaded'
    js = js.replace(
        "document.addEventListener('DOMContentLoaded', async () => {",
        chart_defaults_code + "\ndocument.addEventListener('DOMContentLoaded', async () => {"
    )
    print("[OK] Injected Chart.js light mode defaults")

# B) Switch Leaflet Map from Dark Gray Canvas to CartoDB Positron / OSM Light Gray
old_map_tiles = """  // Esri World Dark Gray Canvas tiles (Clean dark theme, no watermark, 100% free without API key)
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ | Data: AQMS KLHK',
    maxZoom: 16
  }).addTo(state.map);
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16
  }).addTo(state.map);"""

new_map_tiles = """  // CartoDB Positron (Clean Modern Light Vector Theme matching Untitled UI style)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors &copy; <a href=\"https://carto.com/attributions\">CARTO</a> | Data: AQMS KLHK',
    subdomains: 'abcd',
    maxZoom: 19
  }).addTo(state.map);"""

if old_map_tiles in js:
    js = js.replace(old_map_tiles, new_map_tiles)
    print("[OK] Switched map tiles to CartoDB Positron (Light Theme)")
else:
    # Fallback search for L.tileLayer
    pattern = r"L\.tileLayer\('https://server\.arcgisonline\.com[^}]+}\)\.addTo\(state\.map\);\s*L\.tileLayer\('https://server\.arcgisonline\.com[^}]+}\)\.addTo\(state\.map\);"
    match = re.search(pattern, js)
    if match:
        js = js[:match.start()] + new_map_tiles + js[match.end():]
        print("[OK] Switched map tiles via regex fallback")
    else:
        print("[WARN] Could not find dark map tile block to replace")

# C) Replace Chart.js grid colors: from 'rgba(255,255,255,0.05)' to 'rgba(0,0,0,0.06)'
# and axis ticks from '#94a3b8' to '#64748b'
js = js.replace("'rgba(255,255,255,0.05)'", "'rgba(0,0,0,0.06)'")
js = js.replace("'rgba(255, 255, 255, 0.05)'", "'rgba(0,0,0,0.06)'")
js = js.replace("'rgba(255,255,255,0.08)'", "'rgba(0,0,0,0.08)'")
js = js.replace("'rgba(255,255,255,0.12)'", "'rgba(0,0,0,0.08)'")
js = js.replace("color: '#94a3b8'", "color: '#64748b'")

# D) Replace dark radar styling for wind rose:
# angleLines: { color: 'rgba(255,255,255,0.12)' } -> rgba(0,0,0,0.08)
# pointLabels: color: '#cbd5e1' -> '#1e293b'
js = js.replace("color: '#cbd5e1'", "color: '#475569'")

# E) Replace ranking item inner background in renderRankingList
old_rank_item_html = 'background:rgba(255,255,255,0.03); border-radius:6px; border-left:3px solid ${getAQIColor(stn.pm25_avg)};'
new_rank_item_html = 'background:#f8f9fc; border:1px solid #e2e8f0; border-radius:8px; border-left:4px solid ${getAQIColor(stn.pm25_avg)};'
if old_rank_item_html in js:
    js = js.replace(old_rank_item_html, new_rank_item_html)
    print("[OK] Updated ranking item card styling in JS")

# F) Replace Pearson correlation matrix text color in renderCorrelationMatrix
# let textColor = '#94a3b8'; -> let textColor = '#475569';
js = js.replace("let textColor = '#94a3b8';", "let textColor = '#475569';")

with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write(js)
print("[OK] dashboard.js updated for light SaaS theme")


# ==============================================================================
# 3. UPDATE INDEX.HTML CACHE BUSTER
# ==============================================================================
with open(HTML_PATH, encoding="utf-8") as f:
    html = f.read()

html = re.sub(r'style\.css\?v=[0-9.]+', 'style.css?v=5.0', html)
html = re.sub(r'dashboard\.js\?v=[0-9.]+', 'dashboard.js?v=5.0', html)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html updated cache-buster to v=5.0")

print("\nTheme successfully applied!")
