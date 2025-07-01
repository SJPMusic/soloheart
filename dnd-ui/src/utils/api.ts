import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';
const MOCK_MODE = process.env.REACT_APP_MOCK_MODE === 'true';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Logging utility
const logApiCall = (method: string, endpoint: string, data?: any) => {
  console.log(`🌐 API ${method} ${endpoint}`, data ? { data } : '');
};

const logApiResponse = (method: string, endpoint: string, response: any) => {
  console.log(`✅ API ${method} ${endpoint} Response:`, response);
};

const logApiError = (method: string, endpoint: string, error: any) => {
  console.error(`❌ API ${method} ${endpoint} Error:`, error);
};

export interface Message {
  id: string;
  type: 'player' | 'ai';
  content: string;
  timestamp: Date;
}

export interface Session {
  id: string;
  character?: {
    name: string;
    class: string;
    level: number;
    stats: {
      STR: number;
      DEX: number;
      CON: number;
      INT: number;
      WIS: number;
      CHA: number;
    };
    hp: {
      current: number;
      max: number;
    };
    inventory: string[];
  };
  messages: Message[];
  startedAt: Date;
}

export interface ApiResponse {
  success: boolean;
  message?: string;
  data?: any;
  error?: string;
}

// Mock data for development
const mockCharacter = {
  name: "Thorin Ironfist",
  class: "Fighter",
  level: 3,
  stats: {
    STR: 16,
    DEX: 14,
    CON: 15,
    INT: 12,
    WIS: 10,
    CHA: 8
  },
  hp: {
    current: 28,
    max: 30
  },
  inventory: ["Longsword", "Shield", "Torch", "Explorer's Pack", "Healing Potion"]
};

const mockResponses = [
  "You step into a damp cave. The smell of wet stone fills the air, and your torch casts dancing shadows on the rough walls. The sound of dripping water echoes from deeper within.",
  "The forest path winds through ancient trees, their branches creating a natural canopy overhead. You hear the rustling of small creatures in the underbrush.",
  "You carefully examine the mysterious runes carved into the stone wall. They seem to glow faintly in the dim light, written in an ancient script you don't recognize.",
  "The tavern is bustling with activity. The smell of roasted meat and ale fills the air as patrons laugh and share stories around wooden tables.",
  "You draw your weapon as the goblin snarls and lunges forward. The creature's yellow eyes gleam with malice as it brandishes a rusty dagger."
];

// Mock API functions
const mockStartNewGame = (): Promise<ApiResponse> => {
  logApiCall('POST', '/api/start (MOCK)');
  
  const mockSession = {
    session_id: `mock-session-${Date.now()}`,
    character: mockCharacter
  };
  
  const response: ApiResponse = {
    success: true,
    message: 'New game started successfully',
    data: mockSession
  };
  
  logApiResponse('POST', '/api/start (MOCK)', response);
  return Promise.resolve(response);
};

const mockSendPlayerInput = (input: string): Promise<ApiResponse> => {
  logApiCall('POST', '/api/input (MOCK)', { input });
  
  // Select a random response or use input-based logic
  const randomResponse = mockResponses[Math.floor(Math.random() * mockResponses.length)];
  
  const response: ApiResponse = {
    success: true,
    message: 'Input processed successfully',
    data: {
      response: randomResponse,
      character: mockCharacter
    }
  };
  
  logApiResponse('POST', '/api/input (MOCK)', response);
  return Promise.resolve(response);
};

const mockGetSession = (): Promise<ApiResponse> => {
  logApiCall('GET', '/api/session (MOCK)');
  
  const response: ApiResponse = {
    success: true,
    message: 'Session retrieved successfully',
    data: {
      session_id: `mock-session-${Date.now()}`,
      character: mockCharacter,
      messages: []
    }
  };
  
  logApiResponse('GET', '/api/session (MOCK)', response);
  return Promise.resolve(response);
};

const mockSaveGame = (): Promise<ApiResponse> => {
  logApiCall('POST', '/api/save (MOCK)');
  
  const response: ApiResponse = {
    success: true,
    message: 'Game saved successfully'
  };
  
  logApiResponse('POST', '/api/save (MOCK)', response);
  return Promise.resolve(response);
};

const mockLoadGame = (): Promise<ApiResponse> => {
  logApiCall('GET', '/api/load (MOCK)');
  
  const response: ApiResponse = {
    success: true,
    message: 'Game loaded successfully',
    data: {
      session_id: `mock-session-${Date.now()}`,
      character: mockCharacter,
      messages: []
    }
  };
  
  logApiResponse('GET', '/api/load (MOCK)', response);
  return Promise.resolve(response);
};

// Real API functions
export const startNewGame = async (): Promise<ApiResponse> => {
  if (MOCK_MODE) {
    return mockStartNewGame();
  }
  
  logApiCall('POST', '/api/start');
  
  try {
    const response = await api.post('/api/start');
    logApiResponse('POST', '/api/start', response.data);
    return response.data;
  } catch (error) {
    logApiError('POST', '/api/start', error);
    return {
      success: false,
      error: 'Failed to start new game. Please check your connection and try again.'
    };
  }
};

export const sendPlayerInput = async (input: string): Promise<ApiResponse> => {
  if (MOCK_MODE) {
    return mockSendPlayerInput(input);
  }
  
  logApiCall('POST', '/api/input', { input });
  
  try {
    const response = await api.post('/api/input', { input });
    logApiResponse('POST', '/api/input', response.data);
    return response.data;
  } catch (error) {
    logApiError('POST', '/api/input', error);
    return {
      success: false,
      error: 'Failed to send input. Please check your connection and try again.'
    };
  }
};

export const getSession = async (): Promise<ApiResponse> => {
  if (MOCK_MODE) {
    return mockGetSession();
  }
  
  logApiCall('GET', '/api/session');
  
  try {
    const response = await api.get('/api/session');
    logApiResponse('GET', '/api/session', response.data);
    return response.data;
  } catch (error) {
    logApiError('GET', '/api/session', error);
    return {
      success: false,
      error: 'Failed to fetch session. Please check your connection and try again.'
    };
  }
};

export const saveGame = async (): Promise<ApiResponse> => {
  if (MOCK_MODE) {
    return mockSaveGame();
  }
  
  logApiCall('POST', '/api/save');
  
  try {
    const response = await api.post('/api/save');
    logApiResponse('POST', '/api/save', response.data);
    return response.data;
  } catch (error) {
    logApiError('POST', '/api/save', error);
    return {
      success: false,
      error: 'Failed to save game. Please check your connection and try again.'
    };
  }
};

export const loadGame = async (): Promise<ApiResponse> => {
  if (MOCK_MODE) {
    return mockLoadGame();
  }
  
  logApiCall('GET', '/api/load');
  
  try {
    const response = await api.get('/api/load');
    logApiResponse('GET', '/api/load', response.data);
    return response.data;
  } catch (error) {
    logApiError('GET', '/api/load', error);
    return {
      success: false,
      error: 'Failed to load game. Please check your connection and try again.'
    };
  }
};

// Local storage utilities with enhanced error handling
export const saveToLocalStorage = (session: Session): boolean => {
  try {
    const sessionData = JSON.stringify(session);
    localStorage.setItem('dnd-session', sessionData);
    console.log('💾 Session saved to localStorage:', session);
    return true;
  } catch (error) {
    console.error('❌ Error saving to localStorage:', error);
    return false;
  }
};

export const loadFromLocalStorage = (): Session | null => {
  try {
    const saved = localStorage.getItem('dnd-session');
    if (!saved) {
      console.log('📂 No saved session found in localStorage');
      return null;
    }
    
    const session = JSON.parse(saved);
    console.log('📂 Session loaded from localStorage:', session);
    return session;
  } catch (error) {
    console.error('❌ Error loading from localStorage:', error);
    return null;
  }
};

export const clearLocalStorage = (): boolean => {
  try {
    localStorage.removeItem('dnd-session');
    console.log('🗑️ Session cleared from localStorage');
    return true;
  } catch (error) {
    console.error('❌ Error clearing localStorage:', error);
    return false;
  }
};

// Utility to check if we're in mock mode
export const isMockMode = (): boolean => {
  return MOCK_MODE;
};

export default api;
