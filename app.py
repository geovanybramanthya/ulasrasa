"""Aplikasi Web UlasRasa: Asisten Diagnostik Ulasan Kuliner & Rekomendasi Evaluasi Dapur UMKM.
Prototype Interaktif Berbasis NLP (IndoBERT ABSA) dan LLM Generatif.
Dirancang untuk demonstrasi langsung (live demo) dan pitching di hadapan mentor.
Ruangguru AI Engineering Bootcamp - Batch 13 | Student: Azura
"""

import os
import io
import re
from datetime import datetime
from collections import Counter
from typing import Dict, Any, List

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from src.absa_pipeline import ABSAPipeline
from src.action_engine import ActionPlanEngine
from src.preprocessing import clean_text
from src.config import (
    ASPECTS,
    ASPECT_WEIGHTS,
    HEALTH_THRESHOLDS,
    THEME_PALETTE,
    SENTIMENT_COLORS
)
from src.utils.exporter import export_action_plan_text, export_action_plan_pdf

# ==============================================================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="UlasRasa - Kitchen Intelligence Dashboard",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. SISTEM DESAIN UI TEMA HANGAT (WARM OFF-WHITE / ALABASTER CREAM)
# ==============================================================================
CUSTOM_CSS = """
<style>
/* Import Font Modern */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* Global Reset & Base Canvas */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #FAF8F5 !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #1C1917 !important;
}

[data-testid="stHeader"] {
    background-color: rgba(250, 248, 245, 0.85) !important;
    backdrop-filter: blur(10px) !important;
}

/* Sidebar Styling Warm Neutral */
[data-testid="stSidebar"] {
    background-color: #F4F1EA !important;
    border-right: 1px solid #E8E4DA !important;
}

[data-testid="stSidebar"] hr {
    border-color: #E2DDD3 !important;
    margin: 1rem 0 !important;
}

/* Typography Hierarchy */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #1C1917 !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

p, span, label {
    color: #44403C !important;
}

/* Glass & Card Surfaces */
.ulas-card {
    background: #FFFFFF;
    border: 1px solid #EAE6DE;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 20px -2px rgba(45, 35, 25, 0.04), 0 2px 6px -1px rgba(45, 35, 25, 0.02);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.ulas-card:hover {
    border-color: #DDD8CD;
    box-shadow: 0 8px 30px -4px rgba(45, 35, 25, 0.08);
    transform: translateY(-2px);
}

.ulas-card-accent {
    background: linear-gradient(135deg, #FFFDFB 0%, #FAF5EE 100%);
    border-left: 4px solid #C84B2F;
}

/* Metric Display Hero */
.kpi-container {
    background: #FFFFFF;
    border: 1px solid #EAE6DE;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(45, 35, 25, 0.03);
    position: relative;
    overflow: hidden;
}

.kpi-title {
    font-size: 0.82rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #78716C;
    margin-bottom: 4px;
}

.kpi-value {
    font-size: 2.1rem;
    font-weight: 800;
    color: #1C1917;
    line-height: 1.1;
    margin-bottom: 6px;
}

.kpi-subtitle {
    font-size: 0.82rem;
    color: #57534E;
}

/* Pill Badges */
.badge-prima {
    background-color: #F0FDF4;
    color: #15803D;
    border: 1px solid #DCFCE7;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.78rem;
    display: inline-flex;
    align-items: center;
}

.badge-waspada {
    background-color: #FEFCE8;
    color: #B45309;
    border: 1px solid #FEF08A;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.78rem;
    display: inline-flex;
    align-items: center;
}

.badge-kritis {
    background-color: #FEF2F2;
    color: #B91C1C;
    border: 1px solid #FEE2E2;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.78rem;
    display: inline-flex;
    align-items: center;
}

.badge-aspek {
    background-color: #F5F3ED;
    color: #44403C;
    border: 1px solid #E2DDD3;
    padding: 3px 8px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.75rem;
}

/* Interactive Workflow Step Indicator */
.workflow-step {
    background: #FFFFFF;
    border: 1px solid #EAE6DE;
    border-radius: 10px;
    padding: 12px 14px;
    text-align: center;
    box-shadow: 0 2px 6px rgba(45, 35, 25, 0.02);
    transition: transform 0.2s ease;
}

.workflow-step:hover {
    border-color: #C84B2F;
    transform: translateY(-2px);
}

.workflow-num {
    display: inline-block;
    width: 24px;
    height: 24px;
    background: #C84B2F;
    color: #FFFFFF;
    border-radius: 50%;
    font-size: 0.75rem;
    font-weight: 700;
    line-height: 24px;
    margin-bottom: 6px;
}

.workflow-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #1C1917;
    margin-bottom: 2px;
}

.workflow-desc {
    font-size: 0.72rem;
    color: #78716C;
    line-height: 1.25;
}

/* Review Cards */
.review-item {
    background: #FFFFFF;
    border: 1px solid #EAE6DE;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    border-left: 3px solid #EAE6DE;
    transition: border-color 0.2s ease;
}

.review-item:hover {
    border-left-color: #C84B2F;
}

/* Code Snippet Box */
.clean-text-box {
    background: #F5F3ED;
    border: 1px solid #E2DDD3;
    border-radius: 8px;
    padding: 10px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #292524;
}

/* Buttons Styling */
.stButton>button {
    background-color: #C84B2F !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 8px 18px !important;
    transition: all 0.2s ease !important;
}

.stButton>button:hover {
    background-color: #B33E24 !important;
    box-shadow: 0 4px 12px rgba(200, 75, 47, 0.25) !important;
    transform: translateY(-1px) !important;
}

/* Tabs Header Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #F5F3ED;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid #EAE6DE;
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    background-color: transparent;
    border-radius: 8px;
    color: #57534E;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 0 16px;
}

.stTabs [aria-selected="true"] {
    background-color: #FFFFFF !important;
    color: #C84B2F !important;
    box-shadow: 0 2px 8px rgba(45, 35, 25, 0.06) !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# 3. RESOURCE CACHING & PIPELINE ENGINE INITIALIZATION
# ==============================================================================
@st.cache_resource
def load_ai_engines():
    """Memuat modul inferensi NLP dan Action Plan Engine."""
    return ABSAPipeline(), ActionPlanEngine()

pipeline, action_engine = load_ai_engines()

@st.cache_data
def load_default_dataset() -> pd.DataFrame:
    """Memuat 100 sampel ulasan terkurasi dari dataset lokal."""
    csv_path = os.path.join(os.path.dirname(__file__), "data", "sample_reviews.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()

# Inisialisasi Session State
if "custom_reviews_df" not in st.session_state:
    st.session_state.custom_reviews_df = load_default_dataset()

if "custom_checklist_items" not in st.session_state:
    st.session_state.custom_checklist_items = []

if "simulator_text" not in st.session_state:
    st.session_state.simulator_text = (
        "Ayamnya gurih renyah bumbunya mantap meresap, tapi kemasan mangkok tumpah kuah "
        "dan minyak sambal rembes ke kantong plastik. Driver nunggu 30 menit."
    )

# ==============================================================================
# 4. SIDEBAR: PENGENDALIAN DATASET & PANDUAN PITCHING
# ==============================================================================
with st.sidebar:
    st.markdown("### UlasRasa Hub")
    st.caption("AI Kitchen Diagnostic & Evaluation System")
    st.markdown("---")

    # Mode Presentasi / Pitching Guide
    with st.expander("Panduan Pitching Mentor (3 Menit)", expanded=False):
        st.markdown(
            """
            **1. Fenomena & Masalah (Menit 0:00 - 0:45):**
            - Ribuan ulasan liar masuk setiap hari di GoFood/GrabFood/Google Maps.
            - Analisis sentimen konvensional gagal karena cuma biner (+/-), padahal komplain kuliner selalu *mixed sentiment* (rasa enak tapi kemasan bocor).

            **2. Solusi Hybrid AI (Menit 0:45 - 2:00):**
            - **IndoBERT NLP**: Membedah teks ke 5 Aspek Kunci (Rasa, Porsi, Harga, Kemasan, Pelayanan) secara deterministik dan cepat (<100ms).
            - **Kitchen Health Score (KHS)**: Metrik komposit terbobot 0-100%.
            - **Generative LLM**: Mengubah temuan komplain menjadi RCA (5-Why) dan checklist tindakan dapur siap cetak.

            **3. Dampak Bisnis (Menit 2:00 - 3:00):**
            - Memangkas waktu audit pemilik resto dari 10 jam/minggu jadi instan.
            - Mencegah kehilangan rating bintang yang memicu penurunan omzet delivery.
            """
        )

    st.markdown("#### Sumber Data Ulasan")
    data_source_mode = st.radio(
        "Pilih Sumber Data:",
        ["Outlet Bawaan (Preset)", "Upload Dataset Real (CSV)"],
        index=0,
        help="Pilih preset restoran lokal atau unggah file ulasan GoFood/GrabFood/Google Maps milikmu sendiri."
    )

    active_df = st.session_state.custom_reviews_df.copy()

    if data_source_mode == "Upload Dataset Real (CSV)":
        uploaded_file = st.file_uploader(
            "Upload File CSV Ulasan:",
            type=["csv"],
            help="File minimal memiliki kolom 'review_text'. Kolom lain opsional."
        )
        if uploaded_file is not None:
            try:
                user_csv = pd.read_csv(uploaded_file)
                if "review_text" in user_csv.columns:
                    st.success(f"File berhasil dimuat ({len(user_csv)} baris)!")
                    active_df = user_csv
                    selected_resto = user_csv.get("restaurant_name", pd.Series(["Outlet Kustom"])).iloc[0]
                else:
                    st.error("CSV wajib memiliki kolom 'review_text'!")
            except Exception as e:
                st.error(f"Gagal membaca CSV: {e}")
        else:
            st.info("Menggunakan dataset aktif sementara.")
            selected_resto = "Semua Outlet (Benchmark)"
    else:
        # Pilihan Outlet Preset
        if not active_df.empty and "restaurant_name" in active_df.columns:
            outlet_list = ["Semua Outlet (Benchmark Industri)"] + sorted(list(active_df["restaurant_name"].unique()))
            selected_resto = st.selectbox(
                "Pilih Profil Outlet UMKM:",
                outlet_list,
                index=1,
                help="Setiap outlet memiliki karakteristik komplain operasional riil yang berbeda."
            )
        else:
            selected_resto = "Ayam Geprek Sambal Korek Barokah"

    # Filter Dataframe Aktif
    if selected_resto != "Semua Outlet (Benchmark Industri)" and "restaurant_name" in active_df.columns:
        filtered_df = active_df[active_df["restaurant_name"] == selected_resto].copy()
    else:
        filtered_df = active_df.copy()

    st.markdown("---")
    
    # Form Tambah Ulasan Baru Langsung (Interaktif)
    with st.expander("Input Ulasan Baru ke Outlet Ini", expanded=False):
        st.caption("Uji coba menambahkan komplain baru secara live ke database aktif.")
        new_rev_text = st.text_area("Kalimat Ulasan Konsumen:", height=75, placeholder="Contoh: Ayam alot dan sambalnya sedikit...")
        new_rev_menu = st.text_input("Menu Terkait:", value="Menu Favorit")
        
        if st.button("Simpan & Perbarui Dashboard"):
            if new_rev_text.strip():
                # Jalankan inferensi langsung pada ulasan baru
                infer_res = pipeline.analyze_single_review(new_rev_text)
                new_row = {
                    "review_id": len(st.session_state.custom_reviews_df) + 1,
                    "restaurant_name": selected_resto if selected_resto != "Semua Outlet (Benchmark Industri)" else "Ayam Geprek Sambal Korek Barokah",
                    "menu_item": new_rev_menu,
                    "review_text": new_rev_text,
                    "rasa": infer_res["aspects"]["rasa"]["sentiment"],
                    "porsi": infer_res["aspects"]["porsi"]["sentiment"],
                    "harga": infer_res["aspects"]["harga"]["sentiment"],
                    "kemasan": infer_res["aspects"]["kemasan"]["sentiment"],
                    "pelayanan": infer_res["aspects"]["pelayanan"]["sentiment"],
                }
                st.session_state.custom_reviews_df = pd.concat([st.session_state.custom_reviews_df, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Ulasan berhasil ditambahkan! Dashboard terbarui.")
                st.rerun()
            else:
                st.warning("Teks ulasan tidak boleh kosong.")

    st.markdown("---")
    st.markdown(
        """
        <div style='font-size: 0.78rem; color: #78716C;'>
            <b>Bobot Komposit KHS:</b><br>
            • Rasa: 35% | Porsi: 20%<br>
            • Kemasan: 15% | Harga: 15%<br>
            • Pelayanan: 15%<br>
            <i>Total Pembobotan: 100%</i>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==============================================================================
# 5. HEADER UTAMA & PANDUAN LANGKAH SISTEM (SELF-EXPLANATORY UX)
# ==============================================================================
st.title("UlasRasa: Asisten Diagnostik Ulasan Kuliner & Evaluasi Dapur")
st.markdown(
    f"Sistem intelijen berbasis **IndoBERT Multi-Aspect Sentiment Analysis** dan **Generative AI** "
    f"untuk membedah ulasan tidak terstruktur menjadi metrik kesehatan operasional dapur UMKM F&B. "
    f"(Target Analisis: **{selected_resto}** | **{len(filtered_df)}** Ulasan Konsumen Aktif)"
)

# Interactive Workflow Step Indicator
with st.container():
    st.markdown(
        """
        <div style='margin-bottom: 24px;'>
            <div style='display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px;'>
                <div class='workflow-step'>
                    <div class='workflow-num'>1</div>
                    <div class='workflow-title'>Ingestion & Slang</div>
                    <div class='workflow-desc'>Pembersihan teks ulasan & normalisasi bahasa gaul F&B</div>
                </div>
                <div class='workflow-step'>
                    <div class='workflow-num'>2</div>
                    <div class='workflow-title'>ABSA IndoBERT</div>
                    <div class='workflow-desc'>Klasifikasi 5 aspek (Rasa, Porsi, Harga, Kemasan, Pelayanan)</div>
                </div>
                <div class='workflow-step'>
                    <div class='workflow-num'>3</div>
                    <div class='workflow-title'>Health Scoring</div>
                    <div class='workflow-desc'>Perhitungan KHS terbobot & pemetaan Spider Chart</div>
                </div>
                <div class='workflow-step'>
                    <div class='workflow-num'>4</div>
                    <div class='workflow-title'>Root Cause (5-Why)</div>
                    <div class='workflow-desc'>Diagnosa otomatis akar pemicu masalah dapur</div>
                </div>
                <div class='workflow-step'>
                    <div class='workflow-num'>5</div>
                    <div class='workflow-title'>Action Checklist</div>
                    <div class='workflow-desc'>Checklist kru dapur siap cetak & SOP perbaikan fisik</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Evaluasi Dataframe Lengkap via Pipeline
eval_results = pipeline.evaluate_dataframe(filtered_df)
khs = eval_results.get("kitchen_health_score", 0.0)
breakdown = eval_results.get("aspect_breakdown", {})

# Tentukan Status Operasional KHS
if khs >= HEALTH_THRESHOLDS["PRIMA"]:
    status_label = "PRIMA (Dapur Optimal)"
    status_class = "badge-prima"
    status_color = "#15803D"
elif khs >= HEALTH_THRESHOLDS["WASPADA"]:
    status_label = "WASPADA (Perlu Perhatian)"
    status_class = "badge-waspada"
    status_color = "#B45309"
else:
    status_label = "KRITIS (Audit Dapur Segera!)"
    status_class = "badge-kritis"
    status_color = "#B91C1C"

# Aspek dengan kepuasan paling rendah
weakest_aspect = min(breakdown.items(), key=lambda x: x[1].get("satisfaction_score", 100.0))[0] if breakdown else "kemasan"
weakest_score = breakdown.get(weakest_aspect, {}).get("satisfaction_score", 100.0)

# ==============================================================================
# 6. TAB NAVIGASI UTAMA
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Ringkasan Eksekutif & Health Score",
    "2. Deep-Dive Aspek & Sentimen",
    "3. AI Kitchen Action Checklist",
    "4. Single Review Simulator (Live Demo)"
])

# ==============================================================================
# TAB 1: RINGKASAN EKSEKUTIF & HEALTH SCORE
# ==============================================================================
with tab1:
    st.markdown("### Ringkasan Kesehatan Dapur (Executive Overview)")
    st.caption("Visualisasi komprehensif kepuasan pelanggan lintas 5 aspek kunci dan evaluasi skor dapur.")

    # 4 Kartu KPI Utama
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(
            f"""
            <div class='kpi-container'>
                <div class='kpi-title'>Kitchen Health Score</div>
                <div class='kpi-value' style='color: {status_color};'>{khs:.1f}%</div>
                <div class='kpi-subtitle'>
                    {'Baseline tercapai (+5.0% aman)' if khs >= 75 else 'Di bawah ambang target 75%'}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi_col2:
        st.markdown(
            f"""
            <div class='kpi-container'>
                <div class='kpi-title'>Status Operasional</div>
                <div style='margin-top: 8px; margin-bottom: 12px;'>
                    <span class='{status_class}'>{status_label}</span>
                </div>
                <div class='kpi-subtitle'>Berdasarkan ambang industri F&B</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi_col3:
        st.markdown(
            f"""
            <div class='kpi-container'>
                <div class='kpi-title'>Aspek Paling Kritis</div>
                <div class='kpi-value' style='font-size: 1.6rem; color: #B91C1C;'>{weakest_aspect.capitalize()}</div>
                <div class='kpi-subtitle'>Kepuasan: {weakest_score:.1f}% (Komplain tinggi)</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi_col4:
        st.markdown(
            f"""
            <div class='kpi-container'>
                <div class='kpi-title'>Total Sampel Ulasan</div>
                <div class='kpi-value'>{len(filtered_df)}</div>
                <div class='kpi-subtitle'>Ulasan aktif GoFood/GrabFood</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Priority Kitchen Alert Banner jika di bawah ambang batas
    if weakest_score < 75.0:
        st.markdown(
            f"""
            <div class='ulas-card ulas-card-accent'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <b style='color: #C84B2F; font-size: 0.95rem;'>🚨 Peringatan Prioritas Dapur: Aspek {weakest_aspect.capitalize()} Kritis!</b>
                        <p style='margin: 4px 0 0 0; font-size: 0.85rem; color: #57534E;'>
                            Tingkat komplain pada aspek <b>{weakest_aspect.capitalize()}</b> mencapai 
                            <b>{breakdown.get(weakest_aspect, {}).get('negative_rate', 0.0):.1f}%</b>. 
                            Diperlukan tindakan segera di stasiun assembling/packing dapur agar rating toko tidak anjlok di aplikasi food delivery.
                        </p>
                    </div>
                    <span class='badge-kritis'>Action Required</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Visualisasi Spider Radar Chart & Penjelasan Komponen
    col_radar, col_breakdown_cards = st.columns([1.1, 1.3])

    with col_radar:
        st.markdown("#### Spider Chart: Keseimbangan 5 Aspek Dapur")
        categories = [k.capitalize() for k in breakdown.keys()]
        scores = [v["satisfaction_score"] for v in breakdown.values()]
        
        if categories:
            radar_cats = categories + [categories[0]]
            radar_scores = scores + [scores[0]]
            
            fig_radar = go.Figure()
            
            # Area Skor Aktual
            fig_radar.add_trace(go.Scatterpolar(
                r=radar_scores,
                theta=radar_cats,
                fill='toself',
                name='Skor Aktual',
                line=dict(color='#C84B2F', width=2.5),
                fillcolor='rgba(200, 75, 47, 0.22)',
                marker=dict(size=6, color='#C84B2F')
            ))
            
            # Garis Batas Prima (80%)
            fig_radar.add_trace(go.Scatterpolar(
                r=[80.0] * len(radar_cats),
                theta=radar_cats,
                mode='lines',
                name='Batas Prima (80%)',
                line=dict(color='#15803D', dash='dash', width=1.5)
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickvals=[25, 50, 75, 100],
                        tickfont=dict(size=10, color="#78716C"),
                        gridcolor="#EAE6DE"
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=11, color="#1C1917", weight="bold"),
                        gridcolor="#EAE6DE"
                    ),
                    bgcolor="#FAF8F5"
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=True,
                legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
                height=360,
                margin=dict(l=35, r=35, t=25, b=35)
            )
            st.plotly_chart(fig_radar, use_container_width=True)

    with col_breakdown_cards:
        st.markdown("#### Rincian Kinerja 5 Aspek Kunci")
        st.caption("Tingkat kepuasan dihitung dengan formulasi: (Positif + 0.5 × Netral) ÷ Total Disebut × 100%.")

        for asp_name, m in breakdown.items():
            asp_cap = asp_name.capitalize()
            score = m["satisfaction_score"]
            weight = ASPECT_WEIGHTS.get(asp_cap, 0.15) * 100
            
            # Progress bar color
            p_color = "#15803D" if score >= 80 else ("#B45309" if score >= 65 else "#B91C1C")
            
            st.markdown(
                f"""
                <div class='ulas-card' style='padding: 12px 16px; margin-bottom: 8px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>
                        <div style='display: flex; align-items: center; gap: 8px;'>
                            <b style='font-size: 0.95rem; color: #1C1917;'>{asp_cap}</b>
                            <span class='badge-aspek'>Bobot: {weight:.0f}%</span>
                        </div>
                        <div style='font-size: 1.1rem; font-weight: 800; color: {p_color};'>
                            {score:.1f}%
                        </div>
                    </div>
                    <div style='background: #EAE6DE; border-radius: 6px; height: 7px; overflow: hidden; margin-bottom: 8px;'>
                        <div style='background: {p_color}; width: {min(score, 100):.1f}%; height: 100%; border-radius: 6px;'></div>
                    </div>
                    <div style='display: flex; justify-content: space-between; font-size: 0.78rem; color: #78716C;'>
                        <span>Disebut: <b>{m['total_mentioned']}</b> kali</span>
                        <span>👍 Positif: <b style='color: #15803D;'>{m['positive']}</b></span>
                        <span>✋ Netral: <b style='color: #B45309;'>{m['neutral']}</b></span>
                        <span>👎 Komplain: <b style='color: #B91C1C;'>{m['negative']} ({m['negative_rate']:.0f}%)</b></span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# ==============================================================================
# TAB 2: DEEP-DIVE ASPEK & SENTIMEN
# ==============================================================================
with tab2:
    st.markdown("### Deep-Dive Analisis Sentimen & Keluhan Pelanggan")
    st.caption("Bedah distribusi sentimen lintas aspek, frekuensi kata kunci komplain, dan kutipan ulasan langsung.")

    col_selector, col_empty = st.columns([1, 2])
    with col_selector:
        selected_aspect = st.selectbox(
            "Pilih Aspek Diagnostik:",
            ["Rasa", "Porsi", "Harga", "Kemasan", "Pelayanan"],
            index=0
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

    # Filtering Data
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

# ==============================================================================
# TAB 3: AI KITCHEN ACTION CHECKLIST & SOP
# ==============================================================================
with tab3:
    st.markdown("### AI Kitchen Action Checklist & Rekomendasi SOP")
    st.caption("Dihasilkan secara otomatis oleh Generative LLM Engine berbasis sintesis pola ulasan komplain.")

    # Ekstraksi keluhan ulasan nyata untuk generator
    sample_complaints = []
    for asp in ["kemasan", "rasa", "porsi", "harga", "pelayanan"]:
        if asp in filtered_df.columns:
            negs = filtered_df[filtered_df[asp] == "negative"]["review_text"].tolist()
            sample_complaints.extend(negs[:3])

    plan = action_engine.generate_action_plan(
        restaurant_name=selected_resto,
        evaluation_results=eval_results,
        sample_complaints=sample_complaints
    )

    # 1. Root Cause Analysis (5-Why Ishikawa)
    st.markdown("#### 1. Ringkasan Akar Masalah Operasional (Root Cause Analysis)")
    st.caption("Analisis mendalam mengapa keluhan pelanggan terjadi di area dapur/pengemasan:")
    
    for idx, rc in enumerate(plan.get("root_cause_analysis", []), 1):
        st.markdown(
            f"""
            <div class='ulas-card' style='padding: 14px 18px; margin-bottom: 8px;'>
                <div style='display: flex; gap: 10px; align-items: flex-start;'>
                    <div style='background: #C84B2F; color: #FFFFFF; width: 22px; height: 22px; border-radius: 50%; font-size: 0.75rem; font-weight: 700; text-align: center; line-height: 22px; flex-shrink: 0;'>{idx}</div>
                    <div style='font-size: 0.88rem; color: #292524; line-height: 1.4;'>
                        {rc}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2. Checklist Tindakan Dapur Siap Cetak
    st.markdown("#### 2. Checklist Perbaikan Dapur Siap Cetak")
    st.caption("Centang setiap tindakan yang sudah diverifikasi oleh Head Cook / Manajer Dapur saat shift kerja:")

    # Gabungkan item bawaan + item kustom dari session_state
    all_checklist = list(plan.get("kitchen_action_checklist", []))
    for custom_item in st.session_state.custom_checklist_items:
        if custom_item not in all_checklist:
            all_checklist.append(custom_item)

    completed_count = 0
    checked_status = {}

    for idx, item in enumerate(all_checklist):
        is_checked = st.checkbox(item, key=f"action_chk_{selected_resto}_{idx}")
        checked_status[idx] = is_checked
        if is_checked:
            completed_count += 1

    progress_ratio = completed_count / len(all_checklist) if all_checklist else 1.0
    st.progress(progress_ratio)
    st.caption(f"Tingkat Penyelesaian Audit Shift: **{completed_count}/{len(all_checklist)}** Selesai ({progress_ratio*100:.0f}%)")

    # Form Tambah Tindakan Kustom
    with st.expander("Tambah Tindakan Dapur Kustom", expanded=False):
        custom_act_text = st.text_input("Tindakan Baru:", placeholder="Contoh: Kalibrasi ulang termometer minyak fryer setiap jam 10 pagi...")
        if st.button("Tambahkan ke Checklist"):
            if custom_act_text.strip():
                st.session_state.custom_checklist_items.append(custom_act_text.strip())
                st.success("Tindakan kustom berhasil ditambahkan ke checklist!")
                st.rerun()

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 3. Rekomendasi SOP Dapur Standar
    st.markdown("#### 3. Rekomendasi Standard Operating Procedure (SOP)")
    st.caption("Standard Operating Procedure yang disarankan untuk ditempel pada workstation dapur:")

    for sop_item in plan.get("sop_recommendations", []):
        st.markdown(
            f"""
            <div class='ulas-card' style='border-left: 4px solid #15803D; padding: 12px 18px; margin-bottom: 8px;'>
                <b style='color: #15803D; font-size: 0.85rem;'>SOP Operasional Terverifikasi:</b>
                <p style='margin: 4px 0 0 0; font-size: 0.85rem; color: #44403C;'>{sop_item}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 4. Export & Download Center
    st.markdown("#### Unduh Dokumen Checklist Dapur")
    st.caption("Ekspor checklist tindakan untuk dicetak dan ditempel di meja dapur atau dibagikan ke kru:")

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    # Generate Text Report
    checklist_text_content = export_action_plan_text(
        overall_score=khs,
        status=status_label,
        action_items=[
            {
                "aspect": "Operasional",
                "title": item[:35],
                "target_pic": "Tim Dapur / Kru",
                "deadline": "Shift Berjalan",
                "instruction": item,
                "checked": checked_status.get(i, False)
            }
            for i, item in enumerate(all_checklist)
        ],
        critical_alerts=[
            {"title": f"Masalah Aspek {weakest_aspect.capitalize()}", "aspect": weakest_aspect.capitalize(), "message": rc}
            for rc in plan.get("root_cause_analysis", [])[:2]
        ]
    )

    with col_btn1:
        st.download_button(
            label="📄 Unduh Format Teks (.txt)",
            data=checklist_text_content,
            file_name=f"checklist_dapur_{selected_resto.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col_btn2:
        try:
            pdf_bytes = export_action_plan_pdf(
                overall_score=khs,
                status=status_label,
                action_items=[
                    {
                        "id": f"ACT-{i+1}",
                        "aspect": "Dapur",
                        "title": item[:35] + ("..." if len(item) > 35 else ""),
                        "target_pic": "Kru Dapur",
                        "deadline": "Shift Aktif",
                        "instruction": item,
                        "checked": checked_status.get(i, False)
                    }
                    for i, item in enumerate(all_checklist)
                ],
                critical_alerts=[
                    {"title": f"Fokus Perbaikan {weakest_aspect.capitalize()}", "aspect": weakest_aspect.capitalize(), "message": rc}
                    for rc in plan.get("root_cause_analysis", [])[:2]
                ]
            )
            st.download_button(
                label="📑 Unduh Dokumen Resmi PDF (.pdf)",
                data=pdf_bytes,
                file_name=f"checklist_dapur_{selected_resto.lower().replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.caption(f"PDF Generator Notice: {e}")

    with col_btn3:
        # CSV Export
        action_export_df = pd.DataFrame([
            {"No": i+1, "Tindakan": item, "Status_Selesai": checked_status.get(i, False), "PIC": "Kru Dapur"}
            for i, item in enumerate(all_checklist)
        ])
        st.download_button(
            label="📊 Unduh Tabel CSV (.csv)",
            data=action_export_df.to_csv(index=False),
            file_name=f"checklist_dapur_{selected_resto.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ==============================================================================
# TAB 4: SINGLE REVIEW SIMULATOR (LIVE AI DEMO UNTUK PITCHING)
# ==============================================================================
with tab4:
    st.markdown("### Simulator Diagnostik Ulasan Tunggal (Live AI Demo)")
    st.caption("Uji coba model inferensi IndoBERT ABSA secara instan pada teks ulasan bebas:")

    st.markdown("#### 1. Pilih Preset Ulasan Simulasi Pitching:")
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)

    preset_texts = {
        "p1": "Ayamnya gurih renyah bumbunya mantap meresap, tapi kemasan mangkok tumpah kuah dan minyak sambal rembes ke kantong plastik. Driver nunggu 30 menit.",
        "p2": "Gelas kopinya kecil banget es batunya penuh 80%, toast makin tipis, harga 35rb kemahalan buat porsi segini.",
        "p3": "Lama banget pelayanannya, order mie ayam bakso nunggu 50 menit pas jam makan siang. Pelayan jutek kuah dingin keasinan.",
        "p4": "Bebek bumbu hitamnya juara dunia rempahnya medok daging empuk porsi jumbo kemasan besek bambu sangat rapi!"
    }

    with p_col1:
        if st.button("Mixed: Rasa vs Kemasan"):
            st.session_state.simulator_text = preset_texts["p1"]
            st.rerun()

    with p_col2:
        if st.button("Porsi & Harga"):
            st.session_state.simulator_text = preset_texts["p2"]
            st.rerun()

    with p_col3:
        if st.button("Pelayanan & Suhu"):
            st.session_state.simulator_text = preset_texts["p3"]
            st.rerun()

    with p_col4:
        if st.button("Puas Bintang 5"):
            st.session_state.simulator_text = preset_texts["p4"]
            st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    sim_input = st.text_area(
        "Ketik Kalimat Ulasan Konsumen (Bahasa Indonesia Sehari-hari):",
        value=st.session_state.simulator_text,
        height=100
    )

    if st.button("Bedah Aspek Ulasan Sekarang"):
        st.session_state.simulator_text = sim_input
        sim_res = pipeline.analyze_single_review(sim_input)
        
        st.markdown("---")
        st.markdown("#### 2. Hasil Ekstraksi NLP & Normalisasi Slang")

        # Perbandingan Raw vs Cleaned Text
        c_raw, c_clean = st.columns(2)
        with c_raw:
            st.markdown("**Teks Mentah Asli:**")
            st.markdown(f"<div class='clean-text-box'>{sim_res['original_text']}</div>", unsafe_allow_html=True)
        with c_clean:
            st.markdown("**Teks Normalisasi Slang & Indo4B:**")
            st.markdown(f"<div class='clean-text-box'>{sim_res['cleaned_text']}</div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 3. Diagnostik 5 Aspek Kunci (Multi-Head Classification)")

        cols = st.columns(5)
        aspects_map = sim_res["aspects"]

        for idx, (asp, data) in enumerate(aspects_map.items()):
            with cols[idx]:
                asp_title = asp.capitalize()
                is_mentioned = data["mentioned"]
                sent = data["sentiment"]
                conf = data["confidence"]

                if not is_mentioned:
                    badge_html = "<span class='badge-aspek'>Tidak Disebut</span>"
                    box_border = "#EAE6DE"
                    stat_msg = "Aspek tidak dibahas dalam kalimat ulasan."
                elif sent == "positive":
                    badge_html = f"<span class='badge-prima'>Positif ({conf*100:.0f}%)</span>"
                    box_border = "#15803D"
                    stat_msg = "Pelanggan puas dengan kualitas aspek ini."
                elif sent == "negative":
                    badge_html = f"<span class='badge-kritis'>Komplain ({conf*100:.0f}%)</span>"
                    box_border = "#B91C1C"
                    stat_msg = "Keluhan operasional terdeteksi! Perlu mitigasi."
                else:
                    badge_html = f"<span class='badge-waspada'>Netral ({conf*100:.0f}%)</span>"
                    box_border = "#B45309"
                    stat_msg = "Ulasan bersifat netral atau deskriptif."

                st.markdown(
                    f"""
                    <div class='ulas-card' style='border-top: 4px solid {box_border}; padding: 14px; text-align: center;'>
                        <b style='font-size: 1rem; color: #1C1917;'>{asp_title}</b>
                        <div style='margin: 8px 0;'>{badge_html}</div>
                        <div style='font-size: 0.75rem; color: #78716C;'>{stat_msg}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Rekomendasi Instan untuk Ulasan Ini
        neg_detected = [asp.capitalize() for asp, d in aspects_map.items() if d["mentioned"] and d["sentiment"] == "negative"]
        if neg_detected:
            st.markdown(
                f"""
                <div class='ulas-card' style='background: #FFFDFB; border-left: 4px solid #C84B2F; margin-top: 14px;'>
                    <b style='color: #C84B2F;'>💡 Rekomendasi Tindakan Cepat (Instant Mitigation):</b>
                    <p style='margin: 4px 0 0 0; font-size: 0.85rem; color: #44403C;'>
                        Terdeteksi komplain operasional pada aspek <b>{', '.join(neg_detected)}</b>. 
                        Kru dapur disarankan segera memverifikasi SOP pengemasan anti-bocor dan memastikan suhu makanan sebelum diserahkan ke kurir pengantar.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class='ulas-card' style='background: #FDFEFD; border-left: 4px solid #15803D; margin-top: 14px;'>
                    <b style='color: #15803D;'>✅ Ulasan Sangat Positif:</b>
                    <p style='margin: 4px 0 0 0; font-size: 0.85rem; color: #44403C;'>
                        Tidak terdeteksi komplain operasional. Pertahankan konsistensi resep dan standar pelayanan dapur saat ini.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.markdown(
    """
    <div style='display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; color: #78716C;'>
        <span><b>UlasRasa</b> - AI Engineering Final Project (Batch 13) | Student ID: <b>REAENG13TQJLN</b> (Azura)</span>
        <span>Arsitektur: <b>IndoBERT Base (ABSA) + Generative LLM Action Engine</b></span>
    </div>
    """,
    unsafe_allow_html=True
)
