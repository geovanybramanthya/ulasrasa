"""Landing UlasRasa (Adendum Revisi Landing 2026-10-23, DESIGN.md).

Pintu masuk aplikasi: satu akun demo = satu resto. Kiri = brand + judul +
daftar akun; kanan = panel visual besar (ilustrasi + kartu kaca satu
kalimat nilai). Klik tombol pada kartu akun menjalankan
core.enter_account() sebagai on_click (pola callback, aman dari
StreamlitAPIException), lalu run berikutnya masuk dashboard.

Skor Kesehatan Dapur pada kartu dihitung RIIL per akun lewat
core.compute_context() (pipeline.evaluate_dataframe yang sama dengan
dashboard) - tidak ada angka hardcode di file ini.

Kelas CSS khusus landing yang dipakai di sini (definisinya milik
src/ui/theme.py, dikoordinasikan lewat koordinator): .landing-khs-num,
.landing-khs-row, .landing-acct-head, .landing-glass, serta kontainer
berkunci st-key-landing_acct_* dan st-key-landing_visual. Selama tema
belum memuatnya, tampilan ditopang kelas generik yang sudah ada
(.brand-*, .card-title, .card-sub, .label-caps, .chip, .greeting,
.status-line) + style inline seperlunya.
"""

import os

import streamlit as st

from src.ui import core, labels
from src.ui.components import LOGO_SVG

_STATUS_CHIP_CLASS = {
    "badge-prima": "pill-pos",
    "badge-waspada": "pill-neu",
    "badge-kritis": "pill-neg",
}


def _fmt_khs(khs: float) -> str:
    """Format skor gaya Indonesia: 55.84 -> '55,84'."""
    return f"{khs:.2f}".replace(".", ",")


@st.cache_data(show_spinner=False)
def _img_data_uri(path: str) -> str:
    import base64

    with open(path, "rb") as fh:
        return "data:image/jpeg;base64," + base64.b64encode(fh.read()).decode("ascii")


def _asset_path() -> str:
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(repo_root, "assets", "ilustrasi-landing.jpg")


def render(pipeline) -> None:
    """Render landing saja (dipanggil app.py bila belum ada akun aktif)."""
    accounts = []
    for acc in core.list_demo_accounts():
        ev = core.compute_context(acc["df"], pipeline)
        accounts.append({
            "name": acc["name"],
            "count": acc["count"],
            "khs": ev["khs"],
            "status_short": ev["status_label"].split(" (")[0],
            "chip_class": _STATUS_CHIP_CLASS.get(ev["status_class"], "pill-muted"),
        })

    col_left, col_right = st.columns([1.05, 0.95], gap="large")

    with col_left:
        st.markdown(
            f"""
<div class='brand-lockup' style='margin-bottom: 20px;'>
<div class='brand-badge'>{LOGO_SVG}</div>
<div>
<div class='brand-name' style='font-size: 1.45rem;'>{labels.BRAND_NAME}</div>
<div class='brand-sub'>{labels.BRAND_SUB}</div>
</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown(f"<div class='greeting'>{labels.LANDING_TITLE}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='status-line'>{labels.LANDING_SUB}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='label-caps' style='margin: 20px 0 10px 0;'>{labels.LANDING_ACCOUNTS_LABEL}</div>",
            unsafe_allow_html=True,
        )
        for i, acc in enumerate(accounts):
            with st.container(key=f"landing_acct_{i}"):
                st.markdown(
                    f"""
<div class='landing-acct-head' style='display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;'>
<div class='card-title' style='margin-bottom: 2px;'>{acc['name']}</div>
<span class='chip pill-pos'>{labels.DEMO_CHIP}</span>
</div>
<div class='card-sub'>{labels.LANDING_REVIEWS_LINE.format(n=acc['count'])}</div>
<div class='label-caps' style='margin-top: 12px;'>{labels.LANDING_KHS_LABEL}</div>
<div class='landing-khs-row' style='display: flex; align-items: center; gap: 10px; margin: 2px 0 12px 0;'>
<span class='landing-khs-num num' style='font-size: 1.5rem;'>{_fmt_khs(acc['khs'])}</span>
<span class='chip {acc['chip_class']}'>{acc['status_short']}</span>
</div>
""",
                    unsafe_allow_html=True,
                )
                st.button(
                    labels.LANDING_ENTER_BTN,
                    key=f"landing_enter_{i}",
                    type="primary",
                    use_container_width=True,
                    on_click=core.enter_account,
                    args=(acc["name"],),
                )

    with col_right:
        with st.container(key="landing_visual"):
            img_path = _asset_path()
            if os.path.exists(img_path):
                st.markdown(
                    f"<img src='{_img_data_uri(img_path)}' style='width:100%;display:block'/>",
                    unsafe_allow_html=True,
                )
            st.markdown(
                f"""
<div class='landing-glass'>
<div class='card-title'>{labels.LANDING_VISUAL_TITLE}</div>
<div class='card-sub'>{labels.LANDING_VALUE}</div>
</div>
""",
                unsafe_allow_html=True,
            )
