"""
Update .wind-rose-insight strong:
Remove box, pill background, and border.
Keep as clean, bold plain text with high contrast color (#0f172a).
"""
import re

CSS_PATH = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main\assets\css\style.css"
HTML_PATH = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main\index.html"

with open(CSS_PATH, encoding="utf-8") as f:
    css = f.read()

old_strong = """.wind-rose-insight strong {
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

new_strong = """.wind-rose-insight strong {
  color: #0f172a;
  font-weight: 700;
  background: transparent;
  padding: 0;
  border: none;
  margin: 0;
  font-family: inherit;
  font-size: inherit;
  display: inline;
}"""

if old_strong in css:
    css = css.replace(old_strong, new_strong)
    print("[OK] Replaced .wind-rose-insight strong with plain text")
else:
    pattern = r'\.wind-rose-insight\s+strong\s*\{[^}]+\}'
    css = re.sub(pattern, new_strong, css)
    print("[OK] Replaced via regex fallback")

with open(CSS_PATH, "w", encoding="utf-8") as f:
    f.write(css)
print("[OK] style.css saved")

# Update cache buster in index.html to v=5.4
with open(HTML_PATH, encoding="utf-8") as f:
    html = f.read()

html = re.sub(r'style\.css\?v=[0-9.]+', 'style.css?v=5.4', html)
html = re.sub(r'dashboard\.js\?v=[0-9.]+', 'dashboard.js?v=5.4', html)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html updated cache-buster to v=5.4")
