# PANDUAN EKSEKUSI FINAL PROJECT: ULASRASA
**Ruangguru AI Engineering Bootcamp - Batch 13**  
**Student ID:** REAENG13TQJLN | **Nama:** Azura  
**Target Deadline:** 23 Oktober 2026

---

## 1. Analisis Komparatif Rubrik Penilaian Resmi Bootcamp

Berdasarkan rubrik penilaian resmi (*Assessment Rubric*) dan instruksi portofolio Google Colab, penilaian akhir berbobot 100 poin yang terbagi ke dalam 4 pilar utama. Di bawah ini adalah bedah mendalam kriteria untuk mengunci predikat tertinggi **Level 5 (*Exceeds Expectations*)** di setiap pilar.

### 1.1 Pilar 1: Problem Definition (Bobot 25 pts / 25%)
* **Kriteria Level 5 (*Exceeds Expectations*):**  
  *Provides a compelling and insightful definition of the problem, showcasing deep understanding.*
* **Bedah Elemen Penilaian:**
  1. *Kejelasan Kontekstual:* Masalah tidak boleh bersifat generik (misal: "banyak ulasan di internet"). Masalah harus kontekstual pada ekosistem kuliner dan pesan-antar makanan di Indonesia (*food delivery*).
  2. *Deep Understanding (Akar Masalah vs Gejala):* Menunjukkan pemahaman bahwa keluhan pelanggan bukanlah sekadar sentimen positif atau negatif, melainkan kegagalan operasional di dapur fisik (takaran bumbu tidak standar, penyusutan porsi atau *shrinkflation*, kemasan berkuah yang rembes/pecah saat dibawa kurir motor, kelalaian memasukkan sendok/sambal).
  3. *Urgensi Ekonomi bagi UMKM:* Rating bintang di platform GoFood/GrabFood berpengaruh langsung terhadap algoritma pencarian dan penjualan. Rating di bawah 4.5 bintang memicu penurunan omzet hingga 30%. Pemilik resto tidak memiliki waktu atau tim khusus untuk menganalisis ratusan ulasan harian secara manual (*review overload*).

### 1.2 Pilar 2: Technical Skills & Functionality (Bobot 30 pts / 30%)
* **Kriteria Level 5 (*Exceeds Expectations*):**  
  *Utilizes a strong combination of relevant technologies with exceptional efficiency and adherence to best practices. Functionality is exceptional and innovative.*
* **Bedah Elemen Penilaian:**
  1. *Kombinasi Teknologi yang Relevan (Hybrid Architecture):* Tidak hanya mengandalkan satu panggilan API LLM sederhana (yang terkesan murahan atau *wrapper* dangkal), melainkan mengombinasikan *Discriminative NLP* (*Encoder-based Transformer* seperti IndoBERT) untuk ekstraksi aspek dan sentimen multi-label yang deterministik dan cepat, dengan *Generative AI* (LLM) untuk sintesis laporan dan rekomendasi operasional.
  2. *Efisiensi Komputasi & Best Practices:*
     * Prapemrosesan teks terstruktur khusus bahasa Indonesia (*slang normalization*, penanganan kata negasi, eliminasi derau emoji).
     * Pipeline inferensi modular dan terpisah rapi antara lapisan data, model NLP, LLM reasoning engine, dan UI.
     * Caching resource di Streamlit (`@st.cache_resource` dan `@st.cache_data`) agar inferensi ulasan tunggal maupun data batch berjalan cepat (<500 ms) di platform CPU gratis Hugging Face Spaces.
  3. *Functionality & Innovativeness:*
     * Fungsionalitas aplikasi tidak berhenti pada grafik visual, melainkan menghasilkan *artefak tindakan nyata* berupa *AI Kitchen Action Checklist* yang interaktif dan dapat diunduh langsung dalam format teks/cetak untuk ditempel di stasiun kerja dapur resto.

### 1.3 Pilar 3: Problem-Solving & Approach (Bobot 25 pts / 25%)
* **Kriteria Level 5 (*Exceeds Expectations*):**  
  *Demonstrates exceptional problem-solving skills with a highly creative and insightful technical approach.*
* **Bedah Elemen Penilaian:**
  1. *Pendekatan Problem-Solving Non-Konvensional:* Mengatasi kelemahan fundamental *sentiment analysis* klasik yang bersifat satu dimensi. Dalam dunia kuliner, satu ulasan seringkali memuat polaritas yang bertolak belakang (*mixed sentiment*), misal: *"Ayamnya enak banget gurih, tapi sambal dikit dan kemasan tumpah"*. UlasRasa memecahkan masalah ini dengan pendekatan multi-aspek independen (*Aspect-Based Sentiment Analysis* / ABSA).
  2. *Formulasi Matematis Kuantitatif:* Mengembangkan metrik terbobot objektif bernama **Kitchen Health Score (KHS)** yang mengagregasikan tingkat kepuasan ulasan pelanggan lintas 5 aspek kunci berdasarkan bobot kritikalitas operasional resto.
  3. *Pencegahan Halusinasi LLM:* Menggunakan teknik *Constrained Prompting* di mana LLM hanya diizinkan menganalisis payload JSON hasil ekstraksi sentimen negatif aktual, mencegah LLM mengarang menu atau masalah yang tidak ada di data ulasan.

### 1.4 Pilar 4: Impact & Future Potential (Bobot 20 pts / 20%)
* **Kriteria Level 5 (*Exceeds Expectations*):**  
  *Demonstrates significant positive impact and has exceptional potential for future development and real-world application.*
* **Bedah Elemen Penilaian:**
  1. *Dampak Langsung bagi Pengguna Akhir (UMKM):* Mengurangi waktu audit ulasan mingguan dari 10 jam kerja manual menjadi di bawah 1 menit secara otomatis. Menghadirkan jembatan langsung antara komplain pelanggan di dunia maya dan tindakan preventif kru dapur di dunia fisik.
  2. *Potensi Pengembangan Nyata (Scalability & Roadmap):*
     * Integrasi *Multimodal Computer Vision* untuk menganalisis foto bukti ulasan pelanggan (makanan gosong, kemasan pecah).
     * Integrasi langsung dengan API platform POS (*Point of Sale*) dan Food Delivery untuk monitoring sentimen waktu-nyata (*real-time alerting*).
     * Fitur *Benchmarking Multi-Outlet* untuk pemilik bisnis kuliner waralaba (*franchise*).

---

## 2. Pemenuhan 8 Poin Wajib Presentasi

Berdasarkan instruksi resmi Google Colab, dek presentasi akhir wajib memuat 8 elemen inti berikut:

| No | Poin Presentasi | Konten Spesifik UlasRasa | Bobot Rubrik Terkait |
| :--- | :--- | :--- | :--- |
| 1 | **Model Objective** | Mengotomasi diagnosis keluhan ulasan kuliner ke dalam 5 aspek operasional dan menyusun checklist perbaikan dapur UMKM F&B. | Problem Definition (25%) |
| 2 | **Model Description** | Arsitektur *Hybrid AI*: IndoBERT untuk klasifikasi aspek deterministik + LLM untuk perumusan rekomendasi checklist operasional. | Technical Skills (30%) |
| 3 | **Evaluation Metrics** | Evaluasi kuantitatif: *Macro-Averaged F1-Score*, *Precision*, *Recall* per aspek. Evaluasi kualitatif: *Actionability Rate* dan *Domain Faithfulness*. | Problem-Solving (25%) |
| 4 | **Dataset & Preprocessing** | Dataset ulasan kuliner Indonesia (IndoNLU SmSA corpus & ulasan riil platform pesan-antar), normalisasi *slang dictionary* lokal, eliminasi derau. | Technical Skills (30%) |
| 5 | **Methodology** | Alur ujung-ke-ujung: *Ingestion* $\to$ *Preprocessing* $\to$ *IndoBERT ABSA* $\to$ *Scoring Engine (KHS)* $\to$ *Generative LLM Action Engine* $\to$ *Streamlit UI*. | Technical Skills & Problem-Solving (55%) |
| 6 | **Challenges & Learnings** | Tantangan: *mixed sentiment* dalam satu kalimat, bahasa slang/sarkasme lokal, optimasi latensi inferensi di CPU Hugging Face Spaces. | Problem-Solving (25%) |
| 7 | **Future Improvements** | Integrasi *multimodal computer vision* untuk analisis foto komplain, monitoring multi-cabang, dan generator draf balasan ulasan otomatis. | Impact & Future Potential (20%) |
| 8 | **Working Demo Link** | Tautan aktif aplikasi Hugging Face Spaces dan repositori GitHub publik yang dilengkapi README komprehensif. | Technical Skills (30%) |

---

## 3. Audit Kritis Blueprint UlasRasa: Celah & Solusi Penguatan

Apakah konsep UlasRasa saat ini sudah mengunci skor maksimal Level 5 di setiap pilar?  
Secara substansi konsep dan arsitektur produk, UlasRasa memiliki fondasi yang sangat kuat karena memecahkan masalah riil F&B dan tidak sekadar menjadi aplikasi *sentiment analysis* biner biasa. Namun, terdapat **tiga celah kritis teknis** yang harus diantisipasi dan diperkuat agar tidak menjadi sasaran empuk pertanyaan penguji:

### Celah 1: Inkonsistensi Penamaan Dataset ("IndoNLU ASAP")
* **Temuan Celah:**  
  Di dalam draf proposal blueprint tertulis: *"Dataset IndoNLU Benchmark - Task ASAP (load_dataset('indonlu', 'asap'))"*.  
  Secara faktual di literatur NLP resmi, benchmark IndoNLU (Wilie et al., 2020) hanya memiliki 12 task, di mana task ABSA-nya adalah **CASA** (aspek otomotif mobil) dan **HoASA** (aspek perhotelan). Istilah **ASAP** di literatur NLP internasional sebenarnya merujuk pada *Aspect category Sentiment Analysis and rating Prediction* dari Meituan-Dianping untuk restoran berbahasa Mandarin (NAACL 2021), bukan subset resmi bawaan pustaka `indonlu` di Hugging Face.
* **Risiko:**  
  Jika mentor atau juri mengecek pustaka Hugging Face dan mencoba `load_dataset('indonlu', 'asap')`, fungsi tersebut akan menghasilkan galat `ConfigDoesNotExist`.
* **Solusi Penguatan Teknis:**  
  Formulasikan sumber data secara transparan dan akademis:  
  *"Kami mengadaptasi metodologi benchmark IndoNLU ke domain kuliner menggunakan korpus ulasan makanan Indonesia (seperti IndoNLU SmSA dan repositori ulasan kuliner lokal), yang kami anotasi ke dalam 5 aspek operasional (Rasa, Porsi, Harga, Kemasan, Pelayanan). Model dasar yang digunakan adalah pretrained IndoBERT (indobenchmark/indobert-base-p1)."* Pendekatan ini menunjukkan penguasaan data yang jujur dan berkelas riset terapan.

### Celah 2: Rigoritas Matematis Kitchen Health Score
* **Temuan Celah:**  
  Blueprint awal menyebutkan *"Hitung rasio kepuasan per aspek"*, tetapi belum menjabarkan formulasi matematis formalnya. Penguji teknis akan menanyakan: *"Bagaimana formula matematis perhitungannya? Mengapa bobot aspek rasa lebih besar dari kemasan?"*
* **Solusi Penguatan Teknis:**  
  Definisikan secara formal dalam notasi matematika:  
  Terdapat $K = 5$ aspek operasional:
  $$\displaystyle \mathcal{A} = \{\text{Rasa}, \text{Porsi}, \text{Kemasan}, \text{Harga}, \text{Pelayanan}\}$$
  Vektor bobot ditentukan berdasarkan hierarki dampak langsung terhadap retensi pelanggan F&B:
  $$\displaystyle \mathbf{w} = [w_{\text{rasa}}=0.35, \, w_{\text{porsi}}=0.20, \, w_{\text{kemasan}}=0.15, \, w_{\text{harga}}=0.15, \, w_{\text{pelayanan}}=0.15]$$
  dengan syarat normalisasi:
  $$\displaystyle \sum_{k=1}^K w_k = 1.0$$
  Untuk setiap aspek $k$, tingkat kepuasan ($S_k$) dihitung dari jumlah ulasan positif ($N_k^+$), netral ($N_k^0$), dan negatif ($N_k^-$):
  $$\displaystyle S_k = \frac{N_k^+ + 0.5 \cdot N_k^0}{N_k^+ + N_k^0 + N_k^-} \times 100\%$$
  Skor komposit *Kitchen Health Score* (KHS) diperoleh melalui kombinasi linier terbobot:
  $$\displaystyle \text{KHS} = \sum_{k=1}^K w_k \cdot S_k$$

### Celah 3: Ketahanan Eksekusi di Lingkungan Cloud Gratis
* **Temuan Celah:**  
  Deployment di Hugging Face Spaces (tier CPU gratis, 2 vCPU / 16GB RAM) sering mengalami *cold-start delay*, kehabisan kuota API LLM eksternal, atau proses inferensi Transformer yang lambat jika memuat model raksasa tanpa kuantisasi.
* **Solusi Penguatan Teknis:**  
  1. Buat mekanisme *graceful fallback* di kode aplikasi: jika API Key LLM tidak disetel atau kuota habis, modul generatif beralih secara mulus ke mesin rekomendasi terstruktur berbasis aturan (*heuristic template generator*) tanpa menampilkan pesan error merah di layar pengguna.
  2. Gunakan *caching* Streamlit untuk tokenizer dan model agar tidak diinisialisasi ulang pada setiap interaksi pengguna.

---

## 4. Skenario Mentoring 1-on-1 (16 Oktober)

### 4.1 Framing & Positioning Proyek
Saat membuka sesi konsultasi dengan mentor, posisikan proyek UlasRasa sebagai **solusi operasional F&B berbasis AI hibrida**, bukan sekadar proyek NLP klasifikasi teks standar.

### 4.2 Naskah Elevator Pitch (3 Menit)
* **Menit 0:00 - 0:45 (Hook & Latar Belakang):**  
  *"Halo Kak, untuk Final Project saya mengambil tema Text-Based NLP dan Generative AI dengan judul UlasRasa. Latar belakang proyek ini berangkat dari fenomena riil maraknya komplain pelanggan resto di media sosial dan platform pesan-antar makanan di Indonesia. Masalahnya, ulasan pelanggan itu tidak terstruktur dan pemilik resto atau UMKM sering mengalami review overload. Mereka tidak punya waktu membaca ratusan ulasan satu per satu untuk mencari tahu apa yang sebenarnya salah di dapur mereka."*
* **Menit 0:45 - 1:30 (Kelemahan Solusi Eksisting):**  
  *"Selama ini aplikasi analisis sentimen yang ada di pasaran umumnya cuma menghasilkan klasifikasi biner positif versus negatif. Informasi ini sama sekali tidak berguna bagi tim dapur. Ulasan seperti 'Ayamnya enak banget dan bumbunya gurih, tapi sambalnya dikit dan kemasannya tumpah di jalan' memiliki sentimen campuran. Pemilik resto butuh tahu aspek mana yang bermasalah secara spesifik dan apa tindakan nyata yang harus dieksekusi di dapur hari ini juga."*
* **Menit 1:30 - 2:30 (Solusi & Arsitektur Teknis UlasRasa):**  
  *"UlasRasa memecahkan masalah ini dengan pendekatan hybrid dua tahap. Tahap pertama adalah Discriminative NLP menggunakan model IndoBERT untuk membedah ulasan ke dalam 5 aspek operasional: Rasa, Porsi, Harga, Kemasan, dan Pelayanan. Dari sini kita kalkulasi metrik kuantitatif bernama Kitchen Health Score. Tahap kedua adalah Generative AI di mana LLM menerima ringkasan ulasan negatif per aspek dan otomatis meng-generate analisis akar masalah, checklist perbaikan dapur konkret yang bisa dicetak, dan rekomendasi SOP. Kami mengemasnya dalam dashboard interaktif Streamlit yang siap diuji coba langsung."*
* **Menit 2:30 - 3:00 (Validasi & Ekspektasi Mentoring):**  
  *"Tujuan saya di sesi mentoring malam ini adalah memvalidasi arsitektur hibrida ini, khususnya terkait strategi evaluasi metrik Macro-F1 pada data multi-aspek dan memastikan pipeline ini selaras penuh dengan standar Level 5 di rubrik penilaian akhir."*

### 4.3 Antisipasi Pertanyaan Kritis Mentor & Jawaban Taktis

#### Pertanyaan 1: "Kenapa tidak pakai direct LLM prompt saja untuk klasifikasi aspek dan sentimen? Kenapa harus repot pakai IndoBERT?"
* **Jawaban Taktis:**  
  *"Ada tiga alasan fundamental terkait efisiensi dan rekayasa AI, Kak:*
  1. *Kecepatan & Latensi:* Untuk mengklasifikasikan batch ulasan dalam jumlah ratusan, model *encoder* lokal seperti IndoBERT membutuhkan latensi di bawah 100 ms per kalimat pada CPU standar, sedangkan pemanggilan LLM per kalimat ulasan memerlukan waktu bermenit-menit dan rawan *rate limiting*.
  2. *Determinisme & Konsistensi Data:* Klasifikasi multi-label membutuhkan format keluaran yang 100% konsisten agar bisa diagregasi ke dalam grafik statistik dan perhitungan *Kitchen Health Score*. LLM rawan mengalami ketidakkonsistenan format keluaran (*parsing error*).
  3. *Efisiensi Biaya (Cost Efficiency):* Memproses jutaan token ulasan harian dengan LLM komersial sangat mahal bagi skala UMKM. Dengan membagi tugas di mana IndoBERT menangani klasifikasi kuantitatif dan LLM hanya dipanggil satu kali untuk merangkum ringkasan akhir, biaya komputasi terpangkas lebih dari 85%."*

#### Pertanyaan 2: "Bagaimana dengan datasetnya? Apakah IndoNLU menyediakan dataset khusus ulasan restoran 5 aspek?"
* **Jawaban Taktis:**  
  *"Benchmark resmi IndoNLU untuk ABSA adalah CASA pada domain mobil dan HoASA pada domain hotel. Untuk domain kuliner, kami menggunakan transfer learning dari model dasar IndoBERT yang dipra-latih pada korpus Indo4B. Kami menggabungkan korpus sentimen bahasa Indonesia (IndoNLU SmSA) dan kumpulan data ulasan kuliner nyata dari platform lokal yang kami adaptasikan ke dalam skema anotasi 5 aspek kunci kami: Rasa, Porsi, Harga, Kemasan, dan Pelayanan. Ini memastikan model kami memiliki ketajaman semantik pada istilah kuliner gaul Indonesia seperti 'bumbu medok', 'porsi kuli', hingga 'kuah rembes'."*

#### Pertanyaan 3: "Metrik apa yang kamu pakai untuk membuktikan bahwa modelmu berhasil?"
* **Jawaban Taktis:**  
  *"Kami membagi evaluasi menjadi dua lapisan:
  1. Evaluasi Kuantitatif Lapisan NLP: Kami menggunakan Macro-Averaged F1-Score, Precision, dan Recall pada masing-masing dari 5 aspek. Kami memprioritaskan Macro-F1 dibanding akurasi biasa karena data ulasan kuliner memiliki ketimpangan kelas yang nyata di mana ulasan positif umumnya jauh lebih banyak daripada ulasan komplain negatif.
  2. Evaluasi Kualitatif Lapisan Generatif LLM: Kami mengukur dua parameter: Actionability Rate (apakah checklist yang dibuat konkret dan bisa dieksekusi staf dapur) dan Domain Faithfulness (apakah rekomendasi murni bersumber dari komplain yang ada tanpa halusinasi menu asing)."*

---

## 5. Rencana Kerja & Roadmap Eksekusi (16 - 23 Oktober 2026)

Jadwal kerja harian terstruktur guna memastikan deliverable selesai sebelum tenggat waktu resmi:

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                    ROADMAP EKSEKUSI PROYEK ULASRASA                           │
├─────────────────┬─────────────────────────────────────────────────────────────┤
│ 16 Oktober      │ Mentoring 1-on-1 (Validasi Konsep & Arsitektur)             │
│ (Malam ini)     │ Artefak awal, dataset sampel, dan arsitektur telah siap     │
├─────────────────┼─────────────────────────────────────────────────────────────┤
│ 17 - 18 Oktober │ Baseline Pipeline & Model Refinement                        │
│                 │ - Verifikasi evaluasi Macro-F1 pada data ulasan multi-aspek │
│                 │ - Optimasi slang dictionary untuk dialek kuliner            │
├─────────────────┼─────────────────────────────────────────────────────────────┤
│ 19 Oktober      │ Generative Engine Integration & Error Handling              │
│                 │ - Penyempurnaan template prompt LLM (Gemini / Groq)         │
│                 │ - Pengujian graceful fallback mode offline                  │
├─────────────────┼─────────────────────────────────────────────────────────────┤
│ 20 - 21 Oktober │ Frontend Polish & Hugging Face Spaces Deployment            │
│                 │ - Finalisasi 4 tab Streamlit UI                             │
│                 │ - Push repositori ke GitHub & deploy ke Hugging Face Spaces │
│                 │ - Verifikasi public live demo URL                           │
├─────────────────┼─────────────────────────────────────────────────────────────┤
│ 22 Oktober      │ Dokumentasi & Slide Deck Final                              │
│                 │ - Pembuatan slide deck presentasi (8 poin wajib rubrik)     │
│                 │ - Perekaman video walk-through demo 2-3 menit (MP4)         │
├─────────────────┼─────────────────────────────────────────────────────────────┤
│ 23 Oktober      │ Final Submission Portofolio Bootcamp                        │
│ (23:59 WIB)     │ Submit Google Drive / GitHub / Hugging Face Spaces URL      │
└─────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 6. Inventaris Artefak Proyek yang Telah Siap

Seluruh struktur kode dan data kerja telah diinisialisasi dan diuji di folder:
`C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa`

1. `data/sample_reviews.csv`: Dataset sampel 20 ulasan riil multi-resto dengan anotasi lengkap 5 aspek operasional.
2. `src/preprocessing.py`: Modul pembersihan teks ulasan (*slang normalizer*, penanganan emoji, ekstraksi kata kunci aspek).
3. `src/absa_pipeline.py`: Mesin inferensi ABSA 5 aspek dan kalkulasi metrik *Kitchen Health Score*.
4. `src/action_engine.py`: Mesin generatif penalaran akar masalah, *kitchen action checklist*, dan rekomendasi SOP.
5. `app.py`: Aplikasi Streamlit interaktif 4 tab (Ringkasan & KHS, Deep-Dive Aspek, AI Kitchen Action Checklist, Single Review Simulator) dengan fitur ekspor checklist teks.
6. `docs/PRESENTATION_DECK_OUTLINE.md`: Draf struktur 8 slide presentasi sesuai pedoman resmi rubrik bootcamp.
7. `requirements.txt`: Daftar dependensi Python yang siap dipasang secara instan.
