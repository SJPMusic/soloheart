# SoloHeart UI

A modern React web interface for the SoloHeart game engine. This UI provides an immersive, chat-based interface for interacting with the AI SoloHeart Guide.

## Features

- **Chat Interface**: Clean, narrative-focused chat window with Markdown support
- **Responsive Design**: Mobile-friendly layout with collapsible sidebar
- **Session Management**: Start new games, save/load sessions
- **Character Tracking**: Display character stats, HP, and inventory
- **Real-time Updates**: Instant message display with loading indicators
- **Fantasy Theme**: Immersive parchment-style design with fantasy typography
- **Mock Mode**: Full offline development with simulated AI responses
- **Enhanced Logging**: Comprehensive console logging for debugging

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend server running on localhost:5001 (optional with mock mode)

## Installation & Setup

### 1. Install Dependencies

```bash
cd soloheart-ui
npm install
```

**Required packages:**
- react, react-dom, react-markdown
- axios, tailwindcss, typescript
- postcss, autoprefixer

### 2. Environment Configuration

The app includes a `.env.development` file with mock mode enabled by default:

```bash
REACT_APP_MOCK_MODE=true
REACT_APP_API_URL=http://localhost:5001
REACT_APP_DEBUG=true
```

### 3. Start Development Server

```bash
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000).

## Testing & Debugging

### Mock Mode (Recommended for Development)

With `REACT_APP_MOCK_MODE=true`, the app runs completely offline:

- ✅ **No backend required** - All API calls return mock data
- ✅ **Instant responses** - No network delays
- ✅ **Consistent data** - Predictable character and narrative responses
- ✅ **Full functionality** - All features work without backend

**Mock Mode Features:**
- Random narrative responses from predefined scenarios
- Sample character "Thorin Ironfist" (Level 3 Fighter)
- Full localStorage persistence
- Complete session management

### Backend Integration Testing

To test with your actual backend:

1. **Disable Mock Mode:**
   ```bash
   echo "REACT_APP_MOCK_MODE=false" > .env.development
   ```

2. **Start Your Backend Server:**
   ```bash
   # In your backend directory
   python your_backend_server.py
   ```

3. **Verify Backend Endpoints:**
   - `POST /api/start` - Start new session
   - `POST /api/input` - Send player input
   - `GET /api/session` - Get session state (optional)
   - `POST /api/save` - Save session (optional)
   - `GET /api/load` - Load session (optional)

### Console Logging

The app provides comprehensive logging:

- 🌐 **API Calls**: All requests logged with data
- ✅ **API Responses**: Successful responses logged
- ❌ **API Errors**: Error details logged
- 💾 **localStorage**: Save/load operations logged
- 🎮 **Session Events**: Game state changes logged

**Example Console Output:**
```
🌐 API POST /api/start (MOCK) { data: { input: "I walk into the forest" } }
✅ API POST /api/start (MOCK) Response: { success: true, data: {...} }
💾 Session saved to localStorage: { id: "mock-session-123", ... }
```

### Testing Checklist

#### ✅ Frontend Rendering
- [ ] App loads without console errors
- [ ] Tailwind styles are visible (parchment theme)
- [ ] ChatWindow, InputBox, and Sidebar render correctly
- [ ] Responsive design works on different screen sizes

#### ✅ Mock Mode Testing
- [ ] "MOCK MODE" badge appears in header
- [ ] "New Game" button creates session instantly
- [ ] Typing commands returns mock narrative responses
- [ ] Character stats display correctly
- [ ] Save/Load buttons work with localStorage

#### ✅ Backend Integration Testing
- [ ] Disable mock mode (`REACT_APP_MOCK_MODE=false`)
- [ ] Backend server running on localhost:5001
- [ ] "New Game" sends POST to `/api/start`
- [ ] Commands send POST to `/api/input`
- [ ] AI responses display in chat
- [ ] Character data updates from backend

#### ✅ Error Handling
- [ ] Network errors show user-friendly messages
- [ ] localStorage errors are logged
- [ ] Invalid API responses handled gracefully
- [ ] Loading states work correctly

## API Endpoints

The UI communicates with the backend via these endpoints:

### Required Endpoints
- `POST /api/start` - Start a new game session
  - **Request**: `{}`
  - **Response**: `{ success: true, data: { session_id: string, character?: object } }`

- `POST /api/input` - Send player input
  - **Request**: `{ input: string }`
  - **Response**: `{ success: true, data: { response: string, character?: object } }`

### Optional Endpoints
- `GET /api/session` - Get current session state
- `POST /api/save` - Save game state
- `GET /api/load` - Load game state

### Error Response Format
```json
{
  "success": false,
  "error": "Error message for user"
}
```

## Usage Guide

### Starting a Game
1. Click "New Game" button
2. Wait for session initialization (instant in mock mode)
3. Begin typing your actions

### Sending Commands
Type natural language commands like:
- "I search the room"
- "I attack the goblin with my sword"
- "I cast magic missile at the nearest enemy"
- "I examine the mysterious runes"

### Managing Your Character
- Use the sidebar to view:
  - Character stats and HP
  - Inventory items
  - Session information

### Saving Progress
- Click "Save" to store session in browser
- Click "Load" to restore previous session
- Sessions persist between browser sessions

## Project Structure

```
src/
├── components/
│   ├── ChatWindow.tsx    # Main chat display
│   ├── InputBox.tsx      # User input component
│   └── Sidebar.tsx       # Character info and controls
├── utils/
│   └── api.ts           # API communication utilities
├── App.tsx              # Main application component
├── index.tsx            # Application entry point
└── index.css            # Global styles and Tailwind imports
```

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Environment Variables

- `REACT_APP_MOCK_MODE` - Enable/disable mock mode
- `REACT_APP_API_URL` - Backend API URL
- `REACT_APP_DEBUG` - Enable debug logging

### Customization

- Modify `tailwind.config.js` to adjust the theme
- Update `src/index.css` for custom component styles
- Edit API endpoints in `src/utils/api.ts`
- Add mock responses in `src/utils/api.ts`

## Troubleshooting

### Common Issues

1. **Backend not running**: Enable mock mode or start backend server
2. **CORS errors**: Check backend CORS configuration
3. **API errors**: Verify endpoint URLs and response formats
4. **Styling issues**: Check Tailwind CSS compilation
5. **localStorage errors**: Check browser permissions

### Development Tips

- Use browser dev tools to inspect API calls
- Check console for detailed error messages
- Test with different screen sizes
- Verify localStorage functionality
- Use mock mode for rapid development

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## License

This project is part of the SoloHeart system and follows the same licensing terms.

---

This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License. 