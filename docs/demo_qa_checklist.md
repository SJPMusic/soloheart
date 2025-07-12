
# ✅ Narrative Engine D&D Demo — QA Checklist

## 🔰 A. Initialization & Environment Setup

- [ ] `.env` file is present and valid  
  - [ ] Points to the correct active LLM (e.g., `GEMMA_API_URL=http://localhost:1234/v1`)
  - [ ] Contains no references to Ollama unless specifically required
  - [ ] Has entries for bridge and engine endpoints if needed

- [ ] App starts via `python3 simple_unified_interface.py` with no warnings
- [ ] Health check endpoint (`/api/health`) returns `{"status": "ok"}`

## 🧱 B. Modular Boundary Compliance

- [ ] No file in SoloHeart imports from `narrative_engine` or `narrative_bridge` directly  
  _(Only interface through configured endpoints or bridge methods)_

- [ ] No class, method, or file name in TNE/TNB includes the term `soloheart`
- [ ] All symbolic logic is processed via TNE, not locally in the UI layer

## 🧠 C. Memory & Goal Flow Validation

- [ ] Player input is successfully routed to TNB and TNE
- [ ] Memory entries are returned, tagged with types (episodic, emotional, etc.)
- [ ] Goal inference returns correctly and populates UI fields
- [ ] Confidence indicators and timestamps appear on goals (if implemented)
- [ ] Memory entries degrade or evolve over multiple turns (if decay is active)

## 🎭 D. Character Creation & Narrative Input

- [ ] Character creation form accepts and forwards freeform input
- [ ] Vibe code entry maps to a generated character sheet via TNE logic
- [ ] No hardcoded story paths are used during or after character creation
- [ ] Input reflects modular symbolic parsing (e.g., tags, tokens, goal alignment)

## 🎨 E. UI Display Layer

- [ ] Player input is shown in a dedicated pane or stream
- [ ] LLM responses are clearly marked and separated from player text
- [ ] Memory entries appear in a scrollable, filterable panel
- [ ] Goals inferred from input are displayed with symbolic or confidence indicators

## 🔌 F. LLM Routing & Provider Modularity

- [ ] `.env` switching between LLMs functions as expected:
  - [ ] Gemma responds to inputs
  - [ ] Ollama fallback (if enabled) does not hijack symbolic logic
- [ ] Provider abstraction layer logs which backend is in use
- [ ] No LLM-specific hacks or bypass logic is present in the UI

## 📂 G. Legacy Cleanup (Confirmed)

- [ ] `ollama_provider.py` and fallback logic are removed or archived
- [ ] No scripted roleplay modules exist (e.g., "scene1_fallback.py", etc.)
- [ ] No SoloHeart-specific branding remains in:
  - README
  - Terminal logs
  - Class/function names
  - Help dialogs

## 🧪 H. Resilience & Failure Modes

- [ ] If the LLM is offline or errors out:
  - [ ] UI shows graceful failure message (not a traceback)
  - [ ] No logic fallback is triggered
  - [ ] Player is prompted to retry or check system status

- [ ] If TNE or TNB is offline:
  - [ ] Request timeout is handled cleanly
  - [ ] UI disables further input and logs issue

## 🗂 I. Documentation & Dev Hygiene

- [ ] `pivot_strategy.md` reflects accurate rationale and scope
- [ ] `cursor_refactor_spec.md` matches implementation logic
- [ ] `soloheart_pivot_audit.md` correctly labels Archived / Merged / Kept assets
- [ ] README clearly states that this project is a **demo layer for The Narrative Engine**

## ✅ Final Sanity Check

- [ ] All logs, errors, and system messages reflect the new modular purpose
- [ ] All interaction flows demonstrate symbolic interpretation and goal tracking
- [ ] The system is ready to be presented as a clean, maintainable **Narrative Engine demo layer**
