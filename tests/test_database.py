"""
Tests for database operations (CRUD operations).

Tests all database functions with a test database.
"""

import pytest
from datetime import datetime
from core.database import (
    init_db,
    create_call,
    update_call,
    get_call,
    get_calls,
    add_transcript,
    get_transcripts,
    create_score,
    get_score,
    get_or_create_agent,
    update_agent_stats,
    get_agents,
    get_call_summary,
    get_agent_performance
)
from core.models import Call, Transcript, Score, Agent
from tests.conftest import sample_call_data, sample_transcript_segments


class TestCallOperations:
    """Tests for call CRUD operations."""
    
    def test_create_call(self, test_db):
        """Test creating a new call record."""
        call = create_call(
            phone_number="+1234567890",
            status="initiated",
            scenario_id="cancel_subscription"
        )
        
        assert call.id is not None
        assert call.phone_number == "+1234567890"
        assert call.status == "initiated"
        assert call.scenario_id == "cancel_subscription"
        assert call.cost == 0.0
        assert call.duration == 0
    
    def test_get_call(self, test_db):
        """Test retrieving a call by ID."""
        call = create_call(
            phone_number="+1234567890",
            status="completed"
        )
        
        retrieved = get_call(call.id)
        assert retrieved is not None
        assert retrieved.id == call.id
        assert retrieved.phone_number == call.phone_number
    
    def test_update_call(self, test_db):
        """Test updating call information."""
        call = create_call(
            phone_number="+1234567890",
            status="initiated"
        )
        
        updated = update_call(
            call_id=call.id,
            duration=120,
            status="completed",
            cost=0.05
        )
        
        assert updated is not None
        assert updated.duration == 120
        assert updated.status == "completed"
        assert updated.cost == 0.05
    
    def test_get_calls_with_filters(self, test_db):
        """Test getting calls with various filters."""
        # Create test calls
        call1 = create_call(phone_number="+1111111111", status="completed")
        call2 = create_call(phone_number="+2222222222", status="failed")
        call3 = create_call(phone_number="+1111111111", status="completed")
        
        # Filter by status
        completed_calls = get_calls(status="completed")
        assert len(completed_calls) >= 2
        assert all(c.status == "completed" for c in completed_calls)
        
        # Filter by phone number
        phone_calls = get_calls(phone_number="+1111111111")
        assert len(phone_calls) >= 2
        assert all(c.phone_number == "+1111111111" for c in phone_calls)
    
    def test_get_call_not_found(self, test_db):
        """Test getting a non-existent call."""
        call = get_call(99999)
        assert call is None


class TestTranscriptOperations:
    """Tests for transcript CRUD operations."""
    
    def test_add_transcript(self, test_db):
        """Test adding transcript segments."""
        call = create_call(phone_number="+1234567890")
        
        transcript = add_transcript(
            call_id=call.id,
            speaker="agent",
            text="Hello, how can I help you?",
            timestamp=1.5,
            confidence=0.95
        )
        
        assert transcript.id is not None
        assert transcript.call_id == call.id
        assert transcript.speaker == "agent"
        assert transcript.text == "Hello, how can I help you?"
        assert transcript.timestamp == 1.5
        assert transcript.confidence == 0.95
    
    def test_get_transcripts(self, test_db, sample_transcript_segments):
        """Test retrieving all transcripts for a call."""
        call = create_call(phone_number="+1234567890")
        
        # Add multiple transcript segments
        for segment in sample_transcript_segments:
            add_transcript(
                call_id=call.id,
                speaker=segment["speaker"],
                text=segment["text"],
                timestamp=segment["timestamp"],
                confidence=segment["confidence"]
            )
        
        transcripts = get_transcripts(call.id)
        assert len(transcripts) == len(sample_transcript_segments)
        assert transcripts[0].speaker == "customer"
        assert transcripts[1].speaker == "agent"


class TestScoreOperations:
    """Tests for score CRUD operations."""
    
    def test_create_score(self, test_db):
        """Test creating a score record."""
        call = create_call(phone_number="+1234567890")
        
        recommendations = [
            "Great job!",
            "Keep up the good work."
        ]
        
        score = create_score(
            call_id=call.id,
            greeting=10.0,
            hold_time=9.0,
            resolution=10.0,
            tone=8.5,
            compliance=9.0,
            total=9.3,
            recommendations=recommendations
        )
        
        assert score.id is not None
        assert score.call_id == call.id
        assert score.greeting == 10.0
        assert score.total == 9.3
    
    def test_get_score(self, test_db):
        """Test retrieving a score."""
        call = create_call(phone_number="+1234567890")
        
        create_score(
            call_id=call.id,
            greeting=10.0,
            hold_time=9.0,
            resolution=10.0,
            tone=8.5,
            compliance=9.0,
            total=9.3,
            recommendations=[]
        )
        
        score = get_score(call.id)
        assert score is not None
        assert score.total == 9.3


class TestAgentOperations:
    """Tests for agent CRUD operations."""
    
    def test_get_or_create_agent_new(self, test_db):
        """Test creating a new agent."""
        agent = get_or_create_agent(
            name="John Doe",
            phone_number="+1234567890"
        )
        
        assert agent.id is not None
        assert agent.name == "John Doe"
        assert agent.phone_number == "+1234567890"
        assert agent.total_calls == 0
        assert agent.average_score == 0.0
    
    def test_get_or_create_agent_existing(self, test_db):
        """Test getting an existing agent."""
        agent1 = get_or_create_agent(
            name="John Doe",
            phone_number="+1234567890"
        )
        
        agent2 = get_or_create_agent(
            name="Jane Doe",  # Different name, but same phone
            phone_number="+1234567890"
        )
        
        assert agent1.id == agent2.id
        assert agent2.phone_number == "+1234567890"
    
    def test_update_agent_stats(self, test_db):
        """Test updating agent statistics."""
        agent = get_or_create_agent(
            name="John Doe",
            phone_number="+1234567890"
        )
        
        # Update with first call score
        update_agent_stats(agent.id, 8.0)
        
        # Retrieve updated agent (using get_agents to avoid session issues)
        agents = get_agents()
        updated_agent = next((a for a in agents if a.id == agent.id), None)
        
        assert updated_agent is not None
        assert updated_agent.total_calls == 1
        assert updated_agent.average_score == 8.0
        
        # Update with second call score
        update_agent_stats(agent.id, 9.0)
        
        # Retrieve again
        agents = get_agents()
        updated_agent = next((a for a in agents if a.id == agent.id), None)
        
        assert updated_agent is not None
        assert updated_agent.total_calls == 2
        assert updated_agent.average_score == 8.5  # (8.0 + 9.0) / 2
    
    def test_get_agents(self, test_db):
        """Test retrieving all agents."""
        agent1 = get_or_create_agent("Agent 1", "+1111111111")
        agent2 = get_or_create_agent("Agent 2", "+2222222222")
        
        # Update scores to test ordering
        update_agent_stats(agent1.id, 9.0)
        update_agent_stats(agent2.id, 8.0)
        
        agents = get_agents()
        assert len(agents) >= 2
        # Should be ordered by average_score desc
        assert agents[0].average_score >= agents[1].average_score


class TestQueryHelpers:
    """Tests for query helper functions."""
    
    def test_get_call_summary(self, test_db, sample_transcript_segments):
        """Test getting complete call summary."""
        call = create_call(phone_number="+1234567890")
        
        # Add transcripts
        for segment in sample_transcript_segments:
            add_transcript(
                call_id=call.id,
                speaker=segment["speaker"],
                text=segment["text"],
                timestamp=segment["timestamp"],
                confidence=segment["confidence"]
            )
        
        # Add score
        create_score(
            call_id=call.id,
            greeting=10.0,
            hold_time=9.0,
            resolution=10.0,
            tone=8.5,
            compliance=9.0,
            total=9.3,
            recommendations=["Great job!"]
        )
        
        summary = get_call_summary(call.id)
        
        assert summary is not None
        assert summary["call"]["id"] == call.id
        assert len(summary["transcript"]) == len(sample_transcript_segments)
        assert summary["score"]["total"] == 9.3
        assert len(summary["score"]["recommendations"]) == 1
    
    def test_get_agent_performance(self, test_db):
        """Test getting agent performance metrics."""
        agent = get_or_create_agent("Test Agent", "+1234567890")
        
        # Create calls with scores
        call1 = create_call(phone_number=agent.phone_number)
        create_score(call1.id, 10.0, 9.0, 10.0, 8.5, 9.0, 9.3, [])
        update_agent_stats(agent.id, 9.3)
        
        call2 = create_call(phone_number=agent.phone_number)
        create_score(call2.id, 8.0, 7.0, 8.0, 7.5, 8.0, 7.7, [])
        update_agent_stats(agent.id, 7.7)
        
        performance = get_agent_performance(agent.id, days=30)
        
        assert performance["agent_id"] == agent.id
        assert performance["total_calls"] == 2
        assert performance["average_score"] > 0
        assert len(performance["calls"]) == 2

