EVAL_CASES = [
    {
        "id": "q01",
        "question": "我現在有 70,224 元，今天適合買什麼？",
        "expected_keywords": ["分批", "風險", "資金", "不保證獲利"],
        "expected_sources": ["investment_rules.md", "risk_control_rules.md"],
    },
    {
        "id": "q02",
        "question": "0050 現在可以一次買滿嗎？",
        "expected_keywords": ["0050", "不追高", "分批", "ETF"],
        "expected_sources": ["etf_0050_rules.md", "investment_rules.md"],
    },
    {
        "id": "q03",
        "question": "台積電漲太多還能追嗎？",
        "expected_keywords": ["台積電", "追高", "觀望", "分批"],
        "expected_sources": ["tsmc_2330_rules.md", "investment_rules.md"],
    },
    {
        "id": "q04",
        "question": "為什麼不要把全部資金買台積電？",
        "expected_keywords": ["單一個股", "30%", "集中", "風險"],
        "expected_sources": ["tsmc_2330_rules.md", "risk_control_rules.md"],
    },
    {
        "id": "q05",
        "question": "ETF 和個股配置上限有什麼差別？",
        "expected_keywords": ["ETF", "個股", "45%", "30%"],
        "expected_sources": ["risk_control_rules.md", "investment_rules.md"],
    },
    {
        "id": "q06",
        "question": "如果量化分數只有 60 到 74 分，該怎麼做？",
        "expected_keywords": ["觀望", "等待", "分數", "趨勢"],
        "expected_sources": ["investment_rules.md"],
    },
    {
        "id": "q07",
        "question": "什麼情況下應該保留現金？",
        "expected_keywords": ["保留現金", "市場", "過熱", "觀望"],
        "expected_sources": ["investment_rules.md", "risk_control_rules.md"],
    },
    {
        "id": "q08",
        "question": "為什麼觀望也是一種投資決策？",
        "expected_keywords": ["觀望", "等待", "價格", "決策"],
        "expected_sources": ["risk_control_rules.md"],
    },
    {
        "id": "q09",
        "question": "小資金買高價股可以怎麼做？",
        "expected_keywords": ["零股", "小資金", "分批"],
        "expected_sources": ["risk_control_rules.md", "tsmc_2330_rules.md"],
    },
    {
        "id": "q10",
        "question": "請幫我產生下單前檢查清單。",
        "expected_keywords": ["風險", "分批", "追高", "配置"],
        "expected_sources": ["investment_rules.md", "risk_control_rules.md"],
    },
]