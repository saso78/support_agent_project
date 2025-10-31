"""
Quick script to index documents in the manuals directory
"""
from pathlib import Path
from core.rag import RAGSystem
from utils.indexer import DocumentIndexer

def main():
    # Initialize RAG system
    rag_system = RAGSystem()
    
    # Create indexer
    indexer = DocumentIndexer(rag_system)
    
    # Index manuals directory
    manuals_dir = Path("data") / "manuals"
    print(f"\n📚 Indexing documents in {manuals_dir}...")
    count = indexer.index_directory(str(manuals_dir), ['.pdf'])
    print(f"\n✅ Successfully indexed {count} documents")

if __name__ == "__main__":
    main()