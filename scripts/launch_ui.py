"""
Launch script for Gradio UI.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.gradio_app import main

if __name__ == "__main__":
    print("🍄 啟動 Ganoderma Papers RAG Web 介面...")
    print("📍 介面將在 http://localhost:7872 啟動")
    print("⏹️  按 Ctrl+C 停止服務\n")
    
    main()
