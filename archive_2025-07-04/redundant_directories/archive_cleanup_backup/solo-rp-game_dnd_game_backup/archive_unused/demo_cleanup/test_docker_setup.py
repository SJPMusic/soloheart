#!/usr/bin/env python3
"""
Test script to verify Docker setup and environment variable handling
"""

import os
import sys
import requests
import time
from dotenv import load_dotenv

def test_environment_variables():
    """Test that environment variables are properly loaded."""
    print("🔍 Testing environment variable loading...")
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = [
        'OPENAI_API_KEY',
        'FLASK_SECRET_KEY',
        'FLASK_ENV'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f'your_{var.lower()}_here':
            missing_vars.append(var)
        else:
            print(f"  ✅ {var} is set")
    
    if missing_vars:
        print(f"  ⚠️ Missing or default values for: {', '.join(missing_vars)}")
        print("  Please update your .env file with actual values")
        return False
    
    print("  ✅ All required environment variables are properly configured")
    return True

def test_docker_health():
    """Test Docker container health endpoint."""
    print("\n🔍 Testing Docker container health...")
    
    try:
        # Try to connect to the health endpoint
        response = requests.get('http://localhost:5001/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Container is healthy: {data.get('status', 'unknown')}")
            print(f"  📊 Version: {data.get('version', 'unknown')}")
            return True
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Cannot connect to container. Is it running?")
        print("  💡 Try: ./docker-utils.sh run")
        return False
    except Exception as e:
        print(f"  ❌ Error testing health: {e}")
        return False

def test_api_endpoints():
    """Test basic API endpoints."""
    print("\n🔍 Testing API endpoints...")
    
    endpoints = [
        ('/api/health', 'Health Check'),
        ('/api/campaign/demo-campaign/summary', 'Campaign Summary'),
        ('/api/campaign/demo-campaign/lore', 'Lore Entries'),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f'http://localhost:5001{endpoint}', timeout=10)
            if response.status_code in [200, 404]:  # 404 is OK for demo campaign
                print(f"  ✅ {name}: {response.status_code}")
            else:
                print(f"  ⚠️ {name}: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {name}: {e}")

def main():
    """Run all Docker setup tests."""
    print("🚀 Testing Docker Setup for Narrative Engine")
    print("=" * 50)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    # Test Docker container
    docker_ok = test_docker_health()
    
    if docker_ok:
        test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Environment Variables: {'✅' if env_ok else '❌'}")
    print(f"  Docker Container: {'✅' if docker_ok else '❌'}")
    
    if env_ok and docker_ok:
        print("\n🎉 Docker setup is working correctly!")
        print("✨ You can now access the application at: http://localhost:5001")
    else:
        print("\n⚠️ Some tests failed. Please check the output above.")
        
        if not env_ok:
            print("\n🔧 To fix environment variables:")
            print("   1. Copy .env.template to .env")
            print("   2. Update .env with your actual values")
            
        if not docker_ok:
            print("\n🔧 To fix Docker container:")
            print("   1. Build: ./docker-utils.sh build")
            print("   2. Run: ./docker-utils.sh run")
            print("   3. Or use docker-compose: ./docker-utils.sh compose")

if __name__ == "__main__":
    main()
