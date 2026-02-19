# 🚀 Quick Start Guide

This guide will help you start the Ganoderma Papers RAG system in 5 minutes!

## 📋 Prerequisites

Ensure you have installed:
- ✅ Docker Desktop (Running)
- ✅ Python 3.11+
- ✅ At least 10 GB available disk space

## 🎯 Step 1: Configure Environment Variables

```powershell
# Enter project directory
cd "D:\anti test\ganoderma-papers-rag"

# Copy example environment variables
Copy-Item .env.example .env

# Edit with notepad (or your preferred editor)
notepad .env
```

**Minimal Configuration** (Keep others as default):
```bash
# Set a secure password
POSTGRES_PASSWORD=your_secure_password_123

# If you have Jina API Key (Optional, for better embeddings)
JINA_API_KEY=your_jina_api_key_here
```

## 🐳 Step 2: Start Docker Services

```powershell
# Start all services (PostgreSQL, OpenSearch, Redis, Ollama)
docker-compose up -d

# Wait for services to start (approx. 30-60 seconds)
# Check service status
docker-compose ps
```

You should see 4 services running:
- ✅ ganoderma-postgres
- ✅ ganoderma-opensearch  
- ✅ ganoderma-redis
- ✅ ganoderma-ollama

## 🐍 Step 3: Configure Python Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -e .
```

## 🗄️ Step 4: Initialize Database

```powershell
# Create database tables
python scripts/init_db.py
```

You should see:
```
✓ Database schema created successfully!
```

## 🤖 Step 5: Download LLM Model

```powershell
# Enter Ollama container
docker exec -it ganoderma-ollama bash

# Download Llama 3.1 model (approx. 4.7 GB, takes a few minutes)
ollama pull llama3.1:8b

# Verify model downloaded
ollama list

# Exit container
exit
```

## 🧪 Step 6: Test Scraper

```powershell
# Test scraper function
python scripts/test_scraper.py
```

You should see:
```
✓ Successfully extracted paper info
✓ Successfully downloaded PDF
```

## 🎉 Complete!

Congratulations! The system is ready!

## 📝 Next Steps

### Option A: Manual Scraping (Recommended to test first)

```powershell
# Scrape top 10 papers for testing
python scripts/manual_ingest.py --limit 10
```

### Option B: Start API Service

```powershell
# Start FastAPI service
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Then visit: http://localhost:8000/docs

### Option C: Start Gradio Interface

```powershell
# Start web interface
python src/ui/gradio_app.py
```

Then visit: http://localhost:7860

## 🔧 FAQ

### Q: Docker services failed to start?

```powershell
# View logs
docker-compose logs

# Restart
docker-compose down
docker-compose up -d
```

### Q: Virtual environment failed to start?

```powershell
# If execution policy error occurs
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then restart virtual environment
.\.venv\Scripts\Activate.ps1
```

### Q: Database connection failed?

Ensure:
1. Docker services are running: `docker-compose ps`
2. Password in `.env` matches Docker Compose
3. Wait for PostgreSQL to fully start (approx. 30 seconds)

### Q: Ollama model download is slow?

This is normal, model is approx. 4.7 GB. You can:
1. Use smaller model: `ollama pull llama3.1:7b`
2. Or download later, test other functions first

## 📊 Verify System Status

```powershell
# Check Docker services
docker-compose ps

# Check database connection
python -c "from src.config import settings; print(settings.database.connection_string)"

# Check PDF storage directory
Get-ChildItem "D:\anti test\ganoderma-papers-rag\data\pdfs" -Recurse
```

## 🎯 Quick Test Flow

Fully test if system is normal:

```powershell
# 1. Test scraper
python scripts/test_scraper.py

# 2. Check downloaded PDF
Get-ChildItem "data\pdfs\PMC" -Filter "*.pdf"

# 3. View database
python -c "from sqlalchemy import create_engine; from src.config import settings; engine = create_engine(settings.database.connection_string); print('Database connected!')"
```

## 📚 More Info

- Full Documentation: [README.md](README.md)
- System Architecture: [docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md)
- Implementation Plan: [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)

---

**Need Help?** Check FAQ section in README.md!
