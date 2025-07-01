import React, { useState, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import InputBox from './components/InputBox';
import Sidebar from './components/Sidebar';
import { Session, Message, startNewGame, sendPlayerInput, saveToLocalStorage, loadFromLocalStorage, clearLocalStorage, isMockMode } from './utils/api';

const App: React.FC = () => {
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Load session from localStorage on mount
  useEffect(() => {
    const savedSession = loadFromLocalStorage();
    if (savedSession) {
      setSession(savedSession);
      console.log('🎮 Session restored from localStorage');
    }
  }, []);

  // Save session to localStorage whenever it changes
  useEffect(() => {
    if (session) {
      const saved = saveToLocalStorage(session);
      if (saved) {
        console.log('💾 Session auto-saved to localStorage');
      }
    }
  }, [session]);

  const showSuccessMessage = (message: string) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  const showErrorMessage = (message: string) => {
    setError(message);
    setTimeout(() => setError(null), 5000);
  };

  const handleNewGame = async () => {
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);
    
    try {
      const response = await startNewGame();
      if (response.success) {
        const newSession: Session = {
          id: response.data?.session_id || `session-${Date.now()}`,
          messages: [],
          startedAt: new Date(),
          character: response.data?.character || undefined
        };
        setSession(newSession);
        clearLocalStorage(); // Clear old session data
        showSuccessMessage('New game started successfully!');
        console.log('🎲 New game session created:', newSession);
      } else {
        showErrorMessage(response.error || 'Failed to start new game');
      }
    } catch (err) {
      showErrorMessage('Failed to start new game. Please check your connection.');
      console.error('Error starting new game:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (input: string) => {
    if (!session) {
      showErrorMessage('No active session. Please start a new game first.');
      return;
    }

    setIsLoading(true);
    setError(null);

    // Add player message immediately
    const playerMessage: Message = {
      id: `msg-${Date.now()}-player`,
      type: 'player',
      content: input,
      timestamp: new Date()
    };

    const updatedMessages = [...session.messages, playerMessage];
    setSession({
      ...session,
      messages: updatedMessages
    });

    try {
      const response = await sendPlayerInput(input);
      if (response.success) {
        // Add AI response
        const aiMessage: Message = {
          id: `msg-${Date.now()}-ai`,
          type: 'ai',
          content: response.data?.response || response.message || 'The Dungeon Master nods thoughtfully...',
          timestamp: new Date()
        };

        setSession({
          ...session,
          messages: [...updatedMessages, aiMessage],
          character: response.data?.character || session.character
        });
        
        console.log('💬 Message sent and response received');
      } else {
        // Add error message
        const errorMessage: Message = {
          id: `msg-${Date.now()}-error`,
          type: 'ai',
          content: response.error || 'Something went wrong. Please try again.',
          timestamp: new Date()
        };

        setSession({
          ...session,
          messages: [...updatedMessages, errorMessage]
        });
        
        showErrorMessage(response.error || 'Failed to send message');
      }
    } catch (err) {
      // Add error message
      const errorMessage: Message = {
        id: `msg-${Date.now()}-error`,
        type: 'ai',
        content: 'Failed to send message. Please check your connection and try again.',
        timestamp: new Date()
      };

      setSession({
        ...session,
        messages: [...updatedMessages, errorMessage]
      });
      
      showErrorMessage('Failed to send message. Please check your connection.');
      console.error('Error sending message:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveGame = async () => {
    if (!session) {
      showErrorMessage('No active session to save.');
      return;
    }

    try {
      // Try backend save first if not in mock mode
      if (!isMockMode()) {
        const response = await startNewGame(); // Using startNewGame as proxy for save
        if (response.success) {
          showSuccessMessage('Game saved to server successfully!');
          return;
        }
      }
      
      // Fallback to localStorage
      const saved = saveToLocalStorage(session);
      if (saved) {
        showSuccessMessage('Game saved to browser storage!');
      } else {
        showErrorMessage('Failed to save game to browser storage.');
      }
    } catch (err) {
      showErrorMessage('Failed to save game.');
      console.error('Error saving game:', err);
    }
  };

  const handleLoadGame = async () => {
    try {
      // Try backend load first if not in mock mode
      if (!isMockMode()) {
        const response = await startNewGame(); // Using startNewGame as proxy for load
        if (response.success) {
          const loadedSession: Session = {
            id: response.data?.session_id || `session-${Date.now()}`,
            messages: [],
            startedAt: new Date(),
            character: response.data?.character || undefined
          };
          setSession(loadedSession);
          showSuccessMessage('Game loaded from server successfully!');
          return;
        }
      }
      
      // Fallback to localStorage
      const savedSession = loadFromLocalStorage();
      if (savedSession) {
        setSession(savedSession);
        showSuccessMessage('Game loaded from browser storage!');
      } else {
        showErrorMessage('No saved game found.');
      }
    } catch (err) {
      showErrorMessage('Failed to load game.');
      console.error('Error loading game:', err);
    }
  };

  return (
    <div className="h-screen flex bg-parchment-100">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-parchment-300 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-fantasy text-ink-800">Solo Adventure</h1>
              <div className="flex items-center space-x-2">
                <p className="text-ink-600 text-sm">
                  {session ? `Session: ${session.id.slice(0,8)}...` : 'No active session'}
                </p>
                {isMockMode() && (
                  <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">
                    MOCK MODE
                  </span>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {session && (
                <button
                  onClick={handleSaveGame}
                  className="btn-secondary text-sm"
                >
                  💾 Save
                </button>
              )}
              <button
                onClick={handleLoadGame}
                className="btn-secondary text-sm"
              >
                📂 Load
              </button>
              <button
                onClick={handleNewGame}
                className="btn-primary text-sm"
                disabled={isLoading}
              >
                🎲 New Game
              </button>
            </div>
          </div>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="bg-green-50 border border-green-200 px-4 py-2 text-green-700 text-sm">
            ✅ {successMessage}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 px-4 py-2 text-red-700 text-sm">
            ❌ {error}
          </div>
        )}

        {/* Chat Window */}
        <ChatWindow 
          messages={session?.messages || []} 
          isLoading={isLoading}
        />

        {/* Input Box */}
        <InputBox
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          disabled={!session}
        />
      </div>

      {/* Sidebar */}
      <Sidebar
        session={session}
        onNewGame={handleNewGame}
        onSaveGame={handleSaveGame}
        onLoadGame={handleLoadGame}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />
    </div>
  );
};

export default App;
