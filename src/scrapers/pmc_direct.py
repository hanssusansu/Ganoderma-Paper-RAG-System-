"""
Direct PMC Scraper.
Searches PMC for Open Access papers on Ganoderma and extracts IDs.
"""
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import time
from loguru import logger
import random
import json

class PMCDirectScraper:
    """Scraper to find papers directly from PMC search results."""
    
    BASE_URL = "https://pmc.ncbi.nlm.nih.gov"
    SEARCH_URL = "https://pmc.ncbi.nlm.nih.gov/?term=ganoderma+lucidum&filter=open_access"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_papers(self, max_pages: int = 1) -> List[Dict]:
        """
        Search PMC using NCBI E-utilities API.
        """
        found_papers = []
        # retmax: max papers to return (e.g. 20 per page equivalent)
        retmax = 20 * max_pages 
        
        # E-utilities URL
        api_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pmc",
            "term": "Ganoderma lucidum[Title]",
            "retmode": "json",
            "retmax": retmax,
            "sort": "relevance"
        }
        
        logger.info(f"Querying NCBI API: {params}")
        
        try:
            response = self.session.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extract IDs
            id_list = data.get("esearchresult", {}).get("idlist", [])
            logger.info(f"NCBI API returned {len(id_list)} IDs: {id_list}")
            
            for pmc_numeric_id in id_list:
                pmc_id = f"PMC{pmc_numeric_id}"
                full_url = f"{self.BASE_URL}/articles/{pmc_id}/"
                
                found_papers.append({
                    'paper_id': pmc_id,
                    'article_title': f"Ganoderma Paper {pmc_id}", 
                    'paper_url': full_url,
                    'paper_source': 'PMC' 
                })
                
        except Exception as e:
            logger.error(f"Error querying NCBI API: {e}")
            
        logger.info(f"Total structured papers found: {len(found_papers)}")
        return found_papers

if __name__ == "__main__":
    scraper = PMCDirectScraper()
    papers = scraper.search_papers(max_pages=1)
    print(json.dumps(papers, indent=2))
