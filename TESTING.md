# 🧪 Testing Guide

## 📋 Pre-test Check

Before starting tests, please confirm:
- ✅ Docker Desktop is installed and running
- ✅ Python 3.11+ is installed
- ✅ Operating in PowerShell

---

## 🚀 Test Steps (Approx. 10 Minutes)

### Step 1: Enter Project Directory

```powershell
cd "D:\anti test\ganoderma-papers-rag"
```

### Step 2: Configure Environment Variables

```powershell
# Copy example environment variables
Copy-Item .env.example .env

# Edit .env (Optional, default values work)
# notepad .env
```

> **Tip**: If just testing, you can use `.env.example` defaults without modification.

### Step 3: Start Docker Services

```powershell
# Start all services
docker-compose up -d

# Wait 30 seconds for services to fully start
Start-Sleep -Seconds 30

# Check service status
docker-compose ps
```

**Expected Result**: You should see 4 services running (State is "Up")
- ✅ ganoderma-postgres
- ✅ ganoderma-opensearch
- ✅ ganoderma-redis
- ✅ ganoderma-ollama

### Step 4: Create Python Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# If execution policy error occurs, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then re-run the activation command above
```

**Expected Result**: `(.venv)` appears at the start of your command prompt.

### Step 5: Install Python Packages

```powershell
# Install dependencies (Approx. 2-3 minutes)
pip install -e .
```

**Expected Result**: See "Successfully installed..." message.

### Step 6: Initialize Database

```powershell
# Create database tables
python scripts/init_db.py
```

**Expected Result**:
```
✓ Creating papers table...
✓ Creating paper_chunks table...
✓ Creating indexes...
✓ Database schema created successfully!
```

### Step 7: Test Scraper (Important!)

```powershell
# Run scraper test
python scripts/test_scraper.py
```

**Expected Result**:
```
✓ Successfully extracted paper info:
  Title: Iran: Clinical trials show...
  Paper URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC11792735/
  Source: PMC
✓ Successfully downloaded PDF to: D:\anti test\ganoderma-papers-rag\data\pdfs\PMC\PMC11792735.pdf
```

### Step 8: Verify PDF Download

```powershell
# Check downloaded PDF
Get-ChildItem "data\pdfs\PMC" -Filter "*.pdf"
```

**Expected Result**: You should see at least one PDF file.

---

## ✅ Success Criteria

If you see the following results, the system is functioning normally:

1. ✅ All Docker services started
2. ✅ Python virtual environment created successfully
3. ✅ Database tables created successfully
4. ✅ Scraper successfully extracted paper info
5. ✅ PDF successfully downloaded to `data/pdfs/PMC/` directory

---

## 🔧 Troubleshooting

### Issue 1: Docker Service Failed to Start

**Symptom**: `docker-compose ps` shows services "Exit" or "Restarting"

**Solution**:
```powershell
# View logs
docker-compose logs postgres

# Restart
docker-compose down
docker-compose up -d
```

### Issue 2: Virtual Environment Failed to Activate

**Symptom**: `File cannot be loaded because running scripts is disabled on this system.`

**Solution**:
```powershell
# Change execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Reactivate virtual environment
.\.venv\Scripts\Activate.ps1
```

### Issue 3: Database Connection Failed

**Symptom**: `init_db.py` error "could not connect to server"

**Solution**:
```powershell
# Confirm PostgreSQL is running
docker-compose ps postgres

# Wait longer (sometimes needs 1 minute)
Start-Sleep -Seconds 60

# Re-run
python scripts/init_db.py
```

### Issue 4: Scraper Test Failed

**Symptom**: `test_scraper.py` error or cannot download PDF

**Possible Causes**:
1. Network connection issue
2. Ganoderma News website structure changed
3. PDF link invalid

**Solution**:
```powershell
# View detailed error message
python scripts/test_scraper.py

# If network issue, try again later
# If website structure issue, crawler code needs adjustment
```

---

## 📊 Advanced Testing (Optional)

### Test 1: Check Database Content

```powershell
# Query database using Python
python -c "from sqlalchemy import create_engine, text; from src.config import settings; engine = create_engine(settings.database.connection_string); with engine.connect() as conn: result = conn.execute(text('SELECT COUNT(*) FROM papers')); print(f'Papers count: {result.scalar()}')"
```

### Test 2: View Docker Logs

```powershell
# View all service logs
docker-compose logs

# View specific service log
docker-compose logs postgres
docker-compose logs opensearch
```

### Test 3: Test OpenSearch

```powershell
# Test if OpenSearch is running
Invoke-WebRequest -Uri "http://localhost:9200" -Method Get
```

---

## 🎯 After Testing

### If Test Successful ✅

Congratulations! Basic system infrastructure is working. Next steps:

1. **Continue Building**: Let me build PDF processing and RAG modules
2. **Manually Scrape More Papers**: Wait for me to build `manual_ingest.py` script
3. **Pause Testing**: Stop Docker services anytime

### Stop Services

```powershell
# Stop all Docker services
docker-compose down

# Deactivate virtual environment
deactivate
```

### Restart

```powershell
# Start services
docker-compose up -d

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

---

## 📝 Test Checklist

Please complete checks in order:

- [ ] Step 1: Enter project directory
- [ ] Step 2: Configure environment variables
- [ ] Step 3: Start Docker services
- [ ] Step 4: Create Python virtual environment
- [ ] Step 5: Install Python packages
- [ ] Step 6: Initialize database
- [ ] Step 7: Test scraper
- [ ] Step 8: Verify PDF download

---

**Need Help?** Tell me the specific error message!
