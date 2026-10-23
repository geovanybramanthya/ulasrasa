# Bukti Paket T - Penataan Widget + Kelas Landing (revisi landing)

Sumber: `src/ui/theme.py` saja (blok "penataan widget menyeluruh" + blok
"landing akun demo"). Server uji: Streamlit 1.57 lokal port 8531, Playwright
Chromium, viewport 1440x900 (desktop) dan 390x844 (mobile).

## Keadaan SEBELUM (dom_before.json, dom_before2.json, before-*.png)

- Menu selectbox: item `li[role=option]` warna slate `rgb(15,23,42)`, padding
  sempit `0px 5px`, item terpilih TANPA tinta pembeda, kontainer radius 8px.
- Kotak selectbox tertutup: latar slate-50 `rgb(248,250,252)`.
- Radio terpilih: lingkaran BIRU `rgb(37,99,235)` (#2563EB bawaan BaseWeb).
- Text input/area: kotak slate-50 radius 8px, border tak terlihat.
- Expander: border slate `rgba(15,23,42,0.2)` radius 8px, judul Inter.
- Alert info: kontainer radius 8px, font kontainer Source Sans.
- Tombol Upload dropzone: latar `rgba(136,176,215,0.15)`, radius 8px, label Inter.
- Landing: kartu akun tanpa gaya kartu (datar), kartu kaca di BAWAH gambar,
  celah kosong ~180px di atas landing (kompensasi top bar 162px ikut berlaku).

## Keadaan SESUDAH (widget_after.json, scroll_upload.json, scroll_find.json, fix_icon.json, after-*.png)

### (i) Popover selectbox TERBUKA (filter Rincian)
- Kontainer: radius 16px, bayangan `rgba(20,40,30,0.14) 0 16px 40px`, border #E7ECE8.
- Item: font Inter, warna tinta `rgb(20,35,27)`, padding item `2px 4px`,
  padding isi `8px 12px`, radius isi 10px.
- Terpilih (diam): tinta `rgb(205,238,219)` #CDEEDB + weight 600.
- Hover: tinta pastel `rgb(232,249,240)` #E8F9F0. Catatan: BaseWeb menandai item
  yang di-hover sebagai `aria-selected="true"`, jadi aturan `:hover` ditempatkan
  SETELAH aturan terpilih agar pastel menang saat hover.
- Kotak tertutup: latar putih, radius 12px, border #DDE5DF; focus ring hijau
  juga terukur pada textarea (border `rgb(34,197,94)` + ring 3px `rgba(34,197,94,0.15)`).

### (ii) Panel "Ganti Data" + expander TERBUKA
- Sapuan direct-text wilayah panel: mode preset 11 elemen / 0 Source Sans;
  mode unggah 15 elemen / 0 Source Sans.
- Radio: terpilih lingkaran `rgb(34,197,94)` #22C55E + titik putih;
  tak terpilih `rgb(196,210,200)` #C4D2C8.
- Expander: bingkai radius 16px border #E7ECE8; judul `<p>` Plus Jakarta Sans.
- Text area/input: latar putih, radius 12px, border #DDE5DF.
- Tombol primer "Simpan & Perbarui Dashboard" TIDAK tertimpa: gradien
  `linear-gradient(135deg, rgb(34,197,94), rgb(22,163,74))`, Jakarta, radius 12px.
- Dropzone: border putus-putus `rgb(185,207,192)`, radius 16px, latar #FAFCFB,
  teks instruksi Inter. Tombol Upload: putih, radius 12px, border #DDE5DF,
  label Plus Jakarta Sans. Ikon upload tetap "Material Symbols Rounded"
  (span `stIconMaterial` dikecualikan dari aturan font - lihat fix_icon.json
  dan after-dropzone-fix.png).
- Alert info: radius 14px, tinta biru pastel `rgba(28,131,255,0.1)` dipertahankan,
  font kontainer + teks Inter, teks "Menggunakan dataset aktif sementara."

### (iii) Non-regresi D1/D2 + modul lain
- Sapuan Ringkasan: 110 elemen teks, 0 Source Sans. Rencana (observasi
  tambahan): 80 elemen, 0 Source Sans.
- Sapaan: Plus Jakarta Sans. Angka KPI: JetBrains Mono. Judul kartu: Jakarta.
- Top bar: `position: fixed`, rect top 14px sebelum DAN sesudah scroll
  kontainer `section[data-testid=stMain]` sejauh 1042px (maks isi 1942px).
- Top bar 4 kolom desktop: tinggi 62px, bottom 76px, sapaan mulai y=194 -
  tidak menutupi konten; kompensasi 162px TIDAK diubah.
- Top bar mobile 390px: tinggi 230px, bottom 240px, sapaan mulai y=314 -
  kompensasi 282px yang ada cukup, TIDAK diubah.

### Landing (relay Pekerja L)
- Kartu akun `div[class*="st-key-landing_acct_"]`: putih, radius 20px,
  border #EDF1EE, padding 18px 22px 12px, bayangan token (terukur persis).
- Panel visual `div.st-key-landing_visual`: putih radius 20px padding 14px;
  `img` radius 14px. Mobile: margin-top 4px (terukur).
- `.landing-glass`: rgba(255,255,255,0.72) + blur 10px, radius 16px, dan
  MENIMPA gambar (margin-top -56px; terukur glass.top 405 < img.bottom 445
  desktop; juga overlap di mobile).
- `.landing-khs-num`: JetBrains Mono 600; desktop 24px, mobile 20.8px (1.3rem,
  perlu `!important` karena module_landing menulis font-size inline 1.5rem).
- Kompensasi landing: aturan `:not(:has(div.st-key-topbar))` menurunkan
  padding-top kontainer utama menjadi 48px khusus halaman tanpa top bar;
  konten pertama landing mulai y=64 (sebelumnya ~180). Dashboard tidak
  terpengaruh (padding tetap 162px/282px, terukur).
- Top bar: tombol "Ganti Akun" margin-top 6px + nowrap (terukur).
- `.account-identity`: kelas ditambahkan sesuai spesifikasi (nilai sama
  dengan style inline yang sudah ditulis components.py).

## Keterbatasan

- Ikon Material Symbols di dalam widget (chevron expander, ikon upload)
  hanya bisa diwarnai; font/bentuknya milik font ikon, tidak boleh disentuh
  aturan font teks (dibuktikan oleh bug ligatur "upload" yang diperbaiki).
- Warna aksen checkbox Rencana tidak diubah: struktur kotak checkbox adalah
  `span` (bukan pola div radio); keadaan tercentangnya tidak diukur paket ini.
- Border tombol Upload terukur 1px (BaseWeb menang soal ketebalan), warna/
  gaya/radius sesuai tema.
