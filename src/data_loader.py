import pandas as pd
from src.config import SYNTHETIC_CALLS, ENRICHED_V2, ENRICHED_V1, RAW_TRANSCRIPTS


def load_best_dataset() -> pd.DataFrame:
    """
    Load the best available dataset.

    Preference:
    1. synthetic_calls.csv
    2. final_transcripts_enriched_v2.csv
    3. final_transcripts_enriched.csv
    4. call_transcripts.csv
    """
    for path in [SYNTHETIC_CALLS, ENRICHED_V2, ENRICHED_V1, RAW_TRANSCRIPTS]:
        if path.exists():
            df = pd.read_csv(path)
            df["source_file"] = path.name
            return df

    raise FileNotFoundError("No transcript dataset found in /data folder.")