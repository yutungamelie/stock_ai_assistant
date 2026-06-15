import json
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_export_payload(
    cash: int,
    stock_pool: list[str],
    messages: list[dict[str, Any]],
    latest_final_decision: dict[str, Any] | None = None,
    latest_candidates: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    整理要匯出的 JSON 內容。
    """
    return {
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "cash": cash,
        "stock_pool": stock_pool,
        "latest_candidates": latest_candidates or [],
        "latest_final_decision": latest_final_decision or {},
        "messages": messages,
    }


def export_to_json(payload: dict[str, Any]) -> Path:
    """
    寫出 JSON 檔案。
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = EXPORT_DIR / f"investment_chat_{timestamp}.json"

    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return output_path


def payload_to_json_string(payload: dict[str, Any]) -> str:
    """
    給 Streamlit download_button 使用。
    """
    return json.dumps(payload, ensure_ascii=False, indent=2)