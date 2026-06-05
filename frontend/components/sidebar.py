import streamlit as st

def render_sidebar() -> dict:
    """
    Renders the configuration widgets in the Streamlit sidebar.

    Returns:
        dict: A dictionary of configuration options:
            - engine (str): Selected OCR Engine.
            - grayscale (bool): Whether grayscale is enabled.
            - brightness (float): Brightness slider value.
            - contrast (float): Contrast slider value.
            - target_lang (str): Selected target translation language.
    """
    with st.sidebar:
        st.header("Configuration")

        # OCR Engine Selector
        engine = st.selectbox(
            "OCR Engine",
            options=["manga_ocr", "tesseract", "easyocr", "compare"],
            format_func=lambda x: {
                "manga_ocr": "Manga-OCR (Japanese)",
                "tesseract": "Tesseract",
                "easyocr": "EasyOCR",
                "compare": "Run All (Compare)",
            }[x],
        )

        st.divider()

        # Image Manipulation Controls
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

        # Target Language Selector
        target_lang = st.selectbox(
            "Translate To",
            options=["en", "id"],
            format_func=lambda x: {
                "en": "English",
                "id": "Bahasa Indonesia",
            }[x],
        )

    return {
        "engine": engine,
        "grayscale": grayscale,
        "brightness": brightness,
        "contrast": contrast,
        "target_lang": target_lang,
    }
