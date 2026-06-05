"""Backend API client for OCR requests."""

import requests

from config import API_BASE_URL


def process_single(image_bytes: bytes, engine: str, target_lang: str) -> dict:
    """Send image to single-engine OCR endpoint."""
    response = requests.post(
        f"{API_BASE_URL}/api/ocr",
        files={"file": ("image.png", image_bytes, "image/png")},
        data={
            "engine": engine,
            "target_lang": target_lang,
        },
    )
    response.raise_for_status()
    return response.json()


def process_compare(image_bytes: bytes, target_lang: str) -> dict:
    """Send image to comparison OCR endpoint (all engines)."""
    response = requests.post(
        f"{API_BASE_URL}/api/ocr/compare",
        files={"file": ("image.png", image_bytes, "image/png")},
        data={"target_lang": target_lang},
    )
    response.raise_for_status()
    return response.json()
