#!/usr/bin/env python3
"""
Setup script for SaaS API
This script automates the initial setup process.
"""

import os
import sys
import subprocess
import secrets
import string

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def generate_secret_key():
    """Generate a secure secret key."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def create_env_file():
    """Create .env file from template."""
    if os.path.exists('.env'):
        print("⚠️  .env file already exists, skipping...")
        return True
    
    if not os.path.exists('env.example'):
        print("❌ env.example not found!")
        return False
    
    # Read template
    with open('env.example', 'r') as f:
        content = f.read()
    
    # Generate secret key
    secret_key = generate_secret_key()
    content = content.replace('your-super-secret-key-here-change-this-in-production', secret_key)
    
    # Write .env file
    with open('.env', 'w') as f:
        f.write(content)
    
    print("✅ Created .env file with generated secret key")
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up SaaS API...")
    
    # Check if Python is available
    if not run_command("python --version", "Checking Python version"):
        return False
    
    # Create virtual environment
    if not os.path.exists('venv'):
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    else:
        print("⚠️  Virtual environment already exists")
    
    # Activate virtual environment and install dependencies
    if sys.platform == "win32":
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Initialize Alembic
    if not os.path.exists('alembic.ini'):
        if not run_command(f"{python_cmd} -m alembic init alembic", "Initializing Alembic"):
            return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your database settings")
    print("2. Set up PostgreSQL database")
    print("3. Run: python scripts/create_super_admin.py")
    print("4. Run: uvicorn app.main:app --reload")
    print("\n📖 See README.md for detailed instructions")

if __name__ == "__main__":
    main() 