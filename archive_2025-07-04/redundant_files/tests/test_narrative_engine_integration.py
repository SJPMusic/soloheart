#!/usr/bin/env python3
"""
Test script for SoloHeart Narrative Engine Integration
Verifies that SoloHeart can successfully use The Narrative Engine.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add SoloHeart to the path
sys.path.insert(0, str(Path(__file__).parent / "SoloHeart"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_narrative_engine_import():
    """Test that we can import the Narrative Engine integration."""
    try:
        from narrative_engine_integration import SoloHeartNarrativeEngine
        logger.info("✅ Successfully imported SoloHeartNarrativeEngine")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import SoloHeartNarrativeEngine: {e}")
        return False

def test_narrative_engine_initialization():
    """Test that the Narrative Engine can be initialized."""
    try:
        from narrative_engine_integration import SoloHeartNarrativeEngine
        
        # Test initialization
        engine = SoloHeartNarrativeEngine(campaign_id="test_campaign")
        
        if engine.initialized:
            logger.info("✅ Narrative Engine initialized successfully")
            return True
        else:
            logger.error("❌ Narrative Engine failed to initialize")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error initializing Narrative Engine: {e}")
        return False

def test_campaign_initialization():
    """Test campaign initialization with character data."""
    try:
        from narrative_engine_integration import SoloHeartNarrativeEngine
        
        # Create test character data
        character_data = {
            "name": "Test Character",
            "race": "Human",
            "class": "Fighter",
            "level": 1,
            "background": "Soldier",
            "personality": "Brave and determined"
        }
        
        # Initialize engine and campaign
        engine = SoloHeartNarrativeEngine(campaign_id="test_campaign_2")
        campaign_data = engine.initialize_campaign(character_data, "Test Campaign")
        
        if campaign_data and "id" in campaign_data:
            logger.info(f"✅ Campaign initialized successfully: {campaign_data['id']}")
            logger.info(f"   Opening scene: {campaign_data.get('opening_scene', 'N/A')[:100]}...")
            return True
        else:
            logger.error("❌ Campaign initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in campaign initialization: {e}")
        return False

def test_player_input_processing():
    """Test processing player input through the Narrative Engine."""
    try:
        from narrative_engine_integration import SoloHeartNarrativeEngine
        
        # Initialize engine
        engine = SoloHeartNarrativeEngine(campaign_id="test_campaign_3")
        
        # Create test character and campaign
        character_data = {
            "name": "Adventurer",
            "race": "Elf",
            "class": "Ranger",
            "level": 1,
            "background": "Outlander"
        }
        
        campaign_data = engine.initialize_campaign(character_data, "Test Adventure")
        
        # Test player input processing
        test_inputs = [
            "I want to explore the forest",
            "I check for tracks",
            "I draw my bow and prepare for danger"
        ]
        
        for i, player_input in enumerate(test_inputs, 1):
            logger.info(f"\n--- Test Input {i}: '{player_input}' ---")
            
            response = engine.process_player_input(player_input, campaign_data)
            
            if response and len(response) > 10:
                logger.info(f"✅ Response {i}: {response[:100]}...")
            else:
                logger.error(f"❌ Invalid response {i}: {response}")
                return False
        
        logger.info("✅ All player input processing tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in player input processing: {e}")
        return False

def test_memory_integration():
    """Test that memory is being properly stored and retrieved."""
    try:
        from narrative_engine_integration import SoloHeartNarrativeEngine
        
        # Initialize engine
        engine = SoloHeartNarrativeEngine(campaign_id="test_campaign_4")
        
        # Create test character and campaign
        character_data = {
            "name": "Memory Test",
            "race": "Dwarf",
            "class": "Cleric",
            "level": 1
        }
        
        campaign_data = engine.initialize_campaign(character_data, "Memory Test Campaign")
        
        # Process some inputs to generate memories
        test_inputs = [
            "I find a magical key",
            "I meet a friendly dragon named Arkanoth",
            "I show the key to the guards"
        ]
        
        for player_input in test_inputs:
            engine.process_player_input(player_input, campaign_data)
        
        # Get campaign summary to check memory
        summary = engine.get_campaign_summary()
        
        if summary and "statistics" in summary:
            stats = summary["statistics"]
            logger.info(f"✅ Memory statistics: {stats}")
            
            if stats.get("total_memories", 0) > 0:
                logger.info("✅ Memory integration working correctly")
                return True
            else:
                logger.error("❌ No memories found")
                return False
        else:
            logger.error("❌ Failed to get campaign summary")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in memory integration test: {e}")
        return False

def test_soloheart_interface_integration():
    """Test that the SoloHeart interface can use the Narrative Engine."""
    try:
        from simple_unified_interface import SimpleNarrativeBridge
        
        # Initialize the narrative bridge
        bridge = SimpleNarrativeBridge()
        
        # Create test character data
        character_data = {
            "name": "Interface Test",
            "race": "Halfling",
            "class": "Rogue",
            "level": 1,
            "background": "Criminal"
        }
        
        # Initialize campaign
        campaign_data = bridge.initialize_campaign(character_data, "Interface Test Campaign")
        
        if campaign_data and "id" in campaign_data:
            campaign_id = campaign_data["id"]
            logger.info(f"✅ SoloHeart interface campaign initialized: {campaign_id}")
            
            # Test player input processing
            response = bridge.process_player_input("I sneak into the tavern", campaign_id)
            
            if response and len(response) > 10:
                logger.info(f"✅ SoloHeart interface response: {response[:100]}...")
                
                # Test saving
                if bridge.save_campaign(campaign_id):
                    logger.info("✅ SoloHeart interface save successful")
                    return True
                else:
                    logger.error("❌ SoloHeart interface save failed")
                    return False
            else:
                logger.error("❌ SoloHeart interface response invalid")
                return False
        else:
            logger.error("❌ SoloHeart interface campaign initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in SoloHeart interface integration: {e}")
        return False

def main():
    """Run all integration tests."""
    logger.info("🚀 Starting SoloHeart Narrative Engine Integration Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Narrative Engine Import", test_narrative_engine_import),
        ("Narrative Engine Initialization", test_narrative_engine_initialization),
        ("Campaign Initialization", test_campaign_initialization),
        ("Player Input Processing", test_player_input_processing),
        ("Memory Integration", test_memory_integration),
        ("SoloHeart Interface Integration", test_soloheart_interface_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 40)
        
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All integration tests passed! SoloHeart is ready to use The Narrative Engine.")
        return True
    else:
        logger.error(f"⚠️ {total - passed} tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 