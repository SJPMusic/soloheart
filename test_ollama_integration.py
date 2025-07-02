#!/usr/bin/env python3
"""
Test script for Ollama integration
"""

import sys
import os

# Add the solo_heart directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'solo_heart'))

def test_ollama_service():
    """Test the Ollama LLM service"""
    print("🧪 Testing Ollama LLM Service Integration")
    print("=" * 50)
    
    try:
        from ollama_llm_service import OllamaLLMService, chat_completion
        
        print("✅ Ollama LLM service imported successfully")
        
        # Test the service initialization (this will fail if Ollama is not running)
        try:
            service = OllamaLLMService()
            print("✅ Ollama service initialized successfully")
        except Exception as e:
            print(f"⚠️  Ollama service not available: {e}")
            print("This is expected if Ollama is not running")
            return False
        
        # Test a simple chat completion
        try:
            response = chat_completion([
                {"role": "user", "content": "Say 'Hello, SoloHeart!'"}
            ], max_tokens=10)
            print(f"✅ Chat completion test successful: {response}")
            return True
        except Exception as e:
            print(f"❌ Chat completion test failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import Ollama service: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_character_generator():
    """Test the character generator with Ollama"""
    print("\n🧪 Testing Character Generator with Ollama")
    print("=" * 50)
    
    try:
        from character_generator import CharacterGenerator
        
        print("✅ Character generator imported successfully")
        
        # Test initialization (this will fail if Ollama is not running)
        try:
            generator = CharacterGenerator()
            print("✅ Character generator initialized successfully")
            return True
        except Exception as e:
            print(f"⚠️  Character generator not available: {e}")
            print("This is expected if Ollama is not running")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import character generator: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_simple_unified_interface():
    """Test the simple unified interface with Ollama"""
    print("\n🧪 Testing Simple Unified Interface with Ollama")
    print("=" * 50)
    
    try:
        from simple_unified_interface import SimpleCharacterGenerator
        
        print("✅ Simple unified interface imported successfully")
        
        # Test initialization (this will fail if Ollama is not running)
        try:
            generator = SimpleCharacterGenerator()
            print("✅ Simple character generator initialized successfully")
            return True
        except Exception as e:
            print(f"⚠️  Simple character generator not available: {e}")
            print("This is expected if Ollama is not running")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import simple unified interface: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all tests"""
    print("🎲 SoloHeart Ollama Integration Test")
    print("=" * 60)
    
    # Test 1: Ollama service
    test1_passed = test_ollama_service()
    
    # Test 2: Character generator
    test2_passed = test_character_generator()
    
    # Test 3: Simple unified interface
    test3_passed = test_simple_unified_interface()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"✅ Ollama Service: {'PASS' if test1_passed else 'FAIL'}")
    print(f"✅ Character Generator: {'PASS' if test2_passed else 'FAIL'}")
    print(f"✅ Simple Unified Interface: {'PASS' if test3_passed else 'FAIL'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 All tests passed! Ollama integration is working correctly.")
        print("💡 To run the full game, make sure Ollama is running with LLaMA 3:")
        print("   ollama pull llama3")
        print("   ollama serve")
    else:
        print("\n⚠️  Some tests failed. This is expected if Ollama is not running.")
        print("💡 To run the full game, start Ollama first:")
        print("   ollama pull llama3")
        print("   ollama serve")

if __name__ == "__main__":
    main() 