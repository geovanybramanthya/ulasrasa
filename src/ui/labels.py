"""Peta label & teks UI UlasRasa (bahasa semi-formal untuk UMKM, DESIGN.md Bag. 7).

MODULE_CHOICES adalah ID modul kanonis internal (nilai session_state
``active_module_name``) - TIDAK diubah dari versi pra-perombakan.
Nama tampilan pendek mengikuti DESIGN.md Bag. 7 lewat MODULE_LABELS.
Semua teks antarmuka yang baru ditulis di file ini agar konsisten.
"""

MODULE_CHOICES = [
    "Ringkasan Eksekutif & Health Score",
    "Deep-Dive Aspek & Sentimen",
    "AI Kitchen Action Checklist",
    "Single Review Simulator (Live Demo)",
]

# Nama tampilan pendek (DESIGN.md Bag. 7) per ID kanonis.
MODULE_LABELS = {
    "Ringkasan Eksekutif & Health Score": "Ringkasan",
    "Deep-Dive Aspek & Sentimen": "Rincian Aspek",
    "AI Kitchen Action Checklist": "Rencana Aksi",
    "Single Review Simulator (Live Demo)": "Coba Ulasan",
}

# Kebalikan MODULE_LABELS: label tampilan -> ID kanonis.
LABEL_TO_MODULE = {v: k for k, v in MODULE_LABELS.items()}

DEFAULT_MODULE = MODULE_CHOICES[0]

# Urutan aspek kanonis + label tampilannya.
ASPECT_ORDER = ["rasa", "porsi", "harga", "kemasan", "pelayanan"]
ASPECT_LABELS = {a: a.capitalize() for a in ASPECT_ORDER}

SENTIMENT_LABELS = {
    "positive": "Positif",
    "negative": "Negatif",
    "neutral": "Netral",
    "not_mentioned": "Tidak disebut",
}

# Nilai mode sumber data (string dipertahankan persis dari versi lama,
# karena menjadi nilai session dan teks yang dikenali pengguna).
DATA_MODE_PRESET = "Outlet Bawaan (Preset)"
DATA_MODE_UPLOAD = "Upload Dataset Real (CSV)"
DATA_MODES = [DATA_MODE_PRESET, DATA_MODE_UPLOAD]

BENCHMARK_LABEL = "Semua Outlet (Benchmark Industri)"
UPLOAD_FALLBACK_RESTO = "Outlet Kustom"

# ---------------------------------------------------------------- teks shell
APP_TITLE = "UlasRasa - Kesehatan Dapur dari Ulasan"
BRAND_NAME = "UlasRasa"
BRAND_SUB = "Kesehatan Dapur dari Ulasan"
ENGINE_CHIP_PREFIX = "Engine ABSA"

LOADING_TITLE = "Menyiapkan UlasRasa"
LOADING_BODY = (
    "Mesin analisis sedang dimuat. Biasanya kurang dari setengah menit - "
    "setelah itu semua modul langsung siap dipakai."
)

GREETING_BENCHMARK_NAME = "Semua Outlet"
BTN_GANTI_DATA = "Ganti Data"
BTN_TUTUP_PANEL = "Tutup Panel"
PANEL_DATA_TITLE = "Data Ulasan"
PANEL_DATA_SUB = (
    "Pakai data contoh restoran atau unggah file ulasan milik Anda sendiri "
    "(format CSV, paling banyak 200 baris)."
)
PANEL_MODE_LABEL = "Sumber data:"
RESTO_SELECT_LABEL = "Pilih restoran:"
UPLOAD_LABEL = "Unggah file CSV ulasan:"

STATUS_SENTENCE = (
    "Skor Kesehatan Dapur restoran ini berstatus <b>{status}</b>. "
    "Perhatian utama: aspek <b>{aspek}</b> dengan skor kepuasan <b>{skor}</b>."
)
STATUS_SENTENCE_BENCHMARK = (
    "Patokan gabungan semua outlet berstatus <b>{status}</b>. "
    "Aspek terlemah secara keseluruhan: <b>{aspek}</b> dengan skor kepuasan <b>{skor}</b>."
)

FOOTER_LINE = (
    "<b>UlasRasa</b> &bull; Tugas Akhir AI Engineering Batch 13 &bull; "
    "Student ID: <b>REAENG13TQJLN</b> (Azura) &bull; "
    "Mesin: <b>IndoBERT ABSA + Rencana Aksi LLM</b>"
)

# ---------------------------------------------------------------- teks Ringkasan (kerangka Tahap 1, dipakai penuh Tahap 2)
KPI_KHS_LABEL = "Skor Kesehatan Dapur"
KPI_TOTAL_LABEL = "Total Ulasan Dianalisis"
KPI_NEG_LABEL = "Ulasan Negatif"
KPI_KRITIS_LABEL = "Aspek Paling Kritis"
HERO_TITLE = "Skor Kesehatan Dapur"
HERO_CTA = "Lihat Rencana Aksi"
CHART_ASPEK_TITLE = "Kepuasan per Aspek"
CHART_ASPEK_SUB = "Skor kepuasan pelanggan untuk lima aspek dapur. Garis putus-putus adalah batas kritis 70."
REL_KELUHAN_TITLE = "Keluhan Terbaru"
REL_KELUHAN_SUB = "Ulasan negatif paling akhir. Klik tombolnya untuk membuka rincian aspeknya."
