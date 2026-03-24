from __future__ import annotations

import pandas as pd


def simulate_queue(routed_df: pd.DataFrame, timestamp_col: str | None = None, max_records: int = 100) -> pd.DataFrame:
    """Simulate FIFO queue processing for routed interactions."""
    if routed_df.empty:
        return pd.DataFrame(columns=["queue_step", "routing_action", "routing_reason"])

    queue_df = routed_df.copy()

    if timestamp_col and timestamp_col in queue_df.columns:
        queue_df = queue_df.sort_values(timestamp_col)

    queue_df = queue_df.head(max_records).reset_index(drop=True)
    queue_df["queue_step"] = queue_df.index + 1

    cols = ["queue_step"]
    preferred = [timestamp_col, "routing_action", "routing_reason"]
    cols.extend([c for c in preferred if c and c in queue_df.columns])

    for candidate in ["signal_sentiment_negative", "signal_priority_intent", "signal_low_confidence"]:
        if candidate in queue_df.columns:
            cols.append(candidate)

    return queue_df[cols]
