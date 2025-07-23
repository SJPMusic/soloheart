#!/usr/bin/env python3
"""
Unit tests for gender parsing in StepByStepCharacterCreator.

Tests the _parse_gender_with_keywords method to ensure it correctly
extracts gender from natural language input.
"""

import sys
import os
import unittest

# Add the game_app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'game_app'))

from character_creator import StepByStepCharacterCreator


class TestGenderParsing(unittest.TestCase):
    """Test cases for gender parsing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.creator = StepByStepCharacterCreator()
    
    def test_gender_keyword_extraction(self):
        """Test that gender keywords are correctly extracted."""
        
        # Test female keywords
        self.assertEqual(self.creator._parse_gender_with_keywords("She's a female ranger"), "Female")
        self.assertEqual(self.creator._parse_gender_with_keywords("A woman warrior"), "Female")
        
        # Test male keywords
        self.assertEqual(self.creator._parse_gender_with_keywords("He's a male rogue"), "Male")
        self.assertEqual(self.creator._parse_gender_with_keywords("A man fighter"), "Male")
        
        # Test non-binary keywords
        self.assertEqual(self.creator._parse_gender_with_keywords("They are non-binary"), "Non-Binary")
        self.assertEqual(self.creator._parse_gender_with_keywords("A nonbinary character"), "Non-Binary")
    
    def test_gender_priority_handling(self):
        """Test that female keywords take priority over male keywords."""
        
        # Test cases where both male and female keywords might be present
        # Female should take priority
        self.assertEqual(self.creator._parse_gender_with_keywords("She's a female ranger who fights like a man"), "Female")
        self.assertEqual(self.creator._parse_gender_with_keywords("A woman who is as strong as any man"), "Female")
    
    def test_case_insensitive_parsing(self):
        """Test that gender parsing is case insensitive."""
        
        # Test mixed case
        self.assertEqual(self.creator._parse_gender_with_keywords("SHE is a FEMALE ranger"), "Female")
        self.assertEqual(self.creator._parse_gender_with_keywords("HE is a MALE rogue"), "Male")
        self.assertEqual(self.creator._parse_gender_with_keywords("THEY are NON-BINARY"), "Non-Binary")
        
        # Test title case
        self.assertEqual(self.creator._parse_gender_with_keywords("She Is A Female Ranger"), "Female")
        self.assertEqual(self.creator._parse_gender_with_keywords("He Is A Male Rogue"), "Male")
    
    def test_complex_sentences(self):
        """Test gender parsing in complex, realistic sentences."""
        
        # Test the specific bug case mentioned
        self.assertEqual(self.creator._parse_response("gender", "She's a female half-elf ranger..."), "Female")
        
        # Test other complex sentences
        self.assertEqual(self.creator._parse_response("gender", "My character is a woman who survived a forest fire"), "Female")
        self.assertEqual(self.creator._parse_response("gender", "He's a male dwarf cleric from the mountains"), "Male")
        self.assertEqual(self.creator._parse_response("gender", "They are a non-binary elf wizard"), "Non-Binary")
    
    def test_no_gender_keywords(self):
        """Test that None is returned when no gender keywords are found."""
        
        # Test sentences without gender keywords
        self.assertIsNone(self.creator._parse_gender_with_keywords("A ranger from the forest"))
        self.assertIsNone(self.creator._parse_gender_with_keywords("The wizard casts spells"))
        self.assertIsNone(self.creator._parse_gender_with_keywords("A fighter with a sword"))
        self.assertIsNone(self.creator._parse_gender_with_keywords(""))
        self.assertIsNone(self.creator._parse_gender_with_keywords("   "))
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        
        # Test with punctuation
        self.assertEqual(self.creator._parse_gender_with_keywords("She's a female!"), "Female")
        self.assertEqual(self.creator._parse_gender_with_keywords("He is male."), "Male")
        
        # Test with numbers
        self.assertEqual(self.creator._parse_gender_with_keywords("A 25-year-old woman"), "Female")
        self.assertEqual(self.creator._parse_gender_with_keywords("The 30-year-old man"), "Male")
        
        # Test with special characters
        self.assertEqual(self.creator._parse_gender_with_keywords("She's a female@#$%"), "Female")
        self.assertEqual(self.creator._parse_gender_with_keywords("He is male!@#"), "Male")
    
    def test_partial_word_matching(self):
        """Test that partial word matches don't cause false positives."""
        
        # These should return None (no gender keywords)
        self.assertIsNone(self.creator._parse_gender_with_keywords("A ranger from the forest"))
        self.assertIsNone(self.creator._parse_gender_with_keywords("A wizard with spells"))
        self.assertIsNone(self.creator._parse_gender_with_keywords("A fighter with a sword"))
        self.assertIsNone(self.creator._parse_gender_with_keywords("A cleric of light"))
    
    def test_integration_with_parse_response(self):
        """Test that gender parsing integrates correctly with the main parse_response method."""
        
        # Test that gender parsing is called first
        self.assertEqual(self.creator._parse_response("gender", "She's a female half-elf ranger"), "Female")
        self.assertEqual(self.creator._parse_response("gender", "He's a male dwarf cleric"), "Male")
        self.assertEqual(self.creator._parse_response("gender", "They are non-binary"), "Non-Binary")
        
        # Test that other fields still work normally (focus on gender parsing, not race/class)
        self.assertIsNotNone(self.creator._parse_response("race", "She's a female half-elf ranger"))
        self.assertIsNotNone(self.creator._parse_response("class", "She's a female half-elf ranger"))
    
    def test_gender_keywords(self):
        """Test the specific gender keyword cases as requested."""
        creator = StepByStepCharacterCreator()
        assert creator._parse_response("gender", "She's a female ranger") == "Female"
        assert creator._parse_response("gender", "He's a male rogue") == "Male"
        assert creator._parse_response("gender", "Woman warrior from the north") == "Female"
        assert creator._parse_response("gender", "Man with a broadsword") == "Male"


def run_gender_parsing_tests():
    """Run the gender parsing test suite."""
    print("🧪 Running Gender Parsing Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestGenderParsing))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
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
        print("\n✅ All gender parsing tests passed!")
        return True
    else:
        print("\n❌ Some gender parsing tests failed!")
        return False


if __name__ == "__main__":
    success = run_gender_parsing_tests()
    sys.exit(0 if success else 1) 