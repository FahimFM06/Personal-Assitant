import streamlit as st
from groq import Groq
from huggingface_hub import InferenceClient

# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Research & Study Q&A",
    page_icon="💬",
    layout="wide"
)

# ---------------------------------------------------------
# Custom CSS for the UI
# ---------------------------------------------------------
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
    font-size: 54px;
    font-weight: 800;
    color: white;
    margin-bottom: 10px;
}

.hero-sub {
    font-size: 18px;
    color: #d7d7d7;
}

.chat-wrap {
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 24px;
    padding: 18px;
    min-height: 420px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.20);
}

.chat-bubble-user {
    background: rgba(255,255,255,0.85);
    color: #222;
    padding: 16px 18px;
    border-radius: 18px;
    margin: 12px 0;
    font-size: 17px;
}

.chat-bubble-assistant {
    background: rgba(255, 196, 0, 0.92);
    color: #1a1a1a;
    padding: 16px 18px;
    border-radius: 18px;
    margin: 12px 0;
    font-size: 17px;
}

.small-label {
    color: #e5e5e5;
    font-size: 14px;
    margin-bottom: 6px;
    opacity: 0.85;
}

div.stSelectbox > label, div.stTextInput > label, div.stSlider > label {
    color: white !important;
    font-weight: 600 !important;
}

.stButton > button {
    border-radius: 14px;
    height: 44px;
    font-weight: 600;
}

.back-btn {
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Model lists
# ---------------------------------------------------------
GROQ_MODELS = {
    "Llama 3.3 70B (Best quality)": "llama-3.3-70b-versatile",
    "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant",
}

HF_MODELS = {
    "Qwen 2.5 7B Instruct": "Qwen/Qwen2.5-7B-Instruct",
    "Phi 3.5 Mini Instruct": "microsoft/Phi-3.5-mini-instruct",
}

# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello, how can I assist you today?"
        }
    ]

# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------
def ask_groq(api_key, model_id, messages, temperature, max_tokens):
    """
    Send the conversation to Groq and return the assistant reply.
    """
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content


def ask_huggingface(api_key, model_id, messages, temperature, max_tokens):
    """
    Send the conversation to Hugging Face Inference API and return the assistant reply.
    """
    client = InferenceClient(api_key=api_key)

    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content

# ---------------------------------------------------------
# Top area
# ---------------------------------------------------------
col_back, col_head = st.columns([1, 8])

with col_back:
    if st.button("⬅ Back"):
        st.switch_page("Home.py")

with col_head:
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">Chat</div>
        <div class="hero-sub">Ask anything. Your chat stays in this session.</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar settings
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    provider = st.radio(
        "Choose provider",
        ["Groq", "Hugging Face"],
        index=0
    )

    if provider == "Groq":
        selected_model_name = st.selectbox("Select model", list(GROQ_MODELS.keys()))
        selected_model_id = GROQ_MODELS[selected_model_name]
        api_key = st.text_input("Enter Groq API key", type="password")
    else:
        selected_model_name = st.selectbox("Select model", list(HF_MODELS.keys()))
        selected_model_id = HF_MODELS[selected_model_name]
        api_key = st.text_input("Enter Hugging Face token", type="password")

    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max tokens", 128, 2048, 512, 64)

    st.markdown("---")
    if st.button("🧹 Clear chat"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello, how can I assist you today?"
            }
        ]
        st.rerun()

# ---------------------------------------------------------
# Chat area
# ---------------------------------------------------------
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown('<div class="small-label">👤 You</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="small-label">🤖 Assistant</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble-assistant">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Chat input
# ---------------------------------------------------------
user_prompt = st.chat_input("Type your message...")

if user_prompt:
    # Add user message first
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Prepare message format for API
    api_messages = [
        {
            "role": "system",
            "content": (
                "You are an AI Research and Study Assistant. "
                "Answer clearly, accurately, and in a student-friendly way. "
                "When needed, explain step by step."
            )
        }
    ]

    # Add full chat history after system prompt
    for item in st.session_state.messages:
        api_messages.append(
            {"role": item["role"], "content": item["content"]}
        )

    try:
        if not api_key:
            reply = "Please add your API key from the sidebar first."
        else:
            with st.spinner("Thinking..."):
                if provider == "Groq":
                    reply = ask_groq(
                        api_key=api_key,
                        model_id=selected_model_id,
                        messages=api_messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                else:
                    reply = ask_huggingface(
                        api_key=api_key,
                        model_id=selected_model_id,
                        messages=api_messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )

        st.session_state.messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        error_message = f"Something went wrong: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_message})

    st.rerun()
