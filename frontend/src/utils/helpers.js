/**
 * Utility helpers for formatting and display.
 */

/** Format bytes to human-readable string */
export function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/** Format KB to human-readable string */
export function formatFileSizeKB(kb) {
  if (kb < 1024) return `${kb.toFixed(0)} KB`;
  return `${(kb / 1024).toFixed(1)} MB`;
}

/** Format datetime string to relative time */
export function timeAgo(dateStr) {
  if (!dateStr) return "unknown";
  
  // Treat date string as UTC if it doesn't specify a timezone
  let cleanDateStr = dateStr;
  if (!dateStr.includes("Z") && !dateStr.includes("+") && !dateStr.match(/-\d{2}:\d{2}$/)) {
    cleanDateStr = `${dateStr}Z`;
  }

  const date = new Date(cleanDateStr);
  const now = new Date();
  const diffMs = now - date;
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

/** Format datetime to locale string */
export function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString();
}

/** Truncate a string to a max length */
export function truncate(str, maxLen = 60) {
  if (!str) return "";
  return str.length > maxLen ? str.slice(0, maxLen) + "…" : str;
}

/** Generate a gradient color based on a string (for avatars/icons) */
export function stringToGradient(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue1 = Math.abs(hash) % 360;
  const hue2 = (hue1 + 40) % 360;
  return `linear-gradient(135deg, hsl(${hue1},70%,55%), hsl(${hue2},70%,55%))`;
}

/** Get file extension without the dot */
export function getFileExt(filename) {
  return filename.split(".").pop()?.toUpperCase() || "";
}

/** Debounce a function */
export function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}
