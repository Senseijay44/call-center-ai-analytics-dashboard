from __future__ import annotations

from dataclasses import replace

import pandas as pd

from src.config import RoutingConfig
from src.routing_engine import apply_routing


def estimate_policy_cost(routed_df: pd.DataFrame, config: RoutingConfig) -> dict:
    if routed_df.empty or "routing_action" not in routed_df.columns:
        return {
            "base_operation_cost": 0.0,
            "risk_penalty_cost": 0.0,
            "total_estimated_cost": 0.0,
            "high_risk_misses": 0,
            "priority_delays": 0,
        }

    action_cost_map = {
        "AI_HANDLE": config.ai_handle_cost,
        "HUMAN_REVIEW": config.human_review_cost,
        "HUMAN_ESCALATE": config.human_escalate_cost,
        "PRIORITY_ESCALATE": config.priority_escalate_cost,
    }

    eval_df = routed_df.copy()
    eval_df["base_cost"] = eval_df["routing_action"].map(action_cost_map).fillna(config.human_review_cost)

    high_risk_miss_mask = (eval_df["signal_risk_score"] >= config.escalate_risk_threshold) & (
        eval_df["routing_action"].isin(["AI_HANDLE", "HUMAN_REVIEW"])
    )
    priority_delay_mask = (eval_df["signal_risk_score"] >= config.priority_risk_threshold) & (
        eval_df["routing_action"] != "PRIORITY_ESCALATE"
    )

    high_risk_misses = int(high_risk_miss_mask.sum())
    priority_delays = int(priority_delay_mask.sum())

    risk_penalty_cost = (high_risk_misses * config.missed_high_risk_penalty) + (
        priority_delays * config.delayed_priority_penalty
    )
    base_operation_cost = float(eval_df["base_cost"].sum())

    return {
        "base_operation_cost": base_operation_cost,
        "risk_penalty_cost": risk_penalty_cost,
        "total_estimated_cost": base_operation_cost + risk_penalty_cost,
        "high_risk_misses": high_risk_misses,
        "priority_delays": priority_delays,
    }


def threshold_sweep(
    df: pd.DataFrame,
    col_map: dict,
    base_config: RoutingConfig,
    thresholds: list[float] | None = None,
) -> pd.DataFrame:
    thresholds = thresholds or [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]

    rows: list[dict] = []
    for threshold in thresholds:
        trial_cfg = replace(base_config, escalate_risk_threshold=threshold)
        trial_routed = apply_routing(df, col_map, config=trial_cfg)
        costs = estimate_policy_cost(trial_routed, trial_cfg)

        rows.append(
            {
                "escalate_risk_threshold": threshold,
                **costs,
                "ai_handle_rate": (trial_routed["routing_action"] == "AI_HANDLE").mean(),
            }
        )

    return pd.DataFrame(rows).sort_values("total_estimated_cost", ascending=True).reset_index(drop=True)
