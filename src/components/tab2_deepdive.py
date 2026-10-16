"""
Tab 2 Component: Deep-Dive Aspek & Sentimen
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import ASPECTS, SENTIMENT_LABELS, SENTIMENT_COLORS
from src.analytics.text_mining import extract_top_complaints_ngrams, generate_complaint_chart

def render_tab2(df: pd.DataFrame):
    """Merender Tab 2: Deep-Dive Aspek, Distribusi Sentimen & Analisis N-Gram Keluhan."""
    st.markdown("### 🔍 Deep-Dive Aspek & Sentimen Pelanggan")
    st.caption("Eksplorasi mendalam sentimen ulasan dan identifikasi akar masalah (root cause) keluhan.")

    if df.empty:
        st.info("Belum ada data ulasan untuk dianalisis.")
        return

    # 1. Filter Lokal di Tab 2
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        aspect_choices = ["Semua Aspek"] + ASPECTS
        selected_aspect = st.selectbox("Filter Dimensi Aspek:", aspect_choices, index=0)
    with f_col2:
        sentiment_choices = ["Semua Sentimen"] + SENTIMENT_LABELS
        selected_sentiment = st.selectbox("Filter Polaritas Sentimen:", sentiment_choices, index=0)
    with f_col3:
        ngram_size = st.radio("Tipe N-Gram Keluhan:", [1, 2, 3], index=1, horizontal=True, format_func=lambda x: f"{x}-gram")

    # Filter DataFrame
    filtered_df = df.copy()
    if selected_aspect != "Semua Aspek":
        filtered_df = filtered_df[filtered_df["aspect"] == selected_aspect]
    if selected_sentiment != "Semua Sentimen":
        filtered_df = filtered_df[filtered_df["sentiment"] == selected_sentiment]

    st.markdown("---")

    # 2. Charts Row: Distribusi Sentimen + N-Gram Bar Chart
    col_sentiment_bar, col_ngram = st.columns([1, 1])

    with col_sentiment_bar:
        st.markdown("#### 📊 Distribusi Sentimen per Aspek")
        # Agregasi data untuk stacked bar chart
        dist_df = df.groupby(["aspect", "sentiment"]).size().reset_index().rename(columns={0: "count"})
        
        fig_dist = px.bar(
            dist_df,
            x="aspect",
            y="count",
            color="sentiment",
            color_discrete_map=SENTIMENT_COLORS,
            barmode="stack",
            labels={"aspect": "Aspek", "count": "Jumlah Ulasan", "sentiment": "Sentimen"},
            height=340
        )
        fig_dist.update_layout(
            margin=dict(l=20, r=20, t=30, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_ngram:
        ngram_title = f"Top Keluhan {selected_aspect} ({ngram_size}-gram)"
        st.markdown(f"#### 🏷️ {ngram_title}")
        ngrams_data = extract_top_complaints_ngrams(
            df=df,
            aspect=selected_aspect if selected_aspect != "Semua Aspek" else None,
            ngram_size=ngram_size,
            top_k=8
        )
        fig_ngram = generate_complaint_chart(ngrams_data, title="")
        st.plotly_chart(fig_ngram, use_container_width=True)

    # 3. Data Table Ulasan yang Difilter
    st.markdown("#### 📝 Data Ulasan Pelanggan")
    search_query = st.text_input("Cari ulasan berdasarkan kata kunci:", placeholder="Contoh: asin, piring, pelayan, lama...")
    
    table_df = filtered_df
    if search_query:
        mask = [search_query.lower() in str(t).lower() for t in table_df["review_text"]]
        table_df = table_df[mask]

    st.dataframe(
        table_df[["date", "customer_name", "aspect", "sentiment", "rating", "order_channel", "review_text"]],
        column_config={
            "date": st.column_config.DatetimeColumn("Waktu", format="YYYY-MM-DD HH:mm"),
            "customer_name": "Pelanggan",
            "aspect": "Aspek",
            "sentiment": "Sentimen",
            "rating": st.column_config.NumberColumn("Rating", format="%d ⭐"),
            "order_channel": "Channel",
            "review_text": st.column_config.TextColumn("Ulasan", width="large")
        },
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"Menampilkan {len(table_df)} ulasan dari total {len(df)} ulasan.")
