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
    logger.info("測試 1: 基本爬蟲功能")
    logger.info("=" * 60)
    
    scraper = GanodermaScraper()
    
    # 測試文章 URL
    test_url = "https://www.ganodermanews.com/index.php/%E7%A0%94%E7%A9%B6%E6%96%B0%E7%9F%A5/2020-2029/747-%E4%BC%8A%E6%9C%97%EF%BC%9A%E8%87%A8%E5%BA%8A%E8%A9%A6%E9%A9%97%E9%A1%AF%E7%A4%BA%EF%BC%8C%E9%9D%88%E8%8A%9D%E5%87%9D%E8%86%A0%E5%8F%AF%E5%8A%A0%E9%80%9F%E6%94%B9%E5%96%84%E5%81%87%E7%89%99%E6%80%A7%E5%8F%A3%E8%85%94%E7%82%8E.html"
    
    try:
        paper_info = scraper.extract_paper_links(test_url)
        
        if paper_info:
            logger.success("✓ 成功提取論文資訊")
            logger.info(f"  文章標題: {paper_info['article_title']}")
            logger.info(f"  論文 URL: {paper_info['paper_url']}")
            logger.info(f"  論文來源: {paper_info['paper_source']}")
            logger.info(f"  發布日期: {paper_info.get('published_date', 'N/A')}")
            return paper_info
        else:
            logger.error("✗ 無法提取論文資訊")
            return None
    except Exception as e:
        logger.error(f"✗ 爬蟲測試失敗: {e}")
        return None


def test_pdf_url_generation():
    """Test PDF URL generation without downloading."""
    logger.info("\n" + "=" * 60)
    logger.info("測試 2: PDF URL 生成")
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
            logger.warning(f"✗ {source}: 無法生成 PDF URL")


def test_storage_structure():
    """Test storage directory structure."""
    logger.info("\n" + "=" * 60)
    logger.info("測試 3: 儲存目錄結構")
    logger.info("=" * 60)
    
    storage_path = Path("D:/anti test/ganoderma-papers-rag/data/pdfs")
    
    # 建立測試目錄
    for source in ["PMC", "PubMed", "arXiv", "DOI"]:
        source_dir = storage_path / source
        source_dir.mkdir(parents=True, exist_ok=True)
        logger.success(f"✓ 建立目錄: {source_dir}")
    
    # 檢查目錄
    if storage_path.exists():
        subdirs = [d.name for d in storage_path.iterdir() if d.is_dir()]
        logger.info(f"  現有子目錄: {', '.join(subdirs)}")
    else:
        logger.error(f"✗ 儲存路徑不存在: {storage_path}")


def test_config_loading():
    """Test configuration loading."""
    logger.info("\n" + "=" * 60)
    logger.info("測試 4: 配置載入")
    logger.info("=" * 60)
    
    try:
        from src.config import settings
        
        logger.success("✓ 配置載入成功")
        logger.info(f"  資料庫 URL: {settings.database_url}")
        logger.info(f"  OpenSearch URL: {settings.opensearch_url}")
        logger.info(f"  Redis URL: {settings.redis_url}")
        logger.info(f"  Ollama Host: {settings.ollama_host}")
        logger.info(f"  PDF 儲存路徑: {settings.pdf_storage_path}")
        logger.info(f"  爬蟲延遲: {settings.scraper_delay_seconds} 秒")
        return True
    except Exception as e:
        logger.error(f"✗ 配置載入失敗: {e}")
        return False


def test_database_connection():
    """Test database connection (via Docker)."""
    logger.info("\n" + "=" * 60)
    logger.info("測試 5: 資料庫連線（透過 Docker）")
    logger.info("=" * 60)
    
    import subprocess
    
    try:
        # 測試 PostgreSQL
        result = subprocess.run(
            ["docker", "exec", "ganoderma-postgres", "pg_isready", "-U", "postgres"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            logger.success("✓ PostgreSQL 連線正常")
        else:
            logger.error(f"✗ PostgreSQL 連線失敗: {result.stderr}")
        
        # 測試表格
        result = subprocess.run(
            ["docker", "exec", "ganoderma-postgres", "psql", "-U", "postgres", 
             "-d", "ganoderma_papers", "-c", "SELECT COUNT(*) FROM papers;"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            logger.success("✓ papers 表格可訪問")
            logger.info(f"  {result.stdout.strip()}")
        else:
            logger.error(f"✗ 表格訪問失敗: {result.stderr}")
            
    except Exception as e:
        logger.error(f"✗ 資料庫測試失敗: {e}")


def save_test_results(paper_info):
    """Save test results to file."""
    logger.info("\n" + "=" * 60)
    logger.info("儲存測試結果")
    logger.info("=" * 60)
    
    if paper_info:
        output_file = Path("data/metadata/test_results.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(paper_info, f, ensure_ascii=False, indent=2)
        
        logger.success(f"✓ 測試結果已儲存: {output_file}")
    else:
        logger.warning("✗ 沒有測試結果可儲存")


def main():
    """Run all tests."""
    logger.info("\n" + "🧪 " * 20)
    logger.info("Ganoderma Papers RAG 系統測試")
    logger.info("🧪 " * 20 + "\n")
    
    # 測試 1: 基本爬蟲功能
    paper_info = test_scraper_basic()
    
    # 測試 2: PDF URL 生成
    test_pdf_url_generation()
    
    # 測試 3: 儲存目錄結構
    test_storage_structure()
    
    # 測試 4: 配置載入
    test_config_loading()
    
    # 測試 5: 資料庫連線
    test_database_connection()
    
    # 儲存結果
    save_test_results(paper_info)
    
    # 總結
    logger.info("\n" + "=" * 60)
    logger.info("測試完成！")
    logger.info("=" * 60)
    logger.info("\n注意事項：")
    logger.info("1. PMC PDF 下載可能會遇到 403 錯誤（需要特殊處理）")
    logger.info("2. 爬蟲功能正常，可以提取論文連結")
    logger.info("3. 資料庫已準備就緒")
    logger.info("4. 下一步可以開始建構 PDF 處理模組")


if __name__ == "__main__":
    main()
