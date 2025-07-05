# Archive Plan - SoloHeart Project Cleanup

## Overview
This document outlines the redundant and unused files/folders that will be archived to clean up the project structure.

## Redundant Directories

### 1. Duplicate Project Directories
- `SoloHeart/` - Duplicate of main project structure
- `solo-heart-ui/` - Old UI implementation (replaced by page-ui)
- `narrative_engine/` - Standalone narrative engine (functionality integrated into main project)

### 2. Backup/Archive Directories
- `archive_cleanup_backup/` - Contains old backups that are no longer needed
- `archive_unused/` - Already archived files

## Redundant Files

### 1. Empty/Unused Interface Files
- `unified_narrative_interface.py` (0 bytes)
- `unified_game_interface.py` (0 bytes)
- `unified_narrative_interface.py` (in SoloHeart/)
- `unified_game_interface.py` (in SoloHeart/)

### 2. Old/Backup Files
- `simple_unified_interface_backup.py` - Backup of main interface
- `simple_unified_interface_mock.py` - Mock version
- `character_schema.json.backup` - Backup schema file
- `consumer_launcher_old.py` - Old launcher

### 3. Test Files (Redundant)
- `test_semantic_analysis.py` (23B) - Empty test file
- `test_brannic.py` (1.0B) - Empty test file
- `test_ollama_integration.py` - Integration test
- `test_orchestrator_simple.py` - Orchestrator test
- `test_ai_memory.py` - Memory test
- `test_character_memory_storage.py` - Memory storage test
- `test_vibe_code_character_creation.py` - Old vibe code test
- `test_incremental_character_facts.py` - Incremental facts test
- `test_character_review_and_edits.py` - Review/edits test
- `test_mock_llm_simple.py` - Mock LLM test
- `demo_character_creation_enhancements.py` - Demo file
- `test_real_api_character_memory.py` - API memory test
- `test_complete_character_flow.py` - Complete flow test
- `test_narrative_engine_integration.py` - Engine integration test
- `test_character_prompts.py` - Character prompts test
- `test_character_prompts_detailed.py` - Detailed prompts test
- `comprehensive_test_analysis.py` - Comprehensive test analysis

### 4. Documentation Files (Redundant)
- `CHARACTER_CREATION_ENHANCEMENTS_SUMMARY.md`
- `STABILITY_FIRST_CHARACTER_CREATION_SUMMARY.md`
- `COURSE_CORRECTION_SUMMARY.md`
- `FEATURE_BRANCH_SUMMARY.md`
- `EMAIL_PITCH.md`
- `LINKEDIN_ABOUT.md`
- `demo_screenshot.txt`

### 5. Configuration/Setup Files (Redundant)
- `setup_monitoring.py` - Monitoring setup
- `check_status.py` - Status checker
- `launch_with_monitor.py` - Monitor launcher
- `server_monitor.py` - Server monitor
- `com.soloheart.game.plist` - macOS plist
- `soloheart.service` - Service file

### 6. Docker/Deployment Files (Unused)
- `Dockerfile`
- `Dockerfile.prod`
- `docker-compose.yml`
- `docker-utils.sh`
- `.dockerignore`
- `DOCKER_README.md`

### 7. Development Files (Redundant)
- `consumer_launcher.py` (root) - Root launcher
- `consumer_launcher_old.py` - Old launcher
- `launch_unified.py` - Unified launcher
- `launch_start_flow.py` - Start flow launcher
- `launch_game.py` - Game launcher
- `narrative_focused_interface.py` - Narrative interface
- `start_screen_interface.py` - Start screen interface

### 8. Data Files (Redundant)
- `orchestrator_Orchestrator Integration Test.jsonl`
- `plot_threads.jsonl`
- `character_arcs.jsonl`
- `memory_traces.jsonl` (0 bytes)
- `journal_entries.jsonl`

### 9. UI Files (Redundant)
- `simple_test_interface.html` - Test interface
- `test_character_sheet.html` - Test character sheet

## Archive Structure

```
archive_2025-07-04/
├── redundant_directories/
│   ├── SoloHeart/
│   ├── solo-heart-ui/
│   ├── narrative_engine/
│   └── archive_cleanup_backup/
├── redundant_files/
│   ├── interfaces/
│   ├── tests/
│   ├── documentation/
│   ├── configuration/
│   ├── docker/
│   ├── launchers/
│   └── data/
└── archive_log.md
```

## Recovery Instructions

To restore any archived files:
1. Navigate to the archive directory
2. Copy the needed files back to their original location
3. Update any import statements if necessary

## Files to Keep

### Core Application Files
- `solo_heart/simple_unified_interface.py` - Main application
- `solo_heart/templates/` - UI templates
- `solo_heart/utils/` - Utility functions
- `solo_heart/character_generator.py` - Character generation
- `solo_heart/narrative_bridge.py` - Narrative bridge
- `solo_heart/ollama_llm_service.py` - LLM service

### Configuration Files
- `requirements.txt` - Dependencies
- `.gitignore` - Git ignore rules
- `README.md` - Project documentation

### Essential Documentation
- `LICENSE.txt` - License
- `SECURITY.md` - Security policy
- `CONTRIBUTING.md` - Contributing guidelines
- `HOW_TO_PLAY.md` - How to play guide

## Archive Execution

The archive will be created with the following structure:
- All redundant files moved to appropriate subdirectories
- Archive log created with timestamps and original locations
- Recovery instructions included
- Original file structure preserved in archive 