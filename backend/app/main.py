import asyncio
from io import BytesIO

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

# Import your newly created modules
from backend.app.models.schemas import ComparisonResponse, OCRResponse
from backend.app.services.ocr_strategy import OCRContext
from backend.app.services.translation import translate_text

app = FastAPI(title="Manga & Document OCR Application API")

# Add CORS Middleware to allow Streamlit (usually running on port 8501) to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate the OCR Context (this loads the heavy models once on startup)
ocr_context = OCRContext()


@app.get("/")
async def root():
    return {"status": "OCR Backend API is active"}


@app.post("/api/ocr", response_model=OCRResponse)
async def process_ocr(
    file: UploadFile = File(...),
    engine: str = Form(...),
    target_lang: str = Form("en"),
):
    # 1. Validate File Type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    try:
        # 2. Read file bytes into memory
        image_bytes = await file.read()

        # 3. Load image directly using Pillow
        image = Image.open(BytesIO(image_bytes))

        # 4. Execute the specific OCR Engine
        extracted_text, latency_ms = ocr_context.execute_strategy(
            engine, image
        )

        # 5. Translate the result
        translated_text = await translate_text(extracted_text, target_lang)

        return OCRResponse(
            filename=file.filename or "unknown",
            engine=engine,
            extracted_text=extracted_text,
            translated_text=translated_text,
            execution_time_ms=latency_ms,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        # Crucial: Clean up the file stream to prevent memory leaks
        await file.close()


@app.post("/api/ocr/compare", response_model=ComparisonResponse)
async def compare_ocr(
    file: UploadFile = File(...),
    target_lang: str = Form("en"),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    try:
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes))

        results = []

        # Helper function to run a single engine concurrently
        async def run_engine(engine_name: str):
            # execute_strategy is synchronous, so we run it in a threadpool to not block FastAPI
            loop = asyncio.get_running_loop()
            extracted_text, latency = await loop.run_in_executor(
                None, ocr_context.execute_strategy, engine_name, image
            )
            translated_text = await translate_text(extracted_text, target_lang)

            return OCRResponse(
                filename=file.filename or "unknown",
                engine=engine_name,
                extracted_text=extracted_text,
                translated_text=translated_text,
                execution_time_ms=latency,
            )

        # Run all available engines concurrently using asyncio.gather
        tasks = [run_engine(engine_name) for engine_name in ocr_context.engines.keys()]
        results = await asyncio.gather(*tasks)

        return ComparisonResponse(
            filename=file.filename or "unknown",
            engines_evaluated=list(ocr_context.engines.keys()),
            results=results,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Comparison processing failed: {str(e)}"
        )
    finally:
        await file.close()
