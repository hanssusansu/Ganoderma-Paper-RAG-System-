import os
import requests
import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def deep_debug():
    print(f"\n=== ENVIRONMENT ===")
    print(f"OLLAMA_HOST env: {os.environ.get('OLLAMA_HOST')}")
    print(f"OLLAMA_MODEL env: {os.environ.get('OLLAMA_MODEL')}")
    
    print(f"\n=== SETTINGS (Effective) ===")
    print(f"settings.ollama_host: '{settings.ollama_host}'")
    print(f"settings.ollama_model: '{settings.ollama_model}'")
    
    target_host = settings.ollama_host
    target_model = settings.ollama_model
    
    print(f"\n=== TESTING HOST: {target_host} ===")
    
    # 1. Test Version
    try:
        resp = requests.get(f"{target_host}/api/version", timeout=5)
        print(f"Version Check: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Version Check Failed: {e}")
        return

    # 2. List Models
    print(f"\n=== CHECKING MODELS ===")
    try:
        resp = requests.get(f"{target_host}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            model_names = [m['name'] for m in models]
            print(f"Available Models: {json.dumps(model_names, indent=2)}")
            
            if target_model in model_names:
                print(f"✅ Target model '{target_model}' FOUND.")
            else:
                print(f"❌ Target model '{target_model}' NOT FOUND.")
                # fuzzy check
                for m in model_names:
                    if target_model in m:
                        print(f"   (Did you mean '{m}'?)")
        else:
            print(f"List Models Failed: {resp.status_code}")
    except Exception as e:
        print(f"List Models Exception: {e}")

    # 3. Test Generation (Payload inspection)
    print(f"\n=== TESTING GENERATION ===")
    url = f"{target_host}/api/generate"
    payload = {
        "model": target_model,
        "prompt": "Test",
        "stream": False
    }
    print(f"Target URL: {url}")
    print(f"Payload: {json.dumps(payload)}")
    
    try:
        resp = requests.post(url, json=payload, timeout=30)
        print(f"Response Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Response Text: {resp.text}")
        else:
            print("✅ Generation SUCCESS")
    except Exception as e:
        print(f"❌ Generation Exception: {e}")

if __name__ == "__main__":
    deep_debug()
