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
└── tests/             # Test suite
    ├── test_agents.py # Agent tests
    ├── test_core.py   # Core component tests
    └── test_tools.py  # Tool tests
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
   ```

## Usage

Run the main application:
```bash
python run_agent.py
```

### Available Commands

- `/help` - Show available commands
- `/rag <query>` - Query knowledge base
- `/history` - Show conversation history
- `/clear` - Clear conversation memory
- `/prompts` - List available system prompts
- `/quit` - Exit and save conversation

## Components

### Agents

- **BaseAgent**: Abstract base class for all agents
- **GeneralAgent**: General-purpose conversational agent
- **SupportAgent**: Specialized support assistant with RAG integration
- **QAEvaluator**: Evaluates response quality against ground truth

### Core Systems

- **LLM Interface**: Handles communication with OpenRouter API
- **RAG System**: Manages document indexing and retrieval
- **Memory Management**: Handles conversation history
- **System Prompts**: Configurable agent behaviors

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