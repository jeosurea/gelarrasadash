# Sistem Pemantauan & Analisis Kualitas Udara Nasional (AQMS Dashboard)

Dashboard analisis kualitas udara Indonesia untuk memvisualisasikan konsentrasi PM2.5 dari 27 stasiun AQMS di lima pulau besar, faktor pendorong meteorologi dan emisi lalu lintas, dampak kesehatan pada kelompok rentan, serta audit integritas jaringan dan rekomendasi titik pemantauan baru.

---

## Arsitektur & Teknologi

1. **Pipeline Data (Python)**
   - Skrip: `process_data.py`
   - Memproses dataset CSV (data harian, data per jam dalam format Parquet, data kesehatan RS, dan metadata stasiun).
   - Menghasilkan 18 file JSON analitis di `data/json/` yang sudah dibersihkan dari nilai kosong dan siap dipakai frontend.

2. **Frontend (HTML5 + CSS3 + Vanilla JavaScript)**
   - **Tampilan:** tema terang dengan palet krem, teal, dan amber. Latar halaman memakai gradasi teal–oranye yang transparan, kartu chart putih tulang, dan indikator tab di sidebar yang bergeser saat berpindah tab.
   - **Tipografi:** font Brulia Display (judul) dan Brulia Text (teks dan angka), dimuat dari folder `fonts/`.
   - **Leaflet 1.9.4:** peta spasial sebaran stasiun dengan ubin ArcGIS *World Light Gray*, bubble konsentrasi, dan penanda khusus untuk stasiun konversi logger.
   - **Chart.js 4.4.1:** grafik tren bulanan, mawar polusi (radar), scatter plot, kurva lag, grafik batang, donut, dan heatmap.
   - Library Leaflet dan Chart.js dimuat dari CDN, sehingga komputer perlu terhubung ke internet.

---

## Struktur 3 Tab Analisis

### Tab 1: Kondisi Polusi Indonesia
- **Kartu KPI:** rata-rata nasional PM2.5, rata-rata Indeks Kinerja Utama (IKU, target ≥70), persentase kepatuhan baku mutu PP 22/2021 (≤55 µg/m³), dan persentase kepatuhan pedoman WHO tahunan (≤15 µg/m³). Setiap kartu memiliki tooltip penjelasan saat disentuh kursor.
- **Sebaran Spasial Stasiun AQMS:** peta interaktif dengan bubble berwarna sesuai kategori konsentrasi, dan opsi buffer (aktif/nonaktif) dengan pilihan radius adaptif atau seragam.
- **Peringkat Kualitas Udara Stasiun:** daftar stasiun dari konsentrasi tertinggi ke terendah, dengan penanda `[Konversi Logger]`.
- **Dinamika Tren Temporal & Siklus Musim:** garis tren bulanan nasional dan per pulau, dengan pita ambang batas WHO dan PP 22/2021 serta insight otomatis perbandingan musim kemarau (Juli–Oktober) dengan bulan lainnya.
- **Heatmap Diurnal 24 Jam × 7 Hari:** pola jam puncak polusi per kelompok kawasan.
- **Perbandingan Karakteristik Tipe Kawasan:** perbandingan kawasan normal dan musim karhutla.

### Tab 2: Faktor Pendorong & Dampak Kesehatan
- **Pendorong Lingkungan, Meteorologi, & Emisi Transportasi:**
  - *Mawar Polusi (Pollution Rose):* arah angin yang membawa polutan pekat ke stasiun.
  - *Jarak ke Jalan Raya vs PM2.5:* pengaruh kedekatan dengan jalan terhadap konsentrasi partikulat.
  - *Matriks Korelasi Pearson:* hubungan antarvariabel gas dan parameter cuaca.
- **Dampak Nyata Kesehatan Masyarakat & Kelompok Rentan:**
  - *Kurva Efek Jeda Paparan (Lag 0–7 Hari):* kapan kasus penyakit saluran napas memuncak setelah paparan.
  - *Rasio Kerentanan Balita (<5 tahun) vs Lansia (>60 tahun):* perbandingan pada kuartil polusi rendah dan ekstrem.
  - *Ko-Evolusi Tren Bulanan:* PM2.5 bersama kasus gawat darurat asma, PPOK, dan kardiovaskular.

### Tab 3: Evaluasi Stasiun Pemantauan
- **Status Kelayakan Stasiun AQMS:** donut dengan jumlah stasiun OK, CAUTION, dan EXCLUDED, dengan angka ringkasan di tengah.
- **Ketimpangan Sebaran Spasial Pulau:** jumlah stasiun per status di setiap pulau.
- **Gap Analysis: Beban Kasus RS vs Ketersediaan Sensor:** wilayah dengan beban kasus tinggi tetapi sensor bermasalah atau tidak tersedia, seperti Medan dan Banjarbaru.
- **Keandalan Sensor dari Waktu ke Waktu:** heatmap kelengkapan data per stasiun per bulan, dengan skala teal dan amber.
- **Catatan Metodologi Audit:** penjelasan konversi sensor logger (ppm ke µg/m³) dan temuan audit.
- **Matriks Rekomendasi Preskriptif:** prioritas penambahan dan perbaikan stasiun (Prioritas 1: Mendesak, Prioritas 2: Tinggi, Prioritas 3: Peningkatan mutu sensor).
- **Tabel Lengkap Audit Integritas & QA/QC:** frozen hours, overrange, coverage, dan status kelayakan 27 stasiun.

---

## Cara Menjalankan Dashboard

1. **Jalankan dengan Python (disarankan):**
   Buka terminal atau PowerShell di folder proyek ini, lalu jalankan:
   ```bash
   python run_dashboard.py
   ```
   Browser akan terbuka otomatis ke `http://localhost:8080/index.html`. Jika port 8080 sudah dipakai, ubah nilai `PORT` di `run_dashboard.py`.

2. **Memperbarui analisis data (jika CSV diubah):**
   ```bash
   python process_data.py
   ```
   Skrip ini menulis ulang seluruh file di `data/json/`.

3. **Jika tampilan tidak berubah setelah update:** lakukan hard refresh (Ctrl+Shift+R). File `index.html` memuat `style.css` dan `dashboard.js` dengan parameter versi (`?v=...`), jadi naikkan nilai versi tersebut setiap kali file CSS atau JS diubah.

---

## Catatan Pemeliharaan

- File `*.py` berawalan `fix_`, `apply_`, `enlarge_`, `inspect_`, `remove_`, dan `scratch_` adalah skrip bantu sekali pakai untuk merapikan tampilan. Dashboard tidak membutuhkannya untuk berjalan, sehingga bisa dihapus setelah dipastikan tidak diperlukan lagi.
- File `*.bak` (`style.css.bak`, `dashboard.js.bak`) adalah salinan cadangan dan juga bisa dihapus.
- Skrip `process_data.py` adalah satu-satunya sumber data JSON. Jika mengubah isi JSON secara manual, perubahan itu akan hilang saat skrip dijalankan ulang.
