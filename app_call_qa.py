"""
Streamlit App Entry Point for Call QA Tool.

This is the main entry point for deploying the Call QA Tool to Streamlit Cloud.
Run with: streamlit run app_call_qa.py
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import the dashboard main function
from streamlit_pages.call_qa_dashboard import main

if __name__ == "__main__":
    main()

