import sys
from pathlib import Path
import json
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processors.pdf_parser import PDFParser
from src.processors.text_chunker import TextChunker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_regen():
    pdf_path = Path("data/pdfs/PMC/PMC11792735.pdf")
    
    parser = PDFParser()
    chunker = TextChunker()
    
    print(f"Parsing {pdf_path}...")
    parsed_data = parser.parse_pdf(str(pdf_path))
    
    if not parsed_data:
        print("❌ Parse failed")
        return

    print(f"Structure keys: {parsed_data.keys()}")
    print(f"METADATA: {json.dumps(parsed_data.get('metadata', {}), indent=2, default=str)}")
    sections = parsed_data.get('structure', [])
    print(f"Found {len(sections)} sections")
    
    chunks = []
    
    for i, section in enumerate(sections):
        header = section.get('title', '') # Changed from 'header' to 'title' based on pdf_parser.py
        # Wait, pdf_parser.py uses 'title' or 'header'?
        # Let's check pdf_parser.py source code viewed earlier.
        # It uses: 'title': text
        
        content = section.get('content', [])
        print(f"Section {i} Title: {header}")
        print(f"Content type: {type(content)}")
        print(f"Content len: {len(content)}")
        
        content_str = "\n".join(content) if isinstance(content, list) else str(content)
        section_text = f"{header}\n{content_str}"
        print(f"Section text len: {len(section_text)}")
        
        section_chunks = chunker.chunk_text(section_text)
        print(f" Generated {len(section_chunks)} chunks")
        
        for chunk_item in section_chunks:
            # Verify it's a dict
            if isinstance(chunk_item, dict):
                chunks.append(chunk_item.get('content', ''))
            else:
                print(f"❌ Chunk is not dict: {type(chunk_item)}")

    print(f"Total chunks generated: {len(chunks)}")
    if chunks:
        print(f"Sample chunk: {chunks[0][:50]}...")

if __name__ == "__main__":
    debug_regen()
