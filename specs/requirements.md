# Software Requirements Specification (SRS) - Manga and Document OCR Application

This document defines the functional and non-functional requirements for the Manga and Document OCR Application. The system is designed using a decoupled architecture, leveraging FastAPI for backend processing and Streamlit for the user interface.

---

## 1. Introduction

### 1.1 Purpose
The purpose of this document is to specify the software requirements for the Manga and Document OCR Application. This specification is intended for use by developers and evaluators to guide implementation, testing, and project verification.

### 1.2 Scope
The application is an interactive web utility that allows users to upload images (such as manga pages or text documents), manipulate them to enhance readability, extract text using various OCR engines, translate the extracted text into a target language, and evaluate the performance of different OCR models side-by-side.

---

## 2. System Architecture and Tech Stack Overview

The application follows the Separation of Concerns (SoC) principle, splitting responsibilities into two distinct layers:
* **Frontend Layer (Streamlit):** Handles user interactions, file uploading, parameter adjustments, and visual presentation of data and metrics.
* **Backend Layer (FastAPI):** Hosts the business logic, handles image processing computations via OpenCV/Pillow, manages the translation pipeline, and executes the OCR models asynchronously.

---

## 3. Functional Requirements

### 3.1 Core Features

#### FR-01: Image Upload and Validation
* **Description:** The system must allow users to upload images for text extraction.
* **Inputs:** Image files via a drag-and-drop or file-browser component.
* **Processing:**
  * The frontend must restrict file types to `.png`, `.jpg`, and `.jpeg`.
  * The backend must validate the incoming payload's MIME type to ensure it is a valid image.
* **Outputs:** Successful loading of the file into system memory, or an error message if the file format is invalid.

#### FR-02: Real-time Image Preview
* **Description:** The system must display the uploaded image immediately to the user.
* **Inputs:** Validated uploaded image file.
* **Processing:** The frontend renders the image data dynamically.
* **Outputs:** A responsive preview of the uploaded image displayed on the left side of the user interface.

#### FR-03: Image Manipulator
* **Description:** The system must provide image adjustment capabilities to optimize text clarity before passing the image to the OCR engines.
* **Sub-components:**
  * **Image Cropping:** Users can select and crop a specific area of the image (e.g., a single speech bubble or a specific text block).
  * **Grayscale Toggle:** A binary control to convert the image from color (RGB) to black-and-white (grayscale).
  * **Brightness & Contrast Sliders:** Interactive sliders to increase or decrease image illumination and contrast levels.
* **Processing:**
  * The frontend must cache the crop bounding box values within the Streamlit Session State (`st.session_state`) to prevent slider UI state re-runs from resetting active selections.
  * The frontend passes the adjustment parameters to the backend, where OpenCV or Pillow processes the image array before running the OCR analysis.
* **Outputs:** An updated visual preview of the modified image and an optimized image array sent to the OCR pipeline.

#### FR-04: Multi-Engine OCR Selector
* **Description:** The system must support text extraction from multiple independent OCR libraries.
* **Inputs:** User selection from a dropdown interface menu.
* **Processing:** The system routes the image data to the selected OCR strategy backend (e.g., Manga-OCR for vertical/Japanese text, Tesseract for standard documentation, or EasyOCR for general text scenes).
* **Outputs:** Extracted raw text string corresponding to the text detected in the image.

#### FR-05: Text Translation
* **Description:** The system must translate the extracted text into a designated target language.
* **Inputs:** Extracted raw text string from the OCR engine.
* **Processing:** The backend routes the raw text through a translation service (e.g., DeepL API, Googletrans, or a local translation model) to map the source language to the target language.
* **Outputs:** The translated text string displayed inside a copyable text component in the user interface.

### 3.2 Advanced Features

#### FR-06: Side-by-Side Comparison Mode
* **Description:** The system must allow users to run all integrated OCR engines simultaneously to compare text results.
* **Inputs:** Activation of the comparison mode or tab by the user.
* **Processing:** The backend concurrently processes the same optimized image through all available OCR engines using asynchronous workers.
* **Outputs:** A multi-column or tabular layout displaying the text output from each engine side-by-side, allowing the user to evaluate relative accuracy.

#### FR-07: OCR Engine Performance Metrics Tracking
* **Description:** The system must measure and display performance statistics for each OCR operation.
* **Inputs:** Execution triggers for one or all OCR engines.
* **Processing:** The backend calculates the exact execution time (latency) in milliseconds from the moment the image is received by the engine model until the text string is returned.
* **Outputs:** Numerical latency metrics displayed alongside the text results, and a graphical bar chart comparing the processing speeds of the engines.

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements
* **Asynchronous Execution (NFR-P-01):** The backend endpoints must handle image files asynchronously to ensure the web server remains responsive under concurrent user sessions.
* **Processing Latency (NFR-P-02):** Image pre-processing and API routing (excluding the heavy model inference time) must introduce less than 200 milliseconds of overhead.

### 4.2 Usability Requirements
* **Responsive Interface (NFR-U-01):** The user interface layout must adjust responsively, keeping input controls and previews on the left, and extraction or comparison outputs on the right.
* **Error Transparency (NFR-U-02):** If the backend server becomes unavailable or an API connection drops, the frontend must display an explicit user-friendly error message instead of crashing.

### 4.3 Reliability and Maintainability
* **Modularity (NFR-M-01):** The backend must implement a decoupled design pattern (such as the Strategy Pattern) for the OCR execution block, ensuring new engines can be added with minimal changes to existing core code.
* **Data Layer Coercion Safety (NFR-M-02):** The API router boundary must explicitly handle HTTP form data parsing by coercing primitive input types (string-to-float, string-to-boolean) safely at the input schema interface layer before ingestion by the execution pipelines.
