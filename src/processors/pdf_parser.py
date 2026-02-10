"""
PDF parser for extracting text and metadata from academic papers.
"""
from typing import Dict, List, Optional
from pathlib import Path
import fitz  # PyMuPDF
from loguru import logger
import re


class PDFParser:
    """Parse PDF files and extract structured content."""
    
    def __init__(self):
        """Initialize PDF parser."""
        self.supported_formats = ['.pdf']
    
    def parse_pdf(self, pdf_path: str) -> Optional[Dict]:
        """
        Parse a PDF file and extract content.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing parsed content and metadata
        """
        pdf_file = Path(pdf_path)
        
        if not pdf_file.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return None
        
        if pdf_file.suffix.lower() not in self.supported_formats:
            logger.error(f"Unsupported file format: {pdf_file.suffix}")
            return None
        
        try:
            logger.info(f"Parsing PDF: {pdf_file.name}")
            
            # Open PDF
            doc = fitz.open(pdf_path)
            
            # Extract metadata
            metadata = self._extract_metadata(doc)
            
            # Get page count before extracting
            num_pages = len(doc)
            
            # Extract text content
            content = self._extract_text(doc)
            
            # Extract structure
            structure = self._extract_structure(doc)
            
            # Close document
            doc.close()
            
            result = {
                'file_path': str(pdf_path),
                'file_name': pdf_file.name,
                'num_pages': num_pages,
                'metadata': metadata,
                'content': content,
                'structure': structure,
            }
            
            logger.success(f"Successfully parsed PDF: {pdf_file.name}")
            return result
        
        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {e}")
            return None
    
    def _extract_metadata(self, doc: fitz.Document) -> Dict:
        """
        Extract metadata from PDF.
        
        Args:
            doc: PyMuPDF document
            
        Returns:
            Dictionary of metadata
        """
        metadata = doc.metadata or {}
        
        return {
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'subject': metadata.get('subject', ''),
            'keywords': metadata.get('keywords', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'modification_date': metadata.get('modDate', ''),
        }
    
    def _extract_text(self, doc: fitz.Document) -> str:
        """
        Extract all text from PDF.
        
        Args:
            doc: PyMuPDF document
            
        Returns:
            Extracted text
        """
        text_parts = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # Clean up text
            text = self._clean_text(text)
            
            if text.strip():
                text_parts.append(text)
        
        return '\n\n'.join(text_parts)
    
    def _extract_structure(self, doc: fitz.Document) -> List[Dict]:
        """
        Extract document structure (sections, headings).
        
        Args:
            doc: PyMuPDF document
            
        Returns:
            List of sections with their content
        """
        sections = []
        current_section = None
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get text blocks with position info
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block.get("type") == 0:  # Text block
                    for line in block.get("lines", []):
                        text = ""
                        for span in line.get("spans", []):
                            text += span.get("text", "")
                        
                        text = text.strip()
                        if not text:
                            continue
                        
                        # Detect if this is a heading (larger font, bold, etc.)
                        is_heading = self._is_heading(line)
                        
                        if is_heading:
                            # Check if this is a References section
                            if re.search(r'References?|Bibliography|參考文獻', text, re.IGNORECASE):
                                # Stop processing further sections as References are usually at the end
                                logger.info(f"Stop parsing at References section: {text}")
                                break
                            
                            # Start new section
                            if current_section:
                                sections.append(current_section)
                            
                            current_section = {
                                'title': text,
                                'page': page_num + 1,
                                'content': []
                            }
                        elif current_section:
                            current_section['content'].append(text)
        
        # Add last section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _is_heading(self, line: Dict) -> bool:
        """
        Detect if a line is a heading.
        
        Args:
            line: Line dictionary from PyMuPDF
            
        Returns:
            True if line is likely a heading
        """
        if not line.get("spans"):
            return False
        
        # Check first span
        span = line["spans"][0]
        font_size = span.get("size", 0)
        font_flags = span.get("flags", 0)
        
        # Heuristics for heading detection
        is_bold = font_flags & 2 ** 4  # Bold flag
        is_large = font_size > 12
        
        text = span.get("text", "").strip()
        is_short = len(text) < 100
        is_uppercase = text.isupper() and len(text) > 3
        
        # Common heading patterns
        heading_patterns = [
            r'^(Abstract|Introduction|Methods?|Results?|Discussion|Conclusion|References?)',
            r'^\d+\.?\s+[A-Z]',  # "1. Introduction" or "1 Introduction"
        ]
        
        matches_pattern = any(re.match(pattern, text, re.IGNORECASE) for pattern in heading_patterns)
        
        return (is_bold and is_large) or (is_large and is_short) or is_uppercase or matches_pattern
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers (simple heuristic)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Fix hyphenation
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        return text.strip()
    
    def extract_abstract(self, parsed_content: Dict) -> Optional[str]:
        """
        Extract abstract from parsed content.
        
        Args:
            parsed_content: Parsed PDF content
            
        Returns:
            Abstract text or None
        """
        # Try to find abstract in structure
        for section in parsed_content.get('structure', []):
            title = section.get('title', '').lower()
            if 'abstract' in title:
                return ' '.join(section.get('content', []))
        
        # Fallback: search in full text
        content = parsed_content.get('content', '')
        match = re.search(r'abstract\s*[:\-]?\s*(.+?)(?:introduction|keywords|$)', 
                         content, re.IGNORECASE | re.DOTALL)
        
        if match:
            abstract = match.group(1).strip()
            # Limit length
            if len(abstract) > 2000:
                abstract = abstract[:2000] + '...'
            return abstract
        
        return None


def main():
    """Test the PDF parser."""
    parser = PDFParser()
    
    # Test with downloaded PDF
    pdf_path = "data/pdfs/PMC/PMC11792735.pdf"
    
    result = parser.parse_pdf(pdf_path)
    
    if result:
        print(f"✓ Parsed: {result['file_name']}")
        print(f"  Pages: {result['num_pages']}")
        print(f"  Title: {result['metadata'].get('title', 'N/A')}")
        print(f"  Sections: {len(result['structure'])}")
        print(f"  Content length: {len(result['content'])} chars")
        
        # Try to extract abstract
        abstract = parser.extract_abstract(result)
        if abstract:
            print(f"\nAbstract preview:")
            print(abstract[:200] + "...")
    else:
        print("✗ Failed to parse PDF")


if __name__ == "__main__":
    main()
