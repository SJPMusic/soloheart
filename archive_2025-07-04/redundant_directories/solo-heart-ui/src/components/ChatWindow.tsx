import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from '../utils/api';

interface ChatWindowProps {
  messages: Message[];
  isLoading?: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages, isLoading = false }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const formatMessage = (content: string, type: 'player' | 'ai') => {
    if (type === 'ai') {
      return (
        <div className="narrative-text">
          <ReactMarkdown
            components={{
              p: ({ children }) => <p className="mb-4">{children}</p>,
              em: ({ children }) => <em className="italic text-ink-600">{children}</em>,
              strong: ({ children }) => <strong className="font-semibold text-ink-800">{children}</strong>,
              ul: ({ children }) => <ul className="list-disc list-inside mb-4 space-y-1">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal list-inside mb-4 space-y-1">{children}</ol>,
              li: ({ children }) => <li className="text-ink-700">{children}</li>,
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-parchment-400 pl-4 italic text-ink-600 mb-4">
                  {children}
                </blockquote>
              ),
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      );
    }
    
    return <p className="text-ink-800">{content}</p>;
  };

  const LoadingIndicator = () => (
    <div className="chat-bubble ai">
      <div className="flex items-center space-x-2">
        <div className="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <span className="text-ink-600 text-sm">The SoloHeart Guide is thinking...</span>
      </div>
    </div>
  );

  return (
    <div className="flex-1 flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-ink-500">
              <div className="text-4xl mb-4">🎲</div>
              <h3 className="text-xl font-fantasy mb-2">Welcome to SoloHeart</h3>
              <p className="text-lg">Begin your journey by typing your first action or command.</p>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`chat-bubble ${message.type === 'ai' ? 'ai' : 'player'}`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  {message.type === 'ai' ? (
                    <div className="w-8 h-8 bg-parchment-600 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-bold">SH</span>
                    </div>
                  ) : (
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-bold">You</span>
                    </div>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-ink-500 mb-1">
                    {message.type === 'ai' ? 'SoloHeart Guide' : 'You'} •{' '}
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                  {formatMessage(message.content, message.type)}
                </div>
              </div>
            </div>
          ))
        )}
        {isLoading && <LoadingIndicator />}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatWindow;
