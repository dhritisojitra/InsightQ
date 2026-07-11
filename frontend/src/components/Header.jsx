import { Bell, Menu, Search } from "lucide-react";
import ThemeToggle from "./ThemeToggle";
import "./Header.css";

export default function Header({ title, subtitle, theme, onThemeToggle, onMenuToggle }) {
  return (
    <header className="app-header">
      <div className="header-left">
        <button className="header-menu-btn btn btn-ghost btn-icon" onClick={onMenuToggle} aria-label="Toggle menu">
          <Menu size={20} />
        </button>
        <div className="header-title-group">
          {title && <h1 className="header-title">{title}</h1>}
          {subtitle && <p className="header-subtitle">{subtitle}</p>}
        </div>
      </div>

      <div className="header-right">
        <ThemeToggle theme={theme} onToggle={onThemeToggle} />
      </div>
    </header>
  );
}
