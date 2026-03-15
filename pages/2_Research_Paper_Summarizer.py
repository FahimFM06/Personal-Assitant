import streamlit as st
from groq import Groq
from pypdf import PdfReader

# ---------------------------------------------------
# Page config
# ---------------------------------------------------
st.set_page_config(
    page_title="Research Paper Summarizer",
    page_icon="📄",
    layout="wide"
)

# ---------------------------------------------------
# Read Groq API key automatically from secrets
# ---------------------------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# ---------------------------------------------------
# Available Groq models
# ---------------------------------------------------
GROQ_MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "GPT-OSS 120B": "openai/gpt-oss-120b",
    "GPT-OSS 20B": "openai/gpt-oss-20b",
}

# ---------------------------------------------------
# Session state
# ---------------------------------------------------
if "paper_summary_output" not in st.session_state:
    st.session_state.paper_summary_output = ""

if "paper_input_text" not in st.session_state:
    st.session_state.paper_input_text = ""

# ---------------------------------------------------
# Helper: extract text from PDF
# ---------------------------------------------------
def extract_text_from_pdf(uploaded_file):
    """
    Read text from uploaded PDF.
    Simple and beginner-friendly.
    """
    reader = PdfReader(uploaded_file)
    pages_text = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)

    return "\n".join(pages_text).strip()

# ---------------------------------------------------
# Helper: build summarization prompt
# ---------------------------------------------------
def build_summary_prompt(paper_text, summary_style):
    """
    Create a summary prompt based on the selected style.
    """
    if summary_style == "Short Summary":
        instruction = """
        Summarize the research paper in a concise and clear way.
        Keep it around 150 to 200 words.
        Mention:
        1. Main topic
        2. Goal
        3. Method
        4. Main result
        5. Why it matters
        """
    elif summary_style == "Detailed Summary":
        instruction = """
        Summarize the research paper in a detailed but clear way.
        Cover:
        1. Research problem
        2. Objective
        3. Methodology
        4. Dataset or source if available
        5. Key findings
        6. Limitations
        7. Conclusion
        """
    elif summary_style == "Bullet Points":
        instruction = """
        Summarize the research paper in bullet points.
        Include:
        - Topic
        - Problem
        - Objective
        - Method
        - Findings
        - Conclusion
        """
    else:
        instruction = """
        Explain this research paper in very simple student-friendly language.
        Avoid complex jargon where possible.
        """

    prompt = f"""
You are a helpful academic research assistant.

{instruction}

Research paper text:
{paper_text}
"""
    return prompt

# ---------------------------------------------------
# Helper: call Groq
# ---------------------------------------------------
def summarize_with_groq(api_key, model_id, prompt, temperature, max_tokens):
    """
    Send the prompt to Groq and get the summary.
    """
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful research paper summarizer."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content

# ---------------------------------------------------
# Custom CSS
# ---------------------------------------------------
st.markdown("""
<style>
/* Main app background */
.stApp {
    background: #f6f7fb;
}

/* Remove white block feeling by making main area clean */
.main .block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Title area */
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

/* Sidebar card feel */
.sidebar-note {
    font-size: 0.92rem;
    color: #6b7280;
    margin-top: 0.25rem;
}

/* Button style */
.stButton > button {
    border-radius: 14px;
    height: 44px;
    border: 1px solid #d1d5db;
    background: white;
}

/* Input boxes */
.stTextArea textarea,
.stTextInput input {
    border-radius: 16px !important;
}

/* Output area */
.summary-box {
    background: transparent;
    border: none;
    padding: 0.25rem 0 0 0;
    color: #111827;
    font-size: 1rem;
    line-height: 1.7;
}

/* Small message row */
.small-note {
    color: #64748b;
    font-size: 0.95rem;
    margin-top: 0.4rem;
    margin-bottom: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Layout
# ---------------------------------------------------
left_col, right_col = st.columns([4.8, 1.8], gap="large")

# ---------------------------------------------------
# LEFT SIDE
# ---------------------------------------------------
with left_col:
    top1, top2 = st.columns([1, 6])

    with top1:
        if st.button("⬅ Back", use_container_width=True):
            st.switch_page("Home.py")

    with top2:
        st.markdown('<div class="page-title">Research Paper Summarizer</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-subtitle">Upload a paper or paste text, then generate a clean summary.</div>',
            unsafe_allow_html=True
        )

    action1, action2 = st.columns([1, 1])

    with action1:
        if st.button("🆕 New summary", use_container_width=True):
            st.session_state.paper_summary_output = ""
            st.session_state.paper_input_text = ""
            st.rerun()

    with action2:
        if st.button("🗑 Delete output", use_container_width=True):
            st.session_state.paper_summary_output = ""
            st.rerun()

    st.write("")

    input_mode = st.radio(
        "Choose input type",
        ["Paste paper text / abstract", "Upload PDF"],
        horizontal=True
    )

    paper_text = ""

    if input_mode == "Paste paper text / abstract":
        paper_text = st.text_area(
            "Paper text",
            value=st.session_state.paper_input_text,
            height=220,
            placeholder="Paste the research paper abstract or full text here..."
        )
        st.session_state.paper_input_text = paper_text

    else:
        uploaded_pdf = st.file_uploader("Upload research paper PDF", type=["pdf"])

        if uploaded_pdf is not None:
            with st.spinner("Reading PDF..."):
                paper_text = extract_text_from_pdf(uploaded_pdf)
            st.session_state.paper_input_text = paper_text
            st.markdown('<div class="small-note">PDF text extracted successfully.</div>', unsafe_allow_html=True)

    if st.button("📄 Generate summary", use_container_width=True):
        if not GROQ_API_KEY:
            st.error("Groq API key not found in Streamlit secrets. Add GROQ_API_KEY first.")
        elif not st.session_state.paper_input_text.strip():
            st.error("Please paste paper text or upload a PDF first.")
        else:
            summary_prompt = build_summary_prompt(
                st.session_state.paper_input_text,
                st.session_state.summary_style
            )

            with st.spinner("Generating summary..."):
                try:
                    summary = summarize_with_groq(
                        api_key=GROQ_API_KEY,
                        model_id=st.session_state.selected_model_id,
                        prompt=summary_prompt,
                        temperature=st.session_state.temperature,
                        max_tokens=st.session_state.max_tokens
                    )
                    st.session_state.paper_summary_output = summary
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

    st.write("")
    st.markdown("### Summary Output")

    if st.session_state.paper_summary_output:
        st.markdown(
            f'<div class="summary-box">{st.session_state.paper_summary_output}</div>',
            unsafe_allow_html=True
        )
    else:
        st.info("Your summary will appear here.")

# ---------------------------------------------------
# RIGHT SIDE
# ---------------------------------------------------
with right_col:
    st.markdown("## Select Model")

    selected_model_name = st.selectbox(
        "Model",
        list(GROQ_MODELS.keys()),
        label_visibility="collapsed"
    )
    selected_model_id = GROQ_MODELS[selected_model_name]
    st.session_state.selected_model_id = selected_model_id

    st.markdown('<div class="sidebar-note">Groq models only</div>', unsafe_allow_html=True)

    st.write("")
    st.write("")

    summary_style = st.selectbox(
        "Summary Style",
        ["Short Summary", "Detailed Summary", "Bullet Points", "Explain Like a Student"]
    )
    st.session_state.summary_style = summary_style

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1
    )
    st.session_state.temperature = temperature

    max_tokens = st.slider(
        "Max tokens",
        min_value=200,
        max_value=3000,
        value=900,
        step=100
    )
    st.session_state.max_tokens = max_tokens

    st.write("")
    st.markdown("---")

    if st.button("🔄 Reset session", use_container_width=True):
        st.session_state.paper_summary_output = ""
        st.session_state.paper_input_text = ""
        st.rerun()
