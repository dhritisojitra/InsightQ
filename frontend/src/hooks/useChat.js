import { useState, useCallback, useRef } from "react";
import { chatApi } from "../api/client";
import toast from "react-hot-toast";

/**
 * Hook for managing chat Q&A for a single document.
 */
export function useChat(docId) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const abortRef = useRef(null);

  const loadHistory = useCallback(async () => {
    if (!docId) return;
    setHistoryLoading(true);
    try {
      const { data } = await chatApi.getHistory(docId);
      setMessages(data.messages || []);
    } catch {
      // Silently fail — history might not exist yet
    } finally {
      setHistoryLoading(false);
    }
  }, [docId]);

  const sendMessage = useCallback(
    async (question) => {
      if (!question.trim() || loading) return;

      const userMsg = {
        role: "user",
        content: question,
        citations: [],
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);

      try {
        const { data } = await chatApi.ask(docId, question);
        const assistantMsg = {
          role: "assistant",
          content: data.answer,
          citations: data.citations || [],
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMsg]);
        return assistantMsg;
      } catch (err) {
        const errMsg = {
          role: "assistant",
          content: `Sorry, I encountered an error: ${err.message}`,
          citations: [],
          timestamp: new Date().toISOString(),
          isError: true,
        };
        setMessages((prev) => [...prev, errMsg]);
        toast.error("Failed to get answer");
      } finally {
        setLoading(false);
      }
    },
    [docId, loading]
  );

  const clearHistory = useCallback(async () => {
    try {
      await chatApi.clearHistory(docId);
      setMessages([]);
      toast.success("Chat history cleared");
    } catch {
      toast.error("Failed to clear history");
    }
  }, [docId]);

  return {
    messages,
    loading,
    historyLoading,
    loadHistory,
    sendMessage,
    clearHistory,
  };
}
