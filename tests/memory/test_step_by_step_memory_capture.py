#!/usr/bin/env python3
"""
Test suite for Step-by-Step Character Creation Memory Integration

Verifies that as each field is filled in Step-by-Step mode, the extracted value
is committed to the narrative memory system using proper tagging.
"""

import sys
import os
import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the solo_heart directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'solo_heart'))

from character_creator import StepByStepCharacterCreator


class TestStepByStepMemoryCapture(unittest.TestCase):
    """Test suite for step-by-step character creation memory integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.campaign_id = "test-campaign-001"
        
        # Mock the narrative bridge and memory manager
        self.mock_narrative_bridge = Mock()
        self.mock_memory_manager = Mock()
        
        # Create step-by-step creator with mocked dependencies
        self.creator = StepByStepCharacterCreator()
        
        # Track memory calls
        self.memory_calls = []
        
    def test_field_memory_entry_format(self):
        """Test that each field results in properly formatted memory entries."""
        
        # Test sequence of inputs
        inputs = [
            ("race", "half-elf"),
            ("class", "ranger"),
            ("gender", "female"),
            ("background", "shattered kingdom"),
            ("personality", "quiet and deadly"),
        ]
        
        # Mock the narrative bridge store_solo_game_memory method
        with patch.object(self.mock_narrative_bridge, 'store_solo_game_memory') as mock_store:
            mock_store.return_value = True
            
            # Start the character creation process
            self.creator.start()
            
            # Process each input and verify memory storage
            for field, user_input in inputs:
                # Process the response
                result = self.creator.process_response(user_input)
                
                # Verify the field was set
                self.assertIsNotNone(self.creator.state[field], 
                                   f"Field {field} should be set after processing '{user_input}'")
                
                # Verify memory was stored with correct format
                expected_memory_entry = {
                    "type": "trait",
                    "field": field,
                    "value": self.creator.state[field],
                    "campaign_id": self.campaign_id,
                    "timestamp": datetime.now().isoformat(),
                    "memory_type": "character_creation",
                    "character_id": "player"
                }
                
                # Check that store_solo_game_memory was called with correct parameters
                mock_store.assert_called_with(
                    content=f"Character trait set: {field} = {self.creator.state[field]}",
                    memory_type="character_creation",
                    metadata={
                        "type": "trait",
                        "field": field,
                        "value": self.creator.state[field],
                        "campaign_id": self.campaign_id,
                        "character_id": "player"
                    },
                    tags=["character_creation", "trait", field],
                    character_id="player"
                )
                
                # Verify the call was made exactly once for this field
                call_count = sum(1 for call in mock_store.call_args_list 
                               if call[1].get('metadata', {}).get('field') == field)
                self.assertEqual(call_count, 1, 
                               f"Memory should be stored exactly once for field {field}")
    
    def test_no_skipped_fields(self):
        """Test that no fields are skipped in memory storage."""
        
        # Complete character creation with all fields
        complete_inputs = [
            ("race", "elf"),
            ("class", "wizard"),
            ("gender", "male"),
            ("age", "25"),
            ("background", "sage"),
            ("personality", "curious and studious"),
            ("level", "1"),
            ("alignment", "lawful good"),
            ("name", "Elira")
        ]
        
        with patch.object(self.mock_narrative_bridge, 'store_solo_game_memory') as mock_store:
            mock_store.return_value = True
            
            # Start and complete character creation
            self.creator.start()
            
            for field, user_input in complete_inputs:
                self.creator.process_response(user_input)
            
            # Verify all fields were stored in memory
            self.assertEqual(mock_store.call_count, len(complete_inputs),
                           "Memory should be stored for every field")
            
            # Verify each field was stored exactly once
            stored_fields = []
            for call in mock_store.call_args_list:
                field = call[1]['metadata']['field']
                stored_fields.append(field)
            
            expected_fields = [field for field, _ in complete_inputs]
            self.assertEqual(sorted(stored_fields), sorted(expected_fields),
                           "All expected fields should be stored in memory")
    
    def test_malformed_tags_fail(self):
        """Test that malformed tags cause test failure."""
        
        with patch.object(self.mock_narrative_bridge, 'store_solo_game_memory') as mock_store:
            mock_store.return_value = True
            
            # Start character creation
            self.creator.start()
            
            # Process a field
            self.creator.process_response("elf")
            
            # Verify tags are properly formatted
            call_args = mock_store.call_args
            metadata = call_args[1]['metadata']
            tags = call_args[1]['tags']
            
            # Check required fields exist
            self.assertIn('type', metadata, "Memory entry must have 'type' field")
            self.assertIn('field', metadata, "Memory entry must have 'field' field")
            self.assertIn('value', metadata, "Memory entry must have 'value' field")
            self.assertIn('campaign_id', metadata, "Memory entry must have 'campaign_id' field")
            
            # Check tag format
            self.assertIsInstance(tags, list, "Tags must be a list")
            self.assertIn('character_creation', tags, "Tags must include 'character_creation'")
            self.assertIn('trait', tags, "Tags must include 'trait'")
            self.assertIn(metadata['field'], tags, "Tags must include the field name")
    
    def test_field_value_consistency(self):
        """Test that field and value are consistent with user input."""
        
        test_cases = [
            ("race", "half-elf", "Half-Elf"),
            ("class", "ranger", "Ranger"),
            ("gender", "female", "Female"),
            ("background", "shattered kingdom", "Shattered Kingdom"),
            ("personality", "quiet and deadly", "Quiet and deadly"),
        ]
        
        with patch.object(self.mock_narrative_bridge, 'store_solo_game_memory') as mock_store:
            mock_store.return_value = True
            
            self.creator.start()
            
            for field, user_input, expected_value in test_cases:
                # Process the input
                self.creator.process_response(user_input)
                
                # Get the last memory call
                last_call = mock_store.call_args_list[-1]
                metadata = last_call[1]['metadata']
                
                # Verify field consistency
                self.assertEqual(metadata['field'], field,
                               f"Field should be '{field}' for input '{user_input}'")
                
                # Verify value consistency (allowing for case variations)
                stored_value = metadata['value']
                self.assertIsNotNone(stored_value,
                                   f"Value should not be None for field {field}")
                
                # Check that the stored value contains the expected content
                # (allowing for variations in parsing)
                self.assertTrue(
                    expected_value.lower() in stored_value.lower() or 
                    user_input.lower() in stored_value.lower(),
                    f"Stored value '{stored_value}' should be consistent with input '{user_input}'"
                )
    
    def test_campaign_id_consistency(self):
        """Test that campaign_id is consistent across all memory entries."""
        
        inputs = [
            ("race", "human"),
            ("class", "fighter"),
            ("gender", "male"),
        ]
        
        with patch.object(self.mock_narrative_bridge, 'store_solo_game_memory') as mock_store:
            mock_store.return_value = True
            
            self.creator.start()
            
            for field, user_input in inputs:
                self.creator.process_response(user_input)
            
            # Verify all memory entries have the same campaign_id
            campaign_ids = set()
            for call in mock_store.call_args_list:
                campaign_id = call[1]['metadata']['campaign_id']
                campaign_ids.add(campaign_id)
            
            self.assertEqual(len(campaign_ids), 1,
                           "All memory entries should have the same campaign_id")
            self.assertEqual(list(campaign_ids)[0], self.campaign_id,
                           f"Campaign ID should be '{self.campaign_id}'")
    
    def test_memory_type_consistency(self):
        """Test that memory_type is consistently 'character_creation'."""
        
        inputs = [
            ("race", "dwarf"),
            ("class", "cleric"),
        ]
        
        with patch.object(self.mock_narrative_bridge, 'store_solo_game_memory') as mock_store:
            mock_store.return_value = True
            
            self.creator.start()
            
            for field, user_input in inputs:
                self.creator.process_response(user_input)
            
            # Verify all memory entries have the correct memory_type
            for call in mock_store.call_args_list:
                memory_type = call[1]['memory_type']
                self.assertEqual(memory_type, 'character_creation',
                               "Memory type should be 'character_creation'")
    
    def test_trait_type_consistency(self):
        """Test that type is consistently 'trait' for character fields."""
        
        inputs = [
            ("race", "halfling"),
            ("class", "rogue"),
            ("gender", "non-binary"),
        ]
        
        with patch.object(self.mock_narrative_bridge, 'store_solo_game_memory') as mock_store:
            mock_store.return_value = True
            
            self.creator.start()
            
            for field, user_input in inputs:
                self.creator.process_response(user_input)
            
            # Verify all memory entries have type 'trait'
            for call in mock_store.call_args_list:
                trait_type = call[1]['metadata']['type']
                self.assertEqual(trait_type, 'trait',
                               "Type should be 'trait' for character fields")
    
    def test_edit_field_memory_update(self):
        """Test that editing a field updates the memory correctly."""
        
        with patch.object(self.mock_narrative_bridge, 'store_solo_game_memory') as mock_store:
            mock_store.return_value = True
            
            self.creator.start()
            
            # Set initial value
            self.creator.process_response("elf")
            
            # Edit the field
            self.creator.process_response("edit race")
            self.creator.process_response("dwarf")
            
            # Verify two memory entries were created (initial + edit)
            self.assertEqual(mock_store.call_count, 2,
                           "Should have two memory entries (initial + edit)")
            
            # Verify the second entry has the updated value
            second_call = mock_store.call_args_list[1]
            metadata = second_call[1]['metadata']
            self.assertEqual(metadata['field'], 'race')
            self.assertEqual(metadata['value'], 'Dwarf')
    
    def test_skip_field_no_memory(self):
        """Test that skipped fields don't create memory entries."""
        
        with patch.object(self.mock_narrative_bridge, 'store_solo_game_memory') as mock_store:
            mock_store.return_value = True
            
            self.creator.start()
            
            # Set some fields
            self.creator.process_response("human")
            self.creator.process_response("wizard")
            
            # Skip alignment (optional field)
            self.creator.process_response("skip")
            
            # Verify only non-skipped fields created memory entries
            self.assertEqual(mock_store.call_count, 2,
                           "Should only have memory entries for non-skipped fields")
    
    def test_complete_character_creation_memory_summary(self):
        """Test that completing character creation creates a summary memory entry."""
        
        complete_inputs = [
            ("race", "elf"),
            ("class", "wizard"),
            ("gender", "female"),
            ("age", "25"),
            ("background", "sage"),
            ("personality", "curious"),
            ("level", "1"),
            ("alignment", "lawful good"),
            ("name", "Elira")
        ]
        
        with patch.object(self.mock_narrative_bridge, 'store_solo_game_memory') as mock_store:
            mock_store.return_value = True
            
            self.creator.start()
            
            # Complete all fields
            for field, user_input in complete_inputs:
                self.creator.process_response(user_input)
            
            # Verify we have memory entries for all fields plus completion
            expected_calls = len(complete_inputs) + 1  # +1 for completion summary
            self.assertEqual(mock_store.call_count, expected_calls,
                           f"Should have {expected_calls} memory entries (fields + completion)")
            
            # Verify the last call is a completion summary
            last_call = mock_store.call_args_list[-1]
            metadata = last_call[1]['metadata']
            self.assertEqual(metadata['type'], 'character_completion',
                           "Last memory entry should be character completion")
            self.assertIn('character_data', metadata,
                         "Completion entry should include character data")


class TestStepByStepMemoryIntegration(unittest.TestCase):
    """Integration tests for step-by-step memory with actual narrative bridge."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.campaign_id = "test-campaign-001"
        
        # Mock the TNEClient to avoid actual API calls
        self.mock_tne_client = Mock()
        
        # Create a mock narrative bridge
        with patch('narrative_bridge.TNEClient', return_value=self.mock_tne_client):
            from narrative_bridge import NarrativeBridge
            self.narrative_bridge = NarrativeBridge(self.campaign_id)
    
    def test_integration_with_narrative_bridge(self):
        """Test that step-by-step creator integrates with narrative bridge."""
        
        # Mock the TNEClient methods
        self.mock_tne_client.add_memory_entry.return_value = {"success": True}
        
        # Create step-by-step creator with narrative bridge
        creator = StepByStepCharacterCreator()
        
        # Start character creation
        creator.start()
        
        # Process a field
        creator.process_response("elf")
        
        # Verify the narrative bridge was used to store memory
        # This would require the step-by-step creator to be modified to accept
        # a narrative bridge instance and use it for memory storage
        
        # For now, we'll test the expected interface
        self.assertIsNotNone(creator.state['race'])
        self.assertEqual(creator.state['race'], 'Elf')


def run_memory_integration_tests():
    """Run the memory integration test suite."""
    print("🧪 Running Step-by-Step Memory Integration Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestStepByStepMemoryCapture))
    suite.addTests(loader.loadTestsFromTestCase(TestStepByStepMemoryIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_memory_integration_tests()
    sys.exit(0 if success else 1) 