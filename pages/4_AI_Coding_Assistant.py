import json
import streamlit as st
from groq import Groq
from huggingface_hub import InferenceClient

# ---------------------------------------------------
# Page config
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Coding Assistant",
    page_icon="💻",
    layout="wide"
)

# ---------------------------------------------------
# Auto load API keys from Streamlit secrets
# ---------------------------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

# ---------------------------------------------------
# Model lists
# ---------------------------------------------------
GROQ_MODELS = {
    "Llama 3.3 70B (Best quality)": "llama-3.3-70b-versatile",
    "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant"
}


HF_MODELS = {
    "Qwen 2.5 7B Instruct": "Qwen/Qwen2.5-7B-Instruct"
}

# ---------------------------------------------------
# Session state
# ---------------------------------------------------
if "code_messages" not in st.session_state:
    st.session_state.code_messages = [
        {"role": "assistant", "content": "Hello, how can I help you with coding today?"}
    ]

if "code_provider" not in st.session_state:
    st.session_state.code_provider = "Groq"

if "code_model_id" not in st.session_state:
    st.session_state.code_model_id = GROQ_MODELS["Llama 3.3 70B (Best quality)"]

if "code_temperature" not in st.session_state:
    st.session_state.code_temperature = 0.2

if "code_max_tokens" not in st.session_state:
    st.session_state.code_max_tokens = 900

# ---------------------------------------------------
# Helpers
# ---------------------------------------------------
def build_system_prompt():
    return """
    You are an AI Coding Assistant.

    Rules:
    1. Help with Python, Streamlit, SQL, JavaScript, and machine learning code.
    2. When writing code, make it clean and beginner-friendly.
    3. Add comments only when useful.
    4. If debugging, explain the bug and then show the fixed code.
    5. If the user asks for full code, give complete runnable code.
    6. Prefer practical answers over theory.
    """

def ask_groq(messages, model_id, temperature, max_tokens):
    client = Groq(api_key=GROQ_API_KEY)

    api_messages = [{"role": "system", "content": build_system_prompt()}]
    api_messages.extend(messages)

    response = client.chat.completions.create(
        model=model_id,
        messages=api_messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

def ask_huggingface(messages, model_id, temperature, max_tokens):
    client = InferenceClient(api_key=HF_TOKEN)

    api_messages = [{"role": "system", "content": build_system_prompt()}]
    api_messages.extend(messages)

    response = client.chat.completions.create(
        model=model_id,
        messages=api_messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

def export_chat(messages):
    return json.dumps(messages, indent=2, ensure_ascii=False)

# ---------------------------------------------------
# CSS
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

with left_col:
    top1, top2 = st.columns([1, 6])

    with top1:
        if st.button("⬅ Back", use_container_width=True):
            st.switch_page("Home.py")

    with top2:
        st.markdown('<div class="page-title">AI Coding Assistant</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-subtitle">Ask for code generation, debugging, explanations, refactoring, or Streamlit help.</div>',
            unsafe_allow_html=True
        )

    b1, b2, b3 = st.columns(3)

    with b1:
        if st.button("🆕 New chat", use_container_width=True):
            st.session_state.code_messages = [
                {"role": "assistant", "content": "Hello, how can I help you with coding today?"}
            ]
            st.rerun()

    with b2:
        if st.button("🗑 Delete last", use_container_width=True):
            if len(st.session_state.code_messages) > 1:
                st.session_state.code_messages.pop()
                if len(st.session_state.code_messages) > 1:
                    st.session_state.code_messages.pop()
            st.rerun()

    with b3:
        st.download_button(
            "⬇ Export chat",
            data=export_chat(st.session_state.code_messages),
            file_name="ai_coding_assistant_chat.json",
            mime="application/json",
            use_container_width=True
        )

    st.write("")

    for msg in st.session_state.code_messages:
        if msg["role"] == "user":
            st.markdown('<div class="role-label">👤 You</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="user-box">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="role-label">🤖 Assistant</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="assistant-box">{msg["content"]}</div>', unsafe_allow_html=True)

    user_prompt = st.chat_input("Type your coding question...")

    if user_prompt:
        st.session_state.code_messages.append({"role": "user", "content": user_prompt})

        try:
            with st.spinner("Thinking..."):
                if st.session_state.code_provider == "Groq":
                    if not GROQ_API_KEY:
                        st.error("Groq API key not found in Streamlit secrets.")
                        st.stop()

                    reply = ask_groq(
                        messages=st.session_state.code_messages,
                        model_id=st.session_state.code_model_id,
                        temperature=st.session_state.code_temperature,
                        max_tokens=st.session_state.code_max_tokens
                    )
                else:
                    if not HF_TOKEN:
                        st.error("HF token not found in Streamlit secrets.")
                        st.stop()

                    reply = ask_huggingface(
                        messages=st.session_state.code_messages,
                        model_id=st.session_state.code_model_id,
                        temperature=st.session_state.code_temperature,
                        max_tokens=st.session_state.code_max_tokens
                    )

            st.session_state.code_messages.append({"role": "assistant", "content": reply})
            st.rerun()

        except Exception as e:
            st.error(f"Something went wrong: {e}")

with right_col:
    st.markdown("## Provider")
    provider = st.selectbox(
        "Choose provider",
        ["Groq", "Hugging Face"],
        index=0,
        label_visibility="collapsed"
    )
    st.session_state.code_provider = provider

    st.write("")

    if provider == "Groq":
        st.markdown("## Select Model")
        model_name = st.selectbox(
            "Groq model",
            list(GROQ_MODELS.keys()),
            label_visibility="collapsed"
        )
        st.session_state.code_model_id = GROQ_MODELS[model_name]
        st.markdown('<div class="sidebar-note">Groq models only</div>', unsafe_allow_html=True)
    else:
        st.markdown("## Select Model")
        model_name = st.selectbox(
            "HF model",
            list(HF_MODELS.keys()),
            label_visibility="collapsed"
        )
        st.session_state.code_model_id = HF_MODELS[model_name]
        st.markdown('<div class="sidebar-note">Free/open Hugging Face models</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("---")

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.code_temperature,
        step=0.1
    )
    st.session_state.code_temperature = temperature

    max_tokens = st.slider(
        "Max tokens",
        min_value=200,
        max_value=3000,
        value=st.session_state.code_max_tokens,
        step=100
    )
    st.session_state.code_max_tokens = max_tokens

    st.write("")
    st.markdown("---")

    if st.button("🔄 Reset session", use_container_width=True):
        st.session_state.code_messages = [
            {"role": "assistant", "content": "Hello, how can I help you with coding today?"}
        ]
        st.rerun()
