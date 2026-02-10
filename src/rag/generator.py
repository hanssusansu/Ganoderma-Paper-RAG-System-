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
            return "抱歉，我找不到相關的資訊來回答您的問題。"
        
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
            return self._generate_fallback_answer(query, context_chunks, error_msg=f"無法自 {self.api_url} 連線")
        
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
        error_info = f"（錯誤詳情: {error_msg}）" if error_msg else ""
        answer_parts = [
            f"根據檢索到的 {len(chunks)} 個相關段落，以下是相關內容摘要：\n",
            f"（註：Ollama 服務目前不可用，顯示原始檢索內容）{error_info}\n"
        ]
        
        for i, chunk in enumerate(chunks[:3], 1):  # Show top 3
            section = chunk.get('section', '未知章節')
            content = chunk['content'][:300] + "..." if len(chunk['content']) > 300 else chunk['content']
            
            answer_parts.append(f"\n**段落 {i}** ({section}):\n{content}\n")
        
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
            header = f"【文獻 {ref_id}】(ID: {paper_id})"
            
            # Add APA Citation for LLM to see
            citation = chunk.get('metadata', {}).get('citation_str', None)
            if citation:
                header += f"\n[引用資訊: {citation}]"

            # Add AI Metadata if available
            part_used = chunk.get('metadata', {}).get('ai_part_used', 'Unknown')
            extraction = chunk.get('metadata', {}).get('ai_extraction', 'Unknown')
            
            if part_used != 'Unknown' or extraction != 'Unknown':
                header += f"\n[部位: {part_used}] [萃取法: {extraction}]"
            
            if section:
                header += f" - 節錄自: {section}"
            
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
你是一個專業的「靈芝學術圖書館」研究助手。你的角色是客觀地提供文獻摘要，而不是推銷產品或提供醫療建議。

**嚴格遵守以下規則 (法律合規性要求)**：

1. **🚫 絕對禁止詞彙**：
   - 嚴禁使用「功效」、「療效」、「治療」、「改善」、「治癒」、「有效」等涉及醫療效能的詞彙。
   - **替代用語**：請使用「研究指出相關性」、「探討其潛力」、「文獻記載之生物活性」、「實驗結果顯示」、「具有...之特性」等學術中性用語。
   - 例如：不要說「靈芝可以治療癌症」，要說「文獻探討了靈芝在抗腫瘤研究中的生物活性」。

2. **📚 學術定位**：
   - 你是「學術圖書館員」，不是醫生或藥師。只陳述文獻內容，不給予建議。
   - 必須強調這是「實驗結果」或「文獻記載」。

3. **引用格式**：
   - 引用時，請直接在句子後面加上編號，例如：「...研究顯示其生物活性 [1]。」
   - **不要**使用原文的引用編號 (如 (15), [12])。只能使用我賦予的【文獻 x】編號。
   - **參考文獻列表規則 (重要)**：
     - **只列出你在回答中真正引用到的文獻**。
     - 如果你只用了 [1] 和 [3]，參考文獻就只能列出 1 和 3。
     - 格式 (使用 context 提供的 [引用資訊])：
       參考文獻：
       1. Author, A. A. et al. (Year). Title... - [部位: xxx] [萃取: xxx]
       (若無詳細引用資訊，則使用 PMC ID)

4. **語言策略**：
   - **主要敘述**必須使用通順的**繁體中文**。
   - **專有名詞**（如化學成分、特定蛋白質、菌種名）如果沒有通用的中文翻譯，**可以使用英文**，或採用「中文(英文)」的格式。

5. **產品關聯性檢核 (重要)**：
   - 請特別留意文獻標示的 [部位] (子實體/菌絲體) 與 [萃取法]。
   - 若文獻使用的是「注射」或「純化物」，請勿直接推論為「口服」的效果。
   - 回答時若能區分部位或萃取法（例如：「這項針對子實體水萃取物的研究顯示...」），將更具專業度。

6. **免責聲明**：
   - 在回答的開頭或結尾，適當提醒「本內容僅為學術文獻摘要，不代表醫療建議」。

<</SYS>>

檢索到的文獻資料：
{context}

使用者問題："{query}"

請以「靈芝學術圖書館員」的身分，用繁體中文回答上述問題，嚴格遵守合規性用語，避免醫療宣稱，並附上來源引用：
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
            return "無法連接到 Ollama 服務。請確認 Ollama 正在運行。"
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
    
    print(f"\n問題: {query}")
    print(f"\n答案:\n{answer}")


if __name__ == "__main__":
    main()
