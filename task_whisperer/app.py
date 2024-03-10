import streamlit as st

from task_whisperer.src.streamlit_utils.sidebar import render_sidebar

if __name__ == "__main__":
    st.set_page_config(page_title="Main", page_icon="👋", layout="wide")
    st.title("🐎 Task Whisperer")

    sidebar_config = render_sidebar()
