import { Link } from "react-router-dom";
import { Home, Search } from "lucide-react";

export default function NotFound() {
  return (
    <div style={{
      display: "flex", flexDirection: "column", alignItems: "center",
      justifyContent: "center", minHeight: "80vh", gap: 20, textAlign: "center",
      padding: "0 24px"
    }}>
      <div style={{
        fontSize: "6rem", fontWeight: 900, letterSpacing: "-0.05em",
        background: "var(--accent-gradient)", WebkitBackgroundClip: "text",
        WebkitTextFillColor: "transparent"
      }}>
        404
      </div>
      <h2>Page not found</h2>
      <p style={{ color: "var(--text-muted)", maxWidth: 360 }}>
        The page you're looking for doesn't exist or the document may have been deleted.
      </p>
      <Link to="/" className="btn btn-primary">
        <Home size={16} /> Back to Dashboard
      </Link>
    </div>
  );
}
