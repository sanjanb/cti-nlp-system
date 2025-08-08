import snscrape.modules.twitter as sntwitter

def fetch_twitter(query="cybersecurity threat", limit=10):
    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= limit:
            break
        tweets.append({
            "source": "twitter",
            "text": tweet.content,
            "metadata": {
                "date": str(tweet.date),
                "username": tweet.user.username
            }
        })
    return tweets
