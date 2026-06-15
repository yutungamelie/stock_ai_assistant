from tests.test_rag_retrieval import evaluate_retrieval


def main():
    print("開始 Day 7 測試")
    print("=" * 80)

    retrieval_results = evaluate_retrieval()
    retrieval_passed = sum(1 for item in retrieval_results if item["passed"])
    retrieval_total = len(retrieval_results)

    print(f"RAG 檢索測試：{retrieval_passed}/{retrieval_total}")

    if retrieval_passed >= 8:
        print("RAG 檢索結果：通過")
    else:
        print("RAG 檢索結果：需要改善")

    print("=" * 80)
    print("提醒：最終 LLM 回答測試會呼叫 Gemini，若遇到 503 可稍後再跑：")
    print("python -m tests.test_final_decision")


if __name__ == "__main__":
    main()