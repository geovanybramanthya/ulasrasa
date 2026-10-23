"""Modul 3: Rencana Aksi (DESIGN.md Bag. 8 + PRD 4.4).

Susunan baru Tahap 4: ProgressAksi di puncak -> KartuAkarMasalah
(bernomor, cip mode persis P-E3) -> GrupDaftarAksi (checkbox rencana
di kartu daftar + checkbox kustom di kartu terpisah bila ada, kunci
action_chk_<resto>_<idx> global gabungan persis P-D9) ->
FormTambahAksi (expander) -> KartuSOP (bernomor) -> PusatUnduh
(PDF utama type primary, TXT dan CSV ghost).

Logika dipertahankan persis dari versi pra-perombakan: pembangunan
sample_complaints (maks 3 teks negatif per aspek, urutan aspek lama),
pemanggilan generate_action_plan, gabungan all_checklist (rencana
lalu kustom yang belum ada), serta konstruksi argumen
export_action_plan_text dan export_action_plan_pdf (P-X1/P-X2).
Seluruh literal HTML ditulis rata kiri.
"""

import pandas as pd
import streamlit as st

from src.ui import labels
from src.utils.exporter import export_action_plan_text, export_action_plan_pdf


def render(ctx, pipeline, action_engine):
    filtered_df = ctx["filtered_df"]
    eval_results = ctx["eval_results"]
    selected_resto = ctx["selected_resto"]
    khs = ctx["khs"]
    status_label = ctx["status_label"]
    weakest_aspect = ctx["weakest_aspect"]

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

    plan_checklist = list(plan.get("kitchen_action_checklist", []))
    all_checklist = list(plan.get("kitchen_action_checklist", []))
    for custom_item in st.session_state.custom_checklist_items:
        if custom_item not in all_checklist:
            all_checklist.append(custom_item)
    custom_checklist = all_checklist[len(plan_checklist):]

    # ---------------- ProgressAksi (puncak modul) ----------------
    with st.container(key="card_rencana_progress"):
        st.markdown(
            f"<div class='card-title'>{labels.RENCANA_PROGRESS_TITLE}</div>",
            unsafe_allow_html=True,
        )
        completed_count = 0
        for idx in range(len(all_checklist)):
            if st.session_state.get(f"action_chk_{selected_resto}_{idx}", False):
                completed_count += 1
        progress_ratio = completed_count / len(all_checklist) if all_checklist else 1.0
        st.progress(progress_ratio)
        st.markdown(
            f"<div class='card-sub'>{labels.RENCANA_PROGRESS_LINE.format(selesai=completed_count, total=len(all_checklist), persen=f'{progress_ratio * 100:.0f}')}</div>",
            unsafe_allow_html=True,
        )
        if st.button(labels.RENCANA_RESET_BTN):
            for idx in range(len(all_checklist)):
                st.session_state[f"action_chk_{selected_resto}_{idx}"] = False
            st.rerun()

    # ---------------- KartuAkarMasalah ----------------
    with st.container(key="card_rencana_rca"):
        st.markdown(
            f"<div class='card-title'>{labels.RENCANA_RCA_TITLE}</div>"
            f"<span class='chip pill-muted'>Mode rekomendasi: {mode_label}</span>"
            f"<div class='card-sub'>{labels.RENCANA_RCA_SUB}</div>",
            unsafe_allow_html=True,
        )
        rca_html = "".join(
            f"<div class='rca-row'><div class='rca-num'>{idx}</div><div class='rca-text'>{rc}</div></div>"
            for idx, rc in enumerate(plan.get("root_cause_analysis", []), 1)
        )
        if rca_html:
            st.markdown(rca_html, unsafe_allow_html=True)

    # ---------------- GrupDaftarAksi ----------------
    checked_status = {}
    with st.container(key="card_rencana_list"):
        st.markdown(
            f"<div class='card-title'>{labels.RENCANA_LIST_TITLE}</div>"
            f"<span class='chip pill-pos'>{labels.RENCANA_FOKUS_CHIP.format(aspek=weakest_aspect.capitalize())}</span>"
            f"<div class='card-sub'>{labels.RENCANA_LIST_SUB}</div>",
            unsafe_allow_html=True,
        )
        for idx, item in enumerate(plan_checklist):
            is_checked = st.checkbox(item, key=f"action_chk_{selected_resto}_{idx}")
            checked_status[idx] = is_checked

    if custom_checklist:
        with st.container(key="card_rencana_custom"):
            st.markdown(
                f"<div class='card-title'>{labels.RENCANA_CUSTOM_TITLE}</div>"
                f"<div class='card-sub'>{labels.RENCANA_CUSTOM_SUB}</div>",
                unsafe_allow_html=True,
            )
            for offset, item in enumerate(custom_checklist):
                idx = len(plan_checklist) + offset
                is_checked = st.checkbox(item, key=f"action_chk_{selected_resto}_{idx}")
                checked_status[idx] = is_checked

    # ---------------- FormTambahAksi ----------------
    with st.expander(labels.RENCANA_ADD_EXPANDER, expanded=False):
        custom_act_text = st.text_input(labels.RENCANA_ADD_LABEL, placeholder=labels.RENCANA_ADD_PLACEHOLDER)
        if st.button(labels.RENCANA_ADD_BTN, type="primary"):
            if custom_act_text.strip():
                st.session_state.custom_checklist_items.append(custom_act_text.strip())
                st.success(labels.RENCANA_ADD_OK)
                st.rerun()

    # ---------------- KartuSOP ----------------
    with st.container(key="card_rencana_sop"):
        st.markdown(
            f"<div class='card-title'>{labels.RENCANA_SOP_TITLE}</div>"
            f"<div class='card-sub'>{labels.RENCANA_SOP_SUB}</div>",
            unsafe_allow_html=True,
        )
        sop_html = "".join(
            f"<div class='sop-row'><div class='sop-num'>{idx}</div><div class='rca-text'>{sop_item}</div></div>"
            for idx, sop_item in enumerate(plan.get("sop_recommendations", []), 1)
        )
        if sop_html:
            st.markdown(sop_html, unsafe_allow_html=True)

    # ---------------- PusatUnduh ----------------
    with st.container(key="card_rencana_unduh"):
        st.markdown(
            f"<div class='card-title'>{labels.RENCANA_DL_TITLE}</div>"
            f"<div class='card-sub'>{labels.RENCANA_DL_SUB}</div>",
            unsafe_allow_html=True,
        )

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

        pdf_bytes = None
        pdf_error = None
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
        except Exception as e:
            pdf_error = e

        action_export_df = pd.DataFrame([
            {"No": i+1, "Tindakan": item, "Status_Selesai": checked_status.get(i, False), "PIC": "Kru Dapur"}
            for i, item in enumerate(all_checklist)
        ])

        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            if pdf_error is None:
                st.download_button(
                    label=labels.RENCANA_DL_PDF,
                    data=pdf_bytes,
                    file_name=f"checklist_dapur_{selected_resto.lower().replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.caption(f"PDF Generator Notice: {pdf_error}")

        with col_btn2:
            st.download_button(
                label=labels.RENCANA_DL_TXT,
                data=checklist_text_content,
                file_name=f"checklist_dapur_{selected_resto.lower().replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col_btn3:
            st.download_button(
                label=labels.RENCANA_DL_CSV,
                data=action_export_df.to_csv(index=False),
                file_name=f"checklist_dapur_{selected_resto.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
