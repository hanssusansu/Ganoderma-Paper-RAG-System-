# 🍄 Ganoderma Papers RAG System

A specialized Retrieval-Augmented Generation (RAG) system for Ganoderma academic papers, capable of automated scraping, processing, and querying of Ganoderma-related academic research.

## ✨ Features

- 📚 **Multi-Column Scraping**: Automatically scrapes academic papers from all columns of the Ganoderma News website.
- 📄 **PDF Processing**: Smart downloading and parsing of academic paper PDFs.
- 🔍 **Hybrid Retrieval**: Hybrid search strategy combining BM25 and vector search.
- 🤖 **AI Q&A**: Uses Ollama local LLM to provide professional answers with literature citations.
- 📊 **Data Pipeline**: Automated data extraction and processing using Apache Airflow.
- 🎨 **User-Friendly Interface**: Gradio web interface, easy to use.

## 🏗️ System Architecture

```
Data Source → Scraper → PDF Download → Parse → Chunking → Vectorization → Storage → RAG Query → User Interface
```

For detailed architecture, please refer to: [docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md)

## 📦 Tech Stack

- **Language**: Python 3.11+
- **Database**: PostgreSQL 15
- **Vector Database**: OpenSearch 2.11
- **Cache**: Redis 7
- **LLM**: Ollama (llama3.1:8b)
- **Embeddings**: Jina Embeddings v3
- **API**: FastAPI
- **UI**: Gradio
- **Workflow**: Apache Airflow

## 🚀 Quick Start

### Prerequisites

- Docker Desktop
- Python 3.11+
- At least 16 GB RAM
- 20 GB Disk Space

### 1. Clone Project

```bash
git clone https://github.com/Hansforwork1/Ganoderma-Paper-RAG-System-.git
cd Ganoderma-Paper-RAG-System-
```

### 2. Configure Environment Variables

```bash
# Copy example environment variables
# Windows PowerShell
Copy-Item .env.example .env

# Edit .env file to set necessary parameters
notepad .env
```

### 3. Start Docker Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Initialize Database

```bash
# Create Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -e .

# Initialize database
python scripts/init_db.py
```

### 5. Download Ollama Model

```bash
# Enter Ollama container
docker exec -it ganoderma-ollama bash

# Download model
ollama pull llama3.1:8b

# Exit container
exit
```

### 6. Test Scraper

```bash
# Test scraper function
python scripts/test_scraper.py
```

## 📖 Usage Guide

### 🤖 Automated Full-Process Ingestion

This project provides an automated script that performs all steps: "Scrape → Download → Parse → Tag → Store".

```bash
# Run automated script
python scripts/auto_ingest.py
```

This is suitable for periodic execution or first-time database initialization.

### 🛠️ Manual/Step-by-Step Execution

If you need to debug specific steps or scrape only specific papers, use manual commands:

```bash
# Scrape papers from all columns
python scripts/manual_ingest.py --all

# Scrape only specific category
python scripts/manual_ingest.py --category "研究新知"

# Limit quantity
python scripts/manual_ingest.py --limit 10
```

### Start API Service

```bash
# Development mode
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Start Gradio Interface

```bash
python src/ui/gradio_app.py
```

Then open in browser: http://localhost:7860

## 📁 Project Structure

```
ganoderma-papers-rag/
├── src/                      # Main source code
│   ├── scrapers/            # Scraper modules
│   ├── processors/          # Data processing
│   ├── storage/             # Storage layer
│   ├── rag/                 # RAG core
│   ├── api/                 # API service
│   └── ui/                  # User interface
├── data/                     # Data storage
│   ├── pdfs/               # PDF files
│   └── metadata/           # Metadata
├── airflow/                  # Airflow DAGs
├── scripts/                  # Utility scripts
├── tests/                    # Tests
├── docs/                     # Documentation
├── docker-compose.yml        # Docker configuration
├── pyproject.toml           # Python project config
└── README.md                # This file
```

## 🔧 Configuration

Main configuration file: `.env`

Key configurations:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password

# Jina API (for Embeddings)
JINA_API_KEY=your_jina_api_key

# Ollama Model
OLLAMA_MODEL=llama3.1:8b

# Scraper Settings
SCRAPER_DELAY_SECONDS=2  # Polite delay
SCRAPER_MAX_RETRIES=3    # Retry attempts
```

## 📊 Data Flow

1. **Scraping Phase**: Scraper fetches articles from Ganoderma News, extracts paper links.
2. **Download Phase**: PDF downloader downloads paper PDF files.
3. **Processing Phase**: Parses PDF, extracts text, smart chunking.
4. **Vectorization Phase**: Generates vectors using Jina Embeddings.
5. **Storage Phase**: Saves to PostgreSQL and OpenSearch.
6. **Query Phase**: Hybrid retrieval + LLM generates answer.

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_scrapers.py

# Check coverage
pytest --cov=src tests/
```

## 📝 API Documentation

After starting the API service, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Main Endpoint

**POST /ask-agentic**
```json
{
  "query": "What are the therapeutic effects of Ganoderma on denture stomatitis?",
  "citation_format": "APA",
  "top_k": 10
}
```

## 💾 Storage Size

Estimated storage requirements:

- PDF Files: 1-1.5 GB
- Database: 120 MB
- Vector Database: 300 MB
- Docker Containers: 6.75 GB
- **Total: Approx 8-9 GB**

## 🔍 FAQ

### Q: How to change PDF storage location?

A: Modify `PDF_STORAGE_PATH` parameter in `.env`.

### Q: How to add other columns?

A: Edit `CATEGORIES` list in `src/scrapers/ganoderma_news.py`.

### Q: What if download fails?

A: System will auto-retry 3 times. Failed papers are logged in `data/metadata/download_log.json`.

### Q: How to change LLM model?

A: Modify `OLLAMA_MODEL` in `.env`, then run `ollama pull` to download the new model.

## 📚 Related Documentation

- [System Overview](docs/SYSTEM_OVERVIEW.md)
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md)
- [Task List](docs/TASK_LIST.md)

## 🤝 Contribution

Issues and Pull Requests are welcome!

## 📄 License

MIT License

## 👨‍💻 Author

hanssusansu

---

**Note**: This system is for academic research and personal learning only. Please comply with the terms of use and copyright regulations of relevant websites.
