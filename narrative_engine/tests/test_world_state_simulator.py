"""
Unit tests for WorldStateSimulator - Phase 3
============================================

Tests the enhanced world state tracking and simulation system.
Validates location state, timeline, NPC relationships, event flags, and campaign save/load.

References: The Narrative Engine.docx, Narrative_Engine_Comparative_Report.docx
"""

import unittest
import tempfile
import os
import json
import shutil
from datetime import datetime, timezone
from unittest.mock import patch

from narrative_engine.context.world_state_simulator import (
    WorldStateSimulator, LocationState, TimelineEvent, NPCRelationship
)


class TestWorldStateSimulator(unittest.TestCase):
    """Test suite for WorldStateSimulator Phase 3 functionality"""
    
    def setUp(self):
        """Set up test environment with temporary save directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.simulator = WorldStateSimulator(save_directory=self.temp_dir)
        self.campaign_id = "test_campaign"
        self.player_id = "player_character"
        self.npc_id = "test_npc"
        
        # Test location data
        self.location_data = {
            'name': 'Test Tavern',
            'description': 'A cozy tavern in the heart of the city',
            'environmental_state': {
                'lighting': 'dim',
                'atmosphere': 'warm',
                'noise_level': 'moderate'
            }
        }
        
        # Test NPC status
        self.npc_status = {
            'health': 100,
            'mood': 'friendly',
            'current_task': 'serving drinks'
        }

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def test_location_state_management(self):
        """Test enhanced location state tracking"""
        # Update location with metadata
        self.simulator.update_location(
            campaign_id=self.campaign_id,
            character_id=self.player_id,
            new_location="tavern_01",
            location_data=self.location_data
        )
        
        # Get location state
        location_state = self.simulator.get_location_state(self.campaign_id, "tavern_01")
        
        # Verify location state
        self.assertIsNotNone(location_state)
        self.assertEqual(location_state.location_id, "tavern_01")
        self.assertEqual(location_state.name, "Test Tavern")
        self.assertEqual(location_state.description, "A cozy tavern in the heart of the city")
        self.assertIn(self.player_id, location_state.current_occupants)
        self.assertIn(self.player_id, location_state.discovered_by)
        self.assertEqual(location_state.visit_count, 1)
        self.assertIsNotNone(location_state.last_visited)
        
        # Test environmental state
        self.assertEqual(location_state.environmental_state['lighting'], 'dim')
        self.assertEqual(location_state.environmental_state['atmosphere'], 'warm')

    def test_location_transition_tracking(self):
        """Test location transition with occupant tracking"""
        # Move player to tavern
        self.simulator.update_location(
            campaign_id=self.campaign_id,
            character_id=self.player_id,
            new_location="tavern_01",
            location_data=self.location_data
        )
        
        # Move NPC to same location
        self.simulator.update_location(
            campaign_id=self.campaign_id,
            character_id=self.npc_id,
            new_location="tavern_01",
            location_data=self.location_data
        )
        
        # Move player to new location
        self.simulator.update_location(
            campaign_id=self.campaign_id,
            character_id=self.player_id,
            new_location="market_01",
            location_data={'name': 'Market Square', 'description': 'Busy marketplace'}
        )
        
        # Check tavern occupants
        tavern_state = self.simulator.get_location_state(self.campaign_id, "tavern_01")
        self.assertIn(self.npc_id, tavern_state.current_occupants)
        self.assertNotIn(self.player_id, tavern_state.current_occupants)
        
        # Check market occupants
        market_state = self.simulator.get_location_state(self.campaign_id, "market_01")
        self.assertIn(self.player_id, market_state.current_occupants)
        self.assertNotIn(self.npc_id, market_state.current_occupants)

    def test_npc_status_tracking(self):
        """Test enhanced NPC status tracking"""
        # Update NPC status
        self.simulator.update_npc_status(
            campaign_id=self.campaign_id,
            npc_id=self.npc_id,
            status_dict=self.npc_status
        )
        
        # Get current state
        state = self.simulator.get_current_state(self.campaign_id)
        npc_statuses = state.get('npc_status', {})
        
        # Verify status
        self.assertIn(self.npc_id, npc_statuses)
        status = npc_statuses[self.npc_id]
        self.assertEqual(status['health'], 100)
        self.assertEqual(status['mood'], 'friendly')
        self.assertEqual(status['current_task'], 'serving drinks')
        self.assertIn('last_updated', status)

    def test_npc_relationship_management(self):
        """Test NPC relationship network"""
        # Add relationship between NPC and player
        self.simulator.add_npc_relationship(
            campaign_id=self.campaign_id,
            npc_id=self.npc_id,
            target_id=self.player_id,
            relationship_type="friend",
            strength=0.8,
            trust_level=0.7
        )
        
        # Add relationship between two NPCs
        self.simulator.add_npc_relationship(
            campaign_id=self.campaign_id,
            npc_id=self.npc_id,
            target_id="merchant_01",
            relationship_type="business_partner",
            strength=0.6,
            trust_level=0.8
        )
        
        # Get relationships for NPC
        relationships = self.simulator.get_npc_relationships(self.campaign_id, self.npc_id)
        
        # Verify relationships
        self.assertEqual(len(relationships), 2)
        
        # Check player relationship
        player_rel = next(r for r in relationships if r.target_id == self.player_id)
        self.assertEqual(player_rel.relationship_type, "friend")
        self.assertEqual(player_rel.strength, 0.8)
        self.assertEqual(player_rel.trust_level, 0.7)
        
        # Check merchant relationship
        merchant_rel = next(r for r in relationships if r.target_id == "merchant_01")
        self.assertEqual(merchant_rel.relationship_type, "business_partner")
        self.assertEqual(merchant_rel.strength, 0.6)
        self.assertEqual(merchant_rel.trust_level, 0.8)

    def test_faction_reputation_tracking(self):
        """Test faction reputation with history"""
        # Record faction changes
        self.simulator.record_faction_change(
            campaign_id=self.campaign_id,
            faction_id="merchants_guild",
            delta=10,
            reason="Completed trade mission"
        )
        
        self.simulator.record_faction_change(
            campaign_id=self.campaign_id,
            faction_id="merchants_guild",
            delta=-5,
            reason="Failed to deliver goods"
        )
        
        # Get current state
        state = self.simulator.get_current_state(self.campaign_id)
        factions = state.get('factions', {})
        
        # Verify faction data
        self.assertIn("merchants_guild", factions)
        faction = factions["merchants_guild"]
        self.assertEqual(faction['reputation'], 5)  # 10 - 5
        self.assertEqual(len(faction['history']), 2)
        
        # Check history entries
        history = faction['history']
        self.assertEqual(history[0]['change'], 10)
        self.assertEqual(history[0]['reason'], "Completed trade mission")
        self.assertEqual(history[1]['change'], -5)
        self.assertEqual(history[1]['reason'], "Failed to deliver goods")

    def test_event_flag_system(self):
        """Test event flag creation and triggering"""
        # Add event flag
        self.simulator.add_event_flag(
            campaign_id=self.campaign_id,
            flag_id="quest_start",
            name="Begin Main Quest",
            description="The player has been given the main quest",
            trigger_conditions=["talk_to_quest_giver"],
            consequences=["unlock_new_area", "spawn_quest_npc"]
        )
        
        # Get active flags
        active_flags = self.simulator.get_active_event_flags(self.campaign_id)
        self.assertEqual(len(active_flags), 1)
        
        flag = active_flags[0]
        self.assertEqual(flag.flag_id, "quest_start")
        self.assertEqual(flag.name, "Begin Main Quest")
        self.assertFalse(flag.is_triggered)
        self.assertEqual(len(flag.trigger_conditions), 1)
        self.assertEqual(len(flag.consequences), 2)
        
        # Trigger the flag
        self.simulator.trigger_event_flag(
            campaign_id=self.campaign_id,
            flag_id="quest_start",
            triggered_by=self.player_id
        )
        
        # Check that flag is now triggered
        active_flags = self.simulator.get_active_event_flags(self.campaign_id)
        self.assertEqual(len(active_flags), 0)
        
        # Check timeline event was created
        timeline_events = self.simulator.get_recent_timeline_events(self.campaign_id)
        self.assertEqual(len(timeline_events), 1)
        
        event = timeline_events[0]
        self.assertIn("Flag Triggered", event.name)
        self.assertEqual(event.event_type, "flag_trigger")
        self.assertEqual(len(event.consequences), 2)

    def test_timeline_event_tracking(self):
        """Test timeline event creation and retrieval"""
        # Add timeline events
        self.simulator.add_timeline_event(
            campaign_id=self.campaign_id,
            event_id="combat_01",
            name="Goblin Ambush",
            description="The party was ambushed by goblins in the forest",
            location_id="forest_path",
            involved_characters=[self.player_id, self.npc_id],
            event_type="combat"
        )
        
        self.simulator.add_timeline_event(
            campaign_id=self.campaign_id,
            event_id="social_01",
            name="Tavern Meeting",
            description="Met with the mysterious stranger in the tavern",
            location_id="tavern_01",
            involved_characters=[self.player_id],
            event_type="social"
        )
        
        # Get recent events
        events = self.simulator.get_recent_timeline_events(self.campaign_id, limit=5)
        
        # Verify events
        self.assertEqual(len(events), 2)
        
        # Events should be sorted by timestamp (newest first)
        self.assertGreater(events[0].timestamp, events[1].timestamp)
        
        # Check event details
        combat_event = next(e for e in events if e.event_id == "combat_01")
        self.assertEqual(combat_event.name, "Goblin Ambush")
        self.assertEqual(combat_event.location_id, "forest_path")
        self.assertEqual(combat_event.event_type, "combat")
        self.assertIn(self.player_id, combat_event.involved_characters)
        self.assertIn(self.npc_id, combat_event.involved_characters)

    def test_campaign_save_and_load(self):
        """Test campaign state persistence"""
        # Create some state
        self.simulator.update_location(
            campaign_id=self.campaign_id,
            character_id=self.player_id,
            new_location="tavern_01",
            location_data=self.location_data
        )
        
        self.simulator.update_npc_status(
            campaign_id=self.campaign_id,
            npc_id=self.npc_id,
            status_dict=self.npc_status
        )
        
        self.simulator.add_npc_relationship(
            campaign_id=self.campaign_id,
            npc_id=self.npc_id,
            target_id=self.player_id,
            relationship_type="friend",
            strength=0.8,
            trust_level=0.7
        )
        
        # Save state
        save_success = self.simulator.save_campaign_state(self.campaign_id)
        self.assertTrue(save_success)
        
        # Verify save file exists
        save_file = os.path.join(self.temp_dir, f"{self.campaign_id}_world_state.json")
        self.assertTrue(os.path.exists(save_file))
        
        # Create new simulator instance
        new_simulator = WorldStateSimulator(save_directory=self.temp_dir)
        
        # Load state
        load_success = new_simulator.load_campaign_state(self.campaign_id)
        self.assertTrue(load_success)
        
        # Verify state was restored
        state = new_simulator.get_current_state(self.campaign_id)
        
        # Check locations
        self.assertIn('locations', state)
        self.assertEqual(state['locations'][self.player_id], "tavern_01")
        
        # Check location states
        self.assertIn('location_states', state)
        tavern_state = state['location_states']['tavern_01']
        self.assertEqual(tavern_state['name'], "Test Tavern")
        self.assertIn(self.player_id, tavern_state['current_occupants'])
        
        # Check NPC status
        self.assertIn('npc_status', state)
        npc_status = state['npc_status'][self.npc_id]
        self.assertEqual(npc_status['health'], 100)
        self.assertEqual(npc_status['mood'], 'friendly')
        
        # Check relationships
        self.assertIn('npc_relationships', state)
        relationships = list(state['npc_relationships'].values())
        self.assertEqual(len(relationships), 1)
        relationship = relationships[0]
        self.assertEqual(relationship['npc_id'], self.npc_id)
        self.assertEqual(relationship['target_id'], self.player_id)
        self.assertEqual(relationship['relationship_type'], "friend")

    def test_json_compatibility(self):
        """Test that all state data is JSON serializable"""
        # Create comprehensive state
        self.simulator.update_location(
            campaign_id=self.campaign_id,
            character_id=self.player_id,
            new_location="tavern_01",
            location_data=self.location_data
        )
        
        self.simulator.add_npc_relationship(
            campaign_id=self.campaign_id,
            npc_id=self.npc_id,
            target_id=self.player_id,
            relationship_type="friend",
            strength=0.8,
            trust_level=0.7
        )
        
        self.simulator.add_event_flag(
            campaign_id=self.campaign_id,
            flag_id="test_flag",
            name="Test Flag",
            description="A test event flag"
        )
        
        self.simulator.add_timeline_event(
            campaign_id=self.campaign_id,
            event_id="test_event",
            name="Test Event",
            description="A test timeline event"
        )
        
        # Get state and verify JSON serialization
        state = self.simulator.get_current_state(self.campaign_id)
        
        # This should not raise any exceptions
        json_string = json.dumps(state, indent=2)
        self.assertIsInstance(json_string, str)
        
        # Verify we can deserialize
        deserialized = json.loads(json_string)
        self.assertEqual(deserialized['campaign_id'], self.campaign_id)

    def test_campaign_awareness(self):
        """Test that state is properly isolated between campaigns"""
        campaign_1 = "campaign_1"
        campaign_2 = "campaign_2"
        
        # Add data to campaign 1
        self.simulator.update_location(
            campaign_id=campaign_1,
            character_id=self.player_id,
            new_location="tavern_01",
            location_data=self.location_data
        )
        
        # Add data to campaign 2
        self.simulator.update_location(
            campaign_id=campaign_2,
            character_id=self.player_id,
            new_location="castle_01",
            location_data={'name': 'Castle', 'description': 'Royal castle'}
        )
        
        # Verify isolation
        state_1 = self.simulator.get_current_state(campaign_1)
        state_2 = self.simulator.get_current_state(campaign_2)
        
        self.assertEqual(state_1['locations'][self.player_id], "tavern_01")
        self.assertEqual(state_2['locations'][self.player_id], "castle_01")
        
        # Verify location states are different
        self.assertIn('tavern_01', state_1['location_states'])
        self.assertIn('castle_01', state_2['location_states'])
        self.assertNotIn('castle_01', state_1['location_states'])
        self.assertNotIn('tavern_01', state_2['location_states'])

    def test_thread_safety(self):
        """Test that the simulator is thread-safe"""
        import threading
        import time
        
        results = []
        errors = []
        
        def update_location(campaign_id, character_id, location):
            try:
                self.simulator.update_location(
                    campaign_id=campaign_id,
                    character_id=character_id,
                    new_location=location,
                    location_data={'name': f'Location {location}'}
                )
                results.append(f"Updated {character_id} to {location}")
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=update_location,
                args=(self.campaign_id, f"character_{i}", f"location_{i}")
            )
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 5)
        
        # Verify all updates were recorded
        state = self.simulator.get_current_state(self.campaign_id)
        locations = state.get('locations', {})
        self.assertEqual(len(locations), 5)
        
        for i in range(5):
            self.assertEqual(locations[f"character_{i}"], f"location_{i}")


if __name__ == '__main__':
    unittest.main() 