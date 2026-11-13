"""
Fix highlight for .wind-rose-insight and .wind-rose-insight strong in style.css:
- Replace color: #ffffff with high-contrast badge/pill styling
- Background pill with solid vibrant color for numbers and directions
"""
import re

CSS_PATH = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main\assets\css\style.css"
HTML_PATH = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main\index.html"

with open(CSS_PATH, encoding="utf-8") as f:
    css = f.read()

old_block = """.wind-rose-insight {
  margin-top: 10px;
  font-size: 0.72rem;
  color: #1e3a8a;
  text-align: center;
  background: rgba(255, 255, 255, 0.03);
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
  line-height: 1.45;
}

.wind-rose-insight strong {
  color: #ffffff;
}"""

new_block = """.wind-rose-insight {
  margin-top: 10px;
  font-size: 0.78rem;
  color: #334155;
  text-align: center;
  background: #f8f9fc;
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
  line-height: 1.6;
}

.wind-rose-insight strong {
  color: #4f46e5;
  font-weight: 700;
  background: #eef2ff;
  padding: 2px 8px;
  border-radius: 6px;
  border: 1px solid #e0e7ff;
  margin: 0 3px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  display: inline-block;
}"""

if old_block in css:
    css = css.replace(old_block, new_block)
    print("[OK] Replaced .wind-rose-insight block")
else:
    # Pattern fallback
    pattern = r'\.wind-rose-insight\s*\{[^}]+\}\s*\n+\.wind-rose-insight\s+strong\s*\{[^}]+\}'
    css = re.sub(pattern, new_block, css)
    print("[OK] Replaced .wind-rose-insight block via regex")

with open(CSS_PATH, "w", encoding="utf-8") as f:
    f.write(css)
print("[OK] style.css saved")

# Bump cache buster in index.html to v=5.3
with open(HTML_PATH, encoding="utf-8") as f:
    html = f.read()

html = re.sub(r'style\.css\?v=[0-9.]+', 'style.css?v=5.3', html)
html = re.sub(r'dashboard\.js\?v=[0-9.]+', 'dashboard.js?v=5.3', html)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html updated cache-buster to v=5.3")
