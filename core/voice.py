"""
Voice integration for Call QA Tool.

Handles Twilio outbound calls and ElevenLabs text-to-speech generation.
"""

import os
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime

from core.config import get_secret

logger = logging.getLogger(__name__)

# Configuration
USE_MOCK_APIS = get_secret("USE_MOCK_APIS", "true").lower() == "true"
TWILIO_ACCOUNT_SID = get_secret("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = get_secret("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = get_secret("TWILIO_PHONE_NUMBER")
ELEVENLABS_API_KEY = get_secret("ELEVENLABS_API_KEY")
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
MAX_CALL_DURATION = 300  # 5 minutes
CALL_TIMEOUT = 30  # seconds

# Directories
CALL_LOGS_DIR = os.path.join('data', 'call_logs')
os.makedirs(CALL_LOGS_DIR, exist_ok=True)


class VoiceEngine:
    """Handles voice calls via Twilio and TTS via ElevenLabs."""
    
    def __init__(self, use_mock: Optional[bool] = None):
        """
        Initialize voice engine.
        
        Args:
            use_mock: Override USE_MOCK_APIS setting for testing
        """
        self.use_mock = use_mock if use_mock is not None else USE_MOCK_APIS
        
        if not self.use_mock:
            try:
                from twilio.rest import Client as TwilioClient
                self.twilio_client = TwilioClient(
                    TWILIO_ACCOUNT_SID,
                    TWILIO_AUTH_TOKEN
                )
                logger.info("Twilio client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio: {e}")
                self.use_mock = True
                self.twilio_client = None
        else:
            self.twilio_client = None
            logger.info("Voice engine running in MOCK mode")
    
    def generate_speech(self, text: str, voice_id: str = DEFAULT_VOICE_ID) -> Optional[str]:
        """
        Generate speech audio using ElevenLabs TTS.
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            
        Returns:
            Path to audio file or None if failed
        """
        if self.use_mock:
            logger.info(f"[MOCK] Generating speech for text: {text[:50]}...")
            # Create dummy audio file
            audio_path = os.path.join(CALL_LOGS_DIR, f"mock_audio_{datetime.now().timestamp()}.wav")
            with open(audio_path, 'w') as f:
                f.write("mock audio content")
            return audio_path
        
        try:
            import requests
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": ELEVENLABS_API_KEY
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                audio_path = os.path.join(
                    CALL_LOGS_DIR,
                    f"tts_{datetime.now().timestamp()}.mp3"
                )
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Generated TTS audio: {audio_path}")
                return audio_path
            else:
                logger.error(f"ElevenLabs TTS failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate speech: {e}")
            return None
    
    def make_call(
        self,
        to_phone: str,
        twiml_url: Optional[str] = None,
        twiml_instructions: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make an outbound call via Twilio.
        
        Args:
            to_phone: Phone number to call (E.164 format)
            twiml_url: URL for Twilio TwiML instructions
            twiml_instructions: Inline TwiML XML string
            
        Returns:
            Dictionary with call information (sid, status, etc.)
        """
        if self.use_mock:
            logger.info(f"[MOCK] Making call to {to_phone}")
            return {
                "sid": f"CA{''.join([str(i) for i in range(32)])}",
                "status": "initiated",
                "from": TWILIO_PHONE_NUMBER or "+15551234567",
                "to": to_phone,
                "mock": True
            }
        
        try:
            if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
                logger.error("Twilio credentials not configured")
                return None
            
            if not twiml_url and not twiml_instructions:
                logger.error("Either twiml_url or twiml_instructions required")
                return None
            
            call_params = {
                "to": to_phone,
                "from_": TWILIO_PHONE_NUMBER,
                "timeout": CALL_TIMEOUT,
                "record": True
            }
            
            if twiml_url:
                call_params["url"] = twiml_url
            else:
                call_params["twiml"] = twiml_instructions
            
            call = self.twilio_client.calls.create(**call_params)
            
            logger.info(f"Initiated call: {call.sid} to {to_phone}")
            
            return {
                "sid": call.sid,
                "status": call.status,
                "from": call.from_,
                "to": call.to,
                "mock": False
            }
            
        except Exception as e:
            logger.error(f"Failed to make call: {e}")
            return None
    
    def get_call_status(self, call_sid: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of a call.
        
        Args:
            call_sid: Twilio call SID
            
        Returns:
            Dictionary with call status information
        """
        if self.use_mock:
            logger.info(f"[MOCK] Getting status for call {call_sid}")
            return {
                "sid": call_sid,
                "status": "completed",
                "duration": 120,
                "mock": True
            }
        
        try:
            call = self.twilio_client.calls(call_sid).fetch()
            return {
                "sid": call.sid,
                "status": call.status,
                "duration": int(call.duration) if call.duration else 0,
                "mock": False
            }
        except Exception as e:
            logger.error(f"Failed to get call status: {e}")
            return None
    
    def calculate_cost(self, duration_seconds: int, text_length: int = 0) -> float:
        """
        Calculate estimated cost for a call.
        
        Args:
            duration_seconds: Call duration in seconds
            text_length: Length of text used for TTS (characters)
            
        Returns:
            Estimated cost in USD
        """
        # Twilio: $0.013 per minute
        twilio_cost = (duration_seconds / 60) * 0.013
        
        # ElevenLabs: $0.30 per 1K characters
        elevenlabs_cost = (text_length / 1000) * 0.30
        
        # Deepgram: $0.0043 per minute (handled in transcription.py)
        
        total_cost = twilio_cost + elevenlabs_cost
        logger.debug(f"Estimated cost: ${total_cost:.4f} (Twilio: ${twilio_cost:.4f}, ElevenLabs: ${elevenlabs_cost:.4f})")
        return total_cost
    
    def create_twiml_for_call(self, customer_script: list[str]) -> str:
        """
        Create TwiML XML for Twilio call with customer script.
        
        Args:
            customer_script: List of text lines to speak
            
        Returns:
            TwiML XML string
        """
        # For MVP, we'll use simple TwiML
        # In production, this could use Twilio's <Say> verb or play pre-recorded audio
        
        twiml_parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<Response>']
        
        # Add greeting
        twiml_parts.append('<Say voice="alice">Hello, this is a quality assurance test call. Please proceed as normal.</Say>')
        
        # Add pauses between script lines
        for line in customer_script:
            twiml_parts.append(f'<Say voice="alice">{line}</Say>')
            twiml_parts.append('<Pause length="2"/>')  # 2 second pause
        
        twiml_parts.append('</Response>')
        
        return '\n'.join(twiml_parts)

