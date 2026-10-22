"""
Tab 4 Component: Single Review Simulator
Interactive Real-Time Inference Demo

Memakai SATU engine ABSA resmi proyek: src.absa_pipeline.ABSAPipeline
(skema 5 aspek: rasa, porsi, harga, kemasan, pelayanan). Rekomendasi
operasional untuk ulasan negatif dihasilkan oleh
src.action_engine.ActionPlanEngine dari hasil evaluasi pipeline yang sama.
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any

import pandas as pd

from src.absa_pipeline import ABSAPipeline
from src.action_engine import ActionPlanEngine
from src.config import SENTIMENT_COLORS

PRESET_REVIEWS = [
    "Kuah soto dagingnya gurih mantap dan dagingnya empuk banget!",
    "Sup buntut dingin sekali pas sampai di meja dan kuahnya keasinan parah.",
    "Mangkok kuahnya tumpah di jalan, plastiknya rembes sampai basah semua, parah banget.",
    "Pelayanan sangat ramah tapi makanan butuh 40 menit baru keluar, tolong dipercepat.",
    "Harga seporsi nasi goreng 65 ribu tapi porsinya cuma sedikit sekali, kurang worth it.",
    "Ayamnya enak banget gurih, tapi sambalnya dikit dan kemasannya tumpah di jalan."
]

_SENTIMENT_ID = {
    "positive": "Positif",
    "neutral": "Netral",
    "negative": "Negatif",
}


@st.cache_resource
def _get_engines():
    """Singleton pipeline ABSA + action engine (konsisten dengan app.py)."""
    return ABSAPipeline(), ActionPlanEngine()


def init_simulator_state():
    """Inisialisasi history review simulator di session state."""
    if "sim_history" not in st.session_state:
        st.session_state.sim_history = []


def _summarize(aspects: Dict[str, Any]) -> Dict[str, Any]:
    """Ringkasan satu ulasan dari hasil per-aspek ABSAPipeline.

    Mengembalikan aspek yang mentioned (urut skema resmi), polaritas
    dominan (Negatif bila ada satu saja aspek negatif, lalu Positif,
    lalu Netral), dan confidence representatifnya.
    """
    mentioned = [
        (aspect, data)
        for aspect, data in aspects.items()
        if data.get("mentioned")
    ]

    def _max_conf(target: str) -> float:
        confs = [d["confidence"] for _, d in mentioned if d["sentiment"] == target]
        return max(confs) if confs else 0.0

    if any(d["sentiment"] == "negative" for _, d in mentioned):
        overall, conf = "Negatif", _max_conf("negative")
    elif any(d["sentiment"] == "positive" for _, d in mentioned):
        overall, conf = "Positif", _max_conf("positive")
    elif mentioned:
        overall, conf = "Netral", _max_conf("neutral")
    else:
        overall, conf = "Netral", 0.0

    return {"mentioned": mentioned, "overall": overall, "confidence": conf}


def render_tab4():
    """Merender Tab 4: Single Review Simulator untuk inferensi real-time."""
    init_simulator_state()
    pipeline, action_engine = _get_engines()

    st.markdown("### Single Review Simulator")
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
        analyze_clicked = st.button("Analisis Ulasan", type="primary", use_container_width=True)

    if analyze_clicked and review_input.strip():
        # Lakukan inferensi dengan engine ABSA resmi (multi-aspek)
        with st.spinner("Menjalankan pipeline NLP inferensi..."):
            result = pipeline.analyze_single_review(review_input)

        summary = _summarize(result["aspects"])
        mentioned = summary["mentioned"]
        aspect_label = ", ".join(a.capitalize() for a, _ in mentioned) if mentioned else "Tidak ada"

        # Simpan ke history session state
        st.session_state.sim_history.insert(0, {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "text": review_input,
            "aspect": aspect_label,
            "sentiment": summary["overall"],
            "conf": summary["confidence"]
        })

        st.markdown("---")
        st.markdown("#### Hasil Prediksi Model")

        # 2. Output KPI Metric Cards
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric(
                label="Aspek Operasional Terdeteksi",
                value=aspect_label,
                delta=f"{len(mentioned)} aspek terdeteksi"
            )
        with col_res2:
            sent = summary["overall"]
            st.metric(
                label="Polaritas Dominan",
                value=sent,
                delta=f"Keyakinan {int(summary['confidence'] * 100)}%",
                delta_color="normal" if sent == "Positif" else ("off" if sent == "Netral" else "inverse")
            )
        with col_res3:
            st.write("**Detail Sentimen per Aspek:**")
            if mentioned:
                for aspect, data in mentioned:
                    label = _SENTIMENT_ID.get(data["sentiment"], data["sentiment"])
                    st.caption(f"{aspect.capitalize()}: {label} ({int(data['confidence'] * 100)}%)")
                    st.progress(float(data["confidence"]))
            else:
                st.caption("Tidak ada aspek operasional yang terdeteksi pada ulasan ini.")

        # 3. Rekomendasi Respon AI Kitchen
        st.markdown("#### Rekomendasi Tindakan Operasional Dapur:")
        negative_aspects = [a for a, d in mentioned if d["sentiment"] == "negative"]
        if negative_aspects:
            # Rekomendasi resmi dari ActionPlanEngine atas evaluasi pipeline
            evaluation = pipeline.evaluate_dataframe(pd.DataFrame({"review_text": [review_input]}))
            plan = action_engine.generate_action_plan(
                restaurant_name="Simulator UlasRasa",
                evaluation_results=evaluation,
                sample_complaints=[review_input]
            )
            lines = [
                f"**Kitchen Health Score ulasan ini: {plan['overall_health_score']:.1f}%** - "
                f"area prioritas: {', '.join(plan['priority_risk_areas'])}",
                "",
                "**Analisis Akar Masalah:**",
            ]
            lines += [f"- {rc}" for rc in plan["root_cause_analysis"]]
            lines.append("")
            lines.append("**Checklist Tindakan:**")
            lines += [f"{i}. {item}" for i, item in enumerate(plan["kitchen_action_checklist"], 1)]
            lines.append("")
            lines.append("**Rekomendasi SOP:**")
            lines += [f"- {sop}" for sop in plan["sop_recommendations"]]
            st.error("\n".join(lines))
        elif summary["overall"] == "Positif":
            positif = ", ".join(a.capitalize() for a, d in mentioned if d["sentiment"] == "positive")
            st.success(f"[OPTIMAL] Pertahankan standar konsistensi pada aspek {positif}. Berikan apresiasi kepada tim dapur/layanan yang bertugas!")
        elif mentioned:
            st.info("[INFO] Lakukan review berkala pada aspek yang disebut untuk meningkatkan persepsi pelanggan menuju rating 5 bintang.")
        else:
            st.info("Tidak ada aspek operasional (Rasa, Porsi, Harga, Kemasan, Pelayanan) yang terdeteksi pada ulasan ini. Coba ulasan yang menyebut rasa, porsi, harga, kemasan, atau pelayanan secara lebih spesifik.")

    # 4. Riwayat Simulasi
    if st.session_state.sim_history:
        with st.expander(f"Riwayat Simulasi ({len(st.session_state.sim_history)} item)", expanded=False):
            for item in st.session_state.sim_history[:5]:
                st.markdown(f"**[{item['timestamp']}]** `{item['aspect']}` | `{item['sentiment']}` ({int(item['conf']*100)}%) - *\"{item['text']}\"*")
