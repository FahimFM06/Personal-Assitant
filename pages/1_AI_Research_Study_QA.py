import streamlit as st
from groq import Groq

# -----------------------------------
# Page config
# -----------------------------------
st.set_page_config(
    page_title="AI Research Study QA",
    page_icon="💬",
    layout="wide"
)

# -----------------------------------
# Read Groq key automatically
# -----------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# -----------------------------------
# Groq models only
# -----------------------------------
GROQ_MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "GPT-OSS 120B": "openai/gpt-oss-120b",
    "GPT-OSS 20B": "openai/gpt-oss-20b",
}

# -----------------------------------
# Session state
# -----------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, how can I help you today?"}
    ]

if "selected_model" not in st.session_state:
    st.session_state.selected_model = GROQ_MODELS["Llama 3.3 70B"]

# -----------------------------------
# Clean UI
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
def ask_groq(messages, model_name):
    """
    Send chat history to Groq and get the answer.
    """
    client = Groq(api_key=GROQ_API_KEY)

    api_messages = [
        {
            "role": "system",
            "content": (
                "You are an AI Research and Study Assistant. "
                "Answer clearly, accurately, and in a student-friendly way. "
                "If needed, explain step by step."
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


def reset_chat():
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, how can I help you today?"}
    ]


def delete_last_turn():
    """
    Remove the last assistant reply and the user message before it.
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
    return "\\n\\n".join(lines)

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
                selected_model = st.session_state.selected_model

                if not GROQ_API_KEY:
                    reply = "GROQ_API_KEY is missing in Streamlit secrets."
                else:
                    reply = ask_groq(st.session_state.messages, selected_model)

        except Exception as e:
            reply = f"Something went wrong:\\n\\n{str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# -----------------------------------
# Right side: model panel
# -----------------------------------
with right_col:
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)
    st.markdown('<div class="right-title">Select Model</div>', unsafe_allow_html=True)

    selected_label = st.selectbox(
        "Groq model",
        list(GROQ_MODELS.keys()),
        label_visibility="collapsed"
    )
    st.session_state.selected_model = GROQ_MODELS[selected_label]

    st.caption("Groq models only")

    st.markdown("---")

    if st.button("♻ Reset session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
