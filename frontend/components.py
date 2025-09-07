# frontend/components.py
import streamlit as st
from backend.utils import format_sources_for_display


def render_answer(answer, sources):
    st.subheader("Answer")
    st.write(answer)
    st.markdown("---")
    st.subheader("Sources / Retrieved Chunks")
    st.text(format_sources_for_display(sources))
