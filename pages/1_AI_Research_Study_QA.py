import os
import streamlit as st

# =========================================================
# 1) INSTALL + API KEY (do this outside Python)
# =========================================================
# pip install -U streamlit groq
#
# Set env var:
#   mac/linux:  export GROQ_API_KEY="YOUR_KEY"
#   windows PS: setx GROQ_API_KEY "YOUR_KEY"
# =========================================================

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Chat Assistant", page_icon="💬", layout="wide")

# -----------------------------
# Themes (3 only)
# -----------------------------
THEMES = {
    "Cloud (Light)": {
        "app_bg": "#f6f7fb",
        "panel_bg": "#ffffff",
        "title": "#0f172a",
        "sub": "#64748b",
        "border": "#e5e7eb",
        "text": "#111827",
        "shadow": "0 10px 30px rgba(15, 23, 42, 0.08)",
        "input_bg": "#ffffff",
    },
    "Midnight (Dark)": {
        "app_bg": "#0b1220",
        "panel_bg": "#0f172a",
        "title": "#e5e7eb",
        "sub": "#94a3b8",
        "border": "#1f2a44",
        "text": "#e5e7eb",
        "shadow": "0 10px 26px rgba(0,0,0,0.45)",
        "input_bg": "#0f172a",
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
        "shadow": "0 12px 30px rgba(0,0,0,0.55)",
        "input_bg": "rgba(20, 20, 22, 0.72)",
    },
}

MODELS_UI = ["Llama 3.3 70B", "Llama 3.1 8B", "Gemma 2 9B"]
MODEL_MAP = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "Gemma 2 9B": "gemma2-9b-it",
}

# -----------------------------
# Session state
# -----------------------------
if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Midnight (Dark)"

if "model_name" not in st.session_state:
    st.session_state.model_name = MODELS_UI[0]

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello, how can I help you today?"}]

T = THEMES[st.session_state.theme_name]

# -----------------------------
# CSS
# -----------------------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background: {T["app_bg"]} !important;
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
        color: {T["title"]};
        margin: 0 0 0.1rem 0;
    }}
    .page-sub {{
        color: {T["sub"]};
        margin: 0 0 0.8rem 0;
        font-size: 0.95rem;
    }}
    .right-panel {{
        background: {T["panel_bg"]};
        border: 1px solid {T["border"]};
        border-radius: 16px;
        padding: 14px;
        box-shadow: {T["shadow"]};
    }}
    /* Move right panel DOWN (middle) */
    .right-middle {{
        margin-top: 140px;
    }}
    /* Chat input styling */
    div[data-testid="stChatInput"] > div {{
        border-radius: 14px !important;
        border: 1px solid {T["border"]} !important;
        background: {T["input_bg"]} !important;
    }}
    .stButton > button {{
        border-radius: 12px !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# TOP BAR: Title + Theme button (right)
# =========================================================
top_left, top_right = st.columns([0.75, 0.25], vertical_alignment="center")

with top_left:
    st.markdown('<div class="page-title">Chat</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Ask anything. Your chat stays in this session.</div>', unsafe_allow_html=True)

with top_right:
    # If your Streamlit is old and popover doesn't exist, update Streamlit.
    with st.popover("🎨 Theme ▾", use_container_width=True):
        st.session_state.theme_name = st.selectbox(
            "Theme",
            list(THEMES.keys()),
            index=list(THEMES.keys()).index(st.session_state.theme_name),
        )

# =========================================================
# MAIN AREA: 3/4 chat + 1/4 right controls
# =========================================================
chat_col, right_col = st.columns([3, 1], gap="large")

with chat_col:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

with right_col:
    st.markdown('<div class="right-middle">', unsafe_allow_html=True)
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)

    st.markdown("**Select Model**")
    st.session_state.model_name = st.selectbox(
        "Select Model",
        MODELS_UI,
        index=MODELS_UI.index(st.session_state.model_name),
        label_visibility="collapsed",
    )
    st.caption("Groq models only")

    st.divider()

    a, b = st.columns(2)
    with a:
        if st.button("🆕 New chat", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": "Hello, how can I help you today?"}]
            st.rerun()

    with b:
        if st.button("🗑️ Delete last", use_container_width=True):
            if len(st.session_state.messages) > 1:
                st.session_state.messages.pop()
            st.rerun()

    if st.button("🔁 Reset session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)  # right-panel
    st.markdown("</div>", unsafe_allow_html=True)  # right-middle

# =========================================================
# CHAT INPUT (always bottom)
# =========================================================
user_text = st.chat_input("Type your message...")

# =========================================================
# REAL AI RESPONSE (Groq)
# =========================================================
def groq_reply(messages, model_id: str) -> str:
    """
    messages: list of dicts: [{"role":"user|assistant|system","content":"..."}]
    """
    try:
        from groq import Groq
    except Exception:
        return "Groq package not installed. Run: pip install groq"

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "GROQ_API_KEY is missing. Set it in your environment variables."

    try:
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=0.4,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Error calling Groq: {e}"

if user_text:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_text})

    # Prepare messages for API (optional system prompt)
    api_messages = [{"role": "system", "content": "You are a helpful assistant."}] + st.session_state.messages

    # Call Groq
    model_id = MODEL_MAP.get(st.session_state.model_name, "llama-3.3-70b-versatile")
    answer = groq_reply(api_messages, model_id)

    # Add assistant answer
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
