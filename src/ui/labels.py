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
BTN_GANTI_AKUN = "Ganti Akun"
DEMO_CHIP = "Akun Demo"
PRESET_CAPTION = (
    "Menampilkan data contoh untuk akun yang sedang aktif. "
    "Untuk berpindah restoran, gunakan tombol Ganti Akun di kanan atas."
)

# ---------------------------------------------------------------- teks Landing (Adendum 2026-10-23)
LANDING_TITLE = "Pilih restoran untuk masuk ke dashboard"
LANDING_SUB = (
    "Setiap akun demo menampilkan data ulasan satu restoran, lengkap dengan "
    "Skor Kesehatan Dapur dan rencana aksi perbaikannya."
)
LANDING_ACCOUNTS_LABEL = "Pilih Akun Demo"
LANDING_REVIEWS_LINE = "{n} ulasan contoh"
LANDING_KHS_LABEL = "Skor Kesehatan Dapur"
LANDING_ENTER_BTN = "Masuk Dashboard"
LANDING_VISUAL_TITLE = "UlasRasa untuk UMKM Kuliner"
LANDING_VALUE = (
    "UlasRasa membantu pemilik usaha kuliner memahami keluhan pelanggan dari "
    "ulasan dan mengubahnya menjadi langkah perbaikan dapur yang jelas."
)
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
    "Student ID: <b>REAENG13TQJLN</b> (Geovany Bramanthya Samuel Sihombing) &bull; "
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

# ---------------------------------------------------------------- teks Rincian Aspek (Tahap 3)
RINCIAN_PILL_LABEL = "Pilih aspek yang mau dibedah:"
RINCIAN_STAT_MENTIONED = "Total Disebut"
RINCIAN_STAT_POS = "Positif"
RINCIAN_STAT_NEU = "Netral"
RINCIAN_STAT_NEG = "Negatif"
RINCIAN_DONUT_TITLE = "Distribusi Sentimen Aspek Ini"
RINCIAN_DONUT_SUB = "Perbandingan ulasan positif, netral, dan negatif untuk aspek yang dipilih."
RINCIAN_KOMP_TITLE = "Komposisi Sentimen Semua Aspek"
RINCIAN_KOMP_SUB = "Jumlah ulasan positif, netral, dan negatif pada kelima aspek."
RINCIAN_KATA_TITLE = "Kata yang Sering Muncul di Keluhan"
RINCIAN_KATA_SUB = "Kata yang paling sering muncul pada ulasan negatif aspek ini."
RINCIAN_KATA_EMPTY = "Belum ada ulasan negatif pada aspek ini. Kabar baik untuk dapur Anda."
RINCIAN_CONTOH_POS = "Contoh Ulasan Positif"
RINCIAN_CONTOH_NEG = "Contoh Ulasan Negatif"
RINCIAN_CONTOH_EMPTY = "Belum ada contoh pada data aktif."
RINCIAN_TABEL_TITLE = "Semua Ulasan"
RINCIAN_TABEL_SUB = "Seluruh ulasan pada data aktif beserta label sentimen tiap aspeknya."
RINCIAN_FILTER_POL_LABEL = "Saring polaritas:"
RINCIAN_FILTER_MENU_LABEL = "Saring menu:"
RINCIAN_FILTER_OPTIONS = ["Semua Sentimen", "Hanya Negatif (Komplain)", "Hanya Positif", "Hanya Netral"]
RINCIAN_MENU_ALL = "Semua Menu"
RINCIAN_COUNT_LINE = "Menampilkan {n} ulasan yang cocok:"
RINCIAN_EMPTY = "Tidak ada ulasan yang memenuhi kriteria saringan."

# ---------------------------------------------------------------- teks Rencana Aksi (Tahap 4)
RENCANA_RCA_TITLE = "Akar Masalah"
RENCANA_RCA_SUB = "Ringkasan penyebab keluhan pelanggan terjadi, disusun dari data ulasan restoran ini."
RENCANA_PROGRESS_TITLE = "Kemajuan Daftar Aksi"
RENCANA_PROGRESS_LINE = "{selesai} dari {total} aksi selesai ({persen}%)"
RENCANA_LIST_TITLE = "Daftar Aksi Dapur"
RENCANA_LIST_SUB = "Centang setiap tindakan yang sudah dikerjakan dan diperiksa oleh penanggung jawab dapur."
RENCANA_FOKUS_CHIP = "Fokus perbaikan: {aspek}"
RENCANA_CUSTOM_TITLE = "Tindakan Kustom"
RENCANA_CUSTOM_SUB = "Tindakan tambahan yang Anda tulis sendiri untuk dapur Anda."
RENCANA_ADD_EXPANDER = "Tambah Tindakan Kustom"
RENCANA_ADD_LABEL = "Tindakan baru:"
RENCANA_ADD_PLACEHOLDER = "Contoh: Periksa segel kemasan sebelum makanan diserahkan ke kurir..."
RENCANA_ADD_BTN = "Tambahkan ke Daftar Aksi"
RENCANA_ADD_OK = "Tindakan kustom berhasil ditambahkan."
RENCANA_RESET_BTN = "Atur Ulang Centang"
RENCANA_SOP_TITLE = "Rekomendasi SOP Dapur"
RENCANA_SOP_SUB = "Prosedur standar yang disarankan untuk ditempel di area kerja dapur."
RENCANA_DL_TITLE = "Unduh Daftar Aksi"
RENCANA_DL_SUB = "Simpan daftar aksi untuk dicetak dan ditempel di dapur, atau dibagikan ke tim."
RENCANA_DL_PDF = "Unduh PDF"
RENCANA_DL_TXT = "Unduh Teks (.txt)"
RENCANA_DL_CSV = "Unduh CSV"

# ---------------------------------------------------------------- teks Coba Ulasan (Tahap 5)
COBA_INPUT_TITLE = "Tulis Ulasan Pelanggan"
COBA_INPUT_SUB = "Tempel satu ulasan pelanggan, lalu jalankan analisis untuk melihat nilai tiap aspeknya."
COBA_PRESET_TITLE = "Atau coba contoh ulasan:"
COBA_TEXT_LABEL = "Teks ulasan:"
COBA_ANALYZE_BTN = "Analisis Ulasan"
COBA_RESULT_TITLE = "Hasil Analisis"
COBA_RESULT_SUB = "Nilai sentimen per aspek dari mesin yang sedang aktif: {engine}."
COBA_EMPTY_TITLE = "Belum ada hasil"
COBA_EMPTY_BODY = "Hasil analisis akan tampil di sini: aspek apa saja yang disebut pelanggan, nilainya positif atau negatif, dan seberapa yakin mesinnya."
COBA_CLEAN_TITLE = "Teks Setelah Dibersihkan"
COBA_RAW_TITLE = "Teks Asli"
COBA_NOT_MENTIONED = "Tidak disebut: {daftar}"
COBA_FOLLOW_NEG_TITLE = "Saran Tindak Lanjut"
COBA_FOLLOW_NEG_BODY = "Ada keluhan pada aspek <b>{aspek}</b>. Periksa kembali cara kerja dapur untuk aspek tersebut, lalu cocokkan dengan daftar aksi di modul Rencana Aksi."
COBA_FOLLOW_OK_TITLE = "Kondisi Dapur Baik"
COBA_FOLLOW_OK_BODY = "Tidak ada keluhan pada ulasan ini. Pertahankan cara kerja dapur yang sekarang."



