# scripts/ingest_all_sources.py
import json
from datetime import datetime
from data_ingestion.fetch_darkweb import fetch_darkweb
from data_ingestion.fetch_twitter import fetch_twitter
from data_ingestion.fetch_mitre_attack import fetch_mitre_attack
from data_ingestion.preprocess import preprocess_entries

OUTPUT_FILE = "data/ingested_cti.jsonl"

def main():
    all_entries = []
    all_entries.extend(fetch_darkweb())
    all_entries.extend(fetch_twitter())
    all_entries.extend(fetch_mitre_attack())

    # Preprocess
    all_entries = preprocess_entries(all_entries)

    # Append to JSONL
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for entry in all_entries:
            entry["timestamp"] = datetime.utcnow().isoformat()
            f.write(json.dumps(entry) + "\n")

    print(f"Ingested {len(all_entries)} new records into {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
