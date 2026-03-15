import pandas as pd
import requests
import streamlit as st
from groq import Groq
from huggingface_hub import InferenceClient

# ---------------------------------------------------
# Page config
# ---------------------------------------------------
st.set_page_config(
    page_title="Smart Location Finder",
    page_icon="📍",
    layout="wide"
)

# ---------------------------------------------------
# API keys from Streamlit secrets
# ---------------------------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

# ---------------------------------------------------
# Models
# ---------------------------------------------------
GROQ_MODELS = {
    "Llama 3.3 70B (Best quality)": "llama-3.3-70b-versatile",
    "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant"
}


HF_MODELS = {
    "Qwen 2.5 7B Instruct": "Qwen/Qwen2.5-7B-Instruct"
}

# ---------------------------------------------------
# Session state
# ---------------------------------------------------
if "location_result" not in st.session_state:
    st.session_state.location_result = None

if "location_ai_summary" not in st.session_state:
    st.session_state.location_ai_summary = ""

if "location_provider" not in st.session_state:
    st.session_state.location_provider = "Groq"

if "location_temperature" not in st.session_state:
    st.session_state.location_temperature = 0.3

if "location_max_tokens" not in st.session_state:
    st.session_state.location_max_tokens = 500

if "location_model_id" not in st.session_state:
    st.session_state.location_model_id = GROQ_MODELS["Llama 3.3 70B (Best quality)"]

# ---------------------------------------------------
# Helper: geocode location with Nominatim
# ---------------------------------------------------
def search_location(query: str):
    """
    Search a place using OpenStreetMap Nominatim.
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

    response = requests.get(url, params=params, headers=headers, timeout=20)
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

# ---------------------------------------------------
# Helper: build prompt for LLM
# ---------------------------------------------------
def build_location_prompt(location_data: dict):
    """
    Build a friendly summary prompt for the selected place.
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

    prompt = f"""
You are a helpful location assistant.

Write a short, human-friendly summary of this place.
Keep it practical and easy to understand.

Please include:
1. What this place is
2. Where it is
3. Why someone may search for it
4. A short practical note for a visitor or user

Location details:
- Full name: {location_data.get("display_name", "Unknown")}
- Type: {location_data.get("type", "Unknown")}
- Category: {location_data.get("class", "Unknown")}
- City/Area: {city}
- Country: {country}
- Latitude: {location_data.get("lat")}
- Longitude: {location_data.get("lon")}
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
            {"role": "system", "content": "You are a helpful location explanation assistant."},
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
            {"role": "system", "content": "You are a helpful location explanation assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content

# ---------------------------------------------------
# CSS
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
        st.markdown('<div class="page-title">Smart Location Finder</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-subtitle">Search any place and get map coordinates plus an AI summary.</div>',
            unsafe_allow_html=True
        )

    location_query = st.text_input(
        "Search location",
        placeholder="Example: Darmstadt, Germany"
    )

    if st.button("📍 Find Location", use_container_width=True):
        if not location_query.strip():
            st.error("Please enter a place name.")
        else:
            try:
                with st.spinner("Searching location..."):
                    result = search_location(location_query.strip())

                    if not result:
                        st.error("Location not found. Please try another search.")
                    else:
                        st.session_state.location_result = result

                        prompt = build_location_prompt(result)

                        provider = st.session_state.location_provider
                        model_id = st.session_state.location_model_id
                        temperature = st.session_state.location_temperature
                        max_tokens = st.session_state.location_max_tokens

                        if provider == "Groq":
                            if not GROQ_API_KEY:
                                st.error("Groq API key not found in Streamlit secrets.")
                            else:
                                st.session_state.location_ai_summary = ask_groq(
                                    prompt=prompt,
                                    model_id=model_id,
                                    temperature=temperature,
                                    max_tokens=max_tokens
                                )
                        else:
                            if not HF_TOKEN:
                                st.error("HF token not found in Streamlit secrets.")
                            else:
                                st.session_state.location_ai_summary = ask_huggingface(
                                    prompt=prompt,
                                    model_id=model_id,
                                    temperature=temperature,
                                    max_tokens=max_tokens
                                )
            except Exception as e:
                st.error(f"Something went wrong: {e}")

    st.write("")

    if st.session_state.location_result:
        result = st.session_state.location_result
        address = result.get("address", {})

        st.markdown("### Location Details")
        st.markdown(
            f"""
            <div class="info-card">
                <b>Name:</b> {result.get("display_name", "Unknown")}<br>
                <b>Latitude:</b> {result.get("lat")}<br>
                <b>Longitude:</b> {result.get("lon")}<br>
                <b>Type:</b> {result.get("type", "Unknown")}<br>
                <b>Category:</b> {result.get("class", "Unknown")}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### Map View")
        map_df = pd.DataFrame(
            {
                "lat": [result["lat"]],
                "lon": [result["lon"]]
            }
        )
        st.map(map_df, zoom=11)

        st.markdown("### Address Information")
        st.markdown(
            f"""
            <div class="info-card">
                <b>Road:</b> {address.get("road", "N/A")}<br>
                <b>City/Town:</b> {address.get("city", address.get("town", address.get("village", "N/A")))}<br>
                <b>State:</b> {address.get("state", "N/A")}<br>
                <b>Postcode:</b> {address.get("postcode", "N/A")}<br>
                <b>Country:</b> {address.get("country", "N/A")}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### AI Location Summary")
        if st.session_state.location_ai_summary:
            st.markdown(
                f'<div class="summary-box">{st.session_state.location_ai_summary}</div>',
                unsafe_allow_html=True
            )
        else:
            st.info("The AI summary will appear here after a successful search.")

with right_col:
    st.markdown("## Provider")
    provider = st.selectbox(
        "Choose provider",
        ["Groq", "Hugging Face"],
        index=0,
        label_visibility="collapsed"
    )
    st.session_state.location_provider = provider

    st.write("")

    if provider == "Groq":
        st.markdown("## Select Model")
        model_name = st.selectbox(
            "Groq model",
            list(GROQ_MODELS.keys()),
            label_visibility="collapsed"
        )
        st.session_state.location_model_id = GROQ_MODELS[model_name]
        st.markdown('<div class="sidebar-note">Groq models only</div>', unsafe_allow_html=True)
    else:
        st.markdown("## Select Model")
        model_name = st.selectbox(
            "HF model",
            list(HF_MODELS.keys()),
            label_visibility="collapsed"
        )
        st.session_state.location_model_id = HF_MODELS[model_name]
        st.markdown('<div class="sidebar-note">Free/open Hugging Face models</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("---")

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.location_temperature,
        step=0.1
    )
    st.session_state.location_temperature = temperature

    max_tokens = st.slider(
        "Max tokens",
        min_value=200,
        max_value=1500,
        value=st.session_state.location_max_tokens,
        step=100
    )
    st.session_state.location_max_tokens = max_tokens

    st.write("")
    st.markdown("---")

    if st.button("🔄 Reset session", use_container_width=True):
        st.session_state.location_result = None
        st.session_state.location_ai_summary = ""
        st.rerun()
