from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from rag.llm import get_llm
from rag.retriever import search_investment_rules


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


def format_docs(docs) -> str:
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


def answer_with_rag(question: str) -> dict[str, Any]:
    docs = search_investment_rules(question, k=4)
    context = format_docs(docs)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
你是一位台股量化 RAG 投資助理。

你必須遵守：
1. 只能根據「參考資料」與使用者問題回答。
2. 如果參考資料不足，請明確說資料不足。
3. 不要保證獲利。
4. 不要直接叫使用者一定要買。
5. 回答要用繁體中文。
6. 請把回答分成：重點結論、原因、適合做法、風險提醒。
"""
        ),
        (
            "human",
            """
使用者問題：
{question}

參考資料：
{context}
"""
        )
    ])

    chain = prompt | get_llm()
    result = chain.invoke({
        "question": question,
        "context": context,
    })

    answer = parse_llm_content(result.content)

    sources = [
        {
            "filename": doc.metadata.get("filename"),
            "content": doc.page_content,
        }
        for doc in docs
    ]

    return {
        "answer": answer,
        "sources": sources,
    }


if __name__ == "__main__":
    result = answer_with_rag("為什麼台積電漲太多要觀望？")

    print(result["answer"])

    print("\n--- sources ---")
    for source in result["sources"]:
        print(source["filename"])