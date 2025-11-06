import requests
import os
import csv
from datetime import datetime

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
BASE_URL = "https://api.coingecko.com/api/v3"

def get_crypto_data(vs_currency="usd", per_page=10):
    """Fetch top cryptocurrencies by market cap and log them."""
    url = f"{BASE_URL}/coins/markets"
    headers = {"accept": "application/json", "x-cg-demo-api-key": COINGECKO_API_KEY}
    params = {"vs_currency": vs_currency, "order": "market_cap_desc", "per_page": per_page, "page": 1}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    # Log CoinGecko data to CSV for ML dataset building
    with open("market_log.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for crypto in data:
            writer.writerow([
                datetime.now().isoformat(),
                crypto["id"],
                crypto.get("current_price"),
                crypto.get("market_cap"),
                crypto.get("total_volume"),
                crypto.get("price_change_percentage_24h")
            ])

    return data
