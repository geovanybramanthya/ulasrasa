"""Modul 4: Single Review Simulator (Live Demo).

Tahap 0: blok modul dipindah VERBATIM dari app.py lama.
"""

import streamlit as st


def render(ctx, pipeline, action_engine):
    ACTIVE_ABSA_ENGINE_LABEL = ctx["engine_label"]

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
