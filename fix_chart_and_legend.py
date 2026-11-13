"""
1. Adjust Vulnerable Groups chart position:
   - Add top padding (padding: { top: 22 }) so the chart bar area moves down slightly, giving breathing room from the legend.
   - Add legend padding (padding: 16)
2. Adjust Sensor Reliability Heatmap Legend background:
   - Change from dark grey rgba(17, 24, 39, 0.5) to soft neutral light grey #f8f9fc with subtle border #e2e8f0.
   - Text color legible #334155.
"""
import re

CSS_PATH = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main\assets\css\style.css"
JS_PATH  = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main\assets\js\dashboard.js"
HTML_PATH = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main\index.html"

# 1. Update style.css
with open(CSS_PATH, encoding="utf-8") as f:
    css = f.read()

old_legend = """.heatmap-legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: rgba(17, 24, 39, 0.5);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
  font-size: 0.7rem;
  color: #1e3a8a;
}"""

new_legend = """.heatmap-legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 14px;
  padding: 10px 14px;
  background: #f8f9fc;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
  font-size: 0.74rem;
  color: #334155;
}

.heatmap-legend .legend-title {
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.heatmap-legend .legend-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #334155;
  font-weight: 500;
}"""

if old_legend in css:
    css = css.replace(old_legend, new_legend)
    print("[OK] Replaced .heatmap-legend exact block")
else:
    pattern = r'\.heatmap-legend\s*\{[^}]+\}'
    css = re.sub(pattern, new_legend, css)
    print("[OK] Replaced .heatmap-legend via regex")

with open(CSS_PATH, "w", encoding="utf-8") as f:
    f.write(css)
print("[OK] style.css saved")

# 2. Update dashboard.js
with open(JS_PATH, encoding="utf-8") as f:
    js = f.read()

# Update renderVulnerableChart padding to push chart down slightly
old_padding = """      layout: {
        padding: {
          left: 4,
          right: 12,
          top: 6,
          bottom: 2
        }
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: '#64748b',
            boxWidth: 12,
            font: { size: 11, weight: 600 }
          }
        },"""

new_padding = """      layout: {
        padding: {
          left: 4,
          right: 12,
          top: 22,
          bottom: 4
        }
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: '#64748b',
            boxWidth: 12,
            padding: 18,
            font: { size: 11, weight: 600 }
          }
        },"""

if old_padding in js:
    js = js.replace(old_padding, new_padding)
    print("[OK] Updated chart padding and legend padding in dashboard.js")
else:
    print("[WARN] old_padding pattern not matched exactly, trying regex")
    js = re.sub(
        r'layout:\s*\{[\s\S]*?padding:\s*\{[\s\S]*?top:\s*\d+[\s\S]*?\}\s*\},',
        """layout: {
        padding: {
          left: 4,
          right: 12,
          top: 22,
          bottom: 4
        }
      },""",
        js,
        count=1
    )

with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write(js)
print("[OK] dashboard.js saved")

# 3. Update cache-buster in index.html to v=5.7
with open(HTML_PATH, encoding="utf-8") as f:
    html = f.read()

html = re.sub(r'style\.css\?v=[0-9.]+', 'style.css?v=5.7', html)
html = re.sub(r'dashboard\.js\?v=[0-9.]+', 'dashboard.js?v=5.7', html)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html updated cache-buster to v=5.7")
