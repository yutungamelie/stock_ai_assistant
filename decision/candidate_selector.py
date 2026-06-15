from typing import Any

from data.tickers import TAIWAN_STOCKS
from quant.scoring import calculate_stock_score


def rank_candidate_stocks(
    top_n: int = 5,
    ticker_pool: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    對股票清單中的每一檔股票 / ETF 計算量化分數，並依總分排序。
    可選擇只掃描指定股票池。
    """
    results = []

    tickers = ticker_pool if ticker_pool else list(TAIWAN_STOCKS.keys())

    for ticker in tickers:
        try:
            score = calculate_stock_score(ticker)
            results.append(score)
        except Exception as e:
            print(f"略過 {ticker}，原因：{e}")

    results = sorted(
        results,
        key=lambda x: x["total_score"],
        reverse=True,
    )

    return results[:top_n]


def format_candidate_scores(candidates: list[dict[str, Any]]) -> str:
    """
    把候選股分數整理成給 LLM 看得懂的文字。
    """
    lines = []

    for i, stock in enumerate(candidates, start=1):
        lines.append(
            f"""
候選標的 {i}
股票代號：{stock["ticker"]}
股票名稱：{stock["name"]}
類型：{stock["type"]}
產業：{stock["industry"]}
資料日期：{stock["date"]}

最新收盤價：{stock["close"]}
MA20：{stock["ma20"]}
MA60：{stock["ma60"]}
RSI14：{stock["rsi14"]}
20 日報酬率：{stock["return_20d"]}%
20 日波動率：{stock["volatility_20d"]}%

趨勢分數：{stock["trend_score"]}
動能分數：{stock["momentum_score"]}
風險分數：{stock["risk_score"]}
總分：{stock["total_score"]}
初步決策：{stock["action"]}
""".strip()
        )

    return "\n\n---\n\n".join(lines)


if __name__ == "__main__":
    candidates = rank_candidate_stocks(top_n=5)
    print(format_candidate_scores(candidates))