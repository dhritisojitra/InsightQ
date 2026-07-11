import { useState, useEffect, useCallback } from "react";
import { documentsApi } from "../api/client";
import toast from "react-hot-toast";

/**
 * Hook for managing uploaded documents list and upload flow.
 */
export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      const { data } = await documentsApi.list();
      setDocuments(data.documents || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const uploadDocument = useCallback(async (file) => {
    setUploading(true);
    setUploadProgress(0);
    try {
      const { data } = await documentsApi.upload(file, (progress) => {
        setUploadProgress(progress);
      });
      toast.success(`"${file.name}" uploaded and indexed!`);
      await fetchDocuments();
      return data;
    } catch (err) {
      toast.error(err.message || "Upload failed");
      throw err;
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [fetchDocuments]);

  const deleteDocument = useCallback(async (docId, filename) => {
    try {
      await documentsApi.delete(docId);
      setDocuments((prev) => prev.filter((d) => d.doc_id !== docId));
      toast.success(`"${filename}" deleted.`);
    } catch (err) {
      toast.error(err.message || "Delete failed");
    }
  }, []);

  return {
    documents,
    loading,
    uploading,
    uploadProgress,
    error,
    uploadDocument,
    deleteDocument,
    refetch: fetchDocuments,
  };
}
