from __future__ import annotations

import pandas as pd


def decision_funnel_metrics(routed_df: pd.DataFrame) -> dict:
    if routed_df.empty or "routing_action" not in routed_df.columns:
        return {
            "automation_rate": 0.0,
            "escalation_rate": 0.0,
            "review_rate": 0.0,
            "priority_rate": 0.0,
            "mean_risk_score": 0.0,
            "mean_target_resolution_minutes": 0.0,
        }

    total = len(routed_df)
    action = routed_df["routing_action"]

    return {
        "automation_rate": float((action == "AI_HANDLE").sum() / total),
        "escalation_rate": float((action == "HUMAN_ESCALATE").sum() / total),
        "review_rate": float((action == "HUMAN_REVIEW").sum() / total),
        "priority_rate": float((action == "PRIORITY_ESCALATE").sum() / total),
        "mean_risk_score": float(routed_df.get("signal_risk_score", pd.Series([0])).mean()),
        "mean_target_resolution_minutes": float(
            routed_df.get("target_resolution_minutes", pd.Series([0])).mean()
        ),
    }


def rule_hit_table(routed_df: pd.DataFrame) -> pd.DataFrame:
    if "routing_rules" not in routed_df.columns:
        return pd.DataFrame(columns=["rule", "count"])

    exploded = (
        routed_df["routing_rules"]
        .fillna("")
        .str.split(",")
        .explode()
        .astype(str)
        .str.strip()
    )

    exploded = exploded[exploded != ""]
    if exploded.empty:
        return pd.DataFrame(columns=["rule", "count"])

    table = exploded.value_counts().reset_index()
    table.columns = ["rule", "count"]
    return table


def action_by_intent(routed_df: pd.DataFrame, call_type_col: str | None) -> pd.DataFrame:
    if not call_type_col or call_type_col not in routed_df.columns or "routing_action" not in routed_df.columns:
        return pd.DataFrame(columns=["call_type", "routing_action", "count"])

    grouped = (
        routed_df.groupby([call_type_col, "routing_action"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    grouped = grouped.rename(columns={call_type_col: "call_type"})
    return grouped
