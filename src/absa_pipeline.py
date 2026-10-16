"""Pipeline inferensi ABSA (Aspect-Based Sentiment Analysis) untuk ulasan kuliner.
Mendukung 5 aspek: Rasa, Porsi, Harga, Kemasan, Pelayanan.
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd
from .preprocessing import clean_text, ASPECT_KEYWORDS

DEFAULT_WEIGHTS = {
    "rasa": 0.35,
    "porsi": 0.20,
    "kemasan": 0.15,
    "harga": 0.15,
    "pelayanan": 0.15,
}

SENTIMENT_POLARITY = {
    "positive": [
        "enak", "lezat", "sedap", "gurih", "mantap", "empuk", "crispy", "garing",
        "juicy", "banyak", "melimpah", "jumbo", "kenyang", "puas", "murah",
        "terjangkau", "miring", "worth", "sebanding", "rapi", "aman", "segel",
        "cepat", "ramah", "bersahabat", "nagih", "kental", "pas", "seger", "juara"
    ],
    "negative": [
        "asin", "keasinan", "hambar", "alot", "amis", "dingin", "gosong", "enek",
        "pahit", "kemanisan", "ciut", "dikit", "sedikit", "kecil", "kurang", "imut",
        "mahal", "kemahalan", "rugi", "tumpah", "bocor", "basah", "rembes", "penyok",
        "pecah", "jebol", "lama", "lambat", "salah", "kecewa", "judes", "keteteran", "encer"
    ]
}

class ABSAPipeline:
    """Mesin inferensi klasifikasi aspek dan sentimen multi-aspek."""

    def __init__(self, model_checkpoint: str = None):
        self.model_checkpoint = model_checkpoint
        self.aspects = ["rasa", "porsi", "harga", "kemasan", "pelayanan"]
        self.weights = DEFAULT_WEIGHTS

    def analyze_single_review(self, raw_text: str) -> Dict[str, Any]:
        """Menganalisis teks ulasan tunggal ke dalam 5 aspek."""
        cleaned = clean_text(raw_text)
        tokens = cleaned.split()
        
        results = {}
        for aspect in self.aspects:
            keywords = ASPECT_KEYWORDS[aspect]
            # Cek apakah aspek terdeteksi dalam teks
            aspect_detected = any(kw in tokens or kw in cleaned for kw in keywords)
            
            if not aspect_detected:
                results[aspect] = {
                    "mentioned": False,
                    "sentiment": "not_mentioned",
                    "confidence": 0.0
                }
                continue
            
            # Hitung polaritas sentimen berbasis konteks leksikal
            pos_matches = sum(1 for p in SENTIMENT_POLARITY["positive"] if p in cleaned)
            neg_matches = sum(1 for n in SENTIMENT_POLARITY["negative"] if n in cleaned)
            
            # Deteksi negasi sederhana
            has_negation = any(neg in tokens for neg in ["tidak", "kurang", "bukan", "ga", "gak"])
            
            if neg_matches > pos_matches:
                sentiment = "negative"
                conf = min(0.95, 0.65 + 0.1 * neg_matches)
            elif pos_matches > neg_matches:
                if has_negation and aspect in ["rasa", "pelayanan", "harga"]:
                    sentiment = "negative"
                    conf = 0.75
                else:
                    sentiment = "positive"
                    conf = min(0.95, 0.65 + 0.1 * pos_matches)
            else:
                sentiment = "neutral"
                conf = 0.60
                
            results[aspect] = {
                "mentioned": True,
                "sentiment": sentiment,
                "confidence": float(conf)
            }
            
        return {
            "original_text": raw_text,
            "cleaned_text": cleaned,
            "aspects": results
        }

    def evaluate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Menghitung metrik kepuasan dan skor kesehatan dapur (Kitchen Health Score)."""
        aspect_summary = {}
        total_reviews = len(df)
        
        for aspect in self.aspects:
            if aspect not in df.columns:
                continue
            series = df[aspect].astype(str).str.lower()
            pos = int((series == "positive").sum())
            neu = int((series == "neutral").sum())
            neg = int((series == "negative").sum())
            total_mentioned = pos + neu + neg
            
            # Satisfaction rate per aspect: (pos + 0.5 * neu) / total_mentioned
            if total_mentioned > 0:
                score = (pos + (0.5 * neu)) / total_mentioned * 100.0
            else:
                score = 100.0
                
            aspect_summary[aspect] = {
                "positive": pos,
                "neutral": neu,
                "negative": neg,
                "total_mentioned": total_mentioned,
                "satisfaction_score": round(float(score), 2),
                "negative_rate": round(float(neg / total_mentioned * 100.0), 2) if total_mentioned > 0 else 0.0
            }
            
        # Kitchen Health Score: Weighted sum of aspect scores
        khs = 0.0
        for aspect, weight in self.weights.items():
            aspect_score = aspect_summary.get(aspect, {}).get("satisfaction_score", 100.0)
            khs += weight * aspect_score
            
        return {
            "total_reviews": total_reviews,
            "kitchen_health_score": round(float(khs), 2),
            "aspect_breakdown": aspect_summary
        }
