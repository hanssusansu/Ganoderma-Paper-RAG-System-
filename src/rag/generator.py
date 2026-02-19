"""
RAG generator using Ollama for answer generation.
"""
from typing import List, Dict, Optional
from loguru import logger
import requests
from ..config import settings


class RAGGenerator:
    """Generate answers using retrieved context and Ollama."""
    
    def __init__(
        self,
        ollama_host: str = None,
        model: str = None
    ):
        """
        Initialize RAG generator.
        
        Args:
            ollama_host: Ollama API host
            model: Model name to use
        """
        self.ollama_host = ollama_host or settings.ollama_host
        self.model = model or settings.ollama_model
        self.api_url = f"{self.ollama_host}/api/generate"
    
    def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict],
        max_context_length: int = 3500
    ) -> Optional[str]:
        """
        Generate answer using retrieved context.
        
        Args:
            query: User query
            context_chunks: Retrieved chunks
            max_context_length: Maximum context length
            
        Returns:
            Generated answer or None
        """
        if not context_chunks:
            logger.warning("No context chunks provided")
            return "Sorry, I cannot find relevant information to answer your question."
        
        # Build context
        context = self._build_context(context_chunks, max_context_length)
        
        # Try to generate answer with Ollama
        try:
            # Build prompt
            prompt = self._build_prompt(query, context)
            
            # Call Ollama
            answer = self._call_ollama(prompt)
            return answer
        
        except requests.exceptions.ConnectionError:
            # Ollama not available, return context summary instead
            logger.warning("Ollama not available, returning context summary")
            return self._generate_fallback_answer(query, context_chunks, error_msg=f"Cannot connect to {self.api_url}")
        
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return self._generate_fallback_answer(query, context_chunks, error_msg=str(e))

    def _generate_fallback_answer(self, query: str, chunks: List[Dict], error_msg: str = None) -> str:
        """
        Generate fallback answer when Ollama is not available.
        
        Args:
            query: User query
            chunks: Retrieved chunks
            error_msg: Optional error message
            
        Returns:
            Fallback answer
        """
        error_info = f"(Error details: {error_msg})" if error_msg else ""
        answer_parts = [
            f"Based on {len(chunks)} retrieved paragraphs, here is the summary:\n",
            f"(Note: Ollama service is currently unavailable, showing raw retrieval content) {error_info}\n"
        ]
        
        for i, chunk in enumerate(chunks[:3], 1):  # Show top 3
            section = chunk.get('section', 'Unknown Section')
            content = chunk['content'][:300] + "..." if len(chunk['content']) > 300 else chunk['content']
            
            answer_parts.append(f"\n**Paragraph {i}** ({section}):\n{content}\n")
        
        return "\n".join(answer_parts)
    
    def _build_context(self, chunks: List[Dict], max_length: int) -> str:
        """
        Build context from chunks with reference IDs.
        
        Args:
            chunks: List of chunks
            max_length: Maximum context length
            
        Returns:
            Context string
        """
        context_parts = []
        current_length = 0
        
        # Track unique papers to assign IDs
        paper_map = {}
        paper_counter = 1
        
        for chunk in chunks:
            content = chunk.get('content', '')
            section = chunk.get('section', '')
            paper_id = chunk.get('paper_id', 'Unknown')
            
            # Assign reference ID to paper
            if paper_id not in paper_map:
                paper_map[paper_id] = paper_counter
                paper_counter += 1
            
            ref_id = paper_map[paper_id]
            
            # Add header with reference ID
            header = f"【Reference {ref_id}】(ID: {paper_id})"
            
            # Add APA Citation for LLM to see
            citation = chunk.get('metadata', {}).get('citation_str', None)
            if citation:
                header += f"\n[Citation: {citation}]"

            # Add AI Metadata if available
            part_used = chunk.get('metadata', {}).get('ai_part_used', 'Unknown')
            extraction = chunk.get('metadata', {}).get('ai_extraction', 'Unknown')
            
            if part_used != 'Unknown' or extraction != 'Unknown':
                header += f"\n[Part: {part_used}] [Extraction: {extraction}]"
            
            if section:
                header += f" - From section: {section}"
            
            part = f"{header}\n{content}"
            
            part_length = len(part)
            
            if current_length + part_length > max_length:
                break
            
            context_parts.append(part)
            current_length += part_length
        
        return "\n\n---\n\n".join(context_parts)

    def _build_prompt(self, query: str, context: str) -> str:
        """
        Build prompt for LLM.
        """
        prompt = f"""[INST] <<SYS>>
You are a professional "Ganoderma Academic Library" research assistant. Your role is to objectively provide literature summaries, NOT to promote products or provide medical advice.

**Strictly follow these rules (Legal Compliance Requirements)**:

1. **🚫 PROHIBITED TERMS**:
   - Strictly FORBIDDEN to use words involving medical efficacy such as "cure", "treat", "heal", "effective for", etc.
   - **Alternative Wording**: Use academic neutral terms like "studies suggest a correlation", "explore potential", "documented biological activity", "experimental results show", "possesses properties of...".
   - Example: Do NOT say "Ganoderma can treat cancer", SAY "Literature explores the biological activity of Ganoderma in anti-tumor research".

2. **📚 Academic Positioning**:
   - You are a "Librarian", not a doctor or pharmacist. Only state literature content, do not give advice.
   - Must emphasize that these are "experimental results" or "literature records".

3. **Citation Format**:
   - When citing, add the number directly after the sentence, e.g., "...studies show its biological activity [1]."
   - **DO NOT** use original citation numbers (like (15), [12]). Only use the 【Reference x】 numbers I assigned.
   - **Reference List Rules (Important)**:
     - **Only list references you actually cited in your answer**.
     - If you only used [1] and [3], the reference list should only list 1 and 3.
     - Format (Use [Citation] provided in context):
       References:
       1. Author, A. A. et al. (Year). Title... - [Part: xxx] [Extraction: xxx]
       (If detailed citation info is missing, use PMC ID)

4. **Language Strategy**:
   - **Main narrative** must be in **English**.
   - **Proper Nouns** (like chemical components, proteins) can remain in English.

5. **Product Relevance Check (Important)**:
   - Pay special attention to the [Part] (Fruiting Body/Mycelium) and [Extraction] method marked in the literature.
   - If the literature uses "injection" or "purified compounds", DO NOT infer "oral" effects.
   - It improves professionalism if you can distinguish parts or extraction methods (e.g., "This study on fruiting body water extract shows...").

6. **Disclaimer**:
   - At the beginning or end of the answer, appropriately remind "This content is a summary of academic literature and does not constitute medical advice".

<</SYS>>

Retrieved Literature Data:
{context}

User Question: "{query}"

Please answer the above question in English as a "Ganoderma Academic Librarian", strictly adhering to compliance terminology, avoiding medical claims, and attaching source citations:
[/INST]"""
        
        return prompt
    
    def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama API.
        
        Args:
            prompt: Prompt text
            
        Returns:
            Generated text
        """
        logger.info(f"Calling Ollama with model: {self.model}")
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            # Bypass proxies for localhost
            response = requests.post(
                self.api_url, 
                json=data, 
                timeout=300,
                proxies={"http": None, "https": None}
            )
            response.raise_for_status()
            
            result = response.json()
            answer = result.get("response", "")
            
            logger.success("Generated answer successfully")
            return answer
        
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.ollama_host}")
            return "Cannot connect to Ollama service. Please confirm Ollama is running."
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise


def main():
    """Test the generator."""
    generator = RAGGenerator()
    
    # Test with dummy context
    test_chunks = [
        {
            'content': 'Ganoderma lucidum has been shown to have immunomodulatory effects in clinical trials.',
            'section': 'Results'
        }
    ]
    
    query = "What are the effects of Ganoderma lucidum?"
    
    answer = generator.generate_answer(query, test_chunks)
    
    print(f"\nQuestion: {query}")
    print(f"\nAnswer:\n{answer}")


if __name__ == "__main__":
    main()
