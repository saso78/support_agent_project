from typing import List, Dict, Any, Optional
import os
import pdfplumber
import chromadb
from sentence_transformers import SentenceTransformer
from .config import RAG_DB_PATH, COLLECTION_NAME, CHUNK_SIZE, CHUNK_OVERLAP

class RAGSystem:
    def __init__(self):
        """Initialize the RAG system with embedding model and database."""
        # Use a more semantically-aware model
        self.embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        self.client = chromadb.PersistentClient(path=RAG_DB_PATH)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using the local model."""
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist() # type: ignore
        except Exception as e:
            print(f"❌ Embedding error: {e}")
            return None

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from a PDF file with smart formatting."""
        text = ""
        last_y = None  # Track last line's y-position
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # Extract text with positioning
                words = page.extract_words(keep_blank_chars=True, x_tolerance=3)
                lines = []
                current_line = []
                
                for word in words:
                    if last_y is None:
                        current_line.append(word['text'])
                    # Check if word is on same line (with small tolerance)
                    elif abs(word['top'] - last_y) < 3:
                        current_line.append(word['text'])
                    else:
                        # New line detected
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [word['text']]
                    last_y = word['top']
                
                # Add last line if exists
                if current_line:
                    lines.append(' '.join(current_line))
                
                # Join lines into paragraphs
                text += '\n'.join(lines) + '\n\n'
                last_y = None  # Reset for next page
                
        # Clean up excessive whitespace while preserving paragraph breaks
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        return text

    def split_into_chunks(self, text: str, size: int = 1000) -> List[str]:
        """Split text into smaller, more focused chunks with header awareness."""
        # Split into sections by headers first
        sections = []
        current_section = []
        lines = text.split("\n")
        
        for line in lines:
            # Check if line is a header (ends with ':' and has no bullet points)
            if line.strip().endswith(':') and not line.strip().startswith('-'):
                # Store previous section if exists
                if current_section:
                    sections.append('\n'.join(current_section))
                # Start new section
                current_section = [line]
            else:
                current_section.append(line)
        
        # Add last section
        if current_section:
            sections.append('\n'.join(current_section))
        
        chunks = []
        for section in sections:
            # Skip empty sections
            if not section.strip():
                continue
                
            # If section is small enough, keep it as is
            if len(section) <= size:
                chunks.append(section)
                continue
            
            # For large sections, split into smaller parts but keep header
            header = section.split('\n')[0] if ':' in section.split('\n')[0] else ""
            body = section[len(header):] if header else section
            
            # Split body into smaller chunks
            body_chunks = []
            current_chunk = []
            current_size = len(header) if header else 0
            
            for para in [p.strip() for p in body.split("\n") if p.strip()]:
                if current_size + len(para) + 1 > size:
                    if current_chunk:
                        chunk_text = header + '\n' if header else ""
                        chunk_text += '\n'.join(current_chunk)
                        body_chunks.append(chunk_text)
                    current_chunk = [para]
                    current_size = len(header) + len(para)
                else:
                    current_chunk.append(para)
                    current_size += len(para) + 1
            
            if current_chunk:
                chunk_text = header + '\n' if header else ""
                chunk_text += '\n'.join(current_chunk)
                body_chunks.append(chunk_text)
            
            chunks.extend(body_chunks)
        
        return chunks



    def query(self, query_text: str, n_results: int = 5) -> str:
        """Query the knowledge base for relevant information."""
        query_embedding = self.get_embedding(query_text)
        if query_embedding is None:
            return "⚠️ Cannot generate embedding for query."

        try:
            # Get results without filtering first
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results * 3,  # Get more results initially
            )
            
            if not results or "documents" not in results:
                return "📭 No relevant information found."
                
            # Detect which manual to query based on keywords
            query_lower = query_text.lower()
            source_filter = None
            
            # Keywords for each manual
            crusader_keywords = ["crusader", "tracking", "track vehicles", "eztotrack", "live tracking"]
            gdg_keywords = ["gdg", "gooddealgps", "eld", "logging", "electronic log", "gooddeal"]
            hos_keywords = [
                "hos", "hours of service", "driving hours", "rest", "break",
                "34 hour", "11 hour", "14 hour", "sleeper berth", "split break",
                "on duty", "off duty", "driving time", "logbook", "cycle",
                "70 hour", "60 hour", "recap", "rest break", "duty status"
            ]
            
            if any(word in query_lower for word in crusader_keywords):
                source_filter = "CrusaderUserManual"
            elif any(word in query_lower for word in gdg_keywords):
                source_filter = "GDGUserManual"
            elif any(word in query_lower for word in hos_keywords):
                source_filter = "us_hos"
            
            # Filter results by source if needed
            if source_filter and results and isinstance(results, dict):
                result_docs = results.get("documents", [])
                if result_docs and len(result_docs) > 0:
                    docs = result_docs[0]
                    
                    # Safely get metadatas
                    result_metadatas = results.get("metadatas")
                    if result_metadatas and len(result_metadatas) > 0:
                        metadatas = result_metadatas[0]
                    else:
                        metadatas = [{}] * len(docs)
                    
                    # Safely get distances
                    result_distances = results.get("distances")
                    if result_distances and len(result_distances) > 0:
                        distances = result_distances[0]
                    else:
                        distances = [1.0] * len(docs)
                
                # Filter the results
                filtered_results = []
                for i in range(len(docs)):
                    source = str(metadatas[i].get("source", ""))
                    if source_filter in source:
                        filtered_results.append({
                            "document": docs[i],
                            "metadata": metadatas[i],
                            "distance": distances[i] if distances else 1.0
                        })
                
                if filtered_results:
                    # Sort by distance and convert back to format expected by rest of code
                    filtered_results.sort(key=lambda x: x["distance"])
                    docs = [r["document"] for r in filtered_results]
                    metadatas = [r["metadata"] for r in filtered_results]
                    distances = [r["distance"] for r in filtered_results]
                    
                    # Update results
                    results = {
                        "documents": [docs],
                        "metadatas": [metadatas],
                        "distances": [distances]
                    }

            if not results or "documents" not in results or not results["documents"]:
                return "📭 No relevant information found."
                
            # Safely get results
            result_docs = results.get("documents")
            result_metadatas = results.get("metadatas")
            result_distances = results.get("distances")
            
            if not result_docs:
                return "📭 No relevant information found."
                
            docs = result_docs[0]
            metadatas = result_metadatas[0] if result_metadatas else [{}] * len(docs)
            distances = result_distances[0] if result_distances else [1.0] * len(docs)
            
            # Sort results by relevance score
            sorted_results = list(zip(docs, metadatas, distances))
            sorted_results.sort(key=lambda x: x[2])  # Sort by distance (lower is better)
            
            # Enhanced filtering - remove near duplicates and combine related chunks
            filtered_chunks = []
            seen_content = set()
            current_chunk = {"text": "", "source": "", "distance": float('inf')}
            
            for doc, metadata, distance in sorted_results:
                # Create a simplified version for deduplication
                simple_text = ' '.join(doc.lower().split())[:100]
                source = str(metadata.get("source", "unknown"))
                
                if simple_text not in seen_content:
                    seen_content.add(simple_text)
                    
                    # If this chunk is from the same source and close in relevance,
                    # append to current chunk
                    if (current_chunk["source"] == source and 
                        abs(distance - current_chunk["distance"]) < 0.1 and
                        len(current_chunk["text"]) < 1000):
                        current_chunk["text"] += "\n" + doc
                        current_chunk["distance"] = min(current_chunk["distance"], distance)
                    else:
                        # Start new chunk if previous exists
                        if current_chunk["text"]:
                            filtered_chunks.append(current_chunk)
                        current_chunk = {
                            "text": doc,
                            "source": source,
                            "distance": distance
                        }
            
            # Add last chunk
            if current_chunk["text"]:
                filtered_chunks.append(current_chunk)
            
            # Format results more concisely
            context = "📚 Most relevant information:\n\n"
            for chunk in filtered_chunks[:n_results]:
                # Split into sentences and select most relevant
                sentences = [s.strip() + '.' for s in chunk["text"].replace('\n', ' ').split('.') if s.strip()]
                
                # Take most informative sentences (up to 500 chars)
                focused_text = ''
                for sentence in sentences:
                    # Skip very short sentences
                    if len(sentence) < 20:
                        continue
                    if len(focused_text) + len(sentence) <= 500:
                        focused_text += ' ' + sentence
                    else:
                        break
                        
                if focused_text and len(focused_text) < len(chunk["text"]):
                    focused_text = focused_text.strip() + "..."

                source = os.path.basename(chunk["source"])
                if focused_text.strip():  # Only include if we have meaningful content
                    context += f"📄 From {source}:\n{focused_text.strip()}\n\n"

            return context if context != "📚 Most relevant information:\n\n" else "📭 No relevant information found."

        except Exception as e:
            return f"❌ Query error: {str(e)}"

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection."""
        try:
            # Get all items from collection
            items = self.collection.get()
            if not items:
                return {
                    "total_chunks": 0,
                    "total_documents": 0,
                    "sources": [],
                    "categories": {}
                }

            # Safely get IDs and metadata
            ids = items.get('ids', [])
            metadatas = items.get('metadatas', [])
            
            # Extract unique sources and categories
            sources = set()
            categories = {}
            
            if metadatas:
                for metadata in metadatas:
                    if metadata:
                        if 'source' in metadata:
                            sources.add(metadata['source'])
                        if 'category' in metadata:
                            cat = metadata['category']
                            categories[cat] = categories.get(cat, 0) + 1

            return {
                "total_chunks": len(ids),
                "total_documents": len(sources),
                "sources": sorted(list(sources)),
                "categories": categories
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")  # Log the error
            return {
                "total_chunks": 0,
                "total_documents": 0,
                "sources": [],
                "categories": {}
            }

    def delete_document(self, source: str) -> bool:
        """Delete all chunks from a specific document."""
        try:
            # Get all IDs for the document
            results = self.collection.get(
                where={"source": source}
            )
            if results and 'ids' in results:
                self.collection.delete(
                    ids=results['ids']
                )
            return True
        except Exception as e:
            print(f"❌ Error deleting document: {e}")
            return False

    def reindex_document(self, file_path: str, category: str) -> bool:
        """Re-index an existing document."""
        try:
            # First delete existing chunks
            self.delete_document(file_path)
            # Then index again
            self.index_document(file_path, category)
            return True
        except Exception as e:
            print(f"❌ Error reindexing document: {e}")
            return False

    def index_document(self, file_path: str, category: str = "other") -> int:
        """Process a document and add it to the vector store."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Extract text based on file type
        if file_path.lower().endswith('.pdf'):
            text = self.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith(('.txt', '.md', '.docx')):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file type: {file_path}")

        if not text.strip():
            raise ValueError("No text content extracted from document")

        chunks = self.split_into_chunks(text)
        successful = 0

        # Delete existing chunks if any
        self.delete_document(file_path)

        for i, chunk in enumerate(chunks):
            embedding = self.get_embedding(chunk)
            if embedding is None:
                continue

            self.collection.add(
                ids=[f"{os.path.basename(file_path)}_{i}"],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{
                    "source": file_path,
                    "chunk_index": i,
                    "category": category,
                    "filename": os.path.basename(file_path)
                }]
            )
            successful += 1

        return successful

    def preview_document(self, file_path: str, max_chars: int = 500) -> str:
        """Generate a preview of document content."""
        try:
            if file_path.lower().endswith('.pdf'):
                text = self.extract_text_from_pdf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

            # Clean and truncate the text
            preview = ' '.join(text.split())[:max_chars]
            if len(text) > max_chars:
                preview += "..."
            return preview
        except Exception as e:
            return f"Error generating preview: {str(e)}"

    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            self.client.delete_collection(COLLECTION_NAME)
            self.collection = self.client.create_collection(name=COLLECTION_NAME)
            return True
        except Exception as e:
            print(f"❌ Error clearing collection: {e}")
            return False
