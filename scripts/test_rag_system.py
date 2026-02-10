"""
Complete RAG system test.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.retriever import SimpleRetriever
from src.rag.generator import RAGGenerator
from loguru import logger


def test_rag_system():
    """Test complete RAG system."""
    logger.info("=" * 60)
    logger.info("測試完整 RAG 系統")
    logger.info("=" * 60)
    
    # Initialize components
    retriever = SimpleRetriever()
    generator = RAGGenerator()
    
    # Load chunks
    logger.info("\n步驟 1: 載入分塊")
    retriever.load_chunks()
    
    if not retriever.chunks:
        logger.error("沒有可用的分塊")
        return False
    
    # Test queries
    test_queries = [
        "靈芝有什麼功效？",
        "What are the immunomodulatory effects of Ganoderma?",
        "臨床試驗的結果如何？",
    ]
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n{'=' * 60}")
        logger.info(f"測試查詢 {i}/{len(test_queries)}")
        logger.info(f"{'=' * 60}")
        
        # Step 2: Retrieve
        logger.info(f"\n步驟 2: 檢索相關內容")
        logger.info(f"查詢: {query}")
        
        results = retriever.retrieve(query, top_k=3)
        
        if results:
            logger.success(f"✓ 找到 {len(results)} 個相關分塊")
            for j, result in enumerate(results, 1):
                logger.info(f"  {j}. 分數: {result['score']}, 章節: {result.get('section', 'N/A')}")
        else:
            logger.warning("✗ 沒有找到相關分塊")
            continue
        
        # Step 3: Generate answer
        logger.info(f"\n步驟 3: 生成答案")
        
        try:
            answer = generator.generate_answer(query, results)
            
            if answer:
                logger.success("✓ 答案生成成功")
                print(f"\n問題: {query}")
                print(f"\n答案:\n{answer}\n")
            else:
                logger.error("✗ 答案生成失敗")
        
        except Exception as e:
            logger.error(f"✗ 生成答案時發生錯誤: {e}")
            print(f"\n注意: Ollama 可能未運行或模型未下載")
            print(f"請執行: docker exec -it ganoderma-ollama ollama pull llama2")
    
    return True


def main():
    """Run the test."""
    logger.info("\n" + "🧪 " * 20)
    logger.info("RAG 系統完整測試")
    logger.info("🧪 " * 20 + "\n")
    
    success = test_rag_system()
    
    if success:
        logger.success("\n✓ RAG 系統測試完成！")
    else:
        logger.error("\n✗ RAG 系統測試失敗")


if __name__ == "__main__":
    main()
