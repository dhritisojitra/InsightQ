import { NavLink, useNavigate } from "react-router-dom";
import { BookOpen, LayoutDashboard, FileText, Sparkles, ChevronRight, Trash2 } from "lucide-react";
import { truncate, timeAgo } from "../utils/helpers";
import "./Sidebar.css";

export default function Sidebar({ documents, onDeleteDoc }) {
  const navigate = useNavigate();

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">
          <Sparkles size={20} />
        </div>
        <div className="sidebar-logo-text">
          <span className="gradient-text">Insight</span>
          <span className="sidebar-logo-sub">Q</span>
        </div>
      </div>

      <div className="sidebar-divider" />

      {/* Nav */}
      <nav className="sidebar-nav">
        <p className="sidebar-section-label">Navigation</p>
        <NavLink to="/" end className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
          <LayoutDashboard size={18} />
          Dashboard
        </NavLink>
      </nav>

      <div className="sidebar-divider" />

      {/* Documents */}
      <div className="sidebar-docs">
        <p className="sidebar-section-label">
          Documents
          <span className="sidebar-count">{documents.length}</span>
        </p>

        {documents.length === 0 ? (
          <p className="sidebar-empty">No documents yet</p>
        ) : (
          <ul className="sidebar-doc-list">
            {documents.map((doc) => (
              <li key={doc.doc_id} className="sidebar-doc-item">
                <button
                  className="sidebar-doc-btn"
                  onClick={() => navigate(`/doc/${doc.doc_id}`)}
                  title={doc.filename}
                >
                  <FileText size={14} className="sidebar-doc-icon" />
                  <div className="sidebar-doc-info">
                    <span className="sidebar-doc-name">{truncate(doc.filename, 22)}</span>
                    <span className="sidebar-doc-meta">{doc.page_count}p · {timeAgo(doc.uploaded_at)}</span>
                  </div>
                  <ChevronRight size={12} className="sidebar-doc-arrow" />
                </button>
                <button
                  className="sidebar-doc-delete"
                  onClick={(e) => { e.stopPropagation(); onDeleteDoc(doc.doc_id, doc.filename); }}
                  title="Delete document"
                >
                  <Trash2 size={13} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="sidebar-footer-badge">
          <BookOpen size={13} />
          <span>RAG-powered</span>
        </div>
      </div>
    </aside>
  );
}
