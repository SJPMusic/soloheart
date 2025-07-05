# SoloHeart Changelog

This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License.

## [Enhanced Character Creation] - 2025-07-04

### Added
- **Symbolic Meaning Framework**: Complete implementation of Jordan B. Peterson's *Maps of Meaning* principles
  - Archetypal tagging system with 20+ Jungian archetypes (Father, Shadow, Journey, etc.)
  - Chaos/order tension tracking with dynamic state management
  - Narrative decay detection for contradictions and avoidance patterns
  - Symbolic coherence assessment for meaningful character development
  - Integration with character fact extraction and memory systems
- **Enhanced Character Creation**: Immediate fact commitment without staging
  - Robust fact extraction from complex, multi-sentence descriptions
  - Immediate commitment of facts to character sheet (no pending states)
  - Ambiguity detection with intelligent confirmation requests
  - Confidence scoring for extracted facts
  - DnD 5E compliance tracking for missing required fields
- **Advanced Fact Extraction**: Comprehensive character fact extraction
  - Name, age, race, class, background extraction with pattern matching
  - Personality traits, motivations, emotional themes extraction
  - Combat style, experience, gear, and relational history extraction
  - Trauma and backstory extraction with emotional context
  - Gender and alignment detection from natural language
- **Symbolic Integration**: Facts tagged with archetypal meaning
  - Automatic archetypal tagging of all character facts
  - Chaos/order impact assessment for each fact
  - Narrative decay detection from contradictions
  - Symbolic coherence scoring for character development
  - Archetypal state persistence across sessions

### Changed
- **Character Creation Flow**: Replaced linear questioning with immediate fact commitment
  - No more staged fact collection or pending states
  - Facts committed immediately upon extraction
  - Only requests confirmation for truly ambiguous information
  - Seamless transition from character creation to gameplay
- **Memory System Integration**: Enhanced with symbolic meaning
  - Emotional memory now includes archetypal context
  - Chaos/order tension influences memory relevance
  - Symbolic coherence affects narrative responses
  - Archetypal state maintained across campaign sessions
- **API Endpoints**: Updated for enhanced character creation
  - New `/api/character/vibe-code/start` with immediate fact extraction
  - Enhanced `/api/character/vibe-code/continue` with symbolic analysis
  - New `/api/character/vibe-code/symbolic` for archetypal state
  - Updated character summary with symbolic meaning display

### Technical Improvements
- **Fact Extraction Engine**: Centralized utilities in `utils/character_fact_extraction.py`
  - 15+ extraction functions for different character aspects
  - Pattern matching with regex and word boundary detection
  - Confidence scoring and ambiguity detection
  - Integration with symbolic meaning framework
- **Symbolic Framework**: New `utils/symbolic_meaning_framework.py`
  - ArchetypalTags enum with 20+ archetypes
  - ChaosOrderState enum for tension tracking
  - SymbolicMeaningFramework class with full functionality
  - Narrative response generation based on symbolic state
- **Error Handling**: Enhanced error management
  - Graceful handling of extraction failures
  - Symbolic data initialization and validation
  - Character data reset and recovery mechanisms
  - Comprehensive logging for debugging

### Performance
- **Immediate Processing**: Facts processed and committed in real-time
- **Efficient Symbolic Analysis**: Archetypal tagging without performance impact
- **Optimized Memory Usage**: Symbolic data stored efficiently
- **Fast Response Times**: Enhanced extraction without latency increase

## [Unreleased] - 2025-07-02

### Fixed
- **Race Extraction Logic**: Prioritized longer race matches ("Half-Elf" over "Elf") in race extraction logic
  - Created centralized utility functions in `utils/character_fact_extraction.py`
  - Implemented word boundary matching with regex patterns
  - Added fallback substring matching with confirmation patterns
  - Consolidated race extraction across all relevant functions
  - Enhanced logging with detailed input → match → result traces
  - Added comprehensive test coverage for race extraction edge cases

### Added
- **Utility Functions**: New `utils/character_fact_extraction.py` module with:
  - `extract_race_from_text()` - Robust race extraction with length priority
  - `extract_class_from_text()` - Class extraction with similar logic
  - `extract_background_from_text()` - Background extraction
  - `extract_name_from_text()` - Name extraction with pattern matching
- **Enhanced Logging**: Improved logging across all character creation endpoints
  - Raw user input logging
  - Extracted fact logging
  - Full traceback logging for debugging
- **Comprehensive Testing**: Added extensive test coverage
  - Direct utility function testing
  - Race extraction edge case testing
  - Integration testing with API endpoints

### Changed
- **Code Organization**: Refactored character fact extraction to use centralized utilities
  - Replaced duplicated race extraction logic in multiple functions
  - Standardized extraction behavior across the codebase
  - Improved maintainability and consistency

### Technical Details
- **Race Matching Strategy**: 
  - Sorts races by length (longest first) to prioritize longer matches
  - Uses regex word boundaries (`\b`) to ensure full word matches
  - Handles hyphenated races like "Half-Elf" correctly
  - Falls back to substring matching with confirmation patterns
- **Test Coverage**: 
  - 8 race extraction test cases covering edge cases
  - 8 class extraction test cases
  - Utility function direct testing
  - API integration testing with 60-second timeouts 