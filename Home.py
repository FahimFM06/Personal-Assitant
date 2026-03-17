import streamlit as st

st.set_page_config(page_title="AI Dashboard", page_icon="🤖", layout="wide")

THEMES = ["Cloud (Light)", "Midnight (Dark)", "Ocean (Blue)", "Mint (Calm)", "Sunset (Warm)"]

# keep selected theme
if "theme" not in st.session_state:
    st.session_state.theme = THEMES[0]

# --- Top bar (right corner controls) ---
left, right = st.columns([0.82, 0.18], vertical_alignment="center")

with left:
    st.markdown(
        '<div class="title-text">AI Research & Productivity Dashboard</div>'
        '<div class="sub-text">Select one tool from the dashboard</div>',
        unsafe_allow_html=True
    )

with right:
    # This is the "button" that opens options like your screenshot
    with st.popover("⚙️ Theme", use_container_width=True):
        st.session_state.theme = st.selectbox(
            "Select theme",
            THEMES,
            index=THEMES.index(st.session_state.theme),
            label_visibility="collapsed"
        )
        st.caption(f"Current: **{st.session_state.theme}**")

# Now use st.session_state.theme to apply your CSS theme
st.write("Selected theme:", st.session_state.theme)
