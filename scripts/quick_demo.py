#!/usr/bin/env python3
"""
Quick non-interactive demo of Call QA Tool.

Run this to see the tool in action without any prompts.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.database import init_db, create_call, add_transcript, update_call
from core.config import load_config
from core.llm import OpenRouterLLM
from core.memory import ConversationMemory
from agents.call_qa_agent import CallQAAgent


def main():
    print("🚀 Call QA Tool - Quick Demo\n")
    
    # Initialize
    init_db()
    config = load_config()
    llm = OpenRouterLLM(api_key=config.api_key)
    memory = ConversationMemory()
    agent = CallQAAgent(llm, memory)
    
    # Create call
    print("📞 Creating test call...")
    call = create_call(
        phone_number="+1234567890",
        status="completed",
        scenario_id="cancel_subscription"
    )
    print(f"   ✅ Call #{call.id} created\n")
    
    # Add transcripts
    print("📝 Adding transcript...")
    transcripts = [
        ("customer", "Hi, I'd like to cancel my subscription please.", 1.5),
        ("agent", "Hello, thank you for calling ABC Company. This is Sarah. I'd be happy to help you with that. May I have your account number?", 5.2),
        ("customer", "Sure, it's 12345678.", 12.8),
        ("agent", "Thank you. I'm sorry to hear you want to cancel. May I ask what led to this decision?", 18.5),
        ("customer", "I'm just not using the service anymore.", 28.3),
        ("agent", "I understand. I've processed the cancellation. Your confirmation number is CAN-12345. Is there anything else?", 35.1),
        ("customer", "No, that's all. Thank you.", 52.7),
        ("agent", "You're welcome. Have a great day!", 55.2)
    ]
    
    for speaker, text, timestamp in transcripts:
        add_transcript(call.id, speaker, text, timestamp, 0.95)
    
    print(f"   ✅ {len(transcripts)} segments added\n")
    
    # Update call duration
    update_call(call.id, duration=56, cost=0.05)
    
    # Evaluate
    print("🤖 Evaluating call with AI...")
    result = agent.evaluate_call(call.id, "cancel_subscription")
    
    if "error" in result:
        print(f"   ❌ Error: {result['error']}\n")
        return
    
    # Display results
    print("\n" + "="*60)
    print("📊 EVALUATION RESULTS")
    print("="*60)
    
    scores = result["scores"]
    print(f"\nGreeting:    {scores['greeting']:.1f}/10")
    print(f"Hold Time:   {scores['hold_time']:.1f}/10")
    print(f"Resolution:  {scores['resolution']:.1f}/10")
    print(f"Tone:        {scores['tone']:.1f}/10")
    print(f"Compliance:  {scores['compliance']:.1f}/10")
    print(f"\n🎯 TOTAL SCORE: {result['total']:.1f}/10")
    
    if result['recommendations']:
        print("\n💡 Recommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    print(f"\n✅ Demo complete! Call #{call.id} saved to database.")
    print("\n📊 To view in dashboard, run:")
    print("   streamlit run streamlit_pages/call_qa_dashboard.py")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

