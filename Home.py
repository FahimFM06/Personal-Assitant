import streamlit as st

st.set_page_config(page_title="AI Dashboard", page_icon="🤖", layout="wide")

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

.title-text {
    font-size: 2.7rem;
    font-weight: 800;
    color: #0f172a;
    text-align: center;
    margin-bottom: 0.4rem;
}

.sub-text {
    font-size: 1.05rem;
    color: #64748b;
    text-align: center;
    margin-bottom: 2rem;
}

.card-btn button {
    height: 150px !important;
    border-radius: 22px !important;
    border: 1px solid #e5e7eb !important;
    background: white !important;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08) !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #111827 !important;
    white-space: pre-line !important;
}

.card-btn button:hover {
    border: 1px solid #cbd5e1 !important;
    box-shadow: 0 14px 34px rgba(15, 23, 42, 0.12) !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">AI Research & Productivity Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Select one tool from the dashboard</div>', unsafe_allow_html=True)

def go_to(page_path: str):
    try:
        st.switch_page(page_path)
    except Exception:
        st.error(f"Page not found: {page_path}")
        st.stop()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("🤖💬\nAI Research Study QA", use_container_width=True, key="qa"):
        go_to("pages/1_AI_Research_Study_QA.py")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("📄🧠\nResearch Paper Summarizer", use_container_width=True, key="summ"):
        go_to("pages/2_Research_Paper_Summarizer.py")
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("📊➗\nMath & Statistics Solver", use_container_width=True, key="math"):
        go_to("pages/3_Math_Statistics_Solver.py")
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("💻🧠\nAI Coding Assistant", use_container_width=True, key="code"):
        go_to("pages/4_AI_Coding_Assistant.py")
    st.markdown('</div>', unsafe_allow_html=True)

c5, c6, c7 = st.columns(3)

with c5:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    if st.button("🌦️📍\nWeather Information", use_container_width=True, key="weather"):
        go_to("pages/5_Weather_Information.py")
    st.markdown('</div>', unsafe_allow_html=True)

with c6:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    st.button("📍\nSmart Location Finder", use_container_width=True, key="location", disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c7:
    st.markdown('<div class="card-btn">', unsafe_allow_html=True)
    st.button("📰\nAI News Analyzer", use_container_width=True, key="news", disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.info("Active pages: Q&A, Research Paper Summarizer, Math & Statistics Solver, AI Coding Assistant, and Weather Information.")
