import requests
from frontend.config import API_BASE_URL

def upload_image(filename: str, image_bytes: bytes) -> requests.Response:
    """
    Uploads the original image to the backend to get a persistent reference path.
    """
    url = f"{API_BASE_URL}/api/upload"
    return requests.post(
        url,
        files={"file": (filename, image_bytes, "image/png")}
    )

def perform_ocr(image_bytes: bytes, engine: str, target_lang: str, full_image_ref: str = "") -> requests.Response:
    """
    Sends the processed image bytes to the backend OCR APIs.

    Args:
        image_bytes: Raw bytes of the image to be processed (expected in PNG format).
        engine: The OCR engine identifier (e.g., 'manga_ocr', 'tesseract', 'easyocr', or 'compare').
        target_lang: The target translation language code ('en' or 'id').
        full_image_ref: String identifier referencing the pre-uploaded original image.

    Returns:
        requests.Response: The HTTP response from the backend.
    """
    if engine == "compare":
        url = f"{API_BASE_URL}/api/ocr/compare"
        data = {"target_lang": target_lang, "full_image_ref": full_image_ref}
    else:
        url = f"{API_BASE_URL}/api/ocr"
        data = {
            "engine": engine,
            "target_lang": target_lang,
            "full_image_ref": full_image_ref,
        }

    return requests.post(
        url,
        files={"file": ("image.png", image_bytes, "image/png")},
        data=data,
    )


def fetch_history() -> requests.Response:
    """
    Fetches the OCR history from the backend.
    """
    url = f"{API_BASE_URL}/api/history"
    return requests.get(url)

