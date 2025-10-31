from typing import Dict, Any

class SystemPrompts:
    """Manages system prompts for different agent behaviors."""
    
    def __init__(self):
        """Initialize with default system prompts."""
        self._prompts: Dict[str, str] = {
            "default": "You are a helpful AI assistant. Always reply in complete sentences.",
            "concise": "You are a helpful AI assistant. Be extremely concise and direct. Answer in 1-2 sentences when possible.",
            "expert": "You are an expert technical advisor. Provide detailed, accurate explanations with examples.",
            "creative": "You are a creative writing assistant. Be imaginative, descriptive, and engaging in your responses.",
            "teacher": "You are a patient teacher. Explain concepts clearly with analogies and examples. Break down complex topics.",
            "coder": "You are an expert programmer. Provide clean, well-documented code solutions with explanations.",
            "analyst": "You are a data analyst. Provide structured, analytical responses with logical reasoning.",
            "support": """You are a specialized support agent. Your role is to:
                1. Help users with technical issues
                2. Reference relevant documentation
                3. Provide step-by-step solutions
                4. Follow up to ensure issues are resolved
                5. Maintain a professional and helpful tone"""
        }

    @property
    def prompts(self) -> Dict[str, str]:
        """Get all available prompts."""
        return self._prompts.copy()  # Return a copy to prevent direct modification

    def get_prompt(self, prompt_type: str) -> str:
        """Get a system prompt by type."""
        return self._prompts.get(prompt_type, self._prompts["default"])

    def add_prompt(self, name: str, prompt: str) -> None:
        """Add a new system prompt."""
        self._prompts[name] = prompt

    def get_evaluation_prompt(self, query: str, response: str, ground_truth: str) -> str:
        """Generate a prompt for evaluating response quality."""
        return f"""Please evaluate this AI response for accuracy and completeness.

Query: {query}

AI Response: {response}

Ground Truth: {ground_truth}

Evaluate the response on these criteria:
1. Accuracy (0-1): How factually correct is the response?
2. Relevance (0-1): How well does it address the query?
3. Completeness (0-1): How thorough is the response?

Provide your evaluation as a JSON object with these metrics."""

    def get_rag_prompt(self, context: str, query: str) -> str:
        """Generate a prompt for RAG-enhanced responses."""
        return f"""Use the following context to answer the question accurately. 
If the context doesn't contain relevant information, say so.

Context:
{context}

Question: {query}

Answer:"""
