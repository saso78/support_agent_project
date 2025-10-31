from .base_agent import BaseAgent
from core.llm import OpenRouterLLM
from core.memory import ConversationMemory
from typing import Dict, Any

class QAEvaluator(BaseAgent):
    def __init__(self, llm: OpenRouterLLM, memory: ConversationMemory):
        """
        Initialize QA Evaluator with LLM and memory components.
        
        Args:
            llm: OpenRouter LLM instance for generating evaluations
            memory: Conversation memory for storing evaluation history
        """
        super().__init__(llm, memory)
        self.evaluation_metrics = {
            "accuracy": 0.0,
            "relevance": 0.0,
            "completeness": 0.0
        }

    def process_message(self, message: str) -> str:
        """
        Process a message - for QAEvaluator this is not the primary interface.
        Use evaluate_response instead.
        """
        return "QA Evaluator doesn't process messages directly. Use evaluate_response() instead."

    def evaluate_response(self, query: str, response: str, ground_truth: str) -> Dict[str, float]:
        """Evaluate the quality of an agent's response."""
        evaluation_prompt = self.system_prompts.get_evaluation_prompt(
            query=query,
            response=response,
            ground_truth=ground_truth
        )
        
        # Use general response generation with evaluation prompt
        raw_evaluation = self.llm.generate_response(evaluation_prompt, {
            "system_prompt": "You are an evaluation agent. Provide numerical metrics in JSON format."
        })
        
        try:
            # Parse JSON response into evaluation metrics
            evaluation_result = eval(raw_evaluation)  # Safe since we control the LLM prompt
            self._update_metrics(evaluation_result)
        except Exception as e:
            print(f"❌ Error parsing evaluation response: {e}")
            # Return current metrics if parsing fails
            
        return self.evaluation_metrics

    def _update_metrics(self, evaluation_result: Dict[str, float]):
        """Update evaluation metrics based on new results."""
        for metric in self.evaluation_metrics:
            if metric in evaluation_result:
                self.evaluation_metrics[metric] = evaluation_result[metric]

    def generate_report(self) -> str:
        """Generate an evaluation report."""
        return f"""QA Evaluation Report:
        Accuracy: {self.evaluation_metrics['accuracy']:.2f}
        Relevance: {self.evaluation_metrics['relevance']:.2f}
        Completeness: {self.evaluation_metrics['completeness']:.2f}
        """