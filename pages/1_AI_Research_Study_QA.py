import streamlit as st
import requests
from groq import Groq

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="AI Research Q&A", layout="wide")

# -----------------------------
# Load keys automatically
# -----------------------------
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

# -----------------------------
# Model lists
# -----------------------------
GROQ_MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant"
}

HF_MODELS = {
    "Phi-3 Mini": "microsoft/Phi-3-mini-4k-instruct",
    "Gemma 2B": "google/gemma-2b-it",
    "TinyLlama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
}

# -----------------------------
# Chat memory
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, how can I help you today?"}
    ]

# -----------------------------
# Layout
# -----------------------------
chat_col, model_col = st.columns([4,1])

# =============================
# MODEL SELECTION (RIGHT SIDE)
# =============================
with model_col:

    st.markdown("### Select Model")

    provider = st.radio(
        "Provider",
        ["Groq","HuggingFace"]
    )

    if provider == "Groq":

        model_name = st.selectbox(
            "Groq Model",
            list(GROQ_MODELS.keys())
        )

        selected_model = GROQ_MODELS[model_name]

    else:

        model_name = st.selectbox(
            "HF Model",
            list(HF_MODELS.keys())
        )

        selected_model = HF_MODELS[model_name]

# =============================
# CHAT WINDOW
# =============================
with chat_col:

    st.title("Chat")

    # display chat history
    for msg in st.session_state.messages:

        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])

        else:
            st.chat_message("assistant").write(msg["content"])

    # user input
    prompt = st.chat_input("Type your question...")

    if prompt:

        st.session_state.messages.append(
            {"role":"user","content":prompt}
        )

        st.chat_message("user").write(prompt)

        with st.spinner("Thinking..."):

            try:

                # -------------------
                # GROQ
                # -------------------
                if provider == "Groq":

                    client = Groq(api_key=GROQ_API_KEY)

                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=st.session_state.messages
                    )

                    reply = response.choices[0].message.content

                # -------------------
                # HUGGINGFACE
                # -------------------
                else:

                    API_URL = f"https://api-inference.huggingface.co/models/{selected_model}"

                    headers = {
                        "Authorization": f"Bearer {HF_TOKEN}"
                    }

                    payload = {
                        "inputs": prompt,
                        "parameters":{
                            "max_new_tokens":300
                        }
                    }

                    r = requests.post(
                        API_URL,
                        headers=headers,
                        json=payload
                    )

                    result = r.json()

                    if isinstance(result,list):
                        reply = result[0]["generated_text"]
                    else:
                        reply = "Model is loading, please try again."

            except Exception as e:

                reply = str(e)

        st.session_state.messages.append(
            {"role":"assistant","content":reply}
        )

        st.chat_message("assistant").write(reply)
