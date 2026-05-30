# System Design Document (SDD)
**Project Name:** Manga and Document OCR Application
**Author:** Kagendra Amadeo Reynara Pratista
**Program:** Informatics Engineering, Institut Teknologi Sepuluh Nopember (ITS)

---

## 1. System Architecture Overview

The application utilizes a decoupled client-server architecture. To ensure high maintainability and testability, the backend is designed around **Clean Architecture** principles. This isolates the core business rules (OCR processing and image manipulation) from the delivery mechanism (FastAPI) and external dependencies (OCR libraries and translation APIs).

### 1.1 High-Level Architecture
* **Presentation Layer (Frontend):** Built with **Streamlit**. It acts solely as the user interface, handling DOM rendering, state management for user inputs (sliders, toggles), and HTTP communication.
* **Application/Domain Layer (Backend):** Built with **FastAPI**. It handles routing, request validation via Pydantic, and orchestrates the image processing pipeline.
* **Infrastructure Layer:** Contains the actual implementations of the external OCR engines (`manga-ocr`, `pytesseract`, `easyocr`), image processing libraries (`OpenCV`, `Pillow`), and translation services.

---

## 2. User Interface (UI) Layout Design

The Streamlit interface is divided into functional zones to provide a seamless user experience.

### 2.1 Main Application Layout
* **Sidebar (Configuration Panel):**
    * **Engine Selector:** Dropdown to select the OCR Engine (Manga-OCR, Tesseract, EasyOCR, or "Run All" for comparison).
    * **Image Manipulator:** * Grayscale Toggle (Checkbox).
        * Brightness & Contrast adjusters (Sliders).
    * **Language Selector:** Dropdown for target translation language.
* **Main Window - Left Column (Input & Preview):**
    * File Uploader component (drag-and-drop).
    * Interactive Image Cropper component.
    * Live Preview of the pre-processed image (reflecting sidebar adjustments).
    * "Process Image" action button.
* **Main Window - Right Column (Output & Analytics):**
    * *Single Mode:* Displays extracted raw text and the translated text in copyable markdown blocks.
    * *Comparison Mode:* Displays a side-by-side grid of text outputs from all engines, along with a bar chart plotting the execution latency of each engine.

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

The backend exposes RESTful endpoints to communicate with the Streamlit client.

### 4.1 `POST /api/v1/ocr/process`
Processes an image using a single specified OCR engine.

* **Request Form-Data:**
    * `file`: The uploaded image file (`image/jpeg` or `image/png`).
    * `engine`: String (e.g., `"manga_ocr"`, `"tesseract"`).
    * `grayscale`: Boolean.
    * `brightness`: Float (e.g., `1.0` for default).
    * `contrast`: Float (e.g., `1.0` for default).
    * `target_lang`: String (e.g., `"en"`, `"id"`).
* **Response (JSON - 200 OK):**
    ```json
    {
      "status": "success",
      "data": {
        "engine_used": "manga_ocr",
        "extracted_text": "こんにちは世界",
        "translated_text": "Hello World",
        "latency_ms": 450.5
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
            "latency_ms": 450.5
          },
          {
            "engine": "tesseract",
            "extracted_text": "こんには世界",
            "translated_text": "Kon'niwa World",
            "latency_ms": 120.2
          }
        ]
      }
    }
    ```

---

## 5. Image Processing Pipeline Flow

When the Streamlit client sends an image and parameters to the FastAPI backend, the data flows through the following pipeline:

1.  **Ingestion & Validation:** FastAPI receives the multipart form data and Pydantic validates the parameter data types.
2.  **Pre-processing (OpenCV/Pillow):** * The image byte stream is loaded into an array.
    * If `grayscale=True`, the color channels are collapsed.
    * Brightness and contrast matrices are applied based on the slider values.
3.  **OCR Execution (Strategy Context):**
    * The processed image matrix is passed to the selected engine(s).
    * For the `/compare` endpoint, execution runs asynchronously using Python's `asyncio.gather()` to prevent engine bottlenecks.
4.  **Post-processing (Translation):** The extracted text strings are routed to the translation API module.
5.  **Response Delivery:** The latency metrics, raw text, and translated text are packaged into a JSON response and returned to the client.