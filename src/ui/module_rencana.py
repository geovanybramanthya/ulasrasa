"""Modul 3: AI Kitchen Action Checklist & SOP.

Tahap 0: blok modul dipindah VERBATIM dari app.py lama.
"""

import pandas as pd
import streamlit as st

from src.utils.exporter import export_action_plan_text, export_action_plan_pdf


def render(ctx, pipeline, action_engine):
    filtered_df = ctx["filtered_df"]
    eval_results = ctx["eval_results"]
    selected_resto = ctx["selected_resto"]
    khs = ctx["khs"]
    status_label = ctx["status_label"]
    weakest_aspect = ctx["weakest_aspect"]

    st.markdown("### AI Kitchen Action Checklist & Rekomendasi SOP")
    st.caption("Dihasilkan oleh LLM (Gemini/Groq) bila API key tersedia; tanpa key, digunakan katalog template terstruktur berbasis pola keluhan.")

    sample_complaints = {}
    for asp in ["kemasan", "rasa", "porsi", "harga", "pelayanan"]:
        if asp in filtered_df.columns:
            negs = filtered_df[filtered_df[asp] == "negative"]["review_text"].tolist()
            if negs:
                sample_complaints[asp] = [str(t) for t in negs[:3]]

    plan = action_engine.generate_action_plan(
        restaurant_name=selected_resto,
        evaluation_results=eval_results,
        sample_complaints=sample_complaints
    )

    if plan.get("generation_mode") == "llm":
        mode_label = f"LLM ({plan.get('llm_provider') or '-'})"
    else:
        mode_label = "Template (offline)"
    st.caption(f"Mode rekomendasi: {mode_label}")

    # 1. Root Cause Analysis (5-Why Ishikawa)
    st.markdown("#### 1. Ringkasan Akar Masalah Operasional (Root Cause Analysis)")
    st.caption("Analisis mendalam mengapa keluhan pelanggan terjadi di area dapur/pengemasan:")

    for idx, rc in enumerate(plan.get("root_cause_analysis", []), 1):
        st.markdown(
            f"""
            <div class='ulas-card' style='padding: 14px 18px; margin-bottom: 8px;'>
                <div style='display: flex; gap: 10px; align-items: flex-start;'>
                    <div style='background: #C84B2F; color: #FFFFFF; width: 22px; height: 22px; border-radius: 50%; font-size: 0.75rem; font-weight: 700; text-align: center; line-height: 22px; flex-shrink: 0;'>{idx}</div>
                    <div style='font-size: 0.88rem; color: #292524; line-height: 1.4;'>
                        {rc}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2. Checklist Tindakan Dapur Siap Cetak
    st.markdown("#### 2. Checklist Perbaikan Dapur Siap Cetak")
    st.caption("Centang setiap tindakan yang sudah diverifikasi oleh Head Cook / Manajer Dapur saat shift kerja:")

    all_checklist = list(plan.get("kitchen_action_checklist", []))
    for custom_item in st.session_state.custom_checklist_items:
        if custom_item not in all_checklist:
            all_checklist.append(custom_item)

    completed_count = 0
    checked_status = {}

    for idx, item in enumerate(all_checklist):
        is_checked = st.checkbox(item, key=f"action_chk_{selected_resto}_{idx}")
        checked_status[idx] = is_checked
        if is_checked:
            completed_count += 1

    progress_ratio = completed_count / len(all_checklist) if all_checklist else 1.0
    st.progress(progress_ratio)
    st.caption(f"Tingkat Penyelesaian Audit Shift: **{completed_count}/{len(all_checklist)}** Selesai ({progress_ratio*100:.0f}%)")

    # Form Tambah Tindakan Kustom
    with st.expander("Tambah Tindakan Dapur Kustom", expanded=False):
        custom_act_text = st.text_input("Tindakan Baru:", placeholder="Contoh: Kalibrasi ulang termometer minyak fryer setiap jam 10 pagi...")
        if st.button("Tambahkan ke Checklist", type="primary"):
            if custom_act_text.strip():
                st.session_state.custom_checklist_items.append(custom_act_text.strip())
                st.success("Tindakan kustom berhasil ditambahkan ke checklist!")
                st.rerun()

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 3. Rekomendasi SOP Dapur Standar
    st.markdown("#### 3. Rekomendasi Standard Operating Procedure (SOP)")
    st.caption("Standard Operating Procedure yang disarankan untuk ditempel pada workstation dapur:")

    for sop_item in plan.get("sop_recommendations", []):
        st.markdown(
            f"""
            <div class='ulas-card' style='border-left: 4px solid #15803D; padding: 12px 18px; margin-bottom: 8px;'>
                <b style='color: #15803D; font-size: 0.85rem; text-transform: uppercase;'>SOP Operasional Terverifikasi:</b>
                <p style='margin: 4px 0 0 0; font-size: 0.85rem; color: #44403C;'>{sop_item}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 4. Export & Download Center (Zero Emoji)
    st.markdown("#### Unduh Dokumen Checklist Dapur")
    st.caption("Ekspor checklist tindakan untuk dicetak dan ditempel di meja dapur atau dibagikan ke kru:")

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    checklist_text_content = export_action_plan_text(
        overall_score=khs,
        status=status_label,
        action_items=[
            {
                "aspect": "Operasional",
                "title": item[:35],
                "target_pic": "Tim Dapur / Kru",
                "deadline": "Shift Berjalan",
                "instruction": item,
                "checked": checked_status.get(i, False)
            }
            for i, item in enumerate(all_checklist)
        ],
        critical_alerts=[
            {"title": f"Masalah Aspek {weakest_aspect.capitalize()}", "aspect": weakest_aspect.capitalize(), "message": rc}
            for rc in plan.get("root_cause_analysis", [])[:2]
        ]
    )

    with col_btn1:
        st.download_button(
            label="Unduh Format Teks (.txt)",
            data=checklist_text_content,
            file_name=f"checklist_dapur_{selected_resto.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col_btn2:
        try:
            pdf_bytes = export_action_plan_pdf(
                overall_score=khs,
                status=status_label,
                action_items=[
                    {
                        "id": f"ACT-{i+1}",
                        "aspect": "Dapur",
                        "title": item[:35] + ("..." if len(item) > 35 else ""),
                        "target_pic": "Kru Dapur",
                        "deadline": "Shift Aktif",
                        "instruction": item,
                        "checked": checked_status.get(i, False)
                    }
                    for i, item in enumerate(all_checklist)
                ],
                critical_alerts=[
                    {"title": f"Fokus Perbaikan {weakest_aspect.capitalize()}", "aspect": weakest_aspect.capitalize(), "message": rc}
                    for rc in plan.get("root_cause_analysis", [])[:2]
                ]
            )
            st.download_button(
                label="Unduh Dokumen Resmi PDF (.pdf)",
                data=pdf_bytes,
                file_name=f"checklist_dapur_{selected_resto.lower().replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.caption(f"PDF Generator Notice: {e}")

    with col_btn3:
        action_export_df = pd.DataFrame([
            {"No": i+1, "Tindakan": item, "Status_Selesai": checked_status.get(i, False), "PIC": "Kru Dapur"}
            for i, item in enumerate(all_checklist)
        ])
        st.download_button(
            label="Unduh Tabel CSV (.csv)",
            data=action_export_df.to_csv(index=False),
            file_name=f"checklist_dapur_{selected_resto.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )
