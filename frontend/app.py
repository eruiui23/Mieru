import streamlit as st
from PIL import Image


st.set_page_config(
    page_title="Mieru - Manga & Document OCR",
    layout="wide",
)


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



    # Target Language Selector
    target_lang = st.selectbox(
        "Translate To",
        options=["en", "id"],
        format_func=lambda x: {
            "en": "English",
            "id": "Bahasa Indonesia",
 
        }[x],
    )

# ─────────────────────────────────────────────
# Main Content Area
# ─────────────────────────────────────────────
st.title("Welcome to Mieru")
st.caption("Manga & Document OCR with Translation")

# Two-column layout: Left = Input/Preview, Right = Output
left_col, right_col = st.columns([1, 1])


with left_col:
    st.subheader("Upload Image")

    uploaded_file = st.file_uploader(
        "Drag and drop or browse an image",
        type=["png", "jpg", "jpeg"],
    )

    if uploaded_file is not None:
        # Load and display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)


with right_col:
    st.subheader("Results")
    # tempat hasil
