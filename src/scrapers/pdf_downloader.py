"""
Enhanced PDF downloader with multiple download strategies.
"""
from typing import Optional, Dict, List
import requests
from pathlib import Path
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
import hashlib
import time

from ..config import settings


class EnhancedPDFDownloader:
    """Enhanced PDF downloader with multiple strategies."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize enhanced PDF downloader.
        
        Args:
            storage_path: Path to store downloaded PDFs
        """
        self.storage_path = Path(storage_path or settings.pdf_storage_path)
        self.session = requests.Session()
        
        # Enhanced headers for better success rate
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        self.session.headers.update(self.base_headers)
    
    def _get_pdf_path(self, paper_id: str, source: str) -> Path:
        """Get the file path for a PDF."""
        source_dir = self.storage_path / source
        source_dir.mkdir(parents=True, exist_ok=True)
        return source_dir / f"{paper_id}.pdf"
    
    def _get_source_specific_headers(self, source: str, paper_url: str) -> Dict[str, str]:
        """
        Get source-specific headers.
        
        Args:
            source: Paper source (PMC, arXiv, etc.)
            paper_url: Original paper URL
            
        Returns:
            Dictionary of headers
        """
        headers = self.base_headers.copy()
        
        if source == 'PMC':
            headers.update({
                'Referer': 'https://www.ncbi.nlm.nih.gov/',
                'Origin': 'https://www.ncbi.nlm.nih.gov',
                'Accept': 'application/pdf,application/x-pdf,*/*',
            })
        elif source == 'arXiv':
            headers.update({
                'Referer': 'https://arxiv.org/',
            })
        
        return headers
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def download_pdf(self, paper_url: str, paper_source: str, paper_id: Optional[str] = None) -> Optional[str]:
        """
        Download PDF using multiple strategies.
        
        Args:
            paper_url: URL of the paper
            paper_source: Source type (PMC, PubMed, arXiv, DOI)
            paper_id: Optional paper identifier
            
        Returns:
            Path to downloaded PDF or None if failed
        """
        if not paper_id:
            paper_id = hashlib.md5(paper_url.encode()).hexdigest()[:12]
        
        pdf_path = self._get_pdf_path(paper_id, paper_source)
        
        # Check if already downloaded
        if pdf_path.exists():
            logger.info(f"PDF already exists: {pdf_path}")
            return str(pdf_path)
        
        # Try multiple strategies
        strategies = [
            self._strategy_direct_pdf,
            self._strategy_with_referer,
            self._strategy_alternative_url,
        ]
        
        for i, strategy in enumerate(strategies, 1):
            logger.info(f"Trying strategy {i}/{len(strategies)}: {strategy.__name__}")
            
            try:
                result = strategy(paper_url, paper_source, paper_id, pdf_path)
                if result:
                    logger.success(f"Successfully downloaded using {strategy.__name__}")
                    return result
            except Exception as e:
                logger.warning(f"Strategy {strategy.__name__} failed: {e}")
                continue
        
        logger.error(f"All download strategies failed for: {paper_url}")
        return None
    
    def _strategy_direct_pdf(self, paper_url: str, source: str, paper_id: str, pdf_path: Path) -> Optional[str]:
        """
        Strategy 1: Direct PDF download with enhanced headers.
        """
        pdf_url = self._get_pdf_url(paper_url, source)
        if not pdf_url:
            return None
        
        headers = self._get_source_specific_headers(source, paper_url)
        
        response = self.session.get(
            pdf_url,
            headers=headers,
            timeout=settings.pdf_timeout_seconds,
            stream=True,
            allow_redirects=True
        )
        
        # Check if we got a PDF
        content_type = response.headers.get('Content-Type', '')
        if response.status_code == 200 and 'pdf' in content_type.lower():
            return self._save_pdf(response, pdf_path)
        
        response.raise_for_status()
        return None
    
    def _strategy_with_referer(self, paper_url: str, source: str, paper_id: str, pdf_path: Path) -> Optional[str]:
        """
        Strategy 2: Visit the page first, then download PDF.
        """
        # First, visit the paper page to get cookies
        logger.info(f"Visiting paper page: {paper_url}")
        self.session.get(paper_url, timeout=30)
        time.sleep(2)  # Wait a bit
        
        # Now try to download PDF
        pdf_url = self._get_pdf_url(paper_url, source)
        if not pdf_url:
            return None
        
        headers = self._get_source_specific_headers(source, paper_url)
        headers['Referer'] = paper_url  # Use the paper page as referer
        
        response = self.session.get(
            pdf_url,
            headers=headers,
            timeout=settings.pdf_timeout_seconds,
            stream=True,
            allow_redirects=True
        )
        
        content_type = response.headers.get('Content-Type', '')
        if response.status_code == 200 and 'pdf' in content_type.lower():
            return self._save_pdf(response, pdf_path)
        
        return None
    
    def _strategy_alternative_url(self, paper_url: str, source: str, paper_id: str, pdf_path: Path) -> Optional[str]:
        """
        Strategy 3: Try alternative PDF URLs.
        """
        alternative_urls = self._get_alternative_pdf_urls(paper_url, source)
        
        for alt_url in alternative_urls:
            logger.info(f"Trying alternative URL: {alt_url}")
            
            try:
                headers = self._get_source_specific_headers(source, paper_url)
                response = self.session.get(
                    alt_url,
                    headers=headers,
                    timeout=settings.pdf_timeout_seconds,
                    stream=True,
                    allow_redirects=True
                )
                
                content_type = response.headers.get('Content-Type', '')
                if response.status_code == 200 and 'pdf' in content_type.lower():
                    return self._save_pdf(response, pdf_path)
            
            except Exception as e:
                logger.debug(f"Alternative URL failed: {e}")
                continue
        
        return None
    
    def _get_pdf_url(self, paper_url: str, source: str) -> Optional[str]:
        """Convert paper URL to PDF download URL."""
        if source == 'PMC':
            # PMC: Try multiple formats
            if paper_url.endswith('/'):
                return f"{paper_url}pdf/"
            else:
                return f"{paper_url}/pdf/"
        
        elif source == 'arXiv':
            # arXiv: https://arxiv.org/abs/2301.12345 -> https://arxiv.org/pdf/2301.12345.pdf
            return paper_url.replace('/abs/', '/pdf/') + '.pdf'
        
        elif source == 'PubMed':
            logger.warning(f"PubMed papers require manual handling: {paper_url}")
            return None
        
        elif source == 'DOI':
            logger.warning(f"DOI links require manual handling: {paper_url}")
            return None
        
        else:
            logger.warning(f"Unknown source type: {source}")
            return None
    
    def _get_alternative_pdf_urls(self, paper_url: str, source: str) -> List[str]:
        """
        Get alternative PDF URLs to try.
        
        Args:
            paper_url: Original paper URL
            source: Source type
            
        Returns:
            List of alternative URLs
        """
        alternatives = []
        
        if source == 'PMC':
            # Extract PMC ID
            import re
            match = re.search(r'PMC(\d+)', paper_url)
            if match:
                pmc_id = match.group(1)
                alternatives.extend([
                    f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/pdf/",
                    f"https://europepmc.org/articles/PMC{pmc_id}?pdf=render",
                    f"https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_pdf/",  # For open access
                ])
        
        return alternatives
    
    def _save_pdf(self, response: requests.Response, pdf_path: Path) -> Optional[str]:
        """
        Save PDF from response.
        
        Args:
            response: HTTP response
            pdf_path: Path to save PDF
            
        Returns:
            Path to saved PDF or None
        """
        # Check file size
        content_length = int(response.headers.get('Content-Length', 0))
        max_size_bytes = settings.pdf_max_size_mb * 1024 * 1024
        
        if content_length > max_size_bytes:
            logger.warning(f"PDF too large: {content_length / 1024 / 1024:.2f} MB")
            return None
        
        # Download and save
        with open(pdf_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Verify PDF
        if not self._verify_pdf(pdf_path):
            logger.error(f"Downloaded file is not a valid PDF: {pdf_path}")
            pdf_path.unlink()
            return None
        
        logger.success(f"Successfully saved: {pdf_path}")
        return str(pdf_path)
    
    def _verify_pdf(self, pdf_path: Path) -> bool:
        """Verify that the file is a valid PDF."""
        try:
            with open(pdf_path, 'rb') as f:
                header = f.read(5)
                return header == b'%PDF-'
        except Exception as e:
            logger.error(f"Error verifying PDF {pdf_path}: {e}")
            return False
    
    def get_download_stats(self) -> Dict[str, int]:
        """Get statistics about downloaded PDFs."""
        stats = {}
        
        for source_dir in self.storage_path.iterdir():
            if source_dir.is_dir():
                pdf_count = len(list(source_dir.glob('*.pdf')))
                stats[source_dir.name] = pdf_count
        
        stats['total'] = sum(stats.values())
        return stats


# Backward compatibility
PDFDownloader = EnhancedPDFDownloader


def main():
    """Test the enhanced PDF downloader."""
    downloader = EnhancedPDFDownloader()
    
    # Test PMC download
    test_url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC11792735/"
    pdf_path = downloader.download_pdf(test_url, "PMC", "PMC11792735")
    
    if pdf_path:
        print(f"✓ Downloaded to: {pdf_path}")
    else:
        print(f"✗ Download failed")
    
    # Get stats
    stats = downloader.get_download_stats()
    print(f"\nDownload stats: {stats}")


if __name__ == "__main__":
    main()
