"""
Fix Vulnerable Groups Bar Chart Layout & Spacing:
1. Break long horizontal X-axis labels into multiline arrays ['Kuartil Rendah', '(6.8 - 19.5 µg/m³)']
2. Force maxRotation: 0, minRotation: 0 so labels don't slant into huge left margin
3. Expand barPercentage & categoryPercentage so bars fill width evenly from left to right
4. Clean layout padding to fit perfectly inside the card
"""
import re

JS_PATH = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main\assets\js\dashboard.js"
HTML_PATH = r"C:\Users\advan\Downloads\gelarrasa2026-main\gelarrasa2026-main\nyoba_gelarrasa-main\index.html"

with open(JS_PATH, encoding="utf-8") as f:
    js = f.read()

old_fn_pattern = r'function renderVulnerableChart\(\)\s*\{[\s\S]*?^}'
new_fn = """function renderVulnerableChart() {
  const ctx = document.getElementById('vulnerableGroupsChart');
  if (!ctx || !state.data.vulnerable) return;

  const data = state.data.vulnerable;
  const tiers = ['Rendah', 'Sedang', 'Tinggi', 'Ekstrem'];

  const under5 = tiers.map(t => data[t]?.under5_mean ?? 0);
  const over60 = tiers.map(t => data[t]?.over60_mean ?? 0);

  if (state.charts.vulnerable) state.charts.vulnerable.destroy();

  state.charts.vulnerable = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: tiers.map(t => [
        `Kuartil ${t}`,
        `(${data[t]?.pm25_range.min.toFixed(1)} - ${data[t]?.pm25_range.max.toFixed(1)} µg/m³)`
      ]),
      datasets: [
        {
          label: 'Admisi Respiratorik Balita (<5 Thn)',
          data: under5,
          backgroundColor: '#ef4444',
          borderRadius: 6,
          barPercentage: 0.82,
          categoryPercentage: 0.78
        },
        {
          label: 'Admisi Respiratorik Lansia (>60 Thn)',
          data: over60,
          backgroundColor: '#f59e0b',
          borderRadius: 6,
          barPercentage: 0.82,
          categoryPercentage: 0.78
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: {
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
        },
        tooltip: {
          callbacks: {
            title: (items) => {
              const idx = items[0].dataIndex;
              const t = tiers[idx];
              return `Kuartil Polusi ${t} (${data[t]?.pm25_range.min}-${data[t]?.pm25_range.max} µg/m³)`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: {
            color: '#64748b',
            font: { size: 10, weight: 600 },
            maxRotation: 0,
            minRotation: 0,
            autoSkip: false
          }
        },
        y: {
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: { color: '#64748b', font: { size: 10 } },
          title: {
            display: true,
            text: 'Rata-rata Pasien Rawat Inap / Hari',
            color: '#64748b',
            font: { size: 11, weight: 600 }
          }
        }
      }
    }
  });
}"""

js = re.sub(old_fn_pattern, new_fn, js, flags=re.MULTILINE)

with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write(js)
print("[OK] dashboard.js updated renderVulnerableChart")

# Update cache buster in index.html to v=5.6
with open(HTML_PATH, encoding="utf-8") as f:
    html = f.read()

html = re.sub(r'style\.css\?v=[0-9.]+', 'style.css?v=5.6', html)
html = re.sub(r'dashboard\.js\?v=[0-9.]+', 'dashboard.js?v=5.6', html)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] index.html updated cache-buster to v=5.6")
