import { useState } from "react";
import { Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Dashboard from "./pages/Dashboard";
import DocumentView from "./pages/DocumentView";
import NotFound from "./pages/NotFound";

import { useDocuments } from "./hooks/useDocuments";
import { useTheme } from "./hooks/useTheme";
import "./App.css";

export default function App() {
  const { theme, toggleTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const {
    documents,
    loading,
    uploading,
    uploadProgress,
    uploadDocument,
    deleteDocument,
  } = useDocuments();

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <Sidebar
        documents={documents}
        onDeleteDoc={deleteDocument}
        open={sidebarOpen}
      />

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main */}
      <main className="main-content">
        <Routes>
          <Route
            path="/"
            element={
              <>
                <Header
                  title="InsightQ"
                  subtitle="AI-powered academic document assistant"
                  theme={theme}
                  onThemeToggle={toggleTheme}
                  onMenuToggle={() => setSidebarOpen((o) => !o)}
                />
                <div className="page-wrapper">
                  <Dashboard
                    documents={documents}
                    loading={loading}
                    uploading={uploading}
                    uploadProgress={uploadProgress}
                    onUpload={uploadDocument}
                    onDelete={deleteDocument}
                  />
                </div>
              </>
            }
          />
          <Route
            path="/doc/:docId"
            element={
              <>
                <Header
                  theme={theme}
                  onThemeToggle={toggleTheme}
                  onMenuToggle={() => setSidebarOpen((o) => !o)}
                />
                <DocumentView />
              </>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>

      {/* Toast notifications */}
      <Toaster
        position="bottom-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: "var(--bg-secondary)",
            color: "var(--text-primary)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "12px",
            fontSize: "0.88rem",
            fontFamily: "Inter, sans-serif",
          },
          success: {
            iconTheme: { primary: "#10b981", secondary: "white" },
          },
          error: {
            iconTheme: { primary: "#ef4444", secondary: "white" },
          },
        }}
      />
    </div>
  );
}
