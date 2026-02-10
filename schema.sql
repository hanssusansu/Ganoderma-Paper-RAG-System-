-- Ganoderma Papers RAG Database Schema

-- Create papers table
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

-- Create paper_chunks table
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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_paper_id ON papers(paper_id);
CREATE INDEX IF NOT EXISTS idx_publication_date ON papers(publication_date);
CREATE INDEX IF NOT EXISTS idx_category ON papers(category);
CREATE INDEX IF NOT EXISTS idx_chunk_paper_id ON paper_chunks(paper_id);

-- Display success message
SELECT 'Database schema created successfully!' AS status;
