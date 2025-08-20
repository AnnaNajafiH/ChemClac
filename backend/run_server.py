#!/usr/bin/env python3
"""
Simple script to run the ChemCalc backend API server.
"""

import subprocess
import sys
import os

def main():
    """Run the FastAPI server with uvicorn."""
    try:
        # Change to the backend directory if not already there
        if not os.path.exists('main.py'):
            print("Error: main.py not found. Make sure you're in the backend directory.")
            sys.exit(1)
        
        # Check if uvicorn is installed
        try:
            import uvicorn
        except ImportError:
            print("Error: uvicorn is not installed. Please run 'pip install -r requirements.txt'")
            sys.exit(1)
        
        print("Starting ChemCalc Backend API Server...")
        print("API will be available at: http://localhost:8000")
        print("API Documentation: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Run the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
        
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
