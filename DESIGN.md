# DESIGN.md - UlasRasa (Perombakan UI)

Dokumen pengunci arah desain UlasRasa. Hasil wawancara *grill-me* 4 ronde (34 keputusan) + protokol *oil-ui*, disetujui user 2026-10-23. Setiap penyimpangan dari dokumen ini saat pembangunan wajib dicatat alasannya di dokumen ini juga.

## 1. North Star

Satu kalimat penuntun: **dashboard terang beraksen hijau segar dengan kartu pastel yang membuat pemilik UMKM membaca kesehatan dapurnya dalam 3 detik dan langsung tahu harus berbuat apa.**

## 2. Referensi yang Mengikat

Referensi visual utama (wajib diikuti, bukan sekadar inspirasi): *Sales AI Dashboard UI/UX Design - Modern Analytics & E-commerce* (Dribbble, https://dribbble.com/shots/27357293-Sales-AI-Dashboard-UI-UX-Design-Modern-Analytics-E-commerce) - terang, aksen hijau vibran, kartu pastel, bayangan lembut, sudut membulat, panel grafik besar + rel aktivitas.

Tata letak mengacu pola dashboard SaaS modern (Mercury/Plausible: bersih, angka besar terbaca sekilas) dan eksekusi dibatasi pada yang realistis di Streamlit (komponen modern + CSS kustom, tanpa ganti *framework*).

Penyimpangan yang sudah diputuskan sadar:

| Kode | Penyimpangan dari referensi | Alasan |
| :--- | :--- | :--- |
| D-01 | Navigasi di atas (bukan *sidebar* kiri) | Keputusan eksplisit user (grill-me R1Q3) |
| D-02 | Angka memakai *monospace* | Keputusan user soal sistem font multi-fungsi (R4Q1) |

## 3. Struktur Halaman

- *Top bar* lengket (*sticky*): logo SVG (mangkuk + uap daun, kotak membulat hijau) + nama "UlasRasa" di kiri; navigasi *pill* (`st.pills`) di tengah/kanan; cip mode engine kecil di kanan.
- *Sidebar* disembunyikan total. Unggah CSV menjadi kartu *dropzone* garis putus-putus di Modul Ringkasan; *caption* engine pindah ke *top bar*.
- *Header* tiap modul: sapaan "Halo, [nama resto]" (Jakarta Sans 800) + satu kalimat status dari hasil analisis; di kanan: *dropdown* pemilih resto bergaya *pill* + tombol kecil "Ganti Data".
- Judul tab browser: "UlasRasa - Kesehatan Dapur dari Ulasan"; ikon tab = logo SVG. *Chrome* bawaan Streamlit (menu, tombol Deploy, *footer*) disembunyikan.

## 4. Token Warna

| Token | Nilai | Pemakaian |
| :--- | :--- | :--- |
| Latar | `#F6F7F9` | Latar halaman (datar, tanpa gradasi) |
| Kartu | `#FFFFFF` | Semua permukaan kartu |
| Tinta utama | `#14231B` | Judul dan teks utama |
| Tinta redup | `#64756B` | Teks sekunder, label |
| Hijau brand | `#22C55E` | CTA, aksen utama, KHS |
| Hijau pekat | `#15803D` | Teks hijau di atas tint, hover CTA |
| Tint hijau | `#E8F9F0` | Latar cip/pill hijau |
| Negatif | teks `#B42318`, tint `#FDECEC` | Pill dan penanda negatif |
| Netral | teks `#B45309`, tint `#FEF3C7` | Pill netral |

Warna aspek (tetap di semua modul, kartu, dan grafik):

| Aspek | Aksen | Tint |
| :--- | :--- | :--- |
| Rasa | `#E8833A` | `#FFE8D6` |
| Porsi | `#0284C7` | `#E0F2FE` |
| Harga | `#D97706` | `#FEF3C7` |
| Kemasan | `#7C3AED` | `#EDE9FE` |
| Pelayanan | `#0D9488` | `#CCFBF1` |

Satu-satunya gradasi hijau yang diizinkan: kartu *hero* KHS dan tombol CTA utama.

## 5. Tipografi (Sistem 3 Peran)

| Peran | Font | Bobot | Pemakaian |
| :--- | :--- | :--- | :--- |
| Judul & brand | Plus Jakarta Sans | 700/800 | Sapaan, judul modul, judul kartu |
| Isi & tabel | Inter | 400/500/600 | Paragraf, teks ulasan, tabel, keterangan |
| Angka & skor | JetBrains Mono | 600 | Angka KPI, skor KHS, persen, nilai di grafik |

Aturan keras: angka selalu JetBrains Mono, judul selalu Plus Jakarta Sans, sisanya Inter - tidak ada pemakaian di luar peran. Label kecil bergaya kapital: 11 px, *letter-spacing* 0,08 em. Font dimuat dari Google Fonts dengan *fallback* tumpukan font sistem. Grafik Plotly mengikuti sistem yang sama (Inter untuk label, JetBrains Mono untuk nilai).

## 6. Bentuk & Ruang

- Radius kartu 20 px; radius cip/pill penuh; radius tombol 12 px.
- *Padding* kartu 20-24 px; jarak antar elemen 16-20 px; bayangan lembut `0 8px 24px rgba(20,40,30,0.06)`.
- Kepadatan lapang (*airy*) persis referensi; halaman boleh panjang dan bergulir.

## 7. Bahasa Antarmuka (Semi-Formal untuk UMKM)

Aturan: kalimat pendek, kata sehari-hari, sapa "Anda" seperlunya, istilah teknis hanya bila terpaksa dan selalu didampingi penjelasan polos. Pesan galat tidak menyalahkan pengguna. Istilah model (IndoBERT/LLM) hanya muncul kecil di *caption* mode untuk transparansi.

Padanan istilah wajib:

| Istilah teknis | Bahasa antarmuka |
| :--- | :--- |
| Kitchen Health Score (KHS) | Skor Kesehatan Dapur |
| Action Checklist | Daftar Aksi Dapur |
| Root cause | Akar Masalah |
| Deep-dive | Rincian |
| Simulator | Coba Ulasan |

Nama modul di navigasi: **Ringkasan** - **Rincian Aspek** - **Rencana Aksi** - **Coba Ulasan**.

## 8. Komponen per Modul

### Ringkasan (penentu *tone*, dibangun pertama)
- Baris 4 kartu KPI pastel (ikon SVG garis tipis di cip tint): Skor Kesehatan Dapur, Total Ulasan Dianalisis, Ulasan Negatif (%), Aspek Paling Kritis. *Microcopy* kartu bersifat faktual dari data - dilarang panah tren atau angka turunan yang tidak ada di data.
- Kartu *hero* KHS: cincin donat tebal (JetBrains Mono di tengah) di kiri; di kanan label status besar, cip aspek prioritas, tombol CTA "Lihat Rencana Aksi" (lompat ke modul Rencana Aksi). Ambang status mengikuti logika yang sudah ada di aplikasi; garis batas kritis aspek = 70.
- Grafik utama: batang horizontal skor kepuasan 5 aspek, warna per aspek, garis putus-putus di 70 berlabel "Batas kritis".
- Rel kanan "Keluhan Terbaru": maks 5 ulasan negatif, teks terpotong ±140 karakter + cip aspek + pill sentimen; klik kartu membuka Rincian Aspek dengan aspek itu terpilih.

### Rincian Aspek
- *Pill* pemilih aspek; kartu detail: donat distribusi sentimen + dua kolom contoh ulasan (positif vs negatif).
- Kartu tabel "Semua Ulasan": teks terpotong rapi + 5 kolom aspek berisi pill sentimen mini; dapat difilter per aspek.

### Rencana Aksi
- Kartu Akar Masalah di atas (dari LLM) + cip mode (LLM/Template).
- *Progress bar* hijau "% selesai" di puncak.
- Daftar aksi dikelompokkan per aspek dalam kartu, lencana prioritas, kotak centang persisten selama sesi (kunci per resto + data) + tombol "Atur Ulang".
- CTA utama: unduh PDF (hijau solid); sekunder: unduh TXT (*ghost*).

### Coba Ulasan
- Dua kolom: kartu input (area teks besar + tombol "Analisis") dan kartu hasil.
- Hasil: aspek yang disebut tampil sebagai baris penuh (cip ikon, nama aspek, pill sentimen, *bar confidence*); aspek tidak disebut diringkas satu baris redup "Tidak disebut: ...".
- *Empty state* ramah sebelum ada hasil.

## 9. Gerak & Status

Tiga gerak mikro berbasis CSS saja (Streamlit *rerun* terus - tanpa JS berat): kartu terangkat halus saat *hover*, transisi *fade* saat ganti modul, cincin KHS menganimasi saat tampil. Status muat model (pemuatan pertama bisa ±18 detik di CPU) memakai kartu *loading* bermerek dengan teks penjelas - bukan *spinner* polos. *Empty state* dan pesan galat mengikuti aturan bahasa di Bagian 7.

## 10. Responsif

Di bawah ±640 px: *pill* navigasi membungkus dua baris; kartu KPI menjadi grid 2x2; kartu *hero* bertumpuk vertikal (donat di atas); rel kanan Ringkasan pindah ke bawah grafik. Wajib diuji pada lebar 390 px saat pembangunan.

## 11. Urutan Bangun & Gerbang

1. Pekerjaan dilakukan di *branch* `ui-overhaul`; versi `main` (commit teraudit `461e646`) tidak disentuh sampai *submission* selesai.
2. Bangun Modul Ringkasan lebih dulu sebagai penentu *tone*; ambil tangkapan layar bukti (desktop + 390 px); user menilai.
3. Setelah Ringkasan disetujui, wariskan token + komponen ke Rincian Aspek, Rencana Aksi, Coba Ulasan.
4. Selesai semua modul: tinjauan visual independen (protokol *oil-ui*) + uji fungsi penuh (alur unggah -> analisis -> daftar aksi -> unduh) sebelum dinyatakan selesai.

## Adendum Revisi Landing - 2026-10-23

Keputusan terkunci hasil *grill* 2026-10-23 malam (Ronde 1 Q1-Q6 + Ronde 2 Q7-Q12), menyusul keluhan user: *dropdown* resto terasa *default*, *font* panel Ganti Data beda sendiri, dan semua resto tercampur dalam satu sesi. Daftar lengkap keputusan tersimpan di sandbox (`~/workspace/ulasrasa-design/ADENDUM-REVISI-LANDING.md`); bagian ini adalah versi ringkas yang mengikat pembangunan. Dikerjakan di *branch* `revisi-landing` (dari `main` `1ba73bf`); `main` tidak disentuh selama revisi berjalan.

1. Satu akun demo = satu resto. *Landing* adalah pintu masuk; *dashboard* hanya menampilkan resto akun aktif. *Dropdown*/*selectbox* ganti resto di *dashboard* dihapus.
2. "Semua Outlet (Benchmark Industri)" menjadi akun kelima di *landing* (dataset gabungan 100 ulasan).
3. Masuk = klik kartu akun, tanpa *password*/PIN. Kartu berlabel "Akun Demo".
4. *Layout landing* meniru struktur referensi BCS-ESG: kiri = *brand* + judul + daftar akun; kanan = panel visual besar. Kulit tetap identitas UlasRasa: hijau `#22C55E`, pastel, latar `#F6F7F9`, *font* Plus Jakarta Sans/Inter/JetBrains Mono.
5. Kartu akun berisi: nama resto + jumlah ulasan contoh (25 per resto; 100 untuk Benchmark) + cip status Skor Kesehatan Dapur yang dihitung riil dari data lewat *pipeline* yang ada (bukan angka *hardcode*). Target kecocokan: Ayam Geprek Sambal Korek Barokah 55,84 KRITIS; Bakso Rusuk Solo Pak Ndut 68,24 WASPADA; Bebek Goreng Madura Cak Roni 83,00 PRIMA; Kopi Susu Senja & Toast 59,55 KRITIS; Benchmark 67,27 WASPADA.
6. Paket penataan *widget*: *popover dropdown* BaseWeb di-*style* penuh; semua *widget* panel Ganti Data + *widget* bawaan lain diselaraskan (*font* + gaya). Audit wajib menyertakan keadaan panel/*popover* terbuka.
7. Panel "Ganti Data" tetap di *dashboard*. Mode Preset mengembalikan data akun aktif (bukan lagi pilihan resto); mode Upload CSV berperilaku persis seperti lama: dataset aktif sementara (batas 200 baris, wajib kolom `review_text`), sapaan "Outlet Kustom" saat unggahan aktif, dan Preset adalah jalan balik.
8. Fitur "Input Ulasan Baru ke Outlet Ini" dipertahankan di panel Ganti Data.
9. Panel visual kanan *landing*: ilustrasi dari aset `assets/ilustrasi-landing.webp` + satu kartu kaca berisi satu kalimat nilai aplikasi (semi-formal, tanpa angka karangan).
10. Kepala *dashboard*: area *selectbox* lama diganti kartu identitas akun statis (nama resto + cip "Akun Demo"); tombol "Ganti Data" tetap di bawahnya. Tombol "Ganti Akun" (*ghost*) di *top bar* paling kanan: kembali ke *landing* + bersihkan *state* akun dan dataset aktif sesi (unggahan/input ulasan sesi hilang, kembali murni).
11. *Mobile* 390 px: *landing* bertumpuk - *brand* + daftar akun dulu, panel visual menjadi *strip* di bawah.
12. Sapaan "Halo, [nama resto]" dan seluruh angka *dashboard* tidak berubah; perhitungan bersama (*eval_results*/KHS/*breakdown*) tidak bergeser. Kebijakan *merge*: hanya sesudah audit PASS + user melihat *screenshot*; bila mepet *deadline*, *deploy* memakai `main` versi sekarang (URL Space tidak berubah saat di-*update*).
