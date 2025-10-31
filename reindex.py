"""
Script to clear and reindex documents with improved settings
"""
from core.rag import RAGSystem
from utils.indexer import DocumentIndexer
from pathlib import Path

def main():
    # Initialize RAG
    rag = RAGSystem()
    
    # Clear existing collection
    print("\n🗑️ Clearing existing collection...")
    rag.clear_collection()
    
    # Create indexer
    indexer = DocumentIndexer(rag)
    
    # Index manuals directory
    manuals_dir = Path("data") / "manuals"
    print(f"\n📚 Indexing documents in {manuals_dir}...")
    count = indexer.index_directory(str(manuals_dir), ['.pdf'])
    print(f"\n✅ Successfully indexed {count} documents")
    
    # Get collection info
    info = rag.get_collection_info()
    print("\n📊 Collection Info:")
    print(f"Total chunks: {info['total_chunks']}")
    print(f"Total documents: {info['total_documents']}")
    print("Sources:", ", ".join(info['sources']))

if __name__ == "__main__":
    main()