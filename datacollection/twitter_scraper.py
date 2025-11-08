import csv
import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import random
import time
import json
from textblob import TextBlob  # simple sentiment analyzer
import re

# Public Nitter mirrors
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.lucabased.xyz",
    "https://nitter.nohost.network"
]

CACHE_FILE = "data/tweet_cache.json"
CACHE_DURATION = timedelta(minutes=10)  # cache lifespan

def load_cache():
    """Load cached tweet data from JSON file."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_cache(cache):
    """Save updated cache to file."""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def analyze_sentiment(text):
    """Return sentiment label based on polarity score."""
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"


def clean_text(text):
    """Clean tweet text: remove HTML tags, links, hashtags, emojis, and extra spaces."""
    text = re.sub(r"http\S+", "", text)                   # remove links
    text = re.sub(r"@\S+", "", text)                      # remove mentions (optional)
    text = re.sub(r"[\n\r]+", " ", text)                  # remove line breaks
    text = re.sub(r"[^\x00-\x7F]+", "", text)             # remove emojis/non-ASCII
    text = re.sub(r"\s+", " ", text)                      # collapse multiple spaces
    return text.strip()

def get_tweets(crypto_name, max_results=10):
    """Scrape or return cached tweets mentioning a cryptocurrency."""
    cache = load_cache()
    now = datetime.now()

    # Check cache first
    if crypto_name in cache:
        timestamp = datetime.fromisoformat(cache[crypto_name]["timestamp"])
        if now - timestamp < CACHE_DURATION:
            print(f"[CACHE] Returning cached tweets for {crypto_name}")
            return cache[crypto_name]["tweets"]

    # Otherwise, scrape from Nitter
    random.shuffle(NITTER_INSTANCES)
    tweets_data = []

    for base_url in NITTER_INSTANCES:
        try:
            params = {"q": f"{crypto_name} lang:en", "f": "tweets"}
            response = requests.get(f"{base_url}/search", params=params, timeout=10)

            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            tweets = soup.find_all("div", class_="timeline-item")

            for i, tweet in enumerate(tweets[:max_results]):
                content = tweet.find("div", class_="tweet-content")
                date = tweet.find("span", class_="tweet-date")
                stats = tweet.find_all("span", class_="tweet-stat")

                text = clean_text(content.text.strip()) if content else ""
                sentiment = analyze_sentiment(text)

                tweets_data.append({
                    "created_at": date.text.strip() if date else "",
                    "text": text,
                    "sentiment": sentiment,
                    "like_count": stats[0].text.strip() if len(stats) > 0 else "0",
                    "retweet_count": stats[1].text.strip() if len(stats) > 1 else "0",
                })

            if tweets_data:
                break  # success
        except Exception as e:
            print(f"[!] Failed with {base_url}: {e}")
            time.sleep(1)
            continue

    # Save to cache
    cache[crypto_name] = {
        "timestamp": now.isoformat(),
        "tweets": tweets_data
    }
    save_cache(cache)

    # Log to CSV (ML dataset building)
    with open("data/tweets_log.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(["timestamp", "crypto_name", "tweet_created_at", "text", "sentiment", "like_count", "retweet_count"])
        for tweet in tweets_data:
            writer.writerow([
                now.isoformat(),
                crypto_name,
                tweet["created_at"],
                tweet["text"],
                tweet["sentiment"],
                tweet["like_count"],
                tweet["retweet_count"]
            ])
    
    return tweets_data
