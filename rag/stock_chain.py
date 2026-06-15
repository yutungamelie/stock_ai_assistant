from langchain_core.runnables import RunnableLambda

from data.stock_prices import (
    get_latest_stock_summary,
    format_stock_summary,
)


def stock_lookup_function(ticker: str) -> str:
    """
    LangChain 會呼叫的股票查詢 function。
    """
    summary = get_latest_stock_summary(ticker)
    return format_stock_summary(summary)


stock_lookup_chain = RunnableLambda(stock_lookup_function)


if __name__ == "__main__":
    result = stock_lookup_chain.invoke("2330")
    print(result)