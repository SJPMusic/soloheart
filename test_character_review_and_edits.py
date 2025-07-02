#!/usr/bin/env python3
"""
Unit tests for character review and edit functionality.
Tests stability-first logic, review mode, edits, and final lock-in.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the solo_heart directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'solo_heart'))

class TestCharacterReviewAndEdits(unittest.TestCase):
    """Test character review and edit functionality."""
    
    def setUp(self):
        """Set up test environment."""
        os.environ['USE_MOCK_LLM'] = '1'
        from solo_heart.simple_unified_interface import SimpleCharacterGenerator
        self.generator = SimpleCharacterGenerator()
    
    def test_immutability_during_creation(self):
        """Test that facts are immutable during character creation."""
        print("🧪 Testing Immutability During Creation")
        print("=" * 50)
        
        # Start character creation
        result = self.generator.start_character_creation("I want to create a character")
        self.assertTrue(result['success'])
        
        # Confirm race
        result = self.generator.continue_conversation("I want to be a Human")
        self.assertTrue(result['success'])
        self.assertEqual(self.generator.character_data['race'], 'Human')
        self.assertIn('race', self.generator.confirmed_facts)
        
        # Try to change race during creation (should be ignored)
        result = self.generator.continue_conversation("Actually, I want to be an Elf")
        self.assertTrue(result['success'])
        # Race should remain Human (immutable during creation)
        self.assertEqual(self.generator.character_data['race'], 'Human')
        
        # Confirm class
        result = self.generator.continue_conversation("I want to be a Fighter")
        self.assertTrue(result['success'])
        self.assertEqual(self.generator.character_data['class'], 'Fighter')
        
        # Try to change class during creation (should be ignored)
        result = self.generator.continue_conversation("Actually, I want to be a Wizard")
        self.assertTrue(result['success'])
        # Class should remain Fighter (immutable during creation)
        self.assertEqual(self.generator.character_data['class'], 'Fighter')
        
        print("✅ Facts are correctly immutable during creation phase")
    
    def test_completion_detection(self):
        """Test that character completion is properly detected."""
        print("🧪 Testing Completion Detection")
        print("=" * 50)
        
        # Initially incomplete
        self.assertFalse(self.generator.is_character_complete())
        
        # Add required facts
        self.generator.character_data['name'] = 'John'
        self.generator.character_data['race'] = 'Human'
        self.generator.character_data['class'] = 'Fighter'
        self.generator.character_data['background'] = 'Criminal'
        
        # Now should be complete
        self.assertTrue(self.generator.is_character_complete())
        
        # Test with missing facts
        self.generator.character_data['background'] = 'Unknown'
        self.assertFalse(self.generator.is_character_complete())
        
        print("✅ Completion detection works correctly")
    
    def test_review_mode_activation(self):
        """Test that review mode is activated when character is complete."""
        print("🧪 Testing Review Mode Activation")
        print("=" * 50)
        
        # Complete the character
        self.generator.character_data['name'] = 'John'
        self.generator.character_data['race'] = 'Human'
        self.generator.character_data['class'] = 'Fighter'
        self.generator.character_data['background'] = 'Criminal'
        
        # Trigger completion detection
        result = self.generator.continue_conversation("I'm done")
        self.assertTrue(result['success'])
        self.assertTrue(result.get('in_review_mode', False))
        self.assertTrue(self.generator.in_review_mode)
        
        # Should show character summary
        self.assertIn("Character Summary", result['message'])
        self.assertIn("John", result['message'])
        self.assertIn("Human", result['message'])
        self.assertIn("Fighter", result['message'])
        
        print("✅ Review mode activates correctly when character is complete")
    
    def test_character_edits_during_review(self):
        """Test that character edits work during review mode."""
        print("🧪 Testing Character Edits During Review")
        print("=" * 50)
        
        # Set up complete character
        self.generator.character_data['name'] = 'John'
        self.generator.character_data['race'] = 'Human'
        self.generator.character_data['class'] = 'Fighter'
        self.generator.character_data['background'] = 'Criminal'
        self.generator.in_review_mode = True
        
        # Test class change
        result = self.generator.apply_character_edit("change my class to wizard")
        self.assertTrue(result['success'])
        self.assertEqual(self.generator.character_data['class'], 'Wizard')
        self.assertIn("Class: Fighter → Wizard", result['message'])
        
        # Test alignment change
        result = self.generator.apply_character_edit("make me chaotic neutral")
        self.assertTrue(result['success'])
        self.assertEqual(self.generator.character_data['alignment'], 'Chaotic Neutral')
        
        # Test name change
        result = self.generator.apply_character_edit("change my name to alice")
        self.assertTrue(result['success'])
        self.assertEqual(self.generator.character_data['name'], 'Alice')
        self.assertIn("Name: John → Alice", result['message'])
        
        # Test background change
        result = self.generator.apply_character_edit("change my background to noble")
        self.assertTrue(result['success'])
        self.assertEqual(self.generator.character_data['background'], 'Noble')
        self.assertIn("Background: Criminal → Noble", result['message'])
        
        print("✅ Character edits work correctly during review mode")
    
    def test_edits_blocked_outside_review(self):
        """Test that edits are blocked outside review mode."""
        print("🧪 Testing Edits Blocked Outside Review")
        print("=" * 50)
        
        # Not in review mode
        self.assertFalse(self.generator.in_review_mode)
        
        # Try to edit
        result = self.generator.apply_character_edit("change my class to wizard")
        self.assertFalse(result['success'])
        self.assertIn("only allowed during the review phase", result['message'])
        
        print("✅ Edits are correctly blocked outside review mode")
    
    def test_edits_blocked_after_finalization(self):
        """Test that edits are blocked after character finalization."""
        print("🧪 Testing Edits Blocked After Finalization")
        print("=" * 50)
        
        # Set up complete character in review mode
        self.generator.character_data['name'] = 'John'
        self.generator.character_data['race'] = 'Human'
        self.generator.character_data['class'] = 'Fighter'
        self.generator.character_data['background'] = 'Criminal'
        self.generator.in_review_mode = True
        
        # Finalize character
        result = self.generator.finalize_character()
        self.assertTrue(result['success'])
        self.assertTrue(self.generator.character_finalized)
        
        # Try to edit after finalization
        result = self.generator.apply_character_edit("change my class to wizard")
        self.assertFalse(result['success'])
        self.assertIn("already finalized and cannot be edited", result['message'])
        
        print("✅ Edits are correctly blocked after finalization")
    
    def test_character_finalization(self):
        """Test character finalization process."""
        print("🧪 Testing Character Finalization")
        print("=" * 50)
        
        # Set up complete character in review mode
        self.generator.character_data['name'] = 'John'
        self.generator.character_data['race'] = 'Human'
        self.generator.character_data['class'] = 'Fighter'
        self.generator.character_data['background'] = 'Criminal'
        self.generator.in_review_mode = True
        
        # Finalize character
        result = self.generator.finalize_character()
        self.assertTrue(result['success'])
        self.assertTrue(self.generator.character_finalized)
        self.assertFalse(self.generator.in_review_mode)
        self.assertIn("John is now finalized", result['message'])
        
        # Verify character data is preserved
        self.assertEqual(self.generator.character_data['name'], 'John')
        self.assertEqual(self.generator.character_data['race'], 'Human')
        self.assertEqual(self.generator.character_data['class'], 'Fighter')
        self.assertEqual(self.generator.character_data['background'], 'Criminal')
        
        print("✅ Character finalization works correctly")
    
    def test_finalization_requires_completion(self):
        """Test that finalization requires character completion."""
        print("🧪 Testing Finalization Requires Completion")
        print("=" * 50)
        
        # Incomplete character
        self.generator.character_data['name'] = 'John'
        self.generator.character_data['race'] = 'Human'
        # Missing class and background
        self.generator.in_review_mode = True
        
        # Try to finalize
        result = self.generator.finalize_character()
        self.assertFalse(result['success'])
        self.assertIn("not complete", result['message'])
        self.assertFalse(self.generator.character_finalized)
        
        print("✅ Finalization correctly requires character completion")
    
    def test_character_summary_format(self):
        """Test that character summary is properly formatted."""
        print("🧪 Testing Character Summary Format")
        print("=" * 50)
        
        # Set up complete character
        self.generator.character_data['name'] = 'John'
        self.generator.character_data['race'] = 'Human'
        self.generator.character_data['class'] = 'Fighter'
        self.generator.character_data['background'] = 'Criminal'
        self.generator.character_data['alignment'] = 'Chaotic Neutral'
        
        summary = self.generator.get_character_summary()
        
        # Check for required sections
        self.assertIn("Character Summary", summary)
        self.assertIn("**Name:** John", summary)
        self.assertIn("**Race:** Human", summary)
        self.assertIn("**Class:** Fighter", summary)
        self.assertIn("**Background:** Criminal", summary)
        self.assertIn("**Alignment:** Chaotic Neutral", summary)
        self.assertIn("**Ability Scores:**", summary)
        self.assertIn("**Combat Stats:**", summary)
        self.assertIn("**Skills:**", summary)
        self.assertIn("**Equipment:**", summary)
        
        print("✅ Character summary is properly formatted")
    
    def test_vector_memory_updates(self):
        """Test that vector memory is updated during edits."""
        print("🧪 Testing Vector Memory Updates")
        print("=" * 50)
        
        # Mock narrative bridge
        mock_bridge = MagicMock()
        self.generator.narrative_bridge = mock_bridge
        
        # Set up complete character in review mode
        self.generator.character_data['name'] = 'John'
        self.generator.character_data['race'] = 'Human'
        self.generator.character_data['class'] = 'Fighter'
        self.generator.character_data['background'] = 'Criminal'
        self.generator.in_review_mode = True
        
        # Make an edit
        result = self.generator.apply_character_edit("change my class to wizard")
        self.assertTrue(result['success'])
        
        # Verify vector memory was called
        mock_bridge.store_dnd_memory.assert_called()
        
        print("✅ Vector memory is updated during character edits")

def run_tests():
    """Run all tests."""
    print("🧪 Character Review and Edit Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCharacterReviewAndEdits)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 