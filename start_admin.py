#!/usr/bin/env python3
"""
Startup script for the SaaS API and Admin Console
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI dependencies found")
    except ImportError:
        print("❌ FastAPI not found. Please run: pip install -r requirements.txt")
        return False
    return True

def check_database():
    """Check if database is accessible"""
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        database_url = os.getenv('DATABASE_URL', 'postgresql://amit@localhost/saas_db')
        
        # Test database connection
        conn = psycopg2.connect(database_url)
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please make sure PostgreSQL is running and the database exists")
        return False

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting SaaS API server...")
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], cwd=Path(__file__).parent)
        return process
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_admin_console():
    """Start the admin console server"""
    print("🌐 Starting Admin Console server...")
    try:
        admin_dir = Path(__file__).parent / "admin_console"
        process = subprocess.Popen([
            sys.executable, "server.py"
        ], cwd=admin_dir)
        return process
    except Exception as e:
        print(f"❌ Failed to start admin console: {e}")
        return None

def main():
    """Main function"""
    print("🎯 SaaS API & Admin Console Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check database
    if not check_database():
        return
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        return
    
    # Wait a moment for API to start
    time.sleep(3)
    
    # Start admin console
    admin_process = start_admin_console()
    if not admin_process:
        api_process.terminate()
        return
    
    print("\n🎉 Both servers are starting up!")
    print("\n📋 Access URLs:")
    print("   - SaaS API: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Admin Console: http://localhost:8080")
    print("\n🔑 Admin Console Login:")
    print("   - Email: admin@yourcompany.com")
    print("   - Password: your-super-admin-password")
    print("\nPress Ctrl+C to stop both servers")
    print("=" * 40)
    
    try:
        # Wait for both processes
        api_process.wait()
        admin_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        api_process.terminate()
        admin_process.terminate()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main() 