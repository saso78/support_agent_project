"""
Launch script for the Streamlit web interface.
Run this script to start the web UI for the Support Agent.
"""

import subprocess
import sys
from pathlib import Path

def main():
    web_dir = Path(__file__).parent / 'web'
    app_path = web_dir / 'app.py'
    
    print("Starting Support Agent Web Interface...")
    subprocess.run([
        sys.executable, 
        "-m", 
        "streamlit", 
        "run", 
        str(app_path),
        "--server.port=8501",
        "--server.address=localhost"
    ])

if __name__ == "__main__":
    main()