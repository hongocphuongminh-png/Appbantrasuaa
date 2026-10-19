import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(page_title="Trà sữa của Pminh", page_icon="🧋", layout="wide")
st.markdown(
    "<style>header{visibility:hidden}.block-container{padding:0!important}</style>",
    unsafe_allow_html=True,
)

html = Path(__file__).parent.joinpath("tra-sua-pminh.html").read_text(encoding="utf-8")
components.html(html, height=2800, scrolling=True)
