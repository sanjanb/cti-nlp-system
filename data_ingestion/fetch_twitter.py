import time
import requests

def fetch_twitter():
    import os
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        print("[ERROR] Missing Twitter Bearer Token in .env")
        return []

    url = "https://api.twitter.com/2/tweets/search/recent"
    query = {
        "query": "phishing OR ransomware OR zero-day OR exploit lang:en",
        "max_results": 10,
        "tweet.fields": "created_at,lang"
    }
    headers = {"Authorization": f"Bearer {bearer_token}"}

    try:
        resp = requests.get(url, headers=headers, params=query)
        if resp.status_code == 429:
            print("[WARN] Twitter API rate limit hit. Waiting 60 seconds...")
            time.sleep(60)
            resp = requests.get(url, headers=headers, params=query)

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
        return tweets

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Twitter API request failed: {e}")
        return []
