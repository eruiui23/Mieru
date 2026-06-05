"""Image upload, cropping, and preprocessing components."""

import io

import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
from streamlit_cropper import st_cropper

from config import CROPPER_HEIGHT, PREVIEW_HEIGHT, SUPPORTED_IMAGE_TYPES


def render_image_section(settings: dict) -> None:
    """Render the image upload, cropper, and preview section."""
    st.subheader("Upload Image")

    uploaded_files = st.file_uploader(
        "Drag and drop or browse images",
        type=SUPPORTED_IMAGE_TYPES,
        accept_multiple_files=True,
    )
    st.text(" ")
    st.text(" ")
    st.text(" ")

    if not uploaded_files:
        return

    # Row: Original image + image selector
    image_col, select_col = st.columns([2, 2])

    image_options = [f"Image {i + 1}: {f.name}" for i, f in enumerate(uploaded_files)]

    with select_col:
        selected_idx = st.selectbox(
            "Select Image",
            range(len(uploaded_files)),
            format_func=lambda i: image_options[i],
            key="image_selector",
        )

    idx = selected_idx
    uploaded_file = uploaded_files[idx]
    image = Image.open(uploaded_file).convert("RGB")

    with image_col:
        _, center, _ = st.columns([2, 5, 2])
        with center:
            st.image(image, caption="Original Image", width=400)

    # Row 2: Cropper + Processed Preview
    st.divider()
    crop_col, preview_col = st.columns([1, 1])

    with crop_col:
        cropped_image = _render_cropper(image, idx)

    with preview_col:
        _render_preview(cropped_image, idx, settings)


def _render_cropper(image: Image.Image, idx: int) -> Image.Image:
    """Render the crop tool and return the cropped image at original resolution."""
    st.caption("Drag and resize the box to select a crop region")

    ratio = CROPPER_HEIGHT / image.height
    cropper_display = image.resize(
        (int(image.width * ratio), CROPPER_HEIGHT)
    )

    crop_box = st_cropper(
        cropper_display,
        realtime_update=True,
        box_color="red",
        aspect_ratio=None,
        return_type="box",
        should_resize_image=False,
        key=f"cropper_{idx}",
    )

    # Scale crop coordinates back to original image resolution
    scale_back = 1 / ratio
    left = max(0, int(crop_box["left"] * scale_back))
    top = max(0, int(crop_box["top"] * scale_back))
    right = min(image.width, int((crop_box["left"] + crop_box["width"]) * scale_back))
    bottom = min(image.height, int((crop_box["top"] + crop_box["height"]) * scale_back))

    return image.crop((left, top, right, bottom))


def _render_preview(cropped_image: Image.Image, idx: int, settings: dict) -> None:
    """Apply image adjustments and render the processed preview."""
    preview = cropped_image

    if settings["grayscale"]:
        preview = ImageOps.grayscale(preview).convert("RGB")

    if settings["brightness"] != 1.0:
        preview = ImageEnhance.Brightness(preview).enhance(settings["brightness"])

    if settings["contrast"] != 1.0:
        preview = ImageEnhance.Contrast(preview).enhance(settings["contrast"])

    st.caption("Processed Preview")

    preview_ratio = PREVIEW_HEIGHT / preview.height
    preview_display = preview.resize(
        (int(preview.width * preview_ratio), PREVIEW_HEIGHT)
    )
    st.image(preview_display)

    # Store processed bytes for backend submission
    buffer = io.BytesIO()
    preview.save(buffer, format="PNG")
    st.session_state[f"processed_image_bytes_{idx}"] = buffer.getvalue()
