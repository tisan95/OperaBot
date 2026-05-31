"use client";

import { useState } from "react";
import { FileText, Eye, Download, X, AlertCircle } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface DocumentPreviewProps {
  document_id: string | number;
  document_name: string;
  user_role: string;
}

export default function DocumentPreview({
  document_id,
  document_name,
  user_role,
}: DocumentPreviewProps) {
  const [open, setOpen] = useState(false);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canDownload = user_role === "admin" || user_role === "super_admin";

  const openPreview = async () => {
    if (pdfUrl) {
      setOpen(true);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${API_BASE}/api/documents/${document_id}/preview`, {
        credentials: "include",
      });
      if (!resp.ok) {
        const data = await resp.json().catch(() => ({}));
        throw new Error(data.detail || `Error ${resp.status}`);
      }
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      setPdfUrl(url);
      setOpen(true);
    } catch (err: any) {
      setError(err.message || "Error cargando el documento");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      const resp = await fetch(`${API_BASE}/api/documents/${document_id}/download`, {
        credentials: "include",
      });
      if (!resp.ok) {
        const data = await resp.json().catch(() => ({}));
        throw new Error(data.detail || `Error ${resp.status}`);
      }
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = document_name;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.message || "Error descargando el documento");
    }
  };

  const closeModal = () => {
    setOpen(false);
    // Keep pdfUrl cached so re-open is instant
  };

  return (
    <>
      {/* Card */}
      <div
        className="flex items-center justify-between rounded-lg border px-3 py-2.5 mt-2"
        style={{ backgroundColor: "#111111", borderColor: "#2A2A2A" }}
      >
        <div className="flex items-center gap-2 min-w-0">
          <FileText size={14} strokeWidth={1.75} style={{ color: "#C9A84C", flexShrink: 0 }} />
          <span
            className="text-xs font-medium truncate max-w-[200px]"
            style={{ color: "#F5F5F5" }}
            title={document_name}
          >
            {document_name}
          </span>
        </div>

        <div className="flex items-center gap-1.5 ml-3 shrink-0">
          {error && (
            <span className="text-xs" style={{ color: "#E53E3E" }} title={error}>
              <AlertCircle size={13} strokeWidth={2} />
            </span>
          )}

          <button
            onClick={openPreview}
            disabled={loading}
            className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors"
            style={{
              backgroundColor: "rgba(201,168,76,0.1)",
              borderColor: "rgba(201,168,76,0.3)",
              border: "1px solid",
              color: loading ? "#888888" : "#C9A84C",
            }}
          >
            <Eye size={12} strokeWidth={2} />
            {loading ? "..." : "Ver"}
          </button>

          {canDownload && (
            <button
              onClick={handleDownload}
              className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors"
              style={{
                backgroundColor: "transparent",
                borderColor: "#2A2A2A",
                border: "1px solid",
                color: "#888888",
              }}
              onMouseEnter={(e) => ((e.currentTarget as HTMLButtonElement).style.color = "#F5F5F5")}
              onMouseLeave={(e) => ((e.currentTarget as HTMLButtonElement).style.color = "#888888")}
            >
              <Download size={12} strokeWidth={2} />
              Descargar
            </button>
          )}
        </div>
      </div>

      {/* Modal */}
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ backgroundColor: "rgba(0,0,0,0.85)" }}
          onClick={(e) => e.target === e.currentTarget && closeModal()}
        >
          <div
            className="flex flex-col rounded-2xl border overflow-hidden"
            style={{
              width: "min(90vw, 1000px)",
              height: "85vh",
              backgroundColor: "#1A1A1A",
              borderColor: "#2A2A2A",
            }}
          >
            {/* Modal header */}
            <div
              className="flex items-center justify-between px-5 py-3 border-b shrink-0"
              style={{ backgroundColor: "#111111", borderColor: "#2A2A2A" }}
            >
              <div className="flex items-center gap-2 min-w-0">
                <FileText size={15} strokeWidth={1.75} style={{ color: "#C9A84C" }} />
                <span className="text-sm font-medium truncate" style={{ color: "#F5F5F5" }}>
                  {document_name}
                </span>
              </div>
              <button
                onClick={closeModal}
                className="shrink-0 p-1.5 rounded-lg transition-colors ml-4"
                style={{ color: "#888888" }}
                onMouseEnter={(e) => ((e.currentTarget as HTMLButtonElement).style.color = "#F5F5F5")}
                onMouseLeave={(e) => ((e.currentTarget as HTMLButtonElement).style.color = "#888888")}
              >
                <X size={16} strokeWidth={1.75} />
              </button>
            </div>

            {/* PDF viewer */}
            <div className="flex-1 overflow-hidden">
              {pdfUrl ? (
                <iframe
                  src={pdfUrl}
                  className="w-full h-full border-0"
                  title={document_name}
                  style={{ backgroundColor: "#fff" }}
                  onError={() =>
                    setError(
                      "Tu navegador no soporta previsualización inline."
                    )
                  }
                />
              ) : null}

              {error && !pdfUrl && (
                <div className="flex flex-col items-center justify-center h-full gap-3 p-8 text-center">
                  <AlertCircle size={32} strokeWidth={1.5} style={{ color: "#888888" }} />
                  <p className="text-sm" style={{ color: "#888888" }}>
                    Tu navegador no soporta previsualización.
                    <br />
                    Contacta con tu administrador para acceder al documento.
                  </p>
                  {error && (
                    <p className="text-xs" style={{ color: "#555555" }}>
                      {error}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
