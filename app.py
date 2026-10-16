"""Aplikasi Web UlasRasa - Asisten Diagnostik Ulasan Kuliner & Rekomendasi Evaluasi Dapur UMKM.
Dibangun dengan Streamlit untuk deployment Hugging Face Spaces.
"""

import os
import io
import re
from collections import Counter
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from src.absa_pipeline import ABSAPipeline
from src.action_engine import ActionPlanEngine
from src.preprocessing import clean_text

# Inisialisasi konfigurasi halaman
st.set_page_config(
    page_title="UlasRasa - Kitchen Intelligence Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS untuk tampilan elegan tanpa emoji
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-pos {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-neg {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-neu {
        background-color: #f1f5f9;
        color: #475569;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-na {
        background-color: #ffffff;
        color: #94a3b8;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        border: 1px dashed #cbd5e1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource
def load_pipeline():
    return ABSAPipeline(), ActionPlanEngine()

pipeline, action_engine = load_pipeline()

@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "data", "sample_reviews.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()

# Sidebar
st.sidebar.title("UlasRasa Navigation")
st.sidebar.caption("Sistem Intelijen Diagnostik Kuliner UMKM F&B")

df = load_data()

# Filter Resto di Sidebar
if not df.empty and "restaurant_name" in df.columns:
    all_restos = ["Semua Restoran"] + sorted(list(df["restaurant_name"].unique()))
    selected_resto = st.sidebar.selectbox("Pilih Restoran:", all_restos)
    if selected_resto != "Semua Restoran":
        filtered_df = df[df["restaurant_name"] == selected_resto].copy()
    else:
        filtered_df = df.copy()
else:
    filtered_df = df.copy()
    selected_resto = "Sampel Resto"

st.sidebar.divider()
st.sidebar.markdown("**Bobot Kitchen Health Score:**")
st.sidebar.text("- Rasa: 35%\n- Porsi: 20%\n- Kemasan: 15%\n- Harga: 15%\n- Pelayanan: 15%")

# Header Utama
st.title("UlasRasa: Intelligence Hub Evaluasi Dapur")
st.caption(f"Menganalisis {len(filtered_df)} ulasan pelanggan aktif | Target: {selected_resto}")

# Tabs Utama
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Ringkasan Eksekutif & Health Score",
    "2. Deep-Dive Aspek & Sentimen",
    "3. AI Kitchen Action Checklist",
    "4. Single Review Simulator"
])

eval_results = pipeline.evaluate_dataframe(filtered_df)

# ==================== TAB 1 ====================
with tab1:
    st.subheader("Ringkasan Kesehatan Dapur (Kitchen Health Overview)")
    khs = eval_results.get("kitchen_health_score", 0.0)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.metric(
            label="Kitchen Health Score (KHS)",
            value=f"{khs:.1f}%",
            delta=f"{khs - 75.0:.1f}% vs baseline" if khs >= 75 else f"{khs - 75.0:.1f}% perlu atensi"
        )
    with col2:
        status_label = "Optimal" if khs >= 80 else ("Cukup / Perlu Perbaikan" if khs >= 65 else "Kritis")
        st.metric(label="Status Operasional", value=status_label)
    with col3:
        st.write("**Spider Chart: Kesehatan 5 Aspek Dapur (0-100%):**")
        breakdown = eval_results.get("aspect_breakdown", {})
        categories = [k.capitalize() for k in breakdown.keys()]
        scores = [v["satisfaction_score"] for v in breakdown.values()]
        
        if categories:
            radar_cats = categories + [categories[0]]
            radar_scores = scores + [scores[0]]
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=radar_scores,
                theta=radar_cats,
                fill='toself',
                name='Skor Aktual',
                line=dict(color='#2563eb', width=2),
                fillcolor='rgba(37, 99, 235, 0.25)'
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=[80.0] * len(radar_cats),
                theta=radar_cats,
                mode='lines',
                name='Batas Prima (80%)',
                line=dict(color='#10b981', dash='dash', width=1.5)
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], tickvals=[25, 50, 75, 100])
                ),
                showlegend=True,
                height=320,
                margin=dict(l=30, r=30, t=20, b=30)
            )
            st.plotly_chart(fig_radar, use_container_width=True)

    st.divider()
    st.markdown("### Matriks Rincian 5 Aspek Kunci")
    table_rows = []
    for aspect, metrics in breakdown.items():
        table_rows.append({
            "Aspek": aspect.capitalize(),
            "Total Disebut": metrics["total_mentioned"],
            "Positif": metrics["positive"],
            "Netral": metrics["neutral"],
            "Negatif": metrics["negative"],
            "Tingkat Kepuasan (%)": f"{metrics['satisfaction_score']:.1f}%",
            "Tingkat Komplain (%)": f"{metrics['negative_rate']:.1f}%",
        })
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

# ==================== TAB 2 ====================
with tab2:
    st.subheader("Deep-Dive Analisis Sentimen per Aspek")
    selected_aspect = st.selectbox(
        "Pilih Aspek untuk Analisis Mendalam:",
        ["Rasa", "Porsi", "Harga", "Kemasan", "Pelayanan"]
    ).lower()
    
    aspect_data = breakdown.get(selected_aspect, {})
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Ulasan Positif", aspect_data.get("positive", 0))
    col_b.metric("Ulasan Netral", aspect_data.get("neutral", 0))
    col_c.metric("Ulasan Negatif (Komplain)", aspect_data.get("negative", 0))

    # Visualisasi Distribusi Sentimen & N-Gram Kata Kunci Komplain
    col_chart_dist, col_chart_ngram = st.columns([1, 1])
    with col_chart_dist:
        st.write("**Distribusi Sentimen Lintas 5 Aspek:**")
        dist_records = []
        for a_key, a_val in breakdown.items():
            dist_records.append({"Aspek": a_key.capitalize(), "Sentimen": "Positif", "Jumlah": a_val["positive"]})
            dist_records.append({"Aspek": a_key.capitalize(), "Sentimen": "Netral", "Jumlah": a_val["neutral"]})
            dist_records.append({"Aspek": a_key.capitalize(), "Sentimen": "Negatif", "Jumlah": a_val["negative"]})
        dist_df = pd.DataFrame(dist_records)
        fig_dist = px.bar(
            dist_df,
            x="Aspek",
            y="Jumlah",
            color="Sentimen",
            color_discrete_map={"Positif": "#22c55e", "Netral": "#eab308", "Negatif": "#ef4444"},
            barmode="stack",
            height=280
        )
        fig_dist.update_layout(margin=dict(l=20, r=20, t=10, b=20), legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"))
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_chart_ngram:
        st.write(f"**Top Kata Kunci Komplain ({selected_aspect.capitalize()}):**")
        if selected_aspect in filtered_df.columns:
            neg_texts = filtered_df[filtered_df[selected_aspect] == "negative"]["review_text"].tolist()
            words = []
            for t in neg_texts:
                cleaned_t = clean_text(str(t))
                toks = [w for w in cleaned_t.split() if len(w) >= 3 and w not in ["yang", "dan", "di", "ini", "itu", "ke", "dari", "untuk", "pada", "adalah"]]
                words.extend(toks)
            c = Counter(words)
            top_words = c.most_common(6)
            if top_words:
                fig_kw = go.Figure(go.Bar(
                    x=[item[1] for item in top_words][::-1],
                    y=[item[0] for item in top_words][::-1],
                    orientation="h",
                    marker=dict(color="#ef4444")
                ))
                fig_kw.update_layout(height=280, margin=dict(l=60, r=20, t=10, b=20), xaxis_title="Frekuensi")
                st.plotly_chart(fig_kw, use_container_width=True)
            else:
                st.info("Belum ada data komplain untuk aspek ini.")
        else:
            st.info("Aspek tidak ditemukan dalam dataset.")
    
    st.divider()
    st.markdown(f"### Riwayat Komplain pada Aspek {selected_aspect.capitalize()}")
    if selected_aspect in filtered_df.columns:
        neg_subset = filtered_df[filtered_df[selected_aspect] == "negative"]
        if not neg_subset.empty:
            for _, row in neg_subset.iterrows():
                with st.container():
                    st.markdown(f"**Menu:** {row.get('menu_item', 'Menu Umum')}")
                    st.write(f'"{row.get("review_text", "")}"')
                    st.caption(f"ID Ulasan: {row.get('review_id', '-')} | Resto: {row.get('restaurant_name', '-')}")
                    st.markdown("---")
        else:
            st.info(f"Tidak ada komplain negatif tercatat untuk aspek {selected_aspect.capitalize()}.")

# ==================== TAB 3 ====================
with tab3:
    st.subheader("AI Kitchen Action Checklist & SOP Recommendation")
    st.caption("Dihasilkan otomatis berdasarkan sintesis review negatif dan Kitchen Health Score.")
    
    # Kumpulkan keluhan negatif untuk prompt/generator
    sample_complaints = []
    for asp in ["rasa", "porsi", "harga", "kemasan", "pelayanan"]:
        if asp in filtered_df.columns:
            negs = filtered_df[filtered_df[asp] == "negative"]["review_text"].tolist()
            sample_complaints.extend(negs[:3])
            
    plan = action_engine.generate_action_plan(
        restaurant_name=selected_resto,
        evaluation_results=eval_results,
        sample_complaints=sample_complaints
    )
    
    st.markdown("#### 1. Ringkasan Akar Masalah Operasional (Root Cause Analysis)")
    for rc in plan.get("root_cause_analysis", []):
        st.markdown(f"- {rc}")
        
    st.divider()
    st.markdown("#### 2. Checklist Perbaikan Dapur Siap Cetak")
    st.write("Silakan centang item yang telah diselesaikan oleh kru dapur:")
    for idx, item in enumerate(plan.get("kitchen_action_checklist", [])):
        st.checkbox(item, key=f"check_{idx}")
        
    st.divider()
    st.markdown("#### 3. Rekomendasi Standard Operating Procedure (SOP)")
    for sop in plan.get("sop_recommendations", []):
        st.info(sop)
        
    # Download Checklist
    checklist_text = f"=== CHECKLIST PERBAIKAN DAPUR - {selected_resto.upper()} ===\n"
    checklist_text += f"Kitchen Health Score: {khs:.1f}%\n"
    checklist_text += f"Status: {status_label}\n\n"
    checklist_text += "AKAR MASALAH:\n"
    for rc in plan.get("root_cause_analysis", []):
        checklist_text += f"- {rc}\n"
    checklist_text += "\nCHECKLIST TINDAKAN DAPUR:\n"
    for item in plan.get("kitchen_action_checklist", []):
        checklist_text += f"[ ] {item}\n"
    checklist_text += "\nREKOMENDASI SOP:\n"
    for sop in plan.get("sop_recommendations", []):
        checklist_text += f"- {sop}\n"
        
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="📄 Download Checklist Format Text (.txt)",
            data=checklist_text,
            file_name=f"checklist_dapur_{selected_resto.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col_dl2:
        try:
            from src.utils.exporter import export_action_plan_pdf
            pdf_items = [
                {
                    "id": f"ACT-{i+1}",
                    "aspect": "Operasional Dapur",
                    "title": item[:35] + ("..." if len(item) > 35 else ""),
                    "target_pic": "Tim Dapur / Kru",
                    "deadline": "Shift Aktif",
                    "instruction": item,
                    "checked": st.session_state.get(f"check_{i}", False)
                }
                for i, item in enumerate(plan.get("kitchen_action_checklist", []))
            ]
            pdf_bytes = export_action_plan_pdf(
                overall_score=khs,
                status=status_label,
                action_items=pdf_items,
                critical_alerts=[{"title": "Prioritas Audit Dapur", "aspect": "Operasional", "message": rc} for rc in plan.get("root_cause_analysis", [])[:2]]
            )
            st.download_button(
                label="📑 Download Checklist Format PDF (.pdf)",
                data=pdf_bytes,
                file_name=f"checklist_dapur_{selected_resto.lower().replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.caption(f"PDF Exporter: {e}")

# ==================== TAB 4 ====================
with tab4:
    st.subheader("Simulator Diagnostik Ulasan Tunggal (Live AI Demo)")
    st.write("Uji coba deteksi sentimen 5 aspek pada ulasan bebas:")
    
    sample_input = "Ayamnya gurih renyah bumbunya mantap, cuma sambalnya dikit banget dan kemasan mangkok tumpah kuahnya di jalan."
    user_review = st.text_area("Masukkan Kalimat Ulasan:", value=sample_input, height=100)
    
    if st.button("Bedah Aspek Ulasan Sekarang"):
        single_result = pipeline.analyze_single_review(user_review)
        st.markdown(f"**Teks Normalisasi:** *{single_result['cleaned_text']}*")
        
        st.write("**Hasil Ekstraksi 5 Aspek:**")
        cols = st.columns(5)
        aspects_map = single_result["aspects"]
        
        for idx, (asp, data) in enumerate(aspects_map.items()):
            with cols[idx]:
                st.markdown(f"**{asp.capitalize()}**")
                if not data["mentioned"]:
                    st.markdown("<span class='badge-na'>Tidak Disebut</span>", unsafe_allow_html=True)
                elif data["sentiment"] == "positive":
                    st.markdown(f"<span class='badge-pos'>Positif ({data['confidence']*100:.0f}%)</span>", unsafe_allow_html=True)
                elif data["sentiment"] == "negative":
                    st.markdown(f"<span class='badge-neg'>Negatif ({data['confidence']*100:.0f}%)</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span class='badge-neu'>Netral ({data['confidence']*100:.0f}%)</span>", unsafe_allow_html=True)

st.markdown("---")
st.caption("UlasRasa Project - AI Engineering Bootcamp Ruangguru Batch 13 | Student ID: REAENG13TQJLN")
