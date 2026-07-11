import { Bot, User, AlertTriangle } from "lucide-react";
import CitationBadge from "./CitationBadge";
import { formatDate } from "../utils/helpers";
import "./MessageBubble.css";

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";
  const isError = message.isError;

  return (
    <div className={`message-bubble-wrapper ${isUser ? "user" : "assistant"} animate-fadeIn`}>
      {/* Avatar */}
      <div className={`message-avatar ${isUser ? "user-avatar" : "ai-avatar"}`}>
        {isUser ? <User size={16} /> : isError ? <AlertTriangle size={16} /> : <Bot size={16} />}
      </div>

      {/* Bubble */}
      <div className={`message-bubble ${isUser ? "user-bubble" : "ai-bubble"} ${isError ? "error-bubble" : ""}`}>
        <div className="message-content">
          {message.content.split("\n").map((line, i) => (
            <p key={i} className={line.startsWith("•") || line.startsWith("-") ? "message-bullet" : ""}>
              {line || <br />}
            </p>
          ))}
        </div>

        {/* Citations for assistant */}
        {!isUser && message.citations?.length > 0 && (
          <CitationBadge citations={message.citations} />
        )}

        <span className="message-time">{formatDate(message.timestamp)}</span>
      </div>
    </div>
  );
}
