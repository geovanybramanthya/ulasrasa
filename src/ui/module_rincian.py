"""Modul 2: Deep-Dive Aspek & Sentimen.

Tahap 0: blok modul dipindah VERBATIM dari app.py lama.
"""

from collections import Counter

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from src.preprocessing import clean_text


def render(ctx, pipeline, action_engine):
    filtered_df = ctx["filtered_df"]
    breakdown = ctx["breakdown"]

    st.markdown("### Deep-Dive Analisis Sentimen & Keluhan Pelanggan")
    st.caption("Bedah distribusi sentimen lintas aspek, frekuensi kata kunci komplain, dan kutipan ulasan langsung.")

    # Tahap 2: aspek awal mengikuti rincian_aspect (diisi klik RelKeluhan
    # di Modul Ringkasan). Hanya nilai awal selectbox; logika modul utuh.
    _rincian_opts = ["Rasa", "Porsi", "Harga", "Kemasan", "Pelayanan"]
    _rincian_awal = str(st.session_state.get("rincian_aspect", "rasa")).capitalize()
    _rincian_idx = _rincian_opts.index(_rincian_awal) if _rincian_awal in _rincian_opts else 0
    col_selector, col_empty = st.columns([1, 2])
    with col_selector:
        selected_aspect = st.selectbox(
            "Pilih Aspek Diagnostik:",
            _rincian_opts,
            index=_rincian_idx
        ).lower()

    aspect_data = breakdown.get(selected_aspect, {})

    # Metrik Baris
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Total Disebut", f"{aspect_data.get('total_mentioned', 0)} kali")
    m_col2.metric("Ulasan Positif", f"{aspect_data.get('positive', 0)} ({aspect_data.get('positive', 0)/(aspect_data.get('total_mentioned', 1) or 1)*100:.0f}%)")
    m_col3.metric("Ulasan Netral", f"{aspect_data.get('neutral', 0)}")
    m_col4.metric("Ulasan Komplain (Negatif)", f"{aspect_data.get('negative', 0)} ({aspect_data.get('negative_rate', 0.0):.0f}%)")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 2 Grafik: Distribusi Sentimen & N-Gram Komplain
    col_chart1, col_chart2 = st.columns([1.2, 1])

    with col_chart1:
        st.markdown("#### Komposisi Sentimen Lintas 5 Aspek")
        dist_records = []
        for a_key, a_val in breakdown.items():
            dist_records.append({"Aspek": a_key.capitalize(), "Sentimen": "Positif", "Jumlah": a_val["positive"]})
            dist_records.append({"Aspek": a_key.capitalize(), "Sentimen": "Netral", "Jumlah": a_val["neutral"]})
            dist_records.append({"Aspek": a_key.capitalize(), "Sentimen": "Negatif", "Jumlah": a_val["negative"]})

        dist_df = pd.DataFrame(dist_records)
        fig_dist = px.bar(
            dist_df,
            x="Aspek",
            y="Jumlah",
            color="Sentimen",
            color_discrete_map={"Positif": "#15803D", "Netral": "#D97706", "Negatif": "#B91C1C"},
            barmode="stack",
            height=300
        )
        fig_dist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="#EAE6DE", title=""),
            yaxis=dict(gridcolor="#EAE6DE", title="Jumlah Ulasan"),
            margin=dict(l=20, r=20, t=10, b=20),
            legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center")
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_chart2:
        st.markdown(f"#### Top Kata Kunci Komplain ({selected_aspect.capitalize()})")
        if selected_aspect in filtered_df.columns:
            neg_texts = filtered_df[filtered_df[selected_aspect] == "negative"]["review_text"].tolist()
            words = []
            stop_set = {
                "yang", "dan", "di", "ini", "itu", "ke", "dari", "untuk", "pada", "adalah",
                "dengan", "saya", "kami", "anda", "dia", "mereka", "juga", "karena", "tetapi",
                "sudah", "bisa", "akan", "ada", "tidak", "jadi", "hanya", "sangat", "lebih",
                "banget", "buat", "aja", "nya", "ya", "sih", "kok", "lah", "deh", "pun", "bgt", "ga", "gak"
            }
            for t in neg_texts:
                cleaned_t = clean_text(str(t))
                toks = [w for w in cleaned_t.split() if len(w) >= 3 and w not in stop_set]
                words.extend(toks)

            c = Counter(words)
            top_words = c.most_common(6)

            if top_words:
                fig_kw = go.Figure(go.Bar(
                    x=[item[1] for item in top_words][::-1],
                    y=[item[0] for item in top_words][::-1],
                    orientation="h",
                    marker=dict(color="#B91C1C", line=dict(color="#991B1B", width=1))
                ))
                fig_kw.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(gridcolor="#EAE6DE", title="Frekuensi Kemunculan"),
                    yaxis=dict(gridcolor="#EAE6DE", title=""),
                    height=300,
                    margin=dict(l=70, r=20, t=10, b=20)
                )
                st.plotly_chart(fig_kw, use_container_width=True)
            else:
                st.info(f"Belum ada ulasan komplain negatif pada aspek {selected_aspect.capitalize()}.")
        else:
            st.info("Aspek tidak ditemukan dalam dataset.")

    st.markdown("---")

    # Filterable Review Explorer
    st.markdown(f"#### Eksplorasi Kutipan Ulasan Konsumen (Aspek: {selected_aspect.capitalize()})")

    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        sent_filter = st.selectbox(
            "Filter Polaritas Sentimen:",
            ["Semua Sentimen", "Hanya Negatif (Komplain)", "Hanya Positif", "Hanya Netral"],
            index=1
        )
    with col_f2:
        all_menus = ["Semua Menu"]
        if "menu_item" in filtered_df.columns:
            all_menus += sorted(list(filtered_df["menu_item"].dropna().unique()))
        menu_filter = st.selectbox("Filter Berdasarkan Menu:", all_menus)

    sub_df = filtered_df.copy()
    if selected_aspect in sub_df.columns:
        if sent_filter == "Hanya Negatif (Komplain)":
            sub_df = sub_df[sub_df[selected_aspect] == "negative"]
        elif sent_filter == "Hanya Positif":
            sub_df = sub_df[sub_df[selected_aspect] == "positive"]
        elif sent_filter == "Hanya Netral":
            sub_df = sub_df[sub_df[selected_aspect] == "neutral"]
        else:
            sub_df = sub_df[sub_df[selected_aspect] != "not_mentioned"]

    if menu_filter != "Semua Menu" and "menu_item" in sub_df.columns:
        sub_df = sub_df[sub_df["menu_item"] == menu_filter]

    st.caption(f"Menampilkan {len(sub_df)} ulasan yang cocok:")

    if not sub_df.empty:
        for _, row in sub_df.iterrows():
            current_sent = str(row.get(selected_aspect, "neutral")).lower()
            if current_sent == "positive":
                b_badge = "<span class='badge-prima'>Positif</span>"
            elif current_sent == "negative":
                b_badge = "<span class='badge-kritis'>Komplain Negatif</span>"
            else:
                b_badge = "<span class='badge-waspada'>Netral</span>"

            st.markdown(
                f"""
                <div class='review-item'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>
                        <div>
                            <b>Menu: {row.get('menu_item', 'Menu Umum')}</b>
                            <span style='margin-left: 8px; font-size: 0.75rem; color: #78716C;'>ID #{row.get('review_id', '-')}</span>
                        </div>
                        {b_badge}
                    </div>
                    <div style='font-size: 0.9rem; color: #292524; line-height: 1.45;'>
                        "{row.get('review_text', '')}"
                    </div>
                    <div style='font-size: 0.75rem; color: #78716C; margin-top: 6px;'>
                        Outlet: {row.get('restaurant_name', '-')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("Tidak ada ulasan yang memenuhi kriteria filter.")
