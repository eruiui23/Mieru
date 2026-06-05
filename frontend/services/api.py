import requests
from frontend.config import API_BASE_URL

def perform_ocr(image_bytes: bytes, engine: str, target_lang: str) -> requests.Response:
    """
    Sends the processed image bytes to the backend OCR APIs.

    Args:
        image_bytes: Raw bytes of the image to be processed (expected in PNG format).
        engine: The OCR engine identifier (e.g., 'manga_ocr', 'tesseract', 'easyocr', or 'compare').
        target_lang: The target translation language code ('en' or 'id').

    Returns:
        requests.Response: The HTTP response from the backend.
    """
    if engine == "compare":
        url = f"{API_BASE_URL}/api/ocr/compare"
        data = {"target_lang": target_lang}
    else:
        url = f"{API_BASE_URL}/api/ocr"
        data = {
            "engine": engine,
            "target_lang": target_lang,
        }

    return requests.post(
        url,
        files={"file": ("image.png", image_bytes, "image/png")},
        data=data,
    )
