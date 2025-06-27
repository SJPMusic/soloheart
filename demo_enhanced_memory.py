#!/usr/bin/env python3
"""
Enhanced Memory System Demo
===========================

This demo showcases the enhanced memory system with semantic analysis,
categorization, and context-aware parsing similar to how AI reads code.
"""

import sys
import os
import time
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.memory_system import CampaignMemorySystem, SemanticCategory, ContextLevel

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title: str):
    """Print a formatted section"""
    print(f"\n--- {title} ---")

def demo_session_processing():
    """Demo processing a session with enhanced memory system"""
    print_header("Enhanced Session Processing Demo")
    
    # Create memory system
    memory_system = CampaignMemorySystem("demo_campaign_001")
    
    # Sample session text (simulating a DnD session)
    session_text = """
    Session 1: The Adventure Begins
    
    DM: You find yourself in the bustling town of Riverdale. The market square is filled with merchants selling their wares.
    
    Player: I want to explore the town and find a quest.
    
    DM: As you walk through the market, you notice a worried-looking merchant named Aldric the Trader. He's pacing back and forth near his stall.
    
    Player: I approach Aldric and ask what's troubling him.
    
    DM: Aldric looks up with relief. "Thank the gods! I need help. My daughter Elara has been missing for three days. She was last seen near the Old Forest."
    
    Player: I tell him I'll help find his daughter. What can he tell me about the Old Forest?
    
    DM: "The Old Forest is dangerous. There are rumors of goblins and worse. But I'll reward you handsomely if you bring Elara back safely."
    
    Player: I accept the quest and head toward the Old Forest.
    
    DM: The path to the Old Forest leads through rolling hills. As you approach, you see dark trees looming ahead. Suddenly, you hear rustling in the bushes!
    
    Player: I draw my sword and prepare for combat.
    
    DM: Three goblins emerge from the bushes, brandishing crude weapons. Roll for initiative!
    
    Player: I attack the nearest goblin with my sword.
    
    DM: Your sword strikes true! The goblin falls to the ground. The other two goblins look nervous and begin to retreat.
    
    Player: I shout at them to surrender and tell me where Elara is.
    
    DM: One of the goblins, clearly frightened, stammers, "We... we didn't take anyone! We just live here! But we saw a tall figure in black robes heading deeper into the forest yesterday."
    """
    
    print("Processing session text with enhanced memory system...")
    print(f"Text length: {len(session_text)} characters")
    
    # Process the session
    session = memory_system.process_session_log("session_001", session_text)
    
    print_section("Session Analysis Results")
    print(f"Session ID: {session.session_id}")
    print(f"Timestamp: {session.timestamp}")
    print(f"Summary: {session.session_summary}")
    
    # Show semantic analysis
    print_section("Semantic Analysis")
    semantic_analysis = session.semantic_analysis
    print(f"Primary Categories: {semantic_analysis.get('primary_categories', [])}")
    print(f"Context Distribution: {semantic_analysis.get('context_distribution', {})}")
    print(f"Entity Types: {semantic_analysis.get('entity_types', [])}")
    print(f"Relationship Density: {semantic_analysis.get('relationship_density', 0):.2f}")
    print(f"Semantic Coherence: {semantic_analysis.get('semantic_coherence', 0):.2f}")
    print(f"Session Focus: {semantic_analysis.get('session_focus', 'unknown')}")
    
    # Show context map
    print_section("Context Map")
    context_map = session.context_map
    print(f"Entities: {context_map.get('entities', [])}")
    print(f"Relationships: {len(context_map.get('relationships', []))}")
    print(f"Flow Events: {len(context_map.get('flow', []))}")
    print(f"Key Moments: {len(context_map.get('key_moments', []))}")
    
    # Show continuity checks
    print_section("Continuity Checks")
    for check in session.continuity_checks:
        print(f"  - {check}")
    
    return memory_system, session

def demo_entity_extraction(memory_system, session):
    """Demo entity extraction and semantic tagging"""
    print_header("Entity Extraction and Semantic Tagging Demo")
    
    print_section("Extracted Entities")
    for entity in session.parsed_entities:
        print(f"\nEntity: {entity.name}")
        print(f"  Type: {entity.entity_type.value}")
        print(f"  Description: {entity.description}")
        print(f"  Confidence: {entity.confidence:.2f}")
        print(f"  Context Level: {entity.context_level.value}")
        print(f"  Semantic Tags: {len(entity.semantic_tags)}")
        
        for tag in entity.semantic_tags:
            print(f"    - {tag.category.value} (confidence: {tag.confidence:.2f})")
            print(f"      Context: {tag.context}")
            print(f"      Keywords: {tag.keywords}")
        
        print(f"  Relationships: {len(entity.relationships)}")
        for target_id, rel_types in entity.relationships.items():
            target_entity = memory_system.entities.get(target_id)
            if target_entity:
                print(f"    - {target_entity.name}: {rel_types}")

def demo_semantic_search(memory_system):
    """Demo semantic search capabilities"""
    print_header("Semantic Search Demo")
    
    # Search for combat-related content
    print_section("Combat-Related Search")
    combat_results = memory_system.search_campaign_memory_enhanced(
        "combat", 
        semantic_category=SemanticCategory.COMBAT
    )
    
    print(f"Found {len(combat_results)} combat-related results:")
    for result in combat_results[:3]:  # Show top 3
        if result['type'] == 'entity':
            entity = result['content']
            print(f"  - {entity.name} (relevance: {result['relevance']:.2f})")
            print(f"    Type: {entity.entity_type.value}")
            print(f"    Context Level: {entity.context_level.value}")
    
    # Search for social interactions
    print_section("Social Interaction Search")
    social_results = memory_system.search_campaign_memory_enhanced(
        "conversation", 
        semantic_category=SemanticCategory.SOCIAL
    )
    
    print(f"Found {len(social_results)} social interaction results:")
    for result in social_results[:3]:  # Show top 3
        if result['type'] == 'entity':
            entity = result['content']
            print(f"  - {entity.name} (relevance: {result['relevance']:.2f})")
            print(f"    Type: {entity.entity_type.value}")
    
    # Search for specific NPCs
    print_section("NPC Search")
    npc_results = memory_system.search_campaign_memory_enhanced("Aldric")
    
    print(f"Found {len(npc_results)} results for 'Aldric':")
    for result in npc_results:
        if result['type'] == 'entity':
            entity = result['content']
            print(f"  - {entity.name} (relevance: {result['relevance']:.2f})")
            print(f"    Description: {entity.description}")
            print(f"    Context Snippets: {len(entity.context_snippets)}")

def demo_campaign_summary(memory_system):
    """Demo enhanced campaign summary"""
    print_header("Enhanced Campaign Summary Demo")
    
    summary = memory_system.get_campaign_summary_enhanced()
    
    print_section("Campaign Overview")
    print(f"Total Entities: {summary['total_entities']}")
    print(f"Total Sessions: {summary['total_sessions']}")
    
    print_section("Entity Type Distribution")
    for entity_type, count in summary['entity_types'].items():
        print(f"  {entity_type}: {count}")
    
    print_section("Semantic Distribution")
    for category, count in summary['semantic_distribution'].items():
        print(f"  {category}: {count}")
    
    print_section("Key Entities")
    for entity in summary['key_entities']:
        print(f"  - {entity['name']} ({entity['type']})")
        print(f"    Importance: {entity['importance']:.2f}")
        print(f"    Context Level: {entity['context_level']}")
        print(f"    Relationships: {entity['relationship_count']}")
    
    print_section("Relationship Network")
    network = summary['relationship_network']
    print(f"Nodes: {len(network['nodes'])}")
    print(f"Edges: {len(network['edges'])}")
    
    # Show some relationships
    print("Sample Relationships:")
    for edge in network['edges'][:5]:  # Show first 5
        source_node = next((n for n in network['nodes'] if n['id'] == edge['source']), None)
        target_node = next((n for n in network['nodes'] if n['id'] == edge['target']), None)
        if source_node and target_node:
            print(f"  {source_node['name']} --{edge['type']}--> {target_node['name']}")

def demo_continuity_verification(memory_system):
    """Demo continuity verification across sessions"""
    print_header("Continuity Verification Demo")
    
    # Add a second session with potential continuity issues
    session_text_2 = """
    Session 2: The Search Continues
    
    DM: You continue deeper into the Old Forest. The trees grow thicker and the path becomes harder to follow.
    
    Player: I search for any signs of Elara or the figure in black robes.
    
    DM: After some time, you find a small clearing. In the center, you see a young woman named Elara sitting by a campfire. She looks unharmed but frightened.
    
    Player: I approach Elara and introduce myself as someone sent by her father Aldric.
    
    DM: Elara's face lights up with relief. "My father sent you? Thank the gods! I was so worried about him."
    
    Player: I ask her what happened and who the figure in black robes was.
    
    DM: "I was gathering herbs when I met a kind wizard named Malakar. He offered to teach me magic, but then he brought me here and wouldn't let me leave. He said it was for my own safety."
    
    Player: I tell her we should get back to her father. Is Malakar still around?
    
    DM: "No, he left this morning. He said he had important business in the nearby city of Stormhaven."
    
    Player: I escort Elara back to Riverdale.
    
    DM: As you approach Riverdale, Aldric spots you from afar and runs to meet you. The reunion is emotional and joyful.
    
    Player: I tell Aldric about Malakar and that he might be in Stormhaven.
    
    DM: "Stormhaven? That's a dangerous place. But thank you for bringing my daughter back safely. Here's your reward as promised."
    """
    
    print("Processing second session with potential continuity issues...")
    session_2 = memory_system.process_session_log("session_002", session_text_2)
    
    print_section("Continuity Checks for Session 2")
    for check in session_2.continuity_checks:
        print(f"  - {check}")
    
    print_section("Entity Consistency Analysis")
    # Check for entities that appeared in both sessions
    session_1_entities = {entity.name for entity in memory_system.sessions["session_001"].parsed_entities}
    session_2_entities = {entity.name for entity in session_2.parsed_entities}
    
    common_entities = session_1_entities.intersection(session_2_entities)
    print(f"Entities appearing in both sessions: {common_entities}")
    
    for entity_name in common_entities:
        entity_1 = memory_system._find_entity_by_name(entity_name)
        if entity_1:
            print(f"\nEntity: {entity_name}")
            print(f"  First mentioned: {entity_1.first_mentioned}")
            print(f"  Last updated: {entity_1.last_updated}")
            print(f"  Context snippets: {len(entity_1.context_snippets)}")
            print(f"  Semantic tags: {len(entity_1.semantic_tags)}")

def demo_advanced_features(memory_system):
    """Demo advanced memory system features"""
    print_header("Advanced Features Demo")
    
    print_section("Context-Aware Entity Retrieval")
    # Get context for a specific entity
    aldric_entity = memory_system._find_entity_by_name("Aldric")
    if aldric_entity:
        print(f"Entity: {aldric_entity.name}")
        print(f"Context Level: {aldric_entity.context_level.value}")
        print(f"Core Attributes: {aldric_entity.core_attributes}")
        print(f"Variable Attributes: {aldric_entity.variable_attributes}")
        print(f"References: {len(aldric_entity.references)}")
        
        # Show semantic tags
        print("Semantic Tags:")
        for tag in aldric_entity.semantic_tags:
            print(f"  - {tag.category.value}: {tag.context}")
    
    print_section("Relationship Network Analysis")
    # Analyze relationships
    for entity in memory_system.entities.values():
        if entity.relationships:
            print(f"\n{entity.name} relationships:")
            for target_id, rel_types in entity.relationships.items():
                target_entity = memory_system.entities.get(target_id)
                if target_entity:
                    print(f"  - {target_entity.name}: {rel_types}")

def main():
    """Main demo function"""
    print_header("Enhanced Memory System Demo")
    print("This demo showcases the enhanced memory system with semantic analysis,")
    print("categorization, and context-aware parsing similar to how AI reads code.")
    print("Press Enter to continue through each section...")
    
    try:
        # Session processing demo
        input("\nPress Enter to start session processing demo...")
        memory_system, session = demo_session_processing()
        
        # Entity extraction demo
        input("\nPress Enter to start entity extraction demo...")
        demo_entity_extraction(memory_system, session)
        
        # Semantic search demo
        input("\nPress Enter to start semantic search demo...")
        demo_semantic_search(memory_system)
        
        # Campaign summary demo
        input("\nPress Enter to start campaign summary demo...")
        demo_campaign_summary(memory_system)
        
        # Continuity verification demo
        input("\nPress Enter to start continuity verification demo...")
        demo_continuity_verification(memory_system)
        
        # Advanced features demo
        input("\nPress Enter to start advanced features demo...")
        demo_advanced_features(memory_system)
        
        print_header("Demo Complete")
        print("The Enhanced Memory System demo has completed successfully!")
        print("\nKey Features Demonstrated:")
        print("- Semantic analysis and categorization")
        print("- Context-aware entity extraction")
        print("- Relationship mapping and network analysis")
        print("- Continuity verification across sessions")
        print("- Advanced search with semantic understanding")
        print("- Campaign summary with enhanced insights")
        
        print("\nBenefits for Solo DnD Gaming:")
        print("- No more NPC gender/name inconsistencies")
        print("- Persistent memory across all sessions")
        print("- Context-aware AI responses")
        print("- Relationship tracking between entities")
        print("- Semantic understanding of campaign content")
        print("- Continuity verification and conflict detection")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 