import streamlit as st
from groq import Groq
from huggingface_hub import InferenceClient

# -----------------------------------
# Page config
# -----------------------------------
st.set_page_config(
    page_title="AI Research Study QA",
    page_icon="💬",
    layout="wide"
)

# -----------------------------------
# Read keys automatically from secrets
# -----------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

# -----------------------------------
# Models
# Groq = main reliable models
# HF = only 2 smaller free models
# -----------------------------------
GROQ_MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
}

HF_MODELS = {
    "GPT-2": "openai-community/gpt2",
    "DistilGPT-2": "distilgpt2",
}

# -----------------------------------
# Session state
# -----------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, how can I help you today?"}
    ]

if "provider" not in st.session_state:
    st.session_state.provider = "Groq"

if "selected_model" not in st.session_state:
    st.session_state.selected_model = GROQ_MODELS["Llama 3.3 70B"]

# -----------------------------------
# Simple clean style
# -----------------------------------
st.markdown("""
<style>
.main {
    background: #f7f7f8;
}
.block-container {
    max-width: 1400px;
    padding-top: 1.2rem;
    padding-bottom: 1.5rem;
}
.page-title {
    font-size: 42px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 4px;
}
.page-sub {
    color: #6b7280;
    font-size: 16px;
    margin-bottom: 18px;
}
.right-panel {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 18px;
}
.right-title {
    font-size: 22px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 12px;
}
.chat-tools {
    margin-bottom: 10px;
}
div.stButton > button {
    width: 100%;
    border-radius: 12px;
    height: 42px;
    font-weight: 600;
}
div[data-baseweb="select"] > div {
    border-radius: 12px !important;
}
hr {
    border-color: #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# Helper functions
# -----------------------------------
def build_hf_prompt(messages):
    """
    GPT-2 style models are not chat models.
    So we convert chat history into one plain text prompt.
    """
    intro = (
        "You are a helpful AI Research and Study Assistant. "
        "Answer clearly, simply, and in a student-friendly way.\n\n"
    )

    conversation = ""
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        conversation += f"{role}: {msg['content']}\n"

    conversation += "Assistant:"
    return intro + conversation


def ask_groq(messages, model_name):
    """
    Send messages to Groq chat model.
    """
    client = Groq(api_key=GROQ_API_KEY)

    api_messages = [
        {
            "role": "system",
            "content": (
                "You are an AI Research and Study Assistant. "
                "Answer clearly, accurately, and in a student-friendly way."
            )
        }
    ] + messages

    response = client.chat.completions.create(
        model=model_name,
        messages=api_messages,
        temperature=0.3,
        max_tokens=700
    )

    return response.choices[0].message.content.strip()


def ask_huggingface(messages, model_name):
    """
    Use Hugging Face InferenceClient with provider='hf-inference'.
    This is the correct modern serverless route.
    """
    client = InferenceClient(
        provider="hf-inference",
        api_key=HF_TOKEN,
    )

    prompt = build_hf_prompt(messages)

    result = client.text_generation(
        prompt,
        model=model_name,
        max_new_tokens=180,
        temperature=0.3,
        return_full_text=False
    )

    return result.strip()


def reset_chat():
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, how can I help you today?"}
    ]


def delete_last_turn():
    """
    Remove last assistant reply and the user message before it.
    """
    msgs = st.session_state.messages

    if len(msgs) <= 1:
        return

    msgs.pop()

    if len(msgs) > 1 and msgs[-1]["role"] == "user":
        msgs.pop()


def export_chat():
    lines = []
    for msg in st.session_state.messages:
        speaker = "You" if msg["role"] == "user" else "Assistant"
        lines.append(f"{speaker}: {msg['content']}")
    return "\n\n".join(lines)

# -----------------------------------
# Layout
# -----------------------------------
left_col, right_col = st.columns([4.6, 1.4])

# -----------------------------------
# Left side: chat
# -----------------------------------
with left_col:
    st.markdown('<div class="page-title">Chat</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Ask anything. Your chat stays in this session.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1.1])
    with c1:
        if st.button("🆕 New chat"):
            reset_chat()
            st.rerun()

    with c2:
        if st.button("🗑 Delete last"):
            delete_last_turn()
            st.rerun()

    with c3:
        st.download_button(
            "⬇ Export chat",
            data=export_chat(),
            file_name="chat_history.txt",
            mime="text/plain"
        )

    st.markdown("")

    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

    user_prompt = st.chat_input("Type your question...")

    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        try:
            with st.spinner("Thinking..."):
                provider = st.session_state.provider
                selected_model = st.session_state.selected_model

                if provider == "Groq":
                    if not GROQ_API_KEY:
                        reply = "GROQ_API_KEY is missing in Streamlit secrets."
                    else:
                        reply = ask_groq(st.session_state.messages, selected_model)

                else:
                    if not HF_TOKEN:
                        reply = "HF_TOKEN is missing in Streamlit secrets."
                    else:
                        reply = ask_huggingface(st.session_state.messages, selected_model)

        except Exception as e:
            reply = f"Something went wrong:\n\n{str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# -----------------------------------
# Right side: model panel
# -----------------------------------
with right_col:
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)
    st.markdown('<div class="right-title">Select Model</div>', unsafe_allow_html=True)

    provider = st.radio(
        "Provider",
        ["Groq", "HuggingFace"],
        index=0 if st.session_state.provider == "Groq" else 1,
        label_visibility="collapsed"
    )
    st.session_state.provider = provider

    st.caption("Choose model")

    if provider == "Groq":
        selected_label = st.selectbox(
            "Groq model",
            list(GROQ_MODELS.keys()),
            label_visibility="collapsed"
        )
        st.session_state.selected_model = GROQ_MODELS[selected_label]
    else:
        selected_label = st.selectbox(
            "HF model",
            list(HF_MODELS.keys()),
            label_visibility="collapsed"
        )
        st.session_state.selected_model = HF_MODELS[selected_label]

    st.markdown("---")

    if st.button("♻ Reset session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
