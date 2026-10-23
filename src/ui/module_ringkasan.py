"""Modul Ringkasan - Tahap 1: kerangka ber-data asli.

Kerangka kartu sesuai DESIGN.md Bag. 8 dengan nilai sesungguhnya dari
konteks (tidak ada angka tiruan): 4 KartuKPI pastel, HeroKHS ringkas
(donat Plotly + CTA resmi dibangun Tahap 2; CTA di sini sudah berfungsi),
bar skor aspek sederhana dari breakdown, dan rel keluhan terbaru.
Figur-figur Plotly resmi menggantikan bar sederhana pada Tahap 2.

Catatan teknis: seluruh literal HTML ditulis rata kiri (kolom 0) karena
baris terindentasi >= 4 spasi di dalam markdown Streamlit terbaca
sebagai blok kode dan tampil mentah.
"""

import streamlit as st

from src.ui import labels
from src.ui.labels import ASPECT_ORDER
from src.ui.theme import ASPECT_COLORS

_ICONS = {
    "khs": "<svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#15803D' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M22 12h-4l-3 9L9 3l-3 9H2'></path></svg>",
    "total": "<svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#0284C7' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z'></path></svg>",
    "neg": "<svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#B42318' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z'></path><line x1='12' y1='9' x2='12' y2='13'></line><line x1='12' y1='17' x2='12.01' y2='17'></line></svg>",
}


def _pct_negative(filtered_df) -> float:
    """Definisi mengikat PRD 4.2: proporsi baris dengan >=1 aspek 'negative'."""
    if filtered_df is None or len(filtered_df) == 0:
        return 0.0
    cols = [c for c in ASPECT_ORDER if c in filtered_df.columns]
    if not cols:
        return 0.0
    mask = filtered_df[cols].eq("negative").any(axis=1)
    return float(mask.mean() * 100.0)


def render(ctx, pipeline, action_engine):
    filtered_df = ctx["filtered_df"]
    khs = ctx["khs"]
    breakdown = ctx["breakdown"]
    status_label = ctx["status_label"]
    weakest_aspect = ctx["weakest_aspect"]
    weakest_score = ctx["weakest_score"]

    n_total = len(filtered_df)
    pct_neg = _pct_negative(filtered_df)
    w_accent, w_tint = ASPECT_COLORS.get(weakest_aspect, ("#B42318", "#FDECEC"))
    w_icon = (
        "<svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='" + w_accent + "' stroke-width='2' "
        "stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='9'></circle>"
        "<circle cx='12' cy='12' r='4.5'></circle><circle cx='12' cy='12' r='1' fill='" + w_accent + "'></circle></svg>"
    )

    # ---------------- 4 Kartu KPI pastel ----------------
    kpi_html = f"""<div class='kpi-grid'>
<div class='kpi-card' style='background: #E8F9F0;'>
<div class='kpi-icon-chip'>{_ICONS['khs']}</div>
<div class='kpi-label'>{labels.KPI_KHS_LABEL}</div>
<div class='kpi-value'>{khs:.1f}%</div>
<div class='kpi-micro'>Status saat ini: {status_label}</div>
</div>
<div class='kpi-card' style='background: #E0F2FE;'>
<div class='kpi-icon-chip'>{_ICONS['total']}</div>
<div class='kpi-label'>{labels.KPI_TOTAL_LABEL}</div>
<div class='kpi-value'>{n_total}</div>
<div class='kpi-micro'>Dari data yang sedang aktif</div>
</div>
<div class='kpi-card' style='background: #FDECEC;'>
<div class='kpi-icon-chip'>{_ICONS['neg']}</div>
<div class='kpi-label'>{labels.KPI_NEG_LABEL}</div>
<div class='kpi-value'>{pct_neg:.1f}%</div>
<div class='kpi-micro'>dari {n_total} ulasan</div>
</div>
<div class='kpi-card' style='background: {w_tint};'>
<div class='kpi-icon-chip'>{w_icon}</div>
<div class='kpi-label'>{labels.KPI_KRITIS_LABEL}</div>
<div class='kpi-value'>{weakest_aspect.capitalize()}</div>
<div class='kpi-micro'>Skor kepuasan <span class='num'>{weakest_score:.1f}%</span> - terendah dari 5 aspek</div>
</div>
</div>"""
    st.markdown(kpi_html, unsafe_allow_html=True)

    # ---------------- Hero KHS (kerangka: angka + status + CTA berfungsi) ----------------
    neg_rate_w = breakdown.get(weakest_aspect, {}).get("negative_rate", 0.0)
    with st.container(key="hero"):
        h_left, h_right = st.columns([1.0, 1.6])
        with h_left:
            st.markdown("<div class='label-caps'>Skor Kesehatan Dapur</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='hero-score-big'>{khs:.1f}%</div>", unsafe_allow_html=True)
        with h_right:
            st.markdown(f"<div class='hero-status'>{status_label}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='hero-note'>Aspek <b>{weakest_aspect.capitalize()}</b> paling butuh perhatian: "
                f"skor kepuasan {weakest_score:.1f}% dengan tingkat keluhan {neg_rate_w:.1f}%.</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span class='hero-chip'>Prioritas: {weakest_aspect.capitalize()}</span>",
                unsafe_allow_html=True,
            )
            if st.button(labels.HERO_CTA, key="hero_cta_rencana", type="primary"):
                from src.ui.components import sync_nav_pills
                st.session_state.active_module_name = "AI Kitchen Action Checklist"
                sync_nav_pills()
                st.rerun()

    # ---------------- Grafik aspek (kerangka bar sederhana) + Rel keluhan ----------------
    col_main, col_rel = st.columns([1.55, 1.0])
    with col_main:
        baris = []
        for asp in ASPECT_ORDER:
            m = breakdown.get(asp, {})
            score = float(m.get("satisfaction_score", 0.0))
            accent, _tint = ASPECT_COLORS[asp]
            baris.append(
                f"<div style='margin-bottom: 13px;'>"
                f"<div style='display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;'>"
                f"<b>{asp.capitalize()}</b><span class='num'>{score:.1f}%</span></div>"
                f"<div class='mini-bar-track'><div class='mini-bar-fill' style='width: {min(score, 100):.1f}%; background: {accent};'></div></div>"
                f"</div>"
            )
        chart_html = (
            "<div class='ulas-card'>"
            f"<div class='card-title'>{labels.CHART_ASPEK_TITLE}</div>"
            f"<div class='card-sub'>{labels.CHART_ASPEK_SUB}</div>"
            "<div style='height: 10px;'></div>"
            + "".join(baris)
            + "</div>"
        )
        st.markdown(chart_html, unsafe_allow_html=True)
    with col_rel:
        items = []
        if not filtered_df.empty:
            cols = [c for c in ASPECT_ORDER if c in filtered_df.columns]
            neg_rows = filtered_df[filtered_df[cols].eq("negative").any(axis=1)] if cols else filtered_df.iloc[0:0]
            if "review_id" in neg_rows.columns:
                neg_rows = neg_rows.sort_values("review_id", ascending=False)
            for _, row in neg_rows.head(5).iterrows():
                first_neg = next((c for c in ASPECT_ORDER if str(row.get(c, "")) == "negative"), None)
                if first_neg is None:
                    continue
                accent, tint = ASPECT_COLORS[first_neg]
                text = str(row.get("review_text", ""))
                text = (text[:140] + "...") if len(text) > 140 else text
                items.append(
                    f"<div class='rel-item'>"
                    f"<div class='rel-text'>&quot;{text}&quot;</div>"
                    f"<span class='chip' style='background: {tint}; color: {accent}; border: 1px solid {tint};'>{first_neg.capitalize()}</span> "
                    f"<span class='chip pill-neg'>Negatif</span>"
                    f"</div>"
                )
        body = "".join(items) if items else "<div class='card-sub'>Belum ada ulasan negatif pada data aktif. Pertahankan kualitas dapurnya.</div>"
        rel_html = (
            "<div class='ulas-card'>"
            f"<div class='card-title'>{labels.REL_KELUHAN_TITLE}</div>"
            f"<div class='card-sub'>{labels.REL_KELUHAN_SUB}</div>"
            "<div style='height: 10px;'></div>"
            + body
            + "</div>"
        )
        st.markdown(rel_html, unsafe_allow_html=True)
