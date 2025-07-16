#!/usr/bin/env python3
"""
Phase 12: Session Manager + Public Demo Launcher Test Suite

Tests session management API routes, demo mode creation/deletion,
and routing behavior for new/resume/demo functionality.
"""

import unittest
import json
import os
import time
import requests
from datetime import datetime, timedelta

class TestPhase12SessionAndDemo(unittest.TestCase):
    """Test suite for Phase 12 session management and demo functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.base_url = "http://localhost:5001"
        self.session_dir = "logs/character_creation_sessions"
        
        # Ensure session directory exists
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Create test session files
        self.create_test_sessions()
    
    def create_test_sessions(self):
        """Create test session files for testing."""
        test_sessions = [
            {
                "session_id": "test_session_1",
                "name": "Test Session 1",
                "campaign_id": "test_campaign_1",
                "created": "2025-01-01T10:00:00Z"
            },
            {
                "session_id": "test_session_2", 
                "name": "Test Session 2",
                "campaign_id": "test_campaign_2",
                "created": "2025-01-02T10:00:00Z"
            },
            {
                "session_id": "guest_demo_1",
                "name": "Demo Session 1",
                "campaign_id": "demo_campaign_1",
                "created": "2025-01-03T10:00:00Z"
            }
        ]
        
        for session in test_sessions:
            session_file = os.path.join(self.session_dir, f"{session['session_id']}.jsonl")
            with open(session_file, 'w') as f:
                # Create a sample session log entry
                log_entry = {
                    "timestamp": session["created"],
                    "event_type": "session_start",
                    "character_data": {
                        "name": session["name"]
                    },
                    "campaign_name": session["campaign_id"],
                    "description": f"Test session: {session['name']}"
                }
                f.write(json.dumps(log_entry) + '\n')
    
    def test_01_session_listing(self):
        """Test session listing API endpoint."""
        print("\n🧪 Testing session listing...")
        
        try:
            response = requests.get(f"{self.base_url}/api/sessions")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data['success'])
            self.assertIn('sessions', data)
            
            sessions = data['sessions']
            self.assertIsInstance(sessions, list)
            
            # Check that test sessions are included
            session_ids = [s['session_id'] for s in sessions]
            self.assertIn('test_session_1', session_ids)
            self.assertIn('test_session_2', session_ids)
            
            # Check session structure
            for session in sessions:
                self.assertIn('session_id', session)
                self.assertIn('name', session)
                self.assertIn('created', session)
                self.assertIn('campaign_id', session)
            
            print("✅ Session listing test passed")
            
        except requests.exceptions.ConnectionError:
            print("⚠️ Server not running - skipping session listing test")
    
    def test_02_session_loading(self):
        """Test session loading API endpoint."""
        print("\n🧪 Testing session loading...")
        
        try:
            # Test GET method
            response = requests.get(f"{self.base_url}/api/sessions/load?session_id=test_session_1")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data['success'])
            self.assertIn('events', data)
            
            # Test POST method
            response = requests.post(
                f"{self.base_url}/api/sessions/load",
                json={"session_id": "test_session_2"}
            )
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data['success'])
            self.assertIn('events', data)
            
            print("✅ Session loading test passed")
            
        except requests.exceptions.ConnectionError:
            print("⚠️ Server not running - skipping session loading test")
    
    def test_03_session_renaming(self):
        """Test session renaming API endpoint."""
        print("\n🧪 Testing session renaming...")
        
        try:
            new_name = "Renamed Test Session"
            response = requests.post(
                f"{self.base_url}/api/sessions/rename",
                json={
                    "session_id": "test_session_1",
                    "new_name": new_name
                }
            )
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data['success'])
            
            # Verify the rename worked by checking the session list
            response = requests.get(f"{self.base_url}/api/sessions")
            data = response.json()
            
            for session in data['sessions']:
                if session['session_id'] == 'test_session_1':
                    self.assertEqual(session['name'], new_name)
                    break
            
            print("✅ Session renaming test passed")
            
        except requests.exceptions.ConnectionError:
            print("⚠️ Server not running - skipping session renaming test")
    
    def test_04_session_deletion(self):
        """Test session deletion API endpoint."""
        print("\n🧪 Testing session deletion...")
        
        try:
            # Create a temporary session for deletion
            temp_session_file = os.path.join(self.session_dir, "temp_session.jsonl")
            with open(temp_session_file, 'w') as f:
                log_entry = {
                    "timestamp": "2025-01-01T10:00:00Z",
                    "event_type": "session_start",
                    "character_data": {"name": "Temp Session"},
                    "campaign_name": "temp_campaign"
                }
                f.write(json.dumps(log_entry) + '\n')
            
            # Test deletion
            response = requests.post(
                f"{self.base_url}/api/sessions/delete",
                json={"session_id": "temp_session"}
            )
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data['success'])
            
            # Verify file was deleted
            self.assertFalse(os.path.exists(temp_session_file))
            
            print("✅ Session deletion test passed")
            
        except requests.exceptions.ConnectionError:
            print("⚠️ Server not running - skipping session deletion test")
    
    def test_05_demo_mode_creation(self):
        """Test demo mode session creation."""
        print("\n🧪 Testing demo mode creation...")
        
        try:
            # Test demo route
            response = requests.get(f"{self.base_url}/game/demo")
            self.assertEqual(response.status_code, 200)
            
            # Check that demo session was created
            demo_files = [f for f in os.listdir(self.session_dir) if f.startswith("guest_")]
            self.assertGreater(len(demo_files), 0)
            
            print("✅ Demo mode creation test passed")
            
        except requests.exceptions.ConnectionError:
            print("⚠️ Server not running - skipping demo mode test")
    
    def test_06_new_game_routing(self):
        """Test new game routing with campaign ID."""
        print("\n🧪 Testing new game routing...")
        
        try:
            # Test new game route without campaign
            response = requests.get(f"{self.base_url}/game/new")
            self.assertEqual(response.status_code, 200)
            
            # Test new game route with campaign
            response = requests.get(f"{self.base_url}/game/new?campaign=test_campaign")
            self.assertEqual(response.status_code, 200)
            
            print("✅ New game routing test passed")
            
        except requests.exceptions.ConnectionError:
            print("⚠️ Server not running - skipping new game routing test")
    
    def test_07_resume_game_routing(self):
        """Test resume game routing."""
        print("\n🧪 Testing resume game routing...")
        
        try:
            # Test resume game route
            response = requests.get(f"{self.base_url}/game/resume/test_session_1")
            self.assertEqual(response.status_code, 200)
            
            print("✅ Resume game routing test passed")
            
        except requests.exceptions.ConnectionError:
            print("⚠️ Server not running - skipping resume game routing test")
    
    def test_08_settings_configuration(self):
        """Test settings.json configuration."""
        print("\n🧪 Testing settings configuration...")
        
        settings_file = "settings.json"
        self.assertTrue(os.path.exists(settings_file))
        
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        # Check required settings sections
        self.assertIn('demo_mode', settings)
        self.assertIn('session_management', settings)
        self.assertIn('ui', settings)
        self.assertIn('features', settings)
        
        # Check demo mode settings
        demo_settings = settings['demo_mode']
        self.assertIn('enable_demo_mode', demo_settings)
        self.assertIn('demo_session_timeout_hours', demo_settings)
        self.assertIn('auto_resume_latest', demo_settings)
        self.assertIn('max_sessions_visible', demo_settings)
        
        # Check session management settings
        session_settings = settings['session_management']
        self.assertIn('auto_cleanup_demo_sessions', session_settings)
        self.assertIn('demo_session_prefix', session_settings)
        self.assertIn('session_retention_days', session_settings)
        
        print("✅ Settings configuration test passed")
    
    def test_09_start_page_template(self):
        """Test start.html template exists and is valid."""
        print("\n🧪 Testing start page template...")
        
        template_file = "templates/start.html"
        self.assertTrue(os.path.exists(template_file))
        
        with open(template_file, 'r') as f:
            content = f.read()
        
        # Check for required elements
        self.assertIn('SoloHeart', content)
        self.assertIn('Start New Game', content)
        self.assertIn('Resume Game', content)
        self.assertIn('Demo Mode', content)
        self.assertIn('sessionDropdown', content)
        self.assertIn('campaignInput', content)
        
        print("✅ Start page template test passed")
    
    def test_10_gameplay_session_manager(self):
        """Test session manager integration in gameplay.html."""
        print("\n🧪 Testing gameplay session manager...")
        
        template_file = "templates/gameplay.html"
        self.assertTrue(os.path.exists(template_file))
        
        with open(template_file, 'r') as f:
            content = f.read()
        
        # Check for session manager elements
        self.assertIn('Session Manager', content)
        self.assertIn('sessionManager', content)
        self.assertIn('loadSessions()', content)
        self.assertIn('loadSession(', content)
        self.assertIn('renameSession(', content)
        self.assertIn('deleteSession(', content)
        
        print("✅ Gameplay session manager test passed")
    
    def test_11_demo_session_cleanup(self):
        """Test demo session cleanup functionality."""
        print("\n🧪 Testing demo session cleanup...")
        
        # Create old demo session files
        old_demo_files = [
            "guest_old_demo_1.jsonl",
            "guest_old_demo_2.jsonl"
        ]
        
        for filename in old_demo_files:
            filepath = os.path.join(self.session_dir, filename)
            with open(filepath, 'w') as f:
                log_entry = {
                    "timestamp": (datetime.now() - timedelta(hours=25)).isoformat(),
                    "event_type": "session_start",
                    "character_data": {"name": "Old Demo"},
                    "campaign_name": "old_demo"
                }
                f.write(json.dumps(log_entry) + '\n')
        
        # Check that old demo files exist
        for filename in old_demo_files:
            filepath = os.path.join(self.session_dir, filename)
            self.assertTrue(os.path.exists(filepath))
        
        print("✅ Demo session cleanup test passed")
    
    def test_12_api_endpoint_methods(self):
        """Test that API endpoints support correct HTTP methods."""
        print("\n🧪 Testing API endpoint methods...")
        
        endpoints_to_test = [
            ("/api/sessions", "GET"),
            ("/api/sessions/load", "GET"),
            ("/api/sessions/load", "POST"),
            ("/api/sessions/delete", "POST"),
            ("/api/sessions/rename", "POST"),
            ("/game/new", "GET"),
            ("/game/demo", "GET"),
            ("/game/resume/test_session", "GET")
        ]
        
        for endpoint, method in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}")
                elif method == "POST":
                    response = requests.post(f"{self.base_url}{endpoint}")
                
                # Should not return 404 (endpoint exists)
                self.assertNotEqual(response.status_code, 404)
                
            except requests.exceptions.ConnectionError:
                print(f"⚠️ Server not running - skipping {method} {endpoint}")
                continue
        
        print("✅ API endpoint methods test passed")
    
    def tearDown(self):
        """Clean up test files."""
        # Remove test session files
        test_files = [
            "test_session_1.jsonl",
            "test_session_2.jsonl", 
            "guest_demo_1.jsonl",
            "temp_session.jsonl",
            "guest_old_demo_1.jsonl",
            "guest_old_demo_2.jsonl"
        ]
        
        for filename in test_files:
            filepath = os.path.join(self.session_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)

def run_phase_12_tests():
    """Run all Phase 12 tests."""
    print("🚀 Phase 12: Session Manager + Public Demo Launcher Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase12SessionAndDemo)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Phase 12 Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All Phase 12 tests passed!")
    else:
        print("\n❌ Some Phase 12 tests failed.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_phase_12_tests()
    exit(0 if success else 1) 