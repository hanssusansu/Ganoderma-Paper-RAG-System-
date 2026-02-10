"""
Test script for Ganoderma News scraper.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.ganoderma_news import GanodermaScraper
from src.scrapers.pdf_downloader import PDFDownloader
from loguru import logger
import json


def test_single_article():
    """Test scraping a single article."""
    logger.info("=== Testing single article scraping ===")
    
    scraper = GanodermaScraper()
    
    # 測試文章 URL
    test_url = "https://www.ganodermanews.com/index.php/%E7%A0%94%E7%A9%B6%E6%96%B0%E7%9F%A5/2020-2029/747-%E4%BC%8A%E6%9C%97%EF%BC%9A%E8%87%A8%E5%BA%8A%E8%A9%A6%E9%A9%97%E9%A1%AF%E7%A4%BA%EF%BC%8C%E9%9D%88%E8%8A%9D%E5%87%9D%E8%86%A0%E5%8F%AF%E5%8A%A0%E9%80%9F%E6%94%B9%E5%96%84%E5%81%87%E7%89%99%E6%80%A7%E5%8F%A3%E8%85%94%E7%82%8E.html"
    
    paper_info = scraper.extract_paper_links(test_url)
    
    if paper_info:
        logger.success(f"Successfully extracted paper info:")
        logger.info(f"  Title: {paper_info['article_title']}")
        logger.info(f"  Paper URL: {paper_info['paper_url']}")
        logger.info(f"  Source: {paper_info['paper_source']}")
        return paper_info
    else:
        logger.error("Failed to extract paper info")
        return None


def test_pdf_download(paper_info):
    """Test PDF download."""
    if not paper_info:
        logger.warning("Skipping PDF download test (no paper info)")
        return
    
    logger.info("=== Testing PDF download ===")
    
    downloader = PDFDownloader()
    
    # Extract paper ID from URL
    paper_id = paper_info['paper_url'].split('/')[-2] if paper_info['paper_url'].endswith('/') else paper_info['paper_url'].split('/')[-1]
    
    pdf_path = downloader.download_pdf(
        paper_info['paper_url'],
        paper_info['paper_source'],
        paper_id
    )
    
    if pdf_path:
        logger.success(f"Successfully downloaded PDF to: {pdf_path}")
        
        # Get stats
        stats = downloader.get_download_stats()
        logger.info(f"Download statistics: {stats}")
    else:
        logger.error("Failed to download PDF")


def test_category_scraping(limit=5):
    """Test scraping a category."""
    logger.info(f"=== Testing category scraping (limit: {limit}) ===")
    
    scraper = GanodermaScraper()
    
    # 測試「研究新知」分類
    category = "研究新知"
    logger.info(f"Scraping category: {category}")
    
    # Note: This will actually try to scrape the website
    # You may want to comment this out to avoid making too many requests
    
    # article_urls = scraper.scrape_category_page(category)
    # logger.info(f"Found {len(article_urls)} articles")
    
    # # Extract paper links from first few articles
    # papers = []
    # for url in article_urls[:limit]:
    #     paper_info = scraper.extract_paper_links(url)
    #     if paper_info:
    #         papers.append(paper_info)
    
    # logger.success(f"Successfully extracted {len(papers)} papers")
    
    # # Save to file
    # output_file = Path(__file__).parent.parent / "data" / "metadata" / "test_papers.json"
    # output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # with open(output_file, 'w', encoding='utf-8') as f:
    #     json.dump(papers, f, ensure_ascii=False, indent=2)
    
    # logger.info(f"Saved papers to: {output_file}")
    
    logger.warning("Category scraping test is commented out to avoid making too many requests")
    logger.info("Uncomment the code in test_scraper.py to run this test")


def main():
    """Run all tests."""
    logger.info("Starting scraper tests...")
    
    # Test 1: Single article
    paper_info = test_single_article()
    
    # Test 2: PDF download
    if paper_info:
        test_pdf_download(paper_info)
    
    # Test 3: Category scraping (commented out by default)
    # test_category_scraping(limit=5)
    
    logger.success("All tests completed!")


if __name__ == "__main__":
    main()
