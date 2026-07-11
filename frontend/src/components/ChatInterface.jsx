import { useEffect, useRef, useState } from "react";
import { Send, Trash2, MessageSquare } from "lucide-react";
import MessageBubble from "./MessageBubble";
import "./ChatInterface.css";

export default function ChatInterface({
  messages,
  loading,
  onSend,
  onClear,
  suggestedQuestions = [],
}) {
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const q = input.trim();
    if (!q || loading) return;
    onSend(q);
    setInput("");
  };

  const handleSuggested = (q) => {
    setInput(q);
    inputRef.current?.focus();
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="chat-interface">
      {/* Messages */}
      <div className="chat-messages">
        {isEmpty ? (
          <div className="chat-empty">
            <div className="chat-empty-icon">
              <MessageSquare size={36} />
            </div>
            <h3>Ask anything about this document</h3>
            <p>I'll find relevant passages and cite the source page for every answer.</p>

            {suggestedQuestions.length > 0 && (
              <div className="chat-suggestions">
                <p className="chat-suggestions-label">Suggested questions</p>
                <div className="chat-suggestions-list">
                  {suggestedQuestions.map((q, i) => (
                    <button
                      key={i}
                      className="chat-suggestion-btn"
                      onClick={() => handleSuggested(q)}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <>
            {messages.map((msg, i) => (
              <MessageBubble key={i} message={msg} />
            ))}

            {loading && (
              <div className="message-bubble-wrapper assistant animate-fadeIn">
                <div className="message-avatar ai-avatar">
                  <div className="spinner" style={{ width: 16, height: 16 }} />
                </div>
                <div className="message-bubble ai-bubble">
                  <div className="typing-indicator">
                    <div className="typing-dot" />
                    <div className="typing-dot" />
                    <div className="typing-dot" />
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggested pills above input (when chat is not empty) */}
      {!isEmpty && suggestedQuestions.length > 0 && (
        <div className="chat-input-suggestions">
          {suggestedQuestions.slice(0, 3).map((q, i) => (
            <button key={i} className="chat-pill" onClick={() => handleSuggested(q)}>
              {q.length > 50 ? q.slice(0, 50) + "…" : q}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <div className="chat-input-row">
          <input
            ref={inputRef}
            className="input chat-input"
            placeholder="Ask a question about this document…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            maxLength={2000}
            autoComplete="off"
            id="chat-question-input"
          />
          <button
            type="submit"
            className="btn btn-primary chat-send-btn"
            disabled={!input.trim() || loading}
            id="chat-send-btn"
          >
            <Send size={18} />
          </button>
          {messages.length > 0 && (
            <button
              type="button"
              className="btn btn-ghost btn-icon chat-clear-btn"
              onClick={onClear}
              title="Clear history"
            >
              <Trash2 size={18} />
            </button>
          )}
        </div>
        <p className="chat-input-hint">
          Answers are generated from the document content with page citations.
        </p>
      </form>
    </div>
  );
}
