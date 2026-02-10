# 專案上傳至 GitHub 操作指南

本指南將協助您將 `ganoderma-papers-rag` 專案發佈到 GitHub。

## 1. 準備工作

確保您已經：
- [ ] 註冊並登入 [GitHub](https://github.com/)
- [ ] 安裝 Git (若尚未安裝，請前往 [Git 下載頁面](https://git-scm.com/downloads))

## 2. 在 GitHub 上建立新專案 (Repository)

1.  登入 GitHub，點擊右上角的 **+** 號，選擇 **New repository**。
2.  **Repository name** 輸入：`ganoderma-papers-rag` (或您喜歡的名稱)。
3.  **Description** (選填) 輸入：`A RAG system for Ganoderma academic papers with automated scraping and AI Q&A.`
4.  設定為 **Public** (公開) 或 **Private** (私人)。
5.  **不要** 勾選 "Add a README file"、".gitignore" 或 "license" (因為我們專案中已經有了)。
6.  點擊 **Create repository**。

## 3. 初始化 Git 並上傳程式碼

請開啟您的終端機 (Terminal) 或 PowerShell，並執行以下指令。

### 第一步：進入專案資料夾

```powershell
cd "d:\anti test\ganoderma-papers-rag"
```

### 第二步：初始化 Git 倉庫

```powershell
git init
```

### 第三步：加入所有檔案

```powershell
git add .
```

### 第四步：提交第一次變更

```powershell
git commit -m "Initial commit: Ganoderma Papers RAG system"
```

### 第五步：連結到 GitHub 遠端倉庫

> **注意**：請將下方的 `您的帳號` 替換為您的 GitHub 使用者名稱。

```powershell
git branch -M main
git remote add origin https://github.com/您的帳號/ganoderma-papers-rag.git
```

### 第六步：推送到 GitHub

```powershell
git push -u origin main
```

## 4. 完成！

回到您的 GitHub 專案頁面重新整理，您應該就會看到所有的程式碼和 `README.md` 文件了。

---

## 常見問題

### Q: 跳出登入視窗怎麼辦？
A: 請輸入您的 GitHub 帳號密碼。如果您有啟用 2FA (雙重驗證)，密碼欄位請輸入 **Personal Access Token**。

### Q: `git add .` 出現警告？
A: 如果看到關於 LF/CRLF 的警告，通常可以忽略，Git 會自動處理換行符號。

### Q: 推送失敗？
A: 檢查 `git remote -v` 是否正確，或確認您是否有該 Repository 的寫入權限。

### Q: 我可以把 Git 安裝在 D 槽嗎？
A: **可以的！** 在安裝過程中，當出現 "Select Destination Location" 步驟時，您可以直接修改路徑 (例如 `D:\Program Files\Git`)。Git 安裝在任何硬碟都不會影響其功能，也不會影響我們專案的操作。
