import os
import uuid
from pathlib import Path
from typing import List, Dict, Any

from sqlalchemy import create_engine, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "mieru.db"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"

DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class OCRHistory(Base):
    __tablename__ = "ocr_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[str] = mapped_column(
        String, 
        nullable=False, 
        server_default=func.strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
    )
    filename: Mapped[str] = mapped_column(String, nullable=False)
    engine: Mapped[str] = mapped_column(String, nullable=False)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)
    image_path: Mapped[str] = mapped_column(String, nullable=False)

def init_db():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    Base.metadata.create_all(bind=engine)

def save_uploaded_image(filename: str, image_bytes: bytes) -> str:
    """
    Saves incoming raw image bytes to the local upload directory with a unique filename
    to prevent collision. Returns the relative image path reference (e.g. 'static/uploads/filename').
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    file_ext = Path(filename).suffix or ".png"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    target_path = UPLOAD_DIR / unique_filename
    
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
    db = SessionLocal()
    try:
        new_entry = OCRHistory(
            filename=filename,
            engine=engine,
            extracted_text=extracted_text,
            translated_text=translated_text,
            image_path=image_path
        )
        db.add(new_entry)
        db.commit()
    finally:
        db.close()

def get_history() -> List[Dict[str, Any]]:
    """
    Retrieves all past OCR operations from the database, sorted from newest to oldest.
    """
    if not DB_PATH.exists():
        return []
        
    db = SessionLocal()
    try:
        records = db.query(OCRHistory).order_by(OCRHistory.timestamp.desc()).all()
        return [
            {
                "id": record.id,
                "timestamp": record.timestamp,
                "filename": record.filename,
                "engine": record.engine,
                "extracted_text": record.extracted_text,
                "translated_text": record.translated_text,
                "image_path": record.image_path
            }
            for record in records
        ]
    finally:
        db.close()
