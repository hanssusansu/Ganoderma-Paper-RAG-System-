"""
Web scraping utilities for Ganoderma News website.
"""
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import time
import re
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import settings


class GanodermaScraper:
    """Scraper for Ganoderma News website."""
    
    # 支援的專欄列表
    CATEGORIES = [
        "研究新知/2020-2029", # Decade archives
        "研究新知/2010-2019",
        "研究新知/2000-2009",
        "靈芝調節免疫力",     # Immune Regulation
        "天選之材GMI",        # GMI
        "靈芝與我",          # Ganoderma and Me
        "靈芝新聞",          # Ganoderma News
        "活動報導",          # Event Reports
        "歷史回顧",          # Historical Review
    ]
    
    BASE_URL = "https://www.ganodermanews.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.scraper_user_agent
        })
        self.delay = settings.scraper_delay_seconds
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _fetch_url(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch URL with retry logic.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            logger.info(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            time.sleep(self.delay)  # Respectful crawling
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            raise
    
    def scrape_category_page(self, category: str) -> List[str]:
        """
        Scrape all article URLs from a category page.
        
        Args:
            category: Category name (e.g., "研究新知")
            
        Returns:
            List of article URLs
        """
        # 構建分類頁面 URL（需要根據實際網站結構調整）
        category_url = f"{self.BASE_URL}/index.php/{category}.html"
        
        soup = self._fetch_url(category_url)
        if not soup:
            return []
        
        article_urls = []
        
        # 查找所有文章連結（需要根據實際 HTML 結構調整選擇器）
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # 過濾出文章連結
            if '/index.php/' in href and category in href:
                full_url = href if href.startswith('http') else f"{self.BASE_URL}{href}"
                article_urls.append(full_url)
        
        logger.info(f"Found {len(article_urls)} articles in category: {category}")
        return list(set(article_urls))  # 去重
    
    def extract_paper_links(self, article_url: str) -> Optional[Dict]:
        """
        Extract academic paper links from an article.
        
        Args:
            article_url: URL of the article
            
        Returns:
            Dictionary with paper information or None if no paper found
        """
        soup = self._fetch_url(article_url)
        if not soup:
            return None
        
        # 提取文章標題
        title_tag = soup.find('h1') or soup.find('h2')
        article_title = title_tag.get_text(strip=True) if title_tag else "Unknown"
        
        # 查找論文連結
        paper_url = None
        paper_source = None
        
        # 常見的學術論文網站模式
        paper_patterns = {
            'PMC': r'https?://(?:www\.|pmc\.)?ncbi\.nlm\.nih\.gov/(?:pmc/)?articles/(PMC\d+)',
            'PubMed': r'https?://(?:www\.)?pubmed\.ncbi\.nlm\.nih\.gov/(\d+)',
            'arXiv': r'https?://(?:www\.)?arxiv\.org/abs/([\d.]+)',
            'DOI': r'https?://(?:www\.)?doi\.org/(10\.\d+/[^\s]+)',
        }
        
        # 搜尋所有連結
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            for source, pattern in paper_patterns.items():
                match = re.search(pattern, href)
                if match:
                    paper_url = href
                    paper_source = source
                    
                    if len(match.groups()) > 0:
                        paper_id = match.group(1)
                        if source == 'DOI':
                             # Normalize DOI to be filename safe
                            paper_id = paper_id.replace('/', '_').replace('.', '_')
                            # For now, we mainly want PMC. But if we find DOI, we can return it.
                            # Ideally we should resolve DOI to PMC, but let's at least capture it.
                            paper_id = f"DOI_{paper_id}"
                            
                    logger.info(f"    -> Found {source} link: {href} (ID: {paper_id if 'paper_id' in locals() else 'None'})")
                    break
            
            if paper_url:
                break
        
        if not paper_url:
            logger.debug(f"No paper link found in: {article_url}")
            return None
        
        # 提取發布日期（如果有）
        published_date = self._extract_date(soup)
        
        result = {
            'article_title': article_title,
            'article_url': article_url,
            'paper_url': paper_url,
            'paper_source': paper_source,
            'paper_id': paper_id if 'paper_id' in locals() else 'Unknown',
            'published_date': published_date,
            'has_pdf': True  # 稍後會驗證
        }
        
        logger.info(f"Found paper: {paper_source} - {article_title}")
        return result
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date from article page."""
        # 嘗試多種日期格式和位置
        date_patterns = [
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
        ]
        
        text = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None
    
    def scrape_all_categories(self) -> List[Dict]:
        """
        Scrape all categories and extract paper links.
        
        Returns:
            List of paper information dictionaries
        """
        all_papers = []
        seen_urls = set()
        
        for category in self.CATEGORIES:
            logger.info(f"Scraping category: {category}")
            
            try:
                # 獲取分類下的所有文章
                article_urls = self.scrape_category_page(category)
                
                # 提取每篇文章的論文連結
                for article_url in article_urls:
                    try:
                        paper_info = self.extract_paper_links(article_url)
                        
                        if paper_info and paper_info['paper_url'] not in seen_urls:
                            paper_info['category'] = category
                            all_papers.append(paper_info)
                            seen_urls.add(paper_info['paper_url'])
                    
                    except Exception as e:
                        logger.error(f"Error processing article {article_url}: {e}")
                        continue
            
            except Exception as e:
                logger.error(f"Error scraping category {category}: {e}")
                continue
        
        logger.info(f"Total papers found: {len(all_papers)}")
        return all_papers


def main():
    """Test the scraper."""
    scraper = GanodermaScraper()
    
    # 測試單篇文章
    test_url = "https://www.ganodermanews.com/index.php/%E7%A0%94%E7%A9%B6%E6%96%B0%E7%9F%A5/2020-2029/747-%E4%BC%8A%E6%9C%97%EF%BC%9A%E8%87%A8%E5%BA%8A%E8%A9%A6%E9%A9%97%E9%A1%AF%E7%A4%BA%EF%BC%8C%E9%9D%88%E8%8A%9D%E5%87%9D%E8%86%A0%E5%8F%AF%E5%8A%A0%E9%80%9F%E6%94%B9%E5%96%84%E5%81%87%E7%89%99%E6%80%A7%E5%8F%A3%E8%85%94%E7%82%8E.html"
    
    paper_info = scraper.extract_paper_links(test_url)
    print(f"Paper info: {paper_info}")


if __name__ == "__main__":
    main()
