# Support Agent Project

A modular, extensible AI support agent system with RAG (Retrieval Augmented Generation) capabilities.

## Features

- 🤖 Multiple specialized agents (Support, General, QA Evaluation)
- 📚 RAG system for knowledge base integration
- 💾 Persistent conversation memory
- 🔧 Extensible tool system
- 🎭 Configurable system prompts
- 📊 QA response evaluation
- 📝 Comprehensive logging
- 📞 **Call Center QA Tool** - Automated call testing and evaluation (NEW)

## Project Structure

```
├── agents/                 # Agent implementations
│   ├── base_agent.py      # Base agent class
│   ├── general_agent.py   # General purpose agent
│   ├── qa_evaluator.py    # QA evaluation agent
│   └── support_agent.py   # Support specialist agent
├── core/                  # Core components
│   ├── config.py         # Configuration settings
│   ├── llm.py           # LLM interface and implementation
│   ├── memory.py        # Conversation memory management
│   ├── prompts.py       # System prompts management
│   └── rag.py           # RAG system implementation
├── data/                 # Data storage
│   ├── chat_history/    # Conversation history
│   ├── kb_articles/     # Knowledge base articles
│   ├── manuals/         # Documentation
│   └── rag_db/          # Vector database storage
├── tools/               # Tool implementations
│   ├── file_tools.py   # File operations
│   ├── rag_tools.py    # RAG utilities
│   ├── system_tools.py # System operations
│   └── web_tools.py    # Web interactions
├── utils/              # Utility modules
│   ├── indexer.py     # Document indexing
│   ├── report_generator.py # Report generation
│   └── scenario_loader.py # Test scenario loading
├── streamlit_pages/    # Streamlit dashboard pages
│   └── call_qa_dashboard.py # Call QA dashboard
├── scripts/            # Utility scripts
│   ├── run_test_call.py # CLI for making test calls
│   ├── quick_demo.py  # Quick demo script
│   └── demo_call_qa_setup.py # Demo data setup
├── data/
│   └── call_scenarios/ # Call test scenarios (JSON)
└── tests/             # Test suite
    ├── test_agents.py # Agent tests
    ├── test_core.py   # Core component tests
    ├── test_tools.py  # Tool tests
    ├── test_database.py # Database tests (Call QA)
    ├── test_voice.py  # Voice integration tests
    ├── test_transcription.py # Transcription tests
    └── test_evaluation.py # Call evaluation tests
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the environment:
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   
   # Call QA Tool (optional - for real API calls)
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=+1234567890
   ELEVENLABS_API_KEY=your_elevenlabs_key
   DEEPGRAM_API_KEY=your_deepgram_key
   USE_MOCK_APIS=true  # Set to false for real API calls
   ```
   
   See `.env.example` for all available configuration options.

## Usage

### Support Agent Application

Run the main application:
```bash
python run_agent.py
```

**Available Commands:**
- `/help` - Show available commands
- `/rag <query>` - Query knowledge base
- `/history` - Show conversation history
- `/clear` - Clear conversation memory
- `/prompts` - List available system prompts
- `/quit` - Exit and save conversation

### Call QA Tool

The Call Center QA Tool allows you to make automated test calls to evaluate agent performance.

**Quick Demo:**
```bash
# 1. Set up demo data (creates sample calls)
python demo_call_qa_setup.py

# 2. Launch dashboard
python -m streamlit run streamlit_pages/call_qa_dashboard.py

# 3. Open http://localhost:8501 in your browser
```

**CLI Usage:**
```bash
# Make a test call
python scripts/run_test_call.py --scenario cancel_subscription --phone +1234567890 --name "Test Agent"

# Quick demo (creates and evaluates one call)
python scripts/quick_demo.py
```

**Dashboard Features:**
- 📊 View call history with scores
- 📞 Make new test calls
- 👥 Agent performance rankings
- 📈 Analytics and trends

**Mock Mode:**
By default, the tool runs in mock mode (`USE_MOCK_APIS=true`), which means:
- No real API calls (no costs)
- Uses simulated data
- Perfect for development and demos

See [README_CALL_QA_DEMO.md](README_CALL_QA_DEMO.md) for detailed demo instructions.

## Components

### Agents

- **BaseAgent**: Abstract base class for all agents
- **GeneralAgent**: General-purpose conversational agent
- **SupportAgent**: Specialized support assistant with RAG integration
- **QAEvaluator**: Evaluates response quality against ground truth
- **CallQAAgent**: Evaluates call center performance on 5 metrics (greeting, hold time, resolution, tone, compliance)

### Core Systems

- **LLM Interface**: Handles communication with OpenRouter API
- **RAG System**: Manages document indexing and retrieval
- **Memory Management**: Handles conversation history
- **System Prompts**: Configurable agent behaviors

### Call QA Tool Components

- **Voice Engine** (`core/voice.py`): Twilio integration for outbound calls, ElevenLabs TTS
- **Transcription Engine** (`core/transcription.py`): Deepgram integration for call transcription with speaker diarization
- **Database** (`core/database.py`): SQLite database for call logs, transcripts, scores, and agent metrics
- **Call QA Agent** (`agents/call_qa_agent.py`): Evaluates calls using 5-metric scoring rubric
- **Dashboard** (`streamlit_pages/call_qa_dashboard.py`): Web interface for viewing call history, scores, and analytics

### Tools

- **File Tools**: File operations and management
- **Web Tools**: Web content retrieval
- **System Tools**: System operations and monitoring
- **RAG Tools**: Document indexing and querying

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New Features

1. **New Agent**:
   - Inherit from `BaseAgent`
   - Implement `process_message()`
   - Add to agent factory if needed

2. **New Tool**:
   - Add to `tools/` directory
   - Implement tool interface
   - Register in tool registry

3. **New Command**:
   - Add to command handler
   - Update help documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details