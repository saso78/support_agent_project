"""
Pytest fixtures for Call QA Tool tests.

Provides shared test data, database fixtures, and mock setups.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add project root to path
import sys
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.database import init_db, SessionLocal, engine, Base, get_session
from core.models import Call, Transcript, Score, Agent
from core.llm import OpenRouterLLM
from core.memory import ConversationMemory


@pytest.fixture(scope="function")
def test_db(monkeypatch):
    """
    Create a temporary test database for each test.
    
    Uses a temporary database file and ensures cleanup.
    Note: Tests should use the database CRUD functions, not direct session access.
    """
    import tempfile
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Create temporary database
    test_db_path = tempfile.mktemp(suffix='.db')
    
    # Create test engine
    test_engine = create_engine(f'sqlite:///{test_db_path}', connect_args={'check_same_thread': False})
    Base.metadata.create_all(test_engine)
    
    # Create session
    TestSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)
    session = TestSessionLocal()
    
    # Monkeypatch get_session to return our test session
    from core import database
    original_get_session = database.get_session
    monkeypatch.setattr(database, 'get_session', lambda: session)
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass
    
    # Restore original (monkeypatch should handle this, but just in case)
    monkeypatch.setattr(database, 'get_session', original_get_session)


@pytest.fixture
def sample_call_data():
    """Sample call data for testing."""
    return {
        "phone_number": "+1234567890",
        "duration": 120,
        "status": "completed",
        "cost": 0.05,
        "scenario_id": "cancel_subscription",
        "recording_path": "/fake/path/recording.mp3"
    }


@pytest.fixture
def sample_transcript_segments():
    """Sample transcript segments for testing."""
    return [
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


@pytest.fixture
def poor_quality_transcript():
    """Sample transcript with poor quality (low scores expected)."""
    return [
        {
            "speaker": "customer",
            "text": "I want to cancel.",
            "timestamp": 1.0,
            "confidence": 0.5
        },
        {
            "speaker": "agent",
            "text": "What?",
            "timestamp": 10.0,
            "confidence": 0.3
        },
        {
            "speaker": "customer",
            "text": "Cancel subscription.",
            "timestamp": 15.0,
            "confidence": 0.4
        },
        {
            "speaker": "agent",
            "text": "I can't do that right now. Call back later.",
            "timestamp": 30.0,
            "confidence": 0.6
        }
    ]


@pytest.fixture
def sample_scenario():
    """Sample scenario JSON data."""
    return {
        "id": "cancel_subscription",
        "name": "Cancel Subscription Request",
        "description": "Customer wants to cancel their subscription",
        "customer_script": [
            "Hi, I'd like to cancel my subscription please.",
            "I'm not using the service anymore.",
            "Yes, please proceed with the cancellation.",
            "Thank you."
        ],
        "expected_agent_behavior": {
            "greeting": "Should greet with company name and agent name",
            "retention_attempt": "Should ask why customer is canceling",
            "process": "Should explain cancellation process clearly",
            "confirmation": "Should provide cancellation confirmation number"
        },
        "scoring_weights": {
            "greeting": 1.0,
            "hold_time": 0.5,
            "resolution": 2.0,
            "tone": 1.5,
            "compliance": 1.0
        }
    }


@pytest.fixture
def mock_llm():
    """Mock OpenRouterLLM for testing."""
    llm = MagicMock(spec=OpenRouterLLM)
    llm.generate_response.return_value = "8.5"  # Default tone score
    return llm


@pytest.fixture
def mock_memory():
    """Mock ConversationMemory for testing."""
    return MagicMock(spec=ConversationMemory)


@pytest.fixture
def sample_scores():
    """Sample score data."""
    return {
        "greeting": 10.0,
        "hold_time": 9.0,
        "resolution": 10.0,
        "tone": 8.5,
        "compliance": 9.0,
        "total": 9.3
    }

