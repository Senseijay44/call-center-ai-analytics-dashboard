import pandas as pd


def generate_insights(
    kpis: dict,
    automation_df: pd.DataFrame,
    escalation_df: pd.DataFrame,
    policy_costs: dict | None = None,
    decision_metrics: dict | None = None,
) -> list[str]:
    insights = []

    insights.append(
        f"Total calls analyzed: {kpis['total_calls']:,}. Complaint rate: {kpis['complaint_rate']:.1%}. "
        f"Negative sentiment rate: {kpis['negative_rate']:.1%}."
    )

    if decision_metrics:
        insights.append(
            "Routing funnel: "
            f"AI_HANDLE={decision_metrics['automation_rate']:.1%}, "
            f"HUMAN_REVIEW={decision_metrics['review_rate']:.1%}, "
            f"HUMAN_ESCALATE={decision_metrics['escalation_rate']:.1%}, "
            f"PRIORITY_ESCALATE={decision_metrics['priority_rate']:.1%}."
        )

    if not automation_df.empty and "call_type" in automation_df.columns:
        top_auto = automation_df.iloc[0]
        insights.append(
            f"'{top_auto['call_type']}' appears to be the strongest automation candidate "
            "based on call volume and relatively lower negative sentiment."
        )

    if not escalation_df.empty and "call_type" in escalation_df.columns:
        top_escalation = escalation_df.iloc[0]
        insights.append(
            f"'{top_escalation['call_type']}' generates the highest volume of negative interactions "
            "and should likely retain human escalation pathways."
        )

    if policy_costs:
        insights.append(
            f"Current policy simulation estimates ${policy_costs['total_estimated_cost']:,.0f} total operating impact, "
            f"including {policy_costs['high_risk_misses']} high-risk misses and {policy_costs['priority_delays']} priority delays."
        )

    insights.append(
        "Policy is deterministic and auditable: each routed record stores explicit rule hits, risk score, and target resolution window."
    )

    return insights
