"""
Tab 3 Component: AI Kitchen Action Checklist
Interactive tickable checklist with Session State & PDF/Text export
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any

from src.analytics.health_score import (
    calculate_aspect_metrics,
    calculate_overall_health_score,
    get_critical_kitchen_alerts
)
from src.utils.exporter import export_action_plan_text, export_action_plan_pdf

DEFAULT_KITCHEN_ACTIONS = [
    {
        "id": "ACT-101",
        "aspect": "Kemasan",
        "title": "Audit Higienitas & Kualitas Wadah Kemasan",
        "target_pic": "Supervisor Packing",
        "deadline": "Hari ini (Sebelum Shift Malam)",
        "instruction": "Pastikan wadah kemasan food-grade bersih, kering, dan bebas bau sebelum dipakai; wadah yang retak atau berubah bentuk wajib dibuang, bukan dipakai ulang.",
        "checked": False
    },
    {
        "id": "ACT-102",
        "aspect": "Kemasan",
        "title": "Pemeriksaan Segel Kemasan & Higienitas Area Packing",
        "target_pic": "Head Chef",
        "deadline": "Setiap Awal Shift",
        "instruction": "Briefing 5 menit di awal shift: staf packing wajib memakai sarung tangan dan hairnet, lalu melakukan tilt-test segel pada setiap wadah berkuah sebelum diserahkan ke driver.",
        "checked": False
    },
    {
        "id": "ACT-103",
        "aspect": "Rasa",
        "title": "Kalibrasi Standar Seasoning Sup & Kuah",
        "target_pic": "Sous Chef",
        "deadline": "Besok Pagi (10:00 WIB)",
        "instruction": "Uji keasinan kuah menggunakan refraktometer/salinity meter untuk menjaga konsistensi pada kisaran 1.1% - 1.3%.",
        "checked": False
    },
    {
        "id": "ACT-104",
        "aspect": "Rasa",
        "title": "Inspeksi Suhu Makanan di Pick-up Counter",
        "target_pic": "Expeditor Dapur",
        "deadline": "Berkala Tiap Jam",
        "instruction": "Pastikan makanan panas (sop, soto, gorengan) disajikan pada suhu minimum 65°C, jangan dibiarkan menginap di meja saji.",
        "checked": False
    },
    {
        "id": "ACT-105",
        "aspect": "Pelayanan",
        "title": "Evaluasi Waktu Tunggu Tiket Pesanan (>25 Menit)",
        "target_pic": "Floor Captain & Kasir",
        "deadline": "Evaluasi Mingguan",
        "instruction": "Identifikasi menu yang memiliki durasi olah paling lambat dan terapkan batch-prep bahan setengah matang.",
        "checked": False
    }
]

def init_checklist_state():
    """Menginisialisasi session state untuk checklist aksi dapur."""
    if "kitchen_actions" not in st.session_state:
        st.session_state.kitchen_actions = [dict(item) for item in DEFAULT_KITCHEN_ACTIONS]

def render_tab3(df: pd.DataFrame):
    """Merender Tab 3: AI Kitchen Action Checklist Interaktif."""
    init_checklist_state()

    st.markdown("### AI Kitchen Action Checklist")
    st.caption("Daftar instruksi tugas operasional dapur yang dihasilkan otomatis dari sentimen ulasan. Centang tugas yang telah diselesaikan.")

    aspect_df = calculate_aspect_metrics(df)
    overall_score, status, _ = calculate_overall_health_score(aspect_df)
    alerts = get_critical_kitchen_alerts(df, aspect_df)

    # 1. Action Items Interaktif
    action_items: List[Dict[str, Any]] = st.session_state.kitchen_actions

    # Progress Indicator
    total_tasks = len(action_items)
    completed_tasks = sum(1 for item in action_items if item.get("checked", False))
    progress_val = completed_tasks / total_tasks if total_tasks > 0 else 0.0

    prog_col, stat_col = st.columns([3, 1])
    with prog_col:
        st.write(f"**Penyelesaian Tugas:** `{completed_tasks}/{total_tasks}` Diselesaikan ({int(progress_val * 100)}%)")
        st.progress(progress_val)
    with stat_col:
        if completed_tasks == total_tasks and total_tasks > 0:
            st.success("Seluruh Tugas Selesai!")
        else:
            st.info(f"{total_tasks - completed_tasks} Tugas Pending")

    st.markdown("---")

    # Render Checkboxes
    for idx, item in enumerate(action_items):
        item_id = item["id"]
        col_check, col_details = st.columns([1, 11])
        
        with col_check:
            # Checkbox yang terikat dengan session state
            is_checked = st.checkbox(
                label=f"Pilih {item_id}",
                value=item.get("checked", False),
                key=f"check_{item_id}",
                label_visibility="collapsed"
            )
            # Update state jika berubah
            item["checked"] = is_checked

        with col_details:
            title_prefix = "~~" if is_checked else ""
            title_suffix = "~~ (SELESAI)" if is_checked else ""
            st.markdown(f"**{title_prefix}{idx+1}. [{item['aspect']}] {item['title']}{title_suffix}**")
            st.caption(f"**PIC:** `{item['target_pic']}` | **Deadline:** `{item['deadline']}`")
            st.write(f"*{item['instruction']}*")
            st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)

    # 2. Export Section (PDF & Text)
    st.markdown("#### Ekspor Laporan Action Plan")
    st.write("Unduh ringkasan tindakan operasional ini untuk dibagikan kepada Chef dan Tim Kitchen.")

    col_btn_txt, col_btn_pdf, col_reset = st.columns([1, 1, 1])

    with col_btn_txt:
        txt_content = export_action_plan_text(
            overall_score=overall_score,
            status=status,
            action_items=action_items,
            critical_alerts=alerts
        )
        st.download_button(
            label="Download Laporan (TXT)",
            data=txt_content,
            file_name="UlasRasa_Kitchen_Action_Plan.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col_btn_pdf:
        try:
            pdf_bytes = export_action_plan_pdf(
                overall_score=overall_score,
                status=status,
                action_items=action_items,
                critical_alerts=alerts
            )
            st.download_button(
                label="Download Laporan (PDF)",
                data=pdf_bytes,
                file_name="UlasRasa_Kitchen_Action_Plan.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.warning(f"Ekspor PDF opsional: {e}")

    with col_reset:
        if st.button("Reset Status Checklist", use_container_width=True):
            for itm in st.session_state.kitchen_actions:
                itm["checked"] = False
            st.rerun()
