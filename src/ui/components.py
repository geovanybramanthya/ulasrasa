"""Komponen shell UI UlasRasa (Tahap 1 - ditulis dari DESIGN.md).

Isi: TopBar lengket (logo + st.pills navigasi + cip engine), header sapaan
sekaligus rumah fungsi data (pemilih resto, PanelData berisi mode data /
unggah CSV / form tambah ulasan), LoadingBermerek, dan footer ringkas.

Perilaku data di file ini adalah perilaku blok sidebar app.py lama yang
berpindah rumah tanpa berubah aturan (PRD Implementasi UI Bag. 3.1):
- dataset bawaan dari session_state.custom_reviews_df;
- mode preset: resto terurut, pilihan awal resto pertama alfabetis;
- mode unggah: guard 200 baris + wajib kolom review_text, pesan persis lama;
- quirk mode unggah tanpa file (selected_resto "Semua Outlet (Benchmark)")
  dipertahankan apa adanya sesuai catatan PRD;
- evaluate_dataframe tetap dipanggil satu kali per run lewat
  core.compute_context() sesudah filter final.
"""

import pandas as pd
import streamlit as st

from src.ui import labels
from src.ui.core import compute_context
from src.ui.labels import MODULE_CHOICES, MODULE_LABELS, LABEL_TO_MODULE

LOGO_SVG = """
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M4 12h16"></path>
    <path d="M5 12c0 4.2 3.1 7.5 7 7.5s7-3.3 7-7.5"></path>
    <path d="M9.2 8.2c0-1.3 1.1-1.7 1.1-3"></path>
    <path d="M13.8 8.2c0-1.3 1.1-1.7 1.1-3"></path>
    <path d="M8.5 21.5h7"></path>
</svg>
"""


# ------------------------------------------------------------------ navigasi
def _on_nav_change() -> None:
    picked = st.session_state.get("nav_pills")
    if picked in LABEL_TO_MODULE:
        st.session_state.active_module_name = LABEL_TO_MODULE[picked]


def sync_nav_pills() -> None:
    """Selaraskan nilai st.pills dengan active_module_name (sumber kebenaran).

    Dipanggil sebelum TopBar dirender, mis. sesudah modul lain (CTA hero)
    mengubah active_module_name secara programatis.
    """
    desired = MODULE_LABELS.get(st.session_state.get("active_module_name"), MODULE_LABELS[MODULE_CHOICES[0]])
    if st.session_state.get("nav_pills") != desired:
        st.session_state["nav_pills"] = desired


def render_topbar(engine_label: str) -> None:
    """Top bar lengket: brand, navigasi pill, cip engine (teks persis P-E2)."""
    with st.container(key="topbar"):
        c_brand, c_nav, c_chip = st.columns([1.15, 2.2, 1.0])
        with c_brand:
            st.markdown(
                f"""
                <div class='brand-lockup'>
                    <div class='brand-badge'>{LOGO_SVG}</div>
                    <div>
                        <div class='brand-name'>{labels.BRAND_NAME}</div>
                        <div class='brand-sub'>{labels.BRAND_SUB}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c_nav:
            st.pills(
                "Navigasi modul",
                options=[MODULE_LABELS[m] for m in MODULE_CHOICES],
                selection_mode="single",
                default=MODULE_LABELS[st.session_state.active_module_name],
                label_visibility="collapsed",
                key="nav_pills",
                on_change=_on_nav_change,
            )
        with c_chip:
            st.markdown(
                f"<span class='engine-chip'>{labels.ENGINE_CHIP_PREFIX}: {engine_label}</span>",
                unsafe_allow_html=True,
            )


# ------------------------------------------------------------------ loading
def loading_placeholder():
    """Kartu loading bermerek (PRD 4.1). Kembalikan placeholder untuk dikosongkan."""
    ph = st.empty()
    ph.markdown(
        f"""
        <div class='loading-card'>
            <div class='loading-pulse'>{LOGO_SVG}</div>
            <div class='card-title' style='font-size: 1.15rem;'>{labels.LOADING_TITLE}</div>
            <div class='card-sub'>{labels.LOADING_BODY}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return ph


# ------------------------------------------------------------------ panel data
def _process_upload(uploaded_file):
    """Proses file unggahan dengan aturan + teks pesan persis versi lama.

    Mengembalikan (active_df_baru_atau_None, selected_resto_atau_None,
    daftar_pesan) dengan pesan sebagai tuple (jenis, teks) untuk dirender
    di PanelData.
    """
    if uploaded_file is None:
        return None, None, []
    try:
        user_csv = pd.read_csv(uploaded_file)
    except Exception as e:  # teks galat sama seperti versi lama
        return None, None, [("error", f"Gagal membaca CSV: {e}")]
    if len(user_csv) > 200:
        return None, None, [(
            "error",
            f"File berisi {len(user_csv)} baris, melebihi batas maksimum 200 baris ulasan per analisis. "
            "Perkecil file terlebih dahulu, lalu unggah kembali.",
        )]
    if "review_text" in user_csv.columns:
        resto = user_csv.get("restaurant_name", pd.Series([labels.UPLOAD_FALLBACK_RESTO])).iloc[0]
        return user_csv, resto, [("success", f"File berhasil dimuat ({len(user_csv)} baris)")]
    return None, None, [("error", "CSV wajib memiliki kolom 'review_text'")]


def render_data_header(pipeline) -> dict:
    """Header sapaan + kontrol data + PanelData; mengembalikan konteks data.

    Urutan dalam satu run: baca keadaan data dari session -> proses unggahan
    (mode unggah) -> filter -> compute_context (evaluate satu kali) ->
    render header -> render PanelData bila terbuka.
    """
    if "ui_data_mode" not in st.session_state:
        st.session_state.ui_data_mode = labels.DATA_MODE_PRESET
    if "ui_panel_open" not in st.session_state:
        st.session_state.ui_panel_open = False

    mode = st.session_state.ui_data_mode
    active_df = st.session_state.custom_reviews_df.copy()
    upload_messages = []

    if mode == labels.DATA_MODE_UPLOAD:
        uploaded = st.session_state.get("ui_csv_uploader")
        new_df, up_resto, upload_messages = _process_upload(uploaded)
        if new_df is not None:
            active_df = new_df
            selected_resto = up_resto
        elif uploaded is not None:
            # unggahan ditolak guard: data aktif tidak berubah (P-D4);
            # resto mengikuti dataset sesi seperti sebelum unggahan.
            selected_resto = st.session_state.get("ui_resto_select") or labels.BENCHMARK_LABEL
            if selected_resto == labels.BENCHMARK_LABEL:
                active_df = st.session_state.custom_reviews_df.copy()
        else:
            # Quirk lama dipertahankan: string tanpa kata "Industri".
            selected_resto = "Semua Outlet (Benchmark)"
    else:
        if not active_df.empty and "restaurant_name" in active_df.columns:
            outlet_list = [labels.BENCHMARK_LABEL] + sorted(list(active_df["restaurant_name"].unique()))
        else:
            outlet_list = [labels.BENCHMARK_LABEL, "Ayam Geprek Sambal Korek Barokah"]
        selected_resto = st.session_state.get("ui_resto_select")
        if selected_resto not in outlet_list:
            # Pilihan awal = resto pertama alfabetis (index 1) - P-D2.
            selected_resto = outlet_list[1] if len(outlet_list) > 1 else outlet_list[0]
            st.session_state.ui_resto_select = selected_resto

    # Filter dataframe aktif berdasarkan pilihan outlet (aturan lama persis).
    if selected_resto != labels.BENCHMARK_LABEL and "restaurant_name" in active_df.columns:
        filtered_df = active_df[active_df["restaurant_name"] == selected_resto].copy()
    else:
        filtered_df = active_df.copy()

    ev = compute_context(filtered_df, pipeline)

    # ---------------- header sapaan + kontrol kanan ----------------
    is_benchmark = selected_resto == labels.BENCHMARK_LABEL
    greet_name = labels.GREETING_BENCHMARK_NAME if is_benchmark else selected_resto
    sentence_tpl = labels.STATUS_SENTENCE_BENCHMARK if is_benchmark else labels.STATUS_SENTENCE
    sentence = sentence_tpl.format(
        status=ev["status_label"],
        aspek=ev["weakest_aspect"].capitalize(),
        skor=f"{ev['weakest_score']:.1f}%",
    )

    col_left, col_right = st.columns([2.35, 1.0])
    with col_right:
        if mode == labels.DATA_MODE_PRESET and not active_df.empty and "restaurant_name" in active_df.columns:
            st.markdown("<div class='label-caps' style='margin-bottom: 4px;'>Restoran</div>", unsafe_allow_html=True)
            st.selectbox(
                labels.RESTO_SELECT_LABEL,
                outlet_list,
                index=outlet_list.index(selected_resto),
                label_visibility="collapsed",
                key="ui_resto_select",
                help="Setiap outlet memiliki karakteristik komplain operasional riil yang berbeda.",
            )
        toggle_label = labels.BTN_TUTUP_PANEL if st.session_state.ui_panel_open else labels.BTN_GANTI_DATA
        if st.button(toggle_label, key="ui_toggle_panel", use_container_width=True):
            st.session_state.ui_panel_open = not st.session_state.ui_panel_open
            if st.session_state.ui_panel_open and st.session_state.active_module_name != MODULE_CHOICES[0]:
                st.session_state.active_module_name = MODULE_CHOICES[0]
                sync_nav_pills()
            st.rerun()
    with col_left:
        st.markdown(f"<div class='greeting'>Halo, {greet_name}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='status-line'>{sentence}</div>", unsafe_allow_html=True)

    # ---------------- PanelData (bila terbuka) ----------------
    if st.session_state.ui_panel_open:
        with st.container(key="paneldata"):
            st.markdown(f"<div class='card-title'>{labels.PANEL_DATA_TITLE}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-sub'>{labels.PANEL_DATA_SUB}</div>", unsafe_allow_html=True)
            mode_now = st.radio(
                labels.PANEL_MODE_LABEL,
                labels.DATA_MODES,
                index=labels.DATA_MODES.index(mode) if mode in labels.DATA_MODES else 0,
                label_visibility="collapsed",
                key="ui_data_mode",
                help="Pilih preset restoran lokal atau unggah file ulasan GoFood/GrabFood/Google Maps milikmu sendiri.",
            )
            if mode_now == labels.DATA_MODE_UPLOAD:
                st.file_uploader(
                    labels.UPLOAD_LABEL,
                    type=["csv"],
                    help="File minimal memiliki kolom 'review_text'. Kolom lain opsional.",
                    key="ui_csv_uploader",
                )
                for kind, text in upload_messages:
                    getattr(st, kind)(text)
                if st.session_state.get("ui_csv_uploader") is None:
                    st.info("Menggunakan dataset aktif sementara.")
            else:
                st.caption("Data contoh berisi 100 ulasan dari 4 restoran. Pilih restorannya lewat daftar di kanan atas.")

            # Form tambah ulasan (perilaku persis blok 4.6 versi lama - P-D7).
            with st.expander("Input Ulasan Baru ke Outlet Ini", expanded=False):
                st.caption("Uji coba menambahkan komplain baru secara live ke database aktif.")
                new_rev_text = st.text_area("Kalimat Ulasan Konsumen:", height=75, placeholder="Contoh: Ayam alot dan sambalnya sedikit...")
                new_rev_menu = st.text_input("Menu Terkait:", value="Menu Favorit")

                if st.button("Simpan & Perbarui Dashboard", type="primary", use_container_width=True):
                    if new_rev_text.strip():
                        infer_res = pipeline.analyze_single_review(new_rev_text)
                        new_row = {
                            "review_id": len(st.session_state.custom_reviews_df) + 1,
                            "restaurant_name": selected_resto if selected_resto != labels.BENCHMARK_LABEL else "Ayam Geprek Sambal Korek Barokah",
                            "menu_item": new_rev_menu,
                            "review_text": new_rev_text,
                            "rasa": infer_res["aspects"]["rasa"]["sentiment"],
                            "porsi": infer_res["aspects"]["porsi"]["sentiment"],
                            "harga": infer_res["aspects"]["harga"]["sentiment"],
                            "kemasan": infer_res["aspects"]["kemasan"]["sentiment"],
                            "pelayanan": infer_res["aspects"]["pelayanan"]["sentiment"],
                        }
                        st.session_state.custom_reviews_df = pd.concat(
                            [st.session_state.custom_reviews_df, pd.DataFrame([new_row])], ignore_index=True
                        )
                        st.success("Ulasan baru berhasil ditambahkan! Dashboard terbarui.")
                        st.rerun()
                    else:
                        st.warning("Teks ulasan tidak boleh kosong.")

    ctx = {
        "data_source_mode": mode,
        "active_df": active_df,
        "selected_resto": selected_resto,
        "filtered_df": filtered_df,
    }
    ctx.update(ev)
    return ctx


# ------------------------------------------------------------------ footer
def render_footer() -> None:
    """Footer ringkas satu baris (PRD 4.1)."""
    st.markdown("---")
    st.markdown(f"<div class='footer-line'>{labels.FOOTER_LINE}</div>", unsafe_allow_html=True)
