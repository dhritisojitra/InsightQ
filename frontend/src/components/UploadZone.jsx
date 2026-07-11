import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, AlertCircle, CheckCircle2 } from "lucide-react";
import "./UploadZone.css";

export default function UploadZone({ onUpload, uploading, uploadProgress }) {
  const [dragError, setDragError] = useState("");

  const onDrop = useCallback(
    (accepted, rejected) => {
      setDragError("");
      if (rejected.length > 0) {
        setDragError("Only PDF files under 50 MB are accepted.");
        return;
      }
      if (accepted.length > 0) {
        onUpload(accepted[0]);
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024,
    disabled: uploading,
  });

  const zoneClass = [
    "upload-zone",
    isDragActive && !isDragReject ? "drag-active" : "",
    isDragReject ? "drag-reject" : "",
    uploading ? "uploading" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className="upload-zone-wrapper">
      <div {...getRootProps()} className={zoneClass}>
        <input {...getInputProps()} id="pdf-upload-input" />

        {uploading ? (
          <div className="upload-progress-state">
            <div className="upload-spinner-ring">
              <svg viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15" fill="none" stroke="currentColor" strokeWidth="2" opacity="0.2" />
                <circle
                  cx="18" cy="18" r="15" fill="none"
                  stroke="url(#grad)" strokeWidth="2.5"
                  strokeDasharray={`${(uploadProgress / 100) * 94} 94`}
                  strokeLinecap="round"
                  transform="rotate(-90 18 18)"
                />
                <defs>
                  <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#7c3aed" />
                    <stop offset="100%" stopColor="#06b6d4" />
                  </linearGradient>
                </defs>
              </svg>
              <span className="upload-pct">{uploadProgress}%</span>
            </div>
            <p className="upload-status-text">Uploading & indexing PDF…</p>
            <p className="upload-status-sub">Generating embeddings and extracting content</p>
          </div>
        ) : isDragActive && !isDragReject ? (
          <div className="upload-idle-state active">
            <CheckCircle2 size={40} className="upload-icon active" />
            <p className="upload-main-text">Drop your PDF here!</p>
          </div>
        ) : (
          <div className="upload-idle-state">
            <div className="upload-icon-ring">
              <Upload size={28} />
            </div>
            <p className="upload-main-text">
              Drag &amp; drop a PDF here, or{" "}
              <span className="upload-browse-link">browse</span>
            </p>
            <p className="upload-sub-text">PDF only · Max 50 MB · Academic papers, notes, textbooks</p>
          </div>
        )}
      </div>

      {dragError && (
        <div className="upload-error animate-fadeIn">
          <AlertCircle size={14} />
          {dragError}
        </div>
      )}
    </div>
  );
}
