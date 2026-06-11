import io
import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
from streamlit_cropper import st_cropper

def render_image_editor(image: Image.Image, config: dict, idx: int) -> bytes:
    """
    Renders the cropping tool and processed preview side by side.
    Applies grayscale, brightness, and contrast adjustments.

    Args:
        image (Image.Image): The original PIL Image to be cropped/processed.
        config (dict): Adjustment configuration (grayscale, brightness, contrast).
        idx (int): Index of the current active image (used to generate unique keys).

    Returns:
        bytes: The processed cropped image as PNG bytes.
    """
    crop_col, preview_col = st.columns([1, 1])

    with crop_col:
        st.caption("Drag and resize the box to select a crop region")

        # Resize image to a fixed height for the cropper display
        CROPPER_HEIGHT = 500
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
        left = int(crop_box["left"] * scale_back)
        top = int(crop_box["top"] * scale_back)
        right = int((crop_box["left"] + crop_box["width"]) * scale_back)
        bottom = int((crop_box["top"] + crop_box["height"]) * scale_back)

        left = max(0, left)
        top = max(0, top)
        right = min(image.width, right)
        bottom = min(image.height, bottom)

        cropped_image = image.crop((left, top, right, bottom))

    with preview_col:
        preview = cropped_image

        if config.get("grayscale", False):
            preview = ImageOps.grayscale(preview).convert("RGB")

        brightness = config.get("brightness", 1.0)
        if brightness != 1.0:
            preview = ImageEnhance.Brightness(preview).enhance(brightness)

        contrast = config.get("contrast", 1.0)
        if contrast != 1.0:
            preview = ImageEnhance.Contrast(preview).enhance(contrast)

        st.caption("Processed Preview")

        PREVIEW_HEIGHT = 500
        preview_ratio = PREVIEW_HEIGHT / preview.height
        preview_display = preview.resize(
            (int(preview.width * preview_ratio), PREVIEW_HEIGHT)
        )
        st.image(preview_display)

        buffer = io.BytesIO()
        preview.save(buffer, format="PNG")
        return buffer.getvalue()
