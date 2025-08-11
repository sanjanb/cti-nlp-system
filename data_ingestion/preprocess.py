# data_ingestion/preprocess.py
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0  # For consistent detection results

def preprocess_entries(entries):
    processed = []
    for entry in entries:
        text = entry.get("text", "").strip()
        if not text:
            continue

        # Detect language
        try:
            lang = detect(text)
        except:
            lang = "unknown"

        # Translate if not English
        if lang != "en" and lang != "unknown":
            try:
                translated = GoogleTranslator(source='auto', target='en').translate(text)
                entry["original_text"] = text
                entry["text"] = translated
                entry["lang"] = lang
                entry["translated"] = True
            except Exception as e:
                entry["error_translation"] = str(e)
                entry["translated"] = False
        else:
            entry["lang"] = "en"
            entry["translated"] = False

        processed.append(entry)
    return processed
