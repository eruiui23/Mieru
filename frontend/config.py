"""Application configuration constants."""

API_BASE_URL = "http://localhost:8000"

CROPPER_HEIGHT = 500
PREVIEW_HEIGHT = 500

ENGINE_OPTIONS = ["manga_ocr", "tesseract", "easyocr", "compare"]
ENGINE_LABELS = {
    "manga_ocr": "Manga-OCR (Japanese)",
    "tesseract": "Tesseract",
    "easyocr": "EasyOCR",
    "compare": "Run All (Compare)",
}

LANGUAGE_OPTIONS = ["en", "id"]
LANGUAGE_LABELS = {
    "en": "English",
    "id": "Bahasa Indonesia",
}

SUPPORTED_IMAGE_TYPES = ["png", "jpg", "jpeg"]
