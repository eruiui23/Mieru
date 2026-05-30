import asyncio
import logging

from googletrans import Translator

# We use a single translator instance
translator = Translator()


async def translate_text(text: str, target_lang: str = "en") -> str:
    """
    Translates the given text into the target language.
    Uses asyncio.to_thread to run the synchronous googletrans library
    without blocking the FastAPI event loop.
    """
    if not text or not text.strip():
        return ""

    try:
        # Pass the synchronous function and its arguments to a background thread
        result = await asyncio.to_thread(translator.translate, text, dest=target_lang)
        return result.text
    except Exception as e:
        logging.error(f"Translation error: {e}")
        # If translation fails, return the original text with a warning
        return f"[Translation Failed] {text}"
