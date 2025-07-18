#!/usr/bin/env python3

from utils.character_fact_extraction import extract_all_facts_from_text, assess_fact_confidence

text = """His name is Brannic Thorn, a 32-year-old dwarf who once served as a royal blacksmith. After losing his arm in a mysterious forge explosion, he crafted a mechanical replacement powered by arcane energy. Brannic left the mountain kingdom in disgrace, blamed for a fire he did not start. Now he roams from town to town, fixing broken weapons and searching for whoever sabotaged his workshop. He does not talk much, but his eyes never stop scanning a room."""

print("🔍 Testing Brannic Thorn character extraction...")
print(f"📝 Input text: {text[:100]}...")
print()

facts = extract_all_facts_from_text(text)

print("📋 Extracted Facts:")
for fact_type, value in facts.items():
    if not fact_type.startswith('_'):
        print(f"  {fact_type}: {value}")

print()
print("🎯 Confidence Assessment:")
for fact_type, value in facts.items():
    if not fact_type.startswith('_'):
        is_confident, confidence = assess_fact_confidence(fact_type, value, text)
        status = "✅ CONFIDENT" if is_confident else "⚠️ LOW CONFIDENCE"
        print(f"  {fact_type}: {value} - {status} (score: {confidence:.2f})")

print()
print("🔧 Issues Found:")
issues = []
if facts.get("name") != "Brannic Thorn":
    issues.append(f"Name extraction: got '{facts.get('name')}' instead of 'Brannic Thorn'")
if facts.get("age") != 32:
    issues.append(f"Age extraction: got '{facts.get('age')}' instead of 32")
if facts.get("class") == "Wizard":
    issues.append("Class extraction: got 'Wizard' instead of 'Fighter' (blacksmith background)")
if not facts.get("traumas"):
    issues.append("Missing trauma extraction for lost arm")
if not facts.get("motivations") or "sabotage" not in str(facts.get("motivations")).lower():
    issues.append("Missing motivation extraction for finding saboteur")

for issue in issues:
    print(f"  ❌ {issue}")

if not issues:
    print("  ✅ All expected facts extracted correctly!") 