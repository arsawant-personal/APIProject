#!/usr/bin/env python3
"""
Quick start script for SaaS API
This script checks the setup and starts the application.
"""

import os
import sys
import subprocess

def check_setup():
    """Check if the application is properly set up."""
    print("🔍 Checking setup...")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please run: python setup.py")
        return False
    
    # Check if virtual environment exists
    if not os.path.exists('venv'):
        print("❌ Virtual environment not found!")
        print("Please run: python setup.py")
        return False
    
    # Check if dependencies are installed
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("✅ Dependencies are installed")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ Setup looks good!")
    return True

def start_application():
    """Start the FastAPI application."""
    print("🚀 Starting SaaS API...")
    
    # Determine the correct Python executable
    if sys.platform == "win32":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    # Start the application
    try:
        subprocess.run([
            python_cmd, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")

def main():
    """Main function."""
    print("🎯 SaaS API Quick Start")
    print("=" * 30)
    
    if not check_setup():
        return
    
    print("\n📋 Application will be available at:")
    print("   - Main API: http://localhost:8000")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("\nPress Ctrl+C to stop the application")
    print("=" * 30)
    
    start_application()

if __name__ == "__main__":
    main() 