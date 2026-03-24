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

# ============================
# YOUTUBE PART (UPDATED ONLY)
# ============================
def get_youtube_video_id(url: str) -> str:
    """
    More robust video ID extraction:
    - supports watch?v=
    - youtu.be/
    - /embed/
    - /shorts/
    - also handles extra query params
    """
    url = (url or "").strip()

    patterns = [
        r"(?:v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""

def extract_text_from_youtube(url: str) -> str:
    """
    Fixes:
    - works across youtube-transcript-api versions
    - tries get_transcript first, then list_transcripts().fetch()
    - gives clear errors if transcript is disabled/not available
    """
    video_id = get_youtube_video_id(url)
    if not video_id:
        raise ValueError("Could not detect a valid YouTube video ID from the link.")

    languages = ["en", "en-US", "en-GB"]

    # 1) Newer versions
    if hasattr(YouTubeTranscriptApi, "get_transcript"):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            full_text = " ".join(item.get("text", "") for item in transcript)
            full_text = clean_text(full_text)
            if full_text:
                return full_text
        except Exception:
            pass

    # 2) Fallback
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        try:
            t = transcript_list.find_transcript(languages)
        except Exception:
            # if no English, try any available transcript
            # (helps if video only has another language)
            t = transcript_list.find_transcript([tr.language_code for tr in transcript_list])

        transcript = t.fetch()
        full_text = " ".join(item.get("text", "") for item in transcript)
        full_text = clean_text(full_text)

        if not full_text:
            raise ValueError("Transcript was found but returned empty text.")
        return full_text

    except Exception as e:
        # common causes: transcripts disabled, none available, region restrictions
        raise ValueError(
            "Could not load transcript for this video. "
            "The video may have transcripts disabled or unavailable."
        ) from e
# ============================
# END YOUTUBE PART
# ============================

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
            raise ValueError("Please
