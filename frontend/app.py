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
from frontend.services.api import perform_ocr, fetch_history, upload_image

st.set_page_config(
    page_title="Mieru - Manga & Document OCR",
    layout="wide",
)

config = render_sidebar()

st.title("Mieru - Manga & Document OCR")

if config["navigation"] == "OCR Workspace":
    st.caption("Manga & Document OCR with Translation")
    st.subheader("Upload Image")

    # Initialize cache in session state if not present
    if "uploaded_images_cache" not in st.session_state:
        st.session_state["uploaded_images_cache"] = {}

    uploaded_files = st.file_uploader(
        "Drag and drop or browse images",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )
    st.text(' ')

    if uploaded_files:
        for f in uploaded_files:
            if f.name not in st.session_state["uploaded_images_cache"]:
                f.seek(0)
                file_bytes = f.read()
                f.seek(0)
                try:
                    img = Image.open(f).convert("RGB")
                    st.session_state["uploaded_images_cache"][f.name] = (img, file_bytes)
                except Exception as e:
                    st.error(f"Error loading {f.name}: {str(e)}")
                    continue

                state_key = f"full_image_ref_{f.name}"
                if state_key not in st.session_state:
                    try:
                        with st.spinner(f"Pre-uploading {f.name} to server..."):
                            upload_resp = upload_image(f.name, file_bytes)
                            if upload_resp.status_code == 200:
                                ref_path = upload_resp.json().get("full_image_ref", "")
                                st.session_state[state_key] = ref_path
                            else:
                                st.error(f"Failed to pre-upload {f.name}: {upload_resp.status_code}")
                    except Exception as e:
                        st.error(f"Error uploading original image {f.name}: {str(e)}")

    cached_filenames = list(st.session_state["uploaded_images_cache"].keys())
    
    if cached_filenames:
        if st.button("Clear All Uploaded Images"):
            st.session_state["uploaded_images_cache"] = {}
            st.rerun()

        image_col, select_col = st.columns([2, 2])

        image_options = [f"{i + 1}: {name}" for i, name in enumerate(cached_filenames)]

        with select_col:
            selected_idx = st.selectbox(
                "Select Image to Edit/Process",
                range(len(cached_filenames)),
                format_func=lambda i: image_options[i],
                key="image_selector",
                width="stretch"
            )

        idx = selected_idx
        selected_filename = cached_filenames[idx]
        image, file_bytes = st.session_state["uploaded_images_cache"][selected_filename]

        with image_col:
            _, center, _ = st.columns([2, 5, 2])
            with center:
                st.image(image, caption=f"Selected: {selected_filename}", width=400)

        st.divider()
        processed_image_bytes = render_image_editor(image, config, selected_filename)
        st.session_state[f"processed_image_bytes_{selected_filename}"] = processed_image_bytes

        st.divider()

        if st.button("Process Image", type="primary", key=f"process_{selected_filename}"):
            image_bytes = st.session_state.get(f"processed_image_bytes_{selected_filename}")

            if image_bytes is None:
                st.error("No processed image available.")
            else:
                with st.spinner("Processing OCR..."):
                    try:
                        # Retrieve the cached original image reference key
                        ref_key = f"full_image_ref_{selected_filename}"
                        full_image_ref = st.session_state.get(ref_key, "")

                        response = perform_ocr(
                            image_bytes=image_bytes,
                            engine=config["engine"],
                            target_lang=config["target_lang"],
                            full_image_ref=full_image_ref
                        )

                        if response.status_code == 200:
                            st.session_state[f"ocr_result_{selected_filename}"] = response.json()
                        else:
                            st.error(
                                f"Backend error ({response.status_code}): "
                                f"{response.json().get('detail', 'Unknown error')}"
                            )

                    except requests.ConnectionError:
                        st.error("Could not connect to the backend server. Make sure it's running on http://localhost:8000")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

        if f"ocr_result_{selected_filename}" in st.session_state:
            render_results(st.session_state[f"ocr_result_{selected_filename}"], config["engine"])

else:
    # Dedicated History Log View
    st.subheader("Past Operations Audit Log")
    st.caption("View and inspect past OCR processing history saved persistently.")

    try:
        response = fetch_history()
        if response.status_code == 200:
            records = response.json().get("data", [])
            if not records:
                st.info("No history logs found in the SQLite database. Switch to 'OCR Workspace' and process an image first.")
            else:
                st.dataframe(records, use_container_width=True)

                st.divider()

                st.subheader("Historical Detail Viewer")
                selected_record = st.selectbox(
                    "Select a history entry to view full details:",
                    options=records,
                    format_func=lambda r: f"ID {r['id']} | {r['filename']} | {r['engine']} | {r['timestamp']}",
                    key="history_record_selector"
                )

                if selected_record:
                    img_col, txt_col = st.columns([1, 1])

                    with img_col:
                        st.subheader("Archived Image")
                        from frontend.config import API_BASE_URL
                        img_url = f"{API_BASE_URL}/{selected_record['image_path']}"
                        st.image(img_url, use_container_width=True, caption=selected_record['filename'])

                    with txt_col:
                        st.subheader("OCR Result & Translation")
                        st.markdown(f"**Engine Used:** `{selected_record['engine']}`")
                        st.markdown(f"**Processed At:** {selected_record['timestamp']}")

                        st.text_area(
                            "Extracted Text",
                            value=selected_record['extracted_text'],
                            height=150,
                            disabled=True
                        )
                        st.text_area(
                            "Translated Text",
                            value=selected_record['translated_text'],
                            height=150,
                            disabled=True
                        )
        else:
            st.error(f"Failed to fetch history from backend. Status code: {response.status_code}")
    except requests.ConnectionError:
        st.error("Could not connect to the backend server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
