import streamlit as st
from groq import Groq
from huggingface_hub import InferenceClient
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
# Custom CSS
# ---------------------------------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #03131d, #17071f);
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}
.hero-box {
    background: rgba(0, 0, 0, 0.28);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 26px;
    padding: 30px 35px;
    margin-bottom: 24px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
}
.hero-title {
    font-size: 50px;
    font-weight: 800;
    color: white;
    margin-bottom: 10px;
}
.hero-sub {
    font-size: 18px;
    color: #d7d7d7;
}
.result-box {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 22px;
    padding: 22px;
    color: white;
    margin-top: 20px;
}
div.stButton > button {
    border-radius: 14px;
    height: 46px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Model dictionaries
# ---------------------------------------------------
GROQ_MODELS = {
    "Llama 3.3 70B (Best quality)": "llama-3.3-70b-versatile",
    "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant",
}

HF_MODELS = {
    "Qwen 2.5 7B Instruct": "Qwen/Qwen2.5-7B-Instruct",
    "Phi 3.5 Mini Instruct": "microsoft/Phi-3.5-mini-instruct",
}

# ---------------------------------------------------
# Helper: read PDF text
# ---------------------------------------------------
def extract_text_from_pdf(uploaded_file):
    """
    Read text from an uploaded PDF file.
    This keeps the code simple and beginner friendly.
    """
    reader = PdfReader(uploaded_file)
    all_text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            all_text.append(page_text)

    return "\n".join(all_text).strip()


# ---------------------------------------------------
# Helper: build summary prompt
# ---------------------------------------------------
def build_summary_prompt(paper_text, summary_type):
    """
    Create different prompts depending on what kind of summary
    the user wants.
    """
    if summary_type == "Short Summary":
        instruction = """
        Summarize this research paper in a short and simple way.
        Keep it clear, human-friendly, and around 150-200 words.
        Mention:
        1. Main topic
        2. Goal
        3. Method
        4. Main result
        5. Why it matters
        """
    elif summary_type == "Detailed Summary":
        instruction = """
        Summarize this research paper in a detailed but easy-to-read way.
        Cover:
        1. Research problem
        2. Objective
        3. Data or dataset
        4. Methodology
        5. Key results
        6. Limitations
        7. Final conclusion
        """
    elif summary_type == "Bullet Points":
        instruction = """
        Summarize this research paper using bullet points.
        Include:
        - Topic
        - Research objective
        - Method used
        - Dataset or source
        - Important findings
        - Conclusion
        """
    else:
        instruction = """
        Explain this research paper like I am a student.
        Use simple language and avoid heavy jargon.
        """

    final_prompt = f"""
    You are a helpful academic research assistant.

    {instruction}

    Here is the research paper text:
    {paper_text}
    """
    return final_prompt


# ---------------------------------------------------
# Helper: ask Groq
# ---------------------------------------------------
def summarize_with_groq(api_key, model_id, prompt, temperature, max_tokens):
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are a helpful research paper summarizer."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content


# ---------------------------------------------------
# Helper: ask Hugging Face
# ---------------------------------------------------
def summarize_with_hf(api_key, model_id, prompt, temperature, max_tokens):
    client = InferenceClient(api_key=api_key)

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are a helpful research paper summarizer."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content


# ---------------------------------------------------
# Top header
# ---------------------------------------------------
left_col, right_col = st.columns([1, 8])

with left_col:
    if st.button("⬅ Back"):
        st.switch_page("Home.py")

with right_col:
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">Research Paper Summarizer</div>
        <div class="hero-sub">Upload a PDF or paste paper text, then generate a clean summary.</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------
# Sidebar settings
# ---------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    provider = st.radio("Choose provider", ["Groq", "Hugging Face"], index=0)

    if provider == "Groq":
        model_name = st.selectbox("Select model", list(GROQ_MODELS.keys()))
        model_id = GROQ_MODELS[model_name]
        api_key = st.text_input("Enter Groq API key", type="password")
    else:
        model_name = st.selectbox("Select model", list(HF_MODELS.keys()))
        model_id = HF_MODELS[model_name]
        api_key = st.text_input("Enter Hugging Face token", type="password")

    summary_type = st.selectbox(
        "Summary style",
        ["Short Summary", "Detailed Summary", "Bullet Points", "Explain Like a Student"]
    )

    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max tokens", 200, 3000, 900, 100)

# ---------------------------------------------------
# Input section
# ---------------------------------------------------
st.subheader("Choose your input")

input_option = st.radio(
    "How do you want to give the paper?",
    ["Upload PDF", "Paste paper text / abstract"],
    horizontal=True
)

paper_text = ""

if input_option == "Upload PDF":
    uploaded_pdf = st.file_uploader("Upload a research paper PDF", type=["pdf"])

    if uploaded_pdf is not None:
        with st.spinner("Reading PDF..."):
            paper_text = extract_text_from_pdf(uploaded_pdf)

        if paper_text:
            st.success("PDF text extracted successfully.")
            with st.expander("Preview extracted text"):
                st.write(paper_text[:3000] + ("..." if len(paper_text) > 3000 else ""))
        else:
            st.warning("Could not extract text from this PDF.")
else:
    paper_text = st.text_area(
        "Paste the paper abstract or full text here",
        height=260,
        placeholder="Paste research paper text here..."
    )

# ---------------------------------------------------
# Summarize button
# ---------------------------------------------------
if st.button("Generate Summary", type="primary"):
    if not api_key:
        st.error("Please enter your API key in the sidebar.")
    elif not paper_text.strip():
        st.error("Please upload a PDF or paste some paper text first.")
    else:
        prompt = build_summary_prompt(paper_text, summary_type)

        try:
            with st.spinner("Generating summary..."):
                if provider == "Groq":
                    summary = summarize_with_groq(
                        api_key=api_key,
                        model_id=model_id,
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                else:
                    summary = summarize_with_hf(
                        api_key=api_key,
                        model_id=model_id,
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )

            st.markdown(f"""
            <div class="result-box">
                <h3>Summary Output</h3>
                <p>{summary}</p>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
