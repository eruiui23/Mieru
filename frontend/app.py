import os
import sys

# Ensure project root is in sys.path to resolve absolute imports correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import requests
import streamlit as st
from PIL import Image

from frontend.components.sidebar import render_sidebar
from frontend.components.image_editor import render_image_editor
from frontend.components.results import render_results
from frontend.services.api import perform_ocr

# Page configuration setup
st.set_page_config(
    page_title="Mieru - Manga & Document OCR",
    layout="wide",
)

# Render configuration sidebar
config = render_sidebar()

# Main page headers
st.title("Welcome to Mieru")
st.caption("Manga & Document OCR with Translation")

st.subheader("Upload Image")

uploaded_files = st.file_uploader(
    "Drag and drop or browse images",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
)
st.text(' ')
st.text(' ')
st.text(' ')

if uploaded_files:
    # Row: Selectbox on left, Original image on right
    image_col, select_col = st.columns([2, 2])

    image_options = [f"Image {i + 1}: {f.name}" for i, f in enumerate(uploaded_files)]

    with select_col:
        selected_idx = st.selectbox(
            "Select Image",
            range(len(uploaded_files)),
            format_func=lambda i: image_options[i],
            key="image_selector",
            width="stretch"
        )

    idx = selected_idx
    uploaded_file = uploaded_files[idx]
    image = Image.open(uploaded_file).convert("RGB")

    with image_col:
        _, center, _ = st.columns([2, 5, 2])
        with center:
            st.image(image, caption="Original Image", width=400)

    # Row 2: Cropper + Processed Preview side by side
    st.divider()
    processed_image_bytes = render_image_editor(image, config, idx)
    st.session_state[f"processed_image_bytes_{idx}"] = processed_image_bytes

    # Row 3: Process Button & Results
    st.divider()

    if st.button("Process Image", type="primary", key=f"process_{idx}"):
        image_bytes = st.session_state.get(f"processed_image_bytes_{idx}")

        if image_bytes is None:
            st.error("No processed image available.")
        else:
            with st.spinner("Processing OCR..."):
                try:
                    response = perform_ocr(
                        image_bytes=image_bytes,
                        engine=config["engine"],
                        target_lang=config["target_lang"]
                    )

                    if response.status_code == 200:
                        st.session_state[f"ocr_result_{idx}"] = response.json()
                    else:
                        st.error(
                            f"Backend error ({response.status_code}): "
                            f"{response.json().get('detail', 'Unknown error')}"
                        )

                except requests.ConnectionError:
                    st.error("Could not connect to the backend server. Make sure it's running on http://localhost:8000")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    # Display results
    if f"ocr_result_{idx}" in st.session_state:
        render_results(st.session_state[f"ocr_result_{idx}"], config["engine"])
