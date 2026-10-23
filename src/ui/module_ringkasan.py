"""Modul Ringkasan (DESIGN.md Bag. 8) - penentu tone perombakan UI.

Susunan: 4 KartuKPI pastel bermicrocopy faktual -> HeroKHS (donat Plotly
di kartu gradasi hijau + label status persis + cip aspek prioritas +
peringatan aspek terlemah + CTA ke Rencana Aksi) -> grafik batang
horizontal skor kepuasan 5 aspek berwarna per aspek dengan garis batas
kritis 70 -> RelKeluhan interaktif maks 5 (klik membuka Modul Rincian
dengan aspek negatif pertama ulasan itu) -> KartuRincianAspekMini.

Semua angka dibaca dari ctx hasil compute_context (dihitung engine,
identik baseline); modul ini tidak menghitung ulang skor apa pun kecuali
persentase Ulasan Negatif sesuai definisi mengikat PRD 4.2.
Seluruh literal HTML ditulis rata kiri: baris terindentasi >= 4 spasi
di dalam markdown Streamlit terbaca sebagai blok kode.
"""

import streamlit as st

from src.config import ASPECT_WEIGHTS
from src.ui import charts, labels
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


def _keluhan_rows(filtered_df):
    """Baris rel keluhan (PRD 4.2): >=1 aspek negatif, review_id menurun, maks 5.

    Menghasilkan list (review_id, teks, aspek_negatif_pertama).
    """
    if filtered_df is None or filtered_df.empty:
        return []
    cols = [c for c in ASPECT_ORDER if c in filtered_df.columns]
    if not cols:
        return []
    neg_rows = filtered_df[filtered_df[cols].eq("negative").any(axis=1)]
    if "review_id" in neg_rows.columns:
        neg_rows = neg_rows.sort_values("review_id", ascending=False)
    hasil = []
    for rid, row in neg_rows.head(5).iterrows():
        first_neg = next((c for c in ASPECT_ORDER if str(row.get(c, "")) == "negative"), None)
        if first_neg is None:
            continue
        hasil.append((row.get("review_id", rid), str(row.get("review_text", "")), first_neg))
    return hasil


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

    # ---------------- Hero KHS ----------------
    neg_rate_w = float(breakdown.get(weakest_aspect, {}).get("negative_rate", 0.0))
    with st.container(key="hero"):
        h_donut, h_detail = st.columns([0.85, 1.9])
        with h_donut:
            st.plotly_chart(
                charts.build_khs_donut_figure(khs),
                width="stretch",
                config={"displayModeBar": False},
            )
        with h_detail:
            st.markdown("<div class='label-caps'>Skor Kesehatan Dapur</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='hero-status'>{status_label}</div>", unsafe_allow_html=True)
            if weakest_score < 75.0:
                st.markdown(
                    f"<div class='hero-note'>Perhatian: aspek <b>{weakest_aspect.capitalize()}</b> berada di bawah "
                    f"batas aman - skor kepuasan <b>{weakest_score:.1f}%</b> dengan tingkat keluhan "
                    f"<b>{neg_rate_w:.1f}%</b>.</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='hero-note'>Semua aspek berada di atas batas aman. Aspek terendah saat ini "
                    f"<b>{weakest_aspect.capitalize()}</b> dengan skor {weakest_score:.1f}%.</div>",
                    unsafe_allow_html=True,
                )
            st.markdown(
                f"<span class='hero-chip'>Prioritas: {weakest_aspect.capitalize()}</span>",
                unsafe_allow_html=True,
            )
            if st.button(labels.HERO_CTA, key="hero_cta_rencana", type="primary"):
                from src.ui.components import request_nav
                request_nav("AI Kitchen Action Checklist")
                st.rerun()

    # ---------------- Grafik batang aspek + Rel keluhan ----------------
    col_main, col_rel = st.columns([1.55, 1.0])
    with col_main:
        with st.container(key="chartcard"):
            st.markdown(
                f"<div class='card-title'>{labels.CHART_ASPEK_TITLE}</div>"
                f"<div class='card-sub'>{labels.CHART_ASPEK_SUB}</div>",
                unsafe_allow_html=True,
            )
            st.plotly_chart(
                charts.build_satisfaction_bar_figure(breakdown),
                width="stretch",
                config={"displayModeBar": False},
            )
        # Kartu rincian aspek mini (menjaga data P-M1 tetap terlihat)
        baris = []
        for asp in ASPECT_ORDER:
            m = breakdown.get(asp, {})
            accent, _tint = ASPECT_COLORS[asp]
            baris.append(
                f"<tr><td><span class='asp-dot' style='background: {accent};'></span><b>{asp.capitalize()}</b></td>"
                f"<td class='num'>{float(m.get('satisfaction_score', 0.0)):.1f}%</td>"
                f"<td class='num'>{ASPECT_WEIGHTS.get(asp.capitalize(), 0.15) * 100:.0f}%</td>"
                f"<td class='num'>{int(m.get('total_mentioned', 0))}</td>"
                f"<td class='num'>{int(m.get('positive', 0))}</td>"
                f"<td class='num'>{int(m.get('neutral', 0))}</td>"
                f"<td class='num'>{int(m.get('negative', 0))}</td></tr>"
            )
        mini_html = (
            "<div class='ulas-card'>"
            "<div class='card-title'>Angka Rincian per Aspek</div>"
            "<div class='card-sub'>Skor, bobot, dan jumlah ulasan yang menyebut tiap aspek.</div>"
            "<table class='mini-table'><tr><th>Aspek</th><th>Skor</th><th>Bobot</th>"
            "<th>Disebut</th><th>Positif</th><th>Netral</th><th>Negatif</th></tr>"
            + "".join(baris)
            + "</table></div>"
        )
        st.markdown(mini_html, unsafe_allow_html=True)

    with col_rel:
        with st.container(key="relcard"):
            st.markdown(
                f"<div class='card-title'>{labels.REL_KELUHAN_TITLE}</div>"
                f"<div class='card-sub'>{labels.REL_KELUHAN_SUB}</div>",
                unsafe_allow_html=True,
            )
            daftar = _keluhan_rows(filtered_df)
            if not daftar:
                st.markdown(
                    "<div class='card-sub'>Belum ada ulasan negatif pada data aktif. "
                    "Pertahankan kualitas dapurnya.</div>",
                    unsafe_allow_html=True,
                )
            for rid, text, first_neg in daftar:
                accent, tint = ASPECT_COLORS[first_neg]
                potong = (text[:140] + "...") if len(text) > 140 else text
                st.markdown(
                    f"<div class='rel-item'><div class='rel-text'>&quot;{potong}&quot;</div>"
                    f"<span class='chip' style='background: {tint}; color: {accent}; border: 1px solid {tint};'>{first_neg.capitalize()}</span> "
                    f"<span class='chip pill-neg'>Negatif</span></div>",
                    unsafe_allow_html=True,
                )
                if st.button("Lihat di Rincian Aspek", key=f"rel_btn_{rid}"):
                    from src.ui.components import request_nav
                    st.session_state.rincian_aspect = first_neg
                    request_nav("Deep-Dive Aspek & Sentimen")
                    st.rerun()
