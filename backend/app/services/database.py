import os
import sqlite3
import uuid
from pathlib import Path
from typing import List, Dict, Any

# Resolve absolute paths relative to backend directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "mieru.db"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"

def init_db():
    """
    Initializes the SQLite database schema and local upload directories.
    """
    # Create static uploads directory if not exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize SQLite database and create history table
    conn = sqlite3.connect(str(DB_PATH))
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ocr_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
                filename TEXT NOT NULL,
                engine TEXT NOT NULL,
                extracted_text TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                image_path TEXT NOT NULL
            );
        """)
        conn.commit()
    finally:
        conn.close()

def save_uploaded_image(filename: str, image_bytes: bytes) -> str:
    """
    Saves incoming raw image bytes to the local upload directory with a unique filename
    to prevent collision. Returns the relative image path reference (e.g. 'static/uploads/filename').
    """
    # Ensure directory exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename to avoid collision
    file_ext = Path(filename).suffix or ".png"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    target_path = UPLOAD_DIR / unique_filename
    
    # Write image bytes to local disk
    with open(target_path, "wb") as f:
        f.write(image_bytes)
        
    return f"static/uploads/{unique_filename}"

def save_history(
    filename: str,
    engine: str,
    extracted_text: str,
    translated_text: str,
    image_path: str
) -> None:
    """
    Writes a log entry into the SQLite ocr_history table using the provided image path reference.
    """
    conn = sqlite3.connect(str(DB_PATH))
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ocr_history (filename, engine, extracted_text, translated_text, image_path)
            VALUES (?, ?, ?, ?, ?);
        """, (filename, engine, extracted_text, translated_text, image_path))
        conn.commit()
    finally:
        conn.close()

def get_history() -> List[Dict[str, Any]]:
    """
    Retrieves all past OCR operations from the database, sorted from newest to oldest.
    """
    if not DB_PATH.exists():
        return []
        
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, filename, engine, extracted_text, translated_text, image_path
            FROM ocr_history
            ORDER BY timestamp DESC;
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
