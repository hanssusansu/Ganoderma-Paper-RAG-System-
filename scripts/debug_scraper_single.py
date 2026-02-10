import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.ganoderma_news import GanodermaScraper
import logging

# Set up logging to console
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_specific_article():
    scraper = GanodermaScraper()
    
    # Target URL: The one I inspected earlier which definitely has a PMC link in the footer
    # Title: 中國：化療後加用靈芝三萜可清除「老不死」的肝癌細胞...
    url = "https://www.ganodermanews.com/index.php/研究新知/2020-2029/726-中國：化療後加用靈芝三萜可清除「老不死」的肝癌細胞，乘勝追擊腫瘤＆修復化療損傷.html"
    
    print(f"\n--- Testing Article: {url} ---")
    result = scraper.extract_paper_links(url)
    
    if result:
        print("\n✅ SUCCESS! Found:")
        print(f"Paper Source: {result.get('paper_source')}")
        print(f"Paper URL: {result.get('paper_url')}")
        print(f"Paper ID: {result.get('paper_id')}")
    else:
        print("\n❌ FAILED. No paper links found.")
        
        # Debug: Print all links found in the page to see why we missed it
        print("Debugging links on page:")
        soup = scraper._fetch_url(url)
        if soup:
             for link in soup.find_all('a', href=True):
                 href = link['href']
                 if 'ncbi' in href or 'doi' in href:
                     print(f"  [Potential Match]: {href}")

if __name__ == "__main__":
    test_specific_article()
