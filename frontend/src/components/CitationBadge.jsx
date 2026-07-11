import { BookOpen, FileText, Tag } from "lucide-react";
import "./CitationBadge.css";

export default function CitationBadge({ citations }) {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="citations-container">
      <span className="citations-label">
        <BookOpen size={12} /> Sources
      </span>
      <div className="citations-list">
        {citations.map((cite, i) => (
          <span key={i} className="citation-badge">
            <FileText size={11} />
            <span className="citation-file">{cite.filename}</span>
            <span className="citation-page">p.{cite.page_number}</span>
          </span>
        ))}
      </div>
    </div>
  );
}
