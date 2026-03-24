import plotly.express as px
import streamlit as st

from src.analytics import (
    automation_candidates,
    basic_kpis,
    escalation_candidates,
    negative_by_call_type,
    value_counts_table,
)
from src.config import RoutingConfig
from src.data_loader import load_best_dataset
from src.decision_support import action_by_intent, decision_funnel_metrics, rule_hit_table
from src.insights import generate_insights
from src.policy_optimizer import estimate_policy_cost, threshold_sweep
from src.preprocessing import clean_dataframe, get_column_map
from src.routing_engine import apply_routing, routing_distribution, trigger_summary
from src.simulation import simulate_queue
from src.summarizer import generate_handoff_examples

st.set_page_config(page_title="Call Center Decision Intelligence", page_icon="📞", layout="wide")

st.title("📞 Call Center Decision Intelligence Dashboard")
st.markdown(
    """
A portfolio-ready analytics app for AI-assisted support operations.  
It combines descriptive analytics, deterministic routing policy, explainable escalation rules,
and measurable cost/risk tradeoff analysis.
"""
)


@st.cache_data
def load_data():
    df = load_best_dataset()
    return clean_dataframe(df)


try:
    df = load_data()
    col_map = get_column_map(df)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

st.subheader("Dataset Overview")
st.write(f"Source file: `{df['source_file'].iloc[0]}`")
st.write(f"Rows: {len(df):,} | Columns: {len(df.columns)}")
with st.expander("Detected schema map"):
    st.json(col_map)

st.sidebar.header("Filters")
working_df = df.copy()

if col_map["call_type"]:
    call_types = sorted(working_df[col_map["call_type"]].dropna().unique().tolist())
    selected_call_types = st.sidebar.multiselect("Call Type", options=call_types, default=call_types)
    if selected_call_types:
        working_df = working_df[working_df[col_map["call_type"]].isin(selected_call_types)]

if col_map["sentiment"]:
    sentiments = sorted(working_df[col_map["sentiment"]].dropna().unique().tolist())
    selected_sentiments = st.sidebar.multiselect("Sentiment", options=sentiments, default=sentiments)
    if selected_sentiments:
        working_df = working_df[working_df[col_map["sentiment"]].isin(selected_sentiments)]

st.sidebar.header("Policy Controls")
low_conf = st.sidebar.slider("Low confidence threshold", min_value=0.10, max_value=0.95, value=0.45, step=0.05)
escalate_threshold = st.sidebar.slider("Escalate risk threshold", min_value=0.30, max_value=0.90, value=0.55, step=0.05)
priority_threshold = st.sidebar.slider("Priority risk threshold", min_value=0.60, max_value=0.98, value=0.82, step=0.02)

routing_cfg = RoutingConfig(
    low_confidence_threshold=low_conf,
    escalate_risk_threshold=escalate_threshold,
    priority_risk_threshold=priority_threshold,
)

routed_df = apply_routing(working_df, col_map, config=routing_cfg)
kpis = basic_kpis(working_df, col_map)
costs = estimate_policy_cost(routed_df, routing_cfg)
metrics = decision_funnel_metrics(routed_df)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Calls", f"{kpis['total_calls']:,}")
k2.metric("Negative Rate", f"{kpis['negative_rate']:.1%}")
k3.metric("Automation Rate", f"{metrics['automation_rate']:.1%}")
k4.metric("Est. Total Cost", f"${costs['total_estimated_cost']:,.0f}")

st.header("1) Demand and Service Mix")
c1, c2 = st.columns(2)
with c1:
    st.subheader("Call Type Distribution")
    if col_map["call_type"]:
        call_type_df = value_counts_table(working_df, col_map["call_type"], top_n=15)
        st.plotly_chart(px.bar(call_type_df, x="value", y="count"), use_container_width=True)
    else:
        st.info("No call type column detected.")

with c2:
    st.subheader("Sentiment Distribution")
    if col_map["sentiment"]:
        sentiment_df = value_counts_table(working_df, col_map["sentiment"], top_n=15)
        st.plotly_chart(px.pie(sentiment_df, names="value", values="count"), use_container_width=True)
    else:
        st.info("No sentiment column detected.")

st.header("2) Decision Policy Performance")
c3, c4 = st.columns(2)
with c3:
    st.subheader("Routing Decisions")
    route_df = routing_distribution(routed_df)
    if not route_df.empty:
        st.plotly_chart(px.bar(route_df, x="routing_action", y="count", color="routing_action"), use_container_width=True)

with c4:
    st.subheader("Top Escalation Triggers")
    trigger_df = trigger_summary(routed_df)
    if not trigger_df.empty:
        st.plotly_chart(px.bar(trigger_df, x="trigger", y="count"), use_container_width=True)

c5, c6 = st.columns(2)
with c5:
    st.subheader("Rule Hit Frequency")
    rules_df = rule_hit_table(routed_df)
    if not rules_df.empty:
        st.plotly_chart(px.bar(rules_df, x="rule", y="count"), use_container_width=True)

with c6:
    st.subheader("Risk Score Distribution")
    if "signal_risk_score" in routed_df.columns:
        st.plotly_chart(px.histogram(routed_df, x="signal_risk_score", nbins=20), use_container_width=True)

st.subheader("Action by Intent")
action_intent_df = action_by_intent(routed_df, col_map.get("call_type"))
if not action_intent_df.empty:
    st.plotly_chart(
        px.bar(action_intent_df, x="call_type", y="count", color="routing_action", barmode="stack"),
        use_container_width=True,
    )

st.header("3) Cost, Risk, and Policy Tuning")
p1, p2, p3, p4 = st.columns(4)
p1.metric("Base Ops Cost", f"${costs['base_operation_cost']:,.0f}")
p2.metric("Risk Penalty", f"${costs['risk_penalty_cost']:,.0f}")
p3.metric("High-Risk Misses", f"{costs['high_risk_misses']}")
p4.metric("Priority Delays", f"{costs['priority_delays']}")

sweep_df = threshold_sweep(working_df, col_map, routing_cfg)
st.caption("Threshold sweep exposes the cost/risk tradeoff to support policy selection.")
st.dataframe(sweep_df, use_container_width=True)

st.header("4) Operational Guidance")
auto_df = automation_candidates(working_df, col_map)
esc_df = escalation_candidates(working_df, col_map)
left, right = st.columns(2)
with left:
    st.subheader("Automation Candidates")
    if not auto_df.empty:
        display_df = auto_df.copy()
        display_df["negative_rate"] = display_df["negative_rate"].map(lambda x: f"{x:.1%}")
        st.dataframe(display_df, use_container_width=True)

with right:
    st.subheader("Escalation Risk Areas")
    if not esc_df.empty:
        st.dataframe(esc_df, use_container_width=True)

st.subheader("Handoff Summary Examples")
st.dataframe(generate_handoff_examples(routed_df, col_map, limit=5), use_container_width=True)

st.header("5) Queue Simulation")
max_records = st.slider("Records to simulate", min_value=10, max_value=min(200, len(routed_df)), value=min(50, len(routed_df)), step=10)
queue_df = simulate_queue(routed_df, timestamp_col=col_map.get("timestamp"), max_records=max_records)
st.dataframe(queue_df, use_container_width=True)

st.subheader("Recommendation Narrative")
insights = generate_insights(kpis, auto_df, esc_df, policy_costs=costs, decision_metrics=metrics)
for insight in insights:
    st.markdown(f"- {insight}")

st.subheader("Sample Routed Records")
st.dataframe(routed_df.head(25), use_container_width=True)

st.subheader("Negative Sentiment by Call Type")
neg_call_df = negative_by_call_type(working_df, col_map)
if not neg_call_df.empty:
    st.plotly_chart(px.bar(neg_call_df, x="call_type", y="negative_calls"), use_container_width=True)
