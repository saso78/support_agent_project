import os
from typing import List, Dict
from core.rag import RAGSystem

class DocumentIndexer:
    def __init__(self, rag_system: RAGSystem):
        self.rag = rag_system

    def index_directory(self, directory: str, file_types: List[str] | None = None) -> int:
        """
        Index all documents in a directory.
        
        Args:
            directory: Path to directory containing documents
            file_types: List of file extensions to index (e.g., ['.pdf', '.docx']).
                       If None, defaults to ['.pdf', '.docx', '.txt', '.md']
            
        Returns:
            Number of documents indexed
        """
        supported_types = ['.pdf', '.docx', '.txt', '.md']
        extensions_to_check = file_types if file_types is not None else supported_types
            
        indexed_count = 0
        
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions_to_check):
                    file_path = os.path.join(root, file)
                    try:
                        self.rag.index_document(file_path)
                        indexed_count += 1
                        print(f"✅ Indexed {file_path}")
                    except Exception as e:
                        print(f"❌ Error indexing {file_path}: {str(e)}")
        
        return indexed_count