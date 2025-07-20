#!/usr/bin/env python3
"""
TNEClient Usage Example

Demonstrates how to use the TNEClient class to interact with The Narrative Engine API.
"""

import logging
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.tne_client import TNEClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Demonstrate TNEClient usage."""
    print("🚀 TNEClient Usage Example")
    print("=" * 50)
    
    # Initialize the client
    client = TNEClient(
        base_url="http://localhost:5002",
        campaign_id="example_campaign"
    )
    
    print(f"✅ Client initialized for campaign: {client.get_campaign_id()}")
    print()
    
    # Test connection
    print("🔍 Testing connection to TNE API server...")
    connection_result = client.test_connection()
    print(f"Connection status: {connection_result['overall_status']}")
    
    if connection_result['overall_status'] == 'disconnected':
        print("❌ Cannot connect to TNE API server. Make sure it's running on localhost:5002")
        return
    
    print("✅ Connected to TNE API server!")
    print()
    
    # Add a memory entry
    print("📝 Adding memory entry...")
    memory_entry = {
        "text": "The brave warrior entered the ancient temple, sword drawn and ready for battle."
    }
    memory_result = client.add_memory_entry(memory_entry)
    
    if "error" in memory_result:
        print(f"❌ Failed to add memory: {memory_result['error']}")
    else:
        print(f"✅ Memory added: {memory_result['result']['message']}")
    print()
    
    # Add a scene
    print("🎬 Adding scene...")
    scene_data = {
        "text": "Inside the temple, the warrior discovered ancient runes glowing with magical energy."
    }
    scene_result = client.add_scene(scene_data)
    
    if "error" in scene_result:
        print(f"❌ Failed to add scene: {scene_result['error']}")
    else:
        print(f"✅ Scene added with ID: {scene_result['result']['scene_id']}")
    print()
    
    # Query concepts
    print("🔍 Querying symbolic concepts...")
    concepts_result = client.query_concepts()
    
    if "error" in concepts_result:
        print(f"❌ Failed to query concepts: {concepts_result['error']}")
    else:
        concepts = concepts_result['result']
        print(f"✅ Found {concepts['summary']['total_concepts']} concepts")
        print(f"   Conflicts: {concepts['summary']['total_conflicts']}")
    print()
    
    # Query identity
    print("👤 Querying identity information...")
    identity_result = client.query_identity()
    
    if "error" in identity_result:
        print(f"❌ Failed to query identity: {identity_result['error']}")
    else:
        identity = identity_result['result']
        print(f"✅ Identity profile: {len(identity['identity_profile'])} facts")
        print(f"   Contradictions: {len(identity['contradictions'])}")
        print(f"   Alignment score: {identity['alignment_score']:.2f}")
    print()
    
    # Get scene statistics
    print("📊 Getting scene statistics...")
    stats_result = client.get_scene_stats()
    
    if "error" in stats_result:
        print(f"❌ Failed to get scene stats: {stats_result['error']}")
    else:
        stats = stats_result['result']
        print(f"✅ Scene statistics:")
        print(f"   Total scenes: {stats['total_scenes']}")
        print(f"   Total identity facts: {stats['total_identity_facts']}")
        print(f"   Average facts per scene: {stats['average_facts_per_scene']:.1f}")
    print()
    
    # Get symbolic summary
    print("🔮 Getting symbolic summary...")
    summary_result = client.get_symbolic_summary()
    
    if "error" in summary_result:
        print(f"❌ Failed to get symbolic summary: {summary_result['error']}")
    else:
        summary = summary_result['result']
        profile = summary['identity_profile']
        print(f"✅ Symbolic summary:")
        print(f"   Total facts: {profile['total_facts']}")
        print(f"   Confidence score: {profile['confidence_score']:.2f}")
        print(f"   Fact categories: {list(profile['fact_categories'].keys())}")
    print()
    
    # Change campaign and test
    print("🔄 Testing campaign switching...")
    client.set_campaign_id("new_campaign")
    print(f"✅ Switched to campaign: {client.get_campaign_id()}")
    
    # Test health check
    print("🏥 Testing health check...")
    is_healthy = client.is_healthy()
    print(f"✅ Server health: {'Healthy' if is_healthy else 'Unhealthy'}")
    print()
    
    print("🎉 TNEClient example completed successfully!")


if __name__ == "__main__":
    main() 