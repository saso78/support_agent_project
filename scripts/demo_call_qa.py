#!/usr/bin/env python3
"""
Demo script to show Call QA Tool in action.

This script demonstrates the full workflow:
1. Creates a test call
2. Adds mock transcripts
3. Evaluates the call
4. Displays results
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.database import init_db, create_call, add_transcript, create_score
from core.config import load_config
from core.llm import OpenRouterLLM
from core.memory import ConversationMemory
from agents.call_qa_agent import CallQAAgent
import json


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_section(text: str):
    """Print a section header."""
    print(f"\n{'─' * 60}")
    print(f"  {text}")
    print(f"{'─' * 60}")


def demo_call_qa():
    """Run a complete Call QA demonstration."""
    print_header("Call QA Tool - Interactive Demo")
    
    print("\n📞 This demo will:")
    print("  1. Create a test call record")
    print("  2. Add transcript segments")
    print("  3. Evaluate the call using AI scoring")
    print("  4. Display detailed results")
    
    print("\n⏳ Starting demo...")
    
    # Initialize database
    print_section("Initializing Database")
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️  Database already exists or error: {e}")
    
    # Create a test call
    print_section("Step 1: Creating Test Call")
    call = create_call(
        phone_number="+1234567890",
        status="completed",
        scenario_id="cancel_subscription"
    )
    print(f"✅ Created call #{call.id}")
    print(f"   Phone: {call.phone_number}")
    print(f"   Scenario: {call.scenario_id}")
    print(f"   Status: {call.status}")
    
    # Add transcript segments
    print_section("Step 2: Adding Call Transcript")
    
    transcript_segments = [
        {
            "speaker": "customer",
            "text": "Hi, I'd like to cancel my subscription please.",
            "timestamp": 1.5,
            "confidence": 0.95
        },
        {
            "speaker": "agent",
            "text": "Hello, thank you for calling ABC Company. This is Sarah. I'd be happy to help you with that. May I have your account number?",
            "timestamp": 5.2,
            "confidence": 0.92
        },
        {
            "speaker": "customer",
            "text": "Sure, it's 12345678.",
            "timestamp": 12.8,
            "confidence": 0.88
        },
        {
            "speaker": "agent",
            "text": "Thank you. I can see your account. I'm sorry to hear you want to cancel. May I ask what led to this decision?",
            "timestamp": 18.5,
            "confidence": 0.94
        },
        {
            "speaker": "customer",
            "text": "I'm just not using the service anymore.",
            "timestamp": 28.3,
            "confidence": 0.90
        },
        {
            "speaker": "agent",
            "text": "I understand. Well, I've processed the cancellation. Your subscription will end at the end of this billing cycle. Your cancellation confirmation number is CAN-12345. Is there anything else I can help you with today?",
            "timestamp": 35.1,
            "confidence": 0.93
        },
        {
            "speaker": "customer",
            "text": "No, that's all. Thank you.",
            "timestamp": 52.7,
            "confidence": 0.91
        },
        {
            "speaker": "agent",
            "text": "You're welcome. Have a great day!",
            "timestamp": 55.2,
            "confidence": 0.96
        }
    ]
    
    for i, segment in enumerate(transcript_segments, 1):
        add_transcript(
            call_id=call.id,
            speaker=segment["speaker"],
            text=segment["text"],
            timestamp=segment["timestamp"],
            confidence=segment["confidence"]
        )
        print(f"  {i}. [{segment['speaker'].upper():8}] ({segment['timestamp']:5.1f}s): {segment['text'][:60]}...")
    
    print(f"\n✅ Added {len(transcript_segments)} transcript segments")
    
    # Initialize evaluation agent
    print_section("Step 3: Initializing AI Evaluation Agent")
    try:
        config = load_config()
        llm = OpenRouterLLM(api_key=config.api_key)
        memory = ConversationMemory()
        agent = CallQAAgent(llm, memory)
        print("✅ Call QA Agent initialized")
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        print("   (Make sure OPENROUTER_API_KEY is set in .env)")
        return
    
    # Evaluate the call
    print_section("Step 4: Evaluating Call Performance")
    print("   Analyzing transcript and calculating scores...\n")
    
    try:
        evaluation = agent.evaluate_call(call.id, "cancel_subscription")
        
        if "error" in evaluation:
            print(f"❌ Evaluation failed: {evaluation['error']}")
            return
        
        # Display scores
        print_header("📊 Evaluation Results")
        
        scores = evaluation["scores"]
        total = evaluation["total"]
        
        print("\n📈 Individual Scores (out of 10):")
        print(f"   {'Greeting:':<15} {scores['greeting']:>5.1f}/10  {'⭐' * int(scores['greeting'])}")
        print(f"   {'Hold Time:':<15} {scores['hold_time']:>5.1f}/10  {'⭐' * int(scores['hold_time'])}")
        print(f"   {'Resolution:':<15} {scores['resolution']:>5.1f}/10  {'⭐' * int(scores['resolution'])}")
        print(f"   {'Tone/Empathy:':<15} {scores['tone']:>5.1f}/10  {'⭐' * int(scores['tone'])}")
        print(f"   {'Compliance:':<15} {scores['compliance']:>5.1f}/10  {'⭐' * int(scores['compliance'])}")
        
        print(f"\n🎯 Overall Score: {total:.1f}/10")
        
        if total >= 9.0:
            rating = "🌟 Excellent"
        elif total >= 7.0:
            rating = "✅ Good"
        elif total >= 5.0:
            rating = "⚠️  Needs Improvement"
        else:
            rating = "❌ Poor"
        
        print(f"   Rating: {rating}")
        
        # Display recommendations
        if evaluation.get("recommendations"):
            print_section("💡 Recommendations")
            for i, rec in enumerate(evaluation["recommendations"], 1):
                print(f"   {i}. {rec}")
        
        # Show transcript summary
        print_section("📝 Call Summary")
        print(f"   Call ID: {call.id}")
        print(f"   Duration: ~{transcript_segments[-1]['timestamp']:.0f} seconds")
        print(f"   Total Messages: {len(transcript_segments)}")
        print(f"   Agent Messages: {sum(1 for s in transcript_segments if s['speaker'] == 'agent')}")
        print(f"   Customer Messages: {sum(1 for s in transcript_segments if s['speaker'] == 'customer')}")
        
        print_section("✅ Demo Complete!")
        print("\n📊 You can view this call in the dashboard:")
        print("   streamlit run streamlit_pages/call_qa_dashboard.py")
        print("\n💾 Call data saved to: data/call_logs/call_qa.db")
        
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        demo_call_qa()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()

