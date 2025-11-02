"""
Tests for call evaluation and scoring logic.

Tests the CallQAAgent scoring methods with various transcript scenarios.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from core.database import create_call, add_transcript, create_score, get_or_create_agent
from agents.call_qa_agent import CallQAAgent
from core.llm import OpenRouterLLM
from core.memory import ConversationMemory
from tests.conftest import sample_transcript_segments, poor_quality_transcript, sample_scenario


class TestCallQAAgent:
    """Tests for CallQAAgent evaluation methods."""
    
    @pytest.fixture
    def agent(self, mock_llm, mock_memory):
        """Create CallQAAgent instance for testing."""
        return CallQAAgent(mock_llm, mock_memory)
    
    def test_score_greeting_excellent(self, agent, test_db):
        """Test greeting score with excellent greeting."""
        call = create_call(phone_number="+1234567890")
        
        transcripts = [
            MagicMock(speaker="agent", text="Hello, thank you for calling ABC Company. This is Sarah speaking. How can I help you today?"),
            MagicMock(speaker="customer", text="Hi, I need help")
        ]
        
        score = agent._score_greeting(transcripts, call, None)
        
        assert score >= 9.0  # Should be high with company name + agent name + greeting
    
    def test_score_greeting_good(self, agent, test_db):
        """Test greeting score with good greeting."""
        call = create_call(phone_number="+1234567890")
        
        transcripts = [
            MagicMock(speaker="agent", text="Hello, thank you for calling. How can I help?"),
            MagicMock(speaker="customer", text="Hi")
        ]
        
        score = agent._score_greeting(transcripts, call, None)
        
        assert 5.0 <= score <= 9.0  # Should be medium-high
    
    def test_score_greeting_poor(self, agent, test_db):
        """Test greeting score with poor greeting."""
        call = create_call(phone_number="+1234567890")
        
        transcripts = [
            MagicMock(speaker="agent", text="Yeah?"),
            MagicMock(speaker="customer", text="Hi")
        ]
        
        score = agent._score_greeting(transcripts, call, None)
        
        assert score < 5.0  # Should be low
    
    def test_score_hold_time_excellent(self, agent, test_db):
        """Test hold time score with minimal hold time."""
        call = create_call(phone_number="+1234567890")
        
        # Create proper mock objects with timestamp attribute set correctly
        transcript1 = MagicMock()
        transcript1.speaker = "agent"
        transcript1.text = "One moment please, let me check that."
        transcript1.timestamp = 1.0
        
        transcript2 = MagicMock()
        transcript2.speaker = "agent"
        transcript2.text = "Thank you for holding."
        transcript2.timestamp = 25.0  # 24 second gap
        
        transcript3 = MagicMock()
        transcript3.speaker = "customer"
        transcript3.text = "Okay"
        transcript3.timestamp = 26.0
        
        transcripts = [transcript1, transcript2, transcript3]
        
        score = agent._score_hold_time(transcripts, call)
        
        assert score >= 8.0  # Should be high with short hold and explanation
    
    def test_score_hold_time_long(self, agent, test_db):
        """Test hold time score with long hold."""
        call = create_call(phone_number="+1234567890")
        
        # Create proper mock objects with timestamp attribute set correctly
        transcript1 = MagicMock()
        transcript1.speaker = "agent"
        transcript1.text = "Hold on."
        transcript1.timestamp = 1.0
        
        transcript2 = MagicMock()
        transcript2.speaker = "agent"
        transcript2.text = "Still working on it."
        transcript2.timestamp = 150.0  # 149 second gap
        
        transcript3 = MagicMock()
        transcript3.speaker = "customer"
        transcript3.text = "Okay"
        transcript3.timestamp = 151.0
        
        transcripts = [transcript1, transcript2, transcript3]
        
        score = agent._score_hold_time(transcripts, call)
        
        assert score < 5.0  # Should be low with long hold
    
    def test_score_resolution_excellent(self, agent, test_db):
        """Test resolution score with complete resolution."""
        call = create_call(phone_number="+1234567890")
        
        transcripts = [
            MagicMock(speaker="agent", text="I've processed your cancellation. Your confirmation number is CAN-12345. Is there anything else?"),
            MagicMock(speaker="customer", text="No, thanks")
        ]
        
        score = agent._score_resolution(transcripts, call, None)
        
        assert score >= 9.0  # Should be high with resolution + confirmation
    
    def test_score_resolution_partial(self, agent, test_db):
        """Test resolution score with partial resolution."""
        call = create_call(phone_number="+1234567890")
        
        transcripts = [
            MagicMock(speaker="agent", text="I'll need to call you back about this."),
            MagicMock(speaker="customer", text="Okay")
        ]
        
        score = agent._score_resolution(transcripts, call, None)
        
        assert 4.0 <= score <= 7.0  # Should be medium (partial resolution)
    
    def test_score_tone_with_llm(self, agent, test_db):
        """Test tone score using LLM."""
        call = create_call(phone_number="+1234567890")
        
        transcripts = [
            MagicMock(speaker="agent", text="Thank you so much for calling! I really appreciate your patience. I'm so sorry to hear about this issue. Let me help you right away."),
            MagicMock(speaker="customer", text="Thanks")
        ]
        
        # Mock LLM to return high tone score
        agent.llm.generate_response.return_value = "9.5"
        
        score = agent._score_tone(transcripts, "full transcript text")
        
        assert score >= 9.0  # Should be high with empathetic language
    
    def test_score_tone_fallback(self, agent, test_db):
        """Test tone score fallback when LLM fails."""
        call = create_call(phone_number="+1234567890")
        
        transcripts = [
            MagicMock(speaker="agent", text="Thank you please sorry appreciate help happy"),
            MagicMock(speaker="customer", text="Thanks")
        ]
        
        # Mock LLM to raise exception
        agent.llm.generate_response.side_effect = Exception("API Error")
        
        score = agent._score_tone(transcripts, "full transcript text")
        
        # Should use fallback keyword-based scoring
        assert 0.0 <= score <= 10.0
    
    def test_score_compliance_excellent(self, agent, test_db, sample_scenario):
        """Test compliance score with all requirements met."""
        call = create_call(phone_number="+1234567890")
        
        transcripts = [
            MagicMock(speaker="agent", text="Hello, thank you for calling ABC Company. This is Sarah."),  # greeting
            MagicMock(speaker="agent", text="May I ask why you're canceling?"),  # retention attempt
            MagicMock(speaker="agent", text="Here's the cancellation process..."),  # process
            MagicMock(speaker="agent", text="Your confirmation number is CAN-12345.")  # confirmation
        ]
        
        score = agent._score_compliance(transcripts, sample_scenario)
        
        assert score >= 9.0  # Should be high with all elements present
    
    def test_score_compliance_partial(self, agent, test_db, sample_scenario):
        """Test compliance score with partial requirements."""
        call = create_call(phone_number="+1234567890")
        
        transcripts = [
            MagicMock(speaker="agent", text="Hello"),  # Only greeting
            MagicMock(speaker="agent", text="I'll process your cancellation.")
        ]
        
        score = agent._score_compliance(transcripts, sample_scenario)
        
        assert 0.0 <= score <= 5.0  # Should be low with few elements
    
    def test_calculate_weighted_score(self, agent):
        """Test weighted score calculation."""
        scores = {
            "greeting": 10.0,
            "hold_time": 8.0,
            "resolution": 9.0,
            "tone": 7.0,
            "compliance": 8.0
        }
        
        weights = {
            "greeting": 1.0,
            "hold_time": 0.5,
            "resolution": 2.0,
            "tone": 1.5,
            "compliance": 1.0
        }
        
        total = agent._calculate_weighted_score(scores, weights)
        
        # Manual calculation:
        # (10*1 + 8*0.5 + 9*2 + 7*1.5 + 8*1) / (1+0.5+2+1.5+1)
        # = (10 + 4 + 18 + 10.5 + 8) / 6 = 50.5 / 6 ≈ 8.42
        assert 8.0 <= total <= 9.0
    
    def test_generate_recommendations(self, agent, test_db, sample_transcript_segments):
        """Test recommendation generation."""
        call = create_call(phone_number="+1234567890")
        
        transcripts = [
            MagicMock(speaker="agent", text="Yeah?"),  # Poor greeting
            MagicMock(speaker="agent", text="I'll call you back.")  # No resolution
        ]
        
        scores = {
            "greeting": 2.0,  # Low
            "hold_time": 5.0,  # Medium
            "resolution": 3.0,  # Low
            "tone": 6.0,  # Medium
            "compliance": 4.0  # Low
        }
        
        recommendations = agent._generate_recommendations(scores, transcripts, None)
        
        assert len(recommendations) > 0
        assert any("greeting" in rec.lower() for rec in recommendations)
        assert any("resolution" in rec.lower() for rec in recommendations)
    
    def test_evaluate_call_full_workflow(self, agent, test_db, sample_transcript_segments, sample_scenario):
        """Test complete evaluation workflow."""
        # Create call with transcripts
        call = create_call(
            phone_number="+1234567890",
            scenario_id="cancel_subscription"
        )
        
        for segment in sample_transcript_segments:
            add_transcript(
                call_id=call.id,
                speaker=segment["speaker"],
                text=segment["text"],
                timestamp=segment["timestamp"],
                confidence=segment["confidence"]
            )
        
        # Mock scenario loading
        with patch.object(agent, '_load_scenario', return_value=sample_scenario):
            # Mock LLM for tone scoring
            agent.llm.generate_response.return_value = "8.5"
            
            result = agent.evaluate_call(call.id, "cancel_subscription")
            
            assert "error" not in result
            assert "scores" in result
            assert "total" in result
            assert "recommendations" in result
            
            assert result["total"] > 0
            assert len(result["scores"]) == 5
            assert len(result["recommendations"]) > 0
            
            # Verify score was saved to database
            from core.database import get_score
            saved_score = get_score(call.id)
            assert saved_score is not None
            assert saved_score.total == result["total"]
    
    def test_evaluate_call_missing_call(self, agent, test_db):
        """Test evaluation with non-existent call."""
        result = agent.evaluate_call(99999)
        
        assert "error" in result
    
    def test_evaluate_call_no_transcripts(self, agent, test_db):
        """Test evaluation with no transcripts."""
        call = create_call(phone_number="+1234567890")
        
        result = agent.evaluate_call(call.id)
        
        assert "error" in result

