from .base_agent import BaseAgent
from core.llm import LLMInterface, OpenRouterLLM
from core.memory import ConversationMemory
from core.rag import RAGSystem

class SupportAgent(BaseAgent):
    def __init__(self, llm: OpenRouterLLM, memory: ConversationMemory, rag: RAGSystem):
        super().__init__(llm, memory)
        self.rag = rag
        self.support_context = {}

    def process_message(self, message: str) -> str:
        """Process a support query with specialized knowledge."""
        # Get relevant support documentation
        support_docs = self.rag.query(message)
        
        # Update support context
        self.support_context.update({
            "support_docs": support_docs,
            "history": self.memory.get_context()
        })
        
        # Generate specialized support response
        response = self.llm.generate_response(
            message, 
            self.support_context
        )
        
        # Update memory
        self.memory.add_message("user", message)
        self.memory.add_message("assistant", response)
        
        return response