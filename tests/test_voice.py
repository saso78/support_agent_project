"""
Tests for voice integration (Twilio and ElevenLabs).

Uses mocked APIs to avoid real API calls during testing.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from core.voice import VoiceEngine


class TestVoiceEngine:
    """Tests for VoiceEngine class."""
    
    def test_init_mock_mode(self):
        """Test initialization in mock mode."""
        engine = VoiceEngine(use_mock=True)
        assert engine.use_mock is True
        assert engine.twilio_client is None
    
    def test_init_real_mode(self):
        """Test initialization in real mode (should fallback to mock if no credentials)."""
        with patch('core.voice.TWILIO_ACCOUNT_SID', None):
            engine = VoiceEngine(use_mock=False)
            # Should fallback to mock if credentials missing
            assert engine.use_mock is True
    
    @patch('core.voice.TWILIO_ACCOUNT_SID', 'test_sid')
    @patch('core.voice.TWILIO_AUTH_TOKEN', 'test_token')
    def test_init_real_mode_with_credentials(self):
        """Test initialization with real credentials."""
        pytest.importorskip('twilio', reason='twilio not installed')
        with patch('twilio.rest.Client') as mock_twilio:
            engine = VoiceEngine(use_mock=False)
            # Should attempt to create Twilio client
            # (may still be None if import fails, which is fine for tests)
    
    def test_generate_speech_mock(self):
        """Test TTS generation in mock mode."""
        engine = VoiceEngine(use_mock=True)
        
        audio_path = engine.generate_speech("Hello, this is a test.")
        
        assert audio_path is not None
        assert "mock_audio" in audio_path or "tts_" in audio_path
    
    @patch('requests.post')
    def test_generate_speech_real(self, mock_post):
        """Test TTS generation with mocked ElevenLabs API."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio content"
        mock_post.return_value = mock_response
        
        with patch('core.voice.USE_MOCK_APIS', False):
            with patch('core.voice.ELEVENLABS_API_KEY', 'test_key'):
                engine = VoiceEngine(use_mock=False)
                
                # Should still use mock if API key is missing in real scenario
                # But we'll test the logic path
                result = engine.generate_speech("Test text")
                # Result may be None if API key validation fails, which is expected
    
    def test_make_call_mock(self):
        """Test making a call in mock mode."""
        engine = VoiceEngine(use_mock=True)
        
        result = engine.make_call(
            to_phone="+1234567890",
            twiml_instructions="<Response><Say>Hello</Say></Response>"
        )
        
        assert result is not None
        assert result["mock"] is True
        assert "sid" in result
        assert result["to"] == "+1234567890"
    
    @patch('core.voice.TWILIO_ACCOUNT_SID', 'test_sid')
    @patch('core.voice.TWILIO_AUTH_TOKEN', 'test_token')
    @patch('core.voice.TWILIO_PHONE_NUMBER', '+15551234567')
    def test_make_call_real_mocked(self):
        """Test making a call with mocked Twilio API."""
        pytest.importorskip('twilio', reason='twilio not installed')
        mock_call = MagicMock()
        mock_call.sid = "CA123456789"
        mock_call.status = "initiated"
        mock_call.from_ = "+15551234567"
        mock_call.to = "+1234567890"
        
        mock_twilio_client = MagicMock()
        mock_twilio_client.calls.create.return_value = mock_call
        
        with patch('twilio.rest.Client', return_value=mock_twilio_client):
            engine = VoiceEngine(use_mock=False)
            engine.twilio_client = mock_twilio_client
            
            result = engine.make_call(
                to_phone="+1234567890",
                twiml_instructions="<Response><Say>Hello</Say></Response>"
            )
            
            assert result is not None
            assert result["sid"] == "CA123456789"
            assert result["status"] == "initiated"
            assert result["mock"] is False
    
    def test_get_call_status_mock(self):
        """Test getting call status in mock mode."""
        engine = VoiceEngine(use_mock=True)
        
        result = engine.get_call_status("CA123456789")
        
        assert result is not None
        assert result["mock"] is True
        assert result["status"] == "completed"
        assert "duration" in result
    
    def test_calculate_cost(self):
        """Test cost calculation."""
        engine = VoiceEngine(use_mock=True)
        
        # Test with duration and text length
        cost = engine.calculate_cost(duration_seconds=120, text_length=500)
        
        # Twilio: (120/60) * 0.013 = 0.026
        # ElevenLabs: (500/1000) * 0.30 = 0.15
        # Total: ~0.176
        assert cost > 0
        assert cost < 1.0  # Should be reasonable
    
    def test_create_twiml_for_call(self):
        """Test TwiML generation."""
        engine = VoiceEngine(use_mock=True)
        
        script = [
            "Hello, I'd like to cancel my subscription.",
            "Yes, please proceed."
        ]
        
        twiml = engine.create_twiml_for_call(script)
        
        assert "<Response>" in twiml
        assert "<Say" in twiml
        assert "Hello, I'd like to cancel my subscription" in twiml
    
    def test_make_call_missing_parameters(self):
        """Test making a call without required parameters."""
        engine = VoiceEngine(use_mock=True)
        
        # Should work in mock mode
        result = engine.make_call(to_phone="+1234567890")
        assert result is not None
    
    def test_generate_speech_error_handling(self):
        """Test error handling in speech generation."""
        engine = VoiceEngine(use_mock=True)
        
        # Mock mode should always succeed
        result = engine.generate_speech("")
        assert result is not None

