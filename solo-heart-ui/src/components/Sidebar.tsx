import React, { useState } from 'react';
import { Session } from '../utils/api';

interface SidebarProps {
  session: Session | null;
  onNewGame: () => void;
  onSaveGame?: () => void;
  onLoadGame?: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  session,
  onNewGame,
  onSaveGame,
  onLoadGame,
  isCollapsed,
  onToggleCollapse
}) => {
  const [activeTab, setActiveTab] = useState<'character' | 'inventory' | 'session'>('character');

  if (isCollapsed) {
    return (
      <div className="sidebar w-12 flex flex-col items-center py-4">
        <button
          onClick={onToggleCollapse}
          className="btn-secondary p-2 mb-4"
          title="Expand sidebar"
        >
          →
        </button>
        <div className="flex flex-col space-y-2">
          <button
            onClick={onNewGame}
            className="btn-secondary p-2"
            title="New Game"
          >
            🎲
          </button>
          {onSaveGame && (
            <button
              onClick={onSaveGame}
              className="btn-secondary p-2"
              title="Save Game"
              >
              💾
            </button>
          )}
          {onLoadGame && (
            <button
              onClick={onLoadGame}
              className="btn-secondary p-2"
              title="Load Game"
            >
              📂
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="sidebar w-80 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-parchment-300 bg-parchment-50">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-fantasy text-ink-800">SoloHeart Log</h2>
          <button
            onClick={onToggleCollapse}
            className="btn-secondary p-2"
            title="Collapse sidebar"
          >
            ←
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-parchment-300">
        {['character', 'inventory', 'session'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`flex-1 px-4 py-2 text-sm font-medium capitalize ${
              activeTab === tab
                ? 'bg-parchment-200 text-ink-800 border-b-2 border-parchment-300'
                : 'bg-white text-ink-600 hover:bg-parchment-50'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'character' && (
          <CharacterTab session={session} />
        )}
        {activeTab === 'inventory' && (
          <InventoryTab session={session} />
        )}
        {activeTab === 'session' && (
          <SessionTab 
            session={session}
            onNewGame={onNewGame}
            onSaveGame={onSaveGame}
            onLoadGame={onLoadGame}
          />
        )}
      </div>
    </div>
  );
};

const CharacterTab: React.FC<{ session: Session | null }> = ({ session }) => {
  if (!session?.character) {
    return (
      <div className="text-center text-ink-500 py-8">
        <div className="text-2xl mb-2">👤</div>
        <p>No character created yet.</p>
        <p className="text-sm">Start a new game to create your character.</p>
      </div>
    );
  }

  const { character } = session;
  const statNames = { STR: 'Strength', DEX: 'Dexterity', CON: 'Constitution', INT: 'Intelligence', WIS: 'Wisdom', CHA: 'Charisma' };

  return (
    <div className="space-y-4">
      <div className="text-center">
        <h3 className="text-xl font-fantasy text-ink-800 mb-1">{character.name}</h3>
        <p className="text-ink-600">Level {character.level} {character.class}</p>
      </div>

      {/* HP Bar */}
      <div>
        <div className="flex justify-between text-sm mb-1">
          <span>Hit Points</span>
          <span>{character.hp.current} / {character.hp.max}</span>
        </div>
        <div className="w-full bg-parchment-200 rounded-full h-2">
          <div
            className="bg-red-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(character.hp.current / character.hp.max) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Stats */}
      <div>
        <h4 className="font-semibold text-ink-800 mb-2">Ability Scores</h4>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(character.stats).map(([stat, value]) => (
            <div key={stat} className="flex justify-between p-2 bg-parchment-50 rounded">
              <span className="text-sm text-ink-600">{statNames[stat as keyof typeof statNames]}</span>
              <span className="font-semibold text-ink-800">{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const InventoryTab: React.FC<{ session: Session | null }> = ({ session }) => {
  if (!session?.character?.inventory) {
    return (
      <div className="text-center text-ink-500 py-8">
        <div className="text-2xl mb-2">🎒</div>
        <p>No inventory available.</p>
      </div>
    );
  }

  return (
    <div>
      <h4 className="font-semibold text-ink-800 mb-3">Inventory</h4>
      {session.character.inventory.length === 0 ? (
        <p className="text-ink-500 text-center py-4">Your inventory is empty.</p>
      ) : (
        <div className="space-y-2">
          {session.character.inventory.map((item, index) => (
            <div key={index} className="p-2 bg-parchment-50 rounded border border-parchment-200">
              {item}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const SessionTab: React.FC<{
  session: Session | null;
  onNewGame: () => void;
  onSaveGame?: () => void;
  onLoadGame?: () => void;
}> = ({ session, onNewGame, onSaveGame, onLoadGame }) => {
  return (
    <div className="space-y-4">
      <div>
        <h4 className="font-semibold text-ink-800 mb-3">Session Controls</h4>
        <div className="space-y-2">
          <button onClick={onNewGame} className="btn-primary w-full">
            🎲 New Game
          </button>
          {onSaveGame && (
            <button onClick={onSaveGame} className="btn-secondary w-full">
              💾 Save Game
            </button>
          )}
          {onLoadGame && (
            <button onClick={onLoadGame} className="btn-secondary w-full">
              📂 Load Game
            </button>
          )}
        </div>
      </div>

      {session && (
        <div>
          <h4 className="font-semibold text-ink-800 mb-3">Session Info</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-ink-600">Session ID:</span>
              <span className="font-mono text-ink-800">{session.id.slice(0, 8)}...</span>
            </div>
            <div className="flex justify-between">
              <span className="text-ink-600">Started:</span>
              <span className="text-ink-800">
                {new Date(session.startedAt).toLocaleDateString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-ink-600">Messages:</span>
              <span className="text-ink-800">{session.messages.length}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
