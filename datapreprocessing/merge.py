import pandas as pd

def preprocess_and_merge(market_file="data/market_log.csv", tweets_file="data/tweets_log.csv", output_file="merged_df.csv"):
    # Load datasets
    market_df = pd.read_csv(market_file)
    tweets_df = pd.read_csv(tweets_file)

    # --- Preprocessing: Market data ---
    market_df["timestamp"] = pd.to_datetime(market_df["timestamp"], errors="coerce")
    market_df = market_df.dropna(subset=["timestamp"])
    market_df = market_df.sort_values("timestamp")

    # --- Preprocessing: Tweets data ---
    tweets_df["timestamp"] = pd.to_datetime(tweets_df["timestamp"], errors="coerce")
    tweets_df = tweets_df.dropna(subset=["timestamp"])
    tweets_df = tweets_df.sort_values("timestamp")

    # --- Clean text columns ---
    if "text" in tweets_df.columns:
        tweets_df["text"] = tweets_df["text"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()

    # --- Merge: align tweets with nearest market data in time ---
    merged_df = pd.merge_asof(
        tweets_df,
        market_df,
        on="timestamp",
        direction="nearest",
        tolerance=pd.Timedelta("5min")  # adjust tolerance window if needed
    )

    # --- Drop rows where merge failed ---
    merged_df = merged_df.dropna(subset=["id", "price"])

    # --- Save final merged dataset ---
    merged_df.to_csv(output_file, index=False, encoding="utf-8")

    print(f"✅ Merged dataset saved to {output_file}")
    print(f"📊 Shape: {merged_df.shape}")
    return merged_df


if __name__ == "__main__":
    preprocess_and_merge()
