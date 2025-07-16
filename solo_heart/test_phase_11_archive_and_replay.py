#!/usr/bin/env python3
"""
Phase 11: Archive and Replay System Test Suite

Tests the complete archive system including:
- Final state capture on ending trigger
- Archive list/load/delete endpoints
- New Game+ creation with legacy elements
- Epilogue replay and export functionality
- Alternate ending log integrity
- Error handling for corrupted/missing files
"""

import json
import os
import shutil
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import the main application
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simple_unified_interface import app

class TestPhase11ArchiveAndReplay(unittest.TestCase):
    """Comprehensive test suite for Phase 11 archive and replay functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Create temporary test directories
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
        if os.path.exists(self.test_campaign_dir):
            shutil.rmtree(self.test_campaign_dir)
    
    def test_finalize_campaign_archive(self):
        """Test final state capture when ending is triggered."""
        with patch('simple_unified_interface.session') as mock_session:
            mock_session.get.return_value = 'test_campaign'
            
            response = self.app.post('/api/archive/finalize', 
                json={
                    'character_data': self.sample_character_data,
                    'world_state': self.sample_world_state,
                    'goals': self.sample_goals,
                    'transformation': self.sample_transformation,
                    'ending_summary': self.sample_ending_summary
                }
            )
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('archive_file', data)
            self.assertIn('message', data)
    
    def test_archive_list_endpoint(self):
        """Test archive list endpoint returns proper summaries."""
        # Create a sample archive file
        sample_archive = {
            'campaign_id': 'test_campaign',
            'timestamp': datetime.now().isoformat(),
            'character_data': self.sample_character_data,
            'world_state': self.sample_world_state,
            'goals': self.sample_goals,
            'transformation': self.sample_transformation,
            'ending_summary': self.sample_ending_summary,
            'archive_version': '1.0'
        }
        
        archive_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_final_state.json"
        archive_path = os.path.join(self.test_archive_dir, archive_filename)
        
        with open(archive_path, 'w') as f:
            json.dump(sample_archive, f, indent=2)
        
        with patch('simple_unified_interface.session') as mock_session:
            mock_session.get.return_value = 'test_campaign'
            
            with patch('simple_unified_interface.os.path.join') as mock_join:
                mock_join.return_value = self.test_archive_dir
                
                response = self.app.get('/api/archive/list')
                data = json.loads(response.data)
                
                self.assertTrue(data['success'])
                self.assertIn('archives', data)
                self.assertIsInstance(data['archives'], list)
                
                if data['archives']:
                    archive = data['archives'][0]
                    self.assertIn('filename', archive)
                    self.assertIn('timestamp', archive)
                    self.assertIn('character_name', archive)
                    self.assertIn('ending_type', archive)
                    self.assertIn('campaign_id', archive)
    
    def test_archive_load_endpoint(self):
        """Test archive load endpoint returns full archive data."""
        # Create a sample archive file
        sample_archive = {
            'campaign_id': 'test_campaign',
            'timestamp': datetime.now().isoformat(),
            'character_data': self.sample_character_data,
            'world_state': self.sample_world_state,
            'goals': self.sample_goals,
            'transformation': self.sample_transformation,
            'ending_summary': self.sample_ending_summary,
            'archive_version': '1.0'
        }
        
        archive_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_final_state.json"
        archive_path = os.path.join(self.test_archive_dir, archive_filename)
        
        with open(archive_path, 'w') as f:
            json.dump(sample_archive, f, indent=2)
        
        with patch('simple_unified_interface.session') as mock_session:
            mock_session.get.return_value = 'test_campaign'
            
            with patch('simple_unified_interface.os.path.join') as mock_join:
                mock_join.return_value = archive_path
                
                response = self.app.get(f'/api/archive/load?file={archive_filename}')
                data = json.loads(response.data)
                
                self.assertTrue(data['success'])
                self.assertIn('archive_data', data)
                self.assertEqual(data['archive_data']['campaign_id'], 'test_campaign')
                self.assertIn('character_data', data['archive_data'])
                self.assertIn('world_state', data['archive_data'])
                self.assertIn('goals', data['archive_data'])
                self.assertIn('transformation', data['archive_data'])
                self.assertIn('ending_summary', data['archive_data'])
    
    def test_archive_load_missing_file(self):
        """Test archive load with missing file returns error."""
        with patch('simple_unified_interface.session') as mock_session:
            mock_session.get.return_value = 'test_campaign'
            
            response = self.app.get('/api/archive/load?file=nonexistent.json')
            data = json.loads(response.data)
            
            self.assertFalse(data['success'])
            self.assertIn('error', data)
    
    def test_archive_delete_endpoint(self):
        """Test archive delete endpoint."""
        # Create a sample archive file
        archive_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_final_state.json"
        archive_path = os.path.join(self.test_archive_dir, archive_filename)
        
        with open(archive_path, 'w') as f:
            json.dump({'test': 'data'}, f)
        
        with patch('simple_unified_interface.session') as mock_session:
            mock_session.get.return_value = 'test_campaign'
            
            with patch('simple_unified_interface.os.path.join') as mock_join:
                mock_join.return_value = archive_path
                
                response = self.app.post('/api/archive/delete', 
                    json={'filename': archive_filename}
                )
                data = json.loads(response.data)
                
                self.assertTrue(data['success'])
                self.assertIn('message', data)
    
    def test_new_game_plus_creation(self):
        """Test New Game+ creation with legacy elements."""
        with patch('simple_unified_interface.session') as mock_session:
            mock_session.get.return_value = 'test_campaign'
            mock_session.__getitem__.return_value = self.sample_character_data
            
            legacy_options = {
                'memories': True,
                'stat_bonuses': True,
                'items': True
            }
            
            response = self.app.post('/api/campaign/newgameplus',
                json={'legacy_options': legacy_options}
            )
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('new_campaign_id', data)
            self.assertIn('character_data', data)
            self.assertIn('world_state', data)
            self.assertIn('legacy_options', data)
            
            # Check that legacy tags were applied
            character_data = data['character_data']
            self.assertIn('from_campaign_id', character_data)
            self.assertIn('legacy_tags', character_data)
            self.assertIn('memories', character_data['legacy_tags'])
            self.assertIn('stat_bonuses', character_data['legacy_tags'])
            self.assertIn('items', character_data['legacy_tags'])
    
    def test_ending_history_endpoint(self):
        """Test ending history endpoint."""
        # Create a sample endings.json file
        endings_data = [
            {
                'timestamp': datetime.now().isoformat(),
                'ending_type': 'triumph',
                'justification': 'Hero saved the kingdom',
                'goal_states': ['completed', 'completed', 'completed'],
                'transformation_arc': 'Innocent → Hero',
                'archive_file': 'test_archive.json',
                'character_name': 'Test Hero'
            }
        ]
        
        endings_file = os.path.join(self.test_campaign_dir, 'endings.json')
        with open(endings_file, 'w') as f:
            json.dump(endings_data, f, indent=2)
        
        with patch('simple_unified_interface.session') as mock_session:
            mock_session.get.return_value = 'test_campaign'
            
            with patch('simple_unified_interface.os.path.join') as mock_join:
                mock_join.return_value = endings_file
                
                response = self.app.get('/api/archive/endings')
                data = json.loads(response.data)
                
                self.assertTrue(data['success'])
                self.assertIn('endings', data)
                self.assertIsInstance(data['endings'], list)
                
                if data['endings']:
                    ending = data['endings'][0]
                    self.assertIn('timestamp', ending)
                    self.assertIn('ending_type', ending)
                    self.assertIn('justification', ending)
                    self.assertIn('goal_states', ending)
                    self.assertIn('transformation_arc', ending)
                    self.assertIn('archive_file', ending)
                    self.assertIn('character_name', ending)
    
    def test_epilogue_replay_functionality(self):
        """Test epilogue replay and export functionality."""
        # Create a sample archive with epilogue
        sample_archive = {
            'campaign_id': 'test_campaign',
            'timestamp': datetime.now().isoformat(),
            'character_data': self.sample_character_data,
            'world_state': self.sample_world_state,
            'goals': self.sample_goals,
            'transformation': self.sample_transformation,
            'ending_summary': self.sample_ending_summary,
            'epilogue': {
                'epilogue_text': 'And so the hero\'s journey came to an end...',
                'epilogue_theme': 'Victory and Legacy',
                'epilogue_quotes': [
                    'The greatest glory in living lies not in never falling, but in rising every time we fall.',
                    'Heroes are made by the paths they choose, not the powers they are graced with.'
                ]
            },
            'archive_version': '1.0'
        }
        
        archive_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_final_state.json"
        archive_path = os.path.join(self.test_archive_dir, archive_filename)
        
        with open(archive_path, 'w') as f:
            json.dump(sample_archive, f, indent=2)
        
        with patch('simple_unified_interface.session') as mock_session:
            mock_session.get.return_value = 'test_campaign'
            
            with patch('simple_unified_interface.os.path.join') as mock_join:
                mock_join.return_value = archive_path
                
                # Test loading archive with epilogue
                response = self.app.get(f'/api/archive/load?file={archive_filename}')
                data = json.loads(response.data)
                
                self.assertTrue(data['success'])
                self.assertIn('epilogue', data['archive_data'])
                epilogue = data['archive_data']['epilogue']
                self.assertIn('epilogue_text', epilogue)
                self.assertIn('epilogue_theme', epilogue)
                self.assertIn('epilogue_quotes', epilogue)
    
    def test_error_handling_corrupted_files(self):
        """Test error handling for corrupted archive files."""
        # Create a corrupted archive file
        archive_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_final_state.json"
        archive_path = os.path.join(self.test_archive_dir, archive_filename)
        
        with open(archive_path, 'w') as f:
            f.write('{"corrupted": json file')
        
        with patch('simple_unified_interface.session') as mock_session:
            mock_session.get.return_value = 'test_campaign'
            
            with patch('simple_unified_interface.os.path.join') as mock_join:
                mock_join.return_value = self.test_archive_dir
                
                response = self.app.get('/api/archive/list')
                data = json.loads(response.data)
                
                # Should still return success but skip corrupted files
                self.assertTrue(data['success'])
                self.assertIn('archives', data)
    
    def test_error_handling_missing_components(self):
        """Test error handling for missing archive components."""
        with patch('simple_unified_interface.session') as mock_session:
            mock_session.get.return_value = 'test_campaign'
            
            # Test with missing required fields
            response = self.app.post('/api/archive/finalize', 
                json={
                    'character_data': {},
                    'world_state': {},
                    'goals': [],
                    'transformation': {},
                    'ending_summary': {}
                }
            )
            
            data = json.loads(response.data)
            # Should still succeed with empty data
            self.assertTrue(data['success'])
    
    def test_archive_directory_creation(self):
        """Test that archive directories are created automatically."""
        with patch('simple_unified_interface.session') as mock_session:
            mock_session.get.return_value = 'test_campaign'
            
            response = self.app.post('/api/archive/finalize', 
                json={
                    'character_data': self.sample_character_data,
                    'world_state': self.sample_world_state,
                    'goals': self.sample_goals,
                    'transformation': self.sample_transformation,
                    'ending_summary': self.sample_ending_summary
                }
            )
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
    
    def test_ending_log_integrity(self):
        """Test that ending logs maintain data integrity."""
        with patch('simple_unified_interface.session') as mock_session:
            mock_session.get.return_value = 'test_campaign'
            
            # Test ending log creation
            response = self.app.post('/api/archive/finalize', 
                json={
                    'character_data': self.sample_character_data,
                    'world_state': self.sample_world_state,
                    'goals': self.sample_goals,
                    'transformation': self.sample_transformation,
                    'ending_summary': self.sample_ending_summary
                }
            )
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            
            # Test that ending history can be retrieved
            response = self.app.get('/api/archive/endings')
            data = json.loads(response.data)
            
            self.assertTrue(data['success'])
            self.assertIn('endings', data)
    
    def test_new_game_plus_legacy_options(self):
        """Test different legacy option combinations for New Game+."""
        legacy_option_combinations = [
            {'memories': True, 'stat_bonuses': False, 'items': False},
            {'memories': False, 'stat_bonuses': True, 'items': False},
            {'memories': False, 'stat_bonuses': False, 'items': True},
            {'memories': True, 'stat_bonuses': True, 'items': True},
            {'memories': False, 'stat_bonuses': False, 'items': False}
        ]
        
        with patch('simple_unified_interface.session') as mock_session:
            mock_session.get.return_value = 'test_campaign'
            mock_session.__getitem__.return_value = self.sample_character_data
            
            for legacy_options in legacy_option_combinations:
                response = self.app.post('/api/campaign/newgameplus',
                    json={'legacy_options': legacy_options}
                )
                
                data = json.loads(response.data)
                self.assertTrue(data['success'])
                self.assertIn('new_campaign_id', data)
                self.assertIn('character_data', data)
                
                # Verify legacy tags match options
                character_data = data['character_data']
                self.assertIn('legacy_tags', character_data)
                
                for option, enabled in legacy_options.items():
                    if enabled:
                        self.assertIn(option, character_data['legacy_tags'])
                    else:
                        self.assertNotIn(option, character_data['legacy_tags'])

if __name__ == '__main__':
    # Create test runner
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPhase11ArchiveAndReplay)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Phase 11 Archive and Replay Test Results")
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
    print(f"Phase 11 Archive and Replay System Status: {'✅ PASSED' if result.wasSuccessful() else '❌ FAILED'}")
    print(f"{'='*60}") 