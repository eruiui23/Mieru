import time
from abc import ABC, abstractmethod

from PIL import Image

class OCREngine(ABC):
    @abstractmethod
    def extract_text(self, image: Image.Image) -> str:
        pass


class MangaOCRStrategy(OCREngine):
    def __init__(self):
        print("Initializing Manga-OCR Model (This takes a moment)...")
        from manga_ocr import MangaOcr

        try:
            self.mocr = MangaOcr()
        except Exception as e:
            print(f"Failed to initialize MangaOcr with CUDA/default device: {e}. Falling back to CPU...")
            self.mocr = MangaOcr(force_cpu=True)

    def extract_text(self, image: Image.Image) -> str:
        return self.mocr(image)


class TesseractStrategy(OCREngine):
    def __init__(self):
        print("Initializing Tesseract Engine...")
        import pytesseract  

        self.pytesseract = pytesseract

    def extract_text(self, image: Image.Image) -> str:
        text = self.pytesseract.image_to_string(image, lang='jpn+jpn_vert')
        return text.replace("\n", "").replace("\r", "").strip()


class EasyOCRStrategy(OCREngine):
    def __init__(self):
        print("Initializing EasyOCR Engine...")
        import easyocr

        try:
            self.reader = easyocr.Reader(['ja'])
        except Exception as e:
            print(f"Failed to initialize EasyOCR with GPU: {e}. Falling back to CPU...")
            self.reader = easyocr.Reader(['ja'], gpu=False)

    def extract_text(self, image: Image.Image) -> str:
        import numpy as np

        img_np = np.array(image)
        results = self.reader.readtext(img_np, detail=0)
        return "".join(results).strip()


class OCRContext:
    def __init__(self):
        self.engines = {
            "manga_ocr": MangaOCRStrategy(),
            "tesseract": TesseractStrategy(),
            "easyocr": EasyOCRStrategy(),
        }

    def execute_strategy(
        self, engine_name: str, image: Image.Image
    ) -> tuple[str, float]:
        if engine_name not in self.engines:
            raise ValueError(f"OCR Engine '{engine_name}' is not supported.")

        engine = self.engines[engine_name]

        start_time = time.perf_counter()

        text = engine.extract_text(image)

        end_time = time.perf_counter()
        latency_ms = round((end_time - start_time) * 1000, 2)

        return text, latency_ms
