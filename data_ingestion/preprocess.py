# data_ingestion/preprocess.py
import re

def clean_text(text):
    """Basic cleanup: remove URLs, extra spaces."""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def preprocess_entries(entries):
    """Clean and normalize a list of text entries."""
    for e in entries:
        e["text"] = clean_text(e["text"])
    return entries
