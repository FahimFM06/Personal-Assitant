import requests
import streamlit as st
from groq import Groq
from huggingface_hub import InferenceClient

# ---------------------------------------------------
# Page config
# ---------------------------------------------------
st.set_page_config(
    page_title="Weather Information",
    page_icon="🌦️",
    layout="wide"
)

# ---------------------------------------------------
# API keys from Streamlit secrets
# ---------------------------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

# ---------------------------------------------------
# Model lists
# ---------------------------------------------------
GROQ_MODELS = {
    "Llama 3.3 70B (Best quality)": "llama-3.3-70b-versatile",
    "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant"
}

HF_MODELS = {
    "Qwen 2.5 7B Instruct": "Qwen/Qwen2.5-7B-Instruct",
}

# ---------------------------------------------------
# Session state
# ---------------------------------------------------
if "weather_result" not in st.session_state:
    st.session_state.weather_result = None

if "weather_ai_summary" not in st.session_state:
    st.session_state.weather_ai_summary = ""

if "weather_provider" not in st.session_state:
    st.session_state.weather_provider = "Groq"

if "weather_temperature" not in st.session_state:
    st.session_state.weather_temperature = 0.3

if "weather_max_tokens" not in st.session_state:
    st.session_state.weather_max_tokens = 500

# ---------------------------------------------------
# Weather code to text
# ---------------------------------------------------
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm"
}

# ---------------------------------------------------
# Helper: get latitude and longitude from city name
# ---------------------------------------------------
def geocode_city(city_name: str):
    """
    Convert a city name into latitude and longitude using Open-Meteo Geocoding API.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city_name,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
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

# ---------------------------------------------------
# Helper: fetch weather from Open-Meteo
# ---------------------------------------------------
def get_weather_data(lat: float, lon: float, timezone: str):
    """
    Get current weather and 3-day forecast from Open-Meteo.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "forecast_days": 3,
        "timezone": timezone
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()

# ---------------------------------------------------
# Helper: build AI prompt
# ---------------------------------------------------
def build_weather_prompt(location_name: str, country: str, weather_json: dict):
    """
    Build a simple weather prompt for the LLM.
    """
    current = weather_json["current"]
    daily = weather_json["daily"]

    day_lines = []
    for i in range(len(daily["time"])):
        code = daily["weather_code"][i]
        day_lines.append(
            f"Date: {daily['time'][i]}, "
            f"Condition: {WEATHER_CODES.get(code, 'Unknown')}, "
            f"Max temp: {daily['temperature_2m_max'][i]}°C, "
            f"Min temp: {daily['temperature_2m_min'][i]}°C, "
            f"Rain chance: {daily['precipitation_probability_max'][i]}%"
        )

    prompt = f"""
You are a helpful weather assistant.

Write a clear and human-friendly weather summary for {location_name}, {country}.
Keep it practical and easy to understand.

Please include:
1. Current weather
2. Short 3-day forecast
3. Simple advice like umbrella/jacket/hot weather suggestion

Current weather:
- Temperature: {current['temperature_2m']}°C
- Feels like: {current['apparent_temperature']}°C
- Humidity: {current['relative_humidity_2m']}%
- Wind speed: {current['wind_speed_10m']} km/h
- Condition: {WEATHER_CODES.get(current['weather_code'], 'Unknown')}

Forecast:
{chr(10).join(day_lines)}
"""
    return prompt

# ---------------------------------------------------
# Helper: ask Groq
# ---------------------------------------------------
def ask_groq(prompt: str, model_id: str, temperature: float, max_tokens: int):
    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are a helpful weather explanation assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content

# ---------------------------------------------------
# Helper: ask Hugging Face
# ---------------------------------------------------
def ask_huggingface(prompt: str, model_id: str, temperature: float, max_tokens: int):
    client = InferenceClient(api_key=HF_TOKEN)

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are a helpful weather explanation assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content

# ---------------------------------------------------
# Style
# ---------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: #f6f7fb;
}

.main .block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.page-title {
    font-size: 3rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 0.25rem;
}

.page-subtitle {
    font-size: 1.05rem;
    color: #64748b;
    margin-bottom: 1.5rem;
}

.stButton > button {
    border-radius: 14px;
    height: 44px;
    border: 1px solid #d1d5db;
    background: white;
}

.sidebar-note {
    font-size: 0.92rem;
    color: #6b7280;
    margin-top: 0.25rem;
}

.info-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 14px;
}

.summary-box {
    color: #111827;
    font-size: 1rem;
    line-height: 1.7;
    background: transparent;
    border: none;
    padding: 0.2rem 0;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Layout
# ---------------------------------------------------
left_col, right_col = st.columns([4.8, 1.8], gap="large")

with left_col:
    top1, top2 = st.columns([1, 6])

    with top1:
        if st.button("⬅ Back", use_container_width=True):
            st.switch_page("Home.py")

    with top2:
        st.markdown('<div class="page-title">Weather Information</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-subtitle">Search a city and get both live weather data and an AI-written weather summary.</div>',
            unsafe_allow_html=True
        )

    city_name = st.text_input("City name", placeholder="Example: Darmstadt")

    if st.button("🌦️ Get Weather", use_container_width=True):
        if not city_name.strip():
            st.error("Please enter a city name.")
        else:
            try:
                with st.spinner("Fetching weather data..."):
                    location = geocode_city(city_name.strip())

                    if not location:
                        st.error("City not found. Please try another name.")
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

                        prompt = build_weather_prompt(
                            location["name"],
                            location["country"],
                            weather_data
                        )

                        provider = st.session_state.weather_provider

                        if provider == "Groq":
                            if not GROQ_API_KEY:
                                st.error("Groq API key not found in Streamlit secrets.")
                            else:
                                st.session_state.weather_ai_summary = ask_groq(
                                    prompt=prompt,
                                    model_id=st.session_state.weather_model_id,
                                    temperature=st.session_state.weather_temperature,
                                    max_tokens=st.session_state.weather_max_tokens
                                )
                        else:
                            if not HF_TOKEN:
                                st.error("HF token not found in Streamlit secrets.")
                            else:
                                st.session_state.weather_ai_summary = ask_huggingface(
                                    prompt=prompt,
                                    model_id=st.session_state.weather_model_id,
                                    temperature=st.session_state.weather_temperature,
                                    max_tokens=st.session_state.weather_max_tokens
                                )

            except Exception as e:
                st.error(f"Something went wrong: {e}")

    st.write("")

    if st.session_state.weather_result:
        location = st.session_state.weather_result["location"]
        weather_data = st.session_state.weather_result["weather_data"]
        current = weather_data["current"]
        daily = weather_data["daily"]

        st.markdown("### Current Weather")
        st.markdown(
            f"""
            <div class="info-card">
                <b>Location:</b> {location['name']}, {location['country']}<br>
                <b>Temperature:</b> {current['temperature_2m']}°C<br>
                <b>Feels like:</b> {current['apparent_temperature']}°C<br>
                <b>Humidity:</b> {current['relative_humidity_2m']}%<br>
                <b>Wind speed:</b> {current['wind_speed_10m']} km/h<br>
                <b>Condition:</b> {WEATHER_CODES.get(current['weather_code'], 'Unknown')}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 3-Day Forecast")
        day_cols = st.columns(3)

        for i in range(min(3, len(daily["time"]))):
            with day_cols[i]:
                code = daily["weather_code"][i]
                st.markdown(
                    f"""
                    <div class="info-card">
                        <b>{daily['time'][i]}</b><br><br>
                        {WEATHER_CODES.get(code, 'Unknown')}<br>
                        Max: {daily['temperature_2m_max'][i]}°C<br>
                        Min: {daily['temperature_2m_min'][i]}°C<br>
                        Rain: {daily['precipitation_probability_max'][i]}%
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("### AI Weather Summary")
        if st.session_state.weather_ai_summary:
            st.markdown(
                f'<div class="summary-box">{st.session_state.weather_ai_summary}</div>',
                unsafe_allow_html=True
            )
        else:
            st.info("The AI summary will appear here after fetching weather.")

with right_col:
    st.markdown("## Provider")
    provider = st.selectbox(
        "Choose provider",
        ["Groq", "Hugging Face"],
        index=0,
        label_visibility="collapsed"
    )
    st.session_state.weather_provider = provider

    st.write("")

    if provider == "Groq":
        st.markdown("## Select Model")
        model_name = st.selectbox(
            "Groq model",
            list(GROQ_MODELS.keys()),
            label_visibility="collapsed"
        )
        st.session_state.weather_model_id = GROQ_MODELS[model_name]
        st.markdown('<div class="sidebar-note">Groq models only</div>', unsafe_allow_html=True)
    else:
        st.markdown("## Select Model")
        model_name = st.selectbox(
            "HF model",
            list(HF_MODELS.keys()),
            label_visibility="collapsed"
        )
        st.session_state.weather_model_id = HF_MODELS[model_name]
        st.markdown('<div class="sidebar-note">Free/open Hugging Face models</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("---")

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.weather_temperature,
        step=0.1
    )
    st.session_state.weather_temperature = temperature

    max_tokens = st.slider(
        "Max tokens",
        min_value=200,
        max_value=1500,
        value=st.session_state.weather_max_tokens,
        step=100
    )
    st.session_state.weather_max_tokens = max_tokens

    st.write("")
    st.markdown("---")

    if st.button("🔄 Reset session", use_container_width=True):
        st.session_state.weather_result = None
        st.session_state.weather_ai_summary = ""
        st.rerun()
