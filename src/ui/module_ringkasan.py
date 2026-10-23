"""Modul 1: Ringkasan Eksekutif & Health Score.

Tahap 0: blok modul dipindah VERBATIM dari app.py lama (tampilan lama
 dipertahankan; pembangunan ulang sesuai DESIGN.md dilakukan Tahap 2).
"""

import streamlit as st

from src.config import ASPECT_WEIGHTS
from src.ui.charts import build_radar_figure


def render(ctx, pipeline, action_engine):
    filtered_df = ctx["filtered_df"]
    khs = ctx["khs"]
    breakdown = ctx["breakdown"]
    status_label = ctx["status_label"]
    status_class = ctx["status_class"]
    status_color = ctx["status_color"]
    weakest_aspect = ctx["weakest_aspect"]
    weakest_score = ctx["weakest_score"]

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
        fig_radar = build_radar_figure(breakdown)
        if fig_radar is not None:
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
