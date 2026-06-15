# 股票量化 RAG 投資助理

這是一個使用 Streamlit、LangChain、Gemini、Chroma、yfinance 建立的台股量化 RAG 投資助理。

本專案目標是把「量化評分」、「RAG 投資規則檢索」與「LLM 投資建議整理」整合成一個可操作的 Web App。

## Demo 功能

- 輸入可用資金
- 選擇台股 / ETF 股票池
- 自動計算量化分數
- 產生建議資金配置
- 使用 RAG 引用投資規則
- 產生投資建議說明
- 顯示 RAG 引用資料
- 保存對話紀錄
- 匯出 JSON

## 技術架構

```text
使用者問題
↓
yfinance 取得股價資料
↓
量化模型計算 MA20 / MA60 / RSI / 報酬率 / 波動率
↓
候選股排序
↓
Chroma Retriever 檢索投資規則
↓
LangChain Prompt 整合量化分數、資金配置與 RAG 內容
↓
Gemini 產生投資建議
↓
Streamlit 顯示結果

## 使用技術

- Python
- Streamlit
- LangChain
- Google Gemini
- Chroma
- yfinance
- pandas
- NumPy
```
## 專案結構

```text
tw_stock_ai_assistant/
├── app.py
├── env_settings.py
├── requirements.txt
├── README.md
├── .env.example
├── data/
│   ├── tickers.py
│   └── stock_prices.py
├── quant/
│   ├── indicators.py
│   └── scoring.py
├── rag/
│   ├── build_vector_db.py
│   ├── retriever.py
│   └── rag_chain.py
├── rag_docs/
│   ├── investment_rules.md
│   ├── etf_0050_rules.md
│   ├── tsmc_2330_rules.md
│   └── risk_control_rules.md
├── decision/
│   ├── candidate_selector.py
│   ├── position_sizing.py
│   └── final_decision_chain.py
├── database/
│   └── chat_history.py
├── exports/
│   └── export_utils.py
└── tests/
    ├── eval_cases.py
    ├── test_rag_retrieval.py
    ├── test_final_decision.py
    └── run_all_tests.py
```

## 量化評分邏輯

本專案目前使用以下指標建立簡化量化評分模型：

- MA20
- MA60
- RSI14
- 20 日報酬率
- 20 日波動率
- 趨勢分數
- 動能分數
- 風險分數
- 總分

總分會產生初步決策：

```
75 分以上：可配置
60 到 74 分：觀望
低於 60 分：避免
```

## RAG 投資規則

RAG 知識庫包含：

- 不追高原則
- 分批進場原則
- ETF 配置上限
- 單一個股配置上限
- 0050 觀察規則
- 台積電觀察規則
- 風險控管規則

## 安裝方式

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 環境變數

請建立 `.env`：

```
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

## 建立 RAG 向量資料庫

```bash
python -m rag.build_vector_db
```

## 啟動 App

```bash
python -m streamlit run app.py
```

## 測試

```bash
python -m tests.run_all_tests
python -m tests.test_rag_retrieval
python -m tests.test_final_decision
```

## 專案亮點

- 從零建立量化交易助理 MVP
- 串接真實台股 / ETF 股價資料
- 使用 RAG 降低 LLM 幻覺
- 將投資規則引用資料顯示給使用者
- 支援資金配置與零股估算
- 支援 JSON 匯出投資紀錄
- 包含基本 RAG 檢索測試案例

## 風險聲明

本工具僅供學習與決策輔助，不保證獲利，也不構成正式投資建議。

所有投資決策仍需使用者自行判斷並承擔風險。
