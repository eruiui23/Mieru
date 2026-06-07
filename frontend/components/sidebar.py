import streamlit as st

def render_sidebar() -> dict:
    """
    Renders the navigation and configuration widgets in the Streamlit sidebar.

    Returns:
        dict: A dictionary of configuration options:
            - navigation (str): Active view state ("OCR Workspace" or "View History Log").
            - engine (str): Selected OCR Engine.
            - grayscale (bool): Whether grayscale is enabled.
            - brightness (float): Brightness slider value.
            - contrast (float): Contrast slider value.
            - target_lang (str): Selected target translation language.
    """
    with st.sidebar:
        st.header("Mieru Menu")
        navigation = st.radio(
            "Navigation",
            options=["OCR Workspace", "View History Log"],
            key="nav_state_radio",
        )

        st.divider()

        # Defaults for when navigation is set to "View History Log"
        engine = "manga_ocr"
        grayscale = False
        brightness = 1.0
        contrast = 1.0
        target_lang = "en"

        if navigation == "OCR Workspace":
            st.subheader("Engine & Language")
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
        "navigation": navigation,
        "engine": engine,
        "grayscale": grayscale,
        "brightness": brightness,
        "contrast": contrast,
        "target_lang": target_lang,
    }
