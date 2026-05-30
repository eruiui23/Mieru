from pydantic import BaseModel


class OCRResponse(BaseModel):
    filename: str
    engine: str
    extracted_text: str
    translated_text: str
    execution_time_ms: float


class ComparisonResponse(BaseModel):
    filename: str
    engines_evaluated: list[str]
    results: list[OCRResponse]
