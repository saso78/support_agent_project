"""
Streamlit dashboard for Call QA Tool.

Displays call history, scores, agent performance, and analytics.
"""

import streamlit as st
from pathlib import Path
import sys
import json
from datetime import datetime, timedelta
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.database import (
    init_db, get_calls, get_call_summary, get_agents, get_agent_performance
)
from core.config import load_config
from core.llm import OpenRouterLLM
from core.memory import ConversationMemory
from agents.call_qa_agent import CallQAAgent
from core.voice import VoiceEngine
from core.transcription import TranscriptionEngine


def initialize_session_state():
    """Initialize session state variables."""
    if 'call_qa_initialized' not in st.session_state:
        # Initialize database
        init_db()
        
        # Initialize LLM and agent
        config = load_config()
        llm = OpenRouterLLM(api_key=config.api_key)
        memory = ConversationMemory()
        st.session_state.call_qa_agent = CallQAAgent(llm, memory)
        
        st.session_state.call_qa_initialized = True


def main():
    """Main dashboard function."""
    st.set_page_config(
        page_title="Call QA Dashboard",
        page_icon="📞",
        layout="wide"
    )
    
    st.title("📞 Call Center QA Dashboard")
    st.sidebar.title("Options")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigate",
        ["Call History", "Make Test Call", "Agent Performance", "Analytics"]
    )
    
    # Display selected page
    if page == "Call History":
        show_call_history()
    elif page == "Make Test Call":
        show_make_call()
    elif page == "Agent Performance":
        show_agent_performance()
    elif page == "Analytics":
        show_analytics()


def show_call_history():
    """Display call history table."""
    st.header("Call History")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "completed", "failed", "timeout"]
        )
    
    with col2:
        days_filter = st.selectbox(
            "Time Range",
            [7, 30, 90, "All"]
        )
    
    with col3:
        phone_filter = st.text_input("Filter by Phone Number (optional)")
    
    # Get calls
    status = status_filter if status_filter != "All" else None
    phone = phone_filter if phone_filter else None
    
    start_date = None
    if days_filter != "All":
        start_date = datetime.utcnow() - timedelta(days=days_filter)
    
    calls = get_calls(
        limit=100,
        status=status,
        phone_number=phone,
        start_date=start_date
    )
    
    if not calls:
        st.info("No calls found matching filters.")
        return
    
    # Build dataframe
    data = []
    for call in calls:
        # Safely access score attribute
        score = None
        try:
            score = call.score
        except Exception:
            # Score not loaded or doesn't exist
            pass
        
        data.append({
            "ID": call.id,
            "Phone": call.phone_number[-4:].rjust(4, '*') if len(call.phone_number) >= 4 else "****",  # Mask phone number
            "Duration": f"{call.duration}s" if call.duration else "N/A",
            "Status": call.status or "N/A",
            "Score": f"{score.total:.1f}" if score and score.total is not None else "N/A",
            "Cost": f"${call.cost:.2f}" if call.cost else "$0.00",
            "Timestamp": call.timestamp.strftime("%Y-%m-%d %H:%M") if call.timestamp else "N/A"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # Show call details
    selected_call_id = st.selectbox(
        "View Call Details",
        [None] + [call.id for call in calls]
    )
    
    if selected_call_id:
        show_call_details(selected_call_id)


def show_call_details(call_id: int):
    """Display detailed call information."""
    st.subheader(f"Call Details: #{call_id}")
    
    summary = get_call_summary(call_id)
    if not summary:
        st.error("Call not found")
        return
    
    call_data = summary["call"]
    transcript_data = summary["transcript"]
    score_data = summary["score"]
    
    # Call info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", call_data["status"])
    with col2:
        st.metric("Duration", f"{call_data['duration']}s" if call_data["duration"] else "N/A")
    with col3:
        st.metric("Cost", f"${call_data['cost']:.2f}" if call_data["cost"] else "$0.00")
    
    # Scores
    if score_data:
        st.subheader("Scores")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("Greeting", f"{score_data['greeting']:.1f}")
        with col2:
            st.metric("Hold Time", f"{score_data['hold_time']:.1f}")
        with col3:
            st.metric("Resolution", f"{score_data['resolution']:.1f}")
        with col4:
            st.metric("Tone", f"{score_data['tone']:.1f}")
        with col5:
            st.metric("Compliance", f"{score_data['compliance']:.1f}")
        with col6:
            st.metric("Total", f"{score_data['total']:.1f}", delta=None)
        
        # Recommendations
        if score_data.get("recommendations"):
            st.subheader("Recommendations")
            for rec in score_data["recommendations"]:
                st.write(f"- {rec}")
    
    # Transcript
    if transcript_data:
        st.subheader("Transcript")
        transcript_text = ""
        for segment in transcript_data:
            speaker_emoji = "👤" if segment["speaker"] == "agent" else "📞"
            transcript_text += f"{speaker_emoji} **{segment['speaker'].title()}** ({segment['timestamp']:.1f}s): {segment['text']}\n\n"
        
        st.markdown(transcript_text)


def show_make_call():
    """Interface for making a test call."""
    st.header("Make Test Call")
    
    # Load scenarios
    scenario_dir = Path("data/call_scenarios")
    scenarios = []
    if scenario_dir.exists():
        scenarios = [f.stem for f in scenario_dir.glob("*.json")]
    
    if not scenarios:
        st.warning("No scenarios found. Please add scenario JSON files to data/call_scenarios/")
        return
    
    # Form
    with st.form("make_call_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            agent_name = st.text_input("Agent Name", placeholder="John Doe")
            agent_phone = st.text_input("Agent Phone Number", placeholder="+1234567890")
        
        with col2:
            scenario_id = st.selectbox("Test Scenario", scenarios)
            use_mock = st.checkbox("Use Mock APIs (No real calls)", value=True)
        
        submitted = st.form_submit_button("Make Test Call", type="primary")
        
        if submitted:
            if not agent_phone:
                st.error("Please provide agent phone number")
            elif not agent_name:
                st.error("Please provide agent name")
            else:
                with st.spinner("Making call..."):
                    try:
                        # Initialize engines
                        voice_engine = VoiceEngine(use_mock=use_mock)
                        transcription_engine = TranscriptionEngine(use_mock=use_mock)
                        
                        # Load scenario
                        scenario_path = scenario_dir / f"{scenario_id}.json"
                        with open(scenario_path, 'r') as f:
                            scenario = json.load(f)
                        
                        # Create call record
                        from core.database import create_call
                        call = create_call(
                            phone_number=agent_phone,
                            status="initiated",
                            scenario_id=scenario_id
                        )
                        
                        # Make call (simplified for MVP - real implementation would handle async)
                        st.info("Call initiation would happen here. For MVP, this creates a mock call record.")
                        st.success(f"Call #{call.id} initiated (mock mode)")
                        
                        # For real implementation:
                        # 1. Make actual Twilio call
                        # 2. Handle real-time transcription
                        # 3. Update call status
                        # 4. Evaluate call
                        
                    except Exception as e:
                        st.error(f"Error making call: {e}")


def show_agent_performance():
    """Display agent performance metrics."""
    st.header("Agent Performance")
    
    agents = get_agents(limit=50)
    
    if not agents:
        st.info("No agents found.")
        return
    
    # Agent list
    data = []
    for agent in agents:
        data.append({
            "ID": agent.id,
            "Name": agent.name,
            "Phone": agent.phone_number[-4:].rjust(4, '*'),
            "Total Calls": agent.total_calls,
            "Average Score": f"{agent.average_score:.1f}" if agent.average_score else "N/A"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # Agent details
    selected_agent_id = st.selectbox(
        "View Agent Details",
        [None] + [agent.id for agent in agents]
    )
    
    if selected_agent_id:
        performance = get_agent_performance(selected_agent_id, days=30)
        if performance:
            st.subheader(f"Agent: {performance['agent_name']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Calls", performance["total_calls"])
            with col2:
                st.metric("Average Score", f"{performance['average_score']:.1f}")
            with col3:
                st.metric("Score Range", f"{performance['min_score']:.1f} - {performance['max_score']:.1f}")


def show_analytics():
    """Display analytics and trends."""
    st.header("Analytics & Trends")
    
    calls = get_calls(limit=100)
    
    if not calls:
        st.info("No call data available for analytics.")
        return
    
    # Score trends - safely access scores
    scored_calls = []
    for call in calls:
        try:
            if call.score:
                scored_calls.append(call)
        except Exception:
            continue
    
    if scored_calls:
        scores_data = {
            "Date": [call.timestamp.strftime("%Y-%m-%d") if call.timestamp else "" for call in scored_calls],
            "Total Score": [call.score.total for call in scored_calls if call.score and call.score.total is not None],
            "Greeting": [call.score.greeting for call in scored_calls if call.score and call.score.greeting is not None],
            "Resolution": [call.score.resolution for call in scored_calls if call.score and call.score.resolution is not None],
            "Tone": [call.score.tone for call in scored_calls if call.score and call.score.tone is not None]
        }
        
        # Ensure all lists have the same length
        min_len = min(len(v) for v in scores_data.values() if v)
        if min_len > 0:
            scores_data = {k: v[:min_len] for k, v in scores_data.items()}
            df = pd.DataFrame(scores_data)
            
            if not df.empty:
                st.subheader("Score Trends Over Time")
                st.line_chart(df.set_index("Date")[["Total Score", "Greeting", "Resolution", "Tone"]])
        
        # Average scores
        st.subheader("Average Scores by Metric")
        hold_times = [call.score.hold_time for call in scored_calls if call.score and call.score.hold_time is not None]
        compliances = [call.score.compliance for call in scored_calls if call.score and call.score.compliance is not None]
        
        avg_scores = {
            "Greeting": sum([call.score.greeting for call in scored_calls if call.score and call.score.greeting is not None]) / len(scored_calls) if scored_calls else 0,
            "Hold Time": sum(hold_times) / len(hold_times) if hold_times else 0,
            "Resolution": sum([call.score.resolution for call in scored_calls if call.score and call.score.resolution is not None]) / len(scored_calls) if scored_calls else 0,
            "Tone": sum([call.score.tone for call in scored_calls if call.score and call.score.tone is not None]) / len(scored_calls) if scored_calls else 0,
            "Compliance": sum(compliances) / len(compliances) if compliances else 0
        }
        
        avg_df = pd.DataFrame({
            "Metric": ["Greeting", "Hold Time", "Resolution", "Tone", "Compliance"],
            "Average Score": [
                avg_scores["Greeting"],
                avg_scores["Hold Time"],
                avg_scores["Resolution"],
                avg_scores["Tone"],
                avg_scores["Compliance"]
            ]
        })
        
        st.bar_chart(avg_df.set_index("Metric"))


if __name__ == "__main__":
    main()

