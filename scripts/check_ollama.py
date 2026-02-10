import requests
import json
import time

def check_ollama(url="http://localhost:11434"):
    print(f"Checking Ollama at {url}...")
    try:
        # Check version
        resp = requests.get(f"{url}/api/version", timeout=5)
        if resp.status_code == 200:
            print(f"✅ Ollama is up! Version: {resp.json().get('version')}")
        else:
            print(f"❌ Ollam responded with status: {resp.status_code}")
            return

        # Check loaded models
        resp = requests.get(f"{url}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m['name'] for m in resp.json().get('models', [])]
            print(f"📚 Available models: {models}")
            
            target_model = "qwen2.5:14b"
            if target_model in models:
                print(f"✅ Target model '{target_model}' is available.")
            else:
                print(f"⚠️ Target model '{target_model}' NOT found in list.")
        
        # Test generation (simple)
        print("🧪 Testing generation...")
        start = time.time()
        payload = {
            "model": "qwen2.5:14b",
            "prompt": "Hello",
            "stream": False
        }
        resp = requests.post(f"{url}/api/generate", json=payload, timeout=30)
        if resp.status_code == 200:
            print(f"✅ Generation successful in {time.time()-start:.2f}s")
        else:
            print(f"❌ Generation failed: {resp.text}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    check_ollama()
