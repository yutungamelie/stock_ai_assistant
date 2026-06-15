from tests.eval_cases import EVAL_CASES
from decision.final_decision_chain import generate_final_decision


def evaluate_final_answers():
    results = []

    for case in EVAL_CASES:
        question = case["question"]
        expected_keywords = case["expected_keywords"]

        result = generate_final_decision(
            user_question=question,
            cash=70224,
            stock_pool=["0050", "006208", "00878", "00919", "2330"],
        )

        answer = result["answer"]

        hit_keywords = [
            keyword for keyword in expected_keywords
            if keyword in answer
        ]

        has_risk_disclaimer = (
            "不保證獲利" in answer
            or "不構成正式投資建議" in answer
            or "決策輔助" in answer
        )

        passed = len(hit_keywords) >= 2 and has_risk_disclaimer

        results.append({
            "id": case["id"],
            "question": question,
            "expected_keywords": expected_keywords,
            "hit_keywords": hit_keywords,
            "has_risk_disclaimer": has_risk_disclaimer,
            "success": result["success"],
            "passed": passed,
            "answer_preview": answer[:300],
        })

    return results


if __name__ == "__main__":
    results = evaluate_final_answers()

    passed_count = sum(1 for item in results if item["passed"])
    total_count = len(results)

    print(f"最終回答測試通過：{passed_count}/{total_count}")
    print("=" * 80)

    for item in results:
        print(f"\n[{item['id']}] {item['question']}")
        print(f"LLM 成功：{item['success']}")
        print(f"通過：{item['passed']}")
        print(f"命中關鍵字：{item['hit_keywords']}")
        print(f"有風險聲明：{item['has_risk_disclaimer']}")
        print(f"回答預覽：{item['answer_preview']}")