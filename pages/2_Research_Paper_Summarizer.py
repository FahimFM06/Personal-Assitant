import streamlit as st
from groq import Groq
from pypdf import PdfReader

# ---------------------------------------------------
# Page setup
# ---------------------------------------------------
st.set_page_config(
    page_title="Research Paper Summarizer",
    page_icon="📄",
    layout="wide"
)

# ---------------------------------------------------
# Custom CSS
# ---------------------------------------------------
st.markdown("""
<style>
.block-container {
    max-width: 1200px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.main-title {
    font-size: 46px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 0.25rem;
}

.sub-title {
    font-size: 18px;
    color: #64748b;
    margin-bottom: 1.5rem;
}

.action-btn-row {
    margin-bottom: 1rem;
}

.summary-box {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 18px;
    min-height: 320px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
    overflow-y: auto;
}

.message-user {
    background: #f1f5f9;
    color: #111827;
    padding: 14px 16px;
    border-radius: 14px;
    margin-bottom: 12px;
    border: 1px solid #e5e7eb;
}

.message-bot {
    background: #fff7ed;
    color: #111827;
    padding: 14px 16px;
    border-radius: 14px;
    margin-bottom: 12px;
    border: 1px solid #fed7aa;
}

.small-label {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 4px;
    font-weight: 600;
}

.input-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 18px;
    margin-top: 18px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
}

.side-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
    margin-bottom: 16px;
}

.side-heading {
    font-size: 18px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 10px;
}

.stButton > button {
    width: 100%;
    border-radius: 14px;
    height: 44px;
    font-weight: 600;
}

hr {
    margin-top: 20px !important;
    margin-bottom: 20px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Models
# ---------------------------------------------------
GROQ_MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
}

# ---------------------------------------------------
# Session state
# ---------------------------------------------------
if "summary_history" not in st.session_state:
    st.session_state.summary_history = [
        {
            "role": "assistant",
            "content": "Hello, upload a paper or paste the text, and I will summarize it for you."
        }
    ]

if "last_summary_text" not in st.session_state:
    st.session_state.last_summary_text = ""

# ---------------------------------------------------
# Helpers
# ---------------------------------------------------
def extract_text_from_pdf(uploaded_file):
    """Read text from uploaded PDF."""
    reader = PdfReader(uploaded_file)
    pages_text = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)

    return "\n".join(pages_text).strip()


def build_summary_prompt(paper_text, summary_style):
    """Create prompt based on the selected summary style."""
    if summary_style == "Short Summary":
        instruction = """
Summarize the paper clearly in about 150 to 200 words.
Include:
1. Main topic
2. Goal
3. Method
4. Main result
5. Why it matters
"""
    elif summary_style == "Detailed Summary":
        instruction = """
Summarize the paper in a detailed but simple academic style.
Include:
1. Problem statement
2. Objective
3. Methodology
4. Dataset or source
5. Results
6. Limitations
7. Conclusion
"""
    elif summary_style == "Bullet Points":
        instruction = """
Summarize the paper in bullet points.
Include:
- Topic
- Objective
- Method
- Dataset
- Results
- Conclusion
"""
    else:
        instruction = """
Explain the paper in very simple student-friendly language.
Avoid heavy jargon.
"""

    prompt = f"""
You are a helpful research paper summarizer.

{instruction}

Paper text:
{paper_text}
"""
    return prompt


def summarize_with_groq(api_key, model_id, prompt, temperature, max_tokens):
    """Call Groq model and return summary."""
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You summarize academic papers clearly and accurately."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content


def export_history_text(history):
    """Convert history to exportable plain text."""
    lines = []
    for item in history:
        role = "You" if item["role"] == "user" else "Assistant"
        lines.append(f"{role}: {item['content']}")
        lines.append("")
    return "\n".join(lines)

# ---------------------------------------------------
# Main layout
# ---------------------------------------------------
left_col, right_col = st.columns([4.8, 1.6], gap="large")

# ---------------------------------------------------
# Left side
# ---------------------------------------------------
with left_col:
    top_a, top_b, top_c, top_d = st.columns([1.1, 1.3, 1.3, 1.3])

    with top_a:
        if st.button("⬅ Back"):
            st.switch_page("Home.py")

    st.markdown('<div class="main-title">Research Paper Summarizer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Upload a paper or paste text. Your summary stays in this session.</div>',
        unsafe_allow_html=True
    )

    # Action buttons
    btn1, btn2, btn3 = st.columns(3)

    with btn1:
        if st.button("🆕 New summary"):
            st.session_state.summary_history = [
                {
                    "role": "assistant",
                    "content": "Hello, upload a paper or paste the text, and I will summarize it for you."
                }
            ]
            st.session_state.last_summary_text = ""
            st.rerun()

    with btn2:
        if st.button("🗑 Delete last"):
            if len(st.session_state.summary_history) > 1:
                st.session_state.summary_history.pop()
                st.rerun()

    with btn3:
        export_text = export_history_text(st.session_state.summary_history)
        st.download_button(
            "⬇ Export summary",
            data=export_text,
            file_name="research_summary.txt",
            mime="text/plain"
        )

    # Summary area
    st.markdown('<div class="summary-box">', unsafe_allow_html=True)

    for item in st.session_state.summary_history:
        if item["role"] == "user":
            st.markdown('<div class="small-label">📘 Paper Input</div>', unsafe_allow_html=True)
            preview = item["content"][:700] + ("..." if len(item["content"]) > 700 else "")
            st.markdown(f'<div class="message-user">{preview}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="small-label">🤖 Summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="message-bot">{item["content"]}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Input section
    st.markdown('<div class="input-card">', unsafe_allow_html=True)

    input_type = st.radio(
        "Choose input type",
        ["Upload PDF", "Paste Text"],
        horizontal=True
    )

    paper_text = ""

    if input_type == "Upload PDF":
        uploaded_pdf = st.file_uploader("Upload research paper PDF", type=["pdf"])
        if uploaded_pdf is not None:
            with st.spinner("Reading PDF..."):
                paper_text = extract_text_from_pdf(uploaded_pdf)

            if paper_text:
                st.success("PDF loaded successfully.")
            else:
                st.warning("Could not extract text from this PDF.")
    else:
        paper_text = st.text_area(
            "Paste paper text or abstract",
            height=180,
            placeholder="Paste your research paper text here..."
        )

    summarize_now = st.button("Generate Summary", type="primary")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# Right side
# ---------------------------------------------------
with right_col:
    st.markdown('<div class="side-card">', unsafe_allow_html=True)
    st.markdown('<div class="side-heading">Select Model</div>', unsafe_allow_html=True)

    selected_model_name = st.selectbox(
        "Groq models only",
        list(GROQ_MODELS.keys()),
        label_visibility="collapsed"
    )
    selected_model_id = GROQ_MODELS[selected_model_name]
    st.caption("Groq models only")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="side-card">', unsafe_allow_html=True)
    st.markdown('<div class="side-heading">Generation Settings</div>', unsafe_allow_html=True)

    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max tokens", 200, 3000, 900, 100)
    summary_style = st.selectbox(
        "Summary Style",
        ["Short Summary", "Detailed Summary", "Bullet Points", "Explain Like a Student"]
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="side-card">', unsafe_allow_html=True)
    st.markdown('<div class="side-heading">Session</div>', unsafe_allow_html=True)

    groq_api_key = st.text_input("Groq API Key", type="password")

    if st.button("🔄 Reset session"):
        st.session_state.summary_history = [
            {
                "role": "assistant",
                "content": "Hello, upload a paper or paste the text, and I will summarize it for you."
            }
        ]
        st.session_state.last_summary_text = ""
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# Generate summary logic
# ---------------------------------------------------
if summarize_now:
    if not groq_api_key:
        st.error("Please enter your Groq API key on the right side.")
    elif not paper_text.strip():
        st.error("Please upload a PDF or paste paper text first.")
    else:
        st.session_state.summary_history.append({
            "role": "user",
            "content": paper_text
        })

        prompt = build_summary_prompt(paper_text, summary_style)

        try:
            with st.spinner("Generating summary..."):
                summary = summarize_with_groq(
                    api_key=groq_api_key,
                    model_id=selected_model_id,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

            st.session_state.summary_history.append({
                "role": "assistant",
                "content": summary
            })
            st.session_state.last_summary_text = summary
            st.rerun()

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
