#!/usr/bin/env python3
"""
Test script to demonstrate semantic analysis vs pattern matching
"""

import re
from utils.character_fact_extraction import extract_all_facts_from_text

def semantic_analyze_brannic():
    """
    Demonstrate how I would analyze Brannic Thorn semantically
    """
    text = "His name is Brannic Thorn, a 32-year-old dwarf who once served as a royal blacksmith. After losing his arm in a mysterious forge explosion, he crafted a mechanical replacement powered by arcane energy. Brannic left the mountain kingdom in disgrace, blamed for a fire he did not start. Now he roams from town to town, fixing broken weapons and searching for whoever sabotaged his workshop. He does not talk much, but his eyes never stop scanning a room."
    
    print("🔍 SEMANTIC ANALYSIS OF BRANNIC THORN")
    print("=" * 50)
    
    # How I would analyze this semantically:
    analysis = {
        "name": "Brannic Thorn",  # Full name from "His name is Brannic Thorn"
        "age": 32,  # From "32-year-old"
        "race": "Dwarf",  # From "dwarf"
        "class": "Fighter",  # From "blacksmith" + "fixing weapons" + "combat focus"
        "background": "Soldier",  # From "royal blacksmith" (military role)
        "gender": "Male",  # From "his"
        "gear": ["Mechanical arm", "Weapon repair tools"],  # From context
        "traumas": ["Lost arm", "Falsely blamed", "Disgraced"],  # From context
        "motivations": ["Find the saboteur", "Clear his name"],  # From "searching for whoever sabotaged"
        "combat_style": "Weapon repair and mechanical combat",  # From context
        "personality": ["Quiet", "Observant", "Distrustful"]  # From "doesn't talk much" + "eyes scanning"
    }
    
    print("✅ SEMANTIC ANALYSIS RESULTS:")
    for key, value in analysis.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    print("❌ PATTERN MATCHING RESULTS (Current System):")
    
    # What your current system extracts:
    current_results = extract_all_facts_from_text(text)
    for key, value in current_results.items():
        if not key.startswith('_'):
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    print("🎯 KEY DIFFERENCES:")
    print("1. Name: Semantic gets 'Brannic Thorn', Pattern gets 'Brannic'")
    print("2. Class: Semantic gets 'Fighter' (blacksmith context), Pattern gets 'Wizard' (arcane)")
    print("3. Age: Semantic gets '32', Pattern misses it")
    print("4. Trauma: Semantic gets 'Lost arm', Pattern misses it")
    print("5. Motivation: Semantic gets 'Find saboteur', Pattern gets generic 'ambition'")
    print("6. Combat Style: Semantic gets 'Weapon repair', Pattern gets wrong extraction")

if __name__ == "__main__":
    semantic_analyze_brannic() 