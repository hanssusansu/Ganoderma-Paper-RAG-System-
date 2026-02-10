"""
AI Metadata Tagger for classifying Ganoderma papers.
Uses Ollama to analyze paper content and extract key metadata:
1. Part used (Fruiting body, Mycelium, Spore)
2. Extraction method (Water, Ethanol, Methanol, etc.)
"""
import json
import re
from typing import Dict, Optional, List
from loguru import logger
import requests
from ..config import settings

class MetadataTagger:
    """Tags papers with metadata using LLM."""
    
    def __init__(self, ollama_host: str = "http://localhost:11434", model: str = None):
        self.ollama_host = ollama_host
        self.model = model or settings.ollama_model
        logger.info(f"MetadataTagger initialized with model: {self.model}")
        self.api_url = f"{ollama_host}/api/generate"
        
    def tag_paper(self, text_content: str) -> Dict:
        """
        Analyze text content (usually Materials & Methods) to extract metadata.
        
        Args:
            text_content: The text content of the paper (first few pages or Methods section)
            
        Returns:
            Dictionary containing 'part_used' and 'extraction_method'
        """
        # Truncate text if too long to avoid token limits (keep first 6000 chars - about 1500 tokens)
        # We focus on the beginning where Methods usually are, or we should be passed specific sections
        analysis_text = text_content[:6000]
        
        prompt = f"""[INST] <<SYS>>
You are a scientific literature analyst for Ganoderma lucidum (Reishi) research.
Your task is to identify TWO specific details from the research paper text provided below:

1. **Part of the Mushroom Used**:
   - Options: "Fruiting Body" (子實體), "Mycelium" (菌絲體), "Spore" (孢子), "Mixed", or "Unknown".
   
2. **Extraction Method / Solvent**:
   - Options: "Water/Aqueous" (水萃取), "Ethanol/Alcohol" (醇萃取), "Methanol", "Polysaccharide Extract", "Triterpenoid Extract", "Powder" (Raw powder, no extract), or "Unknown".

Return ONLY a JSON object. Do not include any other text.
Format:
{{
  "part_used": "...",
  "extraction_method": "..."
}}
<</SYS>>

Paper Text:
{analysis_text}

JSON Output:
[/INST]"""

        try:
            response = self._call_ollama(prompt)
            # Try to parse JSON from response
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Error tagging paper: {e}")
            return {
                "part_used": "Unknown",
                "extraction_method": "Unknown"
            }
            
    def _call_ollama(self, prompt: str) -> str:
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"  # Force JSON mode if supported by newer Ollama versions, otherwise Llama2 follows prompt
        }
        
        response = requests.post(self.api_url, json=data, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "")

    def _parse_json_response(self, response_text: str) -> Dict:
        """Clean and parse JSON from LLM response."""
        try:
            # Find JSON/Dict like structure
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                json_str = match.group(0)
                return json.loads(json_str)
            else:
                logger.warning(f"No JSON found in response: {response_text}")
                return {"part_used": "Unknown", "extraction_method": "Unknown"}
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {response_text}")
            return {"part_used": "Unknown", "extraction_method": "Unknown"}

if __name__ == "__main__":
    # Test
    tagger = MetadataTagger()
    dummy_text = """
    Materials and Methods:
    Ganoderma lucidum fruiting bodies were collected from Taiwan.
    The dried fruiting bodies were extracted with hot water for 3 hours.
    """
    print(tagger.tag_paper(dummy_text))
