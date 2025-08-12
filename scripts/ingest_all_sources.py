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
# scripts/ingest_all_sources.py
import json
from datetime import datetime, timezone
import os
from data_ingestion.fetch_darkweb import fetch_darkweb
from data_ingestion.fetch_twitter import fetch_twitter
from data_ingestion.fetch_mitre_attack import fetch_mitre_attack
from data_ingestion.preprocess import preprocess_entries

# Ensure paths work from any run location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")

OUTPUT_FILE = os.path.join(DATA_DIR, "ingested_cti.jsonl")
STATUS_FILE = os.path.join(DATA_DIR, "last_ingestion.json")

def main():
    summary = {
        "darkweb": 0,
        "twitter": 0,
        "mitre_attack": 0
    }

    all_entries = []

    # Darkweb
    darkweb_data = fetch_darkweb()
    summary["darkweb"] = len(darkweb_data)
    all_entries.extend(darkweb_data)

    # Twitter
    twitter_data = fetch_twitter()
    summary["twitter"] = len(twitter_data)
    all_entries.extend(twitter_data)

    # MITRE ATT&CK
    mitre_data = fetch_mitre_attack()
    summary["mitre_attack"] = len(mitre_data)
    all_entries.extend(mitre_data)

    # Preprocess
    all_entries = preprocess_entries(all_entries)

    # Append to JSONL
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for entry in all_entries:
            entry["timestamp"] = datetime.now(timezone.utc).isoformat()
            f.write(json.dumps(entry) + "\n")

    # Save status
    status_data = {
        "last_run": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "total_records": len(all_entries)
    }
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2)

    print(f"[INFO] Ingestion Summary: {status_data}")

if __name__ == "__main__":
    main()
