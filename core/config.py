import os
from typing import Dict
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class Config:
    """Configuration class for the support agent."""
    api_key: str
    models: list[str]
    max_tokens: int
    temperature: float
    max_history: int
    rag_db_dir: str
    rag_db_path: str
    collection_name: str
    chunk_size: int
    chunk_overlap: int
    system_prompts: Dict[str, str]
    history_file: str

    def __post_init__(self):
        if not self.api_key:
            raise ValueError("API key is required but none was provided")

def load_config() -> Config:
    """Load and return the configuration."""
    api_key = OPENROUTER_API_KEY
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment")
        
    return Config(
        api_key=api_key,
        models=MODELS,
        max_tokens=DEFAULT_MAX_TOKENS,
        temperature=DEFAULT_TEMPERATURE,
        max_history=MAX_HISTORY_MESSAGES,
        rag_db_dir=RAG_DB_DIR,
        rag_db_path=RAG_DB_PATH,
        collection_name=COLLECTION_NAME,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        system_prompts=SYSTEM_PROMPTS,
        history_file=HISTORY_FILE
    )

# API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Model Configuration
MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "mistralai/mistral-7b-instruct",
    "meta-llama/llama-3-8b-instruct",
]

DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.7

# Memory Configuration
MAX_HISTORY_MESSAGES = 10

# RAG Configuration
RAG_DB_DIR = os.path.join('data', 'rag_db')
RAG_DB_PATH = os.path.join(RAG_DB_DIR, 'chroma.db')
COLLECTION_NAME = "pdf_knowledge"
CHUNK_SIZE = 1000  # Increased chunk size for better context
CHUNK_OVERLAP = 200  # Increased overlap for better continuity

# System prompts
SYSTEM_PROMPTS: Dict[str, str] = {
    "default": "You are a helpful AI assistant. Always reply in complete sentences.",
    "concise": "You are a helpful AI assistant. Be extremely concise and direct. Answer in 1-2 sentences when possible.",
    "expert": "You are an expert technical advisor. Provide detailed, accurate explanations with examples.",
    "creative": "You are a creative writing assistant. Be imaginative, descriptive, and engaging in your responses.",
    "teacher": "You are a patient teacher. Explain concepts clearly with analogies and examples. Break down complex topics.",
    "coder": "You are an expert programmer. Provide clean, well-documented code solutions with explanations.",
    "analyst": "You are a data analyst. Provide structured, analytical responses with logical reasoning."
}

# File paths
HISTORY_FILE = os.path.join('data', 'chat_history', 'chat_history.json')

# Create necessary directories
os.makedirs(RAG_DB_DIR, exist_ok=True)
os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
