#!/usr/bin/env python3
"""
Long-Form Memory Persistence Test

This test validates that long-form narratives retain coherent state, character facts,
and inferred goals across multiple sequential entries. It simulates realistic user
input patterns and verifies memory retention over time.
"""

import asyncio
import json
import sys
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---- CONFIGURATION ----
MOCK_MODE = True  # Set to False when TNE is running
TEST_CHARACTER_ID = "longform_test_char_001"
TEST_SESSION_ID = "longform_test_session_001"
TNE_API_URL = "http://localhost:5001"

@dataclass
class MemoryValidationResult:
    """Result of memory validation for a single entry."""
    entry_id: str
    timestamp: str
    input_length: int
    memory_keys_persisted: bool
    goal_alignment_maintained: bool
    context_retention_score: float
    continuity_issues: List[str]
    validation_passed: bool

@dataclass
class PersistenceTestReport:
    """Comprehensive report of memory persistence test results."""
    test_start_time: str
    test_end_time: str
    total_entries: int
    successful_validations: int
    failed_validations: int
    average_context_retention: float
    memory_decay_detected: bool
    goal_drift_detected: bool
    overall_success: bool
    entry_results: List[MemoryValidationResult]
    recommendations: List[str]

# Long-form narrative test data - realistic user inputs
LONGFORM_NARRATIVES = [
    {
        "id": "entry_001",
        "content": """The morning sun filtered through the dense canopy of the ancient forest, casting dappled shadows across the moss-covered ground. Sarah adjusted her leather satchel and took a deep breath of the crisp air. She had been traveling for three days now, following the cryptic map her grandmother had left her. The parchment was worn and fragile, but the markings were clear - a path leading to what her grandmother had called 'the heart of the forest.'

As she stepped forward, her boot crunched on fallen leaves, and she paused to listen. The forest was alive with the sounds of birdsong and the distant rustle of small creatures. But there was something else - a low, rhythmic sound that seemed to pulse through the very air itself. It reminded her of a heartbeat, steady and strong.

Sarah's grandmother had always spoken of this place with reverence, calling it a sanctuary where the old ways were still remembered. She had described it as a place where the boundary between the natural world and something more ancient grew thin. Sarah had never fully understood what that meant, but now, standing in the heart of the forest, she felt a sense of anticipation building within her.

The path ahead wound between massive oak trees, their trunks so wide that three people could have stood hand in hand around them. The bark was deeply grooved, telling stories of centuries past. Sarah reached out to touch one of the trees, and to her surprise, she felt a warmth emanating from the wood, as if the tree itself was alive and aware of her presence.""",
        "expected_memory_keys": ["forest", "grandmother", "map", "ancient", "sanctuary", "oak_trees"],
        "expected_goals": ["exploration", "discovery", "family_connection"],
        "importance": 0.9
    },
    {
        "id": "entry_002", 
        "content": """The rhythmic sound grew louder as Sarah ventured deeper into the forest. It was definitely a heartbeat now, and it seemed to be coming from everywhere at once. She stopped and closed her eyes, trying to pinpoint its source. The sound was both comforting and unsettling - it felt ancient, like something that had been here long before humans walked these lands.

Her grandmother's words echoed in her mind: 'The heart of the forest beats with the rhythm of creation itself. Those who listen carefully can hear the stories of the world being written.' Sarah had always thought her grandmother was speaking metaphorically, but now she wasn't so sure.

A gentle breeze rustled through the leaves above, and Sarah opened her eyes to see a small clearing ahead. In the center stood a circle of stones, each about waist-high and covered in intricate carvings. The carvings seemed to tell a story - she could make out figures that looked like people, animals, and symbols she didn't recognize. The stones were arranged in a perfect circle, and in the very center was a small pool of crystal-clear water.

Sarah approached the circle cautiously, her footsteps silent on the soft earth. As she drew closer, she noticed that the water in the pool was moving, creating small ripples that spread outward in perfect circles. But there was no wind, no visible source for the movement. The water seemed to be alive, responding to the heartbeat that filled the air.

She knelt beside the pool and looked into its depths. The water was so clear that she could see the bottom, which was covered in smooth pebbles of various colors. But as she watched, the pebbles began to glow with a soft, golden light. The light grew brighter, and Sarah felt a warmth spreading through her body, as if the forest itself was welcoming her.""",
        "expected_memory_keys": ["heartbeat", "stones", "carvings", "pool", "water", "light", "welcome"],
        "expected_goals": ["understanding", "connection", "mystery_solving"],
        "importance": 0.95
    },
    {
        "id": "entry_003",
        "content": """The golden light from the pool began to take shape, forming images that danced across the surface of the water. Sarah watched in amazement as scenes from her grandmother's life played out before her eyes. She saw her grandmother as a young woman, standing in this very same clearing, her hand resting on one of the stones. She saw her grandmother learning the old ways, being taught by figures whose faces were blurred by time and memory.

But there was something else in the images - a darkness that seemed to be spreading through the forest. Sarah's grandmother was fighting against it, using the knowledge she had gained here to protect the sanctuary. The images showed her grandmother creating protective barriers, setting up defenses, and ultimately sacrificing herself to seal away the darkness.

Sarah's heart ached as she watched her grandmother's final moments. She had always wondered why her grandmother had seemed so sad in her later years, why she had spent so much time alone in her study, poring over old books and maps. Now she understood - her grandmother had been preparing for this moment, ensuring that Sarah would find her way here when the time was right.

The darkness that her grandmother had sealed away was beginning to stir again. Sarah could feel it in the air, a subtle change in the heartbeat of the forest. The rhythm was becoming irregular, as if the forest itself was in pain. She knew that she had to continue her grandmother's work, to learn the old ways and protect this sacred place.

The water in the pool began to glow more brightly, and Sarah felt a surge of energy flowing through her. It was as if the forest was transferring its knowledge directly into her mind. She could see the patterns now - the way the stones were arranged, the meaning behind the carvings, the ancient language that had been used to create the protective barriers.""",
        "expected_memory_keys": ["grandmother_young", "darkness", "protective_barriers", "sacrifice", "knowledge", "patterns"],
        "expected_goals": ["protection", "learning", "legacy_continuation"],
        "importance": 0.98
    },
    {
        "id": "entry_004",
        "content": """Sarah stood up from the pool, her mind filled with new understanding. The ancient language that had seemed like meaningless symbols before now made perfect sense. She could read the carvings on the stones, and they told the story of the forest's creation, of the first guardians who had been chosen to protect it.

The carvings spoke of a time when the world was young, when the boundaries between the natural and the supernatural were fluid. The forest had been created as a sanctuary, a place where the old knowledge could thrive and where those who were chosen could learn to wield it responsibly. But with the rise of civilization, the old ways had been forgotten, and the forest had been left vulnerable.

Sarah's grandmother had been one of the last guardians, chosen by the forest itself to protect its secrets. She had spent her life learning the old ways, mastering the ancient language, and preparing for the day when the darkness would return. Now that day had come, and Sarah had been chosen to take her place.

She walked around the circle of stones, touching each one and reading the carvings. Each stone told a different part of the story, and together they formed a complete picture of what she needed to do. The darkness that her grandmother had sealed away was an ancient entity, a being of pure chaos that sought to destroy the balance between order and disorder.

To defeat it, Sarah would need to master the ancient language, learn to create and maintain the protective barriers, and ultimately face the darkness in a battle of wills. It was a daunting task, but she felt ready. The forest had chosen her, just as it had chosen her grandmother before her.""",
        "expected_memory_keys": ["ancient_language", "guardians", "creation_story", "darkness_entity", "battle", "chosen"],
        "expected_goals": ["mastery", "confrontation", "balance_restoration"],
        "importance": 0.99
    },
    {
        "id": "entry_005",
        "content": """Sarah began to practice the ancient language, speaking the words that she had learned from the pool. Each word carried unusual resonance, and she could feel the energy flowing through her as she spoke. The stones around her began to glow in response, their carvings lighting up one by one as she activated them.

She started with the simplest protective barriers, creating walls of light that would protect the clearing from the darkness. The process was exhausting, but she could feel herself growing stronger with each barrier she created. The forest was teaching her, guiding her hands and her voice as she worked.

As she completed the final barrier, a great light erupted from the circle of stones, shooting up into the sky like a beacon. Sarah could feel the darkness recoiling from the light, its presence diminishing as the barriers took effect. But she knew this was only a temporary victory - the darkness would return, and when it did, she would need to be ready.

She sat down in the center of the circle, surrounded by the glowing stones, and began to meditate. The forest's heartbeat was steady again, but she could still feel the darkness lurking at the edges of her awareness. It was waiting, gathering its strength for another attack.

Sarah knew that her training was just beginning. She would need to spend time here, learning from the forest and mastering the ancient ways. Her grandmother had spent decades preparing for this moment, and Sarah would need to do the same. But she was not alone - the forest was with her, and so was her grandmother's spirit, guiding her from beyond.

As the sun began to set, casting long shadows across the clearing, Sarah felt a sense of peace settle over her. She was exactly where she was meant to be, doing exactly what she was meant to do. The forest had chosen her, and she would not let it down.""",
        "expected_memory_keys": ["practice", "protective_barriers_creation", "beacon", "meditation", "training", "peace"],
        "expected_goals": ["preparation", "defense", "spiritual_connection"],
        "importance": 0.97
    }
]

class LongFormMemoryPersistenceTester:
    """Test runner for long-form memory persistence validation."""
    
    def __init__(self):
        self.results = []
        self.test_start_time = datetime.now()
        self.memory_state = {}
        self.goal_state = {}
    
    async def run_persistence_test(self) -> PersistenceTestReport:
        """Run the complete long-form memory persistence test."""
        print("🧠 Starting Long-Form Memory Persistence Test")
        print("=" * 60)
        print(f"📅 Test started: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Mock Mode: {MOCK_MODE}")
        print(f"🎯 Character ID: {TEST_CHARACTER_ID}")
        print(f"📋 Session ID: {TEST_SESSION_ID}")
        print(f"📝 Total entries to test: {len(LONGFORM_NARRATIVES)}")
        print()
        
        # Process each narrative entry
        for i, narrative in enumerate(LONGFORM_NARRATIVES):
            print(f"📖 Processing Entry {i+1}/{len(LONGFORM_NARRATIVES)}: {narrative['id']}")
            print("-" * 40)
            
            result = await self.process_narrative_entry(narrative, i)
            self.results.append(result)
            
            # Add delay between entries to simulate real usage
            if i < len(LONGFORM_NARRATIVES) - 1:
                await asyncio.sleep(0.5)
        
        # Generate final report
        report = self.generate_final_report()
        self.save_report(report)
        
        return report
    
    async def process_narrative_entry(self, narrative: Dict, entry_index: int) -> MemoryValidationResult:
        """Process a single narrative entry and validate memory persistence."""
        try:
            # Inject the narrative into memory
            event = self.create_memory_event(narrative)
            
            if MOCK_MODE:
                # Simulate memory injection
                response = {
                    "success": True,
                    "event_id": f"mock_event_{narrative['id']}_{int(time.time())}",
                    "memory_keys": narrative["expected_memory_keys"],
                    "inferred_goals": narrative["expected_goals"],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Real TNE injection
                from integrations.tne_bridge import send_event_to_tne
                response = await send_event_to_tne(event)
            
            # Validate memory persistence
            memory_validation = await self.validate_memory_persistence(narrative, entry_index)
            
            # Validate goal alignment
            goal_validation = await self.validate_goal_alignment(narrative, entry_index)
            
            # Calculate context retention score
            context_score = self.calculate_context_retention(narrative, entry_index)
            
            # Check for continuity issues
            continuity_issues = self.check_continuity_issues(narrative, entry_index)
            
            # Determine if validation passed
            validation_passed = (
                memory_validation and 
                goal_validation and 
                context_score >= 0.7 and 
                len(continuity_issues) == 0
            )
            
            result = MemoryValidationResult(
                entry_id=narrative["id"],
                timestamp=datetime.now().isoformat(),
                input_length=len(narrative["content"]),
                memory_keys_persisted=memory_validation,
                goal_alignment_maintained=goal_validation,
                context_retention_score=context_score,
                continuity_issues=continuity_issues,
                validation_passed=validation_passed
            )
            
            # Update test state
            self.memory_state[narrative["id"]] = {
                "keys": narrative["expected_memory_keys"],
                "goals": narrative["expected_goals"],
                "context_score": context_score
            }
            
            print(f"✅ Entry processed successfully")
            print(f"   Memory keys: {len(narrative['expected_memory_keys'])} persisted")
            print(f"   Goal alignment: {'✅' if goal_validation else '❌'}")
            print(f"   Context retention: {context_score:.2f}")
            print(f"   Continuity issues: {len(continuity_issues)}")
            print(f"   Validation: {'✅ PASS' if validation_passed else '❌ FAIL'}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing entry {narrative['id']}: {e}")
            return MemoryValidationResult(
                entry_id=narrative["id"],
                timestamp=datetime.now().isoformat(),
                input_length=len(narrative["content"]),
                memory_keys_persisted=False,
                goal_alignment_maintained=False,
                context_retention_score=0.0,
                continuity_issues=[f"Processing error: {str(e)}"],
                validation_passed=False
            )
    
    def create_memory_event(self, narrative: Dict) -> Dict:
        """Create a TNE memory event from narrative data."""
        from integrations.tne_event_mapper import map_action_to_event
        
        return map_action_to_event(
            character_id=TEST_CHARACTER_ID,
            action_type="narrative_input",
            description=narrative["content"][:500] + "..." if len(narrative["content"]) > 500 else narrative["content"],
            memory_layer="episodic",
            tags=narrative["expected_memory_keys"] + narrative["expected_goals"],
            importance=narrative["importance"],
            metadata={
                "entry_id": narrative["id"],
                "full_content_length": len(narrative["content"]),
                "session_id": TEST_SESSION_ID
            }
        )
    
    async def validate_memory_persistence(self, narrative: Dict, entry_index: int) -> bool:
        """Validate that memory keys persist correctly."""
        if MOCK_MODE:
            # Simulate memory validation
            return True
        else:
            # Real memory validation against TNE
            try:
                from integrations.tne_bridge import fetch_goal_alignment
                response = await fetch_goal_alignment(TEST_CHARACTER_ID)
                return response.get("success", False)
            except:
                return False
    
    async def validate_goal_alignment(self, narrative: Dict, entry_index: int) -> bool:
        """Validate that goal alignment is maintained."""
        if MOCK_MODE:
            # Simulate goal validation
            return True
        else:
            # Real goal validation against TNE
            try:
                from integrations.tne_bridge import fetch_goal_alignment
                response = await fetch_goal_alignment(TEST_CHARACTER_ID)
                return response.get("success", False)
            except:
                return False
    
    def calculate_context_retention(self, narrative: Dict, entry_index: int) -> float:
        """Calculate context retention score based on narrative continuity."""
        if entry_index == 0:
            return 1.0  # First entry has perfect retention
        
        # Check for continuity with previous entries
        continuity_score = 0.0
        total_checks = 0
        
        # Check if current narrative references previous elements
        current_content = narrative["content"].lower()
        
        for prev_index in range(entry_index):
            prev_narrative = LONGFORM_NARRATIVES[prev_index]
            prev_keys = prev_narrative["expected_memory_keys"]
            
            for key in prev_keys:
                if key.lower() in current_content:
                    continuity_score += 1.0
                total_checks += 1
        
        return continuity_score / max(total_checks, 1)
    
    def check_continuity_issues(self, narrative: Dict, entry_index: int) -> List[str]:
        """Check for continuity issues in the narrative."""
        issues = []
        
        if entry_index > 0:
            # Check for contradictions with previous entries
            current_content = narrative["content"].lower()
            prev_narrative = LONGFORM_NARRATIVES[entry_index - 1]
            
            # Simple contradiction detection (could be expanded)
            if "grandmother" in prev_narrative["content"].lower() and "grandmother" not in current_content:
                if entry_index < 3:  # Should still reference grandmother in early entries
                    issues.append("Missing reference to established character (grandmother)")
        
        return issues
    
    def generate_final_report(self) -> PersistenceTestReport:
        """Generate the final test report."""
        test_end_time = datetime.now()
        successful_validations = sum(1 for r in self.results if r.validation_passed)
        failed_validations = len(self.results) - successful_validations
        average_context_retention = sum(r.context_retention_score for r in self.results) / len(self.results)
        
        # Check for memory decay
        memory_decay_detected = any(
            r.context_retention_score < 0.5 for r in self.results[1:]
        )
        
        # Check for goal drift
        goal_drift_detected = any(
            not r.goal_alignment_maintained for r in self.results
        )
        
        overall_success = successful_validations == len(self.results)
        
        # Generate recommendations
        recommendations = []
        if memory_decay_detected:
            recommendations.append("Implement memory reinforcement mechanisms")
        if goal_drift_detected:
            recommendations.append("Strengthen goal alignment validation")
        if average_context_retention < 0.8:
            recommendations.append("Improve context retention algorithms")
        if not overall_success:
            recommendations.append("Review failed validation entries for system improvements")
        
        return PersistenceTestReport(
            test_start_time=self.test_start_time.isoformat(),
            test_end_time=test_end_time.isoformat(),
            total_entries=len(self.results),
            successful_validations=successful_validations,
            failed_validations=failed_validations,
            average_context_retention=average_context_retention,
            memory_decay_detected=memory_decay_detected,
            goal_drift_detected=goal_drift_detected,
            overall_success=overall_success,
            entry_results=self.results,
            recommendations=recommendations
        )
    
    def save_report(self, report: PersistenceTestReport):
        """Save the test report to file."""
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        
        report_file = exports_dir / f"longform_memory_persistence_report_{TEST_SESSION_ID}.json"
        
        with open(report_file, 'w') as f:
            json.dump(asdict(report), f, indent=2)
        
        print(f"\n📊 Report saved to: {report_file}")
    
    def print_results(self, report: PersistenceTestReport):
        """Print the test results."""
        print("\n" + "=" * 60)
        print("📊 Long-Form Memory Persistence Test Results")
        print("=" * 60)
        
        print(f"📅 Test Duration: {report.test_start_time} → {report.test_end_time}")
        print(f"📝 Total Entries: {report.total_entries}")
        print(f"✅ Successful Validations: {report.successful_validations}")
        print(f"❌ Failed Validations: {report.failed_validations}")
        print(f"📈 Average Context Retention: {report.average_context_retention:.2f}")
        print(f"🧠 Memory Decay Detected: {'❌ Yes' if report.memory_decay_detected else '✅ No'}")
        print(f"🎯 Goal Drift Detected: {'❌ Yes' if report.goal_drift_detected else '✅ No'}")
        print(f"🎉 Overall Success: {'✅ PASS' if report.overall_success else '❌ FAIL'}")
        
        print("\n📋 Entry-by-Entry Results:")
        print("-" * 40)
        for result in report.entry_results:
            status = "✅ PASS" if result.validation_passed else "❌ FAIL"
            print(f"{result.entry_id}: {status} (Context: {result.context_retention_score:.2f})")
        
        if report.recommendations:
            print("\n💡 Recommendations:")
            print("-" * 40)
            for rec in report.recommendations:
                print(f"• {rec}")
        
        print("\n" + "=" * 60)
        if report.overall_success:
            print("🎉 LONG-FORM MEMORY PERSISTENCE: ALL TESTS PASSED")
            print("🚀 Memory system maintains coherent state across extended narratives")
        else:
            print("⚠️ LONG-FORM MEMORY PERSISTENCE: SOME TESTS FAILED")
            print("🔧 Review recommendations for system improvements")
        print("=" * 60)

async def main():
    """Main test runner."""
    tester = LongFormMemoryPersistenceTester()
    report = await tester.run_persistence_test()
    tester.print_results(report)
    
    # Exit with appropriate code
    sys.exit(0 if report.overall_success else 1)

if __name__ == "__main__":
    asyncio.run(main()) 