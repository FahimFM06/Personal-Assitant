import json
import streamlit as st
import requests
from groq import Groq

# ---------------------------------------------------
# Page setup
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Research Study QA",
    page_icon="💬",
    layout="wide"
)

# ---------------------------------------------------
# Read API keys automatically from Streamlit secrets
# ---------------------------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

# ---------------------------------------------------
# Model lists
# Only 2 free Hugging Face models as requested
# ---------------------------------------------------
GROQ_MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
}

HF_MODELS = {
    "FLAN-T5 Base": "google/flan-t5-base",
    "FLAN-T5 Large": "google/flan-t5-large",
}

# ---------------------------------------------------
# Session state
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, how can I help you today?"}
    ]

if "provider" not in st.session_state:
    st.session_state.provider = "Groq"

if "selected_model" not in st.session_state:
    st.session_state.selected_model = GROQ_MODELS["Llama 3.3 70B"]

# ---------------------------------------------------
# Clean CSS
# Right-side model panel like your sketch
# ---------------------------------------------------
st.markdown("""
<style>
.main {
    background: #0b0b0f;
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1.5rem;
    max-width: 1400px;
}
.title-text {
    font-size: 42px;
    font-weight: 800;
    color: white;
    margin-bottom: 6px;
}
.sub-text {
    color: #cfcfcf;
    font-size: 16px;
    margin-bottom: 18px;
}
.chat-shell {
    background: #111218;
    border: 1px solid #262835;
    border-radius: 24px;
    padding: 20px;
    min-height: 600px;
}
.model-shell {
    background: #111218;
    border: 1px solid #262835;
    border-radius: 22px;
    padding: 18px;
}
.right-title {
    color: white;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 14px;
}
.section-label {
    color: #d9d9d9;
    font-size: 14px;
    margin-top: 8px;
    margin-bottom: 6px;
}
.stChatMessage {
    border-radius: 16px;
}
div[data-testid="stChatMessageContent"] {
    border-radius: 16px;
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
    border-color: #262835;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Helper functions
# ---------------------------------------------------
def format_hf_prompt(messages):
    """
    Convert chat history into a single text prompt for FLAN-T5.
    This works better because FLAN models are instruction-following models,
    not true chat-completion models.
    """
    system_part = (
        "You are an AI Research and Study Assistant. "
        "Answer clearly, accurately, and in a student-friendly way. "
        "Keep the answer focused and helpful.\n\n"
    )

    history_text = ""
    for msg in messages[:-1]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    latest_user = messages[-1]["content"]

    final_prompt = (
        system_part
        + history_text
        + f"User: {latest_user}\n"
        + "Assistant:"
    )
    return final_prompt


def ask_groq(messages, model_name):
    """
    Send full chat history to Groq.
    """
    client = Groq(api_key=GROQ_API_KEY)

    api_messages = [
        {
            "role": "system",
            "content": (
                "You are an AI Research and Study Assistant. "
                "Answer clearly, accurately, and in a student-friendly way."
            ),
        }
    ] + messages

    response = client.chat.completions.create(
        model=model_name,
        messages=api_messages,
        temperature=0.3,
        max_tokens=700,
    )

    return response.choices[0].message.content.strip()


def ask_huggingface(messages, model_name):
    """
    Call Hugging Face free serverless Inference API.
    We use wait_for_model=True so the request waits during cold start.
    """
    prompt = format_hf_prompt(messages)

    api_url = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 220,
            "return_full_text": False,
            "temperature": 0.3,
        },
        "options": {
            "wait_for_model": True,
            "use_cache": False
        }
    }

    response = requests.post(api_url, headers=headers, json=payload, timeout=120)

    # Helpful error handling
    if response.status_code != 200:
        raise Exception(f"Hugging Face error {response.status_code}: {response.text}")

    result = response.json()

    # Common successful response format
    if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
        return result[0]["generated_text"].strip()

    # Some models may return plain dict errors
    if isinstance(result, dict) and "error" in result:
        raise Exception(result["error"])

    raise Exception(f"Unexpected Hugging Face response: {result}")


def reset_chat():
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, how can I help you today?"}
    ]


def delete_last_turn():
    """
    Remove the last assistant+user pair if available.
    """
    msgs = st.session_state.messages

    # Keep at least the welcome message
    if len(msgs) <= 1:
        return

    # Remove last message
    msgs.pop()

    # If previous message is user, remove that too
    if len(msgs) > 1 and msgs[-1]["role"] == "user":
        msgs.pop()


def export_chat_text():
    """
    Turn chat history into downloadable text.
    """
    lines = []
    for msg in st.session_state.messages:
        role = "You" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}")
    return "\n\n".join(lines)

# ---------------------------------------------------
# Main layout
# ---------------------------------------------------
chat_col, model_col = st.columns([4.8, 1.2])

# ---------------------------------------------------
# Left side: chat area
# ---------------------------------------------------
with chat_col:
    st.markdown('<div class="title-text">Chat</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-text">Ask anything. Your chat stays in this session.</div>', unsafe_allow_html=True)

    action_col1, action_col2, action_col3 = st.columns([1, 1, 1.2])
    with action_col1:
        if st.button("🆕 New chat"):
            reset_chat()
            st.rerun()
    with action_col2:
        if st.button("🗑 Delete last"):
            delete_last_turn()
            st.rerun()
    with action_col3:
        st.download_button(
            "⬇ Export chat",
            data=export_chat_text(),
            file_name="chat_history.txt",
            mime="text/plain"
        )

    st.markdown('<div class="chat-shell">', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

    st.markdown('</div>', unsafe_allow_html=True)

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

# ---------------------------------------------------
# Right side: model selection panel
# ---------------------------------------------------
with model_col:
    st.markdown('<div class="model-shell">', unsafe_allow_html=True)
    st.markdown('<div class="right-title">Select Model</div>', unsafe_allow_html=True)

    provider = st.radio(
        "Provider",
        ["Groq", "HuggingFace"],
        index=0 if st.session_state.provider == "Groq" else 1,
        label_visibility="collapsed"
    )
    st.session_state.provider = provider

    st.markdown('<div class="section-label">Choose model</div>', unsafe_allow_html=True)

    if provider == "Groq":
        model_label = st.selectbox(
            "Groq model",
            list(GROQ_MODELS.keys()),
            label_visibility="collapsed"
        )
        st.session_state.selected_model = GROQ_MODELS[model_label]
        st.caption("Best for fast and stable chat.")
    else:
        model_label = st.selectbox(
            "HF model",
            list(HF_MODELS.keys()),
            label_visibility="collapsed"
        )
        st.session_state.selected_model = HF_MODELS[model_label]
        st.caption("Free serverless models. They may cold-start.")

    st.markdown("---")

    st.markdown("**Active key status**")
    st.write(f"Groq: {'✅ Found' if GROQ_API_KEY else '❌ Missing'}")
    st.write(f"HF: {'✅ Found' if HF_TOKEN else '❌ Missing'}")

    st.markdown("---")

    if st.button("♻ Reset session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
