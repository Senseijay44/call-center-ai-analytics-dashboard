from __future__ import annotations

import pandas as pd


def _safe_text(row: pd.Series, col_name: str | None, fallback: str = "Unknown") -> str:
    if not col_name or col_name not in row.index:
        return fallback
    value = row[col_name]
    if pd.isna(value) or str(value).strip() == "":
        return fallback
    return str(value).strip()


def _truncate(text: str, max_chars: int = 220) -> str:
    return text if len(text) <= max_chars else f"{text[: max_chars - 3]}..."


def generate_handoff_summary(row: pd.Series, col_map: dict) -> str:
    issue = _safe_text(row, col_map.get("call_type"))
    sentiment = _safe_text(row, col_map.get("sentiment"))
    transcript = _truncate(_safe_text(row, col_map.get("transcript"), fallback="No transcript available"))
    action = _safe_text(row, "routing_action")
    reason = _safe_text(row, "routing_reason")

    signal_parts = []
    for col in [
        "signal_sentiment_negative",
        "signal_priority_intent",
        "signal_review_intent",
        "signal_low_confidence",
    ]:
        if col in row.index and bool(row[col]):
            signal_parts.append(col.replace("signal_", ""))

    frustration_hits = int(row.get("signal_frustration_hits", 0) or 0)
    escalation_hits = int(row.get("signal_escalation_hits", 0) or 0)
    signal_line = ", ".join(signal_parts) if signal_parts else "No boolean routing triggers"
    risk_score = float(row.get("signal_risk_score", 0.0) or 0.0)
    uncertain_case = bool(row.get("signal_uncertain_case", False))

    return (
        f"Issue Summary: Customer contacted support about '{issue}' with {sentiment.lower()} sentiment. "
        f"Transcript excerpt: \"{transcript}\"\n"
        f"Transfer Reason: Routed to {action} because {reason}\n"
        f"Signals Detected: {signal_line}; frustration_hits={frustration_hits}, escalation_hits={escalation_hits}.\n"
        f"Risk Context: weighted_risk_score={risk_score:.2f}; uncertain_case={uncertain_case}.\n"
        "AI Attempts: Intent classification, policy retrieval, and first-response generation were completed before transfer."
    )


def generate_handoff_examples(routed_df: pd.DataFrame, col_map: dict, limit: int = 5) -> pd.DataFrame:
    if "routing_action" not in routed_df.columns:
        return pd.DataFrame(columns=["routing_action", "handoff_summary"])

    escalated = routed_df[routed_df["routing_action"].isin(["HUMAN_ESCALATE", "PRIORITY_ESCALATE", "HUMAN_REVIEW"])].copy()
    if escalated.empty:
        return pd.DataFrame(columns=["routing_action", "handoff_summary"])

    examples = escalated.head(limit).copy()
    examples["handoff_summary"] = examples.apply(lambda row: generate_handoff_summary(row, col_map), axis=1)

    display_cols = [
        col
        for col in [col_map.get("call_type"), col_map.get("sentiment"), "routing_action", "handoff_summary"]
        if col and col in examples.columns
    ]
    return examples[display_cols]
