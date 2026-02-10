"""
Embedder for generating vector embeddings from text.
"""
from typing import List, Dict, Optional
from loguru import logger
import requests
import numpy as np


class JinaEmbedder:
    """Generate embeddings using Jina AI API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "jina-embeddings-v2-base-zh"):
        """
        Initialize Jina embedder.
        
        Args:
            api_key: Jina API key (optional for local testing)
            model: Model name
        """
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.jina.ai/v1/embeddings"
        self.dimension = 768  # Default dimension for base model
    
    def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None
        
        try:
            # For testing without API key, return random vector
            if not self.api_key:
                logger.warning("No API key provided, using random embeddings for testing")
                return self._generate_random_embedding()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "input": [text]
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            embedding = result["data"][0]["embedding"]
            
            return embedding
        
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def embed_batch(self, texts: List[str], batch_size: int = 10) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            for text in batch:
                embedding = self.embed_text(text)
                embeddings.append(embedding)
        
        logger.success(f"Generated {len(embeddings)} embeddings")
        return embeddings
    
    def _generate_random_embedding(self) -> List[float]:
        """Generate random embedding for testing."""
        return np.random.randn(self.dimension).tolist()


def main():
    """Test the embedder."""
    embedder = JinaEmbedder()
    
    # Test text
    test_text = "Ganoderma lucidum has immunomodulatory effects."
    
    embedding = embedder.embed_text(test_text)
    
    if embedding:
        print(f"✓ Generated embedding")
        print(f"  Dimension: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
    else:
        print("✗ Failed to generate embedding")


if __name__ == "__main__":
    main()
