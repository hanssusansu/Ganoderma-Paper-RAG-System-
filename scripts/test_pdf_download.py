"""
Test script for enhanced PDF downloader.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.pdf_downloader import EnhancedPDFDownloader
from loguru import logger


def test_pmc_download():
    """Test PMC PDF download with multiple strategies."""
    logger.info("=" * 60)
    logger.info("測試 PMC PDF 下載（多策略）")
    logger.info("=" * 60)
    
    downloader = EnhancedPDFDownloader()
    
    # Test cases
    test_cases = [
        ("PMC11792735", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11792735/"),
        # 可以添加更多測試案例
    ]
    
    results = []
    
    for paper_id, paper_url in test_cases:
        logger.info(f"\n測試論文: {paper_id}")
        logger.info(f"URL: {paper_url}")
        
        try:
            pdf_path = downloader.download_pdf(paper_url, "PMC", paper_id)
            
            if pdf_path:
                logger.success(f"✓ 下載成功: {pdf_path}")
                
                # Check file size
                file_size = Path(pdf_path).stat().st_size
                logger.info(f"  檔案大小: {file_size / 1024:.2f} KB")
                
                results.append({
                    'paper_id': paper_id,
                    'status': 'success',
                    'path': pdf_path,
                    'size': file_size
                })
            else:
                logger.error(f"✗ 下載失敗: {paper_id}")
                results.append({
                    'paper_id': paper_id,
                    'status': 'failed'
                })
        
        except Exception as e:
            logger.error(f"✗ 錯誤: {e}")
            results.append({
                'paper_id': paper_id,
                'status': 'error',
                'error': str(e)
            })
    
    return results


def test_arxiv_download():
    """Test arXiv PDF download."""
    logger.info("\n" + "=" * 60)
    logger.info("測試 arXiv PDF 下載")
    logger.info("=" * 60)
    
    downloader = EnhancedPDFDownloader()
    
    # Use a real arXiv paper
    test_url = "https://arxiv.org/abs/2301.00001"
    paper_id = "2301.00001"
    
    logger.info(f"測試論文: {paper_id}")
    logger.info(f"URL: {test_url}")
    
    try:
        pdf_path = downloader.download_pdf(test_url, "arXiv", paper_id)
        
        if pdf_path:
            logger.success(f"✓ 下載成功: {pdf_path}")
            file_size = Path(pdf_path).stat().st_size
            logger.info(f"  檔案大小: {file_size / 1024:.2f} KB")
            return True
        else:
            logger.error(f"✗ 下載失敗")
            return False
    
    except Exception as e:
        logger.error(f"✗ 錯誤: {e}")
        return False


def show_download_stats():
    """Show download statistics."""
    logger.info("\n" + "=" * 60)
    logger.info("下載統計")
    logger.info("=" * 60)
    
    downloader = EnhancedPDFDownloader()
    stats = downloader.get_download_stats()
    
    for source, count in stats.items():
        logger.info(f"  {source}: {count} 個檔案")


def main():
    """Run all tests."""
    logger.info("\n" + "🧪 " * 20)
    logger.info("增強版 PDF 下載器測試")
    logger.info("🧪 " * 20 + "\n")
    
    # Test 1: PMC download
    pmc_results = test_pmc_download()
    
    # Test 2: arXiv download (optional)
    # arxiv_result = test_arxiv_download()
    
    # Show stats
    show_download_stats()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("測試總結")
    logger.info("=" * 60)
    
    success_count = sum(1 for r in pmc_results if r['status'] == 'success')
    total_count = len(pmc_results)
    
    logger.info(f"PMC 下載成功率: {success_count}/{total_count}")
    
    if success_count > 0:
        logger.success("\n✓ 至少有一個 PDF 下載成功！")
        logger.info("增強版下載器運作正常。")
    else:
        logger.warning("\n⚠️ 所有下載都失敗了。")
        logger.info("可能需要：")
        logger.info("1. 檢查網路連線")
        logger.info("2. 使用 VPN")
        logger.info("3. 考慮使用 Selenium")
        logger.info("4. 或使用 PMC API")


if __name__ == "__main__":
    main()
