import streamlit as st
import plotly.express as px

from src.data_loader import load_best_dataset
from src.preprocessing import clean_dataframe, get_column_map
from src.analytics import (
    basic_kpis,
    value_counts_table,
    negative_by_call_type,
    automation_candidates,
    escalation_candidates,
)
from src.insights import generate_insights

st.set_page_config(
    page_title="Call Center Intelligence Dashboard",
    page_icon="📞",
    layout="wide",
)

st.title("📞 AI-Ready Call Center Intelligence Dashboard")
st.markdown(
    """
Analyze customer support call data to identify:
- high-volume automation opportunities
- sentiment-driven escalation risks
- patterns that can improve AI-powered customer service design
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

# filters
st.sidebar.header("Filters")

working_df = df.copy()

if col_map["call_type"]:
    call_types = sorted(working_df[col_map["call_type"]].dropna().unique().tolist())
    selected_call_types = st.sidebar.multiselect(
        "Call Type",
        options=call_types,
        default=call_types,
    )
    if selected_call_types:
        working_df = working_df[working_df[col_map["call_type"]].isin(selected_call_types)]

if col_map["sentiment"]:
    sentiments = sorted(working_df[col_map["sentiment"]].dropna().unique().tolist())
    selected_sentiments = st.sidebar.multiselect(
        "Sentiment",
        options=sentiments,
        default=sentiments,
    )
    if selected_sentiments:
        working_df = working_df[working_df[col_map["sentiment"]].isin(selected_sentiments)]

# KPI section
kpis = basic_kpis(working_df, col_map)

c1, c2, c3 = st.columns(3)
c1.metric("Total Calls", f"{kpis['total_calls']:,}")
c2.metric("Complaint Rate", f"{kpis['complaint_rate']:.1%}")
c3.metric("Negative Sentiment Rate", f"{kpis['negative_rate']:.1%}")

# charts
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
    st.subheader("Negative Sentiment by Call Type")
    neg_call_df = negative_by_call_type(working_df, col_map)
    if not neg_call_df.empty:
        fig = px.bar(neg_call_df, x="call_type", y="negative_calls")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient columns to calculate negative sentiment by call type.")

with col4:
    st.subheader("Top Mentioned Products")
    if col_map["product"]:
        product_df = value_counts_table(working_df, col_map["product"], top_n=10)
        fig = px.bar(product_df, x="value", y="count")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No product column detected.")

# AI optimization section
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

# generated insights
st.header("🧠 Strategic Recommendations")
insights = generate_insights(kpis, auto_df, esc_df)

for insight in insights:
    st.markdown(f"- {insight}")

# sample records
st.header("📄 Sample Records")
st.dataframe(working_df.head(25), use_container_width=True)