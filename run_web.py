"""
Launch script for the Streamlit web interface.
Run this script to start the web UI for the Support Agent.
"""

import subprocess
import sys
import signal
import webbrowser
from pathlib import Path

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    print("\nShutting down Support Agent Web Interface...")
    sys.exit(0)

def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Handle termination
    
    web_dir = Path(__file__).parent / 'web'
    app_path = web_dir / 'app.py'
    
    print("Starting Support Agent Web Interface...")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Start the Streamlit server
        process = subprocess.Popen([
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            str(app_path),
            "--server.port=8501",
            "--server.address=localhost"
        ])
        
        # Wait for the process to complete
        process.wait()
    except KeyboardInterrupt:
        print("\nShutting down Support Agent Web Interface...")
        process.terminate()
        try:
            # Wait for up to 5 seconds for the process to terminate
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # If it doesn't terminate within 5 seconds, force kill it
            process.kill()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # Ensure the process is terminated
        if process.poll() is None:
            process.kill()

if __name__ == "__main__":
    main()