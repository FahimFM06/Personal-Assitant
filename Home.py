import streamlit as st

st.set_page_config(page_title="AI Dashboard", page_icon="🤖", layout="wide")

# -----------------------------
# Themes (4–5 options)
# -----------------------------
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
    },
    "Ocean (Blue)": {
        "app_bg": "linear-gradient(135deg, #eef6ff 0%, #f7fbff 60%, #eef2ff 100%)",
        "title": "#0b1b3a",
        "sub": "#3b5b7a",
        "card_bg": "#ffffff",
        "card_border": "#dbeafe",
        "card_shadow": "0 10px 26px rgba(2, 132, 199, 0.12)",
        "card_shadow_hover": "0 14px 32px rgba(2, 132, 199, 0.18)",
        "btn_text": "#0b1b3a",
    },
    "Mint (Calm)": {
        "app_bg": "linear-gradient(135deg, #ecfeff 0%, #f7fffb 60%, #f0fdf4 100%)",
        "title": "#052e2b",
        "sub": "#0f766e",
        "card_bg": "#ffffff",
        "card_border": "#ccfbf1",
        "card_shadow": "0 10px 26px rgba(13, 148, 136, 0.12)",
        "card_shadow_hover": "0 14px 32px rgba(13, 148, 136, 0.18)",
        "btn_text": "#052e2b",
    },
    "Sunset (Warm)": {
        "app_bg": "linear-gradient(135deg, #fff7ed 0%, #fff1f2 55%, #f5f3ff 100%)",
        "title": "#3b0a2a",
        "sub": "#7c2d12",
        "card_bg": "#ffffff",
        "card_border": "#fed7aa",
        "card_shadow": "0 10px 26px rgba(234, 88, 12, 0.12)",
        "card_shadow_hover": "0 14px 32px rgba(234, 88, 12, 0.18)",
        "btn_text": "#3b0a2a",
    },
}

# Default theme
if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Cloud (Light)"

# Logo (use URL). If you want local file, tell me and I’ll give base64 method.
LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Robot_icon.svg/256px-Robot_icon.svg.png"

T = THEMES[st.session_state.theme_name]

# -----------------------------
# CSS
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
    }}

    .card-btn button:hover {{
        border: 1px solid rgba(203, 213, 225, 1) !important;
        box-shadow: var(--card-shadow-hover) !important;
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
    # Theme button -> opens dropdown like your photo
    with st.popover("🎨 Theme", use_container_width=True):
        st.session_state.theme_name = st.selectbox(
            "Theme",
            list(THEMES.keys()),
            index=list(THEMES.keys()).index(st.session_state.theme_name),
            label_visibility="visible",
        )

        # (No st.write here — you said you don't want text output)

# Re-load theme after selection (Streamlit reruns automatically, but this ensures T updates in same run)
T = THEMES[st.session_state.theme_name]

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
# Dashboard buttons (your same layout)
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("🤖💬\nAI Research Study QA", use_container_width=True, key="qa"):
        go_to("pages/1_AI_Research_Study_QA.py")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("📄🧠\nResearch Paper Summarizer", use_container_width=True, key="summ"):
        go_to("pages/2_Research_Paper_Summarizer.py")
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("📊➗\nMath & Statistics Solver", use_container_width=True, key="math"):
        go_to("pages/3_Math_Statistics_Solver.py")
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("💻🧠\nAI Coding Assistant", use_container_width=True, key="code"):
        go_to("pages/4_AI_Coding_Assistant.py")
    st.markdown('</div>', unsafe_allow_html=True)

c5, c6, c7 = st.columns(3)

with c5:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("🌦️📍\nWeather Information", use_container_width=True, key="weather"):
        go_to("pages/5_Weather_Information.py")
    st.markdown('</div>', unsafe_allow_html=True)

with c6:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("🗺️📍\nSmart Location Finder", use_container_width=True, key="location"):
        go_to("pages/6_Smart_Location_Finder.py")
    st.markdown('</div>', unsafe_allow_html=True)

with c7:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("📰🤖\nAI News Analyzer", use_container_width=True, key="news"):
        go_to("pages/7_AI_News_Analyzer.py")
    st.markdown('</div>', unsafe_allow_html=True)

st.info("All 7 dashboard tools are now connected.")
