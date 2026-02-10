"""
Launch script for FastAPI service.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == "__main__":
    import uvicorn
    from src.api.main import app
    
    print("🍄 啟動 Ganoderma Papers RAG API 服務...")
    print("📍 API 將在 http://localhost:8000 啟動")
    print("📚 API 文件: http://localhost:8000/docs")
    print("⏹️  按 Ctrl+C 停止服務\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
