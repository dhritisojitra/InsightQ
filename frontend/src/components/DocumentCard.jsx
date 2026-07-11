import { useNavigate } from "react-router-dom";
import { FileText, MessageSquare, BookOpen, Clock, Layers, Trash2, ArrowRight } from "lucide-react";
import { formatFileSizeKB, timeAgo } from "../utils/helpers";
import "./DocumentCard.css";

export default function DocumentCard({ doc, onDelete }) {
  const navigate = useNavigate();

  const handleOpen = () => navigate(`/doc/${doc.doc_id}`);

  return (
    <article className="doc-card glass-card animate-fadeIn" onClick={handleOpen}>
      {/* Top row */}
      <div className="doc-card-header">
        <div className="doc-card-icon">
          <FileText size={22} />
        </div>
        <div className="doc-card-meta">
          <h3 className="doc-card-title" title={doc.filename}>{doc.filename}</h3>
          <div className="doc-card-tags">
            <span className="badge badge-violet">
              <Layers size={10} /> {doc.page_count}p
            </span>
            <span className="badge badge-cyan">
              {formatFileSizeKB(doc.file_size_kb)}
            </span>
            <span className="badge badge-green">
              {doc.chunk_count} chunks
            </span>
          </div>
        </div>
        <button
          className="doc-card-delete btn btn-ghost btn-icon"
          onClick={(e) => { e.stopPropagation(); onDelete(doc.doc_id, doc.filename); }}
          title="Delete document"
          aria-label="Delete document"
        >
          <Trash2 size={16} />
        </button>
      </div>

      {/* Summary preview */}
      {doc.summary && (
        <p className="doc-card-summary">{doc.summary.slice(0, 160)}…</p>
      )}

      {/* Footer */}
      <div className="doc-card-footer">
        <span className="doc-card-time">
          <Clock size={12} /> {timeAgo(doc.uploaded_at)}
        </span>
        <button className="doc-card-open btn btn-sm btn-secondary" onClick={handleOpen}>
          Open <ArrowRight size={14} />
        </button>
      </div>
    </article>
  );
}
