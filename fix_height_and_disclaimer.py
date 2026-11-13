"""
1. Fix Vulnerable Groups Bar Chart:
   - Restore top padding in dashboard.js back to original top: 6, legend padding: 12 (do not move the top).
   - In index.html, extend the chart height from height:300px to height:360px (pulls the bottom edge down).
   - Also keep lagEffectChart at height:360px so both sibling cards in the grid row stay aligned.

2. Fix Catatan Metodologis text color:
   - In style.css: change .reliability-disclaimer-banner color from faint #cbd5e1 to crisp dark slate #334155.
   - Update background to soft light blue #f0f9ff and border to #bae6fd.
   - Set strong color to bold dark blue #0284c7.
   - In index.html: update svg color from #38bdf8 to #0284c7.
"""
import re

BASE = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main"
CSS_PATH = BASE + r"\assets\css\style.css"
JS_PATH  = BASE + r"\assets\js\dashboard.js"
HTML_PATH = BASE + r"\index.html"

# 1. Update style.css
with open(CSS_PATH, encoding="utf-8") as f:
    css = f.read()

old_disclaimer = """.reliability-disclaimer-banner {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 14px;
  background: rgba(56, 189, 248, 0.06);
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: var(--radius-sm);
  font-size: 0.72rem;
  color: #cbd5e1;
  line-height: 1.5;
  margin-bottom: 14px;
}

.reliability-disclaimer-banner strong {
  color: #38bdf8;
}"""

new_disclaimer = """.reliability-disclaimer-banner {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 16px;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: var(--radius-sm);
  font-size: 0.76rem;
  color: #334155; /* Gelap dan tegas, sangat kontras & jelas terbaca */
  line-height: 1.55;
  margin-bottom: 14px;
}

.reliability-disclaimer-banner strong {
  color: #0284c7;
  font-weight: 700;
}"""

if old_disclaimer in css:
    css = css.replace(old_disclaimer, new_disclaimer)
    print("[OK] Replaced .reliability-disclaimer-banner exact block")
else:
    pattern = r'\.reliability-disclaimer-banner\s*\{[^}]+\}\s*\n+\.reliability-disclaimer-banner\s+strong\s*\{[^}]+\}'
    css = re.sub(pattern, new_disclaimer, css)
    print("[OK] Replaced .reliability-disclaimer-banner via regex")

with open(CSS_PATH, "w", encoding="utf-8") as f:
    f.write(css)
print("[OK] style.css saved")

# 2. Update dashboard.js
with open(JS_PATH, encoding="utf-8") as f:
    js = f.read()

# Restore top padding to original (top: 6, legend padding: 12)
old_padding = """      layout: {
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

new_padding = """      layout: {
        padding: {
          left: 4,
          right: 12,
          top: 6,
          bottom: 4
        }
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: '#64748b',
            boxWidth: 12,
            padding: 12,
            font: { size: 11, weight: 600 }
          }
        },"""

if old_padding in js:
    js = js.replace(old_padding, new_padding)
    print("[OK] Restored chart top padding and legend padding in dashboard.js")
else:
    # Pattern fallback
    js = re.sub(
        r'layout:\s*\{[\s\S]*?padding:\s*\{[\s\S]*?top:\s*\d+[\s\S]*?\}\s*\},',
        """layout: {
        padding: {
          left: 4,
          right: 12,
          top: 6,
          bottom: 4
        }
      },""",
        js,
        count=1
    )
    print("[OK] Replaced chart padding via regex fallback")

with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write(js)
print("[OK] dashboard.js saved")

# 3. Update index.html
with open(HTML_PATH, encoding="utf-8") as f:
    html = f.read()

# Increase height of lagEffectChart and vulnerableGroupsChart to 360px
html = html.replace(
    '<div class="chart-container" style="height:300px;">\n            <canvas id="lagEffectChart"></canvas>',
    '<div class="chart-container" style="height:360px;">\n            <canvas id="lagEffectChart"></canvas>'
)
html = html.replace(
    '<div class="chart-container" style="height:300px;">\n            <canvas id="vulnerableGroupsChart"></canvas>',
    '<div class="chart-container" style="height:360px;">\n            <canvas id="vulnerableGroupsChart"></canvas>'
)

# Update svg icon color in reliability disclaimer
html = html.replace('style="flex-shrink:0; color:#38bdf8;"', 'style="flex-shrink:0; color:#0284c7;"')

# Bump cache buster to v=5.8
html = re.sub(r'style\.css\?v=[0-9.]+', 'style.css?v=5.8', html)
html = re.sub(r'dashboard\.js\?v=[0-9.]+', 'dashboard.js?v=5.8', html)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html updated (height: 360px and cache-buster v=5.8)")
