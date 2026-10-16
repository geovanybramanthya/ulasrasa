"""
Text Mining & N-Gram Complaint Extractor for UlasRasa
"""

import re
from collections import Counter
from typing import List, Tuple, Dict, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import INDONESIAN_STOPWORDS

def clean_text_indonesian(text: str) -> List[str]:
    """Membersihkan teks ulasan bahasa Indonesia dan mengembalikan list token bersih."""
    if not isinstance(text, str):
        return []
    
    # Case folding & regex sanitization
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\d+", "", text)
    
    tokens = text.split()
    # Filter stopwords & kata terlalu pendek (< 3 karakter)
    filtered = [w for w in tokens if w not in INDONESIAN_STOPWORDS and len(w) >= 3]
    return filtered

def generate_ngrams(tokens: List[str], n: int = 2) -> List[str]:
    """Menghasilkan sequence N-gram dari kumpulan token."""
    if len(tokens) < n:
        return []
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

def extract_top_complaints_ngrams(
    df: pd.DataFrame, 
    aspect: Optional[str] = None, 
    ngram_size: int = 2, 
    top_k: int = 10
) -> List[Tuple[str, int]]:
    """
    Mengekstrak N-gram paling sering muncul dari ulasan bersentimen Negatif.
    Bisa difilter berdasarkan aspek spesifik.
    """
    neg_df = df[df["sentiment"] == "Negatif"]
    if aspect and aspect != "Semua Aspek":
        neg_df = neg_df[neg_df["aspect"] == aspect]
        
    if len(neg_df) == 0:
        return []

    all_ngrams = []
    for text in neg_df["review_text"]:
        tokens = clean_text_indonesian(text)
        if ngram_size == 1:
            all_ngrams.extend(tokens)
        else:
            all_ngrams.extend(generate_ngrams(tokens, n=ngram_size))

    counter = Counter(all_ngrams)
    return counter.most_common(top_k)

def generate_complaint_chart(ngram_data: List[Tuple[str, int]], title: str = "Top 10 Keluhan Pelanggan") -> go.Figure:
    """Membuat visualisasi horizontal bar chart untuk N-Gram keluhan."""
    if not ngram_data:
        # Dummy figure jika kosong
        fig = go.Figure()
        fig.add_annotation(
            text="Tidak ada data keluhan yang cocok dengan filter saat ini.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#94a3b8")
        )
        fig.update_layout(height=320)
        return fig

    phrases = [item[0] for item in ngram_data][::-1]
    counts = [item[1] for item in ngram_data][::-1]

    fig = go.Figure(go.Bar(
        x=counts,
        y=phrases,
        orientation="h",
        marker=dict(
            color=counts,
            colorscale="Reds",
            line=dict(color="#b91c1c", width=1)
        ),
        text=counts,
        textposition="outside"
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#1e293b")),
        xaxis=dict(title="Frekuensi Kemunculan", tickformat="d"),
        yaxis=dict(title="", tickfont=dict(size=11)),
        margin=dict(l=120, r=40, t=40, b=40),
        height=340
    )
    return fig
