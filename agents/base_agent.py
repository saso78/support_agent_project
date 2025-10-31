from typing import List, Dict, Any
from abc import ABC, abstractmethod
from core.memory import ConversationMemory
from core.llm import OpenRouterLLM
from core.prompts import SystemPrompts

class BaseAgent(ABC):
    def __init__(self, llm: OpenRouterLLM, memory: ConversationMemory):
        """Initialize the base agent with LLM and memory components."""
        self.llm = llm
        self.memory = memory
        self.system_prompts = SystemPrompts()
        self.current_prompt_type = "default"

    @abstractmethod
    def process_message(self, message: str) -> str:
        """Process an incoming message and return a response."""
        raise NotImplementedError("Subclasses must implement process_message")

    def get_conversation_context(self) -> Dict[str, Any]:
        """Get current conversation context including history."""
        return {
            "system_prompt": self.system_prompts.get_prompt(self.current_prompt_type),
            "messages": self.memory.get_context()
        }

    def update_conversation_context(self, context: Dict[str, Any]) -> None:
        """Update conversation context with new information."""
        if "prompt_type" in context:
            self.current_prompt_type = context["prompt_type"]
        if "messages" in context:
            self.memory.add_messages(context["messages"])

    def set_prompt_type(self, prompt_type: str) -> None:
        """Change the current system prompt type."""
        if prompt_type in self.system_prompts.prompts:
            self.current_prompt_type = prompt_type