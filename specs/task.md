# Development Task Tracker
**Project:** Manga and Document OCR Application
**Format:** Agile / Phase-Based Task List

This document breaks down the Software Requirements Specification (SRS) and System Design Document (SDD) into actionable development tasks. You can use this in a Kanban board (like Trello, Jira, or GitHub Projects).

---

## Phase 1: Project Setup & Architecture
*Goal: Establish the repository, environments, and foundational folder structure.*

- [x] **Task 1.1: Initialize Version Control**
  - Create a Git repository and define the `.gitignore` for Python (`__pycache__`, `.venv`, `.env`, etc.).
- [x] **Task 1.2: Modern Environment Setup via uv**
  - Initialize a managed Python project workspace using `uv init`.
  - Install core dependencies using `uv add` (`fastapi`, `uvicorn`, `streamlit`, `requests`, `python-multipart`).
- [x] **Task 1.3: Define Directory Structure**
  - Apply Clean Architecture principles—structuring directories by domain models, use cases, and infrastructure—to keep the FastAPI backend decoupled and highly maintainable.
  - Create separate root directories for `/frontend` and `/backend`.

---

## Phase 2: Core Backend Engine (FastAPI)
*Goal: Implement the image processing and OCR strategy logic.*

- [x] **Task 2.1: Implement Strategy Design Pattern**
  - Define the abstract base class `OCREngine`.
  - Create the `MangaOCRStrategy` class and handle the model initialization.
  - Create the `TesseractStrategy` and `EasyOCRStrategy` classes.
- [x] **Task 2.2: Translation Integration**
  - Integrate a translation service (e.g., `googletrans` or DeepL API) as a separate utility function that accepts raw text and a target language parameter.
- [x] **Task 2.3: Develop REST Endpoints**
  - Build `POST /api/v1/ocr/process` for single-engine execution, ensuring parameters (excluding `grayscale`, `brightness`, and `contrast`) are strictly handled via explicit Form data bindings.
  - Build `POST /api/v1/ocr/compare` using `asyncio.gather()` to run multiple engine strategies concurrently.
  - Implement performance tracking to calculate execution latency (`latency_ms`) for each request.

---

## Phase 3: Frontend Interface (Streamlit)
*Goal: Build the interactive UI and connect it to the backend API.*

- [x] **Task 3.1: Construct the Layout**
  - Configure the page layout to `wide` mode.
  - Build the Sidebar containing the Engine Selector dropdown, Grayscale toggle, Brightness/Contrast sliders, and Target Language dropdown.
- [x] **Task 3.2: Image Upload & Preview Component**
  - Implement `st.file_uploader` supporting `.png`, `.jpg`, `.jpeg`.
  - Integrate a custom Streamlit image cropping component (e.g., `streamlit-cropper`) to allow users to isolate specific text bubbles.
  - Use Pillow (`ImageOps` and `ImageEnhance`) to apply Grayscale, Brightness, and Contrast adjustments directly to the uploaded image state.
  - Render the live image preview using this Pillow-processed image, and then convert it to a PNG byte array before sending it via `requests.post`.
- [x] **Task 3.3: API Integration & State Management**
  - Implement Streamlit Session State (`st.session_state`) to cache cropping boundaries, ensuring slider micro-interactions do not clear or reset the active user crop.
  - Write the `requests.post` logic to send the image and parameters to the FastAPI backend.
  - Handle loading states (`st.spinner`) while waiting for the OCR engines to finish processing.
- [x] **Task 3.4: Build the Output Views**
  - Create the Single Mode view to display extracted and translated text using `st.markdown` and `st.code`.
  - Create the Comparison Mode view using columns to display results side-by-side, and integrate `st.bar_chart` to visualize the latency metrics.

---

## Phase 4: Integration & Testing
*Goal: Validate the accuracy, speed, and reliability of the full pipeline.*

- [x] **Task 4.1: End-to-End API Testing**
  - Use Swagger UI (`http://localhost:8000/docs`) to manually test payloads and verify Pydantic schema validation for form-to-primitive parsing.
- [x] **Task 4.2: Manga-OCR Accuracy Validation**
  - Test the Japanese OCR extraction accuracy by feeding raw manga panels (like *Ao no Hako* / *Blue Box* chapters) into the pipeline to verify reliable kanji detection.
- [x] **Task 4.3: Concurrency Testing**
  - Run the Comparison Mode multiple times to ensure the asynchronous backend does not drop requests or mix up image matrices when processing Tesseract, Manga-OCR, and EasyOCR simultaneously.
- [ ] **Task 4.4: Error Handling UI**
  - Simulate backend connection failures and ensure Streamlit displays a graceful error message rather than a raw Python traceback.

---

## Phase 5: Advanced Features
*Goal: Integrate linguistic analysis and other modular advanced features.*

- [ ] **Task 5.1: Backend Text Dissection Pipeline:** Integrate a text parser (like pykakasi) and a dictionary engine (like jamdict) into the backend services layer to dissect raw text strings into structured dictionaries containing tokens, furigana, rōmaji, and English definitions.
- [ ] **Task 5.2: API Schema Extension:** Update the backend endpoints and Pydantic response models (`OCRResponse`) to include an optional data payload field for advanced analysis, ensuring backwards compatibility.
- [ ] **Task 5.3: Frontend Accordion Dropdown (Option B):** Implement an `st.expander` named "文法 & 振り仮名 | Japanese Analysis (Furigana & Readings)" sitting right below the Extracted/Translated text block, which renders the payload (token, furigana, romaji, and meaning) inside a clean, conditional `st.dataframe`.

---

## Phase 6: Finalization & Documentation
*Goal: Prepare the project for the final academic presentation.*

- [ ] **Task 6.1: Code Cleanup & Refactoring**
  - Remove hardcoded values and move sensitive data (like API keys) to `.env` files.
  - Add type hints and docstrings to all major backend functions.
- [ ] **Task 6.2: Write the README**
  - Compile the Feature Backlog, Setup Instructions, and API Documentation into a comprehensive `README.md`.
- [ ] **Task 6.3: Presentation Prep**
  - Prepare a set of sample images (standard documents, manga pages, noisy images) to demonstrate the application's capabilities during the final project review.

