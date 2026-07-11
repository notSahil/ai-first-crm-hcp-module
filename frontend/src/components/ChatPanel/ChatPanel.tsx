import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from '../../store';
import { addMessage, setLoading, setError } from '../../store/chatSlice';
import { applyFormUpdates } from '../../store/formSlice';
import { sendChatMessage } from '../../api/chatApi';
import './ChatPanel.css';

const HINT_TEXT = `Log interaction details here (e.g., "Met Dr. Smith, discussed ProduX efficacy, positive sentiment, shared brochure") or ask for help.`;

const ChatPanel: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { messages, isLoading } = useSelector((state: RootState) => state.chat);
  const formState = useSelector((state: RootState) => state.form);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const text = input.trim();
    if (!text || isLoading) return;

    setInput('');
    dispatch(addMessage({ role: 'user', content: text }));
    dispatch(setLoading(true));
    dispatch(setError(null));

    try {
      const chatHistory = messages.map((m) => ({ role: m.role, content: m.content }));
      const response = await sendChatMessage(text, formState, chatHistory);

      // Apply form updates from AI
      if (response.form_updates && Object.keys(response.form_updates).length > 0) {
        dispatch(applyFormUpdates(response.form_updates));
      }

      dispatch(addMessage({ role: 'assistant', content: response.reply }));
    } catch (err: any) {
      const errMsg = err?.response?.data?.detail || 'Failed to reach the AI assistant. Make sure the backend is running.';
      dispatch(setError(errMsg));
      dispatch(addMessage({
        role: 'assistant',
        content: `⚠️ ${errMsg}`,
      }));
    } finally {
      dispatch(setLoading(false));
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="chat-panel">
      {/* Header */}
      <div className="chat-panel__header">
        <div className="chat-header-icon">🤖</div>
        <div>
          <h2 className="chat-header-title">AI Assistant</h2>
          <p className="chat-header-subtitle">Log Interaction details here via chat</p>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {/* Initial hint bubble */}
        <div className="chat-hint-bubble">
          {HINT_TEXT}
        </div>

        {messages.map((msg) => (
          <div key={msg.id} className={`chat-message chat-message--${msg.role}`}>
            {msg.role === 'assistant' && (
              <div className="chat-avatar chat-avatar--ai">🤖</div>
            )}
            <div className={`chat-bubble chat-bubble--${msg.role}`}>
              <p className="chat-bubble-text">{msg.content}</p>
              <span className="chat-bubble-time">
                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
            {msg.role === 'user' && (
              <div className="chat-avatar chat-avatar--user">👤</div>
            )}
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="chat-message chat-message--assistant">
            <div className="chat-avatar chat-avatar--ai">🤖</div>
            <div className="chat-bubble chat-bubble--assistant chat-bubble--loading">
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <form className="chat-input-area" onSubmit={handleSubmit}>
        <textarea
          ref={inputRef}
          className="chat-input"
          rows={2}
          placeholder="Describe Interaction..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          type="submit"
          className={`chat-submit-btn ${isLoading ? 'chat-submit-btn--loading' : ''}`}
          disabled={isLoading || !input.trim()}
          aria-label="Send message"
        >
          {isLoading ? (
            <span className="btn-spinner" />
          ) : (
            <>
              <span className="btn-a">A</span>
              <span className="btn-log">Log</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default ChatPanel;
