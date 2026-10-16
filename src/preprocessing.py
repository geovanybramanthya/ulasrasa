"""Modul pembersihan dan prapemrosesan teks ulasan kuliner Indonesia."""

import re
import unicodedata

SLANG_DICTIONARY = {
    "ga": "tidak",
    "gak": "tidak",
    "nggak": "tidak",
    "ngga": "tidak",
    "tdk": "tidak",
    "tak": "tidak",
    "bgt": "banget",
    "bgtlah": "banget",
    "pol": "sekali",
    "beneran": "sungguh",
    "bener2": "benar-benar",
    "bener": "benar",
    "dikit": "sedikit",
    "keliatan": "terlihat",
    "ngerasa": "merasa",
    "kerasa": "terasa",
    "ngasal": "asal",
    "bkn": "bukan",
    "tp": "tapi",
    "sdh": "sudah",
    "udh": "sudah",
    "udah": "sudah",
    "blm": "belum",
    "belom": "belum",
    "dr": "dari",
    "dgn": "dengan",
    "dg": "dengan",
    "klo": "kalau",
    "kalo": "kalau",
    "krn": "karena",
    "gmn": "bagaimana",
    "kek": "seperti",
    "kyk": "seperti",
    "msh": "masih",
    "jg": "juga",
    "jga": "juga",
    "sy": "saya",
    "gw": "saya",
    "gue": "saya",
    "lu": "kamu",
    "lo": "kamu",
    "bgtu": "begitu",
    "cuma": "hanya",
    "cuman": "hanya",
    "cm": "hanya",
    "sampe": "sampai",
    "pas": "saat",
    "maknyus": "lezat",
    "mantul": "mantap",
    "mantab": "mantap",
    "worthit": "sebanding",
    "worth": "sebanding",
    "ciut": "kecil",
    "porsi kuli": "porsi sangat banyak",
}

ASPECT_KEYWORDS = {
    "rasa": [
        "rasa", "asin", "hambar", "manis", "pedas", "gurih", "alot", "empuk",
        "enak", "sedap", "lezat", "bumbu", "kematangan", "gosong", "amis", "enek",
        "keasinan", "kemanisan", "dingin", "pahit", "asam", "seger", "crispy", "garing"
    ],
    "porsi": [
        "porsi", "banyak", "dikit", "sedikit", "kenyang", "kurang", "ciut",
        "melimpah", "jumbo", "imut", "kecil", "besar", "tebal", "tipis", "ruah"
    ],
    "harga": [
        "harga", "mahal", "murah", "kemahalan", "terjangkau", "worth", "sebanding",
        "rupiah", "ribu", "rb", "miring", "kantong"
    ],
    "kemasan": [
        "kemasan", "bungkus", "packaging", "tumpah", "bocor", "segel", "rapi",
        "plastik", "box", "kotak", "mangkok", "mika", "basah", "rembes", "penyok"
    ],
    "pelayanan": [
        "pelayanan", "layanan", "lama", "cepat", "lambat", "driver", "tunggu",
        "nunggu", "antre", "antrian", "salah", "pesanan", "ramah", "judes",
        "kasir", "koki", "sendok", "garpu", "alat makan"
    ]
}

def remove_emojis(text: str) -> str:
    """Menghapus karakter non-ASCII dan emoji."""
    cleaned = re.sub(r"[^\x00-\x7F]+", " ", text)
    return cleaned

def clean_text(text: str) -> str:
    """Pipeline pembersihan teks dasar bahasa Indonesia."""
    if not isinstance(text, str):
        return ""
    
    # 1. Normalisasi unicode dan lowercasing
    text = unicodedata.normalize("NFKD", text).casefold()
    
    # 2. Hapus URL atau mention
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    
    # 3. Hapus emoji dan simbol aneh
    text = remove_emojis(text)
    
    # 4. Hapus tanda baca berlebih tapi simpan spasi
    text = re.sub(r"[^\w\s]", " ", text)
    
    # 5. Normalisasi slang words
    tokens = text.split()
    normalized_tokens = [SLANG_DICTIONARY.get(w, w) for w in tokens]
    
    # 6. Gabungkan dan buang spasi ganda
    cleaned = " ".join(normalized_tokens)
    return cleaned
