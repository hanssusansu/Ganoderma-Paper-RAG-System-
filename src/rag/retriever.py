"""
Simple RAG retriever for finding relevant chunks.
"""
from typing import List, Dict, Optional
from loguru import logger
import json
from pathlib import Path
import numpy as np


class SimpleRetriever:
    """Simple retriever using keyword matching and vector similarity."""
    
    def __init__(self, chunks_dir: str = "data/processed"):
        """
        Initialize retriever.
        
        Args:
            chunks_dir: Directory containing processed chunks
        """
        self.chunks_dir = Path(chunks_dir)
        self.chunks = []
        self.embeddings = []
    
    def load_chunks(self, chunks_file: Optional[str] = None):
        """
        Load chunks from file.
        
        Args:
            chunks_file: Path to chunks JSON file
        """
        if chunks_file:
            file_path = Path(chunks_file)
        else:
            # Try to load all_chunks.json first
            all_chunks_file = self.chunks_dir / "all_chunks.json"
            if all_chunks_file.exists():
                file_path = all_chunks_file
            else:
                # Fallback: Load all chunks files
                chunk_files = list(self.chunks_dir.glob("*_chunks.json"))
                if not chunk_files:
                    logger.warning(f"No chunks files found in {self.chunks_dir}")
                    return
                file_path = chunk_files[0]  # Use first file
        
        logger.info(f"Loading chunks from: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        
        logger.success(f"Loaded {len(self.chunks)} chunks")
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        method: str = "keyword"
    ) -> List[Dict]:
        """
        Retrieve relevant chunks.
        
        Args:
            query: Search query
            top_k: Number of results to return
            method: Retrieval method ('keyword' or 'vector')
            
        Returns:
            List of relevant chunks with scores
        """
        if not self.chunks:
            logger.warning("No chunks loaded")
            return []
        
        # Translate query to English for better matching with English papers
        search_query = self._translate_query(query)
        logger.info(f"Original query: {query} -> Search query: {search_query}")
        
        if method == "keyword":
            return self._keyword_retrieval(search_query, top_k)
        elif method == "vector":
            return self._vector_retrieval(search_query, top_k)
        else:
            logger.error(f"Unknown retrieval method: {method}")
            return []

    def _translate_query(self, query: str) -> str:
        """
        Translate query to English keywords using basic mapping or Ollama.
        
        Args:
            query: Original query
            
        Returns:
            Translated query or keywords
        """
        # Dictionary for common keywords (Fast path)
        keywords_map = {
            "靈芝": "Ganoderma lucidum",
            "免疫": "immune immunomodulatory",
            "癌症": "cancer tumor",
            "功效": "effect benefit",
            "臨床": "clinical",
            "試驗": "trial",
            "多醣體": "polysaccharide",
            "三萜": "triterpenoid",
        }
        
        translated_parts = []
        
        # Simple extraction first
        for key, value in keywords_map.items():
            if key in query:
                translated_parts.append(value)
        
        # If we have keywords, return them
        if translated_parts:
            return " ".join(translated_parts) + " " + query  # Append original just in case
            
        # If no keywords matched, try to use Ollama (if available) or return original
        # For now, let's just return original query if no basic keywords match
        # to identify that we need a better translation mechanism later
        return query
    
    def _keyword_retrieval(self, query: str, top_k: int) -> List[Dict]:
        """
        Simple keyword-based retrieval.
        
        Args:
            query: Search query (potentially translated)
            top_k: Number of results
            
        Returns:
            List of chunks with scores
        """
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        scored_chunks = []
        
        for chunk in self.chunks:
            content = chunk.get('content', '').lower()
            
            # Calculate simple score based on term frequency
            score = 0
            for term in query_terms:
                if len(term) < 3: continue  # Skip short words
                score += content.count(term)
            
            if score > 0:
                scored_chunks.append({
                    **chunk,
                    'score': score
                })
        
        # Sort by score
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top k
        results = scored_chunks[:top_k]
        
        logger.info(f"Retrieved {len(results)} chunks using keyword search")
        return results
    
    def _vector_retrieval(self, query: str, top_k: int) -> List[Dict]:
        """
        Vector-based retrieval (placeholder).
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of chunks with scores
        """
        logger.warning("Vector retrieval not yet implemented, falling back to keyword")
        return self._keyword_retrieval(query, top_k)


def main():
    """Test the retriever."""
    retriever = SimpleRetriever()
    
    # Load chunks
    retriever.load_chunks()
    
    # Test query
    query = "Ganoderma lucidum immunomodulatory effects"
    
    results = retriever.retrieve(query, top_k=3)
    
    print(f"\n查詢: {query}")
    print(f"找到 {len(results)} 個相關分塊:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. 分數: {result['score']}")
        print(f"   章節: {result.get('section', 'N/A')}")
        print(f"   內容預覽: {result['content'][:150]}...")
        print()


if __name__ == "__main__":
    main()
