import streamlit as st
from PIL import Image, ImageEnhance
from streamlit_cropper import st_cropper


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

# ─────────────────────────────────────────────
# Main Content Area
# ─────────────────────────────────────────────
st.title("Welcome to Mieru")
st.caption("Manga & Document OCR with Translation")

# ─────────────────────────────────────────────
# Row 1: Image Upload, Cropper, and Preview
# ─────────────────────────────────────────────
st.subheader("Upload Image")

uploaded_file = st.file_uploader(
    "Drag and drop or browse an image",
    type=["png", "jpg", "jpeg"],
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

    # Row 1: Full original image (full width)
    st.image(image, caption="Original Image", width=400)

    # Row 2: Cropper + Processed Preview side by side
    st.divider()
    crop_col, preview_col = st.columns([1, 1])

    with crop_col:
        st.caption("Drag and resize the box to select a crop region")
        cropped_image = st_cropper(
            image,
            realtime_update=True,
            box_color="red",
            aspect_ratio=None,
            return_type="image",
            
        )

    with preview_col:
        preview = cropped_image

        if grayscale:
            preview = preview.convert("L").convert("RGB")

        if brightness != 1.0:
            preview = ImageEnhance.Brightness(preview).enhance(brightness)

        if contrast != 1.0:
            preview = ImageEnhance.Contrast(preview).enhance(contrast)

        st.subheader("Processed Preview")
        st.image(preview, use_container_width=True)

    # ─────────────────────────────────────────────
    # Row 3: Translation Results
    # ─────────────────────────────────────────────
    st.divider()
    st.subheader("Results")
    # tempat hasil
