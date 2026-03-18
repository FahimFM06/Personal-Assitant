import os
import time
import requests
import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="Weather Information", page_icon="🌦️", layout="wide")

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

GROQ_MODELS_UI = ["Llama 3.3 70B", "Llama 3.1 8B", "Gemma 2 9B"]
GROQ_MODEL_MAP = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "Gemma 2 9B": "gemma2-9b-it",
}

HF_MODELS_UI = ["Qwen 2.5 7B Instruct", "Phi 3.5 Mini Instruct"]
HF_MODEL_MAP = {
    "Qwen 2.5 7B Instruct": "Qwen/Qwen2.5-7B-Instruct",
    "Phi 3.5 Mini Instruct": "microsoft/Phi-3.5-mini-instruct",
}

# -----------------------------
# Session state
# -----------------------------
if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Midnight (Dark)"

if "weather_provider" not in st.session_state:
    st.session_state.weather_provider = "Groq"

if "weather_groq_model_name" not in st.session_state:
    st.session_state.weather_groq_model_name = GROQ_MODELS_UI[0]

if "weather_hf_model_name" not in st.session_state:
    st.session_state.weather_hf_model_name = HF_MODELS_UI[0]

if "weather_temperature" not in st.session_state:
    st.session_state.weather_temperature = 0.3

if "weather_max_tokens" not in st.session_state:
    st.session_state.weather_max_tokens = 700

if "weather_city" not in st.session_state:
    st.session_state.weather_city = ""

if "weather_result" not in st.session_state:
    st.session_state.weather_result = None

if "weather_ai_summary" not in st.session_state:
    st.session_state.weather_ai_summary = ""

T = THEMES[st.session_state.theme_name]

# =========================================================
# WEATHER CODE MAP
# =========================================================
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

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

    .weather-mini-card {{
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px;
        padding: 14px;
        box-shadow: var(--shadow) !important;
        color: var(--text) !important;
        text-align: center;
        min-height: 140px;
    }}

    .weather-big {{
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        color: var(--title) !important;
    }}

    .weather-label {{
        color: var(--muted) !important;
        font-size: 0.92rem;
        margin-bottom: 0.3rem;
    }}

    .weather-value {{
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--text) !important;
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


def safe_get(url, params=None, headers=None, retries=2, wait_seconds=2):
    last_error = None
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=25)

            if response.status_code == 429:
                if attempt < retries:
                    time.sleep(wait_seconds * (attempt + 1))
                    continue
                raise Exception("The weather service is busy right now. Please try again in a moment.")

            if response.status_code >= 500:
                if attempt < retries:
                    time.sleep(wait_seconds * (attempt + 1))
                    continue
                raise Exception("The weather service is temporarily unavailable. Please try again later.")

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt < retries:
                time.sleep(wait_seconds * (attempt + 1))
                continue

    raise Exception(f"Request failed: {last_error}")


@st.cache_data(show_spinner=False, ttl=3600)
def geocode_city(city_name: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city_name,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    response = safe_get(url, params=params)
    data = response.json()

    if "results" not in data or not data["results"]:
        return None

    place = data["results"][0]
    return {
        "name": place.get("name", city_name),
        "country": place.get("country", ""),
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "timezone": place.get("timezone", "auto")
    }


@st.cache_data(show_spinner=False, ttl=900)
def get_weather_data(lat: float, lon: float, timezone: str):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "forecast_days": 3,
        "timezone": timezone
    }
    response = safe_get(url, params=params)
    return response.json()


def build_weather_prompt(location_name: str, country: str, weather_json: dict) -> str:
    current = weather_json["current"]
    daily = weather_json["daily"]

    forecast_lines = []
    for i in range(len(daily["time"])):
        code = daily["weather_code"][i]
        forecast_lines.append(
            f"Date: {daily['time'][i]}, "
            f"Condition: {WEATHER_CODES.get(code, 'Unknown')}, "
            f"Max: {daily['temperature_2m_max'][i]}°C, "
            f"Min: {daily['temperature_2m_min'][i]}°C, "
            f"Rain chance: {daily['precipitation_probability_max'][i]}%"
        )

    return f"""
You are a helpful weather assistant.

Write a clear and friendly weather summary for {location_name}, {country}.

Please include:
1. current weather
2. short 3-day forecast
3. simple practical advice for daily life

Current weather:
- Temperature: {current['temperature_2m']}°C
- Feels like: {current['apparent_temperature']}°C
- Humidity: {current['relative_humidity_2m']}%
- Wind speed: {current['wind_speed_10m']} km/h
- Condition: {WEATHER_CODES.get(current['weather_code'], 'Unknown')}

Forecast:
{chr(10).join(forecast_lines)}
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
                {"role": "system", "content": "You are a helpful weather summary assistant."},
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
                {"role": "system", "content": "You are a helpful weather summary assistant."},
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
        st.markdown('<div class="page-title">Weather Information</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-sub">Search a city and get live weather data with an AI-written summary.</div>',
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

    city_value = st.text_input(
        "City name",
        value=st.session_state.weather_city,
        placeholder="Example: Darmstadt"
    )
    st.session_state.weather_city = city_value

    col_a, col_b = st.columns([1, 1])

    with col_a:
        if st.button("🌤️ Get Weather", use_container_width=True):
            if not st.session_state.weather_city.strip():
                st.error("Please enter a city name.")
            else:
                try:
                    with st.spinner("Fetching weather data..."):
                        location = geocode_city(st.session_state.weather_city.strip())

                        if not location:
                            st.error("City not found. Please try another city.")
                        else:
                            weather_data = get_weather_data(
                                location["latitude"],
                                location["longitude"],
                                location["timezone"]
                            )

                            st.session_state.weather_result = {
                                "location": location,
                                "weather_data": weather_data
                            }

                    if st.session_state.weather_result:
                        prompt = build_weather_prompt(
                            st.session_state.weather_result["location"]["name"],
                            st.session_state.weather_result["location"]["country"],
                            st.session_state.weather_result["weather_data"]
                        )

                        with st.spinner("Generating weather summary..."):
                            if st.session_state.weather_provider == "Groq":
                                model_id = GROQ_MODEL_MAP.get(
                                    st.session_state.weather_groq_model_name,
                                    "llama-3.3-70b-versatile"
                                )
                                st.session_state.weather_ai_summary = ask_groq(
                                    prompt=prompt,
                                    model_id=model_id,
                                    temperature=st.session_state.weather_temperature,
                                    max_tokens=st.session_state.weather_max_tokens
                                )
                            else:
                                model_id = HF_MODEL_MAP.get(
                                    st.session_state.weather_hf_model_name,
                                    "Qwen/Qwen2.5-7B-Instruct"
                                )
                                st.session_state.weather_ai_summary = ask_huggingface(
                                    prompt=prompt,
                                    model_id=model_id,
                                    temperature=st.session_state.weather_temperature,
                                    max_tokens=st.session_state.weather_max_tokens
                                )

                    st.rerun()

                except Exception as e:
                    st.error(f"Could not load weather data: {e}")

    with col_b:
        if st.button("🧹 Clear Weather", use_container_width=True):
            st.session_state.weather_city = ""
            st.session_state.weather_result = None
            st.session_state.weather_ai_summary = ""
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.weather_result:
        location = st.session_state.weather_result["location"]
        weather_data = st.session_state.weather_result["weather_data"]
        current = weather_data["current"]
        daily = weather_data["daily"]

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### Current Weather")
        st.markdown(
            f"""
            **Location:** {location['name']}, {location['country']}  
            **Condition:** {WEATHER_CODES.get(current['weather_code'], 'Unknown')}  
            **Temperature:** {current['temperature_2m']}°C  
            **Feels like:** {current['apparent_temperature']}°C  
            **Humidity:** {current['relative_humidity_2m']}%  
            **Wind speed:** {current['wind_speed_10m']} km/h
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### 3-Day Forecast")
        fc1, fc2, fc3 = st.columns(3)

        forecast_cols = [fc1, fc2, fc3]
        for i in range(min(3, len(daily["time"]))):
            with forecast_cols[i]:
                code = daily["weather_code"][i]
                st.markdown(
                    f"""
                    <div class="weather-mini-card">
                        <div class="weather-label">{daily['time'][i]}</div>
                        <div class="weather-big">{daily['temperature_2m_max'][i]}°C</div>
                        <div class="weather-label">{WEATHER_CODES.get(code, 'Unknown')}</div>
                        <div class="weather-value">Min: {daily['temperature_2m_min'][i]}°C</div>
                        <div class="weather-value">Rain: {daily['precipitation_probability_max'][i]}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### AI Weather Summary")
        if st.session_state.weather_ai_summary:
            st.markdown(st.session_state.weather_ai_summary)
        else:
            st.info("Weather data loaded. AI summary will appear here when available.")
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.info("Search for a city to view current weather, forecast, and AI summary.")
        st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="right-middle">', unsafe_allow_html=True)
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)

    st.markdown("**Provider**")
    st.session_state.weather_provider = st.selectbox(
        "Provider",
        PROVIDERS,
        index=PROVIDERS.index(st.session_state.weather_provider),
        label_visibility="collapsed",
    )

    st.caption("Choose the AI provider for summary generation")

    st.divider()

    st.markdown("**Select Model**")
    if st.session_state.weather_provider == "Groq":
        st.session_state.weather_groq_model_name = st.selectbox(
            "Groq Model",
            GROQ_MODELS_UI,
            index=GROQ_MODELS_UI.index(st.session_state.weather_groq_model_name),
            label_visibility="collapsed",
        )
        st.caption("Groq models")
    else:
        st.session_state.weather_hf_model_name = st.selectbox(
            "HF Model",
            HF_MODELS_UI,
            index=HF_MODELS_UI.index(st.session_state.weather_hf_model_name),
            label_visibility="collapsed",
        )
        st.caption("Hugging Face models")

    st.divider()

    st.markdown("**Temperature**")
    st.session_state.weather_temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.weather_temperature,
        step=0.1,
        label_visibility="collapsed",
    )
    st.caption(f"{st.session_state.weather_temperature:.2f}")

    st.markdown("**Max tokens**")
    st.session_state.weather_max_tokens = st.slider(
        "Max tokens",
        min_value=200,
        max_value=2000,
        value=st.session_state.weather_max_tokens,
        step=100,
        label_visibility="collapsed",
    )
    st.caption(str(st.session_state.weather_max_tokens))

    st.divider()

    if st.button("🔁 Reset session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
