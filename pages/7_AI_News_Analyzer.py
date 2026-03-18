import os
import requests
import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="AI News Analyzer", page_icon="📰", layout="wide")

# =========================================================
# THEMES
# =========================================================
THEMES = {
    "Cloud (Light)": {
        "app_bg": "#f6f7fb",
        "panel_bg": "#ffffff",
        "title": "#0f172a",
        "sub": "#475569",
        "border": "#e5e7eb",
        "text": "#0f172a",
        "muted": "#64748b",
        "shadow": "0 10px 30px rgba(15, 23, 42, 0.08)",
        "input_bg": "#ffffff",
        "widget_bg": "#ffffff",
        "widget_text": "#0f172a",
        "menu_bg": "#ffffff",
        "menu_text": "#0f172a",
        "btn_bg": "#111827",
        "btn_text": "#ffffff",
        "btn_border": "#111827",
        "card_bg": "#ffffff",
    },
    "Midnight (Dark)": {
        "app_bg": "#0b1220",
        "panel_bg": "#0f172a",
        "title": "#e5e7eb",
        "sub": "#94a3b8",
        "border": "#1f2a44",
        "text": "#e5e7eb",
        "muted": "#94a3b8",
        "shadow": "0 10px 26px rgba(0,0,0,0.45)",
        "input_bg": "#0f172a",
        "widget_bg": "#111827",
        "widget_text": "#e5e7eb",
        "menu_bg": "#0b1220",
        "menu_text": "#e5e7eb",
        "btn_bg": "#111827",
        "btn_text": "#e5e7eb",
        "btn_border": "#1f2a44",
        "card_bg": "#111827",
    },
    "Night Mode": {
        "app_bg": """
            radial-gradient(ellipse at center, rgba(255,255,255,0.10) 0%, rgba(0,0,0,0.55) 60%, rgba(0,0,0,0.85) 100%),
            repeating-linear-gradient(90deg,
                rgba(255,255,255,0.06) 0px,
                rgba(255,255,255,0.06) 1px,
                rgba(0,0,0,0.00) 2px,
                rgba(0,0,0,0.00) 4px
            ),
            linear-gradient(180deg, #0a0a0b 0%, #111214 35%, #070708 100%)
        """,
        "panel_bg": "rgba(20, 20, 22, 0.72)",
        "title": "#f3f4f6",
        "sub": "#cbd5e1",
        "border": "rgba(255,255,255,0.10)",
        "text": "#f3f4f6",
        "muted": "#cbd5e1",
        "shadow": "0 12px 30px rgba(0,0,0,0.55)",
        "input_bg": "rgba(20, 20, 22, 0.72)",
        "widget_bg": "rgba(20, 20, 22, 0.72)",
        "widget_text": "#f3f4f6",
        "menu_bg": "rgba(20, 20, 22, 0.92)",
        "menu_text": "#f3f4f6",
        "btn_bg": "rgba(20, 20, 22, 0.72)",
        "btn_text": "#f3f4f6",
        "btn_border": "rgba(255,255,255,0.12)",
        "card_bg": "rgba(20, 20, 22, 0.72)",
    },
}

PROVIDERS = ["Groq", "Hugging Face"]

# =========================================================
# MODELS
# =========================================================
GROQ_MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "GPT-OSS 120B": "openai/gpt-oss-120b",
    "GPT-OSS 20B": "openai/gpt-oss-20b",
}

HF_MODELS = {
    "Qwen 2.5 7B Instruct": "Qwen/Qwen2.5-7B-Instruct"
}

SORT_OPTIONS = {
    "Newest": "publishedAt",
    "Relevancy": "relevancy",
    "Popularity": "popularity"
}

# -----------------------------
# Session state
# -----------------------------
if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Midnight (Dark)"

if "news_provider" not in st.session_state:
    st.session_state.news_provider = "Groq"

if "news_groq_model_name" not in st.session_state:
    st.session_state.news_groq_model_name = list(GROQ_MODELS.keys())[0]

if "news_hf_model_name" not in st.session_state:
    st.session_state.news_hf_model_name = list(HF_MODELS.keys())[0]

if "news_temperature" not in st.session_state:
    st.session_state.news_temperature = 0.3

if "news_max_tokens" not in st.session_state:
    st.session_state.news_max_tokens = 900

if "news_topic" not in st.session_state:
    st.session_state.news_topic = ""

if "news_sort_label" not in st.session_state:
    st.session_state.news_sort_label = "Newest"

if "news_page_size" not in st.session_state:
    st.session_state.news_page_size = 5

if "news_articles" not in st.session_state:
    st.session_state.news_articles = []

if "news_ai_summary" not in st.session_state:
    st.session_state.news_ai_summary = ""

T = THEMES[st.session_state.theme_name]

# -----------------------------
# CSS
# -----------------------------
st.markdown(
    f"""
    <style>
    :root {{
        --app-bg: {T["app_bg"]};
        --panel-bg: {T["panel_bg"]};
        --title: {T["title"]};
        --sub: {T["sub"]};
        --border: {T["border"]};
        --text: {T["text"]};
        --muted: {T["muted"]};
        --shadow: {T["shadow"]};
        --input-bg: {T["input_bg"]};
        --widget-bg: {T["widget_bg"]};
        --widget-text: {T["widget_text"]};
        --menu-bg: {T["menu_bg"]};
        --menu-text: {T["menu_text"]};
        --btn-bg: {T["btn_bg"]};
        --btn-text: {T["btn_text"]};
        --btn-border: {T["btn_border"]};
        --card-bg: {T["card_bg"]};
    }}

    .stApp {{
        background: var(--app-bg) !important;
        color: var(--text) !important;
    }}

    html, body, [class*="css"] {{
        color: var(--text) !important;
    }}

    .main .block-container {{
        max-width: 1300px;
        padding-top: 1rem;
        padding-bottom: 0.5rem;
    }}

    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    .page-title {{
        font-size: 2.0rem;
        font-weight: 800;
        color: var(--title) !important;
        margin: 0 0 0.1rem 0;
    }}

    .page-sub {{
        color: var(--sub) !important;
        margin: 0 0 0.8rem 0;
        font-size: 0.95rem;
    }}

    .right-panel {{
        background: var(--panel-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px;
        padding: 14px;
        box-shadow: var(--shadow) !important;
        color: var(--text) !important;
    }}

    .right-middle {{
        margin-top: 140px;
    }}

    .content-card {{
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px;
        padding: 16px;
        box-shadow: var(--shadow) !important;
        color: var(--text) !important;
        margin-bottom: 14px;
    }}

    .article-card {{
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px;
        padding: 14px;
        box-shadow: var(--shadow) !important;
        color: var(--text) !important;
        margin-bottom: 12px;
    }}

    .article-title {{
        color: var(--title) !important;
        font-size: 1.08rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }}

    .article-meta {{
        color: var(--muted) !important;
        font-size: 0.9rem;
        margin-bottom: 0.7rem;
    }}

    .article-desc {{
        color: var(--text) !important;
        font-size: 0.98rem;
        line-height: 1.55;
    }}

    .stTextArea textarea,
    .stTextInput input {{
        background: var(--input-bg) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
    }}

    div[data-testid="stSelectbox"] > div {{
        background: var(--widget-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }}

    div[data-testid="stSelectbox"] * {{
        color: var(--widget-text) !important;
    }}

    div[role="listbox"] {{
        background: var(--menu-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }}

    div[role="listbox"] * {{
        color: var(--menu-text) !important;
    }}

    div[role="option"] {{
        background: transparent !important;
    }}

    div[role="option"]:hover {{
        background: rgba(100, 116, 139, 0.12) !important;
    }}

    button[data-testid="stPopoverButton"] {{
        background: var(--widget-bg) !important;
        color: var(--widget-text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }}

    .stButton > button {{
        background: var(--btn-bg) !important;
        color: var(--btn-text) !important;
        border: 1px solid var(--btn-border) !important;
        border-radius: 12px !important;
    }}

    .stSlider * {{
        color: var(--text) !important;
    }}

    .stCaption {{
        color: var(--muted) !important;
    }}

    a {{
        color: #60a5fa !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HELPERS
# =========================================================
def go_back():
    st.switch_page("Home.py")


@st.cache_data(show_spinner=False, ttl=900)
def fetch_news(topic: str, sort_by: str, page_size: int):
    """
    Fetch news from NewsAPI.
    Cached for 15 minutes to reduce repeated requests.
    """
    api_key = os.environ.get("NEWS_API_KEY") or st.secrets.get("NEWS_API_KEY", "")
    if not api_key:
        raise ValueError("NEWS_API_KEY is missing. Add it in your environment variables or Streamlit secrets.")

    url = "https://newsapi.org/v2/everything"
    headers = {"X-Api-Key": api_key}
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


def build_news_prompt(topic: str, articles: list) -> str:
    """
    Build AI prompt from fetched articles.
    """
    article_blocks = []

    for idx, article in enumerate(articles, start=1):
        article_blocks.append(
            f"""
Article {idx}
Title: {article.get('title', 'N/A')}
Source: {article.get('source', {}).get('name', 'N/A')}
Published At: {article.get('publishedAt', 'N/A')}
Description: {article.get('description', 'N/A')}
Content: {article.get('content', 'N/A')}
"""
        )

    joined_articles = "\n".join(article_blocks)

    return f"""
You are a helpful AI news analyst.

Analyze the following news articles about: {topic}

Write the answer in a clear and human-friendly way.

Please include:
1. main news trend
2. key points across sources
3. overall tone of the news
4. repeated themes or major developments
5. a short conclusion

News content:
{joined_articles}
"""


def ask_groq(prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
    try:
        from groq import Groq
    except Exception:
        return "Groq package not installed. Run: pip install groq"

    api_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        return "GROQ_API_KEY is missing. Add it in your environment variables or Streamlit secrets."

    try:
        client = Groq(api_key=api_key)
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
    except Exception as e:
        return f"Error calling Groq: {e}"


def ask_huggingface(prompt: str, model_id: str, temperature: float, max_tokens: int) -> str:
    api_key = os.environ.get("HF_TOKEN") or st.secrets.get("HF_TOKEN", "")
    if not api_key:
        return "HF_TOKEN is missing. Add it in your environment variables or Streamlit secrets."

    try:
        client = InferenceClient(api_key=api_key)
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
    except Exception as e:
        return f"Error calling Hugging Face: {e}"


# =========================================================
# TOP BAR
# =========================================================
top_left, top_right = st.columns([0.75, 0.25], vertical_alignment="center")

with top_left:
    back_col, title_col = st.columns([0.16, 0.84], vertical_alignment="center")

    with back_col:
        if st.button("⬅ Back", use_container_width=True):
            go_back()

    with title_col:
        st.markdown('<div class="page-title">AI News Analyzer</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-sub">Search a topic, fetch recent articles, and get an AI-generated news analysis.</div>',
            unsafe_allow_html=True
        )

with top_right:
    with st.popover("🎨 Theme ▾", use_container_width=True):
        st.session_state.theme_name = st.selectbox(
            "Theme",
            list(THEMES.keys()),
            index=list(THEMES.keys()).index(st.session_state.theme_name),
        )

# =========================================================
# MAIN AREA
# =========================================================
left_col, right_col = st.columns([3, 1], gap="large")

with left_col:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)

    st.session_state.news_topic = st.text_input(
        "News topic",
        value=st.session_state.news_topic,
        placeholder="Example: artificial intelligence"
    )

    a, b, c = st.columns([1.2, 1, 1])

    with a:
        st.session_state.news_sort_label = st.selectbox(
            "Sort by",
            list(SORT_OPTIONS.keys()),
            index=list(SORT_OPTIONS.keys()).index(st.session_state.news_sort_label)
        )

    with b:
        st.session_state.news_page_size = st.selectbox(
            "Articles",
            [3, 5, 7, 10],
            index=[3, 5, 7, 10].index(st.session_state.news_page_size)
        )

    with c:
        st.write("")
        st.write("")
        if st.button("📰 Analyze News", use_container_width=True):
            if not st.session_state.news_topic.strip():
                st.error("Please enter a news topic.")
            else:
                try:
                    with st.spinner("Fetching latest news..."):
                        sort_by = SORT_OPTIONS[st.session_state.news_sort_label]
                        articles = fetch_news(
                            st.session_state.news_topic.strip(),
                            sort_by,
                            st.session_state.news_page_size
                        )
                        st.session_state.news_articles = articles

                    if not articles:
                        st.warning("No articles found for this topic.")
                        st.session_state.news_ai_summary = ""
                    else:
                        prompt = build_news_prompt(st.session_state.news_topic.strip(), articles)

                        with st.spinner("Generating AI analysis..."):
                            if st.session_state.news_provider == "Groq":
                                model_id = GROQ_MODELS[st.session_state.news_groq_model_name]
                                st.session_state.news_ai_summary = ask_groq(
                                    prompt=prompt,
                                    model_id=model_id,
                                    temperature=st.session_state.news_temperature,
                                    max_tokens=st.session_state.news_max_tokens
                                )
                            else:
                                model_id = HF_MODELS[st.session_state.news_hf_model_name]
                                st.session_state.news_ai_summary = ask_huggingface(
                                    prompt=prompt,
                                    model_id=model_id,
                                    temperature=st.session_state.news_temperature,
                                    max_tokens=st.session_state.news_max_tokens
                                )
                        st.rerun()

                except Exception as e:
                    st.error(f"Something went wrong: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.news_articles:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### Latest Articles")

        for article in st.session_state.news_articles:
            source_name = article.get("source", {}).get("name", "Unknown Source")
            title = article.get("title", "No title")
            description = article.get("description", "No description available.")
            published_at = article.get("publishedAt", "N/A")
            url = article.get("url", "#")

            st.markdown(
                f"""
                <div class="article-card">
                    <div class="article-title">{title}</div>
                    <div class="article-meta">Source: {source_name} | Published: {published_at}</div>
                    <div class="article-desc">{description}</div>
                    <br>
                    <a href="{url}" target="_blank">Read full article</a>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### AI News Analysis")

        if st.session_state.news_ai_summary:
            st.markdown(st.session_state.news_ai_summary)
        else:
            st.info("Your AI news analysis will appear here.")
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.info("Search for a topic to view articles and AI-generated analysis.")
        st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="right-middle">', unsafe_allow_html=True)
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)

    st.markdown("**Provider**")
    st.session_state.news_provider = st.selectbox(
        "Provider",
        PROVIDERS,
        index=PROVIDERS.index(st.session_state.news_provider),
        label_visibility="collapsed",
    )
    st.caption("Choose the AI provider for news analysis")

    st.divider()

    st.markdown("**Select Model**")
    if st.session_state.news_provider == "Groq":
        st.session_state.news_groq_model_name = st.selectbox(
            "Groq Model",
            list(GROQ_MODELS.keys()),
            index=list(GROQ_MODELS.keys()).index(st.session_state.news_groq_model_name),
            label_visibility="collapsed",
        )
        st.caption("Groq models")
    else:
        st.session_state.news_hf_model_name = st.selectbox(
            "HF Model",
            list(HF_MODELS.keys()),
            index=list(HF_MODELS.keys()).index(st.session_state.news_hf_model_name),
            label_visibility="collapsed",
        )
        st.caption("Hugging Face models")

    st.divider()

    st.markdown("**Temperature**")
    st.session_state.news_temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.news_temperature,
        step=0.1,
        label_visibility="collapsed",
    )
    st.caption(f"{st.session_state.news_temperature:.2f}")

    st.markdown("**Max tokens**")
    st.session_state.news_max_tokens = st.slider(
        "Max tokens",
        min_value=200,
        max_value=2500,
        value=st.session_state.news_max_tokens,
        step=100,
        label_visibility="collapsed",
    )
    st.caption(str(st.session_state.news_max_tokens))

    st.divider()

    if st.button("🧹 Clear News", use_container_width=True):
        st.session_state.news_topic = ""
        st.session_state.news_articles = []
        st.session_state.news_ai_summary = ""
        st.rerun()

    if st.button("🔁 Reset session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
