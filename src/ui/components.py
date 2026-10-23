"""Komponen shell UI UlasRasa: sidebar data & navigasi, header, footer.

Tahap 0: seluruh blok dipindah VERBATIM dari app.py pra-perombakan.
render_sidebar() merender sidebar lama apa adanya (brand, navigasi radio,
sumber data, kartu outlet, panduan, form tambah ulasan, kartu bobot) dan
mengembalikan konteks data untuk modul-modul. Blok evaluasi di tengah
sidebar lama kini dihitung lewat core.compute_context() dengan urutan
pemanggilan yang sama (evaluate_dataframe satu kali per run, sesudah
filter resto final).
"""

import pandas as pd
import streamlit as st

from src.ui.core import compute_context
from src.ui.labels import MODULE_CHOICES, TOP_SHORT_LABELS


def render_sidebar(pipeline, engine_label: str) -> dict:
    # Nama lokal dipertahankan sama seperti global app.py lama agar baris
    # caption engine di sidebar tetap verbatim.
    ACTIVE_ABSA_ENGINE_LABEL = engine_label
    with st.sidebar:
        # 4.1 Brand Header & Live Pulse Status
        st.markdown(
            """
        <div class='brand-container'>
            <div class='brand-logo-badge'>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M4 16C4 19.5 7.5 21 12 21C16.5 21 20 19.5 20 16H4Z" fill="#FAF8F5"/>
                    <path d="M12 4L14.5 10H9.5L12 4Z" fill="#FAF8F5"/>
                    <line x1="3" y1="15" x2="21" y2="15" stroke="#FAF8F5" stroke-width="1.8" stroke-linecap="round"/>
                    <line x1="9" y1="21.5" x2="15" y2="21.5" stroke="#FAF8F5" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
            </div>
            <div>
                <div class='brand-text-title'>ULASRASA</div>
                <div class='brand-text-sub'>Kitchen Diagnostics AI</div>
            </div>
        </div>
        <div class='live-status-pill'>
            <span class='pulse-dot'></span>
            <span>Engine Siap &bull; Analisis 5 Aspek</span>
        </div>
        """,
            unsafe_allow_html=True
        )
        st.caption(f"Engine ABSA: {ACTIVE_ABSA_ENGINE_LABEL}")

        # 4.2 Navigasi Modul dengan HIGHLIGHTER
        st.markdown(
            """
        <div class='sidebar-section-header'>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#C84B2F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="7" height="7"></rect>
                <rect x="14" y="3" width="7" height="7"></rect>
                <rect x="14" y="14" width="7" height="7"></rect>
                <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
            MODUL KERJA AKTIF
        </div>
        """,
            unsafe_allow_html=True
        )

        MODULE_CHOICES = [
            "Ringkasan Eksekutif & Health Score",
            "Deep-Dive Aspek & Sentimen",
            "AI Kitchen Action Checklist",
            "Single Review Simulator (Live Demo)"
        ]

        selected_nav = st.radio(
            "Pilih Modul Analisis:",
            MODULE_CHOICES,
            index=MODULE_CHOICES.index(st.session_state.active_module_name) if st.session_state.active_module_name in MODULE_CHOICES else 0,
            label_visibility="collapsed",
            key="sidebar_module_radio"
        )
        st.session_state.active_module_name = selected_nav

        st.markdown("---")

        # 4.3 Konfigurasi Sumber Data Ulasan
        st.markdown(
            """
        <div class='sidebar-section-header'>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#78716C" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
            </svg>
            SUMBER DATA & PROFIL RESTORAN
        </div>
        """,
            unsafe_allow_html=True
        )

        data_source_mode = st.radio(
            "Mode Pengambilan Data:",
            ["Outlet Bawaan (Preset)", "Upload Dataset Real (CSV)"],
            index=0,
            label_visibility="collapsed",
            help="Pilih preset restoran lokal atau unggah file ulasan GoFood/GrabFood/Google Maps milikmu sendiri."
        )

        active_df = st.session_state.custom_reviews_df.copy()

        if data_source_mode == "Upload Dataset Real (CSV)":
            uploaded_file = st.file_uploader(
                "Upload File CSV Ulasan:",
                type=["csv"],
                help="File minimal memiliki kolom 'review_text'. Kolom lain opsional."
            )
            if uploaded_file is not None:
                try:
                    user_csv = pd.read_csv(uploaded_file)
                    if len(user_csv) > 200:
                        st.error(f"File berisi {len(user_csv)} baris, melebihi batas maksimum 200 baris ulasan per analisis. Perkecil file terlebih dahulu, lalu unggah kembali.")
                    elif "review_text" in user_csv.columns:
                        st.success(f"File berhasil dimuat ({len(user_csv)} baris)")
                        active_df = user_csv
                        selected_resto = user_csv.get("restaurant_name", pd.Series(["Outlet Kustom"])).iloc[0]
                    else:
                        st.error("CSV wajib memiliki kolom 'review_text'")
                except Exception as e:
                    st.error(f"Gagal membaca CSV: {e}")
            else:
                st.info("Menggunakan dataset aktif sementara.")
                selected_resto = "Semua Outlet (Benchmark)"
        else:
            # Pilihan Outlet Preset
            if not active_df.empty and "restaurant_name" in active_df.columns:
                outlet_list = ["Semua Outlet (Benchmark Industri)"] + sorted(list(active_df["restaurant_name"].unique()))
                selected_resto = st.selectbox(
                    "Pilih Profil Outlet UMKM:",
                    outlet_list,
                    index=1,
                    help="Setiap outlet memiliki karakteristik komplain operasional riil yang berbeda."
                )
            else:
                selected_resto = "Ayam Geprek Sambal Korek Barokah"

        # Filter Dataframe Aktif Berdasarkan Pilihan Outlet
        if selected_resto != "Semua Outlet (Benchmark Industri)" and "restaurant_name" in active_df.columns:
            filtered_df = active_df[active_df["restaurant_name"] == selected_resto].copy()
        else:
            filtered_df = active_df.copy()

        _ev = compute_context(filtered_df, pipeline)
        eval_results = _ev["eval_results"]
        khs = _ev["khs"]
        breakdown = _ev["breakdown"]
        status_label = _ev["status_label"]
        status_class = _ev["status_class"]
        status_color = _ev["status_color"]
        weakest_aspect = _ev["weakest_aspect"]
        weakest_score = _ev["weakest_score"]

        # 4.4 DYNAMIC LIVE OUTLET PROFILE CARD DI SIDEBAR (UX HIDUP)
        st.markdown(
            f"""
        <div class='sidebar-outlet-card'>
            <div class='sidebar-outlet-header'>
                <div class='sidebar-outlet-name'>{selected_resto}</div>
                <span class='{status_class}'>{status_label.split()[0]}</span>
            </div>
            <div class='sidebar-outlet-score-row'>
                <span class='sidebar-score-label'>Kitchen Health Score</span>
                <span class='sidebar-score-val' style='color: {status_color};'>{khs:.1f}%</span>
            </div>
            <div class='sidebar-progress-track'>
                <div style='width: {min(khs, 100):.1f}%; height: 100%; background: {status_color};'></div>
            </div>
            <div class='sidebar-outlet-chips'>
                <span class='outlet-chip'>{len(filtered_df)} Ulasan Aktif</span>
                <span class='outlet-chip outlet-chip-alert'>Kritis: {weakest_aspect.capitalize()} ({weakest_score:.0f}%)</span>
            </div>
            <div style='font-size: 0.68rem; color: #78716C; margin-top: 6px; display: flex; align-items: center; gap: 4px;'>
                <span class='pulse-dot' style='width: 5px; height: 5px;'></span>
                <span>Konteks Outlet Terpilih Aktif</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        # 4.5 Mode Presentasi / Pitching Guide (Tanpa Emoji)
        with st.expander("Panduan Pitching Mentor (3 Menit)", expanded=False):
            st.markdown(
                """
            <div style='font-size: 0.8rem; color: #44403C; line-height: 1.45;'>
                <div style='background: #FAF8F5; border-left: 3px solid #C84B2F; padding: 6px 10px; margin-bottom: 6px; border-radius: 4px;'>
                    <b>Menit 00:00 - 00:45 | Masalah Riil</b><br>
                    Pemilik resto kewalahan memilah ribuan ulasan liar di GoFood/GrabFood. Sentimen konvensional (+/-) gagal karena komplain kuliner selalu <i>mixed sentiment</i>.
                </div>
                <div style='background: #FAF8F5; border-left: 3px solid #D97706; padding: 6px 10px; margin-bottom: 6px; border-radius: 4px;'>
                    <b>Menit 00:45 - 02:00 | Solusi Hybrid AI</b><br>
                    IndoBERT Base hasil fine-tune membedah 5 aspek per ulasan (lexicon menjadi baseline & fallback). KHS mengukur kesehatan dapur 0-100%, lalu LLM Gemini (bila API key tersedia) atau katalog template merumuskan RCA & checklist fisik.
                </div>
                <div style='background: #FAF8F5; border-left: 3px solid #15803D; padding: 6px 10px; border-radius: 4px;'>
                    <b>Menit 02:00 - 03:00 | Dampak Bisnis</b><br>
                    Memangkas audit operasional dari 10 jam/minggu jadi instan dan mencegah penurunan rating delivery toko.
                </div>
            </div>
            """,
                unsafe_allow_html=True
            )

        # 4.6 Form Tambah Ulasan Baru Langsung
        with st.expander("Input Ulasan Baru ke Outlet Ini", expanded=False):
            st.caption("Uji coba menambahkan komplain baru secara live ke database aktif.")
            new_rev_text = st.text_area("Kalimat Ulasan Konsumen:", height=75, placeholder="Contoh: Ayam alot dan sambalnya sedikit...")
            new_rev_menu = st.text_input("Menu Terkait:", value="Menu Favorit")

            if st.button("Simpan & Perbarui Dashboard", type="primary", use_container_width=True):
                if new_rev_text.strip():
                    infer_res = pipeline.analyze_single_review(new_rev_text)
                    new_row = {
                        "review_id": len(st.session_state.custom_reviews_df) + 1,
                        "restaurant_name": selected_resto if selected_resto != "Semua Outlet (Benchmark Industri)" else "Ayam Geprek Sambal Korek Barokah",
                        "menu_item": new_rev_menu,
                        "review_text": new_rev_text,
                        "rasa": infer_res["aspects"]["rasa"]["sentiment"],
                        "porsi": infer_res["aspects"]["porsi"]["sentiment"],
                        "harga": infer_res["aspects"]["harga"]["sentiment"],
                        "kemasan": infer_res["aspects"]["kemasan"]["sentiment"],
                        "pelayanan": infer_res["aspects"]["pelayanan"]["sentiment"],
                    }
                    st.session_state.custom_reviews_df = pd.concat([st.session_state.custom_reviews_df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success("Ulasan baru berhasil ditambahkan! Dashboard terbarui.")
                    st.rerun()
                else:
                    st.warning("Teks ulasan tidak boleh kosong.")

        st.markdown("---")

        # 4.7 Bobot Komposit KHS (Visual Meter Bar)
        st.markdown(
            """
        <div class='sidebar-weights-card'>
            <div style='display: flex; justify-content: space-between; align-items: center; font-size: 0.72rem; font-weight: 700; color: #78716C;'>
                <span>BOBOT KOMPOSIT KHS</span>
                <span style='background: #EAE6DE; padding: 1px 6px; border-radius: 4px;'>TOTAL 100%</span>
            </div>
            <div class='weights-bar-composite'>
                <div style='width: 35%; background: #C84B2F;' title='Rasa: 35%'></div>
                <div style='width: 20%; background: #D97706;' title='Porsi: 20%'></div>
                <div style='width: 15%; background: #2563EB;' title='Kemasan: 15%'></div>
                <div style='width: 15%; background: #7C3AED;' title='Harga: 15%'></div>
                <div style='width: 15%; background: #059669;' title='Pelayanan: 15%'></div>
            </div>
            <div class='weights-grid'>
                <div class='weight-item' style='border-left: 3px solid #C84B2F;'>Rasa <b>35%</b></div>
                <div class='weight-item' style='border-left: 3px solid #D97706;'>Porsi <b>20%</b></div>
                <div class='weight-item' style='border-left: 3px solid #2563EB;'>Kemasan <b>15%</b></div>
                <div class='weight-item' style='border-left: 3px solid #7C3AED;'>Harga <b>15%</b></div>
                <div class='weight-item' style='border-left: 3px solid #059669; grid-column: span 2;'>Pelayanan <b>15%</b></div>
            </div>
        </div>
        """,
            unsafe_allow_html=True
        )

        return {
            "data_source_mode": data_source_mode,
            "active_df": active_df,
            "selected_resto": selected_resto,
            "filtered_df": filtered_df,
            "eval_results": eval_results,
            "khs": khs,
            "breakdown": breakdown,
            "status_label": status_label,
            "status_class": status_class,
            "status_color": status_color,
            "weakest_aspect": weakest_aspect,
            "weakest_score": weakest_score,
        }


def render_header(ctx: dict) -> str:
    """Header utama + navigasi atas (verbatim dari app.py lama).

    Mengembalikan ID modul aktif sesudah tombol atas diproses.
    """
    selected_resto = ctx["selected_resto"]
    filtered_df = ctx["filtered_df"]
    st.title("UlasRasa: Asisten Diagnostik Ulasan Kuliner & Evaluasi Dapur")
    st.markdown(
        f"Sistem intelijen berbasis **IndoBERT Multi-Aspect Sentiment Analysis** dan **Generative AI** "
        f"untuk membedah ulasan tidak terstruktur menjadi metrik kesehatan operasional dapur UMKM F&B. "
        f"(Target Analisis: **{selected_resto}** | **{len(filtered_df)}** Ulasan Konsumen Aktif)"
    )

    # Interactive Workflow Step Indicator (Zero Emoji)
    with st.container():
        st.markdown(
            """
        <div style='margin-bottom: 20px;'>
            <div style='display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px;'>
                <div class='workflow-step'>
                    <div class='workflow-num'>1</div>
                    <div class='workflow-title'>Ingestion & Slang</div>
                    <div class='workflow-desc'>Pembersihan ulasan & normalisasi bahasa gaul F&B</div>
                </div>
                <div class='workflow-step'>
                    <div class='workflow-num'>2</div>
                    <div class='workflow-title'>ABSA IndoBERT</div>
                    <div class='workflow-desc'>Klasifikasi 5 aspek (Rasa, Porsi, Harga, Kemasan, Pelayanan)</div>
                </div>
                <div class='workflow-step'>
                    <div class='workflow-num'>3</div>
                    <div class='workflow-title'>Health Scoring</div>
                    <div class='workflow-desc'>Kalkulasi KHS terbobot & pemetaan Spider Chart</div>
                </div>
                <div class='workflow-step'>
                    <div class='workflow-num'>4</div>
                    <div class='workflow-title'>Root Cause (5-Why)</div>
                    <div class='workflow-desc'>Diagnosa otomatis akar pemicu masalah dapur</div>
                </div>
                <div class='workflow-step'>
                    <div class='workflow-num'>5</div>
                    <div class='workflow-title'>Action Checklist</div>
                    <div class='workflow-desc'>Checklist kru dapur siap cetak & SOP perbaikan fisik</div>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True
        )

    # Synchronized Top Module Selector (Highlighter Visual Bar)
    st.markdown(
        f"""
    <div style='display: flex; justify-content: space-between; align-items: center; margin: 16px 0 12px 0;'>
        <div style='font-size: 0.78rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: #78716C; display: flex; align-items: center; gap: 8px;'>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#C84B2F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="7" height="7"></rect>
                <rect x="14" y="3" width="7" height="7"></rect>
                <rect x="14" y="14" width="7" height="7"></rect>
                <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
            NAVIGASI MODUL DIAGNOSTIK
        </div>
        <div style='font-size: 0.78rem; color: #57534E;'>
            Modul Aktif: <b style='color: #C84B2F; font-weight: 800;'>{st.session_state.active_module_name}</b>
        </div>
    </div>
    """,
        unsafe_allow_html=True
    )

    col_top_nav1, col_top_nav2, col_top_nav3, col_top_nav4 = st.columns(4)
    top_cols = [col_top_nav1, col_top_nav2, col_top_nav3, col_top_nav4]
    short_labels = ["1. Ringkasan Eksekutif", "2. Deep-Dive Aspek", "3. Checklist & SOP", "4. Review Simulator"]

    for idx, (t_col, full_title, s_label) in enumerate(zip(top_cols, MODULE_CHOICES, short_labels)):
        with t_col:
            is_cur = (st.session_state.active_module_name == full_title)
            if is_cur:
                st.button(
                    f"AKTIF: {s_label}",
                    key=f"top_btn_{idx}",
                    type="primary",
                    use_container_width=True
                )
            else:
                if st.button(
                    s_label,
                    key=f"top_btn_{idx}",
                    type="secondary",
                    use_container_width=True
                ):
                    st.session_state.active_module_name = full_title
                    st.rerun()

    current_module = st.session_state.active_module_name
    return current_module


def render_footer() -> None:
    """Footer (verbatim dari app.py lama)."""
    st.markdown("---")
    st.markdown(
        """
    <div style='display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; color: #78716C;'>
        <span><b>UlasRasa</b> &bull; AI Engineering Final Project (Batch 13) | Student ID: <b>REAENG13TQJLN</b> (Azura)</span>
        <span>Arsitektur: <b>IndoBERT Base (ABSA) + Generative LLM Action Engine</b></span>
    </div>
    """,
        unsafe_allow_html=True
    )
