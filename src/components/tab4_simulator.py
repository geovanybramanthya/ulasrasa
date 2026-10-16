"""
Tab 4 Component: Single Review Simulator
Interactive Real-Time Inference Demo
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any

from src.models.inference import get_inference_engine
from src.config import SENTIMENT_COLORS

PRESET_REVIEWS = [
    "Kuah soto dagingnya gurih mantap dan dagingnya empuk banget!",
    "Sup buntut dingin sekali pas sampai di meja dan kuahnya keasinan parah.",
    "Ada sehelai rambut di dalam mangkuk bakso saya, sangat menjijikkan tolong jaga kebersihan!",
    "Pelayanan sangat ramah tapi makanan butuh 40 menit baru keluar, tolong dipercepat.",
    "Harga seporsi nasi goreng 65 ribu tapi porsinya cuma sedikit sekali, kurang worth it.",
    "Tempatnya estetik dan lagunya tenang, enak banget buat ngobrol lama."
]

def init_simulator_state():
    """Inisialisasi history review simulator di session state."""
    if "sim_history" not in st.session_state:
        st.session_state.sim_history = []

def render_tab4():
    """Merender Tab 4: Single Review Simulator untuk inferensi real-time."""
    init_simulator_state()
    engine = get_inference_engine()

    st.markdown("### 🧪 Single Review Simulator")
    st.caption("Uji coba inferensi real-time untuk memprediksi aspek kuliner, polaritas sentimen, dan respon dapur otomatis.")

    # 1. Preset Selector & Text Input Area
    preset_choice = st.selectbox(
        "Pilih contoh ulasan cepat (atau ketik ulasan kustom di bawah):",
        ["-- Ketik Ulasan Sendiri --"] + PRESET_REVIEWS
    )

    default_text = "" if preset_choice == "-- Ketik Ulasan Sendiri --" else preset_choice
    review_input = st.text_area(
        label="Teks Ulasan Pelanggan:",
        value=default_text,
        height=100,
        placeholder="Contoh: Ayam bakarnya sangat enak, bumbu manis gurih meresap tapi sambalnya kurang pedas..."
    )

    col_btn, col_clear = st.columns([1, 4])
    with col_btn:
        analyze_clicked = st.button("⚡ Analisis Ulasan", type="primary", use_container_width=True)

    if analyze_clicked and review_input.strip():
        # Lakukan inferensi
        with st.spinner("Menjalankan pipeline NLP inferensi..."):
            result = engine.predict(review_input)

        # Simpan ke history session state
        st.session_state.sim_history.insert(0, {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "text": review_input,
            "aspect": result["aspect"],
            "sentiment": result["sentiment"],
            "conf": result["sentiment_confidence"]
        })

        st.markdown("---")
        st.markdown("#### 🎯 Hasil Prediksi Model")

        # 2. Output KPI Metric Cards
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric(
                label="Dimensi Aspek Terdeteksi",
                value=result["aspect"],
                delta=f"Keyakinan {int(result['aspect_confidence'] * 100)}%"
            )
        with col_res2:
            sent = result["sentiment"]
            st.metric(
                label="Polaritas Sentimen",
                value=sent,
                delta=f"Probabilitas {int(result['sentiment_confidence'] * 100)}%",
                delta_color="normal" if sent == "Positif" else ("off" if sent == "Netral" else "inverse")
            )
        with col_res3:
            st.write("**Distribusi Probabilitas:**")
            probs = result["probabilities"]
            for s_label in ["Positif", "Netral", "Negatif"]:
                val = probs.get(s_label, 0.0)
                st.caption(f"{s_label}: {int(val * 100)}%")
                st.progress(val)

        # 3. Rekomendasi Respon AI Kitchen
        st.markdown("#### 👨‍🍳 Rekomendasi Tindakan Operasional Dapur:")
        if result["sentiment"] == "Negatif":
            st.error(result["recommendation"])
        elif result["sentiment"] == "Positif":
            st.success(result["recommendation"])
        else:
            st.info(result["recommendation"])

    # 4. Riwayat Simulasi
    if st.session_state.sim_history:
        with st.expander(f"📜 Riwayat Simulasi ({len(st.session_state.sim_history)} item)", expanded=False):
            for item in st.session_state.sim_history[:5]:
                st.markdown(f"**[{item['timestamp']}]** `{item['aspect']}` | `{item['sentiment']}` ({int(item['conf']*100)}%) — *\"{item['text']}\"*")
