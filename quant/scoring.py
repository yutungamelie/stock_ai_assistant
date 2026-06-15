from typing import Any

import pandas as pd

from data.stock_prices import fetch_price_history
from data.stock_prices import get_stock_info
from data.stock_prices import normalize_ticker
from quant.indicators import add_technical_indicators


def clamp_score(score: float) -> int:
    """
    確保分數在 0～100 之間。
    """
    return int(max(0, min(100, round(score))))


def calculate_trend_score(latest: pd.Series) -> int:
    """
    趨勢分數：
    - 價格高於 MA20 加分
    - 價格高於 MA60 加分
    - MA20 高於 MA60 加分
    """
    score = 50

    close = latest["close"]
    ma20 = latest["ma20"]
    ma60 = latest["ma60"]

    if pd.notna(ma20) and close > ma20:
        score += 20
    elif pd.notna(ma20) and close < ma20:
        score -= 10

    if pd.notna(ma60) and close > ma60:
        score += 20
    elif pd.notna(ma60) and close < ma60:
        score -= 10

    if pd.notna(ma20) and pd.notna(ma60) and ma20 > ma60:
        score += 10
    elif pd.notna(ma20) and pd.notna(ma60) and ma20 < ma60:
        score -= 10

    return clamp_score(score)


def calculate_momentum_score(latest: pd.Series) -> int:
    """
    動能分數：
    - RSI 太高代表過熱，扣分
    - RSI 中性偏強加分
    - 20 日報酬率正向加分
    """
    score = 50

    rsi = latest["rsi14"]
    return_20d = latest["return_20d"]

    if pd.notna(rsi):
        if 45 <= rsi <= 65:
            score += 20
        elif 65 < rsi <= 75:
            score += 5
        elif rsi > 75:
            score -= 20
        elif 30 <= rsi < 45:
            score -= 5
        elif rsi < 30:
            score -= 15

    if pd.notna(return_20d):
        if return_20d > 0.10:
            score += 15
        elif return_20d > 0.03:
            score += 10
        elif return_20d > 0:
            score += 5
        elif return_20d < -0.10:
            score -= 15
        elif return_20d < -0.03:
            score -= 10

    return clamp_score(score)


def calculate_risk_score(latest: pd.Series) -> int:
    """
    風險分數：
    分數越高代表風險越可控。
    20 日波動率越高，分數越低。
    """
    score = 80

    volatility = latest["volatility_20d"]

    if pd.notna(volatility):
        if volatility < 0.015:
            score += 10
        elif volatility < 0.025:
            score += 0
        elif volatility < 0.04:
            score -= 15
        else:
            score -= 30

    return clamp_score(score)


def decide_action(total_score: int) -> str:
    """
    根據總分給出初步決策。
    """
    if total_score >= 75:
        return "可配置"
    elif total_score >= 60:
        return "觀望"
    else:
        return "避免"


def calculate_stock_score(ticker: str) -> dict[str, Any]:
    """
    Day 3 核心 function：
    輸入股票代號，輸出量化分數。
    """
    ticker = normalize_ticker(ticker)
    stock_info = get_stock_info(ticker)

    df = fetch_price_history(ticker, period="6mo")
    df = add_technical_indicators(df)

    latest = df.iloc[-1]

    trend_score = calculate_trend_score(latest)
    momentum_score = calculate_momentum_score(latest)
    risk_score = calculate_risk_score(latest)

    total_score = round(
        trend_score * 0.4
        + momentum_score * 0.3
        + risk_score * 0.3
    )

    result = {
        "ticker": ticker,
        "name": stock_info["name"],
        "type": stock_info["type"],
        "industry": stock_info["industry"],
        "date": str(latest["date"].date()),
        "close": round(float(latest["close"]), 2),
        "ma20": None if pd.isna(latest["ma20"]) else round(float(latest["ma20"]), 2),
        "ma60": None if pd.isna(latest["ma60"]) else round(float(latest["ma60"]), 2),
        "rsi14": None if pd.isna(latest["rsi14"]) else round(float(latest["rsi14"]), 2),
        "return_20d": None if pd.isna(latest["return_20d"]) else round(float(latest["return_20d"]) * 100, 2),
        "volatility_20d": None if pd.isna(latest["volatility_20d"]) else round(float(latest["volatility_20d"]) * 100, 2),
        "trend_score": trend_score,
        "momentum_score": momentum_score,
        "risk_score": risk_score,
        "total_score": total_score,
        "action": decide_action(total_score),
    }

    return result


def format_score_summary(score: dict[str, Any]) -> str:
    """
    把量化分數轉成文字，方便顯示或交給 LLM 解釋。
    """
    return f"""
股票代號：{score["ticker"]}
股票名稱：{score["name"]}
類型：{score["type"]}
產業：{score["industry"]}
資料日期：{score["date"]}

最新收盤價：{score["close"]}
MA20：{score["ma20"]}
MA60：{score["ma60"]}
RSI14：{score["rsi14"]}
20 日報酬率：{score["return_20d"]}%
20 日波動率：{score["volatility_20d"]}%

趨勢分數：{score["trend_score"]}
動能分數：{score["momentum_score"]}
風險分數：{score["risk_score"]}
總分：{score["total_score"]}
初步決策：{score["action"]}
""".strip()


if __name__ == "__main__":
    result = calculate_stock_score("2330")
    print(format_score_summary(result))