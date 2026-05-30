from fastapi import FastAPI, File, Form, UploadFile

from backend.app.schemas import ComparisonResponse, OCRResponse

app = FastAPI(title="Manga & Document OCR API Specification")


@app.get("/")
async def root():
    return {"status": "API spec is active"}


@app.post("/api/ocr", response_model=OCRResponse)
async def process_ocr(
    file: UploadFile = File(...),
    engine: str = Form(...),
    grayscale: bool = Form(False),
    brightness: float = Form(1.0),
    contrast: float = Form(1.0),
):
    # Mocking the single OCR engine process
    return OCRResponse(
        filename=file.filename or "unknown_image.jpg",
        engine=engine,
        extracted_text="こんにちは。これは仕様駆動開発のサンプルです。",
        translated_text="Hello. This is a sample of spec-driven development.",
        execution_time_ms=120.5,
    )


@app.post("/api/ocr/compare", response_model=ComparisonResponse)
async def compare_ocr(
    file: UploadFile = File(...),
    grayscale: bool = Form(False),
    brightness: float = Form(1.0),
    contrast: float = Form(1.0),
):
    # Mocking side-by-side comparison behavior
    mock_results = [
        OCRResponse(
            filename=file.filename or "unknown_image.jpg",
            engine="Manga-OCR",
            extracted_text="こんにちは。",
            translated_text="Hello.",
            execution_time_ms=95.0,
        ),
        OCRResponse(
            filename=file.filename or "unknown_image.jpg",
            engine="Tesseract OCR",
            extracted_text="ニんにちは。",
            translated_text="Ni nichi wa.",
            execution_time_ms=45.2,
        ),
    ]
    return ComparisonResponse(
        filename=file.filename or "unknown_image.jpg",
        engines_evaluated=["Manga-OCR", "Tesseract OCR"],
        results=mock_results,
    )
