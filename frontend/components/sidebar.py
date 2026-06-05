"""Sidebar configuration panel."""

import streamlit as st

from config import ENGINE_LABELS, ENGINE_OPTIONS, LANGUAGE_LABELS, LANGUAGE_OPTIONS


def render_sidebar() -> dict:
    """Render the sidebar and return user-selected configuration values."""
    with st.sidebar:
        st.header("Configuration")

        engine = st.selectbox(
            "OCR Engine",
            options=ENGINE_OPTIONS,
            format_func=lambda x: ENGINE_LABELS[x],
        )

        st.divider()

        st.subheader("Image Adjustments")

        grayscale = st.checkbox("Grayscale", value=False)

        brightness = st.slider(
            "Brightness",
            min_value=0.0,
            max_value=3.0,
            value=1.0,
            step=0.1,
        )

        contrast = st.slider(
            "Contrast",
            min_value=0.0,
            max_value=3.0,
            value=1.0,
            step=0.1,
        )

        st.divider()

        target_lang = st.selectbox(
            "Translate To",
            options=LANGUAGE_OPTIONS,
            format_func=lambda x: LANGUAGE_LABELS[x],
        )

    return {
        "engine": engine,
        "grayscale": grayscale,
        "brightness": brightness,
        "contrast": contrast,
        "target_lang": target_lang,
    }
