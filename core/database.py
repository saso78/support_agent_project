"""
Database operations for Call QA Tool.

Handles SQLite database initialization, CRUD operations, and query helpers.
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

from core.models import Base, Call, Transcript, Score, Agent
from core.config import get_secret

logger = logging.getLogger(__name__)

# Database configuration
CALL_QA_DB_DIR = os.path.join('data', 'call_logs')
CALL_QA_DB_PATH = os.path.join(CALL_QA_DB_DIR, 'call_qa.db')

# Ensure directory exists
os.makedirs(CALL_QA_DB_DIR, exist_ok=True)

# Database engine and session factory
engine = create_engine(
    f'sqlite:///{CALL_QA_DB_PATH}',
    connect_args={'check_same_thread': False},  # For SQLite threading
    echo=False  # Set to True for SQL query logging
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    Raises:
        SQLAlchemyError: If database initialization fails
    """
    try:
        Base.metadata.create_all(engine)
        logger.info(f"Database initialized at {CALL_QA_DB_PATH}")
    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_session() -> Session:
    """
    Get a database session.
    
    Returns:
        Database session
    """
    return SessionLocal()


# Call CRUD Operations

def create_call(
    phone_number: str,
    status: str = "initiated",
    scenario_id: Optional[str] = None,
    recording_path: Optional[str] = None
) -> Call:
    """
    Create a new call record.
    
    Args:
        phone_number: Agent phone number
        status: Call status (initiated, in-progress, completed, failed, timeout)
        scenario_id: Scenario identifier
        recording_path: Path to recording file
        
    Returns:
        Created Call object
        
    Raises:
        SQLAlchemyError: If creation fails
    """
    session = get_session()
    try:
        call = Call(
            phone_number=phone_number,
            status=status,
            scenario_id=scenario_id,
            recording_path=recording_path,
            cost=0.0,
            duration=0
        )
        session.add(call)
        session.commit()
        session.refresh(call)
        logger.info(f"Created call record: {call.id}")
        return call
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Failed to create call: {e}")
        raise
    finally:
        session.close()


def update_call(
    call_id: int,
    duration: Optional[int] = None,
    status: Optional[str] = None,
    cost: Optional[float] = None,
    recording_path: Optional[str] = None
) -> Optional[Call]:
    """
    Update an existing call record.
    
    Args:
        call_id: Call ID
        duration: Call duration in seconds
        status: Updated status
        cost: Estimated cost
        recording_path: Path to recording
        
    Returns:
        Updated Call object or None if not found
    """
    session = get_session()
    try:
        call = session.query(Call).filter(Call.id == call_id).first()
        if not call:
            logger.warning(f"Call {call_id} not found")
            return None
        
        if duration is not None:
            call.duration = duration
        if status is not None:
            call.status = status
        if cost is not None:
            call.cost = cost
        if recording_path is not None:
            call.recording_path = recording_path
        
        session.commit()
        session.refresh(call)
        logger.info(f"Updated call {call_id}")
        return call
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Failed to update call {call_id}: {e}")
        raise
    finally:
        session.close()


def get_call(call_id: int) -> Optional[Call]:
    """Get a call by ID."""
    session = get_session()
    try:
        return session.query(Call).filter(Call.id == call_id).first()
    finally:
        session.close()


def get_calls(
    limit: int = 100,
    status: Optional[str] = None,
    phone_number: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Call]:
    """
    Get calls with optional filtering.
    
    Args:
        limit: Maximum number of calls to return
        status: Filter by status
        phone_number: Filter by phone number
        start_date: Filter calls after this date
        end_date: Filter calls before this date
        
    Returns:
        List of Call objects
    """
    session = get_session()
    try:
        query = session.query(Call)
        
        if status:
            query = query.filter(Call.status == status)
        if phone_number:
            query = query.filter(Call.phone_number == phone_number)
        if start_date:
            query = query.filter(Call.timestamp >= start_date)
        if end_date:
            query = query.filter(Call.timestamp <= end_date)
        
        return query.order_by(Call.timestamp.desc()).limit(limit).all()
    finally:
        session.close()


# Transcript CRUD Operations

def add_transcript(
    call_id: int,
    speaker: str,
    text: str,
    timestamp: float,
    confidence: float = 1.0
) -> Transcript:
    """
    Add a transcript segment to a call.
    
    Args:
        call_id: Call ID
        speaker: 'agent' or 'customer'
        text: Transcript text
        timestamp: Seconds from call start
        confidence: Confidence score (0.0-1.0)
        
    Returns:
        Created Transcript object
    """
    session = get_session()
    try:
        transcript = Transcript(
            call_id=call_id,
            speaker=speaker,
            text=text,
            timestamp=timestamp,
            confidence=confidence
        )
        session.add(transcript)
        session.commit()
        session.refresh(transcript)
        return transcript
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Failed to add transcript: {e}")
        raise
    finally:
        session.close()


def get_transcripts(call_id: int) -> List[Transcript]:
    """Get all transcripts for a call, ordered by timestamp."""
    session = get_session()
    try:
        return session.query(Transcript).filter(
            Transcript.call_id == call_id
        ).order_by(Transcript.timestamp).all()
    finally:
        session.close()


# Score CRUD Operations

def create_score(
    call_id: int,
    greeting: float,
    hold_time: float,
    resolution: float,
    tone: float,
    compliance: float,
    total: float,
    recommendations: List[str]
) -> Score:
    """
    Create a score record for a call.
    
    Args:
        call_id: Call ID
        greeting: Greeting score (0-10)
        hold_time: Hold time score (0-10)
        resolution: Resolution score (0-10)
        tone: Tone score (0-10)
        compliance: Compliance score (0-10)
        total: Total weighted score
        recommendations: List of recommendation strings
        
    Returns:
        Created Score object
    """
    session = get_session()
    try:
        import json
        score = Score(
            call_id=call_id,
            greeting=greeting,
            hold_time=hold_time,
            resolution=resolution,
            tone=tone,
            compliance=compliance,
            total=total,
            recommendations=json.dumps(recommendations)
        )
        session.add(score)
        session.commit()
        session.refresh(score)
        logger.info(f"Created score for call {call_id}: {total:.1f}")
        return score
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Failed to create score: {e}")
        raise
    finally:
        session.close()


def get_score(call_id: int) -> Optional[Score]:
    """Get score for a call."""
    session = get_session()
    try:
        return session.query(Score).filter(Score.call_id == call_id).first()
    finally:
        session.close()


# Agent CRUD Operations

def get_or_create_agent(name: str, phone_number: str) -> Agent:
    """
    Get existing agent or create new one.
    
    Args:
        name: Agent name
        phone_number: Agent phone number
        
    Returns:
        Agent object
    """
    session = get_session()
    try:
        agent = session.query(Agent).filter(
            Agent.phone_number == phone_number
        ).first()
        
        if not agent:
            agent = Agent(
                name=name,
                phone_number=phone_number,
                average_score=0.0,
                total_calls=0
            )
            session.add(agent)
            session.commit()
            session.refresh(agent)
            logger.info(f"Created new agent: {agent.name}")
        else:
            logger.info(f"Found existing agent: {agent.name}")
        
        return agent
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Failed to get/create agent: {e}")
        raise
    finally:
        session.close()


def update_agent_stats(agent_id: int, new_score: float) -> None:
    """
    Update agent statistics after a new call.
    
    Args:
        agent_id: Agent ID
        new_score: Score from latest call
    """
    session = get_session()
    try:
        agent = session.query(Agent).filter(Agent.id == agent_id).first()
        if agent:
            # Calculate new average
            total_score = agent.average_score * agent.total_calls
            agent.total_calls += 1
            agent.average_score = (total_score + new_score) / agent.total_calls
            session.commit()
            logger.info(f"Updated agent {agent_id} stats: avg={agent.average_score:.1f}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Failed to update agent stats: {e}")
        raise
    finally:
        session.close()


def get_agents(limit: int = 100) -> List[Agent]:
    """Get all agents, ordered by average score."""
    session = get_session()
    try:
        return session.query(Agent).order_by(
            Agent.average_score.desc()
        ).limit(limit).all()
    finally:
        session.close()


# Query Helpers

def get_agent_performance(agent_id: int, days: int = 30) -> Dict[str, Any]:
    """
    Get agent performance metrics over a time period.
    
    Args:
        agent_id: Agent ID
        days: Number of days to look back
        
    Returns:
        Dictionary with performance metrics
    """
    session = get_session()
    try:
        agent = session.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return {}
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        calls = session.query(Call).join(Score).filter(
            Call.phone_number == agent.phone_number,
            Call.timestamp >= start_date
        ).all()
        
        scores = [call.score.total for call in calls if call.score]
        
        return {
            "agent_id": agent_id,
            "agent_name": agent.name,
            "total_calls": len(calls),
            "average_score": sum(scores) / len(scores) if scores else 0.0,
            "min_score": min(scores) if scores else 0.0,
            "max_score": max(scores) if scores else 0.0,
            "calls": [
                {
                    "call_id": call.id,
                    "timestamp": call.timestamp.isoformat(),
                    "score": call.score.total if call.score else None
                }
                for call in calls
            ]
        }
    finally:
        session.close()


def get_call_summary(call_id: int) -> Optional[Dict[str, Any]]:
    """
    Get complete call summary with transcript and score.
    
    Args:
        call_id: Call ID
        
    Returns:
        Dictionary with call, transcript, and score data
    """
    session = get_session()
    try:
        call = session.query(Call).filter(Call.id == call_id).first()
        if not call:
            return None
        
        transcripts = get_transcripts(call_id)
        score = get_score(call_id)
        
        return {
            "call": {
                "id": call.id,
                "phone_number": call.phone_number,
                "duration": call.duration,
                "status": call.status,
                "cost": call.cost,
                "timestamp": call.timestamp.isoformat(),
                "scenario_id": call.scenario_id
            },
            "transcript": [
                {
                    "speaker": t.speaker,
                    "text": t.text,
                    "timestamp": t.timestamp,
                    "confidence": t.confidence
                }
                for t in transcripts
            ],
            "score": {
                "greeting": score.greeting if score else None,
                "hold_time": score.hold_time if score else None,
                "resolution": score.resolution if score else None,
                "tone": score.tone if score else None,
                "compliance": score.compliance if score else None,
                "total": score.total if score else None,
                "recommendations": json.loads(score.recommendations) if score and score.recommendations else []
            } if score else None
        }
    except Exception as e:
        logger.error(f"Failed to get call summary: {e}")
        return None
    finally:
        session.close()

