"""Modul Rincian Aspek (DESIGN.md Bag. 8 + PRD 4.3, Tahap 3).

Susunan: PillPemilihAspek (mengikuti sesi rincian_aspect dari klik
RelKeluhan di Modul Ringkasan) -> AngkaHitungAspek (stat-grid 4 kartu
dari breakdown aspek terpilih) -> donat distribusi sentimen + grafik
kata keluhan dalam dua kartu sejajar -> kartu komposisi sentimen semua
aspek -> dua kolom contoh ulasan positif / negatif -> kartu tabel
semua ulasan dengan saringan polaritas + menu.

Semua angka dan label dibaca dari breakdown / filtered_df di ctx
(identik baseline, paritas P-M3 s.d. P-M6); modul ini tidak menghitung
ulang skor apa pun. Cara hitung kata keluhan disalin persis dari versi
lama: clean_text + Counter atas ulasan negatif aspek terpilih dengan
stop_set yang sama. Seluruh literal HTML ditulis rata kiri: baris
terindentasi >= 4 spasi di dalam markdown Streamlit terbaca sebagai
blok kode.
"""

import html
from collections import Counter

import streamlit as st

from src.preprocessing import clean_text
from src.ui import charts, labels
from src.ui.labels import ASPECT_LABELS, ASPECT_ORDER
from src.ui.theme import ASPECT_COLORS


def _mini_pill(value):
    """Pill mini label sentimen satu aspek untuk tabel semua ulasan."""
    v = str(value).lower()
    if v == "positive":
        return "<span class='mini-pill pill-pos'>Positif</span>"
    if v == "negative":
        return "<span class='mini-pill pill-neg'>Negatif</span>"
    if v == "neutral":
        return "<span class='mini-pill pill-neu'>Netral</span>"
    return "<span class='mini-pill pill-muted'>-</span>"


def _review_card_html(row):
    """Kartu contoh ulasan: teks apa adanya + meta menu dan ID."""
    teks = html.escape(str(row.get("review_text", "")))
    menu = html.escape(str(row.get("menu_item", "Menu Umum")))
    rid = html.escape(str(row.get("review_id", "-")))
    return (
        "<div class='review-card'>"
        f"<div class='review-text'>{teks}</div>"
        f"<div class='review-meta'>Menu: {menu} - ID #{rid}</div>"
        "</div>"
    )


def _render_contoh(col, title, rows):
    """Satu kolom contoh ulasan (positif atau negatif), maks 3 kartu."""
    with col:
        st.markdown(
            f"<div class='card-title'>{title}</div>",
            unsafe_allow_html=True,
        )
        if rows.empty:
            st.markdown(
                f"<div class='card-sub'>{labels.RINCIAN_CONTOH_EMPTY}</div>",
                unsafe_allow_html=True,
            )
        else:
            for _, row in rows.iterrows():
                st.markdown(_review_card_html(row), unsafe_allow_html=True)


def render(ctx, pipeline, action_engine):
    filtered_df = ctx["filtered_df"]
    breakdown = ctx["breakdown"]

    # ---------------- PillPemilihAspek ----------------
    # Pola selectbox Fase 1: default diambil dari sesi rincian_aspect
    # (diisi klik RelKeluhan) tanpa key widget, lalu hasil pilihan
    # ditulis balik ke sesi sebagai id lowercase.
    _options = ["Rasa", "Porsi", "Harga", "Kemasan", "Pelayanan"]
    _default_label = str(st.session_state.get("rincian_aspect", "rasa")).capitalize()
    if _default_label not in _options:
        _default_label = "Rasa"
    _pill = st.pills(
        labels.RINCIAN_PILL_LABEL,
        options=_options,
        default=_default_label,
        selection_mode="single",
    )
    selected_aspect = (_pill or _default_label).lower()
    st.session_state.rincian_aspect = selected_aspect

    aspect_data = breakdown.get(selected_aspect, {})
    total_mentioned = int(aspect_data.get("total_mentioned", 0))
    positive = int(aspect_data.get("positive", 0))
    neutral = int(aspect_data.get("neutral", 0))
    negative = int(aspect_data.get("negative", 0))
    positive_pct = aspect_data.get("positive", 0) / (aspect_data.get("total_mentioned", 1) or 1) * 100
    negative_rate = float(aspect_data.get("negative_rate", 0.0))

    # ---------------- AngkaHitungAspek ----------------
    stat_html = f"""<div class='stat-grid'>
<div class='stat-card'><div class='stat-value'>{total_mentioned}</div><div class='stat-label'>{labels.RINCIAN_STAT_MENTIONED}</div></div>
<div class='stat-card'><div class='stat-value'>{positive} <span style='font-size: 0.82rem; color: #64756B;'>({positive_pct:.0f}%)</span></div><div class='stat-label'>{labels.RINCIAN_STAT_POS}</div></div>
<div class='stat-card'><div class='stat-value'>{neutral}</div><div class='stat-label'>{labels.RINCIAN_STAT_NEU}</div></div>
<div class='stat-card'><div class='stat-value'>{negative} <span style='font-size: 0.82rem; color: #64756B;'>({negative_rate:.0f}%)</span></div><div class='stat-label'>{labels.RINCIAN_STAT_NEG}</div></div>
</div>"""
    st.markdown(stat_html, unsafe_allow_html=True)

    # ---------------- Donat distribusi + kata keluhan ----------------
    col_donat, col_kata = st.columns(2)

    with col_donat:
        with st.container(key="card_rincian_donat"):
            st.markdown(
                f"<div class='card-title'>{labels.RINCIAN_DONUT_TITLE}</div>"
                f"<div class='card-sub'>{labels.RINCIAN_DONUT_SUB}</div>",
                unsafe_allow_html=True,
            )
            st.plotly_chart(
                charts.build_distribution_donut_figure(positive, neutral, negative),
                width="stretch",
                config={"displayModeBar": False},
            )

    with col_kata:
        with st.container(key="card_rincian_kata"):
            st.markdown(
                f"<div class='card-title'>{labels.RINCIAN_KATA_TITLE}</div>"
                f"<div class='card-sub'>{labels.RINCIAN_KATA_SUB}</div>",
                unsafe_allow_html=True,
            )
            if selected_aspect in filtered_df.columns:
                neg_texts = filtered_df[filtered_df[selected_aspect] == "negative"]["review_text"].tolist()
                words = []
                stop_set = {
                    "yang", "dan", "di", "ini", "itu", "ke", "dari", "untuk", "pada", "adalah",
                    "dengan", "saya", "kami", "anda", "dia", "mereka", "juga", "karena", "tetapi",
                    "sudah", "bisa", "akan", "ada", "tidak", "jadi", "hanya", "sangat", "lebih",
                    "banget", "buat", "aja", "nya", "ya", "sih", "kok", "lah", "deh", "pun", "bgt", "ga", "gak"
                }
                for t in neg_texts:
                    cleaned_t = clean_text(str(t))
                    toks = [w for w in cleaned_t.split() if len(w) >= 3 and w not in stop_set]
                    words.extend(toks)

                c = Counter(words)
                top_words = c.most_common(6)

                if top_words:
                    accent_hex = ASPECT_COLORS.get(selected_aspect, ("#B42318", "#FDECEC"))[0]
                    st.plotly_chart(
                        charts.build_keyword_figure(top_words, accent_hex),
                        width="stretch",
                        config={"displayModeBar": False},
                    )
                else:
                    st.markdown(
                        f"<div class='card-sub'>{labels.RINCIAN_KATA_EMPTY}</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("Aspek tidak ditemukan dalam dataset.")

    # ---------------- Komposisi sentimen semua aspek ----------------
    with st.container(key="card_rincian_komposisi"):
        st.markdown(
            f"<div class='card-title'>{labels.RINCIAN_KOMP_TITLE}</div>"
            f"<div class='card-sub'>{labels.RINCIAN_KOMP_SUB}</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            charts.build_composition_figure(breakdown),
            width="stretch",
            config={"displayModeBar": False},
        )

    # ---------------- Contoh ulasan positif / negatif ----------------
    if selected_aspect in filtered_df.columns:
        pos_rows = filtered_df[filtered_df[selected_aspect] == "positive"].head(3)
        neg_rows = filtered_df[filtered_df[selected_aspect] == "negative"].head(3)
    else:
        pos_rows = filtered_df.iloc[0:0]
        neg_rows = filtered_df.iloc[0:0]
    col_pos, col_neg = st.columns(2)
    _render_contoh(col_pos, labels.RINCIAN_CONTOH_POS, pos_rows)
    _render_contoh(col_neg, labels.RINCIAN_CONTOH_NEG, neg_rows)

    # ---------------- Tabel semua ulasan ----------------
    with st.container(key="card_rincian_tabel"):
        st.markdown(
            f"<div class='card-title'>{labels.RINCIAN_TABEL_TITLE}</div>"
            f"<div class='card-sub'>{labels.RINCIAN_TABEL_SUB}</div>",
            unsafe_allow_html=True,
        )

        col_f1, col_f2 = st.columns([1, 1])
        with col_f1:
            sent_filter = st.selectbox(
                labels.RINCIAN_FILTER_POL_LABEL,
                labels.RINCIAN_FILTER_OPTIONS,
                index=1
            )
        with col_f2:
            all_menus = [labels.RINCIAN_MENU_ALL]
            if "menu_item" in filtered_df.columns:
                all_menus += sorted(list(filtered_df["menu_item"].dropna().unique()))
            menu_filter = st.selectbox(labels.RINCIAN_FILTER_MENU_LABEL, all_menus)

        sub_df = filtered_df.copy()
        if selected_aspect in sub_df.columns:
            if sent_filter == labels.RINCIAN_FILTER_OPTIONS[1]:
                sub_df = sub_df[sub_df[selected_aspect] == "negative"]
            elif sent_filter == labels.RINCIAN_FILTER_OPTIONS[2]:
                sub_df = sub_df[sub_df[selected_aspect] == "positive"]
            elif sent_filter == labels.RINCIAN_FILTER_OPTIONS[3]:
                sub_df = sub_df[sub_df[selected_aspect] == "neutral"]
            else:
                sub_df = sub_df[sub_df[selected_aspect] != "not_mentioned"]

        if menu_filter != labels.RINCIAN_MENU_ALL and "menu_item" in sub_df.columns:
            sub_df = sub_df[sub_df["menu_item"] == menu_filter]

        st.caption(labels.RINCIAN_COUNT_LINE.format(n=len(sub_df)))

        if not sub_df.empty:
            header = (
                "<tr><th>Ulasan</th>"
                + "".join(f"<th>{ASPECT_LABELS[a]}</th>" for a in ASPECT_ORDER)
                + "</tr>"
            )
            baris = []
            for _, row in sub_df.iterrows():
                teks = html.escape(str(row.get("review_text", "")))
                menu = html.escape(str(row.get("menu_item", "Menu Umum")))
                outlet = html.escape(str(row.get("restaurant_name", "-")))
                rid = html.escape(str(row.get("review_id", "-")))
                sel_aspek = "".join(
                    f"<td>{_mini_pill(row.get(a, ''))}</td>" for a in ASPECT_ORDER
                )
                baris.append(
                    "<tr>"
                    f"<td><div class='review-text'>{teks}</div>"
                    f"<div class='review-meta'>Menu: {menu} - Outlet: {outlet} - ID #{rid}</div></td>"
                    f"{sel_aspek}"
                    "</tr>"
                )
            tabel_html = (
                "<div class='table-wrap'><table class='data-table'>"
                + header
                + "".join(baris)
                + "</table></div>"
            )
            st.markdown(tabel_html, unsafe_allow_html=True)
        else:
            st.info(labels.RINCIAN_EMPTY)
