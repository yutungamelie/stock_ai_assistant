from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from rag.llm import get_llm


def parse_llm_content(content: Any) -> str:
    """
    兼容 Gemini / OpenAI 不同回傳格式。
    """
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


def get_score_summary_chain():
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
你是一位台股量化投資助理。

你的任務：
1. 根據量化分數，用繁體中文解釋股票目前狀態。
2. 不要假裝知道即時新聞或財報。
3. 不要保證獲利。
4. 不要直接叫使用者一定要買。
5. 請用「趨勢、動能、風險、總結」四個段落回答。
6. 如果分數偏高，可以說「可列入觀察或分批配置」。
7. 如果分數普通，可以說「建議觀望」。
8. 如果分數偏低，可以說「暫時避免」。
"""
        ),
        (
            "human",
            """
請根據以下量化資料，產生白話解釋：

{score_text}
"""
        )
    ])

    llm = get_llm()
    return prompt | llm


def explain_score_with_llm(score_text: str) -> str:
    chain = get_score_summary_chain()
    result = chain.invoke({"score_text": score_text})
    return parse_llm_content(result.content)