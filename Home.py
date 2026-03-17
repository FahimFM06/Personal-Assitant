import streamlit as st

THEMES = ["Cloud (Light)", "Midnight (Dark)", "Ocean (Blue)", "Mint (Calm)", "Sunset (Warm)"]

if "theme" not in st.session_state:
    st.session_state.theme = THEMES[0]
if "show_theme" not in st.session_state:
    st.session_state.show_theme = False

left, right = st.columns([0.82, 0.18], vertical_alignment="center")

with left:
    st.markdown(
        '<div class="title-text">AI Research & Productivity Dashboard</div>'
        '<div class="sub-text">Select one tool from the dashboard</div>',
        unsafe_allow_html=True
    )

with right:
    if st.button("⚙️ Theme", use_container_width=True):
        st.session_state.show_theme = not st.session_state.show_theme

    if st.session_state.show_theme:
        st.session_state.theme = st.selectbox(
            "Theme",
            THEMES,
            index=THEMES.index(st.session_state.theme),
            label_visibility="collapsed"
        )
