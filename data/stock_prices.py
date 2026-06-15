from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

from data.tickers import TAIWAN_STOCKS


PRICE_DIR = Path(__file__).resolve().parent / "prices"
PRICE_DIR.mkdir(parents=True, exist_ok=True)


def normalize_ticker(ticker: str) -> str:
    """
    將使用者輸入的股票代號標準化。
    例如：
    2330.TW -> 2330
    2330    -> 2330
    """
    return ticker.upper().replace(".TW", "").replace(".TWO", "").strip()


def get_stock_info(ticker: str) -> dict[str, Any]:
    """
    從股票清單取得基本資料。
    """
    ticker = normalize_ticker(ticker)

    if ticker not in TAIWAN_STOCKS:
        raise ValueError(f"找不到股票代號：{ticker}。請先把它加入 data/tickers.py")

    return TAIWAN_STOCKS[ticker]


def fetch_price_history(ticker: str, period: str = "6mo") -> pd.DataFrame:
    """
    從 Yahoo Finance 取得股價資料。
    """
    ticker = normalize_ticker(ticker)
    stock_info = get_stock_info(ticker)
    yahoo_symbol = stock_info["yahoo_symbol"]

    df = yf.download(
        yahoo_symbol,
        period=period,
        interval="1d",
        auto_adjust=False,
        progress=False,
    )

    if df.empty:
        raise ValueError(f"無法取得 {ticker} 的股價資料。")

    # yfinance 有時會回傳 MultiIndex columns，這裡統一攤平
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    df = df.reset_index()

    # 統一欄位名稱
    df = df.rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        }
    )

    # 只保留需要的欄位
    keep_columns = [
        "date",
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume",
    ]

    df = df[keep_columns]

    # 計算 MA20、MA60
    df["ma20"] = df["close"].rolling(window=20).mean()
    df["ma60"] = df["close"].rolling(window=60).mean()

    return df


def save_price_history(ticker: str, period: str = "6mo") -> Path:
    """
    取得股價資料並存成 CSV。
    """
    ticker = normalize_ticker(ticker)
    df = fetch_price_history(ticker, period=period)

    output_path = PRICE_DIR / f"{ticker}.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    return output_path


def get_latest_stock_summary(ticker: str) -> dict[str, Any]:
    """
    取得最新股票摘要。
    這是 Day 2 最重要的 function。
    """
    ticker = normalize_ticker(ticker)
    stock_info = get_stock_info(ticker)
    df = fetch_price_history(ticker, period="6mo")

    latest = df.iloc[-1]

    summary = {
        "ticker": ticker,
        "name": stock_info["name"],
        "type": stock_info["type"],
        "industry": stock_info["industry"],
        "date": str(latest["date"].date()),
        "close": round(float(latest["close"]), 2),
        "volume": int(latest["volume"]),
        "ma20": None if pd.isna(latest["ma20"]) else round(float(latest["ma20"]), 2),
        "ma60": None if pd.isna(latest["ma60"]) else round(float(latest["ma60"]), 2),
        "csv_path": str(save_price_history(ticker)),
    }

    return summary


def format_stock_summary(summary: dict[str, Any]) -> str:
    """
    把股票摘要轉成適合顯示給使用者看的文字。
    """
    return f"""
股票代號：{summary["ticker"]}
股票名稱：{summary["name"]}
類型：{summary["type"]}
產業：{summary["industry"]}
資料日期：{summary["date"]}

最新收盤價：{summary["close"]}
成交量：{summary["volume"]:,}
MA20：{summary["ma20"]}
MA60：{summary["ma60"]}

CSV 檔案位置：{summary["csv_path"]}
""".strip()


if __name__ == "__main__":
    result = get_latest_stock_summary("2330")
    print(format_stock_summary(result))
