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
    confidence_gap: float
    risk_score: float
    uncertain_case: bool


class RoutingEngine:
    def __init__(self, config: RoutingConfig | None = None) -> None:
        self.config = config or RoutingConfig()

    @staticmethod
    def _as_text(value: object) -> str:
        if pd.isna(value):
            return ""
        return str(value).strip().lower()

    @staticmethod
    def _safe_float(value: object, default: float = 0.0) -> float:
        try:
            if value is None or pd.isna(value):
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    def _compute_risk_score(self, signals: dict, confidence_gap: float) -> tuple[float, list[str]]:
        contributions = {
            "sentiment_negative": self.config.w_sentiment_negative if signals["sentiment_negative"] else 0.0,
            "priority_intent": self.config.w_priority_intent if signals["priority_intent"] else 0.0,
            "review_intent": self.config.w_review_intent if signals["review_intent"] else 0.0,
            "frustration_hits": min(3, signals["frustration_hits"]) * self.config.w_frustration_hit,
            "escalation_hits": min(3, signals["escalation_hits"]) * self.config.w_escalation_hit,
            "low_confidence": self.config.w_low_confidence if signals["low_confidence"] else 0.0,
            "confidence_gap": confidence_gap * self.config.w_confidence_gap,
        }
        risk_score = max(0.0, min(1.0, sum(contributions.values())))
        top_reasons = [
            name for name, _ in sorted(contributions.items(), key=lambda item: item[1], reverse=True) if _ > 0
        ][:3]
        return risk_score, top_reasons

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

        confidence = self._safe_float(row.get(confidence_col) if confidence_col else None, default=1.0)
        low_confidence = confidence < self.config.low_confidence_threshold
        confidence_gap = max(0.0, self.config.medium_confidence_threshold - confidence)

        signal_dict = {
            "sentiment_negative": sentiment_negative,
            "priority_intent": priority_intent,
            "review_intent": review_intent,
            "frustration_hits": frustration_hits,
            "escalation_hits": escalation_hits,
            "low_confidence": low_confidence,
        }
        risk_score, _ = self._compute_risk_score(signal_dict, confidence_gap)
        uncertain_case = self.config.uncertainty_low <= risk_score <= self.config.uncertainty_high

        return RoutingSignals(
            sentiment_negative=sentiment_negative,
            priority_intent=priority_intent,
            review_intent=review_intent,
            frustration_hits=frustration_hits,
            escalation_hits=escalation_hits,
            low_confidence=low_confidence,
            confidence_gap=confidence_gap,
            risk_score=risk_score,
            uncertain_case=uncertain_case,
        )

    def route(self, signals: RoutingSignals) -> tuple[RoutingAction, str]:
        signal_dict = asdict(signals)
        risk_score, top_reasons = self._compute_risk_score(signal_dict, signals.confidence_gap)
        explain = ", ".join(top_reasons) if top_reasons else "low observed risk signals"

        if (
            signals.priority_intent
            or signals.escalation_hits >= 2
            or risk_score >= self.config.priority_risk_threshold
        ):
            return (
                RoutingAction.PRIORITY_ESCALATE,
                f"Risk score {risk_score:.2f} crossed priority threshold. Drivers: {explain}.",
            )

        if risk_score >= self.config.escalate_risk_threshold:
            return (
                RoutingAction.HUMAN_ESCALATE,
                f"Risk score {risk_score:.2f} indicates elevated resolution risk. Drivers: {explain}.",
            )

        if signals.uncertain_case or signals.review_intent or signals.low_confidence:
            return (
                RoutingAction.HUMAN_REVIEW,
                f"Risk score {risk_score:.2f} is in a gray zone or confidence is limited. Drivers: {explain}.",
            )

        return RoutingAction.AI_HANDLE, f"Risk score {risk_score:.2f} supports AI-first handling. Drivers: {explain}."


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
        "signal_uncertain_case",
    ]

    existing = [col for col in trigger_cols if col in routed_df.columns]
    if not existing:
        return pd.DataFrame(columns=["trigger", "count"])

    summary = routed_df[existing].sum().reset_index()
    summary.columns = ["trigger", "count"]
    summary["trigger"] = summary["trigger"].str.replace("signal_", "", regex=False)
    return summary.sort_values("count", ascending=False)
