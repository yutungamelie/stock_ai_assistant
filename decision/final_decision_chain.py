from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel

from decision.candidate_selector import (
    rank_candidate_stocks,
    format_candidate_scores,
)
from decision.position_sizing import (
    calculate_position_plan,
    format_position_plan,
)
from rag.retriever import search_investment_rules
from rag.llm import get_llm


DEFAULT_CASH = 70224


def parse_llm_content(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text = ""
        for item in content:
            if isinstance(item, dict) and "text" in item:
                text += item["text"]
            else:
                text += str(item)
        return text

    return str(content)


def format_rag_docs(docs: list[Any]) -> str:
    formatted = []

    for i, doc in enumerate(docs, start=1):
        filename = doc.metadata.get("filename", "unknown")
        formatted.append(
            f"""
[參考資料 {i}]
來源：{filename}
內容：
{doc.page_content}
""".strip()
        )

    return "\n\n".join(formatted)


def docs_to_references(docs: list[Any]) -> list[dict[str, Any]]:
    """
    把 LangChain Document 轉成可以存進 session_state / JSON 的 references。
    """
    references = []

    for doc in docs:
        references.append({
            "filename": doc.metadata.get("filename", "unknown"),
            "source": doc.metadata.get("source", ""),
            "content": doc.page_content,
        })

    return references


def prepare_decision_inputs(data: dict[str, Any]) -> dict[str, Any]:
    """
    準備 Day 6 需要的完整輸入：
    - 使用者問題
    - 可用資金
    - 股票池
    - 候選股分數
    - 資金配置
    - RAG 參考資料
    """
    user_question = data["user_question"]
    cash = data["cash"]
    stock_pool = data["stock_pool"]

    candidates = rank_candidate_stocks(
        top_n=5,
        ticker_pool=stock_pool,
    )

    candidate_scores_text = format_candidate_scores(candidates)

    position_plan = calculate_position_plan(
        candidates=candidates,
        total_cash=cash,
    )

    position_plan_text = format_position_plan(
        position_plan,
        total_cash=cash,
    )

    rag_query = f"""
使用者問題：{user_question}
可用資金：{cash}
候選標的：{candidate_scores_text}
請找出投資規則、資金控管、分批進場、追高風險、ETF 與個股配置上限。
""".strip()

    rag_docs = search_investment_rules(rag_query, k=5)
    rag_context = format_rag_docs(rag_docs)
    references = docs_to_references(rag_docs)

    return {
        "user_question": user_question,
        "cash": f"{cash:,} 元",
        "cash_number": cash,
        "stock_pool": stock_pool,
        "candidate_scores": candidate_scores_text,
        "candidate_list": candidates,
        "position_plan": position_plan_text,
        "position_plan_list": position_plan,
        "rag_context": rag_context,
        "references": references,
    }


def get_final_decision_chain():
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
你是一位台股量化 RAG 投資助理。

你必須遵守：
1. 不保證獲利。
2. 不構成正式投資建議。
3. 不可以叫使用者一定要買。
4. 必須根據「量化分數」、「資金配置計畫」與「RAG 參考資料」回答。
5. 若資料不足，請明確說資料不足。
6. 回答要用繁體中文。
7. 回答要適合投資新手閱讀。
8. 對於 0050 與台積電，如果它們分數不佳、漲太多或不適合重壓，要清楚解釋原因。
9. 請提醒使用者可以分批進場、保留現金、避免追高。
10. 不得編造不存在的新聞、財報、法人買賣超或即時價格。
11. 如果 RAG 參考資料沒有提到，請說「目前參考資料不足」。
12. 回答中的理由必須能對應到量化資料或 RAG 參考資料。
13. 不要使用「一定會漲」、「保證獲利」、「穩賺」等語句。
14. 建議使用「可觀察」、「可分批」、「暫時觀望」、「避免重壓」等保守措辭。

請用以下格式回答：

## 重點結論
說明今天是否適合進場，以及整體建議是偏向可配置、觀望或避免。

## 推薦標的排序
列出推薦股票 / ETF，每檔包含：
- 股票代號與名稱
- 量化總分
- 初步決策
- 建議配置金額
- 估計可買股數

## 為什麼推薦這些標的
根據趨勢、動能、風險與 RAG 規則解釋。

## 0050 / 台積電觀察
如果 0050 或台積電出現在資料中，請說明是否適合配置，以及為什麼不能一次買滿。

## 建議資金配置
根據使用者可用資金，說明如何分批配置與保留現金。

## 風險提醒
提醒這只是學習與決策輔助，不保證獲利。
"""
        ),
        (
            "human",
            """
使用者問題：
{user_question}

可用資金：
{cash}

候選股量化分數：
{candidate_scores}

資金配置計畫：
{position_plan}

RAG 參考資料：
{rag_context}

請產生完整投資建議。
"""
        )
    ])

    return prompt | get_llm()


def generate_final_decision(
    user_question: str,
    cash: int = DEFAULT_CASH,
    stock_pool: list[str] | None = None,
) -> dict[str, Any]:
    """
    給 Streamlit 呼叫的主函式。
    """
    stock_pool = stock_pool or []

    prepared = prepare_decision_inputs({
        "user_question": user_question,
        "cash": cash,
        "stock_pool": stock_pool,
    })

    chain = get_final_decision_chain()

    try:
        result = chain.invoke({
            "user_question": prepared["user_question"],
            "cash": prepared["cash"],
            "candidate_scores": prepared["candidate_scores"],
            "position_plan": prepared["position_plan"],
            "rag_context": prepared["rag_context"],
        })
        answer = parse_llm_content(result.content)
        success = True

    except Exception as e:
        answer = f"""
Gemini 目前無法產生完整投資建議，可能是模型忙碌或 API 暫時不可用。

以下仍保留本次已完成的量化分數、資金配置與 RAG 參考資料，可供你先人工判讀。

錯誤訊息：
{e}
""".strip()
        success = False

    return {
        "answer": answer,
        "success": success,
        "cash": cash,
        "stock_pool": stock_pool,
        "candidate_list": prepared["candidate_list"],
        "position_plan_list": prepared["position_plan_list"],
        "candidate_scores": prepared["candidate_scores"],
        "position_plan": prepared["position_plan"],
        "rag_context": prepared["rag_context"],
        "references": prepared["references"],
    }


if __name__ == "__main__":
    result = generate_final_decision(
        user_question="我現在有 70,224 元，今天適合買什麼？",
        cash=70224,
        stock_pool=["0050", "006208", "00878", "00919", "2330"],
    )
    print(result["answer"])