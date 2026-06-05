"""Mieru - Manga & Document OCR with Translation (Streamlit Frontend)."""

import streamlit as st

from components.sidebar import render_sidebar
from components.image_processor import render_image_section
from components.results import render_results

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Mieru - Manga & Document OCR",
    layout="wide",
)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
settings = render_sidebar()

# ─────────────────────────────────────────────
# Main Content
# ─────────────────────────────────────────────
st.title("Welcome to Mieru")
st.caption("Manga & Document OCR with Translation")

render_image_section(settings)
render_results(settings)
