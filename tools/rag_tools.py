from core.rag import RAGSystem
from typing import Dict, Any, List

class RAGTools:
    def __init__(self, rag_system: RAGSystem):
        self.rag = rag_system

    def index_document(self, file_path: str) -> Dict[str, Any]:
        """
        Index a document in the RAG system.
        
        Args:
            file_path: Path to the document to index
            
        Returns:
            Dictionary with indexing results
        """
        try:
            chunks_indexed = self.rag.index_document(file_path)
            return {
                "success": True,
                "chunks_indexed": chunks_indexed,
                "message": f"✅ Successfully indexed {chunks_indexed} chunks"
            }
        except Exception as e:
            return {
                "success": False,
                "chunks_indexed": 0,
                "message": f"❌ Error indexing document: {str(e)}"
            }

    def query(self, query_text: str, n_results: int = 3) -> str:
        """
        Query the RAG system.
        
        Args:
            query_text: Text to search for
            n_results: Number of results to return
            
        Returns:
            Query results as formatted string
        """
        return self.rag.query(query_text, n_results)

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the RAG collection.
        
        Returns:
            Dictionary with collection statistics
        """
        return self.rag.get_collection_info()

    def clear_collection(self) -> Dict[str, Any]:
        """
        Clear all documents from the RAG collection.
        
        Returns:
            Status dictionary
        """
        success = self.rag.clear_collection()
        return {
            "success": success,
            "message": "✅ Collection cleared" if success else "❌ Error clearing collection"
        }