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
* **Infrastructure Layer:** Contains the actual implementations of the external OCR engines (`manga-ocr`, `pytesseract`, `easyocr`), translation services, and the **SQLite** persistence layer. Image processing libraries (Pillow) are now handled in the Presentation Layer.

### 1.2 Phase 5: Advanced Features Subsystem
* **Modular Advanced Services:** The advanced features module (including any text dissection, tokenization, or linguistic parsing components, such as `pykakasi`) attaches modularly to the backend domain/services layer. This keeps the core OCR engine implementations (`OCREngine` subclasses) cleanly isolated from downstream text analysis, conforming to the Single Responsibility Principle and ensuring ease of extension for future features.
* **Persistent Storage History:** An SQLite database is integrated into the backend infrastructure to provide persistent regional storage for all processed OCR events. The schema logs metadata, extracted outputs, and the local image file path reference (`id`, `timestamp`, `filename`, `engine`, `extracted_text`, `translated_text`, `image_path`), decoupling workspace sessions from server uptime. To serve these historical image files back to the frontend client, the FastAPI backend mounts a `fastapi.staticfiles.StaticFiles` instance at `/static` referencing the local storage directory (`backend/static/uploads/`).

---

## 2. User Interface (UI) Layout & State Design

The Streamlit interface is divided into functional zones to provide a seamless user experience. It operates as a dual-state view machine controlled by a navigation router in the sidebar.

### 2.1 Dual-State Main Application Layout

The frontend session state tracks the current active view. Based on this value, the main page renders one of two dedicated view modes:

#### 2.1.1 View A: Workspace Mode (OCR Workstation)
* **Sidebar (Configuration Panel):**
    * **Navigation Panel:** State switching buttons/router to toggle between "OCR Workspace" and "View History Log".
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
        * **Advanced Analysis (Optional Expander):** A conditional `st.expander` titled "文法 & 振り仮名 | Japanese Analysis (Furigana & Readings)" that renders a dataframe containing word-level details (`word`, `furigana`, `romaji`, `meaning`). This is a conditional layout block that remains hidden unless the advanced payload is present.
    * *Comparison Mode:* Displays a side-by-side grid of text outputs from all engines, along with a bar chart plotting the execution latency of each engine.

#### 2.1.2 View B: Dedicated History Mode (Database Audit Log & Detail Viewer)
* **Sidebar (Configuration Panel):**
    * **Navigation Panel:** Same state switching buttons/router to return to "OCR Workspace".
* **Main Window:**
    * **Database Audit Log Table:** Displays a clean, structural database audit log of all successful OCR operations using an interactive `st.dataframe`. Contains columns: ID, Timestamp, Filename, Engine Used, Extracted Text, and Translated Text.
    * **Historical Detail Viewer:** Below or side-by-side with the database table, when a user selects/clicks a historical log row, the interface dynamically displays the archived original image side-by-side with its past extracted text and translated text for direct, comparative reading.

### 2.2 Frontend State Preservation and Asset State Machine
Because Streamlit re-executes the entire script upon any widget modification (such as moving the brightness or contrast sliders), the application leverages `st.session_state` to store user cropping boundaries. This mechanism protects crop states from being reset during subsequent pipeline parameter adjustments.

Furthermore, a two-step state-machine governs raw image uploads to prevent redundant network transmissions of the large original file during iterative cropping adjustments:
1. **Immediate Upload Hook:** The instant a file is added via the `st.file_uploader`, it triggers a background upload (`POST /api/upload`) containing only the full, original image.
2. **Backend Reference Caching:** The backend stores the original asset and returns a string identifier (`full_image_ref`). The Streamlit frontend caches this identifier in `st.session_state` indexed by the file slot.
3. **Execution Linkage:** When the user clicks "Process Image", only the tiny cropped crop bytes are sent along with the cached `full_image_ref` token. The backend processes the crop but logs the original image path referenced by `full_image_ref` to the SQLite history log database, ensuring high resolution audit trails with zero redundant uploads.

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
    * `file`: The uploaded cropped image file (`image/jpeg` or `image/png`).
    * `engine`: String (e.g., `"manga_ocr"`, `"tesseract"`).
    * `target_lang`: String (e.g., `"en"`, `"id"`).
    * `full_image_ref`: String (relative URL path pointing to the cached raw original image on the server, e.g., `"static/uploads/uuid.png"`).
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
            "word": "こんにちは",
            "furigana": "こんにちは",
            "romaji": "konnichiha",
            "meaning": "hello; good day"
          },
          {
            "word": "世界",
            "furigana": "せかい",
            "romaji": "sekai",
            "meaning": "world; society; universe"
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
                "word": "こんにちは",
                "furigana": "こんにちは",
                "romaji": "konnichiha",
                "meaning": "hello; good day"
              },
              {
                "word": "世界",
                "furigana": "せかい",
                "romaji": "sekai",
                "meaning": "world; society; universe"
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

### 4.3 `GET /api/history`
Queries the SQLite persistent database for past OCR executions and returns them sorted by the most recent timestamp.

* **Request Parameters:**
    * *(None)*
* **Response (JSON - 200 OK):**
    ```json
    {
      "status": "success",
      "data": [
        {
          "id": 2,
          "timestamp": "2026-06-07T15:43:29Z",
          "filename": "manga_page_1.png",
          "engine": "manga_ocr",
          "extracted_text": "こんにちは世界",
          "translated_text": "Hello World",
          "image_path": "static/uploads/manga_page_1.png"
        },
        {
          "id": 1,
          "timestamp": "2026-06-07T15:30:15Z",
          "filename": "document.png",
          "engine": "tesseract",
          "extracted_text": "Hello, this is a test.",
          "translated_text": "Hello, this is a test.",
          "image_path": "static/uploads/document.png"
        }
      ]
    }
    ```

### 4.4 `POST /api/upload`
Uploads the raw, uncropped file immediately upon user drop and saves it to the local server uploads directory.

* **Request Form-Data:**
    * `file`: The uploaded original image file (`image/jpeg` or `image/png`).
* **Response (JSON - 200 OK):**
    ```json
    {
      "status": "success",
      "filename": "manga_page_1.png",
      "full_image_ref": "static/uploads/7b189283-99fa-45b3-8c4d-2a839a8c17b2.png"
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

---

## 6. Architecture Decision Records (ADR)

### ADR 1: SQLAlchemy Integration within Clean Architecture

* **Topic**: SQLAlchemy Integration within Clean Architecture.
* **Decision**: Moving from raw `sqlite3` to SQLAlchemy 2.0.
* **Rationale**: To gain type safety (via `Mapped` columns) and better maintainability compared to manually managing SQL queries and schemas.
* **Clean Architecture Alignment**: The ORM is strictly confined to the outermost "Frameworks & Drivers" layer. Data mapping to standard Python dictionaries ensures that SQLAlchemy model objects do not leak into our inner domain logic, preserving independence from external database frameworks.
