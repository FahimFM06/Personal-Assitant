import streamlit as st
from groq import Groq

# -----------------------------------
# Page config
# -----------------------------------
st.set_page_config(
    page_title="AI Research Study QA",
    page_icon="💬",
    layout="wide"
)

# -----------------------------------
# Read Groq key automatically
# -----------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# -----------------------------------
# Same 3 themes (match your dashboard)
# -----------------------------------
THEMES = {
    "Cloud (Light)": {
        "app_bg": "#f6f7fb",
        "title": "#0f172a",
        "sub": "#64748b",
        "panel_bg": "#ffffff",
        "panel_border": "#e5e7eb",
        "panel_text": "#111827",
        "chip_bg": "#ffffff",
        "chip_border": "#e5e7eb",
        "info_bg": "#dbeafe",
        "info_border": "#bfdbfe",
        "info_text": "#1d4ed8",
        "btn_bg": "#ffffff",
        "btn_border": "#e5e7eb",
        "btn_text": "#111827",
    },
    "Midnight (Dark)": {
        "app_bg": "#0b1220",
        "title": "#e5e7eb",
        "sub": "#94a3b8",
        "panel_bg": "#0f172a",
        "panel_border": "#1f2a44",
        "panel_text": "#e5e7eb",
        "chip_bg": "#0f172a",
        "chip_border": "#1f2a44",
        "info_bg": "rgba(56, 189, 248, 0.10)",
        "info_border": "rgba(56, 189, 248, 0.25)",
        "info_text": "#e5e7eb",
        "btn_bg": "#0f172a",
        "btn_border": "#1f2a44",
        "btn_text": "#e5e7eb",
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
        "panel_bg": "rgba(20, 20, 22, 0.72)",
        "panel_border": "rgba(255,255,255,0.10)",
        "panel_text": "#f3f4f6",
        "chip_bg": "rgba(20, 20, 22, 0.72)",
        "chip_border": "rgba(255,255,255,0.10)",
        "info_bg": "rgba(255,255,255,0.06)",
        "info_border": "rgba(255,255,255,0.12)",
        "info_text": "#e5e7eb",
        "btn_bg": "rgba(20, 20, 22, 0.72)",
        "btn_border": "rgba(255,255,255,0.10)",
        "btn_text": "#f3f4f6",
    },
}

# -----------------------------------
# Session state (theme + chat + model)
# -----------------------------------
if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Cloud (Light)"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, how can I help you today?"}
    ]

# Groq models only
GROQ_MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "GPT-OSS 120B": "openai/gpt-oss-120b",
    "GPT-OSS 20B": "openai/gpt-oss-20b",
}

if "selected_model" not in st.session_state:
    st.session_state.selected_model = GROQ_MODELS["Llama 3.3 70B"]

T = THEMES[st.session_state.theme_name]

# -----------------------------------
# Apply theme CSS + top-right Theme button look
# -----------------------------------
st.markdown(
    f"""
    <style>
    :root {{
        --app-bg: {T["app_bg"]};
        --title: {T["title"]};
        --sub: {T["sub"]};
        --panel-bg: {T["panel_bg"]};
        --panel-border: {T["panel_border"]};
        --panel-text: {T["panel_text"]};
        --chip-bg: {T["chip_bg"]};
        --chip-border: {T["chip_border"]};
        --info-bg: {T["info_bg"]};
        --info-border: {T["info_border"]};
        --info-text: {T["info_text"]};
        --btn-bg: {T["btn_bg"]};
        --btn-border: {T["btn_border"]};
        --btn-text: {T["btn_text"]};
    }}

    .stApp {{
        background: var(--app-bg) !important;
    }}

    .block-container {{
        max-width: 1400px;
        padding-top: 1.2rem;
        padding-bottom: 1.5rem;
    }}

    .page-title {{
        font-size: 42px;
        font-weight: 800;
        color: var(--title);
        margin-bottom: 4px;
    }}

    .page-sub {{
        color: var(--sub);
        font-size: 16px;
        margin-bottom: 18px;
    }}

    .right-panel {{
        background: var(--panel-bg);
        border: 1px solid var(--panel-border);
        border-radius: 18px;
        padding: 18px;
        color: var(--panel-text);
    }}

    .right-title {{
        font-size: 22px;
        font-weight: 700;
        color: var(--title);
        margin-bottom: 12px;
    }}

    /* Buttons (New chat / Delete last / Export / Reset etc.) */
    div.stButton > button, div.stDownloadButton > button {{
        width: 100%;
        border-radius: 12px !important;
        height: 42px !important;
        font-weight: 600 !important;
        background: var(--btn-bg) !important;
        border: 1px solid var(--btn-border) !important;
        color: var(--btn-text) !important;
    }}

    /* Selectbox rounded */
    div[data-baseweb="select"] > div {{
        border-radius: 12px !important;
        background: var(--chip-bg) !important;
        border: 1px solid var(--chip-border) !important;
        color: var(--panel-text) !important;
    }}

    hr {{
        border-color: var(--panel-border);
    }}

    /* Alert info styling (if you use st.info somewhere) */
    div[data-testid="stAlert"] {{
        background: var(--info-bg) !important;
        border: 1px solid var(--info-border) !important;
    }}
    div[data-testid="stAlert"] * {{
        color: var(--info-text) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# Helper functions
# -----------------------------------
def ask_groq(messages, model_name):
    client = Groq(api_key=GROQ_API_KEY)

    api_messages = [
        {
            "role": "system",
            "content": (
                "You are an AI Research and Study Assistant. "
                "Answer clearly, accurately, and in a student-friendly way. "
                "If needed, explain step by step."
            ),
        }
    ] + messages

    response = client.chat.completions.create(
        model=model_name,
        messages=api_messages,
        temperature=0.3,
        max_tokens=700,
    )

    return response.choices[0].message.content.strip()


def reset_chat():
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, how can I help you today?"}
    ]


def delete_last_turn():
    msgs = st.session_state.messages
    if len(msgs) <= 1:
        return
    msgs.pop()
    if len(msgs) > 1 and msgs[-1]["role"] == "user":
        msgs.pop()


def export_chat():
    lines = []
    for msg in st.session_state.messages:
        speaker = "You" if msg["role"] == "user" else "Assistant"
        lines.append(f"{speaker}: {msg['content']}")
    return "\n\n".join(lines)

# -----------------------------------
# Layout
# -----------------------------------
left_col, right_col = st.columns([4.6, 1.4])

# -----------------------------------
# Left side: chat
# -----------------------------------
with left_col:
    # Header row with Theme button on the right (same idea as dashboard)
    h_left, h_right = st.columns([0.78, 0.22], vertical_alignment="center")

    with h_left:
        st.markdown('<div class="page-title">Chat</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-sub">Ask anything. Your chat stays in this session.</div>',
            unsafe_allow_html=True,
        )

    with h_right:
        with st.popover("🎨 Theme", use_container_width=True):
            st.session_state.theme_name = st.selectbox(
                "Theme",
                list(THEMES.keys()),
                index=list(THEMES.keys()).index(st.session_state.theme_name),
            )
            # No extra text output

    c1, c2, c3 = st.columns([1, 1, 1.1])

    with c1:
        if st.button("🆕 New chat"):
            reset_chat()
            st.rerun()

    with c2:
        if st.button("🗑 Delete last"):
            delete_last_turn()
            st.rerun()

    with c3:
        st.download_button(
            "⬇ Export chat",
            data=export_chat(),
            file_name="chat_history.txt",
            mime="text/plain",
        )

    st.markdown("")

    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

    user_prompt = st.chat_input("Type your question...")

    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        try:
            with st.spinner("Thinking..."):
                selected_model = st.session_state.selected_model
                if not GROQ_API_KEY:
                    reply = "GROQ_API_KEY is missing in Streamlit secrets."
                else:
                    reply = ask_groq(st.session_state.messages, selected_model)

        except Exception as e:
            reply = f"Something went wrong:\n\n{str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# -----------------------------------
# Right side: model panel
# -----------------------------------
with right_col:
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)
    st.markdown('<div class="right-title">Select Model</div>', unsafe_allow_html=True)

    selected_label = st.selectbox(
        "Groq model",
        list(GROQ_MODELS.keys()),
        label_visibility="collapsed",
    )
    st.session_state.selected_model = GROQ_MODELS[selected_label]

    st.caption("Groq models only")

    st.markdown("---")

    if st.button("♻ Reset session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
