import os
import requests
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

# Keywords to track
QUERY = "phishing OR ransomware OR zero-day OR exploit lang:en"
MAX_RESULTS = 10  # adjust as needed

def create_headers():
    return {"Authorization": f"Bearer {BEARER_TOKEN}"}

def fetch_twitter():
    """
    Fetch recent threat chatter tweets from Twitter API v2
    """
    if not BEARER_TOKEN:
        print("[ERROR] Missing Twitter Bearer Token in .env")
        return []

    params = {
        "query": QUERY,
        "max_results": MAX_RESULTS,
        "tweet.fields": "created_at,lang"
    }

    try:
        response = requests.get(SEARCH_URL, headers=create_headers(), params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for tweet in data.get("data", []):
            results.append({
                "source": "twitter",
                "text": tweet["text"],
                "metadata": {
                    "id": tweet["id"],
                    "created_at": tweet["created_at"],
                    "lang": tweet["lang"]
                }
            })
        return results

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Twitter API request failed: {e}")
        return []
