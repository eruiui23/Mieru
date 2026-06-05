import io

import pandas as pd
import requests
import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
from streamlit_cropper import st_cropper

# Backend API URL
API_BASE_URL = "http://localhost:8000"


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
    st.caption("Original Image")
    image = Image.open(uploaded_file).convert("RGB")

    # Row 1: Full original image (full width)
    st.image(image, width=400)

    # Row 2: Cropper + Processed Preview side by side
    st.divider()
    crop_col, preview_col = st.columns([1, 1])

    with crop_col:
        st.caption("Drag and resize the box to select a crop region")

        # Resize image to a fixed height for the cropper display
        CROPPER_HEIGHT = 500
        ratio = CROPPER_HEIGHT / image.height
        cropper_display = image.resize(
            (int(image.width * ratio), CROPPER_HEIGHT)
        )

        cropped_image = st_cropper(
            cropper_display,
            realtime_update=True,
            box_color="red",
            aspect_ratio=None,
            return_type="image",
            should_resize_image=False,
        )

    with preview_col:
        preview = cropped_image

        if grayscale:
            preview = ImageOps.grayscale(preview).convert("RGB")

        if brightness != 1.0:
            preview = ImageEnhance.Brightness(preview).enhance(brightness)

        if contrast != 1.0:
            preview = ImageEnhance.Contrast(preview).enhance(contrast)

        st.caption("Processed Preview")

        # Fixed height container for the preview
        PREVIEW_HEIGHT = 500
        preview_ratio = PREVIEW_HEIGHT / preview.height
        preview_display = preview.resize(
            (int(preview.width * preview_ratio), PREVIEW_HEIGHT)
        )
        st.image(preview_display)

        # Convert processed image to PNG bytes for backend submission
        buffer = io.BytesIO()
        preview.save(buffer, format="PNG")
        st.session_state["processed_image_bytes"] = buffer.getvalue()

    # ─────────────────────────────────────────────
    # Row 3: Process Button & Results
    # ─────────────────────────────────────────────
    st.divider()

    if st.button("Process Image", type="primary"):
        image_bytes = st.session_state.get("processed_image_bytes")

        if image_bytes is None:
            st.error("No processed image available.")
        else:
            with st.spinner("Processing OCR..."):
                try:
                    if engine == "compare":
                        # Compare mode - send to /api/ocr/compare
                        response = requests.post(
                            f"{API_BASE_URL}/api/ocr/compare",
                            files={"file": ("image.png", image_bytes, "image/png")},
                            data={"target_lang": target_lang},
                        )
                    else:
                        # Single engine mode - send to /api/ocr
                        response = requests.post(
                            f"{API_BASE_URL}/api/ocr",
                            files={"file": ("image.png", image_bytes, "image/png")},
                            data={
                                "engine": engine,
                                "target_lang": target_lang,
                            },
                        )

                    if response.status_code == 200:
                        st.session_state["ocr_result"] = response.json()
                    else:
                        st.error(f"Backend error ({response.status_code}): {response.json().get('detail', 'Unknown error')}")

                except requests.ConnectionError:
                    st.error("Could not connect to the backend server. Make sure it's running on http://localhost:8000")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    # Display results
    st.subheader("Results")

    if "ocr_result" in st.session_state:
        result = st.session_state["ocr_result"]

        if engine == "compare":
            # ─────────────────────────────────────────
            # Comparison Mode View
            # ─────────────────────────────────────────
            results_list = result.get("results", [])
            if results_list:
                # Side-by-side results grid
                cols = st.columns(len(results_list))
                for i, r in enumerate(results_list):
                    with cols[i]:
                        st.markdown(f"**{r['engine']}**")
                        st.caption(f"{r['execution_time_ms']} ms")
                        st.markdown("Extracted Text:")
                        st.code(r["extracted_text"], language=None)
                        st.markdown("Translated Text:")
                        st.code(r["translated_text"], language=None)

                # Latency bar chart
                st.markdown("**Performance Comparison**")

                chart_data = pd.DataFrame({
                    "Engine": [r["engine"] for r in results_list],
                    "Latency (ms)": [r["execution_time_ms"] for r in results_list],
                })
                st.bar_chart(chart_data, x="Engine", y="Latency (ms)")
        else:
            # ─────────────────────────────────────────
            # Single Mode View
            # ─────────────────────────────────────────
            st.caption(f"Engine: **{result.get('engine')}** | {result.get('execution_time_ms')} ms")

            text_col, translation_col = st.columns([1, 1])

            with text_col:
                st.markdown("**Extracted Text**")
                st.code(result.get("extracted_text", ""), language=None)

            with translation_col:
                st.markdown("**Translated Text**")
                st.code(result.get("translated_text", ""), language=None)
