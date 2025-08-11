## Documentation: Real-Time Ingestion Module\*\*

**### Overview**
We’ve added a **modular real-time ingestion pipeline** to your CTI-NLP system to pull threat intel from multiple sources and preprocess it before storage or classification.

**### Current Structure**

```
cti-nlp-system/
  data_ingestion/
    fetch_darkweb.py       # Dark web placeholder fetcher
    fetch_twitter.py       # Live Twitter fetcher (rate-limit safe)
    fetch_mitre_attack.py  # MITRE ATT&CK API fetcher
    preprocess.py          # Cleaning & text normalization
  scripts/
    ingest_all_sources.py  # Unified ingestion runner
  data/
    ingested_cti.jsonl     # Appended output of all runs
    cache_twitter.json     # Cached tweets for rate-limit fallback
```

**### How It Works**

1. **`ingest_all_sources.py`** calls all fetch functions:

   - `fetch_darkweb()` → placeholder scraping results
   - `fetch_twitter()` → Twitter API for threat chatter
   - `fetch_mitre_attack()` → MITRE TTP mappings

2. **Preprocessing**:

   - Standardizes text
   - Removes duplicates
   - Strips HTML / special characters

3. **Output Storage**:

   - Appends to `data/ingested_cti.jsonl`
   - Each record contains:

     ```json
     {
       "source": "twitter",
       "text": "Example tweet text",
       "metadata": {...},
       "timestamp": "2025-08-11T16:05:00Z"
     }
     ```

4. **Twitter API Safety**:

   - Caches latest tweets in `data/cache_twitter.json`
   - If rate-limited (HTTP 429) → loads from cache instead of breaking

**### Future Work**

- Connect this ingestion directly to your FastAPI backend in a **background thread** so it runs continuously.
- Add Telegram & dark web live scrapers.
- Push ingested data into a message queue (Kafka or Redis Streams) for real-time classification.

If you want, I can now **wire this ingestion into your FastAPI backend** so it runs continuously in the background without you having to run `ingest_all_sources.py` manually.
That would make it truly **real-time**.
