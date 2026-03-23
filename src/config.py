from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

SYNTHETIC_CALLS = DATA_DIR / "synthetic_calls.csv"
RAW_TRANSCRIPTS = DATA_DIR / "call_transcripts.csv"
ENRICHED_V1 = DATA_DIR / "final_transcripts_enriched.csv"
ENRICHED_V2 = DATA_DIR / "final_transcripts_enriched_v2.csv"
DATA_DESCRIPTION = DATA_DIR / "data_description.csv"
AUDIO_DIR = DATA_DIR / "calls_audio"