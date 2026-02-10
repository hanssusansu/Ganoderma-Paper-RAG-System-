"""
Test script for PDF processing pipeline.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processors.pdf_parser import PDFParser
from src.processors.text_chunker import TextChunker
from loguru import logger
import json


def test_pdf_processing_pipeline():
    """Test complete PDF processing pipeline."""
    logger.info("=" * 60)
    logger.info("測試 PDF 處理管道")
    logger.info("=" * 60)
    
    # Initialize processors
    parser = PDFParser()
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    
    # Test PDF path
    pdf_path = "data/pdfs/PMC/PMC11792735.pdf"
    
    # Step 1: Parse PDF
    logger.info("\n步驟 1: 解析 PDF")
    parsed = parser.parse_pdf(pdf_path)
    
    if not parsed:
        logger.error("PDF 解析失敗")
        return False
    
    logger.success(f"✓ 解析成功")
    logger.info(f"  檔案: {parsed['file_name']}")
    logger.info(f"  頁數: {parsed['num_pages']}")
    logger.info(f"  章節數: {len(parsed['structure'])}")
    logger.info(f"  內容長度: {len(parsed['content'])} 字元")
    
    # Step 2: Extract abstract
    logger.info("\n步驟 2: 提取摘要")
    abstract = parser.extract_abstract(parsed)
    
    if abstract:
        logger.success(f"✓ 摘要提取成功")
        logger.info(f"  長度: {len(abstract)} 字元")
        logger.info(f"  預覽: {abstract[:150]}...")
    else:
        logger.warning("⚠️ 未找到摘要")
    
    # Step 3: Chunk by sections
    logger.info("\n步驟 3: 按章節分塊")
    
    if parsed['structure']:
        chunks = chunker.chunk_by_sections(
            parsed['structure'],
            metadata={
                'file_name': parsed['file_name'],
                'file_path': parsed['file_path'],
            }
        )
        logger.success(f"✓ 分塊成功（按章節）")
    else:
        # Fallback: chunk全文
        logger.info("  沒有章節結構，使用全文分塊")
        chunks = chunker.chunk_text(
            parsed['content'],
            metadata={
                'file_name': parsed['file_name'],
                'file_path': parsed['file_path'],
            }
        )
        logger.success(f"✓ 分塊成功（全文）")
    
    logger.info(f"  總分塊數: {len(chunks)}")
    
    # Show chunk statistics
    if chunks:
        avg_chars = sum(c['char_count'] for c in chunks) / len(chunks)
        avg_words = sum(c['word_count'] for c in chunks) / len(chunks)
        
        logger.info(f"  平均字元數: {avg_chars:.0f}")
        logger.info(f"  平均單詞數: {avg_words:.0f}")
    
    # Step 4: Save results
    logger.info("\n步驟 4: 儲存結果")
    
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save parsed content
    parsed_file = output_dir / f"{Path(pdf_path).stem}_parsed.json"
    with open(parsed_file, 'w', encoding='utf-8') as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)
    
    logger.success(f"✓ 解析結果已儲存: {parsed_file}")
    
    # Save chunks
    chunks_file = output_dir / f"{Path(pdf_path).stem}_chunks.json"
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    logger.success(f"✓ 分塊結果已儲存: {chunks_file}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("處理總結")
    logger.info("=" * 60)
    logger.info(f"✓ PDF 解析: 成功")
    logger.info(f"✓ 摘要提取: {'成功' if abstract else '未找到'}")
    logger.info(f"✓ 文本分塊: 成功 ({len(chunks)} 個分塊)")
    logger.info(f"✓ 結果儲存: 成功")
    
    return True


def main():
    """Run the test."""
    logger.info("\n" + "🧪 " * 20)
    logger.info("PDF 處理管道測試")
    logger.info("🧪 " * 20 + "\n")
    
    success = test_pdf_processing_pipeline()
    
    if success:
        logger.success("\n✓ 所有測試通過！")
        logger.info("PDF 處理管道運作正常。")
    else:
        logger.error("\n✗ 測試失敗")


if __name__ == "__main__":
    main()
