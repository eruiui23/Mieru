# System Design Document (SDD)
**Project Name:** Manga and Document OCR Application
**Author:** Kagendra Amadeo Reynara Pratista
**Program:** Informatics Engineering, Institut Teknologi Sepuluh Nopember (ITS)

---

## 1. System Architecture Overview

The application utilizes a decoupled client-server architecture. To ensure high maintainability and testability, the backend is designed around **Clean Architecture** principles. This isolates the core business rules (OCR processing and image manipulation) from the delivery mechanism (FastAPI) and external dependencies (OCR libraries and translation APIs).

### 1.1 High-Level Architecture
* **Presentation Layer (Frontend):** Built with **Streamlit**. It handles DOM rendering, state management for user inputs (sliders, toggles), image manipulation/processing using Pillow (applying grayscale, brightness, and contrast adjustments), and HTTP communication.
* **Application/Domain Layer (Backend):** Built with **FastAPI**. It handles routing, request validation via Pydantic, and orchestrates the OCR execution and translation pipeline.
* **Infrastructure Layer:** Contains the actual implementations of the external OCR engines (`manga-ocr`, `pytesseract`, `easyocr`) and translation services. Image processing libraries (Pillow) are now handled in the Presentation Layer.

### 1.2 Phase 5: Advanced Features Subsystem
* **Modular Advanced Services:** The advanced features module (including any text dissection, tokenization, or linguistic parsing components, such as `pykakasi`) attaches modularly to the backend domain/services layer. This keeps the core OCR engine implementations (`OCREngine` subclasses) cleanly isolated from downstream text analysis, conforming to the Single Responsibility Principle and ensuring ease of extension for future features.

---

## 2. User Interface (UI) Layout & State Design

The Streamlit interface is divided into functional zones to provide a seamless user experience.

### 2.1 Main Application Layout
* **Sidebar (Configuration Panel):**
    * **Engine Selector:** Dropdown to select the OCR Engine (Manga-OCR, Tesseract, EasyOCR, or "Run All" for comparison).
    * **Image Manipulator:**
        * Grayscale Toggle (Checkbox).
        * Brightness & Contrast adjusters (Sliders).
    * **Language Selector:** Dropdown for target translation language.
* **Main Window - Left Column (Input & Preview):**
    * File Uploader component (drag-and-drop).
    * Interactive Image Cropper component.
    * Live Preview of the pre-processed image (reflecting sidebar adjustments).
    * "Process Image" action button.
* **Main Window - Right Column (Output & Analytics):**
    * *Single Mode:* 
        * Displays extracted raw text and the translated text in copyable markdown blocks.
        * **Advanced Analysis (Optional Expander):** A conditional `st.expander` titled "文法 & 振り仮名 | Japanese Analysis (Furigana & Readings)" that renders a dataframe containing token-level advanced features payload. This is a conditional layout block that remains hidden unless the advanced payload is present.
    * *Comparison Mode:* Displays a side-by-side grid of text outputs from all engines, along with a bar chart plotting the execution latency of each engine.

### 2.2 Frontend State Preservation
Because Streamlit re-executes the entire script upon any widget modification (such as moving the brightness or contrast sliders), the application leverages `st.session_state` to store user cropping boundaries. This mechanism protects crop states from being reset during subsequent pipeline parameter adjustments.

---

## 3. Design Patterns

To meet the modularity requirements defined in the SRS, the following design patterns are implemented:

### 3.1 Strategy Pattern
Applied to the OCR Engine execution. An abstract base class `OCREngine` defines a common interface (e.g., `extract_text(image: bytes) -> str`). Each specific library (`MangaOCRStrategy`, `TesseractStrategy`, `EasyOCRStrategy`) implements this interface. 
* **Benefit:** The backend can easily switch between engines or run them concurrently without tightly coupling the route handlers to specific library syntax.

### 3.2 Factory Pattern
Used to instantiate the correct OCR strategy based on the user's selection from the frontend payload.

---

## 4. API Specification (FastAPI)

The backend exposes RESTful endpoints to communicate with the Streamlit client. Because Multipart Form-Data natively transmits parameters as strings, the backend uses explicit FastAPI `Form(...)` field configurations to automatically enforce string-to-primitive coercion (e.g., parsing incoming string values into strict boolean or float primitives).

### 4.1 `POST /api/v1/ocr/process`
Processes an image using a single specified OCR engine.

* **Request Form-Data:**
    * `file`: The uploaded image file (`image/jpeg` or `image/png`).
    * `engine`: String (e.g., `"manga_ocr"`, `"tesseract"`).
    * `target_lang`: String (e.g., `"en"`, `"id"`).
* **Response (JSON - 200 OK):**
    ```json
    {
      "status": "success",
      "data": {
        "engine_used": "manga_ocr",
        "extracted_text": "こんにちは世界",
        "translated_text": "Hello World",
        "latency_ms": 450.5,
        "advanced_analysis": [
          {
            "kanji": "こんにちは",
            "kana": "こんにちは",
            "roman": "konnichiha"
          },
          {
            "kanji": "世界",
            "kana": "せかい",
            "roman": "sekai"
          }
        ] // Optional: List[Dict[str, str]] - Activates strictly when advanced analysis payload is present.
      }
    }
    ```

### 4.2 `POST /api/v1/ocr/compare`
Executes the image processing concurrently across all available engines for the Side-by-Side Comparison mode.

* **Request Form-Data:**
    * *(Same parameters as 4.1, excluding `engine`)*
* **Response (JSON - 200 OK):**
    ```json
    {
      "status": "success",
      "data": {
        "comparison_results": [
          {
            "engine": "manga_ocr",
            "extracted_text": "こんにちは世界",
            "translated_text": "Hello World",
            "latency_ms": 450.5,
            "advanced_analysis": [
              {
                "kanji": "こんにちは",
                "kana": "こんにちは",
                "roman": "konnichiha"
              },
              {
                "kanji": "世界",
                "kana": "せかい",
                "roman": "sekai"
              }
            ] // Optional: List[Dict[str, str]]
          },
          {
            "engine": "tesseract",
            "extracted_text": "こんには世界",
            "translated_text": "Kon'niwa World",
            "latency_ms": 120.2,
            "advanced_analysis": null // Optional/Null when deactivated or not applicable
          }
        ]
      }
    }
    ```

---

## 5. Image Processing Pipeline Flow

When the Streamlit client sends an image and parameters to the FastAPI backend, the data flows through the following pipeline:

1. **Ingestion & Validation:** FastAPI receives the multipart form data (the pre-optimized image and other parameters). The request values are validated and coerced into their strict primitive data types via FastAPI `Form(...)` handlers matching Pydantic-backed parameter rules.
2. **OCR Execution (Strategy Context):**
    * FastAPI receives the pre-optimized image and passes it directly to the OCR engines without further manipulation.
    * The image byte stream is passed to the selected engine(s).
    * For the `/compare` endpoint, execution runs asynchronously using Python's `asyncio.gather()` to prevent engine bottlenecks.
3. **Post-processing (Translation):** The extracted text strings are routed to the translation API module.
4. **Response Delivery:** The latency metrics, raw text, and translated text are packaged into a JSON response and returned to the client.
