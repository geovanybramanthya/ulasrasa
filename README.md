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
# UlasRasa - AI Kitchen Intelligence & Sentiment Dashboard

**Ruangguru AI Engineering Bootcamp - Batch 13 Final Project**
*Student ID:* `REAENG13TQJLN` | *Author:* Geovany Bramanthya Samuel Sihombing

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://huggingface.co/spaces/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 1. Deskripsi & Latar Belakang Masalah

Pelaku bisnis kuliner dan UMKM F&B di Indonesia sering mengalami *review overload* dari platform pesan-antar makanan (GoFood, GrabFood, ShopeeFood). Analisis sentimen konvensional hanya mengklasifikasikan ulasan secara biner (positif vs negatif), yang gagal menangkap *mixed sentiment* (contoh: *"Ayamnya gurih lezat, tapi sambalnya sedikit dan kemasan mangkok kuahnya tumpah di jalan"*).

**UlasRasa** adalah solusi berbasis *Aspect-Based Sentiment Analysis (ABSA)* dan *Generative AI Action Engine* yang secara otomatis:

1. Membedah ulasan ke dalam **5 aspek operasional**: *Rasa*, *Porsi*, *Harga*, *Kemasan*, dan *Pelayanan*, masing-masing dengan label `positive`, `neutral`, `negative`, atau `not_mentioned`.
2. Mengkalkulasi indeks performa kuantitatif **Kitchen Health Score (KHS)** (0-100%).
3. Menerjemahkan ulasan negatif menjadi **AI Kitchen Action Checklist** yang konkret, interaktif, dan dapat diunduh (TXT & PDF) untuk langsung dieksekusi kru dapur.

---

## 2. Arsitektur Sistem

Aplikasi memakai **satu engine ABSA utama** dengan fallback yang terukur, plus engine rekomendasi berjenjang:

| Komponen | Implementasi | Peran |
| :--- | :--- | :--- |
| Engine ABSA utama | **IndoBERT Base** (`indobenchmark/indobert-base-p1`) hasil *fine-tune* lokal, di `models/indobert-base-absa` | Klasifikasi pasangan (ulasan, aspek) ke 4 kelas per aspek; *confidence* = probabilitas *softmax* model |
| Engine ABSA cadangan | Lexicon/kata kunci (`src/absa_pipeline.py`) | *Baseline* evaluasi + *fallback* otomatis bila model tidak tersedia/gagal dimuat |
| Action Engine | LLM **Gemini** -> **Groq** -> katalog template (`src/action_engine.py`) | Menghasilkan *root cause analysis*, checklist dapur, dan rekomendasi SOP dari payload agregat keluhan (bukan seluruh ulasan mentah) |

Transparansi mode bersifat eksplisit di UI: aplikasi menampilkan caption engine ABSA yang sedang aktif ("IndoBERT (fine-tuned)" atau "Lexicon (fallback)") dan mode rekomendasi yang dipakai ("LLM (gemini/groq)" atau "Template (offline)"). Tanpa API key, aplikasi tetap berfungsi penuh dalam mode template.

```
ulasrasa/
|-- data/
|   |-- sample_reviews.csv        # Dataset inti kurasi manual (100 ulasan, 5 aspek)
|   |-- external_validation.csv   # 45 ulasan asli SmSA untuk validasi eksternal
|   `-- holdout_ids.json          # 25 ID hold-out beku (seed 42)
|-- models/
|   |-- indobert-base-absa/       # Model utama hasil fine-tune + tokenizer
|   `-- indobert-lite-absa/       # Model pembanding (kalah evaluasi, tidak dipakai)
|-- src/
|   |-- models/transformer_engine.py  # Engine IndoBERT (drop-in pengganti pipeline)
|   |-- absa_pipeline.py              # Engine lexicon (baseline & fallback) + KHS
|   |-- action_engine.py              # LLM Gemini/Groq -> template + cache payload
|   `-- preprocessing.py              # Normalisasi slang Indonesia & sanitasi teks
|-- training/                         # Script fine-tune + notebook Colab
|-- evaluation/evaluation_results.json  # Hasil evaluasi resmi di hold-out
|-- tests/                            # Unit test pipeline, KHS, dan action engine
|-- app.py                            # Streamlit entry point (4 modul interaktif)
`-- requirements.txt
```

### 4 Modul Fungsionalitas Utama

1. **Ringkasan Eksekutif & Health Score** - KPI KHS, radar chart 5 aspek, matriks kepuasan per aspek.
2. **Deep-Dive Aspek & Sentimen** - filter aspek, distribusi sentimen, kata kunci komplain, riwayat ulasan negatif.
3. **AI Kitchen Action Checklist** - *root cause analysis*, checklist interaktif tersimpan di `st.session_state`, ekspor TXT & PDF.
4. **Single Review Simulator** - inferensi langsung pada teks ulasan bebas dengan engine ABSA aktif.

---

## 3. Dataset

Kejujuran sumber data adalah bagian dari desain proyek ini:

- **Dataset inti (training & evaluasi):** dataset kurasi manual berisi **100 ulasan yang ditulis meniru pola ulasan platform pesan-antar, dianotasi manual ke 5 aspek operasional** (Rasa, Porsi, Harga, Kemasan, Pelayanan) untuk 4 restoran fiktif. Dataset ini **bukan** ulasan asli yang dikumpulkan dari platform; ia ditulis tangan (lihat `scripts/generate_rich_dataset.py`) agar pola *mixed sentiment* khas keluhan F&B terwakili secara terkendali.
- **Hold-out beku:** 25 dari 100 ulasan dipisahkan dan dibekukan (`data/holdout_ids.json`, *seed* 42, stratifikasi per restoran) **sebelum** proses *fine-tune*; ke-25 ulasan ini tidak pernah masuk data training.
- **Set validasi eksternal:** 45 ulasan **asli** dari korpus SmSA (IndoNLU, lisensi **CC BY-SA 4.0**) yang disaring ke topik kuliner dan dianotasi ke skema 5 aspek yang sama, tersimpan di `data/external_validation.csv`. Set ini hanya dipakai untuk validasi eksternal, bukan training dan bukan hold-out. Detail sumber dan keterbatasannya ada di `docs/external_validation_notes.md`.

---

## 4. Evaluasi Model

Metrik resmi adalah **Macro-F1 per aspek** pada hold-out beku yang sama untuk semua engine (konvensi *scikit-learn*: kelas yang absen di gold dan prediksi dikeluarkan dari rata-rata). Hasil lengkap beserta *confusion matrix* per aspek tersimpan di `evaluation/evaluation_results.json`.

| Aspek | Lexicon (baseline) | IndoBERT Lite | IndoBERT Base |
| :--- | ---: | ---: | ---: |
| Rasa | 0,6799 | 0,1795 | 0,2684 |
| Porsi | 0,4150 | 0,1094 | 0,4672 |
| Harga | 0,4470 | 0,1765 | 0,8003 |
| Kemasan | 0,4206 | 0,1290 | 0,6772 |
| Pelayanan | 0,4264 | 0,1905 | 0,7489 |
| **Overall Macro-F1** | **0,4778** | **0,1570** | **0,5924** |

**Aturan pemilihan engine:** engine utama adalah model dengan *overall* Macro-F1 tertinggi pada hold-out yang sama. Berdasarkan aturan itu, **IndoBERT Base (0,5924)** menjadi engine utama; IndoBERT Lite (0,1570) kalah dari baseline dan tidak dipakai; lexicon (0,4778) tetap dipertahankan sebagai baseline dan fallback.

Catatan kejujuran evaluasi:

- Lexicon dikembangkan terhadap dataset sebelum hold-out dibekukan, sehingga angka baselinenya adalah perbandingan internal, bukan estimasi generalisasi murni. IndoBERT justru tidak pernah melihat hold-out selama training.
- IndoBERT Base masih kalah dari lexicon pada aspek **Rasa** (0,2684 vs 0,6799) - keterbatasan data training (75 ulasan) yang dilaporkan apa adanya, dan menjadi agenda perbaikan utama (penambahan data latih berlabel).

---

## 5. Formulasi Matematis Kitchen Health Score (KHS)

Tingkat kepuasan $S_k$ per aspek $k \in \{\text{Rasa}, \text{Porsi}, \text{Harga}, \text{Kemasan}, \text{Pelayanan}\}$:

$$S_k = \frac{N_k^+ + 0{,}5 \cdot N_k^0}{N_k^+ + N_k^0 + N_k^-} \times 100\%$$

Skor komposit terbobot:

$$\text{KHS} = \sum_{k=1}^5 w_k \cdot S_k$$

dengan vektor bobot operasional dapur:

$$w = [w_{\text{rasa}}=0{,}35, \; w_{\text{porsi}}=0{,}20, \; w_{\text{kemasan}}=0{,}15, \; w_{\text{harga}}=0{,}15, \; w_{\text{pelayanan}}=0{,}15]$$

Rumus ini identik di kedua engine, sehingga KHS selalu dapat dibandingkan antar engine.

---

## 6. Panduan Menjalankan & Deployment

### Menjalankan Lokal

```bash
# 1. Clone repositori
git clone <repo-url>
cd ulasrasa

# 2. Pasang dependensi
pip install -r requirements.txt

# 3. (Opsional) Aktifkan mode LLM untuk Action Engine
#    Tanpa kedua key ini, aplikasi berjalan dalam mode template.
set GEMINI_API_KEY=<key-anda>        # Windows; gunakan export di Linux/macOS
set GROQ_API_KEY=<key-anda>          # cadangan, opsional

# 4. Jalankan aplikasi Streamlit
streamlit run app.py
```

Catatan operasional:

- Model IndoBERT dimuat dari `models/indobert-base-absa` (dapat dioverride dengan env `ULASRASA_MODEL_PATH`). Bila folder model tidak ditemukan, aplikasi otomatis memakai engine lexicon dan menampilkannya secara transparan di UI.
- Upload dataset CSV dibatasi **maksimum 200 baris** per analisis (batasan runtime CPU); file yang lebih besar ditolak dengan pesan penjelasan.
- API key tidak pernah ditulis di kode; di Hugging Face Spaces, simpan sebagai **Secrets** (`GEMINI_API_KEY`, `GROQ_API_KEY`).

### Deployment ke Hugging Face Spaces

1. Buat Space baru di [Hugging Face Spaces](https://huggingface.co/spaces) dengan SDK **Streamlit**.
2. Hubungkan git remote Spaces:
   ```bash
   git remote add space https://huggingface.co/spaces/<username>/ulasrasa
   git push space main
   ```
3. Tambahkan `GEMINI_API_KEY` (dan opsional `GROQ_API_KEY`) di menu **Settings -> Secrets** Space bila ingin mode LLM aktif.
4. Space akan otomatis membangun environment berdasarkan `requirements.txt` dan mengeksekusi `app.py`.
