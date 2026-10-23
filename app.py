"""Aplikasi Web UlasRasa: Asisten Diagnostik Ulasan Kuliner & Rekomendasi Evaluasi Dapur UMKM.
Prototype Interaktif Berbasis NLP (IndoBERT ABSA) dan LLM Generatif.
Dirancang untuk demonstrasi langsung (live demo) dan pitching di hadapan mentor.
Ruangguru AI Engineering Bootcamp - Batch 13 | Student: Azura

Entry point ramping (Tahap 0 PRD Implementasi UI): seluruh tampilan dan
logika UI tinggal di src/ui/; file ini hanya mengorkestrasi urutan run
yang sama seperti app.py monolitik sebelumnya.
"""

import os

import streamlit as st

from src.ui import components, core, theme
from src.ui import module_coba, module_rencana, module_rincian, module_ringkasan
from src.ui.labels import MODULE_CHOICES

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
# 2. CSS (Tahap 0: CSS lama dipindah apa adanya ke src/ui/theme.py)
# ==============================================================================
theme.inject_old_css()

# ==============================================================================
# 3. ENGINE + SESSION STATE (verbatim, kini di src/ui/core.py)
# ==============================================================================
pipeline, action_engine, ACTIVE_ABSA_ENGINE_LABEL = core.load_ai_engines()

core.init_session_state()

# ==============================================================================
# 4-5. SIDEBAR (data + navigasi) DAN HEADER (verbatim, di src/ui/components.py)
# ==============================================================================
ctx = components.render_sidebar(pipeline, ACTIVE_ABSA_ENGINE_LABEL)
ctx["engine_label"] = ACTIVE_ABSA_ENGINE_LABEL

current_module = components.render_header(ctx)

# ==============================================================================
# DISPATCH MODUL (ID kanonis tidak berubah)
# ==============================================================================
if current_module == MODULE_CHOICES[0]:
    module_ringkasan.render(ctx, pipeline, action_engine)
elif current_module == MODULE_CHOICES[1]:
    module_rincian.render(ctx, pipeline, action_engine)
elif current_module == MODULE_CHOICES[2]:
    module_rencana.render(ctx, pipeline, action_engine)
elif current_module == MODULE_CHOICES[3]:
    module_coba.render(ctx, pipeline, action_engine)

components.render_footer()
