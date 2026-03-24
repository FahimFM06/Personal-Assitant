import os
import requests
import streamlit as st

st.set_page_config(page_title="Chat Assistant", page_icon="💬", layout="wide")

# ============================
# ============================
BACK_PAGE = "Home.py"  

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
if "web_search" not in st.session_state:
    st.session_state.web_search = False
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! This is a chatbot. Ask me any question."}
    ]

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
        margin-top: 120px;
    }}

    /* Chat input */
    div[data-testid="stChatInput"] > div {{
        border-radius: 14px !important;
        border: 1px solid var(--border) !important;
        background: var(--input-bg) !important;
    }}
    div[data-testid="stChatInput"] textarea {{
        color: var(--text) !important;
    }}

    /* Chat text */
    div[data-testid="stChatMessage"] * {{
        color: var(--text) !important;
    }}

    /* Selectbox */
    div[data-testid="stSelectbox"] > div {{
        background: var(--widget-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }}
    div[data-testid="stSelectbox"] * {{
        color: var(--widget-text) !important;
    }}

    /* Dropdown menu */
    div[role="listbox"] {{
        background: var(--menu-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }}
    div[role="listbox"] * {{
        color: var(--menu-text) !important;
    }}
    div[role="option"]:hover {{
        background: rgba(100, 116, 139, 0.12) !important;
    }}

    /* Popover button */
    button[data-testid="stPopoverButton"] {{
        background: var(--widget-bg) !important;
        color: var(--widget-text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }}

    /* Buttons */
    .stButton > button {{
        background: var(--btn-bg) !important;
        color: var(--btn-text) !important;
        border: 1px solid var(--btn-border) !important;
        border-radius: 12px !important;
    }}

    .stCaption {{
        color: var(--muted) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# Helpers
# =========================================================
def go_back():
    # No warning message (you asked to keep it simple)
    try:
        st.switch_page(BACK_PAGE)
    except Exception:
        # silently do nothing if path is wrong
        pass

def newsapi_search(query: str, max_items: int = 5) -> list[dict]:
    api_key = os.environ.get("NEWSAPI_KEY")
    if not api_key:
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_items,
        "apiKey": api_key,
    }

    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        articles = data.get("articles", [])[:max_items]
        out = []
        for a in articles:
            out.append({
                "title": a.get("title", ""),
                "source": (a.get("source") or {}).get("name", ""),
                "url": a.get("url", ""),
                "publishedAt": a.get("publishedAt", ""),
            })
        return out
    except Exception:
        return []

def groq_reply(messages, model_id: str) -> str:
    try:
        from groq import Groq
    except Exception:
        return "Install Groq: pip install groq"

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Set GROQ_API_KEY in environment variables."

    try:
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=0.35,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Groq error: {e}"

# =========================================================
# TOP BAR (Back left + Title + Theme right)
# =========================================================
top_back, top_title, top_theme = st.columns([0.12, 0.63, 0.25], vertical_alignment="center")

with top_back:
    if st.button("⬅ Back", use_container_width=True):
        go_back()

with top_title:
    st.markdown('<div class="page-title">Chat</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">This is a chatbot. Ask any question.</div>', unsafe_allow_html=True)

with top_theme:
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

    st.divider()

    st.session_state.web_search = st.toggle("🔎 Web search", value=st.session_state.web_search)

    st.divider()

    a, b = st.columns(2)
    with a:
        if st.button("🆕 New chat", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": "Hi! This is a chatbot. Ask me any question."}]
            st.rerun()
    with b:
        if st.button("🗑️ Delete last", use_container_width=True):
            if len(st.session_state.messages) > 1:
                st.session_state.messages.pop()
            st.rerun()

    if st.button("🔁 Reset session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# CHAT INPUT (always bottom)
# =========================================================
user_text = st.chat_input("Type your message...")

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})

    model_id = MODEL_MAP.get(st.session_state.model_name, "llama-3.3-70b-versatile")

    web_context = ""
    if st.session_state.web_search:
        articles = newsapi_search(user_text, max_items=5)
        if articles:
            lines = []
            for i, a in enumerate(articles, 1):
                if a.get("url"):
                    lines.append(f"{i}. {a['title']} — {a['source']}\n{a['url']}")
            if lines:
                web_context = "\n\nSOURCES:\n" + "\n\n".join(lines)

    system_prompt = (
        "You are a helpful assistant. "
        "If SOURCES are provided, use them and include the URLs you used."
    )

    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages += st.session_state.messages[:-1]
    api_messages.append({"role": "user", "content": user_text + web_context})

    answer = groq_reply(api_messages, model_id)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
