"""Aplikasi Web UlasRasa: Asisten Diagnostik Ulasan Kuliner & Rekomendasi Evaluasi Dapur UMKM.
Prototype Interaktif Berbasis NLP (IndoBERT ABSA) dan LLM Generatif.
Dirancang untuk demonstrasi langsung (live demo) dan pitching di hadapan mentor.
Ruangguru AI Engineering Bootcamp - Batch 13 | Student: Geovany Bramanthya Samuel Sihombing

Entry point ramping (PRD Implementasi UI): tampilan dan logika UI tinggal
di src/ui/. File ini mengorkestrasi urutan run: konfigurasi halaman ->
tema -> loading bermerek -> engine -> sesi -> landing (bila belum ada
akun demo aktif) ATAU shell dashboard (top bar -> header data -> dispatch
modul) -> footer. Alur akun mengikuti Adendum Revisi Landing 2026-10-23.
"""

import os

import streamlit as st

from src.ui import components, core, labels, theme
from src.ui import module_coba, module_landing, module_rencana, module_rincian, module_ringkasan
from src.ui.labels import MODULE_CHOICES

# ==============================================================================
# 1. KONFIGURASI HALAMAN (judul sesuai DESIGN.md Bag. 3 / PRD P-G1)
# ==============================================================================
favicon_path = os.path.join(os.path.dirname(__file__), "assets", "favicon.png")
st.set_page_config(
    page_title=labels.APP_TITLE,
    page_icon=favicon_path if os.path.exists(favicon_path) else "UR",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# 2. TEMA (token DESIGN.md, kini di src/ui/theme.py)
# ==============================================================================
theme.inject_theme()

# ==============================================================================
# 3. ENGINE (kartu loading bermerek tampil lebih dulu - PRD 4.1)
# ==============================================================================
_loading = components.loading_placeholder()
pipeline, action_engine, ACTIVE_ABSA_ENGINE_LABEL = core.load_ai_engines()
_loading.empty()

core.init_session_state()

# ==============================================================================
# 4. LANDING ATAU SHELL DASHBOARD (Adendum Revisi Landing 2026-10-23)
# Belum ada akun aktif -> landing saja (tanpa top bar dashboard, tanpa
# header data, tanpa dispatch modul). Klik kartu akun mengisi
# session_state.active_account lewat callback, lalu run berikutnya masuk
# dashboard khusus akun tersebut.
# ==============================================================================
if not st.session_state.get("active_account"):
    module_landing.render(pipeline)
    components.render_footer()
else:
    # ==========================================================================
    # 5. SHELL: TOP BAR + HEADER DATA (fungsi data kini di components.py)
    # ==========================================================================
    components.sync_nav_pills()
    components.render_topbar(ACTIVE_ABSA_ENGINE_LABEL)

    ctx = components.render_data_header(pipeline)
    ctx["engine_label"] = ACTIVE_ABSA_ENGINE_LABEL

    # ==========================================================================
    # DISPATCH MODUL (ID kanonis tidak berubah)
    # ==========================================================================
    current_module = st.session_state.active_module_name
    if current_module == MODULE_CHOICES[0]:
        module_ringkasan.render(ctx, pipeline, action_engine)
    elif current_module == MODULE_CHOICES[1]:
        module_rincian.render(ctx, pipeline, action_engine)
    elif current_module == MODULE_CHOICES[2]:
        module_rencana.render(ctx, pipeline, action_engine)
    elif current_module == MODULE_CHOICES[3]:
        module_coba.render(ctx, pipeline, action_engine)

    components.render_footer()
