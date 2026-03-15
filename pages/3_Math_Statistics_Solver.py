import json
import streamlit as st
from groq import Groq

# ---------------------------------------------------
# Page config
# ---------------------------------------------------
st.set_page_config(
    page_title="Math & Statistics Solver",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------
# Auto load Groq API key from Streamlit secrets
# ---------------------------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# ---------------------------------------------------
# Groq models
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
if "math_messages" not in st.session_state:
    st.session_state.math_messages = [
        {"role": "assistant", "content": "Hello, how can I help you with math or statistics today?"}
    ]

if "math_selected_model_id" not in st.session_state:
    st.session_state.math_selected_model_id = GROQ_MODELS["Llama 3.3 70B"]

if "math_temperature" not in st.session_state:
    st.session_state.math_temperature = 0.2

if "math_max_tokens" not in st.session_state:
    st.session_state.math_max_tokens = 700

# ---------------------------------------------------
# Helper: ask Groq
# ---------------------------------------------------
def get_math_response(messages, model_id, temperature, max_tokens):
    """
    Send the conversation to Groq and return the answer.
    """
    client = Groq(api_key=GROQ_API_KEY)

    system_prompt = """
    You are a Math and Statistics Assistant.

    Rules:
    1. Solve problems step by step.
    2. Keep explanations clear and student-friendly.
    3. For statistics, explain formulas and meaning.
    4. If the user asks for only the final answer, give the final answer first.
    5. Use simple formatting.
    """

    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages.extend(messages)

    response = client.chat.completions.create(
        model=model_id,
        messages=api_messages,
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content

# ---------------------------------------------------
# Helper: export chat
# ---------------------------------------------------
def export_chat(messages):
    return json.dumps(messages, indent=2, ensure_ascii=False)

# ---------------------------------------------------
# Custom CSS
# ---------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: #f6f7fb;
}

.main .block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

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

.stButton > button {
    border-radius: 14px;
    height: 44px;
    border: 1px solid #d1d5db;
    background: white;
}

/* Chat message styles */
.user-box {
    background: #e5e7eb;
    color: #111827;
    padding: 14px 16px;
    border-radius: 16px;
    margin-bottom: 12px;
    font-size: 1rem;
}

.assistant-box {
    background: #ffffff;
    color: #111827;
    padding: 14px 16px;
    border-radius: 16px;
    margin-bottom: 12px;
    border: 1px solid #e5e7eb;
    font-size: 1rem;
}

.role-label {
    color: #64748b;
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}

.sidebar-note {
    font-size: 0.92rem;
    color: #6b7280;
    margin-top: 0.25rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Layout
# ---------------------------------------------------
left_col, right_col = st.columns([4.8, 1.8], gap="large")

# ---------------------------------------------------
# Left side
# ---------------------------------------------------
with left_col:
    top1, top2 = st.columns([1, 6])

    with top1:
        if st.button("⬅ Back", use_container_width=True):
            st.switch_page("Home.py")

    with top2:
        st.markdown('<div class="page-title">Math & Statistics Solver</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-subtitle">Ask anything about algebra, calculus, probability, statistics, or linear algebra.</div>',
            unsafe_allow_html=True
        )

    b1, b2, b3 = st.columns(3)

    with b1:
        if st.button("🆕 New chat", use_container_width=True):
            st.session_state.math_messages = [
                {"role": "assistant", "content": "Hello, how can I help you with math or statistics today?"}
            ]
            st.rerun()

    with b2:
        if st.button("🗑 Delete last", use_container_width=True):
            if len(st.session_state.math_messages) > 1:
                st.session_state.math_messages.pop()
                if len(st.session_state.math_messages) > 1:
                    st.session_state.math_messages.pop()
            st.rerun()

    with b3:
        st.download_button(
            "⬇ Export chat",
            data=export_chat(st.session_state.math_messages),
            file_name="math_statistics_chat.json",
            mime="application/json",
            use_container_width=True
        )

    st.write("")

    for msg in st.session_state.math_messages:
        if msg["role"] == "user":
            st.markdown('<div class="role-label">👤 You</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="user-box">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="role-label">🤖 Assistant</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="assistant-box">{msg["content"]}</div>', unsafe_allow_html=True)

    user_prompt = st.chat_input("Type your math or statistics question...")

    if user_prompt:
        if not GROQ_API_KEY:
            st.error("Groq API key not found in Streamlit secrets. Add GROQ_API_KEY first.")
        else:
            st.session_state.math_messages.append({"role": "user", "content": user_prompt})

            try:
                with st.spinner("Solving..."):
                    reply = get_math_response(
                        messages=st.session_state.math_messages,
                        model_id=st.session_state.math_selected_model_id,
                        temperature=st.session_state.math_temperature,
                        max_tokens=st.session_state.math_max_tokens
                    )

                st.session_state.math_messages.append({"role": "assistant", "content": reply})
                st.rerun()

            except Exception as e:
                st.error(f"Something went wrong: {e}")

# ---------------------------------------------------
# Right side
# ---------------------------------------------------
with right_col:
    st.markdown("## Select Model")

    selected_model_name = st.selectbox(
        "Model",
        list(GROQ_MODELS.keys()),
        index=0,
        label_visibility="collapsed"
    )
    st.session_state.math_selected_model_id = GROQ_MODELS[selected_model_name]

    st.markdown('<div class="sidebar-note">Groq models only</div>', unsafe_allow_html=True)

    st.write("")
    st.write("")
    st.markdown("---")

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.math_temperature,
        step=0.1
    )
    st.session_state.math_temperature = temperature

    max_tokens = st.slider(
        "Max tokens",
        min_value=200,
        max_value=3000,
        value=st.session_state.math_max_tokens,
        step=100
    )
    st.session_state.math_max_tokens = max_tokens

    st.write("")
    st.markdown("---")

    if st.button("🔄 Reset session", use_container_width=True):
        st.session_state.math_messages = [
            {"role": "assistant", "content": "Hello, how can I help you with math or statistics today?"}
        ]
        st.rerun()
