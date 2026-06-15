from langchain_core.prompts import ChatPromptTemplate
from rag.llm import get_llm


def get_basic_chat_chain():
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
你是一個「台股量化 RAG 投資助理」。

你的任務：
1. 使用繁體中文回答。
2. 協助使用者理解台股、ETF、量化分數、風險控管與資金配置。
3. 目前你還沒有接上即時股價與 RAG 知識庫，所以不能假裝你查到了最新資料。
4. 如果問題涉及買賣建議，請提醒這不是保證獲利，也不是正式投資顧問建議。
5. 回答要清楚、務實、適合初學者閱讀。
"""
        ),
        (
            "human",
            "{question}"
        )
    ])

    llm = get_llm()

    chain = prompt | llm

    return chain
