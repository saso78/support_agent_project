import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agents.support_agent import SupportAgent
from core.memory import ConversationMemory
from core.config import load_config

def initialize_session_state():
    """Initialize session state variables."""
    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationMemory()
    if 'agent' not in st.session_state:
        config = load_config()
        st.session_state.agent = SupportAgent(config, st.session_state.memory)
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

    # RAG query option
    with st.sidebar.expander("RAG Query"):
        rag_query = st.text_input("Search knowledge base:")
        if rag_query:
            response = st.session_state.agent.process_command("/rag " + rag_query)
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