#!/usr/bin/env python3
"""
AQMS Dashboard Data Processor
==============================
Memproses semua CSV data kualitas udara Indonesia dan menghasilkan
file JSON yang siap dikonsumsi oleh frontend dashboard HTML/JS.

Struktur Output:
- data/json/  -> Semua file JSON untuk 3 tab dashboard

Author: AQMS Dashboard Builder
"""

import pandas as pd
import numpy as np
import json
import os
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

# ============================================================
# KONFIGURASI PATH
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
JSON_DIR = DATA_DIR / 'json'
JSON_DIR.mkdir(parents=True, exist_ok=True)

# Baku Mutu
PP22_2021_ANNUAL = 55.0   # µg/m³ (PM2.5 annual)
WHO_ANNUAL = 15.0          # µg/m³ (PM2.5 annual)

# Stasiun konversi logger (ppm -> µg/m³)
LOGGER_STATIONS = ['BJB-01_Banjarbaru', 'MDN-01_Medan', 'PSW-01_Pesawaran']
SPATIAL_VARIABLES = {
    'pm25': 'PM2.5',
    'pm10': 'PM10',
    'so2': 'SO2',
    'co': 'CO',
    'o3': 'O3',
    'no2': 'NO2',
    'temperature_c': 'Suhu',
    'humidity_pct': 'Kelembapan',
    'wind_speed_ms': 'Kecepatan angin'
}

# ============================================================
# FUNGSI UTILITAS
# ============================================================
def save_json(data, filename):
    """Simpan data ke file JSON dengan encoding UTF-8."""
    filepath = JSON_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"  [OK] {filename} ({filepath.stat().st_size:,} bytes)")

def clean_nan(obj):
    """Rekursif konversi NaN/inf ke None untuk JSON serialization."""
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan(v) for v in obj]
    elif isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return round(obj, 2)
    return obj

def boxplot_stats(series):
    """Hitung statistik boxplot dari pandas Series."""
    s = series.dropna()
    if len(s) == 0:
        return None
    return {
        'min': round(float(s.min()), 2),
        'q1': round(float(s.quantile(0.25)), 2),
        'median': round(float(s.median()), 2),
        'q3': round(float(s.quantile(0.75)), 2),
        'max': round(float(s.max()), 2),
        'mean': round(float(s.mean()), 2),
        'count': int(len(s))
    }

# ============================================================
# MUAT DATA
# ============================================================
print("=" * 60)
print("AQMS Dashboard Data Processor")
print("=" * 60)
print("\n[1/2] Memuat data CSV...")

stations = pd.read_csv(DATA_DIR / 'stations_master_clean.csv')
daily = pd.read_csv(DATA_DIR / 'aqms_daily_clean.csv')
hourly = pd.read_parquet(DATA_DIR / 'aqms_hourly_clean.parquet')
health = pd.read_csv(DATA_DIR / 'health_clean.csv')
merged = pd.read_csv(DATA_DIR / 'analysis_daily_merged.csv')
iku_city = pd.read_csv(DATA_DIR / 'iku_city_year.csv')
iku_station = pd.read_csv(DATA_DIR / 'iku_station_year.csv')
quality = pd.read_csv(DATA_DIR / 'station_quality_report.csv')

# Konversi tipe data
daily['date'] = pd.to_datetime(daily['date'])
for column in SPATIAL_VARIABLES:
    daily[column] = pd.to_numeric(daily[column], errors='coerce')
hourly['pm25'] = pd.to_numeric(hourly['pm25'], errors='coerce')
hourly['hour_of_day'] = pd.to_numeric(hourly['hour_of_day'], errors='coerce')
merged['date'] = pd.to_datetime(merged['date'])
merged['pm25'] = pd.to_numeric(merged['pm25'], errors='coerce')
health['date'] = pd.to_datetime(health['date'])

# Konversi kolom numerik di health
for col in ['resp_admissions_under5', 'resp_admissions_over60', 'asthma_emergency_cases',
            'copd_admissions', 'resp', 'cvd', 'death']:
    if col in health.columns:
        health[col] = pd.to_numeric(health[col], errors='coerce')
    if col in merged.columns:
        merged[col] = pd.to_numeric(merged[col], errors='coerce')

print(f"  Stations: {len(stations)} | Daily: {len(daily)} | Hourly: {len(hourly)}")
print(f"  Health: {len(health)} | Merged: {len(merged)} | IKU City: {len(iku_city)}")

# ============================================================
# TAB 1: PANORAMA SPATIOTEMPORAL & EPISODE KRITIS
# ============================================================
print("\n[2/2] Menghasilkan JSON files...")
print("\n--- TAB 1: Panorama Spatiotemporal ---")

# ------ 1. KPI Summary ------
pm25_avg_all = daily['pm25'].mean()
pm25_avg_by_station = daily.groupby('station')['pm25'].mean()
spatial_avg_by_station = daily.groupby('station')[list(SPATIAL_VARIABLES)].mean()

# IKU statistics
iku_latest = iku_city[iku_city['year'] == iku_city['year'].max()]
iku_national_avg = iku_latest['iku'].mean()

# Compliance
stations_above_pp22 = (pm25_avg_by_station > PP22_2021_ANNUAL).sum()
stations_above_who = (pm25_avg_by_station > WHO_ANNUAL).sum()
total_stations = len(pm25_avg_by_station)
compliance_pp22 = round((total_stations - stations_above_pp22) / total_stations * 100, 1)
compliance_who = round((total_stations - stations_above_who) / total_stations * 100, 1)

# Kota teratas
top_clean = pm25_avg_by_station.nsmallest(3)
top_dirty = pm25_avg_by_station.nlargest(3)

kpi_data = {
    'national_pm25_avg': round(float(pm25_avg_all), 2),
    'national_iku_avg': round(float(iku_national_avg), 2),
    'compliance_pp22_pct': compliance_pp22,
    'compliance_who_pct': compliance_who,
    'pp22_standard': PP22_2021_ANNUAL,
    'who_standard': WHO_ANNUAL,
    'total_stations': int(total_stations),
    'stations_exceed_pp22': int(stations_above_pp22),
    'stations_exceed_who': int(stations_above_who),
    'cleanest_stations': [
        {'station': s, 'pm25_avg': round(float(v), 2),
         'is_logger': s in LOGGER_STATIONS}
        for s, v in top_clean.items()
    ],
    'dirtiest_stations': [
        {'station': s, 'pm25_avg': round(float(v), 2),
         'is_logger': s in LOGGER_STATIONS}
        for s, v in top_dirty.items()
    ],
    'data_period': {
        'start': str(daily['date'].min().date()),
        'end': str(daily['date'].max().date())
    }
}
save_json(clean_nan(kpi_data), 'kpi_summary.json')

# ------ 2. Stations Map ------
stations_map = []
for _, row in stations.iterrows():
    label = row['label']
    avg_pm25 = pm25_avg_by_station.get(label, None)
    stations_map.append({
        'label': label,
        'location_id': row['location_id'],
        'lat': float(row['latitude_dd']),
        'lng': float(row['longitude_dd']),
        'provinsi': row['provinsi'],
        'kota': row['kota_kabupaten'],
        'island': row['island'],
        'site_type': row['site_type'],
        'status': row['status'],
        'pm25_avg': round(float(avg_pm25), 2) if avg_pm25 is not None and not np.isnan(avg_pm25) else None,
        'spatial_values': {
            variable: round(float(spatial_avg_by_station.at[label, variable]), 2)
            if label in spatial_avg_by_station.index and pd.notna(spatial_avg_by_station.at[label, variable])
            else None
            for variable in SPATIAL_VARIABLES
        },
        'baseline_pm25': float(row['baseline_pm25']),
        'pm_from_ppm': label in LOGGER_STATIONS,
        'distance_to_road_m': float(row['distance_to_road_m']) if pd.notna(row['distance_to_road_m']) else None,
        'traffic_intensity': float(row['traffic_intensity_per_h']) if pd.notna(row['traffic_intensity_per_h']) else None,
        'karakteristik': row['karakteristik_wilayah'],
        'coverage_pm25': round(float(row['coverage_pm25']), 4) if pd.notna(row['coverage_pm25']) else None,
        'catatan': row['catatan'] if pd.notna(row.get('catatan', '')) else ''
    })
save_json(stations_map, 'stations_map.json')

# ------ 3. Trend Monthly ------
daily['year_month'] = daily['date'].dt.to_period('M').astype(str)
monthly_island = daily.groupby(['year_month', 'island'])['pm25'].mean().round(2)
monthly_all = daily.groupby('year_month')['pm25'].mean().round(2)

# Organisasi per pulau
trend_monthly = {
    'labels': sorted(daily['year_month'].unique().tolist()),
    'national': [],
    'islands': {}
}

for ym in trend_monthly['labels']:
    trend_monthly['national'].append(
        round(float(monthly_all.get(ym, 0)), 2)
    )

for island in stations['island'].unique():
    trend_monthly['islands'][island] = []
    for ym in trend_monthly['labels']:
        val = monthly_island.get((ym, island), None)
        trend_monthly['islands'][island].append(
            round(float(val), 2) if val is not None and not np.isnan(val) else None
        )

# Season markers
trend_monthly['seasons'] = []
for ym in trend_monthly['labels']:
    month_num = int(ym.split('-')[1])
    if 7 <= month_num <= 10:
        trend_monthly['seasons'].append('dry_fire')
    elif 11 <= month_num <= 12 or 1 <= month_num <= 3:
        trend_monthly['seasons'].append('wet')
    else:
        trend_monthly['seasons'].append('transition')

save_json(clean_nan(trend_monthly), 'trend_monthly.json')

# ------ 4. Trend Daily (Sample Stations) ------
# Pilih stasiun menarik: terkotor, terbersih, logger, peatland
interesting_stations = list(top_dirty.index[:2]) + list(top_clean.index[:2]) + ['KTG-01_PalangkaRaya']
interesting_stations = list(set(interesting_stations))[:6]

trend_daily = {}
for stn in interesting_stations:
    stn_data = daily[daily['station'] == stn][['date', 'pm25']].copy()
    stn_data = stn_data.sort_values('date')
    trend_daily[stn] = {
        'dates': stn_data['date'].dt.strftime('%Y-%m-%d').tolist(),
        'pm25': [round(float(v), 2) if not np.isnan(v) else None for v in stn_data['pm25']],
        'is_logger': stn in LOGGER_STATIONS
    }
save_json(trend_daily, 'trend_daily_sample.json')

# ------ 5. Diurnal Heatmap ------
# Rata-rata PM2.5 per jam x hari dalam seminggu untuk beberapa tipe stasiun
dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

diurnal_data = {}
# Group by site type categories
site_groups = {
    'Urban/Traffic': ['Urban Background', 'Traffic / Roadside', 'Urban Background / Highway Corridor'],
    'Peatland': ['Peatland Buffer / Urban', 'Peatland Boundary / Airport', 'Peatland Boundary',
                 'Peatland Boundary / Inland', 'Peatland & Plantation Hinterland',
                 'Peatland Buffer / Urban Artery', 'Airport & Peatland Buffer'],
    'Industrial': ['Industrial / Karst Perimeter', 'Industrial Perimeter',
                   'Industrial Perimeter / Maritime', 'Industrial & Deforestation Buffer'],
    'Clean/Regional': ['Regional / Clean Background', 'Coastal / Regional Background',
                       'Coastal / Remote Savanna', 'Urban Coastal Background']
}

for group_name, types in site_groups.items():
    group_hourly = hourly[hourly['site_type'].isin(types)]
    if len(group_hourly) == 0:
        continue
    pivot = group_hourly.groupby(['hour_of_day', 'dow'])['pm25'].mean()
    matrix = []
    for h in range(24):
        row = []
        for d in dow_order:
            val = pivot.get((h, d), None)
            row.append(round(float(val), 2) if val is not None and not np.isnan(val) else None)
        matrix.append(row)
    diurnal_data[group_name] = {
        'hours': list(range(24)),
        'days': dow_order,
        'matrix': matrix
    }

save_json(clean_nan(diurnal_data), 'diurnal_heatmap.json')

# ------ 6. Site Type Comparison (Boxplot) ------
# Bulan 7-10 = fire season
daily['is_fire_season'] = daily['month'].isin([7, 8, 9, 10])

# Simplify site types
def simplify_site(s):
    s_lower = str(s).lower()
    if 'peatland' in s_lower:
        return 'Peatland'
    elif 'traffic' in s_lower or 'roadside' in s_lower or 'highway' in s_lower:
        return 'Traffic/Roadside'
    elif 'industrial' in s_lower:
        return 'Industrial'
    elif 'clean' in s_lower or 'regional' in s_lower or 'background' in s_lower:
        return 'Background/Clean'
    elif 'coastal' in s_lower:
        return 'Coastal'
    elif 'valley' in s_lower or 'urban' in s_lower:
        return 'Urban'
    return 'Other'

daily['site_group'] = daily['site_type'].apply(simplify_site)

site_comparison = {'normal_season': {}, 'fire_season': {}}
for season, is_fire in [('normal_season', False), ('fire_season', True)]:
    subset = daily[daily['is_fire_season'] == is_fire]
    for sg in sorted(subset['site_group'].unique()):
        stats = boxplot_stats(subset[subset['site_group'] == sg]['pm25'])
        if stats:
            site_comparison[season][sg] = stats

save_json(clean_nan(site_comparison), 'site_type_comparison.json')


# ============================================================
# TAB 2: FAKTOR PENGARUH & DAMPAK KESEHATAN
# ============================================================
print("\n--- TAB 2: Faktor Pengaruh & Dampak Kesehatan ---")

# ------ 7. Correlation Matrix ------
corr_cols = ['pm25', 'pm10', 'temperature_c', 'humidity_pct', 'wind_speed_ms', 'so2', 'no2', 'co', 'o3']
corr_df = daily[corr_cols].apply(pd.to_numeric, errors='coerce')
corr_matrix = corr_df.corr().round(3)

correlation_data = {
    'columns': corr_cols,
    'matrix': corr_matrix.values.tolist()
}
save_json(clean_nan(correlation_data), 'correlation_matrix.json')

# ------ 8. Wind Pollution Rose ------
# 16 arah mata angin dihitung dari data observasi per jam (hourly) untuk akurasi meteorologis
def deg_to_direction(deg):
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    idx = int(round(deg / 22.5)) % 16
    return dirs[idx]

hourly_clean = hourly.dropna(subset=['wind_direction_deg', 'pm25']).copy()
hourly_clean['wind_dir_cat'] = hourly_clean['wind_direction_deg'].apply(deg_to_direction)
daily_clean = daily.dropna(subset=['wind_direction_deg', 'pm25']).copy()
daily_clean['wind_dir_cat'] = daily_clean['wind_direction_deg'].apply(deg_to_direction)

rose_stations = sorted(stations['label'].dropna().unique().tolist())
wind_rose = {}
direction_order = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                   'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

for stn in rose_stations:
    sub_h = hourly_clean[hourly_clean['station'] == stn]
    use_hourly = len(sub_h) >= 50
    stn_data = sub_h if use_hourly else daily_clean[daily_clean['station'] == stn]
    if len(stn_data) == 0:
        continue
    rose_vals = []
    agg = stn_data.groupby('wind_dir_cat')['pm25'].agg(['mean', 'count'])
    for d in direction_order:
        if d in agg.index:
            pm = round(float(agg.loc[d, 'mean']), 2)
            cnt = int(agg.loc[d, 'count'])
        else:
            pm = 0.0
            cnt = 0
        rose_vals.append({
            'direction': d,
            'pm25_avg': pm,
            'frequency': cnt
        })
    wind_rose[stn] = rose_vals

save_json(clean_nan(wind_rose), 'wind_pollution_rose.json')

# ------ 9. Traffic Scatter ------
traffic_data = []
for _, row in stations.iterrows():
    stn = row['label']
    avg = pm25_avg_by_station.get(stn, None)
    if avg is None or np.isnan(avg):
        continue
    traffic_data.append({
        'station': stn,
        'distance_to_road_m': float(row['distance_to_road_m']) if pd.notna(row['distance_to_road_m']) else None,
        'traffic_intensity': float(row['traffic_intensity_per_h']) if pd.notna(row['traffic_intensity_per_h']) else None,
        'pm25_avg': round(float(avg), 2),
        'site_type': row['site_type'],
        'island': row['island'],
        'is_logger': stn in LOGGER_STATIONS
    })
save_json(clean_nan(traffic_data), 'traffic_scatter.json')

# ------ 10. Lag Effect ------
# Hitung korelasi PM2.5 vs health outcomes pada lag 0-7 hari
health_cols = ['resp_admissions_under5', 'resp_admissions_over60',
               'asthma_emergency_cases', 'copd_admissions', 'resp', 'cvd']

lag_results = {}
for hcol in health_cols:
    lag_results[hcol] = []
    for lag in range(8):
        # Shift PM2.5 by lag days
        temp = merged[['location_id', 'date', 'pm25', hcol]].dropna()
        if len(temp) < 10:
            lag_results[hcol].append({'lag': lag, 'correlation': None, 'n': 0})
            continue
        temp = temp.sort_values(['location_id', 'date'])
        temp[f'pm25_lag{lag}'] = temp.groupby('location_id')['pm25'].shift(lag)
        valid = temp.dropna(subset=[f'pm25_lag{lag}', hcol])
        if len(valid) > 10:
            corr = valid[f'pm25_lag{lag}'].corr(valid[hcol])
            lag_results[hcol].append({
                'lag': lag,
                'correlation': round(float(corr), 4) if not np.isnan(corr) else None,
                'n': int(len(valid))
            })
        else:
            lag_results[hcol].append({'lag': lag, 'correlation': None, 'n': 0})

save_json(clean_nan(lag_results), 'lag_effect.json')

# ------ 11. Vulnerable Groups ------
# Bagi PM2.5 ke quartiles
merged_valid = merged.dropna(subset=['pm25', 'resp_admissions_under5', 'resp_admissions_over60'])
if len(merged_valid) > 0:
    merged_valid = merged_valid.copy()
    merged_valid['pm25_category'] = pd.qcut(
        merged_valid['pm25'], q=4,
        labels=['Rendah', 'Sedang', 'Tinggi', 'Ekstrem']
    )

    vuln_data = {}
    for cat in ['Rendah', 'Sedang', 'Tinggi', 'Ekstrem']:
        subset = merged_valid[merged_valid['pm25_category'] == cat]
        vuln_data[cat] = {
            'pm25_range': {
                'min': round(float(subset['pm25'].min()), 2),
                'max': round(float(subset['pm25'].max()), 2)
            },
            'under5_mean': round(float(subset['resp_admissions_under5'].mean()), 2),
            'over60_mean': round(float(subset['resp_admissions_over60'].mean()), 2),
            'under5_median': round(float(subset['resp_admissions_under5'].median()), 2),
            'over60_median': round(float(subset['resp_admissions_over60'].median()), 2),
            'asthma_mean': round(float(subset['asthma_emergency_cases'].mean()), 2),
            'copd_mean': round(float(subset['copd_admissions'].mean()), 2),
            'cvd_mean': round(float(subset['cvd'].mean()), 2),
            'n': int(len(subset))
        }
else:
    vuln_data = {}

save_json(clean_nan(vuln_data), 'vulnerable_groups.json')

# ------ 12. Disease Specific Correlation ------
disease_cols = ['asthma_emergency_cases', 'copd_admissions', 'cvd', 'resp', 'death']
disease_corr = {}
for dcol in disease_cols:
    valid = merged.dropna(subset=['pm25', dcol])
    if len(valid) > 10:
        corr = valid['pm25'].corr(valid[dcol])
        disease_corr[dcol] = {
            'correlation': round(float(corr), 4) if not np.isnan(corr) else None,
            'n': int(len(valid)),
            'pm25_mean': round(float(valid['pm25'].mean()), 2),
            'outcome_mean': round(float(valid[dcol].mean()), 2)
        }

# Scatter data per bulan (aggregat)
disease_monthly = {}
merged['year_month'] = merged['date'].dt.to_period('M').astype(str)
for dcol in disease_cols:
    monthly_agg = merged.groupby('year_month').agg(
        pm25_avg=('pm25', 'mean'),
        outcome_avg=(dcol, 'mean')
    ).dropna().round(2)
    disease_monthly[dcol] = {
        'months': monthly_agg.index.tolist(),
        'pm25': monthly_agg['pm25_avg'].tolist(),
        'outcome': monthly_agg['outcome_avg'].tolist()
    }

disease_data = {
    'correlations': disease_corr,
    'monthly_trends': disease_monthly
}
save_json(clean_nan(disease_data), 'disease_specific.json')


# ============================================================
# TAB 3: AUDIT JARINGAN & REKOMENDASI
# ============================================================
print("\n--- TAB 3: Audit Jaringan & Rekomendasi ---")

# ------ 13. Station Audit ------
audit_data = {
    'status_summary': quality['status'].value_counts().to_dict(),
    'stations': []
}

for _, row in quality.iterrows():
    label = row.get('label', '')
    audit_data['stations'].append({
        'location_id': row['location_id'],
        'label': label,
        'status': row['status'],
        'coverage_pm25': round(float(row['coverage_pm25']), 4) if pd.notna(row['coverage_pm25']) else None,
        'frozen_hours': int(row['frozen_hours']) if pd.notna(row['frozen_hours']) else 0,
        'overrange_hours': int(row['overrange_hours']) if pd.notna(row['overrange_hours']) else 0,
        'island': row['island'],
        'site_type': row['site_type'],
        'pm25_median': round(float(row['pm25_median']), 2) if pd.notna(row['pm25_median']) else None,
        'pm25_p95': round(float(row['pm25_p95']), 2) if pd.notna(row['pm25_p95']) else None,
        'catatan': row['catatan'] if pd.notna(row.get('catatan', '')) else '',
        'is_logger': label in LOGGER_STATIONS
    })

save_json(clean_nan(audit_data), 'station_audit.json')

# ------ 14. Island Distribution ------
island_dist = stations.groupby('island').agg(
    n_stations=('label', 'count'),
    stations_list=('label', list),
    status_ok=('status', lambda x: (x == 'OK').sum()),
    status_caution=('status', lambda x: (x == 'CAUTION').sum()),
    status_excluded=('status', lambda x: (x == 'EXCLUDED').sum()),
).reset_index()

island_data = {
    'islands': [],
    'total_stations': int(len(stations)),
    'coverage_gaps': [
        {'region': 'Maluku', 'stations': 0, 'recommendation': 'Ekspansi - tidak ada stasiun pemantau'},
        {'region': 'Nusa Tenggara', 'stations': 0, 'recommendation': 'Ekspansi - tidak ada stasiun pemantau'},
        {'region': 'Papua (Selatan)', 'stations': 0, 'recommendation': 'Merauke tidak aktif - perlu reaktivasi'}
    ]
}

for _, row in island_dist.iterrows():
    island_data['islands'].append({
        'island': row['island'],
        'n_stations': int(row['n_stations']),
        'stations': row['stations_list'],
        'status_ok': int(row['status_ok']),
        'status_caution': int(row['status_caution']),
        'status_excluded': int(row['status_excluded']),
        'pct_of_total': round(int(row['n_stations']) / len(stations) * 100, 1)
    })

save_json(clean_nan(island_data), 'island_distribution.json')

# ------ 15. Priority Matrix ------
# Skor komposit berdasarkan: coverage, health burden, sensor quality, population gap
priority_items = []

# Prioritas 1: Stasiun bermasalah
caution_excluded = quality[quality['status'].isin(['CAUTION', 'EXCLUDED'])]
for _, row in caution_excluded.iterrows():
    label = row.get('label', '')
    priority_items.append({
        'label': label,
        'location_id': row['location_id'],
        'priority': 1 if row['status'] == 'EXCLUDED' else 2,
        'priority_label': 'Mendesak' if row['status'] == 'EXCLUDED' else 'Tinggi',
        'issue': f"Status: {row['status']}",
        'recommendation': 'Reaktivasi/penggantian sensor' if row['status'] == 'EXCLUDED' else 'Perbaikan & kalibrasi sensor',
        'coverage': round(float(row['coverage_pm25']), 4) if pd.notna(row['coverage_pm25']) else None,
        'island': row['island'],
        'is_logger': label in LOGGER_STATIONS
    })

# Prioritas 2: Wilayah kosong
for gap in island_data['coverage_gaps']:
    priority_items.append({
        'label': f"[Baru] {gap['region']}",
        'location_id': None,
        'priority': 2,
        'priority_label': 'Ekspansi',
        'issue': f"Tidak ada stasiun pemantau ({gap['stations']} stasiun)",
        'recommendation': gap['recommendation'],
        'coverage': 0,
        'island': gap['region'],
        'is_logger': False
    })

# Prioritas 3: Logger stations perlu upgrade
for stn in LOGGER_STATIONS:
    stn_info = stations[stations['label'] == stn].iloc[0] if len(stations[stations['label'] == stn]) > 0 else None
    if stn_info is not None:
        priority_items.append({
            'label': stn,
            'location_id': stn_info['location_id'],
            'priority': 3,
            'priority_label': 'Upgrade',
            'issue': 'Sensor ppm → konversi µg/m³ (faktor empiris 1000×)',
            'recommendation': 'Upgrade ke sensor PM2.5 langsung dalam µg/m³',
            'coverage': round(float(stn_info['coverage_pm25']), 4) if pd.notna(stn_info['coverage_pm25']) else None,
            'island': stn_info['island'],
            'is_logger': True
        })

priority_data = {
    'items': sorted(priority_items, key=lambda x: x['priority']),
    'summary': {
        'total_recommendations': len(priority_items),
        'priority_1_count': sum(1 for i in priority_items if i['priority'] == 1),
        'priority_2_count': sum(1 for i in priority_items if i['priority'] == 2),
        'priority_3_count': sum(1 for i in priority_items if i['priority'] == 3)
    }
}
save_json(clean_nan(priority_data), 'priority_matrix.json')

# ------ 16. Gap Analysis ------
# Health burden vs sensor availability per lokasi
gap_data = []
for _, stn_row in stations.iterrows():
    loc_id = stn_row['location_id']
    label = stn_row['label']

    # Health burden
    health_loc = merged[merged['location_id'] == loc_id]
    if len(health_loc) > 0:
        total_resp = health_loc['resp'].sum()
        total_cvd = health_loc['cvd'].sum()
        avg_resp = health_loc['resp'].mean()
    else:
        total_resp = 0
        total_cvd = 0
        avg_resp = 0

    # Sensor quality
    q_row = quality[quality['location_id'] == loc_id]
    coverage = float(q_row['coverage_pm25'].iloc[0]) if len(q_row) > 0 else 0
    status = q_row['status'].iloc[0] if len(q_row) > 0 else 'UNKNOWN'

    gap_data.append({
        'station': label,
        'location_id': loc_id,
        'island': stn_row['island'],
        'total_resp_cases': round(float(total_resp), 0),
        'total_cvd_cases': round(float(total_cvd), 0),
        'avg_daily_resp': round(float(avg_resp), 2),
        'sensor_coverage': round(float(coverage), 4),
        'sensor_status': status,
        'is_logger': label in LOGGER_STATIONS,
        'is_anomaly': (total_resp > 0 and (status != 'OK' or label in LOGGER_STATIONS))
    })

save_json(clean_nan(gap_data), 'gap_analysis.json')

# ------ 17. Sensitivity Data ------
# Untuk stasiun konversi logger: PM2.5 di berbagai faktor konversi
sensitivity = {}
for stn in LOGGER_STATIONS:
    stn_data = daily[daily['station'] == stn]
    if len(stn_data) == 0:
        continue
    base_avg = stn_data['pm25'].mean()  # asumsi faktor 1000x saat ini
    baseline = stations[stations['label'] == stn]['baseline_pm25'].iloc[0] if len(stations[stations['label'] == stn]) > 0 else 25

    sensitivity[stn] = {
        'baseline_pm25': float(baseline),
        'current_avg': round(float(base_avg), 2),
        'factors': {}
    }
    for factor_label, factor_ratio in [('800x', 0.8), ('900x', 0.9), ('1000x', 1.0), ('1100x', 1.1), ('1200x', 1.2)]:
        adjusted = base_avg * factor_ratio
        sensitivity[stn]['factors'][factor_label] = {
            'pm25_avg': round(float(adjusted), 2),
            'exceeds_pp22': adjusted > PP22_2021_ANNUAL,
            'exceeds_who': adjusted > WHO_ANNUAL,
            'ratio_to_baseline': round(float(adjusted / baseline), 2) if baseline > 0 else None
        }

save_json(clean_nan(sensitivity), 'sensitivity_data.json')

# ------ 18. Sensor Reliability Heatmap (Keandalan Sensor dari Waktu ke Waktu) ------
print("  Generating sensor_reliability_heatmap.json...")
daily_copy = daily.copy()
daily_copy['date'] = pd.to_datetime(daily_copy['date'])
daily_copy['year_month'] = daily_copy['date'].dt.to_period('M').astype(str)

all_months = sorted(daily_copy['year_month'].unique())
month_meta = []
month_expected = {}

month_names_id = {
    '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
    '05': 'Mei', '06': 'Jun', '07': 'Jul', '08': 'Agu',
    '09': 'Sep', '10': 'Okt', '11': 'Nov', '12': 'Des'
}

for ym in all_months:
    sub = daily_copy[daily_copy['year_month'] == ym]
    n_days = int(sub['date'].nunique())
    eh = n_days * 24
    month_expected[ym] = eh
    cal_days = pd.Period(ym, freq='M').days_in_month
    is_partial = n_days < cal_days
    short_m = month_names_id.get(ym.split('-')[1], ym.split('-')[1])
    short_y = ym.split('-')[0][2:]
    
    month_meta.append({
        'key': ym,
        'year': ym.split('-')[0],
        'month_num': ym.split('-')[1],
        'label': f"{short_m} '{short_y}",
        'full_label': f"{short_m} {ym.split('-')[0]}",
        'days': n_days,
        'cal_days': cal_days,
        'expected_hours': eh,
        'is_partial': is_partial
    })

total_expected_per_stn = sum(month_expected.values())
agg_hours = daily_copy.groupby(['station', 'year_month'])['n_hours_pm25'].sum().reset_index()

stations_data = []
lowest = {'completeness_pct': 999.0}

for _, q in quality.iterrows():
    stn_label = q['label']
    loc_id = q['location_id']
    stn_agg = agg_hours[agg_hours['station'] == stn_label].set_index('year_month')['n_hours_pm25'].to_dict()
    
    stn_valid = 0
    monthly_records = []
    
    for mm in month_meta:
        ym = mm['key']
        vh = int(stn_agg.get(ym, 0))
        eh = mm['expected_hours']
        pct = round(min(100.0, (vh / eh * 100)), 1) if eh > 0 else 0.0
        stn_valid += vh
        
        monthly_records.append({
            'month': ym,
            'label': mm['label'],
            'full_label': mm['full_label'],
            'valid_hours': vh,
            'expected_hours': eh,
            'completeness_pct': pct
        })
        
        if q['status'] != 'EXCLUDED' and pct < lowest['completeness_pct']:
            lowest = {
                'station': stn_label,
                'location_id': loc_id,
                'status': q['status'],
                'month': ym,
                'month_label': mm['full_label'],
                'valid_hours': vh,
                'expected_hours': eh,
                'completeness_pct': pct
            }

    stn_pct = round(min(100.0, (stn_valid / total_expected_per_stn * 100)), 1)
    
    stations_data.append({
        'location_id': loc_id,
        'station': stn_label,
        'status': q['status'],
        'island': q['island'],
        'provinsi': q['provinsi'],
        'site_type': q['site_type'],
        'total_valid_hours': stn_valid,
        'total_expected_hours': total_expected_per_stn,
        'overall_completeness_pct': stn_pct,
        'monthly': monthly_records
    })

status_order = {'OK': 1, 'CAUTION': 2, 'EXCLUDED': 3}
stations_data.sort(key=lambda s: (status_order.get(s['status'], 9), s['station']))

net_valid = sum(s['total_valid_hours'] for s in stations_data)
net_expected = len(stations_data) * total_expected_per_stn
net_pct = round(net_valid / net_expected * 100, 1)

reliability_output = {
    'summary': {
        'network_valid_hours': net_valid,
        'network_expected_hours': net_expected,
        'overall_completeness_pct': net_pct,
        'total_stations': len(stations_data),
        'active_stations': sum(1 for s in stations_data if s['status'] != 'EXCLUDED'),
        'excluded_stations': sum(1 for s in stations_data if s['status'] == 'EXCLUDED'),
        'period_months': len(month_meta),
        'start_month': month_meta[0]['full_label'],
        'end_month': month_meta[-1]['full_label'],
        'lowest_station_month': lowest
    },
    'months': month_meta,
    'stations': stations_data
}

save_json(clean_nan(reliability_output), 'sensor_reliability_heatmap.json')

# ============================================================
# SELESAI
# ============================================================
print("\n" + "=" * 60)
print(f"SELESAI! {len(list(JSON_DIR.glob('*.json')))} file JSON dihasilkan di:")
print(f"  {JSON_DIR}")
print("=" * 60)
