import os
import re
import pandas as pd
import spacy
from pathlib import Path

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")

# Define input and output paths
RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

def clean_text(text):
    # Remove URLs, special characters, digits
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    text = re.sub(r"[^a-zA-Z\s]", '', text)
    text = re.sub(r"\s+", ' ', text).strip()
    return text.lower()

def preprocess_text(text):
    doc = nlp(text)
    lemmatized = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(lemmatized)

def preprocess_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    cleaned = clean_text(text)
    lemmatized = preprocess_text(cleaned)
    return lemmatized

def main():
    all_data = []

    for file in RAW_DATA_DIR.glob("*.txt"):
        processed = preprocess_file(file)
        all_data.append({
            "filename": file.name,
            "clean_text": processed
        })

    df = pd.DataFrame(all_data)
    df.to_csv(PROCESSED_DATA_DIR / "preprocessed_data.csv", index=False)
    print(f"Processed {len(all_data)} files → saved to preprocessed_data.csv")

if __name__ == "__main__":
    main()
