import sys
from pathlib import Path
import json
import logging
from tqdm import tqdm

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processors.pdf_parser import PDFParser
from src.processors.text_chunker import TextChunker
# from src.processors.metadata_tagger import MetadataTagger # Skip for speed
from src.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def regenerate_kb():
    pdf_dir = Path("data/pdfs/PMC")
    output_file = Path("data/processed/all_chunks.json")
    
    parser = PDFParser()
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    
    pdfs = list(pdf_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdfs)} PDFs in {pdf_dir}")
    
    all_chunks = []
    
    import requests
    import time
    
    def fetch_pubmed_metadata(pmc_id):
        """Fetch metadata from NCBI api for better citations."""
        try:
            # Use NCBI Citation Exporter API (unofficial but effective for CSL/JSON)
            # Or use E-utilities. Let's use a known reliable endpoint for JSON metadata.
            # 'https://api.ncbi.nlm.nih.gov/lit/ctxp/v1/pmc/?format=csl&id=' is excellent.
            url = f"https://api.ncbi.nlm.nih.gov/lit/ctxp/v1/pmc/?format=csl&id={pmc_id}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                # CSL JSON format usually returns a wrapper
                if data:
                    item = data
                    title = item.get('title', '')
                    container = item.get('container-title', '')
                    
                    # Extract date
                    issued = item.get('issued', {}).get('date-parts', [[None]])[0][0]
                    year = str(issued) if issued else "n.d."
                    
                    # Extract first author
                    authors = item.get('author', [])
                    first_author = "Unknown"
                    if authors:
                        family = authors[0].get('family', '')
                        given = authors[0].get('given', '')
                        first_author = f"{family}, {given}" if family else given
                        if len(authors) > 1:
                            first_author += " et al."
                            
                    return {
                        "title": title,
                        "journal": container,
                        "year": year,
                        "authors": first_author,
                        "citation_str": f"{first_author} ({year}). {title}. {container}."
                    }
        except Exception as e:
            logger.warning(f"Failed to fetch metadata for {pmc_id}: {e}")
        return None

    for pdf_path in tqdm(pdfs, desc="Processing PDFs"):
        try:
            paper_id = pdf_path.stem
            logger.info(f"Processing {paper_id}...")
            
            # Fetch Metadata (APA Style Data)
            # Only fetch if it looks like a PMC ID
            ext_metadata = {}
            if paper_id.startswith("PMC"):
                # Be gentle with API
                time.sleep(0.3) 
                api_meta = fetch_pubmed_metadata(paper_id)
                if api_meta:
                    ext_metadata = api_meta
                    logger.info(f"  -> Fetched metadata: {api_meta.get('citation_str')}")
            
            # Parse
            parsed_data = parser.parse_pdf(str(pdf_path))
            if not parsed_data:
                logger.warning(f"Failed to parse {paper_id}")
                continue
                
            # Chunk
            full_text = ""
            # Reconstruct full text for chunking (or pass sections if chunker supports it)
            # TextChunker usually takes text.
            # Let's concatenate sections with headers
            
            chunks = []
            for section in parsed_data.get('structure', []):
                # PDFParser returns content as list of strings
                content_list = section.get('content', [])
                content_str = "\n".join(content_list) if isinstance(content_list, list) else str(content_list)
                
                # Use 'title' from PDFParser structure
                title = section.get('title', '')
                section_text = f"{title}\n{content_str}"
                
                section_chunks = chunker.chunk_text(section_text)
                
                for chunk_item in section_chunks:
                    # chunk_item is a dictionary!
                    chunks.append({
                        "paper_id": paper_id,
                        "content": chunk_item['content'], # Extract the string content
                        "section": title,
                        "source_url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/{paper_id}/",
                        "metadata": {
                            "reprocessed": True,
                            **ext_metadata  # Inject fetched metadata (title, year, authors)
                        }
                    })
            
            all_chunks.extend(chunks)
            logger.info(f"  -> Generated {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            continue

    # Save
    logger.info(f"Saving {len(all_chunks)} chunks to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    
    logger.info("Done!")

if __name__ == "__main__":
    regenerate_kb()
