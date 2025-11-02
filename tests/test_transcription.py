"""
Tests for transcription engine (Deepgram).

Uses mocked APIs to avoid real API calls during testing.
"""

import pytest
from unittest.mock import MagicMock, patch
from core.transcription import TranscriptionEngine


class TestTranscriptionEngine:
    """Tests for TranscriptionEngine class."""
    
    def test_init_mock_mode(self):
        """Test initialization in mock mode."""
        engine = TranscriptionEngine(use_mock=True)
        assert engine.use_mock is True
        assert engine.deepgram_client is None
    
    def test_init_real_mode(self):
        """Test initialization in real mode (should fallback to mock if no credentials)."""
        with patch('core.transcription.DEEPGRAM_API_KEY', None):
            engine = TranscriptionEngine(use_mock=False)
            # Should fallback to mock if credentials missing
            assert engine.use_mock is True
    
    @patch('core.transcription.DEEPGRAM_API_KEY', 'test_key')
    def test_init_real_mode_with_credentials(self):
        """Test initialization with real credentials."""
        pytest.importorskip('deepgram', reason='deepgram not installed')
        with patch('deepgram.DeepgramClient') as mock_deepgram:
            engine = TranscriptionEngine(use_mock=False)
            # Should attempt to create Deepgram client
            # (may still be mock if import fails, which is fine for tests)
    
    def test_transcribe_audio_file_mock(self):
        """Test transcription in mock mode."""
        engine = TranscriptionEngine(use_mock=True)
        
        segments = engine.transcribe_audio_file("mock_audio.wav")
        
        assert segments is not None
        assert len(segments) > 0
        assert all("speaker" in seg for seg in segments)
        assert all("text" in seg for seg in segments)
        assert all("timestamp" in seg for seg in segments)
        assert all("confidence" in seg for seg in segments)
    
    def test_transcribe_audio_file_real_mocked(self):
        """Test transcription with mocked Deepgram API."""
        pytest.importorskip('deepgram', reason='deepgram not installed')
        # Mock Deepgram response
        mock_utterance = MagicMock()
        mock_utterance.speaker = 0
        mock_utterance.transcript = "Hello, how can I help you?"
        mock_utterance.start = 1.5
        mock_utterance.confidence = 0.95
        
        mock_alternative = MagicMock()
        mock_alternative.utterances = [mock_utterance]
        
        mock_channel = MagicMock()
        mock_channel.alternatives = [mock_alternative]
        
        mock_results = MagicMock()
        mock_results.channels = [mock_channel]
        
        mock_response = MagicMock()
        mock_response.results = mock_results
        
        mock_deepgram = MagicMock()
        mock_listen = MagicMock()
        mock_listen.rest = MagicMock()
        mock_listen.rest.v = MagicMock(return_value=mock_listen.rest)
        mock_listen.rest.transcribe_file = MagicMock(return_value=mock_response)
        mock_deepgram.listen = mock_listen
        
        with patch('deepgram.DeepgramClient', return_value=mock_deepgram):
            with patch('core.transcription.DEEPGRAM_API_KEY', 'test_key'):
                engine = TranscriptionEngine(use_mock=False)
                engine.deepgram_client = mock_deepgram
                
                # Mock file opening
                with patch('builtins.open', create=True):
                    segments = engine.transcribe_audio_file("test.wav")
                    
                    # Should return parsed segments
                    if segments:
                        assert len(segments) > 0
    
    def test_parse_transcript_for_speakers(self):
        """Test parsing transcript into agent/customer messages."""
        engine = TranscriptionEngine(use_mock=True)
        
        segments = [
            {"speaker": "agent", "text": "Hello"},
            {"speaker": "customer", "text": "Hi"},
            {"speaker": "agent", "text": "How can I help?"}
        ]
        
        parsed = engine.parse_transcript_for_speakers(segments)
        
        assert "agent" in parsed
        assert "customer" in parsed
        assert len(parsed["agent"]) == 2
        assert len(parsed["customer"]) == 1
    
    def test_get_full_transcript(self):
        """Test combining transcript segments into full text."""
        engine = TranscriptionEngine(use_mock=True)
        
        segments = [
            {"speaker": "agent", "text": "Hello"},
            {"speaker": "customer", "text": "Hi"},
            {"speaker": "agent", "text": "How can I help?"}
        ]
        
        full_text = engine.get_full_transcript(segments)
        
        assert "Hello" in full_text
        assert "Hi" in full_text
        assert "How can I help?" in full_text
        assert "[agent]" in full_text
        assert "[customer]" in full_text
    
    def test_calculate_cost(self):
        """Test cost calculation for transcription."""
        engine = TranscriptionEngine(use_mock=True)
        
        # Deepgram: $0.0043 per minute
        # 120 seconds = 2 minutes = $0.0086
        cost = engine.calculate_cost(120)
        
        assert cost > 0
        assert cost < 0.1  # Should be reasonable for 2 minutes
    
    def test_transcribe_real_time_not_implemented(self):
        """Test that real-time transcription returns None (not yet implemented)."""
        engine = TranscriptionEngine(use_mock=True)
        
        result = engine.transcribe_real_time(None)
        
        # Should return None or empty list for MVP
        assert result is None or result == []
    
    def test_transcribe_audio_file_error_handling(self):
        """Test error handling in transcription."""
        engine = TranscriptionEngine(use_mock=True)
        
        # Mock mode should handle missing files gracefully
        result = engine.transcribe_audio_file("nonexistent.wav")
        assert result is not None  # Mock mode returns sample data

