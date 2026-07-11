import { Sun, Moon } from "lucide-react";
import "./ThemeToggle.css";

export default function ThemeToggle({ theme, onToggle }) {
  return (
    <button
      className="theme-toggle"
      onClick={onToggle}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
      title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
    >
      <div className={`theme-toggle-track ${theme}`}>
        <div className="theme-toggle-thumb">
          {theme === "dark" ? <Moon size={12} /> : <Sun size={12} />}
        </div>
      </div>
    </button>
  );
}
