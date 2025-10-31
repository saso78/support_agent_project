# main.py
"""
Main entry point for the Support Agent project.

This file orchestrates the agent system, including RAG integration,
conversation memory, and command handling.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Core components
from core.config import MODELS, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE
from core.llm import OpenRouterLLM
from core.memory import ConversationMemory
from core.rag import RAGSystem

# Agents
from agents.support_agent import SupportAgent
from agents.general_agent import GeneralAgent

# Tools
from tools.rag_tools import RAGTools
from tools.file_tools import FileTools
from tools.web_tools import WebTools
from tools.system_tools import SystemTools

# Ensure data directories exist
DATA_DIR = Path("data")
RAG_DB_DIR = DATA_DIR / "rag_db"
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAG_DB_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv()

def handle_command(command: str, tools, memory, rag_tools) -> str | None:
    """Handle special commands."""
    if command.startswith("/"):
        if command == "/help":
            return (
                "� Available commands:\n"
                "/rag <query>  - Query knowledge base\n"
                "/history     - Show conversation history\n"
                "/clear      - Clear conversation memory\n"
                "/system     - Show system information\n"
                "/quit       - Exit and save conversation\n"
            )
        elif command == "/history":
            return memory.get_formatted_history()
        elif command == "/clear":
            memory.clear()
            return "✅ Conversation memory cleared"
        elif command.startswith("/rag "):
            query = command[5:].strip()
            return f"\n📚 Knowledge Base Results:\n{rag_tools.query(query)}"
        elif command == "/system":
            info = tools.system_tools.get_system_info()
            return f"System Info:\n{json.dumps(info, indent=2)}"
    return None

def main():
    # Initialize components
    llm = OpenRouterLLM()
    memory = ConversationMemory()
    rag_system = RAGSystem()
    
    # Initialize tools
    rag_tools = RAGTools(rag_system)
    file_tools = FileTools()
    web_tools = WebTools()
    system_tools = SystemTools()
    
    # Bundle tools for easy access
    tools = type('Tools', (), {
        'file_tools': file_tools,
        'web_tools': web_tools,
        'system_tools': system_tools,
        'rag_tools': rag_tools
    })()

    # Initialize agent
    agent = SupportAgent(
        llm=llm,
        memory=memory,
        rag=rag_system
    )

    print("🤖 Support Agent System")
    print(f"✅ Models available: {', '.join(MODELS)}")
    print("Type /help for available commands. 'exit' to quit.\n")

    try:
        while True:
            user_input = input("🧩 > ").strip()
            
            if user_input.lower() in ["exit", "quit", "/quit"]:
                print("\n💾 Saving conversation...")
                memory.save_history()
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue
                
            # Handle special commands
            command_response = handle_command(user_input, tools, memory, rag_tools)
            if command_response:
                print(f"\n💻 {command_response}\n")
                continue

            # Process through agent
            print("\n⏳ Processing...\n")
            response = agent.process_message(user_input)
            print(f"\n🤖 {response}\n")

    except KeyboardInterrupt:
        print("\n\n💾 Saving conversation...")
        memory.save_history()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
