#!/usr/bin/env python3
"""
Test file for StepByStepCharacterCreator
"""

import sys
import os

# Add the game_app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'game_app'))

from character_creator import StepByStepCharacterCreator


def test_step_by_step_creator():
    """Test the basic functionality of StepByStepCharacterCreator."""
    
    # Create an instance without LLM service (will use pattern matching)
    creator = StepByStepCharacterCreator()
    
    # Test start
    start_prompt = creator.start()
    print("Start prompt:", start_prompt)
    assert "race" in start_prompt.lower()
    
    # Test processing responses
    responses = [
        "I want to be an elf",
        "I'm thinking wizard",
        "Female",
        "25",
        "Sage background",
        "Wise and curious",
        "1",
        "Lawful Good",
        "Elira"
    ]
    
    for i, response in enumerate(responses):
        result = creator.process_response(response)
        print(f"Response {i+1}: {response}")
        print(f"Result: {result}")
        print("-" * 50)
    
    # Test commands
    print("\nTesting commands:")
    
    # Test summary command
    summary = creator.process_response("summary")
    print("Summary command result:")
    print(summary)
    
    # Test help command
    help_result = creator.process_response("help")
    print("Help command result:")
    print(help_result)
    
    # Test edit command
    edit_result = creator.process_response("edit race")
    print("Edit command result:")
    print(edit_result)
    
    print("\nTest completed successfully!")


if __name__ == "__main__":
    test_step_by_step_creator() 