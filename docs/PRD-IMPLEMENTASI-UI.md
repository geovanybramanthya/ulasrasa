# PRD Implementasi - Perombakan Total UI UlasRasa

Dokumen rencana eksekusi yang mengikat Executor. Acuan desain satu-satunya: `DESIGN.md` di *branch* `ui-overhaul` (commit `0dc97b8`). Ditulis oleh Planner berdasarkan inventarisasi kode terverifikasi pada 2026-10-23.

Prinsip yang tidak bisa ditawar:

1. Desain aplikasi sebelumnya dianggap tidak ada. Tidak ada warna, *class* CSS, atau komposisi lama yang dijadikan acuan. Yang dipertahankan hanya **fungsi dan data**.
2. Logika arsitektur (ABSA, KHS, LLM, ekspor) sudah teraudit semalam dan **tidak boleh berubah perilaku**. File di luar wilayah UI tidak disentuh.
3. Setiap tahap berhenti di gerbangnya. Tidak ada tahap yang lanjut sebelum gerbang tahap sebelumnya lulus bukti.

## 1. Fakta Kode Saat Ini (Basis Terverifikasi)

- `app.py`: 1.766 baris, 69.340 byte, SHA256 `8c8d4f24adaa634a127d156bd286db9e73a23c599a6f22d3d8032287dc8a9f49`. Hanya punya **2 fungsi *top-level***; seluruh UI adalah kode skrip sekuensial di level modul.
- `app.py` identik *byte-per-byte* dengan string `APP_CODE` di `scripts/build_clean_app.py` (terverifikasi via AST + hash). File itu adalah artefak *generate*.
- Peta blok `app.py`:

| Blok | Baris | Isi |
| :--- | :--- | :--- |
| Konfigurasi | 1-41 | Docstring, impor, `st.set_page_config` (judul "UlasRasa - Kitchen Intelligence Dashboard", `layout="wide"`, favicon `assets/favicon.png`) |
| CSS lama | 46-676 | Konstanta `CUSTOM_CSS` (±630 baris, ±45 *class*) + injeksi di 676 |
| Engine | 682-707 | `load_ai_engines()` (`@st.cache_resource`) + `load_default_dataset()` (`@st.cache_data`) |
| *Session state* | 710-723 | 4 kunci: `custom_reviews_df`, `custom_checklist_items`, `active_module_name`, `simulator_text` |
| *Sidebar* | 728-982 | Brand, navigasi radio, sumber data + unggah, kartu outlet, panduan, form tambah ulasan, kartu bobot. **Di blok ini juga dihitung satu kali per *run*:** `eval_results`, `khs`, `breakdown`, status, aspek terlemah (baris 804-875) |
| *Header* lama | 987-1076 | Header utama, indikator 5 langkah, 4 tombol navigasi atas |
| Modul 1 | 1081-1264 | Ringkasan Eksekutif & Health Score |
| Modul 2 | 1269-1428 | Deep-Dive Aspek & Sentimen |
| Modul 3 | 1433-1605 | AI Kitchen Action Checklist & SOP |
| Modul 4 | 1610-1752 | Single Review Simulator |
| *Footer* | 1757-1766 | Footer |

- Identitas modul kanonis (nilai `active_module_name`, `MODULE_CHOICES` baris 771-776): `Ringkasan Eksekutif & Health Score`, judul penuh Modul 2-4 sesuai konstanta itu. **Nilai-nilai ini adalah ID internal dan TIDAK diubah**; nama tampilan pendek dari DESIGN.md dipetakan lewat tabel label (Bagian 4).
- Kunci *widget* yang hidup: `sidebar_module_radio`, `top_btn_0`..`top_btn_3`, `action_chk_<nama_resto>_<idx>`, `sim_preset_1`..`sim_preset_4`, `sim_analyze_btn`.
- Impor `src/` oleh `app.py`: `src.absa_pipeline.ABSAPipeline`, `src.models.transformer_engine.TransformerABSAPipeline` (impor malas di dalam `load_ai_engines`), `src.action_engine.ActionPlanEngine`, `src.preprocessing.clean_text`, `src.config` (`ASPECT_WEIGHTS` + `HEALTH_THRESHOLDS` yang benar-benar dipakai), `src.utils.exporter` (`export_action_plan_text`, `export_action_plan_pdf`).
- File `src/components/*`, `src/analytics/*`, `src/utils/sample_data.py` **tidak** diimpor `app.py` - di luar wilayah perombakan, jangan disentuh.

## 2. Keputusan Strategi File: Pensiunkan Build Script, Pecah ke `src/ui/`

**Keputusan (mengikat):** `scripts/build_clean_app.py` dipensiunkan. `app.py` menjadi *entry point* ramping; seluruh tampilan pindah ke modul-modul di `src/ui/`.

Alasan:

1. **Risiko edit.** Pola lama mengharuskan setiap perubahan UI ditulis dua kali di dalam satu string Python raksasa di file lain. Perombakan ini menulis ulang ±630 baris CSS dan hampir semua blok HTML - di dalam string, risiko *escaping* dan ketidakcocokan kutip nyata, dan *diff*-nya tidak bisa ditinjau manusia.
2. **Auditabilitas per modul.** Gerbang desain kita per modul (Ringkasan dulu, dinilai, baru lanjut). Itu hanya bisa diaudit bila kode satu modul = satu file yang bisa dibaca dan diubah tanpa menyentuh modul lain.
3. **Nilai build script sudah habis.** Satu-satunya fungsinya menulis ulang `app.py` dari string. Tidak ada konsumen lain. Riwayat git menyimpannya sebagai arsip; menghapusnya sekarang tidak menghilangkan apa pun.
4. **Konsistensi ke depan.** Struktur `src/ui/` sejajar dengan `src/` yang sudah modular (pipeline, engine, exporter). Spaces tetap menjalankan `app.py` di root repo - nama dan posisi *entry point* tidak berubah.

Struktur target:

```
app.py                        # entry ramping: page config, bootstrap, shell, dispatch modul
src/ui/__init__.py
src/ui/labels.py              # peta ID modul -> nama tampilan + string UI semi-formal
src/ui/theme.py               # token warna/font/spasi (dari DESIGN.md Bag. 4-6) + pembangun CSS + muat font + sembunyikan chrome
src/ui/core.py                # load_ai_engines + load_default_dataset (pindah verbatim) + inisialisasi sesi + pembangun konteks data
src/ui/components.py          # top bar, header sapaan, kartu KPI, dropzone, panel data, pill/badge, kartu ulasan, loading bermerek
src/ui/charts.py              # pembangun figur Plotly: donat hero, batang aspek, donat distribusi, komposisi, kata kunci
src/ui/module_ringkasan.py    # render(ctx)
src/ui/module_rincian.py      # render(ctx)
src/ui/module_rencana.py      # render(ctx)
src/ui/module_coba.py         # render(ctx)
```

Aturan pemindahan:

- `load_ai_engines()` dan `load_default_dataset()` dipindah ke `src/ui/core.py` **verbatim** (termasuk dekorator *cache* dan urutan *fallback* senyap). Tidak ada satu baris logika pun yang ditulis ulang.
- Blok perhitungan bersama (lama: baris 804-875 di *sidebar*) dipindah menjadi pembangun **konteks data** di `core.py` yang menghasilkan satu objek konteks berisi: `active_df`, `filtered_df`, `selected_resto`, `eval_results`, `khs`, `breakdown`, `status_label`, `weakest_aspect`, `weakest_score`. Urutan dan rumus pemanggilannya persis seperti sekarang - `evaluate_dataframe` tetap dipanggil **satu kali per *run***.
- Setiap modul menerima konteks itu sebagai argumen `render(ctx, pipeline, action_engine)` - tidak ada modul yang menghitung ulang KHS atau membaca file sendiri.
- `scripts/build_clean_app.py` dihapus pada commit Tahap 0, setelah hash `app.py` lama tercatat di bukti baseline. Penghapusan dicatat di pesan commit.

## 3. Checklist Paritas Fungsi (44 Butir - Semua Wajib Lulus)

Paritas dibuktikan per butir di gerbang akhir (Bagian 7). "Identik" berarti perilaku dan angka yang teramati pengguna sama dengan versi sebelum perombakan.

### 3.1 Data dan Sesi (9)

| ID | Butir |
| :--- | :--- |
| P-D1 | Dataset bawaan `data/sample_reviews.csv` (100 baris, 4 resto) termuat otomatis saat mulai lewat jalur yang sama (`load_default_dataset`) |
| P-D2 | Mode preset: pemilih resto berisi "Semua Outlet (Benchmark Industri)" + daftar resto terurut; pilihan awal = resto pertama alfabetis (*index* 1) |
| P-D3 | Mode unggah: file CSV terbaca dan menjadi data aktif pada *run* itu |
| P-D4 | Guard unggah: file > 200 baris ditolak dengan pesan galat yang menyebut jumlah baris dan batas 200, data aktif tidak berubah |
| P-D5 | CSV tanpa kolom `review_text` ditolak dengan pesan galat |
| P-D6 | Unggah sukses menampilkan pesan berhasil berisi jumlah baris |
| P-D7 | Form tambah ulasan: menganalisis teks dengan *pipeline* aktif, menambah baris ke dataset sesi, memuat ulang tampilan |
| P-D8 | Hasil unggah tidak persisten antar-*run* (perilaku sama seperti sekarang; jangan "diperbaiki") |
| P-D9 | Empat kunci `session_state` inti tetap sama namanya dan maknanya; pola kunci *checkbox* `action_chk_<resto>_<idx>` dan kunci preset simulator tetap sama |

### 3.2 Engine (5)

| ID | Butir |
| :--- | :--- |
| P-E1 | Urutan muat engine identik: lexicon dibuat dulu, transformer dicoba, kegagalan tertangkap senyap tanpa pesan error ke pengguna |
| P-E2 | Caption engine tetap tampil dengan teks persis `Engine ABSA: <label>` (label dari `engine_name` engine aktif; lokasinya pindah ke *top bar* sesuai DESIGN.md) |
| P-E3 | Caption mode rekomendasi di modul Rencana Aksi tetap dibaca dari `plan["generation_mode"]`/`plan["llm_provider"]` dengan teks persis `Mode rekomendasi: LLM (<provider>)` atau `Mode rekomendasi: Template (offline)` |
| P-E4 | `ActionPlanEngine` diinstansiasi satu kali bersama engine ABSA (jalur `load_ai_engines`) |
| P-E5 | Tidak ada perubahan apa pun pada `src/absa_pipeline.py`, `src/models/transformer_engine.py`, `src/action_engine.py`, `src/config.py`, `src/preprocessing.py`, `src/utils/exporter.py` (dibuktikan dengan `git diff` kosong untuk file-file itu di gerbang akhir) |

### 3.3 Angka (5)

| ID | Butir |
| :--- | :--- |
| P-N1 | Rumus KHS dan bobot aspek tidak berubah karena memang tidak disentuh: $S_k = \frac{N_k^+ + 0{,}5 \cdot N_k^0}{N_k^+ + N_k^0 + N_k^-} \times 100\%$, $\text{KHS} = \sum_k w_k S_k$, bobot Rasa 0,35 / Porsi 0,20 / Kemasan 0,15 / Harga 0,15 / Pelayanan 0,15 |
| P-N2 | Nilai KHS + skor kepuasan per aspek untuk 4 resto sampel dan mode benchmark **sama persis** (2 desimal) dengan baseline yang direkam di Tahap 0 |
| P-N3 | Ambang status tetap: >= 80 PRIMA, >= 65 WASPADA, di bawahnya KRITIS; **teks label status tidak diubah di tempat mana pun** karena teks yang sama mengalir ke isi ekspor TXT/PDF |
| P-N4 | Format tampil KHS tetap `{khs:.1f}%` (di kartu KPI dan hero) |
| P-N5 | Aspek terlemah tetap = aspek dengan `satisfaction_score` minimum; peringatan aspek terlemah (ambang < 75, menampilkan *negative rate*) tetap muncul, berpindah tempat ke area hero Ringkasan |

### 3.4 Modul (16)

| ID | Butir |
| :--- | :--- |
| P-M1 | Ringkasan menampilkan 4 nilai inti yang sama datanya: KHS, label status, aspek paling kritis + skornya, total ulasan terfilter |
| P-M2 | Grafik skor aspek Ringkasan memakai data `satisfaction_score` yang sama per aspek (jenis grafik berubah radar -> batang horizontal sesuai DESIGN.md; ini perubahan desain yang disengaja oleh PRD, datanya paritas) |
| P-M3 | Rincian: 4 angka hitung aspek terpilih (disebut, positif, netral, negatif) identik dari `breakdown` |
| P-M4 | Rincian: grafik komposisi sentimen bertumpuk 5 aspek memakai hitungan `breakdown` yang sama |
| P-M5 | Rincian: grafik 6 kata keluhan teratas aspek terpilih dihitung dengan cara yang sama (`clean_text` + `Counter` atas ulasan berlabel negatif pada aspek itu, *stopword* yang sama) |
| P-M6 | Rincian: penjelajah ulasan mempertahankan filter polaritas (pilihan awal "Hanya Negatif (Komplain)") dan filter menu, dan menampilkan seluruh ulasan lolos filter beserta menu, ID, label sentimen per aspek, teks, dan outlet |
| P-M7 | Rencana Aksi: `sample_complaints` tetap maks 3 teks negatif per aspek, dibangun dari data terfilter |
| P-M8 | Rencana Aksi: seluruh butir `root_cause_analysis` tampil bernomor, tidak ada yang terpotong |
| P-M9 | Rencana Aksi: seluruh butir `kitchen_action_checklist` tampil sebagai *checkbox* + butir kustom sesi; hitungan progres `completed/total` identik |
| P-M10 | Rencana Aksi: tambah tindakan kustom tetap berfungsi dan masuk daftar + ekspor |
| P-M11 | Rencana Aksi: seluruh butir `sop_recommendations` tampil |
| P-M12 | Coba Ulasan: 4 teks preset simulator **persis sama** dengan teks `p1`-`p4` saat ini |
| P-M13 | Coba Ulasan: analisis memakai `pipeline.analyze_single_review` dari engine aktif yang sama |
| P-M14 | Coba Ulasan: teks asli dan teks hasil normalisasi (`cleaned_text`) tetap ditampilkan |
| P-M15 | Coba Ulasan: untuk tiap aspek tampil status disebut/tidak + sentimen + *confidence* dalam persen, dari dict hasil yang sama |
| P-M16 | Coba Ulasan: kartu tindak lanjut kondisional tetap ada - daftar aspek negatif bila ada aspek disebut yang negatif, status optimal bila tidak ada |

### 3.5 Ekspor (4)

| ID | Butir |
| :--- | :--- |
| P-X1 | Unduh TXT: isi dan pola nama file `checklist_dapur_<resto>.txt` identik (fungsi exporter yang sama, argumen yang sama, termasuk 2 RCA pertama sebagai *critical alerts* dan status centang) |
| P-X2 | Unduh PDF: berkas PDF ter-generate ReportLab dengan isi setara dan nama file sama; kegagalan tetap hanya berupa *caption* pemberitahuan |
| P-X3 | Unduh CSV daftar aksi tetap tersedia (penampilan boleh menjadi tombol *ghost* kecil; keberadaan dan isinya paritas) |
| P-X4 | Status centang *checkbox* saat unduh tercermin di isi ekspor, sama seperti sekarang |

### 3.6 Global (5)

| ID | Butir |
| :--- | :--- |
| P-G1 | Judul tab browser menjadi "UlasRasa - Kesehatan Dapur dari Ulasan" (ketentuan DESIGN.md Bag. 3; ini satu-satunya perubahan judul yang disengaja), favicon tetap `assets/favicon.png`, `layout="wide"` tetap |
| P-G2 | Seluruh teks data (nama resto, nama menu, isi ulasan, label) tampil apa adanya dari data - tidak ada penyuntingan konten data |
| P-G3 | `py -m pytest tests/ -q` lulus penuh (13 tes) di setiap gerbang |
| P-G4 | Streamlit AppTest atas `app.py` berjalan dengan 0 *exception* di setiap gerbang |
| P-G5 | Tidak ada file di luar wilayah berikut yang berubah: `app.py`, `src/ui/**` (baru), penghapusan `scripts/build_clean_app.py`, dan dokumen/bukti di `docs/` |

**Catatan quirk terdokumentasi (bukan untuk diperbaiki diam-diam):** pada mode unggah tanpa file, kode lama menyetel `selected_resto` ke string `"Semua Outlet (Benchmark)"` (tanpa kata "Industri") yang tidak cocok dengan string filter. Executor mempertahankan perilaku teramati saat ini; bila quirk ini menghalangi pembangunan panel data, laporkan ke Planner lewat orkestrator - jangan mengubah logika tanpa keputusan tercatat.

## 4. Inventaris Komponen (dari DESIGN.md Bag. 4-9)

Token disingkat: warna/font merujuk tabel DESIGN.md Bag. 4-5 persis (Latar `#F6F7F9`, Kartu `#FFFFFF`, Tinta `#14231B`, Redup `#64756B`, Hijau `#22C55E`, Hijau Pekat `#15803D`, Tint Hijau `#E8F9F0`; aspek: Rasa `#E8833A`/`#FFE8D6`, Porsi `#0284C7`/`#E0F2FE`, Harga `#D97706`/`#FEF3C7`, Kemasan `#7C3AED`/`#EDE9FE`, Pelayanan `#0D9488`/`#CCFBF1`; radius kartu 20 px, tombol 12 px, *padding* 20-24 px, bayangan `0 8px 24px rgba(20,40,30,0.06)`; font: Jakarta 700/800 judul, Inter 400/500/600 isi, JetBrains Mono 600 angka).

### 4.1 Global

| Komponen | Sumber data | Catatan bangun |
| :--- | :--- | :--- |
| TopBar | Logo SVG statis; navigasi <- `active_module_name`; cip engine <- `ACTIVE_ABSA_ENGINE_LABEL` | Lengket (*sticky*). Navigasi memakai `st.pills` dengan label tampilan dari `labels.py`; nilai yang ditulis ke sesi tetap ID kanonis lama. Cip engine teks persis P-E2 |
| HeaderSapaan | `selected_resto`; kalimat status <- `status_label` + `weakest_aspect` | Jakarta 800. Sapaan "Halo, [nama resto]" + 1 kalimat status faktual |
| PemilihResto | Daftar resto <- `active_df` (aturan P-D2) | *Selectbox* bergaya *pill* di kanan header |
| TombolGantiData | Mengalihkan panel data (keadaan sesi lokal UI) | Membuka PanelData di modul Ringkasan |
| PanelData | Mode sumber data; unggah; form tambah ulasan | Isi = seluruh fungsi blok *sidebar* lama 4.3 + 4.6, berpindah tempat tanpa berubah perilaku (P-D2 s.d. P-D8) |
| DropzoneCSV | `st.file_uploader` | Kartu garis putus-putus di Ringkasan (di dalam PanelData); guard P-D4/P-D5 dirender di sini |
| LoadingBermerek | Tampil sebelum `load_ai_engines()` selesai | Pola `st.empty()`: kartu bermerek + teks penjelas, digantikan konten setelah engine siap. Hanya tampil pada *run* pertama per sesi server (karena *cache*) - itu wajar dan dicatat di bukti |
| FooterRingkas | Statis | Satu baris redup; tanpa klaim baru |

### 4.2 Ringkasan (penentu *tone*)

| Komponen | Sumber data | Catatan bangun |
| :--- | :--- | :--- |
| KartuKPI x4 | (1) `khs`; (2) `len(filtered_df)`; (3) persen ulasan negatif; (4) `weakest_aspect` + `weakest_score` | Pastel per makna, ikon SVG garis tipis di cip tint, angka JetBrains Mono. *Microcopy* faktual saja. Definisi butir (3) yang mengikat: proporsi baris `filtered_df` yang memiliki **minimal satu aspek berlabel `negative`** di antara 5 kolom aspek, x 100, satu desimal; *microcopy* "dari <N> ulasan" |
| HeroKHS | Donat <- `khs`; status <- `status_label`; cip prioritas <- `weakest_aspect`; CTA -> modul Rencana Aksi | Satu-satunya kartu bergradasi hijau (bersama CTA). Angka tengah donat JetBrains Mono format P-N4. CTA menulis ID kanonis Modul 3 ke `active_module_name` lalu `st.rerun()` |
| GrafikBatangAspek | `breakdown[k].satisfaction_score` untuk 5 aspek | Batang horizontal, warna per aspek, garis putus-putus di 70 berlabel "Batas kritis" (DESIGN.md). Figur dibangun di `charts.py`; data figur wajib sama dengan `breakdown` |
| RelKeluhan | Baris `filtered_df` dengan minimal satu aspek `negative`, urut `review_id` menurun, maks 5 | Teks terpotong ±140 karakter, cip aspek negatifnya, *pill* sentimen. Klik kartu: set sesi `rincian_aspect` = aspek negatif pertama baris itu + pindah ke modul Rincian (kunci sesi baru khusus UI ini diizinkan) |
| KartuRincianAspekMini | `breakdown` per aspek: skor, bobot `ASPECT_WEIGHTS`, hitungan disebut/positif/netral/negatif | Penerus 5 kartu rincian lama (P-M1); boleh diringkas menjadi baris di bawah grafik utama bila kepadatan menuntut - data tidak boleh hilang |

### 4.3 Rincian Aspek

| Komponen | Sumber data | Catatan bangun |
| :--- | :--- | :--- |
| PillPemilihAspek | Sesi `rincian_aspect` (baru; nilai awal "Rasa") | Menggantikan *selectbox* lama; aspek terpilih menggerakkan semua komponen di bawahnya (paritas data P-M3 s.d. P-M6) |
| AngkaHitungAspek | `breakdown[aspek]`: total_mentioned, positive, neutral, negative | 4 angka, gaya kartu mini |
| DonatDistribusi | Hitungan positif/netral/negatif aspek terpilih | Warna sentimen: positif hijau brand, netral amber netral, negatif merah token DESIGN.md |
| KolomContohUlasan | `filtered_df` difilter label aspek = positive / negative | Dua kolom contoh (positif vs negatif), teks apa adanya (P-G2) |
| GrafikKomposisi | `breakdown` 5 aspek | Batang bertumpuk (penerus `px.bar` lama, P-M4), warna sentimen sama seperti donat |
| GrafikKataKeluhan | `clean_text` + `Counter`, top 6 | Cara hitung persis P-M5; batang horizontal warna aspek terpilih |
| TabelSemuaUlasan | `filtered_df` + filter polaritas + filter menu (+ aspek dari PillPemilihAspek) | Penerus Review Explorer (P-M6): baris berisi teks terpotong rapi, menu, outlet, dan 5 *pill* sentimen mini per aspek. Pilihan awal filter polaritas tetap "Hanya Negatif (Komplain)" |

### 4.4 Rencana Aksi

| Komponen | Sumber data | Catatan bangun |
| :--- | :--- | :--- |
| KartuAkarMasalah | `plan["root_cause_analysis"]` (bernomor) + cip mode <- `plan["generation_mode"]`/`plan["llm_provider"]` | Teks caption mode persis P-E3. Rencana dibangun dari `sample_complaints` aturan P-M7 |
| ProgressAksi | Jumlah tercentang / total dari kunci `action_chk_*` + item kustom | *Progress bar* hijau di puncak modul; teks `<selesai>/<total> aksi selesai` |
| GrupDaftarAksi | `plan["kitchen_action_checklist"]` + `custom_checklist_items` | Kartu per kelompok sumber: "Daftar Aksi Dapur" (dari rencana) dan "Tindakan Kustom" (dari sesi). **Jangan mengarang pemetaan aspek per butir** - keluaran LLM tidak membawa label aspek. Kunci *checkbox* mempertahankan pola + indeks global lama demi paritas keadaan sesi (P-D9) |
| FormTambahAksi | Menulis `custom_checklist_items` | Penerus *expander* lama (P-M10) |
| KartuSOP | `plan["sop_recommendations"]` | Daftar bernomor/berpoin dalam kartu |
| PusatUnduh | `export_action_plan_text` / `export_action_plan_pdf` / CSV dari daftar aksi | Hierarki DESIGN.md: PDF tombol hijau solid (utama), TXT *ghost* (sekunder), CSV *ghost* kecil (P-X3). Argumen pemanggilan exporter persis seperti sekarang (P-X1/P-X2) |

### 4.5 Coba Ulasan

| Komponen | Sumber data | Catatan bangun |
| :--- | :--- | :--- |
| KartuInput | `simulator_text`; 4 preset `p1`-`p4` (P-M12) | Area teks besar + tombol "Analisis" hijau solid (kunci `sim_analyze_btn` dipertahankan) |
| KartuHasil | Dict `analyze_single_review` (P-M13) | Baris penuh per aspek yang disebut: cip ikon aspek, nama aspek, *pill* sentimen, *bar confidence* (persen dari `confidence`). Aspek tidak disebut diringkas satu baris redup "Tidak disebut: ..." (DESIGN.md) |
| KotakTeksBersih | `original_text` vs `cleaned_text` | Dipertahankan sebagai dua kotak kecil di bawah hasil (P-M14) |
| KartuTindakLanjut | Aspek negatif dari hasil | Kondisional persis P-M16 |
| EmptyState | Sebelum analisis pertama | Teks ramah semi-formal, tanpa klaim palsu |

## 5. Rencana Bukti Visual (Metode Terverifikasi)

**Metode utama: Playwright (Python proyek) dengan Chromium bawaannya.** Terverifikasi di PC pada 2026-10-23: `playwright` terpasang; `chromium.launch()` berhasil (Chromium 151.0.7922.34); `chromium.launch(channel='msedge')` juga berhasil (Edge 155.0.4283.62). Cadangan silang: `msedge.exe` ada di `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` untuk `--headless=new --screenshot --virtual-time-budget` bila Playwright bermasalah.

Prosedur baku per tangkapan:

1. Jalankan server terpisah dari repo: `py -m streamlit run app.py --server.headless true --server.port 8510` (proses *detached* via WMI seperti pola semalam; jangan dari sesi SSH yang akan ditutup).
2. Skrip `docs/ui-evidence/capture.py` (ditulis Executor di Tahap 0, dipakai semua tahap): buka halaman, `wait_for_load_state("networkidle")`, tunggu penanda render modul aktif (teks judul modul), jeda stabil 2.000 ms (muat model pertama bisa ±18 detik - penanda ditunggu dengan *timeout* 60 detik), lalu tangkap.
3. Dua *viewport* wajib: **1440x900** (*deviceScaleFactor* 1) dan **390x844** (emulasi sentuh). Untuk modul panjang, ambil versi *viewport* dan *full page*.
4. Interaksi lewat Playwright untuk status non-awal: klik *pill* navigasi, klik preset simulator, centang satu *checkbox* - memakai penanda teks, bukan koordinat.
5. Simpan ke `docs/ui-evidence/tahap-<n>/<modul>-<status>-<viewport>.png`. Bukti lama tidak ditimpa; tiap tahap folder baru.

Daftar status wajib diabadikan (minimum):

| Modul | Status |
| :--- | :--- |
| Shell | Top bar + header pada muat pertama (desktop + 390) |
| Ringkasan | Keadaan awal resto pertama (desktop + 390); mode benchmark; panel data terbuka (dropzone terlihat) |
| Rincian | Aspek Rasa terpilih (desktop + 390); filter polaritas diubah ke Semua |
| Rencana Aksi | Progres 0%; satu status sebagian tercentang; kartu akar masalah + cip mode terlihat |
| Coba Ulasan | *Empty state*; hasil analisis preset 1 (desktop + 390) |
| Loading | Kartu loading bermerek - *best effort*: tangkap pada *start* server segar sebelum engine siap; bila tidak tertangkap, catat alasannya di laporan tahap, jangan dipalsukan |

## 6. Pembagian Kerja Executor dan Gerbang

Aturan main untuk seluruh tahap:

- **Satu penulis per file pada satu waktu.** Executor mengurutkan pekerjanya per tahap; tidak ada dua pekerja menyunting file yang sama secara paralel. `components.py`, `charts.py`, `theme.py` adalah file bersama - hanya disentuh pada tahap yang menyebutnya.
- Setiap tahap = satu commit di `ui-overhaul` (identitas Azura <azura@local>), pesan menyebut tahapnya. Tidak ada *squash* antar-tahap; riwayat tahap adalah jejak audit.
- Setiap gerbang menjalankan: `py -m pytest tests/ -q` (harus 13 lulus), AppTest `app.py` (0 *exception*), dan tangkapan layar tahap itu.
- Bila sebuah butir paritas mustahil dipenuhi bersamaan dengan DESIGN.md, Executor **berhenti dan melapor** ke orkestrator - tidak memutuskan sendiri.

| Tahap | Isi | Gerbang selesai |
| :--- | :--- | :--- |
| 0 - Baseline + pindah verbatim | Rekam `docs/ui-evidence/baseline.json`: KHS + skor per aspek untuk 4 resto + benchmark (dihitung dengan jalur yang sama seperti aplikasi: `evaluate_dataframe` atas data terfilter per resto), hash `app.py` lama, tangkapan UI lama seperlunya. Lalu pecah file sesuai Bagian 2 **tanpa mengubah tampilan** (CSS lama ikut pindah apa adanya ke `theme.py` sebagai string), hapus `build_clean_app.py` | G0: pytest 13 lulus; AppTest 0 *exception*; KHS hasil pecahan == baseline untuk 5 konteks; `git diff` membuktikan tidak ada file `src/` non-UI yang berubah |
| 1 - Fondasi tema + shell | `theme.py` ditulis ulang dari token DESIGN.md (font 3 peran, warna, radius, bayangan, sembunyikan *sidebar* + *chrome* Streamlit); TopBar + HeaderSapaan + `labels.py`; judul tab sesuai P-G1 | G1: tangkapan shell 1440 + 390; pytest + AppTest hijau; caption engine terbaca di top bar (P-E2) |
| 2 - Ringkasan (penentu *tone*) | Semua komponen Bagian 4.2 termasuk PanelData + Dropzone di modul ini | G2: tangkapan Ringkasan lengkap (Bagian 5); angka yang tampil == baseline (P-N2, P-N4); pytest + AppTest hijau. **BERHENTI - menunggu penilaian user lewat orkestrator sebelum Tahap 3** (sesuai DESIGN.md Bag. 11) |
| 3 - Rincian Aspek | Semua komponen Bagian 4.3 | G3: tangkapan Rincian; P-M3 s.d. P-M6 dibuktikan (hitung ulang dari `breakdown` yang sama); pytest + AppTest hijau |
| 4 - Rencana Aksi | Semua komponen Bagian 4.4 | G4: tangkapan Rencana (0% + sebagian); P-M7 s.d. P-M11 + P-X1 s.d. P-X4 dibuktikan (unduh TXT/PDF/CSV benar-benar dihasilkan dan isinya dibandingkan dengan versi pra-perombakan untuk data yang sama); pytest + AppTest hijau |
| 5 - Coba Ulasan | Semua komponen Bagian 4.5 | G5: tangkapan Coba (*empty* + hasil preset 1); P-M12 s.d. P-M16 dibuktikan (preset dibuka dari kode lama dan dibandingkan karakternya); pytest + AppTest hijau |
| 6 - Kilap akhir + paritas penuh | Gerak mikro CSS (Bag. 9 DESIGN.md), LoadingBermerek, responsif 390 untuk semua modul, *footer* | G6: set tangkapan penuh Bagian 5 untuk semua modul; **seluruh 44 butir paritas dibuktikan satu per satu** dalam tabel laporan; pytest + AppTest hijau; siap untuk Auditor independen |

## 7. Risiko Terbesar (Penilaian Planner)

1. **Perhitungan bersama yang berpindah rumah.** `eval_results`/`khs`/`breakdown` saat ini dihitung di tengah blok *sidebar* yang juga menggerakkan widget data. Salah urut saat memindah ke `core.py` bisa mengubah kapan `evaluate_dataframe` dipanggil (harus tetap satu kali per *run*, setelah filter resto final) dan menggeser angka secara diam-diam. Mitigasi: Tahap 0 verbatim + baseline 5 konteks di G0.
2. **Keadaan widget Streamlit.** Mengganti radio/tombol navigasi dengan `st.pills` dan memindah unggah keluar *sidebar* mengubah pohon widget; kunci sesi yang berubah bisa mereset keadaan pengguna (centang checklist, teks simulator) antar-*run*. Mitigasi: ID kanonis + pola kunci lama dipertahankan (P-D9), dibuktikan di G4/G5 dengan skenario centang -> pindah modul -> kembali.
3. **Kesetiaan figur Plotly.** Grafik digambar ulang di `charts.py`; mudah tergelincir ke pembulatan atau agregasi berbeda (mis. memakai ulang data mentah, bukan `breakdown`). Mitigasi: figur hanya boleh membaca `breakdown`/`eval_results` dari konteks; gerbang membandingkan data figur dengan `breakdown`.
4. **Waktu muat model vs tangkapan layar.** Muat pertama ±18 detik di CPU membuat tangkapan mudah menangkap keadaan setengah jadi. Mitigasi: penanda render + *timeout* panjang di `capture.py`, dan status *loading* memang salah satu status yang diabadikan.
5. **Fragilitas selector CSS Streamlit 1.57.** Menyembunyikan *sidebar*/*chrome* dan menata `st.pills` bertumpu pada `data-testid` versi ini. Versi sudah terpin di `requirements.txt` (streamlit 1.57.0) - jangan menaikkan versi di tengah perombakan.

## 8. Yang Secara Eksplisit Tidak Dilakukan

- Tidak mengubah satu pun file logika (daftar P-E5) atau dataset.
- Tidak menambah fitur baru (tidak ada tren waktu, tidak ada penyimpanan persisten checklist, tidak ada mode gelap).
- Tidak menaikkan versi dependensi apa pun.
- Tidak menyentuh `main` - seluruh pekerjaan di `ui-overhaul`.
