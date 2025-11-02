#!/usr/bin/env python3
"""
Quick setup script for Call QA Tool demo.

This script creates sample calls with different quality levels
so you can see the dashboard in action immediately.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from core.database import init_db, create_call, add_transcript, update_call
from core.config import load_config
from core.llm import OpenRouterLLM
from core.memory import ConversationMemory
from agents.call_qa_agent import CallQAAgent


def create_excellent_call():
    """Create a call with excellent scores."""
    print("📞 Creating excellent quality call...")
    
    call = create_call(
        phone_number="+15551111111",
        status="completed",
        scenario_id="cancel_subscription"
    )
    
    transcripts = [
        ("customer", "Hi, I'd like to cancel my subscription please.", 1.5),
        ("agent", "Hello, thank you for calling ABC Company. This is Sarah. I'd be happy to help you with that. May I have your account number?", 5.2),
        ("customer", "Sure, it's 12345678.", 12.8),
        ("agent", "Thank you. I'm sorry to hear you want to cancel. May I ask what led to this decision?", 18.5),
        ("customer", "I'm just not using the service anymore.", 28.3),
        ("agent", "I understand. I've processed your cancellation. Your confirmation number is CAN-12345. Is there anything else?", 35.1),
        ("customer", "No, that's all. Thank you.", 52.7),
        ("agent", "You're welcome. Have a great day!", 55.2)
    ]
    
    for speaker, text, timestamp in transcripts:
        add_transcript(call.id, speaker, text, timestamp, 0.95)
    
    update_call(call.id, duration=56, cost=0.05)
    
    # Evaluate
    config = load_config()
    llm = OpenRouterLLM(api_key=config.api_key)
    memory = ConversationMemory()
    agent = CallQAAgent(llm, memory)
    result = agent.evaluate_call(call.id, "cancel_subscription")
    
    print(f"   ✅ Call #{call.id} - Score: {result['total']:.1f}/10")
    return call.id


def create_average_call():
    """Create a call with average scores."""
    print("📞 Creating average quality call...")
    
    call = create_call(
        phone_number="+15552222222",
        status="completed",
        scenario_id="cancel_subscription"
    )
    
    transcripts = [
        ("customer", "I want to cancel.", 1.0),
        ("agent", "Hello, can I have your account number?", 5.0),
        ("customer", "12345678", 10.0),
        ("agent", "Hold on, let me check.", 12.0),
        ("agent", "Okay, I can cancel that for you.", 45.0),  # Long hold
        ("customer", "Thanks", 50.0),
    ]
    
    for speaker, text, timestamp in transcripts:
        add_transcript(call.id, speaker, text, timestamp, 0.85)
    
    update_call(call.id, duration=50, cost=0.04)
    
    # Evaluate
    config = load_config()
    llm = OpenRouterLLM(api_key=config.api_key)
    memory = ConversationMemory()
    agent = CallQAAgent(llm, memory)
    result = agent.evaluate_call(call.id, "cancel_subscription")
    
    print(f"   ✅ Call #{call.id} - Score: {result['total']:.1f}/10")
    return call.id


def create_poor_call():
    """Create a call with poor scores."""
    print("📞 Creating poor quality call...")
    
    call = create_call(
        phone_number="+15553333333",
        status="completed",
        scenario_id="cancel_subscription"
    )
    
    transcripts = [
        ("customer", "Cancel subscription.", 1.0),
        ("agent", "What?", 10.0),  # Poor greeting, long gap
        ("customer", "I want to cancel.", 15.0),
        ("agent", "I can't do that right now. You'll need to call back later.", 30.0),
    ]
    
    for speaker, text, timestamp in transcripts:
        add_transcript(call.id, speaker, text, timestamp, 0.60)
    
    update_call(call.id, duration=30, cost=0.02)
    
    # Evaluate
    config = load_config()
    llm = OpenRouterLLM(api_key=config.api_key)
    memory = ConversationMemory()
    agent = CallQAAgent(llm, memory)
    result = agent.evaluate_call(call.id, "cancel_subscription")
    
    print(f"   ✅ Call #{call.id} - Score: {result['total']:.1f}/10")
    return call.id


def main():
    print("=" * 60)
    print("🚀 Call QA Tool - Demo Data Setup")
    print("=" * 60)
    print()
    
    # Initialize database
    print("📦 Initializing database...")
    init_db()
    print("   ✅ Database ready\n")
    
    # Create sample calls
    print("Creating sample calls with different quality levels...\n")
    
    try:
        call1 = create_excellent_call()
        call2 = create_average_call()
        call3 = create_poor_call()
        
        print("\n" + "=" * 60)
        print("✅ Demo data created successfully!")
        print("=" * 60)
        print(f"\n📊 Created {3} test calls:")
        print(f"   - Call #{call1}: Excellent quality")
        print(f"   - Call #{call2}: Average quality")
        print(f"   - Call #{call3}: Poor quality")
        
        print("\n🎯 Next Steps:")
        print("   1. Run the dashboard:")
        print("      python -m streamlit run streamlit_pages/call_qa_dashboard.py")
        print("\n   2. Open http://localhost:8501 in your browser")
        print("\n   3. Navigate to 'Call History' to see all calls")
        print("   4. Click on any call to see detailed scores and transcript")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

