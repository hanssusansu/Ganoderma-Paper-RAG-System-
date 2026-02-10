"""
FastAPI service for Ganoderma Papers RAG system.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rag.retriever import SimpleRetriever
from src.rag.generator import RAGGenerator
from loguru import logger


# Pydantic models
class QueryRequest(BaseModel):
    """Query request model."""
    question: str
    top_k: int = 5


class Source(BaseModel):
    """Source citation model."""
    chunk_index: int
    section: Optional[str] = None
    page: Optional[int] = None
    file_name: Optional[str] = None
    score: float
    content_preview: str


class QueryResponse(BaseModel):
    """Query response model."""
    question: str
    answer: str
    sources: List[Source]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    chunks_loaded: int
    ready: bool


# Initialize FastAPI app
app = FastAPI(
    title="Ganoderma Papers RAG API",
    description="REST API for querying Ganoderma research papers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
retriever = SimpleRetriever()
generator = RAGGenerator()

try:
    retriever.load_chunks()
    system_ready = True
    logger.success("RAG system initialized")
except Exception as e:
    logger.error(f"Failed to initialize RAG system: {e}")
    system_ready = False


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Ganoderma Papers RAG API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if system_ready else "unhealthy",
        chunks_loaded=len(retriever.chunks) if system_ready else 0,
        ready=system_ready
    )


@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query(request: QueryRequest):
    """
    Query the RAG system.
    
    Args:
        request: Query request
        
    Returns:
        Query response with answer and sources
    """
    if not system_ready:
        raise HTTPException(
            status_code=503,
            detail="RAG system is not ready"
        )
    
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    
    try:
        # Retrieve relevant chunks
        results = retriever.retrieve(request.question, top_k=request.top_k)
        
        if not results:
            return QueryResponse(
                question=request.question,
                answer="抱歉，我找不到相關的資訊來回答您的問題。",
                sources=[]
            )
        
        # Generate answer
        answer = generator.generate_answer(request.question, results)
        
        # Format sources
        sources = [
            Source(
                chunk_index=r.get('chunk_index', 0),
                section=r.get('section'),
                page=r.get('page'),
                file_name=r.get('file_name'),
                score=r.get('score', 0),
                content_preview=r['content'][:200] + "..."
            )
            for r in results
        ]
        
        return QueryResponse(
            question=request.question,
            answer=answer,
            sources=sources
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/stats", tags=["Stats"])
async def get_stats():
    """Get system statistics."""
    if not system_ready:
        raise HTTPException(
            status_code=503,
            detail="RAG system is not ready"
        )
    
    return {
        "total_chunks": len(retriever.chunks),
        "files_processed": len(set(c.get('file_name', '') for c in retriever.chunks)),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
