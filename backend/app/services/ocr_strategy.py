import asyncio
import time
from abc import ABC, abstractmethod

from PIL import Image


# ---------------------------------------------------------
# 1. The Abstract Base Class (The Interface)
# ---------------------------------------------------------
class OCREngine(ABC):
    @abstractmethod
    def extract_text(self, image: Image.Image) -> str:
        """
        Takes a processed PIL Image and returns the extracted text string.
        Must be implemented by all subclasses.
        """
        pass


# ---------------------------------------------------------
# 2. Concrete Strategy A: Manga-OCR
# ---------------------------------------------------------
class MangaOCRStrategy(OCREngine):
    def __init__(self):
        print("Initializing Manga-OCR Model (This takes a moment)...")
        from manga_ocr import MangaOcr

        self.mocr = MangaOcr()

    def extract_text(self, image: Image.Image) -> str:
        return self.mocr(image)


# ---------------------------------------------------------
# 3. Concrete Strategy B: Tesseract (Simulation for now)
# ---------------------------------------------------------
class TesseractStrategy(OCREngine):
    def __init__(self):
        print("Initializing Tesseract Engine...")
        # import pytesseract

    def extract_text(self, image: Image.Image) -> str:
        # return pytesseract.image_to_string(image)
        time.sleep(0.5)  # Simulate processing time
        return "Tesseract simulation: Extracted text goes here."


# ---------------------------------------------------------
# 4. The Context / Factory
# ---------------------------------------------------------
class OCRContext:
    def __init__(self):
        # We instantiate the models once when the server starts to save time
        self.engines = {
            "manga_ocr": MangaOCRStrategy(),
            "tesseract": TesseractStrategy(),
            # "easyocr": EasyOCRStrategy() # Add this later when needed
        }

    def execute_strategy(
        self, engine_name: str, image: Image.Image
    ) -> tuple[str, float]:
        """
        Executes the selected engine and calculates execution time.
        """
        if engine_name not in self.engines:
            raise ValueError(f"OCR Engine '{engine_name}' is not supported.")

        engine = self.engines[engine_name]

        # Start the timer
        start_time = time.perf_counter()

        # Execute the extraction
        text = engine.extract_text(image)

        # Stop the timer and convert to milliseconds
        end_time = time.perf_counter()
        latency_ms = round((end_time - start_time) * 1000, 2)

        return text, latency_ms
