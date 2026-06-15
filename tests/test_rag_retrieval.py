from tests.eval_cases import EVAL_CASES
from rag.retriever import search_investment_rules


def evaluate_retrieval():
    results = []

    for case in EVAL_CASES:
        question = case["question"]
        expected_sources = case["expected_sources"]

        docs = search_investment_rules(question, k=5)
        retrieved_sources = [
            doc.metadata.get("filename", "")
            for doc in docs
        ]

        hit_sources = [
            source for source in expected_sources
            if source in retrieved_sources
        ]

        passed = len(hit_sources) > 0

        results.append({
            "id": case["id"],
            "question": question,
            "expected_sources": expected_sources,
            "retrieved_sources": retrieved_sources,
            "hit_sources": hit_sources,
            "passed": passed,
        })

    return results


if __name__ == "__main__":
    results = evaluate_retrieval()

    passed_count = sum(1 for item in results if item["passed"])
    total_count = len(results)

    print(f"RAG 檢索測試通過：{passed_count}/{total_count}")
    print("=" * 80)

    for item in results:
        print(f"\n[{item['id']}] {item['question']}")
        print(f"通過：{item['passed']}")
        print(f"預期來源：{item['expected_sources']}")
        print(f"實際來源：{item['retrieved_sources']}")
        print(f"命中來源：{item['hit_sources']}")