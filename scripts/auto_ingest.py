"""
Automated ingestion script.
Traverses Ganoderma News to find papers, downloads them, and runs AI tagging + Indexing.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.ganoderma_news import GanodermaScraper
from src.scrapers.pdf_downloader import EnhancedPDFDownloader
from src.processors.pdf_parser import PDFParser
from src.processors.text_chunker import TextChunker
from src.processors.metadata_tagger import MetadataTagger
from loguru import logger
import json
import os

def main():
    logger.info("🚀 啟動自動爬蟲與資料入庫程序...")
    
    # 1. 初始化組件
    scraper = GanodermaScraper()
    downloader = EnhancedPDFDownloader()
    parser = PDFParser()
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    tagger = MetadataTagger()
    
    # 2. 爬取文章列表
    logger.info("正在掃描靈芝新聞網 (Ganoderma News) ...")
    found_papers = scraper.scrape_all_categories()
    
    # 過濾只支援 PMC 的論文
    pmc_papers = [p for p in found_papers if p.get('paper_source') == 'PMC']
    logger.info(f"掃描完成，找到 {len(pmc_papers)} 篇 PMC 論文連結。")
    
    all_chunks = []
    success_count = 0
    
    # 3. 處理每一篇論文
    for paper in pmc_papers:
        paper_id = paper.get('paper_id')
        paper_url = paper.get('paper_url')
        
        if not paper_id or paper_id == 'Unknown':
            continue
            
        # 檢查是否已下載 (簡單檢查)
        if os.path.exists(f"data/pdfs/PMC/{paper_id}.pdf"):
            logger.info(f"[跳過] 已存在: {paper_id}")
            continue
            
        logger.info(f"\n⚡ 處理: {paper_id} ({paper['article_title']})")
        
        try:
            # Download
            pdf_path = downloader.download_pdf(paper_url, "PMC", paper_id)
            if not pdf_path:
                logger.warning(f"下載失敗: {paper_id}")
                continue
            
            # Parse
            parsed = parser.parse_pdf(pdf_path)
            if not parsed:
                logger.warning(f"解析失敗: {paper_id}")
                continue
            
            # AI Metadata Tagging
            logger.info(f"正在進行 AI 標註...")
            ai_tags = tagger.tag_paper(parsed['content'])
            logger.success(f"AI 標註結果: {ai_tags}")
            
            # Chunking
            base_metadata = {
                'paper_id': paper_id,
                'file_name': parsed['file_name'],
                'source_url': paper_url,
                'title': paper['article_title'],
                'ai_part_used': ai_tags.get('part_used', 'Unknown'),
                'ai_extraction': ai_tags.get('extraction_method', 'Unknown')
            }
            
            if parsed['structure']:
                chunks = chunker.chunk_by_sections(parsed['structure'], metadata=base_metadata)
            else:
                chunks = chunker.chunk_text(parsed['content'], metadata=base_metadata)
                
            all_chunks.extend(chunks)
            success_count += 1
            logger.success(f"✓ {paper_id} 處理完成！")
            
        except Exception as e:
            logger.error(f"Error processing {paper_id}: {e}")
            continue

    # 4. 更新資料庫 (合併新舊數據)
    output_file = Path("data/processed/all_chunks.json")
    existing_data = []
    if output_file.exists():
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except:
            pass
            
    final_data = existing_data + all_chunks
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
        
    logger.success(f"\n🎉 任務完成！")
    logger.info(f"本次新增: {success_count} 篇")
    logger.info(f"資料庫總計: {len(set(c['paper_id'] for c in final_data))} 篇論文")

if __name__ == "__main__":
    main()
