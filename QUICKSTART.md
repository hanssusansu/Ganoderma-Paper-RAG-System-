# 🚀 快速啟動指南

這份指南將幫助你在 5 分鐘內啟動 Ganoderma Papers RAG 系統！

## 📋 前置檢查

確保你已安裝：
- ✅ Docker Desktop（正在運行）
- ✅ Python 3.11+
- ✅ 至少 10 GB 可用硬碟空間

## 🎯 步驟 1：設定環境變數

```powershell
# 進入專案目錄
cd "D:\anti test\ganoderma-papers-rag"

# 複製環境變數範例
Copy-Item .env.example .env

# 使用記事本編輯（或你喜歡的編輯器）
notepad .env
```

**最小配置**（其他保持預設即可）：
```bash
# 設定一個安全的密碼
POSTGRES_PASSWORD=your_secure_password_123

# 如果你有 Jina API Key（可選，用於更好的 embeddings）
JINA_API_KEY=your_jina_api_key_here
```

## 🐳 步驟 2：啟動 Docker 服務

```powershell
# 啟動所有服務（PostgreSQL, OpenSearch, Redis, Ollama）
docker-compose up -d

# 等待服務啟動（約 30-60 秒）
# 查看服務狀態
docker-compose ps
```

你應該看到 4 個服務都在運行：
- ✅ ganoderma-postgres
- ✅ ganoderma-opensearch  
- ✅ ganoderma-redis
- ✅ ganoderma-ollama

## 🐍 步驟 3：設定 Python 環境

```powershell
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境
.\.venv\Scripts\Activate.ps1

# 安裝依賴套件
pip install -e .
```

## 🗄️ 步驟 4：初始化資料庫

```powershell
# 建立資料庫表格
python scripts/init_db.py
```

你應該看到：
```
✓ Database schema created successfully!
```

## 🤖 步驟 5：下載 LLM 模型

```powershell
# 進入 Ollama 容器
docker exec -it ganoderma-ollama bash

# 下載 Llama 3.1 模型（約 4.7 GB，需要幾分鐘）
ollama pull llama3.1:8b

# 驗證模型已下載
ollama list

# 退出容器
exit
```

## 🧪 步驟 6：測試爬蟲

```powershell
# 測試爬蟲功能
python scripts/test_scraper.py
```

你應該看到：
```
✓ Successfully extracted paper info
✓ Successfully downloaded PDF
```

## 🎉 完成！

恭喜！系統已經準備就緒！

## 📝 下一步

### 選項 A：手動抓取論文（推薦先測試）

```powershell
# 抓取前 10 篇論文測試
python scripts/manual_ingest.py --limit 10
```

### 選項 B：啟動 API 服務

```powershell
# 啟動 FastAPI 服務
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

然後訪問：http://localhost:8000/docs

### 選項 C：啟動 Gradio 介面

```powershell
# 啟動網頁介面
python src/ui/gradio_app.py
```

然後訪問：http://localhost:7860

## 🔧 常見問題

### Q: Docker 服務啟動失敗？

```powershell
# 查看日誌
docker-compose logs

# 重新啟動
docker-compose down
docker-compose up -d
```

### Q: 虛擬環境啟動失敗？

```powershell
# 如果出現執行政策錯誤
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 然後重新啟動虛擬環境
.\.venv\Scripts\Activate.ps1
```

### Q: 資料庫連線失敗？

確保：
1. Docker 服務正在運行：`docker-compose ps`
2. `.env` 中的密碼與 Docker Compose 一致
3. 等待 PostgreSQL 完全啟動（約 30 秒）

### Q: Ollama 模型下載很慢？

這是正常的，模型約 4.7 GB。你可以：
1. 使用較小的模型：`ollama pull llama3.1:7b`
2. 或稍後再下載，先測試其他功能

## 📊 驗證系統狀態

```powershell
# 檢查 Docker 服務
docker-compose ps

# 檢查資料庫連線
python -c "from src.config import settings; print(settings.database.connection_string)"

# 檢查 PDF 儲存目錄
Get-ChildItem "D:\anti test\ganoderma-papers-rag\data\pdfs" -Recurse
```

## 🎯 快速測試流程

完整測試系統是否正常：

```powershell
# 1. 測試爬蟲
python scripts/test_scraper.py

# 2. 檢查下載的 PDF
Get-ChildItem "data\pdfs\PMC" -Filter "*.pdf"

# 3. 查看資料庫
python -c "from sqlalchemy import create_engine; from src.config import settings; engine = create_engine(settings.database.connection_string); print('Database connected!')"
```

## 📚 更多資訊

- 完整文件：[README.md](README.md)
- 系統架構：[docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md)
- 實作計畫：[docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)

---

**需要幫助？** 查看 README.md 中的常見問題章節！
