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
from src.insights import generate_insights
from src.preprocessing import clean_dataframe, get_column_map
from src.routing_engine import apply_routing, routing_distribution, trigger_summary
from src.simulation import simulate_queue
from src.summarizer import generate_handoff_examples

st.set_page_config(page_title="Call Center Decision Engine", page_icon="📞", layout="wide")

st.title("📞 AI-Assisted Call Center Decision Engine Prototype")
st.markdown(
    """
This dashboard now combines descriptive analytics with a rules-based routing engine to simulate
how an AI-first support operation decides whether to keep, review, or escalate customer interactions.
"""
)


@st.cache_data
def load_data():
    df = load_best_dataset()
    df = clean_dataframe(df)
    return df


try:
    df = load_data()
    col_map = get_column_map(df)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

st.subheader("Dataset Overview")
st.write(f"Source file: `{df['source_file'].iloc[0]}`")
st.write(f"Rows: {len(df):,} | Columns: {len(df.columns)}")

with st.expander("View detected columns"):
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

st.sidebar.header("Routing Thresholds")
low_conf = st.sidebar.slider("Low confidence threshold", min_value=0.10, max_value=0.95, value=0.45, step=0.05)
frustration_threshold = st.sidebar.slider("Frustration keyword threshold", min_value=1, max_value=4, value=2, step=1)

routing_cfg = RoutingConfig(
    low_confidence_threshold=low_conf,
    frustration_score_threshold=frustration_threshold,
)

routed_df = apply_routing(working_df, col_map, config=routing_cfg)

kpis = basic_kpis(working_df, col_map)
c1, c2, c3 = st.columns(3)
c1.metric("Total Calls", f"{kpis['total_calls']:,}")
c2.metric("Complaint Rate", f"{kpis['complaint_rate']:.1%}")
c3.metric("Negative Sentiment Rate", f"{kpis['negative_rate']:.1%}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Call Type Distribution")
    if col_map["call_type"]:
        call_type_df = value_counts_table(working_df, col_map["call_type"], top_n=15)
        fig = px.bar(call_type_df, x="value", y="count")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No call type column detected.")

with col2:
    st.subheader("Sentiment Distribution")
    if col_map["sentiment"]:
        sentiment_df = value_counts_table(working_df, col_map["sentiment"], top_n=15)
        fig = px.pie(sentiment_df, names="value", values="count")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sentiment column detected.")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Routing Decision Distribution")
    route_df = routing_distribution(routed_df)
    if not route_df.empty:
        fig = px.bar(route_df, x="routing_action", y="count", color="routing_action")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No routing decisions available.")

with col4:
    st.subheader("Escalation Trigger Signals")
    trigger_df = trigger_summary(routed_df)
    if not trigger_df.empty:
        fig = px.bar(trigger_df, x="trigger", y="count")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No routing trigger signals available.")

st.header("🤖 AI Optimization Insights")
auto_df = automation_candidates(working_df, col_map)
esc_df = escalation_candidates(working_df, col_map)
left, right = st.columns(2)

with left:
    st.subheader("Automation Candidates")
    if not auto_df.empty:
        display_df = auto_df.copy()
        display_df["negative_rate"] = display_df["negative_rate"].map(lambda x: f"{x:.1%}")
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("Insufficient columns to identify automation candidates.")

with right:
    st.subheader("Escalation Risk Areas")
    if not esc_df.empty:
        st.dataframe(esc_df, use_container_width=True)
    else:
        st.info("Insufficient columns to identify escalation risks.")

st.header("🧾 Escalation Handoff Summaries")
handoff_examples = generate_handoff_examples(routed_df, col_map, limit=5)
if handoff_examples.empty:
    st.info("No escalated records currently available for handoff previews.")
else:
    st.dataframe(handoff_examples, use_container_width=True)

st.header("⏱️ Simulated Live Queue")
max_records = st.slider("Records to simulate", min_value=10, max_value=min(200, len(routed_df)), value=min(50, len(routed_df)), step=10)
queue_df = simulate_queue(routed_df, timestamp_col=col_map.get("timestamp"), max_records=max_records)
st.dataframe(queue_df, use_container_width=True)

queue_action_summary = queue_df["routing_action"].value_counts().reset_index()
queue_action_summary.columns = ["routing_action", "count"]
if not queue_action_summary.empty:
    fig = px.line(queue_action_summary, x="routing_action", y="count", markers=True)
    st.plotly_chart(fig, use_container_width=True)

st.header("🧠 Strategic Recommendations")
insights = generate_insights(kpis, auto_df, esc_df)
for insight in insights:
    st.markdown(f"- {insight}")

st.header("📄 Sample Routed Records")
st.dataframe(routed_df.head(25), use_container_width=True)

st.subheader("Negative Sentiment by Call Type")
neg_call_df = negative_by_call_type(working_df, col_map)
if not neg_call_df.empty:
    fig = px.bar(neg_call_df, x="call_type", y="negative_calls")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Insufficient columns to calculate negative sentiment by call type.")
