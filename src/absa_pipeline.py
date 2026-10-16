"""Pipeline inferensi ABSA (Aspect-Based Sentiment Analysis) untuk ulasan kuliner.
Mendukung 5 aspek: Rasa, Porsi, Harga, Kemasan, Pelayanan.
"""

import re
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
        "enak", "lezat", "sedap", "gurih", "mantap", "empuk", "crispy", "garing", "renyah",
        "juicy", "banyak", "melimpah", "jumbo", "kenyang", "puas", "murah",
        "terjangkau", "miring", "worth", "sebanding", "rapi", "aman", "segel",
        "cepat", "ramah", "bersahabat", "nagih", "kental", "pas", "seger", "juara",
        "gokil", "maknyus", "bersih"
    ],
    "negative": [
        "asin", "keasinan", "hambar", "alot", "amis", "dingin", "gosong", "enek",
        "pahit", "kemanisan", "ciut", "dikit", "sedikit", "kecil", "kurang", "imut",
        "mungil", "seuprit", "mahal", "kemahalan", "rugi", "tumpah", "bocor", "basah",
        "rembes", "penyok", "pecah", "jebol", "lama", "lambat", "salah", "kecewa",
        "judes", "jutek", "keteteran", "encer"
    ]
}

class ABSAPipeline:
    """Mesin inferensi klasifikasi aspek dan sentimen multi-aspek."""

    def __init__(self, model_checkpoint: str = None):
        self.model_checkpoint = model_checkpoint
        self.aspects = ["rasa", "porsi", "harga", "kemasan", "pelayanan"]
        self.weights = DEFAULT_WEIGHTS

    def analyze_single_review(self, raw_text: str) -> Dict[str, Any]:
        """Menganalisis teks ulasan tunggal ke dalam 5 aspek menggunakan analisis klausa lokal."""
        cleaned = clean_text(raw_text)
        tokens = cleaned.split()
        
        # Pisahkan klausa berdasarkan tanda baca dan konjungsi kontrastif
        clauses = re.split(r"[,;\.!?]|(?:\b(?:tetapi|tapi|namun|sedangkan|padahal|trs|lalu)\b)", cleaned)
        clauses = [c.strip() for c in clauses if c and c.strip()]
        
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
            
            # Cari klausa spesifik yang memuat kata kunci aspek ini
            target_clauses = [c for c in clauses if any(kw in c.split() or kw in c for kw in keywords)]
            eval_text = " ".join(target_clauses) if target_clauses else cleaned
            clause_tokens = eval_text.split()
            
            pos_score = 0
            neg_score = 0
            negation_words = {"tidak", "kurang", "bukan", "ga", "gak", "tanpa", "belum"}
            
            for i, word in enumerate(clause_tokens):
                prev_window = set(clause_tokens[max(0, i-3):i])
                is_negated = bool(prev_window.intersection(negation_words))
                
                if word in SENTIMENT_POLARITY["positive"]:
                    if is_negated:
                        neg_score += 1
                    else:
                        pos_score += 1
                elif word in SENTIMENT_POLARITY["negative"]:
                    if is_negated:
                        pos_score += 1
                    else:
                        neg_score += 1
                        
            # Cek pola frasa khusus F&B
            if "tidak antre lama" in eval_text or "tidak lama" in eval_text or "tidak antri" in eval_text:
                pos_score += 1
                neg_score = max(0, neg_score - 1)
                
            if neg_score > pos_score:
                sentiment = "negative"
                conf = min(0.95, 0.70 + 0.1 * neg_score)
            elif pos_score > neg_score:
                sentiment = "positive"
                conf = min(0.95, 0.70 + 0.1 * pos_score)
            else:
                sentiment = "neutral"
                conf = 0.65
                
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

    def evaluate_dataframe(self, df: pd.DataFrame, progress_callback=None) -> Dict[str, Any]:
        """
        Menghitung metrik kepuasan dan skor kesehatan dapur (Kitchen Health Score).
        Mendukung dataframe beranotasi lengkap maupun ulasan teks mentah ('review_text').
        Jika kolom aspek belum ada, pipeline otomatis melakukan inferensi on-the-fly.
        """
        eval_df = df.copy()
        
        # Cek apakah kolom 5 aspek sudah lengkap
        aspects_present = all(asp in eval_df.columns for asp in self.aspects)
        
        # Jika belum ada kolom aspek, lakukan auto-inferensi pada teks ulasan
        if not aspects_present and "review_text" in eval_df.columns:
            total_rows = len(eval_df)
            inferred_aspects = {asp: [] for asp in self.aspects}
            
            for i, text in enumerate(eval_df["review_text"]):
                res = self.analyze_single_review(str(text))
                for asp in self.aspects:
                    inferred_aspects[asp].append(res["aspects"][asp]["sentiment"])
                if progress_callback:
                    progress_callback((i + 1) / total_rows)
                    
            for asp in self.aspects:
                eval_df[asp] = inferred_aspects[asp]
                
        aspect_summary = {}
        total_reviews = len(eval_df)
        
        for aspect in self.aspects:
            if aspect not in eval_df.columns:
                series = pd.Series(["not_mentioned"] * total_reviews)
            else:
                series = eval_df[aspect].astype(str).str.lower()
                
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
            "aspect_breakdown": aspect_summary,
            "evaluated_df": eval_df
        }
