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
# 1. KONFIGURASI HALAMAN STREAMLIT (ZERO EMOJI - ASSET FAVICON)
# ==============================================================================
favicon_path = os.path.join(os.path.dirname(__file__), "assets", "favicon.png")
st.set_page_config(
    page_title="UlasRasa - Kitchen Intelligence Dashboard",
    page_icon=favicon_path if os.path.exists(favicon_path) else "UR",
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
    margin: 0.85rem 0 !important;
}

/* Typography Hierarchy */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #1C1917 !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

p, span, label {
    color: #44403C;
}

/* Brand Header in Sidebar */
.brand-container {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 0 12px 0;
}

.brand-logo-badge {
    width: 38px;
    height: 38px;
    background: #C84B2F;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(200, 75, 47, 0.25);
    flex-shrink: 0;
}

.brand-text-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #1C1917;
    letter-spacing: -0.01em;
    line-height: 1.1;
}

.brand-text-sub {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #78716C;
}

/* Pulsing Status Dot (Living UI Effect) */
.live-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #FFFFFF;
    border: 1px solid #E2DDD3;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #15803D;
    margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(45, 35, 25, 0.03);
}

.pulse-dot {
    width: 7px;
    height: 7px;
    background-color: #15803D;
    border-radius: 50%;
    box-shadow: 0 0 0 0 rgba(21, 128, 61, 0.5);
    animation: pulse 1.8s infinite;
}

@keyframes pulse {
    0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(21, 128, 61, 0.6);
    }
    70% {
        transform: scale(1);
        box-shadow: 0 0 0 6px rgba(21, 128, 61, 0);
    }
    100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(21, 128, 61, 0);
    }
}

/* Section Header in Sidebar */
.sidebar-section-header {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #78716C;
    margin: 14px 0 8px 0;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* THE HIGHLIGHTER: Navigation Menu Styling */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label {
    background: #FFFFFF !important;
    border: 1px solid #EAE6DE !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    margin-bottom: 6px !important;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    cursor: pointer !important;
    box-shadow: 0 1px 3px rgba(45, 35, 25, 0.02) !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:hover {
    border-color: #C84B2F !important;
    background: #FFFDFB !important;
    transform: translateX(4px) !important;
    box-shadow: 0 4px 12px rgba(45, 35, 25, 0.05) !important;
}

/* HIGHLIGHTER AKTIF: Border Kiri Tebal & Background Lembut */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(90deg, #FFF4EE 0%, #FAF0E8 100%) !important;
    border-color: #C84B2F !important;
    border-left: 5px solid #C84B2F !important;
    box-shadow: 0 4px 14px rgba(200, 75, 47, 0.12) !important;
    transform: translateX(4px) !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) p {
    color: #C84B2F !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"]:checked + div {
    background-color: #C84B2F !important;
    border-color: #C84B2F !important;
}

/* Live Reactive Outlet Micro-Card in Sidebar */
.sidebar-outlet-card {
    background: #FFFFFF;
    border: 1px solid #EAE6DE;
    border-radius: 12px;
    padding: 14px 16px;
    margin-top: 10px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(45, 35, 25, 0.03);
    position: relative;
    border-left: 4px solid #C84B2F;
}

.sidebar-outlet-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 6px;
}

.sidebar-outlet-name {
    font-size: 0.88rem;
    font-weight: 700;
    color: #1C1917;
    line-height: 1.25;
}

.sidebar-outlet-score-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-top: 8px;
    margin-bottom: 4px;
}

.sidebar-score-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    color: #78716C;
}

.sidebar-score-val {
    font-size: 1.25rem;
    font-weight: 800;
}

.sidebar-progress-track {
    background: #EAE6DE;
    border-radius: 4px;
    height: 5px;
    overflow: hidden;
    margin-bottom: 8px;
}

.sidebar-outlet-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 8px;
}

.outlet-chip {
    background: #F5F3ED;
    border: 1px solid #E2DDD3;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    color: #57534E;
}

.outlet-chip-alert {
    background: #FEF2F2;
    border-color: #FEE2E2;
    color: #B91C1C;
    font-weight: 700;
}

/* Sidebar Weighted Composition Card */
.sidebar-weights-card {
    background: #FFFFFF;
    border: 1px solid #EAE6DE;
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: 8px;
}

.weights-bar-composite {
    display: flex;
    height: 6px;
    border-radius: 4px;
    overflow: hidden;
    margin: 8px 0;
}

.weights-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    font-size: 0.72rem;
    color: #57534E;
}

.weight-item {
    background: #FAF8F5;
    border: 1px solid #EAE6DE;
    padding: 3px 6px;
    border-radius: 4px;
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
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
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
    font-size: 0.8rem;
    color: #57534E;
}

/* Pill Badges (Semantic, Zero Emoji) */
.badge-prima {
    background-color: #F0FDF4;
    color: #15803D;
    border: 1px solid #DCFCE7;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.76rem;
    display: inline-flex;
    align-items: center;
    letter-spacing: 0.02em;
}

.badge-waspada {
    background-color: #FEFCE8;
    color: #B45309;
    border: 1px solid #FEF08A;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.76rem;
    display: inline-flex;
    align-items: center;
    letter-spacing: 0.02em;
}

.badge-kritis {
    background-color: #FEF2F2;
    color: #B91C1C;
    border: 1px solid #FEE2E2;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.76rem;
    display: inline-flex;
    align-items: center;
    letter-spacing: 0.02em;
}

.badge-aspek {
    background-color: #F5F3ED;
    color: #44403C;
    border: 1px solid #E2DDD3;
    padding: 3px 8px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.74rem;
}

/* Micro-Pills for Breakdown Cards */
.metric-pill-pos {
    background: #F0FDF4;
    color: #15803D;
    border: 1px solid #DCFCE7;
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.75rem;
}

.metric-pill-neu {
    background: #FEFCE8;
    color: #B45309;
    border: 1px solid #FEF08A;
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.75rem;
}

.metric-pill-neg {
    background: #FEF2F2;
    color: #B91C1C;
    border: 1px solid #FEE2E2;
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 700;
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
.stButton > button {
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    letter-spacing: -0.01em !important;
}

.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: inherit !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: inherit !important;
    line-height: inherit !important;
}

/* PRIMARY BUTTON: The Active Menu Highlighter & Main Actions */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #C84B2F 0%, #A8351D 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid #8F2B15 !important;
    font-weight: 800 !important;
    box-shadow: 0 6px 20px -2px rgba(200, 75, 47, 0.45), 0 2px 6px -1px rgba(200, 75, 47, 0.25) !important;
    transform: translateY(-2px) !important;
}

.stButton > button[kind="primary"] p,
.stButton > button[data-testid="baseButton-primary"] p {
    color: #FFFFFF !important;
    font-weight: 800 !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.25) !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(135deg, #B33E24 0%, #942E17 100%) !important;
    box-shadow: 0 8px 24px -2px rgba(200, 75, 47, 0.55), 0 3px 8px -1px rgba(200, 75, 47, 0.35) !important;
    transform: translateY(-3px) !important;
}

/* SECONDARY BUTTON: Inactive Navigation Menu Cards */
.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"] {
    background-color: #FFFFFF !important;
    color: #1C1917 !important;
    border: 1.5px solid #DDD8CD !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px -1px rgba(45, 35, 25, 0.06), 0 1px 3px rgba(45, 35, 25, 0.03) !important;
}

.stButton > button[kind="secondary"] p,
.stButton > button[data-testid="baseButton-secondary"] p {
    color: #1C1917 !important;
    font-weight: 700 !important;
}

.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover {
    border-color: #C84B2F !important;
    background-color: #FFFDFB !important;
    color: #C84B2F !important;
    box-shadow: 0 6px 18px -2px rgba(45, 35, 25, 0.12), 0 2px 6px -1px rgba(45, 35, 25, 0.06) !important;
    transform: translateY(-2px) !important;
}

.stButton > button[kind="secondary"]:hover p,
.stButton > button[data-testid="baseButton-secondary"]:hover p {
    color: #C84B2F !important;
}

/* Download Buttons Styling */
.stDownloadButton > button {
    background-color: #FFFFFF !important;
    color: #1C1917 !important;
    border: 1.5px solid #DDD8CD !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 10px 18px !important;
    box-shadow: 0 2px 8px -1px rgba(45, 35, 25, 0.06) !important;
    transition: all 0.22s ease !important;
}

.stDownloadButton > button p {
    color: #1C1917 !important;
    font-weight: 700 !important;
}

.stDownloadButton > button:hover {
    border-color: #C84B2F !important;
    background-color: #FFFDFB !important;
    box-shadow: 0 6px 18px -2px rgba(45, 35, 25, 0.12) !important;
    transform: translateY(-2px) !important;
}

.stDownloadButton > button:hover p {
    color: #C84B2F !important;
}

/* Top Synchronized Navigation Bar */
.top-nav-bar {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    background-color: #F4F1EA;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid #EAE6DE;
    margin-bottom: 20px;
}

.top-nav-pill {
    padding: 10px 14px;
    border-radius: 8px;
    text-align: center;
    font-size: 0.85rem;
    font-weight: 600;
    color: #57534E;
    background: transparent;
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.2s ease;
}

.top-nav-pill-active {
    background: #FFFFFF !important;
    color: #C84B2F !important;
    border: 1px solid #EAE6DE !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px rgba(45, 35, 25, 0.06) !important;
}

.active-nav-indicator {
    display: inline-block;
    width: 6px;
    height: 6px;
    background: #C84B2F;
    border-radius: 50%;
    margin-right: 6px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# 3. RESOURCE CACHING & PIPELINE ENGINE INITIALIZATION
# ==============================================================================
@st.cache_resource
def load_ai_engines():
    """Memuat engine ABSA utama dan Action Plan Engine.

    Engine utama adalah IndoBERT Base hasil fine-tune lokal
    (models/indobert-base-absa). Bila model tidak tersedia atau gagal
    dimuat, aplikasi jatuh kembali ke engine lexicon (baseline).
    """
    absa_engine = ABSAPipeline()
    engine_label = "Lexicon (fallback)"
    try:
        from src.models.transformer_engine import TransformerABSAPipeline
        absa_engine = TransformerABSAPipeline()
        engine_label = getattr(absa_engine, "engine_name", "IndoBERT (fine-tuned)")
    except Exception:
        pass
    return absa_engine, ActionPlanEngine(), engine_label

pipeline, action_engine, ACTIVE_ABSA_ENGINE_LABEL = load_ai_engines()

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

if "active_module_name" not in st.session_state:
    st.session_state.active_module_name = "Ringkasan Eksekutif & Health Score"

if "simulator_text" not in st.session_state:
    st.session_state.simulator_text = (
        "Ayamnya gurih renyah bumbunya mantap meresap, tapi kemasan mangkok tumpah kuah "
        "dan minyak sambal rembes ke kantong plastik. Driver nunggu 30 menit."
    )

# ==============================================================================
# 4. SIDEBAR: PENGENDALIAN DATASET, NAVIGASI DENGAN HIGHLIGHTER & OUTLET CARD
# ==============================================================================
with st.sidebar:
    # 4.1 Brand Header & Live Pulse Status
    st.markdown(
        """
        <div class='brand-container'>
            <div class='brand-logo-badge'>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M4 16C4 19.5 7.5 21 12 21C16.5 21 20 19.5 20 16H4Z" fill="#FAF8F5"/>
                    <path d="M12 4L14.5 10H9.5L12 4Z" fill="#FAF8F5"/>
                    <line x1="3" y1="15" x2="21" y2="15" stroke="#FAF8F5" stroke-width="1.8" stroke-linecap="round"/>
                    <line x1="9" y1="21.5" x2="15" y2="21.5" stroke="#FAF8F5" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
            </div>
            <div>
                <div class='brand-text-title'>ULASRASA</div>
                <div class='brand-text-sub'>Kitchen Diagnostics AI</div>
            </div>
        </div>
        <div class='live-status-pill'>
            <span class='pulse-dot'></span>
            <span>Engine Siap &bull; Analisis 5 Aspek</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.caption(f"Engine ABSA: {ACTIVE_ABSA_ENGINE_LABEL}")

    # 4.2 Navigasi Modul dengan HIGHLIGHTER
    st.markdown(
        """
        <div class='sidebar-section-header'>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#C84B2F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="7" height="7"></rect>
                <rect x="14" y="3" width="7" height="7"></rect>
                <rect x="14" y="14" width="7" height="7"></rect>
                <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
            MODUL KERJA AKTIF
        </div>
        """,
        unsafe_allow_html=True
    )

    MODULE_CHOICES = [
        "Ringkasan Eksekutif & Health Score",
        "Deep-Dive Aspek & Sentimen",
        "AI Kitchen Action Checklist",
        "Single Review Simulator (Live Demo)"
    ]

    selected_nav = st.radio(
        "Pilih Modul Analisis:",
        MODULE_CHOICES,
        index=MODULE_CHOICES.index(st.session_state.active_module_name) if st.session_state.active_module_name in MODULE_CHOICES else 0,
        label_visibility="collapsed",
        key="sidebar_module_radio"
    )
    st.session_state.active_module_name = selected_nav

    st.markdown("---")

    # 4.3 Konfigurasi Sumber Data Ulasan
    st.markdown(
        """
        <div class='sidebar-section-header'>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#78716C" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
            </svg>
            SUMBER DATA & PROFIL RESTORAN
        </div>
        """,
        unsafe_allow_html=True
    )

    data_source_mode = st.radio(
        "Mode Pengambilan Data:",
        ["Outlet Bawaan (Preset)", "Upload Dataset Real (CSV)"],
        index=0,
        label_visibility="collapsed",
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
                if len(user_csv) > 200:
                    st.error(f"File berisi {len(user_csv)} baris, melebihi batas maksimum 200 baris ulasan per analisis. Perkecil file terlebih dahulu, lalu unggah kembali.")
                elif "review_text" in user_csv.columns:
                    st.success(f"File berhasil dimuat ({len(user_csv)} baris)")
                    active_df = user_csv
                    selected_resto = user_csv.get("restaurant_name", pd.Series(["Outlet Kustom"])).iloc[0]
                else:
                    st.error("CSV wajib memiliki kolom 'review_text'")
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

    # Filter Dataframe Aktif Berdasarkan Pilihan Outlet
    if selected_resto != "Semua Outlet (Benchmark Industri)" and "restaurant_name" in active_df.columns:
        filtered_df = active_df[active_df["restaurant_name"] == selected_resto].copy()
    else:
        filtered_df = active_df.copy()

    # Evaluasi Dataframe untuk Mendapatkan Skor Nyata Restoran
    eval_results = pipeline.evaluate_dataframe(filtered_df)
    khs = eval_results.get("kitchen_health_score", 0.0)
    breakdown = eval_results.get("aspect_breakdown", {})

    # Status KHS
    if khs >= HEALTH_THRESHOLDS["PRIMA"]:
        status_label = "PRIMA (Optimal)"
        status_class = "badge-prima"
        status_color = "#15803D"
    elif khs >= HEALTH_THRESHOLDS["WASPADA"]:
        status_label = "WASPADA (Perhatian)"
        status_class = "badge-waspada"
        status_color = "#B45309"
    else:
        status_label = "KRITIS (Audit Segera)"
        status_class = "badge-kritis"
        status_color = "#B91C1C"

    weakest_aspect = min(breakdown.items(), key=lambda x: x[1].get("satisfaction_score", 100.0))[0] if breakdown else "kemasan"
    weakest_score = breakdown.get(weakest_aspect, {}).get("satisfaction_score", 100.0)

    # 4.4 DYNAMIC LIVE OUTLET PROFILE CARD DI SIDEBAR (UX HIDUP)
    st.markdown(
        f"""
        <div class='sidebar-outlet-card'>
            <div class='sidebar-outlet-header'>
                <div class='sidebar-outlet-name'>{selected_resto}</div>
                <span class='{status_class}'>{status_label.split()[0]}</span>
            </div>
            <div class='sidebar-outlet-score-row'>
                <span class='sidebar-score-label'>Kitchen Health Score</span>
                <span class='sidebar-score-val' style='color: {status_color};'>{khs:.1f}%</span>
            </div>
            <div class='sidebar-progress-track'>
                <div style='width: {min(khs, 100):.1f}%; height: 100%; background: {status_color};'></div>
            </div>
            <div class='sidebar-outlet-chips'>
                <span class='outlet-chip'>{len(filtered_df)} Ulasan Aktif</span>
                <span class='outlet-chip outlet-chip-alert'>Kritis: {weakest_aspect.capitalize()} ({weakest_score:.0f}%)</span>
            </div>
            <div style='font-size: 0.68rem; color: #78716C; margin-top: 6px; display: flex; align-items: center; gap: 4px;'>
                <span class='pulse-dot' style='width: 5px; height: 5px;'></span>
                <span>Konteks Outlet Terpilih Aktif</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # 4.5 Mode Presentasi / Pitching Guide (Tanpa Emoji)
    with st.expander("Panduan Pitching Mentor (3 Menit)", expanded=False):
        st.markdown(
            """
            <div style='font-size: 0.8rem; color: #44403C; line-height: 1.45;'>
                <div style='background: #FAF8F5; border-left: 3px solid #C84B2F; padding: 6px 10px; margin-bottom: 6px; border-radius: 4px;'>
                    <b>Menit 00:00 - 00:45 | Masalah Riil</b><br>
                    Pemilik resto kewalahan memilah ribuan ulasan liar di GoFood/GrabFood. Sentimen konvensional (+/-) gagal karena komplain kuliner selalu <i>mixed sentiment</i>.
                </div>
                <div style='background: #FAF8F5; border-left: 3px solid #D97706; padding: 6px 10px; margin-bottom: 6px; border-radius: 4px;'>
                    <b>Menit 00:45 - 02:00 | Solusi Hybrid AI</b><br>
                    IndoBERT Base hasil fine-tune membedah 5 aspek per ulasan (lexicon menjadi baseline & fallback). KHS mengukur kesehatan dapur 0-100%, lalu LLM Gemini (bila API key tersedia) atau katalog template merumuskan RCA & checklist fisik.
                </div>
                <div style='background: #FAF8F5; border-left: 3px solid #15803D; padding: 6px 10px; border-radius: 4px;'>
                    <b>Menit 02:00 - 03:00 | Dampak Bisnis</b><br>
                    Memangkas audit operasional dari 10 jam/minggu jadi instan dan mencegah penurunan rating delivery toko.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 4.6 Form Tambah Ulasan Baru Langsung
    with st.expander("Input Ulasan Baru ke Outlet Ini", expanded=False):
        st.caption("Uji coba menambahkan komplain baru secara live ke database aktif.")
        new_rev_text = st.text_area("Kalimat Ulasan Konsumen:", height=75, placeholder="Contoh: Ayam alot dan sambalnya sedikit...")
        new_rev_menu = st.text_input("Menu Terkait:", value="Menu Favorit")
        
        if st.button("Simpan & Perbarui Dashboard", type="primary", use_container_width=True):
            if new_rev_text.strip():
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
                st.success("Ulasan baru berhasil ditambahkan! Dashboard terbarui.")
                st.rerun()
            else:
                st.warning("Teks ulasan tidak boleh kosong.")

    st.markdown("---")

    # 4.7 Bobot Komposit KHS (Visual Meter Bar)
    st.markdown(
        """
        <div class='sidebar-weights-card'>
            <div style='display: flex; justify-content: space-between; align-items: center; font-size: 0.72rem; font-weight: 700; color: #78716C;'>
                <span>BOBOT KOMPOSIT KHS</span>
                <span style='background: #EAE6DE; padding: 1px 6px; border-radius: 4px;'>TOTAL 100%</span>
            </div>
            <div class='weights-bar-composite'>
                <div style='width: 35%; background: #C84B2F;' title='Rasa: 35%'></div>
                <div style='width: 20%; background: #D97706;' title='Porsi: 20%'></div>
                <div style='width: 15%; background: #2563EB;' title='Kemasan: 15%'></div>
                <div style='width: 15%; background: #7C3AED;' title='Harga: 15%'></div>
                <div style='width: 15%; background: #059669;' title='Pelayanan: 15%'></div>
            </div>
            <div class='weights-grid'>
                <div class='weight-item' style='border-left: 3px solid #C84B2F;'>Rasa <b>35%</b></div>
                <div class='weight-item' style='border-left: 3px solid #D97706;'>Porsi <b>20%</b></div>
                <div class='weight-item' style='border-left: 3px solid #2563EB;'>Kemasan <b>15%</b></div>
                <div class='weight-item' style='border-left: 3px solid #7C3AED;'>Harga <b>15%</b></div>
                <div class='weight-item' style='border-left: 3px solid #059669; grid-column: span 2;'>Pelayanan <b>15%</b></div>
            </div>
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

# Interactive Workflow Step Indicator (Zero Emoji)
with st.container():
    st.markdown(
        """
        <div style='margin-bottom: 20px;'>
            <div style='display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px;'>
                <div class='workflow-step'>
                    <div class='workflow-num'>1</div>
                    <div class='workflow-title'>Ingestion & Slang</div>
                    <div class='workflow-desc'>Pembersihan ulasan & normalisasi bahasa gaul F&B</div>
                </div>
                <div class='workflow-step'>
                    <div class='workflow-num'>2</div>
                    <div class='workflow-title'>ABSA IndoBERT</div>
                    <div class='workflow-desc'>Klasifikasi 5 aspek (Rasa, Porsi, Harga, Kemasan, Pelayanan)</div>
                </div>
                <div class='workflow-step'>
                    <div class='workflow-num'>3</div>
                    <div class='workflow-title'>Health Scoring</div>
                    <div class='workflow-desc'>Kalkulasi KHS terbobot & pemetaan Spider Chart</div>
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

# Synchronized Top Module Selector (Highlighter Visual Bar)
st.markdown(
    f"""
    <div style='display: flex; justify-content: space-between; align-items: center; margin: 16px 0 12px 0;'>
        <div style='font-size: 0.78rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: #78716C; display: flex; align-items: center; gap: 8px;'>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#C84B2F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="7" height="7"></rect>
                <rect x="14" y="3" width="7" height="7"></rect>
                <rect x="14" y="14" width="7" height="7"></rect>
                <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
            NAVIGASI MODUL DIAGNOSTIK
        </div>
        <div style='font-size: 0.78rem; color: #57534E;'>
            Modul Aktif: <b style='color: #C84B2F; font-weight: 800;'>{st.session_state.active_module_name}</b>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

col_top_nav1, col_top_nav2, col_top_nav3, col_top_nav4 = st.columns(4)
top_cols = [col_top_nav1, col_top_nav2, col_top_nav3, col_top_nav4]
short_labels = ["1. Ringkasan Eksekutif", "2. Deep-Dive Aspek", "3. Checklist & SOP", "4. Review Simulator"]

for idx, (t_col, full_title, s_label) in enumerate(zip(top_cols, MODULE_CHOICES, short_labels)):
    with t_col:
        is_cur = (st.session_state.active_module_name == full_title)
        if is_cur:
            st.button(
                f"AKTIF: {s_label}",
                key=f"top_btn_{idx}",
                type="primary",
                use_container_width=True
            )
        else:
            if st.button(
                s_label,
                key=f"top_btn_{idx}",
                type="secondary",
                use_container_width=True
            ):
                st.session_state.active_module_name = full_title
                st.rerun()

current_module = st.session_state.active_module_name

# ==============================================================================
# MODUL 1: RINGKASAN EKSEKUTIF & HEALTH SCORE
# ==============================================================================
if current_module == "Ringkasan Eksekutif & Health Score":
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

    # Priority Kitchen Alert Banner jika di bawah ambang batas (Zero Emoji, Clean SVG)
    if weakest_score < 75.0:
        st.markdown(
            f"""
            <div class='ulas-card ulas-card-accent' style='border-left: 4px solid #B91C1C;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div style='display: flex; gap: 12px; align-items: center;'>
                        <div style='width: 36px; height: 36px; background: #FEE2E2; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;'>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#B91C1C" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                                <line x1="12" y1="9" x2="12" y2="13"></line>
                                <line x1="12" y1="17" x2="12.01" y2="17"></line>
                            </svg>
                        </div>
                        <div>
                            <b style='color: #B91C1C; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.03em;'>Peringatan Prioritas Dapur: Aspek {weakest_aspect.capitalize()} Kritis</b>
                            <p style='margin: 4px 0 0 0; font-size: 0.85rem; color: #57534E;'>
                                Tingkat komplain pada aspek <b>{weakest_aspect.capitalize()}</b> mencapai 
                                <b>{breakdown.get(weakest_aspect, {}).get('negative_rate', 0.0):.1f}%</b>. 
                                Diperlukan tindakan segera di stasiun assembling/packing dapur agar rating toko tidak anjlok di aplikasi food delivery.
                            </p>
                        </div>
                    </div>
                    <span class='badge-kritis'>Tindakan Diperlukan</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Visualisasi Spider Radar Chart & Rincian Aspek
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
        st.caption("Tingkat kepuasan dihitung dengan formulasi: (Positif + 0.5 x Netral) / Total Disebut x 100%.")

        for asp_name, m in breakdown.items():
            asp_cap = asp_name.capitalize()
            score = m["satisfaction_score"]
            weight = ASPECT_WEIGHTS.get(asp_cap, 0.15) * 100
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
                        <span class='metric-pill-pos'>Positif: <b>{m['positive']}</b></span>
                        <span class='metric-pill-neu'>Netral: <b>{m['neutral']}</b></span>
                        <span class='metric-pill-neg'>Komplain: <b>{m['negative']} ({m['negative_rate']:.0f}%)</b></span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# ==============================================================================
# MODUL 2: DEEP-DIVE ASPEK & SENTIMEN
# ==============================================================================
elif current_module == "Deep-Dive Aspek & Sentimen":
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
# MODUL 3: AI KITCHEN ACTION CHECKLIST & SOP
# ==============================================================================
elif current_module == "AI Kitchen Action Checklist":
    st.markdown("### AI Kitchen Action Checklist & Rekomendasi SOP")
    st.caption("Dihasilkan oleh LLM (Gemini/Groq) bila API key tersedia; tanpa key, digunakan katalog template terstruktur berbasis pola keluhan.")

    sample_complaints = {}
    for asp in ["kemasan", "rasa", "porsi", "harga", "pelayanan"]:
        if asp in filtered_df.columns:
            negs = filtered_df[filtered_df[asp] == "negative"]["review_text"].tolist()
            if negs:
                sample_complaints[asp] = [str(t) for t in negs[:3]]

    plan = action_engine.generate_action_plan(
        restaurant_name=selected_resto,
        evaluation_results=eval_results,
        sample_complaints=sample_complaints
    )

    if plan.get("generation_mode") == "llm":
        mode_label = f"LLM ({plan.get('llm_provider') or '-'})"
    else:
        mode_label = "Template (offline)"
    st.caption(f"Mode rekomendasi: {mode_label}")

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
        if st.button("Tambahkan ke Checklist", type="primary"):
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
                <b style='color: #15803D; font-size: 0.85rem; text-transform: uppercase;'>SOP Operasional Terverifikasi:</b>
                <p style='margin: 4px 0 0 0; font-size: 0.85rem; color: #44403C;'>{sop_item}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 4. Export & Download Center (Zero Emoji)
    st.markdown("#### Unduh Dokumen Checklist Dapur")
    st.caption("Ekspor checklist tindakan untuk dicetak dan ditempel di meja dapur atau dibagikan ke kru:")

    col_btn1, col_btn2, col_btn3 = st.columns(3)

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
            label="Unduh Format Teks (.txt)",
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
                label="Unduh Dokumen Resmi PDF (.pdf)",
                data=pdf_bytes,
                file_name=f"checklist_dapur_{selected_resto.lower().replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.caption(f"PDF Generator Notice: {e}")

    with col_btn3:
        action_export_df = pd.DataFrame([
            {"No": i+1, "Tindakan": item, "Status_Selesai": checked_status.get(i, False), "PIC": "Kru Dapur"}
            for i, item in enumerate(all_checklist)
        ])
        st.download_button(
            label="Unduh Tabel CSV (.csv)",
            data=action_export_df.to_csv(index=False),
            file_name=f"checklist_dapur_{selected_resto.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ==============================================================================
# MODUL 4: SINGLE REVIEW SIMULATOR (LIVE AI DEMO)
# ==============================================================================
elif current_module == "Single Review Simulator (Live Demo)":
    st.markdown("### Simulator Diagnostik Ulasan Tunggal (Live AI Demo)")
    st.caption(f"Uji coba engine ABSA aktif ({ACTIVE_ABSA_ENGINE_LABEL}) secara instan pada teks ulasan bebas:")

    st.markdown("#### 1. Pilih Preset Ulasan Simulasi Pitching:")
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)

    preset_texts = {
        "p1": "Ayamnya gurih renyah bumbunya mantap meresap, tapi kemasan mangkok tumpah kuah dan minyak sambal rembes ke kantong plastik. Driver nunggu 30 menit.",
        "p2": "Gelas kopinya kecil banget es batunya penuh 80%, toast makin tipis, harga 35rb kemahalan buat porsi segini.",
        "p3": "Lama banget pelayanannya, order mie ayam bakso nunggu 50 menit pas jam makan siang. Pelayan jutek kuah dingin keasinan.",
        "p4": "Bebek bumbu hitamnya juara dunia rempahnya medok daging empuk porsi jumbo kemasan besek bambu sangat rapi!"
    }

    with p_col1:
        if st.button("Mixed: Rasa vs Kemasan", key="sim_preset_1", type="secondary", use_container_width=True):
            st.session_state.simulator_text = preset_texts["p1"]
            st.rerun()

    with p_col2:
        if st.button("Porsi & Harga", key="sim_preset_2", type="secondary", use_container_width=True):
            st.session_state.simulator_text = preset_texts["p2"]
            st.rerun()

    with p_col3:
        if st.button("Pelayanan & Suhu", key="sim_preset_3", type="secondary", use_container_width=True):
            st.session_state.simulator_text = preset_texts["p3"]
            st.rerun()

    with p_col4:
        if st.button("Puas Bintang 5", key="sim_preset_4", type="secondary", use_container_width=True):
            st.session_state.simulator_text = preset_texts["p4"]
            st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    sim_input = st.text_area(
        "Ketik Kalimat Ulasan Konsumen (Bahasa Indonesia Sehari-hari):",
        value=st.session_state.simulator_text,
        height=100
    )

    if st.button("Bedah Aspek Ulasan Sekarang", key="sim_analyze_btn", type="primary", use_container_width=True):
        st.session_state.simulator_text = sim_input
        sim_res = pipeline.analyze_single_review(sim_input)
        
        st.markdown("---")
        st.markdown("#### 2. Hasil Ekstraksi NLP & Normalisasi Slang")

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
                    stat_msg = "Aspek tidak dibahas dalam ulasan."
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

        neg_detected = [asp.capitalize() for asp, d in aspects_map.items() if d["mentioned"] and d["sentiment"] == "negative"]
        if neg_detected:
            st.markdown(
                f"""
                <div class='ulas-card' style='background: #FFFDFB; border-left: 4px solid #C84B2F; margin-top: 14px;'>
                    <div style='display: flex; gap: 10px; align-items: flex-start;'>
                        <div style='width: 32px; height: 32px; background: #FFF0EB; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;'>
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#C84B2F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                            </svg>
                        </div>
                        <div>
                            <b style='color: #C84B2F; font-size: 0.9rem; text-transform: uppercase;'>Rekomendasi Tindakan Cepat (Instant Mitigation):</b>
                            <p style='margin: 4px 0 0 0; font-size: 0.85rem; color: #44403C;'>
                                Terdeteksi komplain operasional pada aspek <b>{', '.join(neg_detected)}</b>. 
                                Kru dapur disarankan segera memverifikasi SOP pengemasan anti-bocor dan memastikan suhu makanan sebelum diserahkan ke kurir pengantar.
                            </p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class='ulas-card' style='background: #FDFEFD; border-left: 4px solid #15803D; margin-top: 14px;'>
                    <div style='display: flex; gap: 10px; align-items: flex-start;'>
                        <div style='width: 32px; height: 32px; background: #DCFCE7; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;'>
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#15803D" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                                <polyline points="22 4 12 14.01 9 11.01"></polyline>
                            </svg>
                        </div>
                        <div>
                            <b style='color: #15803D; font-size: 0.9rem; text-transform: uppercase;'>Status Operasional Optimal:</b>
                            <p style='margin: 4px 0 0 0; font-size: 0.85rem; color: #44403C;'>
                                Tidak terdeteksi komplain operasional. Pertahankan konsistensi resep dan standar pelayanan dapur saat ini.
                            </p>
                        </div>
                    </div>
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
        <span><b>UlasRasa</b> &bull; AI Engineering Final Project (Batch 13) | Student ID: <b>REAENG13TQJLN</b> (Azura)</span>
        <span>Arsitektur: <b>IndoBERT Base (ABSA) + Generative LLM Action Engine</b></span>
    </div>
    """,
    unsafe_allow_html=True
)
