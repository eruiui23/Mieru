import cv2
import numpy as np
from PIL import Image


def process_image(
    image_bytes: bytes, grayscale: bool, brightness: float, contrast: float
) -> Image.Image:
    """
    Decodes raw image bytes, applies OpenCV transformations,
    and returns a PIL Image ready for the OCR engines.
    """
    # 1. Convert raw bytes to a NumPy array for OpenCV
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # ADD THIS GUARD CLAUSE: Satisfies the type checker and prevents runtime crashes
    if img is None:
        raise ValueError(
            "Failed to decode image bytes. The file might be corrupted or unsupported."
        )

    # 2. Apply Grayscale if requested
    if grayscale:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Convert back to BGR so the matrix shape remains consistent for subsequent operations
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # 3. Apply Brightness and Contrast
    # OpenCV uses the formula: new_image = (old_image * alpha) + beta
    # Where alpha is contrast (1.0 = normal) and beta is brightness (0 = normal)
    alpha = contrast
    beta = brightness * 50.0  # Scale up slightly for visible effect

    adjusted_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

    # 4. Convert back to RGB format for Pillow (since OCR engines prefer PIL)
    adjusted_img_rgb = cv2.cvtColor(adjusted_img, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(adjusted_img_rgb)

    return pil_image
