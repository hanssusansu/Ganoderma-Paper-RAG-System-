"""
Debug script to check what links are actually being seen by the scraper.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.ganoderma_news import GanodermaScraper
import logging

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_category():
    scraper = GanodermaScraper()
    
    # Target "Research News" category page
    category = "研究新知"
    url = f"{scraper.BASE_URL}/index.php/{category}.html"
    
    print(f"Fetching: {url}")
    soup = scraper._fetch_url(url)
    
    if not soup:
        print("Failed to fetch.")
        return

    print("\n--- Reviewing Article Links ---")
    article_urls = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/index.php/' in href and category in href:
             full_url = href if href.startswith('http') else f"{scraper.BASE_URL}{href}"
             article_urls.append(full_url)
    
    print(f"Found {len(article_urls)} articles.")
    
    # Pick the first 5 articles and check their paper links
    for i, art_url in enumerate(article_urls[:5]):
        print(f"\n[{i+1}] Checking Article: {art_url}")
        art_soup = scraper._fetch_url(art_url)
        if not art_soup:
            continue
            
        print("  Scanning for paper links...")
        found = False
        for link in art_soup.find_all('a', href=True):
            href = link['href']
            # Print ALL external links to see what we are missing
            if 'ganodermanews' not in href and 'javascript' not in href and '#' not in href:
                 print(f"    Found external link: {href}")
                 
                 # Test PMC regex
                 import re
                 pmc_pattern = r'https?://(?:www\.|pmc\.)?ncbi\.nlm\.nih\.gov/(?:pmc/)?articles/(PMC\d+)'
                 if re.search(pmc_pattern, href):
                     print("    ✅ MATCHES PMC REGEX!")
                     found = True
        
        if not found:
            print("    ❌ No PMC link matched.")

if __name__ == "__main__":
    debug_category()
