import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft, FileText, MessageSquare, BookText,
  GraduationCap, Layers, Clock
} from "lucide-react";
import { documentsApi } from "../api/client";
import { useChat } from "../hooks/useChat";
import ChatInterface from "../components/ChatInterface";
import SummaryPanel from "../components/SummaryPanel";
import MCQPanel from "../components/MCQPanel";
import { formatFileSizeKB, timeAgo } from "../utils/helpers";
import "./DocumentView.css";

const TABS = [
  { id: "chat", label: "Chat", icon: <MessageSquare size={16} /> },
  { id: "summary", label: "Summary", icon: <BookText size={16} /> },
  { id: "mcq", label: "MCQ Quiz", icon: <GraduationCap size={16} /> },
];

export default function DocumentView() {
  const { docId } = useParams();
  const navigate = useNavigate();
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("chat");

  const { messages, loading: chatLoading, historyLoading, loadHistory, sendMessage, clearHistory } =
    useChat(docId);

  useEffect(() => {
    const fetchDoc = async () => {
      setLoading(true);
      try {
        const { data } = await documentsApi.get(docId);
        setDoc(data);
      } catch {
        navigate("/");
      } finally {
        setLoading(false);
      }
    };
    fetchDoc();
    loadHistory();
  }, [docId]);

  if (loading) {
    return (
      <div className="docview-loading">
        <div className="spinner spinner-lg" />
      </div>
    );
  }

  if (!doc) return null;

  return (
    <div className="docview animate-fadeIn">
      {/* Doc header */}
      <div className="docview-header glass-card">
        <button className="btn btn-ghost btn-sm docview-back" onClick={() => navigate("/")}>
          <ArrowLeft size={16} /> Back
        </button>

        <div className="docview-doc-info">
          <div className="docview-doc-icon">
            <FileText size={24} />
          </div>
          <div className="docview-doc-meta">
            <h1 className="docview-doc-title">{doc.filename}</h1>
            <div className="docview-doc-tags">
              <span className="badge badge-violet">
                <Layers size={10} /> {doc.page_count} pages
              </span>
              <span className="badge badge-cyan">{formatFileSizeKB(doc.file_size_kb)}</span>
              <span className="badge badge-green">{doc.chunk_count} chunks</span>
              <span className="docview-upload-time">
                <Clock size={11} /> {timeAgo(doc.uploaded_at)}
              </span>
            </div>
          </div>
        </div>

        {/* Tab nav */}
        <nav className="docview-tabs">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              className={`docview-tab ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      <div className="docview-body">
        {activeTab === "chat" && (
          <div className="docview-chat-container glass-card">
            {historyLoading ? (
              <div className="docview-loading">
                <div className="spinner" />
              </div>
            ) : (
              <ChatInterface
                messages={messages}
                loading={chatLoading}
                onSend={sendMessage}
                onClear={clearHistory}
                suggestedQuestions={doc.suggested_questions || []}
              />
            )}
          </div>
        )}

        {activeTab === "summary" && (
          <div className="docview-panel glass-card animate-fadeIn">
            <SummaryPanel
              docId={docId}
              cachedSummary={doc.summary}
              cachedTopics={[]}
            />
          </div>
        )}

        {activeTab === "mcq" && (
          <div className="docview-panel glass-card animate-fadeIn">
            <MCQPanel docId={docId} />
          </div>
        )}
      </div>
    </div>
  );
}
