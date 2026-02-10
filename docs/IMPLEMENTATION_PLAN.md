# Ganoderma Papers RAG 系統實作計畫

## 專案概述

建立一個專門處理靈芝學術論文的 RAG（Retrieval-Augmented Generation）系統，能夠：
1. 從靈芝新聞網自動抓取論文連結
2. 下載並解析學術論文 PDF
3. 將論文內容向量化並儲存
4. 提供專業的文獻引用查詢服務

## 系統架構

基於提供的參考架構圖，系統包含以下核心組件：

```mermaid
graph TB
    A[靈芝新聞網] --> B[論文連結爬蟲]
    B --> C[PDF 下載器]
    C --> D[Airflow 資料管道]
    D --> E[PDF 解析與分塊]
    E --> F[Jina Embeddings]
    F --> G[PostgreSQL]
    F --> H[OpenSearch]
    I[使用者查詢] --> J[FastAPI]
    J --> K[Redis 快取]
    K --> L[混合檢索]
    L --> H
    L --> G
    L --> M[Ollama LLM]
    M --> N[Gradio 介面]
    O[Langfuse] --> J
```

## 技術堆疊

### 核心技術
- **程式語言**: Python 3.11+
- **容器化**: Docker + Docker Compose
- **工作流程編排**: Apache Airflow
- **API 框架**: FastAPI
- **使用者介面**: Gradio

### 資料處理
- **PDF 解析**: PyMuPDF (fitz) / pdfplumber
- **文本嵌入**: Jina Embeddings (retrieval.passage)
- **文本分塊**: LangChain TextSplitter

### 儲存層
- **關聯式資料庫**: PostgreSQL 15
- **向量資料庫**: OpenSearch 2.x
- **快取層**: Redis 7

### AI/ML
- **LLM**: Ollama (本地部署)
- **可觀測性**: Langfuse

---

## 詳細實作計畫

### 1. 專案結構

```
ganoderma-papers-rag/
├── .env                          # 環境變數配置
├── .env.example                  # 環境變數範例
├── docker-compose.yml            # Docker 服務配置
├── Dockerfile                    # 應用程式容器
├── pyproject.toml               # Python 依賴管理
├── README.md                     # 專案說明文件
│
├── airflow/                      # Airflow 工作流程
│   ├── dags/
│   │   └── papers_ingestion.py  # 論文擷取 DAG
│   └── config/
│
├── data/                         # 資料儲存
│   ├── pdfs/                    # 下載的 PDF 檔案
│   └── metadata/                # 論文元數據
│
├── src/                          # 主要程式碼
│   ├── __init__.py
│   ├── config.py                # 配置管理
│   │
│   ├── scrapers/                # 爬蟲模組
│   │   ├── __init__.py
│   │   ├── ganoderma_news.py   # 靈芝新聞網爬蟲
│   │   └── pdf_downloader.py   # PDF 下載器
│   │
│   ├── processors/              # 資料處理
│   │   ├── __init__.py
│   │   ├── pdf_parser.py       # PDF 解析
│   │   ├── text_chunker.py     # 文本分塊
│   │   └── embedder.py         # 向量化
│   │
│   ├── storage/                 # 儲存層
│   │   ├── __init__.py
│   │   ├── postgres_client.py  # PostgreSQL 客戶端
│   │   └── opensearch_client.py # OpenSearch 客戶端
│   │
│   ├── rag/                     # RAG 核心
│   │   ├── __init__.py
│   │   ├── retriever.py        # 混合檢索器
│   │   ├── generator.py        # 答案生成器
│   │   └── citation_formatter.py # 引用格式化
│   │
│   ├── api/                     # API 服務
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI 主程式
│   │   └── routers/
│   │       └── ask.py          # 查詢端點
│   │
│   └── ui/                      # 使用者介面
│       ├── __init__.py
│       └── gradio_app.py       # Gradio 應用
│
├── scripts/                      # 工具腳本
│   ├── init_db.py               # 初始化資料庫
│   ├── test_scraper.py          # 測試爬蟲
│   └── manual_ingest.py         # 手動擷取
│
└── tests/                        # 測試
    ├── test_scrapers.py
    ├── test_processors.py
    └── test_rag.py
```

---

### 2. 核心模組設計

#### 2.1 論文連結爬蟲 (`scrapers/ganoderma_news.py`)

**功能**：
- 抓取靈芝新聞網**所有專欄**的文章
- 解析文章內容，提取論文原文連結
- 識別不同論文系統（PubMed Central, PubMed, arXiv, DOI 等）

**支援的專欄**：
```python
CATEGORIES = [
    "研究新知",           # Research News
    "靈芝調節免疫力",     # Immune Regulation
    "天選之材GMI",        # GMI (Ganoderma Microsporum Immunomodulatory protein)
    "靈芝與我",          # Ganoderma and Me
    "靈芝新聞",          # Ganoderma News
    "活動報導",          # Event Reports
    "歷史回顧",          # Historical Review
]
```

**關鍵邏輯**：
```python
def scrape_all_categories() -> List[dict]:
    """
    抓取所有專欄的文章
    """
    all_articles = []
    for category in CATEGORIES:
        articles = scrape_category(category)
        all_articles.extend(articles)
    return all_articles

def extract_paper_links(article_url: str) -> dict:
    """
    從文章中提取論文連結
    
    返回格式：
    {
        'article_title': '伊朗：臨床試驗顯示...',
        'article_url': 'https://www.ganodermanews.com/...',
        'category': '研究新知',
        'paper_url': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11792735/',
        'paper_source': 'PMC',
        'published_date': '2024-12-31',
        'has_pdf': True
    }
    """
```

**智能過濾**：
- 只抓取包含學術論文連結的文章
- 跳過純新聞報導或活動報導（無論文引用）
- 去重：避免重複抓取相同論文

**支援的論文來源**：
- PubMed Central (PMC) - 優先，通常有免費 PDF
- PubMed - 次要，可能需要付費
- DOI 連結 - 需解析重定向
- arXiv - 開放存取
- 其他開放存取期刊

---

#### 2.2 PDF 下載器 (`scrapers/pdf_downloader.py`)

**功能**：
- 根據論文連結自動下載 PDF
- 處理不同來源的下載邏輯
- 實作重試機制和錯誤處理
- **本地儲存優先**，可選雲端備份

**儲存策略**：

**本地儲存**（預設）：
```python
# 儲存路徑結構
data/
├── pdfs/
│   ├── PMC/
│   │   ├── PMC11792735.pdf
│   │   └── PMC11792736.pdf
│   ├── PubMed/
│   └── arXiv/
└── metadata/
    └── download_log.json
```

**雲端儲存**（可選）：
```python
# 支援多種雲端服務
CLOUD_STORAGE_OPTIONS = {
    'aws_s3': {
        'bucket': 'ganoderma-papers',
        'region': 'us-east-1'
    },
    'google_drive': {
        'folder_id': 'xxx'
    },
    'azure_blob': {
        'container': 'papers'
    }
}
```

**關鍵邏輯**：
```python
def download_pdf(paper_url: str, paper_source: str, 
                 storage_mode: str = 'local') -> str:
    """
    根據來源類型下載 PDF
    
    Args:
        paper_url: 論文連結
        paper_source: 來源類型 (PMC, PubMed, arXiv 等)
        storage_mode: 'local' 或 'cloud'
    
    Returns:
        PDF 檔案路徑或雲端 URL
    
    下載策略：
    - PMC: 使用 /pdf/ 路徑
    - PubMed: 嘗試找到 PDF 連結
    - DOI: 解析重定向
    - arXiv: 直接下載 PDF
    """
```

> [!IMPORTANT]
> **儲存空間估算**
> 
> 假設從靈芝新聞網抓取所有專欄：
> - **文章數量**：約 300-500 篇（含論文引用）
> - **成功下載 PDF**：約 60-70%（200-350 篇）
> - **單個 PDF 大小**：2-5 MB
> 
> **總儲存需求**：
> ```
> PDF 檔案：     300 篇 × 3 MB  = 900 MB - 1.5 GB
> 資料庫：       文本 + 元數據   = 200 MB - 300 MB
> 向量資料庫：   OpenSearch     = 300 MB - 500 MB
> Docker 容器：  系統映像       = 2 GB - 3 GB
> ─────────────────────────────────────────────
> 總計：                         約 3.5 GB - 5.5 GB
> ```
> 
> **建議**：
> - ✅ 本地儲存即可（一般電腦都能輕鬆處理）
> - ✅ 定期備份到外接硬碟或雲端
> - ⚠️ 如果未來擴展到其他真菌研究，再考慮雲端儲存

**挑戰與解決方案**：

| 挑戰 | 解決方案 |
|------|----------|
| 付費牆（paywalls） | 優先使用開放存取來源（PMC, arXiv） |
| 需要登入的期刊 | 僅儲存摘要和元數據，標記為「需手動下載」 |
| 僅提供摘要的文章 | 儲存摘要，並在 RAG 系統中標註「僅摘要可用」 |
| 下載失敗 | 實作 3 次重試機制，記錄失敗日誌供手動處理 |
| 檔案損壞 | 下載後驗證 PDF 完整性（檢查檔案頭和大小） |


---

#### 2.3 PDF 解析器 (`processors/pdf_parser.py`)

**功能**：
- 提取 PDF 文字內容
- 保留論文結構（標題、摘要、章節、參考文獻）
- 處理多欄位排版和圖表

**技術選擇**：**PyMuPDF (fitz)**
- 優點：速度快、準確度高、支援複雜排版
- 可提取文字、圖片、表格

**關鍵邏輯**：
```python
def parse_pdf(pdf_path: str) -> dict:
    """
    返回格式：
    {
        'title': '論文標題',
        'authors': ['作者1', '作者2'],
        'abstract': '摘要內容',
        'sections': [
            {'heading': 'Introduction', 'content': '...'},
            {'heading': 'Methods', 'content': '...'},
            ...
        ],
        'references': ['參考文獻1', '參考文獻2', ...]
    }
    """
```

---

#### 2.4 文本分塊器 (`processors/text_chunker.py`)

**策略**：智能分塊，保留論文結構

**分塊邏輯**：
1. **按章節分塊**：每個主要章節（Introduction, Methods, Results, Discussion）為一個基本單位
2. **大小限制**：每個塊最大 1000 tokens，超過則進一步分割
3. **重疊策略**：相鄰塊之間保留 200 tokens 重疊，保持上下文連貫

**元數據保留**：
```python
{
    'chunk_id': 'PMC11792735_chunk_3',
    'paper_id': 'PMC11792735',
    'section': 'Results',
    'chunk_index': 3,
    'total_chunks': 8,
    'content': '...',
    'metadata': {
        'title': '...',
        'authors': [...],
        'journal': '...',
        'year': 2024
    }
}
```

---

#### 2.5 向量化模組 (`processors/embedder.py`)

**Embedding 模型**：**Jina Embeddings v3**
- 模型：`jina-embeddings-v3`
- 維度：1024
- 支援長文本（最大 8192 tokens）

**批次處理**：
```python
def generate_embeddings(chunks: List[dict]) -> List[dict]:
    """
    批次生成向量
    每批 32 個文本塊
    """
```

---

### 3. 儲存層設計

#### 3.1 PostgreSQL 資料表結構

**papers 表**（論文元數據）：
```sql
CREATE TABLE papers (
    id SERIAL PRIMARY KEY,
    paper_id VARCHAR(255) UNIQUE NOT NULL,  -- PMC11792735
    title TEXT NOT NULL,
    authors TEXT[],
    abstract TEXT,
    journal VARCHAR(500),
    publication_date DATE,
    doi VARCHAR(255),
    paper_url TEXT NOT NULL,
    pdf_path TEXT,
    source_article_url TEXT,  -- 靈芝新聞網文章連結
    source_article_title TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_paper_id ON papers(paper_id);
CREATE INDEX idx_publication_date ON papers(publication_date);
```

**paper_chunks 表**（文本塊）：
```sql
CREATE TABLE paper_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(255) UNIQUE NOT NULL,
    paper_id VARCHAR(255) REFERENCES papers(paper_id),
    section VARCHAR(255),
    chunk_index INTEGER,
    total_chunks INTEGER,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chunk_paper_id ON paper_chunks(paper_id);
```

---

#### 3.2 OpenSearch 索引結構

**索引名稱**：`ganoderma_papers`

**Mapping**：
```json
{
  "mappings": {
    "properties": {
      "chunk_id": {"type": "keyword"},
      "paper_id": {"type": "keyword"},
      "title": {"type": "text", "analyzer": "standard"},
      "authors": {"type": "text"},
      "section": {"type": "keyword"},
      "content": {"type": "text", "analyzer": "standard"},
      "content_vector": {
        "type": "knn_vector",
        "dimension": 1024,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimilarity",
          "engine": "nmslib"
        }
      },
      "metadata": {"type": "object"},
      "created_at": {"type": "date"}
    }
  }
}
```

---

### 4. Airflow 資料管道

**DAG 名稱**：`ganoderma_papers_ingestion`

**執行頻率**：每週一次（可調整）

**任務流程**：
```python
fetch_articles >> extract_paper_links >> download_pdfs >> parse_pdfs >> 
chunk_texts >> generate_embeddings >> store_to_postgres >> store_to_opensearch
```

**各任務說明**：
1. **fetch_articles**: 抓取靈芝新聞網最新文章
2. **extract_paper_links**: 提取論文連結
3. **download_pdfs**: 下載 PDF 檔案
4. **parse_pdfs**: 解析 PDF 內容
5. **chunk_texts**: 文本分塊
6. **generate_embeddings**: 生成向量
7. **store_to_postgres**: 儲存到 PostgreSQL
8. **store_to_opensearch**: 儲存到 OpenSearch

---

### 5. RAG 查詢系統

#### 5.1 混合檢索器 (`rag/retriever.py`)

**檢索策略**：BM25 + 向量搜尋

```python
def hybrid_search(query: str, top_k: int = 10) -> List[dict]:
    """
    1. 向量搜尋：使用查詢的 embedding 在 OpenSearch 中搜尋
    2. BM25 搜尋：使用關鍵字在 content 欄位搜尋
    3. 混合排序：RRF (Reciprocal Rank Fusion)
    4. 返回 top-10 最相關的文本塊
    """
```

**Context Builder**：
```python
def build_context(chunks: List[dict]) -> str:
    """
    將檢索到的文本塊組織成 LLM 可理解的上下文
    包含：論文標題、作者、章節、內容
    """
```

---

#### 5.2 答案生成器 (`rag/generator.py`)

**LLM**：Ollama (本地部署)
- 模型建議：`llama3.1:8b` 或 `qwen2.5:14b`

**Prompt 模板**：
```python
SYSTEM_PROMPT = """
你是一位專業的靈芝研究文獻助理。你的任務是根據提供的學術論文內容，
回答使用者關於靈芝的問題。

要求：
1. 僅根據提供的論文內容回答，不要編造資訊
2. 使用繁體中文回答
3. 提供具體的文獻引用
4. 如果論文中沒有相關資訊，請明確說明
5. 回答要專業且易於理解

引用格式範例：
根據 Pakravan 等人 (2024) 在 Frontiers in Dentistry 發表的研究...
"""

USER_PROMPT = """
基於以下論文內容，請回答問題。

論文內容：
{context}

問題：{query}

請提供詳細回答，並註明引用來源。
"""
```

---

#### 5.3 引用格式化器 (`rag/citation_formatter.py`)

**支援格式**：
- **APA 格式**（預設）
- **MLA 格式**
- **Chicago 格式**

**範例輸出**：
```
Pakravan, F., Yegdaneh, A., Taymouri, S., Rahimi, S., & Ghahremani, N. (2024). 
Antifungal Efficacy of Ganoderma lucidum and Clotrimazole for Treatment of 
Denture Stomatitis: A Randomized Clinical Trial. Frontiers in Dentistry, 21, 45.
https://pmc.ncbi.nlm.nih.gov/articles/PMC11792735/
```

---

### 6. API 層設計

**FastAPI 端點**：

#### `POST /ask-agentic`
```python
{
  "query": "靈芝對假牙性口腔炎有什麼療效？",
  "citation_format": "APA",  # 可選：APA, MLA, Chicago
  "top_k": 10
}
```

**回應**：
```python
{
  "answer": "根據 Pakravan 等人 (2024) 的臨床研究...",
  "sources": [
    {
      "paper_id": "PMC11792735",
      "title": "Antifungal Efficacy of Ganoderma lucidum...",
      "authors": ["Pakravan F", "Yegdaneh A", ...],
      "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11792735/",
      "citation": "Pakravan, F., et al. (2024)...",
      "relevant_section": "Results"
    }
  ],
  "metadata": {
    "retrieval_time_ms": 234,
    "generation_time_ms": 1567
  }
}
```

#### `POST /restream`
串流式回應，逐字返回答案

---

### 7. Gradio 使用者介面

**功能**：
1. **問答輸入框**：使用者輸入問題
2. **答案顯示區**：顯示 LLM 生成的答案
3. **來源引用區**：顯示相關論文列表
4. **PDF 預覽**：點擊可開啟原始論文連結

**介面設計**：
```python
with gr.Blocks() as app:
    gr.Markdown("# 🍄 靈芝學術論文智能問答系統")
    
    with gr.Row():
        query_input = gr.Textbox(label="請輸入您的問題", lines=3)
        submit_btn = gr.Button("提交查詢")
    
    answer_output = gr.Markdown(label="回答")
    
    with gr.Accordion("📚 參考文獻", open=True):
        sources_output = gr.Dataframe(
            headers=["論文標題", "作者", "期刊", "年份", "連結"],
            label="相關論文"
        )
```

---

### 8. Docker Compose 配置

**服務清單**：
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ganoderma_papers
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  opensearch:
    image: opensearchproject/opensearch:2.11.0
    environment:
      - discovery.type=single-node
      - OPENSEARCH_JAVA_OPTS=-Xms2g -Xmx2g
    volumes:
      - opensearch_data:/usr/share/opensearch/data
    ports:
      - "9200:9200"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"

  airflow-webserver:
    build: .
    command: airflow webserver
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://user:password@postgres/airflow
    ports:
      - "8080:8080"
    depends_on:
      - postgres
      - redis

  airflow-scheduler:
    build: .
    command: airflow scheduler
    depends_on:
      - postgres
      - redis

  api:
    build: .
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - opensearch
      - redis
      - ollama

  gradio:
    build: .
    command: python src/ui/gradio_app.py
    ports:
      - "7860:7860"
    depends_on:
      - api

volumes:
  postgres_data:
  opensearch_data:
  ollama_data:
```

---

## 驗證計畫

### 自動化測試
1. **爬蟲測試**：驗證能正確抓取論文連結
2. **PDF 下載測試**：測試不同來源的 PDF 下載
3. **解析測試**：驗證 PDF 解析準確性
4. **RAG 測試**：測試檢索和生成品質

### 手動驗證
1. **資料品質檢查**：檢查前 10 篇論文的處理結果
2. **查詢測試**：使用 10 個常見問題測試系統回答品質
3. **引用準確性**：驗證引用格式正確性

---

## 專案時程估計

| 階段 | 任務 | 預估時間 |
|------|------|----------|
| 1 | 專案初始化 + Docker 環境 | 2 小時 |
| 2 | 爬蟲開發（論文連結 + PDF 下載） | 4 小時 |
| 3 | PDF 解析 + 文本處理 | 3 小時 |
| 4 | 資料庫設計 + 儲存層 | 2 小時 |
| 5 | Airflow DAG 開發 | 3 小時 |
| 6 | RAG 系統（檢索 + 生成） | 4 小時 |
| 7 | API 開發 | 2 小時 |
| 8 | Gradio UI | 2 小時 |
| 9 | 測試 + 除錯 | 3 小時 |
| **總計** | | **25 小時** |

---

## 後續優化方向

1. **多模態支援**：處理論文中的圖表和表格
2. **自動摘要**：為每篇論文生成中文摘要
3. **關聯分析**：找出論文之間的引用關係
4. **趨勢分析**：分析靈芝研究的熱門主題和趨勢
5. **多語言支援**：支援英文查詢和回答
