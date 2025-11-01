from core.rag import RAGSystem
from pathlib import Path

def index_test_doc():
    rag = RAGSystem()
    file_path = Path.cwd() / 'data' / 'kb_articles' / 'test_glossary.txt'
    
    # First verify the file exists
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
        
    try:
        # Get embedding for each chunk
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        chunks = rag.split_into_chunks(text)
        print(f"Split into {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            embedding = rag.get_embedding(chunk)
            if embedding is None:
                print(f"Failed to get embedding for chunk {i}")
                continue
                
            rag.collection.add(
                ids=[f"test_glossary_{i}"],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{
                    "source": str(file_path),
                    "chunk_index": i,
                    "category": "test",
                    "filename": file_path.name
                }]
            )
            print(f"Added chunk {i}")
            
        print("Indexing complete!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    index_test_doc()