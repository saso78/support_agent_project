import streamlit as st
from pathlib import Path
import sys
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agents.support_agent import SupportAgent
from core.memory import ConversationMemory
from core.config import load_config
from core.llm import OpenRouterLLM
from core.rag import RAGSystem

def initialize_session_state():
    """Initialize session state variables."""
    if 'config' not in st.session_state:
        st.session_state.config = load_config()
    
    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationMemory()
    
    if 'llm' not in st.session_state:
        st.session_state.llm = OpenRouterLLM(
            api_key=st.session_state.config.api_key
        )
    
    if 'rag' not in st.session_state:
        st.session_state.rag = RAGSystem()
    
    if 'agent' not in st.session_state:
        st.session_state.agent = SupportAgent(
            llm=st.session_state.llm,
            memory=st.session_state.memory,
            rag=st.session_state.rag
        )
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def main():
    st.set_page_config(
        page_title="AI Support Agent",
        page_icon="🤖",
        layout="wide"
    )

    st.title("🤖 AI Support Agent")
    st.sidebar.title("Options")

    # Initialize session state
    initialize_session_state()

    # Sidebar options
    if st.sidebar.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.memory.clear()
        st.rerun()

    # Knowledge Base Management
    with st.sidebar.expander("📚 Knowledge Base Management"):
        tabs = st.tabs(["Upload", "Manage", "Stats"])
        
        # Upload Tab
        with tabs[0]:
            st.write("📤 Upload documents to the knowledge base:")
            uploaded_files = st.file_uploader(
                "Drop PDF or DOCX files here",
                type=["pdf", "docx"],
                accept_multiple_files=True,
                help="Supports PDF and DOCX files"
            )
            
            if uploaded_files:
                category = st.selectbox(
                    "Select document category",
                    options=list(st.session_state.config.DOCUMENT_CATEGORIES.keys()),
                    format_func=lambda x: st.session_state.config.DOCUMENT_CATEGORIES[x]
                )
                
                for uploaded_file in uploaded_files:
                    # Create a temporary file to store the upload
                    temp_dir = Path(st.session_state.config.temp_uploads_dir)
                    temp_dir.mkdir(parents=True, exist_ok=True)
                    temp_path = temp_dir / uploaded_file.name
                    
                    # Save uploaded file temporarily
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    try:
                        # Show preview
                        st.write("📄 Document Preview:")
                        preview = st.session_state.rag.preview_document(str(temp_path))
                        st.text_area("Content preview:", preview, height=100)
                        
                        if st.button(f"Index {uploaded_file.name}"):
                            # Index the document
                            with st.spinner(f"Indexing {uploaded_file.name}..."):
                                docs_indexed = st.session_state.rag.index_document(
                                    str(temp_path),
                                    category=category
                                )
                                st.success(f"✅ Successfully indexed {uploaded_file.name}")
                    except Exception as e:
                        st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                    finally:
                        # Clean up temporary file
                        temp_path.unlink(missing_ok=True)
        
        # Manage Tab
        with tabs[1]:
            st.write("🗂️ Manage Documents")
            try:
                collection_info = st.session_state.rag.get_collection_info()
                if collection_info['sources']:
                    for source in collection_info['sources']:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(Path(source).name)
                        with col2:
                            if st.button("🔄 Re-index", key=f"reindex_{source}"):
                                category = next(
                                    (k for k, v in collection_info.get('categories', {}).items() 
                                     if source in v),
                                    'other'
                                )
                                with st.spinner("Re-indexing..."):
                                    if st.session_state.rag.reindex_document(source, category):
                                        st.success("✅ Re-indexed successfully")
                                    else:
                                        st.error("❌ Re-indexing failed")
                        with col3:
                            if st.button("🗑️ Delete", key=f"delete_{source}"):
                                with st.spinner("Deleting..."):
                                    if st.session_state.rag.delete_document(source):
                                        st.success("✅ Deleted successfully")
                                    else:
                                        st.error("❌ Deletion failed")
                else:
                    st.info("No documents in the knowledge base yet")
            except Exception as e:
                st.error(f"Error managing documents: {str(e)}")
        
        # Stats Tab
        with tabs[2]:
            try:
                collection_info = st.session_state.rag.get_collection_info()
                st.write("📊 Knowledge Base Statistics")
                
                # Overall stats
                st.metric("Total Documents", collection_info['total_documents'])
                st.metric("Total Chunks", collection_info['total_chunks'])
                
                # Category breakdown
                if collection_info.get('categories'):
                    st.write("📑 Documents by Category:")
                    for cat, count in collection_info['categories'].items():
                        cat_name = st.session_state.config.DOCUMENT_CATEGORIES.get(cat, cat)
                        st.write(f"- {cat_name}: {count}")
                
                # Source list
                if collection_info['sources']:
                    with st.expander("📚 Document List"):
                        for source in collection_info['sources']:
                            st.write(f"- {Path(source).name}")
            except Exception as e:
                st.error(f"Error getting collection info: {str(e)}")

    # RAG query option
    with st.sidebar.expander("Knowledge Base Search"):
        rag_query = st.text_input("Search:")
        if rag_query:
            with st.spinner("Searching knowledge base..."):
                response = st.session_state.rag.query(rag_query)
                st.sidebar.write(response)

    # Main chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Chat input
        if prompt := st.chat_input("How can I help you today?"):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.write(prompt)

            # Get bot response
            with st.chat_message("assistant"):
                response = st.session_state.agent.process_message(prompt)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()