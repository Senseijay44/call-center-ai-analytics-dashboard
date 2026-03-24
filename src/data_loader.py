from __future__ import annotations

import random
from datetime import datetime, timedelta

import pandas as pd

from src.config import ENRICHED_V1, ENRICHED_V2, RAW_TRANSCRIPTS, SYNTHETIC_CALLS


def _generate_demo_dataset(n_rows: int = 500) -> pd.DataFrame:
    """Fallback dataset to keep the app runnable even when CSV files are missing."""
    call_types = [
        "Billing Question",
        "Technical Support",
        "Complaint",
        "Order Status",
        "Cancellation",
        "Password Reset",
    ]
    sentiments = ["Positive", "Neutral", "Negative", "Frustrated", "Angry"]

    transcript_templates = {
        "Billing Question": "I need help understanding this charge on my account.",
        "Technical Support": "My service is still not fixed after troubleshooting.",
        "Complaint": "This is unacceptable and I want to escalate to a supervisor.",
        "Order Status": "Can you tell me where my order is right now?",
        "Cancellation": "Please cancel my plan immediately if this cannot be resolved.",
        "Password Reset": "I am locked out and need to reset my password.",
    }

    start = datetime.utcnow() - timedelta(days=60)
    rows = []
    for idx in range(n_rows):
        call_type = random.choices(call_types, weights=[22, 20, 16, 18, 10, 14], k=1)[0]
        sentiment = random.choices(sentiments, weights=[20, 35, 18, 17, 10], k=1)[0]
        rows.append(
            {
                "call_id": f"SIM-{idx+1:05d}",
                "timestamp": (start + timedelta(minutes=idx * 6)).isoformat(),
                "call_type": call_type,
                "sentiment": sentiment,
                "transcript": transcript_templates[call_type],
                "confidence": round(random.uniform(0.35, 0.98), 2),
                "source_file": "generated_demo_dataset",
            }
        )

    return pd.DataFrame(rows)


def load_best_dataset() -> pd.DataFrame:
    """
    Load the best available dataset.

    Preference:
    1. synthetic_calls.csv
    2. final_transcripts_enriched_v2.csv
    3. final_transcripts_enriched.csv
    4. call_transcripts.csv
    5. generated fallback dataset
    """
    for path in [SYNTHETIC_CALLS, ENRICHED_V2, ENRICHED_V1, RAW_TRANSCRIPTS]:
        if path.exists():
            df = pd.read_csv(path)
            df["source_file"] = path.name
            return df

    return _generate_demo_dataset()
