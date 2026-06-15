import math
from typing import Any


DEFAULT_CASH = 70224

def is_valid_price(price: Any) -> bool:
    """
    檢查價格是否可以用來計算股數。
    避免 None、NaN、0 或負數造成錯誤。
    """
    try:
        price_float = float(price)
    except (TypeError, ValueError):
        return False

    if math.isnan(price_float):
        return False

    if price_float <= 0:
        return False

    return True

def calculate_position_plan(
    candidates: list[dict[str, Any]],
    total_cash: int = DEFAULT_CASH,
) -> list[dict[str, Any]]:
    """
    根據量化分數與風險控管，計算每檔建議配置金額與可買股數。

    規則：
    - ETF 單檔最高 45%
    - 個股單檔最高 30%
    - 初步決策為「避免」者不配置
    - 保留至少 20% 現金
    """
    investable_cash = int(total_cash * 0.8)
    plan = []

    valid_candidates = [
        stock for stock in candidates
        if stock["action"] != "避免"
        and is_valid_price(stock.get("close"))
    ]

    if not valid_candidates:
        return []

    total_score = sum(stock["total_score"] for stock in valid_candidates)

    for stock in valid_candidates:
        raw_weight = stock["total_score"] / total_score

        if stock["type"] == "ETF":
            max_weight = 0.45
        else:
            max_weight = 0.30

        final_weight = min(raw_weight, max_weight)

        suggested_amount = int(investable_cash * final_weight)
        close_price = float(stock["close"])

        if not is_valid_price(close_price):
            continue

        # 台股可以零股，所以用整股估算
        estimated_shares = int(suggested_amount // close_price)

        plan.append({
            "ticker": stock["ticker"],
            "name": stock["name"],
            "type": stock["type"],
            "close": stock["close"],
            "total_score": stock["total_score"],
            "action": stock["action"],
            "suggested_amount": suggested_amount,
            "estimated_shares": estimated_shares,
            "weight": round(final_weight * 100, 2),
        })

    used_cash = sum(item["suggested_amount"] for item in plan)
    remaining_cash = total_cash - used_cash

    for item in plan:
        item["remaining_cash_after_plan"] = remaining_cash

    return plan


def format_position_plan(plan: list[dict[str, Any]], total_cash: int = DEFAULT_CASH) -> str:
    if not plan:
        return "目前沒有適合配置的標的，建議保留現金並觀望。"

    lines = [
        f"可用資金：{total_cash:,} 元",
        "",
        "建議配置如下：",
    ]

    for item in plan:
        lines.append(
            f"""
股票代號：{item["ticker"]}
股票名稱：{item["name"]}
類型：{item["type"]}
最新收盤價：{item["close"]}
量化總分：{item["total_score"]}
初步決策：{item["action"]}
建議配置比例：{item["weight"]}%
建議配置金額：約 {item["suggested_amount"]:,} 元
估計可買股數：約 {item["estimated_shares"]} 股
""".strip()
        )

    lines.append("")
    lines.append(f"配置後預估剩餘現金：約 {plan[0]['remaining_cash_after_plan']:,} 元")

    return "\n\n---\n\n".join(lines)


if __name__ == "__main__":
    from decision.candidate_selector import rank_candidate_stocks

    candidates = rank_candidate_stocks(top_n=5)
    plan = calculate_position_plan(candidates)
    print(format_position_plan(plan))