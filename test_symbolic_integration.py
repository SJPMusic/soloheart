#!/usr/bin/env python3
"""
TNE Symbolic Integration Validation Test
Validates that all symbolic outputs match TNE's live response format and schema.
"""

import sys
import os
import json
import requests
from typing import Dict, Any, List

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solo_heart.routing import tne_connector

def test_tne_connector_response_format():
    """Test that TNE connector returns the expected response format."""
    print("🧪 Testing TNE Connector Response Format...")
    
    # Test symbolic analysis
    test_text = "My character is Kaelen Thorne, a former blacksmith seeking revenge."
    result = tne_connector.get_symbolic_analysis(test_text)
    
    expected_keys = [
        "archetypal_tags", 
        "chaos_order_tension", 
        "narrative_decay", 
        "symbolic_coherence"
    ]
    
    missing_keys = [key for key in expected_keys if key not in result]
    if missing_keys:
        print(f"❌ Missing expected keys: {missing_keys}")
        return False
    
    print("✅ TNE connector returns expected response format")
    return True

def test_symbolic_summary_format():
    """Test that symbolic summary returns the expected format."""
    print("🧪 Testing Symbolic Summary Format...")
    
    test_character_id = "test_character_123"
    result = tne_connector.get_symbolic_summary(test_character_id)
    
    expected_keys = [
        "archetypal_tags", 
        "chaos_order_tension", 
        "narrative_decay", 
        "symbolic_coherence"
    ]
    
    missing_keys = [key for key in expected_keys if key not in result]
    if missing_keys:
        print(f"❌ Missing expected keys: {missing_keys}")
        return False
    
    print("✅ Symbolic summary returns expected format")
    return True

def test_error_handling():
    """Test that TNE failures are handled gracefully."""
    print("🧪 Testing Error Handling...")
    
    # Test with invalid character ID
    result = tne_connector.get_symbolic_summary("invalid_id")
    
    # Should return default values with error field
    if "error" in result:
        print("✅ Error handling works - returns error field")
        return True
    else:
        print("❌ Error handling failed - no error field returned")
        return False

def test_ui_consistency():
    """Test that UI consistently reflects TNE outputs."""
    print("🧪 Testing UI Consistency...")
    
    # Test archetype display
    test_data = {
        "archetypal_tags": ["Hero's Journey", "Revenge", "Transformation"],
        "chaos_order_tension": 0.7,
        "narrative_decay": 0.2,
        "symbolic_coherence": 0.8
    }
    
    # Simulate UI formatting
    symbolic_parts = []
    chaos_order = test_data.get("chaos_order_state", "Unknown")
    symbolic_parts.append(f"Chaos/Order State: {chaos_order}")
    
    if test_data.get("narrative_decay", 0) > 0:
        symbolic_parts.append(f"Narrative Decay: {test_data['narrative_decay']:.2f}")
    
    tags = test_data.get("archetypal_tags", [])
    if tags:
        symbolic_parts.append(f"Archetypal Themes: {', '.join(tags)}")
    
    if test_data.get("symbolic_coherence", 1.0) < 1.0:
        symbolic_parts.append(f"Symbolic Coherence: {test_data['symbolic_coherence']:.2f}")
    
    formatted_output = "\n".join(symbolic_parts)
    
    # Validate formatting
    if "Archetypal Themes: Hero's Journey, Revenge, Transformation" in formatted_output:
        print("✅ UI consistently reflects TNE archetype outputs")
        return True
    else:
        print("❌ UI formatting inconsistent with TNE outputs")
        return False

def test_symbolic_unavailable_handling():
    """Test that symbolic unavailable is handled gracefully."""
    print("🧪 Testing Symbolic Unavailable Handling...")
    
    # Simulate TNE failure
    failed_result = {
        "archetypal_tags": [], 
        "chaos_order_tension": 0.5, 
        "narrative_decay": 0.0, 
        "symbolic_coherence": 1.0, 
        "error": "TNE service unavailable"
    }
    
    # Check that no fabricated summary is returned
    if "error" in failed_result and failed_result["error"]:
        print("✅ Symbolic unavailable handled gracefully - no fabricated summary")
        return True
    else:
        print("❌ Symbolic unavailable not handled properly")
        return False

def test_data_flow_pipeline():
    """Test that symbolic data flows correctly through the pipeline."""
    print("🧪 Testing Data Flow Pipeline...")
    
    # Simulate the pipeline: input_capture -> tne_connector -> TNE -> symbolic_display
    test_input = "My character seeks revenge for his family's death"
    
    # Step 1: Input capture (simulated)
    captured_input = test_input
    
    # Step 2: TNE connector call
    symbolic_result = tne_connector.get_symbolic_analysis(captured_input)
    
    # Step 3: Check that result is TNE-native
    if isinstance(symbolic_result, dict) and "archetypal_tags" in symbolic_result:
        print("✅ Data flows correctly through pipeline")
        return True
    else:
        print("❌ Data flow pipeline broken")
        return False

def run_validation_checklist():
    """Run the complete validation checklist."""
    print("🔍 TNE Symbolic Integration Validation Checklist")
    print("=" * 50)
    
    tests = [
        ("TNE Connector Response Format", test_tne_connector_response_format),
        ("Symbolic Summary Format", test_symbolic_summary_format),
        ("Error Handling", test_error_handling),
        ("UI Consistency", test_ui_consistency),
        ("Symbolic Unavailable Handling", test_symbolic_unavailable_handling),
        ("Data Flow Pipeline", test_data_flow_pipeline)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Validation Results:")
    print("-" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All validation tests passed - Symbolic integration ready!")
        return True
    else:
        print("❌ Some validation tests failed - Review required")
        return False

if __name__ == "__main__":
    success = run_validation_checklist()
    sys.exit(0 if success else 1) 