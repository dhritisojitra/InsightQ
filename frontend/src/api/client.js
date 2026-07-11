/**
 * Axios API client — typed wrappers for all backend endpoints.
 */
import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000, // 2 min for LLM calls
  headers: { "Content-Type": "application/json" },
});

// ─── Response interceptor ──────────────────────────────────────────────────
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      err.message ||
      "An unexpected error occurred";
    return Promise.reject(new Error(message));
  }
);

// ─── Documents ─────────────────────────────────────────────────────────────
export const documentsApi = {
  upload: (file, onProgress) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/api/documents/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total));
        }
      },
    });
  },

  list: () => api.get("/api/documents/"),
  get: (docId) => api.get(`/api/documents/${docId}`),
  delete: (docId) => api.delete(`/api/documents/${docId}`),
};

// ─── Chat ──────────────────────────────────────────────────────────────────
export const chatApi = {
  ask: (docId, question) =>
    api.post(`/api/chat/${docId}/ask`, { question }),

  getHistory: (docId) => api.get(`/api/chat/${docId}/history`),
  clearHistory: (docId) => api.delete(`/api/chat/${docId}/history`),
};

// ─── Summary ───────────────────────────────────────────────────────────────
export const summaryApi = {
  generate: (docId) => api.post(`/api/summary/${docId}`),
  get: (docId) => api.get(`/api/summary/${docId}`),
};

// ─── MCQ ───────────────────────────────────────────────────────────────────
export const mcqApi = {
  generate: (docId, numQuestions = 5, difficulty = "medium") =>
    api.post(`/api/mcq/${docId}`, { num_questions: numQuestions, difficulty }),
};

// ─── Health ────────────────────────────────────────────────────────────────
export const healthApi = {
  check: () => api.get("/health"),
};

export default api;
