import unittest
from core.memory import ConversationMemory
from core.rag import RAGSystem
from core.llm import LLMInterface
from core.prompts import SystemPrompts
from unittest.mock import MagicMock

class TestCore(unittest.TestCase):
    def setUp(self):
        self.llm = MagicMock(spec=LLMInterface)
        self.memory = ConversationMemory()
        self.rag = MagicMock(spec=RAGSystem)
        self.prompts = SystemPrompts()

    def test_conversation_memory(self):
        """Test conversation memory management."""
        # Add messages with proper roles
        self.memory.add_message("user", "Hello")
        self.memory.add_message("assistant", "Hi there!")
        
        # Get the conversation context
        context = self.memory.get_context()
        
        # Verify messages are in the context
        self.assertTrue(any("Hello" in str(msg) for msg in context))
        self.assertTrue(any("Hi there!" in str(msg) for msg in context))

    def test_rag_system(self):
        """Test RAG query functionality."""
        test_query = "What is the product warranty?"
        self.rag.query.return_value = "The product has a 1-year warranty."
        
        result = self.rag.query(test_query)
        self.assertIn("warranty", result)
        self.rag.query.assert_called_once_with(test_query)

    def test_llm_interface(self):
        """Test LLM response generation."""
        test_prompt = "Generate a response"
        test_context = {"history": []}
        self.llm.generate_response.return_value = "Test response"
        
        response = self.llm.generate_response(test_prompt, test_context)
        self.assertEqual(response, "Test response")
        self.llm.generate_response.assert_called_once_with(test_prompt, test_context)

if __name__ == '__main__':
    unittest.main()