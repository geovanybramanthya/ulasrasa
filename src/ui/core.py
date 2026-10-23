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
from src.ui import labels


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

    # Kunci sesi khusus UI baru (Tahap 1; diizinkan PRD sebagai kunci UI).
    if "ui_data_mode" not in st.session_state:
        st.session_state.ui_data_mode = "Outlet Bawaan (Preset)"

    if "ui_panel_open" not in st.session_state:
        st.session_state.ui_panel_open = False

    if "ui_resto_select" not in st.session_state:
        st.session_state.ui_resto_select = None

    # Akun demo aktif (Adendum Revisi Landing 2026-10-23): None = belum
    # masuk (landing tampil); string = nama resto akun aktif atau
    # labels.BENCHMARK_LABEL untuk akun "Semua Outlet (Benchmark Industri)".
    if "active_account" not in st.session_state:
        st.session_state.active_account = None

    if "rincian_aspect" not in st.session_state:
        st.session_state.rincian_aspect = "Rasa"


def list_demo_accounts() -> list:
    """Daftar akun demo landing: 4 resto (alfabetis) + Benchmark terakhir.

    Mengembalikan list dict {name, count, df} dari dataset bawaan murni
    (load_default_dataset), BUKAN dari dataset sesi, agar landing selalu
    menampilkan data contoh asli (25 ulasan per resto, 100 gabungan).
    """
    df = load_default_dataset()
    accounts = []
    if not df.empty and "restaurant_name" in df.columns:
        for name in sorted(df["restaurant_name"].unique()):
            accounts.append({
                "name": name,
                "count": int((df["restaurant_name"] == name).sum()),
                "df": df[df["restaurant_name"] == name].copy(),
            })
    accounts.append({"name": labels.BENCHMARK_LABEL, "count": int(len(df)), "df": df.copy()})
    return accounts


def enter_account(name: str) -> None:
    """Callback klik kartu akun di landing: jadikan akun aktif.

    Dipakai sebagai on_click st.button (berjalan sebelum widget run
    berikutnya dibuat, jadi aman menulis kunci widget sesi). Dataset sesi
    direset ke dataset bawaan murni agar dashboard mulai bersih.
    """
    st.session_state.active_account = name
    st.session_state.ui_resto_select = name
    st.session_state.custom_reviews_df = load_default_dataset()
    st.session_state.custom_checklist_items = []
    st.session_state.ui_data_mode = labels.DATA_MODE_PRESET
    st.session_state.ui_panel_open = False
    st.session_state.active_module_name = labels.MODULE_CHOICES[0]
    st.session_state.pop("nav_pending", None)


def clear_account_session() -> None:
    """Callback tombol Ganti Akun: kembali ke landing, sesi kembali murni.

    Membersihkan akun aktif DAN dataset aktif sesi: unggahan CSV, ulasan
    hasil input manual, tindakan kustom, dan centang daftar aksi sesi
    hilang; dataset bawaan dimuat ulang dari CSV contoh.
    """
    for key in list(st.session_state.keys()):
        if key.startswith("action_chk_"):
            st.session_state.pop(key, None)
    st.session_state.pop("ui_csv_uploader", None)
    st.session_state.pop("nav_pending", None)
    st.session_state.pop("nav_pills", None)
    st.session_state.active_account = None
    st.session_state.ui_resto_select = None
    st.session_state.custom_reviews_df = load_default_dataset()
    st.session_state.custom_checklist_items = []
    st.session_state.ui_data_mode = labels.DATA_MODE_PRESET
    st.session_state.ui_panel_open = False
    st.session_state.active_module_name = labels.MODULE_CHOICES[0]


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
