"""
Batch download and process papers.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.ganoderma_news import GanodermaScraper
from src.scrapers.pdf_downloader import EnhancedPDFDownloader
from src.processors.pdf_parser import PDFParser
from src.processors.text_chunker import TextChunker
from loguru import logger
import json
import time


def batch_download_papers(max_papers: int = 10):
    """Batch download papers."""
    logger.info("=" * 60)
    logger.info("批次下載論文")
    logger.info("=" * 60)
    
    # Initialize
    scraper = GanodermaScraper()
    downloader = EnhancedPDFDownloader()
    parser = PDFParser()
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    
    # Step 1: Scrape papers
    logger.info("\n步驟 1: 爬取論文列表")
    
    categories = ['研究新知']
    all_papers = []
    
    for category in categories:
        logger.info(f"爬取分類: {category}")
        try:
            # Get article URLs from category page
            article_urls = scraper.scrape_category_page(category)
            logger.info(f"找到 {len(article_urls)} 篇文章")
            
            # Extract paper info from each article
            for article_url in article_urls[:15]:  # Limit to 15 articles
                try:
                    paper_info = scraper.extract_paper_links(article_url)
                    if paper_info:
                        all_papers.append(paper_info)
                        logger.success(f"✓ 提取論文: {paper_info.get('paper_source')}")
                    time.sleep(2)  # Be polite
                except Exception as e:
                    logger.warning(f"提取失敗: {e}")
            
            time.sleep(3)  # Be polite between categories
        except Exception as e:
            logger.error(f"✗ 爬取失敗: {e}")
    
    logger.info(f"\n總共找到 {len(all_papers)} 篇論文")
    
    # Step 2: Download PDFs
    logger.info("\n步驟 2: 下載 PDF")
    
    downloaded = []
    failed = []
    
    for i, paper in enumerate(all_papers[:max_papers], 1):
        paper_url = paper.get('paper_url')
        paper_source = paper.get('paper_source')
        paper_id = paper.get('paper_id')
        
        logger.info(f"\n[{i}/{min(max_papers, len(all_papers))}] {paper_id}")
        
        if not all([paper_url, paper_source, paper_id]):
            logger.warning("缺少必要資訊，跳過")
            continue
        
        try:
            pdf_path = downloader.download_pdf(paper_url, paper_source, paper_id)
            
            if pdf_path:
                logger.success(f"✓ 下載成功: {pdf_path}")
                downloaded.append({
                    **paper,
                    'pdf_path': pdf_path
                })
            else:
                logger.warning(f"✗ 下載失敗")
                failed.append(paper_id)
            
            time.sleep(3)  # Be polite
        
        except Exception as e:
            logger.error(f"✗ 錯誤: {e}")
            failed.append(paper_id)
    
    logger.info(f"\n下載統計:")
    logger.info(f"  成功: {len(downloaded)} 篇")
    logger.info(f"  失敗: {len(failed)} 篇")
    
    # Step 3: Process PDFs
    logger.info("\n步驟 3: 處理 PDF")
    
    all_chunks = []
    
    for i, paper in enumerate(downloaded, 1):
        pdf_path = paper.get('pdf_path')
        paper_id = paper.get('paper_id')
        
        logger.info(f"\n[{i}/{len(downloaded)}] 處理 {paper_id}")
        
        try:
            # Parse PDF
            parsed = parser.parse_pdf(pdf_path)
            
            if not parsed:
                logger.warning("解析失敗")
                continue
            
            # Chunk text
            if parsed['structure']:
                chunks = chunker.chunk_by_sections(
                    parsed['structure'],
                    metadata={
                        'paper_id': paper_id,
                        'file_name': parsed['file_name'],
                        'source_url': paper.get('article_url', ''),
                        'category': paper.get('category', ''),
                    }
                )
            else:
                chunks = chunker.chunk_text(
                    parsed['content'],
                    metadata={
                        'paper_id': paper_id,
                        'file_name': parsed['file_name'],
                        'source_url': paper.get('article_url', ''),
                        'category': paper.get('category', ''),
                    }
                )
            
            all_chunks.extend(chunks)
            logger.success(f"✓ 處理成功: {len(chunks)} 個分塊")
        
        except Exception as e:
            logger.error(f"✗ 處理失敗: {e}")
    
    # Step 4: Save all chunks
    logger.info("\n步驟 4: 儲存分塊")
    
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Combine with existing chunks
    existing_chunks_file = output_dir / "all_chunks.json"
    
    if existing_chunks_file.exists():
        with open(existing_chunks_file, 'r', encoding='utf-8') as f:
            existing_chunks = json.load(f)
        logger.info(f"載入現有分塊: {len(existing_chunks)} 個")
        all_chunks.extend(existing_chunks)
    
    # Remove duplicates by paper_id
    seen_papers = set()
    unique_chunks = []
    
    for chunk in all_chunks:
        paper_id = chunk.get('paper_id', '')
        chunk_index = chunk.get('chunk_index', 0)
        key = f"{paper_id}_{chunk_index}"
        
        if key not in seen_papers:
            seen_papers.add(key)
            unique_chunks.append(chunk)
    
    # Save
    with open(existing_chunks_file, 'w', encoding='utf-8') as f:
        json.dump(unique_chunks, f, ensure_ascii=False, indent=2)
    
    logger.success(f"✓ 儲存完成: {len(unique_chunks)} 個分塊")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("批次處理完成")
    logger.info("=" * 60)
    logger.info(f"爬取論文: {len(all_papers)} 篇")
    logger.info(f"下載成功: {len(downloaded)} 篇")
    logger.info(f"處理成功: {len(all_chunks)} 個新分塊")
    logger.info(f"總分塊數: {len(unique_chunks)} 個")
    logger.info(f"儲存位置: {existing_chunks_file}")
    
    return {
        'scraped': len(all_papers),
        'downloaded': len(downloaded),
        'processed': len(all_chunks),
        'total_chunks': len(unique_chunks)
    }


def main():
    """Run batch download."""
    logger.info("\n" + "🍄 " * 20)
    logger.info("批次下載靈芝論文")
    logger.info("🍄 " * 20 + "\n")
    
    result = batch_download_papers(max_papers=10)
    
    logger.success("\n✓ 批次下載完成！")
    logger.info(f"\n現在知識庫有 {result['total_chunks']} 個分塊可用")
    logger.info("重新啟動 Web 介面即可使用新的論文資料！")


if __name__ == "__main__":
    main()
