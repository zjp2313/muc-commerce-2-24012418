# cspell:ignore PreferedOrderCat
from pathlib import Path

import pandas as pd

# 替换原来的 from services.utils import ...
from .utils import get_riskiest_segment, to_float, to_int, to_str


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def load_dashboard_data(base_dir: Path, selected_category: str = "全部") -> dict:
    data_dir = base_dir / "data"
    metrics_df = _read_csv(data_dir / "overall_metrics.csv")
    category_df = _read_csv(data_dir / "category_analysis.csv")
    segment_df = _read_csv(data_dir / "segment_analysis.csv")

    # 数据文件列名，Pylance 类型提示用 dict[str, str] 明确标量类型
    metric_map: dict[str, str] = dict(zip(metrics_df["指标"], metrics_df["数值"]))

    churn_rate = to_float(metric_map["流失率"])
    avg_orders = to_float(metric_map["平均订单数"])
    metrics = [
        {"label": "总用户数", "value": f"{to_int(metric_map['用户数']):,}", "note": "人"},
        {"label": "流失用户", "value": f"{to_int(metric_map['流失人数']):,}", "note": "人"},
        {"label": "总体流失率", "value": f"{churn_rate:.2%}", "note": f"流失 {to_int(metric_map['流失人数']):,} 人"},
        {"label": "平均订单数", "value": f"{avg_orders:.2f}", "note": "单 / 人"},
    ]

    # 拼写与原始数据文件保持一致（CSV 中为 PreferedOrderCat）
    categories = ["全部", *category_df["PreferedOrderCat"].tolist()]
    table_df = category_df.copy()


    if selected_category and selected_category != "全部":
        table_df = table_df[table_df["PreferedOrderCat"] == selected_category]

    table_df = table_df.rename(
        columns={
            "PreferedOrderCat": "偏好品类",
            "用户数": "用户数",
            "流失率": "流失率",
            "平均订单数": "平均订单数",
        }
    )[["偏好品类", "用户数", "流失率", "平均订单数"]]
    table_df["流失率"] = table_df["流失率"].map(lambda value: f"{to_float(value):.1%}")
    table_df["平均订单数"] = table_df["平均订单数"].map(lambda value: f"{to_float(value):.2f}")


    risk = get_riskiest_segment(segment_df)
    insight = (
        f"流失率最高的生命周期阶段是『{risk['stage']}』，"
        f"流失率达 {risk['churn_rate']:.2%}（{risk['churn_count']} / {risk['user_count']} 人），"
        f"建议在用户首单 30 天内加强引导与召回。"
    )

    return {
        "metrics": metrics,
        "categories": categories,
        "category_rows": table_df.to_dict("records"),
        "insight": insight,
    }


def load_segments_data(base_dir: Path) -> dict:
    """拓展 B：生命周期详情页数据"""
    data_dir = base_dir / "data"
    segment_df = _read_csv(data_dir / "segment_analysis.csv")

    risk = get_riskiest_segment(segment_df)
    rows = []
    for _, row in segment_df.iterrows():
        rows.append({
            "stage": to_str(row["TenureGroup"]),
            "user_count": to_int(row["用户数"]),
            "churn_count": to_int(row["流失人数"]),
            "churn_rate": f"{to_float(row['流失率']):.2%}",
            "avg_orders": f"{to_float(row['平均订单数']):.2f}",
            "avg_cashback": f"{to_float(row['平均返现']):.2f}",
            "avg_days": f"{to_float(row['平均距上次下单天数']):.2f}",
        })

    total_users = to_int(segment_df["用户数"].sum())
    total_churn = to_int(segment_df["流失人数"].sum())
    overall_rate = total_churn / total_users if total_users else 0.0

    return {
        "rows": rows,
        "total_users": f"{total_users:,}",
        "total_churn": f"{total_churn:,}",
        "overall_rate": f"{overall_rate:.2%}",
        "risk_stage": risk["stage"],
        "risk_rate": f"{risk['churn_rate']:.2%}",
        "risk_users": risk["user_count"],
        "risk_churn": risk["churn_count"],
    }
