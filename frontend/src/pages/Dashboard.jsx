import { useState } from "react";
import { Sparkles, Upload, FileText, Zap, BarChart2, BookOpen } from "lucide-react";
import UploadZone from "../components/UploadZone";
import DocumentCard from "../components/DocumentCard";
import "./Dashboard.css";

export default function Dashboard({ documents, loading, uploading, uploadProgress, onUpload, onDelete }) {
  const stats = [
    { label: "Documents", value: documents.length, icon: <FileText size={20} />, color: "violet" },
    {
      label: "Total Pages",
      value: documents.reduce((acc, d) => acc + d.page_count, 0),
      icon: <BookOpen size={20} />,
      color: "cyan",
    },
    {
      label: "Total Chunks",
      value: documents.reduce((acc, d) => acc + d.chunk_count, 0),
      icon: <BarChart2 size={20} />,
      color: "green",
    },
  ];

  return (
    <div className="dashboard animate-fadeIn">
      {/* Hero */}
      <section className="dashboard-hero">
        <div className="dashboard-hero-content">
          <div className="dashboard-hero-badge">
            <Zap size={12} /> AI-Powered Academic RAG
          </div>
          <h1>
            Ask questions,{" "}
            <span className="gradient-text">get cited answers</span>
          </h1>
          <p>
            Upload academic PDFs and get instant, source-cited answers using Retrieval-Augmented Generation
            with Gemini AI and Sentence Transformers.
          </p>
        </div>

        {/* Feature pills */}
        <div className="hero-features">
          {[
            "📖 Semantic Search",
            "🔗 Page Citations",
            "📝 Auto Summary",
            "🎓 MCQ Generation",
            "💬 Chat History",
          ].map((f) => (
            <span key={f} className="hero-feature-pill">{f}</span>
          ))}
        </div>
      </section>

      {/* Stats */}
      {documents.length > 0 && (
        <div className="dashboard-stats stagger-children">
          {stats.map((s) => (
            <div key={s.label} className={`stat-card glass-card stat-${s.color} animate-fadeIn`}>
              <div className="stat-icon">{s.icon}</div>
              <div className="stat-info">
                <span className="stat-value">{s.value.toLocaleString()}</span>
                <span className="stat-label">{s.label}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload */}
      <section className="dashboard-upload glass-card">
        <div className="dashboard-section-header">
          <Upload size={18} />
          <h2>Upload Document</h2>
        </div>
        <UploadZone onUpload={onUpload} uploading={uploading} uploadProgress={uploadProgress} />
      </section>

      {/* Documents */}
      <section className="dashboard-documents">
        <div className="dashboard-section-header">
          <FileText size={18} />
          <h2>
            Your Documents
            {documents.length > 0 && <span className="section-count">{documents.length}</span>}
          </h2>
        </div>

        {loading ? (
          <div className="docs-grid">
            {[1, 2, 3].map((i) => (
              <div key={i} className="doc-card-skeleton glass-card">
                <div className="skeleton" style={{ height: 48, width: 48, borderRadius: 12, marginBottom: 14 }} />
                <div className="skeleton" style={{ height: 16, width: "70%", marginBottom: 8 }} />
                <div className="skeleton" style={{ height: 12, width: "50%" }} />
              </div>
            ))}
          </div>
        ) : documents.length === 0 ? (
          <div className="empty-state">
            <Sparkles size={48} />
            <h3>No documents yet</h3>
            <p>Upload your first PDF to start asking questions and generating insights.</p>
          </div>
        ) : (
          <div className="docs-grid stagger-children">
            {documents.map((doc) => (
              <DocumentCard key={doc.doc_id} doc={doc} onDelete={onDelete} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
