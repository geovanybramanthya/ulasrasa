"""
Sample Data Generator & Loader for UlasRasa
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

SAMPLE_REVIEWS_POOL = [
    # Rasa - Positif
    ("Rasa kuah rawonnya sangat gurih dan dagingnya empuk luar biasa!", "Rasa", "Positif", 5),
    ("Bumbu rendangnya meresap sempurna, sambalnya nendang pol.", "Rasa", "Positif", 5),
    ("Ayam gorengnya krispi di luar dan juicy di dalam, rasanya mantap.", "Rasa", "Positif", 5),
    ("Citarasa autentik khas nusantara, porsi pas dan sedap.", "Rasa", "Positif", 4),
    # Rasa - Netral
    ("Rasanya lumayan standar, bumbu kurang medok tapi masih oke dimakan.", "Rasa", "Netral", 3),
    ("Porsi banyak tapi rasanya agak hambar untuk lidah saya.", "Rasa", "Netral", 3),
    # Rasa - Negatif
    ("Sup buntutnya dingin saat dihidangkan, kuah berlemak dan keasinan.", "Rasa", "Negatif", 1),
    ("Nasi uduknya bau apek dan ayamnya masih agak mentah di bagian tulang.", "Rasa", "Negatif", 1),
    ("Sambal matahnya terlalu asam dan terasa minyak jelantah bekas.", "Rasa", "Negatif", 2),
    ("Soto daging terlalu asin, potongan daging banyak lemak liat.", "Rasa", "Negatif", 2),

    # Kebersihan - Positif
    ("Piring, sendok, dan meja makan sangat steril dan bersih berkilau.", "Kebersihan", "Positif", 5),
    ("Dapur terbuka terlihat sangat higienis, koki pakai sarung tangan dan hairnet.", "Kebersihan", "Positif", 5),
    ("Toilet harum dan lantai ruang makan selalu disapu berkala.", "Kebersihan", "Positif", 5),
    # Kebersihan - Netral
    ("Kebersihan standar, meja agak berminyak sedikit setelah dibersihkan.", "Kebersihan", "Netral", 3),
    # Kebersihan - Negatif
    ("Ditemukan rambut di dalam mangkuk mie kuah! Tolong tingkatkan sanitasi.", "Kebersihan", "Negatif", 1),
    ("Gelas minum ada noda lipstik bekas pengunjung sebelumnya, jorok sekali.", "Kebersihan", "Negatif", 1),
    ("Lantai dapur licin dan terlihat lalat berterbangan dekat display lauk.", "Kebersihan", "Negatif", 1),
    ("Alat makan bau amis sisa cucian sebelumnya.", "Kebersihan", "Negatif", 2),

    # Pelayanan - Positif
    ("Pelayanan ramah sekali, makanan datang kurang dari 10 menit.", "Pelayanan", "Positif", 5),
    ("Waitstaff sangat cekatan merefill es teh dan tanggap menjawab menu.", "Pelayanan", "Positif", 5),
    ("Kasir ramah dan penjelasan promo sangat jelas.", "Pelayanan", "Positif", 4),
    # Pelayanan - Netral
    ("Pelayanan cukup oke meski agak lambat karena resto sedang ramai.", "Pelayanan", "Netral", 3),
    # Pelayanan - Negatif
    ("Makanan keluar 45 menit padahal orderan sederhana, pelayan cuek.", "Pelayanan", "Negatif", 1),
    ("Pelayan salah mencatat pesanan sampai 2 kali dan tidak meminta maaf.", "Pelayanan", "Negatif", 2),
    ("Antrian pesanan tidak teratur, pesanan takeaway diprioritaskan melebihi dine in.", "Pelayanan", "Negatif", 2),

    # Harga - Positif
    ("Harga bersahabat untuk porsi makan siang yang kenyang, worth it!", "Harga", "Positif", 5),
    ("Paket combo sangat hemat dan kualitas bahan makanan premium.", "Harga", "Positif", 5),
    # Harga - Netral
    ("Harga sepadan dengan rasa, tidak terlalu murah tapi tidak kemahalan.", "Harga", "Netral", 3),
    # Harga - Negatif
    ("Porsi sangat sedikit untuk harga semahal itu, tidak sebanding kualitas.", "Harga", "Negatif", 2),
    ("Pajak dan service charge terlalu tinggi untuk resto kelas cepat saji.", "Harga", "Negatif", 2),

    # Suasana - Positif
    ("Interior estetik, pencahayaan hangat dan musik latar tenang nyaman.", "Suasana", "Positif", 5),
    ("AC sejuk dan tempat duduk sofa nyaman untuk makan bersama keluarga.", "Suasana", "Positif", 5),
    # Suasana - Netral
    ("Suasana biasa saja khas warung tenda modern, agak sempit.", "Suasana", "Netral", 3),
    # Suasana - Negatif
    ("Musik terlalu keras memekakkan telinga, tidak cocok untuk mengobrol santai.", "Suasana", "Negatif", 2),
    ("Udara ruangan panas pengap karena exhaust fan dapur sepertinya mati.", "Suasana", "Negatif", 2),
]

def generate_sample_reviews(n: int = 120, output_path: str = "data/sample_reviews.csv") -> pd.DataFrame:
    """Menghasilkan dataset simulasi ulasan restoran dengan distribusi tanggal realistis."""
    np.random.seed(42)
    rows = []
    base_date = datetime.now() - timedelta(days=60)
    
    names = [
        "Andi Pratama", "Siti Nurhaliza", "Budi Santoso", "Dewi Lestari",
        "Rizky Ramadhan", "Putri Handayani", "Eko Prasetyo", "Maya Safitri",
        "Bayu Wicaksono", "Agus Hermawan", "Rina Wulandari", "Farhan Gunawan"
    ]
    channels = ["Dine-in", "Online Delivery", "Takeaway"]

    for i in range(n):
        idx = np.random.randint(0, len(SAMPLE_REVIEWS_POOL))
        text, aspect, sentiment, rating = SAMPLE_REVIEWS_POOL[idx]
        
        # Simulasi sedikit variasi rating
        noise = np.random.choice([-1, 0, 1], p=[0.15, 0.7, 0.15])
        adj_rating = int(np.clip(rating + noise, 1, 5))
        
        review_date = base_date + timedelta(
            days=int(np.random.uniform(0, 60)),
            hours=int(np.random.uniform(10, 22)),
            minutes=int(np.random.uniform(0, 59))
        )
        
        rows.append({
            "review_id": f"REV-{1000 + i}",
            "date": review_date.strftime("%Y-%m-%d %H:%M"),
            "customer_name": np.random.choice(names),
            "review_text": text,
            "aspect": aspect,
            "sentiment": sentiment,
            "rating": adj_rating,
            "order_channel": np.random.choice(channels, p=[0.55, 0.35, 0.10])
        })
        
    df = pd.DataFrame(rows)
    df = df.sort_values(by="date", ascending=False).reset_index(drop=True)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    return df

def load_reviews_dataset(file_path: str = "data/sample_reviews.csv") -> pd.DataFrame:
    """Memuat dataset ulasan restoran dari CSV atau membuat baru jika belum tersedia."""
    if not os.path.exists(file_path):
        return generate_sample_reviews(output_path=file_path)
    df = pd.read_csv(file_path)
    # Pastikan format datetime
    df["date"] = pd.to_datetime(df["date"])
    return df
