import streamlit as st

st.set_page_config(page_title="AI Dashboard", page_icon="🤖", layout="wide")

# =========================================================
# 3 THEMES ONLY:
# 1) Cloud (Light)
# 2) Midnight (Dark)
# 3) Night Mode (your photo style: dark brushed/metal look)
# =========================================================

THEMES = {
    "Cloud (Light)": {
        "app_bg": "#f6f7fb",
        "title": "#0f172a",
        "sub": "#64748b",
        "card_bg": "#ffffff",
        "card_border": "#e5e7eb",
        "card_shadow": "0 10px 30px rgba(15, 23, 42, 0.08)",
        "card_shadow_hover": "0 14px 34px rgba(15, 23, 42, 0.12)",
        "btn_text": "#111827",
        "info_bg": "#dbeafe",
        "info_border": "#bfdbfe",
        "info_text": "#1d4ed8",
    },
    "Midnight (Dark)": {
        "app_bg": "#0b1220",
        "title": "#e5e7eb",
        "sub": "#94a3b8",
        "card_bg": "#0f172a",
        "card_border": "#1f2a44",
        "card_shadow": "0 10px 26px rgba(0,0,0,0.45)",
        "card_shadow_hover": "0 14px 30px rgba(0,0,0,0.55)",
        "btn_text": "#e5e7eb",
        "info_bg": "rgba(56, 189, 248, 0.10)",
        "info_border": "rgba(56, 189, 248, 0.25)",
        "info_text": "#e5e7eb",
    },
    # Night Mode = inspired by your uploaded dark “brushed metal” photo
    "Night Mode": {
        # CSS background with subtle vertical brushed lines + vignette
        "app_bg": """
            radial-gradient(ellipse at center, rgba(255,255,255,0.10) 0%, rgba(0,0,0,0.55) 60%, rgba(0,0,0,0.85) 100%),
            repeating-linear-gradient(90deg,
                rgba(255,255,255,0.06) 0px,
                rgba(255,255,255,0.06) 1px,
                rgba(0,0,0,0.00) 2px,
                rgba(0,0,0,0.00) 4px
            ),
            linear-gradient(180deg, #0a0a0b 0%, #111214 35%, #070708 100%)
        """,
        "title": "#f3f4f6",
        "sub": "#cbd5e1",
        "card_bg": "rgba(20, 20, 22, 0.72)",
        "card_border": "rgba(255,255,255,0.10)",
        "card_shadow": "0 12px 30px rgba(0,0,0,0.55)",
        "card_shadow_hover": "0 16px 38px rgba(0,0,0,0.65)",
        "btn_text": "#f3f4f6",
        "info_bg": "rgba(255,255,255,0.06)",
        "info_border": "rgba(255,255,255,0.12)",
        "info_text": "#e5e7eb",
    },
}

# default theme
if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Cloud (Light)"

# Top-right logo (URL). If you want local image, tell me and I’ll give base64 version.
LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Robot_icon.svg/256px-Robot_icon.svg.png"

T = THEMES[st.session_state.theme_name]

# -----------------------------
# Apply CSS (theme + logo + buttons + info box)
# -----------------------------
st.markdown(
    f"""
    <style>
    :root {{
        --app-bg: {T["app_bg"]};
        --title: {T["title"]};
        --sub: {T["sub"]};
        --card-bg: {T["card_bg"]};
        --card-border: {T["card_border"]};
        --card-shadow: {T["card_shadow"]};
        --card-shadow-hover: {T["card_shadow_hover"]};
        --btn-text: {T["btn_text"]};
        --info-bg: {T["info_bg"]};
        --info-border: {T["info_border"]};
        --info-text: {T["info_text"]};
    }}

    .stApp {{
        background: var(--app-bg) !important;
    }}

    .main .block-container {{
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    .title-text {{
        font-size: 2.7rem;
        font-weight: 800;
        color: var(--title);
        text-align: center;
        margin-bottom: 0.4rem;
    }}

    .sub-text {{
        font-size: 1.05rem;
        color: var(--sub);
        text-align: center;
        margin-bottom: 2rem;
    }}

    /* Card button styling */
    .card-btn button {{
        height: 150px !important;
        border-radius: 22px !important;
        border: 1px solid var(--card-border) !important;
        background: var(--card-bg) !important;
        box-shadow: var(--card-shadow) !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        color: var(--btn-text) !important;
        white-space: pre-line !important;
        transition: all 0.12s ease-in-out !important;
    }}

    .card-btn button:hover {{
        box-shadow: var(--card-shadow-hover) !important;
        transform: translateY(-1px) !important;
    }}

    /* Make Streamlit info box match theme */
    div[data-testid="stAlert"] {{
        background: var(--info-bg) !important;
        border: 1px solid var(--info-border) !important;
    }}
    div[data-testid="stAlert"] * {{
        color: var(--info-text) !important;
    }}

    /* Top-right logo */
    .top-right-logo {{
        position: fixed;
        top: 12px;
        right: 16px;
        z-index: 9999;
        width: 42px;
        height: 42px;
        border-radius: 14px;
        background: rgba(255,255,255,0.75);
        border: 1px solid rgba(229,231,235,0.9);
        backdrop-filter: blur(8px);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        pointer-events: none; /* do not block clicks */
    }}
    .top-right-logo img {{
        width: 28px;
        height: 28px;
        object-fit: contain;
    }}
    </style>

    <div class="top-right-logo">
        <img src="{LOGO_URL}" alt="logo"/>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Header + Theme button (Option A: Popover)
# -----------------------------
header_left, header_right = st.columns([0.78, 0.22], vertical_alignment="center")

with header_left:
    st.markdown('<div class="title-text">AI Research & Productivity Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-text">Select one tool from the dashboard</div>', unsafe_allow_html=True)

with header_right:
    with st.popover("🎨 Theme", use_container_width=True):
        st.session_state.theme_name = st.selectbox(
            "Theme",
            list(THEMES.keys()),
            index=list(THEMES.keys()).index(st.session_state.theme_name),
        )

# -----------------------------
# Navigation helper
# -----------------------------
def go_to(page_path: str):
    try:
        st.switch_page(page_path)
    except Exception:
        st.error(f"Page not found: {page_path}")
        st.stop()

# -----------------------------
# Dashboard buttons
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("Study Chat", use_container_width=True, key="qa"):
        go_to("pages/1_AI_Research_Study_QA.py")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("Paper Summary with Q&A", use_container_width=True, key="summ"):
        go_to("pages/2_Research_Paper_Summarizer.py")
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("Math Solver", use_container_width=True, key="math"):
        go_to("pages/3_Math_Statistics_Solver.py")
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("Code Assistant", use_container_width=True, key="code"):
        go_to("pages/4_AI_Coding_Assistant.py")
    st.markdown('</div>', unsafe_allow_html=True)

c5, c6, c7 = st.columns(3)

with c5:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("Weather", use_container_width=True, key="weather"):
        go_to("pages/5_Weather_Information.py")
    st.markdown('</div>', unsafe_allow_html=True)

with c6:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("Place Finder", use_container_width=True, key="location"):
        go_to("pages/6_Smart_Location_Finder.py")
    st.markdown('</div>', unsafe_allow_html=True)

with c7:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("News Insights", use_container_width=True, key="news"):
        go_to("pages/7_AI_News_Analyzer.py")
    st.markdown('</div>', unsafe_allow_html=True)

