import pandas as pd


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """
    計算 RSI 指標。
    RSI > 70 通常代表偏熱
    RSI < 30 通常代表偏弱或超賣
    """
    delta = close.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    加入 Day 3 需要的技術指標：
    - MA20
    - MA60
    - RSI14
    - 20 日報酬率
    - 20 日波動率
    """
    df = df.copy()

    df["ma20"] = df["close"].rolling(window=20).mean()
    df["ma60"] = df["close"].rolling(window=60).mean()
    df["rsi14"] = calculate_rsi(df["close"], period=14)

    df["return_20d"] = df["close"].pct_change(periods=20)
    df["daily_return"] = df["close"].pct_change()
    df["volatility_20d"] = df["daily_return"].rolling(window=20).std()

    return df