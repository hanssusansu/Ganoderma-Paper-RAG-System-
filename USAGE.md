# 🍄 Ganoderma Papers RAG System Usage Guide

## 🚀 Quick Start

### 1. Start Docker Services

```powershell
cd "D:\anti test\ganoderma-papers-rag"
docker-compose up -d
```

### 2. Download Ollama Model (First Time Use)

```powershell
docker exec -it ganoderma-ollama ollama pull llama2
```

### 3. Start Services

#### Option A: Web Interface (Gradio)

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/launch_ui.py
```

Visit: http://localhost:7860

#### Option B: API Service (FastAPI)

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/launch_api.py
```

Visit: http://localhost:8000/docs

---

## 📖 Features

### Web Interface Features

- ✅ Q&A Interface
- ✅ Source Citation Display
- ✅ Adjustable Retrieval Quantity
- ✅ Example Questions

### API Endpoints

- `GET /` - API Info
- `GET /health` - Health Check
- `POST /query` - Q&A Query
- `GET /stats` - System Stats

### Automated Scraping

Use Airflow DAG to periodically scrape new papers (weekly).

---

## 💡 Usage Examples

### Python Code

```python
from src.rag.retriever import SimpleRetriever
from src.rag.generator import RAGGenerator

# Initialize
retriever = SimpleRetriever()
generator = RAGGenerator()
retriever.load_chunks()

# Query
query = "What are the benefits of Ganoderma?"
results = retriever.retrieve(query, top_k=3)
answer = generator.generate_answer(query, results)

print(answer)
```

### API Request

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the benefits of Ganoderma?", "top_k": 5}'
```

---

## 🎯 System Architecture

```
User
  ↓
Web UI / API
  ↓
RAG System
  ├─ Retriever
  └─ Generator
  ↓
Data Layer
  ├─ PostgreSQL (Metadata)
  ├─ OpenSearch (Vector Search)
  └─ PDF Files
```

---

## 📝 FAQ

### Q: Ollama connection failed?

Confirm Ollama container is running:
```powershell
docker ps | findstr ollama
```

### Q: Cannot find chunk data?

Run PDF processing pipeline:
```powershell
python scripts/test_pdf_processing.py
```

### Q: How to add new papers?

1. Manually download PDF to `data/pdfs/PMC/`
2. Run processing script
3. Restart services

---

**System is ready to use!** 🎉
