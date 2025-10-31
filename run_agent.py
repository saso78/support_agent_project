import os
from core.llm import OpenRouterLLM
from core.memory import ConversationMemory
from core.rag import RAGSystem
from core.config import SYSTEM_PROMPTS
from agents.support_agent import SupportAgent
from tools.file_tools import FileTools
from tools.web_tools import WebTools
from tools.system_tools import SystemTools
from tools.rag_tools import RAGTools
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize core components
    llm = OpenRouterLLM()
    memory = ConversationMemory()
    rag_system = RAGSystem()
    
    # Initialize tools
    file_tools = FileTools()
    web_tools = WebTools()
    system_tools = SystemTools()
    rag_tools = RAGTools(rag_system)
    
    # Initialize agent with all components
    agent = SupportAgent(
        llm=llm,
        memory=memory,
        rag=rag_system
    )
    
    print("🤖 Support Agent System")
    print("Commands: /help /rag /history /clear /prompts /quit")
    
    try:
        while True:
            user_input = input("\n🧩 > ").strip()
            
            if user_input.lower() in ["exit", "quit", "/quit"]:
                print("\n💾 Saving conversation...")
                memory.save_history()
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue
                
            # Handle special commands
            if user_input.startswith("/"):
                if user_input == "/help":
                    print(
                        "🧩 Available commands:\n"
                        "/rag       - Query knowledge base\n"
                        "/history   - Show conversation history\n"
                        "/clear     - Clear conversation memory\n"
                        "/prompts   - List available system prompts\n"
                        "/quit      - Exit and save conversation\n"
                    )
                elif user_input == "/history":
                    print(memory.get_formatted_history())
                elif user_input == "/clear":
                    memory.clear()
                elif user_input == "/prompts":
                    for name, prompt in SYSTEM_PROMPTS.items():
                        print(f"- {name}: {prompt}\n")
                elif user_input.startswith("/rag "):
                    query = user_input[5:].strip()
                    result = rag_tools.query(query)
                    print(f"\n📚 Knowledge Base Results:\n{result}")
                continue
            
            # Process normal messages through the agent
            print("\n⏳ Processing...")
            response = agent.process_message(user_input)
            print(f"\n🤖 {response}")
    
    except KeyboardInterrupt:
        print("\n\n💾 Saving conversation...")
        memory.save_history()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()