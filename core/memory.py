# core/memory.py
import os
import json
from datetime import datetime
from core.config import HISTORY_FILE, MAX_HISTORY_MESSAGES

class ConversationMemory:
    def __init__(self):
        self.messages = []
        self.session_start = datetime.now().isoformat()
        self.MAX_HISTORY_MESSAGES = MAX_HISTORY_MESSAGES
        self.load_history()

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if 'messages' in data:
                        self.messages = data['messages'][-self.MAX_HISTORY_MESSAGES:]
                        print(f"📚 Loaded {len(self.messages)} messages from previous session")
            except Exception as e:
                print(f"⚠️ Could not load history: {e}")

    def save_history(self):
        try:
            data = {
                'session_start': self.session_start,
                'last_updated': datetime.now().isoformat(),
                'messages': self.messages
            }
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            with open(HISTORY_FILE, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Could not save history: {e}")

    def add_message(self, role, content):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.messages) > self.MAX_HISTORY_MESSAGES:
            self.messages = self.messages[-self.MAX_HISTORY_MESSAGES:]

    def get_context(self):
        """Get messages formatted for API (without timestamps)."""
        return [{"role": m["role"], "content": m["content"]} for m in self.messages]

    def add_messages(self, messages):
        """Add multiple messages to the conversation history."""
        for message in messages:
            self.add_message(message["role"], message["content"])

    def clear(self):
        """Clear current session memory."""
        self.messages = []
        print("🧹 Memory cleared!")

    def get_formatted_history(self):
        """Get a formatted string of conversation history."""
        if not self.messages:
            return "📭 No conversation history yet."
        output = "📜 Conversation History:\n" + "="*50 + "\n"
        for i, msg in enumerate(self.messages, 1):
            role_emoji = "👤" if msg["role"] == "user" else "🤖"
            content_preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            output += f"\n{role_emoji} {msg['role'].upper()}: {content_preview}\n"
        return output

    def update_context(self, context):
        """Update conversation context with new information."""
        if "messages" in context:
            self.add_messages(context["messages"])

# create a single memory instance to import elsewhere
memory = ConversationMemory()
