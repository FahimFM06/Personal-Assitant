import os
import requests
import pandas as pd
import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="Smart Location Finder", page_icon="📍", layout="wide")

# =========================================================
# THEMES
# =========================================================
THEMES = {
    "Cloud (Light)": {
        "app_bg": "#f6f7fb",
        "panel_bg": "#ffffff",
        "title": "#0f172a",
        "sub": "#475569",
        "border": "#e5e7eb",
        "text": "#0f172a",
        "muted": "#64748b",
        "shadow": "0 10px 30px rgba(15, 23, 42, 0.08)",
        "input_bg": "#ffffff",
        "widget_bg": "#ffffff",
        "widget_text": "#0f172a",
        "menu_bg": "#ffffff",
        "menu_text": "#0f172a",
        "btn_bg": "#111827",
        "btn_text": "#ffffff",
        "btn_border": "#111827",
        "card_bg": "#ffffff",
    },
    "Midnight (Dark)": {
        "app_bg": "#0b1220",
        "panel_bg": "#0f172a",
        "title": "#e5e7eb",
        "sub": "#94a3b8",
        "border": "#1f2a44",
        "text": "#e5e7eb",
        "muted": "#94a3b8",
        "shadow": "0 10px 26px rgba(0,0,0,0.45)",
        "input_bg": "#0f172a",
        "widget_bg": "#111827",
        "widget_text": "#e5e7eb",
        "menu_bg": "#0b1220",
        "menu_text": "#e5e7eb",
        "btn_bg": "#111827",
        "btn_text": "#e5e7eb",
        "btn_border": "#1f2a44",
        "card_bg": "#111827",
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
        "panel_bg": "rgba(20, 20, 22, 0.72)",
        "title": "#f3f4f6",
        "sub": "#cbd5e1",
        "border": "rgba(255,255,255,0.10)",
        "text": "#f3f4f6",
        "muted": "#cbd5e1",
        "shadow": "0 12px 30px rgba(0,0,0,0.55)",
        "input_bg": "rgba(20, 20, 22, 0.72)",
        "widget_bg": "rgba(20, 20, 22, 0.72)",
        "widget_text": "#f3f4f6",
        "menu_bg": "rgba(20, 20, 22, 0.92)",
        "menu_text": "#f3f4f6",
        "btn_bg": "rgba(20, 20, 22, 0.72)",
        "btn_text": "#f3f4f6",
        "btn_border": "rgba(255,255,255,0.12)",
        "card_bg": "rgba(20, 20, 22, 0.72)",
    },
}

PROVIDERS = ["Groq", "Hugging Face"]

# =========================================================
# MODELS
# =========================================================
GROQ_MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "GPT-OSS 120B": "openai/gpt-oss-120b",
    "GPT-OSS 20B": "openai/gpt-oss-20b",
}

HF_MODELS = {
    "Qwen 2.5 7B Instruct": "Qwen/Qwen2.5-7B-Instruct"
}

# -----------------------------
# Session state
# -----------------------------
if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Midnight (Dark)"

if "location_provider" not in st.session_state:
    st.session_state.location_provider = "Groq"

if "location_groq_model_name" not in st.session_state:
    st.session_state.location_groq_model_name = list(GROQ_MODELS.keys())[0]

if "location_hf_model_name" not in st.session_state:
    st.session_state.location_hf_model_name = list(HF_MODELS.keys())[0]

if "location_temperature" not in st.session_state:
    st.session_state.location_temperature = 0.3

if "location_max_tokens" not in st.session_state:
    st.session_state.location_max_tokens = 700

if "location_query" not in st.session_state:
    st.session_state.location_query = ""

if "location_result" not in st.session_state:
    st.session_state.location_result = None

if "location_ai_summary" not in st.session_state:
    st.session_state.location_ai_summary = ""

T = THEMES[st.session_state.theme_name]

# -----------------------------
# CSS
# -----------------------------
st.markdown(
    f"""
    <style>
    :root {{
        --app-bg: {T["app_bg"]};
        --panel-bg: {T["panel_bg"]};
        --title: {T["title"]};
        --sub: {T["sub"]};
        --border: {T["border"]};
        --text: {T["text"]};
        --muted: {T["muted"]};
        --shadow: {T["shadow"]};
        --input-bg: {T["input_bg"]};
        --widget-bg: {T["widget_bg"]};
        --widget-text: {T["widget_text"]};
        --menu-bg: {T["menu_bg"]};
        --menu-text: {T["menu_text"]};
        --btn-bg: {T["btn_bg"]};
        --btn-text: {T["btn_text"]};
        --btn-border: {T["btn_border"]};
        --card-bg: {T["card_bg"]};
    }}

    .stApp {{
        background: var(--app-bg) !important;
        color: var(--text) !important;
    }}

    html, body, [class*="css"] {{
        color: var(--text) !important;
    }}

    .main .block-container {{
        max-width: 1300px;
        padding-top: 1rem;
        padding-bottom: 0.5rem;
    }}

    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    .page-title {{
        font-size: 2.0rem;
        font-weight: 800;
        color: var(--title) !important;
        margin: 0 0 0.1rem 0;
    }}

    .page-sub {{
        color: var(--sub) !important;
        margin: 0 0 0.8rem 0;
        font-size: 0.95rem;
    }}

    .right-panel {{
        background: var(--panel-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px;
        padding: 14px;
        box-shadow: var(--shadow) !important;
        color: var(--text) !important;
    }}

    .right-middle {{
        margin-top: 140px;
    }}

    .content-card {{
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px;
        padding: 16px;
        box-shadow: var(--shadow) !important;
        color: var(--text) !important;
        margin-bottom: 14px;
    }}

    .mini-card {{
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px;
        padding: 14px;
        box-shadow: var(--shadow) !important;
        color: var(--text) !important;
        min-height: 120px;
    }}

    .mini-label {{
        color: var(--muted) !important;
        font-size: 0.9rem;
        margin-bottom: 0.3rem;
    }}

    .mini-value {{
        color: var(--text) !important;
        font-size: 1rem;
        font-weight: 700;
        word-wrap: break-word;
    }}

    .stTextArea textarea,
    .stTextInput input {{
        background: var(--input-bg) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
    }}

    div[data-testid="stSelectbox"] > div {{
        background: var(--widget-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }}

    div[data-testid="stSelectbox"] * {{
        color: var(--widget-text) !important;
    }}

    div[role="listbox"] {{
        background: var(--menu-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }}

    div[role="listbox"] * {{
        color: var(--menu-text) !important;
    }}

    div[role="option"] {{
        background: transparent !important;
    }}

    div[role="option"]:hover {{
        background: rgba(100, 116, 139, 0.12) !important;
    }}

    button[data-testid="stPopoverButton"] {{
        background: var(--widget-bg) !important;
        color: var(--widget-text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }}

    .stButton > button {{
        background: var(--btn-bg) !important;
        color: var(--btn-text) !important;
        border: 1px solid var(--btn-border) !important;
        border-radius: 12px !important;
    }}

    .stSlider * {{
        color: var(--text) !important;
    }}

    .stCaption {{
        color: var(--muted) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HELPERS
# =========================================================
def go_back():
    st.switch_page("Home.py")


@st.cache_data(show_spinner=False, ttl=3600)
def search_location(query: str):
    """
    Search a place using OpenStreetMap Nominatim.
    Cached to reduce repeated requests.
    """
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "streamlit-location-finder/1.0"
    }
    params = {
        "q": query,
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1
    }

    response = requests.get(url, params=params, headers=headers, timeout=25)
    response.raise_for_status()
    data = response.json()

    if not data:
        return None

    item = data[0]
    return {
        "display_name": item.get("display_name", query),
        "lat": float(item["lat"]),
        "lon": float(item["lon"]),
        "type": item.get("type", "unknown"),
        "class": item.get("class", "unknown"),
        "address": item.get("address", {})
    }


def build_location_prompt(location_data: dict) -> str:
    """
    Build a clean prompt for AI summary.
    """
    address = location_data.get("address", {})

    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or address.get("county")
        or "Unknown"
    )

    country = address.get("country", "Unknown")

    return f"""
You are a helpful location assistant.

Write a short, human-friendly summary of this place.
Keep it practical and easy to understand.

Please include:
1. what this place is
2. where it is
3. why someone may search for it
4. a short practical note for a visitor or user

Location details:
- Full name: {location_data.get("display_name", "Unknown")}
- Type: {location_data.get("type", "Unknown")}
- Category: {location_data.get("class", "Unknown")}
- City/Area: {city}
- Country: {country}
- Latitude: {location_data.get("lat")}
- Longitude: {location_data.get("lon")}
"""


def ask_groq(prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
    try:
        from groq import Groq
    except Exception:
        return "Groq package not installed. Run: pip install groq"

    api_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        return "GROQ_API_KEY is missing. Add it in your environment variables or Streamlit secrets."

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are a helpful location explanation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling Groq: {e}"


def ask_huggingface(prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
    api_key = os.environ.get("HF_TOKEN") or st.secrets.get("HF_TOKEN", "")
    if not api_key:
        return "HF_TOKEN is missing. Add it in your environment variables or Streamlit secrets."

    try:
        client = InferenceClient(api_key=api_key)
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are a helpful location explanation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling Hugging Face: {e}"


# =========================================================
# TOP BAR
# =========================================================
top_left, top_right = st.columns([0.75, 0.25], vertical_alignment="center")

with top_left:
    back_col, title_col = st.columns([0.16, 0.84], vertical_alignment="center")

    with back_col:
        if st.button("⬅ Back", use_container_width=True):
            go_back()

    with title_col:
        st.markdown('<div class="page-title">Smart Location Finder</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-sub">Search any place and get map coordinates plus an AI summary.</div>',
            unsafe_allow_html=True
        )

with top_right:
    with st.popover("🎨 Theme ▾", use_container_width=True):
        st.session_state.theme_name = st.selectbox(
            "Theme",
            list(THEMES.keys()),
            index=list(THEMES.keys()).index(st.session_state.theme_name),
        )

# =========================================================
# MAIN AREA
# =========================================================
left_col, right_col = st.columns([3, 1], gap="large")

with left_col:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)

    query_value = st.text_input(
        "Search location",
        value=st.session_state.location_query,
        placeholder="Example: Darmstadt, Germany"
    )
    st.session_state.location_query = query_value

    c1, c2 = st.columns(2)

    with c1:
        if st.button("📍 Find Location", use_container_width=True):
            if not st.session_state.location_query.strip():
                st.error("Please enter a place name.")
            else:
                try:
                    with st.spinner("Searching location..."):
                        result = search_location(st.session_state.location_query.strip())

                    if not result:
                        st.error("Location not found. Please try another search.")
                    else:
                        st.session_state.location_result = result
                        prompt = build_location_prompt(result)

                        with st.spinner("Generating AI summary..."):
                            if st.session_state.location_provider == "Groq":
                                model_id = GROQ_MODELS[st.session_state.location_groq_model_name]
                                st.session_state.location_ai_summary = ask_groq(
                                    prompt=prompt,
                                    model_id=model_id,
                                    temperature=st.session_state.location_temperature,
                                    max_tokens=st.session_state.location_max_tokens
                                )
                            else:
                                model_id = HF_MODELS[st.session_state.location_hf_model_name]
                                st.session_state.location_ai_summary = ask_huggingface(
                                    prompt=prompt,
                                    model_id=model_id,
                                    temperature=st.session_state.location_temperature,
                                    max_tokens=st.session_state.location_max_tokens
                                )
                        st.rerun()

                except Exception as e:
                    st.error(f"Something went wrong: {e}")

    with c2:
        if st.button("🧹 Clear Location", use_container_width=True):
            st.session_state.location_query = ""
            st.session_state.location_result = None
            st.session_state.location_ai_summary = ""
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.location_result:
        result = st.session_state.location_result
        address = result.get("address", {})

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### Location Details")
        st.markdown(
            f"""
            **Name:** {result.get('display_name', 'Unknown')}  
            **Latitude:** {result.get('lat')}  
            **Longitude:** {result.get('lon')}  
            **Type:** {result.get('type', 'Unknown')}  
            **Category:** {result.get('class', 'Unknown')}
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### Quick Info")
        q1, q2, q3 = st.columns(3)

        city_or_town = address.get("city") or address.get("town") or address.get("village") or "N/A"

        with q1:
            st.markdown(
                f"""
                <div class="mini-card">
                    <div class="mini-label">City / Town</div>
                    <div class="mini-value">{city_or_town}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with q2:
            st.markdown(
                f"""
                <div class="mini-card">
                    <div class="mini-label">State</div>
                    <div class="mini-value">{address.get("state", "N/A")}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with q3:
            st.markdown(
                f"""
                <div class="mini-card">
                    <div class="mini-label">Country</div>
                    <div class="mini-value">{address.get("country", "N/A")}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("### Map View")
        map_df = pd.DataFrame({"lat": [result["lat"]], "lon": [result["lon"]]})
        st.map(map_df, zoom=11)

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### Address Information")
        st.markdown(
            f"""
            **Road:** {address.get('road', 'N/A')}  
            **City/Town:** {city_or_town}  
            **State:** {address.get('state', 'N/A')}  
            **Postcode:** {address.get('postcode', 'N/A')}  
            **Country:** {address.get('country', 'N/A')}
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### AI Location Summary")
        if st.session_state.location_ai_summary:
            st.markdown(st.session_state.location_ai_summary)
        else:
            st.info("The AI summary will appear here after a successful search.")
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.info("Search for a place to view map coordinates, address details, and AI summary.")
        st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="right-middle">', unsafe_allow_html=True)
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)

    st.markdown("**Provider**")
    st.session_state.location_provider = st.selectbox(
        "Provider",
        PROVIDERS,
        index=PROVIDERS.index(st.session_state.location_provider),
        label_visibility="collapsed",
    )
    st.caption("Choose the AI provider for summary generation")

    st.divider()

    st.markdown("**Select Model**")
    if st.session_state.location_provider == "Groq":
        st.session_state.location_groq_model_name = st.selectbox(
            "Groq Model",
            list(GROQ_MODELS.keys()),
            index=list(GROQ_MODELS.keys()).index(st.session_state.location_groq_model_name),
            label_visibility="collapsed",
        )
        st.caption("Groq models")
    else:
        st.session_state.location_hf_model_name = st.selectbox(
            "HF Model",
            list(HF_MODELS.keys()),
            index=list(HF_MODELS.keys()).index(st.session_state.location_hf_model_name),
            label_visibility="collapsed",
        )
        st.caption("Hugging Face models")

    st.divider()

    st.markdown("**Temperature**")
    st.session_state.location_temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.location_temperature,
        step=0.1,
        label_visibility="collapsed",
    )
    st.caption(f"{st.session_state.location_temperature:.2f}")

    st.markdown("**Max tokens**")
    st.session_state.location_max_tokens = st.slider(
        "Max tokens",
        min_value=200,
        max_value=2000,
        value=st.session_state.location_max_tokens,
        step=100,
        label_visibility="collapsed",
    )
    st.caption(str(st.session_state.location_max_tokens))

    st.divider()

    if st.button("🔁 Reset session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
