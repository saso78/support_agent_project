"""
Call QA Agent for evaluating call center performance.

Extends BaseAgent to score calls on multiple metrics and generate recommendations.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base_agent import BaseAgent
from core.llm import OpenRouterLLM
from core.memory import ConversationMemory
from core.database import (
    get_transcripts, get_score, create_score, get_call, update_agent_stats
)

logger = logging.getLogger(__name__)


class CallQAAgent(BaseAgent):
    """Agent for evaluating call center quality."""
    
    def __init__(self, llm: OpenRouterLLM, memory: ConversationMemory):
        """
        Initialize Call QA Agent.
        
        Args:
            llm: OpenRouter LLM instance for evaluation
            memory: Conversation memory for storing evaluations
        """
        super().__init__(llm, memory)
    
    def process_message(self, message: str) -> str:
        """
        Process a message - for CallQAAgent, use evaluate_call() instead.
        
        Args:
            message: Input message
            
        Returns:
            Response indicating to use evaluate_call()
        """
        return "Call QA Agent doesn't process messages directly. Use evaluate_call() instead."
    
    def evaluate_call(self, call_id: int, scenario_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate a call and generate scores.
        
        Args:
            call_id: Call ID from database
            scenario_id: Optional scenario identifier for context
            
        Returns:
            Dictionary with scores and recommendations
        """
        try:
            # Get call and transcripts
            call = get_call(call_id)
            if not call:
                logger.error(f"Call {call_id} not found")
                return {"error": "Call not found"}
            
            transcripts = get_transcripts(call_id)
            if not transcripts:
                logger.error(f"No transcripts found for call {call_id}")
                return {"error": "No transcripts found"}
            
            # Build full transcript
            full_transcript = self._build_full_transcript(transcripts)
            
            # Load scenario if provided
            scenario = None
            if scenario_id:
                scenario = self._load_scenario(scenario_id)
            
            # Score each metric
            scores = {
                "greeting": self._score_greeting(transcripts, call, scenario),
                "hold_time": self._score_hold_time(transcripts, call),
                "resolution": self._score_resolution(transcripts, call, scenario),
                "tone": self._score_tone(transcripts, full_transcript),
                "compliance": self._score_compliance(transcripts, scenario)
            }
            
            # Calculate weighted total (can be customized based on scenario)
            weights = scenario.get("scoring_weights", {}) if scenario else {
                "greeting": 1.0,
                "hold_time": 0.5,
                "resolution": 2.0,
                "tone": 1.5,
                "compliance": 1.0
            }
            
            total_score = self._calculate_weighted_score(scores, weights)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(scores, transcripts, scenario)
            
            # Save scores to database
            create_score(
                call_id=call_id,
                greeting=scores["greeting"],
                hold_time=scores["hold_time"],
                resolution=scores["resolution"],
                tone=scores["tone"],
                compliance=scores["compliance"],
                total=total_score,
                recommendations=recommendations
            )
            
            logger.info(f"Evaluated call {call_id}: Total score = {total_score:.1f}/10")
            
            return {
                "call_id": call_id,
                "scores": scores,
                "total": total_score,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Failed to evaluate call {call_id}: {e}")
            return {"error": str(e)}
    
    def _build_full_transcript(self, transcripts: List[Any]) -> str:
        """Build full transcript text from segments."""
        return " ".join([t.text for t in transcripts if t.text])
    
    def _load_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Load scenario from JSON file."""
        try:
            scenario_path = Path("data/call_scenarios") / f"{scenario_id}.json"
            if scenario_path.exists():
                with open(scenario_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Failed to load scenario {scenario_id}: {e}")
            return None
    
    def _score_greeting(self, transcripts: List[Any], call: Any, scenario: Optional[Dict]) -> float:
        """
        Score greeting quality (0-10).
        
        Scoring:
        - 10: Professional greeting with company name + agent name
        - 7-9: Greeting with one element missing
        - 4-6: Generic greeting ("Hello?")
        - 0-3: No greeting or unprofessional
        """
        if not transcripts:
            return 0.0
        
        # Look for agent's first message
        agent_messages = [t.text.lower() for t in transcripts if t.speaker == "agent"]
        if not agent_messages:
            return 0.0
        
        first_message = agent_messages[0]
        
        # Check for professional greeting elements
        has_company_name = any(word in first_message for word in ["company", "support", "help desk", "service"])
        has_agent_name = "i'm" in first_message or "this is" in first_message
        has_greeting_word = any(word in first_message for word in ["hello", "hi", "good morning", "good afternoon", "thank you"])
        
        if has_greeting_word and has_company_name and has_agent_name:
            return 10.0
        elif has_greeting_word and (has_company_name or has_agent_name):
            return 8.0
        elif has_greeting_word:
            return 5.0
        else:
            return 2.0
    
    def _score_hold_time(self, transcripts: List[Any], call: Any) -> float:
        """
        Score hold time management (0-10).
        
        Scoring:
        - 10: No hold or <30 seconds with explanation
        - 7-9: 30-60 seconds with explanation
        - 4-6: 60-120 seconds or no explanation
        - 0-3: >120 seconds or hang-up
        """
        # For MVP, we'll estimate hold time from transcript gaps
        # In production, use actual call metadata or transcript timestamps
        
        if not transcripts:
            return 0.0
        
        # Calculate average gap between messages (rough estimate)
        timestamps = [t.timestamp for t in transcripts if t.timestamp]
        if len(timestamps) < 2:
            return 10.0  # No gaps detected
        
        gaps = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        max_gap = max(gaps) if gaps else 0
        
        # Check for hold-related phrases
        hold_phrases = ["hold", "please wait", "one moment", "transferring"]
        has_hold_explanation = any(
            phrase in t.text.lower()
            for t in transcripts
            for phrase in hold_phrases
        )
        
        if max_gap < 30 and has_hold_explanation:
            return 10.0
        elif max_gap < 60 and has_hold_explanation:
            return 8.0
        elif max_gap < 120:
            return 5.0
        else:
            return 2.0
    
    def _score_resolution(self, transcripts: List[Any], call: Any, scenario: Optional[Dict]) -> float:
        """
        Score problem resolution (0-10).
        
        Scoring:
        - 10: Issue fully resolved, confirmation provided
        - 7-9: Resolved but missing confirmation
        - 4-6: Partial resolution, requires callback
        - 0-3: Not resolved, incorrect information
        """
        if not transcripts:
            return 0.0
        
        full_text = " ".join([t.text.lower() for t in transcripts])
        
        # Check for resolution indicators
        resolved_phrases = [
            "resolved", "taken care of", "completed", "done", "finished",
            "processed", "cancelled", "refunded", "fixed"
        ]
        has_resolution = any(phrase in full_text for phrase in resolved_phrases)
        
        # Check for confirmation
        confirmation_phrases = [
            "confirmation", "reference number", "ticket number", "case number",
            "you should receive", "email confirmation"
        ]
        has_confirmation = any(phrase in full_text for phrase in confirmation_phrases)
        
        # Check for partial resolution
        partial_phrases = [
            "call back", "follow up", "will contact", "need to", "requires"
        ]
        has_partial = any(phrase in full_text for phrase in partial_phrases)
        
        if has_resolution and has_confirmation:
            return 10.0
        elif has_resolution:
            return 8.0
        elif has_partial:
            return 5.0
        else:
            return 2.0
    
    def _score_tone(self, transcripts: List[Any], full_transcript: str) -> float:
        """
        Score tone/empathy (0-10) using sentiment analysis.
        
        Scoring:
        - 10: Consistently positive, empathetic language
        - 7-9: Professional but neutral
        - 4-6: Occasionally short or impatient
        - 0-3: Rude, dismissive, or hostile
        """
        if not transcripts:
            return 0.0
        
        # Use LLM for sentiment analysis
        agent_text = " ".join([
            t.text for t in transcripts
            if t.speaker == "agent"
        ])
        
        if not agent_text:
            return 5.0  # Neutral if no agent text
        
        prompt = f"""Analyze the tone and empathy of this customer service conversation.
Rate the agent's tone on a scale of 0-10 where:
- 10 = Consistently positive, empathetic, professional
- 7-9 = Professional and polite but neutral
- 4-6 = Occasionally short or impatient
- 0-3 = Rude, dismissive, or hostile

Agent's speech:
{agent_text}

Respond with only a number from 0-10."""

        try:
            response = self.llm.generate_response(
                prompt,
                {"system_prompt": "You are a tone analysis expert. Provide only numerical scores."}
            )
            
            # Extract number from response
            score = float(response.strip().split()[0])
            return max(0.0, min(10.0, score))
            
        except Exception as e:
            logger.error(f"Failed to analyze tone: {e}")
            # Fallback: Simple keyword-based scoring
            positive_words = ["thank", "please", "sorry", "appreciate", "help", "happy"]
            negative_words = ["no", "can't", "won't", "impossible", "busy"]
            
            positive_count = sum(1 for word in positive_words if word in agent_text.lower())
            negative_count = sum(1 for word in negative_words if word in agent_text.lower())
            
            if positive_count > negative_count * 2:
                return 8.0
            elif positive_count > negative_count:
                return 6.0
            else:
                return 4.0
    
    def _score_compliance(self, transcripts: List[Any], scenario: Optional[Dict]) -> float:
        """
        Score script compliance (0-10).
        
        Scoring:
        - 10: All required elements present
        - 5: 50% of elements present
        - 0: No script elements detected
        """
        if not scenario or "expected_agent_behavior" not in scenario:
            return 5.0  # Neutral if no scenario requirements
        
        if not transcripts:
            return 0.0
        
        full_text = " ".join([t.text.lower() for t in transcripts if t.speaker == "agent"])
        expected = scenario["expected_agent_behavior"]
        
        # Check for expected elements
        found_elements = 0
        total_elements = len(expected)
        
        if "greeting" in expected:
            if "hello" in full_text or "hi" in full_text or "thank you for calling" in full_text:
                found_elements += 1
        
        if "retention_attempt" in expected:
            if "why" in full_text or "reason" in full_text or "concern" in full_text:
                found_elements += 1
        
        if "process" in expected:
            if "process" in full_text or "step" in full_text or "procedure" in full_text:
                found_elements += 1
        
        if "confirmation" in expected:
            if "confirmation" in full_text or "reference" in full_text or "number" in full_text:
                found_elements += 1
        
        if total_elements == 0:
            return 5.0
        
        percentage = found_elements / total_elements
        
        if percentage >= 1.0:
            return 10.0
        elif percentage >= 0.5:
            return 5.0
        else:
            return 0.0
    
    def _calculate_weighted_score(self, scores: Dict[str, float], weights: Dict[str, float]) -> float:
        """Calculate weighted average score."""
        total_weight = sum(weights.values())
        if total_weight == 0:
            return sum(scores.values()) / len(scores)
        
        weighted_sum = sum(scores[key] * weights.get(key, 1.0) for key in scores)
        return weighted_sum / total_weight
    
    def _generate_recommendations(
        self,
        scores: Dict[str, float],
        transcripts: List[Any],
        scenario: Optional[Dict]
    ) -> List[str]:
        """Generate improvement recommendations based on scores."""
        recommendations = []
        
        if scores["greeting"] < 7:
            recommendations.append(
                "Improve greeting: Include company name and agent name in initial greeting"
            )
        
        if scores["hold_time"] < 7:
            recommendations.append(
                "Reduce hold times: Keep holds under 60 seconds and always explain why"
            )
        
        if scores["resolution"] < 7:
            recommendations.append(
                "Ensure complete resolution: Confirm issue is resolved and provide reference number"
            )
        
        if scores["tone"] < 7:
            recommendations.append(
                "Improve tone: Use more empathetic language and positive phrasing"
            )
        
        if scores["compliance"] < 7:
            recommendations.append(
                "Follow script requirements: Ensure all required script elements are included"
            )
        
        if not recommendations:
            recommendations.append("Great job! Maintain current performance standards.")
        
        return recommendations

