from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

SYNTHETIC_CALLS = DATA_DIR / "synthetic_calls.csv"
RAW_TRANSCRIPTS = DATA_DIR / "call_transcripts.csv"
ENRICHED_V1 = DATA_DIR / "final_transcripts_enriched.csv"
ENRICHED_V2 = DATA_DIR / "final_transcripts_enriched_v2.csv"
DATA_DESCRIPTION = DATA_DIR / "data_description.csv"
AUDIO_DIR = DATA_DIR / "calls_audio"


@dataclass(frozen=True)
class RoutingConfig:
    """Configurable thresholds for rules-based routing decisions."""

    negative_sentiments: tuple[str, ...] = ("negative", "angry", "frustrated", "upset", "sad")
    priority_call_types: tuple[str, ...] = ("complaint", "billing dispute", "fraud", "account locked")
    review_call_types: tuple[str, ...] = ("cancellation", "technical support", "outage")

    frustration_keywords: tuple[str, ...] = (
        "supervisor",
        "manager",
        "cancel",
        "ridiculous",
        "unacceptable",
        "frustrated",
        "angry",
        "legal",
        "chargeback",
        "again",
    )
    escalation_keywords: tuple[str, ...] = (
        "escalate",
        "complaint",
        "refund now",
        "still not fixed",
        "not resolved",
        "file a claim",
        "formal complaint",
    )

    low_confidence_threshold: float = 0.45
    medium_confidence_threshold: float = 0.70
    frustration_score_threshold: int = 2

    ai_attempts_default: tuple[str, ...] = field(
        default_factory=lambda: (
            "Intent detection and knowledge-base lookup",
            "Generated policy-aligned response",
            "Attempted guided troubleshooting",
        )
    )
