#!/usr/bin/env python3
"""
Server Management Script for SaaS API and Admin Console
"""

import subprocess
import sys
import time
import os
import signal
import psutil
from pathlib import Path

def check_port(port):
    """Check if a port is in use and return PIDs"""
    try:
        result = subprocess.run(['lsof', '-ti', str(port)], 
                              capture_output=True, text=True)
        pids = result.stdout.strip().split('\n') if result.stdout.strip() else []
        return [pid for pid in pids if pid]
    except Exception:
        return []

def kill_processes_on_port(port):
    """Kill all processes on a specific port with force if needed"""
    pids = check_port(port)
    if pids:
        print(f"🛑 Stopping processes on port {port}...")
        for pid in pids:
            if pid:
                try:
                    # First try graceful termination
                    subprocess.run(['kill', pid], timeout=5)
                    time.sleep(0.5)
                    
                    # Check if process is still running
                    if psutil.pid_exists(int(pid)):
                        # Force kill if still running
                        subprocess.run(['kill', '-9', pid])
                        print(f"   Force killed process {pid}")
                    else:
                        print(f"   Killed process {pid}")
                except Exception as e:
                    print(f"   Failed to kill process {pid}: {e}")
                    # Try force kill as last resort
                    try:
                        subprocess.run(['kill', '-9', pid])
                        print(f"   Force killed process {pid}")
                    except:
                        pass
        time.sleep(1)
        
        # Verify port is free
        remaining_pids = check_port(port)
        if remaining_pids:
            print(f"⚠️  Warning: Port {port} still has processes: {remaining_pids}")
        else:
            print(f"✅ Port {port} is free")
    else:
        print(f"✅ Port {port} is free")

def wait_for_port(port, timeout=30):
    """Wait for a port to become available (server started)"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_port(port):  # Port is in use (server started)
            return True
        time.sleep(0.5)
    return False

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting SaaS API server...")
    try:
        # Ensure port is free
        kill_processes_on_port(8000)
        
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], cwd=Path(__file__).parent)
        
        # Wait for server to start
        if wait_for_port(8000, timeout=10):
            print("✅ API server started successfully")
            return process
        else:
            print("❌ API server failed to start")
            process.terminate()
            return None
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_admin_console():
    """Start the admin console server"""
    print("🌐 Starting Admin Console server...")
    try:
        # Ensure port is free
        kill_processes_on_port(8080)
        
        # Wait a moment for port to be fully released
        time.sleep(1)
        
        admin_dir = Path(__file__).parent / "admin_console"
        process = subprocess.Popen([
            sys.executable, "server.py"
        ], cwd=admin_dir)
        
        # Wait for server to start
        if wait_for_port(8080, timeout=10):
            print("✅ Admin console started successfully")
            return process
        else:
            print("❌ Admin console failed to start")
            process.terminate()
            return None
    except Exception as e:
        print(f"❌ Failed to start admin console: {e}")
        return None

def show_status():
    """Show current server status"""
    print("📊 Server Status:")
    print("=" * 30)
    
    api_pids = check_port(8000)
    admin_pids = check_port(8080)
    
    if api_pids:
        print(f"✅ SaaS API (port 8000): Running (PIDs: {', '.join(api_pids)})")
    else:
        print("❌ SaaS API (port 8000): Not running")
    
    if admin_pids:
        print(f"✅ Admin Console (port 8080): Running (PIDs: {', '.join(admin_pids)})")
    else:
        print("❌ Admin Console (port 8080): Not running")

def stop_all():
    """Stop all servers"""
    print("🛑 Stopping all servers...")
    kill_processes_on_port(8000)
    kill_processes_on_port(8080)
    print("✅ All servers stopped")

def start_all():
    """Start both servers"""
    print("🎯 Starting SaaS API and Admin Console...")
    print("=" * 40)
    
    # Stop any existing processes first
    stop_all()
    
    # Wait a moment for ports to be fully released
    time.sleep(2)
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Failed to start API server")
        return
    
    # Wait a moment before starting admin console
    time.sleep(2)
    
    # Start admin console
    admin_process = start_admin_console()
    if not admin_process:
        print("❌ Failed to start admin console")
        api_process.terminate()
        return
    
    print("\n🎉 Both servers are running!")
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

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_servers.py start    - Start both servers")
        print("  python manage_servers.py stop     - Stop all servers")
        print("  python manage_servers.py status   - Show server status")
        print("  python manage_servers.py restart  - Restart all servers")
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_all()
    elif command == "stop":
        stop_all()
    elif command == "status":
        show_status()
    elif command == "restart":
        stop_all()
        time.sleep(2)
        start_all()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: start, stop, status, restart")

if __name__ == "__main__":
    main() 