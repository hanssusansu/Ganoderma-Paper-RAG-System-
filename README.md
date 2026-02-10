# 🍄 Ganoderma Papers RAG System

一個專門處理靈芝學術論文的 RAG（Retrieval-Augmented Generation）系統，能夠自動抓取、處理和查詢靈芝相關的學術研究。

## ✨ 功能特色

- 📚 **多專欄抓取**：自動從靈芝新聞網抓取所有專欄的學術論文
- 📄 **PDF 處理**：智能下載和解析學術論文 PDF
- 🔍 **混合檢索**：結合 BM25 和向量搜尋的混合檢索策略
- 🤖 **AI 問答**：使用 Ollama 本地 LLM 提供專業的文獻引用回答
- 📊 **資料管道**：使用 Airflow 自動化資料擷取和處理
- 🎨 **友善介面**：Gradio 網頁介面，易於使用

## 🏗️ 系統架構

```
資料來源 → 爬蟲 → PDF下載 → 解析 → 分塊 → 向量化 → 儲存 → RAG查詢 → 使用者介面
```

詳細架構請參考：[docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md)

## 📦 技術堆疊

- **語言**: Python 3.11+
- **資料庫**: PostgreSQL 15
- **向量資料庫**: OpenSearch 2.11
- **快取**: Redis 7
- **LLM**: Ollama (llama3.1:8b)
- **Embeddings**: Jina Embeddings v3
- **API**: FastAPI
- **UI**: Gradio
- **工作流程**: Apache Airflow

## 🚀 快速開始

### 前置需求

- Docker Desktop
- Python 3.11+
- 至少 16 GB RAM
- 20 GB 硬碟空間

### 1. 克隆專案

```bash
cd ganoderma-papers-rag
```

### 2. 設定環境變數

```bash
# 複製環境變數範例
Copy-Item .env.example .env

# 編輯 .env 檔案，設定必要的參數
notepad .env
```

### 3. 啟動 Docker 服務

```bash
# 啟動所有服務
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

### 4. 初始化資料庫

```bash
# 建立 Python 虛擬環境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安裝依賴
pip install -e .

# 初始化資料庫
python scripts/init_db.py
```

### 5. 下載 Ollama 模型

```bash
# 進入 Ollama 容器
docker exec -it ganoderma-ollama bash

# 下載模型
ollama pull llama3.1:8b

# 退出容器
exit
```

### 6. 測試爬蟲

```bash
# 測試爬蟲功能
python scripts/test_scraper.py
```

## 📖 使用指南

### 手動抓取論文

```bash
# 抓取所有專欄的論文
python scripts/manual_ingest.py --all

# 只抓取特定專欄
python scripts/manual_ingest.py --category "研究新知"

# 限制數量
python scripts/manual_ingest.py --limit 10
```

### 啟動 API 服務

```bash
# 開發模式
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 生產模式
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 啟動 Gradio 介面

```bash
python src/ui/gradio_app.py
```

然後在瀏覽器開啟：http://localhost:7860

## 📁 專案結構

```
ganoderma-papers-rag/
├── src/                      # 主要程式碼
│   ├── scrapers/            # 爬蟲模組
│   ├── processors/          # 資料處理
│   ├── storage/             # 儲存層
│   ├── rag/                 # RAG 核心
│   ├── api/                 # API 服務
│   └── ui/                  # 使用者介面
├── data/                     # 資料儲存
│   ├── pdfs/               # PDF 檔案
│   └── metadata/           # 元數據
├── airflow/                  # Airflow DAGs
├── scripts/                  # 工具腳本
├── tests/                    # 測試
├── docs/                     # 文件
├── docker-compose.yml        # Docker 配置
├── pyproject.toml           # Python 專案配置
└── README.md                # 本檔案
```

## 🔧 配置說明

主要配置檔案：`.env`

關鍵配置項：

```bash
# 資料庫
POSTGRES_PASSWORD=your_secure_password

# Jina API（用於 Embeddings）
JINA_API_KEY=your_jina_api_key

# Ollama 模型
OLLAMA_MODEL=llama3.1:8b

# 爬蟲設定
SCRAPER_DELAY_SECONDS=2  # 禮貌性延遲
SCRAPER_MAX_RETRIES=3    # 重試次數
```

## 📊 資料流程

1. **抓取階段**：爬蟲從靈芝新聞網抓取文章，提取論文連結
2. **下載階段**：PDF 下載器下載論文 PDF 檔案
3. **處理階段**：解析 PDF，提取文字，智能分塊
4. **向量化階段**：使用 Jina Embeddings 生成向量
5. **儲存階段**：儲存到 PostgreSQL 和 OpenSearch
6. **查詢階段**：混合檢索 + LLM 生成答案

## 🧪 測試

```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/test_scrapers.py

# 查看覆蓋率
pytest --cov=src tests/
```

## 📝 API 文件

啟動 API 服務後，訪問：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要端點

**POST /ask-agentic**
```json
{
  "query": "靈芝對假牙性口腔炎有什麼療效？",
  "citation_format": "APA",
  "top_k": 10
}
```

## 💾 儲存空間

預估儲存需求：

- PDF 檔案：1-1.5 GB
- 資料庫：120 MB
- 向量資料庫：300 MB
- Docker 容器：6.75 GB
- **總計：約 8-9 GB**

## 🔍 常見問題

### Q: 如何更改 PDF 儲存位置？

A: 修改 `.env` 中的 `PDF_STORAGE_PATH` 參數。

### Q: 如何新增其他專欄？

A: 編輯 `src/scrapers/ganoderma_news.py` 中的 `CATEGORIES` 列表。

### Q: 下載失敗怎麼辦？

A: 系統會自動重試 3 次。失敗的論文會記錄在 `data/metadata/download_log.json`。

### Q: 如何更換 LLM 模型？

A: 修改 `.env` 中的 `OLLAMA_MODEL`，然後用 `ollama pull` 下載新模型。

## 📚 相關文件

- [系統架構總覽](docs/SYSTEM_OVERVIEW.md)
- [實作計畫](docs/IMPLEMENTATION_PLAN.md)
- [任務清單](docs/TASK_LIST.md)

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License

## 👨‍💻 作者

數位行銷分析師專用工具

---

**注意**：本系統僅用於學術研究和個人學習，請遵守相關網站的使用條款和版權規定。
