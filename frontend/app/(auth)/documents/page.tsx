"use client";

import { apiFetch } from "@/lib/api";
import { useAuthContext } from "@/components/Auth/AuthProvider";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { UploadCloud, FileText, Trash2 } from "lucide-react";

export default function DocumentsPage() {
  const { user } = useAuthContext();
  const router = useRouter();
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const isAdmin = user?.role === "admin" || user?.role === "super_admin";

  useEffect(() => {
    if (user && !isAdmin) router.push("/dashboard");
  }, [user, isAdmin, router]);

  useEffect(() => {
    loadDocuments();
  }, []);

  if (user && !isAdmin) return null;

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const data = await apiFetch("/documents/");
      if (Array.isArray(data)) setDocuments(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      await apiFetch("/documents/upload", {
        method: "POST",
        body: formData,
      });

      setSelectedFile(null);
      loadDocuments();
      alert("Documento subido exitosamente");
    } catch (err: any) {
      console.error("Error capturado:", err);

      let mensajeFinal = "Error desconocido";

      if (err.detail) {
        mensajeFinal = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
      } else if (err.message) {
        mensajeFinal = err.message;
      } else {
        mensajeFinal = JSON.stringify(err);
      }

      setError(mensajeFinal);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: string, filename: string) => {
    if (!window.confirm(`¿Eliminar "${filename}"? Esta acción no se puede deshacer.`)) {
      return;
    }

    setDeleting(docId);
    try {
      await apiFetch(`/documents/${docId}`, { method: "DELETE" });
      loadDocuments();
    } catch (err: any) {
      console.error("Error al eliminar:", err);
      let mensajeFinal = "Error desconocido";

      if (err.detail) {
        mensajeFinal = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
      } else if (err.message) {
        mensajeFinal = err.message;
      } else {
        mensajeFinal = JSON.stringify(err);
      }

      setError(mensajeFinal);
    } finally {
      setDeleting(null);
    }
  };

  const statusBadge = (status: string) => {
    if (status === "completed") return "badge-success";
    if (status === "processing") return "badge-warning";
    return "badge-error";
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight" style={{ color: "#F5F5F5" }}>
          Documentos
        </h1>
        <p className="text-sm mt-1" style={{ color: "#888888" }}>
          Sube PDFs para vectorizarlos en la base de conocimiento.
        </p>
      </div>

      {/* Upload card */}
      <div className="card card-padding">
        <h2 className="text-sm font-semibold mb-4" style={{ color: "#F5F5F5" }}>
          Subir Documento
        </h2>

        <form onSubmit={handleUpload} className="space-y-4">
          <label
            className="group relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-10 cursor-pointer transition-colors"
            style={{ borderColor: selectedFile ? "#C9A84C" : "#2A2A2A" }}
            onMouseEnter={(e) =>
              ((e.currentTarget as HTMLLabelElement).style.borderColor = "#C9A84C")
            }
            onMouseLeave={(e) =>
              ((e.currentTarget as HTMLLabelElement).style.borderColor = selectedFile ? "#C9A84C" : "#2A2A2A")
            }
          >
            <input
              type="file"
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              accept=".pdf"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            />
            <UploadCloud
              size={32}
              strokeWidth={1.5}
              style={{ color: selectedFile ? "#C9A84C" : "#555555" }}
            />
            <p className="text-sm font-medium mt-3" style={{ color: "#F5F5F5" }}>
              {selectedFile ? selectedFile.name : "Selecciona un PDF"}
            </p>
            <p className="text-xs mt-1" style={{ color: "#555555" }}>
              Haz clic para buscar el archivo
            </p>
          </label>

          <button
            type="submit"
            disabled={!selectedFile || uploading}
            className="btn btn-primary w-full"
          >
            {uploading ? "Procesando..." : "Subir Documento"}
          </button>
        </form>

        {error && (
          <div
            className="mt-4 px-4 py-3 rounded-lg border text-sm"
            style={{
              backgroundColor: "rgba(229,62,62,0.08)",
              borderColor: "rgba(229,62,62,0.3)",
              color: "#E53E3E",
            }}
          >
            <p className="font-semibold mb-1">Error</p>
            <p className="font-mono text-xs break-all">{error}</p>
          </div>
        )}
      </div>

      {/* Documents list */}
      <div className="card overflow-hidden">
        <div
          className="border-b px-6 py-4"
          style={{ borderColor: "#2A2A2A" }}
        >
          <h2 className="text-sm font-semibold" style={{ color: "#F5F5F5" }}>
            Documentos en el sistema
          </h2>
        </div>

        <div className="p-4 space-y-2">
          {loading ? (
            <p className="text-sm px-2" style={{ color: "#888888" }}>
              Cargando documentos...
            </p>
          ) : documents.length === 0 ? (
            <p className="text-sm px-2 italic" style={{ color: "#555555" }}>
              No hay documentos aún.
            </p>
          ) : (
            documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between px-4 py-3 rounded-lg border transition-colors"
                style={{ borderColor: "#2A2A2A", backgroundColor: "#111111" }}
                onMouseEnter={(e) =>
                  ((e.currentTarget as HTMLDivElement).style.backgroundColor = "#161616")
                }
                onMouseLeave={(e) =>
                  ((e.currentTarget as HTMLDivElement).style.backgroundColor = "#111111")
                }
              >
                <div className="flex items-center gap-3 min-w-0">
                  <FileText size={15} strokeWidth={1.5} style={{ color: "#C9A84C", flexShrink: 0 }} />
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate" style={{ color: "#F5F5F5" }}>
                      {doc.filename}
                    </p>
                    <p className="text-xs mt-0.5" style={{ color: "#555555" }}>
                      {doc.file_size ? `${(doc.file_size / 1024).toFixed(1)} KB` : ""}{" "}
                      {doc.vector_count ? `· ${doc.vector_count} vectores` : ""}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0 ml-4">
                  <span className={statusBadge(doc.upload_status)}>
                    {doc.upload_status}
                  </span>
                  <button
                    onClick={() => handleDelete(doc.id, doc.filename)}
                    disabled={deleting === doc.id}
                    className="btn btn-danger btn-sm px-2 py-1"
                    title="Eliminar documento"
                  >
                    {deleting === doc.id ? (
                      <span className="text-xs">...</span>
                    ) : (
                      <Trash2 size={13} strokeWidth={1.75} />
                    )}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
