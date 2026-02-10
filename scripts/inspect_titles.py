import json

def main():
    try:
        with open('data/processed/all_chunks.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        papers = {}
        for chunk in data:
            pid = chunk.get('paper_id')
            # Title might be in metadata or we might have to infer it from first chunk or filename
            # The 'title' field was added in auto_ingest, but manual_download didn't put it in metadata clearly
            # But earlier viewing showed 'content' of first chunk usually has title.
            
            if pid not in papers:
                 papers[pid] = chunk.get('content')[:200].replace('\n', ' ')
        
        print(f"Found {len(papers)} papers:")
        for pid, snippet in papers.items():
            print(f"ID: {pid} | Snippet: {snippet}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
