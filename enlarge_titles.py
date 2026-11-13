"""
Update style.css:
1. Enlarge and darken .chart-title across all cards (from 0.9rem to 1.15rem, color: #0f172a !important, font-weight: 700)
2. Fix .kpi-header-label from rgba(255, 255, 255, 0.75) to color: #334155 !important, font-size: 0.92rem
3. Enlarge .kpi-label to font-size: 0.82rem, color: #475569 !important
4. Enlarge .chart-subtitle to font-size: 0.82rem, color: #64748b
"""
import re

CSS_PATH = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main\assets\css\style.css"
HTML_PATH = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main\index.html"

with open(CSS_PATH, encoding="utf-8") as f:
    css = f.read()

# 1. Fix .kpi-header-label
old_kpi_header_label = """.kpi-header-label {
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: rgba(255, 255, 255, 0.75);
}"""

new_kpi_header_label = """.kpi-header-label {
  font-size: 0.92rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: #334155 !important;
}"""

if old_kpi_header_label in css:
    css = css.replace(old_kpi_header_label, new_kpi_header_label)
    print("[OK] Replaced .kpi-header-label exact block")
else:
    pattern = r'\.kpi-header-label\s*\{[^}]+\}'
    css = re.sub(pattern, new_kpi_header_label, css)
    print("[OK] Replaced .kpi-header-label via regex")

# 2. Fix .chart-title
old_chart_title = """.chart-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}"""

new_chart_title = """.chart-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #0f172a !important;
  letter-spacing: -0.3px;
  line-height: 1.35;
}"""

if old_chart_title in css:
    css = css.replace(old_chart_title, new_chart_title)
    print("[OK] Replaced .chart-title exact block")
else:
    pattern = r'\.chart-title\s*\{[^}]+\}'
    css = re.sub(pattern, new_chart_title, css)
    print("[OK] Replaced .chart-title via regex")

# 3. Fix .chart-title-group .chart-title and .chart-subtitle
css = re.sub(
    r'\.chart-title-group\s+\.chart-title\s*\{[^}]+\}',
    """.chart-title-group .chart-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #0f172a !important;
  white-space: normal;
  letter-spacing: -0.3px;
  line-height: 1.35;
}""",
    css
)

css = re.sub(
    r'\.chart-subtitle\s*\{[^}]+\}',
    """.chart-subtitle {
  font-size: 0.82rem;
  color: #64748b;
  margin-top: 3px;
  line-height: 1.4;
}""",
    css
)

css = re.sub(
    r'\.kpi-label\s*\{[^}]+\}',
    """.kpi-label {
  font-size: 0.8rem;
  line-height: 1.35;
  color: #475569 !important;
  font-weight: 600;
  white-space: normal;
}""",
    css
)

with open(CSS_PATH, "w", encoding="utf-8") as f:
    f.write(css)
print("[OK] style.css saved")

# Update cache buster in index.html to v=5.5
with open(HTML_PATH, encoding="utf-8") as f:
    html = f.read()

html = re.sub(r'style\.css\?v=[0-9.]+', 'style.css?v=5.5', html)
html = re.sub(r'dashboard\.js\?v=[0-9.]+', 'dashboard.js?v=5.5', html)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html updated cache-buster to v=5.5")
