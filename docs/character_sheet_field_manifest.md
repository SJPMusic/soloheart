# CharacterSheet Field Manifest

## Overview

This document provides a complete field mapping manifest for the `CharacterSheet` class used in SoloHeart. Each field is documented with its data type, source, validation rules, and vibe code compatibility status.

## Field Categories

The CharacterSheet fields are organized into the following categories:
- **Identity**: Basic character identification and metadata
- **Ability Scores**: Core D&D 5E ability scores and derived modifiers
- **Saving Throws**: Ability-based saving throw proficiencies and modifiers
- **Skills**: All 18 SRD skills with proficiency tracking
- **Combat Stats**: Combat-related statistics and health tracking
- **Attacks & Spellcasting**: Weapon attacks and magical abilities
- **Equipment & Currency**: Items, gear, and monetary resources
- **Proficiencies & Feats**: Character capabilities and special abilities
- **Personality & Story**: Character background and roleplay elements
- **Physical Description**: Visual and descriptive character details
- **Metadata**: System-level tracking and management data

## Field Manifest

| Field Name | Data Type | Source | Validation Rules | Vibe Compatible |
|------------|-----------|--------|------------------|------------------|

### Identity

| Field Name | Data Type | Source | Validation Rules | Vibe Compatible |
|------------|-----------|--------|------------------|------------------|
| `alignment` | `str` | user | enum (Lawful Good, Neutral Good, Chaotic Good, Lawful Neutral, True Neutral, Chaotic Neutral, Lawful Evil, Neutral Evil, Chaotic Evil) | ✅ |
| `background` | `str` | srd | SRD only, non-empty | ✅ |
| `campaign_id` | `Optional[str]` | derived | optional | ✅ |
| `character_name` | `str` | user | non-empty | ✅ |
| `class_name` | `str` | srd | SRD only, non-empty | ✅ |
| `created_date` | `str` | derived | ISO format | ❌ |
| `creation_method` | `str` | derived | optional | ✅ |
| `experience_points` | `int` | user | range 0-∞ | ✅ |
| `inspiration` | `bool` | user | optional | ✅ |
| `last_modified` | `str` | derived | ISO format | ❌ |
| `level` | `int` | user | range 1-20 | ✅ |
| `player_name` | `str` | user | optional | ✅ |
| `race` | `str` | srd | SRD only, non-empty | ✅ |

### Ability Scores

| Field Name | Data Type | Source | Validation Rules | Vibe Compatible |
|------------|-----------|--------|------------------|------------------|
| `charisma` | `int` | user | range 1-20 | ✅ |
| `charisma_mod` | `int` | derived | calculated from charisma | ❌ |
| `constitution` | `int` | user | range 1-20 | ✅ |
| `constitution_mod` | `int` | derived | calculated from constitution | ❌ |
| `dexterity` | `int` | user | range 1-20 | ✅ |
| `dexterity_mod` | `int` | derived | calculated from dexterity | ❌ |
| `intelligence` | `int` | user | range 1-20 | ✅ |
| `intelligence_mod` | `int` | derived | calculated from intelligence | ❌ |
| `proficiency_bonus` | `int` | derived | calculated from level | ❌ |
| `strength` | `int` | user | range 1-20 | ✅ |
| `strength_mod` | `int` | derived | calculated from strength | ❌ |
| `wisdom` | `int` | user | range 1-20 | ✅ |
| `wisdom_mod` | `int` | derived | calculated from wisdom | ❌ |

### Saving Throws

| Field Name | Data Type | Source | Validation Rules | Vibe Compatible |
|------------|-----------|--------|------------------|------------------|
| `saving_throws` | `Dict[str, Dict[str, Union[bool, int]]]` | derived | structure: {"ability": {"is_proficient": bool, "modifier": int}} | ⚠️ |

### Skills

| Field Name | Data Type | Source | Validation Rules | Vibe Compatible |
|------------|-----------|--------|------------------|------------------|
| `skills` | `Dict[str, Dict[str, Union[str, bool, int]]]` | derived | structure: {"skill_name": {"ability": str, "is_proficient": bool, "modifier": int}} | ⚠️ |

### Combat Stats

| Field Name | Data Type | Source | Validation Rules | Vibe Compatible |
|------------|-----------|--------|------------------|------------------|
| `armor_class` | `int` | derived | range 0-∞ | ✅ |
| `death_saves` | `Dict[str, int]` | user | structure: {"successes": int, "failures": int}, range 0-3 each | ✅ |
| `hit_dice_remaining` | `str` | derived | dice notation format | ✅ |
| `hit_dice_total` | `str` | derived | dice notation format | ✅ |
| `hit_points_current` | `int` | user | range 0-∞ | ✅ |
| `hit_points_max` | `int` | derived | range 1-∞ | ✅ |
| `initiative` | `int` | derived | calculated from dexterity_mod | ❌ |
| `passive_perception` | `int` | derived | calculated from perception skill | ❌ |
| `speed` | `int` | derived | range 0-∞ | ✅ |
| `temporary_hit_points` | `int` | user | range 0-∞ | ✅ |

### Attacks & Spellcasting

| Field Name | Data Type | Source | Validation Rules | Vibe Compatible |
|------------|-----------|--------|------------------|------------------|
| `attacks` | `List[Dict[str, Union[str, int]]]` | user | structure: {"name": str, "attack_bonus": int, "damage": str, "damage_type": str} | ⚠️ |
| `spellcasting` | `Dict[str, Any]` | derived | complex structure with spellcasting data | ⚠️ |

### Equipment & Currency

| Field Name | Data Type | Source | Validation Rules | Vibe Compatible |
|------------|-----------|--------|------------------|------------------|
| `currency` | `Dict[str, int]` | user | structure: {"cp": int, "sp": int, "ep": int, "gp": int, "pp": int}, range 0-∞ | ✅ |
| `equipment` | `List[str]` | user | optional | ✅ |

### Proficiencies & Feats

| Field Name | Data Type | Source | Validation Rules | Vibe Compatible |
|------------|-----------|--------|------------------|------------------|
| `armor_proficiencies` | `List[str]` | derived | SRD armor types | ✅ |
| `feats` | `List[str]` | srd | SRD only | ✅ |
| `languages` | `List[str]` | derived | SRD language names | ✅ |
| `tool_proficiencies` | `List[str]` | derived | SRD tool names | ✅ |
| `weapon_proficiencies` | `List[str]` | derived | SRD weapon categories | ✅ |

### Personality & Story

| Field Name | Data Type | Source | Validation Rules | Vibe Compatible |
|------------|-----------|--------|------------------|------------------|
| `allies_and_organizations` | `List[str]` | user | optional | ✅ |
| `backstory` | `str` | user | optional | ✅ |
| `bonds` | `str` | user | optional | ✅ |
| `character_appearance` | `str` | user | optional | ✅ |
| `features_and_traits` | `List[str]` | derived | from race, class, background | ✅ |
| `faction_symbol` | `Optional[str]` | user | optional | ✅ |
| `flaws` | `str` | user | optional | ✅ |
| `ideals` | `str` | user | optional | ✅ |
| `personality_traits` | `str` | user | optional | ✅ |

### Physical Description

| Field Name | Data Type | Source | Validation Rules | Vibe Compatible |
|------------|-----------|--------|------------------|------------------|
| `age` | `str` | user | optional | ✅ |
| `eyes` | `str` | user | optional | ✅ |
| `hair` | `str` | user | optional | ✅ |
| `height` | `str` | user | optional | ✅ |
| `skin` | `str` | user | optional | ✅ |
| `weight` | `str` | user | optional | ✅ |

## Field Source Definitions

- **user**: Entered directly by the player during character creation
- **srd**: Must match a predefined SRD option from the SRD data files
- **derived**: Calculated or inferred from other values automatically

## Validation Rules Definitions

- **SRD only**: Must exist in the corresponding `srd_data` file (races.json, classes.json, backgrounds.json, feats.json)
- **non-empty**: Field must contain a value and cannot be empty
- **range**: For numeric fields, specifies the valid range (e.g., 1-20 for ability scores)
- **enum**: Field is constrained to a fixed set of values (e.g., alignment options)
- **optional**: Field can be omitted or set to null/empty without validation errors
- **structure**: Complex data structures with specific format requirements

## Vibe Code Compatibility Definitions

- **✅**: Value can be mapped directly from vibe code output without transformation
- **⚠️**: Mapping requires special logic or transformation (e.g., complex data structures)
- **❌**: Not relevant to vibe code input (e.g., system-generated timestamps)

## Usage Notes

### For Developers
- Use this manifest as a source of truth for field validation
- Reference validation rules when implementing new features
- Check vibe compatibility when designing vibe code integration

### For SRD Enforcement
- All fields marked as "SRD only" must be validated against the corresponding SRD data files
- Non-SRD content should never be accepted for these fields
- Validation should occur both during creation and when loading existing characters

### For Vibe Code Integration
- Fields marked as ✅ can be directly mapped from vibe code output
- Fields marked as ⚠️ require special handling for proper mapping
- Fields marked as ❌ should be generated by the system, not mapped from vibe code

### For QA Testing
- Use this manifest as a checklist for field validation testing
- Ensure all validation rules are properly enforced
- Verify vibe code compatibility for all relevant fields

## Schema Evolution

When adding new fields to the CharacterSheet class:
1. Add the field to this manifest with complete metadata
2. Update validation rules in the `validate_field()` method
3. Ensure proper vibe code compatibility
4. Update tests to cover the new field
5. Document any breaking changes

## Related Files

- `game_app/character_sheet.py` - Main CharacterSheet implementation
- `srd_data/races.json` - SRD race definitions
- `srd_data/classes.json` - SRD class definitions
- `srd_data/backgrounds.json` - SRD background definitions
- `srd_data/feats.json` - SRD feat definitions
- `game_app/interactive_character_creator.py` - Interactive creation logic
- `game_app/enhanced_step_by_step_creator.py` - Enhanced creation flow 