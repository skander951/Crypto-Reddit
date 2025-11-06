from fastapi import FastAPI
from coingecko_api import get_crypto_data
from twitter_scraper import get_tweets

app = FastAPI(title="Crypto & Tweets Scraper API")

@app.get("/")
def root():
    return {"message": "Welcome to the Crypto & Tweets Scraper API"}

@app.get("/top_cryptos")
def top_cryptos():
    """Return top cryptos from CoinGecko."""
    data = get_crypto_data()
    return {"count": len(data), "cryptos": data}

@app.get("/tweets/{crypto_name}")
def tweets(crypto_name: str):
    """Return latest tweets for a given cryptocurrency."""
    tweets_data = get_tweets(crypto_name)
    return {"count": len(tweets_data), "tweets": tweets_data}
