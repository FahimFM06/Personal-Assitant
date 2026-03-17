import os
import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="Research Paper Summarizer", page_icon="📄", layout="wide")

# =========================================================
# THEMES
# - Cloud (Light): light widgets + BLACK text everywhere
# - Midnight (Dark)
# - Night Mode
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

    /* Inputs */
    .stTextArea textarea,
    .stTextInput input {{
        background: var(--input-bg) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
    }}

    .stFileUploader {{
        background: transparent !important;
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

    .stDownloadButton > button {{
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

    .small-muted {{
        color: var(--muted) !important;
        font-size: 0.92rem;
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
    """
    Read text from an uploaded PDF.
    """
    reader = PdfReader(uploaded_file)
    all_text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            all_text.append(page_text)

    return "\n".join(all_text).strip()


def build_summary_prompt(paper_text: str, summary_style: str) -> str:
    """
    Create the prompt based on the selected summary style.
    """
    if summary_style == "Short Summary":
        instruction = """
Summarize this research paper in a short and clear way.
Keep it easy to read.
Include:
1. main topic
2. objective
3. method
4. result
5. why it matters
"""
    elif summary_style == "Detailed Summary":
        instruction = """
Summarize this research paper in a detailed but clear way.
Include:
1. research problem
2. objective
3. methodology
4. data or dataset if available
5. key findings
6. limitations
7. conclusion
"""
    elif summary_style == "Bullet Points":
        instruction = """
Summarize this research paper using bullet points.
Include:
- topic
- objective
- method
- dataset or source
- key findings
- conclusion
"""
    else:
        instruction = """
Explain this research paper like I am a student.
Use simple language.
Avoid difficult words where possible.
"""

    return f"""
You are a helpful academic research assistant.

{instruction}

Research paper text:
{paper_text}
"""


def groq_summary(prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
    """
    Generate summary using Groq.
    """
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
                {"role": "system", "content": "You are a helpful research paper summarizer."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling Groq: {e}"


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
            '<div class="page-sub">Upload a PDF or paste text and generate a clean summary.</div>',
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
    input_tab, output_tab = st.tabs(["Input", "Summary Output"])

    with input_tab:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("**Choose input type**")

        input_type = st.radio(
            "Choose input type",
            ["Paste paper text / abstract", "Upload PDF"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if input_type == "Paste paper text / abstract":
            new_text = st.text_area(
                "Paper text",
                value=st.session_state.paper_text,
                height=320,
                placeholder="Paste your research paper abstract or full text here..."
            )
            st.session_state.paper_text = new_text
        else:
            uploaded_pdf = st.file_uploader("Upload research paper PDF", type=["pdf"])
            if uploaded_pdf is not None:
                try:
                    extracted = extract_text_from_pdf(uploaded_pdf)
                    if extracted:
                        st.session_state.paper_text = extracted
                        st.success("PDF text extracted successfully.")
                    else:
                        st.warning("Could not extract text from this PDF.")
                except Exception as e:
                    st.error(f"PDF reading failed: {e}")

            if st.session_state.paper_text:
                with st.expander("Preview extracted text"):
                    preview_text = st.session_state.paper_text[:4000]
                    if len(st.session_state.paper_text) > 4000:
                        preview_text += "\n\n..."
                    st.write(preview_text)

        btn1, btn2 = st.columns(2)

        with btn1:
            if st.button("📄 Generate Summary", use_container_width=True):
                if not st.session_state.paper_text.strip():
                    st.error("Please paste some paper text or upload a PDF first.")
                else:
                    model_id = MODEL_MAP.get(st.session_state.summ_model_name, "llama-3.3-70b-versatile")
                    prompt = build_summary_prompt(
                        st.session_state.paper_text,
                        st.session_state.summary_style
                    )

                    with st.spinner("Generating summary..."):
                        result = groq_summary(
                            prompt=prompt,
                            model_id=model_id,
                            temperature=st.session_state.summary_temperature,
                            max_tokens=st.session_state.summary_max_tokens
                        )
                    st.session_state.summary_output = result
                    st.rerun()

        with btn2:
            if st.button("🧹 Clear Text", use_container_width=True):
                st.session_state.paper_text = ""
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with output_tab:
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
            file_name="research_paper_summary.txt",
            mime="text/plain",
            use_container_width=False
        )

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
        if st.button("🆕 New summary", use_container_width=True):
            st.session_state.paper_text = ""
            st.session_state.summary_output = ""
            st.rerun()

    with b:
        if st.button("🗑️ Clear output", use_container_width=True):
            st.session_state.summary_output = ""
            st.rerun()

    if st.button("🔁 Reset session", use_container_width=True):
        keys_to_keep = []
        st.session_state.clear()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
