import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="نظام التسعير الكهربائي",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit chrome to give the React app full space
st.markdown("""
<style>
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
    .stApp { overflow: hidden; }
</style>
""", unsafe_allow_html=True)

html_path = Path(__file__).parent / "pricing-app.html"
html_content = html_path.read_text(encoding="utf-8")

components.html(html_content, height=1200, scrolling=True)
