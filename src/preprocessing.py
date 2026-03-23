import pandas as pd


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df


def find_best_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)

    # likely useful column guesses
    transcript_col = find_best_column(df, ["transcript", "text", "call_transcript"])
    sentiment_col = find_best_column(df, ["sentiment", "emotion", "sentiment_label"])
    call_type_col = find_best_column(df, ["call_type", "intent", "category"])
    product_col = find_best_column(df, ["product_code", "product", "product_id"])
    caller_col = find_best_column(df, ["caller_name", "customer_name", "name"])
    order_col = find_best_column(df, ["order_number", "order_id"])

    # fill missing values for common columns if they exist
    for col in [transcript_col, sentiment_col, call_type_col, product_col, caller_col, order_col]:
        if col and col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    # normalize sentiment labels
    if sentiment_col:
        df[sentiment_col] = df[sentiment_col].str.title()

    if call_type_col:
        df[call_type_col] = df[call_type_col].str.title()

    return df

def get_column_map(df: pd.DataFrame) -> dict:
    return {
        "transcript": find_best_column(df, [
            "transcript", "text", "call_transcript"
        ]),
        "sentiment": find_best_column(df, [
            "sentiment", "emotion", "sentiment_label"
        ]),
        "call_type": find_best_column(df, [
            "call_type", "type", "intent", "category", "issue_type",
            "call_category", "intent_label", "reason", "call_reason"
        ]),
        "product": find_best_column(df, [
            "product_code", "product", "product_id", "product_number",
            "item", "item_code", "sku", "product_name"
        ]),
        "caller": find_best_column(df, [
            "caller_name", "customer_name", "name"
        ]),
        "order": find_best_column(df, [
            "order_number", "order_id"
        ]),
        "timestamp": find_best_column(df, [
            "timestamp", "call_time", "datetime", "created_at"
        ]),
    }