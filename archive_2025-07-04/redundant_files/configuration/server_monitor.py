#!/usr/bin/env python3
"""
Server Monitor for SoloHeart
Provides robust monitoring, health checks, and auto-restart functionality.
"""

import os
import sys
import time
import signal
import subprocess
import threading
import requests
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/server_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ServerMonitor:
    """Monitors and manages the SoloHeart game server."""
    
    def __init__(self, port: int = 5001, ollama_port: int = 11434):
        self.port = port
        self.ollama_port = ollama_port
        self.server_process: Optional[subprocess.Popen] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.running = False
        self.restart_count = 0
        self.max_restarts = 10
        self.restart_cooldown = 30  # seconds
        self.last_restart_time = None
        self.health_check_interval = 30  # seconds
        self.server_script = 'simple_unified_interface.py'
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Statistics
        self.stats = {
            'start_time': datetime.now(),
            'restarts': 0,
            'health_checks': 0,
            'failed_health_checks': 0,
            'last_health_check': None,
            'uptime': timedelta(0)
        }
    
    def check_port_availability(self) -> bool:
        """Check if the server port is available."""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', self.port))
            sock.close()
            return result != 0  # Port is available if connection fails
        except Exception as e:
            logger.error(f"Error checking port availability: {e}")
            return False
    
    def kill_process_on_port(self) -> bool:
        """Kill any process using the server port."""
        try:
            # Find processes using the port
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    connections = proc.info['connections']
                    if connections:
                        for conn in connections:
                            if conn.laddr.port == self.port:
                                logger.info(f"Killing process {proc.info['pid']} using port {self.port}")
                                proc.terminate()
                                proc.wait(timeout=5)
                                return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    continue
            return False
        except Exception as e:
            logger.error(f"Error killing process on port: {e}")
            return False
    
    def check_ollama_health(self) -> bool:
        """Check if Ollama is running and healthy."""
        try:
            response = requests.get(f"http://localhost:{self.ollama_port}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model.get('name', '') for model in models]
                if 'llama3' in model_names or 'llama3:latest' in model_names:
                    return True
                else:
                    logger.warning("Ollama is running but llama3 model not found")
                    return False
            else:
                logger.error(f"Ollama health check failed with status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama - is it running?")
            return False
        except Exception as e:
            logger.error(f"Ollama health check error: {e}")
            return False
    
    def check_server_health(self) -> bool:
        """Check if the game server is responding."""
        try:
            response = requests.get(f"http://localhost:{self.port}/", timeout=10)
            if response.status_code == 200:
                # Check if it's actually our game server (look for SoloHeart in content)
                if 'SoloHeart' in response.text or 'game' in response.text.lower():
                    return True
                else:
                    logger.warning("Server responding but doesn't appear to be SoloHeart")
                    return False
            else:
                logger.error(f"Server health check failed with status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to game server")
            return False
        except Exception as e:
            logger.error(f"Server health check error: {e}")
            return False
    
    def start_server(self) -> bool:
        """Start the game server."""
        try:
            if self.server_process and self.server_process.poll() is None:
                logger.info("Server is already running")
                return True
            
            # Kill any existing process on the port
            if not self.check_port_availability():
                logger.info("Port is in use, killing existing process...")
                self.kill_process_on_port()
                time.sleep(2)
            
            # Check Ollama before starting
            if not self.check_ollama_health():
                logger.error("Ollama is not healthy - cannot start server")
                return False
            
            logger.info(f"Starting server: {self.server_script}")
            
            # Set environment variables
            env = os.environ.copy()
            env['FLASK_ENV'] = 'production'
            env['WERKZEUG_RUN_MAIN'] = 'true'  # Prevent Flask reloader issues
            
            # Start the server
            self.server_process = subprocess.Popen(
                [sys.executable, self.server_script],
                cwd=os.path.dirname(os.path.abspath(__file__)),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for the server to start
            time.sleep(5)
            
            # Check if the process is still running
            if self.server_process.poll() is not None:
                stdout, stderr = self.server_process.communicate()
                logger.error(f"Server failed to start. stdout: {stdout}, stderr: {stderr}")
                return False
            
            # Verify the server is responding
            if self.check_server_health():
                logger.info("✅ Server started successfully")
                self.restart_count = 0
                return True
            else:
                logger.error("Server started but health check failed")
                return False
                
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            return False
    
    def stop_server(self) -> bool:
        """Stop the game server."""
        try:
            if self.server_process and self.server_process.poll() is None:
                logger.info("Stopping server...")
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning("Server didn't stop gracefully, forcing...")
                    self.server_process.kill()
                    self.server_process.wait()
                logger.info("Server stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping server: {e}")
            return False
    
    def restart_server(self) -> bool:
        """Restart the game server."""
        try:
            # Check restart limits
            if self.restart_count >= self.max_restarts:
                logger.error(f"Maximum restart attempts ({self.max_restarts}) reached")
                return False
            
            # Check cooldown
            if self.last_restart_time:
                time_since_restart = (datetime.now() - self.last_restart_time).total_seconds()
                if time_since_restart < self.restart_cooldown:
                    logger.info(f"Restart cooldown active ({self.restart_cooldown - time_since_restart:.1f}s remaining)")
                    return False
            
            logger.info("🔄 Restarting server...")
            self.stop_server()
            time.sleep(2)
            
            success = self.start_server()
            if success:
                self.restart_count += 1
                self.last_restart_time = datetime.now()
                self.stats['restarts'] += 1
                logger.info(f"✅ Server restarted successfully (attempt {self.restart_count})")
            else:
                logger.error("❌ Server restart failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error restarting server: {e}")
            return False
    
    def health_check_loop(self):
        """Main health check loop."""
        logger.info("🔍 Starting health check loop...")
        
        while self.running:
            try:
                self.stats['health_checks'] += 1
                self.stats['last_health_check'] = datetime.now()
                
                # Check if server process is still running
                if self.server_process and self.server_process.poll() is not None:
                    logger.warning("Server process has died")
                    self.restart_server()
                    continue
                
                # Check server health
                if not self.check_server_health():
                    logger.warning("Server health check failed")
                    self.stats['failed_health_checks'] += 1
                    self.restart_server()
                    continue
                
                # Check Ollama health
                if not self.check_ollama_health():
                    logger.warning("Ollama health check failed")
                    # Don't restart server for Ollama issues, just log
                
                logger.debug("✅ Health check passed")
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
            
            # Wait for next health check
            time.sleep(self.health_check_interval)
    
    def start_monitoring(self):
        """Start the monitoring system."""
        try:
            logger.info("🚀 Starting SoloHeart Server Monitor...")
            self.running = True
            
            # Start the server
            if not self.start_server():
                logger.error("Failed to start server initially")
                return False
            
            # Start health check thread
            self.monitor_thread = threading.Thread(target=self.health_check_loop, daemon=True)
            self.monitor_thread.start()
            
            logger.info("✅ Server monitor started successfully")
            logger.info(f"🌐 Game available at: http://localhost:{self.port}")
            logger.info("📊 Health checks every 30 seconds")
            logger.info("🛑 Press Ctrl+C to stop")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting monitor: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        try:
            logger.info("🛑 Stopping server monitor...")
            self.running = False
            
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            
            self.stop_server()
            
            # Update final stats
            self.stats['uptime'] = datetime.now() - self.stats['start_time']
            
            logger.info("✅ Server monitor stopped")
            self._print_final_stats()
            
        except Exception as e:
            logger.error(f"Error stopping monitor: {e}")
    
    def _print_final_stats(self):
        """Print final statistics."""
        logger.info("📊 Final Statistics:")
        logger.info(f"   Uptime: {self.stats['uptime']}")
        logger.info(f"   Health checks: {self.stats['health_checks']}")
        logger.info(f"   Failed health checks: {self.stats['failed_health_checks']}")
        logger.info(f"   Restarts: {self.stats['restarts']}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status information."""
        return {
            'running': self.running,
            'server_running': self.server_process and self.server_process.poll() is None,
            'server_healthy': self.check_server_health() if self.server_process else False,
            'ollama_healthy': self.check_ollama_health(),
            'port_available': self.check_port_availability(),
            'restart_count': self.restart_count,
            'stats': self.stats.copy()
        }

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down...")
    if monitor:
        monitor.stop_monitoring()
    sys.exit(0)

if __name__ == '__main__':
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start monitor
    monitor = ServerMonitor()
    
    try:
        if monitor.start_monitoring():
            # Keep the main thread alive
            while monitor.running:
                time.sleep(1)
        else:
            logger.error("Failed to start monitoring")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if monitor:
            monitor.stop_monitoring() 