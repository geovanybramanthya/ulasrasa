"""
Tab 1 Component: Ringkasan Eksekutif & Kitchen Health Score
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

from src.analytics.health_score import (
    calculate_aspect_metrics,
    calculate_overall_health_score,
    generate_radar_chart,
    get_critical_kitchen_alerts
)

def render_tab1(df: pd.DataFrame):
    """Merender Tab 1: Ringkasan Eksekutif & Spider Chart Health Score."""
    st.markdown("### 📊 Ringkasan Eksekutif & Health Score Dapur")
    st.caption("Monitoring performa operasional 5 dimensi kuliner secara real-time.")

    # Kalkulasi Metrik
    aspect_df = calculate_aspect_metrics(df)
    overall_score, status, color = calculate_overall_health_score(aspect_df)
    alerts = get_critical_kitchen_alerts(df, aspect_df)

    # 1. Top KPI Metrics Row
    total_reviews = len(df)
    pos_reviews = len(df[df["sentiment"] == "Positif"])
    pos_ratio = round((pos_reviews / total_reviews * 100), 1) if total_reviews > 0 else 0.0
    
    # Aspek terendah
    min_row = aspect_df.sort_values(by="score").iloc[0] if not aspect_df.empty else None
    lowest_aspect = f"{min_row['aspect']} ({min_row['score']}%)" if min_row is not None else "-"

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(
            label="Overall Health Score",
            value=f"{overall_score}%",
            delta="Optimal" if overall_score >= 85 else ("Waspada" if overall_score >= 70 else "Kritis"),
            delta_color="normal" if overall_score >= 70 else "inverse"
        )
    with kpi2:
        st.metric(label="Total Ulasan Masuk", value=f"{total_reviews:,}")
    with kpi3:
        st.metric(label="Kepuasan Pelanggan", value=f"{pos_ratio}%", delta=f"{pos_reviews} Positif")
    with kpi4:
        st.metric(label="Aspek Terlemah", value=lowest_aspect)

    st.markdown("---")

    # 2. Critical Alert Banner
    if alerts:
        for alert in alerts:
            if alert["level"] == "danger":
                st.error(f"🚨 **{alert['title']}** — {alert['message']}")
            else:
                st.warning(f"⚠️ **{alert['title']}** — {alert['message']}")

    # 3. Main Visualization: Spider Chart + Aspect Score Cards
    col_chart, col_breakdown = st.columns([3, 2])

    with col_chart:
        st.markdown("#### 🕸️ Spider Chart: Performa 5 Dimensi Dapur")
        radar_fig = generate_radar_chart(aspect_df)
        st.plotly_chart(radar_fig, use_container_width=True)

    with col_breakdown:
        st.markdown("#### 🎯 Skor Dimensi & Target Operasional")
        for record in aspect_df.to_dict(orient="records"):
            asp_name = str(record["aspect"])
            asp_score = float(record["score"])
            asp_weight = int(float(record.get("weight", 0.2)) * 100)
            
            # Label & Progress Bar
            st.write(f"**{asp_name}** (Bobot {asp_weight}%): `{asp_score}%`")
            st.progress(min(max(int(asp_score), 0), 100) / 100)

    # 4. Rekomendasi Eksekutif
    with st.expander("💡 Rekomendasi Tindakan Strategis untuk Manajemen", expanded=True):
        st.markdown(f"""
        - **Status Saat Ini:** `{status}` dengan indeks kesehatan dapur **{overall_score}%**.
        - **Prioritas Intervensi:** Fokus pembenahan pada aspek **{lowest_aspect}** guna mencegah churn pelanggan.
        - **Action Next Step:** Buka tab **AI Kitchen Action Checklist** untuk melihat instruksi delegasi SOP bagi koki dan staf lantai.
        """)
