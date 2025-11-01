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
            # Get relevant information directly from RAG system
            rag_response = rag_system.query(user_message)
            logger.info("RAG response retrieved successfully")
            
            if "No relevant information found" in rag_response:
                # Only use agent if RAG has no direct answer
                response = agent.process_message(user_message)
            else:
                # Use RAG response directly
                response = rag_response
            
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