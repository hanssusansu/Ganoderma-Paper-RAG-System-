"""
Configuration management for Ganoderma Papers RAG system.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Main application settings."""
    
    # Database
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_db: str = Field(default="ganoderma_papers", env="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", env="POSTGRES_PASSWORD")
    
    # OpenSearch
    opensearch_host: str = Field(default="localhost", env="OPENSEARCH_HOST")
    opensearch_port: int = Field(default=9200, env="OPENSEARCH_PORT")
    opensearch_user: str = Field(default="admin", env="OPENSEARCH_USER")
    opensearch_password: str = Field(default="admin", env="OPENSEARCH_PASSWORD")
    opensearch_index: str = Field(default="ganoderma_papers", env="OPENSEARCH_INDEX")
    
    # Redis
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # Ollama
    ollama_host: str = Field(default="http://127.0.0.1:11434", env="OLLAMA_HOST")
    ollama_model: str = Field(default="qwen2.5:14b", env="OLLAMA_MODEL")
    
    # Jina
    jina_api_key: str = Field(default="", env="JINA_API_KEY")
    jina_model: str = Field(default="jina-embeddings-v3", env="JINA_MODEL")
    
    # Scraper
    scraper_user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        env="SCRAPER_USER_AGENT"
    )
    scraper_delay_seconds: int = Field(default=2, env="SCRAPER_DELAY_SECONDS")
    scraper_max_retries: int = Field(default=3, env="SCRAPER_MAX_RETRIES")
    
    # PDF
    pdf_storage_path: str = Field(default="./data/pdfs", env="PDF_STORAGE_PATH")
    pdf_max_size_mb: int = Field(default=50, env="PDF_MAX_SIZE_MB")
    pdf_timeout_seconds: int = Field(default=30, env="PDF_TIMEOUT_SECONDS")
    
    # Chunking
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    chunk_min_size: int = Field(default=100, env="CHUNK_MIN_SIZE")
    
    # RAG
    rag_top_k: int = Field(default=10, env="RAG_TOP_K")
    rag_min_score: float = Field(default=0.5, env="RAG_MIN_SCORE")
    rag_temperature: float = Field(default=0.7, env="RAG_TEMPERATURE")
    rag_max_tokens: int = Field(default=2000, env="RAG_MAX_TOKENS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Helper properties
    @property
    def database_url(self) -> str:
        """PostgreSQL connection string."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def opensearch_url(self) -> str:
        """OpenSearch URL."""
        return f"http://{self.opensearch_host}:{self.opensearch_port}"
    
    @property
    def redis_url(self) -> str:
        """Redis URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


# Global settings instance
settings = Settings()
