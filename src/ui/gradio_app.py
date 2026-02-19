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
            return "System is not ready, please check if chunks data is available.", ""
        
        if not question or not question.strip():
            return "Please enter a question.", ""
        
        try:
            # Retrieve relevant chunks
            results = self.retriever.retrieve(question, top_k=top_k)
            
            if not results:
                return "Sorry, I cannot find relevant information to answer your question.", ""
            
            # Generate answer
            answer = self.generator.generate_answer(question, results)
            
            # Format sources
            sources = self._format_sources(results)
            
            return answer, sources
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Error processing query: {str(e)}", ""
    
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
**Source {i}** (Relevance: {score})
- Citation: {citation}
- Section: {section}
- Page: {page}
- Preview: {content_preview}
"""
            sources.append(source)
        
        return "\n---\n".join(sources)
    
    def create_interface(self):
        """Create Gradio interface."""
        with gr.Blocks(title="🍄 Ganoderma Papers RAG", theme=gr.themes.Soft()) as demo:
            gr.Markdown("""
            # 🍄 Ganoderma Papers RAG System
            
            Intelligent Q&A system based on academic papers, answering questions about Ganoderma research.
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    question_input = gr.Textbox(
                        label="Ask a question",
                        placeholder="e.g.: What are the immunomodulatory effects of Ganoderma?",
                        lines=3
                    )
                    
                    top_k_slider = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=5,
                        step=1,
                        label="Number of retrieved chunks"
                    )
                    
                    submit_btn = gr.Button("🔍 Search", variant="primary")
                
                with gr.Column(scale=3):
                    answer_output = gr.Textbox(
                        label="Answer",
                        lines=10,
                        max_lines=20,
                        interactive=False
                    )
            
            with gr.Accordion("🔍 View Retrieved Sources (Click to expand)", open=False):
                sources_output = gr.Markdown()
            
            # Examples
            gr.Examples(
                examples=[
                    ["What are the studies related to Ganoderma and immune regulation?", 5],
                    ["What are the scientific findings on Ganoderma polysaccharides and cells?", 5],
                    ["What is the current status of clinical trials?", 3],
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
            ### ⚠️ Disclaimer
            This system is a retrieval tool for the "Ganoderma Academic Library". All content is a summary and compilation of academic research literature.
            The content is for academic research and educational purposes only and **does not represent any medical advice, efficacy claims, or promises**.
            If you have medical needs, please consult a professional physician.
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
