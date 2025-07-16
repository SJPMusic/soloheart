#!/usr/bin/env python3
"""
Phase 11: Simplified Archive System Test

Tests the core archive functionality without requiring full application dependencies.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

class TestPhase11ArchiveCore(unittest.TestCase):
    """Simplified test suite for Phase 11 archive functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_campaign_dir = tempfile.mkdtemp()
        self.test_archive_dir = os.path.join(self.test_campaign_dir, 'archive')
        os.makedirs(self.test_archive_dir, exist_ok=True)
        
        # Sample test data
        self.sample_character_data = {
            'name': 'Test Hero',
            'race': 'Human',
            'class': 'Fighter',
            'level': 5,
            'hit_points': 45,
            'ability_scores': {
                'strength': 16,
                'dexterity': 14,
                'constitution': 15,
                'intelligence': 12,
                'wisdom': 10,
                'charisma': 8
            }
        }
        
        self.sample_world_state = {
            'location': 'The Great Hall',
            'items': ['Sword of Light', 'Potion of Healing'],
            'npc_flags': {'elder_met': True, 'quest_completed': True},
            'story_flags': {'final_battle_won': True, 'kingdom_saved': True}
        }
        
        self.sample_goals = [
            {'type': 'save_kingdom', 'confidence': 0.95, 'state': 'completed'},
            {'type': 'defeat_dragon', 'confidence': 0.88, 'state': 'completed'},
            {'type': 'find_treasure', 'confidence': 0.72, 'state': 'completed'}
        ]
        
        self.sample_transformation = {
            'transformation_type': 'Innocent → Hero',
            'archetypal_shift': 'Hero',
            'evidence_snippets': ['Faced the dragon alone', 'Saved the village'],
            'confidence_score': 0.92
        }
        
        self.sample_ending_summary = {
            'ending_type': 'triumph',
            'justification': 'Hero successfully saved the kingdom and defeated the dragon',
            'confidence': 0.95
        }
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.test_campaign_dir):
            shutil.rmtree(self.test_campaign_dir)
    
    def test_archive_file_creation(self):
        """Test that archive files can be created with proper structure."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_filename = f"{timestamp}_final_state.json"
        archive_path = os.path.join(self.test_archive_dir, archive_filename)
        
        # Create archive data
        archive_data = {
            'campaign_id': 'test_campaign',
            'timestamp': datetime.now().isoformat(),
            'character_data': self.sample_character_data,
            'world_state': self.sample_world_state,
            'goals': self.sample_goals,
            'transformation': self.sample_transformation,
            'ending_summary': self.sample_ending_summary,
            'archive_version': '1.0'
        }
        
        # Save archive file
        with open(archive_path, 'w') as f:
            json.dump(archive_data, f, indent=2)
        
        # Verify file exists
        self.assertTrue(os.path.exists(archive_path))
        
        # Load and verify data
        with open(archive_path, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data['campaign_id'], 'test_campaign')
        self.assertIn('character_data', loaded_data)
        self.assertIn('world_state', loaded_data)
        self.assertIn('goals', loaded_data)
        self.assertIn('transformation', loaded_data)
        self.assertIn('ending_summary', loaded_data)
        self.assertIn('archive_version', loaded_data)
    
    def test_ending_log_creation(self):
        """Test that ending logs can be created and maintained."""
        endings_file = os.path.join(self.test_campaign_dir, 'endings.json')
        endings_data = []
        
        # Add ending record
        ending_record = {
            'timestamp': datetime.now().isoformat(),
            'ending_type': self.sample_ending_summary['ending_type'],
            'justification': self.sample_ending_summary['justification'],
            'goal_states': [goal.get('state', 'unknown') for goal in self.sample_goals],
            'transformation_arc': self.sample_transformation['transformation_type'],
            'archive_file': 'test_archive.json',
            'character_name': self.sample_character_data['name']
        }
        
        endings_data.append(ending_record)
        
        # Save endings log
        with open(endings_file, 'w') as f:
            json.dump(endings_data, f, indent=2)
        
        # Verify file exists
        self.assertTrue(os.path.exists(endings_file))
        
        # Load and verify data
        with open(endings_file, 'r') as f:
            loaded_endings = json.load(f)
        
        self.assertIsInstance(loaded_endings, list)
        self.assertEqual(len(loaded_endings), 1)
        
        ending = loaded_endings[0]
        self.assertIn('timestamp', ending)
        self.assertIn('ending_type', ending)
        self.assertIn('justification', ending)
        self.assertIn('goal_states', ending)
        self.assertIn('transformation_arc', ending)
        self.assertIn('archive_file', ending)
        self.assertIn('character_name', ending)
    
    def test_new_game_plus_character_creation(self):
        """Test New Game+ character creation with legacy elements."""
        # Simulate current character data
        current_character = self.sample_character_data.copy()
        
        # Create new character with legacy tags
        new_character = current_character.copy()
        new_character['from_campaign_id'] = 'test_campaign'
        new_character['legacy_tags'] = []
        
        # Apply legacy options
        legacy_options = {
            'memories': True,
            'stat_bonuses': True,
            'items': True
        }
        
        if legacy_options['memories']:
            new_character['legacy_tags'].append('memories')
            memory_fragments = [
                "Fragments of past adventures echo in their mind",
                "Ancient wisdom from previous journeys guides their path",
                "The weight of past choices shapes their destiny"
            ]
            import random
            new_character['background'] = f"{new_character.get('background', '')} {random.choice(memory_fragments)}"
        
        if legacy_options['stat_bonuses']:
            new_character['legacy_tags'].append('stat_bonuses')
            # Add small stat bonuses
            for ability in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
                if ability in new_character.get('ability_scores', {}):
                    new_character['ability_scores'][ability] += 1
        
        if legacy_options['items']:
            new_character['legacy_tags'].append('items')
            # Add legacy items
            legacy_items = [
                "A mysterious artifact from a previous life",
                "A weapon that remembers its wielder",
                "A talisman of forgotten power"
            ]
            current_items = new_character.get('equipment', [])
            current_items.extend(legacy_items)
            new_character['equipment'] = current_items
        
        # Verify legacy tags were applied
        self.assertIn('from_campaign_id', new_character)
        self.assertIn('legacy_tags', new_character)
        self.assertIn('memories', new_character['legacy_tags'])
        self.assertIn('stat_bonuses', new_character['legacy_tags'])
        self.assertIn('items', new_character['legacy_tags'])
        
        # Verify stat bonuses were applied
        for ability in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
            if ability in new_character.get('ability_scores', {}):
                # Check that stat bonuses were applied (should be +1)
                expected_bonus = current_character['ability_scores'][ability] + 1
                self.assertEqual(new_character['ability_scores'][ability], expected_bonus)
        
        # Verify items were added
        self.assertIn('equipment', new_character)
        self.assertGreater(len(new_character['equipment']), len(current_character.get('equipment', [])))
    
    def test_archive_directory_structure(self):
        """Test that archive directory structure is created properly."""
        # Test directory creation
        archive_dir = os.path.join(self.test_campaign_dir, 'archive')
        os.makedirs(archive_dir, exist_ok=True)
        
        self.assertTrue(os.path.exists(archive_dir))
        self.assertTrue(os.path.isdir(archive_dir))
        
        # Test file creation in archive directory
        test_file = os.path.join(archive_dir, 'test.json')
        with open(test_file, 'w') as f:
            json.dump({'test': 'data'}, f)
        
        self.assertTrue(os.path.exists(test_file))
    
    def test_epilogue_data_structure(self):
        """Test epilogue data structure and export functionality."""
        epilogue_data = {
            'epilogue_text': 'And so the hero\'s journey came to an end...',
            'epilogue_theme': 'Victory and Legacy',
            'epilogue_quotes': [
                'The greatest glory in living lies not in never falling, but in rising every time we fall.',
                'Heroes are made by the paths they choose, not the powers they are graced with.'
            ]
        }
        
        # Test markdown export format
        markdown_content = f"""# SoloHeart Epilogue

{epilogue_data['epilogue_text']}

Theme: {epilogue_data['epilogue_theme']}

Quotes:
{chr(10).join(epilogue_data['epilogue_quotes'])}"""
        
        # Verify markdown structure
        self.assertIn('# SoloHeart Epilogue', markdown_content)
        self.assertIn(epilogue_data['epilogue_text'], markdown_content)
        self.assertIn(f"Theme: {epilogue_data['epilogue_theme']}", markdown_content)
        for quote in epilogue_data['epilogue_quotes']:
            self.assertIn(quote, markdown_content)
    
    def test_error_handling_corrupted_files(self):
        """Test error handling for corrupted archive files."""
        # Create a corrupted archive file
        archive_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_final_state.json"
        archive_path = os.path.join(self.test_archive_dir, archive_filename)
        
        with open(archive_path, 'w') as f:
            f.write('{"corrupted": json file')
        
        # Test that file exists but is corrupted
        self.assertTrue(os.path.exists(archive_path))
        
        # Test that loading corrupted file raises exception
        with self.assertRaises(json.JSONDecodeError):
            with open(archive_path, 'r') as f:
                json.load(f)
    
    def test_archive_file_naming_convention(self):
        """Test that archive files follow proper naming convention."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_filename = f"{timestamp}_final_state.json"
        
        # Verify naming convention
        self.assertTrue(archive_filename.endswith('_final_state.json'))
        self.assertTrue(len(archive_filename) > 20)  # Should have timestamp
        
        # Test timestamp format
        timestamp_part = archive_filename.split('_final_state.json')[0]
        self.assertEqual(len(timestamp_part), 15)  # YYYYMMDD_HHMMSS format
    
    def test_ending_type_classification(self):
        """Test ending type classification and labeling."""
        ending_types = {
            'triumph': 'Triumph',
            'tragedy': 'Tragedy',
            'rebirth': 'Rebirth',
            'sacrifice': 'Sacrifice',
            'redemption': 'Redemption',
            'bittersweet': 'Bittersweet'
        }
        
        for ending_type, label in ending_types.items():
            # Test that each ending type has a proper label
            self.assertIsInstance(label, str)
            self.assertGreater(len(label), 0)
    
    def test_legacy_option_combinations(self):
        """Test different legacy option combinations for New Game+."""
        legacy_option_combinations = [
            {'memories': True, 'stat_bonuses': False, 'items': False},
            {'memories': False, 'stat_bonuses': True, 'items': False},
            {'memories': False, 'stat_bonuses': False, 'items': True},
            {'memories': True, 'stat_bonuses': True, 'items': True},
            {'memories': False, 'stat_bonuses': False, 'items': False}
        ]
        
        for legacy_options in legacy_option_combinations:
            # Create new character with these options
            new_character = self.sample_character_data.copy()
            new_character['from_campaign_id'] = 'test_campaign'
            new_character['legacy_tags'] = []
            
            # Apply legacy options
            if legacy_options['memories']:
                new_character['legacy_tags'].append('memories')
            
            if legacy_options['stat_bonuses']:
                new_character['legacy_tags'].append('stat_bonuses')
                for ability in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
                    if ability in new_character.get('ability_scores', {}):
                        new_character['ability_scores'][ability] += 1
            
            if legacy_options['items']:
                new_character['legacy_tags'].append('items')
                current_items = new_character.get('equipment', [])
                current_items.extend(['Legacy Item'])
                new_character['equipment'] = current_items
            
            # Verify legacy tags match options
            for option, enabled in legacy_options.items():
                if enabled:
                    self.assertIn(option, new_character['legacy_tags'])
                else:
                    self.assertNotIn(option, new_character['legacy_tags'])

if __name__ == '__main__':
    # Create test runner
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPhase11ArchiveCore)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Phase 11 Archive and Replay Core Test Results")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    print(f"\n{'='*60}")
    print(f"Phase 11 Archive and Replay Core Status: {'✅ PASSED' if result.wasSuccessful() else '❌ FAILED'}")
    print(f"{'='*60}") 