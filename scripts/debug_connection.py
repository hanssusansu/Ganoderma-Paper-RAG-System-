import os
import requests
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_connection():
    print("--- Environment Variables ---")
    print(f"HTTP_PROXY: {os.environ.get('HTTP_PROXY')}")
    print(f"HTTPS_PROXY: {os.environ.get('HTTPS_PROXY')}")
    print(f"ALL_PROXY: {os.environ.get('ALL_PROXY')}")
    print(f"NO_PROXY: {os.environ.get('NO_PROXY')}")
    
    url = "http://127.0.0.1:11434/api/generate"
    data = {
        "model": "qwen2.5:14b",
        "prompt": "hi",
        "stream": False
    }
    
    print(f"\n--- Testing Connection to {url} ---")
    
    # Test 1: Standard Request
    print("\n[Test 1] Standard Request:")
    try:
        resp = requests.post(url, json=data, timeout=10)
        print(f"✅ Success! Status: {resp.status_code}")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Test 2: Proxy Bypass
    print("\n[Test 2] With proxies={}:")
    try:
        # Force bypass of system proxies
        resp = requests.post(url, json=data, timeout=10, proxies={"http": None, "https": None})
        print(f"✅ Success! Status: {resp.status_code}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    check_connection()
