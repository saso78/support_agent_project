"""
SQLAlchemy ORM models for Call QA Tool database.

Defines database schema for calls, transcripts, scores, and agents.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Call(Base):
    """Model for storing call metadata."""
    
    __tablename__ = 'calls'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), nullable=False)
    duration = Column(Integer)  # Duration in seconds
    status = Column(String(20))  # 'completed', 'failed', 'timeout'
    cost = Column(Float, default=0.0)  # Estimated cost in USD
    timestamp = Column(DateTime, default=datetime.utcnow)
    scenario_id = Column(String(100))  # Reference to scenario file
    recording_path = Column(String(500))  # Path to recording file
    
    # Relationships
    transcripts = relationship("Transcript", back_populates="call", cascade="all, delete-orphan")
    score = relationship("Score", back_populates="call", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Call(id={self.id}, phone={self.phone_number}, status={self.status})>"


class Transcript(Base):
    """Model for storing transcript segments with speaker identification."""
    
    __tablename__ = 'transcripts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    call_id = Column(Integer, ForeignKey('calls.id'), nullable=False)
    speaker = Column(String(20))  # 'agent' or 'customer'
    text = Column(Text)
    timestamp = Column(Float)  # Seconds from call start
    confidence = Column(Float)  # Confidence score 0.0-1.0
    
    # Relationships
    call = relationship("Call", back_populates="transcripts")
    
    def __repr__(self) -> str:
        return f"<Transcript(id={self.id}, speaker={self.speaker}, text={self.text[:50]}...)>"


class Score(Base):
    """Model for storing call evaluation scores."""
    
    __tablename__ = 'scores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    call_id = Column(Integer, ForeignKey('calls.id'), nullable=False, unique=True)
    greeting = Column(Float)  # 0-10
    hold_time = Column(Float)  # 0-10
    resolution = Column(Float)  # 0-10
    tone = Column(Float)  # 0-10
    compliance = Column(Float)  # 0-10
    total = Column(Float)  # Weighted average
    recommendations = Column(Text)  # JSON array of recommendation strings
    
    # Relationships
    call = relationship("Call", back_populates="score")
    
    def __repr__(self) -> str:
        return f"<Score(call_id={self.call_id}, total={self.total:.1f})>"


class Agent(Base):
    """Model for storing agent profiles and performance metrics."""
    
    __tablename__ = 'agents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False, unique=True)
    average_score = Column(Float, default=0.0)
    total_calls = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name={self.name}, avg_score={self.average_score:.1f})>"

