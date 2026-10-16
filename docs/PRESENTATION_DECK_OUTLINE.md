# Outline Dek Presentasi Final Project UlasRasa
**Ruangguru AI Engineering Bootcamp - Batch 13**  
**Student ID:** REAENG13TQJLN | **Nama:** Azura  
**Judul:** *UlasRasa: Asisten Diagnostik Ulasan Kuliner & Rekomendasi Evaluasi Dapur UMKM Berbasis NLP dan LLM*

---

## Slide 1: Title & Executive Summary
* **Judul Proyek:** UlasRasa
* **Subjudul:** *Aspect-Based Sentiment Analysis & Automated Kitchen Action Plan Engine for Indonesian F&B*
* **Student Identity:** Azura (REAENG13TQJLN)
* **Kategori:** *Text-Based Natural Language Processing & Generative AI*
* **Core Value:** Mengubah keluhan pelanggan tidak terstruktur di platform pesan-antar (*GoFood, GrabFood, ShopeeFood, Google Reviews*) menjadi diagnostik 5 aspek kualitas dan *checklist* perbaikan dapur konkret.

---

## Slide 2: Model Objective (Poin 1 Rubrik)
* **Latar Belakang Industri:**
  * Pertumbuhan pesat GMV pasar pesan-antar makanan di Indonesia (*food delivery*).
  * Tingginya tingkat kehilangan pelanggan (*customer churn*) akibat inkonsistensi rasa, porsi menyusut (*shrinkflation*), dan kemasan tumpah.
* **Problem Statement:**
  * *Review overload*: Resto aktif menerima ratusan ulasan harian lintas platform tanpa kapasitas untuk membaca manual satu per satu.
  * *Failure of generic sentiment*: Analisis sentimen biner (positif vs negatif) gagal mendeteksi *mixed sentiments* dan tidak memberikan rekomendasi operasional.
* **Tujuan Spesifik Model:**
  1. Mengekstraksi 5 aspek kualitas operasional (Rasa, Porsi, Harga, Kemasan, Pelayanan) secara independen dari ulasan bahasa Indonesia liar/informal.
  2. Mengkuantifikasi performa operasional dapur melalui metrik terbobot *Kitchen Health Score* (KHS).
  3. Mengotomasi pembuatan *action checklist* dapur dan SOP preventif berbasis sintesis LLM.

---

## Slide 3: Model Description & System Architecture (Poin 2 Rubrik)
* **Paradigma Hybrid AI:**
  * Menggabungkan *Discriminative NLP* (IndoBERT) untuk klasifikasi aspek yang deterministik dan cepat, dengan *Generative AI* (LLM) untuk penalaran kontekstual dan pembuatan rekomendasi.
* **Arsitektur Sistem (5-Stage Pipeline):**
  1. *Ingestion Layer*: Menerima batch review CSV / input ulasan teks tunggal.
  2. *Normalization Layer*: Pembersihan slang bahasa Indonesia, eliminasi derau emoji, dan standardisasi istilah.
  3. *Discriminative ABSA Layer*: IndoBERT Fine-Tuned / Multi-head Classification Head memprediksi status ketersebutan (*mention status*) dan polaritas sentimen (Positif, Netral, Negatif) pada 5 aspek.
  4. *Aggregation Engine*: Perhitungan rasio kepuasan aspek dan *Kitchen Health Score* terbobot.
  5. *Generative Action Engine*: LLM merangkum akar masalah (*root cause*) dan menyusun *kitchen checklist* siap cetak.

---

## Slide 4: Dataset & Preprocessing (Poin 4 Rubrik)
* **Sumber Data Primer & Sekunder:**
  * *Benchmark Base*: IndoNLU benchmark corpus (SmSA & adaptasi transfer learning ABSA).
  * *Domain Adaptation Dataset*: 1.000+ data ulasan riil kuliner Indonesia (restoran lokal, warung geprek, cafe) dari Google Maps & GoFood.
* **Skema Anotasi 5 Aspek Kunci:**
  * **Rasa:** Kelezatan, keasinan, kepedasan, bumbu meresap, kematangan (*keywords*: gurih, hambar, keasinan, alot).
  * **Porsi:** Kuantitas makanan, rasio nasi vs lauk (*keywords*: porsi kuli, kenyang, ciut, dikit).
  * **Harga:** *Value for money* (*keywords*: sebanding, worth it, mahal, kemahalan, kantong).
  * **Kemasan:** Integritas fisik pengiriman (*keywords*: tumpah, bocor, rembes, mika pecah, segel).
  * **Pelayanan:** Kecepatan dapur dan kelengkapan (*keywords*: lama, driver nunggu, salah menu, sendok).
* **Tahapan Prapemrosesan:**
  * *Lowercasing & Unicode Normalization (NFKD)*.
  * *Slang Normalization Dictionary* (normalisasi 50+ kata gaul Indonesia: bgt, bgtu, pol, ga, bener2).
  * *Emoji Stripping & Non-ASCII Filtration*.

---

## Slide 5: Methodology & Mathematical Formulation (Poin 5 Rubrik)
* **Klasifikasi Aspek & Sentimen (Multi-Label ABSA):**
  * Teks ulasan diproses ke representasi vektor kontekstual.
* **Formulasi Kuantitatif Kitchen Health Score (KHS):**
  * Misal terdapat $K = 5$ aspek dengan bobot operasional $w_k$ ($\sum_{k=1}^K w_k = 1.0$):
    * Bobot: Rasa ($w_1 = 0.35$), Porsi ($w_2 = 0.20$), Kemasan ($w_3 = 0.15$), Harga ($w_4 = 0.15$), Pelayanan ($w_5 = 0.15$).
  * Tingkat kepuasan per aspek ($S_k$):
    $$\displaystyle S_k = \frac{N_k^+ + 0.5 \cdot N_k^0}{N_k^+ + N_k^0 + N_k^-} \times 100\%$$
  * *Kitchen Health Score* Akhir:
    $$\displaystyle \text{KHS} = \sum_{k=1}^K w_k \cdot S_k$$
* **Prompt Engineering untuk Generative Action Engine:**
  * *Constrained Structured Prompting*: LLM menerima payload JSON ringkasan komplain negatif dan menghasilkan rekomendasi dengan format:
    1. Analisis Gejala & Frekuensi
    2. Dugaan Akar Masalah (*Root Cause*)
    3. Checklist Tindakan Dapur Langsung (*Actionable Tasks*)
    4. Rekomendasi SOP Baku

---

## Slide 6: Evaluation Metrics & Experimental Results (Poin 3 Rubrik)
* **Metrik Evaluasi Kuantitatif ABSA:**
  * *Macro-Averaged F1-Score*: Mengukur performa klasifikasi berimbang antar-kelas sentimen (positif, netral, negatif) guna mengantisipasi *class imbalance*.
  * *Precision & Recall per Aspek*: Memastikan minimnya *false positive* pada komplain dapur.
  * *Target Benchmark*: Macro-F1 $\ge 0.82$ pada ulasan domain kuliner.
* **Evaluasi Kualitatif Modul Generatif LLM:**
  * *Actionability Rate*: Rasio rekomendasi yang dapat dieksekusi langsung tanpa interpretasi ambigu oleh kru dapur.
  * *Domain Faithfulness / Hallucination Rate*: Menjamin rekomendasi hanya berasal dari keluhan faktual dalam batch ulasan, bukan halusinasi menu yang tidak dijual resto.
* **Efisiensi Komputasi & Latensi:**
  * Latensi inferensi IndoBERT: $\le 120\text{ ms}$ per kalimat pada CPU standar.
  * Latensi pipeline generatif LLM: $\le 2.5\text{ detik}$ per ringkasan batch 50 ulasan.

---

## Slide 7: Challenges, Learnings & Future Improvements (Poin 6 & 7 Rubrik)
* **Tantangan yang Dihadapi (*Challenges*):**
  * *Linguistic Nuances*: Tingginya penggunaan sarkasme, singkatan ekstrem, dan istilah kuliner lokal khas daerah (misal: "bumbu medok", "prengus", "alot").
  * *Mixed Sentiment Granularity*: Satu kalimat ulasan sering memuji rasa namun mengkritik keras kemasan dan waktu tunggu secara bersamaan.
  * *Inference Constraints*: Kebutuhan deployment di platform publik gratis (*Hugging Face Spaces CPU*) tanpa latensi tinggi.
* **Pembelajaran Kunci (*Key Learnings*):**
  * Arsitektur *hybrid* (IndoBERT + LLM) jauh lebih superior dibanding *pure LLM zero-shot* dalam hal efisiensi biaya API, kecepatan inferensi, dan konsistensi deterministik angka.
  * Normalisasi *slang dictionary* lokal menyumbang peningkatan F1-score sebesar $6\text{--}8\%$ pada data ulasan informal.
* **Peluang Pengembangan Masa Depan (*Future Improvements*):**
  * *Multimodal Kitchen QA*: Menganalisis foto kondisi makanan yang diunggah pelanggan (misal: mendeteksi gosong atau tumpah via CNN/Vision-Language Model).
  * *Multi-Outlet Benchmarking*: Dashboard perbandingan performa antar-cabang resto bagi pemilik bisnis waralaba (*franchise*).
  * *Automated Customer Reply Generator*: Pembuatan draf respon permintaan maaf dan klarifikasi resmi kepada pelanggan di aplikasi GoFood/GrabFood.

---

## Slide 8: Working Demo & Deployment Link (Poin 8 Rubrik)
* **Tautan Aplikasi Aktif (Working Demo):**
  * Hugging Face Spaces: `https://huggingface.co/spaces/azura/ulasrasa`
  * Repositori GitHub: `https://github.com/geovanybramanthya/ulasrasa`
* **Fitur Utama yang Ditampilkan:**
  1. *Executive Dashboard & Health Score Gauge*.
  2. *Aspect Sentiment Breakdown & Complaint Log*.
  3. *Interactive AI Kitchen Action Checklist & Printable Text Export*.
  4. *Single Review Diagnostic Simulator*.
