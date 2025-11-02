"""
Transcription engine for Call QA Tool.

Handles Deepgram real-time transcription with speaker diarization.
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from core.config import get_secret

logger = logging.getLogger(__name__)

# Configuration
USE_MOCK_APIS = get_secret("USE_MOCK_APIS", "true").lower() == "true"
DEEPGRAM_API_KEY = get_secret("DEEPGRAM_API_KEY")

# Directories
CALL_LOGS_DIR = os.path.join('data', 'call_logs')
os.makedirs(CALL_LOGS_DIR, exist_ok=True)


class TranscriptionEngine:
    """Handles call transcription via Deepgram."""
    
    def __init__(self, use_mock: Optional[bool] = None):
        """
        Initialize transcription engine.
        
        Args:
            use_mock: Override USE_MOCK_APIS setting for testing
        """
        self.use_mock = use_mock if use_mock is not None else USE_MOCK_APIS
        
        if not self.use_mock:
            try:
                from deepgram import DeepgramClient, PrerecordedOptions, FileSource
                self.deepgram_client = DeepgramClient(DEEPGRAM_API_KEY)
                logger.info("Deepgram client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Deepgram: {e}")
                self.use_mock = True
                self.deepgram_client = None
        else:
            self.deepgram_client = None
            logger.info("Transcription engine running in MOCK mode")
    
    def transcribe_audio_file(self, audio_path: str) -> Optional[List[Dict[str, Any]]]:
        """
        Transcribe an audio file using Deepgram.
        
        Args:
            audio_path: Path to audio file (MP3, WAV, etc.)
            
        Returns:
            List of transcript segments with speaker identification
        """
        if self.use_mock:
            logger.info(f"[MOCK] Transcribing audio file: {audio_path}")
            # Return mock transcript
            return [
                {
                    "speaker": "customer",
                    "text": "Hi, I'd like to cancel my subscription please.",
                    "timestamp": 1.5,
                    "confidence": 0.95
                },
                {
                    "speaker": "agent",
                    "text": "Hello, thank you for calling. I'd be happy to help you with that. May I have your account number?",
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
                    "text": "I understand. Well, I've processed the cancellation. Your subscription will end at the end of this billing cycle. Is there anything else I can help you with today?",
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
        
        try:
            with open(audio_path, "rb") as audio_file:
                payload: FileSource = {
                    "buffer": audio_file,
                }
                
                options = PrerecordedOptions(
                    model="nova-2",
                    language="en-US",
                    smart_format=True,
                    punctuate=True,
                    diarize=True,  # Enable speaker diarization
                    utterances=True
                )
                
                response = self.deepgram_client.listen.rest.v("1").transcribe_file(
                    payload,
                    options
                )
                
                # Parse Deepgram response
                transcript_segments = []
                
                if response.results and response.results.channels:
                    for channel in response.results.channels:
                        for utterance in channel.alternatives[0].utterances:
                            # Deepgram diarization uses speaker labels (0, 1, etc.)
                            # We'll map: speaker 0 = agent, speaker 1 = customer
                            # In real scenarios, you may need to determine this dynamically
                            speaker_label = utterance.speaker
                            speaker = "agent" if speaker_label == 0 else "customer"
                            
                            transcript_segments.append({
                                "speaker": speaker,
                                "text": utterance.transcript,
                                "timestamp": utterance.start,  # Start time in seconds
                                "confidence": utterance.confidence
                            })
                
                logger.info(f"Transcribed {len(transcript_segments)} segments from {audio_path}")
                return transcript_segments
                
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            return None
    
    def transcribe_real_time(self, audio_stream) -> Optional[List[Dict[str, Any]]]:
        """
        Transcribe real-time audio stream.
        
        Args:
            audio_stream: Audio stream object
            
        Returns:
            List of transcript segments (or None if error)
            
        Note:
            Real-time transcription would use Deepgram's WebSocket API.
            For MVP, we'll primarily use file-based transcription.
        """
        if self.use_mock:
            logger.info("[MOCK] Real-time transcription")
            return []
        
        # TODO: Implement WebSocket-based real-time transcription for Phase 2
        logger.warning("Real-time transcription not yet implemented")
        return None
    
    def parse_transcript_for_speakers(self, segments: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Parse transcript segments into agent and customer messages.
        
        Args:
            segments: List of transcript segments with speaker labels
            
        Returns:
            Dictionary with 'agent' and 'customer' message lists
        """
        agent_messages = []
        customer_messages = []
        
        for segment in segments:
            speaker = segment.get("speaker", "unknown")
            text = segment.get("text", "")
            
            if speaker == "agent":
                agent_messages.append(text)
            elif speaker == "customer":
                customer_messages.append(text)
        
        return {
            "agent": agent_messages,
            "customer": customer_messages
        }
    
    def get_full_transcript(self, segments: List[Dict[str, Any]]) -> str:
        """
        Combine all transcript segments into full text.
        
        Args:
            segments: List of transcript segments
            
        Returns:
            Full transcript text
        """
        return " ".join([
            f"[{seg.get('speaker', 'unknown')}]: {seg.get('text', '')}"
            for seg in segments
        ])
    
    def calculate_cost(self, duration_seconds: int) -> float:
        """
        Calculate estimated Deepgram transcription cost.
        
        Args:
            duration_seconds: Audio duration in seconds
            
        Returns:
            Estimated cost in USD
        """
        # Deepgram: $0.0043 per minute
        cost = (duration_seconds / 60) * 0.0043
        logger.debug(f"Estimated Deepgram cost: ${cost:.4f}")
        return cost

