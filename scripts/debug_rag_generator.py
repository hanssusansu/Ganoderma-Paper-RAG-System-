import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.generator import RAGGenerator
from src.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_generator():
    print(f"\n--- Debugging RAGGenerator ---")
    print(f"Settings.ollama_host: {settings.ollama_host}")
    print(f"Settings.ollama_model: {settings.ollama_model}")
    
    generator = RAGGenerator()
    print(f"Generator initialized with model: {generator.model}")
    print(f"Generator API URL: {generator.api_url}")
    
    # Mock context
    chunks = [{'content': 'Test context', 'section': 'Test', 'paper_id': 'PMC123'}]
    
    print("\n--- Attempting Generation ---")
    answer = generator.generate_answer("Test query", chunks)
    print(f"\nResult: {answer}")

if __name__ == "__main__":
    test_generator()
