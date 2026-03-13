import streamlit as st

st.set_page_config(page_title="AI Dashboard", page_icon="🤖", layout="wide")

# -----------------------------
# Simple custom CSS for card UI
# -----------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #04151f, #12061d);
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.big-title {
    font-size: 42px;
    font-weight: 700;
    color: white;
    text-align: center;
    margin-bottom: 10px;
}
.sub-text {
    font-size: 18px;
    color: #d9d9d9;
    text-align: center;
    margin-bottom: 30px;
}
.card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    padding: 28px 20px;
    border-radius: 22px;
    text-align: center;
    color: white;
    box-shadow: 0 8px 30px rgba(0,0,0,0.20);
    min-height: 120px;
}
div.stButton > button {
    width: 100%;
    border-radius: 16px;
    height: 52px;
    font-size: 18px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">AI Research & Productivity Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Choose one module from the dashboard</div>', unsafe_allow_html=True)

topics = [
    "AI Research & Study Q&A",
    "Research Paper Summarizer",
    "Math & Statistics Solver",
    "AI Coding Assistant",
    "Weather Information",
    "Smart Location Finder",
    "News & AI Trend Analyzer"
]

# 4 cards in first row
cols1 = st.columns(4)
for i in range(4):
    with cols1[i]:
        st.markdown(f'<div class="card">{topics[i]}</div>', unsafe_allow_html=True)
        if i == 0:
            if st.button(f"Open {i+1}", key=f"btn_{i}"):
                st.switch_page("pages/1_AI_Research_Study_QA.py")
        else:
            st.button(f"Open {i+1}", key=f"btn_{i}", disabled=True)

# 3 cards in second row
cols2 = st.columns(3)
for i in range(4, 7):
    with cols2[i - 4]:
        st.markdown(f'<div class="card">{topics[i]}</div>', unsafe_allow_html=True)
        st.button(f"Open {i+1}", key=f"btn_{i}", disabled=True)

st.info("For now, only the 'AI Research & Study Q&A' page is connected.")
