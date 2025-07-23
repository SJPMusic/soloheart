# Step-by-Step Character Creation Memory Integration Tests

## Overview

This test suite verifies that the Step-by-Step Character Creator properly integrates with the narrative memory system. It ensures that as each character field is filled in, the extracted value is committed to memory with proper tagging and metadata.

## Test Purpose

The tests are designed to **fail** when memory integration is missing, ensuring that:

1. **No fields are skipped** in memory storage
2. **Tags are properly formatted** with required metadata
3. **Field and value consistency** is maintained
4. **Campaign ID consistency** is preserved across all entries
5. **Memory type consistency** is maintained
6. **Edit operations** properly update memory
7. **Skip operations** don't create unnecessary memory entries
8. **Completion** creates a summary memory entry

## Expected Memory Entry Format

Each field should result in a memory entry similar to:

```json
{
  "type": "trait",
  "field": "race",
  "value": "Half-Elf",
  "campaign_id": "test-campaign-001",
  "memory_type": "character_creation",
  "character_id": "player",
  "timestamp": "2024-01-01T12:00:00",
  "tags": ["character_creation", "trait", "race"]
}
```

## Test Cases

### 1. Field Memory Entry Format (`test_field_memory_entry_format`)
- **Purpose**: Verify each field creates properly formatted memory entries
- **Input**: Sequence of field inputs (race, class, gender, background, personality)
- **Expected**: Each field triggers a memory storage call with correct metadata
- **Current Status**: ❌ **FAILS** - No memory integration implemented

### 2. No Skipped Fields (`test_no_skipped_fields`)
- **Purpose**: Ensure all fields are stored in memory
- **Input**: Complete character creation with all 9 fields
- **Expected**: 9 memory entries (one per field)
- **Current Status**: ❌ **FAILS** - No memory integration implemented

### 3. Malformed Tags Detection (`test_malformed_tags_fail`)
- **Purpose**: Verify memory entries have proper tag structure
- **Input**: Single field input
- **Expected**: Memory entry with required fields and proper tag format
- **Current Status**: ❌ **FAILS** - No memory integration implemented

### 4. Field Value Consistency (`test_field_value_consistency`)
- **Purpose**: Ensure stored values match user input
- **Input**: Various field inputs with expected parsed values
- **Expected**: Stored values are consistent with input (allowing for parsing variations)
- **Current Status**: ❌ **FAILS** - No memory integration implemented

### 5. Campaign ID Consistency (`test_campaign_id_consistency`)
- **Purpose**: Verify all memory entries use the same campaign ID
- **Input**: Multiple field inputs
- **Expected**: All memory entries have identical campaign_id
- **Current Status**: ❌ **FAILS** - No memory integration implemented

### 6. Memory Type Consistency (`test_memory_type_consistency`)
- **Purpose**: Ensure all entries have correct memory_type
- **Input**: Multiple field inputs
- **Expected**: All entries have memory_type = "character_creation"
- **Current Status**: ✅ **PASSES** - Test structure is correct

### 7. Trait Type Consistency (`test_trait_type_consistency`)
- **Purpose**: Verify all character fields have type = "trait"
- **Input**: Multiple field inputs
- **Expected**: All entries have type = "trait"
- **Current Status**: ✅ **PASSES** - Test structure is correct

### 8. Edit Field Memory Update (`test_edit_field_memory_update`)
- **Purpose**: Test that editing fields updates memory correctly
- **Input**: Set field, edit field, set new value
- **Expected**: Two memory entries (initial + edit)
- **Current Status**: ❌ **FAILS** - No memory integration implemented

### 9. Skip Field No Memory (`test_skip_field_no_memory`)
- **Purpose**: Verify skipped fields don't create memory entries
- **Input**: Set some fields, skip optional field
- **Expected**: Memory entries only for non-skipped fields
- **Current Status**: ❌ **FAILS** - No memory integration implemented

### 10. Complete Character Creation Summary (`test_complete_character_creation_memory_summary`)
- **Purpose**: Test completion creates summary memory entry
- **Input**: Complete all character fields
- **Expected**: N+1 memory entries (N fields + 1 completion summary)
- **Current Status**: ❌ **FAILS** - No memory integration implemented

## Implementation Requirements

To make these tests pass, the `StepByStepCharacterCreator` needs to be modified to:

1. **Accept a narrative bridge instance** in the constructor
2. **Call memory storage** after each field is successfully parsed
3. **Use proper metadata format** for memory entries
4. **Handle edit operations** by storing updated values
5. **Skip memory storage** for skipped fields
6. **Create completion summary** when character creation is finished

## Example Implementation

```python
class StepByStepCharacterCreator:
    def __init__(self, narrative_bridge=None, campaign_id="test-campaign-001"):
        self.narrative_bridge = narrative_bridge
        self.campaign_id = campaign_id
        # ... existing initialization ...
    
    def _store_field_memory(self, field: str, value: str):
        """Store a field value in memory."""
        if self.narrative_bridge:
            self.narrative_bridge.store_solo_game_memory(
                content=f"Character trait set: {field} = {value}",
                memory_type="character_creation",
                metadata={
                    "type": "trait",
                    "field": field,
                    "value": value,
                    "campaign_id": self.campaign_id,
                    "character_id": "player"
                },
                tags=["character_creation", "trait", field],
                character_id="player"
            )
    
    def process_response(self, user_input: str) -> str:
        # ... existing processing logic ...
        
        if parsed_value:
            self.state[current_field] = parsed_value
            # Store in memory
            self._store_field_memory(current_field, parsed_value)
            # ... continue with existing logic ...
```

## Running the Tests

```bash
cd SoloHeart
python tests/memory/test_step_by_step_memory_capture.py
```

## Expected Behavior

- **Current**: Tests fail because memory integration is not implemented
- **After Implementation**: All tests should pass, verifying proper memory integration
- **Regression**: If memory integration is broken, tests will fail and catch the issue

## Integration Points

The tests verify integration with:
- `NarrativeBridge.store_solo_game_memory()` method
- Proper metadata structure for memory entries
- Campaign ID consistency
- Field value parsing and storage
- Edit and skip operation handling 