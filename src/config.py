"""
UlasRasa Configuration & Domain Constants
"""

from typing import Dict

# 5 Aspek Utama Analisis Ulasan Restoran / Dapur
ASPECTS = [
    "Rasa",         # Food Quality & Taste
    "Kebersihan",   # Hygiene & Sanitation
    "Pelayanan",    # Service & Speed
    "Harga",        # Value for Money
    "Suasana",      # Ambiance & Cleanliness of Dining Area
]

# Bobot Kitchen Health Score (Total = 1.0)
# Aspek Dapur Inti (Rasa & Kebersihan) mendapatkan prioritas tertinggi
ASPECT_WEIGHTS: Dict[str, float] = {
    "Rasa": 0.30,
    "Kebersihan": 0.25,
    "Pelayanan": 0.20,
    "Harga": 0.15,
    "Suasana": 0.10,
}

# Skala Kategori Health Score
HEALTH_THRESHOLDS = {
    "PRIMA": 85.0,     # >= 85: Dapur dalam kondisi prima
    "WASPADA": 70.0,   # 70 - 84.9: Butuh perhatian pada aspek tertentu
    "KRITIS": 0.0,     # < 70: Kondisi darurat dapur / komplain tinggi
}

# Label Sentimen
SENTIMENT_LABELS = ["Positif", "Netral", "Negatif"]

# Warna Sentimen untuk Visualisasi Plotly
SENTIMENT_COLORS = {
    "Positif": "#22c55e",  # Emerald Green
    "Netral": "#eab308",   # Amber
    "Negatif": "#ef4444",  # Red
}

# Stopwords Bahasa Indonesia untuk Text Mining
INDONESIAN_STOPWORDS = {
    "dan", "di", "ke", "dari", "ini", "itu", "yang", "untuk", "pada", "adalah",
    "dengan", "saya", "kami", "anda", "dia", "mereka", "juga", "karena", "tetapi",
    "sudah", "bisa", "akan", "ada", "tidak", "jadi", "hanya", "sangat", "lebih",
    "banget", "buat", "aja", "nya", "ya", "sih", "kok", "lah", "deh", "pun",
    "terus", "kalau", "kalo", "lagi", "sama", "udah", "pas", "bgt", "gak", "nggak"
}
