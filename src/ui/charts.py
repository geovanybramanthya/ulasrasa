"""Pembangun figur Plotly UlasRasa.

Tahap 0: figur radar Modul Ringkasan dipindah verbatim dari app.py lama.
"""

import plotly.graph_objects as go


def build_radar_figure(breakdown):
    """Spider chart keseimbangan 5 aspek (verbatim dari app.py lama)."""
    categories = [k.capitalize() for k in breakdown.keys()]
    scores = [v["satisfaction_score"] for v in breakdown.values()]

    if categories:
        radar_cats = categories + [categories[0]]
        radar_scores = scores + [scores[0]]

        fig_radar = go.Figure()

        # Area Skor Aktual
        fig_radar.add_trace(go.Scatterpolar(
            r=radar_scores,
            theta=radar_cats,
            fill='toself',
            name='Skor Aktual',
            line=dict(color='#C84B2F', width=2.5),
            fillcolor='rgba(200, 75, 47, 0.22)',
            marker=dict(size=6, color='#C84B2F')
        ))

        # Garis Batas Prima (80%)
        fig_radar.add_trace(go.Scatterpolar(
            r=[80.0] * len(radar_cats),
            theta=radar_cats,
            mode='lines',
            name='Batas Prima (80%)',
            line=dict(color='#15803D', dash='dash', width=1.5)
        ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickvals=[25, 50, 75, 100],
                    tickfont=dict(size=10, color="#78716C"),
                    gridcolor="#EAE6DE"
                ),
                angularaxis=dict(
                    tickfont=dict(size=11, color="#1C1917", weight="bold"),
                    gridcolor="#EAE6DE"
                ),
                bgcolor="#FAF8F5"
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
            height=360,
            margin=dict(l=35, r=35, t=25, b=35)
        )
    return fig_radar
