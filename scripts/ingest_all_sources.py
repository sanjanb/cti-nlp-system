# scripts/ingest_all_sources.py
import json
import os
import sys
from datetime import datetime, timezone

# Ensure root path is in sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_ingestion.fetch_darkweb import fetch_darkweb
from data_ingestion.fetch_twitter import fetch_twitter
from data_ingestion.fetch_mitre_attack import fetch_mitre_attack
from data_ingestion.preprocess import preprocess_entries

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "ingested_cti.jsonl")
STATUS_FILE = os.path.join(DATA_DIR, "last_ingestion.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def main():
    summary = {
        "darkweb": 0,
        "twitter": 0,
        "mitre_attack": 0
    }
    errors = {}
    all_entries = []

    # Fetch Darkweb
    try:
        darkweb_data = fetch_darkweb()
        summary["darkweb"] = len(darkweb_data)
        all_entries.extend(darkweb_data)
    except Exception as e:
        errors["darkweb"] = str(e)

    # Fetch Twitter
    try:
        twitter_data = fetch_twitter()
        summary["twitter"] = len(twitter_data)
        all_entries.extend(twitter_data)
    except Exception as e:
        errors["twitter"] = str(e)

    # Fetch MITRE ATT&CK
    try:
        mitre_data = fetch_mitre_attack()
        summary["mitre_attack"] = len(mitre_data)
        all_entries.extend(mitre_data)
    except Exception as e:
        errors["mitre_attack"] = str(e)

    # Preprocess entries if we got any
    if all_entries:
        all_entries = preprocess_entries(all_entries)

        # Append to JSONL
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            for entry in all_entries:
                entry["timestamp"] = datetime.now(timezone.utc).isoformat()
                f.write(json.dumps(entry) + "\n")

    # Save status JSON
    status_data = {
        "last_run": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "total_records": len(all_entries),
        "errors": errors
    }
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2)

    # Console log
    print("\n[INFO] Ingestion Summary:")
    for source, count in summary.items():
        print(f"  - {source}: {count} records")
    if errors:
        print("\n[WARN] Some sources failed:")
        for src, err in errors.items():
            print(f"  - {src}: {err}")
    print(f"=> Total appended: {len(all_entries)} to {OUTPUT_FILE}\n")

if __name__ == "__main__":
    main()
