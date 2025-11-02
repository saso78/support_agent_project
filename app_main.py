"""
Main Streamlit App with Multi-Page Navigation.

Combines Support Agent and Call QA Tool in a single multi-page app.
Run with: streamlit run app_main.py
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Page configuration
st.set_page_config(
    page_title="Support Agent & Call QA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choose a page:",
    ["🤖 Support Agent", "📞 Call QA Tool"]
)

if page == "🤖 Support Agent":
    # Import and run Support Agent app
    from web.app import main as support_agent_main
    support_agent_main()
    
elif page == "📞 Call QA Tool":
    # Import and run Call QA dashboard
    from streamlit_pages.call_qa_dashboard import main as call_qa_main
    call_qa_main()

