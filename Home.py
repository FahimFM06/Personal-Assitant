import streamlit as st

st.set_page_config(page_title="AI Dashboard", page_icon="🤖", layout="wide")

# -----------------------------
# Page style
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
.title-text {
    font-size: 42px;
    font-weight: 800;
    color: white;
    text-align: center;
    margin-bottom: 8px;
}
.sub-text {
    font-size: 18px;
    color: #d9d9d9;
    text-align: center;
    margin-bottom: 30px;
}
.card-box {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    padding: 24px 18px;
    border-radius: 22px;
    text-align: center;
    color: white;
    min-height: 120px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.20);
}
div.stButton > button {
    width: 100%;
    border-radius: 14px;
    height: 48px;
    font-size: 16px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">AI Research & Productivity Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Select one tool from the dashboard</div>', unsafe_allow_html=True)

topics = [
    "AI Research & Study Q&A",
    "Research Paper Summarizer",
    "Math & Statistics Solver",
    "AI Coding Assistant",
    "Weather Information",
    "Smart Location Finder",
    "News & AI Trend Analyzer"
]

# First row
row1 = st.columns(4)
for i in range(4):
    with row1[i]:
        st.markdown(f'<div class="card-box">{topics[i]}</div>', unsafe_allow_html=True)

        # Only connect the summarizer page for now
        if topics[i] == "Research Paper Summarizer":
            if st.button("Open", key=f"open_{i}"):
                st.switch_page("pages/2_Research_Paper_Summarizer.py")
        else:
            st.button("Open", key=f"open_{i}", disabled=True)

# Second row
row2 = st.columns(3)
for i in range(4, 7):
    with row2[i - 4]:
        st.markdown(f'<div class="card-box">{topics[i]}</div>', unsafe_allow_html=True)
        st.button("Open", key=f"open_{i}", disabled=True)

st.info("For now, only the Research Paper Summarizer page is active.")
