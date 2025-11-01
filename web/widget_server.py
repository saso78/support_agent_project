from pathlib import Path
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agents.support_agent import SupportAgent
from core.memory import ConversationMemory
from core.config import load_config
from core.llm import OpenRouterLLM
from core.rag import RAGSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize components
config = load_config()
rag_system = RAGSystem()  # Initialize RAG first
memory = ConversationMemory()
llm = OpenRouterLLM(api_key=config.api_key)

# Initialize support agent with RAG system
agent = SupportAgent(
    llm=llm,
    memory=memory,
    rag=rag_system
)

# Log initialization status
logger.info("Widget server initialized with RAG system. Documents loaded: %s", 
            rag_system.get_collection_info().get('total_documents', 0))

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files for the widget."""
    return send_from_directory('static', filename)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the widget."""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message parameter'}), 400

        user_message = data['message']
        history = data.get('history', [])

        # Log incoming request
        logger.info("Processing chat request: %s", user_message)

        try:
            # Record the message
            from utils.usage_stats import usage_tracker
            usage_tracker.record_message(user_message, source="widget")
            
            # For basic chat messages (greetings, short queries), just use agent
            if len(user_message.split()) <= 2 or any(word in user_message.lower() for word in [
                'hi', 'hello', 'hey', 'thanks', 'thank you', 'bye', 'goodbye'
            ]):
                response = agent.process_message(user_message)
                logger.info("Simple greeting - using agent response only")
            else:
                # First try to get relevant information from RAG
                rag_response = rag_system.query(user_message)
                logger.info("RAG response retrieved")
                
                if "No relevant information found" in rag_response:
                    # If no RAG info, use just the agent response
                    response = agent.process_message(user_message)
                    logger.info("No RAG info - using agent response only")
                else:
                    # If we have RAG info, provide it to the agent for context
                    context_prompt = f"""Based on our documentation, here are the relevant details:
{rag_response}

Please provide a VERY CONCISE response using this information. Focus only on the most directly relevant information to answer the user's question. Do not include system requirements or other technical details unless specifically asked."""
                    
                    # Get agent response with RAG context
                    agent_response = agent.process_message(context_prompt)
                    logger.info("Generated contextualized agent response")
                    
                    # Extract only the most relevant part from RAG response
                    if "📄 From test_glossary.txt:" in rag_response:
                        sections = rag_response.split("📄 From test_glossary.txt:")
                        # Get main section (first relevant hit)
                        main_section = sections[1].split("\n\n")[0].strip()
                        
                        # Get related topics
                        related_topics = []
                        for section in sections[1:]:
                            title = section.split(':')[0].strip()
                            if title and title != "Common Issues" and title != "System Requirements":
                                related_topics.append(title)
                    else:
                        main_section = rag_response
                        related_topics = []

                    # Create a concise response focusing on the main answer
                    concise_response = f"{main_section}"
                    
                    # Add related topics as suggestions if available
                    if related_topics:
                        suggestions = "\n\n💡 Related topics you might be interested in:"
                        for topic in related_topics[:3]:  # Limit to 3 suggestions
                            suggestions += f"\n• Ask me about '{topic}'"
                        concise_response += suggestions
                    
                    response = concise_response
            
            return jsonify({
                'response': response,
                'sources': rag_system.get_collection_info()['sources']
            })
        except Exception as e:
            logger.error("Error processing message: %s", str(e))
            return jsonify({
                'error': 'Error processing message',
                'details': str(e)
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_widget_server(host: str = 'localhost', port: int = 8000, debug: bool = False):
    """Run the Flask server for the chat widget."""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_widget_server(debug=True)