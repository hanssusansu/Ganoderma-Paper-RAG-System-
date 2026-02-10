import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.gradio_app import GanodermaRAGUI
import logging

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_full_stack():
    print("\n--- Initializing System (Simulating UI startup) ---")
    try:
        ui = GanodermaRAGUI()
        if not ui.ready:
            print("❌ System failed to initialize!")
            return
        
        print("\n✅ System initialized. Testing Query...")
        query = "靈芝有什麼功效？"
        answer, sources = ui.query(query)
        
        print("\n--- RESPONSE ---")
        print(f"Answer: {answer[:200]}...") # Print preview
        print(f"Sources: {len(sources)} chars")
        
        if "Ollama" in answer and "不可用" in answer:
             print("\n❌ FAILURE: Ollama unavailable message detected.")
        else:
             print("\n✅ SUCCESS: Real answer generated.")
             
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_stack()
