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


def build_khs_donut_figure(khs: float):
    """HeroKHS (DESIGN.md Bag. 8): donat tebal skor kesehatan dapur.

    Sisa cincin memudar di atas kartu gradasi hijau; angka KHS tampil
    sebagai anotasi JetBrains Mono putih di tengah donat. Hanya visual:
    nilai berasal dari ctx (dihitung engine), tidak dihitung ulang di sini.
    """
    nilai = max(0.0, min(100.0, float(khs)))
    fig = go.Figure(
        data=[
            go.Pie(
                values=[nilai, 100.0 - nilai],
                hole=0.72,
                direction="clockwise",
                sort=False,
                marker=dict(colors=["#FFFFFF", "rgba(255,255,255,0.28)"],
                            line=dict(width=0)),
                textinfo="none",
                hoverinfo="skip",
            )
        ]
    )
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=6, r=6, t=6, b=6),
        height=190,
        annotations=[
            dict(
                text=f"<b>{nilai:.1f}%</b>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(family="JetBrains Mono, Consolas, monospace",
                          size=27, color="#FFFFFF"),
            )
        ],
    )
    return fig


def build_satisfaction_bar_figure(breakdown: dict):
    """Grafik batang horizontal skor kepuasan 5 aspek (DESIGN.md Bag. 8).

    Warna batang per aspek mengikuti token ASPECT_COLORS; garis putus-
    putus di 70 berlabel 'Batas kritis'. Figur hanya membaca breakdown
    dari ctx; urutan aspek dibalik agar Rasa tampil paling atas.
    """
    from src.ui.labels import ASPECT_ORDER
    from src.ui.theme import ASPECT_COLORS

    aspek_terbalik = list(reversed(ASPECT_ORDER))
    skor = [float(breakdown.get(a, {}).get("satisfaction_score", 0.0)) for a in aspek_terbalik]
    warna = [ASPECT_COLORS[a][0] for a in aspek_terbalik]
    nama = [a.capitalize() for a in aspek_terbalik]
    fig = go.Figure(
        data=[
            go.Bar(
                x=skor, y=nama, orientation="h",
                marker=dict(color=warna, line=dict(width=0)),
                text=[f"{s:.1f}%" for s in skor],
                textposition="outside",
                textfont=dict(family="JetBrains Mono, Consolas, monospace", size=12, color="#14231B"),
                hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
                width=0.58,
            )
        ]
    )
    fig.add_vline(
        x=70, line_dash="dash", line_color="#64756B", line_width=1.4,
    )
    # Label garis ditaruh di strip atas figur (di luar area batang) agar
    # tidak menabrak label nilai batang teratas.
    fig.add_annotation(
        x=70, y=1.04, xref="x", yref="paper",
        text="Batas kritis", showarrow=False, xanchor="left",
        font=dict(size=11, color="#64756B", family="Inter, sans-serif"),
    )
    fig.update_layout(
        xaxis=dict(range=[0, 112], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(tickfont=dict(size=13, color="#14231B", family="Inter, sans-serif")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=6, r=10, t=24, b=6),
        height=275,
        bargap=0.35,
    )
    return fig
