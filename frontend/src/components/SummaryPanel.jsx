import { useState, useEffect } from "react";
import { BookText, Tag, AlignLeft, RefreshCw, FileText } from "lucide-react";
import { summaryApi } from "../api/client";
import "./SummaryPanel.css";

export default function SummaryPanel({ docId, cachedSummary, cachedTopics }) {
  const [summary, setSummary] = useState(cachedSummary || "");
  const [topics, setTopics] = useState(cachedTopics || []);
  const [wordCount, setWordCount] = useState(0);
  const [loading, setLoading] = useState(!cachedSummary);
  const [error, setError] = useState("");

  const loadSummary = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await summaryApi.generate(docId);
      setSummary(data.summary);
      setTopics(data.key_topics || []);
      setWordCount(data.word_count || 0);
    } catch (err) {
      setError(err.message || "Failed to generate summary");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!cachedSummary) {
      loadSummary();
    }
  }, [docId]);

  return (
    <div className="summary-panel">
      <div className="summary-header">
        <div className="summary-header-left">
          <BookText size={18} className="summary-icon" />
          <h3>Document Summary</h3>
        </div>
        <button
          className="btn btn-ghost btn-sm btn-icon"
          onClick={loadSummary}
          disabled={loading}
          title="Regenerate summary"
        >
          <RefreshCw size={15} className={loading ? "spin" : ""} />
        </button>
      </div>

      {wordCount > 0 && (
        <p className="summary-wordcount">
          <FileText size={11} /> {wordCount.toLocaleString()} words
        </p>
      )}

      {loading ? (
        <div className="summary-loading">
          <div className="skeleton" style={{ height: 18, width: "90%", marginBottom: 10 }} />
          <div className="skeleton" style={{ height: 18, width: "75%", marginBottom: 10 }} />
          <div className="skeleton" style={{ height: 18, width: "82%" }} />
        </div>
      ) : error ? (
        <p className="summary-error">{error}</p>
      ) : (
        <>
          <div className="summary-body">
            {summary.split("\n\n").map((para, i) => (
              <p key={i}>{para}</p>
            ))}
          </div>

          {topics.length > 0 && (
            <div className="summary-topics">
              <p className="summary-topics-label">
                <Tag size={13} /> Key Topics
              </p>
              <div className="summary-topics-list">
                {topics.map((t, i) => (
                  <span key={i} className="badge badge-violet">{t}</span>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
