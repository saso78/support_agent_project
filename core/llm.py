from typing import List, Dict, Any, Optional, Generator
import requests
import json
import time
from abc import ABC, abstractmethod
from .config import OPENROUTER_API_KEY, MODELS, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE

class LLMInterface(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, context: Dict[str, Any]) -> str:
        pass
    
    @abstractmethod
    def stream_response(self, prompt: str, context: Dict[str, Any]) -> Generator[str, None, None]:
        pass

class OpenRouterLLM(LLMInterface):
    def __init__(self, api_key: str = "") -> None:
        """Initialize with API key, defaulting to config value if not provided."""
        self.api_key = api_key or OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("API key is required but none was provided")
            
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_messages(self, prompt: str, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build the messages array for the API request."""
        messages = []
        
        # Add system prompt if provided
        if "system_prompt" in context:
            messages.append({
                "role": "system",
                "content": context["system_prompt"]
            })
        
        # Add conversation history
        if "history" in context:
            messages.extend(context["history"])
            
        # Add the current prompt
        messages.append({
            "role": "user",
            "content": prompt.strip()
        })
        
        return messages

    def generate_response(
        self, 
        prompt: str, 
        context: Dict[str, Any],
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE
    ) -> str:
        """Generate a response using the OpenRouter API."""
        messages = self._build_messages(prompt, context)
        
        # Try each model in order until one works
        for model in MODELS:
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "stream": False
                    },
                    timeout=45
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"].get("content", "").strip()
                        if content:
                            return content
                
                elif response.status_code == 429:
                    print(f"⚠️ Rate limit for {model}, trying next...")
                    time.sleep(2)
                    continue
                    
            except Exception as e:
                print(f"❌ Error with {model}: {str(e)}")
                continue
                
        return "❌ All models are currently unavailable. Please try again later."

    def stream_response(
        self, 
        prompt: str, 
        context: Dict[str, Any],
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE
    ) -> Generator[str, None, None]:
        """Stream a response using the OpenRouter API."""
        messages = self._build_messages(prompt, context)
        
        for model in MODELS:
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "stream": True
                    },
                    timeout=45,
                    stream=True
                )
                
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            line_text = line.decode('utf-8')
                            if line_text.startswith('data: '):
                                data_str = line_text[6:]
                                if data_str.strip() == '[DONE]':
                                    break
                                try:
                                    data = json.loads(data_str)
                                    if 'choices' in data and len(data['choices']) > 0:
                                        delta = data['choices'][0].get('delta', {})
                                        content_chunk = delta.get('content', '')
                                        if content_chunk:
                                            yield content_chunk
                                except json.JSONDecodeError:
                                    continue
                    return
                    
                elif response.status_code == 429:
                    print(f"⚠️ Rate limit for {model}, trying next...")
                    time.sleep(2)
                    continue
                    
            except Exception as e:
                print(f"❌ Error with {model}: {str(e)}")
                continue
        
        yield "❌ All models are currently unavailable. Please try again later."
