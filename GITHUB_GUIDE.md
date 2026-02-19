# GitHub Upload Guide

This guide will assist you in publishing the `ganoderma-papers-rag` project to GitHub.

## 1. Preparation

Ensure you have:
- [ ] Registered and logged in to [GitHub](https://github.com/)
- [ ] Installed Git (If not, visit [Git Downloads](https://git-scm.com/downloads))

## 2. Create New Repository on GitHub

1.  Log in to GitHub, click the **+** icon in the top right, select **New repository**.
2.  **Repository name**: `ganoderma-papers-rag` (or your preferred name).
3.  **Description** (Optional): `A RAG system for Ganoderma academic papers with automated scraping and AI Q&A.`
4.  Set to **Public** or **Private**.
5.  **DO NOT** check "Add a README file", ".gitignore" or "license" (as we already have them in the project).
6.  Click **Create repository**.

## 3. Initialize Git and Upload Code

Open your Terminal or PowerShell and run the following commands.

### Step 1: Enter Project Directory

```powershell
cd "d:\anti test\ganoderma-papers-rag"
```

### Step 2: Initialize Git Repository

```powershell
git init
```

### Step 3: Add All Files

```powershell
git add .
```

### Step 4: Commit First Change

```powershell
git commit -m "Initial commit: Ganoderma Papers RAG system"
```

### Step 5: Link to Remote GitHub Repository

> **Note**: Replace `your_username` below with your GitHub username.

```powershell
git branch -M main
git remote add origin https://github.com/your_username/ganoderma-papers-rag.git
```

### Step 6: Push to GitHub

```powershell
git push -u origin main
```

## 4. Complete!

Refresh your GitHub project page, and you should see all code and the `README.md` file.
