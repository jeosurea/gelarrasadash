/**
 * AQMS DASHBOARD - Interactive Visualizations & Data Handler
 * Powered by Leaflet.js, Chart.js, and Vanilla Modern JS
 */

// Global State
const state = {
  currentTab: 'tab1',
  filterStandardizedOnly: false,
  statusFilter: 'ALL', // 'ALL', 'OK', 'CAUTION', 'EXCLUDED'
  sensitivityFactor: 1.0,
  data: {},
  charts: {},
  map: null,
  mapMarkers: [],
  mapBuffers: [],
  bufferEnabled: false,
  bufferRadius: 'adaptive',
  lisaMap: null,
  lisaMarkers: []
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
  traffic: 'data/json/traffic_scatter.json',
  lagEffect: 'data/json/lag_effect.json',
  vulnerable: 'data/json/vulnerable_groups.json',
  disease: 'data/json/disease_specific.json',
  audit: 'data/json/station_audit.json',
  islands: 'data/json/island_distribution.json',
  priority: 'data/json/priority_matrix.json',
  gap: 'data/json/gap_analysis.json',
  sensitivity: 'data/json/sensitivity_data.json'
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
document.addEventListener('DOMContentLoaded', async () => {
  setupTabEvents();
  setupFilterEvents();
  setupSpatialEvents();
  await loadAllData();
  document.getElementById('loadingOverlay').classList.add('hidden');
  renderDashboard();
});

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
      if (target === 'tab3' && state.lisaMap) {
        setTimeout(() => {
          state.lisaMap.invalidateSize();
          renderSpatialAutocorrelation();
        }, 200);
      }
    });
  });
}

// Setup Filters
function setupFilterEvents() {
  const toggleAll = document.getElementById('toggleAllStations');
  const toggleStd = document.getElementById('toggleStdOnly');
  const auditSelect = document.getElementById('statusFilterSelect');
  const slider = document.getElementById('sensitivitySlider');

  if (toggleAll && toggleStd) {
    toggleAll.addEventListener('click', () => {
      toggleAll.classList.add('active');
      toggleStd.classList.remove('active');
      state.filterStandardizedOnly = false;
      applyFilters();
    });

    toggleStd.addEventListener('click', () => {
      toggleStd.classList.add('active');
      toggleAll.classList.remove('active');
      state.filterStandardizedOnly = true;
      applyFilters();
    });
  }

  if (auditSelect) {
    auditSelect.addEventListener('change', (e) => {
      state.statusFilter = e.target.value;
      applyFilters();
    });
  }

  if (slider) {
    slider.addEventListener('input', (e) => {
      const val = parseInt(e.target.value);
      state.sensitivityFactor = val / 1000;
      document.getElementById('sensitivityFactorVal').innerText = val + '×';
      updateSensitivityUI(val);
    });
  }
}

function setupSpatialEvents() {
  const bufferOn = document.getElementById('bufferOnButton');
  const bufferOff = document.getElementById('bufferOffButton');
  const bufferRadius = document.getElementById('bufferRadiusSelect');
  const islandSelect = document.getElementById('spatialIslandSelect');
  const neighborsSelect = document.getElementById('spatialNeighborsSelect');
  const variableSelect = document.getElementById('spatialVariableSelect');
  const alternativeSelect = document.getElementById('spatialAlternativeSelect');
  const alphaSelect = document.getElementById('spatialAlphaSelect');
  const permutationInput = document.getElementById('permutationCountInput');
  const permutationValue = document.getElementById('permutationCountValue');

  if (bufferOn) bufferOn.addEventListener('click', () => setBufferEnabled(true));
  if (bufferOff) bufferOff.addEventListener('click', () => setBufferEnabled(false));

  if (bufferRadius) {
    bufferRadius.addEventListener('change', (event) => {
      const val = event.target.value;
      state.bufferRadius = val === 'adaptive' ? 'adaptive' : Number(val);
      updateBufferControls();
      renderMap();
    });
  }

  updateBufferControls();

  if (islandSelect) {
    islandSelect.addEventListener('change', () => {
      updateNeighborOptions();
      renderSpatialAutocorrelation();
    });
  }

  if (neighborsSelect) {
    neighborsSelect.addEventListener('change', renderSpatialAutocorrelation);
  }

  if (variableSelect) {
    variableSelect.addEventListener('change', () => {
      updateNeighborOptions();
      renderSpatialAutocorrelation();
    });
  }

  if (alternativeSelect) alternativeSelect.addEventListener('change', renderSpatialAutocorrelation);
  if (alphaSelect) alphaSelect.addEventListener('change', renderSpatialAutocorrelation);
  if (permutationInput) {
    permutationInput.addEventListener('input', () => {
      if (permutationValue) permutationValue.value = permutationInput.value;
      renderSpatialAutocorrelation();
    });
    if (permutationValue) permutationValue.value = permutationInput.value;
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
    const promises = keys.map(k => fetch(DATA_PATHS[k]).then(r => r.json()));
    const results = await Promise.all(promises);
    keys.forEach((k, idx) => {
      state.data[k] = results[idx];
    });
  } catch (err) {
    console.error("Error loading JSON data:", err);
  }
}

function applyFilters() {
  renderMap();
  renderRankingList();
  renderSiteTypeChart();
  renderTrafficScatter();
  renderAuditTable();
}

function renderDashboard() {
  renderKPIs();
  initMap();
  renderTrendMonthly();
  renderDiurnalHeatmap();
  renderSiteTypeChart();
  renderRankingList();
  
  // Tab 2
  renderCorrelationMatrix();
  renderWindRose();
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
  renderSpatialAutocorrelation();

  // Sensitivity
  initSensitivity();
}

// ==============================================================
// TAB 1 VISUALIZATIONS
// ==============================================================

function renderKPIs() {
  const kpi = state.data.kpi;
  if (!kpi) return;

  document.getElementById('kpiNationalPm25').innerHTML = `${kpi.national_pm25_avg} <span class="unit">µg/m³</span>`;
  document.getElementById('kpiIkuAvg').innerHTML = `${kpi.national_iku_avg} <span class="unit">IKU</span>`;
  document.getElementById('kpiPp22Compliance').innerHTML = `${kpi.compliance_pp22_pct}%`;
  document.getElementById('kpiWhoCompliance').innerHTML = `${kpi.compliance_who_pct}%`;
}

function initMap() {
  if (state.map) return;
  // Centered on Indonesia
  state.map = L.map('stationMap', {
    zoomControl: true,
    minZoom: 4,
    maxZoom: 10
  }).setView([-1.5, 118.0], 5);

  // Esri World Dark Gray Canvas tiles (Clean dark theme, no watermark, 100% free without API key)
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ | Data: AQMS KLHK',
    maxZoom: 16
  }).addTo(state.map);
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
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
    if (state.filterStandardizedOnly && s.pm_from_ppm) return false;
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
        color: '#38bdf8',
        weight: 1.5,
        opacity: 0.85,
        fillColor: '#38bdf8',
        fillOpacity: 0.12,
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

function renderSpatialAutocorrelation() {
  const stations = state.data.stations;
  const islandSelect = document.getElementById('spatialIslandSelect');
  const variableSelect = document.getElementById('spatialVariableSelect');
  const alternativeSelect = document.getElementById('spatialAlternativeSelect');
  const alphaSelect = document.getElementById('spatialAlphaSelect');
  const permutationInput = document.getElementById('permutationCountInput');
  if (!stations || !islandSelect || !variableSelect || !alternativeSelect || !alphaSelect || !permutationInput) return;

  const variable = variableSelect.value;
  const variableLabel = variableSelect.options[variableSelect.selectedIndex].textContent;
  const alternative = alternativeSelect.value;
  const alpha = Number(alphaSelect.value);
  const permutationCount = Number(permutationInput.value);
  const eligible = stations.filter(s => s.status === 'OK' && !s.pm_from_ppm &&
    Number.isFinite(s.spatial_values?.[variable]) && Number.isFinite(s.lat) && Number.isFinite(s.lng));
  const islandCounts = eligible.reduce((counts, station) => {
    counts[station.island] = (counts[station.island] || 0) + 1;
    return counts;
  }, {});
  const islands = Object.keys(islandCounts).filter(island => islandCounts[island] >= 4).sort();

  if (!islands.length) {
    updateSpatialSummary(null, 'Tidak ada pulau dengan minimal empat stasiun yang memenuhi kriteria QA.');
    return;
  }

  const previousIsland = islandSelect.value;
  islandSelect.innerHTML = islands.map(island =>
    `<option value="${island}">${island} (${islandCounts[island]} stasiun)</option>`
  ).join('');
  islandSelect.value = islands.includes(previousIsland) ? previousIsland : islands[0];
  updateNeighborOptions();

  const islandStations = eligible.filter(s => s.island === islandSelect.value);
  const requestedK = Number(document.getElementById('spatialNeighborsSelect').value) || 4;
  const k = Math.min(requestedK, islandStations.length - 1);
  const result = calculateMoranStatistics(islandStations, k, variable, alternative, alpha, permutationCount);

  if (!result) {
    updateSpatialSummary(null, 'Nilai PM2.5 pada pulau ini tidak bervariasi; Moran tidak dapat dihitung.');
    return;
  }

  const denseWeightsNote = k === islandStations.length - 1
    ? ` Catatan: k=${k} memasukkan semua stasiun lain sebagai tetangga, sehingga pola kedekatan lokal tidak dapat dibedakan.`
    : '';
  updateSpatialSummary(result, `Variabel ${variableLabel}; hipotesis ${alternativeLabel(alternative)}; α=${alpha}; ${permutationCount} simulasi. Analisis mencakup ${islandStations.length} stasiun ${islandSelect.value}, status OK dan tanpa konversi logger; tetangga ${k}-NN dalam pulau. LISA dikoreksi FDR. Hasil bersifat eksploratif karena jumlah stasiun per pulau terbatas.${denseWeightsNote}`);
  renderLisaMap(result);
}

function updateNeighborOptions() {
  const islandSelect = document.getElementById('spatialIslandSelect');
  const neighborsSelect = document.getElementById('spatialNeighborsSelect');
  const variable = document.getElementById('spatialVariableSelect')?.value;
  if (!islandSelect || !neighborsSelect || !state.data.stations || !variable) return;

  const count = state.data.stations.filter(s => s.island === islandSelect.value && s.status === 'OK' &&
    !s.pm_from_ppm && Number.isFinite(s.spatial_values?.[variable]) && Number.isFinite(s.lat) && Number.isFinite(s.lng)).length;
  const maxK = Math.min(5, count - 1);
  const previousK = Number(neighborsSelect.value) || 4;
  neighborsSelect.innerHTML = Array.from({ length: Math.max(0, maxK - 1) }, (_, index) => index + 2)
    .map(k => `<option value="${k}">${k}</option>`).join('');
  neighborsSelect.value = String(Math.min(previousK, maxK));
}

function calculateMoranStatistics(stations, k, variable, alternative, alpha, permutationCount) {
  const values = stations.map(s => s.spatial_values[variable]);
  const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
  const deviations = values.map(value => value - mean);
  const standardDeviation = Math.sqrt(deviations.reduce((sum, value) => sum + value * value, 0) / values.length);
  if (!standardDeviation || !Number.isFinite(standardDeviation)) return null;

  const z = deviations.map(value => value / standardDeviation);
  const denominator = z.reduce((sum, value) => sum + value * value, 0);
  const neighbors = stations.map((station, index) => stations
    .map((candidate, candidateIndex) => ({
      index: candidateIndex,
      distance: candidateIndex === index ? Infinity : haversineKm(station.lat, station.lng, candidate.lat, candidate.lng)
    }))
    .sort((a, b) => a.distance - b.distance)
    .slice(0, k)
    .map(candidate => candidate.index));
  const globalI = moranIndex(z, neighbors, denominator);
  const expectedGlobal = -1 / (stations.length - 1);
  const randomSeed = stations.reduce((seed, station) => seed + station.label.length, 0) +
    [...variable].reduce((seed, character) => seed + character.charCodeAt(0), 0);
  const globalRandom = seededRandom(randomSeed);
  let globalExtreme = 0;

  for (let iteration = 0; iteration < permutationCount; iteration++) {
    const permuted = shuffle(z, globalRandom);
    const permutedI = moranIndex(permuted, neighbors, denominator);
    if (isAtLeastAsExtreme(permutedI, globalI, expectedGlobal, alternative)) globalExtreme++;
  }

  const m2 = denominator / stations.length;
  const localResults = stations.map((station, index) => {
    const lag = neighbors[index].reduce((sum, neighborIndex) => sum + z[neighborIndex], 0) / k;
    const localI = z[index] * lag / m2;
    const expectedLocal = z[index] * (-z[index] / (stations.length - 1)) / m2;
    const candidates = z.filter((_, candidateIndex) => candidateIndex !== index);
    const stationSeed = randomSeed + station.label.split('').reduce((sum, character) => sum + character.charCodeAt(0), 0);
    const random = seededRandom(stationSeed);
    let extreme = 0;

    for (let iteration = 0; iteration < permutationCount; iteration++) {
      const sampled = shuffle(candidates, random).slice(0, k);
      const permutedLag = sampled.reduce((sum, value) => sum + value, 0) / k;
      const permutedI = z[index] * permutedLag / m2;
      if (isAtLeastAsExtreme(permutedI, localI, expectedLocal, alternative)) extreme++;
    }

    return { station, z: z[index], lag, localI, p: (extreme + 1) / (permutationCount + 1) };
  });

  applyFdrCorrection(localResults);
  localResults.forEach(result => {
    if (result.q > alpha) result.cluster = 'NS';
    else if (result.z >= 0 && result.lag >= 0) result.cluster = 'HH';
    else if (result.z < 0 && result.lag < 0) result.cluster = 'LL';
    else if (result.z >= 0) result.cluster = 'HL';
    else result.cluster = 'LH';
  });

  return {
    stations: localResults,
    globalI,
    globalP: (globalExtreme + 1) / (permutationCount + 1),
    globalExtreme,
    expectedGlobal,
    variable,
    alternative,
    alpha,
    permutationCount,
    k
  };
}

function isAtLeastAsExtreme(simulated, observed, expected, alternative) {
  if (alternative === 'positive') return simulated + 1e-12 >= observed;
  if (alternative === 'negative') return simulated - 1e-12 <= observed;
  return Math.abs(simulated - expected) + 1e-12 >= Math.abs(observed - expected);
}

function alternativeLabel(alternative) {
  if (alternative === 'positive') return 'sisi atas/positif';
  if (alternative === 'negative') return 'sisi bawah/negatif';
  return 'dua sisi';
}

function seededRandom(seed) {
  let value = seed || 1;
  return () => {
    value ^= value << 13;
    value ^= value >>> 17;
    value ^= value << 5;
    return (value >>> 0) / 4294967296;
  };
}

function shuffle(values, random) {
  const shuffled = values.slice();
  for (let index = shuffled.length - 1; index > 0; index--) {
    const target = Math.floor(random() * (index + 1));
    [shuffled[index], shuffled[target]] = [shuffled[target], shuffled[index]];
  }
  return shuffled;
}

function moranIndex(values, neighbors, denominator) {
  const numerator = neighbors.reduce((sum, neighborIndexes, index) => {
    const lag = neighborIndexes.reduce((neighborSum, neighborIndex) => neighborSum + values[neighborIndex], 0) / neighborIndexes.length;
    return sum + values[index] * lag;
  }, 0);
  return numerator / denominator;
}

function haversineKm(lat1, lng1, lat2, lng2) {
  const radians = degrees => degrees * Math.PI / 180;
  const deltaLat = radians(lat2 - lat1);
  const deltaLng = radians(lng2 - lng1);
  const a = Math.sin(deltaLat / 2) ** 2 + Math.cos(radians(lat1)) * Math.cos(radians(lat2)) * Math.sin(deltaLng / 2) ** 2;
  return 6371 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function applyFdrCorrection(results) {
  const ordered = results.slice().sort((a, b) => a.p - b.p);
  let adjusted = 1;
  for (let index = ordered.length - 1; index >= 0; index--) {
    adjusted = Math.min(adjusted, ordered[index].p * ordered.length / (index + 1));
    ordered[index].q = Math.min(1, adjusted);
  }
}

function updateSpatialSummary(result, message) {
  const globalValue = document.getElementById('globalMoranValue');
  const globalP = document.getElementById('globalMoranP');
  const permutationDetail = document.getElementById('globalMoranPermutationDetail');
  const stationCount = document.getElementById('spatialStationCount');
  const interpretation = document.getElementById('globalMoranInterpretation');
  const messageNode = document.getElementById('spatialAnalysisMessage');
  if (!globalValue || !globalP || !permutationDetail || !stationCount || !interpretation || !messageNode) return;

  if (!result) {
    globalValue.textContent = '-';
    globalP.textContent = '-';
    permutationDetail.textContent = 'Simulasi ekstrem: -';
    stationCount.textContent = '0';
    interpretation.textContent = 'Analisis tidak tersedia';
    messageNode.textContent = message;
    return;
  }

  globalValue.textContent = result.globalI.toFixed(3);
  globalP.textContent = result.globalP.toFixed(3);
  permutationDetail.textContent = `${result.globalExtreme} dari ${result.permutationCount} simulasi ekstrem`;
  stationCount.textContent = String(result.stations.length);
  document.getElementById('globalMoranPLabel').textContent = `p-value ${alternativeLabel(result.alternative)}`;
  document.getElementById('permutationSummary').textContent = String(result.permutationCount);
  if (result.globalP <= result.alpha) {
    const positive = result.globalI > result.expectedGlobal;
    interpretation.textContent = positive ? 'Autokorelasi positif signifikan' : 'Autokorelasi negatif signifikan';
  } else {
    interpretation.textContent = `Tidak signifikan pada α = ${result.alpha}`;
  }
  messageNode.textContent = `${message} p-value global memakai koreksi Monte Carlo (+1); p lokal diuji dengan simulasi kondisional dan dikoreksi Benjamini-Hochberg.`;
}

function renderLisaMap(result) {
  const mapNode = document.getElementById('lisaMap');
  if (!mapNode || typeof L === 'undefined') return;

  if (!state.lisaMap) {
    state.lisaMap = L.map(mapNode, { zoomControl: true, minZoom: 4, maxZoom: 12 }).setView([-2, 118], 4);
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
      maxZoom: 16
    }).addTo(state.lisaMap);
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 16
    }).addTo(state.lisaMap);
  }

  state.lisaMarkers.forEach(marker => state.lisaMap.removeLayer(marker));
  state.lisaMarkers = [];
  const colors = { HH: '#ef4444', LL: '#10b981', HL: '#f59e0b', LH: '#38bdf8', NS: '#94a3b8' };

  result.stations.forEach(item => {
    const marker = L.circleMarker([item.station.lat, item.station.lng], {
      radius: 9,
      fillColor: colors[item.cluster],
      color: '#f8fafc',
      weight: 1.5,
      fillOpacity: 0.9
    }).bindPopup(`<strong>${item.station.label}</strong><br>${result.variable.toUpperCase()}: ${item.station.spatial_values[result.variable].toFixed(2)}<br>Klaster: ${item.cluster}<br>Local I: ${item.localI.toFixed(3)}<br>p: ${item.p.toFixed(3)} · q: ${item.q.toFixed(3)}`);
    marker.addTo(state.lisaMap);
    state.lisaMarkers.push(marker);
  });

  if (state.currentTab === 'tab3' && result.stations.length) {
    state.lisaMap.fitBounds(L.latLngBounds(result.stations.map(item => [item.station.lat, item.station.lng])), { padding: [24, 24], maxZoom: 7 });
  }
}

function renderRankingList() {
  const container = document.getElementById('rankingLeaderboard');
  if (!container || !state.data.stations) return;

  let list = [...state.data.stations].filter(s => s.pm25_avg !== null);
  if (state.filterStandardizedOnly) {
    list = list.filter(s => !s.pm_from_ppm);
  }
  if (state.statusFilter !== 'ALL') {
    list = list.filter(s => s.status === state.statusFilter);
  }

  // Sort descending by PM2.5
  list.sort((a, b) => b.pm25_avg - a.pm25_avg);

  let html = `<div style="max-height: 420px; overflow-y: auto; padding-right: 6px;">`;
  list.forEach((stn, idx) => {
    const isLogger = stn.pm_from_ppm;
    const badge = isLogger ? `<span class="badge badge-logger" title="Sensor datalogger ppm dikonversi ke ug/m3">* [Konversi Logger]</span>` : '';
    const exceedsPP22 = stn.pm25_avg > 55;
    const exceedsWHO = stn.pm25_avg > 15;

    html += `
      <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 12px; margin-bottom:6px; background:rgba(255,255,255,0.03); border-radius:6px; border-left:3px solid ${getAQIColor(stn.pm25_avg)};">
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-family:'JetBrains Mono'; font-size:0.75rem; color:#64748b; width:22px;">#${idx+1}</span>
          <div>
            <div style="font-weight:600; font-size:0.8rem;">${stn.label} ${badge}</div>
            <div style="font-size:0.7rem; color:#94a3b8;">${stn.island} &bull; ${stn.site_type}</div>
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-family:'JetBrains Mono'; font-weight:700; font-size:0.9rem; color:${getAQIColor(stn.pm25_avg)};">
            ${stn.pm25_avg} <span style="font-size:0.7rem; font-weight:normal;">µg/m³</span>
          </div>
          <div style="font-size:0.65rem; color:${exceedsPP22 ? '#ef4444' : (exceedsWHO ? '#f59e0b' : '#10b981')}">
            ${exceedsPP22 ? '> Baku Mutu PP22' : (exceedsWHO ? '> Pedoman WHO' : '✓ Memenuhi WHO')}
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
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderWidth: 3,
      tension: 0.3,
      pointRadius: 3
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
      borderWidth: 1.8,
      borderDash: isl === 'Kalimantan' ? [] : [4, 4],
      tension: 0.3,
      pointRadius: 2
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
        legend: { labels: { color: '#94a3b8', font: { size: 10 } } },
        tooltip: {
          callbacks: {
            footer: (items) => {
              const label = items[0].label;
              const m = parseInt(label.split('-')[1]);
              if (m >= 7 && m <= 10) return '🔥 Musim Kemarau / Episode Karhutla & Asap Gambut';
              return '🌧️ Musim Hujan / Dispersi Basah';
            }
          }
        }
      },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
        y: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#94a3b8' },
          title: { display: true, text: 'Konsentrasi PM2.5 (µg/m³)', color: '#94a3b8' }
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

  let html = `<div style="overflow-x:auto;"><div class="heatmap-grid" style="grid-template-columns: 80px repeat(24, 1fr); min-width: 650px;">`;
  
  // Header hours (0-23)
  html += `<div></div>`;
  for (let h = 0; h < 24; h++) {
    html += `<div class="heatmap-label">${h}:00</div>`;
  }

  // Days
  data.days.forEach((day, dIdx) => {
    html += `<div class="heatmap-label" style="justify-content:flex-start; font-weight:600;">${day.substring(0,3)}</div>`;
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
        legend: { labels: { color: '#94a3b8' } },
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
        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
        y: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#94a3b8' },
          title: { display: true, text: 'Median PM2.5 (µg/m³)', color: '#94a3b8' }
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

  let html = `<div class="data-table-wrapper"><table class="data-table"><thead><tr><th>Variabel</th>`;
  cols.forEach(c => html += `<th>${c.toUpperCase()}</th>`);
  html += `</tr></thead><tbody>`;

  matrix.forEach((row, i) => {
    html += `<tr><td style="font-weight:600; color:#cbd5e1;">${cols[i].toUpperCase()}</td>`;
    row.forEach((val, j) => {
      let bg = 'transparent';
      let textColor = '#94a3b8';
      if (val !== null) {
        if (val > 0) {
          const alpha = Math.min(0.85, Math.abs(val));
          bg = `rgba(59, 130, 246, ${alpha})`;
          if (alpha > 0.4) textColor = '#ffffff';
        } else if (val < 0) {
          const alpha = Math.min(0.85, Math.abs(val));
          bg = `rgba(239, 68, 68, ${alpha})`;
          if (alpha > 0.4) textColor = '#ffffff';
        }
      }
      html += `<td style="background:${bg}; color:${textColor}; text-align:center; font-family:'JetBrains Mono';">${val !== null ? val.toFixed(2) : '-'}</td>`;
    });
    html += `</tr>`;
  });
  html += `</tbody></table></div>`;
  container.innerHTML = html;
}

function renderWindRose() {
  const ctx = document.getElementById('windRoseChart');
  const selector = document.getElementById('windRoseStationSelect');
  if (!ctx || !state.data.windRose) return;

  const stn = selector ? selector.value : 'SM2-01_Samarinda';
  const roseData = state.data.windRose[stn] || [];

  const labels = roseData.map(d => d.direction);
  const pmVals = roseData.map(d => d.pm25_avg);

  if (state.charts.windRose) state.charts.windRose.destroy();

  state.charts.windRose = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [
        {
          label: `Rata-rata PM2.5 per Arah Angin (${stn})`,
          data: pmVals,
          backgroundColor: 'rgba(239, 68, 68, 0.25)',
          borderColor: '#ef4444',
          borderWidth: 2,
          pointBackgroundColor: '#ef4444'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8' } }
      },
      scales: {
        r: {
          angleLines: { color: 'rgba(255,255,255,0.1)' },
          grid: { color: 'rgba(255,255,255,0.08)' },
          pointLabels: { color: '#cbd5e1', font: { size: 10 } },
          ticks: { backdropColor: 'transparent', color: '#94a3b8' }
        }
      }
    }
  });

  if (selector && !selector.dataset.initialized) {
    selector.dataset.initialized = 'true';
    selector.addEventListener('change', () => renderWindRose());
  }
}

function renderTrafficScatter() {
  const ctx = document.getElementById('trafficScatterChart');
  if (!ctx || !state.data.traffic) return;

  let points = state.data.traffic.filter(d => d.distance_to_road_m && d.pm25_avg);
  if (state.filterStandardizedOnly) points = points.filter(p => !p.is_logger);

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
        legend: { labels: { color: '#94a3b8' } },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const raw = ctx.raw;
              return `${raw.station}: Jarak = ${raw.x}m, PM2.5 = ${raw.y} µg/m³, Trafik = ${raw.traffic || 'N/A'}/jam`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#94a3b8' },
          title: { display: true, text: 'Jarak Stasiun ke Jalan Raya (meter)', color: '#94a3b8' }
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#94a3b8' },
          title: { display: true, text: 'Konsentrasi Rata-rata PM2.5 (µg/m³)', color: '#94a3b8' }
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
      backgroundColor: '#ef4444',
      tension: 0.3,
      borderWidth: 2.5
    },
    {
      label: 'Lansia (>60 thn)',
      data: lags.map(l => data.resp_admissions_over60[l]?.correlation ?? 0),
      borderColor: '#f59e0b',
      backgroundColor: '#f59e0b',
      tension: 0.3,
      borderWidth: 2.5
    },
    {
      label: 'Kunjungan Asma IGD',
      data: lags.map(l => data.asthma_emergency_cases[l]?.correlation ?? 0),
      borderColor: '#3b82f6',
      borderDash: [5, 5],
      tension: 0.3,
      borderWidth: 2
    },
    {
      label: 'PPOK (COPD)',
      data: lags.map(l => data.copd_admissions[l]?.correlation ?? 0),
      borderColor: '#10b981',
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
        legend: { labels: { color: '#94a3b8' } },
        tooltip: {
          callbacks: {
            afterBody: (items) => {
              const lag = items[0].dataIndex;
              if (lag >= 1 && lag <= 3) return '⚡ Puncak Efek Jeda: Reaksi inflamasi saluran nafas memuncak pada hari ke 1-3 pasca pajanan.';
              return '';
            }
          }
        }
      },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
        y: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#94a3b8' },
          title: { display: true, text: 'Koefisien Korelasi Pearson (r)', color: '#94a3b8' }
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
      labels: tiers.map(t => `Kuartil Polusi ${t} (${data[t]?.pm25_range.min}-${data[t]?.pm25_range.max} µg/m³)`),
      datasets: [
        {
          label: 'Admisi Respiratorik Balita (<5 Thn)',
          data: under5,
          backgroundColor: '#ef4444',
          borderRadius: 4
        },
        {
          label: 'Admisi Respiratorik Lansia (>60 Thn)',
          data: over60,
          backgroundColor: '#f59e0b',
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8' } }
      },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8', font: { size: 10 } } },
        y: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#94a3b8' },
          title: { display: true, text: 'Rata-rata Pasien Rawat Inap / Hari', color: '#94a3b8' }
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
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          yAxisID: 'y1',
          borderWidth: 2.5,
          tension: 0.3
        },
        {
          label: 'Kasus IGD Asma (Sumbu Kanan)',
          data: trend.asthma_emergency_cases?.outcome || [],
          borderColor: '#3b82f6',
          yAxisID: 'y2',
          borderWidth: 2,
          tension: 0.3
        },
        {
          label: 'Admisi PPOK (Sumbu Kanan)',
          data: trend.copd_admissions?.outcome || [],
          borderColor: '#10b981',
          yAxisID: 'y2',
          borderWidth: 2,
          tension: 0.3
        },
        {
          label: 'Kardiovaskular (CVD)',
          data: trend.cvd?.outcome || [],
          borderColor: '#8b5cf6',
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
        legend: { labels: { color: '#94a3b8' } }
      },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
        y1: {
          type: 'linear',
          position: 'left',
          grid: { color: 'rgba(255,255,255,0.05)' },
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
        legend: { position: 'bottom', labels: { color: '#94a3b8' } }
      },
      cutout: '70%'
    }
  });
}

function renderAuditTable() {
  const container = document.getElementById('auditTableContainer');
  if (!container || !state.data.audit) return;

  let stations = state.data.audit.stations;
  if (state.filterStandardizedOnly) {
    stations = stations.filter(s => !s.is_logger);
  }
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
        legend: { labels: { color: '#94a3b8' } }
      },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
        y: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#94a3b8' },
          title: { display: true, text: 'Jumlah Stasiun AQMS', color: '#94a3b8' }
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
        legend: { labels: { color: '#94a3b8' } },
        tooltip: {
          callbacks: {
            label: (c) => {
              const r = c.raw;
              return `${r.station} (${r.island}): Kasus ISPA/Resp = ${r.x}, Ketersediaan Sensor = ${r.y.toFixed(1)}% [${r.status}]`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#94a3b8' },
          title: { display: true, text: 'Total Beban Kasus Respiratorik RS (Jiwa)', color: '#94a3b8' }
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#94a3b8' },
          title: { display: true, text: 'Keandalan / Coverage Sensor (%)', color: '#94a3b8' }
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
            <th>Tingkat Prioritas</th>
            <th>Lokasi / Wilayah Target</th>
            <th>Wilayah / Pulau</th>
            <th>Masalah Utama</th>
            <th>Rekomendasi Kebijakan Tindakan</th>
          </tr>
        </thead>
        <tbody>
  `;

  items.forEach(item => {
    const pClass = `priority-${item.priority}`;
    html += `
      <tr>
        <td><span class="priority-badge ${pClass}">Prioritas ${item.priority}: ${item.priority_label}</span></td>
        <td style="font-weight:600; color:#f1f5f9;">${item.label}</td>
        <td>${item.island || '-'}</td>
        <td style="color:#f59e0b;">${item.issue}</td>
        <td style="color:#cbd5e1; font-weight:500;">${item.recommendation}</td>
      </tr>
    `;
  });

  html += `</tbody></table></div>`;
  container.innerHTML = html;
}

// ==============================================================
// SENSITIVITY TEST (INTERACTIVE SLIDER)
// ==============================================================

function initSensitivity() {
  updateSensitivityUI(1000);
}

function updateSensitivityUI(factorVal) {
  const container = document.getElementById('sensitivityResultsContainer');
  if (!container || !state.data.sensitivity) return;

  const sens = state.data.sensitivity;
  const ratio = factorVal / 1000;

  let html = '';
  Object.keys(sens).forEach(stn => {
    const item = sens[stn];
    const adjPM25 = item.current_avg * ratio;
    const exceedsPP22 = adjPM25 > 55;
    const exceedsWHO = adjPM25 > 15;

    html += `
      <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:16px;">
        <div style="font-weight:700; font-size:0.95rem; margin-bottom:4px;">${stn}</div>
        <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:12px;">Baseline Referensi: ${item.baseline_pm25} µg/m³</div>
        
        <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:8px;">
          <span style="font-size:0.8rem; color:#94a3b8;">Estimasi PM2.5 (${factorVal}×):</span>
          <span style="font-family:'JetBrains Mono'; font-weight:700; font-size:1.3rem; color:${getAQIColor(adjPM25)};">
            ${adjPM25.toFixed(2)} <span style="font-size:0.75rem; font-weight:normal;">µg/m³</span>
          </span>
        </div>

        <div style="margin-top:10px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.06); font-size:0.75rem; display:flex; flex-direction:column; gap:4px;">
          <div style="display:flex; justify-content:space-between;">
            <span>Baku Mutu PP 22/2021 (55 µg/m³):</span>
            <span style="font-weight:600; color:${exceedsPP22 ? '#ef4444' : '#10b981'};">
              ${exceedsPP22 ? '⚠️ Terlampaui' : '✓ Memenuhi'}
            </span>
          </div>
          <div style="display:flex; justify-content:space-between;">
            <span>Pedoman WHO (15 µg/m³):</span>
            <span style="font-weight:600; color:${exceedsWHO ? '#ef4444' : '#10b981'};">
              ${exceedsWHO ? '⚠️ Terlampaui' : '✓ Memenuhi'}
            </span>
          </div>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}
