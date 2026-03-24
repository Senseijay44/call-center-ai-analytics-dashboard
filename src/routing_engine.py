from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum

import pandas as pd

from src.config import RoutingConfig


class RoutingAction(str, Enum):
    AI_HANDLE = "AI_HANDLE"
    HUMAN_ESCALATE = "HUMAN_ESCALATE"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    PRIORITY_ESCALATE = "PRIORITY_ESCALATE"


@dataclass
class RoutingSignals:
    sentiment_negative: bool
    priority_intent: bool
    review_intent: bool
    frustration_hits: int
    escalation_hits: int
    low_confidence: bool


class RoutingEngine:
    def __init__(self, config: RoutingConfig | None = None) -> None:
        self.config = config or RoutingConfig()

    @staticmethod
    def _as_text(value: object) -> str:
        if pd.isna(value):
            return ""
        return str(value).strip().lower()

    def detect_signals(
        self,
        row: pd.Series,
        sentiment_col: str | None,
        call_type_col: str | None,
        transcript_col: str | None,
        confidence_col: str | None,
    ) -> RoutingSignals:
        sentiment = self._as_text(row.get(sentiment_col, "")) if sentiment_col else ""
        call_type = self._as_text(row.get(call_type_col, "")) if call_type_col else ""
        transcript = self._as_text(row.get(transcript_col, "")) if transcript_col else ""

        sentiment_negative = sentiment in self.config.negative_sentiments
        priority_intent = any(token in call_type for token in self.config.priority_call_types)
        review_intent = any(token in call_type for token in self.config.review_call_types)

        frustration_hits = sum(1 for token in self.config.frustration_keywords if token in transcript)
        escalation_hits = sum(1 for token in self.config.escalation_keywords if token in transcript)

        confidence = row.get(confidence_col) if confidence_col else None
        low_confidence = False
        if confidence is not None and not pd.isna(confidence):
            low_confidence = float(confidence) < self.config.low_confidence_threshold

        return RoutingSignals(
            sentiment_negative=sentiment_negative,
            priority_intent=priority_intent,
            review_intent=review_intent,
            frustration_hits=frustration_hits,
            escalation_hits=escalation_hits,
            low_confidence=low_confidence,
        )

    def route(self, signals: RoutingSignals) -> tuple[RoutingAction, str]:
        if signals.priority_intent or signals.escalation_hits >= 2:
            return RoutingAction.PRIORITY_ESCALATE, "High-risk intent or repeated explicit escalation language detected."

        if signals.sentiment_negative and (
            signals.frustration_hits >= self.config.frustration_score_threshold or signals.low_confidence
        ):
            return RoutingAction.HUMAN_ESCALATE, "Negative sentiment combined with frustration or low model confidence."

        if signals.review_intent or signals.low_confidence:
            return RoutingAction.HUMAN_REVIEW, "Potentially complex issue or uncertain model confidence requires human validation."

        return RoutingAction.AI_HANDLE, "Low-risk interaction suitable for AI-first handling."


def apply_routing(
    df: pd.DataFrame,
    col_map: dict,
    config: RoutingConfig | None = None,
) -> pd.DataFrame:
    """Apply routing decisions to each interaction record."""
    engine = RoutingEngine(config)
    routed_rows: list[dict] = []
    confidence_col = col_map.get("confidence")

    for _, row in df.iterrows():
        signals = engine.detect_signals(
            row=row,
            sentiment_col=col_map.get("sentiment"),
            call_type_col=col_map.get("call_type"),
            transcript_col=col_map.get("transcript"),
            confidence_col=confidence_col,
        )
        action, reason = engine.route(signals)
        routed_rows.append(
            {
                "routing_action": action.value,
                "routing_reason": reason,
                **{f"signal_{k}": v for k, v in asdict(signals).items()},
            }
        )

    return pd.concat([df.reset_index(drop=True), pd.DataFrame(routed_rows)], axis=1)


def routing_distribution(routed_df: pd.DataFrame) -> pd.DataFrame:
    if "routing_action" not in routed_df.columns:
        return pd.DataFrame(columns=["routing_action", "count"])

    distribution = routed_df["routing_action"].value_counts().reset_index()
    distribution.columns = ["routing_action", "count"]
    return distribution


def trigger_summary(routed_df: pd.DataFrame) -> pd.DataFrame:
    trigger_cols = [
        "signal_sentiment_negative",
        "signal_priority_intent",
        "signal_review_intent",
        "signal_low_confidence",
    ]

    existing = [col for col in trigger_cols if col in routed_df.columns]
    if not existing:
        return pd.DataFrame(columns=["trigger", "count"])

    summary = routed_df[existing].sum().reset_index()
    summary.columns = ["trigger", "count"]
    summary["trigger"] = summary["trigger"].str.replace("signal_", "", regex=False)
    return summary.sort_values("count", ascending=False)
