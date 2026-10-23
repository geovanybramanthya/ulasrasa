"""Tema UI UlasRasa - ditulis dari token DESIGN.md Bag. 4-6 (Tahap 1).

Sumber kebenaran visual satu-satunya adalah DESIGN.md:
- Warna: latar #F6F7F9, kartu putih, tinta #14231B, hijau brand #22C55E.
- Font 3 peran: Plus Jakarta Sans (judul), Inter (isi), JetBrains Mono (angka).
- Radius kartu 20 px, tombol 12 px, bayangan lembut token.
Sidebar dan chrome bawaan Streamlit disembunyikan total (DESIGN.md Bag. 3).
"""

import streamlit as st

# ---------------------------------------------------------------- token warna
COLORS = {
    "bg": "#F6F7F9",
    "card": "#FFFFFF",
    "ink": "#14231B",
    "muted": "#64756B",
    "green": "#22C55E",
    "green_deep": "#15803D",
    "green_tint": "#E8F9F0",
    "neg_text": "#B42318",
    "neg_tint": "#FDECEC",
    "neu_text": "#B45309",
    "neu_tint": "#FEF3C7",
    "line": "#E7ECE8",
}

ASPECT_COLORS = {
    "rasa": ("#E8833A", "#FFE8D6"),
    "porsi": ("#0284C7", "#E0F2FE"),
    "harga": ("#D97706", "#FEF3C7"),
    "kemasan": ("#7C3AED", "#EDE9FE"),
    "pelayanan": ("#0D9488", "#CCFBF1"),
}

FONT_DISPLAY = "'Plus Jakarta Sans', 'Inter', -apple-system, 'Segoe UI', sans-serif"
FONT_BODY = "'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif"
FONT_MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, monospace"

SHADOW_CARD = "0 8px 24px rgba(20,40,30,0.06)"

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@600&display=swap');

/* ---------- basis ---------- */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #F6F7F9 !important;
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
    color: #14231B !important;
}
[data-testid="stAppViewContainer"] .main .block-container {
    padding-top: 1.1rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1400px !important;
}
h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
    color: #14231B !important;
    letter-spacing: -0.01em !important;
}
p, span, label, li, td, th { color: #14231B; }
.num, .kpi-value, .hero-score {
    font-family: 'JetBrains Mono', Consolas, monospace !important;
    font-weight: 600 !important;
}
.label-caps {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 11px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #64756B;
}

/* ---------- font isi elemen bawaan Streamlit/BaseWeb (perbaikan D1) ---------- */
/* Streamlit/BaseWeb menetapkan "Source Sans" langsung pada elemen-elemen ini,
   sehingga aturan font di html/body tidak menjangkaunya. Paksa Inter di sini.
   Aturan sengaja sempit (tipe elemen di dalam wadah markdown, textarea, input,
   select) agar tidak menimpa peran font lain: judul tetap Plus Jakarta Sans
   (aturan h1-h6 + kelas kustom) dan angka tetap JetBrains Mono (kelas .num dsb.
   berbasis <div>/<span> kustom, bukan target aturan ini). */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] blockquote,
[data-testid="stWidgetLabel"] p,
[data-testid="stCaptionContainer"] p {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
}
/* label tombol Streamlit juga <p> di dalam wadah markdown - pertahankan Jakarta */
.stButton [data-testid="stMarkdownContainer"] p,
.stDownloadButton [data-testid="stMarkdownContainer"] p {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
}
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
}
[data-baseweb="select"], [data-baseweb="select"] *,
[data-baseweb="popover"], [data-baseweb="popover"] *,
[data-baseweb="menu"], [data-baseweb="menu"] * {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
}

/* ---------- font isi elemen HTML kustom (perbaikan D1 putaran 2) ---------- */
/* Audit ulang menemukan sisa "Source Sans" pada div/span HTML KUSTOM di dalam
   wadah markdown (subjudul kartu, microcopy KPI, teks ulasan, teks akar
   masalah, dst). Akar masalahnya: wadah markdown Streamlit menetapkan
   "Source Sans" yang diwarisi div/span kustom, dan kelas-kelas teks isi di
   tema ini semula tidak menyatakan font-family sendiri. Perbaikan berlapis:
   (a) setiap kelas teks isi di bawah menyatakan Inter secara eksplisit pada
       definisinya masing-masing (lihat .card-sub, .kpi-micro, .review-text,
       .rca-text, dan kawan-kawannya);
   (b) jaring pengaman keturunan di sini menangkap div/span kustom lain yang
       belum berkelas peran. :where() membuat spesifisitas aturan ini NOL,
       jadi aturan kelas eksplisit mana pun selalu menang; daftar :not()
       mengecualikan pembawa kelas berperan Jakarta/Mono DAN keturunannya
       (mis. span persen di dalam .stat-value yang harus tetap Mono). */
:where(
  [data-testid="stMarkdownContainer"] div:not(.greeting):not(.card-title):not(.kpi-label):not(.label-caps):not(.brand-name):not(.brand-sub):not(.hero-status):not(.stat-label):not(.num):not(.kpi-value):not(.hero-score):not(.hero-score-big):not(.stat-value):not(.conf-val):not(.sop-num):not(.rca-num):not(.greeting *):not(.card-title *):not(.kpi-label *):not(.label-caps *):not(.brand-name *):not(.brand-sub *):not(.hero-status *):not(.stat-label *):not(.num *):not(.kpi-value *):not(.hero-score *):not(.hero-score-big *):not(.stat-value *):not(.conf-val *):not(.sop-num *):not(.rca-num *),
  [data-testid="stMarkdownContainer"] span:not(.greeting):not(.card-title):not(.kpi-label):not(.label-caps):not(.brand-name):not(.brand-sub):not(.hero-status):not(.stat-label):not(.num):not(.kpi-value):not(.hero-score):not(.hero-score-big):not(.stat-value):not(.conf-val):not(.sop-num):not(.rca-num):not(.greeting *):not(.card-title *):not(.kpi-label *):not(.label-caps *):not(.brand-name *):not(.brand-sub *):not(.hero-status *):not(.stat-label *):not(.num *):not(.kpi-value *):not(.hero-score *):not(.hero-score-big *):not(.stat-value *):not(.conf-val *):not(.sop-num *):not(.rca-num *)
) {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
}

/* ---------- chrome streamlit disembunyikan ---------- */
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer { display: none !important; visibility: hidden !important; }

/* ---------- gerak mikro ---------- */
@keyframes fadeUp { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
.ulas-card, .kpi-card, .hero-card { animation: fadeUp 0.4s ease both; }

/* ---------- top bar ---------- */
/* Perbaikan D2: position: sticky GAGAL di Streamlit 1.57 karena pembungkus
   stLayoutWrapper hanya setinggi top bar itu sendiri (sticky kehabisan ruang
   gerak di dalam induknya). Solusi yang terbukti bekerja: position: fixed +
   kompensasi padding-top pada kontainer utama (lihat aturan
   stMainBlockContainer di bawah) supaya konten awal tidak tertutup. */
div.st-key-topbar {
    position: fixed; top: 14px; left: 80px; right: 80px; width: auto; z-index: 1000;
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(10px);
    border: 1px solid #E7ECE8; border-radius: 16px;
    padding: 10px 18px 4px 18px;
    box-shadow: 0 8px 24px rgba(20,40,30,0.06);
    margin: 0;
}
/* kompensasi ruang yang dulu ditempati top bar di alur dokumen:
   padding-top bawaan Streamlit (96px) + tinggi pembungkus top bar (66px) */
[data-testid="stMainBlockContainer"] {
    padding-top: 162px !important;
}
.brand-lockup { display: flex; align-items: center; gap: 10px; padding-top: 2px; }
.brand-badge {
    width: 38px; height: 38px; border-radius: 12px; flex-shrink: 0;
    background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 6px 16px rgba(34,197,94,0.35);
}
.brand-name { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; font-size: 1.18rem; color: #14231B; line-height: 1.05; }
.brand-sub { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase; color: #64756B; }
.engine-chip {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
    display: inline-flex; align-items: center; gap: 6px;
    background: #E8F9F0; color: #15803D;
    border: 1px solid #CDEEDB; border-radius: 999px;
    padding: 4px 11px; font-size: 0.72rem; font-weight: 600;
    float: right; margin-top: 8px; white-space: nowrap;
}

/* st.pills navigasi */
/* Streamlit 1.57: pills = stButtonGroup; aktif berkind="pillsActive" */
[data-testid="stButtonGroup"] { justify-content: center; }
[data-testid="stButtonGroup"] button {
    border-radius: 999px !important;
    border: 1px solid #E2E8E4 !important;
    background: #FFFFFF !important;
    color: #14231B !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    padding: 6px 16px !important;
}
[data-testid="stButtonGroup"] button[kind="pillsActive"] {
    background: #22C55E !important; border-color: #22C55E !important; color: #FFFFFF !important;
}

/* ---------- header sapaan ---------- */
.greeting {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800; font-size: 1.72rem; color: #14231B;
    letter-spacing: -0.02em; line-height: 1.15; margin-bottom: 2px;
}
.status-line { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; font-size: 0.92rem; color: #64756B; line-height: 1.45; }
.status-line b { color: #14231B; }

/* ---------- kartu generik ---------- */
.ulas-card {
    background: #FFFFFF; border: 1px solid #EDF1EE; border-radius: 20px;
    padding: 20px 24px; margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(20,40,30,0.06);
    transition: transform 0.22s ease, box-shadow 0.22s ease;
}
.ulas-card:hover { transform: translateY(-2px); box-shadow: 0 14px 32px rgba(20,40,30,0.09); }
.card-title {
    font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700;
    font-size: 1.02rem; color: #14231B; margin-bottom: 4px;
}
.card-sub { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; font-size: 0.83rem; color: #64756B; line-height: 1.45; }

/* ---------- kartu KPI pastel ---------- */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px; }
.kpi-card {
    border-radius: 20px; padding: 18px 20px;
    box-shadow: 0 8px 24px rgba(20,40,30,0.05);
    transition: transform 0.22s ease, box-shadow 0.22s ease;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 14px 30px rgba(20,40,30,0.09); }
.kpi-icon-chip {
    width: 34px; height: 34px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    background: rgba(255,255,255,0.65); margin-bottom: 10px;
}
.kpi-label {
    font-family: 'Plus Jakarta Sans', sans-serif; font-size: 11px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em; color: #64756B; margin-bottom: 4px;
}
.kpi-value { font-size: 1.9rem; line-height: 1.1; color: #14231B; }
.kpi-micro { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; font-size: 0.78rem; color: #64756B; margin-top: 4px; line-height: 1.4; }

/* ---------- hero KHS ---------- */
.hero-card {
    background: linear-gradient(120deg, #22C55E 0%, #12994A 55%, #0D9488 130%);
    border-radius: 20px; padding: 22px 26px; color: #FFFFFF;
    box-shadow: 0 16px 36px rgba(21,128,61,0.25); margin-bottom: 16px;
}
.hero-card .label-caps { color: rgba(255,255,255,0.85); }
.hero-status { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; font-size: 1.5rem; color: #FFFFFF; line-height: 1.2; }
.hero-note { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; font-size: 0.88rem; color: rgba(255,255,255,0.92); line-height: 1.5; }
.hero-chip {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.35);
    color: #FFFFFF; border-radius: 999px; padding: 4px 12px;
    font-size: 0.76rem; font-weight: 600;
}

/* hero sebagai container berkunci (agar tombol Streamlit bisa tinggal di dalamnya) */
div.st-key-hero {
    background: linear-gradient(120deg, #22C55E 0%, #12994A 55%, #0D9488 130%);
    border-radius: 20px; padding: 10px 14px;
    box-shadow: 0 16px 36px rgba(21,128,61,0.25); margin-bottom: 16px;
    animation: fadeUp 0.4s ease both;
}
div.st-key-hero .hero-score-big {
    font-family: 'JetBrains Mono', Consolas, monospace; font-weight: 600;
    font-size: 3rem; color: #FFFFFF; line-height: 1.05;
}
div.st-key-hero .label-caps { color: rgba(255,255,255,0.85); }

/* kerangka bar skor aspek (Tahap 1; figur Plotly resmi menyusul) */
.mini-bar-track { background: #EFF3F0; border-radius: 6px; height: 8px; overflow: hidden; }
.mini-bar-fill { height: 100%; border-radius: 6px; }
.rel-item { border: 1px solid #EDF1EE; border-radius: 14px; padding: 12px 14px; margin-bottom: 10px; background: #FFFFFF; }
.rel-text { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; font-size: 0.86rem; color: #14231B; line-height: 1.45; margin-bottom: 8px; }

/* kartu grafik & rel keluhan sebagai container berkunci (Tahap 2) */
div.st-key-chartcard, div.st-key-relcard {
    background: #FFFFFF; border: 1px solid #EDF1EE; border-radius: 20px;
    padding: 18px 20px 10px 20px;
    box-shadow: 0 8px 24px rgba(20,40,30,0.06);
    animation: fadeUp 0.4s ease both; margin-bottom: 16px;
}
div.st-key-relcard button {
    padding: 2px 10px !important; font-size: 0.78rem !important; min-height: 28px !important;
    border-radius: 999px !important;
}
div.st-key-hero [data-testid="stPlotlyChart"] { margin-top: -6px; margin-bottom: -8px; }

/* tabel mini rincian aspek */
.mini-table { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; width: 100%; border-collapse: collapse; font-size: 0.87rem; }
.mini-table th {
    text-align: left; color: #64756B; font-weight: 600; font-size: 0.72rem;
    text-transform: uppercase; letter-spacing: 0.06em;
    border-bottom: 1px solid #EDF1EE; padding: 6px 8px;
}
.mini-table td { border-bottom: 1px solid #F3F6F4; padding: 8px; color: #14231B; }
.mini-table tr:last-child td { border-bottom: none; }
.asp-dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 7px; }

/* panel data sebagai container berkunci */
div.st-key-paneldata {
    background: #FFFFFF; border: 1px solid #EDF1EE; border-radius: 20px;
    padding: 18px 22px 8px 22px; margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(20,40,30,0.06);
    animation: fadeUp 0.4s ease both;
}

/* ---------- chip & pill ---------- */
.chip {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
    display: inline-flex; align-items: center; gap: 6px;
    border-radius: 999px; padding: 3px 10px;
    font-size: 0.74rem; font-weight: 600;
}
.pill-pos { background: #E8F9F0; color: #15803D; border: 1px solid #CDEEDB; }
.pill-neg { background: #FDECEC; color: #B42318; border: 1px solid #F8D2CF; }
.pill-neu { background: #FEF3C7; color: #B45309; border: 1px solid #F3E3AC; }
.pill-muted { background: #EFF3F0; color: #64756B; border: 1px solid #E2E8E4; }

/* ---------- panel data / dropzone ---------- */
.panel-data {
    background: #FFFFFF; border: 1px solid #EDF1EE; border-radius: 20px;
    padding: 20px 24px; margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(20,40,30,0.06);
}
[data-testid="stFileUploader"] section {
    border: 1.5px dashed #B9CFC0 !important; border-radius: 16px !important;
    background: #FAFCFB !important;
}

/* ---------- widget umum ---------- */
.stButton > button {
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%) !important;
    color: #FFFFFF !important; border: 1px solid #15803D !important;
    box-shadow: 0 8px 20px rgba(34,197,94,0.30) !important;
}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(135deg, #1DB455 0%, #129244 100%) !important; color: #FFFFFF !important;
}
.stButton > button[kind="secondary"], .stButton > button[data-testid="baseButton-secondary"] {
    background: #FFFFFF !important; color: #14231B !important; border: 1.5px solid #DDE5DF !important;
}
.stButton > button[kind="secondary"]:hover, .stButton > button[data-testid="baseButton-secondary"]:hover {
    border-color: #22C55E !important; color: #15803D !important;
}
.stDownloadButton > button {
    border-radius: 12px !important; background: #FFFFFF !important; color: #14231B !important;
    border: 1.5px solid #DDE5DF !important; font-weight: 700 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stDownloadButton > button:hover { border-color: #22C55E !important; color: #15803D !important; }
div[data-baseweb="select"] > div { border-radius: 12px !important; border-color: #DDE5DF !important; }
[data-testid="stProgress"] [data-baseweb="progress-bar"] > div > div { background-color: #EFF3F0 !important; }
[data-testid="stProgress"] [data-baseweb="progress-bar"] > div > div > div { background-color: #22C55E !important; }
[data-testid="stCheckbox"] label p { font-size: 0.9rem; }

/* ---------- penataan widget menyeluruh (revisi landing, paket T) ---------- */
/* Celah audit sebelumnya: keadaan TERBUKA tidak pernah tersapu - popover menu
   selectbox (lapisan BaseWeb yang dirender sebagai portal di <body>) dan isi
   Panel "Ganti Data" (radio/uploader/expander/input/alert) masih membawa
   gaya bawaan BaseWeb (teks slate #0F172A, aksen biru #2563EB, radius 8px,
   latar slate-50) yang terasa "setelan default" di tengah tema. Aturan di
   bawah menata semuanya ke token tema. Semua selector spesifik
   BaseWeb/Streamlit 1.57 (data-baseweb / data-testid / role), TANPA selector
   div/span generik, dan jaring pengaman D1 di atas tidak diubah. */

/* --- selectbox tertutup: kotak selaras kartu --- */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #14231B !important;
}
div[data-baseweb="select"] > div:focus-within {
    border-color: #22C55E !important;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.15) !important;
}
[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] p {
    color: #14231B !important;
}

/* --- popover / menu selectbox TERBUKA (BaseWeb) --- */
[data-baseweb="popover"] > div {
    border-radius: 16px !important;
    border: 1px solid #E7ECE8 !important;
    box-shadow: 0 16px 40px rgba(20,40,30,0.14) !important;
    overflow: hidden !important;
}
[data-baseweb="menu"], ul[data-baseweb="menu"],
[data-testid="stSelectboxVirtualDropdown"] {
    border-radius: 16px !important;
    background-color: transparent !important;
    padding: 6px !important;
}
[data-baseweb="menu"] li, [data-baseweb="menu"] li *,
[data-testid="stSelectboxVirtualDropdown"] li,
[data-testid="stSelectboxVirtualDropdown"] li * {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
    color: #14231B !important;
}
[data-baseweb="menu"] li[role="option"],
[data-testid="stSelectboxVirtualDropdown"] li[role="option"] {
    padding: 2px 4px !important;
}
[data-baseweb="menu"] li[role="option"] > div,
[data-testid="stSelectboxVirtualDropdown"] li[role="option"] > div {
    padding: 8px 12px !important;
    border-radius: 10px !important;
}
/* Urutan penting: aturan :hover SETELAH [aria-selected] karena BaseWeb
   ikut menandai item yang di-hover sebagai aria-selected="true";
   dengan spesifisitas setara, aturan terakhir menang saat hover
   (pastel terang), sedangkan item terpilih diam tampil lebih tegas. */
[data-baseweb="menu"] li[role="option"][aria-selected="true"] > div,
[data-testid="stSelectboxVirtualDropdown"] li[role="option"][aria-selected="true"] > div {
    background-color: #CDEEDB !important;
    font-weight: 600 !important;
}
[data-baseweb="menu"] li[role="option"]:hover > div,
[data-testid="stSelectboxVirtualDropdown"] li[role="option"]:hover > div {
    background-color: #E8F9F0 !important;
}

/* --- label widget konsisten --- */
[data-testid="stWidgetLabel"] p {
    font-weight: 500 !important;
    color: #14231B !important;
}

/* --- radio: aksen hijau saat terpilih --- */
/* Struktur 1.57: label > div lingkaran luar (16px) > div titik dalam.
   Bawaan BaseWeb mewarnai lingkaran terpilih biru #2563EB. */
[data-testid="stRadio"] label > div:first-child {
    background-color: #C4D2C8 !important;
}
[data-testid="stRadio"] label:has(input:checked) > div:first-child {
    background-color: #22C55E !important;
}
[data-testid="stRadio"] label:has(input:checked) > div:first-child > div {
    background-color: #FFFFFF !important;
}
[data-testid="stRadio"] label [data-testid="stMarkdownContainer"] p {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
    color: #14231B !important;
}

/* --- file uploader: dropzone + tombol Upload gaya ghost --- */
/* Span ikon stIconMaterial DIKECUALIKAN dari aturan font di bawah:
   font-nya "Material Symbols Rounded" (ligatur "upload" dsb.);
   memaksakan Inter mengubah ikon menjadi teks literal tumpang tindih. */
[data-testid="stFileUploader"] section,
[data-testid="stFileUploaderDropzone"] {
    border: 1.5px dashed #B9CFC0 !important;
    border-radius: 16px !important;
    background: #FAFCFB !important;
}
[data-testid="stFileUploaderDropzone"] div,
[data-testid="stFileUploaderDropzone"] span:not([data-testid="stIconMaterial"]),
[data-testid="stFileUploaderDropzoneInstructions"] div,
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stUploadedFile"] div, [data-testid="stUploadedFile"] span:not([data-testid="stIconMaterial"]) {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
    color: #14231B !important;
}
[data-testid="stFileUploader"] button[kind="secondary"],
[data-testid="stFileUploader"] button[data-testid="stBaseButton-secondary"] {
    background: #FFFFFF !important;
    color: #14231B !important;
    border: 1.5px solid #DDE5DF !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}
[data-testid="stFileUploader"] button[kind="secondary"]:hover,
[data-testid="stFileUploader"] button[data-testid="stBaseButton-secondary"]:hover {
    border-color: #22C55E !important;
    color: #15803D !important;
}
[data-testid="stFileUploader"] button [data-testid="stMarkdownContainer"] p {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
    font-weight: 700 !important;
}

/* --- expander: judul Jakarta, chevron + bingkai selaras --- */
[data-testid="stExpander"] details {
    border: 1px solid #E7ECE8 !important;
    border-radius: 16px !important;
    background: #FFFFFF !important;
}
[data-testid="stExpander"] summary {
    border-radius: 16px !important;
    padding: 10px 14px !important;
}
[data-testid="stExpander"] summary:hover {
    background-color: #F2F9F4 !important;
}
[data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] p {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
    font-weight: 700 !important;
    color: #14231B !important;
}
[data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
    color: #64756B !important;
}
[data-testid="stExpanderDetails"] {
    border-top: 1px solid #EDF1EE !important;
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
}

/* --- text area & text input: kotak putih + focus ring hijau lembut --- */
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"] {
    background-color: #FFFFFF !important;
    border: 1px solid #DDE5DF !important;
    border-radius: 12px !important;
}
[data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stTextAreaRootElement"]:focus-within {
    border-color: #22C55E !important;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.15) !important;
}
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {
    color: #14231B !important;
    background-color: transparent !important;
}

/* --- alert / info box: radius kartu + Inter, tinta varian dipertahankan --- */
[data-testid="stAlertContainer"] {
    border-radius: 14px !important;
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
}
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
    color: #14231B !important;
}



/* ---------- landing akun demo (revisi landing, relay Pekerja L) ---------- */
/* Kelas untuk module_landing.py + kartu identitas di components.py.
   Nama kelas/kunci persis dari kedua file itu: kontainer berkunci
   st-key-landing_acct_* dan st-key-landing_visual; kelas .landing-khs-num,
   .landing-khs-row, .landing-acct-head, .landing-glass, .account-identity.
   Pola kartu mengikuti div[class*="st-key-card_"] yang sudah ada. */
div[class*="st-key-landing_acct_"] {
    background: #FFFFFF; border: 1px solid #EDF1EE; border-radius: 20px;
    padding: 18px 22px 12px 22px; margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(20,40,30,0.06);
    animation: fadeUp 0.4s ease both;
}
div.st-key-landing_visual {
    background: #FFFFFF; border: 1px solid #EDF1EE; border-radius: 20px;
    padding: 14px;
    box-shadow: 0 8px 24px rgba(20,40,30,0.06);
    animation: fadeUp 0.4s ease both;
}
div.st-key-landing_visual img { border-radius: 14px; }
.landing-khs-num {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600; font-size: 1.5rem; color: #14231B; line-height: 1.1;
}
.landing-khs-row { display: flex; align-items: center; gap: 10px; margin: 2px 0 12px 0; }
.landing-acct-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
/* Kartu kaca MENIMPA bagian bawah gambar di dalam panel visual:
   position relative + margin-top negatif menariknya naik ke atas gambar
   (di dalam padding 14px panel), margin samping menyelaraskan tepi. */
.landing-glass {
    position: relative; z-index: 2;
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.65); border-radius: 16px;
    padding: 16px 18px;
    box-shadow: 0 8px 24px rgba(20,40,30,0.08);
    margin-top: -56px; margin-left: 14px; margin-right: 14px;
}
/* kartu identitas akun di header dashboard (pengganti selectbox resto lama) */
.account-identity {
    background: #FFFFFF; border: 1px solid #EDF1EE; border-radius: 16px;
    padding: 12px 16px; margin-bottom: 8px;
    box-shadow: 0 8px 24px rgba(20,40,30,0.06);
}
/* Landing TIDAK punya top bar, jadi kompensasi padding-top D2 (162px) 
   tidak boleh berlaku di sana (celah kosong ~180px di atas judul). 
   Aturan :not(:has(...)) hanya aktif bila top bar absen; dashboard 
   selalu merender top bar sehingga kompensasi D2 tidak berubah. */
[data-testid="stMainBlockContainer"]:not(:has(div.st-key-topbar)) {
    padding-top: 3rem !important;
}

/* top bar 4 kolom: tombol Ganti Akun (ghost) sejajar pill navigasi */
div.st-key-topbar [data-testid="stButton"] button {
    margin-top: 6px; white-space: nowrap;
}

/* ---------- kartu statistik mini (Rincian, Tahap 3) ---------- */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
.stat-card { background: #FFFFFF; border: 1px solid #EDF1EE; border-radius: 16px; padding: 14px 16px; box-shadow: 0 8px 24px rgba(20,40,30,0.05); }
.stat-value { font-family: 'JetBrains Mono', Consolas, monospace; font-weight: 600; font-size: 1.45rem; color: #14231B; line-height: 1.15; }
.stat-label { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: #64756B; margin-top: 2px; }

/* ---------- kartu contoh ulasan (Rincian, Tahap 3) ---------- */
.review-card { border: 1px solid #EDF1EE; border-radius: 14px; padding: 12px 14px; margin-bottom: 10px; background: #FFFFFF; }
.review-text { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; font-size: 0.88rem; color: #14231B; line-height: 1.5; }
.review-meta { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; font-size: 0.74rem; color: #64756B; margin-top: 6px; }

/* ---------- tabel semua ulasan (Rincian, Tahap 3) ---------- */
.table-wrap { overflow-x: auto; }
.data-table { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; width: 100%; border-collapse: collapse; font-size: 0.85rem; min-width: 660px; }
.data-table th { text-align: left; color: #64756B; font-weight: 600; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; border-bottom: 1px solid #EDF1EE; padding: 6px 8px; white-space: nowrap; }
.data-table td { border-bottom: 1px solid #F3F6F4; padding: 8px; color: #14231B; vertical-align: top; }
.data-table tr:last-child td { border-bottom: none; }
.mini-pill { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; display: inline-block; border-radius: 999px; padding: 1px 8px; font-size: 0.7rem; font-weight: 600; white-space: nowrap; }

/* ---------- akar masalah & daftar aksi (Rencana, Tahap 4) ---------- */
.rca-num { width: 24px; height: 24px; border-radius: 50%; background: #B42318; color: #FFFFFF; font-size: 0.78rem; font-weight: 700; text-align: center; line-height: 24px; flex-shrink: 0; font-family: 'JetBrains Mono', Consolas, monospace; }
.rca-row { display: flex; gap: 10px; align-items: flex-start; padding: 10px 0; border-bottom: 1px solid #F3F6F4; }
.rca-row:last-child { border-bottom: none; }
.rca-text { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; font-size: 0.9rem; color: #14231B; line-height: 1.5; }
.sop-row { display: flex; gap: 10px; align-items: flex-start; padding: 9px 0; border-bottom: 1px solid #F3F6F4; }
.sop-row:last-child { border-bottom: none; }
.sop-num { font-family: 'JetBrains Mono', Consolas, monospace; font-weight: 600; font-size: 0.85rem; color: #15803D; min-width: 22px; }
.stDownloadButton > button[kind="primary"], .stDownloadButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%) !important;
    color: #FFFFFF !important; border: 1px solid #15803D !important;
    box-shadow: 0 8px 20px rgba(34,197,94,0.30) !important;
}

/* ---------- baris hasil analisis (Coba, Tahap 5) ---------- */
.aspect-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #F3F6F4; }
.aspect-row:last-child { border-bottom: none; }
.aspect-chip { width: 32px; height: 32px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.aspect-name { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; font-weight: 600; font-size: 0.92rem; min-width: 84px; color: #14231B; }
.conf-track { flex: 1; background: #EFF3F0; border-radius: 6px; height: 8px; overflow: hidden; }
.conf-fill { height: 100%; border-radius: 6px; }
.conf-val { font-family: 'JetBrains Mono', Consolas, monospace; font-weight: 600; font-size: 0.8rem; min-width: 54px; text-align: right; color: #14231B; }
.not-mentioned-line { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; font-size: 0.84rem; color: #64756B; padding-top: 10px; }

/* ---------- wadah kartu generik berkunci card_* (Tahap 3-5) ---------- */
div[class*="st-key-card_"] {
    background: #FFFFFF; border: 1px solid #EDF1EE; border-radius: 20px;
    padding: 18px 22px 12px 22px; margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(20,40,30,0.06);
    animation: fadeUp 0.4s ease both;
}

/* ---------- loading bermerek ---------- */
.loading-card {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
    background: #FFFFFF; border: 1px solid #EDF1EE; border-radius: 20px;
    padding: 34px 28px; text-align: center;
    box-shadow: 0 8px 24px rgba(20,40,30,0.06); margin-top: 60px;
}
.loading-pulse {
    width: 54px; height: 54px; border-radius: 16px; margin: 0 auto 14px auto;
    background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%);
    display: flex; align-items: center; justify-content: center;
    animation: lpulse 1.6s ease-in-out infinite;
}
@keyframes lpulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.07); } }

/* ---------- footer ---------- */
.footer-line { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; font-size: 0.76rem; color: #64756B; text-align: center; padding: 10px 0 2px 0; }
.footer-line b { color: #14231B; }

/* ---------- responsif (<=640px) ---------- */
@media (max-width: 640px) {
    .kpi-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
    .stat-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
    .aspect-name { min-width: 64px; font-size: 0.86rem; flex: 1; }
    .aspect-row { flex-wrap: wrap; row-gap: 6px; }
    .conf-track { order: 5; flex: 1 1 100%; }
    .conf-val { min-width: 46px; }
    .greeting { font-size: 1.35rem; }
    .ulas-card, .panel-data { padding: 16px; border-radius: 16px; }
    .hero-card { padding: 18px; }
    div.st-key-topbar { padding: 8px 12px 2px 12px; top: 10px; left: 16px; right: 16px; }
    /* kompensasi D2 mobile: 96px bawaan + pembungkus top bar 186px */
    [data-testid="stMainBlockContainer"] { padding-top: 282px !important; }
    .engine-chip { float: none; margin-top: 4px; }
    .landing-khs-num { font-size: 1.3rem !important; }
    div.st-key-landing_visual { margin-top: 4px; }
}
</style>
"""


def inject_theme() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)
