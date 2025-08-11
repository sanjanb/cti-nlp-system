# data_ingestion/fetch_twitter.py
import os
import time
import requests
import json

CACHE_FILE = "data/cache_twitter.json"

def fetch_twitter():
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        print("[ERROR] Missing Twitter Bearer Token in .env")
        return load_cache()

    url = "https://api.twitter.com/2/tweets/search/recent"
    query = {
        "query": "phishing OR ransomware OR zero-day OR exploit lang:en",
        "max_results": 10,
        "tweet.fields": "created_at,lang"
    }
    headers = {"Authorization": f"Bearer {bearer_token}"}

    try:
        resp = requests.get(url, headers=headers, params=query)

        # Handle rate limit (HTTP 429)
        if resp.status_code == 429:
            print("[WARN] Twitter API rate limit hit. Using cached tweets.")
            return load_cache()

        resp.raise_for_status()
        data = resp.json()

        tweets = []
        for tw in data.get("data", []):
            tweets.append({
                "source": "twitter",
                "text": tw.get("text", ""),
                "metadata": {
                    "id": tw.get("id"),
                    "created_at": tw.get("created_at"),
                    "lang": tw.get("lang")
                }
            })

        # Save to cache for fallback use
        save_cache(tweets)
        return tweets

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Twitter API request failed: {e}")
        return load_cache()

def save_cache(tweets):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
