"""
Text chunker for splitting documents into manageable chunks.
"""
from typing import List, Dict, Optional
from loguru import logger
import re


class TextChunker:
    """Split text into chunks while preserving context."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100
    ):
        """
        Initialize text chunker.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            min_chunk_size: Minimum chunk size to keep
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Split text into chunks.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of chunk dictionaries
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []
        
        # Split into sentences first
        sentences = self._split_sentences(text)
        
        # Group sentences into chunks
        chunks = self._create_chunks(sentences)
        
        # Create chunk dictionaries with metadata
        chunk_dicts = []
        for i, chunk_text in enumerate(chunks):
            chunk_dict = {
                'chunk_index': i,
                'total_chunks': len(chunks),
                'content': chunk_text,
                'char_count': len(chunk_text),
                'word_count': len(chunk_text.split()),
            }
            
            # Add metadata if provided
            if metadata:
                chunk_dict.update(metadata)
            
            chunk_dicts.append(chunk_dict)
        
        logger.info(f"Created {len(chunk_dicts)} chunks from {len(text)} characters")
        return chunk_dicts
    
    def chunk_by_sections(
        self,
        sections: List[Dict],
        metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Chunk text by sections (from PDF structure).
        
        Args:
            sections: List of sections from PDF parser
            metadata: Optional metadata
            
        Returns:
            List of chunk dictionaries
        """
        all_chunks = []
        
        for section in sections:
            section_title = section.get('title', '')
            section_content = ' '.join(section.get('content', []))
            section_page = section.get('page', 0)
            
            # Chunk the section content
            section_text = f"{section_title}\n\n{section_content}"
            chunks = self.chunk_text(section_text)
            
            # Add section metadata
            for chunk in chunks:
                chunk['section'] = section_title
                chunk['page'] = section_page
                
                if metadata:
                    chunk.update(metadata)
            
            all_chunks.extend(chunks)
        
        # Update total chunks count
        total = len(all_chunks)
        for i, chunk in enumerate(all_chunks):
            chunk['chunk_index'] = i
            chunk['total_chunks'] = total
        
        logger.info(f"Created {total} chunks from {len(sections)} sections")
        return all_chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved with spaCy or NLTK)
        # Split on period, exclamation, question mark followed by space and capital
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        
        # Clean up sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _create_chunks(self, sentences: List[str]) -> List[str]:
        """
        Create chunks from sentences.
        
        Args:
            sentences: List of sentences
            
        Returns:
            List of chunks
        """
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            # If adding this sentence exceeds chunk size
            if current_size + sentence_size > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                if len(chunk_text) >= self.min_chunk_size:
                    chunks.append(chunk_text)
                
                # Start new chunk with overlap
                # Keep last few sentences for context
                overlap_text = ' '.join(current_chunk)
                overlap_sentences = []
                overlap_size = 0
                
                for s in reversed(current_chunk):
                    if overlap_size + len(s) <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_size += len(s)
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_size = overlap_size
            
            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Add last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append(chunk_text)
        
        return chunks


def main():
    """Test the text chunker."""
    chunker = TextChunker(chunk_size=500, chunk_overlap=100)
    
    # Test text
    test_text = """
    Ganoderma lucidum is a medicinal mushroom that has been used in traditional Chinese medicine for centuries.
    It contains various bioactive compounds including polysaccharides and triterpenoids.
    Recent studies have shown that Ganoderma lucidum has immunomodulatory effects.
    The polysaccharides from Ganoderma lucidum can enhance immune function.
    Clinical trials have demonstrated its potential in treating various diseases.
    However, more research is needed to fully understand its mechanisms of action.
    """
    
    chunks = chunker.chunk_text(test_text, metadata={'source': 'test'})
    
    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"\nChunk {chunk['chunk_index'] + 1}/{chunk['total_chunks']}:")
        print(f"  Characters: {chunk['char_count']}")
        print(f"  Words: {chunk['word_count']}")
        print(f"  Content: {chunk['content'][:100]}...")


if __name__ == "__main__":
    main()
