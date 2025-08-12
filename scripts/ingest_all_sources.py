# scripts/ingest_all_sources.py
import json
import os
import sys
from datetime import datetime, timezone

# Ensure root path is in sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Source fetchers
from data_ingestion.fetch_darkweb import fetch_darkweb
from data_ingestion.fetch_twitter import fetch_twitter
from data_ingestion.fetch_mitre_attack import fetch_mitre_attack
from data_ingestion.preprocess import preprocess_entries

# ML pipelines
from backend.threat_ner import extract_threat_entities
from backend.classifier import classify_threat
from backend.severity_predictor import predict_severity

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

    # Fetch raw data
    darkweb_data = fetch_darkweb()
    summary["darkweb"] = len(darkweb_data)
    all_entries.extend(darkweb_data)

    twitter_data = fetch_twitter()
    summary["twitter"] = len(twitter_data)
    all_entries.extend(twitter_data)

    mitre_data = fetch_mitre_attack()
    summary["mitre_attack"] = len(mitre_data)
    all_entries.extend(mitre_data)

    # Preprocess
    all_entries = preprocess_entries(all_entries)

    enriched_entries = []
    for entry in all_entries:
        try:
            text = entry.get("text", "")
            if not text.strip():
                continue

            # Enrichment: NER, classification, severity
            entities = extract_threat_entities(text)
            threat_type = classify_threat(text)
            severity = predict_severity(text)

            entry.update({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "entities": entities,
                "threat_type": str(threat_type),
                "severity": str(severity)
            })

            enriched_entries.append(entry)

        except Exception as e:
            print(f"[WARN] Failed to process entry: {e}")

    # Save to JSONL
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for entry in enriched_entries:
            f.write(json.dumps(entry) + "\n")

    # Save status file
    status_data = {
        "last_run": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "total_records": len(enriched_entries)
    }
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2)

    print(f"[INFO] Ingestion Summary: {status_data}")

if __name__ == "__main__":
    main()
