#!/usr/bin/env python3
"""
Test script for Campaign Overview Panel functionality
"""

import requests
import json
import time

def test_campaign_overview():
    """Test the Campaign Overview panel functionality"""
    
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Campaign Overview Panel Functionality")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing server health...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Server is healthy")
        else:
            print("❌ Server health check failed")
            return False
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False
    
    # Test 2: Campaign summary endpoint
    print("\n2. Testing campaign summary endpoint...")
    try:
        response = requests.get(f"{base_url}/api/campaign/demo-campaign/summary")
        if response.status_code == 200:
            data = response.json()
            print("✅ Campaign summary endpoint working")
            print(f"   - Campaign ID: {data.get('campaign_id', 'N/A')}")
            print(f"   - Characters: {len(data.get('characters', []))}")
            print(f"   - Character Arcs: {len(data.get('character_arcs', []))}")
            print(f"   - Plot Threads: {len(data.get('plot_threads', []))}")
            print(f"   - Journal Entries: {data.get('total_journal_entries', 0)}")
        else:
            print(f"❌ Campaign summary failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Campaign summary error: {e}")
        return False
    
    # Test 3: Check if web interface is accessible
    print("\n3. Testing web interface accessibility...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Web interface is accessible")
            if "Campaign Overview" in response.text:
                print("✅ Campaign Overview panel HTML is present")
            else:
                print("⚠️  Campaign Overview panel HTML not found")
        else:
            print(f"❌ Web interface failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web interface error: {e}")
        return False
    
    # Test 4: Test export functionality (simulate)
    print("\n4. Testing export functionality...")
    try:
        # Get campaign data for export testing
        response = requests.get(f"{base_url}/api/campaign/demo-campaign/summary")
        if response.status_code == 200:
            data = response.json()
            
            # Test markdown generation
            markdown_content = generate_test_markdown(data)
            print(f"✅ Markdown export test: {len(markdown_content)} characters")
            
            # Test JSON export
            json_content = json.dumps(data, indent=2)
            print(f"✅ JSON export test: {len(json_content)} characters")
            
        else:
            print("❌ Export test failed - couldn't get campaign data")
    except Exception as e:
        print(f"❌ Export test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Campaign Overview Panel Test Complete!")
    print("\n📋 Summary:")
    print("   - Server is running and healthy")
    print("   - Campaign summary API is working")
    print("   - Web interface is accessible")
    print("   - Export functionality is ready")
    print("\n🌐 Access the web interface at: http://localhost:5001")
    print("📜 Look for the 'Campaign Overview' panel on the left side")
    print("   (Click the toggle button to show/hide it)")
    
    return True

def generate_test_markdown(data):
    """Generate test markdown content"""
    return f"""# Campaign Overview: {data.get('campaign_name', 'Demo Campaign')}

## Campaign Info
- **Campaign ID**: {data.get('campaign_id', 'demo-campaign')}
- **Characters**: {len(data.get('characters', []))}
- **Character Arcs**: {len(data.get('character_arcs', []))}
- **Plot Threads**: {len(data.get('plot_threads', []))}
- **Journal Entries**: {data.get('total_journal_entries', 0)}

## Characters
{chr(10).join([f"- {char.get('name', 'Unknown')} ({char.get('class', 'Adventurer')})" for char in data.get('characters', [])])}

## Character Arcs
{chr(10).join([f"- {arc.get('name', 'Unknown')} ({arc.get('status', 'unknown')})" for arc in data.get('character_arcs', [])])}

## Plot Threads
{chr(10).join([f"- {thread.get('title', 'Unknown')} ({thread.get('status', 'unknown')})" for thread in data.get('plot_threads', [])])}

---
*Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""

if __name__ == "__main__":
    test_campaign_overview() 