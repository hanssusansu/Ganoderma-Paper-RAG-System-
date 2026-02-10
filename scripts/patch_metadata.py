import json
import logging
from pathlib import Path
import requests
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def patch_metadata():
    json_path = Path("data/processed/all_chunks.json")
    
    if not json_path.exists():
        logger.error("all_chunks.json not found")
        return
        
    logger.info(f"Loading {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
        
    # Get unique paper IDs
    paper_ids = list(set(c['paper_id'] for c in chunks))
    logger.info(f"Found {len(paper_ids)} unique papers.")
    
    metadata_cache = {}
    
    for paper_id in paper_ids:
        if not paper_id.startswith("PMC"):
            continue
            
        logger.info(f"Fetching metadata for {paper_id}...")
        
        try:
            # Try E-utilities Summary endpoint (more stable)
            # Remove PMC prefix for ID
            clean_id = paper_id.replace("PMC", "")
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&retmode=json&id={clean_id}"
            
            headers = {
                "User-Agent": "GanodermaRAG/1.0 (research@example.com)"
            }
            
            # Simple retry logic
            resp = None
            for _ in range(3):
                try:
                    resp = requests.get(url, headers=headers, timeout=10)
                    if resp.status_code == 200:
                        break
                    time.sleep(1)
                except:
                    time.sleep(1)
                    
            if resp and resp.status_code == 200:
                data = resp.json()
                # Parse E-utilities JSON format
                # Structure: result -> uids -> title, pubdate, source, authors...
                if 'result' in data and clean_id in data['result']:
                    item = data['result'][clean_id]
                    
                    title = item.get('title', '')
                    container = item.get('source', '') # Journal name
                    
                    # pubdate: "2015 Aug 18"
                    pubdate = item.get('pubdate', '')
                    year = pubdate.split(' ')[0] if pubdate else "n.d."
                    
                    # authors: list of dicts {name: ...}
                    authors_list = item.get('authors', [])
                    first_author = "Unknown"
                    if authors_list:
                        first_author = authors_list[0].get('name', 'Unknown')
                        if len(authors_list) > 1:
                            first_author += " et al."
                    
                    citation_str = f"{first_author} ({year}). {title}. {container}."
                    metadata_cache[paper_id] = {
                        "title": title,
                        "journal": container,
                        "year": year,
                        "authors": first_author,
                        "citation_str": citation_str,
                        "has_citation": True
                    }
                    logger.info(f"  -> Got: {citation_str[:50]}...")
            else:
                 logger.warning(f"Failed to fetch {paper_id}: HTTP {resp.status_code if resp else 'Error'}")

        except Exception as e:
            logger.error(f"Error fetching {paper_id}: {e}")
            
        time.sleep(0.5) # Rate limit niceness
        
    # Apply to chunks
    updated_count = 0
    for chunk in chunks:
        pid = chunk['paper_id']
        if pid in metadata_cache:
            if 'metadata' not in chunk:
                chunk['metadata'] = {}
            chunk['metadata'].update(metadata_cache[pid])
            updated_count += 1
            
    logger.info(f"Updated {updated_count} chunks with new metadata.")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
        
    logger.info("Patch complete!")

if __name__ == "__main__":
    patch_metadata()
