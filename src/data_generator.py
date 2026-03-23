import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SOURCE_FILE = DATA_DIR / "final_transcripts_enriched_v2.csv"
OUTPUT_FILE = DATA_DIR / "synthetic_calls.csv"


def generate_synthetic_calls(base_df: pd.DataFrame, n_samples: int = 3000) -> pd.DataFrame:
    df = base_df.copy()
    rows = []

    sentiment_candidates = ["Positive", "Neutral", "Negative", "Frustrated", "Angry"]

    for _ in range(n_samples):
        sample = df.sample(1, replace=True).iloc[0].to_dict()

        sample["call_id"] = f"C{random.randint(100000, 999999)}"

        start_date = datetime.now() - timedelta(days=90)
        sample["timestamp"] = start_date + timedelta(
            seconds=random.randint(0, 90 * 24 * 60 * 60)
        )

        if "sentiment" in sample and random.random() < 0.2:
            sample["sentiment"] = random.choice(sentiment_candidates)

        rows.append(sample)

    synthetic_df = pd.DataFrame(rows)
    return synthetic_df


def main():
    print(f"Reading source file from: {SOURCE_FILE}")

    if not SOURCE_FILE.exists():
        available = [p.name for p in DATA_DIR.glob("*.csv")]
        raise FileNotFoundError(
            f"Could not find {SOURCE_FILE.name} in {DATA_DIR}. "
            f"Available CSV files: {available}"
        )

    df = pd.read_csv(SOURCE_FILE)
    synthetic_df = generate_synthetic_calls(df, n_samples=3000)
    synthetic_df.to_csv(OUTPUT_FILE, index=False)

    print(f"Generated synthetic dataset: {len(synthetic_df):,} rows")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()