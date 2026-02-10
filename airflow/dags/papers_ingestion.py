"""
Airflow DAG for automated paper ingestion.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scrapers.ganoderma_news import GanodermaScraper
from src.scrapers.pdf_downloader import EnhancedPDFDownloader
from src.processors.pdf_parser import PDFParser
from src.processors.text_chunker import TextChunker
from loguru import logger


# Default arguments
default_args = {
    'owner': 'ganoderma-rag',
    'depends_on_past': False,
    'start_date': datetime(2026, 2, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


def scrape_papers(**context):
    """Scrape papers from Ganoderma News."""
    logger.info("Starting paper scraping...")
    
    scraper = GanodermaScraper()
    
    # Scrape from all categories
    categories = [
        '研究新知',
        '靈芝調節免疫力',
        '天選之材GMI',
    ]
    
    all_papers = []
    
    for category in categories:
        logger.info(f"Scraping category: {category}")
        papers = scraper.scrape_category(category, max_pages=2)
        all_papers.extend(papers)
    
    logger.success(f"Scraped {len(all_papers)} papers")
    
    # Push to XCom
    context['task_instance'].xcom_push(key='papers', value=all_papers)
    
    return len(all_papers)


def download_pdfs(**context):
    """Download PDFs for scraped papers."""
    logger.info("Starting PDF downloads...")
    
    # Pull papers from XCom
    papers = context['task_instance'].xcom_pull(key='papers', task_ids='scrape_papers')
    
    if not papers:
        logger.warning("No papers to download")
        return 0
    
    downloader = EnhancedPDFDownloader()
    downloaded = []
    
    for paper in papers[:10]:  # Limit to 10 papers per run
        paper_url = paper.get('paper_url')
        paper_source = paper.get('paper_source')
        paper_id = paper.get('paper_id')
        
        if not all([paper_url, paper_source, paper_id]):
            continue
        
        try:
            pdf_path = downloader.download_pdf(paper_url, paper_source, paper_id)
            if pdf_path:
                downloaded.append({
                    'paper_id': paper_id,
                    'pdf_path': pdf_path,
                    **paper
                })
        except Exception as e:
            logger.error(f"Failed to download {paper_id}: {e}")
    
    logger.success(f"Downloaded {len(downloaded)} PDFs")
    
    # Push to XCom
    context['task_instance'].xcom_push(key='downloaded_papers', value=downloaded)
    
    return len(downloaded)


def process_pdfs(**context):
    """Process downloaded PDFs."""
    logger.info("Starting PDF processing...")
    
    # Pull downloaded papers from XCom
    papers = context['task_instance'].xcom_pull(key='downloaded_papers', task_ids='download_pdfs')
    
    if not papers:
        logger.warning("No PDFs to process")
        return 0
    
    parser = PDFParser()
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    
    processed = 0
    
    for paper in papers:
        pdf_path = paper.get('pdf_path')
        
        if not pdf_path:
            continue
        
        try:
            # Parse PDF
            parsed = parser.parse_pdf(pdf_path)
            
            if not parsed:
                continue
            
            # Chunk text
            if parsed['structure']:
                chunks = chunker.chunk_by_sections(
                    parsed['structure'],
                    metadata={
                        'paper_id': paper.get('paper_id'),
                        'file_name': parsed['file_name'],
                    }
                )
            else:
                chunks = chunker.chunk_text(
                    parsed['content'],
                    metadata={
                        'paper_id': paper.get('paper_id'),
                        'file_name': parsed['file_name'],
                    }
                )
            
            # Save chunks (implement database storage here)
            logger.success(f"Processed {paper.get('paper_id')}: {len(chunks)} chunks")
            processed += 1
        
        except Exception as e:
            logger.error(f"Failed to process {paper.get('paper_id')}: {e}")
    
    logger.success(f"Processed {processed} PDFs")
    
    return processed


# Define DAG
dag = DAG(
    'ganoderma_papers_ingestion',
    default_args=default_args,
    description='Automated ingestion of Ganoderma research papers',
    schedule_interval=timedelta(days=7),  # Run weekly
    catchup=False,
    tags=['ganoderma', 'rag', 'ingestion'],
)

# Define tasks
scrape_task = PythonOperator(
    task_id='scrape_papers',
    python_callable=scrape_papers,
    dag=dag,
)

download_task = PythonOperator(
    task_id='download_pdfs',
    python_callable=download_pdfs,
    dag=dag,
)

process_task = PythonOperator(
    task_id='process_pdfs',
    python_callable=process_pdfs,
    dag=dag,
)

# Set task dependencies
scrape_task >> download_task >> process_task
