import pandas as pd


def basic_kpis(df: pd.DataFrame, col_map: dict) -> dict:
    sentiment_col = col_map["sentiment"]
    call_type_col = col_map["call_type"]

    total_calls = len(df)

    complaints = 0
    if call_type_col:
        complaints = (df[call_type_col].str.lower() == "complaint").sum()

    negative_calls = 0
    if sentiment_col:
        negative_calls = df[sentiment_col].str.lower().isin(
            ["negative", "angry", "frustrated", "upset", "sad"]
        ).sum()

    return {
        "total_calls": total_calls,
        "complaint_calls": complaints,
        "negative_calls": negative_calls,
        "complaint_rate": complaints / total_calls if total_calls else 0,
        "negative_rate": negative_calls / total_calls if total_calls else 0,
    }


def value_counts_table(df: pd.DataFrame, column: str, top_n: int = 10) -> pd.DataFrame:
    if not column or column not in df.columns:
        return pd.DataFrame(columns=["value", "count"])

    counts = (
        df[column]
        .value_counts(dropna=False)
        .head(top_n)
        .reset_index()
    )
    counts.columns = ["value", "count"]
    return counts


def negative_by_call_type(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    sentiment_col = col_map["sentiment"]
    call_type_col = col_map["call_type"]

    if not sentiment_col or not call_type_col:
        return pd.DataFrame(columns=["call_type", "negative_calls"])

    negative_mask = df[sentiment_col].str.lower().isin(
        ["negative", "angry", "frustrated", "upset", "sad"]
    )

    result = (
        df.loc[negative_mask]
        .groupby(call_type_col)
        .size()
        .reset_index(name="negative_calls")
        .sort_values("negative_calls", ascending=False)
    )
    result.columns = ["call_type", "negative_calls"]
    return result


def automation_candidates(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    sentiment_col = col_map["sentiment"]
    call_type_col = col_map["call_type"]

    if not sentiment_col or not call_type_col:
        return pd.DataFrame(columns=["call_type", "total_calls", "negative_rate", "automation_score"])

    summary = (
        df.groupby(call_type_col)
        .size()
        .reset_index(name="total_calls")
    )

    negative_mask = df[sentiment_col].str.lower().isin(
        ["negative", "angry", "frustrated", "upset", "sad"]
    )

    negative_summary = (
        df.loc[negative_mask]
        .groupby(call_type_col)
        .size()
        .reset_index(name="negative_calls")
    )

    merged = summary.merge(negative_summary, on=call_type_col, how="left")
    merged["negative_calls"] = merged["negative_calls"].fillna(0)
    merged["negative_rate"] = merged["negative_calls"] / merged["total_calls"]

    # simple heuristic:
    # high volume + low negative rate = strong automation candidate
    merged["automation_score"] = merged["total_calls"] * (1 - merged["negative_rate"])
    merged = merged.sort_values("automation_score", ascending=False)

    merged.columns = ["call_type", "total_calls", "negative_calls", "negative_rate", "automation_score"]
    return merged

def escalation_candidates(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    sentiment_col = col_map["sentiment"]
    call_type_col = col_map["call_type"]

    if not sentiment_col or not call_type_col:
        return pd.DataFrame(columns=["call_type", "negative_calls"])

    negative_mask = df[sentiment_col].str.lower().isin(
        ["negative", "angry", "frustrated", "upset", "sad"]
    )

    result = (
        df.loc[negative_mask]
        .groupby(call_type_col)
        .size()
        .reset_index(name="negative_calls")
        .sort_values("negative_calls", ascending=False)
    )

    result.columns = ["call_type", "negative_calls"]
    return result