import os
import time
import pandas as pd
from datetime import datetime, timezone
from textblob import TextBlob
import requests

OUTPUT_FILE = "/data/crypto_reddit.csv"
COINS = ["solana", "ethereum", "cardano"]
INTERVAL = 60  # every 1 minute

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_posts(coin):
    url = f"https://www.reddit.com/r/cryptocurrency/search.json?q={coin}&restrict_sr=1&sort=new&limit=20"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching posts for {coin}: {e}")
        return []

    rows = []
    for post in data.get("data", {}).get("children", []):
        text = post["data"].get("title", "")
        if text:
            sentiment = TextBlob(text).sentiment.polarity
            rows.append({
                "timestamp": datetime.now(timezone.utc),
                "coin": coin,
                "post_text": text,
                "sentiment_score": sentiment
            })
    return rows

def main():
    os.makedirs("/data", exist_ok=True)
    
    while True:
        all_rows = []
        for coin in COINS:
            rows = fetch_posts(coin)
            all_rows.extend(rows)
        
        if all_rows:  # only write if there are posts
            df = pd.DataFrame(all_rows)
            df.to_csv(
                OUTPUT_FILE,
                index=False,
                header=not os.path.exists(OUTPUT_FILE),
                mode='a'
            )
            print(f"[{datetime.now(timezone.utc)}] Reddit sentiment saved ({len(df)} posts).")
        else:
            print(f"[{datetime.now(timezone.utc)}] No posts fetched this cycle.")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
