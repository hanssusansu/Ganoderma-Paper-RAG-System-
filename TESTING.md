# 🧪 測試指南

## 📋 測試前檢查

在開始測試前，請確認：
- ✅ 已安裝 Docker Desktop 並正在運行
- ✅ 已安裝 Python 3.11+
- ✅ 在 PowerShell 中操作

---

## 🚀 測試步驟（約 10 分鐘）

### 步驟 1：進入專案目錄

```powershell
cd "D:\anti test\ganoderma-papers-rag"
```

### 步驟 2：設定環境變數

```powershell
# 複製環境變數範例
Copy-Item .env.example .env

# 編輯 .env（可選，使用預設值也可以）
# notepad .env
```

> **提示**：如果只是測試，可以直接使用 `.env.example` 的預設值，不需要修改。

### 步驟 3：啟動 Docker 服務

```powershell
# 啟動所有服務
docker-compose up -d

# 等待 30 秒讓服務完全啟動
Start-Sleep -Seconds 30

# 檢查服務狀態
docker-compose ps
```

**預期結果**：你應該看到 4 個服務都在運行（State 為 "Up"）
- ✅ ganoderma-postgres
- ✅ ganoderma-opensearch
- ✅ ganoderma-redis
- ✅ ganoderma-ollama

### 步驟 4：建立 Python 虛擬環境

```powershell
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境
.\.venv\Scripts\Activate.ps1

# 如果出現執行政策錯誤，執行：
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# 然後重新執行上面的啟動命令
```

**預期結果**：你的命令提示符前面會出現 `(.venv)`

### 步驟 5：安裝 Python 套件

```powershell
# 安裝依賴套件（約 2-3 分鐘）
pip install -e .
```

**預期結果**：看到 "Successfully installed..." 訊息

### 步驟 6：初始化資料庫

```powershell
# 建立資料庫表格
python scripts/init_db.py
```

**預期結果**：
```
✓ Creating papers table...
✓ Creating paper_chunks table...
✓ Creating indexes...
✓ Database schema created successfully!
```

### 步驟 7：測試爬蟲（重要！）

```powershell
# 執行爬蟲測試
python scripts/test_scraper.py
```

**預期結果**：
```
✓ Successfully extracted paper info:
  Title: 伊朗：臨床試驗顯示...
  Paper URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC11792735/
  Source: PMC
✓ Successfully downloaded PDF to: D:\anti test\ganoderma-papers-rag\data\pdfs\PMC\PMC11792735.pdf
```

### 步驟 8：驗證 PDF 下載

```powershell
# 檢查下載的 PDF
Get-ChildItem "data\pdfs\PMC" -Filter "*.pdf"
```

**預期結果**：你應該看到至少一個 PDF 檔案

---

## ✅ 測試成功的標準

如果你看到以下結果，表示系統運作正常：

1. ✅ Docker 服務全部啟動
2. ✅ Python 虛擬環境建立成功
3. ✅ 資料庫表格建立成功
4. ✅ 爬蟲成功提取論文資訊
5. ✅ PDF 成功下載到 `data/pdfs/PMC/` 目錄

---

## 🔧 常見問題排除

### 問題 1：Docker 服務啟動失敗

**症狀**：`docker-compose ps` 顯示服務 "Exit" 或 "Restarting"

**解決方法**：
```powershell
# 查看日誌
docker-compose logs postgres

# 重新啟動
docker-compose down
docker-compose up -d
```

### 問題 2：虛擬環境啟動失敗

**症狀**：`無法載入檔案...因為這個系統上已停用指令碼執行`

**解決方法**：
```powershell
# 修改執行政策
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 重新啟動虛擬環境
.\.venv\Scripts\Activate.ps1
```

### 問題 3：資料庫連線失敗

**症狀**：`init_db.py` 報錯 "could not connect to server"

**解決方法**：
```powershell
# 確認 PostgreSQL 正在運行
docker-compose ps postgres

# 等待更長時間（有時需要 1 分鐘）
Start-Sleep -Seconds 60

# 重新執行
python scripts/init_db.py
```

### 問題 4：爬蟲測試失敗

**症狀**：`test_scraper.py` 報錯或無法下載 PDF

**可能原因**：
1. 網路連線問題
2. 靈芝新聞網網站結構改變
3. PDF 連結失效

**解決方法**：
```powershell
# 查看詳細錯誤訊息
python scripts/test_scraper.py

# 如果是網路問題，稍後再試
# 如果是網站結構問題，需要調整爬蟲程式碼
```

---

## 📊 進階測試（可選）

### 測試 1：檢查資料庫內容

```powershell
# 使用 Python 查詢資料庫
python -c "from sqlalchemy import create_engine, text; from src.config import settings; engine = create_engine(settings.database.connection_string); with engine.connect() as conn: result = conn.execute(text('SELECT COUNT(*) FROM papers')); print(f'Papers count: {result.scalar()}')"
```

### 測試 2：查看 Docker 日誌

```powershell
# 查看所有服務日誌
docker-compose logs

# 查看特定服務日誌
docker-compose logs postgres
docker-compose logs opensearch
```

### 測試 3：測試 OpenSearch

```powershell
# 測試 OpenSearch 是否運行
Invoke-WebRequest -Uri "http://localhost:9200" -Method Get
```

---

## 🎯 測試完成後

### 如果測試成功 ✅

恭喜！系統基礎架構運作正常。下一步你可以：

1. **繼續建構系統**：讓我建立 PDF 處理和 RAG 模組
2. **手動抓取更多論文**：等我建立 `manual_ingest.py` 腳本
3. **暫停測試**：隨時可以停止 Docker 服務

### 停止服務

```powershell
# 停止所有 Docker 服務
docker-compose down

# 停用虛擬環境
deactivate
```

### 重新啟動

```powershell
# 啟動服務
docker-compose up -d

# 啟動虛擬環境
.\.venv\Scripts\Activate.ps1
```

---

## 📝 測試檢查清單

請按順序完成以下檢查：

- [ ] 步驟 1：進入專案目錄
- [ ] 步驟 2：設定環境變數
- [ ] 步驟 3：啟動 Docker 服務
- [ ] 步驟 4：建立 Python 虛擬環境
- [ ] 步驟 5：安裝 Python 套件
- [ ] 步驟 6：初始化資料庫
- [ ] 步驟 7：測試爬蟲
- [ ] 步驟 8：驗證 PDF 下載

---

**需要幫助？** 如果遇到任何問題，請告訴我具體的錯誤訊息！
