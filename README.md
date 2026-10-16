---
title: UlasRasa - AI Kitchen Intelligence Dashboard
emoji: 🍲
colorFrom: red
colorTo: yellow
sdk: streamlit
sdk_version: "1.38.0"
app_file: app.py
pinned: false
license: mit
---

# 🍲 UlasRasa — AI Kitchen Intelligence & Sentiment Dashboard
**Ruangguru AI Engineering Bootcamp - Batch 13 Final Project**  
*Student ID:* `REAENG13TQJLN` | *Author:* Azura

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://huggingface.co/spaces/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🎯 1. Deskripsi & Latar Belakang Masalah
Pelaku bisnis kuliner dan UMKM F&B di Indonesia sering mengalami *review overload* dari platform pesan-antar makanan (GoFood, GrabFood, ShopeeFood). Analisis sentimen konvensional hanya mengklasifikasikan ulasan secara biner (positif vs negatif), yang gagal menangkap *mixed sentiment* (contoh: *"Ayamnya gurih lezat, tapi sambalnya sedikit dan kemasan mangkok kuahnya tumpah di jalan"*).

**UlasRasa** hadir sebagai solusi berbasis *Aspect-Based Sentiment Analysis (ABSA)* dan *Generative AI Action Engine* yang secara otomatis:
1. Membedah ulasan ke dalam **5 aspek operasional**: *Rasa*, *Porsi*, *Harga*, *Kemasan*, dan *Pelayanan*.
2. Mengkalkulasi indeks performa kuantitatif **Kitchen Health Score (KHS)** (0–100%).
3. Menerjemahkan ulasan negatif menjadi **AI Kitchen Action Checklist** yang konkret, interaktif, dan dapat diunduh (TXT & PDF) untuk langsung dieksekusi kru dapur.

---

## 🏗️ 2. Arsitektur Frontend-Backend di Streamlit

Aplikasi dirancang dengan pemisahan tanggung jawab (*Separation of Concerns*) yang ketat:

```
ulasrasa/
├── .streamlit/
│   └── config.toml             # Konfigurasi headless server & port 7860 untuk HF Spaces
├── data/
│   └── sample_reviews.csv      # Dataset 20 ulasan anotasi multi-aspek F&B
├── src/
│   ├── absa_pipeline.py        # Mesin klasifikasi ABSA 5 aspek & kalkulasi KHS
│   ├── action_engine.py        # Mesin generatif penalaran akar masalah & rekomendasi SOP
│   ├── preprocessing.py        # Normalisasi slang bahasa Indonesia & sanitasi teks
│   └── utils/
│       └── exporter.py         # Generator ekspor laporan Text & PDF (ReportLab)
├── tests/
│   └── test_pipeline.py        # Unit testing otomatis pipeline & evaluasi KHS
├── app.py                      # Streamlit entry point (4 Tab Interaktif)
├── requirements.txt            # Pustaka Python terpin untuk cloud CPU runtime
└── README.md                   # HF Spaces metadata & dokumentasi teknis
```

### 4 Tab Fungsionalitas Utama:
1. **Tab 1: Ringkasan Eksekutif & Health Score**  
   - KPI metric cards (KHS %, Delta baseline, Status operasional).
   - Spider / Radar Chart Plotly interaktif memetakan kepuasan 5 aspek.
   - Matriks tabular lengkap: Total ulasan, rasio kepuasan, dan rasio komplain.
2. **Tab 2: Deep-Dive Aspek & Sentimen**  
   - Filter aspek dinamis.
   - Stacked Bar Chart distribusi sentimen lintas 5 dimensi.
   - N-Gram / Top Kata Kunci Komplain untuk investigasi akar masalah keluhan.
   - Riwayat ulasan negatif per menu.
3. **Tab 3: AI Kitchen Action Checklist**  
   - Ringkasan akar masalah operasional (*Root Cause Analysis*).
   - Interactive tickable checklist kru dapur yang tersimpan di `st.session_state`.
   - Download tombol ganda: Format Text (`.txt`) dan Dokumen Cetak PDF (`.pdf`).
4. **Tab 4: Single Review Simulator**  
   - Demo inferensi real-time ulasan bebas berbahasa Indonesia.
   - Deteksi otomatis aspek relevan, polaritas sentimen, tingkat keyakinan (*confidence score*), dan rekomendasi SOP dapur instan.

---

## 🧮 3. Formulasi Matematis Kitchen Health Score (KHS)

Tingkat kepuasan $S_k$ per aspek $k \in \{\text{Rasa}, \text{Porsi}, \text{Harga}, \text{Kemasan}, \text{Pelayanan}\}$:
$$S_k = \frac{N_k^+ + 0.5 \cdot N_k^0}{N_k^+ + N_k^0 + N_k^-} \times 100\%$$

Skor komposit terbobot:
$$\text{KHS} = \sum_{k=1}^5 w_k \cdot S_k$$
dengan vektor bobot operasional dapur:
$$w = [w_{\text{rasa}}=0.35, \, w_{\text{porsi}}=0.20, \, w_{\text{kemasan}}=0.15, \, w_{\text{harga}}=0.15, \, w_{\text{pelayanan}}=0.15]$$

---

## 🚀 4. Panduan Menjalankan Secara Lokal & Deployment

### Menjalankan Lokal:
```bash
# 1. Clone repositori
git clone <repo-url>
cd ulasrasa

# 2. Pasang dependensi
pip install -r requirements.txt

# 3. Jalankan aplikasi Streamlit
streamlit run app.py
```

### Deployment ke Hugging Face Spaces:
1. Buat Space baru di [Hugging Face Spaces](https://huggingface.co/spaces) dengan SDK **Streamlit**.
2. Hubungkan git remote Spaces:
   ```bash
   git remote add space https://huggingface.co/spaces/<username>/ulasrasa
   git push space main
   ```
3. Space akan otomatis membangun environment berdasarkan `requirements.txt` dan mengeksekusi `app.py`.
