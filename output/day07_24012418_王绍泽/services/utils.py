"""Shared utilities for data services."""

from typing import Any

import pandas as pd


def to_str(value: Any) -> str:
    return str(value)


def to_int(value: Any) -> int:
    return int(value)


def to_float(value: Any) -> float:
    return float(value)


def get_riskiest_segment(segment_df: pd.DataFrame) -> dict[str, int | float | str]:
    """Return the segment row with the highest churn rate."""
    risk_idx = to_int(segment_df["流失率"].idxmax())
    return {
        "stage": to_str(segment_df.at[risk_idx, "TenureGroup"]),
        "churn_rate": to_float(segment_df.at[risk_idx, "流失率"]),
        "churn_count": to_int(segment_df.at[risk_idx, "流失人数"]),
        "user_count": to_int(segment_df.at[risk_idx, "用户数"]),
    }
