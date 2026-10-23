"""Inti data & engine UI UlasRasa.

Berisi load_ai_engines() dan load_default_dataset() yang dipindah VERBATIM
dari app.py pra-perombakan, inisialisasi session state, dan pembangun
konteks data (compute_context) yang isinya persis blok evaluasi lama di
sidebar app.py (PRD Implementasi UI Bag. 2).

Satu penyesuaian mekanis yang terdokumentasi: load_default_dataset()
menghitung path CSV dari root repo karena file ini kini tinggal di
src/ui/ (bukan lagi di root repo seperti app.py lama).
"""

import os

import pandas as pd
import streamlit as st

from src.absa_pipeline import ABSAPipeline
from src.action_engine import ActionPlanEngine
from src.config import HEALTH_THRESHOLDS


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


@st.cache_data
def load_default_dataset() -> pd.DataFrame:
    """Memuat 100 sampel ulasan terkurasi dari dataset lokal."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_path = os.path.join(repo_root, "data", "sample_reviews.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()


def init_session_state() -> None:
    """Inisialisasi Session State (dipindah verbatim dari app.py)."""
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


def compute_context(filtered_df: pd.DataFrame, pipeline) -> dict:
    """Blok evaluasi bersama (verbatim dari sidebar app.py lama).

    Memanggil pipeline.evaluate_dataframe() tepat satu kali untuk
    dataframe terfilter final, lalu menurunkan status dan aspek terlemah
    dengan rumus yang persis sama seperti sebelumnya.
    """
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
    return {
        "eval_results": eval_results,
        "khs": khs,
        "breakdown": breakdown,
        "status_label": status_label,
        "status_class": status_class,
        "status_color": status_color,
        "weakest_aspect": weakest_aspect,
        "weakest_score": weakest_score,
    }
