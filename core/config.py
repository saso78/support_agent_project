import os
from typing import Dict
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

def get_secret(key: str, default=None):
    """
    Get secret from Streamlit secrets (cloud) or environment variables (local).
    
    Args:
        key: The secret key to retrieve
        default: Default value if key not found
    
    Returns:
        The secret value or default
    """
    try:
        import streamlit as st
        # Try Streamlit secrets first (cloud deployment)
        if key in st.secrets:
            return st.secrets[key]
    except (ImportError, FileNotFoundError, AttributeError):
        pass
    
    # Fall back to environment variable (local development)
    return os.getenv(key, default)

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
    temp_uploads_dir: str
    kb_articles_dir: str
    manuals_dir: str
    DOCUMENT_CATEGORIES: Dict[str, str]
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError(
                "API key is required but none was provided. "
                "Please set OPENROUTER_API_KEY in your .env file or Streamlit secrets."
            )

def load_config() -> Config:
    """Load and return the configuration."""
    api_key = OPENROUTER_API_KEY
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY not found in environment. "
            "Please add it to your .env file (local) or Streamlit secrets (cloud)."
        )
        
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
        history_file=HISTORY_FILE,
        temp_uploads_dir=TEMP_UPLOADS_DIR,
        kb_articles_dir=KB_ARTICLES_DIR,
        manuals_dir=MANUALS_DIR,
        DOCUMENT_CATEGORIES=DOCUMENT_CATEGORIES
    )

# API Configuration - now reads from both .env and Streamlit secrets
OPENROUTER_API_KEY = get_secret("OPENROUTER_API_KEY")

# Document Categories
DOCUMENT_CATEGORIES = {
    "manual": "Product Manuals",
    "kb": "Knowledge Base Articles",
    "guide": "User Guides",
    "faq": "FAQs",
    "policy": "Policies",
    "other": "Other Documents"
}

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

# Define additional paths
TEMP_UPLOADS_DIR = os.path.join('data', 'temp_uploads')
KB_ARTICLES_DIR = os.path.join('data', 'kb_articles')
MANUALS_DIR = os.path.join('data', 'manuals')

# Create necessary directories
for directory in [RAG_DB_DIR, os.path.dirname(HISTORY_FILE), 
                 TEMP_UPLOADS_DIR, KB_ARTICLES_DIR, MANUALS_DIR]:
    os.makedirs(directory, exist_ok=True)