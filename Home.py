import streamlit as st

st.set_page_config(page_title="AI Dashboard", page_icon="🤖", layout="wide")

# --------------------------
# Custom dashboard style
# --------------------------
st.markdown("""
<style>

.main {
    background: linear-gradient(135deg,#04151f,#12061d);
}

.card {
    background: rgba(255,255,255,0.08);
    border-radius:20px;
    padding:40px 20px;
    text-align:center;
    cursor:pointer;
    transition:0.3s;
    box-shadow:0 8px 25px rgba(0,0,0,0.2);
}

.card:hover{
    transform:scale(1.05);
    background:rgba(255,255,255,0.12);
}

.icon{
    font-size:40px;
}

.title{
    font-size:20px;
    font-weight:600;
    color:white;
    margin-top:10px;
}

</style>
""", unsafe_allow_html=True)

st.title("AI Research & Productivity Dashboard")

st.write("Select one tool from the dashboard")

# --------------------------
# First Row
# --------------------------

col1,col2,col3,col4 = st.columns(4)

# -------- AI Q&A ----------
with col1:
    if st.button("🤖💬\nAI Research Study QA",use_container_width=True):
        st.switch_page("pages/1_AI_Research_Study_QA.py")

# -------- Summarizer -------
with col2:
    if st.button("📄🧠\nResearch Paper Summarizer",use_container_width=True):
        st.switch_page("pages/2_Research_Paper_Summarizer.py")

# other placeholders
with col3:
    st.button("📊\nMath & Statistics Solver", disabled=True,use_container_width=True)

with col4:
    st.button("💻\nAI Coding Assistant", disabled=True,use_container_width=True)

# --------------------------
# Second Row
# --------------------------

col5,col6,col7 = st.columns(3)

with col5:
    st.button("🌦\nWeather Information",disabled=True,use_container_width=True)

with col6:
    st.button("📍\nSmart Location Finder",disabled=True,use_container_width=True)

with col7:
    st.button("📰\nAI News Analyzer",disabled=True,use_container_width=True)
