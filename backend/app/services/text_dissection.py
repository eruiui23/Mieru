import pykakasi
from jamdict import Jamdict
from typing import List, Dict, Any

kks = pykakasi.kakasi()
jam = Jamdict()

def dissect_text(text: str) -> List[Dict[str, Any]]:
    if not text or not text.strip():
        return []

    try:
        result = kks.convert(text)
        analysis = []
        for item in result:
            token = item.get("orig", "")
            furigana = item.get("hira", "")
            romaji = item.get("hepburn", "")
            
            meaning = "N/A"
            if token.strip():
                try:
                    lookup_res = jam.lookup(token)
                    if lookup_res.entries:
                        entry = lookup_res.entries[0]
                        senses = []
                        for sense in entry.senses:
                            gloss_texts = [gloss.text for gloss in sense.gloss]
                            if gloss_texts:
                                senses.append(", ".join(gloss_texts))
                        if senses:
                            meaning = " | ".join(senses)
                except Exception as lookup_err:
                    print(f"Jamdict lookup failed for token '{token}': {lookup_err}")
            
            analysis.append({
                "word": token,
                "furigana": furigana,
                "romaji": romaji,
                "meaning": meaning
            })
        return analysis
    except Exception as e:
        print(f"Text dissection failed: {e}")
        return []
