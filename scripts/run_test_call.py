#!/usr/bin/env python3
"""
CLI script to run a test call for Call QA Tool.

Usage:
    python scripts/run_test_call.py --scenario cancel_subscription --phone +1234567890
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.database import init_db, create_call, get_transcripts, add_transcript, create_score
from core.config import load_config
from core.llm import OpenRouterLLM
from core.memory import ConversationMemory
from agents.call_qa_agent import CallQAAgent
from core.voice import VoiceEngine
from core.transcription import TranscriptionEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_scenario(scenario_id: str) -> dict:
    """Load scenario from JSON file."""
    scenario_path = Path("data/call_scenarios") / f"{scenario_id}.json"
    
    if not scenario_path.exists():
        logger.error(f"Scenario not found: {scenario_id}")
        sys.exit(1)
    
    with open(scenario_path, 'r') as f:
        return json.load(f)


def make_test_call(
    agent_phone: str,
    agent_name: str,
    scenario_id: str,
    use_mock: bool = True
) -> int:
    """
    Make a test call and return call ID.
    
    Args:
        agent_phone: Agent phone number (E.164 format)
        agent_name: Agent name
        scenario_id: Scenario identifier
        use_mock: Whether to use mock APIs
        
    Returns:
        Call ID
    """
    logger.info(f"Starting test call to {agent_phone} using scenario {scenario_id}")
    
    # Initialize database
    init_db()
    
    # Load scenario
    scenario = load_scenario(scenario_id)
    logger.info(f"Loaded scenario: {scenario['name']}")
    
    # Create call record
    call = create_call(
        phone_number=agent_phone,
        status="initiated",
        scenario_id=scenario_id
    )
    logger.info(f"Created call record: #{call.id}")
    
    # Initialize engines
    voice_engine = VoiceEngine(use_mock=use_mock)
    transcription_engine = TranscriptionEngine(use_mock=use_mock)
    
    # For MVP with mock mode, simulate the call
    if use_mock:
        logger.info("Using MOCK mode - simulating call")
        
        # Simulate call duration
        call_duration = 120  # 2 minutes
        
        # Generate mock transcript
        logger.info("Generating mock transcript...")
        mock_transcript = transcription_engine.transcribe_audio_file("mock_audio.wav")
        
        if mock_transcript:
            # Save transcripts
            for segment in mock_transcript:
                add_transcript(
                    call_id=call.id,
                    speaker=segment["speaker"],
                    text=segment["text"],
                    timestamp=segment["timestamp"],
                    confidence=segment.get("confidence", 1.0)
                )
            
            logger.info(f"Saved {len(mock_transcript)} transcript segments")
        
        # Update call status
        from core.database import update_call
        text_length = sum(len(line) for line in scenario["customer_script"])
        estimated_cost = voice_engine.calculate_cost(call_duration, text_length)
        
        update_call(
            call_id=call.id,
            duration=call_duration,
            status="completed",
            cost=estimated_cost
        )
        
        logger.info(f"Call completed: {call_duration}s, Cost: ${estimated_cost:.4f}")
        
        # Evaluate call
        logger.info("Evaluating call...")
        config = load_config()
        llm = OpenRouterLLM(api_key=config.api_key)
        memory = ConversationMemory()
        agent = CallQAAgent(llm, memory)
        
        evaluation = agent.evaluate_call(call.id, scenario_id)
        
        if "error" not in evaluation:
            logger.info(f"Evaluation complete: Total score = {evaluation['total']:.1f}/10")
            logger.info("Scores:")
            for metric, score in evaluation["scores"].items():
                logger.info(f"  {metric}: {score:.1f}")
            
            if evaluation.get("recommendations"):
                logger.info("Recommendations:")
                for rec in evaluation["recommendations"]:
                    logger.info(f"  - {rec}")
        else:
            logger.error(f"Evaluation failed: {evaluation['error']}")
    
    else:
        # Real API mode (for production)
        logger.info("Making real call via Twilio...")
        
        # Create TwiML for call
        twiml = voice_engine.create_twiml_for_call(scenario["customer_script"])
        
        # Make call
        call_result = voice_engine.make_call(
            to_phone=agent_phone,
            twiml_instructions=twiml
        )
        
        if call_result:
            logger.info(f"Call initiated: {call_result['sid']}")
            logger.info("Waiting for call to complete...")
            # In production, you would wait for the call to complete
            # and then transcribe the recording
        else:
            logger.error("Failed to initiate call")
            from core.database import update_call
            update_call(call.id, status="failed")
    
    return call.id


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Make a test call for Call QA Tool"
    )
    parser.add_argument(
        "--scenario",
        required=True,
        help="Scenario ID (e.g., cancel_subscription)"
    )
    parser.add_argument(
        "--phone",
        required=True,
        help="Agent phone number (E.164 format, e.g., +1234567890)"
    )
    parser.add_argument(
        "--name",
        default="Test Agent",
        help="Agent name (default: Test Agent)"
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Use real APIs (default: mock mode)"
    )
    
    args = parser.parse_args()
    
    try:
        call_id = make_test_call(
            agent_phone=args.phone,
            agent_name=args.name,
            scenario_id=args.scenario,
            use_mock=not args.real
        )
        
        print(f"\n✅ Test call completed successfully!")
        print(f"   Call ID: {call_id}")
        print(f"   View results in dashboard or database")
        print(f"   Run: streamlit run streamlit_pages/call_qa_dashboard.py")
        
    except Exception as e:
        logger.error(f"Failed to make test call: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

