"""
Simple manual download script.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.pdf_downloader import EnhancedPDFDownloader
from src.processors.pdf_parser import PDFParser
from src.processors.text_chunker import TextChunker
from src.processors.metadata_tagger import MetadataTagger
from loguru import logger
import json

# Manually curated list of PMC papers about Ganoderma
PAPERS = [
    ("PMC11792735", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11792735/"),
    ("PMC9572368", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9572368/"),
    ("PMC8401537", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8401537/"),
    ("PMC7824689", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7824689/"),
    ("PMC6982109", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6982109/"),
]

def main():
    logger.info("開始手動下載論文...")
    
    downloader = EnhancedPDFDownloader()
    parser = PDFParser()
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    tagger = MetadataTagger()  # Initialize AI Tagger
    
    all_chunks = []
    downloaded_count = 0
    
    for paper_id, paper_url in PAPERS:
        logger.info(f"\n處理: {paper_id}")
        
        try:
            # Download
            pdf_path = downloader.download_pdf(paper_url, "PMC", paper_id)
            
            if not pdf_path:
                logger.warning(f"下載失敗: {paper_id}")
                continue
            
            downloaded_count += 1
            logger.success(f"✓ 下載成功")
            
            # Parse
            parsed = parser.parse_pdf(pdf_path)
            if not parsed:
                logger.warning(f"解析失敗: {paper_id}")
                continue
            
            logger.success(f"✓ 解析成功: {parsed['num_pages']} 頁")
            
            # AI Metadata Tagging
            logger.info(f"正在進行 AI 標註 (分析部位與萃取法)...")
            ai_tags = tagger.tag_paper(parsed['content'])
            logger.info(f"AI 標註結果: {ai_tags}")
            
            # Prepare metadata
            base_metadata = {
                'paper_id': paper_id,
                'file_name': parsed['file_name'],
                'source_url': paper_url,
                'ai_part_used': ai_tags.get('part_used', 'Unknown'),
                'ai_extraction': ai_tags.get('extraction_method', 'Unknown')
            }
            
            # Chunk
            if parsed['structure']:
                chunks = chunker.chunk_by_sections(
                    parsed['structure'],
                    metadata=base_metadata
                )
            else:
                chunks = chunker.chunk_text(
                    parsed['content'],
                    metadata=base_metadata
                )
            
            all_chunks.extend(chunks)
            logger.success(f"✓ 分塊成功: {len(chunks)} 個")
            
        except Exception as e:
            logger.error(f"錯誤: {e}")
    
    # Save
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "all_chunks.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    
    logger.success(f"\n✓ 完成！")
    logger.info(f"下載論文: {downloaded_count} 篇")
    logger.info(f"總分塊數: {len(all_chunks)} 個")
    logger.info(f"儲存位置: {output_file}")

if __name__ == "__main__":
    main()
