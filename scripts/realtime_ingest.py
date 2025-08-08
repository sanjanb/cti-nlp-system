import time
from sources.twitter_source import fetch_twitter
from sources.mitre_source import fetch_mitre
from sources.telegram_source import fetch_telegram
from sources.darkweb_source import fetch_darkweb
from transformers import pipeline
from deep_translator import GoogleTranslator

# Load your existing model
ner_pipeline = pipeline(
    "ner",
    model="backend/models/ner_model",
    tokenizer="backend/models/ner_model",
    aggregation_strategy="simple"
)

def preprocess_text(text, target_lang="en"):
    # Translate to English if not already
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except:
        return text

def process_entry(entry):
    text = preprocess_text(entry["text"])
    entities = ner_pipeline(text)
    return {
        "source": entry["source"],
        "text": text,
        "entities": entities,
        "metadata": entry["metadata"]
    }

def run_realtime_pipeline(interval=60):
    while True:
        print("[INFO] Fetching data sources...")
        data = []
        data.extend(fetch_twitter(limit=5))
        data.extend(fetch_mitre())
        data.extend(fetch_telegram())
        data.extend(fetch_darkweb())

        for entry in data:
            result = process_entry(entry)
            print(f"\n[{result['source'].upper()}] {result['text']}")
            print(f"Entities: {result['entities']}")

        print(f"[INFO] Sleeping for {interval} seconds...\n")
        time.sleep(interval)

if __name__ == "__main__":
    run_realtime_pipeline()
