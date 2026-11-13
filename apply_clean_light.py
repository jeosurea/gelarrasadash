"""
Surgical Theme Script:
Applies Clean Light SaaS Theme (Untitled UI style) to AQMS Dashboard WITHOUT breaking any layouts:
1. Replaces dark variables with crisp light theme variables
2. Replaces Esri Dark Canvas with Esri Light Gray Canvas (official Esri, NO watermark, NO API key)
3. Keeps exact layout for wind-rose (grid 2 cols, text-align: center vertical flow)
4. Keeps map-header-tools flex-wrap and buffer/radius controls neatly aligned
5. Fixes Chart.js gridlines to soft light gray and ticks to slate
"""
import re

BASE = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main"
CSS_PATH = BASE + r"\assets\css\style.css"
JS_PATH  = BASE + r"\assets\js\dashboard.js"
HTML_PATH = BASE + r"\index.html"

# ==============================================================================
# 1. UPDATE DASHBOARD.JS
# ==============================================================================
with open(JS_PATH, encoding="utf-8") as f:
    js = f.read()

# A) Set global Chart.js defaults to light mode
chart_defaults = """// Chart.js Light Mode Defaults
if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#64748b';
  Chart.defaults.font.family = "'Inter', sans-serif";
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
    js = js.replace(
        "document.addEventListener('DOMContentLoaded', async () => {",
        chart_defaults + "\ndocument.addEventListener('DOMContentLoaded', async () => {"
    )
    print("[OK] Injected Chart.js light mode defaults")

# B) Switch Leaflet Map to Esri World Light Gray Canvas (OFFICIAL ESRI, NO WATERMARK, NO API KEY)
old_esri_dark = """  // Esri World Dark Gray Canvas tiles (Clean dark theme, no watermark, 100% free without API key)
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ | Data: AQMS KLHK',
    maxZoom: 16
  }).addTo(state.map);
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16
  }).addTo(state.map);"""

new_esri_light = """  // Esri World Light Gray Canvas (Official Esri, 100% Free, NO API Key, NO Watermark)
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ | Data: AQMS KLHK',
    maxZoom: 16
  }).addTo(state.map);
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16
  }).addTo(state.map);"""

if old_esri_dark in js:
    js = js.replace(old_esri_dark, new_esri_light)
    print("[OK] Replaced Esri Dark Gray with Esri Light Gray Canvas")
else:
    # Check if there is any other tileLayer call
    pattern = r"L\.tileLayer\('https://server\.arcgisonline\.com[^}]+}\)\.addTo\(state\.map\);\s*L\.tileLayer\('https://server\.arcgisonline\.com[^}]+}\)\.addTo\(state\.map\);"
    match = re.search(pattern, js)
    if match:
        js = js[:match.start()] + new_esri_light + js[match.end():]
        print("[OK] Replaced tileLayer via regex")
    else:
        print("[WARN] TileLayer block not found by exact string or regex")

# C) Chart gridlines and ticks in JS
js = js.replace("'rgba(255,255,255,0.05)'", "'rgba(0,0,0,0.06)'")
js = js.replace("'rgba(255, 255, 255, 0.05)'", "'rgba(0,0,0,0.06)'")
js = js.replace("'rgba(255,255,255,0.08)'", "'rgba(0,0,0,0.08)'")
js = js.replace("'rgba(255,255,255,0.12)'", "'rgba(0,0,0,0.08)'")
js = js.replace("color: '#94a3b8'", "color: '#64748b'")
js = js.replace("color: '#cbd5e1'", "color: '#475569'")

# D) Ranking card items in JS: light background
old_rank_bg = 'background:rgba(255,255,255,0.03); border-radius:6px; border-left:3px solid ${getAQIColor(stn.pm25_avg)};'
new_rank_bg = 'background:#f8f9fc; border:1px solid #e2e8f0; border-radius:8px; border-left:4px solid ${getAQIColor(stn.pm25_avg)};'
if old_rank_bg in js:
    js = js.replace(old_rank_bg, new_rank_bg)
    print("[OK] Updated ranking item card styling in JS")

# E) Wind rose grid cell values unit color
js = js.replace("color:#94a3b8;margin-left:2px;", "color:#64748b;margin-left:2px;")

# F) Pearson correlation matrix default text color
js = js.replace("let textColor = '#94a3b8';", "let textColor = '#475569';")

with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write(js)
print("[OK] dashboard.js saved")


# ==============================================================================
# 2. UPDATE STYLE.CSS (PRESERVING ALL LAYOUT RULES)
# ==============================================================================
with open(CSS_PATH, encoding="utf-8") as f:
    css = f.read()

# Replace :root
old_root_pattern = r':root\s*\{[^}]+\}'
new_root = """:root {
  /* Background & Surface (Clean Modern Light SaaS) */
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

  /* Status */
  --status-ok: #10b981;
  --status-caution: #f59e0b;
  --status-excluded: #ef4444;

  /* Glass/Card */
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
  --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
  --shadow-card-hover: 0 6px 16px -2px rgba(15, 23, 42, 0.08);
  --shadow-glow: 0 0 20px rgba(94, 92, 230, 0.15);
}"""

css = re.sub(old_root_pattern, new_root, css, count=1)
print("[OK] Replaced :root custom properties")

# Disable dark ambient body::before glow
css = css.replace(
"""body::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59, 130, 246, 0.08), transparent),
    radial-gradient(ellipse 60% 40% at 80% 100%, rgba(139, 92, 246, 0.05), transparent);
  pointer-events: none;
  z-index: 0;
}""",
"""body::before {
  display: none;
}"""
)

# Scrollbars
css = css.replace("::-webkit-scrollbar-track { background: var(--bg-secondary); }", "::-webkit-scrollbar-track { background: #f1f5f9; }")
css = css.replace("::-webkit-scrollbar-thumb { background: var(--border-medium); border-radius: 3px; }", "::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }")

# Navbar styling
css = css.replace("background: rgba(6, 10, 19, 0.85);", "background: #ffffff;")
css = css.replace("border-bottom: 1px solid var(--glass-border);", "border-bottom: 1px solid var(--border-subtle); box-shadow: 0 1px 2px rgba(0,0,0,0.03);")
css = css.replace(
"""  background: linear-gradient(135deg, var(--text-primary), var(--accent-primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;""",
"""  color: #0f172a;"""
)

# Navbar logo
css = css.replace("background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));", "background: linear-gradient(135deg, #5e5ce6, #8b5cf6);")

# Filter select in navbar
css = css.replace(
"""  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Cpolyline points='6,9 12,15 18,9'/%3E%3C/svg%3E");""",
"""  appearance: none;
  -webkit-appearance: none;
  background-color: #f8f9fc;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2'%3E%3Cpolyline points='6,9 12,15 18,9'/%3E%3C/svg%3E");"""
)

# Sidebar styling
css = css.replace("background: var(--bg-secondary);", "background: #ffffff;")
css = css.replace("color: var(--text-secondary);\n  cursor: pointer;\n  transition: all var(--transition-base);\n  white-space: normal;\n  display: flex;\n  align-items: flex-start;\n  gap: 12px;\n  text-align: left;\n  width: 100%;", "color: #475569;\n  cursor: pointer;\n  transition: all var(--transition-base);\n  white-space: normal;\n  display: flex;\n  align-items: flex-start;\n  gap: 12px;\n  text-align: left;\n  width: 100%;")
css = css.replace(".tab-btn:hover {\n  background: rgba(255, 255, 255, 0.06);\n  color: var(--text-primary);\n  border-color: var(--border-medium);\n}", ".tab-btn:hover {\n  background: #f1f5f9;\n  color: #0f172a;\n}")

# Tab Active (Solid Indigo Purple with white text matching user reference)
old_tab_active = """.tab-btn.active {
  background: rgba(59, 130, 246, 0.12);
  border-color: rgba(59, 130, 246, 0.4);
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  left: 0;
  top: 10px;
  bottom: 10px;
  width: 4px;
  background: var(--accent-primary);
  border-radius: 0 3px 3px 0;
  box-shadow: 0 0 10px var(--accent-primary-glow);
}"""

new_tab_active = """.tab-btn.active {
  background: #5e5ce6;
  border-color: #5e5ce6;
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 4px 14px rgba(94, 92, 230, 0.25);
}

.tab-btn.active::after {
  display: none;
}"""

if old_tab_active in css:
    css = css.replace(old_tab_active, new_tab_active)
    print("[OK] Replaced tab-btn.active")

css = css.replace("background: rgba(255, 255, 255, 0.08);", "background: #f1f5f9;")
css = css.replace("background: var(--accent-primary);\n  color: #ffffff;", "background: rgba(255, 255, 255, 0.22);\n  color: #ffffff;")
css = css.replace(".tab-btn.active .tab-desc {\n  color: #93c5fd;\n}", ".tab-btn.active .tab-desc {\n  color: rgba(255, 255, 255, 0.85);\n}")

# Sidebar status box
css = css.replace("background: rgba(17, 24, 39, 0.7);", "background: #f8f9fc;")
css = css.replace(".sidebar-status-desc {\n  font-size: 0.65rem;\n  color: var(--accent-warning);", ".sidebar-status-desc {\n  font-size: 0.65rem;\n  color: #d97706; font-weight: 500;")

# KPI Hero Grid Banner & Floating Cards
old_kpi_grid = """.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr) !important;
  gap: 12px;
  margin-bottom: var(--gap-lg);
}"""

new_kpi_grid = """.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr) !important;
  gap: 16px;
  margin-bottom: var(--gap-lg);
  padding: 24px;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, #38bdf8 0%, #6366f1 50%, #8b5cf6 100%);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2);
}"""

if old_kpi_grid in css:
    css = css.replace(old_kpi_grid, new_kpi_grid)
    print("[OK] Replaced kpi-grid with Hero Gradient Banner")

# KPI Card styles
old_kpi_card = """.kpi-card {
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  -webkit-backdrop-filter: blur(var(--glass-blur));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  position: relative;
  overflow: hidden;
  transition: all var(--transition-base);
  min-width: 0;
}"""

new_kpi_card = """.kpi-card {
  background: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.9) !important;
  border-radius: var(--radius-md);
  padding: 16px 18px;
  position: relative;
  overflow: hidden;
  transition: all var(--transition-base);
  min-width: 0;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08) !important;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.12) !important;
}"""

if old_kpi_card in css:
    css = css.replace(old_kpi_card, new_kpi_card)
    print("[OK] Replaced kpi-card")

# KPI card index colors (Remove dark backgrounds! Clean top accent borders & pastel badges)
old_kpi_colors = """.kpi-card.index-green {
  background: #0d382e !important;
  border: 1px solid #10b981 !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4) !important;
}
.kpi-card.index-green::before {
  background: #10b981 !important;
  opacity: 1 !important;
}
.kpi-card.index-green .kpi-value {
  color: #ffffff !important;
  text-shadow: none !important;
}
.kpi-card.index-green .kpi-value .unit {
  color: #a7f3d0 !important;
}
.kpi-card.index-green .kpi-label {
  color: #d1fae5 !important;
}
.kpi-card.index-green .kpi-icon {
  background: rgba(255, 255, 255, 0.12) !important;
  color: #ffffff !important;
  box-shadow: none !important;
}
.kpi-card.index-green .kpi-trend {
  color: #ffffff !important;
  background: rgba(0, 0, 0, 0.3) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: none !important;
}

.kpi-card.index-yellow {
  background: #3d3008 !important;
  border: 1px solid #eab308 !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4) !important;
}
.kpi-card.index-yellow::before {
  background: #eab308 !important;
  opacity: 1 !important;
}
.kpi-card.index-yellow .kpi-value {
  color: #ffffff !important;
  text-shadow: none !important;
}
.kpi-card.index-yellow .kpi-value .unit {
  color: #fef08a !important;
}
.kpi-card.index-yellow .kpi-label {
  color: #fef9c3 !important;
}
.kpi-card.index-yellow .kpi-icon {
  background: rgba(255, 255, 255, 0.12) !important;
  color: #ffffff !important;
  box-shadow: none !important;
}
.kpi-card.index-yellow .kpi-trend {
  color: #ffffff !important;
  background: rgba(0, 0, 0, 0.3) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: none !important;
}

.kpi-card.index-orange {
  background: #421e08 !important;
  border: 1px solid #f97316 !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4) !important;
}
.kpi-card.index-orange::before {
  background: #f97316 !important;
  opacity: 1 !important;
}
.kpi-card.index-orange .kpi-value {
  color: #ffffff !important;
  text-shadow: none !important;
}
.kpi-card.index-orange .kpi-value .unit {
  color: #fed7aa !important;
}
.kpi-card.index-orange .kpi-label {
  color: #ffedd5 !important;
}
.kpi-card.index-orange .kpi-icon {
  background: rgba(255, 255, 255, 0.12) !important;
  color: #ffffff !important;
  box-shadow: none !important;
}
.kpi-card.index-orange .kpi-trend {
  color: #ffffff !important;
  background: rgba(0, 0, 0, 0.3) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: none !important;
}

.kpi-card.index-red {
  background: #401414 !important;
  border: 1px solid #ef4444 !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4) !important;
}
.kpi-card.index-red::before {
  background: #ef4444 !important;
  opacity: 1 !important;
}
.kpi-card.index-red .kpi-value {
  color: #ffffff !important;
  text-shadow: none !important;
}
.kpi-card.index-red .kpi-value .unit {
  color: #fecaca !important;
}
.kpi-card.index-red .kpi-label {
  color: #fee2e2 !important;
}
.kpi-card.index-red .kpi-icon {
  background: rgba(255, 255, 255, 0.12) !important;
  color: #ffffff !important;
  box-shadow: none !important;
}
.kpi-card.index-red .kpi-trend {
  color: #ffffff !important;
  background: rgba(0, 0, 0, 0.3) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: none !important;
}"""

new_kpi_colors = """.kpi-card.index-green {
  border-top: 4px solid #10b981 !important;
}
.kpi-card.index-green .kpi-value { color: #0f172a !important; }
.kpi-card.index-green .kpi-value .unit { color: #64748b !important; }
.kpi-card.index-green .kpi-label { color: #64748b !important; }
.kpi-card.index-green .kpi-trend {
  background: #ecfdf5 !important;
  color: #059669 !important;
  border: none !important;
}

.kpi-card.index-yellow {
  border-top: 4px solid #eab308 !important;
}
.kpi-card.index-yellow .kpi-value { color: #0f172a !important; }
.kpi-card.index-yellow .kpi-value .unit { color: #64748b !important; }
.kpi-card.index-yellow .kpi-label { color: #64748b !important; }
.kpi-card.index-yellow .kpi-trend {
  background: #fefce8 !important;
  color: #ca8a04 !important;
  border: none !important;
}

.kpi-card.index-orange {
  border-top: 4px solid #f97316 !important;
}
.kpi-card.index-orange .kpi-value { color: #0f172a !important; }
.kpi-card.index-orange .kpi-value .unit { color: #64748b !important; }
.kpi-card.index-orange .kpi-label { color: #64748b !important; }
.kpi-card.index-orange .kpi-trend {
  background: #fff7ed !important;
  color: #ea580c !important;
  border: none !important;
}

.kpi-card.index-red {
  border-top: 4px solid #ef4444 !important;
}
.kpi-card.index-red .kpi-value { color: #0f172a !important; }
.kpi-card.index-red .kpi-value .unit { color: #64748b !important; }
.kpi-card.index-red .kpi-label { color: #64748b !important; }
.kpi-card.index-red .kpi-trend {
  background: #fef2f2 !important;
  color: #dc2626 !important;
  border: none !important;
}"""

if old_kpi_colors in css:
    css = css.replace(old_kpi_colors, new_kpi_colors)
    print("[OK] Replaced KPI index colors with clean light mode")

# Info box
css = css.replace("background: rgba(59,130,246,0.06);\n  border: 1px solid rgba(59,130,246,0.15);", "background: #eff6ff;\n  border: 1px solid #bfdbfe;")
css = css.replace("color: var(--text-secondary);", "color: #1e3a8a;")

# Wind rose sector grid cells (KEEP TEXT-ALIGN: CENTER, VERTICAL FLOW, JUST UPDATE COLORS)
css = css.replace(
"""  background: rgba(17, 24, 39, 0.7);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 8px 6px;
  text-align: center;
  min-width: 0;""",
"""  background: #f8f9fc;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 8px 6px;
  text-align: center;
  min-width: 0;"""
)

css = css.replace(
""".rose-grid-cell {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: var(--radius-sm);
  padding: 5px 6px;
  text-align: center;
  transition: all var(--transition-base);
}

.rose-grid-cell:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--border-medium);
}

.rose-grid-cell.highlight {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}""",
""".rose-grid-cell {
  background: #f8f9fc;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 6px 6px;
  text-align: center;
  transition: all var(--transition-base);
}

.rose-grid-cell:hover {
  background: #ffffff;
  border-color: #cbd5e1;
  box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

.rose-grid-cell.highlight {
  border-color: #ef4444;
  background: #fef2f2;
}"""
)

css = css.replace(
""".wind-rose-insight {
  margin-top: 10px;
  font-size: 0.72rem;
  color: var(--text-secondary);
  text-align: center;
  background: rgba(255, 255, 255, 0.03);
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.wind-rose-insight strong {
  color: #ffffff;
}""",
""".wind-rose-insight {
  margin-top: 10px;
  font-size: 0.74rem;
  color: #475569;
  text-align: center;
  background: #f8f9fc;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.wind-rose-insight strong {
  color: #0f172a;
}"""
)

# Correlation matrix
css = css.replace("background: rgba(15, 23, 42, 0.4);", "background: #ffffff;")
css = css.replace("background: rgba(15, 23, 42, 0.85);", "background: #f8f9fc;")
css = css.replace("border-bottom: 1px solid rgba(255, 255, 255, 0.05);", "border-bottom: 1px solid #f1f5f9;")
css = css.replace("color: #ffffff;\n  background: rgba(15, 23, 42, 0.9);", "color: #0f172a;\n  background: #f8f9fc;")

# Heatmap sensor reliability table
css = css.replace("background: rgba(15, 23, 42, 0.5);", "background: #ffffff;")
css = css.replace("background: rgba(15, 23, 42, 0.9);", "background: #f8f9fc;")
css = css.replace("background: rgba(30, 41, 59, 0.95);", "background: #edf2f7; color: #1e293b;")
css = css.replace("background: #0d1424;", "background: #ffffff;")
css = css.replace("border-bottom: 1px solid rgba(255, 255, 255, 0.04);", "border-bottom: 1px solid #f1f5f9;")
css = css.replace("border-right: 1px solid rgba(255, 255, 255, 0.03);", "border-right: 1px solid #f8f9fc;")

# Reliability summary grid stat cards
css = css.replace(
""".reliability-stat-card {
  background: rgba(17, 24, 39, 0.7);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
}""",
""".reliability-stat-card {
  background: #f8f9fc;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
}"""
)
css = css.replace("color: #ffffff;\n  font-family: 'JetBrains Mono', monospace;\n  margin-top: 2px;", "color: #0f172a;\n  font-family: 'JetBrains Mono', monospace;\n  margin-top: 2px;")

# Heatmap legend
css = css.replace("background: rgba(15, 23, 42, 0.7);", "background: #f8f9fc;")

# Audit methodology callout
css = css.replace(
""".audit-methodology-callout {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.25);
  border-left: 4px solid #3b82f6;
  border-radius: 10px;
  padding: 18px 20px;
  margin: 0 0 20px 0;
  color: #cbd5e1;
  font-size: 0.85rem;
  line-height: 1.6;
}""",
""".audit-methodology-callout {
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
}"""
)
css = css.replace("color: #93c5fd;", "color: #14532d;")
css = css.replace(".audit-methodology-callout .callout-body p {\n  margin: 0;\n  color: #94a3b8;\n}", ".audit-methodology-callout .callout-body p {\n  margin: 0;\n  color: #166534;\n}")

# Data Table styling
css = css.replace("background: rgba(17, 24, 39, 0.7);", "background: #ffffff;")
css = css.replace("background: var(--bg-surface);", "background: #f8f9fc;")
css = css.replace("background: rgba(255,255,255,0.02);", "background: #f8f9fc;")
css = css.replace("border-bottom: 1px solid var(--border-subtle);", "border-bottom: 1px solid #f1f5f9;")

# Toggle button for buffer
css = css.replace("background: var(--bg-card);", "background: #f8f9fc;")
css = css.replace("background: #0e7490;", "background: var(--accent-primary);")

# Map container
css = css.replace("background: var(--bg-primary);", "background: #f1f5f9;")
css = css.replace("background: rgba(15, 23, 42, 0.96);", "background: #ffffff; color: #0f172a;")

with open(CSS_PATH, "w", encoding="utf-8") as f:
    f.write(css)
print("[OK] style.css saved with clean light SaaS theme (all layout rules intact)")


# ==============================================================================
# 3. UPDATE INDEX.HTML CACHE BUSTER TO V=5.2
# ==============================================================================
with open(HTML_PATH, encoding="utf-8") as f:
    html = f.read()

html = re.sub(r'style\.css\?v=[0-9.]+', 'style.css?v=5.2', html)
html = re.sub(r'dashboard\.js\?v=[0-9.]+', 'dashboard.js?v=5.2', html)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html updated cache-buster to v=5.2")

print("\nAll done!")
