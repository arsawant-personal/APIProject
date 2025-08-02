#!/usr/bin/env python3
"""
Server Management Script for SaaS API and Unified Console
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
        # Try lsof first
        result = subprocess.run(['lsof', '-ti', str(port)], 
                              capture_output=True, text=True)
        pids = result.stdout.strip().split('\n') if result.stdout.strip() else []
        pids = [pid for pid in pids if pid]
        
        # If lsof doesn't work, try socket connection
        if not pids:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                result = sock.connect_ex(('localhost', port))
                if result == 0:
                    # Port is in use, but we can't get PID with socket method
                    return ['unknown']
            except:
                pass
            finally:
                sock.close()
        
        return pids
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
        pids = check_port(port)
        if pids:  # Port is in use (server started)
            print(f"✅ Port {port} is now in use by PIDs: {pids}")
            return True
        time.sleep(0.5)
    print(f"❌ Port {port} did not become available within {timeout} seconds")
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
        
        # Wait for server to start (increased timeout for database connection)
        if wait_for_port(8000, timeout=30):
            print("✅ API server started successfully")
            return process
        else:
            print("❌ API server failed to start")
            process.terminate()
            return None
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_unified_console():
    """Start the unified console server"""
    print("🌐 Starting Unified Console server...")
    try:
        # Ensure port is free
        kill_processes_on_port(8082)
        
        # Wait a moment for port to be fully released
        time.sleep(1)
        
        unified_dir = Path(__file__).parent / "unified_console"
        process = subprocess.Popen([
            sys.executable, "server.py"
        ], cwd=unified_dir)
        
        # Wait for server to start
        if wait_for_port(8082, timeout=15):
            print("✅ Unified console started successfully")
            return process
        else:
            print("❌ Unified console failed to start")
            process.terminate()
            return None
    except Exception as e:
        print(f"❌ Failed to start unified console: {e}")
        return None

def show_status():
    """Show current server status"""
    print("📊 Server Status:")
    print("=" * 30)
    
    api_pids = check_port(8000)
    unified_pids = check_port(8082)
    
    if api_pids:
        print(f"✅ SaaS API (port 8000): Running (PIDs: {', '.join(api_pids)})")
    else:
        print("❌ SaaS API (port 8000): Not running")
    
    if unified_pids:
        print(f"✅ Unified Console (port 8082): Running (PIDs: {', '.join(unified_pids)})")
    else:
        print("❌ Unified Console (port 8082): Not running")

def stop_all():
    """Stop all servers"""
    print("🛑 Stopping all servers...")
    kill_processes_on_port(8000)
    kill_processes_on_port(8082)
    print("✅ All servers stopped")

def start_all():
    """Start all servers"""
    print("🎯 Starting SaaS API and Unified Console...")
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
    
    # Wait a moment before starting unified console
    time.sleep(2)
    
    # Start unified console
    unified_process = start_unified_console()
    if not unified_process:
        print("❌ Failed to start unified console")
        api_process.terminate()
        return
    
    print("\n🎉 All servers are running!")
    print("\n📋 Access URLs:")
    print("   - SaaS API: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Unified Console: http://localhost:8082")
    print("\n🔑 Login Credentials:")
    print("   Unified Console:")
    print("     - Super Admin: admin@yourcompany.com / your-super-admin-password")
    print("     - Automatically routes users based on role")
    print("\nPress Ctrl+C to stop all servers")
    print("=" * 40)
    
    try:
        # Wait for all processes
        api_process.wait()
        unified_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        api_process.terminate()
        unified_process.terminate()
        print("✅ Servers stopped")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_servers.py start [--debug] [--detailed] [--log-file] - Start both servers")
        print("  python manage_servers.py stop     - Stop all servers")
        print("  python manage_servers.py status   - Show server status")
        print("  python manage_servers.py restart  - Restart all servers")
        print("\nLogging Options:")
        print("  --debug     - Enable DEBUG level logging")
        print("  --detailed  - Enable detailed function call logging")
        print("  --log-file  - Enable logging to file (logs/app.log)")
        return
    
    command = sys.argv[1].lower()
    
    # Parse logging options
    enable_debug = "--debug" in sys.argv
    enable_detailed = "--detailed" in sys.argv
    enable_log_file = "--log-file" in sys.argv
    
    if command == "start":
        # Set environment variables for logging
        if enable_debug:
            os.environ["LOG_LEVEL"] = "DEBUG"
        if enable_detailed:
            os.environ["ENABLE_DETAILED_LOGGING"] = "true"
        if enable_log_file:
            os.environ["LOG_TO_FILE"] = "true"
        
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