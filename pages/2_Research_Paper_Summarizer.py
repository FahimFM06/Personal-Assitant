import os
import re
import requests
import streamlit as st
from bs4 import BeautifulSoup
from pypdf import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi

st.set_page_config(page_title="Research Paper Summarizer", page_icon="📄", layout="wide")

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

MODELS_UI = ["Llama 3.3 70B", "Llama 3.1 8B", "Gemma 2 9B"]
MODEL_MAP = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "Gemma 2 9B": "gemma2-9b-it",
}

SUMMARY_STYLES = [
    "Short Summary",
    "Detailed Summary",
    "Bullet Points",
    "Explain Like a Student",
]

INPUT_TYPES = [
    "Paste text",
    "Upload PDF",
    "Website URL",
    "YouTube URL",
]

# -----------------------------
# Session state
# -----------------------------
if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Midnight (Dark)"

if "summ_model_name" not in st.session_state:
    st.session_state.summ_model_name = MODELS_UI[0]

if "summary_style" not in st.session_state:
    st.session_state.summary_style = SUMMARY_STYLES[0]

if "paper_text" not in st.session_state:
    st.session_state.paper_text = ""

if "summary_output" not in st.session_state:
    st.session_state.summary_output = ""

if "summary_temperature" not in st.session_state:
    st.session_state.summary_temperature = 0.3

if "summary_max_tokens" not in st.session_state:
    st.session_state.summary_max_tokens = 900

if "source_type" not in st.session_state:
    st.session_state.source_type = INPUT_TYPES[0]

if "source_url" not in st.session_state:
    st.session_state.source_url = ""

if "qa_messages_doc" not in st.session_state:
    st.session_state.qa_messages_doc = [
        {"role": "assistant", "content": "Hello, upload a PDF or provide text/link, and then ask questions about it."}
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

    .stDownloadButton > button {{
        background: var(--btn-bg) !important;
        color: var(--btn-text) !important;
        border: 1px solid var(--btn-border) !important;
        border-radius: 12px !important;
    }}

    .stSlider * {{
        color: var(--text) !important;
    }}

    div[data-testid="stChatMessage"] * {{
        color: var(--text) !important;
    }}

    div[data-testid="stChatInput"] > div {{
        border-radius: 14px !important;
        border: 1px solid var(--border) !important;
        background: var(--input-bg) !important;
    }}

    div[data-testid="stChatInput"] textarea {{
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


def extract_text_from_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text)
    return "\n".join(texts).strip()


def clean_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def extract_text_from_website(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=25)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "header", "footer", "svg"]):
        tag.decompose()

    texts = soup.stripped_strings
    joined = "\n".join(texts)
    return clean_text(joined)


def get_youtube_video_id(url: str) -> str:
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""


def extract_text_from_youtube(url: str) -> str:
    """
    Free method using youtube-transcript-api.
    Works only when the video has captions/transcript available.
    """
    video_id = get_youtube_video_id(url)
    if not video_id:
        raise ValueError("Could not detect a valid YouTube video ID from the link.")

    try:
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id)
        full_text = " ".join(snippet.text for snippet in fetched_transcript)
    except Exception as e:
        raise ValueError(
            f"Could not fetch YouTube transcript. This video may not have captions enabled, "
            f"or YouTube may be blocking transcript access temporarily. Details: {e}"
        )

    full_text = clean_text(full_text)
    if not full_text:
        raise ValueError("Transcript was fetched but no usable text was found.")

    return full_text


def build_summary_prompt(source_text: str, summary_style: str) -> str:
    if summary_style == "Short Summary":
        instruction = """
Summarize this content in a short and clear way.
Include:
1. main topic
2. objective or purpose
3. key ideas
4. result or main takeaway
5. why it matters
"""
    elif summary_style == "Detailed Summary":
        instruction = """
Summarize this content in a detailed but clear way.
Include:
1. main topic
2. important sections
3. key arguments or methods
4. major results or findings
5. conclusion
"""
    elif summary_style == "Bullet Points":
        instruction = """
Summarize this content using bullet points.
Include:
- topic
- purpose
- important ideas
- main findings
- conclusion
"""
    else:
        instruction = """
Explain this content like I am a student.
Use simple language.
Avoid difficult words where possible.
"""

    return f"""
You are a helpful summarization assistant.

{instruction}

Content:
{source_text}
"""


def build_qa_messages(source_text: str, chat_history: list) -> list:
    system_prompt = f"""
You are a document and link assistant.

Answer only from the provided content below.
If the answer is not clearly available in the content, say:
"I could not find that clearly in the provided content."

Provided content:
{source_text}
"""
    return [{"role": "system", "content": system_prompt}] + chat_history


def call_groq(messages: list, model_id: str, temperature: float, max_tokens: int) -> str:
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
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling Groq: {e}"


def load_source_text(input_type: str, pasted_text: str, url_value: str, pdf_file) -> str:
    if input_type == "Paste text":
        return clean_text(pasted_text)

    if input_type == "Upload PDF":
        if pdf_file is None:
            raise ValueError("Please upload a PDF file first.")
        return extract_text_from_pdf(pdf_file)

    if input_type == "Website URL":
        if not url_value.strip():
            raise ValueError("Please enter a website URL first.")
        return extract_text_from_website(url_value.strip())

    if input_type == "YouTube URL":
        if not url_value.strip():
            raise ValueError("Please enter a YouTube URL first.")
        return extract_text_from_youtube(url_value.strip())

    return ""


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
        st.markdown('<div class="page-title">Research Paper Summarizer</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-sub">Summarize and ask questions from PDF, website, YouTube link, or pasted text.</div>',
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
    tab1, tab2, tab3 = st.tabs(["Input", "Summary Output", "Chat with Content"])

    with tab1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)

        st.markdown("**Choose input type**")
        input_type = st.radio(
            "Choose input type",
            INPUT_TYPES,
            index=INPUT_TYPES.index(st.session_state.source_type),
            horizontal=True,
            label_visibility="collapsed"
        )
        st.session_state.source_type = input_type

        uploaded_pdf = None

        if input_type == "Paste text":
            pasted = st.text_area(
                "Paste text",
                value=st.session_state.paper_text,
                height=320,
                placeholder="Paste paper text, notes, article text, or any content here..."
            )
            st.session_state.paper_text = pasted

        elif input_type == "Upload PDF":
            uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
            if st.session_state.paper_text:
                with st.expander("Preview current loaded text"):
                    preview_text = st.session_state.paper_text[:4000]
                    if len(st.session_state.paper_text) > 4000:
                        preview_text += "\n\n..."
                    st.write(preview_text)

        elif input_type == "Website URL":
            url_value = st.text_input(
                "Website URL",
                value=st.session_state.source_url,
                placeholder="https://example.com/article"
            )
            st.session_state.source_url = url_value

        elif input_type == "YouTube URL":
            url_value = st.text_input(
                "YouTube URL",
                value=st.session_state.source_url,
                placeholder="https://www.youtube.com/watch?v=..."
            )
            st.session_state.source_url = url_value

        btn1, btn2, btn3 = st.columns(3)

        with btn1:
            if st.button("📥 Load Content", use_container_width=True):
                try:
                    if input_type == "Paste text":
                        source_text = load_source_text(
                            input_type=input_type,
                            pasted_text=st.session_state.paper_text,
                            url_value="",
                            pdf_file=None
                        )
                    elif input_type == "Upload PDF":
                        source_text = load_source_text(
                            input_type=input_type,
                            pasted_text="",
                            url_value="",
                            pdf_file=uploaded_pdf
                        )
                    else:
                        source_text = load_source_text(
                            input_type=input_type,
                            pasted_text="",
                            url_value=st.session_state.source_url,
                            pdf_file=None
                        )

                    if not source_text:
                        st.error("No content was found.")
                    else:
                        st.session_state.paper_text = source_text
                        st.success("Content loaded successfully.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Could not load content: {e}")

        with btn2:
            if st.button("📄 Generate Summary", use_container_width=True):
                try:
                    source_text = st.session_state.paper_text.strip()
                    if not source_text:
                        st.error("Please load content first.")
                    else:
                        model_id = MODEL_MAP.get(st.session_state.summ_model_name, "llama-3.3-70b-versatile")
                        prompt = build_summary_prompt(source_text, st.session_state.summary_style)

                        with st.spinner("Generating summary..."):
                            result = call_groq(
                                messages=[
                                    {"role": "system", "content": "You are a helpful summarization assistant."},
                                    {"role": "user", "content": prompt}
                                ],
                                model_id=model_id,
                                temperature=st.session_state.summary_temperature,
                                max_tokens=st.session_state.summary_max_tokens
                            )
                        st.session_state.summary_output = result
                        st.rerun()
                except Exception as e:
                    st.error(f"Summary generation failed: {e}")

        with btn3:
            if st.button("🧹 Clear Content", use_container_width=True):
                st.session_state.paper_text = ""
                st.session_state.source_url = ""
                st.session_state.summary_output = ""
                st.session_state.qa_messages_doc = [
                    {"role": "assistant", "content": "Hello, upload a PDF or provide text/link, and then ask questions about it."}
                ]
                st.rerun()

        if st.session_state.paper_text:
            st.markdown("**Loaded Content Preview**")
            preview = st.session_state.paper_text[:5000]
            if len(st.session_state.paper_text) > 5000:
                preview += "\n\n..."
            st.text_area("Preview", value=preview, height=240, disabled=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        if st.session_state.summary_output:
            st.markdown(st.session_state.summary_output)
        else:
            st.info("Your summary will appear here.")
        st.markdown("</div>", unsafe_allow_html=True)

        download_text = st.session_state.summary_output if st.session_state.summary_output else "No summary generated yet."
        st.download_button(
            "⬇ Download Summary",
            data=download_text,
            file_name="content_summary.txt",
            mime="text/plain",
            use_container_width=False
        )

    with tab3:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)

        if not st.session_state.paper_text.strip():
            st.info("Load a PDF, website, YouTube link, or pasted text first. Then you can ask questions here.")
        else:
            for msg in st.session_state.qa_messages_doc:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            user_q = st.chat_input("Ask a question based on the loaded content...")

            if user_q:
                st.session_state.qa_messages_doc.append({"role": "user", "content": user_q})

                model_id = MODEL_MAP.get(st.session_state.summ_model_name, "llama-3.3-70b-versatile")
                api_messages = build_qa_messages(
                    source_text=st.session_state.paper_text,
                    chat_history=st.session_state.qa_messages_doc
                )

                with st.spinner("Thinking..."):
                    answer = call_groq(
                        messages=api_messages,
                        model_id=model_id,
                        temperature=st.session_state.summary_temperature,
                        max_tokens=st.session_state.summary_max_tokens
                    )

                st.session_state.qa_messages_doc.append({"role": "assistant", "content": answer})
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="right-middle">', unsafe_allow_html=True)
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)

    st.markdown("**Select Model**")
    st.session_state.summ_model_name = st.selectbox(
        "Select Model",
        MODELS_UI,
        index=MODELS_UI.index(st.session_state.summ_model_name),
        label_visibility="collapsed",
    )
    st.caption("Groq models only")

    st.divider()

    st.markdown("**Summary Style**")
    st.session_state.summary_style = st.selectbox(
        "Summary Style",
        SUMMARY_STYLES,
        index=SUMMARY_STYLES.index(st.session_state.summary_style),
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("**Temperature**")
    st.session_state.summary_temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.summary_temperature,
        step=0.1,
        label_visibility="collapsed",
    )
    st.caption(f"{st.session_state.summary_temperature:.2f}")

    st.markdown("**Max tokens**")
    st.session_state.summary_max_tokens = st.slider(
        "Max tokens",
        min_value=200,
        max_value=3000,
        value=st.session_state.summary_max_tokens,
        step=100,
        label_visibility="collapsed",
    )
    st.caption(str(st.session_state.summary_max_tokens))

    st.divider()

    a, b = st.columns(2)

    with a:
        if st.button("🆕 New session", use_container_width=True):
            st.session_state.paper_text = ""
            st.session_state.source_url = ""
            st.session_state.summary_output = ""
            st.session_state.qa_messages_doc = [
                {"role": "assistant", "content": "Hello, upload a PDF or provide text/link, and then ask questions about it."}
            ]
            st.rerun()

    with b:
        if st.button("🗑️ Clear output", use_container_width=True):
            st.session_state.summary_output = ""
            st.rerun()

    if st.button("🔁 Reset session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
