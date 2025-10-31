from .base_agent import BaseAgent
from core.llm import OpenRouterLLM
from core.memory import ConversationMemory
from core.rag import RAGSystem
from typing import Dict, Any

class GeneralAgent(BaseAgent):
    def __init__(self, llm: OpenRouterLLM, memory: ConversationMemory, rag: RAGSystem):
        super().__init__(llm, memory)
        self.rag = rag

    def process_message(self, message: str) -> str:
        """Process a general query using RAG and LLM."""
        # Get relevant context from RAG system
        rag_results = self.rag.query(message)
        
        # Get base context and add RAG results
        context: Dict[str, Any] = self.get_conversation_context()
        context["rag_context"] = rag_results
        
        # Generate response using LLM
        response = self.llm.generate_response(message, context)
        
        # Update memory
        self.memory.add_message("user", message)
        self.memory.add_message("assistant", response)
        
        return response