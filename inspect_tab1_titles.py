import re

HTML_PATH = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main\index.html"
CSS_PATH = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main\assets\css\style.css"

with open(HTML_PATH, encoding="utf-8") as f:
    html = f.read()

idx_tab1 = html.find('id="tab1"')
idx_tab2 = html.find('id="tab2"')
tab1 = html[idx_tab1:idx_tab2]

print("=== TAB 1 TITLES / HEADINGS ===")
for m in re.finditer(r'class="([^"]*title[^"]*)"[^>]*>([^<]+)<', tab1):
    print("Class:", m.group(1), "| Text:", m.group(2).strip())

print("\n=== TAB 1 KPI LABELS ===")
for m in re.finditer(r'class="([^"]*label[^"]*)"[^>]*>([^<]+)<', tab1):
    print("Class:", m.group(1), "| Text:", m.group(2).strip())

with open(CSS_PATH, encoding="utf-8") as f:
    css = f.read()

print("\n=== CHECKING COLOR RULES IN CSS FOR TAB 1 TITLES ===")
for cls in [".chart-title", ".kpi-label", ".kpi-header-label", ".kpi-trend", ".chart-subtitle", ".section-header"]:
    print(f"\n--- {cls} ---")
    for m in re.finditer(r'(' + re.escape(cls) + r'[^{]*\{[^}]*\})', css):
        print(m.group(0))
