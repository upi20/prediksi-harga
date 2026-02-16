# 📊 Aplikasi Prediksi Harga Produk

Aplikasi web interaktif untuk prediksi harga produk berdasarkan berbagai atribut dan tren historis. Menggunakan pendekatan **per-produk** dengan machine learning sebagai fallback untuk akurasi tinggi.

## ✨ Fitur Utama

### 1. **Prediksi Harga Per-Produk**
- Prediksi spesifik untuk setiap kombinasi atribut produk
- Model trend linear individual untuk setiap varian produk
- Fallback ke model global untuk produk yang belum ada di dataset
- Visualisasi riwayat dan proyeksi harga

### 2. **Versus — Perbandingan Dinamis**
- Bandingkan hingga 10 produk sekaligus
- Line chart tren harga aktual
- Perubahan harga (Δ) per bulan dalam Rupiah dan persentase
- Tabel perbandingan lengkap dengan total perubahan
- Ranking harga termurah dan penurunan terbesar

### 3. **Analisis Tren Harga**
- Visualisasi tren harga per produk
- Filter multi-atribut (kondisi, generasi, variant)
- Tabel rangkuman tren dengan indikator naik/turun/stabil
- Deteksi otomatis pola harga (naik, turun, stabil)

### 4. **Heatmap Interaktif**
- 5 jenis heatmap dengan filter lengkap:
  - Generasi × Variant
  - Generasi × Storage
  - Variant × Storage (dengan filter generasi)
  - Perbandingan antar kondisi produk
  - Perubahan harga antar bulan (Δ)
- Filter dinamis: kondisi, bulan, storage

### 5. **Evaluasi Model**
- Metrik akurasi: MAPE, MAE, R² Score
- Scatter plot aktual vs prediksi
- Perbandingan performa 3 model global:
  - XGBoost
  - Random Forest
  - Gradient Boosting
- Cross-validation results

### 6. **Analisis Statistik**
- Box plot distribusi harga per atribut
- Scatter plot korelasi storage-harga
- Dataset browser dengan multi-filter

## 🧠 Metode & Algoritma

### Pendekatan Per-Produk (Primary)
- **Linear Regression** untuk setiap kombinasi produk unik
- Menangkap tren spesifik: depresiasi produk bekas, stabilitas produk baru
- Leave-last-out evaluation untuk validasi
- **Akurasi**: MAPE ~2-3% pada produk dengan data cukup

### Model Global (Fallback)
Digunakan ketika produk tidak ada di dataset historis:

1. **XGBoost Regressor**
   - 200 trees, max depth 6
   - Best performer: R² > 0.99, MAPE ~1.6%
   - Features: interaction terms untuk kondisi × waktu

2. **Random Forest**
   - 200 estimators, max depth 12
   - Robust terhadap outliers

3. **Gradient Boosting**
   - Learning rate 0.1, 200 iterations
   - Sequential error correction

### Feature Engineering
- Kondisi tier encoding (BC/Second/New)
- Storage logaritmik transform
- Interaction features: Kondisi×Bulan, Depresiasi×Bulan, Age×Bulan
- Generasi age relative to latest

## 🏗️ Arsitektur Modular

```
├── app.py              # Main entry point (~170 lines)
├── data_loader.py      # Data loading & preprocessing
├── models.py           # ML models (per-product + global)
└── tabs/
    ├── tab_evaluasi.py    # Model evaluation
    ├── tab_tren.py        # Trend analysis
    ├── tab_versus.py      # Dynamic comparison (NEW)
    ├── tab_heatmap.py     # Interactive heatmaps
    ├── tab_analisis.py    # Statistical analysis
    └── tab_data.py        # Dataset browser
```

## 🛠️ Teknologi

| Kategori | Stack |
|----------|-------|
| **Framework** | Streamlit 1.50+ |
| **ML/Data** | scikit-learn, XGBoost, pandas, numpy |
| **Visualisasi** | Plotly Express, Plotly Graph Objects |
| **Language** | Python 3.9+ |

## 🚀 Instalasi & Menjalankan

### Prasyarat
- Python 3.9 atau lebih tinggi
- pip package manager

### Setup

```bash
# Clone repository
git clone <repository-url>
cd prediksi-harga

# Install dependencies
pip3 install streamlit xgboost plotly scikit-learn pandas

# Jalankan aplikasi
python3 -m streamlit run app.py
```

Aplikasi akan berjalan di `http://localhost:8501`

## 📊 Format Data

Dataset harus berformat CSV dengan kolom:
- `Bulan` — Tanggal (format: YYYY-MM-DD)
- `Kondisi` — Kondisi produk (contoh: New, Second, BC)
- `Generasi` — Generasi/model produk
- `Variant` — Varian produk
- `Storage` — Kapasitas penyimpanan (GB)
- `Harga` — Harga dalam Rupiah

Contoh:
```csv
Bulan,Kondisi,Generasi,Variant,Storage,Harga
2025-10-01,New,Gen 15,Pro Max,256,15000000
```

## 🎯 Use Cases

- **E-commerce**: Prediksi harga kompetitif
- **Marketplace**: Estimasi harga jual optimal
- **Inventory Management**: Forecasting nilai aset
- **Research**: Analisis tren pasar produk elektronik
- **Price Comparison**: Benchmark harga antar varian

## 📈 Performa Model

| Model | MAPE | R² Score | Use Case |
|-------|------|----------|----------|
| Per-Product Linear | ~2.5% | Varies | Produk dalam dataset |
| XGBoost Global | ~1.6% | 0.9975 | Produk baru/tidak dikenal |
| Random Forest | ~2.1% | 0.9968 | Alternative fallback |
| Gradient Boosting | ~2.3% | 0.9945 | Robust prediction |

## 🔍 Fitur Tambahan

- **Auto-detection** tren harga (naik/turun/stabil)
- **Cascading filters** untuk navigasi intuitif
- **Responsive layout** dengan Streamlit columns
- **Interactive charts** dengan Plotly hover info
- **Export-ready** data tables
- **Cache optimization** untuk performa cepat

## 📝 Catatan

- Model per-produk memerlukan minimal 2 data points historis
- Prediksi di luar rentang data historis diberi warning
- Storage 1000GB otomatis dinormalisasi ke 1024GB
- Variant dengan nama warna dinormalisasi ke base variant

## 🤝 Kontribusi

Proyek ini menggunakan arsitektur modular untuk memudahkan pengembangan:
- Tambahkan tab baru di `tabs/`
- Extend feature engineering di `data_loader.py`
- Implementasi model baru di `models.py`

---

**Built with ❤️ using Python & Streamlit**
