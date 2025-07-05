# SoloHeart Monitoring System

This monitoring system ensures that your SoloHeart game server never stops working. It provides automatic restart, health checks, and robust error handling.

## Features

- 🔄 **Auto-restart**: Automatically restarts the server if it crashes or becomes unresponsive
- 🔍 **Health checks**: Monitors server health every 30 seconds
- 🤖 **Ollama monitoring**: Ensures Ollama is running and has the required model
- 📊 **Comprehensive logging**: Detailed logs for troubleshooting
- 🚀 **Automatic startup**: Can be configured to start automatically on boot
- 🛡️ **Process management**: Kills conflicting processes and manages port conflicts

## Quick Start

### 1. Install the monitoring system

```bash
cd solo_heart
python setup_monitoring.py
```

This will:
- Install required dependencies
- Set up Ollama if not already installed
- Configure automatic startup
- Create necessary directories

### 2. Start the game with monitoring

```bash
python launch_with_monitor.py
```

This launches the game with full monitoring and auto-restart capabilities.

### 3. Check status

```bash
python check_status.py
```

This quickly checks if everything is running properly.

## Manual Setup

If you prefer to set up manually:

### Install Dependencies

```bash
pip install psutil requests flask ollama
```

### Start Ollama

```bash
# Install Ollama (if not already installed)
brew install ollama  # macOS
# or
curl -fsSL https://ollama.ai/install.sh | sh  # Linux

# Start Ollama
ollama serve &

# Pull the required model
ollama pull llama3
```

### Start the Monitor

```bash
python server_monitor.py
```

## Automatic Startup

### macOS

The setup script creates a launchd service that starts automatically on boot:

```bash
# Check if service is loaded
launchctl list | grep soloheart

# Start the service
launchctl start com.soloheart.game

# Stop the service
launchctl stop com.soloheart.game

# Unload the service
launchctl unload ~/Library/LaunchAgents/com.soloheart.game.plist
```

### Linux

The setup script creates a systemd service:

```bash
# Check service status
sudo systemctl status soloheart

# Start the service
sudo systemctl start soloheart

# Stop the service
sudo systemctl stop soloheart

# Enable auto-start on boot
sudo systemctl enable soloheart

# Disable auto-start on boot
sudo systemctl disable soloheart
```

## Monitoring Features

### Health Checks

The monitor performs several health checks every 30 seconds:

1. **Server Process**: Checks if the Flask server process is still running
2. **Server Response**: Verifies the server responds to HTTP requests
3. **Ollama Health**: Ensures Ollama is running and has the llama3 model
4. **Port Availability**: Checks for port conflicts

### Auto-Restart Logic

The monitor will automatically restart the server when:

- The server process dies unexpectedly
- The server stops responding to health checks
- Port conflicts are detected

Restart limits:
- Maximum 10 restarts
- 30-second cooldown between restarts
- Detailed logging of all restart attempts

### Logging

All monitoring activity is logged to:

- `logs/server_monitor.log` - Main monitor log
- `logs/soloheart.log` - Server output (macOS)
- `logs/soloheart_error.log` - Server errors (macOS)

## Troubleshooting

### Server Won't Start

1. Check if port 5001 is in use:
   ```bash
   lsof -i :5001
   ```

2. Check Ollama status:
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. Check logs:
   ```bash
   tail -f logs/server_monitor.log
   ```

### Server Keeps Restarting

1. Check the restart count and cooldown:
   ```bash
   python check_status.py
   ```

2. Look for error patterns in logs:
   ```bash
   grep "ERROR" logs/server_monitor.log
   ```

3. Check if Ollama is stable:
   ```bash
   ps aux | grep ollama
   ```

### Performance Issues

The monitor includes resource limits:

- Memory limit: 2GB
- File descriptor limit: 65536
- Automatic cleanup of zombie processes

## API Endpoints

The server includes a health check endpoint:

```bash
curl http://localhost:5001/api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "ollama_healthy": true,
  "game_healthy": true,
  "version": "1.0.0"
}
```

## Configuration

### Environment Variables

- `FLASK_ENV`: Set to 'production' for monitoring
- `WERKZEUG_RUN_MAIN`: Set to 'true' to prevent Flask reloader issues

### Monitor Settings

You can modify these settings in `server_monitor.py`:

- `health_check_interval`: How often to check health (default: 30 seconds)
- `max_restarts`: Maximum restart attempts (default: 10)
- `restart_cooldown`: Time between restarts (default: 30 seconds)

## Security

The monitoring system includes several security features:

- Process isolation
- Resource limits
- Secure file permissions
- No privilege escalation

## Support

If you encounter issues:

1. Check the logs in `logs/server_monitor.log`
2. Run `python check_status.py` for a quick diagnosis
3. Ensure Ollama is running: `ollama serve`
4. Verify the llama3 model is available: `ollama list`

## Files

- `server_monitor.py` - Main monitoring system
- `launch_with_monitor.py` - Launcher with monitoring
- `setup_monitoring.py` - Setup script
- `check_status.py` - Status checker
- `soloheart.service` - Linux systemd service
- `com.soloheart.game.plist` - macOS launchd service

This monitoring system ensures your SoloHeart game is always available and automatically recovers from any issues. 