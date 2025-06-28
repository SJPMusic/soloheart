#!/usr/bin/env python3
"""
Setup script for The Narrative Engine
====================================

Installs dependencies and sets up the environment for The Narrative Engine.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    # Determine the pip command based on the platform
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
    
    try:
        # Upgrade pip first
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = [
        "data",
        "exports",
        "logs",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created")

def create_config_file():
    """Create a default configuration file."""
    config_path = Path("config/config.json")
    
    if config_path.exists():
        print("✅ Configuration file already exists")
        return True
    
    config_content = {
        "memory": {
            "short_term_max": 50,
            "mid_term_max": 1000,
            "long_term_max": 10000,
            "forget_threshold": 0.1
        },
        "analysis": {
            "cache_enabled": True,
            "cache_ttl": 3600
        },
        "logging": {
            "level": "INFO",
            "file": "logs/narrative_engine.log"
        }
    }
    
    try:
        import json
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config_content, f, indent=2)
        print("✅ Configuration file created")
        return True
    except Exception as e:
        print(f"❌ Failed to create configuration file: {e}")
        return False

def run_tests():
    """Run basic tests to verify installation."""
    print("🧪 Running tests...")
    
    # Determine the python command based on the platform
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "venv/bin/python"
    
    try:
        # Run the test file
        result = subprocess.run([python_cmd, "tests/test_narrative_engine.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tests passed")
            return True
        else:
            print("⚠️  Tests had issues:")
            print(result.stdout)
            print(result.stderr)
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def run_demo():
    """Run the demo to showcase functionality."""
    print("🚀 Running demo...")
    
    # Determine the python command based on the platform
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "venv/bin/python"
    
    try:
        subprocess.run([python_cmd, "examples/demo.py"], check=True)
        print("✅ Demo completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Demo failed: {e}")
        return False

def print_activation_instructions():
    """Print instructions for activating the virtual environment."""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    
    if os.name == 'nt':  # Windows
        print("\nTo activate the virtual environment:")
        print("  venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("\nTo activate the virtual environment:")
        print("  source venv/bin/activate")
    
    print("\nTo run the demo:")
    print("  python examples/demo.py")
    
    print("\nTo run tests:")
    print("  python tests/test_narrative_engine.py")
    
    print("\nTo start using The Narrative Engine:")
    print("  python")
    print("  >>> from core.narrative_engine import NarrativeEngine")
    print("  >>> engine = NarrativeEngine()")
    print("  >>> narrative = engine.create_narrative('My Story', 'A test narrative', 'gaming')")
    
    print("\n📚 Documentation:")
    print("  - README.md: Overview and quick start")
    print("  - docs/API.md: Complete API documentation")
    print("  - examples/demo.py: Working examples")
    
    print("\n🔧 Configuration:")
    print("  - Edit config/config.json to customize settings")
    
    print("\n" + "="*60)

def main():
    """Main setup function."""
    print("🚀 The Narrative Engine Setup")
    print("="*40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create configuration
    if not create_config_file():
        print("⚠️  Continuing without configuration file")
    
    # Run tests
    if not run_tests():
        print("⚠️  Tests failed, but continuing with setup")
    
    # Run demo
    if not run_demo():
        print("⚠️  Demo failed, but setup is complete")
    
    # Print instructions
    print_activation_instructions()

if __name__ == "__main__":
    main() 