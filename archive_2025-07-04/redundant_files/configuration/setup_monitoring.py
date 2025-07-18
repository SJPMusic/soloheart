#!/usr/bin/env python3
"""
Setup script for SoloHeart monitoring system
Installs dependencies and configures automatic startup.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def install_dependencies():
    """Install required Python dependencies."""
    print("📦 Installing Python dependencies...")
    
    dependencies = [
        'psutil',
        'requests',
        'flask',
        'ollama'
    ]
    
    for dep in dependencies:
        print(f"  Installing {dep}...")
        success, stdout, stderr = run_command(f"pip install {dep}")
        if success:
            print(f"  ✅ {dep} installed")
        else:
            print(f"  ❌ Failed to install {dep}: {stderr}")
            return False
    
    return True

def check_ollama():
    """Check and setup Ollama."""
    print("🤖 Checking Ollama...")
    
    # Check if Ollama is installed
    success, stdout, stderr = run_command("which ollama")
    if not success:
        print("  ❌ Ollama not found")
        print("  💡 Installing Ollama...")
        
        system = platform.system().lower()
        if system == "darwin":  # macOS
            success, stdout, stderr = run_command("brew install ollama")
        elif system == "linux":
            success, stdout, stderr = run_command("curl -fsSL https://ollama.ai/install.sh | sh")
        else:
            print("  ❌ Unsupported system for automatic Ollama installation")
            print("  💡 Please install Ollama manually from https://ollama.ai")
            return False
        
        if not success:
            print(f"  ❌ Failed to install Ollama: {stderr}")
            return False
    
    print("  ✅ Ollama found")
    
    # Start Ollama service
    print("  🚀 Starting Ollama...")
    success, stdout, stderr = run_command("ollama serve &")
    if not success:
        print(f"  ❌ Failed to start Ollama: {stderr}")
        return False
    
    # Wait a moment for Ollama to start
    import time
    time.sleep(3)
    
    # Pull the llama3 model
    print("  📥 Pulling llama3 model...")
    success, stdout, stderr = run_command("ollama pull llama3")
    if not success:
        print(f"  ❌ Failed to pull llama3 model: {stderr}")
        return False
    
    print("  ✅ Ollama setup complete")
    return True

def setup_autostart():
    """Setup automatic startup based on the operating system."""
    print("🚀 Setting up automatic startup...")
    
    system = platform.system().lower()
    current_dir = Path(__file__).parent.absolute()
    
    if system == "darwin":  # macOS
        return setup_macos_autostart(current_dir)
    elif system == "linux":
        return setup_linux_autostart(current_dir)
    else:
        print("  ⚠️ Automatic startup not supported on this system")
        print("  💡 You can manually start the game with: python launch_with_monitor.py")
        return True

def setup_macos_autostart(current_dir):
    """Setup macOS launchd service."""
    print("  🍎 Setting up macOS autostart...")
    
    # Create the plist file
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.soloheart.game</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{current_dir}/launch_with_monitor.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>{current_dir}</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>{current_dir}/logs/soloheart.log</string>
    
    <key>StandardErrorPath</key>
    <string>{current_dir}/logs/soloheart_error.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
    
    <key>ProcessType</key>
    <string>Background</string>
    
    <key>ThrottleInterval</key>
    <integer>10</integer>
    
    <key>ExitTimeOut</key>
    <integer>30</integer>
</dict>
</plist>"""
    
    # Write the plist file
    plist_path = current_dir / "com.soloheart.game.plist"
    with open(plist_path, 'w') as f:
        f.write(plist_content)
    
    # Copy to LaunchAgents
    launch_agents_dir = Path.home() / "Library/LaunchAgents"
    launch_agents_dir.mkdir(exist_ok=True)
    
    target_plist = launch_agents_dir / "com.soloheart.game.plist"
    shutil.copy2(plist_path, target_plist)
    
    # Load the service
    success, stdout, stderr = run_command(f"launchctl load {target_plist}")
    if success:
        print("  ✅ macOS autostart configured")
        print(f"  📁 Service file: {target_plist}")
        print("  💡 To start: launchctl start com.soloheart.game")
        print("  💡 To stop: launchctl stop com.soloheart.game")
        return True
    else:
        print(f"  ❌ Failed to load service: {stderr}")
        return False

def setup_linux_autostart(current_dir):
    """Setup Linux systemd service."""
    print("  🐧 Setting up Linux autostart...")
    
    # Create the service file
    service_content = f"""[Unit]
Description=SoloHeart Game Server with Monitor
After=network.target ollama.service
Wants=ollama.service

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={current_dir}
Environment=PATH={os.getenv('PATH', '/usr/local/bin:/usr/bin:/bin')}
ExecStart={sys.executable} {current_dir}/launch_with_monitor.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={current_dir}/logs {current_dir}/campaign_saves

# Resource limits
LimitNOFILE=65536
MemoryMax=2G

[Install]
WantedBy=multi-user.target"""
    
    # Write the service file
    service_path = current_dir / "soloheart.service"
    with open(service_path, 'w') as f:
        f.write(service_content)
    
    # Copy to systemd directory
    systemd_dir = Path("/etc/systemd/system")
    if not systemd_dir.exists():
        print("  ❌ Systemd directory not found")
        return False
    
    target_service = systemd_dir / "soloheart.service"
    try:
        shutil.copy2(service_path, target_service)
    except PermissionError:
        print("  ❌ Permission denied - run with sudo")
        print(f"  💡 Copy manually: sudo cp {service_path} {target_service}")
        return False
    
    # Reload systemd and enable service
    success, stdout, stderr = run_command("sudo systemctl daemon-reload")
    if not success:
        print(f"  ❌ Failed to reload systemd: {stderr}")
        return False
    
    success, stdout, stderr = run_command("sudo systemctl enable soloheart.service")
    if success:
        print("  ✅ Linux autostart configured")
        print(f"  📁 Service file: {target_service}")
        print("  💡 To start: sudo systemctl start soloheart")
        print("  💡 To stop: sudo systemctl stop soloheart")
        print("  💡 To check status: sudo systemctl status soloheart")
        return True
    else:
        print(f"  ❌ Failed to enable service: {stderr}")
        return False

def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    
    dirs = ['logs', 'campaign_saves', 'character_saves']
    current_dir = Path(__file__).parent
    
    for dir_name in dirs:
        dir_path = current_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"  ✅ Created {dir_path}")

def main():
    """Main setup function."""
    print("🎲 SoloHeart Monitoring Setup")
    print("=" * 40)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Check Ollama
    if not check_ollama():
        print("❌ Failed to setup Ollama")
        sys.exit(1)
    
    # Setup autostart
    if not setup_autostart():
        print("❌ Failed to setup autostart")
        sys.exit(1)
    
    print("\n✅ Setup complete!")
    print("\n🎮 To start the game:")
    print("  • Automatic: The game will start automatically on boot")
    print("  • Manual: python launch_with_monitor.py")
    print("\n📊 Monitoring features:")
    print("  • Auto-restart on failure")
    print("  • Health checks every 30 seconds")
    print("  • Logs in logs/server_monitor.log")
    print("\n🌐 Game will be available at: http://localhost:5001")

if __name__ == '__main__':
    main() 