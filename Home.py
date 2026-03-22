import streamlit as st
import base64
from pathlib import Path

st.set_page_config(page_title="AI Dashboard", page_icon="🤖", layout="wide")

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
        "label_text": "#0f172a",
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
        "label_text": "#e5e7eb",
    },
    "Night Mode": {
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
        "label_text": "#f3f4f6",
    },
}

if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Cloud (Light)"

T = THEMES[st.session_state.theme_name]

# -------------------------------------------------
# Logo image paths inside your GitHub project
# -------------------------------------------------
IMG_STUDY = "assets/logos/study_chat.png"
IMG_PAPER = "assets/logos/paper_summary.png"
IMG_MATH = "assets/logos/math_solver.png"
IMG_CODE = "code_assistant.png"
IMG_WEATHER = "assets/logos/weather.png"
IMG_LOCATION = "assets/logos/place_finder.png"
IMG_NEWS = "assets/logos/news_insights.png"


def img_to_base64(img_path: str) -> str:
    path = Path(img_path)
    if not path.exists():
        return ""
    return base64.b64encode(path.read_bytes()).decode()


study_b64 = img_to_base64(IMG_STUDY)
paper_b64 = img_to_base64(IMG_PAPER)
math_b64 = img_to_base64(IMG_MATH)
code_b64 = img_to_base64(IMG_CODE)
weather_b64 = img_to_base64(IMG_WEATHER)
location_b64 = img_to_base64(IMG_LOCATION)
news_b64 = img_to_base64(IMG_NEWS)

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
        --label-text: {T["label_text"]};
    }}

    .stApp {{
        background: var(--app-bg) !important;
    }}

    .main .block-container {{
        max-width: 1250px;
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

    div[data-testid="stAlert"] {{
        background: var(--info-bg) !important;
        border: 1px solid var(--info-border) !important;
    }}

    div[data-testid="stAlert"] * {{
        color: var(--info-text) !important;
    }}

    .logo-card {{
        text-align: center;
        margin-bottom: 22px;
    }}

    .logo-label {{
        margin-top: 10px;
        font-size: 1.02rem;
        font-weight: 700;
        color: var(--label-text);
        text-align: center;
    }}

    .logo-btn div[data-testid="stButton"] > button {{
        width: 100% !important;
        height: 185px !important;
        border-radius: 24px !important;
        border: 1px solid var(--card-border) !important;
        background-color: var(--card-bg) !important;
        box-shadow: var(--card-shadow) !important;
        background-repeat: no-repeat !important;
        background-position: center center !important;
        background-size: contain !important;
        color: transparent !important;
        transition: all 0.15s ease-in-out !important;
        padding: 0 !important;
    }}

    .logo-btn div[data-testid="stButton"] > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: var(--card-shadow-hover) !important;
        border: 1px solid rgba(59,130,246,0.45) !important;
    }}

    .logo-btn div[data-testid="stButton"] > button p {{
        color: transparent !important;
    }}

    .study-btn div[data-testid="stButton"] > button {{
        background-image: url("data:image/png;base64,{study_b64}");
    }}

    .paper-btn div[data-testid="stButton"] > button {{
        background-image: url("data:image/png;base64,{paper_b64}");
    }}

    .math-btn div[data-testid="stButton"] > button {{
        background-image: url("data:image/png;base64,{math_b64}");
    }}

    .code-btn div[data-testid="stButton"] > button {{
        background-image: url("data:image/png;base64,{code_b64}");
    }}

    .weather-btn div[data-testid="stButton"] > button {{
        background-image: url("data:image/png;base64,{weather_b64}");
    }}

    .location-btn div[data-testid="stButton"] > button {{
        background-image: url("data:image/png;base64,{location_b64}");
    }}

    .news-btn div[data-testid="stButton"] > button {{
        background-image: url("data:image/png;base64,{news_b64}");
    }}
    </style>
    """,
    unsafe_allow_html=True
)

header_left, header_right = st.columns([0.78, 0.22], vertical_alignment="center")

with header_left:
    st.markdown(
        '<div class="title-text">AI Research & Productivity Dashboard</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sub-text">Select one tool from the dashboard</div>',
        unsafe_allow_html=True
    )

with header_right:
    with st.popover("🎨 Theme", use_container_width=True):
        st.session_state.theme_name = st.selectbox(
            "Theme",
            list(THEMES.keys()),
            index=list(THEMES.keys()).index(st.session_state.theme_name),
        )

def go_to(page_path: str):
    try:
        st.switch_page(page_path)
    except Exception:
        st.error(f"Page not found: {page_path}")
        st.stop()

def logo_button(label: str, key: str, page_path: str, css_class: str):
    st.markdown(f'<div class="logo-card logo-btn {css_class}">', unsafe_allow_html=True)
    clicked = st.button(" ", key=key, use_container_width=True)
    st.markdown(f'<div class="logo-label">{label}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if clicked:
        go_to(page_path)

c1, c2, c3, c4 = st.columns(4)

with c1:
    logo_button("Study Chat", "qa", "pages/1_AI_Research_Study_QA.py", "study-btn")

with c2:
    logo_button("Paper Summary with Q&A", "summ", "pages/2_Research_Paper_Summarizer.py", "paper-btn")

with c3:
    logo_button("Math Solver", "math", "pages/3_Math_Statistics_Solver.py", "math-btn")

with c4:
    logo_button("Code Assistant", "code", "pages/4_AI_Coding_Assistant.py", "code-btn")

c5, c6, c7 = st.columns(3)

with c5:
    logo_button("Weather", "weather", "pages/5_Weather_Information.py", "weather-btn")

with c6:
    logo_button("Place Finder", "location", "pages/6_Smart_Location_Finder.py", "location-btn")

with c7:
    logo_button("News Insights", "news", "pages/7_AI_News_Analyzer.py", "news-btn")
