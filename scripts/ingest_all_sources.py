# scripts/ingest_all_sources.py
import json
import os
import sys
from datetime import datetime

# Ensure root path is in sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_ingestion.fetch_darkweb import fetch_darkweb
from data_ingestion.fetch_twitter import fetch_twitter
from data_ingestion.fetch_mitre_attack import fetch_mitre_attack
from data_ingestion.preprocess import preprocess_entries

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "ingested_cti.jsonl")


def ensure_data_dir():
    """Ensure data folder exists."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"[INFO] Created directory: {OUTPUT_DIR}")


def main():
    ensure_data_dir()

    all_entries = []
    source_counts = {}

    sources = {
        "darkweb": fetch_darkweb,
        "twitter": fetch_twitter,
        "mitre_attack": fetch_mitre_attack
    }

    # Fetch from all sources
    for name, func in sources.items():
        try:
            entries = func()
            source_counts[name] = len(entries)
            all_entries.extend(entries)
        except Exception as e:
            source_counts[name] = 0
            print(f"[ERROR] Failed to fetch from {name}: {e}")

    # Preprocess entries
    all_entries = preprocess_entries(all_entries)

    # Append with timestamp
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for entry in all_entries:
            entry["timestamp"] = datetime.utcnow().isoformat()
            f.write(json.dumps(entry) + "\n")

    # Summary log
    print("\n[INFO] Ingestion Summary:")
    for src, count in source_counts.items():
        print(f"  - {src}: {count} records")
    print(f"  => Total appended: {len(all_entries)} to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
