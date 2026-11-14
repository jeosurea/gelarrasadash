/**
 * AQMS DASHBOARD - Interactive Visualizations & Data Handler
 * Powered by Leaflet.js, Chart.js, and Vanilla Modern JS
 */

// Global State
const state = {
  currentTab: 'tab1',
  statusFilter: 'ALL', // 'ALL', 'OK', 'CAUTION', 'EXCLUDED'
  data: {},
  charts: {},
  map: null,
  mapMarkers: [],
  mapBuffers: [],
  bufferEnabled: false,
  bufferRadius: 'adaptive'
};

// Data paths
const DATA_PATHS = {
  kpi: 'data/json/kpi_summary.json',
  stations: 'data/json/stations_map.json',
  trendMonthly: 'data/json/trend_monthly.json',
  trendDaily: 'data/json/trend_daily_sample.json',
  diurnal: 'data/json/diurnal_heatmap.json',
  siteType: 'data/json/site_type_comparison.json',
  corr: 'data/json/correlation_matrix.json',
  windRose: 'data/json/wind_pollution_rose.json',
  sensorReliability: 'data/json/sensor_reliability_heatmap.json',
  traffic: 'data/json/traffic_scatter.json',
  lagEffect: 'data/json/lag_effect.json',
  vulnerable: 'data/json/vulnerable_groups.json',
  disease: 'data/json/disease_specific.json',
  audit: 'data/json/station_audit.json',
  islands: 'data/json/island_distribution.json',
  priority: 'data/json/priority_matrix.json',
  gap: 'data/json/gap_analysis.json',
};

// Color Utilities
function getAQIColor(val) {
  if (val === null || val === undefined) return '#94a3b8';
  if (val <= 15) return '#10b981'; // Good (WHO)
  if (val <= 35) return '#eab308'; // Moderate
  if (val <= 55) return '#f97316'; // Unhealthy Sensitive (PP22 threshold)
  if (val <= 150) return '#ef4444'; // Unhealthy
  return '#a855f7'; // Very Unhealthy / Hazardous
}

function getAQILabel(val) {
  if (val === null || val === undefined) return 'N/A';
  if (val <= 15) return 'Baik (WHO Compliant)';
  if (val <= 35) return 'Sedang';
  if (val <= 55) return 'Tidak Sehat (Sensitif)';
  if (val <= 150) return 'Tidak Sehat (PP22 Exceeded)';
  return 'Sangat Tidak Sehat';
}

// Representativeness radius based on EPA 40 CFR Part 58 & KLHK guidelines
function getStationRepresentativenessRadius(siteType) {
  const s = String(siteType || '').toLowerCase();
  if (s.includes('traffic') || s.includes('roadside')) return 1000; // 1 km (Microscale / Roadside)
  if (s.includes('highway')) return 2000; // 2 km (Highway Corridor)
  if (s.includes('industrial')) return 5000; // 5 km (Neighborhood / Industrial)
  if (s.includes('urban')) return 10000; // 10 km (Urban Background)
  return 50000; // 50 km (Regional / Peatland / Remote Background)
}

// Initialization
// Chart.js Light Mode Defaults
if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#64748b';
  Chart.defaults.font.family = "'Brulia Text', sans-serif";
  Chart.defaults.plugins.tooltip.backgroundColor = '#0f172a';
  Chart.defaults.plugins.tooltip.titleColor = '#ffffff';
  Chart.defaults.plugins.tooltip.bodyColor = '#e2e8f0';
  Chart.defaults.plugins.tooltip.borderColor = '#334155';
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.plugins.tooltip.padding = 10;
}

document.addEventListener('DOMContentLoaded', async () => {
  setupSidebarToggle();
  setupTabEvents();
  setupFilterEvents();
  setupBufferEvents();
  setupReliabilityEvents();
  await loadAllData();
  document.getElementById('loadingOverlay').classList.add('hidden');
  renderDashboard();
  // Setup wind rose station selector (after data loaded)
  const wrSelect = document.getElementById('windRoseStationSelect');
  if (wrSelect) {
    wrSelect.addEventListener('change', () => {
      if (state.charts.windRose) {
        try { state.charts.windRose.destroy(); } catch(e) {}
        state.charts.windRose = null;
      }
      renderWindRose();
    });
  }
});

// Setup Sidebar Toggle (Logo AQ Click)
function setupSidebarToggle() {
  const toggleBtn = document.getElementById('sidebarToggleBtn');
  const dashboardBody = document.querySelector('.dashboard-body');
  if (!toggleBtn || !dashboardBody) return;

  function toggle() {
    const isCollapsed = dashboardBody.classList.toggle('sidebar-collapsed');
    toggleBtn.classList.toggle('collapsed', isCollapsed);
    toggleBtn.title = isCollapsed
      ? 'Klik logo untuk memunculkan kembali menu navigasi'
      : 'Klik logo untuk menyembunyikan menu navigasi';

    // Resize maps and charts after slide transition
    setTimeout(() => {
      if (state.map) state.map.invalidateSize();
      if (state.charts.windRose && typeof state.charts.windRose.resize === 'function') {
        state.charts.windRose.resize();
      }
      Object.values(state.charts).forEach(c => {
        if (c && typeof c.resize === 'function') c.resize();
      });
    }, 380);
  }

  toggleBtn.addEventListener('click', toggle);
  toggleBtn.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      toggle();
    }
  });
}

// Setup Navigation Tabs
function setupTabEvents() {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      
      const target = tab.dataset.tab;
      tab.classList.add('active');
      document.getElementById(target).classList.add('active');
      state.currentTab = target;

      // Invalidate map size if Tab 1 active
      if (target === 'tab1' && state.map) {
        setTimeout(() => state.map.invalidateSize(), 200);
      }
      // Tab 2: always re-render wind rose fresh when tab is activated
      if (target === 'tab2') {
        // Destroy cached chart so it can be rebuilt at correct canvas size
        if (state.charts.windRose) {
          try { state.charts.windRose.destroy(); } catch(e) {}
          state.charts.windRose = null;
        }
        // Small delay so CSS display:block takes effect before Chart.js measures canvas
        setTimeout(() => {
          renderWindRose();
          if (state.charts.trafficScatter && typeof state.charts.trafficScatter.resize === 'function') {
            state.charts.trafficScatter.resize();
          }
          if (state.charts.lagEffect && typeof state.charts.lagEffect.resize === 'function') {
            state.charts.lagEffect.resize();
          }
          if (state.charts.vulnerable && typeof state.charts.vulnerable.resize === 'function') {
            state.charts.vulnerable.resize();
          }
          if (state.charts.diseaseTrend && typeof state.charts.diseaseTrend.resize === 'function') {
            state.charts.diseaseTrend.resize();
          }
        }, 80);
      }
      if (target === 'tab3') {
        renderSensorReliabilityHeatmap();
      }
    });
  });
}

// Setup Filters
function setupFilterEvents() {
  const auditSelect = document.getElementById('statusFilterSelect');
  if (auditSelect) {
    auditSelect.addEventListener('change', (e) => {
      state.statusFilter = e.target.value;
      applyFilters();
    });
  }
}

function setupBufferEvents() {
  const bufferOn = document.getElementById('bufferOnButton');
  const bufferOff = document.getElementById('bufferOffButton');
  const bufferRadius = document.getElementById('bufferRadiusSelect');

  if (bufferOn) {
    bufferOn.addEventListener('click', () => setBufferEnabled(true));
  }
  if (bufferOff) {
    bufferOff.addEventListener('click', () => setBufferEnabled(false));
  }
  if (bufferRadius) {
    bufferRadius.addEventListener('change', (e) => {
      state.bufferRadius = e.target.value;
      updateBufferControls();
      if (state.bufferEnabled) {
        renderMap();
      }
    });
  }
  updateBufferControls();
}

function setupReliabilityEvents() {
  // Setup floating tooltip for reliability heatmap
  let tooltip = document.getElementById('reliabilityTooltip');
  if (!tooltip) {
    tooltip = document.createElement('div');
    tooltip.id = 'reliabilityTooltip';
    tooltip.className = 'reliability-tooltip';
    document.body.appendChild(tooltip);
  }

  const container = document.getElementById('sensorReliabilityHeatmap');
  if (container) {
    container.addEventListener('mouseover', (e) => {
      const cell = e.target.closest('.heat-cell');
      if (!cell) return;
      const d = cell.dataset;
      const statusClass = (d.status || 'ok').toLowerCase();
      tooltip.innerHTML = `
        <div style="font-weight:700; color:#ffffff; font-size:0.76rem; margin-bottom:3px;">${d.stn}</div>
        <div style="color:#94a3b8; font-size:0.65rem; margin-bottom:6px;">${d.prov} &bull; Status: <span class="status-badge-sm ${statusClass}">${d.status}</span></div>
        <div style="display:flex; justify-content:space-between; gap:14px; margin-bottom:2px;">
          <span style="color:#94a3b8;">Bulan:</span><strong style="color:#ffffff;">${d.month}</strong>
        </div>
        <div style="display:flex; justify-content:space-between; gap:14px; margin-bottom:2px;">
          <span style="color:#94a3b8;">Kelengkapan:</span><strong style="color:${getReliabilityColor(Number(d.pct))}">${d.pct}%</strong>
        </div>
        <div style="display:flex; justify-content:space-between; gap:14px;">
          <span style="color:#94a3b8;">Jam Observasi:</span><strong style="color:#ffffff;">${Number(d.valid).toLocaleString('id-ID')} / ${Number(d.expected).toLocaleString('id-ID')} jam</strong>
        </div>
      `;
      tooltip.style.display = 'block';
    });

    container.addEventListener('mousemove', (e) => {
      if (tooltip.style.display !== 'block') return;
      let x = e.clientX + 14;
      let y = e.clientY + 14;
      const tw = tooltip.offsetWidth || 230;
      const th = tooltip.offsetHeight || 120;
      if (x + tw > window.innerWidth - 10) x = e.clientX - tw - 12;
      if (y + th > window.innerHeight - 10) y = e.clientY - th - 12;
      tooltip.style.left = x + 'px';
      tooltip.style.top = y + 'px';
    });

    container.addEventListener('mouseout', (e) => {
      const cell = e.target.closest('.heat-cell');
      if (cell) tooltip.style.display = 'none';
    });
  }
}

function setBufferEnabled(enabled) {
  state.bufferEnabled = enabled;
  updateBufferControls();
  renderMap();
}

function updateBufferControls() {
  const bufferOn = document.getElementById('bufferOnButton');
  const bufferOff = document.getElementById('bufferOffButton');
  const note = document.getElementById('bufferNote');

  if (bufferOn) {
    bufferOn.classList.toggle('active', state.bufferEnabled);
    bufferOn.setAttribute('aria-pressed', String(state.bufferEnabled));
  }
  if (bufferOff) {
    bufferOff.classList.toggle('active', !state.bufferEnabled);
    bufferOff.setAttribute('aria-pressed', String(!state.bufferEnabled));
  }
  if (note) {
    if (!state.bufferEnabled) {
      note.textContent = 'Buffer nonaktif. Lingkaran jarak bukan model dispersi atau batas paparan polusi.';
    } else if (state.bufferRadius === 'adaptive') {
      note.textContent = 'Buffer aktif: Radius adaptif skala riil EPA/KLHK (Roadside 1 km, Industri 5 km, Urban 10 km, Peatland/Regional 50 km). Menunjukkan keterwakilan sensor, bukan dispersi asap.';
    } else {
      note.textContent = `Buffer aktif: Radius seragam ${Number(state.bufferRadius) / 1000} km. Lingkaran jarak bukan model dispersi atau batas paparan polusi.`;
    }
  }
}

// Load All JSON Files in Parallel
async function loadAllData() {
  try {
    const keys = Object.keys(DATA_PATHS);
    const bust = `?v=3.1_${Date.now()}`;
    const promises = keys.map(k => fetch(DATA_PATHS[k] + bust).then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status} fetching ${DATA_PATHS[k]}`);
      return r.json();
    }));
    const results = await Promise.all(promises);
    keys.forEach((k, idx) => {
      state.data[k] = results[idx];
    });
    console.log("Data JSON berhasil dimuat. Total stasiun Mawar Polusi:", Object.keys(state.data.windRose || {}).length);
  } catch (err) {
    console.error("Error loading JSON data:", err);
  }
}

function applyFilters() {
  renderKPIs();
  renderMap();
  renderRankingList();
  renderSiteTypeChart();
  renderTrafficScatter();
  renderAuditTable();
  renderSensorReliabilityHeatmap();
}

function renderDashboard() {
  renderKPIs();
  initMap();
  renderTrendMonthly();
  renderDiurnalHeatmap();
  renderSiteTypeChart();
  renderRankingList();
  
  // Tab 2 (wind rose rendered on first tab click to avoid 0x0 canvas issue)
  renderCorrelationMatrix();
  renderTrafficScatter();
  renderLagEffectChart();
  renderVulnerableChart();
  renderDiseaseChart();

  // Tab 3
  renderAuditCharts();
  renderAuditTable();
  renderIslandDistribution();
  renderGapAnalysisChart();
  renderPriorityMatrix();
  renderSensorReliabilityHeatmap();
}

// ==============================================================
// TAB 1 VISUALIZATIONS
// ==============================================================

function renderKPIs() {
  const kpi = state.data.kpi;
  if (!kpi) return;

  // Nilai awal dari ringkasan KPI nasional
  let pmVal = kpi.national_pm25_avg;
  let ikuVal = kpi.national_iku_avg;
  let pp22Val = kpi.compliance_pp22_pct;
  let whoVal = kpi.compliance_who_pct;

  // Jika ada filter aktif (misal Standardisasi Saja atau Status), hitung ulang secara dinamis
  if (state.data.stations && state.statusFilter !== 'ALL') {
    const activeStations = state.data.stations.filter(s => {
      if (state.statusFilter !== 'ALL' && s.status !== state.statusFilter) return false;
      return true;
    });

    if (activeStations.length > 0) {
      const validPm = activeStations.map(s => s.pm25_avg).filter(v => typeof v === 'number' && !isNaN(v));
      if (validPm.length > 0) {
        pmVal = Number((validPm.reduce((a, b) => a + b, 0) / validPm.length).toFixed(2));
        const abovePP22 = validPm.filter(v => v > 55).length;
        const aboveWHO = validPm.filter(v => v > 15).length;
        pp22Val = Number(((validPm.length - abovePP22) / validPm.length * 100).toFixed(1));
        whoVal = Number(((validPm.length - aboveWHO) / validPm.length * 100).toFixed(1));
      }
    }
  }

  // 1. Evaluasi PM2.5 (Mengikuti 4 Kategori Legenda: Hijau <=15, Kuning 15-35, Oranye 35-55, Merah >55)
  let pmClass = 'index-orange';
  let pmStatus = '35-55 Sensitif';
  if (pmVal <= 15) {
    pmClass = 'index-green';
    pmStatus = '≤15 WHO (Baik)';
  } else if (pmVal <= 35) {
    pmClass = 'index-yellow';
    pmStatus = '15-35 Sedang';
  } else if (pmVal <= 55) {
    pmClass = 'index-orange';
    pmStatus = '35-55 Sensitif';
  } else {
    pmClass = 'index-red';
    pmStatus = '>55 Kritis';
  }

  // 2. Evaluasi IKU (Standar KLHK RI: Hijau >=70, Kuning 60-70, Oranye 50-60, Merah <50)
  let ikuClass = 'index-green';
  let ikuStatus = '≥70 Baik (Target)';
  if (ikuVal >= 70) {
    ikuClass = 'index-green';
    ikuStatus = '≥70 Baik (Target)';
  } else if (ikuVal >= 60) {
    ikuClass = 'index-yellow';
    ikuStatus = '60-70 Sedang';
  } else if (ikuVal >= 50) {
    ikuClass = 'index-orange';
    ikuStatus = '50-60 Sensitif';
  } else {
    ikuClass = 'index-red';
    ikuStatus = '<50 Kritis';
  }

  // 3. Evaluasi Kepatuhan PP 22/2021 (Baku Mutu 55 ug/m3)
  let pp22Class = 'index-green';
  let pp22Status = 'Patuh Tinggi (Baik)';
  if (pp22Val >= 75) {
    pp22Class = 'index-green';
    pp22Status = 'Patuh Tinggi (Baik)';
  } else if (pp22Val >= 50) {
    pp22Class = 'index-yellow';
    pp22Status = 'Kepatuhan Sedang';
  } else if (pp22Val >= 25) {
    pp22Class = 'index-orange';
    pp22Status = 'Sensitif';
  } else {
    pp22Class = 'index-red';
    pp22Status = 'Kritis / Rendah';
  }

  // 4. Evaluasi Kepatuhan WHO Annual (Pedoman Ketat 15 ug/m3)
  let whoClass = 'index-red';
  let whoStatus = 'Kritis';
  if (whoVal >= 50) {
    whoClass = 'index-green';
    whoStatus = 'Tinggi (Baik)';
  } else if (whoVal >= 35) {
    whoClass = 'index-yellow';
    whoStatus = 'Sedang';
  } else if (whoVal >= 20) {
    whoClass = 'index-orange';
    whoStatus = 'Sensitif';
  } else {
    whoClass = 'index-red';
    whoStatus = 'Kritis';
  }

  // Tampilkan nilai ke elemen DOM
  const elPm = document.getElementById('kpiNationalPm25');
  const elIku = document.getElementById('kpiIkuAvg');
  const elPp22 = document.getElementById('kpiPp22Compliance');
  const elWho = document.getElementById('kpiWhoCompliance');

  if (elPm) elPm.innerHTML = `${pmVal} <span class="unit">µg/m³</span>`;
  if (elIku) elIku.innerHTML = `${ikuVal} <span class="unit">IKU</span>`;
  if (elPp22) elPp22.innerHTML = `${pp22Val}% <span class="unit">hari dalam setahun</span>`;
  if (elWho) elWho.innerHTML = `${whoVal}% <span class="unit">hari dalam setahun</span>`;

  // Terapkan warna kartu, efek glow, dan badge tag
  const applyCardStyle = (cardId, tagId, statusClass, statusLabel) => {
    const card = document.getElementById(cardId);
    const tag = document.getElementById(tagId);
    if (card) {
      card.classList.remove('index-green', 'index-yellow', 'index-orange', 'index-red', 'index-blue', 'index-purple');
      card.classList.add(statusClass);
    }
    if (tag) {
      tag.textContent = statusLabel;
    }
  };

  applyCardStyle('cardNationalPm25', 'tagNationalPm25', pmClass, pmStatus);
  applyCardStyle('cardIkuAvg', 'tagIkuAvg', ikuClass, ikuStatus);
  applyCardStyle('cardPp22Compliance', 'tagPp22Compliance', pp22Class, pp22Status);
  applyCardStyle('cardWhoCompliance', 'tagWhoCompliance', whoClass, whoStatus);
}

function initMap() {
  if (state.map) return;
  // Centered on Indonesia
  state.map = L.map('stationMap', {
    zoomControl: true,
    minZoom: 4,
    maxZoom: 10
  }).setView([-1.5, 118.0], 5);

  // Esri World Light Gray Canvas (Official Esri, 100% Free, NO API Key, NO Watermark)
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ | Data: AQMS KLHK',
    maxZoom: 16
  }).addTo(state.map);
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16
  }).addTo(state.map);

  renderMap();
}

function renderMap() {
  if (!state.map || !state.data.stations) return;

  // Clear existing markers
  state.mapMarkers.forEach(m => state.map.removeLayer(m));
  state.mapMarkers = [];
  state.mapBuffers.forEach(buffer => state.map.removeLayer(buffer));
  state.mapBuffers = [];

  const stations = state.data.stations.filter(s => {
    if (state.statusFilter !== 'ALL' && s.status !== state.statusFilter) return false;
    return true;
  });

  if (state.bufferEnabled) {
    stations.forEach(s => {
      if (!Number.isFinite(s.lat) || !Number.isFinite(s.lng)) return;
      const radiusMeters = state.bufferRadius === 'adaptive'
        ? getStationRepresentativenessRadius(s.site_type)
        : Number(state.bufferRadius);
      const buffer = L.circle([s.lat, s.lng], {
        radius: radiusMeters,
        color: '#2563eb',
        weight: 1.5,
        opacity: 0.85,
        fillColor: '#3b82f6',
        fillOpacity: 0.15,
        dashArray: '4, 4',
        interactive: false
      }).addTo(state.map);
      state.mapBuffers.push(buffer);
    });
  }

  stations.forEach(s => {
    const color = getAQIColor(s.pm25_avg);
    const isLogger = s.pm_from_ppm;
    const radius = state.bufferEnabled ? 4 : Math.max(7, Math.min(18, (s.pm25_avg || 20) / 4));

    const circle = L.circleMarker([s.lat, s.lng], {
      radius: radius,
      fillColor: color,
      color: isLogger ? '#f59e0b' : '#ffffff',
      weight: isLogger ? 2.5 : 1.5,
      opacity: 0.9,
      fillOpacity: 0.75,
      dashArray: isLogger ? '3, 3' : null
    });

    const loggerBadge = isLogger 
      ? `<span class="badge badge-logger">[Konversi Logger]</span>
         <div style="font-size:0.7rem; color:#f59e0b; margin-top:4px;">
           *Sensor datalogger terekspor dlm ppm. Dikonversi dg faktor 1000× kalibrasi baseline.
         </div>`
      : '';

    const popupHtml = `
      <div class="popup-title">${s.label}</div>
      <div style="margin-bottom:6px;">${loggerBadge}</div>
      <div class="popup-row">
        <span class="popup-label">Kota / Provinsi:</span>
        <span class="popup-value">${s.kota}, ${s.provinsi}</span>
      </div>
      <div class="popup-row">
        <span class="popup-label">Tipe Lokasi:</span>
        <span class="popup-value">${s.site_type}</span>
      </div>
      <div class="popup-row">
        <span class="popup-label">Jangkauan Sensor:</span>
        <span class="popup-value" style="color:#38bdf8; font-weight:600;">${(getStationRepresentativenessRadius(s.site_type) / 1000).toFixed(0)} km (Skala EPA)</span>
      </div>
      <div class="popup-row">
        <span class="popup-label">Rata-rata PM2.5:</span>
        <span class="popup-value" style="color:${color}; font-weight:bold;">${s.pm25_avg ?? 'N/A'} µg/m³</span>
      </div>
      <div class="popup-row">
        <span class="popup-label">Kategori Udara:</span>
        <span class="popup-value">${getAQILabel(s.pm25_avg)}</span>
      </div>
      <div class="popup-row">
        <span class="popup-label">Status Audit:</span>
        <span class="popup-value"><span class="badge badge-${s.status.toLowerCase()}">${s.status}</span></span>
      </div>
      <div class="popup-row">
        <span class="popup-label">Coverage Valid:</span>
        <span class="popup-value">${(s.coverage_pm25 * 100).toFixed(1)}%</span>
      </div>
    `;

    circle.bindTooltip(
      `<strong>${s.label}</strong><br>PM2.5: ${s.pm25_avg ?? 'N/A'} µg/m³`,
      { direction: 'top', sticky: true, opacity: 0.98, className: 'station-map-tooltip' }
    );
    circle.bindPopup(popupHtml);
    circle.addTo(state.map);
    state.mapMarkers.push(circle);
  });
}

function getReliabilityColor(pct) {
  if (pct >= 90) return '#10b981'; // >= 90% Sangat Baik
  if (pct >= 75) return '#84cc16'; // 75 - 89% Baik
  if (pct >= 50) return '#eab308'; // 50 - 74% Cukup
  if (pct >= 25) return '#f97316'; // 25 - 49% Kurang
  if (pct > 0)  return '#ef4444'; // > 0 - 24% Kritis
  return '#334155';               // 0% Kosong / Non-aktif
}

function renderSensorReliabilityHeatmap() {
  const container = document.getElementById('sensorReliabilityHeatmap');
  const data = state.data.sensorReliability;
  if (!container || !data) return;

  const summary = data.summary;
  const months = data.months;
  const statusFilter = state.statusFilter;

  // 1. Update KPI Summary
  const netValEl = document.getElementById('netCompletenessVal');
  const netSubEl = document.getElementById('netCompletenessDetail');
  const lowValEl = document.getElementById('lowestMonthVal');
  const lowSubEl = document.getElementById('lowestMonthDetail');
  const totStnEl = document.getElementById('totalMonitoredStations');
  const obsPerEl = document.getElementById('observationPeriodVal');

  if (netValEl) netValEl.textContent = `${summary.overall_completeness_pct}%`;
  if (netSubEl) netSubEl.textContent = `${summary.network_valid_hours.toLocaleString('id-ID')} dari ${summary.network_expected_hours.toLocaleString('id-ID')} jam valid`;
  if (lowValEl) lowValEl.textContent = `${summary.lowest_station_month.completeness_pct}%`;
  if (lowSubEl) lowSubEl.textContent = `${summary.lowest_station_month.station} (${summary.lowest_station_month.month_label})`;
  if (totStnEl) totStnEl.textContent = `${summary.total_stations} Stasiun (${summary.active_stations} Aktif)`;
  if (obsPerEl) obsPerEl.textContent = `${summary.period_months} Bulan (${summary.start_month} – ${summary.end_month})`;

  // 2. Filter Stations
  const filtered = data.stations.filter(s => statusFilter === 'ALL' || s.status === statusFilter);

  // Group months by year for multi-header table
  const yearGroups = {};
  months.forEach(m => {
    if (!yearGroups[m.year]) yearGroups[m.year] = [];
    yearGroups[m.year].push(m);
  });

  // 3. Build Table HTML
  let html = `<table class="reliability-heatmap-table">
    <thead>
      <tr class="year-row">
        <th rowspan="2" class="sticky-col">Stasiun & Wilayah</th>
        <th rowspan="2" class="sticky-status">Status QC</th>
        <th rowspan="2" style="width:75px; text-align:center;">Rata-rata</th>`;

  Object.keys(yearGroups).sort().forEach(yr => {
    const group = yearGroups[yr];
    const partialNotice = yr === '2026' ? ' (Jan–Okt*)' : ` (${group.length} Bulan)`;
    html += `<th colspan="${group.length}">Tahun ${yr}${partialNotice}</th>`;
  });

  html += `</tr><tr>`;

  months.forEach(m => {
    const isPart = m.is_partial;
    const title = `${m.full_label} (${m.days} hari = ${m.expected_hours} jam)${isPart ? ' [Bulan Parsial]' : ''}`;
    html += `<th title="${title}">${m.month_num}${isPart ? '*' : ''}</th>`;
  });

  html += `</tr></thead><tbody>`;

  filtered.forEach(stn => {
    const statusClass = (stn.status || 'ok').toLowerCase();
    const avgColor = getReliabilityColor(stn.overall_completeness_pct);

    html += `<tr>
      <td class="sticky-col">
        <div class="stn-cell-title" title="${stn.station}">${stn.station}</div>
        <div class="stn-cell-sub">${stn.provinsi} &bull; ${stn.island}</div>
      </td>
      <td class="sticky-status">
        <span class="status-badge-sm ${statusClass}">${stn.status}</span>
      </td>
      <td style="text-align:center;">
        <span style="font-family:'Brulia Text'; font-weight:700; color:${avgColor}; font-size:0.75rem;">
          ${stn.overall_completeness_pct}%
        </span>
      </td>`;

    stn.monthly.forEach(m => {
      const color = getReliabilityColor(m.completeness_pct);
      const textColor = (m.completeness_pct >= 50 && m.completeness_pct < 90) ? '#0f172a' : '#ffffff';
      const cellText = m.completeness_pct === 0 ? '0' : Math.round(m.completeness_pct);

      html += `<td>
        <span class="heat-cell"
              style="background:${color}; color:${textColor};"
              data-stn="${stn.station}"
              data-prov="${stn.provinsi} (${stn.island})"
              data-status="${stn.status}"
              data-month="${m.full_label}"
              data-pct="${m.completeness_pct}"
              data-valid="${m.valid_hours}"
              data-expected="${m.expected_hours}">
          ${cellText}
        </span>
      </td>`;
    });

    html += `</tr>`;
  });

  html += `</tbody></table>`;
  container.innerHTML = html;
}

function renderRankingList() {
  const container = document.getElementById('rankingLeaderboard');
  if (!container || !state.data.stations) return;

  let list = [...state.data.stations].filter(s => s.pm25_avg !== null);

  if (state.statusFilter !== 'ALL') {
    list = list.filter(s => s.status === state.statusFilter);
  }

  // Sort descending by PM2.5
  list.sort((a, b) => b.pm25_avg - a.pm25_avg);

  let html = `<div class="ranking-scroll-container">`;
  list.forEach((stn, idx) => {
    const isLogger = stn.pm_from_ppm;
    const badge = isLogger ? `<span class="badge badge-logger" title="Sensor datalogger ppm dikonversi ke ug/m3">* [Konversi Logger]</span>` : '';
    const exceedsPP22 = stn.pm25_avg > 55;
    const exceedsWHO = stn.pm25_avg > 15;

    html += `
      <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 12px; margin-bottom:6px; background:#f8f9fc; border:1px solid #e2e8f0; border-radius:8px; border-left:4px solid ${getAQIColor(stn.pm25_avg)};">
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-family:'Brulia Text'; font-size:0.75rem; color:#64748b; width:22px;">#${idx+1}</span>
          <div>
            <div style="font-weight:600; font-size:0.8rem;">${stn.label} ${badge}</div>
            <div style="font-size:0.7rem; color:#94a3b8;">${stn.island} &bull; ${stn.site_type}</div>
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-family:'Brulia Text'; font-weight:700; font-size:0.9rem; color:${getAQIColor(stn.pm25_avg)};">
            ${stn.pm25_avg} <span style="font-size:0.7rem; font-weight:normal;">µg/m³</span>
          </div>
          <div style="font-size:0.65rem; color:${exceedsPP22 ? '#ef4444' : (exceedsWHO ? '#f59e0b' : '#10b981')}">
            ${exceedsPP22 ? '> Baku Mutu PP22' : (exceedsWHO ? '> Pedoman WHO' : 'Memenuhi WHO')}
          </div>
        </div>
      </div>
    `;
  });
  html += `</div>`;
  container.innerHTML = html;
}

function renderTrendMonthly() {
  const ctx = document.getElementById('monthlyTrendChart');
  if (!ctx || !state.data.trendMonthly) return;

  const data = state.data.trendMonthly;
  const labels = data.labels;

  const datasets = [
    {
      label: 'Rata-rata Nasional',
      data: data.national,
      borderColor: '#3b82f6',
      backgroundColor: 'transparent',
      borderWidth: 3,
      tension: 0.3,
      pointRadius: 3,
      pointStyle: 'circle',
      fill: false
    }
  ];

  const islandColors = {
    'Kalimantan': '#ef4444',
    'Sumatera': '#f59e0b',
    'Jawa': '#8b5cf6',
    'Sulawesi': '#10b981',
    'Papua': '#06b6d4'
  };

  Object.keys(data.islands).forEach(isl => {
    datasets.push({
      label: isl,
      data: data.islands[isl],
      borderColor: islandColors[isl] || '#94a3b8',
      backgroundColor: 'transparent',
      borderWidth: 1.8,
      borderDash: isl === 'Kalimantan' ? [] : [4, 4],
      tension: 0.3,
      pointRadius: 2,
      pointStyle: 'circle',
      fill: false
    });
  });

  if (state.charts.monthlyTrend) state.charts.monthlyTrend.destroy();

  state.charts.monthlyTrend = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 26,
            color: '#475569',
            padding: 14,
            font: { size: 11, weight: '500' },
            generateLabels: (chart) => {
              const original = Chart.defaults.plugins.legend.labels.generateLabels(chart);
              return original.map(item => {
                item.pointStyle = 'line';
                const ds = chart.data.datasets[item.datasetIndex];
                if (ds) {
                  item.lineDash = ds.borderDash || [];
                  item.lineWidth = ds.borderWidth || 2;
                  item.strokeStyle = ds.borderColor;
                }
                return item;
              });
            }
          }
        },
        tooltip: {
          callbacks: {
            footer: (items) => {
              const label = items[0].label;
              const m = parseInt(label.split('-')[1]);
              if (m >= 7 && m <= 10) return 'Musim Kemarau / Episode Karhutla & Asap Gambut';
              return 'Musim Hujan / Dispersi Basah';
            }
          }
        }
      },
      scales: {
        x: { grid: { color: 'rgba(0,0,0,0.06)' }, ticks: { color: '#64748b' } },
        y: {
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: { color: '#64748b' },
          title: { display: true, text: 'Konsentrasi PM2.5 (µg/m³)', color: '#64748b' }
        }
      }
    }
  });
}

function renderDiurnalHeatmap() {
  const container = document.getElementById('diurnalHeatmapContainer');
  const selector = document.getElementById('diurnalGroupSelect');
  if (!container || !state.data.diurnal) return;

  const groupName = selector ? selector.value : 'Peatland';
  const data = state.data.diurnal[groupName];
  if (!data) return;

  let html = `<div style="overflow-x:auto; padding-bottom:14px;"><div class="heatmap-grid" style="grid-template-columns: 44px repeat(24, 1fr); min-width: 780px;">`;
  
  // Header hours (0-23)
  html += `<div></div>`;
  for (let h = 0; h < 24; h++) {
    html += `<div class="heatmap-label">${h}:00</div>`;
  }

  // Days
  data.days.forEach((day, dIdx) => {
    html += `<div class="heatmap-label" style="justify-content:flex-start; font-weight:600; padding-left:2px;">${day.substring(0,3)}</div>`;
    for (let h = 0; h < 24; h++) {
      const val = data.matrix[h] ? data.matrix[h][dIdx] : null;
      const color = val ? getAQIColor(val) : '#1e293b';
      const textColor = (val && val > 35) ? '#ffffff' : '#000000';
      html += `
        <div class="heatmap-cell" style="background:${color}; color:${textColor};" title="${day} ${h}:00 - PM2.5: ${val || 'N/A'} µg/m³">
          ${val ? Math.round(val) : '-'}
        </div>
      `;
    }
  });

  html += `</div></div>`;
  container.innerHTML = html;

  if (selector && !selector.dataset.initialized) {
    selector.dataset.initialized = 'true';
    selector.addEventListener('change', () => renderDiurnalHeatmap());
  }
}

function renderSiteTypeChart() {
  const ctx = document.getElementById('siteTypeCompareChart');
  if (!ctx || !state.data.siteType) return;

  const comp = state.data.siteType;
  const groups = Object.keys(comp.normal_season || {});

  const normalMedians = groups.map(g => comp.normal_season[g]?.median ?? 0);
  const fireMedians = groups.map(g => comp.fire_season[g]?.median ?? 0);

  if (state.charts.siteType) state.charts.siteType.destroy();

  state.charts.siteType = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: groups,
      datasets: [
        {
          label: 'Musim Normal (Hujan & Transisi)',
          data: normalMedians,
          backgroundColor: '#3b82f6',
          borderRadius: 4
        },
        {
          label: 'Musim Kritis Asap / Kemarau (Jul - Okt)',
          data: fireMedians,
          backgroundColor: '#ef4444',
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            boxWidth: 14,
            boxHeight: 14,
            borderRadius: 3,
            color: '#475569',
            padding: 14,
            font: { size: 11, weight: '500' }
          }
        },
        tooltip: {
          callbacks: {
            afterBody: (items) => {
              const idx = items[0].dataIndex;
              const group = groups[idx];
              const f = comp.fire_season[group];
              const n = comp.normal_season[group];
              return `Normal Q1-Q3: ${n?.q1} - ${n?.q3} µg/m³\nKemarau Q1-Q3: ${f?.q1} - ${f?.q3} µg/m³`;
            }
          }
        }
      },
      scales: {
        x: { grid: { color: 'rgba(0,0,0,0.06)' }, ticks: { color: '#64748b' } },
        y: {
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: { color: '#64748b' },
          title: { display: true, text: 'Median PM2.5 (µg/m³)', color: '#64748b' }
        }
      }
    }
  });
}

// ==============================================================
// TAB 2 VISUALIZATIONS
// ==============================================================

function renderCorrelationMatrix() {
  const container = document.getElementById('correlationMatrixTable');
  if (!container || !state.data.corr) return;

  const data = state.data.corr;
  const cols = data.columns;
  const matrix = data.matrix;

  const colNameMap = {
    'pm25': 'PM2.5',
    'pm10': 'PM10',
    'temperature_c': 'Suhu (°C)',
    'humidity_pct': 'Kelembapan (%)',
    'wind_speed_ms': 'Kec. Angin (m/s)',
    'so2': 'SO2',
    'no2': 'NO2',
    'co': 'CO',
    'o3': 'O3'
  };

  const getLabel = (c) => colNameMap[c] || c.toUpperCase();

  let html = `<table class="correlation-matrix-table"><thead><tr><th>Variabel</th>`;
  cols.forEach(c => html += `<th>${getLabel(c)}</th>`);
  html += `</tr></thead><tbody>`;

  matrix.forEach((row, i) => {
    html += `<tr><td>${getLabel(cols[i])}</td>`;
    row.forEach((val, j) => {
      let bg = 'transparent';
      let textColor = '#475569';
      if (val !== null) {
        if (val > 0) {
          const alpha = Math.min(0.85, Math.abs(val));
          bg = `rgba(59, 130, 246, ${alpha})`;
          if (alpha > 0.35) textColor = '#ffffff';
        } else if (val < 0) {
          const alpha = Math.min(0.85, Math.abs(val));
          bg = `rgba(239, 68, 68, ${alpha})`;
          if (alpha > 0.35) textColor = '#ffffff';
        }
      }
      const displayVal = val !== null ? (val === 1 ? '1.00' : val.toFixed(2)) : '-';
      html += `<td style="background:${bg}; color:${textColor};">${displayVal}</td>`;
    });
    html += `</tr>`;
  });
  html += `</tbody></table>`;
  container.innerHTML = html;
}

function renderWindRose() {
  const canvas = document.getElementById('windRoseChart');
  const selector = document.getElementById('windRoseStationSelect');
  const insightEl = document.getElementById('windRoseInsight');
  const maxEl = document.getElementById('roseMaxVal');
  const avgEl = document.getElementById('roseAvgVal');
  const minEl = document.getElementById('roseMinVal');
  const freqEl = document.getElementById('roseFreqVal');
  const gridEl = document.getElementById('windRoseDataGrid');

  if (!state.data.windRose) return;

  const stn = selector ? selector.value : 'SM2-01_Samarinda';
  const roseData = state.data.windRose[stn] || [];

  if (roseData.length === 0) {
    if (insightEl) insightEl.textContent = `Tidak ada data arah angin untuk stasiun ${stn}.`;
    return;
  }

  const labels = roseData.map(d => d.direction);
  const pmVals = roseData.map(d => d.pm25_avg);
  const freqs = roseData.map(d => d.frequency);

  // Analisis statistik arah angin & polutan
  const nonZero = roseData.filter(d => d.pm25_avg > 0);
  let maxItem = { direction: '-', pm25_avg: 0 };
  let minItem = { direction: '-', pm25_avg: 9999 };
  let dominantItem = { direction: '-', frequency: 0 };
  let sumPm = 0;
  let totalObs = 0;

  roseData.forEach(d => {
    if (d.pm25_avg > maxItem.pm25_avg) maxItem = d;
    if (d.pm25_avg > 0 && d.pm25_avg < minItem.pm25_avg) minItem = d;
    if (d.frequency > dominantItem.frequency) dominantItem = d;
    sumPm += d.pm25_avg * d.frequency;
    totalObs += d.frequency;
  });

  const avgVal = totalObs > 0 ? (sumPm / totalObs) : (nonZero.length > 0 ? nonZero.reduce((a, b) => a + b.pm25_avg, 0) / nonZero.length : 0);
  if (minItem.pm25_avg === 9999) minItem = { direction: '-', pm25_avg: 0 };

  // 1. Tampilkan Quick Metrics Bar
  if (maxEl) maxEl.innerHTML = `${maxItem.direction} &bull; ${maxItem.pm25_avg.toFixed(1)} <span style="font-size:0.65rem;font-weight:normal;">µg/m³</span>`;
  if (avgEl) avgEl.innerHTML = `${avgVal.toFixed(1)} <span style="font-size:0.65rem;font-weight:normal;">µg/m³</span>`;
  if (minEl) minEl.innerHTML = `${minItem.direction} &bull; ${minItem.pm25_avg.toFixed(1)} <span style="font-size:0.65rem;font-weight:normal;">µg/m³</span>`;
  if (freqEl) freqEl.innerHTML = `${dominantItem.direction} &bull; ${(dominantItem.frequency || 0).toLocaleString()} <span style="font-size:0.65rem;font-weight:normal;">jam</span>`;

  // 2. Tampilkan Insight Banner
  if (insightEl) {
    if (maxItem.pm25_avg > 0) {
      insightEl.innerHTML = `Polutan tertinggi terhembus dari arah <strong>${maxItem.direction}</strong> (<strong>${maxItem.pm25_avg.toFixed(1)} µg/m³</strong>) &bull; Angin paling sering dari <strong>${dominantItem.direction}</strong> (${(dominantItem.frequency || 0).toLocaleString()} jam observasi)`;
    } else {
      insightEl.innerHTML = `Data konsentrasi PM2.5 stasiun <strong>${stn}</strong> tercatat 0 µg/m³`;
    }
  }

  // 3. Tampilkan Data Grid 8 Arah Utama (Nilai Nyata Eksplisit di UI)
  if (gridEl) {
    const mainDirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    const dirNames = {
      'N': 'Utara (N)', 'NE': 'Timur Laut (NE)', 'E': 'Timur (E)', 'SE': 'Tenggara (SE)',
      'S': 'Selatan (S)', 'SW': 'Barat Daya (SW)', 'W': 'Barat (W)', 'NW': 'Barat Laut (NW)'
    };

    let gridHtml = '';
    mainDirs.forEach(d => {
      const match = roseData.find(x => x.direction === d) || { pm25_avg: 0, frequency: 0 };
      const val = match.pm25_avg;
      const cnt = match.frequency;
      const color = val > 55 ? '#ef4444' : (val > 35 ? '#f97316' : (val > 15 ? '#eab308' : (val > 0 ? '#10b981' : '#64748b')));
      const isMax = d === maxItem.direction;

      gridHtml += `
        <div class="rose-grid-cell ${isMax ? 'highlight' : ''}">
          <div class="rose-grid-dir">${d}</div>
          <div class="rose-grid-val" style="color: ${color};">${val > 0 ? val.toFixed(1) + '<span style="font-size:0.58rem;font-weight:normal;color:#64748b;margin-left:2px;">µg/m³</span>' : '-'}</div>
          <div class="rose-grid-sub">${cnt > 0 ? cnt.toLocaleString() + ' jam' : '0'}</div>
        </div>
      `;
    });
    gridEl.innerHTML = gridHtml;
  }

  // 4. Render Radar Chart Canvas
  if (!canvas) return;

  if (state.charts.windRose) {
    state.charts.windRose.destroy();
  }

  const maxVal = maxItem.pm25_avg || 50;
  const strokeColor = maxVal > 55 ? '#ef4444' : (maxVal > 35 ? '#f97316' : (maxVal > 15 ? '#eab308' : '#10b981'));
  const fillColor = maxVal > 55 ? 'rgba(239, 68, 68, 0.28)' : (maxVal > 35 ? 'rgba(249, 115, 22, 0.28)' : (maxVal > 15 ? 'rgba(234, 179, 8, 0.28)' : 'rgba(16, 185, 129, 0.28)'));
  const suggestedMaxVal = Math.max(30, Math.ceil((maxVal * 1.15) / 10) * 10);

  // Radar data points: gunakan nilai riil, spanGaps true agar terhubung rapi
  state.charts.windRose = new Chart(canvas, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [
        {
          label: `Rata-rata PM2.5 (${stn})`,
          data: pmVals,
          backgroundColor: fillColor,
          borderColor: strokeColor,
          borderWidth: 2,
          pointBackgroundColor: strokeColor,
          pointBorderColor: '#ffffff',
          pointBorderWidth: 1.5,
          pointRadius: 3.5,
          pointHoverRadius: 6,
          fill: true,
          spanGaps: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 350
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            color: '#64748b',
            font: { size: 11, family: 'Inter' },
            boxWidth: 12
          }
        },
        tooltip: {
          backgroundColor: '#0f172a',
          borderColor: 'rgba(255,255,255,0.15)',
          borderWidth: 1,
          titleColor: '#ffffff',
          bodyColor: '#cbd5e1',
          callbacks: {
            title: (items) => `Arah Angin: ${items[0].label}`,
            label: (item) => {
              const idx = item.dataIndex;
              const f = freqs[idx] || 0;
              const val = item.raw || 0;
              return [
                `Konsentrasi PM2.5: ${val.toFixed(2)} µg/m³`,
                `Total Observasi: ${f.toLocaleString()} jam`
              ];
            }
          }
        }
      },
      scales: {
        r: {
          beginAtZero: true,
          min: 0,
          suggestedMax: suggestedMaxVal,
          angleLines: { color: 'rgba(0,0,0,0.08)' },
          grid: { color: 'rgba(0,0,0,0.08)' },
          pointLabels: {
            color: '#475569',
            font: { size: 10, weight: 600, family: 'Inter' }
          },
          ticks: {
            backdropColor: 'transparent',
            color: '#64748b',
            font: { size: 9 },
            stepSize: Math.ceil(suggestedMaxVal / 4)
          }
        }
      }
    }
  });

  // Event listener for selector is set up once via setupTabEvents
}

function renderTrafficScatter() {
  const ctx = document.getElementById('trafficScatterChart');
  if (!ctx || !state.data.traffic) return;

  let points = state.data.traffic.filter(d => d.distance_to_road_m && d.pm25_avg);

  const scatterData = points.map(p => ({
    x: p.distance_to_road_m,
    y: p.pm25_avg,
    station: p.station,
    traffic: p.traffic_intensity,
    is_logger: p.is_logger
  }));

  if (state.charts.trafficScatter) state.charts.trafficScatter.destroy();

  state.charts.trafficScatter = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: 'Stasiun Standar',
          data: scatterData.filter(d => !d.is_logger),
          backgroundColor: '#3b82f6',
          pointRadius: 6
        },
        {
          label: 'Stasiun Logger [Konversi]',
          data: scatterData.filter(d => d.is_logger),
          backgroundColor: '#f59e0b',
          pointRadius: 8,
          pointStyle: 'triangle'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 8,
            color: '#475569',
            padding: 14,
            font: { size: 11, weight: '500' }
          }
        },
        tooltip: {
          backgroundColor: '#0f172a',
          borderColor: 'rgba(255, 255, 255, 0.18)',
          borderWidth: 1,
          padding: 10,
          titleColor: '#ffffff',
          titleFont: { size: 12, weight: 'bold', family: 'Inter' },
          bodyColor: '#cbd5e1',
          bodyFont: { size: 11, family: 'Inter' },
          displayColors: true,
          boxPadding: 4,
          callbacks: {
            title: (items) => items[0].raw.station,
            label: (ctx) => {
              const raw = ctx.raw;
              return [
                `Jarak ke Jalan: ${Number(raw.x).toLocaleString('id-ID')} m`,
                `Rata-rata PM2.5: ${raw.y.toFixed(1)} µg/m³`,
                `Intensitas Trafik: ${raw.traffic || 'N/A'}/jam`
              ];
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: { color: '#64748b' },
          title: { display: true, text: 'Jarak Stasiun ke Jalan Raya (meter)', color: '#64748b' }
        },
        y: {
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: { color: '#64748b' },
          title: { display: true, text: 'Konsentrasi Rata-rata PM2.5 (µg/m³)', color: '#64748b' }
        }
      }
    }
  });
}

function renderLagEffectChart() {
  const ctx = document.getElementById('lagEffectChart');
  if (!ctx || !state.data.lagEffect) return;

  const data = state.data.lagEffect;
  const lags = [0, 1, 2, 3, 4, 5, 6, 7];

  const datasets = [
    {
      label: 'Balita (<5 thn)',
      data: lags.map(l => data.resp_admissions_under5[l]?.correlation ?? 0),
      borderColor: '#ef4444',
      backgroundColor: 'transparent',
      tension: 0.3,
      borderWidth: 2.5
    },
    {
      label: 'Lansia (>60 thn)',
      data: lags.map(l => data.resp_admissions_over60[l]?.correlation ?? 0),
      borderColor: '#f59e0b',
      backgroundColor: 'transparent',
      tension: 0.3,
      borderWidth: 2.5
    },
    {
      label: 'Kunjungan Asma IGD',
      data: lags.map(l => data.asthma_emergency_cases[l]?.correlation ?? 0),
      borderColor: '#3b82f6',
      backgroundColor: 'transparent',
      borderDash: [5, 5],
      tension: 0.3,
      borderWidth: 2
    },
    {
      label: 'PPOK (COPD)',
      data: lags.map(l => data.copd_admissions[l]?.correlation ?? 0),
      borderColor: '#10b981',
      backgroundColor: 'transparent',
      borderDash: [3, 3],
      tension: 0.3,
      borderWidth: 2
    }
  ];

  if (state.charts.lagEffect) state.charts.lagEffect.destroy();

  state.charts.lagEffect = new Chart(ctx, {
    type: 'line',
    data: {
      labels: lags.map(l => `Lag ${l} Hari`),
      datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 26,
            color: '#475569',
            padding: 12,
            font: { size: 11, weight: '500' },
            generateLabels: (chart) => {
              const original = Chart.defaults.plugins.legend.labels.generateLabels(chart);
              return original.map(item => {
                item.pointStyle = 'line';
                const ds = chart.data.datasets[item.datasetIndex];
                if (ds) {
                  item.lineDash = ds.borderDash || [];
                  item.lineWidth = ds.borderWidth || 2;
                  item.strokeStyle = ds.borderColor;
                }
                return item;
              });
            }
          }
        },
        tooltip: {
          callbacks: {
            afterBody: (items) => {
              const lag = items[0].dataIndex;
              if (lag >= 1 && lag <= 3) return 'Puncak Efek Jeda: Reaksi inflamasi saluran nafas memuncak pada hari ke 1-3 pasca pajanan.';
              return '';
            }
          }
        }
      },
      scales: {
        x: { grid: { color: 'rgba(0,0,0,0.06)' }, ticks: { color: '#64748b' } },
        y: {
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: { color: '#64748b' },
          title: { display: true, text: 'Koefisien Korelasi Pearson (r)', color: '#64748b' }
        }
      }
    }
  });
}

function renderVulnerableChart() {
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
}

function renderDiseaseChart() {
  const ctx = document.getElementById('diseaseTrendChart');
  if (!ctx || !state.data.disease) return;

  const trend = state.data.disease.monthly_trends;
  const months = trend.asthma_emergency_cases?.months || [];

  if (state.charts.disease) state.charts.disease.destroy();

  state.charts.disease = new Chart(ctx, {
    type: 'line',
    data: {
      labels: months,
      datasets: [
        {
          label: 'PM2.5 Rata-rata (Sumbu Kiri)',
          data: trend.asthma_emergency_cases?.pm25 || [],
          borderColor: '#ef4444',
          backgroundColor: 'transparent',
          yAxisID: 'y1',
          borderWidth: 2.5,
          tension: 0.3
        },
        {
          label: 'Kasus IGD Asma (Sumbu Kanan)',
          data: trend.asthma_emergency_cases?.outcome || [],
          borderColor: '#3b82f6',
          backgroundColor: 'transparent',
          yAxisID: 'y2',
          borderWidth: 2,
          tension: 0.3
        },
        {
          label: 'Admisi PPOK (Sumbu Kanan)',
          data: trend.copd_admissions?.outcome || [],
          borderColor: '#10b981',
          backgroundColor: 'transparent',
          yAxisID: 'y2',
          borderWidth: 2,
          tension: 0.3
        },
        {
          label: 'Kardiovaskular (CVD)',
          data: trend.cvd?.outcome || [],
          borderColor: '#8b5cf6',
          backgroundColor: 'transparent',
          yAxisID: 'y2',
          borderWidth: 2,
          borderDash: [4, 4],
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 26,
            color: '#475569',
            padding: 12,
            font: { size: 11, weight: '500' },
            generateLabels: (chart) => {
              const original = Chart.defaults.plugins.legend.labels.generateLabels(chart);
              return original.map(item => {
                item.pointStyle = 'line';
                const ds = chart.data.datasets[item.datasetIndex];
                if (ds) {
                  item.lineDash = ds.borderDash || [];
                  item.lineWidth = ds.borderWidth || 2;
                  item.strokeStyle = ds.borderColor;
                }
                return item;
              });
            }
          }
        }
      },
      scales: {
        x: { grid: { color: 'rgba(0,0,0,0.06)' }, ticks: { color: '#64748b' } },
        y1: {
          type: 'linear',
          position: 'left',
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: { color: '#ef4444' },
          title: { display: true, text: 'PM2.5 (µg/m³)', color: '#ef4444' }
        },
        y2: {
          type: 'linear',
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { color: '#3b82f6' },
          title: { display: true, text: 'Rata-rata Kasus RS / Hari', color: '#3b82f6' }
        }
      }
    }
  });
}

// ==============================================================
// TAB 3 VISUALIZATIONS
// ==============================================================

function renderAuditCharts() {
  const ctx = document.getElementById('auditStatusDonutChart');
  if (!ctx || !state.data.audit) return;

  const summary = state.data.audit.status_summary;

  if (state.charts.auditDonut) state.charts.auditDonut.destroy();

  state.charts.auditDonut = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['OK (Layak)', 'CAUTION (Perhatian)', 'EXCLUDED (Gagal/Nonaktif)'],
      datasets: [
        {
          data: [summary.OK || 22, summary.CAUTION || 4, summary.EXCLUDED || 1],
          backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
          borderWidth: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { color: '#64748b' } }
      },
      cutout: '70%'
    }
  });
}

function renderAuditTable() {
  const container = document.getElementById('auditTableContainer');
  if (!container || !state.data.audit) return;

  let stations = state.data.audit.stations;

  if (state.statusFilter !== 'ALL') {
    stations = stations.filter(s => s.status === state.statusFilter);
  }

  let html = `
    <div class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>Stasiun</th>
            <th>Pulau</th>
            <th>Status</th>
            <th>Coverage Valid</th>
            <th>Jam Beku (Frozen)</th>
            <th>Overrange</th>
            <th>Median PM2.5</th>
            <th>P95 PM2.5</th>
            <th>Catatan Teknis</th>
          </tr>
        </thead>
        <tbody>
  `;

  stations.forEach(s => {
    const isLogger = s.is_logger;
    const loggerBadge = isLogger ? `<span class="badge badge-logger">[Konversi Logger]</span>` : '';
    html += `
      <tr>
        <td style="font-weight:600;">${s.label} ${loggerBadge}</td>
        <td>${s.island}</td>
        <td><span class="badge badge-${s.status.toLowerCase()}">${s.status}</span></td>
        <td class="cell-value">${(s.coverage_pm25 * 100).toFixed(1)}%</td>
        <td class="cell-value">${s.frozen_hours} jam</td>
        <td class="cell-value">${s.overrange_hours} jam</td>
        <td class="cell-value">${s.pm25_median ?? '-'} µg/m³</td>
        <td class="cell-value">${s.pm25_p95 ?? '-'} µg/m³</td>
        <td style="font-size:0.75rem; color:#94a3b8;">${s.catatan || (isLogger ? 'Unit sensor logger ppm dikonversi ke ug/m3' : 'Operasional normal')}</td>
      </tr>
    `;
  });

  html += `</tbody></table></div>`;
  container.innerHTML = html;
}

function renderIslandDistribution() {
  const ctx = document.getElementById('islandBarChart');
  if (!ctx || !state.data.islands) return;

  const islands = state.data.islands.islands;
  const labels = islands.map(i => i.island);
  const okCounts = islands.map(i => i.status_ok);
  const cautionCounts = islands.map(i => i.status_caution);
  const excludedCounts = islands.map(i => i.status_excluded);

  if (state.charts.islandBar) state.charts.islandBar.destroy();

  state.charts.islandBar = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Status OK', data: okCounts, backgroundColor: '#10b981', stack: 'stack0' },
        { label: 'Status CAUTION', data: cautionCounts, backgroundColor: '#f59e0b', stack: 'stack0' },
        { label: 'Status EXCLUDED', data: excludedCounts, backgroundColor: '#ef4444', stack: 'stack0' }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#64748b' } }
      },
      scales: {
        x: { grid: { color: 'rgba(0,0,0,0.06)' }, ticks: { color: '#64748b' } },
        y: {
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: { color: '#64748b' },
          title: { display: true, text: 'Jumlah Stasiun AQMS', color: '#64748b' }
        }
      }
    }
  });
}

function renderGapAnalysisChart() {
  const ctx = document.getElementById('gapScatterChart');
  if (!ctx || !state.data.gap) return;

  const points = state.data.gap.map(g => ({
    x: g.total_resp_cases,
    y: g.sensor_coverage * 100,
    station: g.station,
    status: g.sensor_status,
    is_anomaly: g.is_anomaly,
    island: g.island
  }));

  if (state.charts.gapScatter) state.charts.gapScatter.destroy();

  state.charts.gapScatter = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: 'Kondisi Normal / Terpantau Baik',
          data: points.filter(p => !p.is_anomaly),
          backgroundColor: '#10b981',
          pointRadius: 6
        },
        {
          label: 'Titik Kritis Anomali (Beban Sakit Tinggi, Sensor Bermasalah)',
          data: points.filter(p => p.is_anomaly),
          backgroundColor: '#ef4444',
          pointRadius: 9,
          pointHoverRadius: 12
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#64748b' } },
        tooltip: {
          backgroundColor: '#0f172a',
          borderColor: 'rgba(255, 255, 255, 0.18)',
          borderWidth: 1,
          padding: 10,
          titleColor: '#ffffff',
          titleFont: { size: 12, weight: 'bold', family: 'Inter' },
          bodyColor: '#cbd5e1',
          bodyFont: { size: 11, family: 'Inter' },
          displayColors: true,
          boxPadding: 4,
          callbacks: {
            title: (items) => {
              const r = items[0].raw;
              return `${r.station} (${r.island})`;
            },
            label: (c) => {
              const r = c.raw;
              const anomalyTag = r.is_anomaly ? ' [ANOMALI KRITIS]' : ' [Normal]';
              return [
                `Beban Kasus RS: ${Number(r.x).toLocaleString('id-ID')} jiwa`,
                `Ketersediaan Sensor: ${r.y.toFixed(1)}%`,
                `Status: ${r.status}${anomalyTag}`
              ];
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: { color: '#64748b' },
          title: { display: true, text: 'Total Beban Kasus Respiratorik RS (Jiwa)', color: '#64748b' }
        },
        y: {
          grid: { color: 'rgba(0,0,0,0.06)' },
          ticks: { color: '#64748b' },
          title: { display: true, text: 'Keandalan / Coverage Sensor (%)', color: '#64748b' }
        }
      }
    }
  });
}

function renderPriorityMatrix() {
  const container = document.getElementById('priorityMatrixContainer');
  if (!container || !state.data.priority) return;

  const items = state.data.priority.items;

  let html = `
    <div class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th style="font-size:0.75rem; font-weight:700; color:#1e293b;">Tingkat Prioritas</th>
            <th style="font-size:0.75rem; font-weight:700; color:#1e293b;">Lokasi / Wilayah Target</th>
            <th style="font-size:0.75rem; font-weight:700; color:#1e293b;">Wilayah / Pulau</th>
            <th style="font-size:0.75rem; font-weight:700; color:#1e293b;">Masalah Utama</th>
            <th style="font-size:0.75rem; font-weight:700; color:#1e293b;">Rekomendasi Kebijakan Tindakan</th>
          </tr>
        </thead>
        <tbody>
  `;

  items.forEach(item => {
    const pClass = `priority-${item.priority}`;
    html += `
      <tr>
        <td><span class="priority-badge ${pClass}">Prioritas ${item.priority}: ${item.priority_label}</span></td>
        <td style="font-weight:700; color:#0f172a; font-size:0.88rem; letter-spacing:-0.2px;">${item.label}</td>
        <td style="color:#334155; font-weight:600; font-size:0.82rem;">${item.island || '-'}</td>
        <td style="color:#b45309; font-weight:600; font-size:0.82rem;">${item.issue}</td>
        <td style="color:#1d4ed8; font-weight:600; font-size:0.84rem; white-space:normal; line-height:1.45;">${item.recommendation}</td>
      </tr>
    `;
  });

  html += `</tbody></table></div>`;
  container.innerHTML = html;
}

// ==============================================================
