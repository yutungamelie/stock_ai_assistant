from datetime import datetime
from typing import Any


def create_message(role: str, content: str, references: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """
    建立單筆對話紀錄。
    role: user / assistant / system
    """
    return {
        "role": role,
        "content": content,
        "references": references or [],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }


def add_message(
    messages: list[dict[str, Any]],
    role: str,
    content: str,
    references: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    將訊息加入 messages。
    """
    messages.append(
        create_message(
            role=role,
            content=content,
            references=references,
        )
    )
    return messages


def clear_messages() -> list[dict[str, Any]]:
    """
    清空對話紀錄。
    """
    return []