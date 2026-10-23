"""Tema UI UlasRasa.

Tahap 0: CSS lama dipindah apa adanya dari app.py (konstanta CUSTOM_CSS)
tanpa perubahan isi, sesuai gerbang verbatim PRD Implementasi UI.
Penulisan ulang dari token DESIGN.md dilakukan pada Tahap 1.
"""

import streamlit as st

OLD_CSS = """
<style>
/* Import Font Modern */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* Global Reset & Base Canvas */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #FAF8F5 !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #1C1917 !important;
}

[data-testid="stHeader"] {
    background-color: rgba(250, 248, 245, 0.85) !important;
    backdrop-filter: blur(10px) !important;
}

/* Sidebar Styling Warm Neutral */
[data-testid="stSidebar"] {
    background-color: #F4F1EA !important;
    border-right: 1px solid #E8E4DA !important;
}

[data-testid="stSidebar"] hr {
    border-color: #E2DDD3 !important;
    margin: 0.85rem 0 !important;
}

/* Typography Hierarchy */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #1C1917 !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

p, span, label {
    color: #44403C;
}

/* Brand Header in Sidebar */
.brand-container {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 0 12px 0;
}

.brand-logo-badge {
    width: 38px;
    height: 38px;
    background: #C84B2F;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(200, 75, 47, 0.25);
    flex-shrink: 0;
}

.brand-text-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #1C1917;
    letter-spacing: -0.01em;
    line-height: 1.1;
}

.brand-text-sub {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #78716C;
}

/* Pulsing Status Dot (Living UI Effect) */
.live-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #FFFFFF;
    border: 1px solid #E2DDD3;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #15803D;
    margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(45, 35, 25, 0.03);
}

.pulse-dot {
    width: 7px;
    height: 7px;
    background-color: #15803D;
    border-radius: 50%;
    box-shadow: 0 0 0 0 rgba(21, 128, 61, 0.5);
    animation: pulse 1.8s infinite;
}

@keyframes pulse {
    0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(21, 128, 61, 0.6);
    }
    70% {
        transform: scale(1);
        box-shadow: 0 0 0 6px rgba(21, 128, 61, 0);
    }
    100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(21, 128, 61, 0);
    }
}

/* Section Header in Sidebar */
.sidebar-section-header {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #78716C;
    margin: 14px 0 8px 0;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* THE HIGHLIGHTER: Navigation Menu Styling */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label {
    background: #FFFFFF !important;
    border: 1px solid #EAE6DE !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    margin-bottom: 6px !important;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    cursor: pointer !important;
    box-shadow: 0 1px 3px rgba(45, 35, 25, 0.02) !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:hover {
    border-color: #C84B2F !important;
    background: #FFFDFB !important;
    transform: translateX(4px) !important;
    box-shadow: 0 4px 12px rgba(45, 35, 25, 0.05) !important;
}

/* HIGHLIGHTER AKTIF: Border Kiri Tebal & Background Lembut */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(90deg, #FFF4EE 0%, #FAF0E8 100%) !important;
    border-color: #C84B2F !important;
    border-left: 5px solid #C84B2F !important;
    box-shadow: 0 4px 14px rgba(200, 75, 47, 0.12) !important;
    transform: translateX(4px) !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) p {
    color: #C84B2F !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"]:checked + div {
    background-color: #C84B2F !important;
    border-color: #C84B2F !important;
}

/* Live Reactive Outlet Micro-Card in Sidebar */
.sidebar-outlet-card {
    background: #FFFFFF;
    border: 1px solid #EAE6DE;
    border-radius: 12px;
    padding: 14px 16px;
    margin-top: 10px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(45, 35, 25, 0.03);
    position: relative;
    border-left: 4px solid #C84B2F;
}

.sidebar-outlet-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 6px;
}

.sidebar-outlet-name {
    font-size: 0.88rem;
    font-weight: 700;
    color: #1C1917;
    line-height: 1.25;
}

.sidebar-outlet-score-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-top: 8px;
    margin-bottom: 4px;
}

.sidebar-score-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    color: #78716C;
}

.sidebar-score-val {
    font-size: 1.25rem;
    font-weight: 800;
}

.sidebar-progress-track {
    background: #EAE6DE;
    border-radius: 4px;
    height: 5px;
    overflow: hidden;
    margin-bottom: 8px;
}

.sidebar-outlet-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 8px;
}

.outlet-chip {
    background: #F5F3ED;
    border: 1px solid #E2DDD3;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    color: #57534E;
}

.outlet-chip-alert {
    background: #FEF2F2;
    border-color: #FEE2E2;
    color: #B91C1C;
    font-weight: 700;
}

/* Sidebar Weighted Composition Card */
.sidebar-weights-card {
    background: #FFFFFF;
    border: 1px solid #EAE6DE;
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: 8px;
}

.weights-bar-composite {
    display: flex;
    height: 6px;
    border-radius: 4px;
    overflow: hidden;
    margin: 8px 0;
}

.weights-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    font-size: 0.72rem;
    color: #57534E;
}

.weight-item {
    background: #FAF8F5;
    border: 1px solid #EAE6DE;
    padding: 3px 6px;
    border-radius: 4px;
}

/* Glass & Card Surfaces */
.ulas-card {
    background: #FFFFFF;
    border: 1px solid #EAE6DE;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 20px -2px rgba(45, 35, 25, 0.04), 0 2px 6px -1px rgba(45, 35, 25, 0.02);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.ulas-card:hover {
    border-color: #DDD8CD;
    box-shadow: 0 8px 30px -4px rgba(45, 35, 25, 0.08);
    transform: translateY(-2px);
}

.ulas-card-accent {
    background: linear-gradient(135deg, #FFFDFB 0%, #FAF5EE 100%);
    border-left: 4px solid #C84B2F;
}

/* Metric Display Hero */
.kpi-container {
    background: #FFFFFF;
    border: 1px solid #EAE6DE;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(45, 35, 25, 0.03);
    position: relative;
    overflow: hidden;
}

.kpi-title {
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #78716C;
    margin-bottom: 4px;
}

.kpi-value {
    font-size: 2.1rem;
    font-weight: 800;
    color: #1C1917;
    line-height: 1.1;
    margin-bottom: 6px;
}

.kpi-subtitle {
    font-size: 0.8rem;
    color: #57534E;
}

/* Pill Badges (Semantic, Zero Emoji) */
.badge-prima {
    background-color: #F0FDF4;
    color: #15803D;
    border: 1px solid #DCFCE7;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.76rem;
    display: inline-flex;
    align-items: center;
    letter-spacing: 0.02em;
}

.badge-waspada {
    background-color: #FEFCE8;
    color: #B45309;
    border: 1px solid #FEF08A;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.76rem;
    display: inline-flex;
    align-items: center;
    letter-spacing: 0.02em;
}

.badge-kritis {
    background-color: #FEF2F2;
    color: #B91C1C;
    border: 1px solid #FEE2E2;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.76rem;
    display: inline-flex;
    align-items: center;
    letter-spacing: 0.02em;
}

.badge-aspek {
    background-color: #F5F3ED;
    color: #44403C;
    border: 1px solid #E2DDD3;
    padding: 3px 8px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.74rem;
}

/* Micro-Pills for Breakdown Cards */
.metric-pill-pos {
    background: #F0FDF4;
    color: #15803D;
    border: 1px solid #DCFCE7;
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.75rem;
}

.metric-pill-neu {
    background: #FEFCE8;
    color: #B45309;
    border: 1px solid #FEF08A;
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.75rem;
}

.metric-pill-neg {
    background: #FEF2F2;
    color: #B91C1C;
    border: 1px solid #FEE2E2;
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.75rem;
}

/* Interactive Workflow Step Indicator */
.workflow-step {
    background: #FFFFFF;
    border: 1px solid #EAE6DE;
    border-radius: 10px;
    padding: 12px 14px;
    text-align: center;
    box-shadow: 0 2px 6px rgba(45, 35, 25, 0.02);
    transition: transform 0.2s ease;
}

.workflow-step:hover {
    border-color: #C84B2F;
    transform: translateY(-2px);
}

.workflow-num {
    display: inline-block;
    width: 24px;
    height: 24px;
    background: #C84B2F;
    color: #FFFFFF;
    border-radius: 50%;
    font-size: 0.75rem;
    font-weight: 700;
    line-height: 24px;
    margin-bottom: 6px;
}

.workflow-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #1C1917;
    margin-bottom: 2px;
}

.workflow-desc {
    font-size: 0.72rem;
    color: #78716C;
    line-height: 1.25;
}

/* Review Cards */
.review-item {
    background: #FFFFFF;
    border: 1px solid #EAE6DE;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    border-left: 3px solid #EAE6DE;
    transition: border-color 0.2s ease;
}

.review-item:hover {
    border-left-color: #C84B2F;
}

/* Code Snippet Box */
.clean-text-box {
    background: #F5F3ED;
    border: 1px solid #E2DDD3;
    border-radius: 8px;
    padding: 10px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #292524;
}

/* Buttons Styling */
.stButton > button {
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    letter-spacing: -0.01em !important;
}

.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: inherit !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: inherit !important;
    line-height: inherit !important;
}

/* PRIMARY BUTTON: The Active Menu Highlighter & Main Actions */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #C84B2F 0%, #A8351D 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid #8F2B15 !important;
    font-weight: 800 !important;
    box-shadow: 0 6px 20px -2px rgba(200, 75, 47, 0.45), 0 2px 6px -1px rgba(200, 75, 47, 0.25) !important;
    transform: translateY(-2px) !important;
}

.stButton > button[kind="primary"] p,
.stButton > button[data-testid="baseButton-primary"] p {
    color: #FFFFFF !important;
    font-weight: 800 !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.25) !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(135deg, #B33E24 0%, #942E17 100%) !important;
    box-shadow: 0 8px 24px -2px rgba(200, 75, 47, 0.55), 0 3px 8px -1px rgba(200, 75, 47, 0.35) !important;
    transform: translateY(-3px) !important;
}

/* SECONDARY BUTTON: Inactive Navigation Menu Cards */
.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"] {
    background-color: #FFFFFF !important;
    color: #1C1917 !important;
    border: 1.5px solid #DDD8CD !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px -1px rgba(45, 35, 25, 0.06), 0 1px 3px rgba(45, 35, 25, 0.03) !important;
}

.stButton > button[kind="secondary"] p,
.stButton > button[data-testid="baseButton-secondary"] p {
    color: #1C1917 !important;
    font-weight: 700 !important;
}

.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover {
    border-color: #C84B2F !important;
    background-color: #FFFDFB !important;
    color: #C84B2F !important;
    box-shadow: 0 6px 18px -2px rgba(45, 35, 25, 0.12), 0 2px 6px -1px rgba(45, 35, 25, 0.06) !important;
    transform: translateY(-2px) !important;
}

.stButton > button[kind="secondary"]:hover p,
.stButton > button[data-testid="baseButton-secondary"]:hover p {
    color: #C84B2F !important;
}

/* Download Buttons Styling */
.stDownloadButton > button {
    background-color: #FFFFFF !important;
    color: #1C1917 !important;
    border: 1.5px solid #DDD8CD !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 10px 18px !important;
    box-shadow: 0 2px 8px -1px rgba(45, 35, 25, 0.06) !important;
    transition: all 0.22s ease !important;
}

.stDownloadButton > button p {
    color: #1C1917 !important;
    font-weight: 700 !important;
}

.stDownloadButton > button:hover {
    border-color: #C84B2F !important;
    background-color: #FFFDFB !important;
    box-shadow: 0 6px 18px -2px rgba(45, 35, 25, 0.12) !important;
    transform: translateY(-2px) !important;
}

.stDownloadButton > button:hover p {
    color: #C84B2F !important;
}

/* Top Synchronized Navigation Bar */
.top-nav-bar {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    background-color: #F4F1EA;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid #EAE6DE;
    margin-bottom: 20px;
}

.top-nav-pill {
    padding: 10px 14px;
    border-radius: 8px;
    text-align: center;
    font-size: 0.85rem;
    font-weight: 600;
    color: #57534E;
    background: transparent;
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.2s ease;
}

.top-nav-pill-active {
    background: #FFFFFF !important;
    color: #C84B2F !important;
    border: 1px solid #EAE6DE !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px rgba(45, 35, 25, 0.06) !important;
}

.active-nav-indicator {
    display: inline-block;
    width: 6px;
    height: 6px;
    background: #C84B2F;
    border-radius: 50%;
    margin-right: 6px;
}
</style>
"""


def inject_old_css() -> None:
    st.markdown(OLD_CSS, unsafe_allow_html=True)
