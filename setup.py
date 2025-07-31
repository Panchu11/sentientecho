#!/usr/bin/env python3
"""
SentientEcho Setup Script
Validates environment and prepares for deployment.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_environment_variables():
    """Check if required environment variables are set."""
    required_vars = [
        "FIREWORKS_API_KEY",
        "FIREWORKS_MODEL_ID", 
        "SERPER_API_KEY",
        "JINA_AI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var} is set")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file or environment")
        return False
    
    return True

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def validate_config():
    """Validate configuration."""
    print("🔧 Validating configuration...")
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from config import validate_config
        validate_config()
        print("✅ Configuration is valid")
        return True
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def test_basic_functionality():
    """Test basic agent functionality."""
    print("🧪 Testing basic functionality...")
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from sentient_echo_agent import SentientEchoAgent
        
        # Try to create agent
        agent = SentientEchoAgent("SentientEcho")
        print("✅ Agent creation successful")
        return True
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 SentientEcho Setup & Validation")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment Variables", check_environment_variables),
        ("Dependencies", install_dependencies),
        ("Configuration", validate_config),
        ("Basic Functionality", test_basic_functionality),
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}...")
        if not check_func():
            failed_checks.append(check_name)
    
    print("\n" + "=" * 50)
    if failed_checks:
        print(f"❌ Setup failed. Failed checks: {', '.join(failed_checks)}")
        print("\nPlease fix the issues above and run setup again.")
        sys.exit(1)
    else:
        print("🎉 Setup completed successfully!")
        print("\n🚀 SentientEcho is ready for deployment!")
        print("\nNext steps:")
        print("1. Start the agent: python src/main.py")
        print("2. Or use Docker: docker-compose up")
        print("3. Test at: http://localhost:8000/health")

if __name__ == "__main__":
    main()
