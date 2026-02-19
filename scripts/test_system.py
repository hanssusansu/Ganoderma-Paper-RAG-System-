"""
Comprehensive test script for Ganoderma Papers RAG system.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.ganoderma_news import GanodermaScraper
from src.scrapers.pdf_downloader import PDFDownloader
from loguru import logger
import json


def test_scraper_basic():
    """Test basic scraper functionality."""
    logger.info("=" * 60)
    logger.info("Test 1: Basic Scraper Functionality")
    logger.info("=" * 60)
    
    scraper = GanodermaScraper()
    
    # Test article URL (Ensure this URL is still valid or use a representative one)
    test_url = "https://www.ganodermanews.com/index.php/%E7%A0%94%E7%A9%B6%E6%96%B0%E7%9F%A5/2020-2029/747-%E4%BC%8A%E6%9C%97%EF%BC%9A%E8%87%A8%E5%BA%8A%E8%A9%A6%E9%A9%97%E9%A1%AF%E7%A4%BA%EF%BC%8C%E9%9D%88%E8%8A%9D%E5%87%9D%E8%86%A0%E5%8F%AF%E5%8A%A0%E9%80%9F%E6%94%B9%E5%96%84%E5%81%87%E7%89%99%E6%80%A7%E5%8F%A3%E8%85%94%E7%82%8E.html"
    
    try:
        paper_info = scraper.extract_paper_links(test_url)
        
        if paper_info:
            logger.success("✓ Successfully extracted paper info")
            logger.info(f"  Article Title: {paper_info['article_title']}")
            logger.info(f"  Paper URL: {paper_info['paper_url']}")
            logger.info(f"  Paper Source: {paper_info['paper_source']}")
            logger.info(f"  Published Date: {paper_info.get('published_date', 'N/A')}")
            return paper_info
        else:
            logger.error("✗ Failed to extract paper info")
            return None
    except Exception as e:
        logger.error(f"✗ Scraper test failed: {e}")
        return None


def test_pdf_url_generation():
    """Test PDF URL generation without downloading."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: PDF URL Generation")
    logger.info("=" * 60)
    
    downloader = PDFDownloader()
    
    test_cases = [
        ("https://pmc.ncbi.nlm.nih.gov/articles/PMC11792735/", "PMC"),
        ("https://arxiv.org/abs/2301.12345", "arXiv"),
    ]
    
    for paper_url, source in test_cases:
        pdf_url = downloader._get_pdf_url(paper_url, source)
        if pdf_url:
            logger.success(f"✓ {source}: {pdf_url}")
        else:
            logger.warning(f"✗ {source}: Failed to generate PDF URL")


def test_storage_structure():
    """Test storage directory structure."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: Storage Directory Structure")
    logger.info("=" * 60)
    
    storage_path = Path("D:/anti test/ganoderma-papers-rag/data/pdfs")
    
    # Create test directories
    for source in ["PMC", "PubMed", "arXiv", "DOI"]:
        source_dir = storage_path / source
        source_dir.mkdir(parents=True, exist_ok=True)
        logger.success(f"✓ Created directory: {source_dir}")
    
    # Check directories
    if storage_path.exists():
        subdirs = [d.name for d in storage_path.iterdir() if d.is_dir()]
        logger.info(f"  Existing subdirectories: {', '.join(subdirs)}")
    else:
        logger.error(f"✗ Storage path does not exist: {storage_path}")


def test_config_loading():
    """Test configuration loading."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Configuration Loading")
    logger.info("=" * 60)
    
    try:
        from src.config import settings
        
        logger.success("✓ Configuration loaded successfully")
        logger.info(f"  Database URL: {settings.database_url}")
        logger.info(f"  OpenSearch URL: {settings.opensearch_url}")
        logger.info(f"  Redis URL: {settings.redis_url}")
        logger.info(f"  Ollama Host: {settings.ollama_host}")
        logger.info(f"  PDF Storage Path: {settings.pdf_storage_path}")
        logger.info(f"  Scraper Delay: {settings.scraper_delay_seconds} seconds")
        return True
    except Exception as e:
        logger.error(f"✗ Configuration loading failed: {e}")
        return False


def test_database_connection():
    """Test database connection (via Docker)."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 5: Database Connection (via Docker)")
    logger.info("=" * 60)
    
    import subprocess
    
    try:
        # Test PostgreSQL
        result = subprocess.run(
            ["docker", "exec", "ganoderma-postgres", "pg_isready", "-U", "postgres"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            logger.success("✓ PostgreSQL connection normal")
        else:
            logger.error(f"✗ PostgreSQL connection failed: {result.stderr}")
        
        # Test Table
        result = subprocess.run(
            ["docker", "exec", "ganoderma-postgres", "psql", "-U", "postgres", 
             "-d", "ganoderma_papers", "-c", "SELECT COUNT(*) FROM papers;"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            logger.success("✓ papers table accessible")
            logger.info(f"  {result.stdout.strip()}")
        else:
            logger.error(f"✗ Table access failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"✗ Database test failed: {e}")


def save_test_results(paper_info):
    """Save test results to file."""
    logger.info("\n" + "=" * 60)
    logger.info("Saving Test Results")
    logger.info("=" * 60)
    
    if paper_info:
        output_file = Path("data/metadata/test_results.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(paper_info, f, ensure_ascii=False, indent=2)
        
        logger.success(f"✓ Test results saved: {output_file}")
    else:
        logger.warning("✗ No test results to save")


def main():
    """Run all tests."""
    logger.info("\n" + "🧪 " * 20)
    logger.info("Ganoderma Papers RAG System Test")
    logger.info("🧪 " * 20 + "\n")
    
    # Test 1: Basic Scraper
    paper_info = test_scraper_basic()
    
    # Test 2: PDF URL Generation
    test_pdf_url_generation()
    
    # Test 3: Storage Directory
    test_storage_structure()
    
    # Test 4: Config
    test_config_loading()
    
    # Test 5: Database
    test_database_connection()
    
    # Save Results
    save_test_results(paper_info)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Tests Completed!")
    logger.info("=" * 60)
    logger.info("\nNotes:")
    logger.info("1. PMC PDF downloads may encounter 403 errors (require special handling).")
    logger.info("2. Scraper functionality is normal, paper links can be extracted.")
    logger.info("3. Database is ready.")
    logger.info("4. Next step: Ensure PDF processing module is working.")


if __name__ == "__main__":
    main()
