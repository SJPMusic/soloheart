This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License.

# Manual UI Test Checklist

## Overview
This checklist provides step-by-step instructions for manually testing the Narrative Engine Web UI, including the Lore Panel, Diagnostics Panel, and all export functionality.

## Prerequisites
- Web server running on `http://localhost:5001`
- Test campaign data seeded (run `python seed_data/seed_test_campaign.py`)
- Modern web browser (Chrome, Firefox, Safari, Edge)

---

## 🎯 Core Functionality Tests

### 1. Basic UI Loading
- [ ] **Page loads without errors**
  - Navigate to `http://localhost:5001`
  - Check browser console for JavaScript errors
  - Verify all UI elements render correctly
  - Confirm dark theme is applied

- [ ] **Header elements display correctly**
  - App title shows "DnD 5E Solo Adventure"
  - Character selector dropdown is present
  - Save/Load/Debug buttons are visible
  - All icons display properly

- [ ] **Sidebar functionality**
  - Sidebar is visible by default
  - Toggle button works (collapses/expands sidebar)
  - Character info section displays
  - Character arcs section is present
  - Plot threads section is present
  - Journal entries section is present

### 2. Character Management
- [ ] **Character creation**
  - Click "Add Character" button
  - Modal opens with form
  - Fill in character name and class
  - Submit form successfully
  - New character appears in dropdown

- [ ] **Character selection**
  - Select different characters from dropdown
  - Sidebar updates with character info
  - Active character is highlighted
  - Character-specific data loads

---

## 📚 Lore Panel Tests

### 3. Lore Panel Loading
- [ ] **Lore panel opens correctly**
  - Click "📚 Lore & Worldbuilding" toggle
  - Panel slides in from right
  - Search bar is visible
  - Filters are present
  - Lore summary stats display

- [ ] **Lore summary statistics**
  - Total entries count is accurate
  - Recent entries count shows correctly
  - Secrets count displays properly
  - All stat values are reasonable

### 4. Lore Search and Filtering
- [ ] **Search functionality**
  - Type in search box
  - Results filter in real-time
  - Search works for titles and content
  - Clear search shows all entries

- [ ] **Type filtering**
  - Select different lore types from dropdown
  - Results filter correctly
  - "All Types" shows everything
  - Each type shows appropriate entries

- [ ] **Importance filtering**
  - Select different importance levels
  - Results filter by importance
  - "All Importance" shows everything
  - High importance entries are highlighted

- [ ] **Secrets toggle**
  - Check/uncheck "Show Secrets"
  - Secret entries appear/disappear
  - Secret entries are visually distinct

### 5. Lore Entry Display
- [ ] **Lore entry cards**
  - All entries display as cards
  - Titles are clearly visible
  - Content previews show correctly
  - Tags display properly
  - Importance stars show correctly
  - Discovery status is indicated

- [ ] **Lore entry details**
  - Click on lore entry card
  - Modal opens with full details
  - All metadata displays correctly
  - Linked items show properly
  - Close button works

### 6. Lore Entry Creation
- [ ] **Add lore entry**
  - Click "Add Lore Entry" button
  - Modal opens with form
  - Fill in all required fields
  - Add tags using tag input
  - Submit form successfully
  - New entry appears in list

- [ ] **Form validation**
  - Try submitting empty form
  - Validation errors display
  - Required fields are marked
  - Invalid data shows errors

---

## 📈 Diagnostics Panel Tests

### 7. Diagnostics Panel Loading
- [ ] **Diagnostics panel opens**
  - Click "📈 Diagnostics" toggle
  - Panel slides in from right
  - All sections are visible
  - Loading states work correctly

- [ ] **Panel sections display**
  - Conflict Timeline section
  - Character Arcs section
  - Emotion Heatmap section
  - Summary Report section

### 8. Conflict Timeline
- [ ] **Timeline displays correctly**
  - Conflicts show in chronological order
  - Each conflict has proper metadata
  - Status indicators work (resolved/unresolved)
  - Type indicators work (internal/interpersonal/external)
  - Urgency levels are color-coded

- [ ] **Timeline filtering**
  - Type filter works (internal/interpersonal/external)
  - Status filter works (resolved/unresolved)
  - Filters can be combined
  - Clear filters shows all conflicts

### 9. Character Arcs
- [ ] **Arc map displays**
  - Character arcs show correctly
  - Progress bars display properly
  - Status indicators work
  - Milestones show correctly

- [ ] **Arc controls**
  - "Show All Arcs" checkbox works
  - Resolved arcs can be hidden/shown
  - Arc details expand/collapse

### 10. Emotion Heatmap
- [ ] **Chart renders correctly**
  - Chart.js canvas displays
  - Multiple emotion lines show
  - Colors are distinct for each emotion
  - Axes and labels are readable
  - Legend displays properly

- [ ] **Character filtering**
  - Character selector dropdown works
  - Switching characters updates chart
  - "All Characters" shows aggregated data
  - Individual character data displays

- [ ] **Chart interactivity**
  - Hover tooltips show emotion values
  - Tooltips display timestamps
  - Chart is responsive to window resize
  - Zoom/pan works (if implemented)

### 11. Heatmap Export
- [ ] **PNG export**
  - Click "Export as PNG" button
  - Chart downloads as PNG file
  - File opens correctly
  - Image quality is good
  - Success notification appears

- [ ] **CSV export**
  - Click "Export as CSV" button
  - CSV file downloads
  - File opens in spreadsheet software
  - Data is properly formatted
  - Success notification appears

### 12. Diagnostic Report
- [ ] **Report displays correctly**
  - Campaign statistics show
  - Dominant emotions display
  - Arc progress summary shows
  - All metrics are reasonable

- [ ] **Report export options**
  - All export buttons are present
  - Buttons have proper icons
  - Tooltips display on hover

### 13. Report Export Functions
- [ ] **JSON export**
  - Click "Download as JSON" button
  - JSON file downloads
  - File contains valid JSON
  - All report data is included
  - Success notification appears

- [ ] **Markdown export**
  - Click "Download as Markdown" button
  - Markdown file downloads
  - File opens in text editor
  - Formatting is correct
  - Success notification appears

- [ ] **PDF export**
  - Click "Export as PDF" button
  - PDF generation starts
  - PDF file downloads
  - File opens in PDF viewer
  - Layout is properly formatted
  - Success notification appears

- [ ] **Copy Markdown**
  - Click "Copy Markdown" button
  - Button shows "Copied!" feedback
  - Markdown is copied to clipboard
  - Paste works in text editor
  - Success notification appears

---

## 🎮 Gameplay Integration Tests

### 14. Player Actions
- [ ] **Action input**
  - Type action in text area
  - Character count updates
  - Send button enables/disables
  - Enter key sends message
  - Shift+Enter creates new line

- [ ] **Action processing**
  - Submit natural language action
  - Typing indicator appears
  - DM narration generates
  - Response appears in chat
  - Sidebar updates with new data

### 15. Narrative Dynamics
- [ ] **Dynamics panel**
  - Click "Narrative Dynamics" toggle
  - Panel opens with real-time data
  - Campaign momentum displays
  - Active events show
  - Emotional themes update

- [ ] **Real-time updates**
  - Submit actions
  - Dynamics panel updates
  - Momentum changes
  - Events appear/disappear
  - Themes evolve

### 16. Chat History
- [ ] **Chat functionality**
  - Messages display in chronological order
  - Character attribution works
  - Timestamps show correctly
  - Message formatting is proper
  - Scroll to bottom works

---

## 🔧 Debug and Utility Tests

### 17. Debug Mode
- [ ] **Debug toggle**
  - Click debug button
  - Debug mode activates
  - Additional info appears
  - Debug modal opens
  - Technical details display

### 18. Save/Load System
- [ ] **Save campaign**
  - Click save button
  - Modal opens
  - Enter save name
  - Campaign saves successfully
  - Success notification appears

- [ ] **Load campaign**
  - Click load button
  - Modal shows saved campaigns
  - Select campaign to load
  - Campaign loads successfully
  - All data restores correctly

### 19. Responsive Design
- [ ] **Mobile responsiveness**
  - Resize browser window
  - UI adapts to smaller screens
  - Panels stack properly
  - Touch interactions work
  - Text remains readable

- [ ] **Tablet responsiveness**
  - Test on tablet-sized viewport
  - Sidebar behavior is appropriate
  - Charts scale correctly
  - Buttons are touch-friendly

---

## 🚨 Error Handling Tests

### 20. Network Errors
- [ ] **API failures**
  - Disconnect network
  - Submit action
  - Error message displays
  - UI remains functional
  - Retry mechanism works

### 21. Data Validation
- [ ] **Invalid input**
  - Submit empty actions
  - Enter invalid data in forms
  - Error messages display
  - Form validation works
  - UI doesn't crash

---

## 📊 Performance Tests

### 22. Loading Performance
- [ ] **Initial load**
  - Page loads within 3 seconds
  - No long loading spinners
  - Data loads progressively
  - UI is responsive during load

- [ ] **Data handling**
  - Large datasets load properly
  - Charts render quickly
  - Export functions complete promptly
  - No memory leaks

---

## ✅ Final Verification

### 23. Cross-browser Testing
- [ ] **Chrome compatibility**
  - All features work in Chrome
  - No console errors
  - Performance is good

- [ ] **Firefox compatibility**
  - All features work in Firefox
  - No console errors
  - Performance is good

- [ ] **Safari compatibility**
  - All features work in Safari
  - No console errors
  - Performance is good

### 24. Accessibility
- [ ] **Keyboard navigation**
  - Tab through all elements
  - Enter/Space activate buttons
  - Escape closes modals
  - Focus indicators are visible

- [ ] **Screen reader compatibility**
  - Alt text on images
  - Proper heading structure
  - ARIA labels where needed
  - Semantic HTML

---

## 📝 Test Results

**Test Date:** _______________
**Tester:** _______________
**Browser:** _______________
**Campaign ID:** _______________

**Overall Status:**
- [ ] ✅ All tests passed
- [ ] ⚠️ Minor issues found
- [ ] ❌ Major issues found

**Issues Found:**
1. ________________________________
2. ________________________________
3. ________________________________

**Notes:**
________________________________
________________________________
________________________________

---

## 🎯 Success Criteria

The UI test is considered successful when:
- All core functionality works as expected
- No JavaScript errors in console
- All export functions work properly
- UI is responsive and accessible
- Performance is acceptable
- Error handling is robust

**Test Status:** ✅ PASS / ❌ FAIL 