import pykakasi
from typing import List, Dict, Any

kks = pykakasi.kakasi()

def dissect_text(text: str) -> List[Dict[str, Any]]:
    if not text or not text.strip():
        return []

    try:
        result = kks.convert(text)
        analysis = []
        for item in result:
            analysis.append({
                "kanji": item.get("orig", ""),
                "kana": item.get("hira", ""),
                "roman": item.get("hepburn", ""),
                "part_of_speech": "N/A"
            })
        return analysis
    except Exception as e:
        print(f"Text dissection failed: {e}")
        return []
