# SoloHeart Character Creation Flow - Manual Test Plan

## 1. Metadata

- **Test Name**: Character Creation Flow
- **Last Updated**: 2025-07-19
- **Tested By**: [Manual entry]
- **SoloHeart Version**: v0.9.1
- **Server URL**: http://localhost:5001
- **Test Environment**: Local Development

## 2. Prerequisites

- [ ] Server running at `http://localhost:5001`
- [ ] Browser or HTTP client access
- [ ] Local storage enabled (if testing browser state persistence)
- [ ] Network connectivity for API calls
- [ ] JavaScript enabled in browser

---

## 3. Test: Start Screen Load

**Objective**: Verify the start screen displays correctly with all required options

- [ ] Navigate to `http://localhost:5001`
- [ ] Verify page loads without errors
- [ ] Confirm display of campaign list (empty if no campaigns exist)
- [ ] Verify presence of character creation section
- [ ] Confirm the two character creation buttons exist:
  - [ ] "📝 Step-by-Step Creation" button
  - [ ] "✨ Vibe Code Creation" button
- [ ] Verify button styling and hover effects work
- [ ] Check that page title is "SoloHeart - Start Screen"

**Expected Result**: Start screen displays with both character creation options clearly visible

---

## 4. Test: Step-by-Step Creation

**Objective**: Validate the traditional form-based character creation process

### 4.1 Navigation to Character Creation
- [ ] Click on "📝 Step-by-Step Creation" button
- [ ] Confirm redirection to `/character-creation`
- [ ] Verify page title changes to "Character Creation"
- [ ] Check that form loads without JavaScript errors

### 4.2 Form Field Validation
- [ ] Verify presence of all required input fields:
  - [ ] **Name** (text input, required)
  - [ ] **Race** (dropdown/select, required)
  - [ ] **Class** (dropdown/select, required)
  - [ ] **Background** (dropdown/select, optional)
  - [ ] **Level** (number input, default: 1)
  - [ ] **Age** (number input, optional)
  - [ ] **Gender** (text input, optional)
  - [ ] **Alignment** (dropdown/select, optional)

### 4.3 Ability Scores Section
- [ ] Verify all six ability scores are present:
  - [ ] **Strength** (number input, 1-20 range)
  - [ ] **Dexterity** (number input, 1-20 range)
  - [ ] **Constitution** (number input, 1-20 range)
  - [ ] **Intelligence** (number input, 1-20 range)
  - [ ] **Wisdom** (number input, 1-20 range)
  - [ ] **Charisma** (number input, 1-20 range)
- [ ] Verify ability modifiers are calculated and displayed
- [ ] Test ability score validation (invalid values should be rejected)

### 4.4 Combat Stats Section
- [ ] Verify combat-related fields:
  - [ ] **Hit Points** (number input, calculated or manual)
  - [ ] **Armor Class** (number input, calculated or manual)
  - [ ] **Speed** (number input, feet per round)
  - [ ] **Initiative Bonus** (number input, calculated from DEX)

### 4.5 Skills and Proficiencies
- [ ] Verify skills section:
  - [ ] **Skill Proficiencies** (checkbox list or multi-select)
  - [ ] **Tool Proficiencies** (checkbox list or multi-select)
  - [ ] **Language Proficiencies** (checkbox list or multi-select)

### 4.6 Equipment and Items
- [ ] Verify equipment section:
  - [ ] **Weapons** (multi-select or text area)
  - [ ] **Armor** (dropdown/select)
  - [ ] **Equipment Pack** (dropdown/select)
  - [ ] **Additional Items** (text area)

### 4.7 Personality and Background
- [ ] Verify personality fields:
  - [ ] **Personality Traits** (text area or dropdown)
  - [ ] **Ideals** (text area or dropdown)
  - [ ] **Bonds** (text area or dropdown)
  - [ ] **Flaws** (text area or dropdown)

### 4.8 Form Submission
- [ ] Fill out all required fields with valid data
- [ ] Click "Create Character" button
- [ ] Verify form submission without errors
- [ ] Confirm character is saved successfully
- [ ] Verify redirection to `/game` interface
- [ ] Confirm character data is loaded in game interface

**Expected Result**: Complete character creation and successful transition to game

---

## 5. Test: Vibe Code Creation

**Objective**: Validate the AI-powered conversation-based character creation

### 5.1 Navigation to Vibe Code Creation
- [ ] Click on "✨ Vibe Code Creation" button
- [ ] Confirm redirection to `/vibe-code-creation`
- [ ] Verify page title changes to "Vibe Code Character Creation"
- [ ] Check that chat interface loads without errors

### 5.2 Chat Interface Validation
- [ ] Verify presence of chat container
- [ ] Confirm input field for user messages
- [ ] Verify "Send" button is present and functional
- [ ] Check that welcome message is displayed
- [ ] Verify chat history area is present

### 5.3 Initial Character Prompt
- [ ] Enter a vibe prompt (e.g., "a grumpy half-orc monk with a tragic past")
- [ ] Click "Send" or press Enter
- [ ] Verify AI response is received
- [ ] Confirm response includes character summary
- [ ] Check that response is properly formatted

### 5.4 Conversation Flow
- [ ] Continue conversation with follow-up questions
- [ ] Test various character concepts:
  - [ ] "A wise old dwarf cleric seeking redemption"
  - [ ] "A young elf wizard with a thirst for knowledge"
  - [ ] "A charismatic human bard with a mysterious past"
- [ ] Verify AI maintains conversation context
- [ ] Confirm AI asks clarifying questions when needed

### 5.5 Character Refinement
- [ ] Test character refinement through conversation:
  - [ ] Modify character background details
  - [ ] Adjust personality traits
  - [ ] Change equipment preferences
  - [ ] Modify ability score focus
- [ ] Verify AI incorporates changes into character summary

### 5.6 Final Character Review
- [ ] Complete character creation conversation
- [ ] Verify final character summary is displayed
- [ ] Confirm all required SRD 5.1 fields are present:
  - [ ] Name, Race, Class, Level
  - [ ] Ability scores and modifiers
  - [ ] Combat stats (HP, AC, Speed, Initiative)
  - [ ] Skills and proficiencies
  - [ ] Equipment and items
  - [ ] Personality traits
- [ ] Verify "Confirm Character" button is present
- [ ] Click "Confirm Character" to proceed

### 5.7 Character Confirmation
- [ ] Verify character is saved successfully
- [ ] Confirm redirection to `/game` interface
- [ ] Verify character data is loaded correctly in game
- [ ] Check that character matches conversation summary

**Expected Result**: Complete AI-driven character creation and successful game transition

---

## 6. Test: Save and Load Campaigns

**Objective**: Validate campaign persistence and loading functionality

### 6.1 Campaign Saving
- [ ] After creating a character, return to `http://localhost:5001`
- [ ] Verify the saved campaign appears in the campaign list
- [ ] Confirm campaign displays:
  - [ ] Campaign name/ID
  - [ ] Character name
  - [ ] Character class and level
  - [ ] Creation date
  - [ ] "Load" button

### 6.2 Campaign Loading
- [ ] Click on a saved campaign's "Load" button
- [ ] Verify redirection to `/game` interface
- [ ] Confirm character data is loaded correctly:
  - [ ] All ability scores match saved values
  - [ ] Equipment and items are present
  - [ ] Personality traits are preserved
  - [ ] Combat stats are accurate

### 6.3 Campaign Management
- [ ] Test campaign deletion (if available):
  - [ ] Click "Delete" button on a campaign
  - [ ] Confirm deletion dialog appears
  - [ ] Verify campaign is removed from list
- [ ] Test multiple campaign creation:
  - [ ] Create 2-3 different characters
  - [ ] Verify all appear in campaign list
  - [ ] Confirm each loads correctly

**Expected Result**: Reliable campaign saving and loading with data integrity

---

## 7. Test: Error Handling and Edge Cases

**Objective**: Validate system behavior under error conditions

### 7.1 Network Issues
- [ ] Test with slow network connection
- [ ] Verify timeout handling for API calls
- [ ] Check error messages for network failures
- [ ] Test recovery after network restoration

### 7.2 Invalid Input Handling
- [ ] Test form validation:
  - [ ] Submit empty required fields
  - [ ] Enter invalid ability scores (0, 25, -1)
  - [ ] Test special characters in name field
  - [ ] Verify appropriate error messages
- [ ] Test vibe code edge cases:
  - [ ] Very short prompts ("test")
  - [ ] Very long prompts (1000+ characters)
  - [ ] Non-English input
  - [ ] Special characters and emojis

### 7.3 Browser Compatibility
- [ ] Test in different browsers:
  - [ ] Chrome
  - [ ] Firefox
  - [ ] Safari
  - [ ] Edge
- [ ] Test responsive design on mobile devices
- [ ] Verify local storage functionality

### 7.4 Server Issues
- [ ] Test behavior when server is down
- [ ] Verify graceful error handling
- [ ] Check recovery after server restart
- [ ] Test session timeout handling

**Expected Result**: Graceful error handling with informative user feedback

---

## 8. Performance Testing

**Objective**: Validate system performance under normal usage

### 8.1 Response Times
- [ ] Measure page load times:
  - [ ] Start screen: < 2 seconds
  - [ ] Character creation form: < 3 seconds
  - [ ] Vibe code interface: < 2 seconds
- [ ] Test API response times:
  - [ ] Character creation: < 5 seconds
  - [ ] Vibe code responses: < 10 seconds
  - [ ] Campaign loading: < 3 seconds

### 8.2 Memory Usage
- [ ] Monitor browser memory usage during extended sessions
- [ ] Test with multiple browser tabs open
- [ ] Verify no memory leaks during character creation

### 8.3 Concurrent Users
- [ ] Test with multiple browser sessions
- [ ] Verify no interference between sessions
- [ ] Test campaign isolation between users

**Expected Result**: Responsive performance under normal load

---

## 9. Known Issues / Notes

### 9.1 Current Issues
- [ ] **Character Schema Loading**: Error loading character schema (JSON parsing issue)
- [ ] **SRD Data Loading**: Error loading SRD data (JSON parsing issue)
- [ ] **LLM Model**: Warning about 'llama3' model not found, using 'llama3:latest' instead

### 9.2 UI/UX Issues
- [ ] Broken links (if any)
- [ ] UI glitches or layout problems
- [ ] Missing fields or validation
- [ ] Responsive design issues

### 9.3 API Issues
- [ ] API failures or timeouts
- [ ] Incorrect response formats
- [ ] Missing error handling
- [ ] Authentication issues (if applicable)

### 9.4 AI Model Issues
- [ ] Model errors or unexpected responses
- [ ] Inconsistent character generation
- [ ] Context loss in conversations
- [ ] Inappropriate or unsafe content

### 9.5 Data Persistence Issues
- [ ] Campaign save failures
- [ ] Data corruption or loss
- [ ] Inconsistent state between sessions
- [ ] Local storage limitations

---

## 10. Test Results Summary

### 10.1 Test Execution
- **Date**: [Fill in test date]
- **Tester**: [Fill in tester name]
- **Environment**: [Fill in test environment details]

### 10.2 Pass/Fail Summary
- [ ] Start Screen Load: ✅ PASS / ❌ FAIL
- [ ] Step-by-Step Creation: ✅ PASS / ❌ FAIL
- [ ] Vibe Code Creation: ✅ PASS / ❌ FAIL
- [ ] Save and Load Campaigns: ✅ PASS / ❌ FAIL
- [ ] Error Handling: ✅ PASS / ❌ FAIL
- [ ] Performance: ✅ PASS / ❌ FAIL

### 10.3 Critical Issues Found
1. [List any critical issues that prevent normal operation]
2. [Include severity level and impact]
3. [Note any workarounds or temporary fixes]

### 10.4 Recommendations
1. [List any improvements or enhancements]
2. [Note any missing features]
3. [Suggest usability improvements]

---

## 11. Sign-off

- **Test Completed By**: _________________
- **Date**: _________________
- **Approved By**: _________________
- **Next Review Date**: _________________

---

**Note**: This test plan should be updated whenever new features are added or existing functionality is modified. Regular testing ensures the character creation flow remains reliable and user-friendly. 