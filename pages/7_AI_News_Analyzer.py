import requests
import streamlit as st
from groq import Groq
from huggingface_hub import InferenceClient

# ---------------------------------------------------
# Page config
# ---------------------------------------------------
st.set_page_config(
    page_title="AI News Analyzer",
    page_icon="📰",
    layout="wide"
)

# ---------------------------------------------------
# API keys from Streamlit secrets
# ---------------------------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "")

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
if "news_articles" not in st.session_state:
    st.session_state.news_articles = []

if "news_ai_summary" not in st.session_state:
    st.session_state.news_ai_summary = ""

if "news_provider" not in st.session_state:
    st.session_state.news_provider = "Groq"

if "news_temperature" not in st.session_state:
    st.session_state.news_temperature = 0.3

if "news_max_tokens" not in st.session_state:
    st.session_state.news_max_tokens = 700

if "news_model_id" not in st.session_state:
    st.session_state.news_model_id = GROQ_MODELS["Llama 3.3 70B (Best quality)"]

# ---------------------------------------------------
# Helper: fetch news
# ---------------------------------------------------
def fetch_news(topic: str, sort_by: str, page_size: int):
    """
    Get news articles from NewsAPI.
    """
    url = "https://newsapi.org/v2/everything"
    headers = {
        "X-Api-Key": NEWS_API_KEY
    }
    params = {
        "q": topic,
        "language": "en",
        "sortBy": sort_by,
        "pageSize": page_size
    }

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    if data.get("status") != "ok":
        raise ValueError(data.get("message", "Failed to fetch news."))

    return data.get("articles", [])

# ---------------------------------------------------
# Helper: make prompt
# ---------------------------------------------------
def build_news_prompt(topic: str, articles: list):
    """
    Build the AI analysis prompt from fetched articles.
    """
    article_text = []

    for i, article in enumerate(articles, start=1):
        article_text.append(
            f"""
Article {i}
Title: {article.get('title', 'N/A')}
Source: {article.get('source', {}).get('name', 'N/A')}
Published At: {article.get('publishedAt', 'N/A')}
Description: {article.get('description', 'N/A')}
Content: {article.get('content', 'N/A')}
"""
        )

    joined_articles = "\n".join(article_text)

    prompt = f"""
You are a helpful AI news analyst.

Analyze the following news articles about: {topic}

Write the answer in a clear and human-friendly way.

Please include:
1. Main news trend
2. Key points across sources
3. Overall tone of the news
4. Any repeated themes or major developments
5. A short conclusion

News content:
{joined_articles}
"""
    return prompt

# ---------------------------------------------------
# Helper: ask Groq
# ---------------------------------------------------
def ask_groq(prompt: str, model_id: str, temperature: float, max_tokens: int):
    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are a helpful news analysis assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content

# ---------------------------------------------------
# Helper: ask Hugging Face
# ---------------------------------------------------
def ask_huggingface(prompt: str, model_id: str, temperature: float, max_tokens: int):
    client = InferenceClient(api_key=HF_TOKEN)

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are a helpful news analysis assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content

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

.sidebar-note {
    font-size: 0.92rem;
    color: #6b7280;
    margin-top: 0.25rem;
}

.info-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 14px;
}

.summary-box {
    color: #111827;
    font-size: 1rem;
    line-height: 1.7;
    background: transparent;
    border: none;
    padding: 0.2rem 0;
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
        st.markdown('<div class="page-title">AI News Analyzer</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-subtitle">Search a topic, fetch recent articles, and get an AI-generated news analysis.</div>',
            unsafe_allow_html=True
        )

    topic = st.text_input("News topic", placeholder="Example: artificial intelligence")

    col_a, col_b = st.columns(2)

    with col_a:
        sort_by = st.selectbox(
            "Sort by",
            ["publishedAt", "relevancy", "popularity"],
            index=0
        )

    with col_b:
        page_size = st.selectbox(
            "Number of articles",
            [3, 5, 7, 10],
            index=1
        )

    if st.button("📰 Fetch and Analyze News", use_container_width=True):
        if not NEWS_API_KEY:
            st.error("NEWS_API_KEY not found in Streamlit secrets.")
        elif not topic.strip():
            st.error("Please enter a news topic.")
        else:
            try:
                with st.spinner("Fetching latest news..."):
                    articles = fetch_news(topic.strip(), sort_by, page_size)
                    st.session_state.news_articles = articles

                if not articles:
                    st.warning("No articles found for this topic.")
                else:
                    prompt = build_news_prompt(topic.strip(), articles)

                    with st.spinner("Generating AI analysis..."):
                        if st.session_state.news_provider == "Groq":
                            if not GROQ_API_KEY:
                                st.error("Groq API key not found in Streamlit secrets.")
                            else:
                                st.session_state.news_ai_summary = ask_groq(
                                    prompt=prompt,
                                    model_id=st.session_state.news_model_id,
                                    temperature=st.session_state.news_temperature,
                                    max_tokens=st.session_state.news_max_tokens
                                )
                        else:
                            if not HF_TOKEN:
                                st.error("HF token not found in Streamlit secrets.")
                            else:
                                st.session_state.news_ai_summary = ask_huggingface(
                                    prompt=prompt,
                                    model_id=st.session_state.news_model_id,
                                    temperature=st.session_state.news_temperature,
                                    max_tokens=st.session_state.news_max_tokens
                                )

            except Exception as e:
                st.error(f"Something went wrong: {e}")

    st.write("")

    if st.session_state.news_articles:
        st.markdown("### Latest Articles")

        for article in st.session_state.news_articles:
            source_name = article.get("source", {}).get("name", "Unknown Source")
            title = article.get("title", "No title")
            description = article.get("description", "No description available.")
            published_at = article.get("publishedAt", "N/A")
            url = article.get("url", "#")

            st.markdown(
                f"""
                <div class="info-card">
                    <b>{title}</b><br><br>
                    <b>Source:</b> {source_name}<br>
                    <b>Published:</b> {published_at}<br><br>
                    {description}<br><br>
                    <a href="{url}" target="_blank">Read full article</a>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("### AI News Analysis")
    if st.session_state.news_ai_summary:
        st.markdown(
            f'<div class="summary-box">{st.session_state.news_ai_summary}</div>',
            unsafe_allow_html=True
        )
    else:
        st.info("Your AI news analysis will appear here.")

with right_col:
    st.markdown("## Provider")
    provider = st.selectbox(
        "Choose provider",
        ["Groq", "Hugging Face"],
        index=0,
        label_visibility="collapsed"
    )
    st.session_state.news_provider = provider

    st.write("")

    if provider == "Groq":
        st.markdown("## Select Model")
        model_name = st.selectbox(
            "Groq model",
            list(GROQ_MODELS.keys()),
            label_visibility="collapsed"
        )
        st.session_state.news_model_id = GROQ_MODELS[model_name]
        st.markdown('<div class="sidebar-note">Groq models only</div>', unsafe_allow_html=True)
    else:
        st.markdown("## Select Model")
        model_name = st.selectbox(
            "HF model",
            list(HF_MODELS.keys()),
            label_visibility="collapsed"
        )
        st.session_state.news_model_id = HF_MODELS[model_name]
        st.markdown('<div class="sidebar-note">Free/open Hugging Face models</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("---")

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.news_temperature,
        step=0.1
    )
    st.session_state.news_temperature = temperature

    max_tokens = st.slider(
        "Max tokens",
        min_value=200,
        max_value=1500,
        value=st.session_state.news_max_tokens,
        step=100
    )
    st.session_state.news_max_tokens = max_tokens

    st.write("")
    st.markdown("---")

    if st.button("🔄 Reset session", use_container_width=True):
        st.session_state.news_articles = []
        st.session_state.news_ai_summary = ""
        st.rerun()
