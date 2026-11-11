# 🍃 Sistem Pemantauan & Analisis Kualitas Udara Nasional (AQMS Dashboard)

Dashboard profesional standar kompetisi / evaluasi kebijakan untuk memvisualisasikan data kualitas udara Indonesia, faktor pendorong meteorologi dan emisi lalu lintas, dampak kesehatan terhadap kelompok rentan, serta audit jaringan pemantauan AQMS dan rekomendasi penambahan stasiun baru.

---

## 🏗️ Arsitektur & Teknologi

1. **Backend / Data Pipeline (Python):**
   - Script: `process_data.py`
   - Memproses 8 file dataset CSV (26.000+ data harian, 630.000+ data per jam, data kesehatan RS, dll.)
   - Menghasilkan 17 file JSON analitis di `data/json/` yang teroptimasi, bersih dari NaN, dan memiliki struktur siap visualisasi.

2. **Frontend Visualisasi Interaktif (HTML5 + CSS3 + Vanilla JavaScript):**
   - **HTML/CSS:** Antarmuka tema gelap profesional (*Bloomberg Terminal meets modern analytics*) dengan efek *glassmorphism*, indikator status, kartu KPI beranimasi, dan tata letak responsif.
   - **Leaflet.js:** Peta spasial interaktif sebaran 27 stasiun di 5 pulau besar Indonesia dengan ubin peta gelap CartoDB, bubble konsentrasi, dan penanda stasiun konversi logger.
   - **Chart.js:** Visualisasi grafik tren bulanan & musiman, mawar polusi (*pollution rose radar*), diagram sebar (*scatter plot*), kurva jeda paparan (*lag effect 0-7 hari*), perbandingan balita vs lansia, dan grafik audit status.

---

## 📑 Struktur 3 Tab Analisis

### 🌟 Tab 1: Panorama Spatiotemporal & Episode Kritis
- **KPI Summary Cards:** Rata-rata nasional PM2.5, Indeks Kualitas Udara (IKU), % kepatuhan baku mutu PP 22/2021 (55 µg/m³) dan pedoman WHO (15 µg/m³).
- **Peta Spasial Interaktif:** Bubble map sebaran stasiun pemantau di seluruh pulau Indonesia dengan popup analitis lengkap.
- **Peringkat Stasiun:** Leaderboard stasiun terbersih vs paling tercemar dengan penanda khusus `[Konversi Logger]`.
- **Dinamika Tren Musim:** Garis tren bulanan per pulau yang membuktikan lonjakan ekstrem pada musim kemarau & kebakaran gambut (Juli–Oktober).
- **Heatmap Diurnal 24 Jam × 7 Hari:** Mengidentifikasi jam puncak polusi pada kawasan penyangga gambut vs koridor lalu lintas urban.
- **Boxplot Karakteristik Kawasan:** Membuktikan kawasan penyangga gambut (*Peatland*) melonjak drastis mengalahkan kawasan industri pada musim kebakaran lahan.

### 🌟 Tab 2: Faktor Pendorong & Dampak Kesehatan
- **Zona 1: Pendorong Lingkungan (Sebab):**
  - *Mawar Polusi (Pollution Rose):* Menunjukkan arah mata angin pembawa polutan pekat ke stasiun.
  - *Scatter Jarak Jalan & Trafik vs PM2.5:* Dampak kedekatan transportasi terhadap polutan partikulat.
  - *Matriks Korelasi Pearson:* Hubungan antar-variabel gas dan parameter cuaca.
- **Zona 2: Dampak Nyata Kesehatan (Akibat):**
  - *Kurva Lag Effect (0–7 Hari):* Membuktikan lonjakan kasus penyakit saluran nafas memuncak pada hari ke 1–3 pasca-pajanan polusi.
  - *Rasio Balita (<5 Thn) vs Lansia (>60 Thn):* Komparasi admisi rawat inap balita vs lansia pada kuartil polusi rendah vs ekstrem.
  - *Ko-Evolusi Bulanan:* Tren bersamaan antara PM2.5 dengan kasus IGD Asma, rawat inap PPOK, dan penyakit kardiovaskular.

### 🌟 Tab 3: Audit Jaringan & Rekomendasi Titik Baru
- **Audit Integritas Jaringan:** Status kelayakan 22 stasiun OK (81%), 4 CAUTION (15%), 1 EXCLUDED (4%).
- **Ketimpangan Spasial:** Analisis dominasi stasiun di Sumatera & Jawa versus kekosongan di Kepulauan Maluku & Nusa Tenggara.
- **Gap Analysis (Beban Sakit vs Sensor):** Menyoroti wilayah anomali di mana beban kasus RS tinggi namun sensor mengalami gangguan (seperti Medan dan Banjarbaru).
- **Uji Sensitivitas Interaktif (Slider 800× — 1200×):** Pengujian interaktif pita ketidakpastian konversi logger, membuktikan bahwa meski faktor digeser ±20%, ambang batas PP 22/2021 tetap terlampaui.
- **Matriks Preskriptif Prioritas Kebijakan:** Rekomendasi terstruktur titik baru (Prioritas 1: Mendesak, Prioritas 2: Ekspansi, Prioritas 3: Peningkatan Mutu Sensor).
- **Tabel Lengkap QA/QC:** Audit rinci jam beku (*frozen*), overrange, dan kelayakan operasional 27 stasiun.

---

## 🚀 Cara Menjalankan Dashboard

1. **Jalankan melalui Python (Rekomendasi Terbaik):**
   Buka terminal/PowerShell di direktori ini, lalu jalankan:
   ```bash
   python run_dashboard.py
   ```
   Browser default Anda akan otomatis terbuka ke alamat `http://localhost:8080/index.html`.

2. **Memperbarui Analisis Data (Jika CSV Diubah):**
   ```bash
   python process_data.py
   ```
