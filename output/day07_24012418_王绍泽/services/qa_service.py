# cspell:ignore PreferedOrderCat
from pathlib import Path

import pandas as pd

# 替换原来的 from services.utils import ...
from .utils import get_riskiest_segment, to_float, to_int, to_str

def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def answer_question(base_dir: Path, question: str) -> str:
    data_dir = base_dir / "data"
    metrics_df = _read_csv(data_dir / "overall_metrics.csv")
    metrics: dict[str, str] = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    category_df = _read_csv(data_dir / "category_analysis.csv")
    segment_df = _read_csv(data_dir / "segment_analysis.csv")

    normalized = question.replace(" ", "").lower()

    if any(word in normalized for word in ["多少用户", "用户数", "总用户"]):
        return f"数据集中共有{to_int(metrics['用户数']):,}名用户。"


    # 每个回答都必须引用data目录中已经计算的指标，不得编造数值。
    if any(word in normalized for word in ["流失率", "流失情况", "流失多少"]):
        churn = to_int(metrics["流失人数"])
        rate = to_float(metrics["流失率"])
        return f"总体流失率为 {rate:.2%}（{churn:,} / {to_int(metrics['用户数']):,} 人）。"

    if any(word in normalized for word in ["偏好品类", "哪个品类", "品类最多", "最多品类"]):
        top_idx = to_int(category_df["用户数"].idxmax())
        top_cat = to_str(category_df.at[top_idx, "PreferedOrderCat"])
        top_users = to_int(category_df.at[top_idx, "用户数"])
        top_ratio = to_float(category_df.at[top_idx, "用户占比"])
        return (
            f"用户最多的偏好品类是『{top_cat}』，"
            f"共 {top_users:,} 人，占比 {top_ratio:.2%}。"
        )

    if any(word in normalized for word in ["生命周期", "阶段", "风险", "哪一段"]):
        risk = get_riskiest_segment(segment_df)
        return (
            f"流失率最高的生命周期阶段是『{risk['stage']}』，"
            f"流失率达 {risk['churn_rate']:.2%}（{risk['churn_count']:,} / {risk['user_count']:,} 人）。"
        )

    if any(word in normalized for word in ["订单", "平均订单", "订单数"]):
        avg = to_float(metrics["平均订单数"])
        median = to_float(metrics["订单数中位数"])
        return f"平均订单数为 {avg:.2f} 单，订单数中位数为 {median:.0f} 单。"

    return (
        "暂不支持这个问题。可尝试：总用户数 / 总体流失率 / 偏好品类 / 生命周期风险 / 平均订单数。"
    )
