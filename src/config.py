"""
UlasRasa Configuration & Domain Constants
"""

from typing import Dict

# 5 Aspek Utama Analisis Ulasan Restoran / Dapur
ASPECTS = [
    "Rasa",         # Food Quality & Taste
    "Porsi",        # Portion Size & Quantity
    "Harga",        # Value for Money
    "Kemasan",      # Packaging & Delivery Integrity
    "Pelayanan",    # Service Speed & Staff Behavior
]

# Bobot Kitchen Health Score (Total = 1.0)
ASPECT_WEIGHTS: Dict[str, float] = {
    "Rasa": 0.35,
    "Porsi": 0.20,
    "Kemasan": 0.15,
    "Harga": 0.15,
    "Pelayanan": 0.15,
}

ASPECT_WEIGHTS_LOWER: Dict[str, float] = {
    "rasa": 0.35,
    "porsi": 0.20,
    "kemasan": 0.15,
    "harga": 0.15,
    "pelayanan": 0.15,
}

# Skala Kategori Health Score
HEALTH_THRESHOLDS = {
    "PRIMA": 80.0,     # >= 80: Dapur dalam kondisi prima
    "WASPADA": 65.0,   # 65 - 79.9: Butuh perhatian pada aspek tertentu
    "KRITIS": 0.0,     # < 65: Kondisi darurat dapur / komplain tinggi
}

# Palet Tema Hangat (Warm Off-White / Alabaster Cream)
THEME_PALETTE = {
    "bg_main": "#FAF9F5",        # Warm Off-White Alabaster
    "bg_card": "#FFFFFF",        # Soft White Card
    "bg_card_alt": "#F5F3ED",    # Subtle Warm Neutral
    "border": "#EAE6DE",         # Warm Stone Border
    "text_primary": "#1C1917",   # Warm Stone 900
    "text_muted": "#57534E",     # Warm Stone 600
    "accent_primary": "#C84B2F", # Terracotta Culinary Brick
    "accent_hover": "#B33E24",   # Deep Terracotta
    "accent_light": "#FDF2EE",   # Terracotta Soft Pastel
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
