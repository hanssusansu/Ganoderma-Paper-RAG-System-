# 🍄 Ganoderma Papers RAG 系統使用指南

## 🚀 快速啟動

### 1. 啟動 Docker 服務

```powershell
cd "D:\anti test\ganoderma-papers-rag"
docker-compose up -d
```

### 2. 下載 Ollama 模型（首次使用）

```powershell
docker exec -it ganoderma-ollama ollama pull llama2
```

### 3. 啟動服務

#### 選項 A: Web 介面（Gradio）

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/launch_ui.py
```

訪問: http://localhost:7860

#### 選項 B: API 服務（FastAPI）

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/launch_api.py
```

訪問: http://localhost:8000/docs

---

## 📖 功能說明

### Web 介面功能

- ✅ 問答介面
- ✅ 來源引用顯示
- ✅ 可調整檢索數量
- ✅ 範例問題

### API 端點

- `GET /` - API 資訊
- `GET /health` - 健康檢查
- `POST /query` - 問答查詢
- `GET /stats` - 系統統計

### 自動化爬取

使用 Airflow DAG 定期爬取新論文（每週一次）

---

## 💡 使用範例

### Python 程式碼

```python
from src.rag.retriever import SimpleRetriever
from src.rag.generator import RAGGenerator

# 初始化
retriever = SimpleRetriever()
generator = RAGGenerator()
retriever.load_chunks()

# 查詢
query = "靈芝有什麼功效？"
results = retriever.retrieve(query, top_k=3)
answer = generator.generate_answer(query, results)

print(answer)
```

### API 請求

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "靈芝有什麼功效？", "top_k": 5}'
```

---

## 🎯 系統架構

```
使用者
  ↓
Web UI / API
  ↓
RAG 系統
  ├─ 檢索器 (Retriever)
  └─ 生成器 (Generator)
  ↓
資料層
  ├─ PostgreSQL (元數據)
  ├─ OpenSearch (向量搜尋)
  └─ PDF 檔案
```

---

## 📝 常見問題

### Q: Ollama 連線失敗？

確認 Ollama 容器正在運行：
```powershell
docker ps | findstr ollama
```

### Q: 找不到分塊資料？

執行 PDF 處理管道：
```powershell
python scripts/test_pdf_processing.py
```

### Q: 如何添加新論文？

1. 手動下載 PDF 到 `data/pdfs/PMC/`
2. 執行處理腳本
3. 重啟服務

---

**系統已完全可用！** 🎉
