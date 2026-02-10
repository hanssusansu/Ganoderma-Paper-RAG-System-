"""
Gradio web interface for Ganoderma Papers RAG system.
"""
import gradio as gr
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rag.retriever import SimpleRetriever
from src.rag.generator import RAGGenerator
from loguru import logger


class GanodermaRAGUI:
    """Gradio UI for RAG system."""
    
    def __init__(self):
        """Initialize UI."""
        self.retriever = SimpleRetriever()
        self.generator = RAGGenerator()
        
        # Load chunks
        try:
            self.retriever.load_chunks()
            self.ready = True
            logger.success("RAG system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            self.ready = False
    
    def query(self, question: str, top_k: int = 5) -> tuple[str, str]:
        """
        Process a query.
        
        Args:
            question: User question
            top_k: Number of chunks to retrieve
            
        Returns:
            Tuple of (answer, sources)
        """
        if not self.ready:
            return "系統尚未準備就緒，請檢查是否有可用的分塊資料。", ""
        
        if not question or not question.strip():
            return "請輸入問題。", ""
        
        try:
            # Retrieve relevant chunks
            results = self.retriever.retrieve(question, top_k=top_k)
            
            if not results:
                return "抱歉，我找不到相關的資訊來回答您的問題。", ""
            
            # Generate answer
            answer = self.generator.generate_answer(question, results)
            
            # Format sources
            sources = self._format_sources(results)
            
            return answer, sources
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"處理查詢時發生錯誤: {str(e)}", ""
    
    def _format_sources(self, results: list) -> str:
        """Format source citations."""
        sources = []
        
        for i, result in enumerate(results, 1):
            section = result.get('section', 'N/A')
            page = result.get('page', 'N/A')
            file_name = result.get('file_name', 'N/A')
            score = result.get('score', 0)
            content_preview = result['content'][:200] + "..."
            
            # Try to get formatted APA citation
            metadata = result.get('metadata', {})
            citation = metadata.get('citation_str', file_name)
            
            source = f"""
**來源 {i}** (相關度: {score})
- 引用: {citation}
- 章節: {section}
- 頁碼: {page}
- 內容預覽: {content_preview}
"""
            sources.append(source)
        
        return "\n---\n".join(sources)
    
    def create_interface(self):
        """Create Gradio interface."""
        with gr.Blocks(title="🍄 Ganoderma Papers RAG", theme=gr.themes.Soft()) as demo:
            gr.Markdown("""
            # 🍄 靈芝論文問答系統
            
            基於學術論文的智能問答系統，可以回答關於靈芝研究的問題。
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    question_input = gr.Textbox(
                        label="請輸入您的問題",
                        placeholder="例如：靈芝有什麼免疫調節作用？",
                        lines=3
                    )
                    
                    top_k_slider = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=5,
                        step=1,
                        label="檢索分塊數量"
                    )
                    
                    submit_btn = gr.Button("🔍 查詢", variant="primary")
                
                with gr.Column(scale=3):
                    answer_output = gr.Textbox(
                        label="答案",
                        lines=10,
                        max_lines=20,
                        interactive=False
                    )
            
            with gr.Accordion("🔍 系統原始檢索資料 (點擊展開查看)", open=False):
                sources_output = gr.Markdown()
            
            # Examples
            gr.Examples(
                examples=[
                    ["靈芝與免疫調節相關的研究有哪些？", 5],
                    ["靈芝多醣體對於細胞的科學研究發現為何？", 5],
                    ["相關臨床研究的現狀？", 3],
                ],
                inputs=[question_input, top_k_slider]
            )
            
            # Event handlers
            submit_btn.click(
                fn=self.query,
                inputs=[question_input, top_k_slider],
                outputs=[answer_output, sources_output]
            )
            
            question_input.submit(
                fn=self.query,
                inputs=[question_input, top_k_slider],
                outputs=[answer_output, sources_output]
            )
        
            gr.Markdown("""
            ---
            ### ⚠️ 免責聲明
            本系統僅為「靈芝學術文獻圖書館」之檢索工具，所有內容皆為學術研究文獻之摘要與整理。
            內容僅供學術研究與教育用途，**不代表任何醫療建議、功效宣稱或承諾**。
            若有疾病或醫療需求，請務必諮詢專業醫師。
            """)
    
        return demo


def main():
    """Launch the UI."""
    ui = GanodermaRAGUI()
    demo = ui.create_interface()
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7872,
        share=False
    )


if __name__ == "__main__":
    main()
