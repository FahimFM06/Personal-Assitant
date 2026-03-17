import streamlit as st
from datetime import datetime

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
        "muted": "#6b7280",
        "shadow": "0 10px 30px rgba(15, 23, 42, 0.08)",
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
    },
}

# -----------------------------
# Session state
# -----------------------------
if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Midnight (Dark)"

if "model_name" not in st.session_state:
    st.session_state.model_name = "Llama 3.3 70B"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, how can I help you today?"}
    ]

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
        max-width: 1200px;
        padding-top: 1.0rem;
        padding-bottom: 1.0rem;
    }}

    /* Hide the default Streamlit header spacing a bit */
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* Page title */
    .page-title {{
        font-size: 2rem;
        font-weight: 800;
        color: {T["title"]};
        margin: 0 0 0.1rem 0;
    }}
    .page-sub {{
        color: {T["sub"]};
        margin: 0 0 0.8rem 0;
        font-size: 0.95rem;
    }}

    /* Right control panel look */
    .right-panel {{
        background: {T["panel_bg"]};
        border: 1px solid {T["border"]};
        border-radius: 16px;
        padding: 14px;
        box-shadow: {T["shadow"]};
    }}

    /* Chat area - remove the "extra empty middle" feeling */
    div[data-testid="stChatMessage"] {{
        border-radius: 14px;
    }}

    /* Make chat input look nicer */
    div[data-testid="stChatInput"] > div {{
        border-radius: 14px !important;
        border: 1px solid {T["border"]} !important;
        background: {T["panel_bg"]} !important;
    }}

    /* Slightly reduce top blank space above chat */
    .stChatFloatingInputContainer {{
        padding-bottom: 0.25rem;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# TOP BAR: left = title, right = theme button (popover)
# =========================================================
top_left, top_right = st.columns([0.72, 0.28], vertical_alignment="center")

with top_left:
    st.markdown('<div class="page-title">Chat</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Ask anything. Your chat stays in this session.</div>', unsafe_allow_html=True)

with top_right:
    # Theme button on the top bar (as you want)
    with st.popover("🎨 Theme ▾", use_container_width=True):
        st.session_state.theme_name = st.selectbox(
            "Theme",
            list(THEMES.keys()),
            index=list(THEMES.keys()).index(st.session_state.theme_name),
        )

# Update theme after selection (rerun also happens automatically)
T = THEMES[st.session_state.theme_name]

# =========================================================
# MAIN LAYOUT: left = chat messages, right = controls (moved DOWN)
# =========================================================
chat_col, right_col = st.columns([0.74, 0.26], gap="large")

with right_col:
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)

    st.markdown("**Select Model**")
    st.session_state.model_name = st.selectbox(
        "Select Model",
        ["Llama 3.3 70B", "Llama 3.1 8B", "Gemma 2 9B"],
        index=["Llama 3.3 70B", "Llama 3.1 8B", "Gemma 2 9B"].index(st.session_state.model_name),
        label_visibility="collapsed",
    )
    st.caption("Groq models only")

    st.divider()

    colA, colB = st.columns(2)
    with colA:
        if st.button("🆕 New chat", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": "Hello, how can I help you today?"}]
            st.rerun()

    with colB:
        if st.button("🗑️ Delete last", use_container_width=True):
            # remove last user/assistant if exists
            if len(st.session_state.messages) > 1:
                st.session_state.messages.pop()
            st.rerun()

    if st.button("🔁 Reset session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

with chat_col:
    # Show chat messages only (no empty middle box)
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# =========================================================
# CHAT INPUT (always bottom)
# =========================================================
user_text = st.chat_input("Type your message...")

if user_text:
    # add user message
    st.session_state.messages.append({"role": "user", "content": user_text})

    # demo assistant response (replace with your real LLM call)
    reply = f"Got it. (Model: {st.session_state.model_name})\n\nYou said: {user_text}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
