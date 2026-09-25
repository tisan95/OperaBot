"use client";

import { useEffect, useRef, useState } from "react";
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
  const dialogRef = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canDownload = user_role === "admin" || user_role === "super_admin";

  // Escape para cerrar
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") closeModal(); };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [open]);

  // Focus trap
  useEffect(() => {
    if (!open || !dialogRef.current) return;
    const el = dialogRef.current;
    const focusable = Array.from(
      el.querySelectorAll<HTMLElement>(
        'button:not([disabled]),input:not([disabled]),[tabindex]:not([tabindex="-1"])'
      )
    );
    focusable[0]?.focus();
    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== "Tab" || focusable.length === 0) return;
      const first = focusable[0];
      const last  = focusable[focusable.length - 1];
      if (e.shiftKey) {
        if (document.activeElement === first) { e.preventDefault(); last.focus(); }
      } else {
        if (document.activeElement === last)  { e.preventDefault(); first.focus(); }
      }
    };
    document.addEventListener("keydown", handleTab);
    return () => document.removeEventListener("keydown", handleTab);
  }, [open]);

  const openPreview = async () => {
    if (pdfUrl) { setOpen(true); return; }
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
      setPdfUrl(URL.createObjectURL(blob));
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
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = document_name;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.message || "Error descargando el documento");
    }
  };

  const closeModal = () => setOpen(false);

  return (
    <>
      {/* Tarjeta inline */}
      <div className="flex items-center justify-between rounded-lg border px-3 py-2.5 mt-2 bg-surface border-border">
        <div className="flex items-center gap-2 min-w-0">
          <FileText size={14} strokeWidth={1.5} className="text-gold shrink-0" />
          <span
            className="text-xs font-medium truncate max-w-[200px] text-text-primary"
            title={document_name}
          >
            {document_name}
          </span>
        </div>

        <div className="flex items-center gap-1.5 ml-3 shrink-0">
          {error && (
            <span className="text-xs text-error" title={error}>
              <AlertCircle size={13} strokeWidth={1.5} />
            </span>
          )}
          <button
            onClick={openPreview}
            disabled={loading}
            className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors border bg-gold/10 border-gold/30 ${loading ? "text-text-secondary" : "text-gold"}`}
          >
            <Eye size={12} strokeWidth={1.5} />
            {loading ? "..." : "Ver"}
          </button>
          {canDownload && (
            <button
              onClick={handleDownload}
              className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors border border-border text-text-secondary hover:text-text-primary"
            >
              <Download size={12} strokeWidth={1.5} />
              Descargar
            </button>
          )}
        </div>
      </div>

      {/* Modal */}
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-backdropIn"
          style={{ backgroundColor: "rgba(0,0,0,0.85)" }}
          onClick={(e) => e.target === e.currentTarget && closeModal()}
        >
          <div
            ref={dialogRef}
            role="dialog"
            aria-modal="true"
            aria-label={document_name}
            className="flex flex-col rounded-2xl border overflow-hidden bg-card border-border animate-modalIn"
            style={{ width: "min(90vw, 1000px)", height: "85vh" }}
          >
            {/* Cabecera del modal */}
            <div className="flex items-center justify-between px-5 py-3 border-b shrink-0 bg-surface border-border">
              <div className="flex items-center gap-2 min-w-0">
                <FileText size={15} strokeWidth={1.5} className="text-gold" />
                <span className="text-sm font-medium truncate text-text-primary">
                  {document_name}
                </span>
              </div>
              <button
                onClick={closeModal}
                className="shrink-0 p-1.5 rounded-lg transition-colors ml-4 text-text-secondary hover:text-text-primary"
                aria-label="Cerrar"
              >
                <X size={16} strokeWidth={1.5} />
              </button>
            </div>

            {/* Visor PDF */}
            <div className="flex-1 overflow-hidden">
              {pdfUrl ? (
                <iframe
                  src={pdfUrl}
                  className="w-full h-full border-0"
                  title={document_name}
                  style={{ backgroundColor: "#fff" }}
                  onError={() => setError("Tu navegador no soporta previsualización inline.")}
                />
              ) : null}

              {error && !pdfUrl && (
                <div className="flex flex-col items-center justify-center h-full gap-3 p-8 text-center">
                  <AlertCircle size={32} strokeWidth={1.5} className="text-text-secondary" />
                  <p className="text-sm text-text-secondary">
                    Tu navegador no soporta previsualización.
                    <br />
                    Contacta con tu administrador para acceder al documento.
                  </p>
                  <p className="text-xs text-muted">{error}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
