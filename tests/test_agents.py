import unittest
from agents.base_agent import BaseAgent
from agents.general_agent import GeneralAgent
from agents.support_agent import SupportAgent
from agents.qa_evaluator import QAEvaluator
from core.llm import LLMInterface
from core.memory import ConversationMemory
from core.rag import RAGSystem
from unittest.mock import MagicMock

class TestAgents(unittest.TestCase):
    def setUp(self):
        self.llm = MagicMock(spec=LLMInterface)
        self.memory = MagicMock(spec=ConversationMemory)
        self.rag = MagicMock(spec=RAGSystem)

    def test_general_agent(self):
        """Test general purpose agent."""
        agent = GeneralAgent(self.llm, self.memory, self.rag)
        
        # Test message processing
        test_message = "What are the product features?"
        self.rag.query.return_value = "Product features include..."
        self.llm.generate_response.return_value = "Here are the features..."
        
        response = agent.process_message(test_message)
        
        self.assertIsInstance(response, str)
        self.rag.query.assert_called_once()
        self.llm.generate_response.assert_called_once()

    def test_support_agent(self):
        """Test support specialist agent."""
        agent = SupportAgent(self.llm, self.memory, self.rag)
        
        # Test support query processing
        test_query = "How do I reset my password?"
        self.rag.query_support_docs.return_value = "Password reset instructions..."
        self.llm.generate_support_response.return_value = "To reset your password..."
        
        response = agent.process_message(test_query)
        
        self.assertIsInstance(response, str)
        self.rag.query_support_docs.assert_called_once()
        self.llm.generate_support_response.assert_called_once()

    def test_qa_evaluator(self):
        """Test QA evaluation agent."""
        evaluator = QAEvaluator(self.llm, self.memory)
        
        # Test response evaluation
        query = "What is the return policy?"
        response = "You can return items within 30 days."
        ground_truth = "Returns are accepted within 30 days with receipt."
        
        self.llm.evaluate_response.return_value = {
            "accuracy": 0.9,
            "relevance": 0.8,
            "completeness": 0.7
        }
        
        metrics = evaluator.evaluate_response(query, response, ground_truth)
        
        self.assertIsInstance(metrics, dict)
        self.assertIn("accuracy", metrics)
        self.assertIn("relevance", metrics)
        self.assertIn("completeness", metrics)
        self.llm.evaluate_response.assert_called_once()

    def test_base_agent(self):
        """Test base agent functionality."""
        class TestAgent(BaseAgent):
            def process_message(self, message: str) -> str:
                return f"Processed: {message}"
        
        agent = TestAgent(self.llm, self.memory)
        
        # Test context management
        test_context = {"key": "value"}
        self.memory.get_context.return_value = ["message1", "message2"]
        
        context = agent.get_conversation_context()
        self.assertIsInstance(context, dict)
        self.assertIn("system_prompt", context)
        self.assertIn("messages", context)
        self.memory.get_context.assert_called_once()
        
        # Test context update
        agent.update_conversation_context({"messages": test_context})
        self.memory.add_messages.assert_called_once_with(test_context)

if __name__ == '__main__':
    unittest.main()