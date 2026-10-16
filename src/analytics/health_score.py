"""
Kitchen Health Score Calculation & Radar Chart Generator
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any, Tuple

from src.config import ASPECTS, ASPECT_WEIGHTS, HEALTH_THRESHOLDS

def calculate_aspect_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghitung metrik sentimen dan skor per aspek (0-100%).
    Formula: Skor Aspek = ((Positif + 0.5 * Netral) / Total) * 100
    """
    if df.empty:
        # Fallback default empty
        return pd.DataFrame({
            "aspect": ASPECTS,
            "total_reviews": [0] * len(ASPECTS),
            "positif": [0] * len(ASPECTS),
            "netral": [0] * len(ASPECTS),
            "negatif": [0] * len(ASPECTS),
            "score": [0.0] * len(ASPECTS),
            "weight": [ASPECT_WEIGHTS.get(a, 0.2) for a in ASPECTS]
        })

    # Grouping by aspect and sentiment
    grouped = df.groupby(["aspect", "sentiment"]).size().unstack(fill_value=0)
    for col in ["Positif", "Netral", "Negatif"]:
        if col not in grouped.columns:
            grouped[col] = 0

    # Ensure all 5 aspects exist in table
    for asp in ASPECTS:
        if asp not in grouped.index:
            grouped.loc[asp] = 0

    grouped["total"] = grouped["Positif"] + grouped["Netral"] + grouped["Negatif"]
    
    # Skor per aspek (0 - 100%)
    # Hindari ZeroDivisionError dengan np.where
    scores = np.where(
        grouped["total"] > 0,
        ((grouped["Positif"] + 0.5 * grouped["Netral"]) / grouped["total"]) * 100.0,
        50.0 # Default baseline jika belum ada data
    )
    
    grouped["score"] = np.round(scores, 1)
    grouped["weight"] = [ASPECT_WEIGHTS.get(str(asp), 0.20) for asp in grouped.index]

    result_df = grouped.reset_index().rename(columns={"index": "aspect"})
    return result_df

def calculate_overall_health_score(aspect_df: pd.DataFrame) -> Tuple[float, str, str]:
    """
    Menghitung Overall Kitchen Health Score (0-100%) berbasis bobot prioritas F&B.
    Returns:
        score (float): 0 - 100%
        status (str): PRIMA / WASPADA / KRITIS
        color (str): Hex color code
    """
    if aspect_df.empty or "score" not in aspect_df.columns:
        return 0.0, "KRITIS", "#ef4444"

    # Merge weights if not present
    if "weight" not in aspect_df.columns:
        aspect_df["weight"] = aspect_df["aspect"].apply(lambda a: ASPECT_WEIGHTS.get(str(a), 0.2))

    total_weighted_score = (aspect_df["score"] * aspect_df["weight"]).sum()
    overall_score = round(float(total_weighted_score), 1)

    if overall_score >= HEALTH_THRESHOLDS["PRIMA"]:
        status = "PRIMA (Dapur Optimal)"
        color = "#22c55e"
    elif overall_score >= HEALTH_THRESHOLDS["WASPADA"]:
        status = "WASPADA (Perlu Pembenahan)"
        color = "#eab308"
    else:
        status = "KRITIS (Audit Segera!)"
        color = "#ef4444"

    return overall_score, status, color

def generate_radar_chart(aspect_df: pd.DataFrame) -> go.Figure:
    """
    Membuat visualisasi Spider/Radar Chart 5 Aspek menggunakan Plotly.
    """
    # Pastikan urutan aspek konsisten
    chart_df = aspect_df.set_index("aspect").reindex(ASPECTS).reset_index()
    categories = chart_df["aspect"].tolist()
    values = chart_df["score"].tolist()

    # Tutup lingkaran radar (circular loop)
    radar_categories = categories + [categories[0]]
    radar_values = values + [values[0]]

    fig = go.Figure()

    # Area Score Aktual
    fig.add_trace(go.Scatterpolar(
        r=radar_values,
        theta=radar_categories,
        fill="toself",
        name="Skor Aktual Dapur",
        line=dict(color="#3b82f6", width=3),
        fillcolor="rgba(59, 130, 246, 0.25)",
        marker=dict(size=7, color="#1d4ed8")
    ))

    # Garis Benchmark Standar Prima (85%)
    benchmark_values = [85.0] * len(radar_categories)
    fig.add_trace(go.Scatterpolar(
        r=benchmark_values,
        theta=radar_categories,
        mode="lines",
        name="Standar Prima (85%)",
        line=dict(color="#10b981", width=1.5, dash="dash"),
    ))

    # Garis Batas Kritis (70%)
    critical_values = [70.0] * len(radar_categories)
    fig.add_trace(go.Scatterpolar(
        r=critical_values,
        theta=radar_categories,
        mode="lines",
        name="Batas Kritis (70%)",
        line=dict(color="#ef4444", width=1.5, dash="dot"),
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[20, 40, 60, 80, 100],
                ticktext=["20%", "40%", "60%", "80%", "100%"],
                tickfont=dict(size=10, color="#64748b")
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#0f172a", family="Inter, sans-serif")
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=30, b=50),
        height=380
    )

    return fig

def get_critical_kitchen_alerts(df: pd.DataFrame, aspect_df: pd.DataFrame) -> list:
    """
    Mendeteksi peringatan darurat dapur (Critical Alerts) dari sentimen negatif.
    """
    alerts = []
    
    # Cek Aspek Kebersihan
    kebersihan_row = aspect_df[aspect_df["aspect"] == "Kebersihan"]
    if not kebersihan_row.empty:
        score = float(list(kebersihan_row["score"])[0])
        if score < 75.0:
            alerts.append({
                "level": "danger",
                "aspect": "Kebersihan",
                "title": "Peringatan Sanitasi & Higienitas Dapur!",
                "message": f"Skor kebersihan berada di angka {score}% (< 75%). Ulasan negatif mengindikasikan masalah sanitasi alat makan atau area dapur."
            })

    # Cek Aspek Rasa
    rasa_row = aspect_df[aspect_df["aspect"] == "Rasa"]
    if not rasa_row.empty:
        score = float(list(rasa_row["score"])[0])
        if score < 75.0:
            alerts.append({
                "level": "warning",
                "aspect": "Rasa",
                "title": "Konsistensi Rasa & Suhu Makanan Menurun",
                "message": f"Skor rasa berada di angka {score}%. Ditemukan keluhan mengenai rasa terlalu asin atau makanan disajikan dingin."
            })

    # Cek Aspek Pelayanan
    pelayanan_row = aspect_df[aspect_df["aspect"] == "Pelayanan"]
    if not pelayanan_row.empty:
        score = float(list(pelayanan_row["score"])[0])
        if score < 70.0:
            alerts.append({
                "level": "warning",
                "aspect": "Pelayanan",
                "title": "Bottleneck Waktu Penyajian (Kitchen Lead Time)",
                "message": f"Skor pelayanan {score}%. Keluhan durasi tunggu lama (>30-40 menit) mendominasi."
            })

    return alerts
