"""
Initialize database schema for Ganoderma Papers RAG system.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from loguru import logger
from src.config import settings


def create_tables():
    """Create database tables."""
    
    engine = create_engine(settings.database_url)
    
    # SQL for creating tables
    create_papers_table = """
    CREATE TABLE IF NOT EXISTS papers (
        id SERIAL PRIMARY KEY,
        paper_id VARCHAR(255) UNIQUE NOT NULL,
        title TEXT NOT NULL,
        authors TEXT[],
        abstract TEXT,
        journal VARCHAR(500),
        publication_date DATE,
        doi VARCHAR(255),
        paper_url TEXT NOT NULL,
        pdf_path TEXT,
        source_article_url TEXT,
        source_article_title TEXT,
        category VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    create_chunks_table = """
    CREATE TABLE IF NOT EXISTS paper_chunks (
        id SERIAL PRIMARY KEY,
        chunk_id VARCHAR(255) UNIQUE NOT NULL,
        paper_id VARCHAR(255) REFERENCES papers(paper_id) ON DELETE CASCADE,
        section VARCHAR(255),
        chunk_index INTEGER,
        total_chunks INTEGER,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    create_indexes = """
    CREATE INDEX IF NOT EXISTS idx_paper_id ON papers(paper_id);
    CREATE INDEX IF NOT EXISTS idx_publication_date ON papers(publication_date);
    CREATE INDEX IF NOT EXISTS idx_category ON papers(category);
    CREATE INDEX IF NOT EXISTS idx_chunk_paper_id ON paper_chunks(paper_id);
    """
    
    try:
        with engine.connect() as conn:
            logger.info("Creating papers table...")
            conn.execute(text(create_papers_table))
            conn.commit()
            
            logger.info("Creating paper_chunks table...")
            conn.execute(text(create_chunks_table))
            conn.commit()
            
            logger.info("Creating indexes...")
            for index_sql in create_indexes.split(';'):
                if index_sql.strip():
                    conn.execute(text(index_sql))
            conn.commit()
            
            logger.success("Database schema created successfully!")
    
    except Exception as e:
        logger.error(f"Error creating database schema: {e}")
        raise


def main():
    """Main function."""
    logger.info("Initializing database...")
    logger.info(f"Database: {settings.postgres_db}")
    logger.info(f"Host: {settings.postgres_host}:{settings.postgres_port}")
    
    create_tables()
    
    logger.success("Database initialization complete!")


if __name__ == "__main__":
    main()
