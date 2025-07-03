# SoloHeart Changelog

This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License.

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