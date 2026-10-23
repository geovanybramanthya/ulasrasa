"""Modul 4: Coba Ulasan (Simulator Ulasan Tunggal).

Tahap 5 perombakan UI (DESIGN.md Bag. 8 + PRD 4.5): dua kolom -
kartu input (preset + area teks + tombol Analisis) di kiri dan kartu
hasil (baris aspek + bar confidence) di kanan; di bawahnya kotak teks
asli/bersih dan kartu tindak lanjut.

Paritas perilaku dengan versi lama dijaga:
- P-M12: teks preset p1-p4 persis sama (PRESET_TEXTS di bawah).
- P-M13: analisis lewat pipeline.analyze_single_review.
- P-M14: teks asli dan teks bersih (cleaned_text) tetap ditampilkan.
- P-M15: tiap aspek yang disebut tampil dengan sentimen + confidence.
- P-M16: kartu tindak lanjut kondisional (ada aspek negatif / tidak).
Hasil hanya tampil pada run klik Analisis, sama seperti versi lama.
Seluruh literal HTML ditulis rata kiri (dirakit sebagai satu baris):
baris terindentasi di dalam markdown Streamlit terbaca sebagai blok kode.
"""

import html

import streamlit as st

from src.ui import labels
from src.ui.theme import ASPECT_COLORS

PRESET_TEXTS = {
    "p1": "Ayamnya gurih renyah bumbunya mantap meresap, tapi kemasan mangkok tumpah kuah dan minyak sambal rembes ke kantong plastik. Driver nunggu 30 menit.",
    "p2": "Gelas kopinya kecil banget es batunya penuh 80%, toast makin tipis, harga 35rb kemahalan buat porsi segini.",
    "p3": "Lama banget pelayanannya, order mie ayam bakso nunggu 50 menit pas jam makan siang. Pelayan jutek kuah dingin keasinan.",
    "p4": "Bebek bumbu hitamnya juara dunia rempahnya medok daging empuk porsi jumbo kemasan besek bambu sangat rapi!"
}

PRESET_LABELS = {
    "p1": "Mixed: Rasa vs Kemasan",
    "p2": "Porsi & Harga",
    "p3": "Pelayanan & Suhu",
    "p4": "Puas Bintang 5",
}

# Pasangan (kunci preset, kunci tombol) - kunci tombol dipertahankan dari lama.
_PRESET_KEYS = (
    ("p1", "sim_preset_1"),
    ("p2", "sim_preset_2"),
    ("p3", "sim_preset_3"),
    ("p4", "sim_preset_4"),
)

# Ikon garis tipis gaya Lucide per aspek (isi <svg>, stroke diisi warna aksen).
_ICON_PATHS = {
    "rasa": "<path d='M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z'></path>",
    "porsi": "<polygon points='12 2 2 7 12 12 22 7 12 2'></polygon><polyline points='2 17 12 22 22 17'></polyline><polyline points='2 12 12 17 22 12'></polyline>",
    "harga": "<path d='M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z'></path><line x1='7' y1='7' x2='7.01' y2='7'></line>",
    "kemasan": "<path d='M16.5 9.4L7.55 4.24'></path><path d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'></path><polyline points='3.29 7 12 12 20.71 7'></polyline><line x1='12' y1='22' x2='12' y2='12'></line>",
    "pelayanan": "<path d='M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9'></path><path d='M13.73 21a2 2 0 0 1-3.46 0'></path>",
}

_PILL_CLASS = {
    "positive": "pill-pos",
    "negative": "pill-neg",
    "neutral": "pill-neu",
}

_STATUS_MSG = {
    "positive": "Pelanggan puas dengan aspek ini.",
    "negative": "Ada keluhan pada aspek ini.",
    "neutral": "Disebut secara netral.",
}

_CONF_COLOR = {
    "positive": "#22C55E",
    "negative": "#B42318",
    "neutral": "#D97706",
}


def _aspect_icon(asp, accent):
    paths = _ICON_PATHS.get(asp, "<circle cx='12' cy='12' r='4'></circle>")
    return (
        "<svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='" + accent + "' "
        "stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>" + paths + "</svg>"
    )


def render(ctx, pipeline, action_engine):
    sim_res = None

    col_input, col_result = st.columns([1, 1.15])

    with col_input:
        with st.container(key="card_coba_input"):
            st.markdown(
                f"<div class='card-title'>{labels.COBA_INPUT_TITLE}</div>"
                f"<div class='card-sub'>{labels.COBA_INPUT_SUB}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='card-sub'>{labels.COBA_PRESET_TITLE}</div>",
                unsafe_allow_html=True,
            )
            for row_pair in ((_PRESET_KEYS[0], _PRESET_KEYS[1]), (_PRESET_KEYS[2], _PRESET_KEYS[3])):
                p_col1, p_col2 = st.columns(2)
                for p_col, (p_key, btn_key) in zip((p_col1, p_col2), row_pair):
                    with p_col:
                        if st.button(PRESET_LABELS[p_key], key=btn_key, type="secondary", use_container_width=True):
                            st.session_state.simulator_text = PRESET_TEXTS[p_key]
                            st.rerun()
            sim_input = st.text_area(
                labels.COBA_TEXT_LABEL,
                value=st.session_state.simulator_text,
                height=130
            )
            if st.button(labels.COBA_ANALYZE_BTN, key="sim_analyze_btn", type="primary", use_container_width=True):
                st.session_state.simulator_text = sim_input
                sim_res = pipeline.analyze_single_review(sim_input)

    with col_result:
        with st.container(key="card_coba_result"):
            st.markdown(
                f"<div class='card-title'>{labels.COBA_RESULT_TITLE}</div>"
                f"<div class='card-sub'>{labels.COBA_RESULT_SUB.format(engine=ctx['engine_label'])}</div>",
                unsafe_allow_html=True,
            )
            if sim_res is None:
                st.markdown(
                    f"<div class='card-title'>{labels.COBA_EMPTY_TITLE}</div>"
                    f"<div class='card-sub'>{labels.COBA_EMPTY_BODY}</div>",
                    unsafe_allow_html=True,
                )
            else:
                rows = []
                not_mentioned = []
                for asp, data in sim_res["aspects"].items():
                    if not data["mentioned"]:
                        not_mentioned.append(asp.capitalize())
                        continue
                    sent = data["sentiment"]
                    conf = float(data["confidence"])
                    accent, tint = ASPECT_COLORS.get(asp, ("#64756B", "#EFF3F0"))
                    rows.append(
                        "<div class='aspect-row'>"
                        f"<div class='aspect-chip' style='background: {tint};'>{_aspect_icon(asp, accent)}</div>"
                        f"<div class='aspect-name'>{asp.capitalize()}"
                        f"<div style='font-size: 0.74rem; font-weight: 400; color: #64756B;'>{_STATUS_MSG.get(sent, _STATUS_MSG['neutral'])}</div></div>"
                        f"<span class='chip {_PILL_CLASS.get(sent, 'pill-neu')}'>{labels.SENTIMENT_LABELS.get(sent, sent)}</span>"
                        f"<div class='conf-track'><div class='conf-fill' style='width: {conf * 100:.0f}%; background: {_CONF_COLOR.get(sent, '#D97706')};'></div></div>"
                        f"<div class='conf-val'>{conf * 100:.0f}%</div>"
                        "</div>"
                    )
                if not_mentioned:
                    rows.append(
                        f"<div class='not-mentioned-line'>{labels.COBA_NOT_MENTIONED.format(daftar=', '.join(not_mentioned))}</div>"
                    )
                st.markdown("".join(rows), unsafe_allow_html=True)

    if sim_res is not None:
        with st.container(key="card_coba_teks"):
            st.markdown(
                "<div class='review-card'>"
                f"<div class='label-caps' style='margin-bottom: 6px;'>{labels.COBA_RAW_TITLE}</div>"
                f"<div class='review-text'>{html.escape(str(sim_res['original_text']))}</div>"
                "</div>"
                "<div class='review-card'>"
                f"<div class='label-caps' style='margin-bottom: 6px;'>{labels.COBA_CLEAN_TITLE}</div>"
                f"<div class='review-text'>{html.escape(str(sim_res['cleaned_text']))}</div>"
                "</div>",
                unsafe_allow_html=True,
            )

        neg_aspects = [
            asp.capitalize()
            for asp, d in sim_res["aspects"].items()
            if d["mentioned"] and d["sentiment"] == "negative"
        ]
        with st.container(key="card_coba_lanjut"):
            if neg_aspects:
                st.markdown(
                    f"<div class='card-title'>{labels.COBA_FOLLOW_NEG_TITLE}</div>"
                    f"<div class='card-sub'>{labels.COBA_FOLLOW_NEG_BODY.format(aspek=', '.join(neg_aspects))}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='card-title'>{labels.COBA_FOLLOW_OK_TITLE}</div>"
                    f"<div class='card-sub'>{labels.COBA_FOLLOW_OK_BODY}</div>",
                    unsafe_allow_html=True,
                )
